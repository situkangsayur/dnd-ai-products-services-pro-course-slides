# -*- coding: utf-8 -*-
"""Chapter 7 notebooks — A Deep Dive on Keras."""

DECK = "ch07"

NOTEBOOKS = [
    {
        "file": "01_three_ways_to_build_a_model.ipynb",
        "title": "Sequential, Functional, and subclassing",
        "lede": "The same model three ways, and the concrete thing you lose when you "
                "give up the graph.",
        "needs": "CPU — about 2 minutes",
        "section": "01 — Three APIs for building models",
        "cells": [
            ("h2", "Sequential"),
            ("py", """import keras
from keras import layers

seq = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(10, activation="softmax"),
], name="sequential")

seq.build((None, 784))
seq.summary()"""),
            ("md",
             "A stack. One input, one output, no branches. It covers a great "
             "deal and it stops the moment you need two of anything."),

            ("h2", "Functional"),
            ("py", """inputs = keras.Input(shape=(784,), name="pixels")
x = layers.Dense(64, activation="relu")(inputs)
outputs = layers.Dense(10, activation="softmax")(x)
func = keras.Model(inputs, outputs, name="functional")
func.summary()"""),
            ("md",
             "Same model, written as a **graph of layers**. `keras.Input` is not "
             "a tensor of data — it is a description of the shape that will "
             "arrive, which is what lets Keras build and check the whole graph "
             "before any data exists."),

            ("h2", "Functional earns its keep with multiple inputs"),
            ("py", """import numpy as np

vocabulary_size, num_tags, num_departments = 10000, 100, 4

title = keras.Input(shape=(vocabulary_size,), name="title")
text_body = keras.Input(shape=(vocabulary_size,), name="text_body")
tags = keras.Input(shape=(num_tags,), name="tags")

features = layers.Concatenate()([title, text_body, tags])
features = layers.Dense(64, activation="relu")(features)

priority = layers.Dense(1, activation="sigmoid", name="priority")(features)
department = layers.Dense(num_departments, activation="softmax",
                          name="department")(features)

ticket = keras.Model(inputs=[title, text_body, tags],
                     outputs=[priority, department])
print(f"{len(ticket.inputs)} inputs, {len(ticket.outputs)} outputs, "
      f"{ticket.count_params():,} parameters")"""),
            ("py", """keras.utils.plot_model(ticket, "ticket_model.png",
                       show_shapes=True, rankdir="LR")
print("wrote ticket_model.png -- open it; this is the payoff")"""),
            ("note",
             "`plot_model` needs `pydot` and Graphviz. If it fails, "
             "`ticket.summary()` shows the same connectivity as a table — the "
             "*Connected to* column is the part Sequential cannot give you."),

            ("h2", "Subclassing"),
            ("py", """class CustomerTicketModel(keras.Model):
    def __init__(self, num_departments):
        super().__init__()
        self.concat_layer = layers.Concatenate()
        self.mixing_layer = layers.Dense(64, activation="relu")
        self.priority_scorer = layers.Dense(1, activation="sigmoid")
        self.department_classifier = layers.Dense(
            num_departments, activation="softmax")

    def call(self, inputs):
        title = inputs["title"]
        text_body = inputs["text_body"]
        tags = inputs["tags"]
        features = self.concat_layer([title, text_body, tags])
        features = self.mixing_layer(features)
        return (self.priority_scorer(features),
                self.department_classifier(features))

sub = CustomerTicketModel(num_departments=4)
print("Arbitrary Python is allowed in call() -- loops, conditionals, recursion.")"""),

            ("h2", "What subclassing costs"),
            ("py", """rng = np.random.default_rng(0)
data = {"title": rng.random((4, vocabulary_size)).astype("float32"),
        "text_body": rng.random((4, vocabulary_size)).astype("float32"),
        "tags": rng.random((4, num_tags)).astype("float32")}
_ = sub(data)

for name, m in [("functional", ticket), ("subclassed", sub)]:
    try:
        layer = m.get_layer(index=2)
        conn = "yes"
    except Exception:
        conn = "no"
    print(f"{name:12s} layers addressable by index: {conn}")

print("\\nfunctional model, connectivity is inspectable:")
print(" ", [t.shape for t in ticket.inputs], "->", [t.shape for t in ticket.outputs])
print("\\nsubclassed model: there is no graph. The forward pass is bytecode.")"""),
            ("md",
             "Three concrete losses, and they are not stylistic:\n\n"
             "- `summary()` cannot show connectivity, because there is none to "
             "show.\n"
             "- `plot_model()` cannot draw it.\n"
             "- **Feature extraction is impossible** — you cannot ask for the "
             "output of an intermediate layer, because layers are not nodes in "
             "anything.\n\n"
             "Chapter 10 depends entirely on that last capability. Subclass when "
             "the forward pass genuinely needs Python control flow; use the "
             "Functional API otherwise."),

            ("h2", "Mixing them"),
            ("py", """class Classifier(keras.Model):
    def __init__(self, num_classes=2):
        super().__init__()
        if num_classes == 2:
            self.dense = layers.Dense(1, activation="sigmoid")
        else:
            self.dense = layers.Dense(num_classes, activation="softmax")

    def call(self, inputs):
        return self.dense(inputs)

# A subclassed model used as a layer inside a functional one.
inputs = keras.Input(shape=(3,))
features = layers.Dense(64, activation="relu")(inputs)
outputs = Classifier(num_classes=10)(features)
mixed = keras.Model(inputs, outputs)
print("mixed model params:", mixed.count_params())"""),
            ("md",
             "They compose in both directions. **Use the least powerful API that "
             "does the job** — the capability you keep is inspectability, and it "
             "is worth more than it looks until the day you need it."),
        ],
        "takeaways": [
            "Sequential is a stack; Functional is a graph; subclassing is "
            "arbitrary Python.",
            "`keras.Input` describes a shape, not data — which is what allows "
            "static checking.",
            "Subclassing loses connectivity, `plot_model`, and **feature "
            "extraction**, which chapter 10 needs.",
            "The three compose freely. Use the least powerful one that works.",
        ],
    },

    {
        "file": "02_custom_metrics_and_callbacks.ipynb",
        "title": "Custom metrics, callbacks, and TensorBoard",
        "lede": "Metrics carry state across a whole epoch; callbacks let you interrupt "
                "the loop without rewriting it.",
        "needs": "CPU — about 2 minutes",
        "section": "02 — Metrics, callbacks, and monitoring",
        "cells": [
            ("h2", "A metric is a stateful object"),
            ("md",
             "A loss is computed per batch and thrown away. A metric has to "
             "report a number over the **whole epoch**, so it accumulates."),
            ("py", """import keras
from keras import ops
import numpy as np

class RootMeanSquaredError(keras.metrics.Metric):
    def __init__(self, name="rmse", **kwargs):
        super().__init__(name=name, **kwargs)
        self.mse_sum = self.add_weight(shape=(), initializer="zeros",
                                       name="mse_sum")
        self.total_samples = self.add_weight(shape=(), initializer="zeros",
                                             name="total_samples",
                                             dtype="int32")

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true = ops.one_hot(y_true, num_classes=ops.shape(y_pred)[1])
        mse = ops.sum(ops.square(y_true - y_pred))
        self.mse_sum.assign_add(mse)
        num_samples = ops.shape(y_pred)[0]
        self.total_samples.assign_add(num_samples)

    def result(self):
        return ops.sqrt(self.mse_sum / ops.cast(self.total_samples, "float32"))

    def reset_state(self):
        self.mse_sum.assign(0.)
        self.total_samples.assign(0)"""),
            ("md",
             "Three methods, and the third is the one people forget. Without "
             "`reset_state`, epoch two reports the running total from epoch one "
             "as well — a plausible number, quietly wrong."),

            ("h2", "Using it"),
            ("py", """from keras import layers
from keras.datasets import mnist

(x, y), (xt, yt) = mnist.load_data()
x = x.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

model = keras.Sequential([layers.Dense(64, activation="relu"),
                          layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy", RootMeanSquaredError()])
model.fit(x, y, epochs=3, batch_size=128, validation_split=.2, verbose=2)"""),

            ("h2", "The callbacks worth knowing"),
            ("py", """callbacks = [
    keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=2,
        restore_best_weights=True,      # otherwise you keep the WORST weights
    ),
    keras.callbacks.ModelCheckpoint(
        filepath="checkpoint.keras",
        monitor="val_loss",
        save_best_only=True,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=1, min_lr=1e-6,
    ),
]

model = keras.Sequential([layers.Dense(64, activation="relu"),
                          layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
h = model.fit(x, y, epochs=30, batch_size=128, validation_split=.2,
              callbacks=callbacks, verbose=2)
print(f"stopped after {len(h.history['loss'])} of 30 epochs")"""),
            ("warn",
             "`restore_best_weights=True`.** Without it, `EarlyStopping` leaves "
             "you holding the weights from the *last* epoch — which, by "
             "definition of why it stopped, are the worst ones it saw."),

            ("h2", "A callback of your own"),
            ("py", """import matplotlib.pyplot as plt

class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs=None):
        self.per_batch_losses = []

    def on_batch_end(self, batch, logs=None):
        self.per_batch_losses.append(logs["loss"])

    def on_epoch_end(self, epoch, logs=None):
        plt.figure(figsize=(7, 2.6))
        plt.plot(self.per_batch_losses, lw=.7)
        plt.title(f"per-batch loss through epoch {epoch}")
        plt.xlabel("batch"); plt.show()
        plt.close()

model = keras.Sequential([layers.Dense(64, activation="relu"),
                          layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy")
model.fit(x[:12000], y[:12000], epochs=2, batch_size=128,
          callbacks=[LossHistory()], verbose=0)"""),
            ("md",
             "Per-batch loss is far noisier than the per-epoch number `fit()` "
             "prints, and the noise is informative: a rising envelope means the "
             "learning rate is too high, long flat stretches mean it is too low."),

            ("h2", "TensorBoard"),
            ("py", """tb = keras.callbacks.TensorBoard(log_dir="./tb_logs")
model = keras.Sequential([layers.Dense(64, activation="relu"),
                          layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(x, y, epochs=3, batch_size=128, validation_split=.2,
          callbacks=[tb], verbose=0)
print("now run:  tensorboard --logdir ./tb_logs")"""),
            ("md",
             "Worth it once you are running more than a handful of experiments — "
             "which chapter 18 guarantees you will be."),
        ],
        "takeaways": [
            "A metric is stateful: `update_state`, `result`, and **`reset_state`**.",
            "`EarlyStopping` without `restore_best_weights` leaves you the worst "
            "weights it saw.",
            "Callbacks hook the loop at batch, epoch, and train boundaries "
            "without rewriting it.",
            "Per-batch loss shows problems the per-epoch average hides.",
        ],
    },

    {
        "file": "03_custom_train_step_per_backend.ipynb",
        "title": "Overriding train_step, and the backend-agnostic alternative",
        "lede": "How to change what one training step does — and why compute_loss() is "
                "usually the better place to do it.",
        "needs": "CPU — about 2 minutes",
        "section": "03 — Writing your own training logic",
        "cells": [
            ("h2", "The escape hatches, in order of how much they cost you"),
            ("md",
             "| What you override | What you keep | What it costs |\n"
             "|---|---|---|\n"
             "| `compute_loss()` | everything | nothing — **backend agnostic** |\n"
             "| `train_step()` | callbacks, metrics, progress | the code is "
             "backend-specific |\n"
             "| the whole loop | nothing | everything |\n\n"
             "Chapter 17's VAE and diffusion models both take the first option, "
             "for exactly this reason."),

            ("h2", "compute_loss(): the portable escape hatch"),
            ("py", """import keras
from keras import layers, ops
import numpy as np

class WeightedModel(keras.Model):
    \"\"\"Penalise mistakes on class 0 five times as heavily.\"\"\"

    def compute_loss(self, x=None, y=None, y_pred=None,
                     sample_weight=None, training=True):
        base = keras.losses.sparse_categorical_crossentropy(y, y_pred)
        weights = ops.where(ops.equal(y, 0), 5.0, 1.0)
        return ops.mean(base * weights)

inputs = keras.Input(shape=(784,))
h = layers.Dense(64, activation="relu")(inputs)
outputs = layers.Dense(10, activation="softmax")(h)
model = WeightedModel(inputs, outputs)

from keras.datasets import mnist
(x, y), (xt, yt) = mnist.load_data()
x = x.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

model.compile(optimizer="rmsprop", metrics=["accuracy"])
model.fit(x, y, epochs=2, batch_size=128, verbose=2)"""),
            ("md",
             "No `loss=` in `compile()` — the model supplies its own. This runs "
             "unchanged on all three backends, because nothing in it touches a "
             "gradient."),

            ("h2", "train_step(): where the backend leaks in"),
            ("md",
             "If you need the gradients themselves — to clip them, to accumulate "
             "them, to update two sets of weights alternately — you have to "
             "write backend-specific code. Here is the same idea three ways."),
            ("py", """# TensorFlow
class TFModel(keras.Model):
    def train_step(self, data):
        x, y = data
        import tensorflow as tf
        with tf.GradientTape() as tape:
            y_pred = self(x, training=True)
            loss = self.compute_loss(x=x, y=y, y_pred=y_pred)
        grads = tape.gradient(loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
        for m in self.metrics:
            m.update_state(y, y_pred)
        return {m.name: m.result() for m in self.metrics}"""),
            ("py", """# PyTorch
class TorchModel(keras.Model):
    def train_step(self, data):
        x, y = data
        self.zero_grad()
        y_pred = self(x, training=True)
        loss = self.compute_loss(x=x, y=y, y_pred=y_pred)
        loss.backward()
        trainable = [v for v in self.trainable_weights]
        grads = [v.value.grad for v in trainable]
        with torch.no_grad():
            self.optimizer.apply(grads, trainable)
        for m in self.metrics:
            m.update_state(y, y_pred)
        return {m.name: m.result() for m in self.metrics}"""),
            ("py", """# JAX -- stateless, so the signature is different entirely
class JaxModel(keras.Model):
    def train_step(self, state, data):
        x, y = data
        (trainable, non_trainable, optimizer_vars, metrics_vars) = state
        grad_fn = jax.value_and_grad(self.compute_loss_and_updates,
                                     has_aux=True)
        (loss, aux), grads = grad_fn(trainable, non_trainable, x, y)
        trainable, optimizer_vars = self.optimizer.stateless_apply(
            optimizer_vars, grads, trainable)
        return logs, (trainable, non_trainable, optimizer_vars, metrics_vars)"""),
            ("md",
             "Three genuinely different shapes, and the JAX one is not even the "
             "same signature. **This is the cost of overriding `train_step`** — "
             "and the reason chapter 17 goes out of its way to avoid it."),

            ("h2", "A real use: gradient clipping"),
            ("py", """# The common case has a built-in, no subclassing required.
model = keras.Sequential([layers.Dense(64, activation="relu"),
                          layers.Dense(10, activation="softmax")])
model.compile(
    optimizer=keras.optimizers.RMSprop(clipnorm=1.0),
    loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(x, y, epochs=1, batch_size=128, verbose=2)
print("clipnorm handled by the optimizer -- no custom train_step needed")"""),
            ("note",
             "Before writing a custom `train_step`, check whether the optimizer "
             "already takes the argument. `clipnorm`, `clipvalue`, "
             "`loss_scale_factor`, `use_ema`, and `weight_decay` all live there, "
             "and all of them are things people subclass to reimplement."),

            ("h2", "run_eagerly, for when it will not work"),
            ("py", """model.compile(optimizer="rmsprop",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"],
              run_eagerly=True)     # slow, but print() and pdb work
model.fit(x[:2000], y[:2000], epochs=1, batch_size=128, verbose=2)"""),
            ("md",
             "Compiled graphs do not run your `print` statements the way you "
             "expect and cannot be stepped through. `run_eagerly=True` makes "
             "debugging possible and training slow — **turn it on to find the "
             "bug, off before measuring anything.**"),
        ],
        "takeaways": [
            "Override `compute_loss()` when you can — it is portable across all "
            "three backends.",
            "Override `train_step()` only when you need the gradients "
            "themselves, and accept that it is backend-specific.",
            "Check the optimizer's arguments first; clipping, EMA and loss "
            "scaling are already there.",
            "`run_eagerly=True` to debug, off to measure.",
        ],
    },
]
