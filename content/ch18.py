# -*- coding: utf-8 -*-
"""Chapter 18 — Best practices for the real world.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 18
(pp. 538-563), read from the book PDF.

Three ways to move past "works okay". Hyperparameter search and ensembling for
quality; data and model parallelism for scale; and lower-precision arithmetic
for a speed-up that is very nearly free. This is the chapter a professional
audience will return to most, because every technique in it is a cost decision.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_HPO_LOOP = """
flowchart TB
  A["<b>1.</b> Choose hyperparameters<br/><small>automatically</small>"]
  B["<b>2.</b> Build the model"]
  C["<b>3.</b> Fit, and measure on<br/>the validation data"]
  D["<b>4.</b> Choose the next set<br/><small>automatically</small>"]
  E["<b>6.</b> Eventually, measure<br/>on the test data"]
  A --> B --> C --> D
  D -- "5. repeat" --> A
  C --> E
"""

MMD_HPO_HARD = """
flowchart TB
  W["<b>Training weights</b><br/><small>compute a loss on a mini-batch,<br/>backpropagate</small>"]
  H["<b>Updating hyperparameters</b>"]
  H1["Space is <b>discrete</b><br/><small>no gradient descent;<br/>gradient-free methods only</small>"]
  H2["Feedback is <b>expensive</b><br/><small>each signal costs a full<br/>training run from scratch</small>"]
  H3["Feedback is <b>noisy</b><br/><small>is 0.2% a better config,<br/>or a lucky init?</small>"]
  W --> E["Easy"]
  H --> H1
  H --> H2
  H --> H3
"""

MMD_TUNER = """
flowchart LR
  P["<b>Pick</b> a set of<br/>hyperparameter values"]
  B["<b>Call</b> the model-building<br/>function with them"]
  T["<b>Train</b> and record<br/>the metrics"]
  P --> B --> T
  T -. "loop, max_trials times" .-> P
"""

MMD_ENSEMBLE = """
flowchart TB
  A["Model A<br/><small>touches the trunk</small>"]
  B["Model B<br/><small>touches a leg</small>"]
  C["Model C<br/><small>touches an ear</small>"]
  D["Model D<br/><small>a tree model, quite<br/>different from the rest</small>"]
  W["<b>Weighted average</b><br/><small>weights learned on<br/>the validation set</small>"]
  O["A far more accurate<br/>description than any one<br/>of them alone"]
  A --> W
  B --> W
  C --> W
  D --> W
  W --> O
"""

MMD_PARALLELISM = """
flowchart TB
  Q["Two ways to spread work<br/>across devices"]
  DP["<b>Data parallelism</b><br/><small>one model replicated on<br/>every device; each processes<br/>a different sub-batch</small>"]
  MP["<b>Model parallelism</b><br/><small>different parts of one model<br/>on different devices, working<br/>on the same batch</small>"]
  DR["Speed. Requires the model<br/>to <b>fit on one device</b>."]
  MR["Size. Used when the model<br/><b>does not fit</b> anywhere."]
  Q --> DP --> DR
  Q --> MP --> MR
"""

MMD_DATA_PARALLEL = """
flowchart TB
  B["Global batch<br/><small>128 samples</small>"]
  S1["Sub-batch<br/><small>64 samples</small>"]
  S2["Sub-batch<br/><small>64 samples</small>"]
  R1["<b>Replica 0</b><br/>gpu:0"]
  R2["<b>Replica 1</b><br/>gpu:1"]
  G["<b>Average the gradients</b><br/><small>update every replica<br/>from the average</small>"]
  E["State identical to training<br/>on the full batch of 128<br/><small>synchronous training</small>"]
  B --> S1 --> R1 --> G
  B --> S2 --> R2 --> G
  G --> E
"""

MMD_PARTITION = """
flowchart TB
  Q["Splitting one model<br/>across devices"]
  H["<b>Horizontal partitioning</b><br/><small>each device handles<br/>different layers</small>"]
  V["<b>Vertical partitioning</b><br/><small>each layer split across<br/>all devices</small>"]
  HR["Communication overhead:<br/>layer 1's output must be<br/>copied before layer 2 runs.<br/><b>GPUs sit idle.</b>"]
  VR["matmul and convolution are<br/>highly parallelizable, so this is<br/>easy to implement and<br/><b>almost always the best fit</b>."]
  Q --> H --> HR
  Q --> V --> VR
"""

MMD_MESH = """
flowchart TB
  M["<b>DeviceMesh</b><br/><small>shape (2, 4), eight devices</small>"]
  A0["<b>axis 0: &quot;data&quot;</b><br/><small>2 replicas</small>"]
  A1["<b>axis 1: &quot;model&quot;</b><br/><small>each replica split<br/>across 4 devices</small>"]
  L["<b>LayoutMap</b><br/><small>per variable, per dimension:<br/>shard or replicate</small>"]
  M --> A0 --> L
  M --> A1 --> L
"""

MMD_FLOAT = """
flowchart TB
  P["<b>Precision is to numbers<br/>what resolution is to images</b>"]
  H["<b>float16</b><br/>half precision<br/><small>smallest safe gap: 1e-3</small>"]
  S["<b>float32</b><br/>single precision<br/><small>smallest safe gap: 1e-7</small>"]
  D["<b>float64</b><br/>double precision<br/><small>smallest safe gap: 1e-16</small>"]
  P --> H
  P --> S
  P --> D
"""

MMD_MIXED = """
flowchart TB
  I["Inputs"]
  C["<b>compute_dtype = float16</b><br/><small>most of the forward pass,<br/>on half-precision copies<br/>of the weights</small>"]
  G["float16 gradients"]
  CAST["<b>Cast to float32</b>"]
  V["<b>variable_dtype = float32</b><br/><small>weights stored and updated<br/>in full precision</small>"]
  I --> C --> G --> CAST --> V
  V -. "half-precision copies" .-> C
"""

MMD_QUANT = """
flowchart LR
  A["float32 tensors"]
  B["<b>Scale</b><br/><small>abs-max, into [-127, 127]</small>"]
  C["<b>Cast to int8</b><br/><small>round and clip</small>"]
  D["<b>matmul in int8</b><br/><small>the fast part</small>"]
  E["<b>Cast back, unscale</b><br/><small>divide by the product<br/>of the two scales</small>"]
  F["float32 output,<br/>very nearly identical"]
  A --> B --> C --> D --> E --> F
"""

NB = ["01_kerastuner_search.ipynb", "02_ensembling_and_weights.ipynb",
      "03_data_and_model_parallel_jax.ipynb", "04_mixed_precision_and_loss_scaling.ipynb",
      "05_int8_quantization.ipynb"]

DECK = {
    "id": "ch18",
    "kind": "chapter",
    "number": 18,
    "title": "Best Practices for the Real World",
    "subtitle": "Past \"works okay\": automatic hyperparameter search, ensembling, "
                "distributed training across devices, and a near-free 2× from "
                "lower-precision arithmetic.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 18",
    "source_url": chapter_url(18),
    "duration": "3 hours (2 sessions)",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(18, local_notebooks=NB),
    "objectives": [
        "Distinguish **hyperparameters from parameters**, and say why hyperparameter "
        "search cannot use gradient descent.",
        "Define a **search space** with KerasTuner and run a Bayesian optimization "
        "search, then retrain the best configurations properly.",
        "Explain **validation-set overfitting** in tuning, and how to avoid trusting "
        "a contaminated number.",
        "Ensemble models with a **weighted average**, and explain why diversity "
        "matters more than individual quality.",
        "Choose between **data parallelism and model parallelism**, and say what "
        "each one is actually for.",
        "Use the **DeviceMesh and LayoutMap** APIs to shard a model across devices "
        "under the JAX backend.",
        "Explain **floating-point precision**, and use float16 inference, "
        "mixed-precision training, and loss scaling correctly.",
        "Apply **int8 quantization** to a trained model, and explain why the "
        "scale-and-unscale trick preserves the result.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "Getting the most out of your models",
         "lead": "From \"works okay\" to \"wins machine learning competitions\"."},

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "Hyperparameters are the decisions backpropagation cannot make",
            "blocks": [
                {"t": "p", "md": "How many layers? How many units or filters in each? `relu` or "
                                 "something else? `BatchNormalization` after this layer? How "
                                 "much dropout?"},
                {"t": "p", "md": "These architecture-level choices are called **hyperparameters**, "
                                 "to distinguish them from the model's **parameters**, which are "
                                 "trained by backpropagation."},
                {"t": "band", "md": "Experienced engineers build intuition about what works. But "
                                    "**there are no formal rules**, and initial decisions are "
                                    "almost always suboptimal even with very good intuition. "
                                    "==It should not be your job to fiddle with hyperparameters "
                                    "all day.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "The optimization loop",
            "blocks": [
                {"t": "mmd", "id": "ch18-hpo-loop", "src": MMD_HPO_LOOP,
                 "cap": "Automatic hyperparameter optimization is an entire field of research, "
                        "and an important one."},
                {"t": "p", "md": "The key to the whole process is **step 4** — the algorithm "
                                 "that analyses the relationship between validation performance "
                                 "and hyperparameter values to choose what to try next. Bayesian "
                                 "optimization, genetic algorithms, plain random search."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1 · why it is hard",
            "title": "Three reasons this is not like training weights",
            "blocks": [
                {"t": "mmd", "id": "ch18-hpo-hard", "src": MMD_HPO_HARD,
                 "cap": "Training weights is easy by comparison: one loss, one backward pass."},
                {"t": "p", "md": "The third point is the one people underestimate. If a run "
                                 "performs 0.2% better, was that **a better configuration** or "
                                 "**a lucky weight initialization**? Without answering that, you "
                                 "are optimizing noise."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1 · listing 18.1",
            "title": "KerasTuner: replace a constant with a range",
            "blocks": [
                {"t": "p", "md": "Replace hardcoded values like `units=32` with a range of "
                                 "choices. The set of such choices is the **search space**."},
                {"t": "code", "lang": "python", "file": "listing 18.1", "src": """import keras
from keras import layers

def build_model(hp):
    units = hp.Int(name="units", min_value=16, max_value=64, step=16)
    model = keras.Sequential(
        [
            layers.Dense(units, activation="relu"),
            layers.Dense(10, activation="softmax"),
        ]
    )
    optimizer = hp.Choice(name="optimizer", values=["rmsprop", "adam"])
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model"""},
                {"t": "p", "md": "The function takes `hp` and returns a **compiled model**. "
                                 "Four kinds of range exist: `Int`, `Float`, `Boolean`, "
                                 "`Choice`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1 · listing 18.2",
            "title": "Or subclass HyperModel for something configurable",
            "blocks": [
                {"t": "p", "md": "Model constants become constructor arguments."},
                {"t": "code", "lang": "python", "file": "listing 18.2", "src": """import keras_tuner as kt

class SimpleMLP(kt.HyperModel):
    def __init__(self, num_classes):
        self.num_classes = num_classes

    def build(self, hp):
        units = hp.Int(name="units", min_value=16, max_value=64, step=16)
        model = keras.Sequential(
            [
                layers.Dense(units, activation="relu"),
                layers.Dense(self.num_classes, activation="softmax"),
            ]
        )
        model.compile(...)   # exactly as in listing 18.1
        return model

hypermodel = SimpleMLP(num_classes=10)"""},
                {"t": "p", "md": "`build()` is the same function as before. The gain is "
                                 "**reuse**: one hypermodel, any number of classes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "The tuner is a for loop with a strategy",
            "blocks": [
                {"t": "mmd", "id": "ch18-tuner", "src": MMD_TUNER,
                 "cap": "Three built-in tuners: RandomSearch, BayesianOptimization, Hyperband."},
                {"t": "p", "md": "**BayesianOptimization** makes smart predictions about which "
                                 "new values are likely to perform best, given the outcome of "
                                 "previous choices — which is what separates it from random "
                                 "search."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "Configuring the tuner",
            "blocks": [
                {"t": "p", "md": "Six arguments, four of which decide whether the search is "
                                 "worth running at all."},
                {"t": "code", "lang": "python", "src": """tuner = kt.BayesianOptimization(
    build_model,
    objective="val_accuracy",
    max_trials=20,
    executions_per_trial=2,
    directory="mnist_kt_test",
    overwrite=True,
)"""},
                {"t": "table",
                 "head": ["Argument", "What it controls"],
                 "widths": [28, 72],
                 "rows": [
                     ["`objective`",
                      "The metric to optimize. **Always a validation metric** — the goal of the "
                      "search is models that generalize."],
                     ["`max_trials`", "How many different configurations to try."],
                     ["`executions_per_trial`",
                      "How many training runs **per configuration**, averaged — this is the "
                      "answer to the noisy-feedback problem."],
                     ["`overwrite`",
                      "`True` to start fresh; **`False` to resume** a crashed search from the "
                      "trial logs on disk."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1 · sidebar",
            "title": "Which direction is better?",
            "blocks": [
                {"t": "p", "md": "For built-in metrics KerasTuner infers the direction — accuracy "
                                 "should go up, a loss should go down. For a **custom metric** "
                                 "you must say so yourself."},
                {"t": "code", "lang": "python", "src": """objective = kt.Objective(
    name="val_accuracy",
    direction="max",
)

tuner = kt.BayesianOptimization(
    build_model,
    objective=objective,
    ...
)"""},
                {"t": "p", "md": "`name` must match what appears in the epoch logs. Get it wrong "
                                 "and the search runs happily while optimizing nothing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "Launching the search",
            "blocks": [
                {"t": "p", "md": "`search()` takes the same arguments as `fit()` — it simply "
                                 "passes them down for each new model."},
                {"t": "code", "lang": "python", "src": """num_val_samples = 10000
x_train, x_val = x_train[:-num_val_samples], x_train[-num_val_samples:]
y_train, y_val = y_train[:-num_val_samples], y_train[-num_val_samples:]

callbacks = [keras.callbacks.EarlyStopping(monitor="val_loss", patience=5)]

tuner.search(
    x_train, y_train,
    batch_size=128,
    epochs=100,
    validation_data=(x_val, y_val),
    callbacks=callbacks,
    verbose=2,
)"""},
                {"t": "band", "md": "**Never use your test set as validation data here.** You "
                                    "would overfit to it immediately, and your test metrics "
                                    "would stop meaning anything.", "style": "rose"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "A large epoch count plus early stopping",
            "blocks": [
                {"t": "p", "md": "`epochs=100` looks reckless until you notice the "
                                 "`EarlyStopping` callback. You **do not know in advance** how "
                                 "many epochs each configuration will need, so you give a "
                                 "generous budget and let the callback cut each run short."},
                {"t": "p", "md": "The MNIST example above runs in a few minutes. With a typical "
                                 "search space and dataset you will find yourself letting a "
                                 "search run **overnight, or over several days**."},
                {"t": "band", "md": "If the process crashes, restart it with `overwrite=False` "
                                    "and it resumes from the trial logs on disk. ==Set the "
                                    "directory somewhere durable before you start a multi-day "
                                    "search.==", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1 · listing 18.3",
            "title": "Retraining the winners is a separate job",
            "blocks": [
                {"t": "p", "md": "The search gives you configurations, not finished models."},
                {"t": "code", "lang": "python", "file": "listing 18.3", "src": """top_n = 4
best_hps = tuner.get_best_hyperparameters(top_n)"""},
                {"t": "p", "md": "When retraining, **fold the validation data back into "
                                 "training** — you are making no more hyperparameter changes, so "
                                 "there is nothing left to evaluate against it. Here that means "
                                 "training on all of MNIST's training split."},
                {"t": "p", "md": "But that leaves one parameter unsettled: **how many epochs**. "
                                 "The aggressive `patience` used during the search saved time; "
                                 "it may also have left models underfitted."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "First, find the best epoch on the validation set",
            "blocks": [
                {"t": "p", "md": "One more run per configuration, this time with a **much higher "
                                 "patience** — 10 rather than the 5 used during the search."},
                {"t": "code", "lang": "python", "src": """def get_best_epoch(hp):
    model = build_model(hp)
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", mode="min", patience=10
        )
    ]
    history = model.fit(
        x_train, y_train,
        validation_data=(x_val, y_val),
        epochs=100, batch_size=128, callbacks=callbacks,
    )
    val_loss_per_epoch = history.history["val_loss"]
    best_epoch = val_loss_per_epoch.index(min(val_loss_per_epoch)) + 1
    return best_epoch"""},
                {"t": "p", "md": "The high patience is affordable now: this runs a handful of "
                                 "times, not once per trial."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "Then retrain on everything, for 20% longer",
            "blocks": [
                {"t": "p", "md": "With the epoch count settled, train on the full data — "
                                 "validation folded back in."},
                {"t": "code", "lang": "python", "src": """def get_best_trained_model(hp):
    best_epoch = get_best_epoch(hp)
    model = build_model(hp)
    model.fit(
        x_train_full, y_train_full,
        batch_size=128, epochs=int(best_epoch * 1.2),
    )
    return model

best_models = []
for hp in best_hps:
    model = get_best_trained_model(hp)
    model.evaluate(x_test, y_test)
    best_models.append(model)"""},
                {"t": "p", "md": "The `* 1.2` accounts for the extra data: **more samples per "
                                 "epoch means the same number of epochs is a longer run**, but "
                                 "also that the model can absorb a little more before it starts "
                                 "overfitting."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1 · the shortcut, and the warning",
            "title": "Two things to remember about tuning at scale",
            "blocks": [
                {"t": "p", "md": "If you are not worried about slightly underperforming, there is "
                                 "a shortcut — reload the top models with the weights saved "
                                 "during the search:"},
                {"t": "code", "lang": "python", "src": """best_models = tuner.get_best_models(top_n)"""},
                {"t": "band", "md": "And the warning: **validation-set overfitting**. Because you "
                                    "are updating hyperparameters using a signal computed on "
                                    "validation data, you are effectively ==training them on the "
                                    "validation data==, and they will quickly overfit to it. "
                                    "Always keep this in mind.", "style": "rose"},
            ],
            "notes": "For a professional audience: this is why a genuinely held-out test set, "
                     "touched once, is a governance control and not just good hygiene.",
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1 · the art of it",
            "title": "Tuning is automation, not magic",
            "blocks": [
                {"t": "p", "md": "Once upon a time people handcrafted the features that went into "
                                 "shallow models. Deep learning automated that — features are "
                                 "learned from a feedback signal, not hand-tuned. **In the same "
                                 "way, you should not handcraft architectures.**"},
                {"t": "p", "md": "But search spaces grow **combinatorially** with the number of "
                                 "choices, so turning everything into a hyperparameter is far "
                                 "too expensive. You still need to handpick configurations with "
                                 "the potential to yield good metrics."},
                {"t": "band", "md": "The gain is that your decisions **graduate**: from "
                                    "micro-decisions (*how many units in this layer?*) to "
                                    "higher-level ones (*should I use residual connections "
                                    "throughout?*). And higher-level decisions ==generalize "
                                    "across tasks and datasets==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.1",
            "title": "Premade search spaces",
            "blocks": [
                {"t": "p", "md": "Following that logic, KerasTuner ships search spaces relevant "
                                 "to broad categories of problems. Pretty much every image "
                                 "classification problem can be solved with the same **search "
                                 "space template**."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🏗", "h": "kt.applications.HyperXception", "style": "accent",
                     "p": "A tunable version of the Keras Applications Xception model."},
                    {"ico": "🏗", "h": "kt.applications.HyperResNet", "style": "accent",
                     "p": "The same for ResNet. **Add data, run the search, get a pretty good "
                          "model.**"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.2",
            "title": "Ensembling, and the blind men",
            "blocks": [
                {"t": "p", "md": "**Ensembling** pools the predictions of several models to "
                                 "produce better predictions. Kaggle winners use very large "
                                 "ensembles that inevitably beat any single model, however good."},
                {"t": "p", "md": "The assumption: different well-performing models trained "
                                 "independently are likely to be good **for different reasons**. "
                                 "Each looks at slightly different aspects of the data, getting "
                                 "part of the truth but not all of it."},
                {"t": "quote", "md": "Blind men meeting an elephant: one touches the trunk — "
                                     "*\"it's like a snake\"*; another a leg — *\"like a pillar\"*. "
                                     "Each has part of the truth. **Interviewed together, they "
                                     "can tell a fairly accurate story.**",
                 "cite": "Section 18.1.2"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.2",
            "title": "Averaging, and then averaging better",
            "blocks": [
                {"t": "p", "md": "The easiest pooling is a plain average at inference time."},
                {"t": "code", "lang": "python", "src": """preds_a = model_a.predict(x_val)
preds_b = model_b.predict(x_val)
preds_c = model_c.predict(x_val)
preds_d = model_d.predict(x_val)

final_preds = 0.25 * (preds_a + preds_b + preds_c + preds_d)"""},
                {"t": "p", "md": "This only works if the classifiers are **more or less equally "
                                 "good**. If one is significantly worse, the result may be worse "
                                 "than the best single model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.2",
            "title": "Weighted average, weights learned on validation data",
            "blocks": [
                {"t": "p", "md": "The smarter pooling weights each model by how good it is."},
                {"t": "code", "lang": "python", "src": """final_preds = (
    0.5 * preds_a
    + 0.25 * preds_b
    + 0.1 * preds_c
    + 0.15 * preds_d
)"""},
                {"t": "p", "md": "Better classifiers get a higher weight. To find a good set, use "
                                 "**random search** or a simple optimization algorithm such as "
                                 "**Nelder-Mead** — over the validation data."},
                {"t": "band", "md": "There are many variants — averaging an exponential of the "
                                    "predictions, for instance. In general a **simple weighted "
                                    "average with weights optimized on validation data is a very "
                                    "strong baseline**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.2 · the actual principle",
            "title": "Diversity is strength",
            "blocks": [
                {"t": "mmd", "id": "ch18-ensemble", "src": MMD_ENSEMBLE,
                 "cap": "If all the blind men touched only the trunk, they would agree that "
                        "elephants are like snakes — and stay wrong together."},
                {"t": "p", "md": "In machine learning terms: **if all your models are biased the "
                                 "same way, the ensemble keeps that bias.** If they are biased "
                                 "differently, the biases cancel and the ensemble is more robust."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.1.2 · what follows from that",
            "title": "As good as possible, while as different as possible",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✅", "h": "Worth doing", "style": "good",
                     "p": "Very different **architectures**, or even different **brands** of "
                          "machine learning — tree-based methods alongside deep networks."},
                    {"ico": "❌", "h": "Largely not worth doing", "style": "bad",
                     "p": "The same network trained several times from different random "
                          "initializations. **Low diversity, tiny improvement.**"},
                ]},
                {"t": "p", "md": "In 2014 Chollet and Andrei Kolev took **fourth place** in "
                                 "Kaggle's Higgs Boson challenge with an ensemble of tree models "
                                 "and deep networks. One member — a regularized greedy forest — "
                                 "had a **significantly worse score** than the others and was "
                                 "given a small weight."},
                {"t": "band", "md": "It improved the ensemble **by a large factor**, precisely "
                                    "because it was so different: it carried information no other "
                                    "model had. ==It is not about how good your best model is; "
                                    "it is about the diversity of your candidates.=="},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "Scaling up with multiple devices",
         "lead": "Faster training directly improves the quality of your solutions."},

        {
            "type": "slide",
            "kicker": "Section 18.2 · figure 18.1",
            "title": "The loop of progress, and its next bottleneck",
            "blocks": [
                {"t": "p", "md": "From chapter 7: the quality of an idea is a function of how "
                                 "many refinement cycles it has been through. The speed of "
                                 "iteration depends on how fast you can **set up**, **run**, and "
                                 "**analyse** an experiment."},
                {"t": "lead", "md": "As your Keras fluency grows, coding up an experiment stops "
                                    "being the bottleneck. **The next bottleneck is training "
                                    "speed.**"},
                {"t": "p", "md": "Fast infrastructure means results back in 10 or 15 minutes, "
                                 "and hence dozens of iterations a day. ==Faster training "
                                 "directly improves the quality of your deep learning "
                                 "solutions.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.1",
            "title": "Two kinds of parallelism, for two different problems",
            "blocks": [
                {"t": "mmd", "id": "ch18-parallelism", "src": MMD_PARALLELISM,
                 "cap": "Model parallelism is not a way to speed up ordinary models — it is a "
                        "way to train larger ones."},
                {"t": "p", "md": "And you can mix them: split a model across four devices, then "
                                 "replicate that split model twice, for **eight devices total**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.1 · data parallelism",
            "title": "Divide and conquer",
            "blocks": [
                {"t": "mmd", "id": "ch18-data-parallel", "src": MMD_DATA_PARALLEL,
                 "cap": "Different samples processed in parallel — hence *data* parallelism."},
                {"t": "p", "md": "In **inference** you concatenate the sub-batch predictions. In "
                                 "**training** you average the gradients and update every replica "
                                 "from the average, so all replicas hold identical weights at all "
                                 "times. This is **synchronous training**; non-synchronous "
                                 "alternatives exist but are less efficient and no longer used."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.1 · the limitation",
            "title": "Simple, scalable, and it needs the model to fit",
            "blocks": [
                {"t": "p", "md": "Data parallelism is a simple and highly scalable way to train "
                                 "faster: get more devices, increase your batch size, and "
                                 "throughput rises accordingly."},
                {"t": "band", "md": "One limitation, and it is decisive at the frontier: the "
                                    "model must **fit on a single device**. It is now common to "
                                    "train foundation models with tens of billions of parameters, "
                                    "which ==will not fit on any single GPU==.", "style": "amber"},
                {"t": "p", "md": "That is where model parallelism comes in."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.1 · listing 18.4",
            "title": "A model too large for one device",
            "blocks": [
                {"t": "p", "md": "A concrete example to think with: 16,000 features in, 8,000 "
                                 "potentially overlapping categories out, two dense layers."},
                {"t": "code", "lang": "python", "file": "listing 18.4", "src": """model = keras.Sequential(
    [
        keras.layers.Input(shape=(16000,)),
        keras.layers.Dense(64000, activation="relu"),
        keras.layers.Dense(8000, activation="sigmoid"),
    ]
)"""},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "~1 billion", "l": "parameters in the first Dense"},
                    {"v": "~512 million", "l": "parameters in the second"},
                ]},
                {"t": "p", "md": "With two small devices, data parallelism is not available — "
                                 "the model does not fit on either. What you can do is **shard** "
                                 "(or *partition*) a single instance across both."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.1 · two ways to shard",
            "title": "Horizontal and vertical partitioning",
            "blocks": [
                {"t": "mmd", "id": "ch18-partition", "src": MMD_PARTITION,
                 "cap": "Vertical partitioning is almost always the right choice for large "
                        "models."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.1 · vertical partitioning by hand",
            "title": "Splitting one layer across two devices",
            "blocks": [
                {"t": "p", "md": "Split the kernel and bias of the first `Dense` in half, compute "
                                 "each half on its own device, and concatenate."},
                {"t": "code", "lang": "python", "src": """half_kernel_0 = kernel[:, :32000]
half_bias_0 = bias[:32000]
half_kernel_1 = kernel[:, 32000:]
half_bias_1 = bias[32000:]

with keras.device("gpu:0"):
    half_output_0 = keras.ops.matmul(inputs, half_kernel_0) + half_bias_0

with keras.device("gpu:1"):
    half_output_1 = keras.ops.matmul(inputs, half_kernel_1) + half_bias_1"""},
                {"t": "p", "md": "Each device now holds a kernel of shape **(16000, 32000)** "
                                 "instead of (16000, 64000). Nobody writes this by hand at "
                                 "scale — but seeing it once makes the `LayoutMap` API that "
                                 "follows read as ordinary code."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2 · a strong opinion, stated plainly",
            "title": "Use JAX",
            "blocks": [
                {"t": "quote", "md": "We will only cover the JAX backend, as it is the most "
                                     "performant and most scalable of the various Keras backends, "
                                     "**by a mile**. If you're doing any kind of large-scale "
                                     "distributed training and you aren't using JAX, you're "
                                     "making a mistake — and wasting your dollars burning way "
                                     "more compute than you actually need.",
                 "cite": "Section 18.2.2"},
                {"t": "p", "md": "For getting hold of the devices, there are two realistic "
                                 "options: acquire two to eight GPUs and mount them in one "
                                 "machine — *it will require a beefy power supply* — or **rent a "
                                 "multi-GPU VM** on Google Cloud, Azure, or AWS with drivers "
                                 "preinstalled. For anyone not training 24/7, the second."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2",
            "title": "Data parallelism is one line",
            "blocks": [
                {"t": "p", "md": "Before building your model, add this. That is the whole "
                                 "change."},
                {"t": "code", "lang": "python", "src": """keras.distribution.set_distribution(keras.distribution.DataParallel())"""},
                {"t": "p", "md": "For finer control, list the devices and pass them explicitly:"},
                {"t": "code", "lang": "python", "src": """keras.distribution.list_devices()
# ["gpu:0", "gpu:1", ...]

keras.distribution.set_distribution(
    keras.distribution.DataParallel(["gpu:0", "gpu:1"])
)"""},
                {"t": "p", "md": "Note the ordering requirement: **before creating the model**. "
                                 "Setting it afterwards silently does nothing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2 · what to actually expect",
            "title": "N GPUs do not give an N× speedup",
            "blocks": [
                {"t": "stats", "cols": 3, "items": [
                    {"v": "~2.0×", "l": "with 2 GPUs"},
                    {"v": "~3.8×", "l": "with 4 GPUs"},
                    {"v": "~7.3×", "l": "with 8 GPUs"},
                ]},
                {"t": "p", "md": "Distribution introduces overhead — in particular, **merging "
                                 "the weight deltas** from different devices takes time. The "
                                 "efficiency loss grows with the device count."},
                {"t": "band", "md": "These numbers assume a **global batch size large enough to "
                                    "keep every GPU at full capacity**. If your batch is too "
                                    "small, the local batch will not keep the GPUs busy and the "
                                    "speedup collapses.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2 · the DeviceMesh API",
            "title": "A grid of devices, with named axes",
            "blocks": [
                {"t": "p", "md": "A **device mesh** is a grid of devices, organised along axes. "
                                 "Typically one axis handles data parallelism and one handles "
                                 "model parallelism."},
                {"t": "code", "lang": "python", "src": """device_mesh = keras.distribution.DeviceMesh(
    shape=(2, 4),
    axis_names=["data", "model"],
)

# or, naming the devices explicitly:
devices = [f"gpu:{i}" for i in range(8)]
device_mesh = keras.distribution.DeviceMesh(
    shape=(2, 4),
    axis_names=["data", "model"],
    devices=devices,
)"""},
                {"t": "p", "md": "Two devices along axis 0, four along axis 1: computation is "
                                 "**split across four GPUs**, and **two copies** of that split "
                                 "model each process a different sub-batch. A mesh need not be "
                                 "2D, but in practice you will only ever see 1D and 2D."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2 · the LayoutMap API",
            "title": "Per variable, per dimension: shard or replicate",
            "blocks": [
                {"t": "p", "md": "Variables are the frame of reference. Shard or replicate them "
                                 "across the mesh, and the compiler moves the associated "
                                 "computation to the right device."},
                {"t": "mmd", "id": "ch18-mesh", "src": MMD_MESH,
                 "cap": "Two independent decisions, made per dimension of each variable."},
                {"t": "p", "md": "**Replicate** — every device along that axis sees the same "
                                 "value. **Shard** — a (32, 64) variable becomes four chunks of "
                                 "(32, 16), one per device."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2",
            "title": "Variable paths, and the rule of thumb",
            "blocks": [
                {"t": "p", "md": "A **variable path** is a string identifier like "
                                 "`\"sequential/dense_1/kernel\"` — a way to refer to a variable "
                                 "without holding the instance. Print them all with:"},
                {"t": "code", "lang": "python", "src": """for v in model.variables:
    print(v.path)

# sequential/dense/kernel
# sequential/dense/bias
# sequential/dense_1/kernel
# sequential/dense_1/bias"""},
                {"t": "band", "md": "For a simple model, the go-to rule is: **shard the last "
                                    "dimension along the `\"model\"` axis, replicate everything "
                                    "else.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2",
            "title": "Writing the layout, and turning it on",
            "blocks": [
                {"t": "p", "md": "`None` means replicate along this dimension; a mesh axis name "
                                 "means shard across the devices of that axis."},
                {"t": "code", "lang": "python", "src": """layout_map = keras.distribution.LayoutMap(device_mesh)
layout_map["sequential/dense/kernel"] = (None, "model")
layout_map["sequential/dense/bias"] = ("model",)
layout_map["sequential/dense_1/kernel"] = (None, "model")
layout_map["sequential/dense_1/bias"] = ("model",)

model_parallel = keras.distribution.ModelParallel(
    layout_map=layout_map,
    batch_dim_name="data",
)
keras.distribution.set_distribution(model_parallel)"""},
                {"t": "p", "md": "Once the configuration is set, **no other part of your code "
                                 "changes** — the model definition and the training code are the "
                                 "same, whether you use `fit()` or your own loop."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2",
            "title": "This is the whole of large-scale training",
            "blocks": [
                {"t": "lead", "md": "Assuming the right `LayoutMap`, the few snippets you just "
                                    "saw are **enough to distribute any large language model "
                                    "training run** — scaling to as many devices as you have and "
                                    "to arbitrary model sizes."},
                {"t": "p", "md": "To check what actually happened, inspect the sharding:"},
                {"t": "out", "src": """>>> model.layers[0].kernel.value.sharding
NamedSharding(
    mesh=Mesh("data": 2, "model": 4),
    spec=PartitionSpec(None, "model")
)"""},
                {"t": "p", "md": "Or visualise it with `jax.debug.visualize_sharding(value.shape, "
                                 "value.sharding)`. **Verify the layout before you pay for a "
                                 "long run** — a silently wrong layout still trains, just "
                                 "slowly."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.2 · sidebar",
            "title": "tf.data performance under distribution",
            "blocks": [
                {"t": "bullets", "items": [
                    "Always provide data as a **`tf.data.Dataset`** for best performance. NumPy "
                    "arrays work too — `fit()` converts them to Datasets anyway.",
                    "Always **prefetch**: call `dataset.prefetch(buffer_size)` before passing to "
                    "`fit()`.",
                    "If unsure of the buffer size, use **`dataset.prefetch(tf.data.AUTOTUNE)`** "
                    "and let it choose.",
                ]},
                {"t": "p", "md": "The pattern is the same one chapter 8 introduced. It matters "
                                 "far more here: a starved input pipeline turns eight expensive "
                                 "GPUs into eight expensive idle GPUs."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.3",
            "title": "TPUs: fast enough to be worth the hoops",
            "blocks": [
                {"t": "p", "md": "There is a general trend toward hardware designed specifically "
                                 "for deep learning — **ASICs**, application-specific integrated "
                                 "circuits. The most prominent is Google's **Tensor Processing "
                                 "Unit**."},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "15×", "l": "TPU v2 against an NVIDIA P100"},
                    {"v": "3×", "l": "more cost-effective than GPU, on average"},
                ]},
                {"t": "p", "md": "TPU v2 is **free in Colab** (Runtime → Change Runtime Type). "
                                 "Google Cloud offers v3 through v5 for serious runs. With the "
                                 "JAX backend, all you need is the same "
                                 "`keras.distribution.set_distribution(...)` call — **before "
                                 "creating your model**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.2.3 · two TPU-specific gotchas",
            "title": "The data pipeline, and step fusing",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🚰", "h": "GCS read speed becomes the bottleneck", "style": "warn",
                     "p": "TPUs process batches extremely quickly. If the dataset is small "
                          "enough, call **`dataset.cache()`** so it is read from Cloud Storage "
                          "only once."},
                    {"ico": "🔗", "h": "Small models underutilize the TPU", "style": "warn",
                     "p": "Keeping the cores busy can demand batches **upward of 10,000 "
                          "samples**. And with enormous batches you must raise the learning rate "
                          "— fewer updates, each more accurate."},
                ]},
                {"t": "p", "md": "**Step fusing** is the way out: run several training steps per "
                                 "TPU execution, doing more work between round trips to VM "
                                 "memory."},
                {"t": "code", "lang": "python", "src": """model.compile(..., steps_per_execution=8)"""},
                {"t": "p", "md": "For a small model that underutilizes the TPU, this alone can "
                                 "be a **dramatic** speedup — and it changes nothing else about "
                                 "the training run."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "Lower-precision computation",
         "lead": "Up to 2× faster on almost any model, basically for free."},

        {
            "type": "slide",
            "kicker": "Section 18.3.1",
            "title": "Precision is to numbers what resolution is to images",
            "blocks": [
                {"t": "p", "md": "In mathematics the reals form a continuous axis — there are "
                                 "infinitely many points between any two numbers, and you can "
                                 "always zoom in. **In computer science this is not true.** "
                                 "There is a finite number of points between 3 and 4."},
                {"t": "mmd", "id": "ch18-float", "src": MMD_FLOAT,
                 "cap": "How many points depends on how many bits you store the number in."},
                {"t": "p", "md": "The practical way to think about it is the **smallest distance "
                                 "between two numbers you can safely process**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.1 · sidebar",
            "title": "Representable numbers are not uniformly spaced",
            "blocks": [
                {"t": "p", "md": "A counterintuitive fact: **larger numbers have lower "
                                 "precision.** There are as many representable values between "
                                 "2^N and 2^(N+1) as there are between 1 and 2, for any N."},
                {"t": "p", "md": "That falls out of the encoding — sign, mantissa, exponent:"},
                {"t": "out", "src": """{sign} * (2 ** ({exponent} - 127)) * 1.{mantissa}

Pi in float32:   sign 0 | exponent 10000000 | mantissa 10010010000111111011011
                        1 bit       8 bits             23 bits

value = +1 * (2 ** (128 - 127)) * 1.5707963705062866
value = 3.1415927410125732"""},
                {"t": "p", "md": "So the error incurred converting a number to floating point "
                                 "**varies with the value**, and tends to grow with its absolute "
                                 "magnitude."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.2",
            "title": "float16 inference: one line, nearly 2×",
            "blocks": [
                {"t": "p", "md": "Every model so far has used single precision — float32 weights, "
                                 "float32 computation. That is enough to run forward and backward "
                                 "without losing information, particularly for small gradient "
                                 "updates (learning rates around 1e-3, weight updates around "
                                 "1e-6)."},
                {"t": "p", "md": "Modern GPUs and TPUs have hardware that runs 16-bit operations "
                                 "**much faster and with less memory**."},
                {"t": "code", "lang": "python", "src": """import keras

keras.config.set_dtype_policy("float16")"""},
                {"t": "p", "md": "Set it **before you define your model**. Expect a nearly **2× "
                                 "speed boost** on `model.predict()` on GPU and TPU."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.2",
            "title": "float16 or bfloat16 — try both",
            "blocks": [
                {"t": "table",
                 "head": ["dtype", "float16", "bfloat16"],
                 "widths": [30, 35, 35],
                 "rows": [
                     ["Exponent bits", "5", "**8**"],
                     ["Mantissa bits", "**10**", "7"],
                     ["Sign bits", "1", "1"],
                     ["Character", "Finer resolution, narrower range",
                      "**Much wider range**, lower resolution"],
                 ]},
                {"t": "p", "md": "Table 18.1. `bfloat16` covers a far wider range of values at "
                                 "lower resolution over that range, and **works better on some "
                                 "devices, particularly TPUs**."},
                {"t": "band", "md": "Some devices are better optimised for one than the other, so "
                                    "==try both and settle for whichever turns out fastest==. It "
                                    "is a one-line experiment."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.3",
            "title": "Training in 16 bits does not work — so use both",
            "blocks": [
                {"t": "p", "md": "Setting the default to 16 bits is great for inference. For "
                                 "**training** there is a significant complication: gradient "
                                 "descent will not run smoothly, because gradient updates around "
                                 "1e-5 or 1e-6 — which are common — are not representable."},
                {"t": "p", "md": "**Mixed-precision training** is the hybrid: 16-bit computation "
                                 "where precision does not matter, 32-bit where numerical "
                                 "stability does — in particular for gradients and variable "
                                 "updates."},
                {"t": "code", "lang": "python", "src": """import keras

keras.config.set_dtype_policy("mixed_float16")"""},
                {"t": "p", "md": "**Most of the speed benefit of 16-bit, without meaningfully "
                                 "impacting model quality.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.3 · how it works",
            "title": "compute_dtype and variable_dtype",
            "blocks": [
                {"t": "mmd", "id": "ch18-mixed", "src": MMD_MIXED,
                 "cap": "Two dtypes per layer. Both default to float32; mixed precision changes "
                        "only the first."},
                {"t": "band", "md": "Some operations are **numerically unstable in float16** — "
                                    "notably softmax and crossentropy. To opt a specific layer "
                                    "out, pass `dtype=\"float32\"` to its constructor.",
                 "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.4",
            "title": "Loss scaling: multiply the loss so gradients survive",
            "blocks": [
                {"t": "p", "md": "Under mixed precision the gradients stay in float16, so the "
                                 "limited range can round small gradients **down to zero** — and "
                                 "the model stops learning."},
                {"t": "p", "md": "Gradient values are proportional to the loss, so the fix is "
                                 "simple: multiply the loss by a large scalar."},
                {"t": "code", "lang": "python", "src": """# a fixed factor
optimizer = keras.optimizers.Adam(learning_rate=1e-3, loss_scale_factor=10)

# or let the optimizer work it out
optimizer = keras.optimizers.LossScaleOptimizer(
    keras.optimizers.Adam(learning_rate=1e-3)
)"""},
                {"t": "p", "md": "**`LossScaleOptimizer` is usually the better option** — the "
                                 "right scaling value can change over the course of training."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.5",
            "title": "Why float8 is not simply the next step down",
            "blocks": [
                {"t": "p", "md": "float16 in the forward pass is **the last level of precision "
                                 "that just works** — enough bits for all intermediate tensors, "
                                 "with float32 reserved for gradient updates."},
                {"t": "p", "md": "At float8 that stops being true; you lose too much information. "
                                 "float8 is still usable in *some* computations, but it requires "
                                 "considerable modifications to the forward pass. **You cannot "
                                 "simply set `compute_dtype` to float8 and run.**"},
                {"t": "p", "md": "Keras has a built-in implementation targeting Transformers, "
                                 "covering only `Dense`, `EinsumDense`, and `Embedding`. It "
                                 "tracks past activation values to rescale activations each step "
                                 "so as to use the full float8 range, and overrides part of the "
                                 "backward pass to do the same for gradients."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.5 · when it pays",
            "title": "float8 can make your model slower",
            "blocks": [
                {"t": "band", "md": "That added machinery has a **computational cost**. If your "
                                    "model is too small or your GPU not powerful enough, the cost "
                                    "exceeds the benefit and you get a ==slowdown, not a "
                                    "speedup==.", "style": "rose"},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📏", "h": "Model size", "style": "warn",
                     "p": "Viable only for **very large** models, typically over **5 billion "
                          "parameters**."},
                    {"ico": "🖥", "h": "Hardware", "style": "warn",
                     "p": "Large, recent GPUs such as the **NVIDIA H100**."},
                ]},
                {"t": "p", "md": "**float8 is rarely used in practice**, except in foundation "
                                 "model training runs. Worth knowing exists; not worth reaching "
                                 "for."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.6",
            "title": "int8 quantization: a different trick",
            "blocks": [
                {"t": "p", "md": "Take an already-trained model with float32 weights and convert "
                                 "them to a lower-precision dtype — typically **int8** — while "
                                 "preserving the numerical correctness of the forward pass as "
                                 "far as possible."},
                {"t": "mmd", "id": "ch18-quant", "src": MMD_QUANT,
                 "cap": "matmul is linear, so the final unscaling cancels the initial scaling "
                        "exactly."},
                {"t": "p", "md": "Any loss of accuracy comes **only from the rounding** that "
                                 "happens when casting to int8 — not from the matmul itself."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.6 · abs-max scaling",
            "title": "Doing it by hand, once",
            "blocks": [
                {"t": "p", "md": "Casting naively would be destructive: "
                                 "`[[0.1, 0.9], [1.2, -0.8]]` becomes `[[0, 0], [1, 0]]`. So we "
                                 "spread each tensor across the full [-127, 127] range first."},
                {"t": "code", "lang": "python", "src": """from keras import ops

x = ops.array([[0.1, 0.9], [1.2, -0.8]])
kernel = ops.array([[-0.1, -2.2], [1.1, 0.7]])

def abs_max_quantize(value):
    abs_max = ops.max(ops.abs(value), keepdims=True)
    scale = ops.divide(127, abs_max + 1e-7)
    scaled_value = value * scale
    scaled_value = ops.clip(ops.round(scaled_value), -127, 127)
    scaled_value = ops.cast(scaled_value, dtype="int8")
    return scaled_value, scale

int_x, x_scale = abs_max_quantize(x)
int_kernel, kernel_scale = abs_max_quantize(kernel)"""},
                {"t": "p", "md": "`+ 1e-7` avoids dividing by zero. Rounding and clipping "
                                 "**before** casting is more accurate than casting directly."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.6",
            "title": "How accurate is it?",
            "blocks": [
                {"t": "p", "md": "Do the matmul in int8, then cast back and divide by the product "
                                 "of the two scales."},
                {"t": "code", "lang": "python", "src": """int_y = ops.matmul(int_x, int_kernel)
y = ops.cast(int_y, dtype="float32") / (x_scale * kernel_scale)"""},
                {"t": "out", "src": """>>> y
array([[ 0.9843736,  0.3933239],
       [-1.0151455, -3.1965137]])

>>> ops.matmul(x, kernel)
array([[ 0.98      ,  0.40999997],
       [-1.        , -3.2       ]])"""},
                {"t": "p", "md": "Accurate to about three decimal places. For a large matmul "
                                 "this saves a great deal of compute — int8 can be considerably "
                                 "faster than even float16 — and all we added were **fast "
                                 "elementwise ops**: abs, max, clip, cast, divide, multiply."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 18.3.6",
            "title": "In practice, one method call",
            "blocks": [
                {"t": "p", "md": "Nobody should implement quantization by hand. Like float8, int8 "
                                 "is built into `Dense`, `EinsumDense`, and `Embedding` — which "
                                 "unlocks int8 inference for **any Transformer-based model**."},
                {"t": "code", "lang": "python", "src": """model = ...
model.quantize("int8")
predictions = model.predict(...)"""},
                {"t": "p", "md": "`predict()` and `call()` now run partially in int8. **The "
                                 "weights are converted in place**, so this is a one-way "
                                 "operation on that model object — quantize a copy if you still "
                                 "need the float32 version."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Choosing between them",
            "title": "Which lever to pull, and when",
            "blocks": [
                {"t": "table",
                 "head": ["Technique", "What it buys", "What it costs"],
                 "widths": [26, 38, 36],
                 "rows": [
                     ["**Hyperparameter search**", "The last few points of accuracy",
                      "Hours to days of compute; validation-set overfitting risk"],
                     ["**Ensembling**", "More than any single model can reach",
                      "N× inference cost; needs genuinely diverse members"],
                     ["**Data parallelism**", "Up to ~7.3× on 8 GPUs",
                      "Model must fit on one device; large batches needed"],
                     ["**Model parallelism**", "Models that fit nowhere else",
                      "A LayoutMap to design and verify"],
                     ["**Mixed precision**", "Near 2× on training, nearly free",
                      "Loss scaling; unstable ops opted out by hand"],
                     ["**int8 quantization**", "Faster inference than float16",
                      "A small, measurable accuracy loss"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Common failure modes",
            "title": "Four ways this chapter goes wrong in practice",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "Tuning against the test set", "style": "bad",
                     "p": "Passing test data as `validation_data` to `search()`. Every number "
                          "you report afterwards is contaminated, and nothing warns you."},
                    {"ico": "👯", "h": "Ensembling identical models", "style": "bad",
                     "p": "Same architecture, different seeds. Low diversity, negligible gain, "
                          "N× the inference bill."},
                    {"ico": "⏰", "h": "set_distribution after model creation", "style": "warn",
                     "p": "It silently does nothing. Both `set_distribution` and "
                          "`set_dtype_policy` must come **before** the model exists."},
                    {"ico": "🕳", "h": "Mixed precision without loss scaling", "style": "warn",
                     "p": "Small gradients round to zero in float16 and the model quietly stops "
                          "learning. Use `LossScaleOptimizer`."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Hyperparameters cannot be learned by gradient descent** — the space is "
                    "discrete, the feedback expensive and noisy.",
                    "**KerasTuner replaces constants with ranges**; a tuner is a loop with a "
                    "strategy, and BayesianOptimization is the strategy worth defaulting to.",
                    "**Tuning is automation, not magic.** You still design the search space, and "
                    "your decisions graduate from micro to architectural.",
                    "**Validation-set overfitting is real**: tuning trains hyperparameters on "
                    "the validation data.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter (2 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**Ensembling works on diversity**, not on individual quality — a worse "
                    "model of a different kind can lift the whole ensemble.",
                    "**Data parallelism is for speed, model parallelism is for size.** JAX, "
                    "DeviceMesh, LayoutMap — and nothing else in your code changes.",
                    "**N GPUs do not give N× speedup**: about 7.3× on eight, and only if the "
                    "global batch keeps every device busy.",
                    "**Mixed precision is close to free**: float16 compute, float32 variables, "
                    "loss scaling to keep small gradients alive.",
                    "**float8 is not the next step down** — it needs a rewritten forward pass, "
                    "5B+ parameters, and recent hardware to pay for itself.",
                    "**int8 quantization** scales into [-127, 127], multiplies, and unscales — "
                    "and `model.quantize(\"int8\")` does it for you.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "04_mixed_precision_and_loss_scaling.ipynb",
                     "href": "../../course-slides/notebooks/ch18/04_mixed_precision_and_loss_scaling.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 19 — The future of AI",
                     "href": "../ch19/index.html"},
                ]},
            ],
        },
    ],
}
