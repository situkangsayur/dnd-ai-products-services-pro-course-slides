# -*- coding: utf-8 -*-
"""Chapter 3 notebooks — TensorFlow, PyTorch, JAX, and Keras."""

DECK = "ch03"

NOTEBOOKS = [
    {
        "file": "01_three_frameworks_side_by_side.ipynb",
        "title": "The same twenty lines, in three frameworks",
        "lede": "A linear classifier trained from scratch in TensorFlow, PyTorch, and "
                "JAX. Reading the three side by side is the fastest way to see what "
                "is essential and what is dialect.",
        "needs": "CPU — 2 minutes. Only the backend you have installed will run; "
                 "read the others.",
        "section": "02 — The three frameworks",
        "cells": [
            ("h2", "The problem, once"),
            ("py", """import numpy as np

num_samples_per_class = 1000
negative_samples = np.random.multivariate_normal(
    mean=[0, 3], cov=[[1, 0.5], [0.5, 1]], size=num_samples_per_class)
positive_samples = np.random.multivariate_normal(
    mean=[3, 0], cov=[[1, 0.5], [0.5, 1]], size=num_samples_per_class)

inputs = np.vstack((negative_samples, positive_samples)).astype("float32")
targets = np.vstack((np.zeros((num_samples_per_class, 1), dtype="float32"),
                     np.ones((num_samples_per_class, 1), dtype="float32")))

import matplotlib.pyplot as plt
plt.figure(figsize=(5, 5))
plt.scatter(inputs[:, 0], inputs[:, 1], c=targets[:, 0], s=8, cmap="coolwarm")
plt.gca().set_aspect("equal"); plt.title("Two Gaussian blobs"); plt.show()"""),

            ("h2", "TensorFlow: a tape, and assign_sub"),
            ("py", """import tensorflow as tf

W = tf.Variable(initial_value=tf.random.uniform(shape=(2, 1)))
b = tf.Variable(initial_value=tf.zeros(shape=(1,)))

def model(x):
    return tf.matmul(x, W) + b

def mean_squared_error(targets, predictions):
    return tf.reduce_mean(tf.square(targets - predictions))

learning_rate = 0.1

def training_step(inputs, targets):
    with tf.GradientTape() as tape:
        predictions = model(inputs)
        loss = mean_squared_error(targets, predictions)
    grad_loss_wrt_W, grad_loss_wrt_b = tape.gradient(loss, [W, b])
    W.assign_sub(grad_loss_wrt_W * learning_rate)
    b.assign_sub(grad_loss_wrt_b * learning_rate)
    return loss

for step in range(40):
    loss = training_step(inputs, targets)
    if step % 10 == 0:
        print(f"step {step:3d}  loss {float(loss):.4f}")"""),
            ("out", """step   0  loss 3.xxxx
step  10  loss 0.0xxx
step  20  loss 0.0xxx
step  30  loss 0.0xxx"""),

            ("h2", "PyTorch: backward(), and no_grad()"),
            ("py", """import torch

W_t = torch.rand(2, 1, requires_grad=True)
b_t = torch.zeros(1, requires_grad=True)

x_t = torch.tensor(inputs)
y_t = torch.tensor(targets)

for step in range(40):
    predictions = torch.matmul(x_t, W_t) + b_t
    loss = torch.mean(torch.square(y_t - predictions))
    loss.backward()                     # gradients accumulate onto .grad
    with torch.no_grad():               # the update is not part of the graph
        W_t -= W_t.grad * 0.1
        b_t -= b_t.grad * 0.1
        W_t.grad.zero_()                # ...and must be cleared, every step
        b_t.grad.zero_()
    if step % 10 == 0:
        print(f"step {step:3d}  loss {float(loss):.4f}")"""),
            ("warn",
             "The two lines people forget.** `no_grad()` around the update, and "
             "`grad.zero_()` after it. Omit the second and gradients accumulate "
             "across steps — the model still trains, badly, with no error."),

            ("h2", "JAX: no state at all"),
            ("py", """import jax
import jax.numpy as jnp

def compute_loss(state, inputs, targets):
    W, b = state
    predictions = jnp.matmul(inputs, W) + b
    return jnp.mean(jnp.square(targets - predictions))

grad_fn = jax.jit(jax.value_and_grad(compute_loss))

state = (jnp.array(np.random.uniform(size=(2, 1)), dtype="float32"),
         jnp.zeros((1,), dtype="float32"))

for step in range(40):
    loss, grads = grad_fn(state, inputs, targets)
    state = tuple(p - g * 0.1 for p, g in zip(state, grads))
    if step % 10 == 0:
        print(f"step {step:3d}  loss {float(loss):.4f}")"""),
            ("md",
             "No variables, no in-place mutation, no `.grad` to clear. "
             "`value_and_grad` turns a **function** into another function, and "
             "`jit` compiles it. Chapter 18 recommends JAX for distributed "
             "training, and this slide is why: there is no hidden state to "
             "shard."),

            ("h2", "What was the same"),
            ("md",
             "| | TensorFlow | PyTorch | JAX |\n"
             "|---|---|---|---|\n"
             "| gradients | `tape.gradient` | `loss.backward()` | "
             "`jax.grad` |\n"
             "| state | `tf.Variable` | tensors with `requires_grad` | "
             "**none — passed in** |\n"
             "| update | `assign_sub` | in place under `no_grad` | build a new "
             "tuple |\n"
             "| clearing | not needed | **`grad.zero_()`** | not applicable |\n\n"
             "The forward pass and the loss are identical in all three. "
             "**Everything that differs is state management.**"),
        ],
        "takeaways": [
            "The maths is the same in all three; the differences are entirely "
            "about where state lives.",
            "TensorFlow records on a tape; PyTorch accumulates onto `.grad`; "
            "JAX transforms pure functions.",
            "PyTorch's `zero_()` is a silent-failure trap worth knowing before "
            "you meet it.",
            "JAX's statelessness is the reason chapter 18 prefers it for "
            "distributed training.",
        ],
    },

    {
        "file": "02_keras3_switch_backend.ipynb",
        "title": "One model, three backends",
        "lede": "Keras 3 runs the same model on any of the three. This notebook trains "
                "it on each in turn and checks that the numbers agree — which is the "
                "claim worth verifying rather than assuming.",
        "needs": "CPU — 3 minutes if all three backends are installed",
        "section": "03 — Keras 3 and the backend switch",
        "cells": [
            ("h2", "Choosing the backend"),
            ("warn",
             "This must happen before `import keras`.** The backend is read at "
             "import time; setting it afterwards silently does nothing."),
            ("py", """import os
os.environ["KERAS_BACKEND"] = "tensorflow"   # or "torch", or "jax"

import keras
print("keras", keras.__version__, "on", keras.backend.backend())"""),

            ("h2", "keras.ops: NumPy, dispatched"),
            ("py", """from keras import ops
import numpy as np

x = ops.array(np.linspace(-3, 3, 7, dtype="float32"))
print("relu   ", ops.relu(x))
print("softmax", ops.softmax(x))
print("mean   ", float(ops.mean(x)))
print("type   ", type(x))"""),
            ("md",
             "The returned type is the **backend's** tensor type — a "
             "`tf.Tensor`, a `torch.Tensor`, or a `jax.Array` — while the API "
             "you wrote against is the same. That is the whole trick."),

            ("h2", "A model that does not know which backend it is on"),
            ("py", """from keras import layers
from keras.datasets import mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(-1, 784).astype("float32") / 255
x_test = x_test.reshape(-1, 784).astype("float32") / 255

def build():
    keras.utils.set_random_seed(1337)
    m = keras.Sequential([
        layers.Dense(128, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ])
    m.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

model = build()
model.fit(x_train, y_train, epochs=2, batch_size=128, verbose=2)
loss, acc = model.evaluate(x_test, y_test, verbose=0)
print(f"{keras.backend.backend():12s} test accuracy {acc:.4f}")"""),
            ("out", "tensorflow   test accuracy 0.96xx"),

            ("h2", "Running the comparison"),
            ("md",
             "A backend cannot be changed inside a live process. To compare, run "
             "this notebook three times — or drive it from the shell:"),
            ("py", """script = '''
import os, sys
os.environ["KERAS_BACKEND"] = sys.argv[1]
import keras
from keras import layers
from keras.datasets import mnist

(x, y), (xt, yt) = mnist.load_data()
x = x.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

keras.utils.set_random_seed(1337)
m = keras.Sequential([layers.Dense(128, activation="relu"),
                      layers.Dense(10, activation="softmax")])
m.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
          metrics=["accuracy"])
m.fit(x, y, epochs=2, batch_size=128, verbose=0)
print(sys.argv[1], m.evaluate(xt, yt, verbose=0)[1])
'''
open("_backend_check.py", "w").write(script)
print("now run, in a terminal:")
for b in ["tensorflow", "torch", "jax"]:
    print(f"  python3 _backend_check.py {b}")"""),
            ("note",
             "Expect the three accuracies to agree to about two decimal places, "
             "not exactly. Random number generators differ across backends even "
             "under the same seed, and float reductions are not associative — "
             "**the same computation in a different order is a different "
             "number.**"),

            ("h2", "Saving on one, loading on another"),
            ("py", """model.save("mnist_mlp.keras")

reloaded = keras.saving.load_model("mnist_mlp.keras")
print("reloaded on:", keras.backend.backend())
print("same accuracy:", reloaded.evaluate(x_test, y_test, verbose=0)[1])"""),
            ("md",
             "The `.keras` format is backend-independent. Train under "
             "TensorFlow, serve under PyTorch — this is the practical payoff of "
             "the abstraction, and the reason chapter 18 can recommend switching "
             "to JAX for one phase of a project without rewriting the model."),
        ],
        "takeaways": [
            "`KERAS_BACKEND` must be set **before** `import keras`.",
            "`keras.ops` is a NumPy-shaped API that dispatches to the backend's "
            "own tensors.",
            "Results agree across backends to about two decimals, not exactly — "
            "different RNGs, different reduction orders.",
            "`.keras` files move between backends, which is what makes the "
            "abstraction worth having.",
        ],
    },

    {
        "file": "03_custom_layer_and_fit.ipynb",
        "title": "Writing a layer, and letting fit() drive it",
        "lede": "A Dense layer written as a keras.Layer subclass — build(), call(), "
                "and the lazy weight creation that makes input shapes optional.",
        "needs": "CPU — about 1 minute",
        "section": "04 — Layers, models, and the training loop",
        "cells": [
            ("h2", "The layer"),
            ("py", """import keras
from keras import ops

class SimpleDense(keras.Layer):
    def __init__(self, units, activation=None):
        super().__init__()
        self.units = units
        self.activation = activation

    def build(self, input_shape):
        # Called on the first invocation, once the input shape is known.
        # This is why you never have to declare input sizes in Keras.
        input_dim = input_shape[-1]
        self.W = self.add_weight(
            shape=(input_dim, self.units),
            initializer="glorot_uniform",
            name="kernel",
        )
        self.b = self.add_weight(
            shape=(self.units,), initializer="zeros", name="bias",
        )

    def call(self, inputs):
        y = ops.matmul(inputs, self.W) + self.b
        if self.activation is not None:
            y = self.activation(y)
        return y"""),

            ("h2", "Weights appear on first call, not on construction"),
            ("py", """layer = SimpleDense(units=32, activation=ops.relu)
print("weights before any call:", len(layer.weights))

import numpy as np
out = layer(np.random.random((2, 784)).astype("float32"))
print("weights after one call: ", len(layer.weights))
print("output shape:           ", out.shape)
print("kernel shape:           ", layer.W.shape)"""),
            ("out", """weights before any call: 0
weights after one call:  2
output shape:            (2, 32)
kernel shape:            (784, 32)"""),
            ("md",
             "This is *lazy building*, and it is why a Keras model can be "
             "written without ever stating an input size. The shape arrives "
             "with the first batch."),

            ("h2", "Composing them"),
            ("py", """from keras.datasets import mnist

model = keras.Sequential([
    SimpleDense(512, activation=ops.relu),
    SimpleDense(10, activation=ops.softmax),
])

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(-1, 784).astype("float32") / 255
x_test = x_test.reshape(-1, 784).astype("float32") / 255

model.compile(optimizer="rmsprop",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(x_train, y_train, epochs=3, batch_size=128, verbose=2)
print("test:", model.evaluate(x_test, y_test, verbose=0))"""),
            ("md",
             "A layer you wrote, driven by `fit()` you did not. Everything "
             "Keras offers — callbacks, metrics, validation splits, the "
             "progress bar — works because `SimpleDense` implements the two "
             "methods the framework asks for."),

            ("h2", "What compile() actually stores"),
            ("py", """print("optimizer:", model.optimizer.__class__.__name__)
print("loss:     ", model.loss)
print("metrics:  ", [m.name for m in model.metrics])
print("trainable weights:", len(model.trainable_weights))
print("total params:", model.count_params())"""),
            ("note",
             "`compile()` does not compute anything. It records three "
             "decisions — how to measure wrongness, how to move the weights, "
             "and what else to report — and `fit()` reads them back."),
        ],
        "takeaways": [
            "A layer needs `build()` and `call()`; everything else is inherited.",
            "Weights are created lazily on first call, which is why input shapes "
            "are optional.",
            "`compile()` records three decisions; `fit()` executes them.",
            "Custom layers get the whole framework for free — callbacks, "
            "metrics, validation.",
        ],
    },
]
