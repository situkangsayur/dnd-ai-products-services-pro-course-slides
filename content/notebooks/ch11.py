# -*- coding: utf-8 -*-
"""Chapter 11 notebooks — Image Segmentation."""

DECK = "ch11"

NOTEBOOKS = [
    {
        "file": "01_segmentation_from_scratch.ipynb",
        "title": "Semantic segmentation on Oxford Pets",
        "lede": "Classifying every pixel rather than the image. Same ConvNet ideas, one "
                "decisive change: strides instead of pooling, because now position "
                "matters.",
        "needs": "GPU recommended — about 25 minutes on CPU",
        "section": "01 — Image segmentation",
        "cells": [
            ("h2", "The data"),
            ("py", """import os, pathlib
import keras

input_dir = "images/"
target_dir = "annotations/trimaps/"

# Download from https://www.robots.ox.ac.uk/~vgg/data/pets/ if not present.
input_img_paths = sorted(
    [os.path.join(input_dir, f) for f in os.listdir(input_dir)
     if f.endswith(".jpg")])
target_paths = sorted(
    [os.path.join(target_dir, f) for f in os.listdir(target_dir)
     if f.endswith(".png") and not f.startswith(".")])

print(f"{len(input_img_paths)} images")
print(input_img_paths[9])
print(target_paths[9])"""),
            ("py", """import matplotlib.pyplot as plt
import numpy as np
from keras.utils import load_img, img_to_array, array_to_img

plt.figure(figsize=(4, 4))
plt.axis("off")
plt.imshow(load_img(input_img_paths[9]))
plt.show()

def display_target(target_array):
    # Labels are 1, 2, 3. Subtract 1 and scale so they are visible.
    normalized = (target_array.astype("uint8") - 1) * 127
    plt.axis("off")
    plt.imshow(normalized[:, :, 0])

img = img_to_array(load_img(target_paths[9], color_mode="grayscale"))
plt.figure(figsize=(4, 4)); display_target(img); plt.show()
print("unique label values:", np.unique(img))"""),
            ("out", "unique label values: [1. 2. 3.]"),
            ("md",
             "Three classes per pixel: **1 = the animal, 2 = the background, "
             "3 = the outline.** The target has the same spatial shape as the "
             "input, which is the entire difference from chapter 8."),

            ("h2", "Loading everything into memory"),
            ("py", """img_size = (200, 200)
num_imgs = len(input_img_paths)

import random
random.Random(1337).shuffle(input_img_paths)
random.Random(1337).shuffle(target_paths)

def path_to_input_image(path):
    return img_to_array(load_img(path, target_size=img_size))

def path_to_target(path):
    img = img_to_array(
        load_img(path, target_size=img_size, color_mode="grayscale"))
    img = img.astype("uint8") - 1        # labels become 0, 1, 2
    return img

input_imgs = np.zeros((num_imgs,) + img_size + (3,), dtype="float32")
targets = np.zeros((num_imgs,) + img_size + (1,), dtype="uint8")
for i in range(num_imgs):
    input_imgs[i] = path_to_input_image(input_img_paths[i])
    targets[i] = path_to_target(target_paths[i])

num_val_samples = 1000
train_input_imgs = input_imgs[:-num_val_samples]
train_targets = targets[:-num_val_samples]
val_input_imgs = input_imgs[-num_val_samples:]
val_targets = targets[-num_val_samples:]
print(train_input_imgs.shape, train_targets.shape)"""),
            ("note",
             "The same shuffle seed on both lists. **They must stay aligned** — "
             "and two independently shuffled lists is a silent, total failure "
             "with no error message."),

            ("h2", "The model, and the one decisive change"),
            ("py", """from keras import layers

def get_model(img_size, num_classes):
    inputs = keras.Input(shape=img_size + (3,))
    x = layers.Rescaling(1./255)(inputs)

    x = layers.Conv2D(64, 3, strides=2, activation="relu", padding="same")(x)
    x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)
    x = layers.Conv2D(128, 3, strides=2, activation="relu", padding="same")(x)
    x = layers.Conv2D(128, 3, activation="relu", padding="same")(x)
    x = layers.Conv2D(256, 3, strides=2, padding="same", activation="relu")(x)
    x = layers.Conv2D(256, 3, activation="relu", padding="same")(x)

    x = layers.Conv2DTranspose(256, 3, activation="relu", padding="same")(x)
    x = layers.Conv2DTranspose(256, 3, activation="relu", padding="same",
                               strides=2)(x)
    x = layers.Conv2DTranspose(128, 3, activation="relu", padding="same")(x)
    x = layers.Conv2DTranspose(128, 3, activation="relu", padding="same",
                               strides=2)(x)
    x = layers.Conv2DTranspose(64, 3, activation="relu", padding="same")(x)
    x = layers.Conv2DTranspose(64, 3, activation="relu", padding="same",
                               strides=2)(x)

    outputs = layers.Conv2D(num_classes, 3, activation="softmax",
                            padding="same")(x)
    return keras.Model(inputs, outputs)

model = get_model(img_size=img_size, num_classes=3)
model.summary()"""),
            ("md",
             "**`strides=2` everywhere, and no `MaxPooling2D`.** Max pooling "
             "throws away *where* the maximum was, and for classification that "
             "is a feature — for segmentation it is the answer being discarded."),

            ("h2", "Training"),
            ("py", """model.compile(optimizer="rmsprop",
              loss="sparse_categorical_crossentropy")

callbacks = [keras.callbacks.ModelCheckpoint("oxford_segmentation.keras",
                                             save_best_only=True)]
history = model.fit(train_input_imgs, train_targets,
                    epochs=50, callbacks=callbacks, batch_size=64,
                    validation_data=(val_input_imgs, val_targets), verbose=2)"""),
            ("py", """epochs = range(1, len(history.history["loss"]) + 1)
plt.figure(figsize=(7, 4.2))
plt.plot(epochs, history.history["loss"], lw=1, label="training")
plt.plot(epochs, history.history["val_loss"], lw=1.7, label="validation")
plt.xlabel("epoch"); plt.ylabel("loss"); plt.legend()
plt.title(f"Overfits from about epoch "
          f"{int(np.argmin(history.history['val_loss']))+1}")
plt.show()"""),

            ("h2", "Predictions"),
            ("py", """model = keras.models.load_model("oxford_segmentation.keras")

i = 4
test_image = val_input_imgs[i]
mask = model.predict(np.expand_dims(test_image, 0), verbose=0)[0]

def display_mask(pred):
    mask = np.argmax(pred, axis=-1) * 127
    plt.axis("off"); plt.imshow(mask)

fig = plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1); plt.axis("off")
plt.imshow(array_to_img(test_image)); plt.title("input")
plt.subplot(1, 3, 2); plt.axis("off")
plt.imshow(val_targets[i][:, :, 0] * 127); plt.title("ground truth")
plt.subplot(1, 3, 3); display_mask(mask); plt.title("prediction")
plt.tight_layout(); plt.show()"""),
            ("md",
             "The animal is found. The **outline class is the weak one** — a "
             "one-pixel-wide band, and there are far fewer of those pixels than "
             "of the other two."),

            ("h2", "Per-class IoU, because pixel accuracy lies"),
            ("py", """preds = model.predict(val_input_imgs[:200], verbose=0).argmax(-1)
truth = val_targets[:200, :, :, 0]

print(f"pixel accuracy: {(preds == truth).mean():.4f}\\n")
names = ["animal", "background", "outline"]
for c in range(3):
    inter = ((preds == c) & (truth == c)).sum()
    union = ((preds == c) | (truth == c)).sum()
    freq = (truth == c).mean()
    print(f"{names[c]:11s} IoU {inter/union:.3f}   "
          f"{freq:.1%} of all pixels")"""),
            ("out", """pixel accuracy: 0.87xx

animal      IoU 0.8xx   3x.x% of all pixels
background  IoU 0.8xx   5x.x% of all pixels
outline     IoU 0.2xx    6.x% of all pixels"""),
            ("md",
             "**Pixel accuracy of 87% hides an outline IoU of 0.2.** Chapter 6's "
             "rule about choosing a metric that reflects what you want has teeth "
             "here: a model that ignored the outline entirely would barely dent "
             "the headline number."),
        ],
        "takeaways": [
            "Segmentation predicts a class per pixel; the target has the input's "
            "spatial shape.",
            "**Strides, not pooling** — max pooling discards the position that is "
            "the answer.",
            "Shuffle inputs and targets with the same seed, or fail silently and "
            "completely.",
            "Report per-class IoU; pixel accuracy hides the rare class you "
            "probably care about.",
        ],
    },

    {
        "file": "02_conv2dtranspose.ipynb",
        "title": "Conv2DTranspose, and the checkerboard artifact",
        "lede": "How upsampling with a learned kernel works, why it produces a grid "
                "pattern, and the two ways to avoid it.",
        "needs": "CPU — about 2 minutes",
        "section": "02 — Upsampling",
        "cells": [
            ("h2", "What it does to a shape"),
            ("py", """import keras
from keras import layers
import numpy as np

x = np.zeros((1, 8, 8, 4), dtype="float32")

for stride in [1, 2, 4]:
    out = layers.Conv2DTranspose(4, 3, strides=stride, padding="same")(x)
    print(f"strides={stride}: {x.shape} -> {out.shape}")"""),
            ("out", """strides=1: (1, 8, 8, 4) -> (1, 8, 8, 4)
strides=2: (1, 8, 8, 4) -> (1, 16, 16, 4)
strides=4: (1, 8, 8, 4) -> (1, 32, 32, 4)"""),
            ("md",
             "The inverse of a strided convolution in **shape** — not in value. "
             "It is sometimes called a *deconvolution*, which is wrong and "
             "misleading: nothing is being deconvolved."),

            ("h2", "The mechanism"),
            ("py", """import matplotlib.pyplot as plt

# One hot pixel, one fixed kernel, so the mechanism is visible.
inp = np.zeros((1, 4, 4, 1), dtype="float32")
inp[0, 1, 1, 0] = 1.0
inp[0, 2, 3, 0] = 1.0

ct = layers.Conv2DTranspose(1, 3, strides=2, padding="same",
                            use_bias=False,
                            kernel_initializer="ones")
out = ct(inp).numpy()

fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3.6))
a1.imshow(inp[0, :, :, 0], cmap="gray_r"); a1.set_title("input 4x4, two hot pixels")
a2.imshow(out[0, :, :, 0], cmap="gray_r"); a2.set_title("output 8x8")
for a in (a1, a2): a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()"""),
            ("md",
             "Each input pixel is **multiplied by the whole kernel** and stamped "
             "into the output at its strided position. Where the stamps overlap, "
             "the contributions add — and that overlap is where the artifact "
             "comes from."),

            ("h2", "The checkerboard"),
            ("py", """# kernel_size=3 with strides=2 gives uneven overlap.
bad = layers.Conv2DTranspose(1, 3, strides=2, padding="same",
                             use_bias=False, kernel_initializer="ones")
ones = np.ones((1, 16, 16, 1), dtype="float32")
out_bad = bad(ones).numpy()[0, :, :, 0]

# kernel_size divisible by stride overlaps evenly.
good = layers.Conv2DTranspose(1, 4, strides=2, padding="same",
                              use_bias=False, kernel_initializer="ones")
out_good = good(ones).numpy()[0, :, :, 0]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
a1.imshow(out_bad, cmap="gray"); a1.set_title(
    f"kernel 3, stride 2 -- values {np.unique(out_bad)}")
a2.imshow(out_good, cmap="gray"); a2.set_title(
    f"kernel 4, stride 2 -- values {np.unique(out_good)}")
for a in (a1, a2): a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()"""),
            ("md",
             "A uniform input produces a **striped output**. With kernel 3 and "
             "stride 2, some output pixels receive two contributions and some "
             "receive one — the grid pattern is baked into the arithmetic, "
             "before any learning happens."),

            ("h2", "Two fixes"),
            ("py", """# Fix 1: make kernel_size divisible by strides.
fix1 = keras.Sequential([layers.Conv2DTranspose(32, 4, strides=2,
                                                padding="same")])

# Fix 2: separate the upsampling from the convolution entirely.
fix2 = keras.Sequential([
    layers.UpSampling2D(size=2, interpolation="bilinear"),
    layers.Conv2D(32, 3, padding="same"),
])

probe = np.ones((1, 16, 16, 8), dtype="float32")
print("Conv2DTranspose(4, stride 2):", fix1(probe).shape,
      f"{fix1.count_params():,} params")
print("UpSampling + Conv2D:        ", fix2(probe).shape,
      f"{fix2.count_params():,} params")"""),
            ("md",
             "Fix 2 is what chapter 17's U-Net uses, and it is the one to reach "
             "for by default. **Interpolate, then convolve** — the upsampling is "
             "fixed and artifact-free, and the convolution learns what to do "
             "with the result."),

            ("h2", "Seeing it in a real decoder"),
            ("py", """def decoder(kind):
    keras.utils.set_random_seed(0)
    i = keras.Input(shape=(8, 8, 64))
    x = i
    for f in [64, 32, 16]:
        if kind == "transpose":
            x = layers.Conv2DTranspose(f, 3, strides=2, padding="same",
                                       activation="relu")(x)
        else:
            x = layers.UpSampling2D(2, interpolation="bilinear")(x)
            x = layers.Conv2D(f, 3, padding="same", activation="relu")(x)
    o = layers.Conv2D(1, 3, padding="same", activation="sigmoid")(x)
    return keras.Model(i, o)

probe = np.random.default_rng(0).normal(size=(1, 8, 8, 64)).astype("float32")
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
for ax, kind in zip(axes, ["transpose", "upsample"]):
    out = decoder(kind)(probe).numpy()[0, :, :, 0]
    ax.imshow(out, cmap="gray"); ax.set_title(kind); ax.axis("off")
plt.suptitle("Untrained decoders on the same input", y=1.0)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Untrained, so this shows the **structural bias** rather than "
             "anything learned. Training reduces the artifact; it does not "
             "remove it, and generative models in chapter 17 are where it "
             "becomes most visible."),
        ],
        "takeaways": [
            "`Conv2DTranspose` stamps a learned kernel at strided positions and "
            "adds the overlaps.",
            "Uneven overlap produces the **checkerboard artifact**, before any "
            "training.",
            "Fix by making kernel size divisible by stride, or by separating "
            "upsampling from convolution.",
            "`UpSampling2D` + `Conv2D` is the safer default, and what chapter "
            "17's U-Net uses.",
        ],
    },

    {
        "file": "03_segment_anything.ipynb",
        "title": "Segment Anything: a promptable pretrained segmenter",
        "lede": "The chapter-8 lesson in a new modality — a foundation model for "
                "segmentation, prompted with a point or a box, with no training at all.",
        "needs": "GPU recommended · downloads ~400 MB of weights",
        "section": "03 — Segment Anything",
        "cells": [
            ("h2", "Loading it"),
            ("py", """import keras
import keras_hub
import numpy as np
import matplotlib.pyplot as plt

model = keras_hub.models.SAMImageSegmenter.from_preset("sam_base_sa1b")
print(type(model).__name__)"""),
            ("md",
             "**SAM was trained on 1.1 billion masks over 11 million images.** "
             "Like the backbones in chapter 8, everything it knows was learned "
             "before this notebook started."),

            ("h2", "An image"),
            ("py", """image_path = keras.utils.get_file(
    origin="https://img-datasets.s3.amazonaws.com/elephant.jpg")
image = np.array(keras.utils.load_img(image_path, target_size=(1024, 1024)))

plt.figure(figsize=(6, 6))
plt.imshow(image); plt.axis("off"); plt.show()"""),

            ("h2", "Prompting with a point"),
            ("py", """def show_mask(mask, ax, color=(0.13, 0.55, 0.85, 0.6)):
    h, w = mask.shape[-2:]
    ax.imshow(mask.reshape(h, w, 1) * np.array(color).reshape(1, 1, -1))

point = np.array([[[580.0, 450.0]]])          # (batch, num_points, 2)
label = np.array([[1]])                        # 1 = foreground, 0 = background

outputs = model.predict({
    "images": image[np.newaxis, ...].astype("float32"),
    "points": point,
    "labels": label,
}, verbose=0)

mask = outputs["masks"][0][0] > 0.0
fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(image)
show_mask(mask, ax)
ax.scatter(point[0, :, 0], point[0, :, 1], c="yellow", s=200, marker="*",
           edgecolors="k")
ax.axis("off"); ax.set_title("One point, one mask")
plt.show()"""),
            ("md",
             "One click, no training, no labels. **This is the chapter-8 "
             "argument again**: the largest single jump available is not "
             "architecture, it is starting from something already trained."),

            ("h2", "The ambiguity SAM handles explicitly"),
            ("py", """# A point on a person could mean the shirt, the torso, or the whole person.
# SAM returns several masks and a confidence for each.
all_masks = outputs["masks"][0]
iou = outputs["iou_pred"][0]

fig, axes = plt.subplots(1, len(all_masks), figsize=(4 * len(all_masks), 4.4))
for ax, m, score in zip(np.atleast_1d(axes), all_masks, iou):
    ax.imshow(image); show_mask(m > 0.0, ax)
    ax.set_title(f"predicted IoU {float(score):.2f}", fontsize=10)
    ax.axis("off")
plt.suptitle("A point is ambiguous, so several masks are returned", y=1.02)
plt.tight_layout(); plt.show()"""),
            ("md",
             "**The ambiguity is in the prompt, not the model**, and SAM does "
             "not pretend otherwise. Returning several candidates with "
             "confidences is a better design than picking one and being "
             "confidently wrong — a pattern worth borrowing."),

            ("h2", "Prompting with a box"),
            ("py", """box = np.array([[[300.0, 200.0], [900.0, 800.0]]])   # two corners

outputs = model.predict({
    "images": image[np.newaxis, ...].astype("float32"),
    "boxes": box,
}, verbose=0)

fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(image)
show_mask(outputs["masks"][0][0] > 0.0, ax)
x0, y0 = box[0, 0]; x1, y1 = box[0, 1]
ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0,
                           fill=False, edgecolor="yellow", lw=2))
ax.axis("off"); ax.set_title("Box prompt — far less ambiguous")
plt.show()"""),

            ("h2", "When to reach for this, and when not"),
            ("md",
             "| Situation | What to do |\n"
             "|---|---|\n"
             "| Generic objects, no labelled data | **SAM, zero-shot.** Nothing "
             "you train in a week will compete. |\n"
             "| A specific domain — cells, defects, satellite imagery | SAM **as "
             "a labelling accelerator**, then fine-tune a smaller model on the "
             "masks it helped you produce. |\n"
             "| Fixed classes, plenty of labels, tight latency budget | Notebook "
             "01's model, or a U-Net. SAM is large and general, and you are "
             "paying for generality you do not need. |\n\n"
             "The middle row is the one most projects land on, and it is worth "
             "planning for: **the fastest route to a labelled dataset is often a "
             "foundation model plus a human correcting it.**"),
        ],
        "takeaways": [
            "SAM segments generic objects with no training, prompted by a point "
            "or a box.",
            "It returns several masks with confidences, because a point prompt "
            "is genuinely ambiguous.",
            "The chapter-8 lesson holds in a new modality: pretraining beats "
            "architecture.",
            "In a specialised domain, use it to build the labelled dataset, then "
            "train something small.",
        ],
    },
]
