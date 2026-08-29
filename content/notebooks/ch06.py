# -*- coding: utf-8 -*-
"""Chapter 6 notebooks — The Universal Workflow of Machine Learning."""

DECK = "ch06"

NOTEBOOKS = [
    {
        "file": "01_understand_data_before_modelling.ipynb",
        "title": "Looking at the data before building anything",
        "lede": "The step that gets skipped, done properly once: class balance, "
                "duplicates, leakage candidates, and a common-sense baseline — all "
                "before a single layer is written.",
        "needs": "CPU — about 2 minutes",
        "section": "01 — Define the task",
        "cells": [
            ("h2", "The dataset"),
            ("py", """import numpy as np
import pandas as pd
from keras.datasets import reuters

(train_data, train_labels), (test_data, test_labels) = reuters.load_data(
    num_words=10000)

print(f"train {len(train_data)}   test {len(test_data)}")
print(f"classes: {len(set(train_labels))}")
print(f"sequence length: min {min(map(len, train_data))}, "
      f"median {int(np.median([len(s) for s in train_data]))}, "
      f"max {max(map(len, train_data))}")"""),

            ("h2", "Class balance"),
            ("py", """import matplotlib.pyplot as plt

counts = np.bincount(train_labels)
order = counts.argsort()[::-1]

plt.figure(figsize=(10, 3.4))
plt.bar(range(len(counts)), counts[order])
plt.xlabel("class (sorted by frequency)"); plt.ylabel("samples")
plt.title("Severely imbalanced — the top class is a third of the data")
plt.show()

print(f"largest class: {counts.max()} samples ({counts.max()/len(train_labels):.1%})")
print(f"smallest class: {counts.min()} samples")
print(f"classes with fewer than 20 samples: {(counts < 20).sum()}")"""),
            ("md",
             "**This changes the metric.** Plain accuracy on a dataset where one "
             "class is 36% of the data rewards a model that ignores the tail "
             "entirely. Chapter 6's rule — choose a measure of success that "
             "reflects what you actually want — starts here, not after training."),

            ("h2", "Duplicates and near-duplicates"),
            ("py", """as_tuples = [tuple(s) for s in train_data]
unique = len(set(as_tuples))
print(f"{len(as_tuples) - unique} exact duplicates in the training set")

# Also check across the train/test boundary -- the leak that matters.
train_set = set(as_tuples)
cross = sum(1 for s in test_data if tuple(s) in train_set)
print(f"{cross} test samples appear verbatim in training")"""),
            ("warn",
             "Any nonzero number on the second line invalidates the test "
             "score.** Deduplicate across the split, not just within it."),

            ("h2", "Sequence length, and what it implies for preprocessing"),
            ("py", """lengths = np.array([len(s) for s in train_data])

plt.figure(figsize=(7, 3.6))
plt.hist(lengths, bins=80)
for q in [0.5, 0.9, 0.99]:
    v = np.quantile(lengths, q)
    plt.axvline(v, ls="--", lw=1, label=f"{q:.0%} at {int(v)}")
plt.xlabel("tokens"); plt.legend(); plt.title("Sequence length distribution")
plt.show()"""),
            ("md",
             "Truncating at the median throws away half of half the documents. "
             "Truncating at the 99th percentile pads almost everything. "
             "**Neither is free**, and the histogram is what turns that into a "
             "decision rather than a default."),

            ("h2", "Three baselines, in ascending order of effort"),
            ("py", """from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier

def vectorize(seqs, dim=10000):
    out = np.zeros((len(seqs), dim), dtype="float32")
    for i, s in enumerate(seqs):
        out[i, s] = 1.
    return out

x_tr, x_te = vectorize(train_data), vectorize(test_data)

d = DummyClassifier(strategy="most_frequent").fit(x_tr, train_labels)
print(f"1. majority class:        {d.score(x_te, test_labels):.4f}")

lr = LogisticRegression(max_iter=400, n_jobs=-1).fit(x_tr, train_labels)
print(f"2. logistic on bag-of-words: {lr.score(x_te, test_labels):.4f}")"""),
            ("out", """1. majority class:        0.36x
2. logistic on bag-of-words: 0.7xx"""),
            ("md",
             "The second number is the real bar. **A deep model that scores 0.75 "
             "here has not earned its place** — and finding that out took thirty "
             "seconds rather than a week."),

            ("h2", "What could leak"),
            ("md",
             "A checklist to run before every project, not only this one.\n\n"
             "| Question | Why it matters |\n"
             "|---|---|\n"
             "| Is any feature computed **after** the label is known? | The "
             "classic target leak — a field that only exists once the outcome "
             "has happened. |\n"
             "| Is the data ordered in time? | Then the split must be too. |\n"
             "| Are samples grouped — by patient, customer, document? | The "
             "split must be by **group**, not by row. |\n"
             "| Was anything fitted before the split? | Scalers, vocabularies, "
             "and `adapt()` calls all count. |\n"
             "| Are there duplicates? | Checked above. |\n\n"
             "None of these produce an error. All of them produce a good number."),
        ],
        "takeaways": [
            "Class balance decides the metric, before any model exists.",
            "Check for duplicates **across** the split, not just within it.",
            "The length distribution turns truncation from a default into a "
            "decision.",
            "The baseline to beat is a simple model on the same features, not "
            "random guessing.",
        ],
    },

    {
        "file": "02_common_preprocessing.ipynb",
        "title": "Vectorization, normalization, and missing values",
        "lede": "The three preprocessing steps almost every project needs, with the "
                "mistakes each one invites.",
        "needs": "CPU — about 2 minutes",
        "section": "02 — Develop a model",
        "cells": [
            ("h2", "Everything becomes a float tensor"),
            ("py", """import numpy as np

# Text -> integers -> multi-hot, as in chapters 4 and 5.
# Categorical -> one-hot.
# Images -> float in [0, 1].
# Everything else -> normalized floats.

categories = np.array(["red", "green", "blue", "green", "red"])
vocab = sorted(set(categories))
lookup = {v: i for i, v in enumerate(vocab)}
onehot = np.eye(len(vocab))[[lookup[c] for c in categories]]
print(vocab)
print(onehot)"""),
            ("note",
             "One-hot, not integers. Encoding *red=0, green=1, blue=2* tells the "
             "model that green is between red and blue, which is a fact you "
             "invented."),

            ("h2", "Normalization, and why it is not optional"),
            ("py", """import keras
from keras import layers
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
# Two features on wildly different scales -- a common real-world shape.
X = np.column_stack([rng.normal(0, 1, 2000),
                     rng.normal(5000, 2000, 2000)]).astype("float32")
y = (X[:, 0] * 2 + (X[:, 1] - 5000) / 1000 > 0).astype("float32")

def run(data, label):
    keras.utils.set_random_seed(0)
    m = keras.Sequential([layers.Dense(16, activation="relu"),
                          layers.Dense(1, activation="sigmoid")])
    m.compile(optimizer="rmsprop", loss="binary_crossentropy",
              metrics=["accuracy"])
    h = m.fit(data, y, epochs=20, batch_size=64, validation_split=.3, verbose=0)
    print(f"{label:14s} best val acc {max(h.history['val_accuracy']):.4f}")
    return h

raw = run(X, "raw")
Xn = (X - X.mean(axis=0)) / X.std(axis=0)
norm = run(Xn, "normalized")

plt.figure(figsize=(6.5, 4))
plt.plot(raw.history["val_accuracy"], label="raw features")
plt.plot(norm.history["val_accuracy"], label="normalized")
plt.xlabel("epoch"); plt.ylabel("validation accuracy"); plt.legend()
plt.title("One feature 2000x larger than the other")
plt.show()"""),
            ("md",
             "Large input values produce large gradient updates, which "
             "destabilise everything downstream. **Small, homogeneous values — "
             "roughly zero mean, unit variance** — is the rule, and it costs one "
             "line."),

            ("h2", "Doing it inside the model"),
            ("md",
             "A `Normalization` layer keeps the statistics **with the model**, "
             "so they cannot be lost between training and serving. This is the "
             "shape of a whole class of production bugs, removed."),
            ("py", """norm_layer = layers.Normalization()
norm_layer.adapt(X[:1400])          # TRAINING data only

model = keras.Sequential([
    norm_layer,
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="rmsprop", loss="binary_crossentropy",
              metrics=["accuracy"])
model.fit(X[:1400], y[:1400], epochs=20, batch_size=64, verbose=0)
print("test:", model.evaluate(X[1400:], y[1400:], verbose=0))

# The statistics now travel with the saved model.
model.save("normalized_model.keras")
reloaded = keras.saving.load_model("normalized_model.keras")
print("after reload:", reloaded.evaluate(X[1400:], y[1400:], verbose=0))"""),
            ("warn",
             "`adapt()` is fitting.** Call it on the training split only. "
             "Calling it on everything is the leak from notebook 03 of chapter "
             "5, wearing a Keras-shaped disguise."),

            ("h2", "Missing values"),
            ("py", """Xm = Xn.copy()
missing = rng.random(Xm.shape) < 0.1
Xm[missing] = np.nan
print(f"{missing.mean():.1%} of entries missing")

# 0 is a safe fill *after* normalization: it is the mean, and the network
# will learn to treat it as "no information" -- provided it sees such
# samples during training.
Xf = np.where(np.isnan(Xm), 0.0, Xm)
print("any NaN left:", bool(np.isnan(Xf).any()))"""),
            ("md",
             "Two conditions make zero-filling work, and both are easy to "
             "break.\n\n"
             "1. The data must be **normalized first**, so that 0 means *the "
             "average*, not *nothing*.\n"
             "2. The network must **see missing values during training**. If "
             "they only appear at inference time, artificially remove some from "
             "the training data — otherwise the model has never met the pattern "
             "it is about to be given."),

            ("h2", "The order these must happen in"),
            ("md",
             "```\nsplit  ->  fit preprocessing on train  ->  apply to all splits\n```\n\n"
             "Not: preprocess, then split. Every leak in chapter 5's notebook 03 "
             "comes from getting this order wrong, and no framework will warn "
             "you."),
        ],
        "takeaways": [
            "Everything becomes a float tensor; categories become one-hot, not "
            "integers.",
            "Normalize to roughly zero mean and unit variance — large inputs "
            "destabilise training.",
            "A `Normalization` layer keeps the statistics with the model, which "
            "removes a whole class of serving bugs.",
            "Split first, fit preprocessing on train, then apply. Always that "
            "order.",
        ],
    },

    {
        "file": "03_export_and_quantize.ipynb",
        "title": "Deploying: saving, serving, and making it smaller",
        "lede": "What happens after fit() returns — the .keras format, inference-only "
                "export, and the two ways to make a model cheaper to run.",
        "needs": "CPU — about 2 minutes",
        "section": "03 — Deploy the model",
        "cells": [
            ("h2", "A model to deploy"),
            ("py", """import keras
from keras import layers
from keras.datasets import mnist
import numpy as np

(x, y), (xt, yt) = mnist.load_data()
x = x.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

keras.utils.set_random_seed(0)
model = keras.Sequential([
    layers.Dense(256, activation="relu"),
    layers.Dense(128, activation="relu"),
    layers.Dense(10, activation="softmax"),
])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(x, y, epochs=3, batch_size=128, verbose=0)
base_acc = model.evaluate(xt, yt, verbose=0)[1]
print(f"accuracy: {base_acc:.4f}   parameters: {model.count_params():,}")"""),

            ("h2", "Saving, and what is in the file"),
            ("py", """import os, zipfile

model.save("mnist.keras")
size = os.path.getsize("mnist.keras")
print(f"mnist.keras: {size/1e6:.2f} MB")

with zipfile.ZipFile("mnist.keras") as z:
    for n in z.namelist():
        print(" ", n, f"{z.getinfo(n).file_size/1e6:.2f} MB")"""),
            ("out", """mnist.keras: 1.2x MB
  metadata.json 0.00 MB
  config.json 0.00 MB
  model.weights.h5 1.2x MB"""),
            ("md",
             "A zip of three things: the architecture as JSON, the weights, and "
             "a little metadata. **Backend-independent** — chapter 3's notebook "
             "02 saved under one backend and loaded under another."),

            ("h2", "Preprocessing belongs inside the exported model"),
            ("md",
             "The most common serving bug is not a broken model — it is "
             "preprocessing that differs by a fraction between the training "
             "script and the service. Put it in the graph and the question "
             "cannot arise."),
            ("py", """inputs = keras.Input(shape=(28, 28), dtype="uint8", name="image")
x_ = keras.layers.Rescaling(1./255)(keras.ops.cast(inputs, "float32"))
x_ = keras.layers.Reshape((784,))(x_)
outputs = model(x_)
servable = keras.Model(inputs, outputs, name="mnist_servable")

# It now takes exactly what the caller has: raw uint8 images.
raw = mnist.load_data()[1][0][:4]
print("input dtype:", raw.dtype, " shape:", raw.shape)
print("predictions:", servable.predict(raw, verbose=0).argmax(axis=1))
servable.save("mnist_servable.keras")"""),

            ("h2", "Making it smaller: int8 quantization"),
            ("md",
             "Chapter 18 explains the arithmetic. Here is what it costs and what "
             "it buys, measured."),
            ("py", """import copy, time

q = keras.saving.load_model("mnist.keras")
q.quantize("int8")
q_acc = q.evaluate(xt, yt, verbose=0)[1]
q.save("mnist_int8.keras")

fp = os.path.getsize("mnist.keras") / 1e6
qs = os.path.getsize("mnist_int8.keras") / 1e6
print(f"float32: {fp:.2f} MB   accuracy {base_acc:.4f}")
print(f"int8:    {qs:.2f} MB   accuracy {q_acc:.4f}")
print(f"size: {fp/qs:.1f}x smaller   accuracy cost: {base_acc-q_acc:+.4f}")"""),
            ("out", """float32: 1.2x MB   accuracy 0.97xx
int8:    0.3x MB   accuracy 0.97xx
size: ~4x smaller   accuracy cost: -0.00xx"""),
            ("note",
             "Measure the accuracy cost on **your** data, every time. It is "
             "usually negligible and it is not guaranteed to be — and quantizing "
             "is a one-way operation on the model object, so keep the float32 "
             "file."),

            ("h2", "Measuring inference cost honestly"),
            ("py", """def bench(m, data, n=5, warmup=2):
    for _ in range(warmup):
        m.predict(data, verbose=0)
    t0 = time.perf_counter()
    for _ in range(n):
        m.predict(data, verbose=0)
    return (time.perf_counter() - t0) / n

batch = xt[:512]
print(f"float32: {bench(model, batch)*1000:.1f} ms / 512 samples")
print(f"int8:    {bench(q, batch)*1000:.1f} ms / 512 samples")"""),
            ("md",
             "**Warm up first.** The first call compiles; timing it measures the "
             "compiler. Chapter 16's generation notebook makes the same mistake "
             "deliberately, and it costs two orders of magnitude there."),

            ("h2", "What still has to be built around this"),
            ("md",
             "The model is the small part. A deployment also needs:\n\n"
             "- **Input validation** — the shape and dtype the model expects, "
             "enforced at the boundary rather than assumed.\n"
             "- **Monitoring** — not just errors, but the distribution of "
             "inputs. Chapter 19's point about distribution shift starts "
             "counting from the day you deploy.\n"
             "- **A rollback** — models are data, and a bad model ships as "
             "easily as a good one.\n"
             "- **A held-out set you have not touched**, so the number you "
             "quote is one you can defend."),
        ],
        "takeaways": [
            "`.keras` is a zip of config plus weights, and it is "
            "backend-independent.",
            "Put preprocessing **inside** the exported model — it removes the "
            "most common serving bug.",
            "int8 quantization is roughly 4× smaller; measure the accuracy cost "
            "on your own data.",
            "Warm up before benchmarking, or you are timing the compiler.",
        ],
    },
]
