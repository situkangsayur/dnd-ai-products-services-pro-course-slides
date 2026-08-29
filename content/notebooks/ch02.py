# -*- coding: utf-8 -*-
"""Chapter 2 notebooks — The Mathematical Building Blocks of Neural Networks."""

DECK = "ch02"

NOTEBOOKS = [
    {
        "file": "01_first_mnist.ipynb",
        "title": "A first look at a neural network",
        "lede": "The book's opening example, run end to end in about twenty lines. "
                "The point is not the accuracy — it is that every line of it will "
                "be taken apart in the notebooks that follow.",
        "needs": "CPU — about 1 minute",
        "section": "01 — A first look at a neural network",
        "cells": [
            ("h2", "The data"),
            ("py", """import keras
from keras.datasets import mnist

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

print(train_images.shape, train_images.dtype)
print(train_labels[:10])
print(test_images.shape)"""),
            ("out", """(60000, 28, 28) uint8
[5 0 4 1 9 2 1 3 1 4]
(10000, 28, 28)"""),
            ("py", """import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 8, figsize=(11, 3))
for ax, img, lab in zip(axes.ravel(), train_images, train_labels):
    ax.imshow(img, cmap="gray_r")
    ax.set_title(int(lab), fontsize=10)
    ax.axis("off")
plt.tight_layout(); plt.show()"""),

            ("h2", "The model: two dense layers"),
            ("md",
             "Two `Dense` layers. The first re-represents the 784 pixels as 512 "
             "numbers; the second turns those into ten probabilities. Chapter 1 "
             "called this a search for a useful representation, and this is the "
             "smallest honest instance of it."),
            ("py", """from keras import layers

model = keras.Sequential([
    layers.Dense(512, activation="relu"),
    layers.Dense(10, activation="softmax"),
])

model.compile(
    optimizer="rmsprop",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)"""),

            ("h2", "Preparing the data"),
            ("md",
             "Two changes, both required. Flatten each 28×28 image into a 784-vector, "
             "and scale the `uint8` range [0, 255] into floats in [0, 1]."),
            ("py", """train_x = train_images.reshape((60000, 28 * 28)).astype("float32") / 255
test_x = test_images.reshape((10000, 28 * 28)).astype("float32") / 255

print(train_x.shape, train_x.dtype, train_x.min(), train_x.max())"""),
            ("out", "(60000, 784) float32 0.0 1.0"),

            ("h2", "Training"),
            ("py", """history = model.fit(train_x, train_labels, epochs=5, batch_size=128)"""),
            ("out", """Epoch 1/5
469/469 - 2s - loss: 0.2xxx - accuracy: 0.92xx
...
Epoch 5/5
469/469 - 2s - loss: 0.0xxx - accuracy: 0.98xx"""),

            ("h2", "Predicting, and evaluating"),
            ("py", """predictions = model.predict(test_x[:10], verbose=0)

print("first test digit, probability per class:")
for i, p in enumerate(predictions[0]):
    print(f"  {i}: {p:.4f}")
print("argmax:", predictions[0].argmax(), " label:", test_labels[0])"""),
            ("py", """test_loss, test_acc = model.evaluate(test_x, test_labels, verbose=0)
print(f"test accuracy: {test_acc:.4f}")
print(f"train accuracy at the last epoch: {history.history['accuracy'][-1]:.4f}")"""),
            ("out", """test accuracy: 0.97xx
train accuracy at the last epoch: 0.98xx"""),
            ("note",
             "Test accuracy is **lower** than training accuracy. That gap has a "
             "name — overfitting — and chapter 5 is entirely about it. Notice it "
             "here so that it is not a surprise there."),

            ("h2", "Looking at what it got wrong"),
            ("md",
             "A number on its own tells you very little. The mistakes tell you a "
             "great deal, and they cost nothing to look at."),
            ("py", """import numpy as np

probs = model.predict(test_x, verbose=0)
pred = probs.argmax(axis=1)
wrong = np.where(pred != test_labels)[0]
print(f"{len(wrong)} wrong out of {len(test_labels)}")

fig, axes = plt.subplots(2, 8, figsize=(11, 3.2))
for ax, i in zip(axes.ravel(), wrong[:16]):
    ax.imshow(test_images[i], cmap="gray_r")
    ax.set_title(f"{pred[i]} not {test_labels[i]}", fontsize=9)
    ax.axis("off")
plt.tight_layout(); plt.show()"""),
            ("md",
             "Most of them are digits you would hesitate over yourself. A few "
             "are not — and those are the ones worth understanding."),
        ],
        "takeaways": [
            "A working classifier is about twenty lines: data, two layers, "
            "compile, fit.",
            "Preprocessing is not optional — reshape and scale, every time.",
            "**Test accuracy below training accuracy is overfitting**, visible "
            "from the very first example.",
            "Always look at the errors. The number tells you how much; the "
            "errors tell you what.",
        ],
    },

    {
        "file": "02_tensors_and_operations.ipynb",
        "title": "Tensors, and the operations layers are made of",
        "lede": "Rank, shape, dtype; broadcasting; the dot product; and the geometric "
                "reading of what a Dense layer does to a space.",
        "needs": "CPU — under a minute",
        "section": "02 — Data representations and tensor operations",
        "cells": [
            ("h2", "Rank, shape, dtype"),
            ("py", """import numpy as np

scalar = np.array(12)
vector = np.array([12, 3, 6, 14, 7])
matrix = np.array([[5, 78, 2], [6, 79, 3], [7, 80, 4]])

for name, t in [("scalar", scalar), ("vector", vector), ("matrix", matrix)]:
    print(f"{name:8s} ndim={t.ndim}  shape={t.shape}  dtype={t.dtype}")"""),
            ("out", """scalar   ndim=0  shape=()  dtype=int64
vector   ndim=1  shape=(5,)  dtype=int64
matrix   ndim=2  shape=(3, 3)  dtype=int64"""),
            ("note",
             "A vector of five entries is a **5-dimensional vector** and a "
             "**rank-1 tensor**. Those two uses of *dimension* are different "
             "things and the confusion between them is worth killing early."),

            ("h2", "The shapes you will actually meet"),
            ("py", """from keras.datasets import mnist
(train_images, _), _ = mnist.load_data()

print("images     ", train_images.shape, "  (samples, height, width)")
print("timeseries ", (256, 200, 5), "  (samples, timesteps, features)")
print("video      ", (4, 120, 144, 256, 3), "  (samples, frames, h, w, channels)")"""),

            ("h2", "Slicing is how batches are made"),
            ("py", """batch = train_images[:128]
print("first batch:", batch.shape)

n = 3
print(f"batch {n}:", train_images[128 * n:128 * (n + 1)].shape)

# Axis 0 is always the samples axis. Every other axis belongs to one sample.
print("bottom-right quadrant of the first image:",
      train_images[0, 14:, 14:].shape)"""),

            ("h2", "Element-wise operations, written out and then not"),
            ("md",
             "`relu` and addition are element-wise. Written as loops they are "
             "clear and slow; NumPy dispatches the same thing to BLAS."),
            ("py", """def naive_relu(x):
    assert len(x.shape) == 2
    x = x.copy()
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            x[i, j] = max(x[i, j], 0)
    return x

import time
x = np.random.random((2000, 1000)) - 0.5

t0 = time.time(); naive_relu(x); slow = time.time() - t0
t0 = time.time(); np.maximum(x, 0.0); fast = time.time() - t0
print(f"loop:  {slow:.3f}s\\nnumpy: {fast:.5f}s\\nratio: {slow/fast:.0f}x")"""),
            ("out", "ratio: several hundred x"),

            ("h2", "Broadcasting"),
            ("md",
             "The smaller tensor is treated as if it were repeated along the "
             "missing axes — without actually being repeated, which is the "
             "point."),
            ("py", """X = np.random.random((32, 10))
b = np.random.random((10,))

print("X + b ->", (X + b).shape)

# What broadcasting is doing, made explicit:
B = np.tile(b[np.newaxis, :], (32, 1))
print("identical to the explicit tile:", np.allclose(X + b, X + B))"""),

            ("h2", "The dot product is the layer"),
            ("py", """def naive_matrix_vector_dot(x, y):
    z = np.zeros(x.shape[0])
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            z[i] += x[i, j] * y[j]
    return z

W = np.random.random((3, 4))
v = np.random.random((4,))
print(np.allclose(naive_matrix_vector_dot(W, v), W @ v))

# Shape compatibility is the only rule: (a, b) . (b, c) -> (a, c)
print((np.zeros((64, 3, 32, 10)) @ np.zeros((10, 7))).shape)"""),

            ("h2", "What a Dense layer does to a space"),
            ("md",
             "`output = relu(dot(input, W) + b)` is: a linear transform, a "
             "translation, then a fold. Here is that sequence applied to a grid, "
             "so the geometry is visible rather than asserted."),
            ("py", """import matplotlib.pyplot as plt

g = np.stack(np.meshgrid(np.linspace(-1, 1, 21), np.linspace(-1, 1, 21)), -1)
pts = g.reshape(-1, 2)

W2 = np.array([[1.2, -0.7], [0.5, 1.1]])
b2 = np.array([0.15, -0.25])

stages = [
    ("input", pts),
    ("dot(x, W)", pts @ W2),
    ("+ b", pts @ W2 + b2),
    ("relu(...)", np.maximum(pts @ W2 + b2, 0)),
]

fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
for ax, (name, p) in zip(axes, stages):
    ax.scatter(p[:, 0], p[:, 1], s=5, c=np.arctan2(pts[:, 1], pts[:, 0]), cmap="twilight")
    ax.set_title(name); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.show()"""),
            ("md",
             "The last panel is the one that matters: `relu` **collapses** a "
             "whole region onto the axes. That is the nonlinearity, and it is "
             "why stacking layers buys you something that one layer cannot do."),
        ],
        "takeaways": [
            "Rank, shape, and dtype describe every tensor you will meet; axis 0 "
            "is always the samples axis.",
            "Element-wise operations, broadcasting, and the dot product are the "
            "whole vocabulary of a Dense layer.",
            "Broadcasting repeats **conceptually**, not in memory.",
            "A layer is an affine transform followed by a fold — geometry, not "
            "magic.",
        ],
    },

    {
        "file": "03_gradients_and_sgd.ipynb",
        "title": "Derivatives, gradients, and stochastic gradient descent",
        "lede": "Why a differentiable loss makes learning tractable, and what "
                "backpropagation is doing when Keras calls fit().",
        "needs": "CPU — about 1 minute",
        "section": "03 — The engine of neural networks",
        "cells": [
            ("h2", "A derivative, numerically and then exactly"),
            ("py", """import numpy as np

f = lambda x: x ** 2 + 3 * x + 1
df_exact = lambda x: 2 * x + 3

x0, eps = 2.0, 1e-6
numeric = (f(x0 + eps) - f(x0)) / eps
print(f"numeric: {numeric:.6f}   exact: {df_exact(x0):.6f}")"""),
            ("md",
             "The derivative says: *move x a little, and f moves this much, in "
             "this direction*. Learning is nothing more than using that to "
             "decide which way to move."),

            ("h2", "Gradient descent by hand"),
            ("py", """import matplotlib.pyplot as plt

x = 4.0
lr = 0.15
path = [x]
for _ in range(25):
    x = x - lr * df_exact(x)
    path.append(x)

xs = np.linspace(-6, 5, 300)
plt.figure(figsize=(6, 4))
plt.plot(xs, f(xs), lw=1.5)
plt.plot(path, [f(p) for p in path], "o-", ms=4, lw=.8, color="#c0392b")
plt.title(f"25 steps, lr={lr}  ->  x = {x:.4f} (minimum at -1.5)")
plt.show()"""),

            ("h2", "The learning rate is the whole story"),
            ("md",
             "Chapter 3 will show this again with a real model. It is cheaper "
             "to learn it here, on a parabola, where nothing takes two minutes "
             "to fail."),
            ("py", """fig, axes = plt.subplots(1, 3, figsize=(13, 3.4))
for ax, lr in zip(axes, [0.02, 0.15, 0.95]):
    x, path = 4.0, [4.0]
    for _ in range(25):
        x = x - lr * df_exact(x)
        path.append(x)
    ax.plot(xs, f(xs), lw=1.2)
    ax.plot(path, [f(p) for p in path], "o-", ms=3.5, lw=.8, color="#c0392b")
    ax.set_title(f"lr = {lr}  ->  {x:.3f}")
    ax.set_ylim(-2, 40)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Too small and it never arrives. Too large and it oscillates or "
             "diverges. **There is no correct value in the abstract** — only one "
             "that suits the curvature of the surface you happen to be on."),

            ("h2", "A gradient: the same idea in many dimensions"),
            ("py", """import keras
from keras import ops

# Keras 3 exposes autodiff through the backend; here is the shape of it.
import tensorflow as tf

W = tf.Variable(tf.random.normal((2, 1)))
b = tf.Variable(tf.zeros((1,)))
X = tf.random.normal((64, 2))
y = X @ tf.constant([[2.0], [-3.0]]) + 0.5

with tf.GradientTape() as tape:
    pred = X @ W + b
    loss = tf.reduce_mean(tf.square(pred - y))

gW, gb = tape.gradient(loss, [W, b])
print("loss:", float(loss))
print("dL/dW:", gW.numpy().ravel())
print("dL/db:", gb.numpy())"""),
            ("md",
             "`tape.gradient` is backpropagation. It applies the chain rule "
             "backwards through every operation recorded in the block above it "
             "— which is why the loss has to be **differentiable**, and why that "
             "constraint reappears in chapter 19 as a limitation rather than a "
             "detail."),

            ("h2", "Full-batch, mini-batch, and stochastic"),
            ("py", """def descend(batch_size, steps=120, lr=0.08, seed=0):
    rng = np.random.default_rng(seed)
    Xd = rng.normal(size=(512, 2))
    yd = Xd @ np.array([2.0, -3.0]) + 0.5 + rng.normal(scale=.3, size=512)
    w = np.zeros(2); bb = 0.0; hist = []
    for s in range(steps):
        idx = rng.choice(len(Xd), size=batch_size, replace=False)
        xb, yb = Xd[idx], yd[idx]
        err = xb @ w + bb - yb
        w -= lr * (2 * xb.T @ err / len(xb))
        bb -= lr * (2 * err.mean())
        hist.append(((Xd @ w + bb - yd) ** 2).mean())
    return hist

plt.figure(figsize=(7, 4))
for bs, label in [(1, "stochastic (1)"), (32, "mini-batch (32)"), (512, "full batch")]:
    plt.plot(descend(bs), lw=1.3, label=label)
plt.yscale("log"); plt.xlabel("step"); plt.ylabel("full-dataset MSE")
plt.legend(); plt.title("Batch size trades noise against cost per step")
plt.show()"""),
            ("md",
             "Full batch gives the smoothest curve and the most expensive step. "
             "Stochastic is noisy and cheap. **Mini-batch is neither, on "
             "purpose**, and it is what every model in this course uses."),
        ],
        "takeaways": [
            "A derivative tells you which way to move; gradient descent does "
            "nothing else.",
            "The learning rate has no correct value in the abstract — too small "
            "stalls, too large diverges.",
            "Backpropagation is the chain rule applied backwards over recorded "
            "operations, which is why the whole chain must be differentiable.",
            "Batch size trades gradient noise against cost per step; mini-batch "
            "is the deliberate middle.",
        ],
    },

    {
        "file": "04_mnist_from_scratch.ipynb",
        "title": "Reimplementing the first example from scratch",
        "lede": "A Dense layer, a Sequential model, a batch generator, and a training "
                "step — written by hand, then checked against Keras. Nothing here is "
                "how you should work; everything here is what fit() is doing.",
        "needs": "CPU — about 2 minutes",
        "section": "04 — Looking back at our first example",
        "cells": [
            ("h2", "A Dense layer, by hand"),
            ("py", """import tensorflow as tf
import numpy as np

class NaiveDense:
    def __init__(self, input_size, output_size, activation):
        self.activation = activation
        w_shape = (input_size, output_size)
        w_initial = tf.random.uniform(w_shape, minval=0, maxval=1e-1)
        self.W = tf.Variable(w_initial)
        self.b = tf.Variable(tf.zeros((output_size,)))

    def __call__(self, inputs):
        return self.activation(tf.matmul(inputs, self.W) + self.b)

    @property
    def weights(self):
        return [self.W, self.b]"""),
            ("md",
             "Three lines of substance: a matrix multiply, an addition, an "
             "activation. Everything else is bookkeeping."),

            ("h2", "A Sequential model, by hand"),
            ("py", """class NaiveSequential:
    def __init__(self, layers):
        self.layers = layers

    def __call__(self, inputs):
        x = inputs
        for layer in self.layers:
            x = layer(x)
        return x

    @property
    def weights(self):
        return [w for layer in self.layers for w in layer.weights]

model = NaiveSequential([
    NaiveDense(28 * 28, 512, activation=tf.nn.relu),
    NaiveDense(512, 10, activation=tf.nn.softmax),
])
assert len(model.weights) == 4
print(f"{sum(int(np.prod(w.shape)) for w in model.weights):,} parameters")"""),
            ("out", "407,050 parameters"),

            ("h2", "A batch generator"),
            ("py", """class BatchGenerator:
    def __init__(self, images, labels, batch_size=128):
        assert len(images) == len(labels)
        self.index = 0
        self.images = images
        self.labels = labels
        self.batch_size = batch_size
        self.num_batches = math.ceil(len(images) / batch_size)

    def next(self):
        images = self.images[self.index:self.index + self.batch_size]
        labels = self.labels[self.index:self.index + self.batch_size]
        self.index += self.batch_size
        return images, labels

import math"""),

            ("h2", "One training step"),
            ("md",
             "Forward pass under a tape, loss, gradients, update. **This is the "
             "whole of `fit()`**, minus callbacks, metrics, and every "
             "convenience."),
            ("py", """learning_rate = 1e-3

def update_weights(gradients, weights):
    for g, w in zip(gradients, weights):
        w.assign_sub(g * learning_rate)

def one_training_step(model, images_batch, labels_batch):
    with tf.GradientTape() as tape:
        predictions = model(images_batch)
        per_sample_losses = tf.keras.losses.sparse_categorical_crossentropy(
            labels_batch, predictions
        )
        average_loss = tf.reduce_mean(per_sample_losses)
    gradients = tape.gradient(average_loss, model.weights)
    update_weights(gradients, model.weights)
    return average_loss"""),
            ("note",
             "`w.assign_sub(g * lr)` is the entire optimizer. Replace this one "
             "line and you have SGD with momentum, or RMSprop, or Adam — that "
             "is genuinely the only difference between them."),

            ("h2", "The training loop"),
            ("py", """def fit(model, images, labels, epochs, batch_size=128):
    for epoch_counter in range(epochs):
        print(f"Epoch {epoch_counter}")
        batch_generator = BatchGenerator(images, labels, batch_size)
        for batch_counter in range(batch_generator.num_batches):
            images_batch, labels_batch = batch_generator.next()
            loss = one_training_step(model, images_batch, labels_batch)
            if batch_counter % 100 == 0:
                print(f"  loss at batch {batch_counter}: {loss:.2f}")

from keras.datasets import mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images.reshape((60000, 28 * 28)).astype("float32") / 255
test_images = test_images.reshape((10000, 28 * 28)).astype("float32") / 255

fit(model, train_images, train_labels, epochs=10, batch_size=128)"""),
            ("out", """Epoch 0
  loss at batch 0: 5.02
  loss at batch 100: 2.23
  ...
Epoch 9
  loss at batch 400: 0.19"""),

            ("h2", "Did it work?"),
            ("py", """predictions = model(test_images).numpy()
predicted_labels = np.argmax(predictions, axis=1)
matches = predicted_labels == test_labels
print(f"accuracy: {matches.mean():.3f}")"""),
            ("out", "accuracy: 0.81 — 0.83"),
            ("md",
             "Around 82%, against 97% from the Keras version in notebook 01. "
             "**Same architecture, same data.** The difference is the "
             "optimizer — plain SGD at a fixed 1e-3, against RMSprop — and it "
             "is a fifteen-point difference.\n\n"
             "That is a useful number to carry: the parts of Keras that look "
             "like convenience are frequently not."),

            ("h2", "Checking one gradient against Keras"),
            ("py", """import keras
from keras import layers

kmodel = keras.Sequential([layers.Dense(4, activation="relu"),
                           layers.Dense(3, activation="softmax")])
xb = tf.random.normal((8, 5))
yb = tf.constant([0, 1, 2, 0, 1, 2, 0, 1])

with tf.GradientTape() as tape:
    loss = tf.reduce_mean(
        keras.losses.sparse_categorical_crossentropy(yb, kmodel(xb))
    )
g = tape.gradient(loss, kmodel.trainable_weights)
print("gradient shapes:", [tuple(t.shape) for t in g])
print("finite:", all(bool(tf.reduce_all(tf.math.is_finite(t))) for t in g))"""),
            ("md",
             "Same mechanism, same tape. Keras is not doing anything else — it "
             "is doing this, with the loop, the metrics, and the callbacks "
             "written for you."),
        ],
        "takeaways": [
            "`fit()` is a batch generator, a gradient tape, and one "
            "`assign_sub` per weight.",
            "The optimizer is one line, and swapping it is worth fifteen points "
            "of accuracy here.",
            "Writing it by hand once is what makes the framework legible "
            "afterwards.",
            "You should never work this way — but you should know exactly what "
            "you are calling.",
        ],
    },
]
