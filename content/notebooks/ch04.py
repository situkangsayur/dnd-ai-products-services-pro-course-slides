# -*- coding: utf-8 -*-
"""Chapter 4 notebooks — Classification and Regression."""

DECK = "ch04"

NOTEBOOKS = [
    {
        "file": "01_imdb_binary_classification.ipynb",
        "title": "Binary classification: movie reviews",
        "lede": "The first real problem in the book. Multi-hot encoding, two Dense "
                "layers, and the moment the validation loss turns around while the "
                "training loss keeps falling.",
        "needs": "CPU — about 2 minutes",
        "section": "01 — Classifying movie reviews",
        "cells": [
            ("h2", "The data"),
            ("py", """from keras.datasets import imdb

(train_data, train_labels), (test_data, test_labels) = imdb.load_data(
    num_words=10000
)

print(len(train_data), "training reviews")
print("first review, as word indices:", train_data[0][:12], "...")
print("label:", train_labels[0], " (1 = positive)")
print("largest index anywhere:", max(max(seq) for seq in train_data))"""),
            ("out", """25000 training reviews
first review, as word indices: [1, 14, 22, 16, 43, 530, 973, 1622, 1385, 65, 458, 4468] ...
label: 1  (1 = positive)
largest index anywhere: 9999"""),
            ("py", """word_index = imdb.get_word_index()
reverse_word_index = {v: k for k, v in word_index.items()}

# Indices 0, 1 and 2 are reserved for padding, start-of-sequence, and unknown.
decoded = " ".join(reverse_word_index.get(i - 3, "?") for i in train_data[0])
print(decoded[:400], "...")"""),

            ("h2", "Multi-hot encoding"),
            ("md",
             "Lists of integers cannot be fed to a Dense layer. Turn each review "
             "into a 10,000-vector with a 1 at every index that appears — "
             "**word order is discarded entirely**, and chapter 14 will return "
             "to whether that matters."),
            ("py", """import numpy as np

def vectorize_sequences(sequences, dimension=10000):
    results = np.zeros((len(sequences), dimension), dtype="float32")
    for i, sequence in enumerate(sequences):
        for j in sequence:
            results[i, j] = 1.
    return results

x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)
y_train = np.asarray(train_labels).astype("float32")
y_test = np.asarray(test_labels).astype("float32")

print(x_train.shape, x_train[0][:12])"""),

            ("h2", "The model"),
            ("py", """import keras
from keras import layers

model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="rmsprop",
              loss="binary_crossentropy",
              metrics=["accuracy"])"""),
            ("note",
             "One unit, `sigmoid`, `binary_crossentropy`. That triple is fixed "
             "for binary classification, and chapter 20 puts all five such "
             "triples in one table."),

            ("h2", "A validation set, held out by hand"),
            ("py", """x_val, partial_x_train = x_train[:10000], x_train[10000:]
y_val, partial_y_train = y_train[:10000], y_train[10000:]

history = model.fit(partial_x_train, partial_y_train,
                    epochs=20, batch_size=512,
                    validation_data=(x_val, y_val), verbose=2)"""),

            ("h2", "The plot this whole chapter exists for"),
            ("py", """import matplotlib.pyplot as plt

h = history.history
epochs = range(1, len(h["loss"]) + 1)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
a1.plot(epochs, h["loss"], "o-", ms=3, label="training loss")
a1.plot(epochs, h["val_loss"], "s-", ms=3, label="validation loss")
a1.set_xlabel("epoch"); a1.legend(); a1.set_title("Loss")

a2.plot(epochs, h["accuracy"], "o-", ms=3, label="training accuracy")
a2.plot(epochs, h["val_accuracy"], "s-", ms=3, label="validation accuracy")
a2.set_xlabel("epoch"); a2.legend(); a2.set_title("Accuracy")
plt.tight_layout(); plt.show()

best = int(np.argmin(h["val_loss"])) + 1
print(f"validation loss is lowest at epoch {best}, then rises for "
      f"{len(epochs) - best} more epochs while training loss keeps falling")"""),
            ("md",
             "**Training loss falls monotonically. Validation loss turns around "
             "at about epoch 4.** Everything after that point is the model "
             "memorising the training set. This picture is the reason chapter 5 "
             "exists."),

            ("h2", "Retraining to the right number of epochs"),
            ("py", """model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="rmsprop", loss="binary_crossentropy",
              metrics=["accuracy"])
model.fit(x_train, y_train, epochs=4, batch_size=512, verbose=0)
print("test:", model.evaluate(x_test, y_test, verbose=0))"""),
            ("out", "test: [0.29xx, 0.88xx]"),
            ("md",
             "About 88%. A state-of-the-art model reaches roughly 95% — chapter "
             "15 gets there with RoBERTa. Note how far a two-layer network on "
             "bag-of-words gets, and remember it when the expensive option is "
             "proposed."),
        ],
        "takeaways": [
            "Sequences must be vectorized before a Dense layer will take them.",
            "Binary classification: one unit, sigmoid, binary_crossentropy.",
            "**Validation loss turning around while training loss falls is "
            "overfitting**, and it happens by epoch 4 here.",
            "A simple baseline reaches 88% on a problem where the ceiling is "
            "about 95%.",
        ],
    },

    {
        "file": "02_reuters_multiclass.ipynb",
        "title": "Multiclass classification: newswires",
        "lede": "Forty-six classes, and the information bottleneck that appears when "
                "an intermediate layer is smaller than the output.",
        "needs": "CPU — about 2 minutes",
        "section": "02 — Classifying newswires",
        "cells": [
            ("h2", "The data"),
            ("py", """from keras.datasets import reuters
import numpy as np

(train_data, train_labels), (test_data, test_labels) = reuters.load_data(
    num_words=10000
)
print(len(train_data), "training,", len(test_data), "test")
print("classes:", len(set(train_labels)))
print("class distribution (top 5):",
      np.bincount(train_labels).argsort()[::-1][:5])"""),
            ("out", """8982 training, 2246 test
classes: 46
class distribution (top 5): [ 3  4 19 16  1]"""),

            ("h2", "Vectorizing inputs and targets"),
            ("py", """def vectorize_sequences(sequences, dimension=10000):
    results = np.zeros((len(sequences), dimension), dtype="float32")
    for i, seq in enumerate(sequences):
        for j in seq:
            results[i, j] = 1.
    return results

x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)

# Two equally valid ways to encode the targets.
y_train_int = np.asarray(train_labels)
y_test_int = np.asarray(test_labels)

import keras
y_train_oh = keras.utils.to_categorical(train_labels)
print("integer targets:", y_train_int.shape, " one-hot:", y_train_oh.shape)"""),
            ("note",
             "One-hot targets go with `categorical_crossentropy`; integer "
             "targets go with `sparse_categorical_crossentropy`. **Same loss, "
             "different interface** — pairing them wrongly produces a shape "
             "error, which is the good outcome."),

            ("h2", "The model"),
            ("py", """from keras import layers

model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(46, activation="softmax"),
])
model.compile(optimizer="rmsprop",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])

x_val, partial_x = x_train[:1000], x_train[1000:]
y_val, partial_y = y_train_int[:1000], y_train_int[1000:]

history = model.fit(partial_x, partial_y, epochs=20, batch_size=512,
                    validation_data=(x_val, y_val), verbose=2)"""),
            ("md",
             "Sixty-four units, not sixteen. With 46 output classes, a "
             "**16-unit layer would be an information bottleneck** — the next "
             "cell demonstrates that rather than asserting it."),

            ("h2", "The bottleneck, demonstrated"),
            ("py", """import matplotlib.pyplot as plt

def run(units, epochs=20):
    keras.utils.set_random_seed(0)
    m = keras.Sequential([
        layers.Dense(units, activation="relu"),
        layers.Dense(units, activation="relu"),
        layers.Dense(46, activation="softmax"),
    ])
    m.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    h = m.fit(partial_x, partial_y, epochs=epochs, batch_size=512,
              validation_data=(x_val, y_val), verbose=0)
    return h.history["val_accuracy"]

plt.figure(figsize=(7, 4.4))
for u in [4, 16, 64]:
    plt.plot(run(u), lw=1.5, label=f"{u} hidden units")
plt.xlabel("epoch"); plt.ylabel("validation accuracy")
plt.legend(); plt.title("An intermediate layer smaller than the output loses information")
plt.show()"""),
            ("md",
             "Four units cannot carry 46 classes' worth of separation, and no "
             "amount of training recovers it. **Information dropped by a layer "
             "is never recovered by a later one** — the layers form a pipeline, "
             "not a committee."),

            ("h2", "A baseline worth computing"),
            ("py", """import copy
test_labels_copy = copy.copy(test_labels)
np.random.shuffle(test_labels_copy)
random_baseline = float((np.array(test_labels) == np.array(test_labels_copy)).mean())
majority = np.bincount(train_labels).max() / len(train_labels)

model.fit(x_train, y_train_int, epochs=9, batch_size=512, verbose=0)
_, acc = model.evaluate(x_test, y_test_int, verbose=0)

print(f"random guessing:  {random_baseline:.3f}")
print(f"always the most common class: {majority:.3f}")
print(f"this model:       {acc:.3f}")"""),
            ("out", """random guessing:  0.0xx
always the most common class: 0.36x
this model:       0.79x"""),
            ("md",
             "**Beating random is not the bar.** The majority-class baseline is "
             "36% here, and it costs one line to compute. Chapter 6 makes this a "
             "required step of the workflow."),
        ],
        "takeaways": [
            "N-way classification: N units, softmax, and a crossentropy loss.",
            "One-hot targets pair with `categorical_crossentropy`; integers with "
            "the `sparse_` variant.",
            "**An intermediate layer smaller than the output is a permanent "
            "bottleneck.**",
            "Compute the majority-class baseline before believing any accuracy "
            "figure.",
        ],
    },

    {
        "file": "03_housing_regression.ipynb",
        "title": "Regression, and K-fold validation on a small dataset",
        "lede": "506 samples, thirteen features on wildly different scales, and no "
                "validation set big enough to trust. K-fold is not a nicety here.",
        "needs": "CPU — about 3 minutes",
        "section": "03 — Predicting house prices",
        "cells": [
            ("h2", "A very small dataset"),
            ("py", """from keras.datasets import boston_housing
import numpy as np

(train_data, train_targets), (test_data, test_targets) = \\
    boston_housing.load_data()

print(train_data.shape, test_data.shape)
print("targets, in thousands of dollars:", train_targets[:6])
print("\\nfeature ranges — note the scales:")
for i in range(train_data.shape[1]):
    col = train_data[:, i]
    print(f"  feature {i:2d}: {col.min():9.3f} .. {col.max():9.3f}")"""),
            ("out", """(404, 13) (102, 13)
targets, in thousands of dollars: [15.2 42.3 50.  21.1 17.7 18.5]"""),

            ("h2", "Normalization, and the rule about it"),
            ("py", """mean = train_data.mean(axis=0)
std = train_data.std(axis=0)

train_data = (train_data - mean) / std
test_data = (test_data - mean) / std      # note: TRAIN statistics

print("after normalization, feature 0:",
      f"mean {train_data[:, 0].mean():+.3f}  std {train_data[:, 0].std():.3f}")"""),
            ("warn",
             "The test set is normalized with the **training** mean and "
             "standard deviation.** Using its own statistics leaks information "
             "from data you are pretending not to have — and the resulting "
             "number will be quietly optimistic."),

            ("h2", "The model"),
            ("py", """import keras
from keras import layers

def build_model():
    model = keras.Sequential([
        layers.Dense(64, activation="relu"),
        layers.Dense(64, activation="relu"),
        layers.Dense(1),                    # no activation
    ])
    model.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
    return model"""),
            ("md",
             "**No activation on the last layer.** A sigmoid would cap the "
             "output at 1; anything else would constrain the range. Regression "
             "wants the layer left alone."),

            ("h2", "K-fold, because 404 samples cannot spare a validation set"),
            ("py", """k = 4
num_val_samples = len(train_data) // k
num_epochs = 100
all_scores = []

for i in range(k):
    print(f"fold {i}")
    val_data = train_data[i * num_val_samples: (i + 1) * num_val_samples]
    val_targets = train_targets[i * num_val_samples: (i + 1) * num_val_samples]
    partial_train_data = np.concatenate(
        [train_data[:i * num_val_samples],
         train_data[(i + 1) * num_val_samples:]], axis=0)
    partial_train_targets = np.concatenate(
        [train_targets[:i * num_val_samples],
         train_targets[(i + 1) * num_val_samples:]], axis=0)

    model = build_model()
    model.fit(partial_train_data, partial_train_targets,
              epochs=num_epochs, batch_size=16, verbose=0)
    _, val_mae = model.evaluate(val_data, val_targets, verbose=0)
    all_scores.append(val_mae)

print("\\nper fold:", [round(s, 3) for s in all_scores])
print(f"mean {np.mean(all_scores):.3f}   spread {max(all_scores)-min(all_scores):.3f}")"""),
            ("out", """per fold: [2.0xx, 2.9xx, 2.5xx, 2.4xx]
mean 2.5xx   spread 0.9xx"""),
            ("md",
             "**The spread between folds is comparable to the differences you "
             "would be trying to measure.** That is the whole argument for "
             "K-fold: with a single split, which fold you happened to draw "
             "would decide your conclusion."),

            ("h2", "Finding the right number of epochs"),
            ("py", """import matplotlib.pyplot as plt

num_epochs = 200
all_mae_histories = []
for i in range(k):
    val_data = train_data[i * num_val_samples: (i + 1) * num_val_samples]
    val_targets_f = train_targets[i * num_val_samples: (i + 1) * num_val_samples]
    ptd = np.concatenate([train_data[:i * num_val_samples],
                          train_data[(i + 1) * num_val_samples:]], axis=0)
    ptt = np.concatenate([train_targets[:i * num_val_samples],
                          train_targets[(i + 1) * num_val_samples:]], axis=0)
    model = build_model()
    h = model.fit(ptd, ptt, validation_data=(val_data, val_targets_f),
                  epochs=num_epochs, batch_size=16, verbose=0)
    all_mae_histories.append(h.history["val_mae"])

average_mae = [np.mean([x[i] for x in all_mae_histories])
               for i in range(num_epochs)]

plt.figure(figsize=(7, 4.2))
plt.plot(range(11, len(average_mae) + 1), average_mae[10:], lw=1.5)
plt.xlabel("epoch"); plt.ylabel("validation MAE (averaged over 4 folds)")
plt.title(f"best around epoch {int(np.argmin(average_mae)) + 1}")
plt.show()"""),
            ("md",
             "The first ten epochs are dropped so the rest is readable — their "
             "values are on a different scale entirely. Averaging over folds is "
             "what makes the minimum locatable at all; a single fold's curve is "
             "too noisy to read."),

            ("h2", "The final model"),
            ("py", """model = build_model()
model.fit(train_data, train_targets, epochs=130, batch_size=16, verbose=0)
_, test_mae = model.evaluate(test_data, test_targets, verbose=0)
print(f"test MAE: {test_mae:.3f}  (thousands of dollars)")

pred = model.predict(test_data, verbose=0).ravel()
plt.figure(figsize=(5, 5))
plt.scatter(test_targets, pred, s=14, alpha=.7)
lims = [0, max(test_targets.max(), pred.max()) + 3]
plt.plot(lims, lims, "k--", lw=1)
plt.xlabel("actual"); plt.ylabel("predicted"); plt.gca().set_aspect("equal")
plt.title("Predicted against actual"); plt.show()"""),
            ("md",
             "Read the scatter, not the MAE. A model can hit a respectable "
             "average error while being systematically wrong at one end of the "
             "range — and here you can see whether it is."),
        ],
        "takeaways": [
            "Regression: no activation on the last layer, `mse` loss, `mae` as "
            "the readable metric.",
            "Normalize with **training** statistics, always.",
            "On small data, K-fold is not a refinement — the fold-to-fold spread "
            "is as large as the effects you are measuring.",
            "Plot predicted against actual; an average error hides systematic "
            "bias.",
        ],
    },
]
