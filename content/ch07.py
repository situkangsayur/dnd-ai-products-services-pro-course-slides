# -*- coding: utf-8 -*-
"""Chapter 7 — A deep dive on Keras.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 7
(pp. 190-230), read from the book PDF.

The longest chapter in the first half of the book, organised around one
principle: progressive disclosure of complexity -- easy to start, and no
ceiling.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url, notebook_url  # noqa: E402


MMD_TICKET = """
flowchart LR
  T["title<br/><code>(10000,)</code>"] --> C["Concatenate<br/><code>(20100,)</code>"]
  B["text_body<br/><code>(10000,)</code>"] --> C
  G["tags<br/><code>(100,)</code>"] --> C
  C --> D["Dense 64 relu<br/><code>dense_features</code>"]
  D --> P["priority<br/>1 unit, sigmoid"]
  D --> DP["department<br/>4 units, softmax"]
"""

MMD_REUSE = """
flowchart LR
  D["dense_features<br/><small>an intermediate node</small>"]
  P["priority"]
  DP["department"]
  N["difficulty<br/><small>a NEW head, added later</small>"]
  D --> P
  D --> DP
  D --> N
"""

MMD_APICHOICE = """
flowchart TB
  Q1{"Can the model be drawn as a<br/>directed acyclic graph of layers?"}
  Q2{"Is it a simple<br/>linear stack?"}
  SEQ["Sequential"]
  FUN["Functional API<br/><small>recommended default</small>"]
  SUB["Model subclassing"]
  Q1 -- yes --> Q2
  Q2 -- yes --> SEQ
  Q2 -- no --> FUN
  Q1 -- "no: loops, recursion,<br/>arbitrary control flow" --> SUB
"""

MMD_CALLBACKS = """
flowchart LR
  TB["on_train_begin"] --> EB["on_epoch_begin"]
  EB --> BB["on_batch_begin"]
  BB --> BE["on_batch_end"]
  BE -. "next batch" .-> BB
  BE --> EE["on_epoch_end"]
  EE -. "next epoch" .-> EB
  EE --> TE["on_train_end"]
"""

MMD_TRAINSTEP = """
flowchart LR
  A["1. Forward pass<br/><code>model(x, training=True)</code>"]
  B["2. Loss<br/><code>loss_fn(y, y_pred)</code>"]
  C["3. Gradients<br/>w.r.t. trainable_weights"]
  D["4. Update<br/><code>optimizer.apply(...)</code>"]
  A --> B --> C --> D
  D -. "next batch" .-> A
"""

MMD_LOOPCHOICE = """
flowchart TB
  Q1{"Does built-in fit()<br/>do what you need?"}
  Q2{"Do you still want callbacks,<br/>distribution, and speed?"}
  FIT["fit() as-is"]
  OVR["Override train_step()<br/><small>fit() still runs</small>"]
  RAW["Write the whole loop<br/><small>full control, no callbacks</small>"]
  Q1 -- yes --> FIT
  Q1 -- no --> Q2
  Q2 -- yes --> OVR
  Q2 -- no --> RAW
"""

FIG_SPECTRUM = "figs/book/figure-7-1.png"


NB = ["01_three_ways_to_build_a_model.ipynb", "02_custom_metrics_and_callbacks.ipynb",
      "03_custom_train_step_per_backend.ipynb"]

DECK = {
    "id": "ch07",
    "kind": "chapter",
    "number": 7,
    "title": "A Deep Dive on Keras",
    "subtitle": "Three ways to build a model, three levels of control over training "
                "— and one principle holding them together: easy to start, and no "
                "ceiling.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 7",
    "source_url": chapter_url(7),
    "duration": "3 hours (2 sessions)",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(7, local_notebooks=NB),
    "objectives": [
        "Explain **progressive disclosure of complexity**, and place yourself on "
        "the spectrum of Keras workflows.",
        "Build multi-input, multi-output models with the **Functional API**, and "
        "train them with either lists or dictionaries.",
        "Use **access to layer connectivity**: plot a topology with `plot_model()` "
        "and **extract features** from intermediate nodes.",
        "Write a **Model subclass** — and name what you give up by choosing it.",
        "Write **custom metrics** (`update_state`, `result`, `reset_state`) and "
        "**custom callbacks**, and combine `EarlyStopping` with `ModelCheckpoint`.",
        "Write your own **`train_step()`** in TensorFlow, PyTorch, and JAX, and "
        "plug it into `fit()` so callbacks and built-in optimisations still apply.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Section 7.1",
            "title": "One principle behind the whole API",
            "blocks": [
                {"t": "img", "src": FIG_SPECTRUM, "credit": True, "max_h": "34vh",
                 "cap": "Figure 7.1 — not four different frameworks, but one spectrum built "
                        "on shared APIs."},
                {"t": "quote",
                 "md": "You could be using Keras like you would use scikit-learn — just "
                       "calling fit() and letting the framework do its thing — or you could "
                       "be using it like NumPy, taking full control of every little detail.",
                 "cite": "Chollet & Watson, section 7.1"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.1",
            "title": "Why that matters for a career, not just a project",
            "blocks": [
                {"t": "p", "md": "Because every workflow rests on the same `Layer` and `Model` "
                                 "APIs, components from one can be used in any other. "
                                 "**They all talk to each other.**"},
                {"t": "band",
                 "md": "So what you learn today stays valid once you are an expert. You do "
                       "**not** have to switch frameworks going from student to researcher, "
                       "or from data scientist to deep learning engineer."},
                {"t": "p", "md": "The book's analogy: **Keras is the Python of deep learning** "
                                 "— multiparadigm, with several usage patterns that work "
                                 "together rather than one \"true\" way."},
            ],
            "notes": "Worth repeating: this removes the anxiety of 'will I have to relearn "
                     "all this later?'",
        },

        {"type": "section", "num": "01", "title": "Three ways to build a model",
         "lead": "Sequential, Functional, subclassing — and when each is right."},

        {
            "type": "slide",
            "kicker": "Section 7.2.1",
            "title": "Sequential is essentially a Python list",
            "blocks": [
                {"t": "p", "md": "It is the most approachable API, and its limits are equally "
                                 "clear: it can only express models with **one input and one "
                                 "output**, applying one layer after another."},
                {"t": "band", "style": "amber",
                 "md": "In practice, models with **multiple inputs** (an image and its "
                       "metadata), **multiple outputs** (several things to predict), or a "
                       "**non-linear topology** are ==entirely ordinary=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.2",
            "title": "The Functional API, and the symbolic tensor",
            "blocks": [
                {"t": "p", "md": "The same two-layer stack, written functionally. The key new "
                                 "object is what `keras.Input` returns."},
                {"t": "code", "lang": "python", "file": "listing 7.8 — a simple Functional model",
                 "src": """inputs = keras.Input(shape=(3,), name="my_input")
features = layers.Dense(64, activation="relu")(inputs)
outputs = layers.Dense(10, activation="softmax")(features)

model = keras.Model(inputs=inputs, outputs=outputs, name="my_functional_model")

print(inputs.shape, inputs.dtype)      # (None, 3) float32  -- None = batch size
print(features.shape)                  # (None, 64)"""},
                {"t": "band",
                 "md": "`inputs` is a **symbolic tensor**: it holds ==no data at all==, only "
                       "the specification of the tensors the model will eventually see. Every "
                       "Keras layer accepts either real tensors or symbolic ones."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.2",
            "title": "A model that Sequential cannot express",
            "blocks": [
                {"t": "p", "md": "The book's worked example: a system that ranks customer "
                                 "support tickets by priority and routes them to the right "
                                 "department. Three inputs, two outputs."},
                {"t": "mmd", "id": "ch07-ticket", "src": MMD_TICKET,
                 "cap": "Three inputs, one shared intermediate representation, two heads."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.2 · listing 7.9",
            "title": "…and it is nine lines",
            "blocks": [
                {"t": "p", "md": "Each `Input` is named, so the pieces can be referred to by "
                                 "name later rather than by position."},
                {"t": "code", "lang": "python", "file": "listing 7.9 — multi-input, multi-output",
                 "src": """vocabulary_size, num_tags, num_departments = 10000, 100, 4

title     = keras.Input(shape=(vocabulary_size,), name="title")
text_body = keras.Input(shape=(vocabulary_size,), name="text_body")
tags      = keras.Input(shape=(num_tags,), name="tags")

features = layers.Concatenate()([title, text_body, tags])
features = layers.Dense(64, activation="relu", name="dense_features")(features)

priority   = layers.Dense(1, activation="sigmoid", name="priority")(features)
department = layers.Dense(num_departments, activation="softmax",
                          name="department")(features)

model = keras.Model(inputs=[title, text_body, tags],
                    outputs=[priority, department])"""},
                {"t": "band",
                 "md": "The book describes it as ==like playing with LEGO bricks==: simple, "
                       "and flexible enough for arbitrary graphs of layers."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.2 · listing 7.10–7.11",
            "title": "Training it: by position, or by name",
            "blocks": [
                {"t": "p", "md": "Losses and metrics have to be supplied per output. There are "
                                 "two ways to say which is which."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.10 — lists",
                         "src": """model.compile(
    optimizer="adam",
    loss=["mean_squared_error",
          "sparse_categorical_crossentropy"],
    metrics=[["mean_absolute_error"],
             ["accuracy"]])

model.fit(
    [title_data, text_body_data, tags_data],
    [priority_data, department_data],
    epochs=1)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.11 — dictionaries",
                         "src": """model.compile(
    optimizer="adam",
    loss={"priority": "mean_squared_error",
          "department":
              "sparse_categorical_crossentropy"},
    metrics={"priority": ["mean_absolute_error"],
             "department": ["accuracy"]})

model.fit(
    {"title": title_data,
     "text_body": text_body_data,
     "tags": tags_data},
    {"priority": priority_data,
     "department": department_data},
    epochs=1)"""},
                    ],
                ]},
                {"t": "band",
                 "md": "The list form **must follow the order** given to `Model()`. With many "
                       "inputs or outputs, ==use the dictionary form== — order stops mattering "
                       "and the code becomes far harder to get wrong."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.2",
            "title": "The real payoff: the graph is inspectable",
            "blocks": [
                {"t": "p", "md": "A Functional model is an **explicit graph data structure**. "
                                 "That enables two things a subclassed model cannot do: "
                                 "plotting the topology, and extracting features."},
                {"t": "code", "lang": "python", "file": "plotting and inspecting",
                 "src": """keras.utils.plot_model(model, "ticket_classifier.png")

# far more useful while debugging:
keras.utils.plot_model(model, "ticket_classifier_with_shape_info.png",
                       show_shapes=True, show_layer_names=True)

print(model.layers[3].output)"""},
                {"t": "out", "src": "<KerasTensor shape=(None, 20100), dtype=float32>"},
                {"t": "p", "md": "The `None` is the batch size: this model accepts batches of "
                                 "any size."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.2 · listing 7.13",
            "title": "Feature extraction: adding a head without retraining",
            "blocks": [
                {"t": "p", "md": "Suppose you now also want to estimate how hard a ticket will "
                                 "be to resolve. Because the intermediate node is reachable, "
                                 "**nothing has to be rebuilt from scratch**."},
                {"t": "code", "lang": "python", "file": "listing 7.13 — reusing an intermediate node",
                 "src": """features = model.layers[4].output          # the shared Dense layer
difficulty = layers.Dense(3, activation="softmax", name="difficulty")(features)

new_model = keras.Model(
    inputs=[title, text_body, tags],
    outputs=[priority, department, difficulty])"""},
                {"t": "mmd", "id": "ch07-reuse", "src": MMD_REUSE,
                 "cap": "One shared representation, now feeding three heads."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.3 · listing 7.14",
            "title": "Model subclassing: total control",
            "blocks": [
                {"t": "p", "md": "Define the layers in `__init__()`, define the forward pass "
                                 "in `call()`. Weights are created the first time the model "
                                 "is called on data."},
                {"t": "code", "lang": "python", "file": "listing 7.14 — the same model, subclassed",
                 "src": """class CustomerTicketModel(keras.Model):
    def __init__(self, num_departments):
        super().__init__()                       # do not forget the super constructor
        self.concat_layer = layers.Concatenate()
        self.mixing_layer = layers.Dense(64, activation="relu")
        self.priority_scorer = layers.Dense(1, activation="sigmoid")
        self.department_classifier = layers.Dense(num_departments,
                                                  activation="softmax")

    def call(self, inputs):                      # the forward pass lives here
        features = self.concat_layer(
            [inputs["title"], inputs["text_body"], inputs["tags"]])
        features = self.mixing_layer(features)
        return self.priority_scorer(features), self.department_classifier(features)"""},
                {"t": "p", "md": "This unlocks models that ==cannot be expressed as a directed "
                                 "acyclic graph== — a `call()` that uses layers inside a `for` "
                                 "loop, or calls them recursively."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.3",
            "title": "Layer or Model — what actually differs",
            "blocks": [
                {"t": "table",
                 "head": ["", "`Layer`", "`Model`"],
                 "widths": [34, 33, 33],
                 "rows": [
                     ["Role", "A building block used to make models.",
                      "The top-level object you train and export."],
                     ["`fit()`, `evaluate()`, `predict()`", "Does not have them.", "Has them."],
                     ["Saveable to a file", "No.", "Yes."],
                 ]},
                {"t": "p", "md": "Beyond that the two classes are **virtually identical**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.3",
            "title": "What subclassing costs you",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**A Functional model** is an explicit data structure "
                                         "— a graph of layers you can view, inspect, and "
                                         "modify."},
                        {"t": "p", "md": "**A subclassed model** is ==a piece of bytecode==: a "
                                         "Python class with a `call()` method containing raw "
                                         "code. That is the source of its flexibility, and of "
                                         "its limitations."},
                    ],
                    [
                        {"t": "cards", "cols": 1, "items": [
                            {"ico": "🚫", "h": "Lost when you subclass",
                             "p": "`summary()` **does not show layer connectivity** · "
                                  "`plot_model()` **cannot be used** · **feature extraction "
                                  "is impossible** — there is simply no graph.",
                             "style": "bad"},
                        ]},
                    ],
                ]},
                {"t": "band", "style": "rose",
                 "md": "Once instantiated, the forward pass becomes **a complete black box**. "
                       "You are developing a new Python object rather than snapping bricks "
                       "together, so ==the error surface is much larger=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.4 · listing 7.15–7.16",
            "title": "The three mix freely",
            "blocks": [
                {"t": "p", "md": "Choosing one pattern does not lock you out of the others. "
                                 "All Keras models interoperate."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.15 — subclass inside Functional",
                         "src": """class Classifier(keras.Model):
    def __init__(self, num_classes=2):
        super().__init__()
        units, act = ((1, "sigmoid") if num_classes == 2
                      else (num_classes, "softmax"))
        self.dense = layers.Dense(units, activation=act)

    def call(self, inputs):
        return self.dense(inputs)

inputs = keras.Input(shape=(3,))
features = layers.Dense(64, activation="relu")(inputs)
outputs = Classifier(num_classes=10)(features)
model = keras.Model(inputs, outputs)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.16 — Functional inside subclass",
                         "src": """inputs = keras.Input(shape=(64,))
outputs = layers.Dense(1, activation="sigmoid")(inputs)
binary_classifier = keras.Model(inputs, outputs)

class MyModel(keras.Model):
    def __init__(self):
        super().__init__()
        self.dense = layers.Dense(64, activation="relu")
        self.classifier = binary_classifier

    def call(self, inputs):
        return self.classifier(self.dense(inputs))"""},
                    ],
                ]},
                {"t": "p", "md": "They are all part of the same spectrum, so the boundary is "
                                 "a design choice rather than a wall."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.2.5",
            "title": "Which one to reach for",
            "blocks": [
                {"t": "mmd", "id": "ch07-apichoice", "src": MMD_APICHOICE,
                 "cap": "The book's own recommendation, as a decision."},
                {"t": "band",
                 "md": "Every example in the rest of the book uses the **Functional API** — "
                       "but with **subclassed layers** inside it. That combination gives "
                       "==development flexibility while keeping the Functional API's "
                       "advantages=="},
            ],
        },

        {"type": "section", "num": "02", "title": "The built-in training loop",
         "lead": "Custom metrics, callbacks, and TensorBoard."},

        {
            "type": "slide",
            "kicker": "Section 7.3",
            "title": "The workflow you already know",
            "blocks": [
                {"t": "p", "md": "Everything in this section customises the following four "
                                 "calls without replacing them."},
                {"t": "code", "lang": "python", "file": "listing 7.17 — the standard workflow",
                 "src": """def get_mnist_model():
    inputs = keras.Input(shape=(28 * 28,))
    features = layers.Dense(512, activation="relu")(inputs)
    features = layers.Dropout(0.5)(features)
    outputs = layers.Dense(10, activation="softmax")(features)
    return keras.Model(inputs, outputs)

model = get_mnist_model()
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_images, train_labels, epochs=3,
          validation_data=(val_images, val_labels))
test_metrics = model.evaluate(test_images, test_labels)
predictions = model.predict(test_images)"""},
                {"t": "p", "md": "Two ways to customise it: **your own metrics**, and "
                                 "**callbacks** scheduled at specific points during training."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.1 · listing 7.18",
            "title": "Writing your own metric",
            "blocks": [
                {"t": "p", "md": "A metric subclasses `keras.metrics.Metric`. Like a layer it "
                                 "holds state in Keras variables — but that state is "
                                 "==not updated by backpropagation==, so you write the update "
                                 "logic yourself."},
                {"t": "code", "lang": "python", "file": "listing 7.18 — RMSE as a custom metric",
                 "src": """from keras import ops

class RootMeanSquaredError(keras.metrics.Metric):
    def __init__(self, name="rmse", **kwargs):
        super().__init__(name=name, **kwargs)
        self.mse_sum = self.add_weight(name="mse_sum", initializer="zeros")
        self.total_samples = self.add_weight(name="total_samples", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true = ops.one_hot(y_true, num_classes=ops.shape(y_pred)[1])
        self.mse_sum.assign_add(ops.sum(ops.square(y_true - y_pred)))
        self.total_samples.assign_add(ops.shape(y_pred)[0])

    def result(self):
        return ops.sqrt(self.mse_sum / self.total_samples)

    def reset_state(self):
        self.mse_sum.assign(0.)
        self.total_samples.assign(0.)"""},
                {"t": "p", "md": "The next slide names what each of those three methods is "
                                 "responsible for."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.1",
            "title": "The three methods that form the contract",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "➕", "h": "update_state()",
                     "p": "Called once per batch with the targets and predictions. This is "
                          "where the accumulation happens.", "style": "accent"},
                    {"ico": "📤", "h": "result()",
                     "p": "Returns the metric's current value from that accumulated state.",
                     "style": "accent"},
                    {"ico": "🧹", "h": "reset_state()",
                     "p": "Clears the state without rebuilding the object, so the same "
                          "instance serves every epoch and both training and evaluation.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Unlike a layer, none of this state is touched by backpropagation — "
                       "==you own the update logic entirely=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.1",
            "title": "…and using it is the same as any built-in",
            "blocks": [
                {"t": "p", "md": "Custom metrics are passed to `compile()` exactly like the "
                                 "built-in ones, and appear in the progress bar."},
                {"t": "code", "lang": "python", "file": "using the custom metric",
                 "src": """model = get_mnist_model()
model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy", RootMeanSquaredError()])
model.fit(train_images, train_labels, epochs=3,
          validation_data=(val_images, val_labels))"""},
                {"t": "out", "src": "accuracy: 0.9612 - loss: 0.1284 - rmse: 0.2371"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.2",
            "title": "Callbacks: from a paper aeroplane to a drone",
            "blocks": [
                {"t": "quote",
                 "md": "Launching a training run on a large dataset for tens of epochs using "
                       "model.fit() can be a bit like launching a paper airplane: past the "
                       "initial impulse, you don't have any control over its trajectory or "
                       "its landing spot.",
                 "cite": "Chollet & Watson, section 7.3.2"},
                {"t": "p", "md": "A callback is an object passed to `fit()` that Keras calls "
                                 "at various points during training. It can see the model's "
                                 "state and **act**: interrupt training, save the model, load "
                                 "different weights."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.2",
            "title": "What callbacks are used for",
            "blocks": [
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "💾", "h": "Checkpointing",
                     "p": "Saving the model state at different points during training."},
                    {"ico": "⏹", "h": "Early stopping",
                     "p": "Halting when validation stops improving — and keeping the best "
                          "model found."},
                    {"ico": "🎚", "h": "Dynamic parameters",
                     "p": "Adjusting things like the optimizer's learning rate mid-run."},
                    {"ico": "📝", "h": "Logging and plotting",
                     "p": "The `fit()` progress bar you already know is ==itself a callback=="},
                ]},
                {"t": "code", "lang": "python", "file": "some of the built-in callbacks",
                 "src": """keras.callbacks.ModelCheckpoint
keras.callbacks.EarlyStopping
keras.callbacks.LearningRateScheduler
keras.callbacks.ReduceLROnPlateau
keras.callbacks.CSVLogger"""},
                {"t": "p", "md": "Two of these do most of the work in practice, and the next "
                                 "slide shows them used together."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.2 · listing 7.19",
            "title": "The standard pair",
            "blocks": [
                {"t": "p", "md": "`EarlyStopping` decides when to stop; `ModelCheckpoint` "
                                 "makes sure the best version is on disk when it does."},
                {"t": "code", "lang": "python", "file": "listing 7.19 — callbacks in fit()",
                 "src": """callbacks_list = [
    keras.callbacks.EarlyStopping(
        monitor="accuracy",     # must be among the model's metrics
        patience=1,             # stop if it has not improved for one epoch
    ),
    keras.callbacks.ModelCheckpoint(
        filepath="checkpoint_path.keras",
        monitor="val_loss",
        save_best_only=True,    # only overwrite when val_loss improves
    ),
]

model.fit(train_images, train_labels, epochs=10,
          callbacks=callbacks_list,
          validation_data=(val_images, val_labels))   # REQUIRED: val_* is monitored"""},
                {"t": "band",
                 "md": "This replaces the wasteful pattern from chapters 4 and 5 — train to "
                       "find the best epoch, then retrain from scratch. ==One run is now "
                       "enough.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.2",
            "title": "Saving and reloading by hand",
            "blocks": [
                {"t": "p", "md": "Checkpointing is a convenience, not the only route. A model "
                                 "can be written and read at any time."},
                {"t": "code", "lang": "python", "file": "manual save and load",
                 "src": """model.save("my_checkpoint_path.keras")
model = keras.models.load_model("checkpoint_path.keras")"""},
                {"t": "p", "md": "This is the format chapter 6 exports from when preparing a "
                                 "model for deployment."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.3",
            "title": "Six hooks you can implement",
            "blocks": [
                {"t": "mmd", "id": "ch07-callbacks", "src": MMD_CALLBACKS,
                 "cap": "Each hook receives a `logs` dictionary with the metrics available at "
                        "that moment."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.3 · listing 7.20",
            "title": "A custom callback, end to end",
            "blocks": [
                {"t": "p", "md": "This one records the loss of every batch and plots the "
                                 "curve at the end of each epoch — far finer resolution than "
                                 "the per-epoch history gives."},
                {"t": "code", "lang": "python", "file": "listing 7.20 — per-batch loss history",
                 "src": """from matplotlib import pyplot as plt

class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs):
        self.per_batch_losses = []

    def on_batch_end(self, batch, logs):
        self.per_batch_losses.append(logs.get("loss"))

    def on_epoch_end(self, epoch, logs):
        plt.clf()
        plt.plot(range(len(self.per_batch_losses)), self.per_batch_losses,
                 label="Training loss for each batch")
        plt.xlabel(f"Batch (epoch {epoch})")
        plt.ylabel("Loss")
        plt.savefig(f"plot_at_epoch_{epoch}", dpi=300)
        self.per_batch_losses = []"""},
                {"t": "band",
                 "md": "Pass it as `callbacks=[LossHistory()]`. Useful when a run looks "
                       "unstable and you need to see ==whether the instability is within an "
                       "epoch or between them=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.4",
            "title": "TensorBoard closes the experiment loop",
            "blocks": [
                {"t": "p", "md": "Progress is iterative: **idea → experiment → result → next "
                                 "idea**. Keras shortens idea-to-experiment; fast GPUs shorten "
                                 "experiment-to-result; TensorBoard handles ==result-to-next "
                                 "idea=="},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "📈", "h": "Monitor metrics", "p": "Visually, while training runs."},
                    {"ico": "🏗", "h": "Visualise the architecture", "p": "The model graph."},
                    {"ico": "📊", "h": "Histograms", "p": "Of activations and gradients."},
                    {"ico": "🧭", "h": "Explore embeddings", "p": "In 3D."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.3.4",
            "title": "Turning it on",
            "blocks": [
                {"t": "p", "md": "It is a callback like any other. Point it at a log directory "
                                 "and it writes as training proceeds."},
                {"t": "code", "lang": "python", "file": "the callback",
                 "src": """tensorboard = keras.callbacks.TensorBoard(log_dir="/full_path_to_your_log_dir")

model.fit(train_images, train_labels, epochs=10,
          validation_data=(val_images, val_labels),
          callbacks=[tensorboard])"""},
                {"t": "code", "lang": "bash", "file": "and the viewer",
                 "src": """# on a local machine
tensorboard --logdir /full_path_to_your_log_dir

# inside a Colab notebook
%load_ext tensorboard
%tensorboard --logdir /full_path_to_your_log_dir"""},
                {"t": "p", "md": "If `tensorboard` is not on your PATH, it installs with "
                                 "`pip install tensorboard`."},
            ],
        },

        {"type": "section", "num": "03", "title": "Writing your own training loop",
         "lead": "When fit() is not enough — and how to keep it anyway."},

        {
            "type": "slide",
            "kicker": "Section 7.4",
            "title": "Where the built-in loop stops",
            "blocks": [
                {"t": "p", "md": "`fit()` is built for **supervised learning**: known targets, "
                                 "and a loss computed from those targets and the model's "
                                 "predictions. Not every form of learning fits that shape."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🎨", "h": "Generative learning",
                     "p": "No explicit targets at all. Introduced in **chapter 16**."},
                    {"ico": "🔁", "h": "Self-supervised",
                     "p": "Targets are taken **from the inputs themselves**."},
                    {"ico": "🐕", "h": "Reinforcement learning",
                     "p": "Driven by occasional **rewards** — much like training a dog."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.1",
            "title": "Two details that break custom loops",
            "blocks": [
                {"t": "steps", "items": [
                    "**Pass `training=True` on the forward pass.** Layers such as `Dropout` "
                    "behave differently during training and inference. "
                    "`dropout(inputs, training=True)` drops activations; `training=False` does "
                    "nothing. So: `predictions = model(inputs, training=True)`.",
                    "**Use `model.trainable_weights`, not `model.weights`.** Models hold two "
                    "kinds: **trainable** weights updated by backpropagation, and "
                    "**non-trainable** weights updated by the layers themselves during the "
                    "forward pass.",
                ]},
                {"t": "band",
                 "md": "Among the built-in layers, the only one with non-trainable weights is "
                       "**`BatchNormalization`** — it tracks the mean and standard deviation "
                       "of the data flowing through it (chapter 9)."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.2",
            "title": "The shape of a training step",
            "blocks": [
                {"t": "mmd", "id": "ch07-trainstep", "src": MMD_TRAINSTEP,
                 "cap": "Identical in all three backends. Only step 3 is written differently."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.2",
            "title": "TensorFlow and PyTorch, side by side",
            "blocks": [
                {"t": "p", "md": "Both are close to the pseudocode. The difference is who "
                                 "holds the gradients between steps 2 and 3."},
                {"t": "code", "lang": "python", "file": "TensorFlow",
                 "src": """def train_step(inputs, targets):
    with tf.GradientTape() as tape:
        predictions = model(inputs, training=True)
        loss = loss_fn(targets, predictions)
    gradients = tape.gradient(loss, model.trainable_weights)
    optimizer.apply(gradients, model.trainable_weights)
    return loss"""},
                {"t": "code", "lang": "python", "file": "PyTorch",
                 "src": """def train_step(inputs, targets):
    predictions = model(inputs, training=True)
    loss = loss_fn(targets, predictions)
    loss.backward()                                     # fill in the gradients
    gradients = [w.value.grad for w in model.trainable_weights]
    with torch.no_grad():                               # must be inside no_grad()
        optimizer.apply(gradients, model.trainable_weights)
    model.zero_grad()                                   # backward() accumulates
    return loss"""},
                {"t": "band", "style": "rose",
                 "md": "`model.zero_grad()` is **not optional** in PyTorch: `backward()` adds "
                       "to the existing gradients, so without it the values pile up and "
                       "==training will not proceed=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.2 · JAX",
            "title": "JAX is harder, and the reason is statelessness",
            "blocks": [
                {"t": "p", "md": "Because the gradient function is obtained by transformation, "
                                 "you must first write a function that **returns** the loss. "
                                 "It has to be stateless: everything it uses comes in as an "
                                 "argument, and everything it updates comes back out."},
                {"t": "code", "lang": "python", "file": "stateless_call and value_and_grad",
                 "src": """outputs, non_trainable_weights = model.stateless_call(
    trainable_weights, non_trainable_weights, inputs)

def compute_loss_and_updates(trainable_variables, non_trainable_variables,
                             inputs, targets):
    outputs, non_trainable_variables = model.stateless_call(
        trainable_variables, non_trainable_variables, inputs, training=True)
    loss = loss_fn(targets, outputs)
    return loss, non_trainable_variables     # scalar FIRST, the rest is 'aux'

grad_fn = jax.value_and_grad(compute_loss_and_updates, has_aux=True)
(loss, non_trainable_weights), gradients = grad_fn(
    trainable_variables, non_trainable_variables, inputs, targets)"""},
                {"t": "p", "md": "`has_aux=True` is required because `jax.grad` only accepts "
                                 "functions returning a scalar, and this one also returns the "
                                 "updated non-trainable weights."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.2 · JAX",
            "title": "The optimizer has state too",
            "blocks": [
                {"t": "p", "md": "Most optimizers track auxiliary variables — momentum, for "
                                 "instance — which also have to be threaded through by hand."},
                {"t": "code", "lang": "python", "file": "stateless_apply",
                 "src": """trainable_variables, optimizer_variables = optimizer.stateless_apply(
    optimizer_variables, gradients, trainable_variables)"""},
                {"t": "band",
                 "md": "The same pattern covers metrics: inside a stateless function you "
                       "cannot call `update_state()`, so Keras provides "
                       "==`stateless_update_state()`, `stateless_result()`, and "
                       "`stateless_reset_state()`=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.3",
            "title": "Using metrics at the low level",
            "blocks": [
                {"t": "p", "md": "Outside `fit()`, metrics are driven by hand: update per "
                                 "batch, query when you want a number."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "a normal metric",
                         "src": """metric = keras.metrics.SparseCategoricalAccuracy()
targets = ops.array([0, 1, 2])
predictions = ops.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])
metric.update_state(targets, predictions)
print(f"result: {metric.result():.2f}")"""},
                        {"t": "out", "src": "result: 1.00"},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "tracking a scalar average",
                         "src": """values = ops.array([0, 1, 2, 3, 4])
mean_tracker = keras.metrics.Mean()
for value in values:
    mean_tracker.update_state(value)
print(f"Mean: {mean_tracker.result():.2f}")"""},
                        {"t": "out", "src": "Mean: 2.00"},
                    ],
                ]},
                {"t": "band", "style": "amber",
                 "md": "Remember `metric.reset_state()` **at the start of each training epoch "
                       "and at the start of evaluation**. Forgetting it ==mixes numbers "
                       "across epochs== and quietly misleads you."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.4",
            "title": "The middle ground",
            "blocks": [
                {"t": "mmd", "id": "ch07-loopchoice", "src": MMD_LOOPCHOICE,
                 "cap": "Writing the whole loop costs you callbacks, performance "
                        "optimisations, and distributed training support."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 7.4.4 · listing 7.21",
            "title": "Override train_step(), keep fit()",
            "blocks": [
                {"t": "p", "md": "Subclass `keras.Model`, replace the one method `fit()` calls "
                                 "per batch, and return a dictionary of metric names to "
                                 "values. Everything else keeps working."},
                {"t": "code", "lang": "python", "file": "listing 7.21 — a custom train_step",
                 "src": """loss_fn = keras.losses.SparseCategoricalCrossentropy()
loss_tracker = keras.metrics.Mean(name="loss")

class CustomModel(keras.Model):
    def train_step(self, data):
        inputs, targets = data
        with tf.GradientTape() as tape:
            predictions = self(inputs, training=True)   # self, not model
            loss = loss_fn(targets, predictions)
        gradients = tape.gradient(loss, self.trainable_weights)
        self.optimizer.apply(gradients, self.trainable_weights)
        loss_tracker.update_state(loss)
        return {"loss": loss_tracker.result()}

    @property
    def metrics(self):
        return [loss_tracker]      # listed here so reset_state() is called for you"""},
                {"t": "bullets", "items": [
                    "Works whether you build with **Sequential, Functional, or subclassing**.",
                    "You do **not** need `@tf.function` or `@jax.jit` — ==the framework "
                    "applies it for you==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Progressive disclosure of complexity** — one spectrum of workflows over "
                    "the shared `Layer` and `Model` APIs, not several frameworks.",
                    "**Sequential** for simple stacks; **Functional API** for graphs of layers, "
                    "and that is what the rest of the book uses; **subclassing** for anything "
                    "that is not a graph.",
                    "Functional gives **access to layer connectivity**: `plot_model()` and "
                    "feature extraction. Subclassing ==forfeits both==.",
                    "The best combination in practice: **a Functional model containing "
                    "subclassed layers**.",
                    "**Custom metrics** = `update_state` / `result` / `reset_state`. "
                    "**Callbacks** = the six `on_*` hooks.",
                    "**`EarlyStopping` + `ModelCheckpoint`** replaces the wasteful "
                    "train-twice pattern.",
                    "Writing `train_step()`: remember **`training=True`** and "
                    "**`trainable_weights`**; in PyTorch **`zero_grad()`**; in JAX everything "
                    "goes through the **`stateless_*`** family.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_custom_train_step_per_backend.ipynb",
                     "href": notebook_url(7, "03_custom_train_step_per_backend.ipynb")},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 8 — Image classification",
                     "href": "../ch08/index.html"},
                ]},
            ],
        },
    ],
}
