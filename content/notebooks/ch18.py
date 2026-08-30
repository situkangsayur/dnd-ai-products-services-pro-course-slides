# -*- coding: utf-8 -*-
"""Chapter 18 notebooks — Best Practices for the Real World."""

DECK = "ch18"

NOTEBOOKS = [
    {
        "file": "01_kerastuner_search.ipynb",
        "title": "Automatic hyperparameter search with KerasTuner",
        "lede": "A search space, a Bayesian tuner, and the two things that separate a "
                "usable result from a contaminated one.",
        "needs": "CPU — about 10 minutes",
        "section": "01 — Hyperparameter optimization",
        "cells": [
            ("h2", "Install and set up"),
            ("py", """# !pip install keras-tuner -q
import keras
from keras import layers
import keras_tuner as kt
import numpy as np

(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
x_train = x_train.reshape((-1, 28 * 28)).astype("float32") / 255
x_test = x_test.reshape((-1, 28 * 28)).astype("float32") / 255

x_train_full, y_train_full = x_train[:], y_train[:]
num_val = 10000
x_train, x_val = x_train[:-num_val], x_train[-num_val:]
y_train, y_val = y_train[:-num_val], y_train[-num_val:]
print(f"train {len(x_train)}  val {len(x_val)}  test {len(x_test)}")"""),

            ("h2", "A search space is a model-building function"),
            ("py", """def build_model(hp):
    units = hp.Int(name="units", min_value=16, max_value=64, step=16)
    model = keras.Sequential([
        layers.Dense(units, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ])
    optimizer = hp.Choice(name="optimizer", values=["rmsprop", "adam"])
    model.compile(optimizer=optimizer,
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    return model"""),
            ("md",
             "Hardcoded values become **ranges**. Four kinds exist: `Int`, "
             "`Float`, `Boolean`, `Choice`. After sampling they are ordinary "
             "Python constants — the function is called once per trial with "
             "concrete values."),

            ("h2", "A wider space, to make the point"),
            ("py", """def build_deeper(hp):
    model = keras.Sequential()
    for i in range(hp.Int("num_layers", 1, 3)):
        model.add(layers.Dense(
            hp.Int(f"units_{i}", 32, 256, step=32), activation="relu"))
        if hp.Boolean(f"dropout_{i}"):
            model.add(layers.Dropout(hp.Float(f"rate_{i}", 0.1, 0.5, step=0.1)))
    model.add(layers.Dense(10, activation="softmax"))
    model.compile(
        optimizer=keras.optimizers.Adam(
            hp.Float("lr", 1e-4, 1e-2, sampling="log")),
        loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

print("The space grows combinatorially:")
print("  3 depths x 8 widths^3 x 2 dropout^3 x 5 rates^3 x learning rate")
print("  = millions of configurations, from six lines.")
print()
print("That is why designing the space is your job, not the tuner's.")"""),
            ("note",
             "`sampling=\"log\"` on the learning rate. Sampling it uniformly "
             "between 1e-4 and 1e-2 would put 90% of the trials above 1e-3 — "
             "**learning rates should be searched on a log scale**, always."),

            ("h2", "The tuner"),
            ("py", """tuner = kt.BayesianOptimization(
    build_model,
    objective="val_accuracy",
    max_trials=20,
    executions_per_trial=2,
    directory="mnist_kt_test",
    overwrite=True,
)
tuner.search_space_summary()"""),
            ("md",
             "**`executions_per_trial=2`** is the answer to noisy feedback. "
             "Chapter 18 named the problem — *is 0.2% a better configuration or "
             "a lucky initialization?* — and this is the fix: train each "
             "configuration twice and average.\n\n"
             "**`overwrite=False`** resumes a crashed search from the trial logs "
             "on disk. Set the directory somewhere durable before starting a "
             "multi-day run."),

            ("h2", "Searching"),
            ("py", """callbacks = [keras.callbacks.EarlyStopping(monitor="val_loss", patience=5)]

tuner.search(
    x_train, y_train,
    batch_size=128,
    epochs=100,
    validation_data=(x_val, y_val),
    callbacks=callbacks,
    verbose=2,
)"""),
            ("warn",
             "Never pass the test set as `validation_data` here.** You would "
             "overfit to it immediately, and every number you report afterwards "
             "would be fiction.\n\n"
             "`epochs=100` with `EarlyStopping` — you do not know in advance how "
             "many epochs each configuration needs, so give a generous budget "
             "and let the callback cut each run short."),

            ("h2", "The results"),
            ("py", """tuner.results_summary(num_trials=5)

best_hps = tuner.get_best_hyperparameters(4)
for i, hp in enumerate(best_hps):
    print(f"{i}: {hp.values}")"""),

            ("h2", "Retraining properly"),
            ("py", """def get_best_epoch(hp):
    model = build_model(hp)
    cb = [keras.callbacks.EarlyStopping(monitor="val_loss", mode="min",
                                        patience=10)]
    history = model.fit(x_train, y_train,
                        validation_data=(x_val, y_val),
                        epochs=100, batch_size=128, callbacks=cb, verbose=0)
    v = history.history["val_loss"]
    best = int(np.argmin(v)) + 1
    print(f"  best epoch: {best}")
    return best

def get_best_trained_model(hp):
    best_epoch = get_best_epoch(hp)
    model = build_model(hp)
    model.fit(x_train_full, y_train_full, batch_size=128,
              epochs=int(best_epoch * 1.2), verbose=0)
    return model

best_models = []
for i, hp in enumerate(best_hps):
    print(f"config {i}: {hp.values}")
    m = get_best_trained_model(hp)
    acc = m.evaluate(x_test, y_test, verbose=0)[1]
    print(f"  test accuracy: {acc:.4f}\\n")
    best_models.append(m)"""),
            ("md",
             "Two details, both easy to skip:\n\n"
             "**A much higher patience** (10, not 5) in this second pass. The "
             "aggressive patience saved time during the search and may have left "
             "models underfitted.\n\n"
             "**`* 1.2` epochs, and training on the full data** — validation "
             "folded back in, because there are no more hyperparameter decisions "
             "to make with it."),

            ("h2", "The shortcut, and the warning"),
            ("py", """quick = tuner.get_best_models(4)
print("reloaded from the search, without retraining:")
for i, m in enumerate(quick):
    print(f"  {i}: {m.evaluate(x_test, y_test, verbose=0)[1]:.4f}")
print()
print("Slightly worse than a proper retrain, and one line.")"""),
            ("warn",
             "Validation-set overfitting.** You have been updating "
             "hyperparameters using a signal computed on validation data — which "
             "means you have been **training them on it**, and they will overfit "
             "to it.\n\n"
             "That is the entire purpose of keeping a separate test set, and it "
             "is why the test set is a **one-shot instrument**."),

            ("h2", "Premade search spaces"),
            ("py", """print("KerasTuner ships tunable versions of the Keras Applications:")
print("  kt.applications.HyperXception")
print("  kt.applications.HyperResNet")
print()
print("Add data, run the search, get a pretty good model. Worth knowing")
print("because the higher-level decisions -- 'should I use residual")
print("connections throughout?' -- generalize across tasks in a way that")
print("'how many units in layer 2' never does.")"""),
        ],
        "takeaways": [
            "Replace constants with ranges; search learning rates on a **log "
            "scale**.",
            "`executions_per_trial` averages away the noise in the feedback "
            "signal.",
            "Retrain the winners with higher patience, on the full data, for "
            "~20% more epochs.",
            "**Tuning trains hyperparameters on the validation set.** The test "
            "set is a one-shot instrument.",
        ],
    },

    {
        "file": "02_ensembling_and_weights.ipynb",
        "title": "Ensembling, and why diversity beats quality",
        "lede": "A weighted average with weights learned on validation data — and the "
                "experiment showing that a worse, different model helps more than a "
                "better, similar one.",
        "needs": "CPU — about 8 minutes",
        "section": "02 — Model ensembling",
        "cells": [
            ("h2", "Four different models"),
            ("py", """import keras
from keras import layers
import numpy as np
from keras.datasets import cifar10

(x, y), (xt, yt) = cifar10.load_data()
x = x.astype("float32") / 255
xt = xt.astype("float32") / 255
y, yt = y.ravel(), yt.ravel()

x_tr, y_tr = x[:40000], y[:40000]
x_val, y_val = x[40000:], y[40000:]

def small_convnet(seed):
    keras.utils.set_random_seed(seed)
    m = keras.Sequential([
        layers.Conv2D(32, 3, activation="relu", padding="same"),
        layers.MaxPooling2D(2),
        layers.Conv2D(64, 3, activation="relu", padding="same"),
        layers.MaxPooling2D(2),
        layers.GlobalAveragePooling2D(),
        layers.Dense(10, activation="softmax"),
    ])
    m.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

def wide_mlp(seed):
    keras.utils.set_random_seed(seed)
    m = keras.Sequential([
        layers.Flatten(),
        layers.Dense(512, activation="relu"),
        layers.Dropout(0.4),
        layers.Dense(256, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ])
    m.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

def separable_convnet(seed):
    keras.utils.set_random_seed(seed)
    m = keras.Sequential([
        layers.Conv2D(32, 3, activation="relu", padding="same"),
        layers.SeparableConv2D(64, 3, activation="relu", padding="same"),
        layers.MaxPooling2D(2),
        layers.SeparableConv2D(128, 3, activation="relu", padding="same"),
        layers.GlobalAveragePooling2D(),
        layers.Dense(10, activation="softmax"),
    ])
    m.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m"""),
            ("py", """from sklearn.ensemble import RandomForestClassifier

models, val_preds, test_preds, names = [], [], [], []

for fn, name in [(small_convnet, "convnet"),
                 (wide_mlp, "mlp"),
                 (separable_convnet, "separable")]:
    m = fn(0)
    m.fit(x_tr, y_tr, epochs=8, batch_size=128, verbose=0)
    val_preds.append(m.predict(x_val, verbose=0))
    test_preds.append(m.predict(xt, verbose=0))
    names.append(name)
    print(f"{name:12s} val acc "
          f"{(val_preds[-1].argmax(1) == y_val).mean():.4f}")

# A genuinely different KIND of model.
rf = RandomForestClassifier(n_estimators=120, n_jobs=-1, random_state=0)
rf.fit(x_tr.reshape(len(x_tr), -1)[:15000], y_tr[:15000])
val_preds.append(rf.predict_proba(x_val.reshape(len(x_val), -1)))
test_preds.append(rf.predict_proba(xt.reshape(len(xt), -1)))
names.append("random forest")
print(f"{'random forest':12s} val acc "
      f"{(val_preds[-1].argmax(1) == y_val).mean():.4f}")"""),
            ("md",
             "The random forest is deliberately the **worst** member. Whether it "
             "helps anyway is the experiment."),

            ("h2", "A plain average"),
            ("py", """V = np.stack(val_preds)     # (models, samples, classes)
T = np.stack(test_preds)

simple = T.mean(axis=0)
print(f"simple average: test acc {(simple.argmax(1) == yt).mean():.4f}")
for n, p in zip(names, T):
    print(f"  {n:14s} {(p.argmax(1) == yt).mean():.4f}")"""),
            ("md",
             "A plain average only works if the members are **roughly equally "
             "good**. With a much weaker member it can be worse than the best "
             "single model."),

            ("h2", "Weights learned on validation data"),
            ("py", """from scipy.optimize import minimize

def neg_acc(w):
    w = np.abs(w); w = w / w.sum()
    blend = np.tensordot(w, V, axes=(0, 0))
    return -(blend.argmax(1) == y_val).mean()

w0 = np.ones(len(V)) / len(V)
res = minimize(neg_acc, w0, method="Nelder-Mead",
               options={"maxiter": 400, "xatol": 1e-3, "fatol": 1e-4})
w = np.abs(res.x); w = w / w.sum()

print("learned weights:")
for n, wi in zip(names, w):
    print(f"  {n:14s} {wi:.3f}")

weighted = np.tensordot(w, T, axes=(0, 0))
print(f"\\nweighted average: test acc {(weighted.argmax(1) == yt).mean():.4f}")"""),
            ("md",
             "**Nelder-Mead over the validation set** — exactly what chapter 18 "
             "suggests. The weak member gets a small weight rather than being "
             "dropped, which is the interesting part."),

            ("h2", "Does the weak, different model earn its place?"),
            ("py", """def blend_acc(indices, weights=None):
    sub = T[list(indices)]
    if weights is None:
        weights = np.ones(len(sub)) / len(sub)
    b = np.tensordot(np.array(weights) / np.sum(weights), sub, axes=(0, 0))
    return (b.argmax(1) == yt).mean()

nn_only = blend_acc([0, 1, 2])
all_four = blend_acc([0, 1, 2, 3], w)
print(f"three neural networks:        {nn_only:.4f}")
print(f"+ the (worse) random forest:  {all_four:.4f}")
print(f"difference:                   {all_four - nn_only:+.4f}")"""),
            ("md",
             "Chollet's Higgs Boson story, reproduced in miniature. A "
             "regularized greedy forest with a **significantly worse** score "
             "improved the ensemble by a large factor, because it was so "
             "different — it carried information no other model had.\n\n"
             "**It is not about how good your best model is; it is about the "
             "diversity of your candidates.**"),

            ("h2", "Measuring diversity directly"),
            ("py", """import matplotlib.pyplot as plt

errs = np.stack([(p.argmax(1) != yt) for p in T])
n = len(names)
overlap = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        both = (errs[i] & errs[j]).sum()
        either = (errs[i] | errs[j]).sum()
        overlap[i, j] = both / max(either, 1)

plt.figure(figsize=(6.5, 5.4))
plt.imshow(overlap, cmap="Reds", vmin=0, vmax=1)
plt.xticks(range(n), names, rotation=45, ha="right")
plt.yticks(range(n), names)
for i in range(n):
    for j in range(n):
        plt.text(j, i, f"{overlap[i,j]:.2f}", ha="center", va="center",
                 fontsize=9, color="w" if overlap[i,j] > .5 else "k")
plt.colorbar(label="error overlap (Jaccard)")
plt.title("Models that fail on the SAME samples add nothing")
plt.tight_layout(); plt.show()"""),
            ("md",
             "**This is the diagnostic to run before adding a model to an "
             "ensemble.** A high overlap means the new member is biased the same "
             "way as an existing one, and the ensemble will keep that bias.\n\n"
             "It also explains why ensembling the same network from different "
             "seeds is *largely not worth doing*: the overlap is near 1."),

            ("h2", "The cost"),
            ("py", """print(f"{'':22s} {'accuracy':>9s} {'inference cost':>16s}")
print("-" * 50)
print(f"{'best single model':22s} "
      f"{max((p.argmax(1) == yt).mean() for p in T):>9.4f} {'1x':>16s}")
print(f"{'4-model ensemble':22s} "
      f"{(weighted.argmax(1) == yt).mean():>9.4f} {'4x':>16s}")
print()
print("Kaggle does not charge you for inference. Production does.")"""),
        ],
        "takeaways": [
            "Weighted averaging with weights learned on validation data is a "
            "very strong baseline.",
            "A **worse but different** model can lift the ensemble more than a "
            "better, similar one.",
            "Measure error overlap before adding a member; near-identical "
            "failures add nothing.",
            "The accuracy gain costs N× inference — which Kaggle does not charge "
            "for and production does.",
        ],
    },

    {
        "file": "03_data_and_model_parallel_jax.ipynb",
        "title": "Distributing training across devices",
        "lede": "Data parallelism in one line, model parallelism in a DeviceMesh and a "
                "LayoutMap — and the sharding you should verify before paying for a long "
                "run.",
        "needs": "Multiple GPUs or a TPU · runs single-device with reduced output",
        "section": "03 — Scaling up with multiple devices",
        "cells": [
            ("h2", "What is available"),
            ("py", """import os
os.environ["KERAS_BACKEND"] = "jax"     # BEFORE importing keras

import keras
print("backend:", keras.backend.backend())
print("devices:", keras.distribution.list_devices())"""),
            ("md",
             "The chapter is blunt about the backend: **JAX is the most "
             "performant and most scalable, by a mile**, and using anything else "
             "for large-scale distributed training wastes compute you are paying "
             "for."),

            ("h2", "Two kinds of parallelism, for two different problems"),
            ("py", """print("DATA PARALLELISM")
print("  one model replicated on every device")
print("  each replica processes a different sub-batch")
print("  gradients averaged; all replicas stay identical (synchronous)")
print("  -> for SPEED. Requires the model to fit on one device.")
print()
print("MODEL PARALLELISM")
print("  one model split across devices, all working on the same batch")
print("  -> for SIZE. Used when the model fits nowhere.")
print()
print("They compose: split across 4, replicate that split twice = 8 devices.")"""),

            ("h2", "Data parallelism is one line"),
            ("py", """keras.distribution.set_distribution(keras.distribution.DataParallel())

# ...or naming the devices explicitly:
# keras.distribution.set_distribution(
#     keras.distribution.DataParallel(["gpu:0", "gpu:1"]))

print("set. Nothing else in your code changes.")"""),
            ("warn",
             "Before creating the model.** Setting the distribution afterwards "
             "silently does nothing — the same ordering trap as "
             "`set_dtype_policy` and `KERAS_BACKEND`."),

            ("h2", "What to actually expect"),
            ("py", """for n, speedup in [(2, 2.0), (4, 3.8), (8, 7.3)]:
    print(f"{n} GPUs -> about {speedup}x   "
          f"({speedup/n:.0%} efficiency)")
print()
print("Merging the weight deltas from different devices takes time,")
print("and the loss grows with device count.")
print()
print("These numbers assume a global batch large enough to keep every")
print("GPU at full capacity. Too small and the speedup collapses.")"""),

            ("h2", "A model too large for one device"),
            ("py", """from keras import layers

model = keras.Sequential([
    keras.layers.Input(shape=(16000,)),
    keras.layers.Dense(64000, activation="relu"),
    keras.layers.Dense(8000, activation="sigmoid"),
])
print(f"{model.count_params():,} parameters")
print(f"{model.count_params() * 4 / 1e9:.1f} GB in float32, weights alone")
print()
for v in model.variables:
    print(f"  {v.path:34s} {tuple(v.shape)}")"""),

            ("h2", "The DeviceMesh"),
            ("py", """device_mesh = keras.distribution.DeviceMesh(
    shape=(2, 4),
    axis_names=["data", "model"],
)
print(device_mesh)
print()
print("Two devices along axis 0 ('data'): two replicas.")
print("Four along axis 1 ('model'): each replica split across four.")
print("Total: eight devices.")"""),
            ("note",
             "A mesh need not be 2-D, but in practice you will only ever see 1-D "
             "and 2-D. Naming the axes is not decoration — the `LayoutMap` "
             "refers to them by name."),

            ("h2", "The LayoutMap"),
            ("py", """layout_map = keras.distribution.LayoutMap(device_mesh)
layout_map["sequential/dense/kernel"] = (None, "model")
layout_map["sequential/dense/bias"] = ("model",)
layout_map["sequential/dense_1/kernel"] = (None, "model")
layout_map["sequential/dense_1/bias"] = ("model",)

print("None    -> replicate along this dimension")
print("'model' -> shard across the devices of the 'model' mesh axis")
print()
print("Rule of thumb for a simple model:")
print("  shard the LAST dimension along 'model'; replicate everything else.")"""),
            ("py", """model_parallel = keras.distribution.ModelParallel(
    layout_map=layout_map,
    batch_dim_name="data",
)
keras.distribution.set_distribution(model_parallel)

print("Once set, NOTHING else changes -- the model definition and the")
print("training code are identical, whether you use fit() or your own loop.")"""),

            ("h2", "Verify the sharding before paying for a long run"),
            ("py", """# Rebuild under the distribution so the layout takes effect.
model = keras.Sequential([
    keras.layers.Input(shape=(16000,)),
    keras.layers.Dense(64000, activation="relu"),
    keras.layers.Dense(8000, activation="sigmoid"),
])

try:
    print(model.layers[0].kernel.value.sharding)
    import jax
    v = model.layers[0].kernel.value
    jax.debug.visualize_sharding(v.shape, v.sharding)
except Exception as e:
    print("(single-device run -- nothing to shard)", e)"""),
            ("md",
             "**A silently wrong layout still trains — just slowly, and on the "
             "wrong devices.** Print the sharding, or visualise it, before "
             "committing to a run you will be billed for."),

            ("h2", "The input pipeline, which becomes the bottleneck"),
            ("py", """print("Always pass a tf.data.Dataset (NumPy arrays get converted anyway).")
print("Always prefetch:")
print("    dataset = dataset.prefetch(tf.data.AUTOTUNE)")
print()
print("On TPU, also cache if the dataset fits in VM memory:")
print("    dataset = dataset.cache()")
print()
print("A starved input pipeline turns eight expensive GPUs into eight")
print("expensive IDLE GPUs -- and that is the most common way a")
print("distributed run underperforms.")"""),

            ("h2", "TPUs, and step fusing"),
            ("py", """print("TPU v2 is free in Colab (Runtime -> Change Runtime Type).")
print("~15x an NVIDIA P100; ~3x more cost-effective than GPU on average.")
print()
print("With the JAX backend, the same set_distribution() call is all")
print("you need -- again, BEFORE creating the model.")
print()
print("Small models underutilize a TPU. Keeping the cores busy can need")
print("batches upward of 10,000 samples, which also means raising the")
print("learning rate: fewer updates, each more accurate.")
print()
print("Or use step fusing, which keeps the batch reasonable:")
print("    model.compile(..., steps_per_execution=8)")"""),
        ],
        "takeaways": [
            "Data parallelism is for speed and needs the model to fit; model "
            "parallelism is for size.",
            "Set the distribution **before** creating the model.",
            "8 GPUs give about 7.3×, and only with a large enough global batch.",
            "Verify the sharding, and prefetch — a starved pipeline is the "
            "commonest way a distributed run underperforms.",
        ],
    },

    {
        "file": "04_mixed_precision_and_loss_scaling.ipynb",
        "title": "Lower precision, measured",
        "lede": "float16 inference, mixed-precision training, and the loss scaling "
                "without which small gradients round to zero.",
        "needs": "GPU recommended — about 10 minutes",
        "section": "04 — Lower-precision computation",
        "cells": [
            ("h2", "What precision actually means"),
            ("py", """import numpy as np

for dtype, name in [(np.float16, "float16"), (np.float32, "float32"),
                    (np.float64, "float64")]:
    info = np.finfo(dtype)
    print(f"{name:9s} bits {info.bits:2d}   eps {info.eps:.2e}   "
          f"max {info.max:.2e}   tiny {info.tiny:.2e}")"""),
            ("md",
             "**`eps` is the resolution**: the smallest distance between two "
             "representable numbers near 1. float16 gives about 1e-3, float32 "
             "about 1e-7, float64 about 1e-16.\n\n"
             "Typical learning rates are 1e-3 and typical weight updates around "
             "1e-6. **float16 cannot represent that update at all.**"),

            ("h2", "Representable numbers are not evenly spaced"),
            ("py", """import matplotlib.pyplot as plt

def spacing(dtype, values):
    return [float(np.spacing(dtype(v))) for v in values]

vals = np.logspace(-3, 4, 40)
plt.figure(figsize=(7, 4.2))
plt.loglog(vals, spacing(np.float16, vals), "o-", ms=3, label="float16")
plt.loglog(vals, spacing(np.float32, vals), "s-", ms=3, label="float32")
plt.xlabel("magnitude"); plt.ylabel("gap to the next representable number")
plt.legend(); plt.title("Larger numbers have lower precision")
plt.show()"""),
            ("md",
             "There are as many representable values between 2^N and 2^(N+1) as "
             "between 1 and 2, for any N. **The error of converting a number to "
             "floating point grows with its magnitude** — which is why "
             "normalizing your inputs was never only about gradients."),

            ("h2", "float16 or bfloat16"),
            ("py", """print(f"{'':16s} {'exponent':>9s} {'mantissa':>9s} {'sign':>5s}")
print(f"{'float16':16s} {5:>9d} {10:>9d} {1:>5d}")
print(f"{'bfloat16':16s} {8:>9d} {7:>9d} {1:>5d}")
print(f"{'float32':16s} {8:>9d} {23:>9d} {1:>5d}")
print()
print("bfloat16 has float32's RANGE with far less resolution.")
print("Some devices -- TPUs especially -- are better optimized for it.")
print("It is a one-line experiment: try both, keep the faster.")"""),

            ("h2", "float16 inference"),
            ("py", """import keras
from keras import layers
import time

keras.config.set_dtype_policy("float32")
(x, y), (xt, yt) = keras.datasets.mnist.load_data()
x = x.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

def build():
    keras.utils.set_random_seed(0)
    m = keras.Sequential([layers.Dense(512, activation="relu"),
                          layers.Dense(512, activation="relu"),
                          layers.Dense(10, activation="softmax")])
    m.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

fp32 = build()
fp32.fit(x, y, epochs=3, batch_size=128, verbose=0)

def bench(m, data, n=10, warmup=3):
    for _ in range(warmup):
        m.predict(data, verbose=0)
    t0 = time.perf_counter()
    for _ in range(n):
        m.predict(data, verbose=0)
    return (time.perf_counter() - t0) / n

batch = xt[:2048]
t32 = bench(fp32, batch)
print(f"float32: {t32*1000:6.1f} ms   acc {fp32.evaluate(xt, yt, verbose=0)[1]:.4f}")"""),
            ("warn",
             "Warm up before timing.** The first call compiles; timing it "
             "measures the compiler, not the model."),

            ("h2", "Mixed precision for training"),
            ("py", """keras.config.set_dtype_policy("mixed_float16")

mixed = build()
t0 = time.time()
mixed.fit(x, y, epochs=3, batch_size=128, verbose=0)
t_mixed = time.time() - t0

print(f"mixed_float16 training: {t_mixed:.1f}s   "
      f"acc {mixed.evaluate(xt, yt, verbose=0)[1]:.4f}")
print()
for layer in mixed.layers:
    print(f"{layer.name:12s} compute {layer.compute_dtype:12s} "
          f"variables {layer.variable_dtype}")"""),
            ("md",
             "**`compute_dtype` is float16; `variable_dtype` stays float32.** "
             "Most of the forward pass runs on half-precision copies of the "
             "weights; the weights themselves are stored and updated in full "
             "precision, so they can receive accurate small updates.\n\n"
             "Some operations are numerically unstable in float16 — notably "
             "softmax and crossentropy. Pass `dtype=\"float32\"` to opt a "
             "specific layer out."),

            ("h2", "Loss scaling"),
            ("py", """import numpy as np

# Gradients that vanish in float16.
tiny = np.array([1e-4, 1e-5, 1e-6, 1e-7, 1e-8], dtype=np.float32)
print(f"{'value':>10s} {'as float16':>14s} {'x 1024, as float16':>22s}")
for v in tiny:
    print(f"{v:10.1e} {np.float16(v):>14.1e} "
          f"{np.float16(v * 1024):>22.1e}")"""),
            ("out", """  1.0e-07        1.2e-07                 1.0e-04
  1.0e-08        0.0e+00                 1.0e-05"""),
            ("md",
             "**1e-8 rounds to zero in float16, and multiplying the loss by 1024 "
             "rescues it.** Gradients are proportional to the loss, so a large "
             "scalar factor moves them into the representable range; the "
             "optimizer divides it back out before updating."),
            ("py", """keras.utils.set_random_seed(0)
m = keras.Sequential([layers.Dense(512, activation="relu"),
                      layers.Dense(512, activation="relu"),
                      layers.Dense(10, activation="softmax")])
m.compile(
    optimizer=keras.optimizers.LossScaleOptimizer(
        keras.optimizers.Adam(learning_rate=1e-3)),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
m.fit(x, y, epochs=3, batch_size=128, verbose=0)
print("with LossScaleOptimizer:", m.evaluate(xt, yt, verbose=0)[1])
print()
print("A fixed factor also works:")
print("  keras.optimizers.Adam(learning_rate=1e-3, loss_scale_factor=10)")
print("but LossScaleOptimizer adapts -- and the right value changes")
print("over the course of training.")"""),

            ("h2", "float8: why it is not simply the next step"),
            ("py", """print("float16 is the LAST level that 'just works'.")
print()
print("At float8 you lose too much information. Keras has a built-in")
print("implementation, but it:")
print("  - covers only Dense, EinsumDense, and Embedding")
print("  - tracks past activations to rescale each step")
print("  - overrides part of the backward pass to do the same for gradients")
print()
print("That machinery has a cost. Below roughly 5 BILLION parameters, or")
print("on anything short of an H100, the cost exceeds the benefit and you")
print("get a SLOWDOWN. float8 is rare outside foundation-model training.")"""),

            ("h2", "Restore the default before continuing"),
            ("py", """keras.config.set_dtype_policy("float32")
print("back to float32")"""),
            ("note",
             "The dtype policy is **global**. Leaving it set affects every model "
             "built afterwards in the same process, which is a confusing "
             "afternoon if you forget."),
        ],
        "takeaways": [
            "float16 resolves to about 1e-3; typical weight updates are 1e-6, so "
            "training in it alone fails.",
            "Mixed precision computes in float16 and stores variables in "
            "float32 — most of the speed, none of the instability.",
            "**Loss scaling** rescues gradients that would round to zero; "
            "`LossScaleOptimizer` adapts the factor.",
            "float8 needs 5B+ parameters and recent hardware to pay for itself.",
        ],
    },

    {
        "file": "05_int8_quantization.ipynb",
        "title": "int8 quantization, by hand and then properly",
        "lede": "The scale-and-unscale trick that makes int8 matmul lossless enough — "
                "implemented from scratch, then applied with one method call.",
        "needs": "CPU — about 4 minutes",
        "section": "04 — Faster inference with quantization",
        "cells": [
            ("h2", "Why casting naively fails"),
            ("py", """from keras import ops
import numpy as np

x = ops.array([[0.1, 0.9], [1.2, -0.8]])
kernel = ops.array([[-0.1, -2.2], [1.1, 0.7]])

print("naive cast to int8:")
print(ops.convert_to_numpy(ops.cast(x, "int8")))
print()
print("Everything below 1.0 becomes zero. Total loss of information.")"""),

            ("h2", "abs-max scaling"),
            ("py", """def abs_max_quantize(value):
    abs_max = ops.max(ops.abs(value), keepdims=True)
    scale = ops.divide(127, abs_max + 1e-7)
    scaled_value = value * scale
    scaled_value = ops.clip(ops.round(scaled_value), -127, 127)
    scaled_value = ops.cast(scaled_value, dtype="int8")
    return scaled_value, scale

int_x, x_scale = abs_max_quantize(x)
int_kernel, kernel_scale = abs_max_quantize(kernel)

print("x as int8:     ", ops.convert_to_numpy(int_x))
print("kernel as int8:", ops.convert_to_numpy(int_kernel))
sx = ops.convert_to_numpy(x_scale).item()
sk = ops.convert_to_numpy(kernel_scale).item()
print(f"scales: {sx:.2f}, {sk:.2f}")"""),
            ("md",
             "The tensor is spread across the full **[-127, 127]** range before "
             "casting. `+ 1e-7` avoids dividing by zero, and **rounding and "
             "clipping before the cast** is more accurate than casting "
             "directly."),

            ("h2", "The matmul, and unscaling"),
            ("py", """int_y = ops.matmul(int_x, int_kernel)
y = ops.cast(int_y, dtype="float32") / (x_scale * kernel_scale)

print("quantized result:")
print(ops.convert_to_numpy(y))
print()
print("float32 result:")
print(ops.convert_to_numpy(ops.matmul(x, kernel)))
print()
err = np.abs(ops.convert_to_numpy(y) - ops.convert_to_numpy(ops.matmul(x, kernel)))
print(f"max absolute error: {err.max():.4f}")"""),
            ("md",
             "**matmul is linear**, so the final unscaling cancels the initial "
             "scaling exactly. Any error comes **only from the rounding** when "
             "casting to int8 — not from the multiplication.\n\n"
             "The added operations are abs, max, clip, cast, divide, multiply — "
             "all elementwise and fast, against a matmul that is now int8 and "
             "can be considerably faster than even float16."),

            ("h2", "How the error scales with matrix size"),
            ("py", """import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
sizes = [8, 32, 128, 512]
errs = []
for n in sizes:
    a = ops.array(rng.normal(size=(n, n)).astype("float32"))
    b = ops.array(rng.normal(size=(n, n)).astype("float32"))
    ia, sa = abs_max_quantize(a)
    ib, sb = abs_max_quantize(b)
    q = ops.cast(ops.matmul(ia, ib), "float32") / (sa * sb)
    f = ops.matmul(a, b)
    rel = np.abs(ops.convert_to_numpy(q - f)).mean() / np.abs(
        ops.convert_to_numpy(f)).mean()
    errs.append(rel)
    print(f"{n:4d}x{n:<4d} mean relative error {rel:.4f}")

plt.figure(figsize=(6, 3.8))
plt.semilogx(sizes, errs, "o-")
plt.xlabel("matrix size"); plt.ylabel("mean relative error")
plt.title("Quantization error stays small as the matmul grows")
plt.show()"""),
            ("md",
             "The error does not blow up with size, because the rounding errors "
             "are independent and largely cancel in the sum. **That is what "
             "makes the technique usable on real models** rather than only on "
             "2×2 examples."),

            ("h2", "One method call"),
            ("py", """import keras, os
from keras import layers

(x_tr, y_tr), (xt, yt) = keras.datasets.mnist.load_data()
x_tr = x_tr.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

keras.utils.set_random_seed(0)
model = keras.Sequential([layers.Dense(512, activation="relu"),
                          layers.Dense(256, activation="relu"),
                          layers.Dense(10, activation="softmax")])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(x_tr, y_tr, epochs=4, batch_size=128, verbose=0)
model.save("fp32.keras")
base_acc = model.evaluate(xt, yt, verbose=0)[1]

q = keras.saving.load_model("fp32.keras")
q.quantize("int8")
q.save("int8.keras")
q_acc = q.evaluate(xt, yt, verbose=0)[1]

fp = os.path.getsize("fp32.keras") / 1e6
qs = os.path.getsize("int8.keras") / 1e6
print(f"float32: {fp:6.2f} MB   accuracy {base_acc:.4f}")
print(f"int8:    {qs:6.2f} MB   accuracy {q_acc:.4f}")
print(f"\\n{fp/qs:.1f}x smaller, accuracy cost {base_acc - q_acc:+.4f}")"""),
            ("warn",
             "`quantize()` converts the weights **in place**.** It is a one-way "
             "operation on that model object — keep the float32 file, as done "
             "above."),

            ("h2", "Where the error lands"),
            ("py", """import numpy as np

p32 = model.predict(xt, verbose=0)
p8 = q.predict(xt, verbose=0)

disagree = (p32.argmax(1) != p8.argmax(1))
print(f"{disagree.sum()} of {len(xt)} predictions changed "
      f"({disagree.mean():.2%})")

conf32 = p32.max(1)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
a1.hist(conf32[~disagree], bins=40, alpha=.7, label="unchanged", density=True)
a1.hist(conf32[disagree], bins=40, alpha=.7, label="changed", density=True)
a1.set_xlabel("float32 confidence"); a1.legend()
a1.set_title("Disagreements cluster at LOW confidence")

a2.scatter(p32.max(1), p8.max(1), s=2, alpha=.2)
a2.plot([0, 1], [0, 1], "k--", lw=1)
a2.set_xlabel("float32 confidence"); a2.set_ylabel("int8 confidence")
a2.set_title("Confidence is largely preserved")
plt.tight_layout(); plt.show()"""),
            ("md",
             "**The predictions that change are the ones the model was unsure "
             "about anyway.** That is the reassuring shape — but measure it on "
             "*your* data. It is not guaranteed, and a model whose "
             "high-confidence predictions move under quantization is telling you "
             "something."),

            ("h2", "Which layers it covers"),
            ("py", """print("int8 quantization is built into:")
print("  Dense, EinsumDense, Embedding")
print()
print("EinsumDense is what MultiHeadAttention uses -- which means")
print("int8 inference works for any Transformer-based model.")
print()
print("Convolutions are not covered by model.quantize(). For vision")
print("models, look at post-training quantization in the deployment")
print("runtime you are targeting.")"""),
        ],
        "takeaways": [
            "Scale into [-127, 127], cast, multiply, unscale — matmul is linear "
            "so the scaling cancels.",
            "Rounding is the only source of error, and it does not grow with "
            "matrix size.",
            "`model.quantize(\"int8\")` is one line and **in place** — keep the "
            "float32 file.",
            "Disagreements cluster at low confidence, but verify that on your own "
            "data.",
        ],
    },
]
