# -*- coding: utf-8 -*-
"""Chapter 2 — The mathematical building blocks of neural networks.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 2
(pp. 17-56), read from the book PDF.

Every listing here follows the book's own code (Keras 3). Where a printed
result is reproduced, it is the book's; where a number swings between runs,
the slide says so rather than pretending to a precision it does not have.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url, notebook_url  # noqa: E402
from diagrams import (backprop, forward_pass, geometric_ops,  # noqa: E402
                      neural_net,
                      sgd_descent, tensor_ranks)


MMD_RANKS = """
flowchart LR
  R0["rank 0<br/><b>scalar</b><br/><code>shape ()</code>"]
  R1["rank 1<br/><b>vector</b><br/><code>shape (5,)</code>"]
  R2["rank 2<br/><b>matrix</b><br/><code>shape (3, 5)</code>"]
  R3["rank 3<br/><b>cube</b><br/><code>shape (3, 3, 5)</code>"]
  R0 --> R1 --> R2 --> R3
"""

MMD_BROADCAST = """
flowchart LR
  X["X<br/><code>(32, 10)</code>"] --> ADD(("+"))
  Y["y<br/><code>(10,)</code>"] --> S1["add an axis<br/><code>(1, 10)</code>"]
  S1 --> S2["repeat 32 times<br/><code>(32, 10)</code>"]
  S2 --> ADD
  ADD --> OUT["result<br/><code>(32, 10)</code>"]
"""

MMD_GRAPH = """
flowchart LR
  X["x"] --> X1["x1 = W . x"]
  X1 --> X2["x2 = x1 + b"]
  X2 --> Y["y = relu(x2)"]
  Y --> L["loss"]
  L -. "d loss / d y" .-> Y
  Y -. "d y / d x2" .-> X2
  X2 -. "d x2 / d x1" .-> X1
  X1 -. "d x1 / d W" .-> X
"""

MMD_LOOP4 = """
flowchart LR
  S1["1. Draw a batch<br/>x and y_true"]
  S2["2. Forward pass<br/>y_pred = model(x)"]
  S3["3. Compute loss<br/>how far off?"]
  S4["4. Update weights<br/>lower the loss"]
  S1 --> S2 --> S3 --> S4
  S4 -. "repeat" .-> S1
"""

MMD_GEOM = """
flowchart TB
  A["Vector addition"] --> A1["Translation"]
  B["Multiply by a rotation matrix"] --> B1["Rotation"]
  C["Multiply by a diagonal matrix"] --> C1["Scaling"]
  D["Multiply by any matrix"] --> D1["Linear transform"]
  E["Linear transform + translation"] --> E1["<b>Affine transform</b><br/>y = W . x + b"]
"""


MMD_PIPELINE = """
flowchart LR
  A["raw images<br/><code>(60000, 28, 28)</code><br/>uint8 0..255"]
  B["reshape<br/><code>(60000, 784)</code>"]
  C["cast + scale<br/>float32 0..1"]
  D["Dense 512<br/>relu"]
  E["Dense 10<br/>softmax"]
  F["10 probabilities<br/>per image"]
  A --> B --> C --> D --> E --> F
"""

MMD_SCRATCH = """
flowchart TB
  NS["NaiveSequential<br/><small>calls layers in order</small>"]
  ND1["NaiveDense<br/><small>W, b, activation</small>"]
  ND2["NaiveDense<br/><small>W, b, activation</small>"]
  BG["BatchGenerator<br/><small>slices the batch axis</small>"]
  ST["one_training_step<br/><small>forward, loss, grads, update</small>"]
  FIT["fit<br/><small>epochs x batches</small>"]
  NS --> ND1
  NS --> ND2
  FIT --> BG
  FIT --> ST
  ST --> NS
"""

NB = ["01_first_mnist.ipynb", "02_tensors_and_operations.ipynb",
      "03_gradients_and_sgd.ipynb", "04_mnist_from_scratch.ipynb"]

DECK = {
    "id": "ch02",
    "kind": "chapter",
    "number": 2,
    "title": "The Mathematical Building Blocks of Neural Networks",
    "subtitle": "Tensors, tensor operations, and gradient-based optimisation — "
                "explained through code you can run rather than notation you have "
                "to decode.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 2",
    "source_url": chapter_url(2),
    "duration": "3 hours (2 sessions)",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(2, local_notebooks=NB),
    "objectives": [
        "Run the first MNIST example end to end and name the role of **layers, "
        "loss, optimizer, and metrics** in each line of it.",
        "Read a tensor's **rank, shape, and dtype**, and map real data — vectors, "
        "timeseries, images, video — onto its tensor shape.",
        "Explain **element-wise operations, broadcasting, the tensor product, and "
        "reshaping**, together with what each one means geometrically.",
        "Describe **derivatives, gradients, mini-batch SGD, and the chain rule**, "
        "and point to where each lives in a computation graph.",
        "Rewrite MNIST **from scratch** — layer, model, batch generator, and "
        "training loop — without calling `fit()`.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Roadmap",
            "title": "One example, taken apart all the way down",
            "blocks": [
                {"t": "lead", "md": "The chapter travels a full circle: run MNIST with "
                                    "`fit()`, dismantle every piece of it, then "
                                    "==rewrite the whole thing from scratch== and show the "
                                    "result holds up."},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "🔢", "h": "1 · First example",
                     "p": "MNIST in ten lines. Working first, understood second.",
                     "tag": "2.1"},
                    {"ico": "📦", "h": "2 · Tensors",
                     "p": "Rank, shape, dtype, slicing, the batch axis, real-world data.",
                     "tag": "2.2"},
                    {"ico": "⚙", "h": "3 · Tensor operations",
                     "p": "Element-wise, broadcasting, matmul, reshape — and their geometry.",
                     "tag": "2.3"},
                    {"ico": "📉", "h": "4 · The engine",
                     "p": "Derivatives, gradients, SGD, the chain rule, autodiff.",
                     "tag": "2.4 – 2.6"},
                ]},
            ],
            "notes": "Long session. Break between 2.3 and 2.4: the first half is about data, "
                     "the second half about learning.",
        },

        {
            "type": "slide",
            "kicker": "Roadmap",
            "title": "Why this chapter shows code instead of notation",
            "blocks": [
                {"t": "quote",
                 "md": "Runnable code is the most precise, unambiguous description of a "
                       "mathematical operation.",
                 "cite": "The working principle of chapter 2"},
                {"t": "p", "md": "Every concept here is introduced twice: once as an idea, "
                                 "and once as a few lines you can execute and inspect. "
                                 "If the two ever disagree, ==the code is right=="},
            ],
        },

        {"type": "section", "num": "01", "title": "A first look at a neural network",
         "lead": "MNIST — the \"hello world\" of deep learning."},

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "The data: 60,000 to train on, 10,000 to be judged on",
            "blocks": [
                {"t": "p", "md": "MNIST is a set of grayscale images of handwritten digits, "
                                 "each 28×28 pixels, already split into a training set and a "
                                 "test set. Keras ships it, so there is nothing to download "
                                 "by hand."},
                {"t": "code", "lang": "python", "file": "listing 2.1 — loading MNIST",
                 # Walked line by line, with the state after each. Reading a
                 # listing and watching one run are different things, and a
                 # slide only ever supported the first.
                 "run": [
                     {"line": 1,
                      "note": "Keras ships the dataset. The first call downloads "
                              "it; later calls read the local cache.",
                      "vars": {}},
                     {"line": 3,
                      "note": "Four arrays come back, already split into a "
                              "training set and a test set.",
                      "vars": {"train_images": "ndarray", "train_labels": "ndarray",
                               "test_images": "ndarray", "test_labels": "ndarray"}},
                     {"line": 5,
                      "note": "60,000 images, each a 28x28 grid of 8-bit values. "
                              "Rank 3 — three indices to reach one pixel.",
                      "vars": {"train_images.shape": "(60000, 28, 28)",
                               "dtype": "uint8"},
                      "out": "(60000, 28, 28) uint8"},
                     {"line": 6,
                      "note": "One label per image, 0 to 9. Rank 1.",
                      "vars": {"len(train_labels)": "60000"},
                      "out": "60000 [5 0 4 1 9 2 1 3 1 4]"},
                     {"line": 7,
                      "note": "A separate 10,000 — not trained on, and not looked "
                              "at until the very end.",
                      "vars": {"test_images.shape": "(10000, 28, 28)"},
                      "out": "(10000, 28, 28)"},
                 ],
                 "src": """from keras.datasets import mnist

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

print(train_images.shape, train_images.dtype)
print(len(train_labels), train_labels[:10])
print(test_images.shape)"""},
                {"t": "out", "src": """(60000, 28, 28) uint8
60000 [5 0 4 1 9 2 1 3 1 4]
(10000, 28, 28)"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "Three words used precisely from here on",
            "blocks": [
                {"t": "table",
                 "head": ["Term", "What it means here"],
                 "widths": [22, 78],
                 "rows": [
                     ["**Sample**", "One data point — a single 28×28 image."],
                     ["**Class**", "One category — a digit from 0 to 9."],
                     ["**Label**", "The class attached to one particular sample."],
                 ]},
                {"t": "p", "md": "These are used consistently for the rest of the book, and "
                                 "mixing them up is the fastest way to misread an error "
                                 "message later."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "The model: two layers, and what a layer is for",
            "blocks": [
                {"t": "p", "md": "A **layer** is a filter for data: it takes data in and puts "
                                 "out a more useful representation of it. The model below "
                                 "chains two of them."},
                {"t": "code", "lang": "python", "file": "listing 2.2 — the model",
                 "src": """import keras
from keras import layers

model = keras.Sequential([
    layers.Dense(512, activation="relu"),
    layers.Dense(10, activation="softmax"),
])"""},
                {"t": "band",
                 "md": "The final `softmax` layer emits ==10 probability scores that sum to "
                       "1== — one per digit class. Note there is no `input_shape` anywhere; "
                       "Keras infers it on the first call, which chapter 3 explains."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "Compilation: three choices, and only three",
            "blocks": [
                {"t": "p", "md": "Before a model can be trained it has to be told how to judge itself and how to improve. `compile()` is where those decisions are recorded."},
                {"t": "code", "lang": "python", "file": "listing 2.3 — compile",
                 "src": """model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)"""},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📏", "h": "Loss",
                     "p": "The feedback signal the network steers by. **This is what gets "
                          "minimised.**", "style": "accent"},
                    {"ico": "🎚", "h": "Optimizer",
                     "p": "The mechanism by which the network updates itself from that signal.",
                     "style": "accent"},
                    {"ico": "👁", "h": "Metrics",
                     "p": "Watched during training, but ==never optimised for==.",
                     "style": "accent"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "Preprocessing: flatten, cast, and scale",
            "blocks": [
                {"t": "p", "md": "The images arrive as 8-bit integers in a 28×28 grid. The "
                                 "`Dense` layers want a flat vector of floats in a small "
                                 "range, so both shape and dtype have to change."},
                {"t": "code", "lang": "python", "file": "listing 2.4 — preparing the data",
                 "src": """train_images = train_images.reshape((60000, 28 * 28))
train_images = train_images.astype("float32") / 255

test_images = test_images.reshape((10000, 28 * 28))
test_images = test_images.astype("float32") / 255

print(train_images.shape, train_images.dtype, train_images.min(), train_images.max())"""},
                {"t": "out", "src": "(60000, 784) float32 0.0 1.0"},
                {"t": "band",
                 "md": "Two things changed: the shape went from `(60000, 28, 28)` to "
                       "`(60000, 784)`, and the values went from `0..255` integers to "
                       "==`0..1` floats==. Chapter 6 explains why the second matters so much."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "The same network, drawn as what it is",
            "blocks": [
                neural_net(
                    "ch02-mnist-net",
                    [("Input", 784, "one per pixel"),
                     ("Dense · relu", 512),
                     ("Dense · softmax", 10, "one per digit")],
                    highlight=(1, 2),
                    cap="784 units, then 512, then 10. Six are drawn per layer and the "
                        "rest are the ellipsis — the counts underneath are the real "
                        "ones."),
                {"t": "p", "md": "This is the model from listing 2.2, drawn. Every unit in "
                                 "a layer is connected to every unit in the next, which is "
                                 "what `Dense` means — and why the first layer alone holds "
                                 "**401,920 weights**. The next slide shrinks it to four "
                                 "inputs so the arithmetic fits on a slide."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "One forward pass, with the arithmetic",
            "blocks": [
                forward_pass(
                    "ch02-forward",
                    inputs=[0.9, 0.2, 0.7, 0.4],
                    layers=[5, 3],
                    out_labels=["cat", "dog", "bird"],
                    cap="A four-input toy of the same shape, small enough that every "
                        "number fits on the slide. Press play."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "Reading the forward pass",
            "blocks": [
                {"t": "steps", "items": [
                    "**Every edge is a weight, and the drawing shows it.** Warm means "
                    "positive, rose means negative, and thickness is magnitude. A "
                    "trained network is exactly this picture with different numbers on "
                    "the edges — nothing else changes.",
                    "**Each unit sums what reaches it, adds a bias, then applies relu.** "
                    "The sum for the top hidden unit is printed under the figure so you "
                    "can check it against the inputs and weights shown.",
                    "**A unit reading `0` is not broken — it is `relu` doing its job.** "
                    "Its sum came out negative and `max(0, z)` clipped it. That unit "
                    "contributes nothing to this input, and ==a different input would "
                    "wake it up==.",
                    "**The output layer uses softmax**, so its three numbers are "
                    "positive and sum to 1 — which is what makes them readable as "
                    "probabilities.",
                ]},
                {"t": "band", "md": "Scale this to 784 inputs, 512 hidden units and 10 "
                                    "outputs and you have the MNIST model from listing "
                                    "2.2 — **401,920 weights on the first layer alone**, "
                                    "every one doing what the four here are doing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "The whole first example, as a shape pipeline",
            "blocks": [
                {"t": "mmd", "id": "ch02-pipeline", "src": MMD_PIPELINE,
                 "cap": "Every arrow changes either the shape or the dtype. Nothing else "
                        "happens in the first example."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "Training, and the first crack to notice",
            "blocks": [
                {"t": "p", "md": "`fit()` runs the training loop: five passes over the data, 128 samples at a time. Then `evaluate()` asks the only question that matters — how does it do on images it has never seen?"},
                {"t": "code", "lang": "python", "file": "listing 2.5 — fit",
                 "src": """model.fit(train_images, train_labels, epochs=5, batch_size=128)

test_loss, test_acc = model.evaluate(test_images, test_labels)
print(f"test accuracy: {test_acc:.3f}")"""},
                {"t": "out", "src": """Epoch 1/5
469/469 ---- 3s 5ms/step - accuracy: 0.8747 - loss: 0.4358
Epoch 5/5
469/469 ---- 2s 5ms/step - accuracy: 0.9890 - loss: 0.0361

313/313 ---- 1s 2ms/step - accuracy: 0.9780 - loss: 0.0745
test accuracy: 0.978"""},
                {"t": "band", "style": "amber",
                 "md": "**98.9%** on data it trained on, **97.8%** on data it had never seen. "
                       "That gap is not noise — it is ==overfitting==, and chapter 5 treats "
                       "it as the central problem of the field."},
            ],
            "notes": "Say up front that the exact digits move between runs, so nobody panics "
                     "when their notebook prints 97.6%.",
        },

        {
            "type": "slide",
            "kicker": "Section 2.1",
            "title": "Making a prediction, and reading it",
            "blocks": [
                {"t": "p", "md": "`predict()` returns the ten probabilities per image. The "
                                 "predicted class is simply the index of the largest one."},
                {"t": "code", "lang": "python", "file": "listing 2.6 — predicting",
                 "src": """test_digits = test_images[0:10]
predictions = model.predict(test_digits)

print(predictions[0].argmax())      # which class?
print(predictions[0].max())         # how confident?
print(test_labels[0])               # what was the truth?"""},
                {"t": "out", "src": """7
0.99993
7"""},
                {"t": "p", "md": "Right answer, and near-total confidence. Chapter 5 will show "
                                 "why ==confidence and correctness are not the same thing=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Data representations: tensors",
         "lead": "A container for data. Three attributes, and one special axis."},

        {
            "type": "slide",
            "kicker": "Section 2.2",
            "title": "Rank, shape, dtype",
            "blocks": [
                tensor_ranks(
                    "ch02-tensor-ranks",
                    cap="The same four numbers 7, 2, 9, 4 appear at every rank. What "
                        "changes is how many indices it takes to reach one of them."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.2",
            "title": "Reading the drawing: what each rank actually is",
            "blocks": [
                {"t": "p", "md": "Every tensor has exactly three defining attributes: its "
                                 "**number of axes** (rank), its **shape**, and its "
                                 "**dtype**. Everything else follows from those."},
                {"t": "table",
                 "head": ["Rank", "Name", "Shape", "To reach one number", "Example"],
                 "widths": [10, 16, 16, 26, 32],
                 "rows": [
                     ["0", "scalar", "`()`", "`t`",
                      "a loss value — one number per batch"],
                     ["1", "vector", "`(4,)`", "`t[i]`",
                      "one MNIST image after flattening is `(784,)`"],
                     ["2", "matrix", "`(3, 4)`", "`t[i][j]`",
                      "a batch of flattened images, `(128, 784)`"],
                     ["3", "tensor", "`(2, 3, 4)`", "`t[i][j][k]`",
                      "a batch of images before flattening, `(128, 28, 28)`"],
                 ]},
                {"t": "p", "md": "**Rank is a count of axes, not a size.** A `(60000, 28, "
                                 "28)` tensor and a `(2, 3, 4)` tensor are both rank 3, "
                                 "and every rule you learn about one applies to the other. "
                                 "==That is the whole reason the abstraction is worth "
                                 "having.=="},
                {"t": "band", "md": "The word *dimension* is used for two different things "
                                    "and causes real confusion: a rank-3 tensor has **3 "
                                    "axes**, while a `(784,)` vector is often called "
                                    "*784-dimensional*. Say **rank** for axes and **shape** "
                                    "for sizes, and the ambiguity disappears."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.2",
            "title": "Reading them off a real tensor",
            "blocks": [
                {"t": "p", "md": "MNIST before preprocessing is a rank-3 tensor: 60,000 "
                                 "images, each a 28×28 grid of 8-bit grayscale values."},
                {"t": "code", "lang": "python", "file": "the three attributes",
                 "src": """(train_images, train_labels), _ = mnist.load_data()

print(train_images.ndim)     # rank: how many axes
print(train_images.shape)    # shape: how long each axis is
print(train_images.dtype)    # dtype: what the entries are"""},
                {"t": "out", "src": """3
(60000, 28, 28)
uint8"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.2",
            "title": "The terminology trap that costs people an afternoon",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "A **5-dimensional vector** is not a **5-dimensional tensor**. The "
                       "first has ==one axis holding five numbers==; the second has "
                       "==five axes=="},
                {"t": "p", "md": "Misreading this makes shape error messages unintelligible, "
                                 "and shape errors are the most common failure you will hit "
                                 "in the exercises."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.2",
            "title": "Slicing tensors",
            "blocks": [
                {"t": "p", "md": "Selecting part of a tensor uses the same bracket syntax as "
                                 "NumPy. A colon means *all of this axis*, and negative "
                                 "indices count from the end."},
                {"t": "code", "lang": "python", "file": "listing 2.7–2.8 — slices",
                 "src": """print(train_images[10:100].shape)          # 90 images
print(train_images[:, 14:, 14:].shape)     # bottom-right 14x14 corner
print(train_images[:, 7:-7, 7:-7].shape)   # centre 14x14, via negative indices""",
                 "run": [
                     {"line": 1, "note": "Slicing the first axis picks **images**. "
                                         "100 − 10 = 90, and each is still the "
                                         "full 28 × 28.",
                      "vars": {"result": "(90, 28, 28)"}},
                     {"line": 2, "note": "Two colons: keep every image, then cut "
                                         "rows and columns. `14:` means from 14 "
                                         "to the end — the bottom-right quarter.",
                      "vars": {"result": "(60000, 14, 14)"}},
                     {"line": 3, "note": "`7:-7` counts 7 in from each end, which "
                                         "is 28 − 7 − 7 = 14. Same size as the "
                                         "line above, ==a different 14 × 14==.",
                      "vars": {"result": "(60000, 14, 14)",
                               "region": "the centre, not the corner"}},
                 ]},
                {"t": "out", "src": """(90, 28, 28)
(60000, 14, 14)
(60000, 14, 14)"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.2",
            "title": "The batch axis is always axis 0",
            "blocks": [
                {"t": "p", "md": "Models are not trained on whole datasets; they are trained on "
                                 "small **batches**. Cutting a batch is just a slice along "
                                 "the first axis."},
                {"t": "code", "lang": "python", "file": "listing 2.9 — batches",
                 "src": """batch = train_images[:128]        # batch 0
batch = train_images[128:256]     # batch 1

n = 3
batch = train_images[128 * n : 128 * (n + 1)]     # batch n
print(batch.shape)"""},
                {"t": "out", "src": "(128, 28, 28)"},
                {"t": "band",
                 "md": "Axis 0 is the **samples axis** — and because of batching it is also "
                       "called the **batch axis**. ==Every shape error you will read starts "
                       "with identifying this axis.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.2.7 – 2.2.10",
            "title": "Real-world data, and the shape it takes",
            "blocks": [
                {"t": "table",
                 "head": ["Kind of data", "Rank", "Shape", "Example from the book"],
                 "widths": [20, 8, 30, 42],
                 "rows": [
                     ["**Vector data**", "2", "`(samples, features)`",
                      "100,000 people × (age, gender, income) → (100000, 3)"],
                     ["**Timeseries**", "3", "`(samples, timesteps, features)`",
                      "250 days × 390 minutes × 3 values → (250, 390, 3)"],
                     ["**Images**", "4", "`(samples, h, w, channels)`",
                      "128 RGB images at 256×256 → (128, 256, 256, 3)"],
                     ["**Video**", "5", "`(samples, frames, h, w, channels)`",
                      "4 clips × 240 frames × 144×256 × RGB → (4, 240, 144, 256, 3)"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.2.9",
            "title": "Channels-last or channels-first — and why it bites",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "bullets", "items": [
                            "**Channels-last** `(…, h, w, c)` — the TensorFlow and JAX "
                            "convention.",
                            "**Channels-first** `(…, c, h, w)` — the PyTorch convention.",
                        ]},
                        {"t": "p", "md": "Keras 3 picks between them with "
                                         "`image_data_format`."},
                    ],
                    [
                        {"t": "band", "style": "amber",
                         "md": "Getting this wrong produces shape errors that look "
                               "nonsensical, because both orderings are *valid* — just not "
                               "for the same layer."},
                    ],
                ]},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "106,168,320", "l": "values in that 60-second video example"},
                    {"v": "425 MB", "l": "its size at float32"},
                ]},
            ],
        },

        {"type": "section", "num": "03", "title": "The gears: tensor operations",
         "lead": "It all reduces to a handful of operations — each with a geometric meaning."},

        {
            "type": "slide",
            "kicker": "Section 2.3",
            "title": "A Dense layer is three operations, and nothing else",
            "blocks": [
                {"t": "p", "md": "Whatever else a network contains, its `Dense` layer computes "
                                 "exactly this. Every symbol in it is covered in this section."},
                {"t": "code", "lang": "python", "file": "the whole of a Dense layer",
                 "src": """output = relu(matmul(input, W) + b)
#        ^          ^            ^
#        |          |            +-- addition (with broadcasting)
#        |          +--------------- tensor product
#        +-------------------------- element-wise operation"""},
                {"t": "p", "md": "`relu(x)` is simply `max(x, 0)`: it zeroes out anything "
                                 "negative and leaves the rest alone."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.1",
            "title": "Element-wise operations, written the slow way",
            "blocks": [
                {"t": "p", "md": "An element-wise operation applies independently to each "
                                 "entry — which is precisely why it parallelises so well. "
                                 "Written out as loops, `relu` is this:"},
                {"t": "code", "lang": "python", "file": "listing 2.10 — naive relu",
                 # Two nested loops over a matrix. Watching the indices move is
                 # what makes "element-wise" mean something.
                 "run": [
                     {"line": 1, "note": "The assertions state what the function "
                                         "assumes. A rank-2 float tensor, and "
                                         "nothing else.",
                      "vars": {"x.ndim": "2"}},
                     {"line": 4, "note": "Copy first. Without this the function "
                                         "would modify its caller's tensor — a "
                                         "surprise nobody wants.",
                      "vars": {"x": "a copy"}},
                     {"line": 5, "note": "Outer loop: one row at a time.",
                      "vars": {"i": "0"}},
                     {"line": 6, "note": "Inner loop: one element at a time. "
                                         "This is the pair of loops NumPy "
                                         "replaces with vectorised C.",
                      "vars": {"i": "0", "j": "0"}},
                     {"line": 7, "note": "The operation itself: keep it if "
                                         "positive, otherwise zero.",
                      "vars": {"x[0][0]": "max(x[0][0], 0)"}},
                     {"line": 8, "note": "Every element, independently. Nothing "
                                         "here looks at its neighbours — that "
                                         "is what element-wise means.",
                      "vars": {"i·j": "all pairs"}, "out": "the same shape, "
                                                           "no negatives"},
                 ],
                 "src": """def naive_relu(x):
    assert len(x.shape) == 2
    x = x.copy()
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            x[i, j] = max(x[i, j], 0)
    return x"""},
                {"t": "p", "md": "Correct, readable — and unusably slow, as the next slide "
                                 "shows."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.1",
            "title": "…and the fast way, which is the same operation",
            "blocks": [
                {"t": "p", "md": "In practice you never write those loops. NumPy expresses the identical computation in two lines — and the difference is not cosmetic."},
                {"t": "code", "lang": "python", "file": "the vectorised version",
                 "src": """z = x + y
z = np.maximum(z, 0.0)"""},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "0.02 s", "l": "vectorised NumPy, 1,000 iterations"},
                    {"v": "2.45 s", "l": "naive Python loops, 1,000 iterations"},
                ]},
                {"t": "band",
                 "md": "Roughly **100×**, and it is not a language effect. NumPy hands the "
                       "work to BLAS routines written in C and Fortran; on a GPU the same "
                       "operation runs as ==fully vectorised CUDA=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.2",
            "title": "Broadcasting: fitting a small shape to a big one",
            "blocks": [
                {"t": "mmd", "id": "ch02-broadcast", "src": MMD_BROADCAST,
                 "cap": "Two steps: add axes until the ranks match, then repeat along the "
                        "new axes."},
                {"t": "p", "md": "No memory is actually duplicated — the repetition is "
                                 "==algorithmic, not physical=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.2",
            "title": "The rule, and where it quietly goes wrong",
            "blocks": [
                {"t": "p", "md": "Broadcasting applies when one tensor has shape "
                                 "`(a, b, …, n, n+1, …, m)` and the other has "
                                 "`(n, n+1, …, m)`."},
                {"t": "code", "lang": "python", "file": "listing 2.11 — broadcasting in anger",
                 "src": """X = np.random.random((64, 3, 32, 10))
y = np.random.random((32, 10))

z = np.maximum(X, y)      # y is broadcast across the first two axes
print(z.shape)"""},
                {"t": "out", "src": "(64, 3, 32, 10)"},
                {"t": "band", "style": "amber",
                 "md": "This is the most common source of **silent** bugs: the shapes line "
                       "up, the code runs, and the ==meaning is wrong==. When a result looks "
                       "strange, print the shapes first."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.3",
            "title": "The tensor product, and its one compatibility rule",
            "blocks": [
                {"t": "p", "md": "The tensor product — `matmul`, or the `@` operator — is the "
                                 "operation that actually combines features. It has exactly "
                                 "one rule you must remember."},
                {"t": "code", "lang": "python", "file": "matmul",
                 "src": """z = np.matmul(x, y)
z = x @ y                      # the same thing, shorter

# compatibility:  x.shape[1] == y.shape[0]
# result shape:  (x.shape[0], y.shape[1])

# (a, b, c, d) @ (d,)    -> (a, b, c)
# (a, b, c, d) @ (d, e)  -> (a, b, c, e)""",
                 "run": [
                     {"line": 4, "note": "The only rule. The **last** axis of x "
                                         "must match the **first** axis of y — "
                                         "everything else about the shapes is "
                                         "free.",
                      "vars": {"x.shape": "(64, 3, 32)", "y.shape": "(32, 10)"}},
                     {"line": 4, "note": "32 == 32, so it is legal. Had y been "
                                         "(16, 10) this line is where it fails, "
                                         "not somewhere later.",
                      "vars": {"x.shape[-1]": "32", "y.shape[0]": "32",
                               "compatible": "yes"}},
                     {"line": 5, "note": "The matched axis **disappears**. That "
                                         "is what the product does: it sums over "
                                         "it.",
                      "vars": {"z.shape": "(64, 3, 10)"}},
                     {"line": 8, "note": "Which is exactly the general rule, with "
                                         "a = 64, b = 3, d = 32, e = 10. A dense "
                                         "layer is this line.",
                      "vars": {"(a,b,d) @ (d,e)": "(a,b,e)"}},
                 ]},
                {"t": "p", "md": "Visually: line the two up as rectangles — ==the width of the "
                                 "first must match the height of the second=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.4",
            "title": "Reshaping rearranges; it never invents or destroys",
            "blocks": [
                {"t": "p", "md": "A reshape changes how the same coefficients are laid out. "
                                 "The total count is unchanged, which is why it is cheap."},
                {"t": "code", "lang": "python", "file": "listing 2.12 — reshape and transpose",
                 "src": """x = np.array([[0., 1.],
              [2., 3.],
              [4., 5.]])          # shape (3, 2)

print(np.reshape(x, (6,)).shape)     # flattened
print(np.reshape(x, (2, 3)).shape)   # regrouped

print(np.transpose(np.zeros((300, 20))).shape)   # rows and columns exchanged""",
                 "run": [
                     {"line": 1, "note": "Six numbers, arranged as three rows of "
                                         "two. Count them — the count is the "
                                         "thing that will not change.",
                      "vars": {"x.shape": "(3, 2)", "elements": "6"}},
                     {"line": 5, "note": "Flattened. Same six numbers, read in "
                                         "the same order, grouped differently.",
                      "vars": {"shape": "(6,)", "elements": "6",
                               "values": "0. 1. 2. 3. 4. 5."}},
                     {"line": 6, "note": "Regrouped as two rows of three. Still "
                                         "the same six, still in that order — "
                                         "==reshape never reorders, it only "
                                         "regroups==.",
                      "vars": {"shape": "(2, 3)", "elements": "6"}},
                     {"line": 8, "note": "Transpose is the exception worth "
                                         "noticing: it **does** change which "
                                         "number sits where, but 300 × 20 and "
                                         "20 × 300 are still 6 000 numbers.",
                      "vars": {"before": "(300, 20)", "after": "(20, 300)",
                               "elements": "6 000 either way"}},
                 ]},
                {"t": "out", "src": """(6,)
(2, 3)
(20, 300)"""},
                {"t": "band",
                 "md": "This is exactly what `train_images.reshape((60000, 784))` did in the "
                       "first example: ==the pixels never changed, only their arrangement=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.5",
            "title": "Every tensor operation is a geometric one",
            "blocks": [
                geometric_ops(
                    "ch02-geom-ops",
                    cap="One shape, four operations. The dashed outline is where it "
                        "started."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.5",
            "title": "Reading the drawing: what moved, and what did it",
            "blocks": [
                {"t": "p", "md": "Treat the numbers in a tensor as **coordinates**. Then "
                                 "every operation in the previous slide is a movement, and "
                                 "the matrix is the instruction for the movement."},
                {"t": "table",
                 "head": ["Operation", "What it does to the shape", "Written as"],
                 "widths": [22, 46, 32],
                 "rows": [
                     ["**Translation**",
                      "Slides it. Every point moves by the same vector; nothing turns "
                      "or stretches.", "`y = x + b`"],
                     ["**Rotation**",
                      "Turns it about the origin. Lengths and angles survive — the shape "
                      "is the same shape, pointing elsewhere.", "`y = R @ x`"],
                     ["**Scaling**",
                      "Stretches each axis by its own factor. Here x by 1.5 and y by 0.6, "
                      "which is why it comes out squat.", "`y = D @ x`"],
                     ["**Affine**",
                      "Any matrix, then a vector. Straight lines stay straight and "
                      "parallel lines stay parallel — but angles do not survive.",
                      "`y = W @ x + b`"],
                 ]},
                {"t": "band", "md": "**A `Dense` layer is the fourth row.** `W @ x + b` is "
                                    "an affine transform, and nothing else. A stack of "
                                    "them with no activation between is still one affine "
                                    "transform — which is the next slide, and the reason "
                                    "activations exist."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.5",
            "title": "Why an activation function is not optional",
            "blocks": [
                {"t": "p", "md": "A `Dense` layer without an activation computes "
                                 "`y = W @ x + b` — an affine transform. Chain two of them "
                                 "and expand:"},
                {"t": "code", "lang": "python", "file": "two affine layers collapse into one",
                 "src": """affine2(affine1(x)) == (W2 @ W1) @ x + (W2 @ b1 + b2)
#                     \\_________/         \\______________/
#                      one matrix           one vector"""},
                {"t": "band", "style": "rose",
                 "md": "So a deep stack of `Dense` layers with no activation is ==secretly a "
                       "single linear model==, however many layers you give it. Nonlinearities "
                       "such as `relu` are what make the hypothesis space rich."},
            ],
            "notes": "If a product manager takes one thing from chapter 2, this is it: "
                     "without nonlinearity, depth buys nothing at all.",
        },

        {
            "type": "slide",
            "kicker": "Section 2.3.5",
            "title": "Deep learning as uncrumpling a paper ball",
            "blocks": [
                {"t": "p", "md": "Chollet's image for what a deep network does: complicated, "
                                 "folded data **manifolds** are gradually pulled apart until "
                                 "the classes separate cleanly."},
                {"t": "band",
                 "md": "It happens through a long series of **small, elementary geometric "
                       "moves** — like uncrumpling a paper ball with successive finger "
                       "movements. ==Each layer disentangles the data a little.=="},
                {"t": "p", "md": "Chapter 5 makes this precise, under the name of the "
                                 "*manifold hypothesis*."},
            ],
        },

        {"type": "section", "num": "04", "title": "The engine: gradient-based optimisation",
         "lead": "Derivatives, gradients, SGD, and the chain rule."},

        {
            "type": "slide",
            "kicker": "Section 2.4",
            "title": "The training loop, and which step is hard",
            "blocks": [
                {"t": "mmd", "id": "ch02-loop4", "src": MMD_LOOP4,
                 "cap": "Four steps, repeated over batches. Only the fourth is difficult."},
                {"t": "band", "style": "amber",
                 "md": "Tuning each coefficient by hand is impossible — modern networks have "
                       "==millions to billions of parameters==. Gradient descent solves for "
                       "all of them at once."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.1",
            "title": "A derivative is the slope of a local approximation",
            "blocks": [
                {"t": "p", "md": "For a smooth function, a small change in `x` produces a "
                                 "small change in `y`. Near a point, `f(x + ε) ≈ y + a·ε`, "
                                 "and that `a` is the **derivative**."},
                {"t": "bullets", "items": [
                    "`a` negative → increasing `x` **decreases** `f(x)`.",
                    "`a` positive → increasing `x` **increases** `f(x)`.",
                    "Its magnitude says how fast the change happens.",
                ]},
                {"t": "band",
                 "md": "So to make `f` smaller, move `x` ==in the direction opposite its "
                       "derivative==. That single sentence is the whole of optimisation."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.2",
            "title": "A gradient is a derivative for tensors",
            "blocks": [
                {"t": "p", "md": "Hold the data fixed, and the loss becomes a function of the "
                                 "weights alone: `loss_value = f(W)`."},
                {"t": "code", "lang": "python", "file": "what the gradient is a gradient of",
                 "src": """y_pred = matmul(x, W)
loss_value = loss(y_pred, y_true)

# For fixed x and y_true this is just  loss_value = f(W)
# grad(loss_value, W0) is a tensor SHAPED LIKE W, whose every coefficient says
# in which direction, and how strongly, the loss moves if you nudge that weight."""},
                {"t": "band",
                 "md": "To lower the loss, step against the gradient: "
                       "`W1 = W0 - step * grad(f(W0), W0)`"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.3",
            "title": "Why this is done by iteration and not by solving",
            "blocks": [
                {"t": "p", "md": "Minima occur where the derivative is zero. So why not just "
                                 "solve `grad(f(W), W) = 0` directly?"},
                {"t": "band", "style": "rose",
                 "md": "Because for a network with millions of parameters that is "
                       "==analytically intractable==. Iteration is not a shortcut; it is the "
                       "only available route."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.3",
            "title": "Mini-batch stochastic gradient descent",
            "blocks": [
                {"t": "steps", "items": [
                    "Draw a **random** batch of samples and targets. (The word *stochastic* "
                    "comes from this randomness.)",
                    "Forward pass → predictions.",
                    "Compute the loss.",
                    "**Backward pass** → gradient of the loss with respect to the parameters.",
                    "`W -= learning_rate * gradient`.",
                ]},
                {"t": "p", "md": "Repeat. Each step lowers the loss a little; enough steps "
                                 "and the model fits."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.3",
            "title": "Seven steps of it, on a real curve",
            "blocks": [
                sgd_descent(
                    "ch02-sgd-walk",
                    cap="Cyan: the slope measured at that point. Amber: the step taken "
                        "because of it."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.3",
            "title": "Reading the walk: three things to notice",
            "blocks": [
                {"t": "steps", "items": [
                    "**The step is the slope, scaled.** Nothing decides how far to move "
                    "except `learning_rate × gradient`. Where the curve is steep the step "
                    "is long; where it flattens the step shortens ==on its own==. No "
                    "schedule does that — it falls out of the rule.",
                    "**It never lands exactly on the minimum,** and it does not need to. "
                    "Training stops when the loss stops improving, not when the gradient "
                    "reaches zero.",
                    "**Only the local slope is known.** At every point the walk sees the "
                    "tangent and nothing else — not the shape of the curve, not where the "
                    "minimum is. That is why a bad learning rate is fatal: the step is "
                    "taken blind.",
                ]},
                {"t": "p", "md": "The arithmetic beside the curve is the whole algorithm. "
                                 "`w ← w − lr · dL/dw`, five times, with real numbers you "
                                 "can check on paper. **Everything else in this chapter is "
                                 "about computing that one derivative efficiently** for "
                                 "millions of parameters at once."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.3",
            "title": "Learning rate: the one number that decides whether it works",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🐢", "h": "Too small",
                     "p": "Convergence crawls — many steps for very little progress. It can "
                          "look as though training has stalled.", "style": "warn"},
                    {"ico": "🌀", "h": "Too large",
                     "p": "Updates overshoot wildly; the loss jumps around and ==never comes "
                          "down==.", "style": "bad"},
                    {"ico": "🎯", "h": "Momentum",
                     "p": "Update using the current gradient **and** previous updates — like "
                          "a ball rolling downhill with enough speed to cross a shallow dip.",
                     "style": "good"},
                ]},
                {"t": "p", "md": "The variants that improve on plain SGD are called "
                                 "**optimizers**: SGD with momentum, Adagrad, RMSprop, Adam."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.4",
            "title": "The chain rule, applied backwards over a graph",
            "blocks": [
                backprop(
                    "ch02-backprop",
                    cap="Top row forward, bottom row backward. Every number computed from "
                        "the one above it."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.4",
            "title": "Reading it backwards: three things that make it work",
            "blocks": [
                {"t": "steps", "items": [
                    "**Each node only needs its own derivative.** Multiply by 1 for the "
                    "addition, by `x` for the multiplication, by 1 or 0 for the relu. "
                    "Nothing on the slide required knowing the whole graph — which is "
                    "exactly why this scales to a network with millions of nodes.",
                    "**The gradient is a product along the path.** "
                    "`2.6 × 1 × 1 × 2 = 5.2`. Applying the chain rule this way, node by "
                    "node from the loss backwards, ==is== backpropagation. There is no "
                    "further mechanism.",
                    "**The forward values are needed by the backward pass.** `∂x1/∂w` is "
                    "`x`, so the input has to still be there when the gradient comes "
                    "back. That is why training uses so much more memory than "
                    "inference — the forward pass is kept.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "**Now make the relu die.** Set `b = -1.2` so `x2` comes out "
                       "negative. Then `∂y/∂x2 = 0`, the product collapses, and "
                       "`∂loss/∂w = 0` — the weight receives **no** gradient and cannot "
                       "learn from this example. A dead unit is not a bug in the code; "
                       "it is this multiplication reaching a zero."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.5",
            "title": "Two details that make the graph work",
            "blocks": [
                {"t": "bullets", "items": [
                    "When there are **several paths** from node `a` to node `b`, the "
                    "contributions of the paths are ==summed==.",
                    "A **computation graph** is a directed acyclic graph of operations. It "
                    "makes computation itself into data — a structure a machine can read and "
                    "manipulate.",
                ]},
                {"t": "band",
                 "md": "Modern frameworks walk that graph for you. That is **automatic "
                       "differentiation**, and it is why ==you will never write "
                       "backpropagation by hand=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.5",
            "title": "Autodiff in three lines",
            "blocks": [
                {"t": "p", "md": "TensorFlow records operations inside a `GradientTape` scope, "
                                 "then replays them backwards on request."},
                {"t": "code", "lang": "python", "file": "listing 2.19 — a first derivative",
                 "src": """import tensorflow as tf

x = tf.Variable(3.0)
with tf.GradientTape() as tape:
    y = 2 * x + 3

print(tape.gradient(y, x))      # dy/dx"""},
                {"t": "out", "src": "tf.Tensor(2.0, shape=(), dtype=float32)"},
                {"t": "p", "md": "The answer is 2, which is what you would get by hand — "
                                 "except nothing here was told the rule for differentiating "
                                 "a line."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.4.5",
            "title": "…and a second derivative, which is a physics answer",
            "blocks": [
                {"t": "p", "md": "Tapes can be nested: the inner one differentiates the position, the outer one differentiates that result again."},
                {"t": "code", "lang": "python", "file": "listing 2.20 — nested tapes",
                 "src": """time = tf.Variable(0.0)

with tf.GradientTape() as outer_tape:
    with tf.GradientTape() as inner_tape:
        position = 4.9 * time ** 2
    speed = inner_tape.gradient(position, time)

acceleration = outer_tape.gradient(speed, time)
print(acceleration)"""},
                {"t": "out", "src": "tf.Tensor(9.8, shape=(), dtype=float32)"},
                {"t": "band",
                 "md": "`position = 4.9·t²` is free fall. Its second derivative is the "
                       "==acceleration due to gravity==, and autodiff returned 9.8 without "
                       "ever being given the formula."},
            ],
        },

        {"type": "section", "num": "05", "title": "Rewriting the first example from scratch",
         "lead": "No fit(), no built-in Dense. The result has to hold up."},

        {
            "type": "slide",
            "kicker": "Section 2.6",
            "title": "What we are about to rebuild",
            "blocks": [
                {"t": "mmd", "id": "ch02-scratch", "src": MMD_SCRATCH,
                 "cap": "Four small classes and one function replace Sequential, Dense, and "
                        "fit() between them."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.6.1",
            "title": "A layer, written out",
            "blocks": [
                {"t": "p", "md": "A `Dense` layer owns two weights and applies one "
                                 "transformation. That is the entire class."},
                {"t": "code", "lang": "python", "file": "listing 2.21 — NaiveDense",
                 "src": """import keras
from keras import ops

class NaiveDense:
    def __init__(self, input_size, output_size, activation=None):
        self.activation = activation
        self.W = keras.Variable(shape=(input_size, output_size), initializer="uniform")
        self.b = keras.Variable(shape=(output_size,), initializer="zeros")

    def __call__(self, inputs):
        x = ops.matmul(inputs, self.W) + self.b
        return self.activation(x) if self.activation is not None else x

    @property
    def weights(self):
        return [self.W, self.b]"""},
                {"t": "p", "md": "`W` starts random and `b` starts at zero — exactly the "
                                 "starting condition chapter 1 described."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.6.1",
            "title": "A model is just layers, applied in order",
            "blocks": [
                {"t": "p", "md": "With a layer in hand, a model needs to do only two things: call the layers in sequence, and expose all their weights together so the optimizer can reach them."},
                {"t": "code", "lang": "python", "file": "listing 2.22 — NaiveSequential",
                 "src": """class NaiveSequential:
    def __init__(self, layers):
        self.layers = layers

    def __call__(self, inputs):
        x = inputs
        for layer in self.layers:
            x = layer(x)
        return x

    @property
    def weights(self):
        return [w for layer in self.layers for w in layer.weights]"""},
                {"t": "band",
                 "md": "Note how little there is to it: a model is ==a list of layers and a "
                       "for loop==. Everything else in Keras is convenience on top."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.6.2 – 2.6.3",
            "title": "One training step is the four figures, in code",
            "blocks": [
                {"t": "p", "md": "Forward pass, loss, gradients, update — the same four moves "
                                 "as the loop diagram, now with a real optimizer."},
                {"t": "code", "lang": "python", "file": "listing 2.24 — one_training_step",
                 "src": """import tensorflow as tf
from keras import optimizers

optimizer = optimizers.SGD(learning_rate=1e-3)

def one_training_step(model, images_batch, labels_batch):
    with tf.GradientTape() as tape:
        predictions = model(images_batch)                       # forward
        loss = ops.sparse_categorical_crossentropy(labels_batch, predictions)
        average_loss = ops.mean(loss)                           # loss
    gradients = tape.gradient(average_loss, model.weights)      # gradients
    optimizer.apply_gradients(zip(gradients, model.weights))    # update
    return average_loss"""},
                {"t": "band",
                 "md": "Four lines, four ideas: ==forward, loss, gradients, update==. Every "
                       "training loop in the rest of the book is a variation on this shape."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.6.4",
            "title": "And the loop around it",
            "blocks": [
                {"t": "p", "md": "Wrapping that single step in two loops — over epochs, and over batches within an epoch — is all that `fit()` does underneath."},
                {"t": "code", "lang": "python", "file": "listing 2.26 — fit, by hand",
                 "src": """def fit(model, images, labels, epochs, batch_size=128):
    for epoch in range(epochs):
        print(f"Epoch {epoch}")
        gen = BatchGenerator(images, labels, batch_size)
        for i in range(gen.num_batches):
            images_batch, labels_batch = gen.next()
            loss = one_training_step(model, images_batch, labels_batch)
            if i % 100 == 0:
                print(f"  loss at batch {i}: {loss:.2f}")"""},
                {"t": "p", "md": "`BatchGenerator` is a dozen lines that hand out consecutive "
                                 "slices — the batch axis from section 2.2, put to work."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.6.5",
            "title": "Does it work? Run it and see",
            "blocks": [
                {"t": "p", "md": "Assemble the same two-layer network out of the hand-written parts, train it for ten epochs, and score it the same way the built-in version was scored."},
                {"t": "code", "lang": "python", "file": "listing 2.27 — evaluating it",
                 "src": """model = NaiveSequential([
    NaiveDense(input_size=28 * 28, output_size=512, activation=ops.relu),
    NaiveDense(input_size=512, output_size=10, activation=ops.softmax),
])
fit(model, train_images, train_labels, epochs=10, batch_size=128)

predictions = model(test_images)
predicted_labels = ops.argmax(predictions, axis=1)
print(f"accuracy: {ops.mean(predicted_labels == test_labels):.2f}")"""},
                {"t": "out", "src": """Epoch 0
  loss at batch 0: 6.19
  loss at batch 400: 2.21
Epoch 9
  loss at batch 0: 0.36
  loss at batch 400: 0.34
accuracy: 0.90"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 2.6.5",
            "title": "90% versus 97.8% — and why that is the lesson",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "The hand-written version scores **lower**, and that is not a bug. "
                       "It uses plain SGD at `learning_rate=1e-3`; the first example used "
                       "==**Adam**=="},
                {"t": "p", "md": "So the gap measures **the choice of optimizer**, not the "
                                 "quality of the implementation. It is one of the clearest "
                                 "demonstrations in the book of how much that choice is worth."},
            ],
            "notes": "This slide is misread more than any other in the chapter. State plainly "
                     "that the lower number does not mean the manual code is wrong.",
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Tensors** are containers with **rank, shape, dtype**. Axis 0 is the "
                    "samples axis, and therefore the batch axis.",
                    "**Tensor operations are geometric.** A Dense layer without an activation "
                    "is an affine transform, and stacking those still gives an affine transform.",
                    "**Learning** means finding weight values that minimise the loss on the "
                    "training data.",
                    "**Mini-batch SGD** updates weights from gradients computed on random batches.",
                    "**Chain rule + autodiff = backpropagation**, carried out over a "
                    "computation graph.",
                    "**Loss** measures success at the task; **optimizer** decides how the "
                    "descent is performed — and that choice is worth several points of accuracy.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_first_mnist.ipynb",
                     "href": notebook_url(2, "01_first_mnist.ipynb")},
                    {"k": "NOTEBOOK", "ic": "📓", "v": "04_mnist_from_scratch.ipynb",
                     "href": notebook_url(2, "04_mnist_from_scratch.ipynb")},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 3 — The frameworks",
                     "href": "../ch03/index.html"},
                ]},
            ],
        },
    ],
}
