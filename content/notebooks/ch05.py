# -*- coding: utf-8 -*-
"""Chapter 5 notebooks — Fundamentals of Machine Learning."""

DECK = "ch05"

NOTEBOOKS = [
    {
        "file": "01_spurious_correlations.ipynb",
        "title": "Adding noise channels makes a model worse",
        "lede": "The experiment that shows generalization is not something you get "
                "for free from more features. Same model, same digits, plus 784 "
                "columns of pure noise.",
        "needs": "CPU — about 3 minutes",
        "section": "01 — Generalization: the goal of machine learning",
        "cells": [
            ("h2", "Two versions of MNIST"),
            ("py", """import numpy as np
from keras.datasets import mnist

(train_images, train_labels), _ = mnist.load_data()
train_images = train_images.reshape((60000, 28 * 28)).astype("float32") / 255

train_images_with_noise_channels = np.concatenate(
    [train_images, np.random.random((len(train_images), 784))], axis=1)

train_images_with_zeros_channels = np.concatenate(
    [train_images, np.zeros((len(train_images), 784))], axis=1)

print(train_images_with_noise_channels.shape)"""),
            ("md",
             "Both new versions are 1568 columns wide. One has random noise in "
             "the extra half; the other has zeros. **Neither carries any "
             "information about the digit.**"),

            ("h2", "Training both"),
            ("py", """import keras
from keras import layers

def get_model():
    keras.utils.set_random_seed(0)
    model = keras.Sequential([
        layers.Dense(512, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ])
    model.compile(optimizer="rmsprop",
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    return model

history_noise = get_model().fit(
    train_images_with_noise_channels, train_labels,
    epochs=10, batch_size=128, validation_split=0.2, verbose=0)

history_zeros = get_model().fit(
    train_images_with_zeros_channels, train_labels,
    epochs=10, batch_size=128, validation_split=0.2, verbose=0)"""),

            ("h2", "The result"),
            ("py", """import matplotlib.pyplot as plt

epochs = range(1, 11)
plt.figure(figsize=(7, 4.4))
plt.plot(epochs, history_noise.history["val_accuracy"], "b-",
         label="noise channels")
plt.plot(epochs, history_zeros.history["val_accuracy"], "b--",
         label="zero channels")
plt.xlabel("epoch"); plt.ylabel("validation accuracy"); plt.legend()
plt.title("Effect of noise channels on validation accuracy")
plt.show()

gap = (history_zeros.history["val_accuracy"][-1]
       - history_noise.history["val_accuracy"][-1])
print(f"final gap: {gap:.3f}")"""),
            ("out", "final gap: about 0.01 to 0.02 — one to two percentage points"),
            ("md",
             "Both sets of extra columns are uninformative. Only one **hurts**.\n\n"
             "The difference is that noise offers something to latch onto: with "
             "enough capacity the model finds correlations in the random columns "
             "that happen to hold on the training set and hold nowhere else. "
             "==Feature selection is not tidiness; it is a defence.=="),

            ("h2", "How much noise before it collapses"),
            ("py", """results = {}
for n_noise in [0, 128, 784, 2000]:
    x = train_images if n_noise == 0 else np.concatenate(
        [train_images, np.random.random((len(train_images), n_noise))], axis=1)
    h = get_model().fit(x, train_labels, epochs=6, batch_size=128,
                        validation_split=0.2, verbose=0)
    results[n_noise] = h.history["val_accuracy"][-1]
    print(f"{n_noise:5d} noise columns -> val acc {results[n_noise]:.4f}")

plt.figure(figsize=(6, 4))
plt.plot(list(results), list(results.values()), "o-")
plt.xlabel("noise columns added"); plt.ylabel("validation accuracy")
plt.title("Degradation is gradual, not a cliff")
plt.show()"""),
            ("md",
             "It degrades smoothly. There is no threshold to stay under — which "
             "is exactly why the practical rule is to measure feature usefulness "
             "rather than to guess at it."),
        ],
        "takeaways": [
            "Uninformative features are not harmless: **noise hurts, zeros do "
            "not**.",
            "With enough capacity a model will find correlations in noise that "
            "hold only on the training set.",
            "Degradation is gradual, so there is no safe amount of junk to leave "
            "in.",
            "Feature selection is a generalization technique, not housekeeping.",
        ],
    },

    {
        "file": "02_shuffled_labels_and_manifolds.ipynb",
        "title": "A network will fit random labels — and what that means",
        "lede": "Deep learning models can memorise an arbitrary mapping. Generalization "
                "therefore cannot come from the model; it comes from structure in the "
                "data.",
        "needs": "CPU — about 4 minutes",
        "section": "02 — The nature of generalization",
        "cells": [
            ("h2", "Shuffling the labels"),
            ("py", """import numpy as np
import keras
from keras import layers
from keras.datasets import mnist

(train_images, train_labels), _ = mnist.load_data()
train_images = train_images.reshape((60000, 28 * 28)).astype("float32") / 255

random_train_labels = train_labels[:]
np.random.shuffle(random_train_labels)

model = keras.Sequential([
    layers.Dense(512, activation="relu"),
    layers.Dense(10, activation="softmax"),
])
model.compile(optimizer="rmsprop",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
h = model.fit(train_images, random_train_labels,
              epochs=100, batch_size=128, validation_split=0.2, verbose=0)"""),
            ("py", """import matplotlib.pyplot as plt

plt.figure(figsize=(7, 4.4))
plt.plot(h.history["accuracy"], label="training accuracy")
plt.plot(h.history["val_accuracy"], label="validation accuracy")
plt.axhline(0.1, color="k", ls=":", lw=1, label="chance (10 classes)")
plt.xlabel("epoch"); plt.legend()
plt.title("Fitting labels that carry no information at all")
plt.show()

print(f"final training accuracy:   {h.history['accuracy'][-1]:.3f}")
print(f"final validation accuracy: {h.history['val_accuracy'][-1]:.3f}")"""),
            ("out", """final training accuracy:   0.9xx
final validation accuracy: 0.1xx"""),
            ("md",
             "Training accuracy climbs toward 1.0. Validation accuracy sits at "
             "chance, because there is nothing to generalize to.\n\n"
             "**Deep learning models can be trained to fit anything.** So "
             "generalization is not a property of the model — it is a property "
             "of *the structure of the data*, which the model can exploit when "
             "it exists and cannot invent when it does not."),

            ("h2", "The manifold hypothesis, made visible"),
            ("md",
             "MNIST digits live in a 784-dimensional space. The claim is that "
             "they occupy a **very low-dimensional manifold** inside it. Here is "
             "one piece of evidence: a random point in that space, against a "
             "real digit."),
            ("py", """fig, axes = plt.subplots(2, 6, figsize=(10, 3.6))
for ax, img in zip(axes[0], train_images[:6]):
    ax.imshow(img.reshape(28, 28), cmap="gray_r"); ax.axis("off")
axes[0, 0].set_title("real digits", loc="left", fontsize=10)

for ax in axes[1]:
    ax.imshow(np.random.random((28, 28)), cmap="gray_r"); ax.axis("off")
axes[1, 0].set_title("uniform random points in the same space",
                     loc="left", fontsize=10)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Sampling uniformly from the 784-dimensional cube gives you noise, "
             "essentially always. **The digits occupy a vanishingly small "
             "region** — and it is a connected one, which is the part that "
             "matters next."),

            ("h2", "Interpolating between two digits"),
            ("py", """a = train_images[np.where(train_labels == 4)[0][0]]
b = train_images[np.where(train_labels == 9)[0][0]]

alphas = np.linspace(0, 1, 9)
fig, axes = plt.subplots(1, 9, figsize=(12, 1.8))
for ax, t in zip(axes, alphas):
    ax.imshow(((1 - t) * a + t * b).reshape(28, 28), cmap="gray_r")
    ax.set_title(f"{t:.2f}", fontsize=8); ax.axis("off")
plt.suptitle("Linear interpolation in pixel space", y=1.12)
plt.show()"""),
            ("md",
             "The midpoints are **ghosts** — two digits superimposed, not a "
             "digit. Linear interpolation in *pixel* space leaves the manifold "
             "immediately.\n\n"
             "Chapter 17 does the same interpolation in a **learned latent** "
             "space and every midpoint is a valid digit. That difference is the "
             "entire value of representation learning, and it is worth seeing "
             "the failure before seeing the success."),

            ("h2", "Why more data is the best regularizer"),
            ("py", """def train_on(n, epochs=20):
    keras.utils.set_random_seed(0)
    m = keras.Sequential([layers.Dense(512, activation="relu"),
                          layers.Dense(10, activation="softmax")])
    m.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    hh = m.fit(train_images[:n], train_labels[:n], epochs=epochs,
               batch_size=128, validation_split=0.2, verbose=0)
    return max(hh.history["val_accuracy"])

sizes = [500, 2000, 10000, 60000]
scores = [train_on(n) for n in sizes]
for n, s in zip(sizes, scores):
    print(f"{n:6d} samples -> best val acc {s:.4f}")

plt.figure(figsize=(6, 4))
plt.semilogx(sizes, scores, "o-")
plt.xlabel("training samples"); plt.ylabel("best validation accuracy")
plt.title("A denser sampling of the manifold generalizes better")
plt.show()"""),
            ("md",
             "A model trained on a **dense** sampling of the manifold "
             "interpolates between points that are genuinely close together. On "
             "a sparse sampling it interpolates across gaps, and the "
             "interpolation is a guess. That is the whole argument."),
        ],
        "takeaways": [
            "A network will fit shuffled labels to near-perfect training "
            "accuracy — so generalization comes from the **data**, not the "
            "model.",
            "Real data occupies a tiny, structured manifold inside its "
            "nominal space.",
            "Interpolating in pixel space leaves the manifold; interpolating in "
            "a learned space does not.",
            "More data is the most effective regularizer there is, because it "
            "samples the manifold more densely.",
        ],
    },

    {
        "file": "03_evaluation_protocols.ipynb",
        "title": "Three evaluation protocols, and the leaks that defeat them",
        "lede": "Hold-out, K-fold, and iterated K-fold — with the four ways a test "
                "score gets quietly contaminated.",
        "needs": "CPU — about 3 minutes",
        "section": "03 — Evaluating machine learning models",
        "cells": [
            ("h2", "A common-sense baseline first"),
            ("py", """import numpy as np
from keras.datasets import mnist

(x, y), (xt, yt) = mnist.load_data()
x = x.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

print("random guessing:      ", f"{1/10:.3f}")
print("most common class:    ", f"{np.bincount(y).max()/len(y):.3f}")

# A genuinely trivial model, as a floor to beat.
from sklearn.linear_model import LogisticRegression
lr = LogisticRegression(max_iter=200, n_jobs=-1).fit(x[:10000], y[:10000])
print("logistic regression:  ", f"{lr.score(xt, yt):.3f}")"""),
            ("md",
             "**If a deep model cannot beat that third number, something is "
             "wrong** — and finding out now costs a minute rather than a week."),

            ("h2", "Hold-out validation"),
            ("py", """num_validation_samples = 10000
np.random.seed(0)
idx = np.random.permutation(len(x))
x_sh, y_sh = x[idx], y[idx]

validation_x, training_x = x_sh[:num_validation_samples], x_sh[num_validation_samples:]
validation_y, training_y = y_sh[:num_validation_samples], y_sh[num_validation_samples:]

print(f"train {len(training_x)}   validation {len(validation_x)}   test {len(xt)}")"""),
            ("note",
             "Simplest, and it needs enough data that the validation split is "
             "statistically meaningful. With a few hundred samples it is not, "
             "which is why chapter 4's housing example reached for K-fold."),

            ("h2", "K-fold, and why the spread matters more than the mean"),
            ("py", """import keras
from keras import layers

def small_model():
    keras.utils.set_random_seed(0)
    m = keras.Sequential([layers.Dense(64, activation="relu"),
                          layers.Dense(10, activation="softmax")])
    m.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

k, n = 5, 5000                    # a deliberately small subset
xs, ys = x[:n], y[:n]
fold = n // k
scores = []
for i in range(k):
    vx, vy = xs[i*fold:(i+1)*fold], ys[i*fold:(i+1)*fold]
    tx = np.concatenate([xs[:i*fold], xs[(i+1)*fold:]])
    ty = np.concatenate([ys[:i*fold], ys[(i+1)*fold:]])
    m = small_model()
    m.fit(tx, ty, epochs=8, batch_size=64, verbose=0)
    scores.append(m.evaluate(vx, vy, verbose=0)[1])

print("folds:", [f"{s:.4f}" for s in scores])
print(f"mean {np.mean(scores):.4f}   std {np.std(scores):.4f}   "
      f"spread {max(scores)-min(scores):.4f}")"""),
            ("md",
             "Report the spread alongside the mean. **A one-point improvement "
             "inside a two-point spread is not an improvement** — it is a "
             "different fold."),

            ("h2", "Leak 1: preprocessing fitted before the split"),
            ("py", """from sklearn.preprocessing import StandardScaler

# WRONG: statistics computed over everything, including validation.
bad = StandardScaler().fit(np.vstack([training_x, validation_x]))

# RIGHT: statistics from training data only.
good = StandardScaler().fit(training_x)

print("mean of feature 400, all data:  ", f"{bad.mean_[400]:.6f}")
print("mean of feature 400, train only:", f"{good.mean_[400]:.6f}")
print("difference:", f"{abs(bad.mean_[400]-good.mean_[400]):.6f}")"""),
            ("md",
             "The difference is tiny here and the principle is not. Anything "
             "**fitted** on data — a scaler, a vocabulary, a PCA basis, "
             "`TextVectorization.adapt()` — must see only the training split."),

            ("h2", "Leak 2: duplicates across the split"),
            ("py", """# Simulate a dataset where some samples appear twice.
dup = np.vstack([x[:2000], x[:500]])
dup_y = np.concatenate([y[:2000], y[:500]])

perm = np.random.permutation(len(dup))
dup, dup_y = dup[perm], dup_y[perm]

train_part, val_part = dup[:2000], dup[2000:]
# Are any validation samples byte-identical to a training sample?
shared = sum(any(np.array_equal(v, t) for t in train_part) for v in val_part[:50])
print(f"{shared} of the first 50 validation samples also appear in training")"""),
            ("warn",
             "Redundancy is the leak nobody looks for.** A scraped dataset with "
             "duplicate records will put the same sample on both sides of the "
             "split, and your validation score becomes partly a training score."),

            ("h2", "Leak 3: temporal data split at random"),
            ("py", """import matplotlib.pyplot as plt

t = np.arange(400)
series = np.cumsum(np.random.default_rng(1).normal(size=400)) + 20

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.6))
r = np.random.default_rng(0).permutation(400)
a1.scatter(t[r[:320]], series[r[:320]], s=8, label="train")
a1.scatter(t[r[320:]], series[r[320:]], s=8, label="validation")
a1.set_title("WRONG — random split on a timeseries"); a1.legend()

a2.plot(t[:320], series[:320], lw=1.4, label="train")
a2.plot(t[320:], series[320:], lw=1.4, label="validation")
a2.set_title("RIGHT — validation is posterior"); a2.legend()
plt.tight_layout(); plt.show()"""),
            ("md",
             "In the left panel the model interpolates between points it has "
             "already seen on both sides. **You would be predicting the past "
             "from the future**, and the score would be excellent and "
             "worthless."),

            ("h2", "Leak 4: the test set used more than once"),
            ("md",
             "The subtlest one, and it has no code. Every time you look at the "
             "test score and change something, a little information moves from "
             "the test set into your model — through you.\n\n"
             "Chapter 18 gives this a name in the context of automated tuning "
             "(**validation-set overfitting**), but it applies just as much to a "
             "human iterating by hand. ==A test set is a one-shot instrument.=="),
        ],
        "takeaways": [
            "Compute a common-sense baseline before believing any score.",
            "Report the **spread** across folds, not only the mean.",
            "Anything fitted on data must be fitted on the training split only.",
            "Duplicates, temporal splits, and repeated test-set use are the "
            "three leaks that produce excellent, worthless numbers.",
        ],
    },

    {
        "file": "04_model_capacity.ipynb",
        "title": "Underfitting, overfitting, and finding the capacity you need",
        "lede": "The book's prescription is deliberately counterintuitive: make the "
                "model overfit first, then fight it. This notebook runs three "
                "capacities and shows why.",
        "needs": "CPU — about 4 minutes",
        "section": "04 — Improving model fit",
        "cells": [
            ("h2", "Three models of different sizes"),
            ("py", """import numpy as np
import keras
from keras import layers
from keras.datasets import imdb

(train_data, train_labels), _ = imdb.load_data(num_words=10000)

def vectorize(seqs, dim=10000):
    out = np.zeros((len(seqs), dim), dtype="float32")
    for i, s in enumerate(seqs):
        out[i, s] = 1.
    return out

x = vectorize(train_data)
y = np.asarray(train_labels).astype("float32")

def run(units, epochs=20, name=""):
    keras.utils.set_random_seed(0)
    m = keras.Sequential([layers.Dense(units, activation="relu"),
                          layers.Dense(units, activation="relu"),
                          layers.Dense(1, activation="sigmoid")])
    m.compile(optimizer="rmsprop", loss="binary_crossentropy",
              metrics=["accuracy"])
    h = m.fit(x, y, epochs=epochs, batch_size=512,
              validation_split=0.4, verbose=0)
    print(f"{name:12s} best val loss {min(h.history['val_loss']):.4f} "
          f"at epoch {int(np.argmin(h.history['val_loss']))+1}")
    return h

h_small = run(4, name="tiny (4)")
h_medium = run(16, name="medium (16)")
h_large = run(512, name="large (512)")"""),

            ("h2", "The three curves"),
            ("py", """import matplotlib.pyplot as plt

plt.figure(figsize=(8, 4.8))
for h, lab, c in [(h_small, "tiny (4)", "#1f77b4"),
                  (h_medium, "medium (16)", "#2ca02c"),
                  (h_large, "large (512)", "#d62728")]:
    plt.plot(h.history["val_loss"], c=c, lw=1.6, label=f"{lab} — validation")
    plt.plot(h.history["loss"], c=c, lw=1.0, ls="--", alpha=.6,
             label=f"{lab} — training")
plt.xlabel("epoch"); plt.ylabel("loss"); plt.ylim(0, 0.8)
plt.legend(fontsize=9); plt.title("Capacity, and when overfitting starts")
plt.show()"""),
            ("md",
             "Read it in three parts.\n\n"
             "**Tiny** — training loss stays high. It cannot represent the "
             "problem; this is underfitting, and no amount of regularization "
             "helps.\n\n"
             "**Large** — training loss collapses almost immediately and "
             "validation loss turns around within two epochs. Enormous "
             "capacity, memorized fast.\n\n"
             "**Medium** — the useful one, and note that it *also* overfits. "
             "The goal was never a model that does not overfit."),

            ("h2", "Why you should make it overfit first"),
            ("md",
             "The book's sequence is: **get to overfitting, then regularize**. "
             "The reason is that a model that has not overfit tells you nothing "
             "— you cannot distinguish *not enough capacity* from *not enough "
             "training* from *the wrong architecture* by looking at a flat "
             "curve.\n\n"
             "Once it overfits, you know the capacity is sufficient and every "
             "subsequent change is measurable."),

            ("h2", "Three things to check before blaming capacity"),
            ("py", """# 1. Is the learning rate right? Chapter 3's lesson, on a real model.
for lr in [1e-5, 1e-3, 1e-1]:
    keras.utils.set_random_seed(0)
    m = keras.Sequential([layers.Dense(16, activation="relu"),
                          layers.Dense(16, activation="relu"),
                          layers.Dense(1, activation="sigmoid")])
    m.compile(optimizer=keras.optimizers.RMSprop(learning_rate=lr),
              loss="binary_crossentropy", metrics=["accuracy"])
    h = m.fit(x, y, epochs=5, batch_size=512, validation_split=0.4, verbose=0)
    print(f"lr={lr:<7} train loss after 5 epochs: "
          f"{h.history['loss'][-1]:.4f}   val acc {h.history['val_accuracy'][-1]:.4f}")"""),
            ("out", """lr=1e-05   train loss after 5 epochs: 0.6xxx   val acc 0.6xxx
lr=0.001   train loss after 5 epochs: 0.1xxx   val acc 0.88xx
lr=0.1     train loss after 5 epochs: 0.6xxx   val acc 0.5xxx"""),
            ("md",
             "Both extremes look like *the model cannot learn*. Only one of "
             "them is about the model. **Check the learning rate, the batch "
             "size, and whether the problem is learnable at all** before "
             "reaching for a bigger network."),

            ("h2", "A problem with no signal in it"),
            ("py", """rng = np.random.default_rng(0)
x_junk = rng.random((5000, 100)).astype("float32")
y_junk = rng.integers(0, 2, size=5000).astype("float32")

keras.utils.set_random_seed(0)
m = keras.Sequential([layers.Dense(64, activation="relu"),
                      layers.Dense(64, activation="relu"),
                      layers.Dense(1, activation="sigmoid")])
m.compile(optimizer="rmsprop", loss="binary_crossentropy", metrics=["accuracy"])
h = m.fit(x_junk, y_junk, epochs=30, batch_size=128,
          validation_split=0.3, verbose=0)
print(f"training accuracy:   {h.history['accuracy'][-1]:.3f}")
print(f"validation accuracy: {h.history['val_accuracy'][-1]:.3f}  (chance is 0.5)")"""),
            ("md",
             "Training accuracy climbs; validation sits at chance. **This is "
             "what a genuinely unlearnable problem looks like**, and it is worth "
             "recognising, because the response is to go back to the data rather "
             "than to the architecture."),
        ],
        "takeaways": [
            "Underfitting and overfitting look different on the loss curves and "
            "have opposite remedies.",
            "**Make the model overfit first** — a flat curve is uninformative.",
            "Check the learning rate and the batch size before concluding the "
            "model is too small.",
            "A model that fits training data while validation sits at chance "
            "means the problem, not the model, is the issue.",
        ],
    },

    {
        "file": "05_regularisation_l2_dropout.ipynb",
        "title": "Regularizing: smaller, L2, and dropout",
        "lede": "Three ways to fight overfitting on the same problem, measured against "
                "each other rather than described.",
        "needs": "CPU — about 4 minutes",
        "section": "05 — Improving generalization",
        "cells": [
            ("h2", "The setup, and the baseline to beat"),
            ("py", """import numpy as np
import keras
from keras import layers, regularizers
from keras.datasets import imdb

(train_data, train_labels), _ = imdb.load_data(num_words=10000)

def vectorize(seqs, dim=10000):
    out = np.zeros((len(seqs), dim), dtype="float32")
    for i, s in enumerate(seqs):
        out[i, s] = 1.
    return out

x = vectorize(train_data)
y = np.asarray(train_labels).astype("float32")

def fit(model, epochs=20):
    model.compile(optimizer="rmsprop", loss="binary_crossentropy",
                  metrics=["accuracy"])
    return model.fit(x, y, epochs=epochs, batch_size=512,
                     validation_split=0.4, verbose=0)

keras.utils.set_random_seed(0)
baseline = fit(keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
]))"""),

            ("h2", "Option 1: a smaller model"),
            ("py", """keras.utils.set_random_seed(0)
smaller = fit(keras.Sequential([
    layers.Dense(4, activation="relu"),
    layers.Dense(4, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
]))"""),

            ("h2", "Option 2: L2 weight regularization"),
            ("md",
             "Add the sum of the squared weights to the loss. The model now pays "
             "for complexity, so it keeps only the weights that earn their "
             "place."),
            ("py", """keras.utils.set_random_seed(0)
l2 = fit(keras.Sequential([
    layers.Dense(16, kernel_regularizer=regularizers.l2(0.002),
                 activation="relu"),
    layers.Dense(16, kernel_regularizer=regularizers.l2(0.002),
                 activation="relu"),
    layers.Dense(1, activation="sigmoid"),
]))"""),

            ("h2", "Option 3: dropout"),
            ("md",
             "Zero a random half of the outputs during training. The layer "
             "cannot rely on any specific unit being present, so it cannot build "
             "a fragile conspiracy of units that happens to fit the training "
             "set."),
            ("py", """keras.utils.set_random_seed(0)
dropout = fit(keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(16, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(1, activation="sigmoid"),
]))"""),
            ("note",
             "Dropout is active during **training only**. At inference Keras "
             "scales the outputs instead, so `predict()` is deterministic — "
             "which is why you never see it in the evaluation numbers."),

            ("h2", "All four, on one axis"),
            ("py", """import matplotlib.pyplot as plt

runs = [("baseline (16, 16)", baseline, "#888888"),
        ("smaller (4, 4)", smaller, "#1f77b4"),
        ("L2 0.002", l2, "#2ca02c"),
        ("dropout 0.5", dropout, "#d62728")]

plt.figure(figsize=(8, 4.8))
for name, h, c in runs:
    plt.plot(h.history["val_loss"], lw=1.7, c=c, label=name)
plt.xlabel("epoch"); plt.ylabel("validation loss"); plt.ylim(0.25, 0.75)
plt.legend(); plt.title("Three ways to delay overfitting")
plt.show()

print(f"{'run':22s} {'best val loss':>14s} {'at epoch':>9s}")
for name, h, _ in runs:
    v = h.history["val_loss"]
    print(f"{name:22s} {min(v):14.4f} {int(np.argmin(v))+1:9d}")"""),
            ("md",
             "Read the **epoch of the minimum**, not just the minimum. "
             "Regularization does not usually give a dramatically better best "
             "score on this problem — it delays the turn, which buys you a "
             "wider window in which the model is good."),

            ("h2", "Dropout rate is a real hyperparameter"),
            ("py", """rates = [0.0, 0.2, 0.5, 0.8]
best = []
for r in rates:
    keras.utils.set_random_seed(0)
    layers_list = [layers.Dense(16, activation="relu")]
    if r: layers_list.append(layers.Dropout(r))
    layers_list.append(layers.Dense(16, activation="relu"))
    if r: layers_list.append(layers.Dropout(r))
    layers_list.append(layers.Dense(1, activation="sigmoid"))
    h = fit(keras.Sequential(layers_list), epochs=15)
    best.append(min(h.history["val_loss"]))
    print(f"dropout {r:.1f} -> best val loss {best[-1]:.4f}")

plt.figure(figsize=(5.5, 3.8))
plt.plot(rates, best, "o-")
plt.xlabel("dropout rate"); plt.ylabel("best validation loss")
plt.title("Too much dropout underfits")
plt.show()"""),
            ("md",
             "At 0.8 the model is being asked to work with a fifth of its units "
             "and it underfits. **Regularization taken far enough becomes the "
             "other failure** — which is why chapter 18 hands the choice to a "
             "tuner rather than to intuition."),

            ("h2", "What actually works best"),
            ("md",
             "The most effective regularizer on this problem is not on the chart: "
             "**more training data**. Notebook 02 showed the curve. Every "
             "technique here is what you reach for when more data is not "
             "available — which is most of the time, and is why they matter."),
        ],
        "takeaways": [
            "Reducing capacity, L2, and dropout all delay overfitting by "
            "different mechanisms.",
            "Read the epoch at which validation loss turns, not only its "
            "minimum.",
            "Dropout is training-only; inference is deterministic.",
            "Over-regularizing produces underfitting — the rate is a "
            "hyperparameter, not a constant.",
        ],
    },
]
