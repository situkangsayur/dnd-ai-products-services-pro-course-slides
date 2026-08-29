# -*- coding: utf-8 -*-
"""Chapter 13 — Timeseries forecasting.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 13
(pp. 351-385), read from the book PDF.

The chapter that teaches the value of a common-sense baseline the hard way: a
dense network and a 1D ConvNet both *lose* to "tomorrow will be like today",
and only an LSTM beats it.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_TASKS = """
flowchart TB
  F["<b>Forecasting</b><br/>what happens next<br/><small>demand, revenue, weather</small>"]
  A["<b>Anomaly detection</b><br/>something unusual<br/><small>usually unsupervised:<br/>you cannot train on<br/>anomalies you have not seen</small>"]
  C["<b>Classification</b><br/>a label for a whole series<br/><small>bot or human?</small>"]
  E["<b>Event detection</b><br/>a specific expected event<br/><small>&quot;OK Google&quot;, &quot;Hey Alexa&quot;</small>"]
  F ~~~ A ~~~ C ~~~ E
"""

MMD_LADDER = """
flowchart LR
  B["Common-sense baseline<br/><b>2.44</b> val MAE"]
  D["Dense network<br/><b>~2.5</b> — worse"]
  C["1D ConvNet<br/><b>~2.9</b> — much worse"]
  L["LSTM<br/><b>2.36</b> — finally better"]
  B --> D --> C --> L
"""

MMD_RNNLOOP = """
flowchart LR
  I["input at time t"] --> R["RNN cell"]
  R --> O["output at time t"]
  R -. "state carried<br/>to the next step" .-> R
"""

MMD_FEEDVSREC = """
flowchart TB
  subgraph F["Feedforward — no memory"]
    direction TB
    F1["Flatten the whole sequence<br/>into one big vector"] --> F2["Process it in one go"]
    F2 --> F3["<b>The notion of time is gone</b>"]
  end
  subgraph R["Recurrent — has memory"]
    direction TB
    R1["Iterate through<br/>the sequence"] --> R2["Keep a state describing<br/>what has been seen"]
    R2 --> R3["<b>Order and causality survive</b>"]
  end
  F ~~~ R
"""

MMD_LSTM = """
flowchart LR
  C0["carry c(t-1)"] --> C1["carry c(t)"] --> C2["carry c(t+1)"]
  I["input at t"] --> CELL["cell"]
  S["state at t"] --> CELL
  CELL --> OUT["output at t"]
  CELL --> C1
  C1 -. "modulates the next<br/>output and state" .-> CELL
"""

MMD_DROPOUTMASK = """
flowchart TB
  subgraph W["Wrong — a new mask each timestep"]
    direction TB
    W1["mask A at t=1"] --> W2["mask B at t=2"] --> W3["mask C at t=3"]
    W3 --> W4["<b>The error signal through<br/>time is disrupted</b>"]
  end
  subgraph C["Correct — one mask, held constant"]
    direction TB
    C1["mask A at t=1"] --> C2["mask A at t=2"] --> C3["mask A at t=3"]
    C3 --> C4["<b>Error propagates through<br/>time properly</b>"]
  end
  W ~~~ C
"""

MMD_STACK = """
flowchart LR
  I["Input sequence"]
  L1["GRU<br/><code>return_sequences=True</code><br/><small>emits a full sequence</small>"]
  L2["GRU<br/><small>emits only the last step</small>"]
  D["Dense 1"]
  I --> L1 --> L2 --> D
"""


MMD_WINDOWS = """
flowchart LR
  D["data = [0 1 2 3 4 5 6]<br/>sequence_length = 3"]
  W1["[0 1 2]"]
  W2["[1 2 3]"]
  W3["[2 3 4]"]
  W4["[3 4 5]"]
  W5["[4 5 6]"]
  D --> W1 --> W2 --> W3 --> W4 --> W5
"""

MMD_SPLITSPLIT = """
flowchart LR
  A["Full series,<br/>in chronological order"]
  T["Training<br/><small>earliest</small>"]
  V["Validation<br/><small>middle</small>"]
  E["Test<br/><small>latest</small>"]
  A --> T --> V --> E
  T -. "mean and std<br/>computed HERE only" .-> T
"""

NB = ["01_jena_data_and_baseline.ipynb", "02_dense_and_conv1d.ipynb",
      "03_lstm_and_gru.ipynb", "04_dropout_stacking_bidirectional.ipynb"]

DECK = {
    "id": "ch13",
    "kind": "chapter",
    "number": 13,
    "title": "Timeseries Forecasting",
    "subtitle": "Where a common-sense baseline beats two deep learning models in a "
                "row — and what that teaches about architecture priors.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 13",
    "source_url": chapter_url(13),
    "duration": "3 hours (2 sessions)",
    "presenter": {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    "resources": chapter_resources(13, local_notebooks=NB),
    "objectives": [
        "Name the four common timeseries tasks and say which are supervised.",
        "Build a **common-sense baseline** for a forecasting problem and evaluate it "
        "properly.",
        "Explain **why a dense network and a 1D ConvNet fail** on this problem — and "
        "what that says about architecture priors.",
        "Explain what an **RNN** is, and how it differs from a feedforward network.",
        "Say why **`SimpleRNN` is not used in practice**, and how **LSTM** solves it.",
        "Apply **recurrent dropout** correctly, and say why the naive version is "
        "harmful.",
        "**Stack** recurrent layers with `return_sequences`, and know when a "
        "**bidirectional** layer helps and when it cannot.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Section 13.1",
            "title": "What a timeseries is, and why it is different",
            "blocks": [
                {"t": "p", "md": "Any data obtained by measurement at regular intervals: a "
                                 "daily stock price, a city's hourly electricity consumption, "
                                 "a store's weekly sales."},
                {"t": "band",
                 "md": "Unlike everything so far, working with timeseries means understanding "
                       "**the dynamics of a system** — its periodic cycles, how it trends, its "
                       "regular regime, and ==its sudden spikes=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.1",
            "title": "Four things you can do with one",
            "blocks": [
                {"t": "mmd", "id": "ch13-tasks", "src": MMD_TASKS,
                 "cap": "Forecasting is by far the most common, and is what this chapter "
                        "covers."},
                {"t": "p", "md": "Note the parenthetical on anomaly detection: it is usually "
                                 "**unsupervised**, because you often do not know what kind of "
                                 "anomaly you are looking for — so ==you cannot train on "
                                 "examples of it=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2",
            "title": "The running example",
            "blocks": [
                {"t": "p", "md": "Every code example in the chapter targets one problem: "
                                 "**predict the temperature 24 hours from now**, given "
                                 "readings from the recent past."},
                {"t": "p", "md": "The data is the Jena weather dataset — fourteen "
                                 "meteorological quantities recorded every ten minutes over "
                                 "several years. It is small enough to work with and "
                                 "==genuinely hard enough to be instructive=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.1",
            "title": "The split has to respect time",
            "blocks": [
                {"t": "mmd", "id": "ch13-splitsplit", "src": MMD_SPLITSPLIT,
                 "cap": "Chapter 5's arrow-of-time pitfall, made concrete."},
                {"t": "p", "md": "The data must **not** be shuffled before splitting: all test "
                                 "data has to be later than all training data. And the "
                                 "normalisation statistics come from ==the training portion "
                                 "only=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.1 · listing 13.6",
            "title": "Normalising fourteen quantities on different scales",
            "blocks": [
                {"t": "p", "md": "No vectorisation is needed — the data is already numeric. "
                                 "But atmospheric pressure sits around **1,000 mbar** while "
                                 "H2OC sits around **3**, so each series is normalised "
                                 "independently."},
                {"t": "code", "lang": "python", "file": "listing 13.6 — normalising",
                 "src": """mean = raw_data[:num_train_samples].mean(axis=0)
raw_data -= mean
std = raw_data[:num_train_samples].std(axis=0)
raw_data /= std"""},
                {"t": "band",
                 "md": "Note the slice: `[:num_train_samples]`. The statistics are computed "
                       "on the **first 210,225 timesteps only** — ==the same information-leak "
                       "rule as chapter 4's housing example=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.1",
            "title": "Windows without copying the data",
            "blocks": [
                {"t": "mmd", "id": "ch13-windows", "src": MMD_WINDOWS,
                 "cap": "Consecutive samples share most of their timesteps, so materialising "
                        "each one would waste enormous memory."},
                {"t": "p", "md": "Keras has a utility for exactly this — "
                                 "`timeseries_dataset_from_array()` — which **generates the "
                                 "windows on the fly**, keeping only the original array in "
                                 "memory."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.1",
            "title": "Understanding it on a toy example first",
            "blocks": [
                {"t": "p", "md": "The offset between `data` and `targets` is what turns "
                                 "windowing into forecasting, and it is easiest to see on ten "
                                 "integers."},
                {"t": "code", "lang": "python", "file": "the utility, on integers",
                 "src": """int_sequence = np.arange(10)

dummy_dataset = keras.utils.timeseries_dataset_from_array(
    data=int_sequence[:-3],       # windows come from here
    targets=int_sequence[3:],     # the target is 3 steps ahead
    sequence_length=3,
    batch_size=2,
)

for inputs, targets in dummy_dataset:
    for i in range(inputs.shape[0]):
        print([int(x) for x in inputs[i]], int(targets[i]))"""},
                {"t": "out", "src": """[0, 1, 2] 3
[1, 2, 3] 4
[2, 3, 4] 5
[3, 4, 5] 6
[4, 5, 6] 7"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.1",
            "title": "…then the real thing",
            "blocks": [
                {"t": "p", "md": "Same call, with the problem's actual parameters: five days of "
                                 "history sampled hourly, predicting 24 hours ahead."},
                {"t": "code", "lang": "python", "file": "the training dataset",
                 "src": """sampling_rate = 6        # one sample per hour (data is every 10 minutes)
sequence_length = 120    # five days of hourly readings
delay = sampling_rate * (sequence_length + 24 - 1)

train_dataset = keras.utils.timeseries_dataset_from_array(
    raw_data[:-delay],
    targets=temperature[delay:],
    sampling_rate=sampling_rate,
    sequence_length=sequence_length,
    shuffle=True,
    batch_size=256,
    start_index=0,
    end_index=num_train_samples,
)"""},
                {"t": "band",
                 "md": "`start_index` and `end_index` are how the three splits are carved out "
                       "of one array **without shuffling** — ==the chronological order is "
                       "preserved by construction=="},
            ],
        },

        {"type": "section", "num": "01", "title": "The baseline, and two failures",
         "lead": "Common sense contains information a model has no access to."},

        {
            "type": "slide",
            "kicker": "Section 13.2.2",
            "title": "Before any model: what would common sense do?",
            "blocks": [
                {"t": "p", "md": "Temperature is continuous and daily-periodic, so a sensible "
                                 "heuristic is: **the temperature in 24 hours will equal the "
                                 "temperature right now.**"},
                {"t": "code", "lang": "python", "file": "listing 13.9 — the common-sense baseline",
                 "src": """def evaluate_naive_method(dataset):
    total_abs_err, samples_seen = 0.0, 0
    for samples, targets in dataset:
        # column 1 is temperature; un-normalise it back to degrees Celsius
        preds = samples[:, -1, 1] * std[1] + mean[1]
        total_abs_err += np.sum(np.abs(preds - targets))
        samples_seen += samples.shape[0]
    return total_abs_err / samples_seen

print(f"Validation MAE: {evaluate_naive_method(val_dataset):.2f}")
print(f"Test MAE: {evaluate_naive_method(test_dataset):.2f}")"""},
                {"t": "out", "src": """Validation MAE: 2.44
Test MAE: 2.62"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.2",
            "title": "That is the number to beat",
            "blocks": [
                {"t": "band",
                 "md": "Assume tomorrow is like today and you are off by **two and a half "
                       "degrees on average**. Not good enough to launch a forecasting service "
                       "— but ==every model from here on has to beat it to justify itself=="},
                {"t": "p", "md": "The book makes the general point too: for an unbalanced "
                                 "classification task with 90% class A, *always predict A* "
                                 "scores 90%. **Such elementary baselines can prove "
                                 "surprisingly hard to beat.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.3 · listing 13.10",
            "title": "Attempt 1 — a small dense network",
            "blocks": [
                {"t": "p", "md": "Before anything expensive, try something cheap. Flatten the "
                                 "sequence and run it through two dense layers."},
                {"t": "code", "lang": "python", "file": "listing 13.10 — a densely connected model",
                 "src": """inputs = keras.Input(shape=(sequence_length, raw_data.shape[-1]))
x = layers.Flatten()(inputs)
x = layers.Dense(16, activation="relu")(x)
outputs = layers.Dense(1)(x)            # no activation: a regression output
model = keras.Model(inputs, outputs)

model.compile(optimizer="adam", loss="mse", metrics=["mae"])
history = model.fit(train_dataset, epochs=10,
                    validation_data=val_dataset, callbacks=callbacks)"""},
                {"t": "band",
                 "md": "**MSE as the loss, MAE as the metric.** MSE is used for training "
                       "because it is ==smooth around zero==, which gradient descent needs; "
                       "MAE is reported because it is the number a human can interpret."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.3",
            "title": "…and it does not beat the baseline",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "Some validation losses come close to the no-learning baseline, "
                       "**but not reliably**. This is exactly why the baseline was worth "
                       "computing: it turns out to be ==not easy to outperform=="},
                {"t": "p", "md": "As the book puts it: **your common sense contains a lot of "
                                 "valuable information to which a machine learning model has "
                                 "no access.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.3",
            "title": "Why gradient descent could not find the obvious answer",
            "blocks": [
                {"t": "p", "md": "A natural objection: the common-sense heuristic *is* "
                                 "expressible as a two-layer network. So why does training not "
                                 "find it?"},
                {"t": "band",
                 "md": "Because your **hypothesis space** is the space of all two-layer "
                       "networks with that configuration, and the heuristic is **one model "
                       "among millions** in it. ==Like looking for a needle in a haystack.=="},
                {"t": "p", "md": "The general limitation: **unless the learning algorithm is "
                                 "hardcoded to look for a specific kind of simple model, it "
                                 "can fail to find a simple solution to a simple problem.**"},
            ],
            "notes": "This is one of the most quotable passages in the book. It is the "
                     "clearest argument for feature engineering and architecture priors "
                     "anywhere in it.",
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.4",
            "title": "Attempt 2 — a 1D ConvNet",
            "blocks": [
                {"t": "p", "md": "The input has daily cycles, so a convolutional prior looks "
                                 "reasonable: the same pattern recurring at different points "
                                 "in time."},
                {"t": "code", "lang": "python", "file": "the 1D convolutional model",
                 "src": """x = layers.Conv1D(8, 24, activation="relu")(inputs)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(8, 12, activation="relu")(x)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(8, 6, activation="relu")(x)
x = layers.GlobalAveragePooling1D()(x)
outputs = layers.Dense(1)(x)"""},
                {"t": "out", "src": "validation MAE: about 2.9 degrees"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.2.4",
            "title": "Worse than the dense model. Two reasons.",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🕐", "h": "Weather is not translation invariant",
                     "p": "There are daily cycles, but **morning data behaves differently "
                          "from evening or night data**. The invariance holds only at one "
                          "very specific timescale.", "style": "bad"},
                    {"ico": "🔀", "h": "Order matters, a lot",
                     "p": "The recent past is far more informative than five days ago — and "
                          "**max pooling and global average pooling destroy order "
                          "information**.", "style": "bad"},
                ]},
                {"t": "band",
                 "md": "A worked demonstration of chapter 9's claim: an architecture encodes "
                       "assumptions, and ==when those assumptions are false the architecture "
                       "actively hurts=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Recurrent neural networks",
         "lead": "Treat the data as what it is: a sequence where order matters."},

        {
            "type": "slide",
            "kicker": "Section 13.3.1",
            "title": "Every network so far had no memory",
            "blocks": [
                {"t": "mmd", "id": "ch13-feedvsrec", "src": MMD_FEEDVSREC,
                 "cap": "The dense model removed time; the convolutional model destroyed "
                        "order. Neither treated the data as a sequence."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.1",
            "title": "The biological analogy the book uses",
            "blocks": [
                {"t": "p", "md": "As you read this sentence you process it **word by word — or "
                                 "rather, eye saccade by eye saccade — while keeping memories "
                                 "of what came before**. That gives you a fluid representation "
                                 "of its meaning."},
                {"t": "band",
                 "md": "Biological intelligence processes information **incrementally, while "
                       "maintaining an internal model** built from past information and "
                       "constantly updated. An RNN adopts the same principle — ==in an "
                       "extremely simplified version=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.1",
            "title": "An RNN is a network with an internal loop",
            "blocks": [
                {"t": "mmd", "id": "ch13-rnnloop", "src": MMD_RNNLOOP,
                 "cap": "Figure 13.6 — it iterates through the sequence, keeping a state "
                        "describing what it has seen so far."},
                {"t": "p", "md": "The state is **reset between independent sequences**, so one "
                                 "sequence is still one data point. What changes is that "
                                 "==the data point is no longer processed in a single step=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.2",
            "title": "Why you will rarely use SimpleRNN",
            "blocks": [
                {"t": "p", "md": "Keras has `SimpleRNN`, and it is **generally too simplistic "
                                 "to be of real use**. In theory it can retain information from "
                                 "many timesteps back; in practice such long-term dependencies "
                                 "prove impossible to learn."},
                {"t": "band", "style": "rose",
                 "md": "The cause is **the vanishing gradient problem** — the same effect "
                       "chapter 9 described for very deep feedforward networks. Studied by "
                       "Hochreiter, Schmidhuber and Bengio in the early 1990s."},
                {"t": "p", "md": "Keras offers two alternatives designed to fix it: "
                                 "**`LSTM`** and **`GRU`**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.2",
            "title": "LSTM: a conveyor belt running beside the sequence",
            "blocks": [
                {"t": "p", "md": "Long Short-Term Memory, from Hochreiter and Schmidhuber "
                                 "(1997), was the culmination of their work on vanishing "
                                 "gradients."},
                {"t": "band",
                 "md": "Imagine a **conveyor belt running parallel to the sequence**. "
                       "Information can jump onto it at any point, be carried to a later "
                       "timestep, and jump off **intact** when needed — ==preventing older "
                       "signals from gradually vanishing=="},
                {"t": "p", "md": "The book points out this should remind you of **residual "
                                 "connections** from chapter 9. It is very nearly the same "
                                 "idea, applied along time rather than along depth."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.2",
            "title": "The carry track, in a picture",
            "blocks": [
                {"t": "mmd", "id": "ch13-lstm", "src": MMD_LSTM,
                 "cap": "Figures 13.8–13.9 — the carry `c` modulates both the next output and "
                        "the next state."},
                {"t": "p", "md": "That is all the structural difference amounts to: a "
                                 "`SimpleRNN` cell, plus **an extra data flow that crosses "
                                 "timesteps without being squashed at every step**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.2",
            "title": "And it finally beats the baseline",
            "blocks": [
                {"t": "p", "md": "One layer, sixteen units. Nothing about it is elaborate — the "
                                 "architecture prior is what changed."},
                {"t": "code", "lang": "python", "file": "a simple LSTM model",
                 "src": """inputs = keras.Input(shape=(sequence_length, raw_data.shape[-1]))
x = layers.LSTM(16)(inputs)
outputs = layers.Dense(1)(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer="adam", loss="mse", metrics=["mae"])
history = model.fit(train_dataset, epochs=10,
                    validation_data=val_dataset, callbacks=callbacks)"""},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "2.44", "l": "common-sense baseline, validation MAE"},
                    {"v": "2.36", "l": "LSTM, validation MAE"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Sections 13.2 – 13.3",
            "title": "The whole chapter, as one ladder",
            "blocks": [
                {"t": "mmd", "id": "ch13-ladder", "src": MMD_LADDER,
                 "cap": "Two deep learning models lose to the heuristic before one beats it."},
                {"t": "band",
                 "md": "The margin over the baseline is **small**, and the chapter does not "
                       "pretend otherwise. The lesson is not that LSTMs are powerful; it is "
                       "that ==the right architecture prior is what made the difference=="},
            ],
        },

        {"type": "section", "num": "03", "title": "Getting more out of RNNs",
         "lead": "Recurrent dropout, stacking, and bidirectional layers."},

        {
            "type": "slide",
            "kicker": "Section 13.3.4",
            "title": "Dropout in a recurrent layer is not obvious",
            "blocks": [
                {"t": "p", "md": "The LSTM overfits quickly despite having very few units: "
                                 "training and validation losses diverge after a few epochs. "
                                 "Dropout is the obvious remedy — **but applying it naively "
                                 "makes things worse**."},
                {"t": "band", "style": "amber",
                 "md": "It has long been known that applying dropout **before** a recurrent "
                       "layer ==hinders learning rather than helping regularisation=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.4",
            "title": "Yarin Gal's result: hold the mask constant",
            "blocks": [
                {"t": "mmd", "id": "ch13-dropoutmask", "src": MMD_DROPOUTMASK,
                 "cap": "The same pattern of dropped units at every timestep, rather than a "
                        "fresh random one."},
                {"t": "p", "md": "Determined in 2015 as part of Gal's PhD thesis on Bayesian "
                                 "deep learning. He did the research **using Keras**, and "
                                 "helped build the mechanism directly into its recurrent "
                                 "layers."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.4",
            "title": "The two arguments that implement it",
            "blocks": [
                {"t": "p", "md": "Every recurrent layer in Keras takes two dropout-related "
                                 "arguments, and they regularise different things."},
                {"t": "code", "lang": "python", "file": "recurrent dropout",
                 "src": """inputs = keras.Input(shape=(sequence_length, raw_data.shape[-1]))
x = layers.LSTM(32, recurrent_dropout=0.25)(inputs)
x = layers.Dropout(0.5)(x)              # regularise the LSTM's OUTPUT too
outputs = layers.Dense(1)(x)"""},
                {"t": "table",
                 "head": ["Argument", "What it drops"],
                 "widths": [30, 70],
                 "rows": [
                     ["`dropout`", "The layer's **input** units."],
                     ["`recurrent_dropout`",
                      "The layer's **inner recurrent activations** — a temporally constant "
                      "mask, which is the part Gal's result is about."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.5",
            "title": "Stacking: when you stop overfitting, add capacity",
            "blocks": [
                {"t": "p", "md": "Once dropout has stopped the overfitting but performance has "
                                 "plateaued, chapter 5's rule applies: **increase capacity "
                                 "until overfitting becomes the main obstacle again**."},
                {"t": "band",
                 "md": "Recurrent layer stacking is the classic way to do it. Not long ago "
                       "**Google Translate was powered by a stack of seven large LSTM "
                       "layers** — ==which is huge=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.5",
            "title": "The one argument that makes stacking work",
            "blocks": [
                {"t": "mmd", "id": "ch13-stack", "src": MMD_STACK,
                 "cap": "Intermediate layers must emit a full sequence; only the last one "
                        "emits a single vector."},
                {"t": "code", "lang": "python", "file": "a stack of two GRU layers",
                 "src": """x = layers.GRU(32, recurrent_dropout=0.5, return_sequences=True)(inputs)
x = layers.GRU(32, recurrent_dropout=0.5)(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1)(x)"""},
                {"t": "band",
                 "md": "`return_sequences=True` makes a layer return a **rank-3 tensor** — its "
                       "output at every timestep — instead of only the last one. Omit it on an "
                       "intermediate layer and ==the next layer has no sequence to read=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.5",
            "title": "GRU, and why the book switches to it here",
            "blocks": [
                {"t": "p", "md": "A **Gated Recurrent Unit** is a streamlined variant of LSTM: "
                                 "the same idea of a carried track, with a simpler gating "
                                 "structure and therefore fewer parameters."},
                {"t": "band",
                 "md": "In practice the choice between them is empirical. GRU is **cheaper to "
                       "run**; LSTM has **slightly more representational power**. ==Try both "
                       "and measure== rather than arguing about it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.3.6",
            "title": "Bidirectional layers: the same data, read backwards too",
            "blocks": [
                {"t": "p", "md": "A bidirectional RNN runs **two copies** of a recurrent layer "
                                 "— one over the sequence in order, one in reverse — and "
                                 "merges their representations."},
                {"t": "code", "lang": "python", "file": "wrapping a layer",
                 "src": """inputs = keras.Input(shape=(sequence_length, raw_data.shape[-1]))
x = layers.Bidirectional(layers.LSTM(16))(inputs)
outputs = layers.Dense(1)(x)"""},
                {"t": "band", "style": "amber",
                 "md": "On **this** problem it does not help: for weather, the recent past is "
                       "what matters, so reading in reverse gives a ==chronologically "
                       "backwards view that is simply worse==. It shines on text, where both "
                       "directions carry meaning — chapter 14 returns to it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 13.4",
            "title": "Going further",
            "blocks": [
                {"t": "bullets", "items": [
                    "**Adjust the number of units** in each recurrent layer, and the dropout "
                    "rates — the configurations here were chosen largely arbitrarily.",
                    "**Adjust the learning rate** of the optimizer.",
                    "Try a **stack of `Dense` layers** as the regressor on top instead of a "
                    "single one.",
                    "**Improve the input**: try longer or shorter sequences, or a different "
                    "sampling rate.",
                ]},
                {"t": "band",
                 "md": "And the standing warning: **always evaluate on the validation set**, "
                       "then confirm once on test — otherwise you end up ==overfitting to "
                       "your validation procedure==, exactly as chapter 5 described."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Practice",
            "title": "What this chapter changes about how you start",
            "blocks": [
                {"t": "steps", "items": [
                    "**Compute the baseline before writing any model.** It is cheap, and here "
                    "it would have saved two failed attempts.",
                    "**State the architecture prior out loud.** *Convolution assumes "
                    "translation invariance* — is that true of your data, at the timescale "
                    "you care about?",
                    "**Check whether order matters.** If it does, any layer that pools or "
                    "flattens is throwing away the signal.",
                ]},
                {"t": "band",
                 "md": "For transactional or operational data these three questions usually "
                       "settle the architecture before a single experiment runs — which is "
                       "==the cheapest hour in the whole project=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Always establish a common-sense baseline first.** Here it beat two "
                    "deep learning models.",
                    "**A good solution existing in your hypothesis space does not mean "
                    "gradient descent will find it.**",
                    "**Dense flattens away time; 1D convolution pools away order.** Neither "
                    "prior fits a forecasting problem.",
                    "**RNNs keep a state** and process a sequence incrementally.",
                    "**`SimpleRNN` cannot learn long dependencies**; LSTM adds a carry track — "
                    "residual connections, along time.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "…and the three refinements",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "💧", "h": "Recurrent dropout",
                     "p": "A **temporally constant mask**. A fresh random mask each timestep "
                          "disrupts the error signal through time.", "style": "accent"},
                    {"ico": "🧱", "h": "Stacking",
                     "p": "More capacity, at more compute. Intermediate layers need "
                          "`return_sequences=True`.", "style": "accent"},
                    {"ico": "↔", "h": "Bidirectional",
                     "p": "Helps where **both directions carry meaning** — text. Does not help "
                          "where only the recent past matters.", "style": "accent"},
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_lstm_and_gru.ipynb",
                     "href": "../../course-slides/notebooks/ch13/03_lstm_and_gru.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 14 — Text classification",
                     "href": "../ch14/index.html"},
                ]},
            ],
        },
    ],
}
