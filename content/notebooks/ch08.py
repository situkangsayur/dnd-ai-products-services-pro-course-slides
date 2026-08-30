# -*- coding: utf-8 -*-
"""Chapter 8 notebooks — Image Classification."""

DECK = "ch08"

NOTEBOOKS = [
    {
        "file": "01_convnet_on_mnist.ipynb",
        "title": "A ConvNet on MNIST, and why it beats the dense model",
        "lede": "The same problem as chapter 2, with a fraction of the parameters and "
                "a better score. The reason is two properties of the convolution "
                "operation, and both are visible in the numbers.",
        "needs": "CPU — about 3 minutes (GPU: 30 seconds)",
        "section": "01 — Introduction to convnets",
        "cells": [
            ("h2", "The model"),
            ("py", """import keras
from keras import layers

inputs = keras.Input(shape=(28, 28, 1))
x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(inputs)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=64, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
x = layers.Flatten()(x)
outputs = layers.Dense(10, activation="softmax")(x)
model = keras.Model(inputs=inputs, outputs=outputs)
model.summary()"""),
            ("out", """Total params: 104,202"""),

            ("h2", "Training it"),
            ("py", """from keras.datasets import mnist

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images.reshape((60000, 28, 28, 1)).astype("float32") / 255
test_images = test_images.reshape((10000, 28, 28, 1)).astype("float32") / 255

model.compile(optimizer="rmsprop",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_images, train_labels, epochs=5, batch_size=64, verbose=2)
_, test_acc = model.evaluate(test_images, test_labels, verbose=0)
print(f"test accuracy: {test_acc:.4f}")"""),
            ("out", "test accuracy: 0.99xx"),

            ("h2", "Against the dense model from chapter 2"),
            ("py", """dense = keras.Sequential([layers.Flatten(),
                          layers.Dense(512, activation="relu"),
                          layers.Dense(10, activation="softmax")])
dense.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
dense.fit(train_images, train_labels, epochs=5, batch_size=64, verbose=0)
_, dense_acc = dense.evaluate(test_images, test_labels, verbose=0)

print(f"{'model':10s} {'params':>10s} {'test acc':>10s}   error rate")
print(f"{'dense':10s} {dense.count_params():>10,} {dense_acc:>10.4f}   "
      f"{1-dense_acc:.4f}")
print(f"{'convnet':10s} {model.count_params():>10,} {test_acc:>10.4f}   "
      f"{1-test_acc:.4f}")
print(f"\\nerror reduced by {(1-dense_acc)/(1-test_acc):.1f}x, "
      f"with {dense.count_params()/model.count_params():.1f}x fewer parameters")"""),
            ("md",
             "**Fewer parameters and a lower error.** Two properties of "
             "convolution do this:\n\n"
             "- **Translation invariance** — a pattern learned in one corner is "
             "recognised everywhere, so the model does not relearn it 784 times.\n"
             "- **Spatial hierarchies** — small local patterns compose into "
             "larger ones, layer by layer.\n\n"
             "A Dense layer has neither, which is why it needs five times as "
             "many parameters to do worse."),

            ("h2", "Watching the spatial dimensions shrink"),
            ("py", """for layer in model.layers:
    print(f"{layer.__class__.__name__:16s} {str(layer.output.shape):24s} "
          f"{layer.count_params():>8,} params")"""),
            ("md",
             "Height and width fall — 28, 26, 13, 11, 5, 3 — while depth rises: "
             "1, 32, 64, 128. **Trading space for semantics**, which is the "
             "shape of every ConvNet in this course."),

            ("h2", "Why max pooling and not something gentler"),
            ("py", """def build(pooling):
    keras.utils.set_random_seed(0)
    i = keras.Input(shape=(28, 28, 1))
    x = layers.Conv2D(32, 3, activation="relu")(i)
    if pooling == "max":
        x = layers.MaxPooling2D(2)(x)
    elif pooling == "avg":
        x = layers.AveragePooling2D(2)(x)
    elif pooling == "stride":
        x = layers.Conv2D(32, 3, strides=2, activation="relu", padding="same")(x)
    x = layers.Conv2D(64, 3, activation="relu")(x)
    x = layers.Flatten()(x)
    o = layers.Dense(10, activation="softmax")(x)
    m = keras.Model(i, o)
    m.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    m.fit(train_images[:20000], train_labels[:20000], epochs=3,
          batch_size=64, verbose=0)
    return m.evaluate(test_images, test_labels, verbose=0)[1]

for p in ["max", "avg", "stride"]:
    print(f"{p:8s} pooling -> test accuracy {build(p):.4f}")"""),
            ("md",
             "Max pooling usually wins here. The argument is that features "
             "encode the **presence** of a pattern, and averaging dilutes "
             "presence while max preserves it. Note that chapters 11 and 17 "
             "prefer strides — because segmentation and generation care *where* "
             "things are, and max pooling discards exactly that."),

            ("h2", "What the first layer learned"),
            ("py", """import numpy as np
import matplotlib.pyplot as plt

filters = model.layers[1].get_weights()[0]      # (3, 3, 1, 32)
f = filters[:, :, 0, :]
f = (f - f.min()) / (f.max() - f.min())

fig, axes = plt.subplots(4, 8, figsize=(9, 4.6))
for ax, i in zip(axes.ravel(), range(32)):
    ax.imshow(f[:, :, i], cmap="gray"); ax.axis("off")
plt.suptitle("The 32 first-layer 3x3 filters", y=1.02)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Edge and blob detectors, learned rather than designed. Chapter 10 "
             "does this properly, at every depth, and the story it tells is the "
             "same one this glimpse suggests."),
        ],
        "takeaways": [
            "A ConvNet beats a dense model on images with **five times fewer "
            "parameters**.",
            "Translation invariance and spatial hierarchies are the two reasons.",
            "Height and width shrink while depth grows — space traded for "
            "semantics.",
            "Max pooling preserves presence; use strides when position matters "
            "(chapters 11 and 17).",
        ],
    },

    {
        "file": "02_small_dataset_from_scratch.ipynb",
        "title": "2,000 images, from scratch",
        "lede": "The realistic case: a few thousand images, a model that overfits within "
                "five epochs, and a baseline to improve on in the next two notebooks.",
        "needs": "GPU recommended — about 10 minutes on CPU · needs the Kaggle cats-vs-dogs archive",
        "section": "02 — Training a convnet from scratch on a small dataset",
        "cells": [
            ("h2", "Getting the data"),
            ("py", """import os, shutil, pathlib
import keras

# Cats vs dogs. Requires a Kaggle account; see the book for the download step.
# If you already have the archive, point original_dir at the extracted folder.
original_dir = pathlib.Path("train")
new_base_dir = pathlib.Path("cats_vs_dogs_small")

def make_subset(subset_name, start_index, end_index):
    for category in ("cat", "dog"):
        dir = new_base_dir / subset_name / category
        os.makedirs(dir, exist_ok=True)
        fnames = [f"{category}.{i}.jpg" for i in range(start_index, end_index)]
        for fname in fnames:
            shutil.copyfile(src=original_dir / fname, dst=dir / fname)

if original_dir.exists() and not new_base_dir.exists():
    make_subset("train", 0, 1000)
    make_subset("validation", 1000, 1500)
    make_subset("test", 1500, 2500)
    print("subsets created")
else:
    print("point original_dir at your extracted Kaggle download")"""),
            ("note",
             "**2,000 training images, 1,000 validation, 2,000 test.** "
             "Deliberately small. Everything interesting in this chapter follows "
             "from that number."),

            ("h2", "image_dataset_from_directory"),
            ("py", """from keras.utils import image_dataset_from_directory

train_dataset = image_dataset_from_directory(
    new_base_dir / "train", image_size=(180, 180), batch_size=32)
validation_dataset = image_dataset_from_directory(
    new_base_dir / "validation", image_size=(180, 180), batch_size=32)
test_dataset = image_dataset_from_directory(
    new_base_dir / "test", image_size=(180, 180), batch_size=32)

for data_batch, labels_batch in train_dataset:
    print("data batch shape:", data_batch.shape)
    print("labels batch shape:", labels_batch.shape)
    break"""),
            ("out", """data batch shape: (32, 180, 180, 3)
labels batch shape: (32,)"""),
            ("py", """import matplotlib.pyplot as plt

for images, labels in train_dataset.take(1):
    fig, axes = plt.subplots(2, 6, figsize=(13, 4.4))
    for ax, img, lab in zip(axes.ravel(), images, labels):
        ax.imshow(img.numpy().astype("uint8"))
        ax.set_title("dog" if lab == 1 else "cat", fontsize=9)
        ax.axis("off")
    plt.tight_layout(); plt.show()"""),

            ("h2", "The model"),
            ("py", """from keras import layers

inputs = keras.Input(shape=(180, 180, 3))
x = layers.Rescaling(1./255)(inputs)
x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=64, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.Flatten()(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs=inputs, outputs=outputs)

model.compile(loss="binary_crossentropy", optimizer="rmsprop",
              metrics=["accuracy"])
model.summary()"""),
            ("md",
             "`Rescaling` is **inside the model**, not in the data pipeline. "
             "Chapter 6's point about preprocessing travelling with the model, "
             "applied by default."),

            ("h2", "Training, with a checkpoint"),
            ("py", """callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath="convnet_from_scratch.keras",
        save_best_only=True,
        monitor="val_loss")
]
history = model.fit(train_dataset, epochs=30,
                    validation_data=validation_dataset,
                    callbacks=callbacks, verbose=2)"""),

            ("h2", "The curves, and the diagnosis"),
            ("py", """import numpy as np

h = history.history
epochs = range(1, len(h["accuracy"]) + 1)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
a1.plot(epochs, h["accuracy"], "o-", ms=3, label="training")
a1.plot(epochs, h["val_accuracy"], "s-", ms=3, label="validation")
a1.set_title("Accuracy"); a1.legend(); a1.set_xlabel("epoch")
a2.plot(epochs, h["loss"], "o-", ms=3, label="training")
a2.plot(epochs, h["val_loss"], "s-", ms=3, label="validation")
a2.set_title("Loss"); a2.legend(); a2.set_xlabel("epoch")
plt.tight_layout(); plt.show()

turn = int(np.argmin(h["val_loss"])) + 1
print(f"validation loss bottoms out at epoch {turn} of {len(epochs)}")"""),
            ("md",
             "Training accuracy runs to nearly 100%. Validation stalls around "
             "70% and validation loss turns up within about five epochs. "
             "**Textbook overfitting**, and entirely expected with 2,000 "
             "samples."),

            ("h2", "The baseline"),
            ("py", """test_model = keras.models.load_model("convnet_from_scratch.keras")
_, test_acc = test_model.evaluate(test_dataset, verbose=0)
print(f"test accuracy: {test_acc:.3f}")"""),
            ("out", "test accuracy: ~0.70"),
            ("md",
             "Around 70%. Hold onto that number: notebook 03 adds augmentation "
             "and reaches the low 80s; notebook 04 uses a pretrained backbone "
             "and reaches the high 90s. **Same data, same budget.**"),
        ],
        "takeaways": [
            "`image_dataset_from_directory` turns a folder tree into a batched "
            "dataset in one call.",
            "Put `Rescaling` inside the model so preprocessing travels with it.",
            "2,000 images overfit a from-scratch ConvNet within five epochs.",
            "**70% is the baseline** the next two notebooks improve on.",
        ],
    },

    {
        "file": "03_data_augmentation.ipynb",
        "title": "Data augmentation, and what it can and cannot fix",
        "lede": "Random flips, rotations, and zooms buy ten points here. Understanding "
                "why it is not twenty is the more useful half.",
        "needs": "GPU recommended — about 15 minutes on CPU · needs the Kaggle cats-vs-dogs archive",
        "section": "03 — Using data augmentation",
        "cells": [
            ("h2", "Augmentation as layers"),
            ("py", """import keras
from keras import layers

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.2),
])"""),
            ("note",
             "These are **layers**, active during training and inert at "
             "inference — exactly like `Dropout`. Putting them in the model "
             "rather than the data pipeline means they follow the model "
             "everywhere it goes."),

            ("h2", "Seeing what it does"),
            ("py", """import matplotlib.pyplot as plt
from keras.utils import image_dataset_from_directory
import pathlib

new_base_dir = pathlib.Path("cats_vs_dogs_small")
train_dataset = image_dataset_from_directory(
    new_base_dir / "train", image_size=(180, 180), batch_size=32)

for images, _ in train_dataset.take(1):
    fig, axes = plt.subplots(3, 6, figsize=(13, 6.6))
    for row in range(3):
        aug = data_augmentation(images)
        for col in range(6):
            axes[row, col].imshow(aug[col].numpy().astype("uint8"))
            axes[row, col].axis("off")
    plt.suptitle("The same six images, three times through augmentation", y=1.0)
    plt.tight_layout(); plt.show()"""),
            ("md",
             "The same photographs, differently. **No new information** — that "
             "is the point and also the limit. Augmentation resamples the "
             "manifold you already have; it cannot show the model a breed it has "
             "never seen."),

            ("h2", "The model, with augmentation and dropout"),
            ("py", """inputs = keras.Input(shape=(180, 180, 3))
x = data_augmentation(inputs)
x = layers.Rescaling(1./255)(x)
x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=64, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.Flatten()(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs=inputs, outputs=outputs)

model.compile(loss="binary_crossentropy", optimizer="rmsprop",
              metrics=["accuracy"])

validation_dataset = image_dataset_from_directory(
    new_base_dir / "validation", image_size=(180, 180), batch_size=32)

callbacks = [keras.callbacks.ModelCheckpoint(
    filepath="convnet_with_augmentation.keras",
    save_best_only=True, monitor="val_loss")]
history = model.fit(train_dataset, epochs=100,
                    validation_data=validation_dataset,
                    callbacks=callbacks, verbose=2)"""),
            ("warn",
             "One hundred epochs, not thirty.** Augmentation slows overfitting "
             "down, so the model needs longer to reach its best. Running it for "
             "thirty and concluding augmentation *did not help* is a common and "
             "expensive mistake."),

            ("h2", "The result"),
            ("py", """import numpy as np

h = history.history
epochs = range(1, len(h["accuracy"]) + 1)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
a1.plot(epochs, h["accuracy"], lw=1, label="training")
a1.plot(epochs, h["val_accuracy"], lw=1.6, label="validation")
a1.set_title("Accuracy"); a1.legend(); a1.set_xlabel("epoch")
a2.plot(epochs, h["loss"], lw=1, label="training")
a2.plot(epochs, h["val_loss"], lw=1.6, label="validation")
a2.set_title("Loss"); a2.legend(); a2.set_xlabel("epoch")
plt.tight_layout(); plt.show()

from keras.utils import image_dataset_from_directory
test_dataset = image_dataset_from_directory(
    new_base_dir / "test", image_size=(180, 180), batch_size=32)
best = keras.models.load_model("convnet_with_augmentation.keras")
print(f"test accuracy: {best.evaluate(test_dataset, verbose=0)[1]:.3f}")
print(f"validation loss bottoms out at epoch "
      f"{int(np.argmin(h['val_loss']))+1} of {len(epochs)}")"""),
            ("out", "test accuracy: ~0.83"),

            ("h2", "Where the ten points came from, and why not more"),
            ("md",
             "| | test accuracy |\n"
             "|---|---|\n"
             "| from scratch, no augmentation | ~0.70 |\n"
             "| + augmentation + dropout | **~0.83** |\n"
             "| pretrained backbone (notebook 04) | ~0.97 |\n\n"
             "Augmentation is worth thirteen points and stops there. It "
             "**resamples the manifold you have**; it does not add information "
             "the 2,000 photographs never contained.\n\n"
             "The pretrained model in notebook 04 gets its advantage from "
             "somewhere else entirely: 1.4 million images it was trained on "
             "before you arrived."),

            ("h2", "Choosing augmentations that are true"),
            ("py", """# A horizontal flip of a cat is still a cat.
# A horizontal flip of a digit is not still that digit.
from keras.datasets import mnist
(x, y), _ = mnist.load_data()

flip = layers.RandomFlip("horizontal")
img = x[0:1].reshape(1, 28, 28, 1).astype("float32")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(5, 2.6))
a1.imshow(img[0, :, :, 0], cmap="gray_r"); a1.set_title(f"label {y[0]}"); a1.axis("off")
a2.imshow(flip(img, training=True)[0, :, :, 0], cmap="gray_r")
a2.set_title("flipped -- still a 5?"); a2.axis("off")
plt.show()"""),
            ("md",
             "**An augmentation encodes a claim about your data**: *this "
             "transformation does not change the label*. Horizontal flip is true "
             "of animals and false of digits, text, and most medical imaging. "
             "Getting it wrong teaches the model something untrue, with no "
             "error message."),
        ],
        "takeaways": [
            "Augmentation layers are training-only, like dropout, and belong "
            "inside the model.",
            "It delays overfitting, so **train for longer** — judging it at the "
            "old epoch count understates it.",
            "Worth about thirteen points here; it resamples the manifold rather "
            "than adding information.",
            "Every augmentation asserts that a transformation preserves the "
            "label. Check that it does.",
        ],
    },

    {
        "file": "04_feature_extraction_and_finetuning.ipynb",
        "title": "A pretrained backbone: feature extraction, then fine-tuning",
        "lede": "The same 2,000 images, and 97% — because the model has already seen "
                "1.4 million others. This is the most valuable technique in the "
                "chapter and the one with the strictest procedure.",
        "needs": "GPU recommended — about 20 minutes on CPU · needs the Kaggle cats-vs-dogs archive",
        "section": "04 — Using a pretrained model",
        "cells": [
            ("h2", "Loading a backbone without its head"),
            ("py", """import keras
from keras import layers

conv_base = keras.applications.vgg16.VGG16(
    weights="imagenet",
    include_top=False,          # drop the 1000-class classifier
    input_shape=(180, 180, 3),
)
conv_base.summary()
print(f"\\n{conv_base.count_params():,} parameters, all pretrained")"""),
            ("md",
             "`include_top=False` drops the ImageNet classifier and keeps the "
             "**convolutional base** — the part that learned edges, textures, "
             "and object parts. Those transfer; the 1000-class head does not."),

            ("h2", "Fast feature extraction, without augmentation"),
            ("md",
             "Run every image through the frozen base once, cache the features, "
             "and train a small classifier on those. **Very fast, and it rules "
             "out augmentation** — the features are computed once, so there is "
             "nothing to randomise."),
            ("py", """import numpy as np
import pathlib
from keras.utils import image_dataset_from_directory

new_base_dir = pathlib.Path("cats_vs_dogs_small")
train_dataset = image_dataset_from_directory(
    new_base_dir / "train", image_size=(180, 180), batch_size=32)
validation_dataset = image_dataset_from_directory(
    new_base_dir / "validation", image_size=(180, 180), batch_size=32)
test_dataset = image_dataset_from_directory(
    new_base_dir / "test", image_size=(180, 180), batch_size=32)

def get_features_and_labels(dataset):
    all_features, all_labels = [], []
    for images, labels in dataset:
        preprocessed = keras.applications.vgg16.preprocess_input(images)
        features = conv_base.predict(preprocessed, verbose=0)
        all_features.append(features)
        all_labels.append(labels)
    return np.concatenate(all_features), np.concatenate(all_labels)

train_features, train_labels = get_features_and_labels(train_dataset)
val_features, val_labels = get_features_and_labels(validation_dataset)
test_features, test_labels = get_features_and_labels(test_dataset)
print(train_features.shape)"""),
            ("out", "(2000, 5, 5, 512)"),
            ("py", """inputs = keras.Input(shape=(5, 5, 512))
x = layers.Flatten()(inputs)
x = layers.Dense(256)(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(loss="binary_crossentropy", optimizer="rmsprop",
              metrics=["accuracy"])

callbacks = [keras.callbacks.ModelCheckpoint(
    "feature_extraction.keras", save_best_only=True, monitor="val_loss")]
h1 = model.fit(train_features, train_labels, epochs=20,
               validation_data=(val_features, val_labels),
               callbacks=callbacks, verbose=2)
print("test:", keras.models.load_model("feature_extraction.keras")
      .evaluate(test_features, test_labels, verbose=0)[1])"""),
            ("out", "test: ~0.97"),
            ("md",
             "**Ninety-seven percent, in twenty seconds of training.** Against "
             "70% from scratch and 83% with augmentation. Everything the base "
             "knows was learned before this notebook started."),

            ("h2", "Feature extraction with augmentation"),
            ("md",
             "Slower, because the base runs on every batch — but augmentation "
             "works again, and the ceiling is higher."),
            ("py", """conv_base.trainable = False
print("trainable weights after freezing:", len(conv_base.trainable_weights))

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.2),
])

inputs = keras.Input(shape=(180, 180, 3))
x = data_augmentation(inputs)
x = keras.applications.vgg16.preprocess_input(x)
x = conv_base(x)
x = layers.Flatten()(x)
x = layers.Dense(256)(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(loss="binary_crossentropy", optimizer="rmsprop",
              metrics=["accuracy"])"""),
            ("warn",
             "`conv_base.trainable = False` **before** compiling.** Setting it "
             "afterwards has no effect on an already-compiled model, and the "
             "base will train — destroying the weights you came for, with no "
             "error."),

            ("h2", "Fine-tuning: the procedure, in order"),
            ("md",
             "Unfreezing part of the base can add a few more points. The order "
             "is not negotiable.\n\n"
             "1. Add your head to a **frozen** base.\n"
             "2. Train the head to convergence.\n"
             "3. Unfreeze the **top few** layers of the base.\n"
             "4. Retrain both, at a **much lower** learning rate.\n\n"
             "Skip step 2 and the large, random gradients from an untrained head "
             "propagate into the base and wreck it on the first batch."),
            ("py", """conv_base.trainable = True
for layer in conv_base.layers[:-4]:
    layer.trainable = False

for layer in conv_base.layers:
    print(f"  {layer.name:24s} trainable={layer.trainable}")"""),
            ("py", """model.compile(loss="binary_crossentropy",
              optimizer=keras.optimizers.RMSprop(learning_rate=1e-5),
              metrics=["accuracy"])

callbacks = [keras.callbacks.ModelCheckpoint(
    "fine_tuning.keras", save_best_only=True, monitor="val_loss")]
h2 = model.fit(train_dataset, epochs=30,
               validation_data=validation_dataset,
               callbacks=callbacks, verbose=2)

best = keras.models.load_model("fine_tuning.keras")
print(f"test accuracy: {best.evaluate(test_dataset, verbose=0)[1]:.3f}")"""),
            ("md",
             "`learning_rate=1e-5` — a hundred times smaller than the default. "
             "The same discipline reappears in chapter 15 for RoBERTa and "
             "chapter 16 for Gemma. **Large updates destroy representations that "
             "cost a great deal to learn.**"),

            ("h2", "Why only the top layers"),
            ("py", """import matplotlib.pyplot as plt

names = [l.name for l in conv_base.layers if "conv" in l.name]
print("Earlier layers encode generic features -- edges, colours, textures.")
print("Later layers encode specific ones -- 'dog ear', 'car wheel'.")
print()
for i, n in enumerate(names):
    kind = "generic (keep frozen)" if i < len(names) - 3 else "specific (worth tuning)"
    print(f"  {n:16s} {kind}")"""),
            ("md",
             "Two reasons to leave the early layers alone: they encode features "
             "that transfer to *any* image problem, and every unfrozen layer is "
             "more parameters to fit from 2,000 samples. **More trainable "
             "parameters on a small dataset is more overfitting**, which is the "
             "thing you were trying to fix."),

            ("h2", "The whole chapter, in one table"),
            ("py", """print(f"{'approach':38s} {'test acc':>9s}")
print(f"{'-'*48}")
for name, acc in [("from scratch", 0.70),
                  ("+ augmentation + dropout", 0.83),
                  ("VGG16 features, cached", 0.97),
                  ("VGG16 + augmentation", 0.975),
                  ("VGG16 fine-tuned (top 4 layers)", 0.98)]:
    print(f"{name:38s} {acc:>9.3f}")
print("\\n(your numbers will vary by a point or two)")"""),
            ("md",
             "The largest single jump is **from scratch to pretrained**, and it "
             "is not close. Chapter 15 makes the same point about text and "
             "chapter 16 about generation. If there is one habit to take from "
             "this chapter: ==start from a pretrained backbone, always, and "
             "justify not doing so.=="),
        ],
        "takeaways": [
            "`include_top=False` keeps the convolutional base and drops the "
            "task-specific head.",
            "Cached features are fastest but rule out augmentation; running the "
            "base per batch costs time and restores it.",
            "Freeze **before** compiling, or the base trains and is destroyed.",
            "Fine-tune only the top layers, only after the head has converged, "
            "and only at a much lower learning rate.",
        ],
    },
]
