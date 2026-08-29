# -*- coding: utf-8 -*-
"""Chapter 13 notebooks — Timeseries Forecasting."""

DECK = "ch13"

NOTEBOOKS = [
    {
        "file": "01_jena_data_and_baseline.ipynb",
        "title": "The Jena weather data, and a baseline nothing beats for a while",
        "lede": "Eight years of readings every ten minutes, a windowed dataset, and a "
                "common-sense baseline that several neural networks will fail to beat.",
        "needs": "CPU — about 3 minutes",
        "section": "01 — A temperature-forecasting example",
        "cells": [
            ("h2", "The data"),
            ("py", """import os
import numpy as np
import keras

fname = keras.utils.get_file(
    origin="https://storage.googleapis.com/tensorflow/tf-keras-datasets/"
           "jena_climate_2009_2016.csv.zip",
    fname="jena_climate_2009_2016.csv.zip", extract=True)
csv_path = os.path.join(fname, "jena_climate_2009_2016.csv")

with open(csv_path) as f:
    data = f.read()

lines = data.split("\\n")
header = lines[0].split(",")
lines = [l for l in lines[1:] if l]
print(len(header), "columns,", len(lines), "rows")
print(header)"""),
            ("py", """temperature = np.zeros((len(lines),))
raw_data = np.zeros((len(lines), len(header) - 1))
for i, line in enumerate(lines):
    values = [float(x) for x in line.split(",")[1:]]
    temperature[i] = values[1]
    raw_data[i, :] = values[:]

print(raw_data.shape)"""),

            ("h2", "Look at it before modelling it"),
            ("py", """import matplotlib.pyplot as plt

fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 6))
a1.plot(range(len(temperature)), temperature, lw=.4)
a1.set_title("Temperature, all eight years"); a1.set_ylabel("degC")
a2.plot(range(1440), temperature[:1440], lw=1)
a2.set_title("The first ten days"); a2.set_xlabel("10-minute steps")
plt.tight_layout(); plt.show()"""),
            ("md",
             "Two periodicities, immediately visible: **yearly**, and "
             "**daily**. The yearly one is why a naive *predict the annual "
             "average* model would be poor, and the daily one is why *predict "
             "the last value* will be surprisingly good."),

            ("h2", "The split, and why it is not random"),
            ("py", """num_train_samples = int(0.5 * len(raw_data))
num_val_samples = int(0.25 * len(raw_data))
num_test_samples = len(raw_data) - num_train_samples - num_val_samples

print(f"train {num_train_samples}   validation {num_val_samples}   "
      f"test {num_test_samples}")"""),
            ("warn",
             "Chronological, always.** The validation and test data must be "
             "*posterior* to the training data. A random split lets the model "
             "interpolate between readings it has already seen, and the score "
             "becomes meaningless — chapter 5's notebook 03 drew the picture."),

            ("h2", "Normalizing with training statistics"),
            ("py", """mean = raw_data[:num_train_samples].mean(axis=0)
std = raw_data[:num_train_samples].std(axis=0)
raw_data -= mean
raw_data /= std
print("normalized using the first half only")"""),

            ("h2", "Windowing"),
            ("py", """sampling_rate = 6      # one reading per hour
sequence_length = 120  # five days of history
delay = sampling_rate * (sequence_length + 24 - 1)   # target is 24h ahead
batch_size = 256

train_dataset = keras.utils.timeseries_dataset_from_array(
    raw_data[:-delay],
    targets=temperature[delay:],
    sampling_rate=sampling_rate,
    sequence_length=sequence_length,
    shuffle=True,
    batch_size=batch_size,
    start_index=0,
    end_index=num_train_samples)

val_dataset = keras.utils.timeseries_dataset_from_array(
    raw_data[:-delay], targets=temperature[delay:],
    sampling_rate=sampling_rate, sequence_length=sequence_length,
    shuffle=True, batch_size=batch_size,
    start_index=num_train_samples,
    end_index=num_train_samples + num_val_samples)

test_dataset = keras.utils.timeseries_dataset_from_array(
    raw_data[:-delay], targets=temperature[delay:],
    sampling_rate=sampling_rate, sequence_length=sequence_length,
    shuffle=True, batch_size=batch_size,
    start_index=num_train_samples + num_val_samples)

for samples, targets in train_dataset:
    print("samples shape:", samples.shape)
    print("targets shape:", targets.shape)
    break"""),
            ("out", """samples shape: (256, 120, 14)
targets shape: (256,)"""),
            ("md",
             "**120 timesteps × 14 features per sample**, one temperature as the "
             "target. `sampling_rate=6` means we keep one reading per hour, so "
             "120 steps is five days of history."),

            ("h2", "The baseline"),
            ("py", """def evaluate_naive_method(dataset):
    total_abs_err = 0.
    samples_seen = 0
    for samples, targets in dataset:
        # Column 1 is temperature; the last timestep is "now".
        preds = samples[:, -1, 1] * std[1] + mean[1]
        total_abs_err += np.sum(np.abs(preds - targets))
        samples_seen += samples.shape[0]
    return total_abs_err / samples_seen

print(f"validation MAE: {evaluate_naive_method(val_dataset):.2f} degC")
print(f"test MAE:       {evaluate_naive_method(test_dataset):.2f} degC")"""),
            ("out", """validation MAE: 2.44 degC
test MAE:       2.62 degC"""),
            ("md",
             "**Tomorrow will be like today.** Two and a half degrees of average "
             "error, from a model with no parameters.\n\n"
             "That number is the bar. Chapter 6 said to compute a common-sense "
             "baseline before believing anything; here it takes four lines and "
             "several of the neural networks in the next notebook will not "
             "clear it."),

            ("h2", "Understanding why the baseline is strong"),
            ("py", """h = temperature[::6]                 # hourly
diffs = np.abs(h[24:] - h[:-24])    # change over 24 hours

plt.figure(figsize=(7, 4))
plt.hist(diffs, bins=80)
plt.axvline(diffs.mean(), color="r", ls="--",
            label=f"mean {diffs.mean():.2f} degC")
plt.xlabel("|temperature change over 24 hours|"); plt.legend()
plt.title("Why 'tomorrow is like today' is hard to beat")
plt.show()"""),
            ("md",
             "The distribution is concentrated near zero. **Most of the time the "
             "temperature 24 hours from now is close to now**, and any model has "
             "to earn its keep on the tail."),
        ],
        "takeaways": [
            "Timeseries splits are chronological. Never random.",
            "`timeseries_dataset_from_array` handles windowing, sampling rate, "
            "and the target offset.",
            "**The naive baseline is 2.44 °C** and several neural networks will "
            "not beat it.",
            "Understand *why* the baseline is strong before trying to beat it.",
        ],
    },

    {
        "file": "02_dense_and_conv1d.ipynb",
        "title": "Two architectures that fail, and why each one fails",
        "lede": "A dense model and a 1D convnet on the same problem. Both lose to the "
                "baseline, for two different and instructive reasons.",
        "needs": "CPU — about 10 minutes",
        "section": "02 — Trying machine learning",
        "cells": [
            ("h2", "Setup"),
            ("md",
             "This notebook assumes the datasets from notebook 01. Re-run its "
             "cells, or import them if you have factored them out."),
            ("py", """import keras
from keras import layers
import numpy as np
import matplotlib.pyplot as plt

sequence_length, n_features = 120, 14
NAIVE_MAE = 2.44

def train(model, name, epochs=10):
    model.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
    cb = [keras.callbacks.ModelCheckpoint(f"jena_{name}.keras",
                                          save_best_only=True)]
    h = model.fit(train_dataset, epochs=epochs,
                  validation_data=val_dataset, callbacks=cb, verbose=2)
    best = keras.models.load_model(f"jena_{name}.keras")
    mae = best.evaluate(test_dataset, verbose=0)[1]
    print(f"\\n{name}: test MAE {mae:.2f} degC   (baseline {NAIVE_MAE})")
    return h, mae"""),

            ("h2", "A dense model"),
            ("py", """inputs = keras.Input(shape=(sequence_length, n_features))
x = layers.Flatten()(inputs)
x = layers.Dense(16, activation="relu")(x)
outputs = layers.Dense(1)(x)
dense_model = keras.Model(inputs, outputs)

h_dense, mae_dense = train(dense_model, "dense")"""),
            ("out", "dense: test MAE 2.6x — 2.7x degC   (baseline 2.44)"),
            ("md",
             "**Worse than doing nothing.** The reason is instructive: "
             "`Flatten` destroys the time axis. The model receives 1,680 "
             "numbers with no indication that some of them are recent and some "
             "are five days old.\n\n"
             "The simple solution is in its hypothesis space — it *could* learn "
             "to read the last temperature — but gradient descent has no reason "
             "to find that particular point among millions."),

            ("h2", "A 1D convnet"),
            ("py", """inputs = keras.Input(shape=(sequence_length, n_features))
x = layers.Conv1D(8, 24, activation="relu")(inputs)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(8, 12, activation="relu")(x)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(8, 6, activation="relu")(x)
x = layers.GlobalAveragePooling1D()(x)
outputs = layers.Dense(1)(x)
conv_model = keras.Model(inputs, outputs)

h_conv, mae_conv = train(conv_model, "conv")"""),
            ("out", "conv: test MAE 3.1x degC   (baseline 2.44)"),
            ("md",
             "**Worse still**, and for a different reason. Two properties that "
             "made convolution excellent on images are wrong here:\n\n"
             "**Translation invariance.** A convolution treats a pattern the "
             "same wherever it occurs. But weather from five days ago is not "
             "equivalent to weather from an hour ago — and *recency is exactly "
             "what matters*.\n\n"
             "**Pooling.** `MaxPooling1D` discards order within its window, and "
             "the most recent readings are the most informative ones being "
             "thrown away."),

            ("h2", "The comparison"),
            ("py", """plt.figure(figsize=(8, 4.6))
for h, name in [(h_dense, "dense"), (h_conv, "conv1d")]:
    plt.plot(h.history["val_mae"], lw=1.6, label=f"{name} — validation")
plt.axhline(NAIVE_MAE, color="k", ls="--", lw=1.4,
            label=f"naive baseline ({NAIVE_MAE})")
plt.xlabel("epoch"); plt.ylabel("validation MAE (degC)"); plt.legend()
plt.title("Neither architecture beats 'tomorrow is like today'")
plt.show()"""),

            ("h2", "The general lesson"),
            ("md",
             "> A model's hypothesis space containing the right answer does not "
             "mean gradient descent will find it.\n\n"
             "The dense model *could* have learned to output the last "
             "temperature. It did not, because nothing in its structure "
             "suggested that. **Architecture is a prior**, and the right prior "
             "for this problem is *the recent past matters more than the distant "
             "past* — which is precisely what a recurrent layer encodes, and "
             "what notebook 03 uses."),

            ("h2", "One thing worth trying"),
            ("py", """# Give the dense model the hint explicitly and watch what happens.
inputs = keras.Input(shape=(sequence_length, n_features))
recent = layers.Lambda(lambda t: t[:, -6:, :])(inputs)   # last six hours only
x = layers.Flatten()(recent)
x = layers.Dense(16, activation="relu")(x)
outputs = layers.Dense(1)(x)
recent_model = keras.Model(inputs, outputs)

h_recent, mae_recent = train(recent_model, "recent")"""),
            ("md",
             "Cutting the input to the last six hours usually **improves** the "
             "dense model, sometimes to near the baseline. Removing information "
             "made it better — which tells you the problem was never capacity. "
             "It was the prior."),
        ],
        "takeaways": [
            "`Flatten` destroys the time axis; the model cannot tell recent from "
            "distant.",
            "Convolution's translation invariance is **wrong** for forecasting, "
            "where recency is the signal.",
            "A hypothesis space containing the answer does not mean gradient "
            "descent will find it.",
            "Architecture is a prior. Choose one that matches the structure of "
            "the problem.",
        ],
    },

    {
        "file": "03_lstm_and_gru.ipynb",
        "title": "Recurrent layers, and the first model that beats the baseline",
        "lede": "A single LSTM layer with 16 units — fewer parameters than the dense "
                "model that failed, and the first thing in this chapter that works.",
        "needs": "CPU — about 15 minutes (GPU: 3 minutes)",
        "section": "03 — Recurrent neural networks",
        "cells": [
            ("h2", "A recurrent layer, written out"),
            ("py", """import numpy as np

timesteps, input_features, output_features = 100, 32, 64
inputs = np.random.random((timesteps, input_features))
state_t = np.zeros((output_features,))

W = np.random.random((output_features, input_features))
U = np.random.random((output_features, output_features))
b = np.random.random((output_features,))

successive_outputs = []
for input_t in inputs:
    output_t = np.tanh(np.dot(W, input_t) + np.dot(U, state_t) + b)
    successive_outputs.append(output_t)
    state_t = output_t          # <- the recurrence
final_output_sequence = np.stack(successive_outputs, axis=0)
print(final_output_sequence.shape)"""),
            ("md",
             "`state_t = output_t` is the entire idea. The output at each step "
             "depends on the input **and on everything that came before**, "
             "carried in a state vector. Chapter 15 will replace this loop with "
             "attention and get a large speed-up for exactly this reason: a loop "
             "cannot be parallelised."),

            ("h2", "An LSTM on Jena"),
            ("py", """import keras
from keras import layers
import matplotlib.pyplot as plt

NAIVE_MAE = 2.44
sequence_length, n_features = 120, 14

inputs = keras.Input(shape=(sequence_length, n_features))
x = layers.LSTM(16)(inputs)
outputs = layers.Dense(1)(x)
lstm_model = keras.Model(inputs, outputs)

lstm_model.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
cb = [keras.callbacks.ModelCheckpoint("jena_lstm.keras", save_best_only=True)]
h_lstm = lstm_model.fit(train_dataset, epochs=10,
                        validation_data=val_dataset, callbacks=cb, verbose=2)

best = keras.models.load_model("jena_lstm.keras")
mae_lstm = best.evaluate(test_dataset, verbose=0)[1]
print(f"\\nLSTM test MAE: {mae_lstm:.2f} degC   (baseline {NAIVE_MAE})")
print(f"parameters: {lstm_model.count_params():,}")"""),
            ("out", """LSTM test MAE: 2.3x degC   (baseline 2.44)
parameters: 2,001"""),
            ("md",
             "**Two thousand parameters**, against nearly 27,000 for the dense "
             "model that lost to doing nothing. Architecture, not capacity."),

            ("h2", "The picture"),
            ("py", """plt.figure(figsize=(8, 4.6))
plt.plot(h_lstm.history["mae"], lw=1, label="training")
plt.plot(h_lstm.history["val_mae"], lw=1.7, label="validation")
plt.axhline(NAIVE_MAE, color="k", ls="--", lw=1.4, label="naive baseline")
plt.xlabel("epoch"); plt.ylabel("MAE (degC)"); plt.legend()
plt.title("The first model in this chapter that beats doing nothing")
plt.show()"""),

            ("h2", "LSTM against GRU"),
            ("py", """def rnn(layer_cls, units=16, epochs=10, name=""):
    keras.utils.set_random_seed(0)
    i = keras.Input(shape=(sequence_length, n_features))
    x = layer_cls(units)(i)
    o = layers.Dense(1)(x)
    m = keras.Model(i, o)
    m.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
    cb = [keras.callbacks.ModelCheckpoint(f"jena_{name}.keras",
                                          save_best_only=True)]
    h = m.fit(train_dataset, epochs=epochs, validation_data=val_dataset,
              callbacks=cb, verbose=0)
    mae = keras.models.load_model(f"jena_{name}.keras").evaluate(
        test_dataset, verbose=0)[1]
    print(f"{name:6s} {m.count_params():>7,} params   test MAE {mae:.3f}")
    return h, mae

h_g, mae_g = rnn(layers.GRU, name="gru")
h_s, mae_s = rnn(layers.SimpleRNN, name="simple")"""),
            ("md",
             "**GRU** has three gates against LSTM's four — fewer parameters, "
             "usually comparable results, and it is what chapter 15 uses.\n\n"
             "**SimpleRNN** is the loop from the first cell with no gates at "
             "all. It performs poorly on sequences of this length, and that is "
             "the vanishing-gradient problem: information from 120 steps ago has "
             "to survive 120 multiplications. Gates give it a path that does not."),

            ("h2", "What the gates are for"),
            ("py", """print("SimpleRNN:  state_t = tanh(W.x + U.state + b)")
print()
print("LSTM adds a separate carry track, and three gates that control it:")
print("  forget gate  -- what to drop from the carry")
print("  input gate   -- what to add to it")
print("  output gate  -- what of it to expose")
print()
print("The carry can pass through many steps ~unchanged, which is")
print("exactly the residual-connection idea from chapter 9, applied to time.")"""),

            ("h2", "How far back does it actually look?"),
            ("py", """import numpy as np

for L in [24, 48, 120, 240]:
    ds = keras.utils.timeseries_dataset_from_array(
        raw_data[:-delay], targets=temperature[delay:],
        sampling_rate=6, sequence_length=L, shuffle=True, batch_size=256,
        start_index=0, end_index=num_train_samples)
    vds = keras.utils.timeseries_dataset_from_array(
        raw_data[:-delay], targets=temperature[delay:],
        sampling_rate=6, sequence_length=L, shuffle=True, batch_size=256,
        start_index=num_train_samples,
        end_index=num_train_samples + num_val_samples)
    keras.utils.set_random_seed(0)
    i = keras.Input(shape=(L, n_features))
    m = keras.Model(i, layers.Dense(1)(layers.GRU(16)(i)))
    m.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
    hh = m.fit(ds, epochs=6, validation_data=vds, verbose=0)
    print(f"history {L:3d} steps ({L//24} days): "
          f"best val MAE {min(hh.history['val_mae']):.3f}")"""),
            ("md",
             "More history is not monotonically better. Beyond a few days the "
             "extra steps are mostly noise, and the model pays for them in "
             "training time and in gradient path length. **The window length is "
             "a hyperparameter**, and chapter 18's tuner would find it for you."),
        ],
        "takeaways": [
            "A recurrent layer carries state forward: `state_t = output_t`.",
            "A 2,000-parameter LSTM beats a 27,000-parameter dense model here — "
            "prior, not capacity.",
            "Gates give information a path through time that does not vanish, "
            "the same idea as residual connections.",
            "Window length is a hyperparameter; longer is not automatically "
            "better.",
        ],
    },

    {
        "file": "04_dropout_stacking_bidirectional.ipynb",
        "title": "Recurrent dropout, stacking, and the one that does not work",
        "lede": "Three standard refinements. Two help; the third fails, and its failure "
                "says something specific about the problem.",
        "needs": "CPU — about 25 minutes (GPU: 5 minutes)",
        "section": "04 — Advanced use of recurrent neural networks",
        "cells": [
            ("h2", "Recurrent dropout"),
            ("md",
             "Ordinary dropout applied to a recurrent layer would use a "
             "**different mask at every timestep**, which destroys the signal "
             "the state is carrying. Recurrent dropout uses the *same* mask at "
             "every step, so the noise is consistent along the sequence."),
            ("py", """import keras
from keras import layers
import matplotlib.pyplot as plt

NAIVE_MAE = 2.44
sequence_length, n_features = 120, 14

inputs = keras.Input(shape=(sequence_length, n_features))
x = layers.GRU(32, recurrent_dropout=0.25)(inputs)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1)(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
cb = [keras.callbacks.ModelCheckpoint("jena_dropout.keras",
                                      save_best_only=True)]
h_do = model.fit(train_dataset, epochs=50, validation_data=val_dataset,
                 callbacks=cb, verbose=2)
mae_do = keras.models.load_model("jena_dropout.keras").evaluate(
    test_dataset, verbose=0)[1]
print(f"\\nwith recurrent dropout: test MAE {mae_do:.2f}")"""),
            ("warn",
             "Fifty epochs, and it will be slow.** `recurrent_dropout` disables "
             "the cuDNN fast path, so a GPU loses most of its advantage. That is "
             "a real cost, and worth knowing before you start a run you expect "
             "to take five minutes."),

            ("h2", "Stacking recurrent layers"),
            ("py", """inputs = keras.Input(shape=(sequence_length, n_features))
x = layers.GRU(32, recurrent_dropout=0.5, return_sequences=True)(inputs)
x = layers.GRU(32, recurrent_dropout=0.5)(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1)(x)
stacked = keras.Model(inputs, outputs)

stacked.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
cb = [keras.callbacks.ModelCheckpoint("jena_stacked.keras",
                                      save_best_only=True)]
h_st = stacked.fit(train_dataset, epochs=50, validation_data=val_dataset,
                   callbacks=cb, verbose=2)
mae_st = keras.models.load_model("jena_stacked.keras").evaluate(
    test_dataset, verbose=0)[1]
print(f"\\nstacked: test MAE {mae_st:.2f}")"""),
            ("note",
             "**`return_sequences=True` on every layer but the last.** Without "
             "it the first GRU returns only its final state, and the second has "
             "a single vector rather than a sequence to work with — a shape "
             "error if you are lucky, a silently worse model if you are not."),

            ("h2", "Bidirectional: the one that does not work"),
            ("py", """inputs = keras.Input(shape=(sequence_length, n_features))
x = layers.Bidirectional(layers.LSTM(16))(inputs)
outputs = layers.Dense(1)(x)
bidir = keras.Model(inputs, outputs)

bidir.compile(optimizer="rmsprop", loss="mse", metrics=["mae"])
h_bi = bidir.fit(train_dataset, epochs=10, validation_data=val_dataset,
                 verbose=2)
print(f"\\nbidirectional: best val MAE "
      f"{min(h_bi.history['val_mae']):.2f}   (naive {NAIVE_MAE})")"""),
            ("md",
             "**Worse than the plain LSTM, and worse than the baseline.** This "
             "failure is informative rather than embarrassing.\n\n"
             "A bidirectional layer runs the sequence forwards and backwards and "
             "merges the results. On text — chapter 14 — that is exactly right: "
             "the end of a sentence informs the beginning.\n\n"
             "On weather it is not. **Chronological order is not an arbitrary "
             "convention here; it is the causal structure of the data.** The "
             "backward pass gives the model the sequence in an order that never "
             "occurs, and the extra parameters spent on it are wasted."),

            ("h2", "Everything on one axis"),
            ("py", """import numpy as np

results = [
    ("naive baseline", NAIVE_MAE),
    ("dense", 2.66),
    ("conv1d", 3.15),
    ("LSTM 16", 2.36),
    ("GRU 32 + rec. dropout", mae_do),
    ("stacked GRU", mae_st),
    ("bidirectional LSTM", min(h_bi.history["val_mae"])),
]

names = [r[0] for r in results]
vals = [r[1] for r in results]
colors = ["#888"] + ["#c0392b" if v > NAIVE_MAE else "#12b886" for v in vals[1:]]

plt.figure(figsize=(9, 4.4))
plt.barh(names[::-1], vals[::-1], color=colors[::-1])
plt.axvline(NAIVE_MAE, color="k", ls="--", lw=1.4)
plt.xlabel("test MAE (degC) -- lower is better")
plt.title("Red bars lose to a model with no parameters")
plt.tight_layout(); plt.show()"""),
            ("md",
             "**Three of six neural networks lose to *tomorrow is like today*.** "
             "That is the most valuable result in the chapter, and it is why "
             "chapter 6 makes the baseline a required step rather than a "
             "suggestion."),

            ("h2", "Where the remaining error lives"),
            ("py", """best = keras.models.load_model("jena_stacked.keras")

preds, trues = [], []
for samples, targets in test_dataset.take(20):
    preds.append(best.predict(samples, verbose=0).ravel())
    trues.append(np.array(targets))
preds = np.concatenate(preds); trues = np.concatenate(trues)
err = np.abs(preds - trues)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.2))
a1.scatter(trues, preds, s=5, alpha=.35)
lims = [trues.min() - 2, trues.max() + 2]
a1.plot(lims, lims, "k--", lw=1)
a1.set_xlabel("actual (degC)"); a1.set_ylabel("predicted")
a1.set_title("Predicted against actual"); a1.set_aspect("equal")

a2.scatter(trues, err, s=5, alpha=.35)
a2.set_xlabel("actual temperature (degC)"); a2.set_ylabel("absolute error")
a2.set_title("Error is largest at the extremes")
plt.tight_layout(); plt.show()

print(f"MAE overall:      {err.mean():.2f}")
cold = trues < np.percentile(trues, 10)
hot = trues > np.percentile(trues, 90)
print(f"MAE coldest 10%:  {err[cold].mean():.2f}")
print(f"MAE hottest 10%:  {err[hot].mean():.2f}")"""),
            ("md",
             "The error concentrates at the extremes — which are exactly the "
             "cases a weather forecast is most needed for. **A single MAE hides "
             "that entirely**, and it is the same lesson as chapter 11's IoU per "
             "class: report the metric where it matters, not only on average."),
        ],
        "takeaways": [
            "Recurrent dropout needs a consistent mask across timesteps, and it "
            "disables the fast cuDNN path.",
            "Stack with `return_sequences=True` on every layer but the last.",
            "**Bidirectional fails here** — chronological order is the causal "
            "structure, not a convention.",
            "Half the neural networks in this chapter lose to a parameterless "
            "baseline. Compute the baseline.",
        ],
    },
]
