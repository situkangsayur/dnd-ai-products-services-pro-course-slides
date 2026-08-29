# -*- coding: utf-8 -*-
"""Chapter 4 — Classification and regression.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 4
(pp. 105-135), read from the book PDF.

Three complete worked examples: IMDB (binary), Reuters (multiclass), and
California Housing (scalar regression). The reported numbers are the book's;
where a figure moves between runs the slide says so.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_WORKFLOW = """
flowchart LR
  A["Raw data"] --> B["Vectorise<br/>multi-hot / normalise"]
  B --> C["Split off<br/>validation"]
  C --> D["Train long enough<br/>to overfit"]
  D --> E["Read the curve<br/>find the turning point"]
  E --> F["Retrain to that<br/>epoch only"]
  F --> G["Evaluate once<br/>on the test set"]
"""

MMD_BOTTLENECK = """
flowchart LR
  subgraph OK["What works"]
    direction LR
    A1["Dense 64"] --> A2["Dense 64"] --> A3["Dense 46<br/>softmax"]
  end
  subgraph BAD["Information bottleneck"]
    direction LR
    B1["Dense 64"] --> B2["Dense 4"] --> B3["Dense 46<br/>softmax"]
  end
  OK ~~~ BAD
"""

MMD_KFOLD = """
flowchart TB
  D["Training data<br/>split into 4 folds"]
  F1["Fold 1<br/>validate on part 1"]
  F2["Fold 2<br/>validate on part 2"]
  F3["Fold 3<br/>validate on part 3"]
  F4["Fold 4<br/>validate on part 4"]
  AVG["Final score<br/>average of the four"]
  D --> F1 --> AVG
  D --> F2 --> AVG
  D --> F3 --> AVG
  D --> F4 --> AVG
"""

MMD_HEADS = """
flowchart TB
  T1["Binary<br/>2 classes"] --> H1["1 unit<br/>sigmoid"]
  T2["Multiclass<br/>N classes, one label"] --> H2["N units<br/>softmax"]
  T3["Multilabel<br/>N classes, many labels"] --> H3["N units<br/>sigmoid"]
  T4["Scalar regression"] --> H4["1 unit<br/>no activation"]
"""


MMD_CURVE = """
flowchart LR
  E1["Epochs 1-4<br/>both losses fall"] --> E2["Epoch 4<br/><b>turning point</b>"]
  E2 --> E3["Epochs 5-20<br/>training loss keeps falling,<br/>validation loss climbs"]
  E3 --> ACT["Retrain a fresh model<br/>for 4 epochs only"]
"""

MMD_LEAK = """
flowchart TB
  OK["mean, std from<br/>TRAINING data"] --> A1["apply to training set"]
  OK --> A2["apply to test set"]
  BAD["mean, std from<br/>the TEST set"] --> B1["information leak:<br/>the model learns something<br/>about data it must not see"]
"""

NB = ["01_imdb_binary_classification.ipynb", "02_reuters_multiclass.ipynb",
      "03_housing_regression.ipynb"]

DECK = {
    "id": "ch04",
    "kind": "chapter",
    "number": 4,
    "title": "Classification and Regression",
    "subtitle": "Three complete workflows — binary, multiclass, and scalar "
                "regression — and the rules for choosing a loss and an output "
                "activation that the rest of the book relies on.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 4",
    "source_url": chapter_url(4),
    "duration": "3 hours (2 sessions)",
    "presenter": {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    "resources": chapter_resources(4, local_notebooks=NB),
    "objectives": [
        "Choose the correct **output activation and loss function** for binary, "
        "multiclass, and regression tasks — without guessing.",
        "Prepare text with **multi-hot encoding**, and labels as either **one-hot** "
        "or **sparse integers**.",
        "Read a **validation loss curve** to find the best stopping point, then "
        "retrain to exactly that point.",
        "Recognise an **information bottleneck** and size intermediate layers from "
        "the number of classes.",
        "Normalise features using **training-set statistics only**, and evaluate a "
        "small-data model with **K-fold cross-validation**.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Roadmap",
            "title": "The same six steps, three times over",
            "blocks": [
                {"t": "mmd", "id": "ch04-workflow", "src": MMD_WORKFLOW,
                 "cap": "Every example in this chapter follows this path. By the third one "
                        "it should feel routine."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Vocabulary",
            "title": "Terms used precisely from here to chapter 20",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "table",
                         "head": ["Term", "Meaning"],
                         "widths": [32, 68],
                         "rows": [
                             ["**Sample / input**", "One data point entering the model."],
                             ["**Prediction / output**", "What comes out."],
                             ["**Target**", "The ground truth, from outside the model."],
                             ["**Loss value**", "A measure of distance between the two."],
                             ["**Mini-batch**", "Typically 8–128 samples at a time."],
                         ]},
                    ],
                    [
                        {"t": "table",
                         "head": ["Task type", "Defining feature"],
                         "widths": [40, 60],
                         "rows": [
                             ["**Binary classification**", "Two mutually exclusive categories."],
                             ["**Multiclass**", "More than two, one label per sample."],
                             ["**Multilabel**", "A sample may carry several labels at once."],
                             ["**Scalar regression**", "One continuous value."],
                             ["**Vector regression**", "Several continuous values."],
                         ]},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Vocabulary",
            "title": "The distinction that decides your output layer",
            "blocks": [
                {"t": "mmd", "id": "ch04-heads", "src": MMD_HEADS,
                 "cap": "Multiclass and multilabel look similar and need different heads."},
                {"t": "band",
                 "md": "**Softmax** forces the outputs to sum to 1 — right when exactly one "
                       "class is true. **Sigmoid per class** lets several be true at once. "
                       "Choosing the wrong one ==trains a model that cannot express the "
                       "answer=="},
            ],
        },

        {"type": "section", "num": "01", "title": "Binary classification: IMDB reviews",
         "lead": "50,000 movie reviews, positive or negative."},

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "The dataset, and what has already been done to it",
            "blocks": [
                {"t": "p", "md": "IMDB ships with Keras, already split and already converted "
                                 "from words into integer indices. `num_words=10000` keeps "
                                 "only the ten thousand most frequent words."},
                {"t": "code", "lang": "python", "file": "listing 4.1 — loading IMDB",
                 "src": """from keras.datasets import imdb

(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=10000)

print(len(train_data), len(test_data))
print(train_data[0][:12])          # a review, as word indices
print(train_labels[0])             # 1 = positive, 0 = negative"""},
                {"t": "out", "src": """25000 25000
[1, 14, 22, 16, 43, 530, 973, 1622, 1385, 65, 458, 4468]
1"""},
                {"t": "p", "md": "The split is balanced 50:50, which matters for the baseline "
                                 "we set in a moment."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "Turning a list of words into a tensor",
            "blocks": [
                {"t": "p", "md": "A `Dense` layer needs a fixed-length numeric vector, but "
                                 "reviews have different lengths. Multi-hot encoding solves "
                                 "that by turning each review into a 10,000-long vector of "
                                 "0s and 1s."},
                {"t": "code", "lang": "python", "file": "listing 4.2 — multi-hot encoding",
                 "src": """import numpy as np

def multi_hot_encode(sequences, num_classes):
    results = np.zeros((len(sequences), num_classes))
    for i, sequence in enumerate(sequences):
        results[i][sequence] = 1.0        # mark every word index that appears
    return results

x_train = multi_hot_encode(train_data, num_classes=10000)
x_test = multi_hot_encode(test_data, num_classes=10000)
y_train = train_labels.astype("float32")
y_test = test_labels.astype("float32")

print(x_train.shape, x_train[0][:12])"""},
                {"t": "out", "src": "(25000, 10000) [0. 1. 1. 0. 1. 1. 1. 1. 1. 1. 0. 0.]"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "What that encoding throws away",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "Multi-hot records **which words appear**, not **in what order**. "
                       "*\"good, not bad\"* and *\"bad, not good\"* become ==the identical "
                       "vector=="},
                {"t": "p", "md": "For sentiment on long reviews that turns out to be good "
                                 "enough. Chapters 14 and 15 replace it as soon as word order "
                                 "starts to carry the meaning."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "A deliberately small model",
            "blocks": [
                {"t": "p", "md": "Two 16-unit hidden layers and a single sigmoid output. The "
                                 "model is kept small on purpose — the dataset is not large, "
                                 "and chapter 5 explains what happens when it is not."},
                {"t": "code", "lang": "python", "file": "listing 4.3 — the model",
                 "src": """import keras
from keras import layers

model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),      # one probability, 0 to 1
])

model.compile(optimizer="adam",
              loss="binary_crossentropy",
              metrics=["accuracy"])"""},
                {"t": "p", "md": "`relu` zeroes out negatives; `sigmoid` squashes the final "
                                 "score into the interval [0, 1] so it can be read as a "
                                 "probability."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "Why crossentropy and not mean squared error",
            "blocks": [
                {"t": "quote",
                 "md": "Crossentropy is a quantity from the field of information theory that "
                       "measures the distance between probability distributions.",
                 "cite": "Chollet & Watson, section 4.1"},
                {"t": "p", "md": "The model outputs a **distribution**; the target is a "
                                 "distribution too. Crossentropy is the natural way to "
                                 "compare them, which is why it pairs with sigmoid and "
                                 "softmax rather than MSE."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "Holding out a validation set, and training long",
            "blocks": [
                {"t": "p", "md": "Ten thousand samples are set aside. The model is then "
                                 "trained for **20 epochs — deliberately too many** — so the "
                                 "turning point becomes visible."},
                {"t": "code", "lang": "python", "file": "listing 4.4–4.5 — validate and fit",
                 "src": """x_val, partial_x_train = x_train[:10000], x_train[10000:]
y_val, partial_y_train = y_train[:10000], y_train[10000:]

history = model.fit(
    partial_x_train, partial_y_train,
    epochs=20,
    batch_size=512,
    validation_data=(x_val, y_val),
)"""},
                {"t": "band",
                 "md": "Training past the optimum is not waste here — it is ==how you find "
                       "the optimum==. The next slide shows what the curves say."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "What the two curves do",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "bullets", "items": [
                            "**Training loss** falls monotonically, epoch after epoch.",
                            "**Validation loss** falls, bottoms out around **epoch 4**, then "
                            "==turns and climbs==.",
                        ]},
                    ],
                    [
                        {"t": "band", "style": "amber",
                         "md": "Everything after epoch 4 makes the model **better on data it "
                               "has seen and worse on data it has not**."},
                    ],
                ]},
                {"t": "quote",
                 "md": "After the fourth epoch, you're overoptimizing on the training data, "
                       "and you end up learning representations that are specific to the "
                       "training data and don't generalize to data outside of the training set.",
                 "cite": "Chollet & Watson, section 4.1"},
            ],
            "notes": "This pattern reappears in every later chapter. Train to see the turning "
                     "point, then retrain to it.",
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "The procedure, stated once and reused everywhere",
            "blocks": [
                {"t": "mmd", "id": "ch04-curve", "src": MMD_CURVE,
                 "cap": "Overtraining is used as a measuring instrument, then discarded."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "Retrain to four epochs, and score it once",
            "blocks": [
                {"t": "p", "md": "With the turning point known, build a fresh model and stop "
                                 "at exactly that epoch. Only now does the test set get "
                                 "touched."},
                {"t": "code", "lang": "python", "file": "the production run",
                 "src": """model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
model.fit(x_train, y_train, epochs=4, batch_size=512)

results = model.evaluate(x_test, y_test)
print(results)"""},
                {"t": "out", "src": "[0.2929, 0.8834]"},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "88%", "l": "test accuracy after retraining to 4 epochs"},
                    {"v": "50%", "l": "the random baseline — the classes are balanced"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.1",
            "title": "Reading a prediction back",
            "blocks": [
                {"t": "p", "md": "A binary model returns one number per sample. Turning it "
                                 "into a decision means choosing a threshold — and that "
                                 "choice belongs to the business, not to the model."},
                {"t": "code", "lang": "python", "file": "predicting on new reviews",
                 "src": """predictions = model.predict(x_test)
print(predictions[:5].ravel())

positive = predictions > 0.5        # the threshold is a CHOICE, not a given
print(positive[:5].ravel())"""},
                {"t": "out", "src": """[0.982 0.031 0.671 0.118 0.945]
[ True False  True False  True]"""},
                {"t": "band",
                 "md": "Note the third review at **0.67** — confident enough to call "
                       "positive at a 0.5 threshold, and negative at 0.7. Chapter 6 shows "
                       "how to set that number ==against a cost, not a habit=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Multiclass: Reuters newswires",
         "lead": "46 topics, mutually exclusive."},

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "Same shape of problem, more classes",
            "blocks": [
                {"t": "p", "md": "8,982 training and 2,246 test newswires, each belonging to "
                                 "exactly one of 46 topics. The inputs are encoded exactly as "
                                 "before; only the labels and the output layer change."},
                {"t": "code", "lang": "python", "file": "listing 4.9 — loading Reuters",
                 "src": """from keras.datasets import reuters

(train_data, train_labels), (test_data, test_labels) = reuters.load_data(num_words=10000)

x_train = multi_hot_encode(train_data, num_classes=10000)
x_test = multi_hot_encode(test_data, num_classes=10000)

print(len(train_data), len(test_data), max(train_labels) + 1)"""},
                {"t": "out", "src": "8982 2246 46"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "Two ways to write the labels",
            "blocks": [
                {"t": "p", "md": "The same information can be given to Keras in two shapes. "
                                 "The maths is identical; only the interface differs."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "one-hot labels",
                         "src": """from keras.utils import to_categorical

y_train = to_categorical(train_labels)
y_test = to_categorical(test_labels)
# shape (8982, 46)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"])"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "sparse integer labels",
                         "src": """y_train = train_labels      # leave as integers
y_test = test_labels
# shape (8982,)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])"""},
                    ],
                ]},
                {"t": "band",
                 "md": "Pick whichever avoids a conversion. Mixing them up gives a shape "
                       "error that names the loss function, ==which is the clue to what "
                       "went wrong=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "The model, and a metric that asks a better question",
            "blocks": [
                {"t": "p", "md": "The hidden layers are wider than in the IMDB example — the "
                                 "next slide explains why — and a second metric is added."},
                {"t": "code", "lang": "python", "file": "listing 4.11 — model and top-K",
                 "src": """model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(46, activation="softmax"),      # one unit per class
])

top_3 = keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy")
model.compile(optimizer="adam",
              loss="categorical_crossentropy",
              metrics=["accuracy", top_3])"""},
                {"t": "band",
                 "md": "**Top-K accuracy** asks whether the true class is among the top k "
                       "guesses. For a system that ==suggests rather than decides==, that is "
                       "often the honest measure."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "An experiment designed to fail",
            "blocks": [
                {"t": "mmd", "id": "ch04-bottleneck", "src": MMD_BOTTLENECK,
                 "cap": "The same network, except one intermediate layer is squeezed to four "
                        "units."},
                {"t": "p", "md": "The book deliberately builds the broken version to show what "
                                 "an **information bottleneck** does. Squeezing 46 classes "
                                 "through 4 dimensions loses information ==that no later "
                                 "layer can recover=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "What the bottleneck costs",
            "blocks": [
                {"t": "p", "md": "One line changes: the second hidden layer drops from 64 units to 4. Everything else about the network and the training run is identical."},
                {"t": "code", "lang": "python", "file": "listing 4.13 — the broken model",
                 "src": """model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(4, activation="relu"),          # the bottleneck
    layers.Dense(46, activation="softmax"),
])"""},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "≈ 80%", "l": "validation accuracy without the bottleneck"},
                    {"v": "≈ 71%", "l": "with it — nine points gone"},
                ]},
                {"t": "quote",
                 "md": "The model is able to cram most of the necessary information into these "
                       "4-dimensional representations, but not all of it.",
                 "cite": "Chollet & Watson, section 4.2"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "The sizing rule that follows",
            "blocks": [
                {"t": "band",
                 "md": "**An intermediate layer should not be narrower than the number of "
                       "output classes.** That is why IMDB was fine on 16 units (2 classes) "
                       "and Reuters needs 64."},
                {"t": "p", "md": "It is a floor, not a target. Chapter 5 covers how to find "
                                 "the right size above that floor."},
            ],
            "notes": "The failed experiment is the best part of chapter 4. Show it in full — "
                     "people learn more from it than from the working version.",
        },

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "Retrain, evaluate, and check against the right baseline",
            "blocks": [
                {"t": "p", "md": "Same procedure as IMDB: the curve turns at epoch 9, so a "
                                 "fresh model is trained to exactly nine epochs."},
                {"t": "code", "lang": "python", "file": "listing 4.14 — production model",
                 "src": """model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(46, activation="softmax"),
])
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.fit(x_train, y_train, epochs=9, batch_size=512)

print(model.evaluate(x_test, y_test))"""},
                {"t": "out", "src": """71/71 ---- 0s 3ms/step - accuracy: 0.7969 - loss: 0.9127
[0.9127, 0.7969]"""},
                {"t": "band",
                 "md": "80% sounds unremarkable until you know the baseline: guessing "
                       "according to the class frequencies gets about **19%**, because the "
                       "46 classes are ==far from evenly distributed=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.2",
            "title": "Where the remaining 20% goes",
            "blocks": [
                {"t": "p", "md": "Roughly one newswire in five is misfiled. Looking at the "
                                 "confusion between classes tells you whether that matters."},
                {"t": "code", "lang": "python", "file": "inspecting the errors",
                 "src": """predictions = model.predict(x_test)
predicted = predictions.argmax(axis=1)

print((predicted == test_labels).mean())          # overall accuracy
print(predictions[0].max())                       # confidence on the first one

import collections
print(collections.Counter(test_labels).most_common(3))   # class imbalance"""},
                {"t": "out", "src": """0.7969
0.94
[(3, 813), (4, 474), (19, 133)]"""},
                {"t": "band", "style": "amber",
                 "md": "Class 3 alone accounts for **813 of 2,246** test samples. That "
                       "imbalance is why the honest baseline is 19% rather than 1/46 — and "
                       "why ==accuracy alone is a thin way to describe this model=="},
            ],
        },

        {"type": "section", "num": "03", "title": "Scalar regression: house prices",
         "lead": "Very little data. The rules change."},

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "480 training samples, eight features",
            "blocks": [
                {"t": "p", "md": "A small extract of the 1990 California census: 480 training "
                                 "and 120 test districts, each described by eight numeric "
                                 "features, with median house price as the target."},
                {"t": "code", "lang": "python", "file": "listing 4.16 — loading the data",
                 "src": """from keras.datasets import california_housing

(train_data, train_targets), (test_data, test_targets) = (
    california_housing.load_data(version="small"))

print(train_data.shape, test_data.shape)
print(train_targets[:4])"""},
                {"t": "out", "src": """(480, 8) (120, 8)
[452600. 358500. 352100. 341300.]"""},
                {"t": "p", "md": "Features: longitude, latitude, median house age, population, "
                                 "households, median income, total rooms, total bedrooms."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "Normalisation — and the leak hiding in it",
            "blocks": [
                {"t": "p", "md": "The features live on wildly different scales, which "
                                 "destabilises optimisation. Each is centred and scaled — "
                                 "but look carefully at which statistics are used."},
                {"t": "code", "lang": "python", "file": "listing 4.17 — normalising",
                 "src": """mean = train_data.mean(axis=0)
std = train_data.std(axis=0)

x_train = (train_data - mean) / std
x_test = (test_data - mean) / std      # TRAINING statistics, not the test set's

y_train = train_targets / 100000       # scale the target to a sane range
y_test = test_targets / 100000"""},
                {"t": "band", "style": "rose",
                 "md": "Recomputing `mean` and `std` from the test data would be an "
                       "==information leak==: the model would know something about data it "
                       "is supposed never to have seen. Chapter 5 gives this its formal name."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "Which statistics may touch which data",
            "blocks": [
                {"t": "mmd", "id": "ch04-leak", "src": MMD_LEAK,
                 "cap": "The rule in one picture: statistics flow outward from the training "
                        "set only."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "A regression head has no activation",
            "blocks": [
                {"t": "p", "md": "Three design choices here differ from the classifiers, and "
                                 "each follows from the task or the data size."},
                {"t": "code", "lang": "python", "file": "listing 4.18 — the model",
                 "src": """def get_model():
    model = keras.Sequential([
        layers.Dense(64, activation="relu"),
        layers.Dense(64, activation="relu"),
        layers.Dense(1),                    # NO activation — free to predict any value
    ])
    model.compile(optimizer="adam",
                  loss="mean_squared_error",
                  metrics=["mean_absolute_error"])
    return model"""},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔓", "h": "No output activation",
                     "p": "A sigmoid would trap predictions in [0, 1]. Regression must be free.",
                     "style": "accent"},
                    {"ico": "🤏", "h": "A small model",
                     "p": "480 samples. A large model would simply memorise them.",
                     "style": "warn"},
                    {"ico": "📏", "h": "MSE to train, MAE to read",
                     "p": "MAE is human-readable: 0.5 means being off by about $50,000.",
                     "style": "accent"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "With this little data, one validation split is not enough",
            "blocks": [
                {"t": "mmd", "id": "ch04-kfold", "src": MMD_KFOLD,
                 "cap": "Each quarter takes a turn as the validation set; the four scores are "
                        "averaged."},
                {"t": "p", "md": "With 480 samples, a single split of, say, 120 is small "
                                 "enough that the score depends heavily on ==which 120 you "
                                 "happen to draw=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "K-fold, written out",
            "blocks": [
                {"t": "p", "md": "The loop below carves out fold *i*, trains a **brand-new** "
                                 "model on the rest, and records its validation MAE."},
                {"t": "code", "lang": "python", "file": "listing 4.19 — the K-fold loop",
                 "src": """k, num_epochs, all_scores = 4, 50, []
num_val_samples = len(x_train) // k

for i in range(k):
    fold_x_val = x_train[i * num_val_samples : (i + 1) * num_val_samples]
    fold_y_val = y_train[i * num_val_samples : (i + 1) * num_val_samples]
    fold_x_train = np.concatenate(
        [x_train[: i * num_val_samples], x_train[(i + 1) * num_val_samples :]], axis=0)
    fold_y_train = np.concatenate(
        [y_train[: i * num_val_samples], y_train[(i + 1) * num_val_samples :]], axis=0)

    model = get_model()                 # a FRESH model every fold
    model.fit(fold_x_train, fold_y_train, epochs=num_epochs, batch_size=16, verbose=0)
    val_loss, val_mae = model.evaluate(fold_x_val, fold_y_val, verbose=0)
    all_scores.append(val_mae)"""},
                {"t": "out", "src": """[0.265, 0.292, 0.232, 0.349]
mean MAE: 0.296   ->  off by roughly $29,600"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "The spread is the point",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "The four folds scored **0.232 to 0.349** — a spread of nearly 50% of "
                       "the smallest value. Any single split would have reported one of those "
                       "numbers and ==told you nothing about the other three=="},
                {"t": "p", "md": "That variance is exactly why K-fold exists, and why it is "
                                 "worth four times the compute on a dataset this size."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "How long to train? Average the curves",
            "blocks": [
                {"t": "p", "md": "Run the folds again for 200 epochs, keep the per-epoch "
                                 "validation MAE from each, and average them into one curve."},
                {"t": "code", "lang": "python", "file": "listing 4.20 — averaging MAE curves",
                 "src": """all_mae_histories = []
for i in range(k):
    # ... same fold setup as before ...
    history = model.fit(fold_x_train, fold_y_train,
                        validation_data=(fold_x_val, fold_y_val),
                        epochs=200, batch_size=16, verbose=0)
    all_mae_histories.append(history.history["val_mean_absolute_error"])

average_mae_history = [
    np.mean([h[i] for h in all_mae_histories]) for i in range(200)
]"""},
                {"t": "band",
                 "md": "The averaged curve flattens around **epoch 120–140** and worsens "
                       "after. ==That is the stopping point==, and it is far more trustworthy "
                       "than any single fold's curve."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 4.3",
            "title": "The final model, and what its error means",
            "blocks": [
                {"t": "p", "md": "Train once more on all the training data, to the epoch the "
                                 "averaged curve identified, then evaluate on the test set."},
                {"t": "code", "lang": "python", "file": "the production model",
                 "src": """model = get_model()
model.fit(x_train, y_train, epochs=130, batch_size=16, verbose=0)

test_mse, test_mae = model.evaluate(x_test, y_test)
predictions = model.predict(x_test)
print(f"test MAE {test_mae:.2f}   first prediction {predictions[0][0]:.2f}")"""},
                {"t": "out", "src": "test MAE 0.31   first prediction 2.83"},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "≈ $31,000", "l": "average error, at the 100k scaling"},
                    {"v": "≈ $283,000", "l": "what a prediction of 2.83 means"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Across all three examples",
            "title": "Why every model here was kept small",
            "blocks": [
                {"t": "table",
                 "head": ["Example", "Training samples", "Hidden layers", "Reasoning"],
                 "widths": [22, 20, 22, 36],
                 "rows": [
                     ["IMDB", "15,000", "2 × 16 units",
                      "Two classes, so 16 units is comfortably above the floor."],
                     ["Reuters", "8,982", "2 × 64 units",
                      "46 classes: anything much narrower becomes a bottleneck."],
                     ["Housing", "480", "2 × 64 units",
                      "Tiny dataset — a larger model would memorise it outright."],
                 ]},
                {"t": "band",
                 "md": "The rule pulls in two directions at once: **wide enough not to "
                       "bottleneck the classes, small enough not to memorise the samples**. "
                       "Chapter 5 turns that tension into a method."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Across all three examples",
            "title": "Four ways these workflows go wrong",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📉", "h": "Training to a fixed epoch count",
                     "p": "Picking 20 epochs because a tutorial did. The turning point is a "
                          "property of **your** data and has to be measured.", "style": "bad"},
                    {"ico": "🔁", "h": "Reusing a trained model across folds",
                     "p": "`get_model()` must be called **inside** the K-fold loop. Reusing "
                          "one carries knowledge between folds and voids the score.",
                     "style": "bad"},
                    {"ico": "🧪", "h": "Normalising with test statistics",
                     "p": "An information leak, and it inflates your score in a way you will "
                          "not discover until production.", "style": "bad"},
                    {"ico": "🎯", "h": "Reporting accuracy with no baseline",
                     "p": "80% is excellent against 19% and poor against 90%. The number "
                          "alone says nothing.", "style": "bad"},
                ]},
            ],
            "notes": "Every one of these shows up in the group assignments. Naming them now "
                     "saves a lot of rework later.",
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "The table you will keep coming back to",
            "blocks": [
                {"t": "table",
                 "head": ["Task", "Last-layer activation", "Loss function", "Typical metrics"],
                 "widths": [28, 22, 32, 18],
                 "rows": [
                     ["**Binary** classification", "`sigmoid` (1 unit)",
                      "`binary_crossentropy`", "accuracy, ROC AUC"],
                     ["**Multiclass**, one-hot labels", "`softmax` (N units)",
                      "`categorical_crossentropy`", "accuracy, top-K"],
                     ["**Multiclass**, integer labels", "`softmax` (N units)",
                      "`sparse_categorical_crossentropy`", "accuracy"],
                     ["**Multilabel**", "`sigmoid` (N units)",
                      "`binary_crossentropy`", "accuracy, ROC AUC"],
                     ["**Scalar regression**", "none (1 unit)",
                      "`mean_squared_error`", "MAE"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Vectorise** discrete data; **normalise features using training-set "
                    "statistics only**.",
                    "**Intermediate layers must not be narrower than the class count** — "
                    "otherwise you build an information bottleneck.",
                    "**Little data → a small model**, one or two hidden layers.",
                    "**Train until it overfits to find the turning point**, then retrain to "
                    "exactly that epoch.",
                    "**Little data → K-fold**, not a single validation split — and read the "
                    "spread, not just the mean.",
                    "Always compare against a **common-sense baseline** before deciding a "
                    "score is good.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_imdb_binary_classification.ipynb",
                     "href": "../../course-slides/notebooks/ch04/01_imdb_binary_classification.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 5 — Fundamentals of machine learning",
                     "href": "../ch05/index.html"},
                ]},
            ],
        },
    ],
}
