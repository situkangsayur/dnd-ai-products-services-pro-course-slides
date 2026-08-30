# -*- coding: utf-8 -*-
"""Chapter 8 — Image classification.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 8
(pp. 231-267), read from the book PDF.

The chapter builds one toolbox in three passes over the same dogs-vs-cats
problem: train small from scratch, extract features from a pretrained model,
then fine-tune it. Accuracy climbs 80% -> 84% -> 98.1% -> 98.6%.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402
from diagrams import conv_compute  # noqa: E402


MMD_LOCALGLOBAL = """
flowchart TB
  subgraph D["Dense layer"]
    direction TB
    D1["Sees ALL pixels at once"] --> D2["Learns <b>global</b> patterns"]
    D2 --> D3["A pattern learned in one corner<br/>must be relearned in another"]
  end
  subgraph C["Convolution layer"]
    direction TB
    C1["Sees a small window<br/>3 x 3 or 5 x 5"] --> C2["Learns <b>local</b> patterns"]
    C2 --> C3["Translation invariant:<br/>learn once, recognise anywhere"]
  end
  D ~~~ C
"""

MMD_HIERARCHY = """
flowchart LR
  P["Pixels"] --> L1["Conv layer 1<br/>edges, colours,<br/>textures"]
  L1 --> L2["Conv layer 2<br/>corners and<br/>simple shapes"]
  L2 --> L3["Conv layer 3<br/>eyes, ears,<br/>object parts"]
  L3 --> L4["Conv layer 4<br/>whole objects:<br/>&quot;cat&quot;"]
"""

MMD_SHAPES = """
flowchart LR
  A["Input<br/><code>180 x 180 x 3</code>"] --> B["Conv + Pool<br/><code>89 x 89 x 32</code>"]
  B --> C["Conv + Pool<br/><code>43 x 43 x 64</code>"]
  C --> D["Conv + Pool<br/><code>20 x 20 x 128</code>"]
  D --> E["Conv + Pool<br/><code>9 x 9 x 256</code>"]
  E --> F["Conv<br/><code>7 x 7 x 512</code>"]
  F --> G["GlobalAvgPool<br/><code>512</code>"]
  G --> H["Dense 1<br/>sigmoid"]
"""

MMD_TRANSFER = """
flowchart TB
  subgraph A["Original model"]
    direction TB
    A1["Trained convolutional base"] --> A2["Trained classifier"]
  end
  subgraph B["Feature extraction"]
    direction TB
    B1["Trained convolutional base<br/><b>FROZEN</b>"] --> B2["New classifier<br/>randomly initialised"]
  end
  subgraph C["Fine-tuning"]
    direction TB
    C1["Convolutional base<br/><b>top layers unfrozen</b>"] --> C2["Classifier<br/>already trained"]
  end
  A ~~~ B ~~~ C
"""

MMD_FINETUNE = """
flowchart LR
  S1["1. Add your classifier<br/>on top of a trained base"]
  S2["2. Freeze the base"]
  S3["3. Train the part<br/>you added"]
  S4["4. Unfreeze the base<br/><small>or just its top layers</small>"]
  S5["5. Train both jointly<br/><small>at a very low learning rate</small>"]
  S1 --> S2 --> S3 --> S4 --> S5
"""

MMD_TWOWAYS = """
flowchart TB
  Q{"Do you need<br/>data augmentation?"}
  F["<b>Fast</b> feature extraction<br/>run the base once,<br/>cache features to disk<br/><small>seconds per epoch</small>"]
  S["<b>End-to-end</b> extraction<br/>chain base + classifier,<br/>run every image every time<br/><small>far more expensive</small>"]
  Q -- "no" --> F
  Q -- "yes" --> S
"""

FIG_CONV = "figs/book/figure-8-4.png"


NB = ["01_convnet_on_mnist.ipynb", "02_small_dataset_from_scratch.ipynb",
      "03_data_augmentation.ipynb", "04_feature_extraction_and_finetuning.ipynb"]

DECK = {
    "id": "ch08",
    "kind": "chapter",
    "number": 8,
    "title": "Image Classification",
    "subtitle": "ConvNets from first principles, then the three strategies that make "
                "small image datasets tractable — from 80% to 98.6% on the same 2,000 "
                "pictures.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 8",
    "source_url": chapter_url(8),
    "duration": "3 hours (2 sessions)",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(8, local_notebooks=NB),
    "objectives": [
        "Explain why a convolution layer beats a dense layer on images: "
        "**translation invariance** and **spatial hierarchies**.",
        "Read a ConvNet summary and predict how **feature-map shape and depth** "
        "change layer by layer.",
        "Say what **max pooling** is for, and what breaks in a ConvNet without it.",
        "Build an image pipeline with **`image_dataset_from_directory`** and "
        "**`tf.data`**, including prefetching.",
        "Apply **data augmentation** and explain what it can and cannot fix.",
        "Use a pretrained model two ways — **fast feature extraction** and "
        "**end-to-end with augmentation** — and know the trade-off.",
        "**Fine-tune** a pretrained base in the right order, at the right learning "
        "rate, and know which layers to leave frozen.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Roadmap",
            "title": "One problem, three strategies, four numbers",
            "blocks": [
                {"t": "stats", "cols": 4, "items": [
                    {"v": "≈80%", "l": "small ConvNet from scratch, no regularisation"},
                    {"v": "≈84%", "l": "the same, with data augmentation"},
                    {"v": "98.1%", "l": "feature extraction from a pretrained model"},
                    {"v": "98.6%", "l": "fine-tuning that pretrained model"},
                ]},
                {"t": "p", "md": "All four use the **same 2,000 training images**. The lesson "
                                 "of the chapter is in the gap between the second number and "
                                 "the third — ==reusing learned features is worth more than "
                                 "any amount of tuning your own small model=="},
            ],
        },

        {"type": "section", "num": "01", "title": "Introduction to ConvNets",
         "lead": "Why a convolution beats a dense layer on images."},

        {
            "type": "slide",
            "kicker": "Section 8.1 · listing 8.1",
            "title": "A basic ConvNet is a stack of two layer types",
            "blocks": [
                {"t": "p", "md": "Before any theory, here is one that works. It classifies "
                                 "MNIST digits, the same task chapter 2 solved with a dense "
                                 "network."},
                {"t": "code", "lang": "python", "file": "listing 8.1 — a small ConvNet",
                 "src": """import keras
from keras import layers

inputs = keras.Input(shape=(28, 28, 1))
x = layers.Conv2D(filters=64, kernel_size=3, activation="relu")(inputs)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.GlobalAveragePooling2D()(x)
outputs = layers.Dense(10, activation="softmax")(x)
model = keras.Model(inputs=inputs, outputs=outputs)"""},
                {"t": "p", "md": "A ConvNet takes tensors of shape "
                                 "`(image_height, image_width, image_channels)`, not counting "
                                 "the batch dimension."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1 · listing 8.2",
            "title": "What the summary tells you",
            "blocks": [
                {"t": "p", "md": "Two patterns are visible in the shapes, and they hold for "
                                 "almost every ConvNet you will meet."},
                {"t": "out", "src": """Layer (type)                  Output Shape          Param #
input_layer (InputLayer)      (None, 28, 28, 1)            0
conv2d (Conv2D)               (None, 26, 26, 64)         640
max_pooling2d (MaxPooling2D)  (None, 13, 13, 64)           0
conv2d_1 (Conv2D)             (None, 11, 11, 128)     73,856
max_pooling2d_1 (MaxPooling2D)(None, 5, 5, 128)            0
conv2d_2 (Conv2D)             (None, 3, 3, 256)      295,168
global_average_pooling2d      (None, 256)                  0
dense (Dense)                 (None, 10)               2,570

Total params: 372,234 (1.42 MB)"""},
                {"t": "bullets", "items": [
                    "**Width and height shrink** as you go deeper: 28 → 26 → 13 → 11 → 5 → 3.",
                    "**Depth grows**: 1 → 64 → 128 → 256, controlled by the first argument to "
                    "`Conv2D`.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1 · listing 8.3–8.4",
            "title": "The result, against the dense network from chapter 2",
            "blocks": [
                {"t": "p", "md": "Same data, same loss, same number of epochs. Only the "
                                 "architecture changed."},
                {"t": "code", "lang": "python", "file": "listing 8.3 — training it",
                 "src": """train_images = train_images.reshape((60000, 28, 28, 1)).astype("float32") / 255
test_images = test_images.reshape((10000, 28, 28, 1)).astype("float32") / 255

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_images, train_labels, epochs=5, batch_size=64)

test_loss, test_acc = model.evaluate(test_images, test_labels)
print(f"Test accuracy: {test_acc:.3f}")"""},
                {"t": "out", "src": "Test accuracy: 0.991"},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "97.8% → 99.1%", "l": "dense network vs ConvNet"},
                    {"v": "≈ 60%", "l": "relative reduction in error rate"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "The fundamental difference: global versus local",
            "blocks": [
                {"t": "mmd", "id": "ch08-localglobal", "src": MMD_LOCALGLOBAL,
                 "cap": "The one architectural change that produced that 60% error reduction."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "Property 1 — translation invariance",
            "blocks": [
                {"t": "p", "md": "Having learned a pattern in the lower-right corner, a "
                                 "ConvNet can recognise it **anywhere** — upper-left included. "
                                 "A dense network would have to learn it again for the new "
                                 "position."},
                {"t": "band",
                 "md": "This makes ConvNets **data efficient** on images, because the visual "
                       "world is fundamentally translation invariant. They ==need fewer "
                       "training samples== to learn representations that generalise."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "Property 2 — spatial hierarchies",
            "blocks": [
                {"t": "mmd", "id": "ch08-hierarchy", "src": MMD_HIERARCHY,
                 "cap": "Elementary lines and textures combine into eyes and ears, which "
                        "combine into high-level concepts."},
                {"t": "p", "md": "This works because **the visual world is itself spatially "
                                 "hierarchical**. The architecture matches the structure of "
                                 "the data — which is exactly what chapter 5 called a good "
                                 "==architecture prior=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "Feature maps, filters, and response maps",
            "blocks": [
                {"t": "p", "md": "Convolutions operate over rank-3 tensors called **feature "
                                 "maps**: two spatial axes plus a depth axis. For an RGB image "
                                 "the depth is 3; for grayscale it is 1."},
                {"t": "bullets", "items": [
                    "The output's depth is **a parameter of the layer**, and its channels no "
                    "longer stand for colours — they stand for **filters**.",
                    "A filter encodes a specific aspect of the input; at a high level, one "
                    "filter might encode *\"presence of a face\"*.",
                    "In the MNIST example the first layer turns `(28, 28, 1)` into "
                    "`(26, 26, 64)` — it computes **64 filters** over its input.",
                    "Each of those 64 channels is a 26×26 grid: a **response map** saying "
                    "==how strongly that filter's pattern appears at each location==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "How the convolution actually runs",
            "blocks": [
                {"t": "img", "src": FIG_CONV, "credit": True, "max_h": "40vh",
                 "cap": "Figure 8.4 — a window slides over the input, each 3D patch is turned "
                        "into a vector by the same learned kernel, and the vectors are "
                        "reassembled into an output map."},
                {"t": "p", "md": "Three things to take from the picture. The window moves "
                                 "over **every** position. The **same** kernel is used at "
                                 "each one — that is weight sharing. And the outputs are "
                                 "reassembled in the positions they came from, which is why "
                                 "the result is still an image and not a list. ==The next "
                                 "slide computes one of those positions.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "One position of that window, computed",
            "blocks": [
                conv_compute(
                    "ch08-conv-compute",
                    image=[[3, 1, 0, 2, 4],
                           [1, 5, 2, 0, 1],
                           [0, 2, 7, 3, 2],
                           [4, 1, 3, 6, 0],
                           [2, 0, 1, 2, 5]],
                    kernel=[[1, 0, -1],
                            [2, 0, -2],
                            [1, 0, -1]],
                    at=(1, 1),
                    cap="A 3×3 kernel over one 3×3 patch. This kernel is a Sobel filter, "
                        "which responds to vertical edges."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "Reading the arithmetic: three things it settles",
            "blocks": [
                {"t": "steps", "items": [
                    "**A convolution is multiply-and-add, and nothing else.** Nine "
                    "products and a sum give one output cell. Slide the window to the "
                    "next position and do it again — that is the whole operation.",
                    "**The kernel is what gets learned.** Its nine numbers are "
                    "`1, 0, -1 / 2, 0, -2 / 1, 0, -1` here because a person chose a Sobel "
                    "filter. In a ConvNet ==those nine numbers are parameters==, found by "
                    "gradient descent, and nobody chooses what they end up detecting.",
                    "**The same nine numbers are reused at every position.** That is "
                    "weight sharing: it is why a ConvNet has so few parameters compared "
                    "with a `Dense` layer over the same image, and why a pattern learned "
                    "in one corner is recognised in the other.",
                ]},
                {"t": "band", "md": "Why this kernel finds vertical edges: the left column "
                                    "is positive and the right column is negative, so the "
                                    "sum is large wherever **the left side is brighter than "
                                    "the right**, and near zero on flat ground. Run it on a "
                                    "patch where every cell is equal and the answer is "
                                    "exactly 0."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.1",
            "title": "The two parameters that define a convolution",
            "blocks": [
                {"t": "table",
                 "head": ["Parameter", "Typical value", "What it controls"],
                 "widths": [30, 22, 48],
                 "rows": [
                     ["**Patch size**", "3 × 3 or 5 × 5",
                      "How large a neighbourhood each output value can see."],
                     ["**Output depth**", "32 to 512",
                      "How many filters are computed — how many different patterns the layer "
                      "can look for."],
                 ]},
                {"t": "code", "lang": "python", "file": "how Keras spells it",
                 "src": """layers.Conv2D(output_depth, (window_height, window_width))

# the same kernel is reused for every patch, which is why the layer is
# translation invariant and why it has so few parameters"""},
                {"t": "p", "md": "Because the kernel is shared across all positions, "
                                 "==parameter count depends on the window and depth, not on "
                                 "the image size=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.2",
            "title": "Max pooling: downsample, aggressively",
            "blocks": [
                {"t": "p", "md": "After each `MaxPooling2D` the feature map halves: 26×26 "
                                 "becomes 13×13. It extracts windows and outputs the maximum "
                                 "value of each channel."},
                {"t": "table",
                 "head": ["", "Convolution", "Max pooling"],
                 "widths": [26, 37, 37],
                 "rows": [
                     ["Transformation", "A **learned** linear transform (the kernel).",
                      "A **hardcoded** max operation."],
                     ["Typical window", "3 × 3, stride 1", "2 × 2, stride 2"],
                     ["Effect on size", "Shrinks slightly (no padding).",
                      "**Halves** each spatial dimension."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.1.2 · listing 8.5",
            "title": "What happens without it",
            "blocks": [
                {"t": "p", "md": "The book builds the broken version deliberately: the same "
                                 "network with every pooling layer removed."},
                {"t": "code", "lang": "python", "file": "listing 8.5 — an incorrectly structured ConvNet",
                 "src": """inputs = keras.Input(shape=(28, 28, 1))
x = layers.Conv2D(filters=64, kernel_size=3, activation="relu")(inputs)
x = layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.GlobalAveragePooling2D()(x)
outputs = layers.Dense(10, activation="softmax")(x)
model_no_max_pool = keras.Model(inputs=inputs, outputs=outputs)"""},
                {"t": "band", "style": "rose",
                 "md": "**It is not conducive to learning a spatial hierarchy.** The 3×3 "
                       "windows in the third layer still only see information from ==7×7 "
                       "windows of the original image== — far too small a view to assemble a "
                       "whole digit."},
            ],
        },

        {"type": "section", "num": "02", "title": "Training from scratch on a small dataset",
         "lead": "2,000 pictures of cats and dogs. A situation you will actually meet."},

        {
            "type": "slide",
            "kicker": "Section 8.2",
            "title": "The setup, and why it is realistic",
            "blocks": [
                {"t": "p", "md": "Having to train an image classifier on very little data is "
                                 "**a common situation** in professional computer vision. A "
                                 "\"few\" samples can mean a few hundred to a few tens of "
                                 "thousands."},
                {"t": "stats", "cols": 3, "items": [
                    {"v": "2,000", "l": "training images"},
                    {"v": "1,000", "l": "validation images"},
                    {"v": "2,000", "l": "test images"},
                ]},
                {"t": "p", "md": "Drawn from the original Kaggle Dogs vs. Cats dataset, which "
                                 "was released as a competition in late 2013 — ==before "
                                 "ConvNets were mainstream=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.1",
            "title": "Why deep learning still applies with little data",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "ConvNets are data efficient",
                     "p": "Because they learn **local, translation-invariant** features, they "
                          "give reasonable results on small image datasets without any custom "
                          "feature engineering.", "style": "good"},
                    {"ico": "♻", "h": "Models are repurposable",
                     "p": "A classifier trained on a large dataset can be reused on a "
                          "significantly different problem with minor changes. **Feature "
                          "reuse is one of deep learning's greatest strengths.**",
                     "style": "good"},
                ]},
                {"t": "p", "md": "What counts as *enough* is relative — to the size and depth "
                                 "of the model. A few tens of samples will not do; a few "
                                 "hundred can suffice if the model is small, well regularised, "
                                 "and the task is simple."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.3 · listing 8.7",
            "title": "A bigger ConvNet for bigger images",
            "blocks": [
                {"t": "p", "md": "Same alternating pattern as before, with two extra stages — "
                                 "the images are larger and the problem harder. Note the "
                                 "`Rescaling` layer, which moves the preprocessing **inside "
                                 "the model**."},
                {"t": "code", "lang": "python", "file": "listing 8.7 — dogs vs cats, from scratch",
                 "src": """inputs = keras.Input(shape=(180, 180, 3))
x = layers.Rescaling(1.0 / 255)(inputs)          # 0..255 -> 0..1, inside the model
x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=64, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=512, kernel_size=3, activation="relu")(x)
x = layers.GlobalAveragePooling2D()(x)
outputs = layers.Dense(1, activation="sigmoid")(x)     # binary -> one sigmoid unit
model = keras.Model(inputs=inputs, outputs=outputs)"""},
                {"t": "p", "md": "Putting `Rescaling` in the model means the deployed artefact "
                                 "carries its own preprocessing — one fewer thing to get "
                                 "wrong in production."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.3",
            "title": "The pattern you will see in almost every ConvNet",
            "blocks": [
                {"t": "mmd", "id": "ch08-shapes", "src": MMD_SHAPES,
                 "cap": "Depth rises from 32 to 512 while the spatial size falls from 180×180 "
                        "to 7×7."},
                {"t": "band",
                 "md": "**Feature-map depth increases while feature-map size decreases.** "
                       "Information moves out of *where* and into *what* — ==and that is "
                       "the whole shape of a classification ConvNet=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.4",
            "title": "From JPEG files to batched tensors",
            "blocks": [
                {"t": "p", "md": "The data sits on disk as JPEGs. Five steps are needed to "
                                 "make it model-ready, and Keras does all of them in one call."},
                {"t": "steps", "items": [
                    "Read the picture files.",
                    "Decode the JPEG content into RGB grids of pixels.",
                    "Convert those into floating-point tensors.",
                    "Resize them to a shared size — here 180 × 180.",
                    "Pack them into batches.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.4 · listing 8.9",
            "title": "`image_dataset_from_directory` does all five",
            "blocks": [
                {"t": "p", "md": "It lists the subdirectories, treats each as a class, indexes "
                                 "the files, and returns a `tf.data.Dataset` that shuffles, "
                                 "decodes, resizes, and batches."},
                {"t": "code", "lang": "python", "file": "listing 8.9 — building the pipeline",
                 "src": """from keras.utils import image_dataset_from_directory

batch_size = 64
image_size = (180, 180)

train_dataset = image_dataset_from_directory(
    new_base_dir / "train", image_size=image_size, batch_size=batch_size)
validation_dataset = image_dataset_from_directory(
    new_base_dir / "validation", image_size=image_size, batch_size=batch_size)
test_dataset = image_dataset_from_directory(
    new_base_dir / "test", image_size=image_size, batch_size=batch_size)"""},
                {"t": "p", "md": "The directory layout **is** the label set: one subfolder per "
                                 "class, and the folder names become the classes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.4",
            "title": "What a `tf.data.Dataset` buys you",
            "blocks": [
                {"t": "bullets", "items": [
                    "It works with **any backend** — JAX and PyTorch included — not only "
                    "TensorFlow.",
                    "It is an **iterator**: usable in a `for` loop, and passable straight to "
                    "`fit()`.",
                    "It **parallelises preprocessing across CPU cores**.",
                    "It does **asynchronous prefetching**: preparing the next batch while the "
                    "model is still working on the previous one, so ==execution never "
                    "stalls==.",
                ]},
                {"t": "band",
                 "md": "Those last two are the difference between a GPU that is busy and a GPU "
                       "that spends most of its time waiting for JPEGs to decode."},
            ],
        },

        {"type": "section", "num": "03", "title": "Data augmentation",
         "lead": "Making more training data out of the training data you have."},

        {
            "type": "slide",
            "kicker": "Section 8.2.5",
            "title": "The idea, and where the layers go",
            "blocks": [
                {"t": "p", "md": "Overfitting comes from having too few samples. Augmentation "
                                 "generates more of them by applying **random but believable** "
                                 "transformations, so the model ==never sees exactly the same "
                                 "picture twice=="},
                {"t": "table",
                 "head": ["Where you put the layers", "Runs on", "Trade-off"],
                 "widths": [30, 20, 50],
                 "rows": [
                     ["**Inside the model**, before `Rescaling`", "GPU",
                      "Sometimes faster, but the augmentation ships with the model."],
                     ["**In the data pipeline**, via `map()`", "CPU, in parallel",
                      "**Usually the better option** — and the one the book takes."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.5 · listing 8.18",
            "title": "Three transformations, and prefetching",
            "blocks": [
                {"t": "p", "md": "The layers are defined as a list, wrapped in a function, and "
                                 "mapped over the dataset."},
                {"t": "code", "lang": "python", "file": "listing 8.18 — the augmentation stage",
                 "src": """data_augmentation_layers = [
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.2),
]

def data_augmentation(images, targets):
    for layer in data_augmentation_layers:
        images = layer(images)
    return images, targets

augmented_train_dataset = train_dataset.map(data_augmentation, num_parallel_calls=8)
augmented_train_dataset = augmented_train_dataset.prefetch(tf.data.AUTOTUNE)"""},
                {"t": "bullets", "items": [
                    "`RandomFlip(\"horizontal\")` — flips a random **50%** of images.",
                    "`RandomRotation(0.1)` — rotates by a random value in **[−10%, +10%]** of "
                    "a full circle, i.e. **±36 degrees**.",
                    "`RandomZoom(0.2)` — zooms in or out by a random factor in **[−20%, +20%]**.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.2.5",
            "title": "What augmentation cannot do",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "The model will never see the same input twice — but the inputs it does "
                       "see are **still heavily intercorrelated**, because they come from a "
                       "small number of originals. ==You cannot produce new information; you "
                       "can only remix existing information.=="},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "≈ 80%", "l": "from scratch, no augmentation"},
                    {"v": "≈ 84%", "l": "from scratch, with augmentation"},
                ]},
                {"t": "p", "md": "Four points for a change that costs nothing but CPU time — "
                                 "worth having, and clearly not enough on its own."},
            ],
        },

        {"type": "section", "num": "04", "title": "Using a pretrained model",
         "lead": "Where the remaining fourteen points come from."},

        {
            "type": "slide",
            "kicker": "Section 8.3",
            "title": "Why features transfer between problems",
            "blocks": [
                {"t": "p", "md": "A model trained on a large, general dataset learns a spatial "
                                 "hierarchy of features that acts as **a generic model of the "
                                 "visual world** — useful even for classes it never saw."},
                {"t": "p", "md": "The book uses **Xception** trained on ImageNet: 1.4 million "
                                 "labelled images across 1,000 classes. ImageNet contains many "
                                 "cat and dog breeds, so it should transfer well here."},
                {"t": "band",
                 "md": "Such portability across problems is **a key advantage of deep learning "
                       "over older shallow methods**, and it is what makes it effective on "
                       "small-data problems at all."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3",
            "title": "Two ways to reuse it",
            "blocks": [
                {"t": "mmd", "id": "ch08-transfer", "src": MMD_TRANSFER,
                 "cap": "Feature extraction swaps the classifier; fine-tuning then also "
                        "adjusts the top of the base."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1",
            "title": "Why only the convolutional base is reused",
            "blocks": [
                {"t": "p", "md": "A ConvNet has two parts: a **convolutional base** (the "
                                 "pooling and convolution layers, also called the *backbone*) "
                                 "and a densely connected classifier. Only the first is worth "
                                 "keeping."},
                {"t": "bullets", "items": [
                    "The base produces **presence maps of generic concepts** — useful "
                    "regardless of the vision problem.",
                    "The classifier's representations are **specific to the classes it was "
                    "trained on**.",
                    "Worse, dense layers **discard spatial information**: they no longer know "
                    "*where* anything is. For problems where location matters they are "
                    "==largely useless==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1",
            "title": "How much of the base to reuse",
            "blocks": [
                {"t": "p", "md": "Generality depends on depth. **Earlier layers extract local, "
                                 "highly generic feature maps** — edges, colours, textures. "
                                 "**Higher layers extract abstract concepts** such as *cat ear* "
                                 "or *dog eye*."},
                {"t": "band", "style": "amber",
                 "md": "So if your new dataset differs a lot from the original, you may be "
                       "better off using ==only the first few layers== for feature extraction "
                       "rather than the entire base."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1 · listing 8.23–8.24",
            "title": "Loading a pretrained backbone",
            "blocks": [
                {"t": "p", "md": "KerasHub ships Keras implementations of popular architectures "
                                 "with downloadable weights. Note that the preprocessing comes "
                                 "**paired with the checkpoint**."},
                {"t": "code", "lang": "python", "file": "listing 8.23–8.24 — backbone and preprocessing",
                 "src": """import keras_hub

conv_base = keras_hub.models.Backbone.from_preset("xception_41_imagenet")

preprocessor = keras_hub.layers.ImageConverter.from_preset(
    "xception_41_imagenet",
    image_size=(180, 180),
)"""},
                {"t": "bullets", "items": [
                    "**backbone** is KerasHub's word for the feature extractor without its "
                    "classification head.",
                    "The **41** is a naming convention: 41 trainable layers. Pretrained "
                    "ConvNets are conventionally named by depth.",
                    "`ImageConverter` matters more than it looks: every pretrained ConvNet "
                    "expects a particular input range, and feeding the wrong one forces the "
                    "model to ==relearn how to see==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1",
            "title": "Fast, or augmentable — pick one",
            "blocks": [
                {"t": "mmd", "id": "ch08-twoways", "src": MMD_TWOWAYS,
                 "cap": "The base is by far the most expensive part of the pipeline, so "
                        "running it once versus every epoch is the whole trade-off."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1 · listing 8.25",
            "title": "Fast route — cache the features once",
            "blocks": [
                {"t": "p", "md": "Run the frozen base over each dataset a single time and keep "
                                 "the outputs as NumPy arrays."},
                {"t": "code", "lang": "python", "file": "listing 8.25 — extracting features",
                 "src": """def get_features_and_labels(dataset):
    all_features, all_labels = [], []
    for images, labels in dataset:
        preprocessed_images = preprocessor(images)
        features = conv_base.predict(preprocessed_images, verbose=0)
        all_features.append(features)
        all_labels.append(labels)
    return np.concatenate(all_features), np.concatenate(all_labels)

train_features, train_labels = get_features_and_labels(train_dataset)
val_features, val_labels = get_features_and_labels(validation_dataset)
test_features, test_labels = get_features_and_labels(test_dataset)

print(train_features.shape)"""},
                {"t": "out", "src": "(2000, 6, 6, 2048)"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1 · listing 8.26",
            "title": "…then train a tiny classifier on the cache",
            "blocks": [
                {"t": "p", "md": "The classifier now sees 6×6×2048 feature maps rather than "
                                 "images, so it is small and trains in seconds."},
                {"t": "code", "lang": "python", "file": "listing 8.26 — the dense classifier",
                 "src": """inputs = keras.Input(shape=(6, 6, 2048))
x = layers.GlobalAveragePooling2D()(inputs)
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.25)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

history = model.fit(train_features, train_labels, epochs=10,
                    validation_data=(val_features, val_labels),
                    callbacks=callbacks)"""},
                {"t": "out", "src": """validation accuracy: slightly over 98%
test accuracy      : 0.981
(an epoch takes under 1 second, even on CPU)"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1",
            "title": "Read that result carefully",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "It is **a slightly unfair comparison**: ImageNet contains many dog and "
                       "cat instances, so the pretrained model already holds ==the exact "
                       "knowledge this task needs==. That will not always be true."},
                {"t": "p", "md": "The curves also show **overfitting almost from the start**, "
                                 "despite a fairly large dropout rate — because this route "
                                 "cannot use augmentation, which is essential on small image "
                                 "datasets."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1 · listing 8.28–8.29",
            "title": "Slow route — freeze the base and chain it",
            "blocks": [
                {"t": "p", "md": "Freezing means preventing weights from updating. Without it, "
                                 "the randomly initialised classifier would send huge updates "
                                 "backwards and ==destroy the representations the base already "
                                 "learned=="},
                {"t": "code", "lang": "python", "file": "listing 8.28–8.29 — freezing",
                 "src": """conv_base = keras_hub.models.Backbone.from_preset(
    "xception_41_imagenet",
    trainable=False,
)

conv_base.trainable = True
print(len(conv_base.trainable_weights))     # before freezing
conv_base.trainable = False
print(len(conv_base.trainable_weights))     # after freezing"""},
                {"t": "out", "src": """26
0"""},
                {"t": "p", "md": "Setting `trainable = False` **empties the list of trainable "
                                 "weights** — which is exactly how you verify that a freeze "
                                 "took effect."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.1",
            "title": "The chained model, and a recompile trap",
            "blocks": [
                {"t": "p", "md": "Now the preprocessing, the frozen base, and a new classifier "
                                 "are one model — so augmentation applies to every image on "
                                 "every epoch."},
                {"t": "code", "lang": "python", "file": "the end-to-end model",
                 "src": """inputs = keras.Input(shape=(180, 180, 3))
x = preprocessor(inputs)
x = conv_base(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(256)(x)
x = layers.Dropout(0.25)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])"""},
                {"t": "band", "style": "rose",
                 "md": "Only the two `Dense` layers train — four weight tensors in total. And "
                       "a trap worth memorising: **if you change trainability after compiling, "
                       "you must recompile**, or ==the change is silently ignored=="},
            ],
        },

        {"type": "section", "num": "05", "title": "Fine-tuning",
         "lead": "Unfreezing the top of the base — carefully, and last."},

        {
            "type": "slide",
            "kicker": "Section 8.3.2",
            "title": "The five steps, and why the order is fixed",
            "blocks": [
                {"t": "mmd", "id": "ch08-finetune", "src": MMD_FINETUNE,
                 "cap": "Steps 1–3 are exactly the feature-extraction workflow. Fine-tuning "
                        "is what you do afterwards."},
                {"t": "band", "style": "rose",
                 "md": "The base can only be fine-tuned **once the classifier on top is "
                       "already trained**. Otherwise the error signal propagating back is too "
                       "large, and ==the representations being fine-tuned are destroyed=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.2",
            "title": "Partial fine-tuning, and why the top layers",
            "blocks": [
                {"t": "p", "md": "With large pretrained models it is common to unfreeze only "
                                 "the top few layers of the base."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "bullets", "items": [
                            "Earlier layers encode **generic, reusable** features; higher ones "
                            "encode **specialised** features.",
                            "It is the specialised ones that need repurposing, so there are "
                            "==fast-decreasing returns== to fine-tuning lower layers.",
                            "The base has **15 million parameters** — training all of them on "
                            "2,000 images risks overfitting.",
                        ]},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "unfreezing the top four",
                         "src": """conv_base.trainable = True
for layer in conv_base.layers[:-4]:
    layer.trainable = False"""},
                    ],
                ]},
                {"t": "band", "style": "amber",
                 "md": "One layer type to leave alone: **do not unfreeze `BatchNormalization` "
                       "layers**. Chapter 9 explains why."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.2 · listing 8.31",
            "title": "Fine-tune at a very low learning rate",
            "blocks": [
                {"t": "p", "md": "The learning rate is deliberately tiny — the goal is to "
                                 "**limit the magnitude of the changes** made to representations "
                                 "that are already good."},
                {"t": "code", "lang": "python", "file": "listing 8.31 — fine-tuning",
                 "src": """model.compile(
    loss="binary_crossentropy",
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),    # note: 1e-5
    metrics=["accuracy"],
)

callbacks = [keras.callbacks.ModelCheckpoint(
    filepath="fine_tuning.keras", save_best_only=True, monitor="val_loss")]

history = model.fit(augmented_train_dataset, epochs=30,
                    validation_data=validation_dataset, callbacks=callbacks)"""},
                {"t": "band",
                 "md": "Updates that are too large ==harm the representations you are trying "
                       "to keep==. This is one of the few places in the book where the "
                       "learning rate is prescribed rather than searched for."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 8.3.2",
            "title": "The final number, in context",
            "blocks": [
                {"t": "p", "md": "The checkpoint callback kept the best version, so the "
                                 "model that gets evaluated is the best one seen during the "
                                 "run rather than the last one."},
                {"t": "code", "lang": "python", "file": "evaluating the fine-tuned model",
                 "src": """model = keras.models.load_model("fine_tuning.keras")
test_loss, test_acc = model.evaluate(test_dataset)
print(f"Test accuracy: {test_acc:.3f}")"""},
                {"t": "out", "src": "Test accuracy: 0.986"},
                {"t": "p", "md": "In the original Kaggle competition this **would have been "
                                 "among the top results** — though not a fair comparison, "
                                 "since the pretrained features already carried prior knowledge "
                                 "about cats and dogs that competitors could not use."},
                {"t": "band",
                 "md": "The fairer point: this was reached using **about 10% of the training "
                       "data** available in that competition. ==There is a huge difference "
                       "between training on 20,000 samples and on 2,000.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Convolutions learn local patterns**, which buys translation invariance "
                    "and spatial hierarchies — and makes ConvNets data efficient on images.",
                    "**Depth rises as spatial size falls.** That shape is nearly universal in "
                    "classification ConvNets.",
                    "**Max pooling is not optional**: without it, deep layers still only see a "
                    "tiny window of the original image.",
                    "**`image_dataset_from_directory` + `tf.data`** turns a folder of JPEGs "
                    "into a parallel, prefetching pipeline.",
                    "**Augmentation remixes information; it cannot create it.** Worth about "
                    "four points here.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "…and the part that changes how you plan a project",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "♻", "h": "Reuse beats tuning",
                     "p": "Feature extraction from a pretrained base took the same 2,000 "
                          "images from **84% to 98.1%** — more than anything you could do to "
                          "a small model of your own.", "style": "good"},
                    {"ico": "🎚", "h": "Fine-tune last, and gently",
                     "p": "Only after the new classifier is trained, at a **very low learning "
                          "rate**, and with `BatchNormalization` left frozen.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Which is why the first question on a new vision problem is not "
                       "*what architecture?* but ==*whose features can I start from?*=="},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "04_feature_extraction_and_finetuning.ipynb",
                     "href": "../../course-slides/notebooks/ch08/04_feature_extraction_and_finetuning.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 9 — ConvNet architecture patterns",
                     "href": "../ch09/index.html"},
                ]},
            ],
        },
    ],
}
