# -*- coding: utf-8 -*-
"""Chapter 9 notebooks — ConvNet Architecture Patterns."""

DECK = "ch09"

NOTEBOOKS = [
    {
        "file": "01_residual_connections.ipynb",
        "title": "Residual connections, and the depth they buy",
        "lede": "A network that stops learning past a certain depth, and the same "
                "network with shortcuts added. The difference is not subtle.",
        "needs": "CPU — about 5 minutes",
        "section": "02 — Residual connections",
        "cells": [
            ("h2", "The problem: depth without shortcuts"),
            ("py", """import keras
from keras import layers
from keras.datasets import mnist
import numpy as np

(x, y), (xt, yt) = mnist.load_data()
x = x.reshape(-1, 28, 28, 1).astype("float32") / 255
xt = xt.reshape(-1, 28, 28, 1).astype("float32") / 255

def plain_net(depth):
    keras.utils.set_random_seed(0)
    i = keras.Input(shape=(28, 28, 1))
    z = layers.Conv2D(32, 3, padding="same", activation="relu")(i)
    for _ in range(depth):
        z = layers.Conv2D(32, 3, padding="same", activation="relu")(z)
    z = layers.GlobalAveragePooling2D()(z)
    o = layers.Dense(10, activation="softmax")(z)
    m = keras.Model(i, o)
    m.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

results = {}
for d in [2, 8, 20]:
    m = plain_net(d)
    h = m.fit(x[:15000], y[:15000], epochs=6, batch_size=128,
              validation_split=.2, verbose=0)
    results[("plain", d)] = max(h.history["val_accuracy"])
    print(f"plain, {d:2d} extra layers -> val acc {results[('plain', d)]:.4f}")"""),
            ("out", """plain,  2 extra layers -> val acc 0.98xx
plain,  8 extra layers -> val acc 0.97xx
plain, 20 extra layers -> val acc 0.1x — 0.6x"""),
            ("md",
             "**Deeper is worse.** Not slightly — the twenty-layer version may "
             "fail to train at all. That is the vanishing-gradient problem: the "
             "signal has to survive twenty successive multiplications on its way "
             "back, and it does not."),

            ("h2", "The fix, in one line"),
            ("py", """def residual_net(depth):
    keras.utils.set_random_seed(0)
    i = keras.Input(shape=(28, 28, 1))
    z = layers.Conv2D(32, 3, padding="same", activation="relu")(i)
    for _ in range(depth):
        residual = z
        z = layers.Conv2D(32, 3, padding="same", activation="relu")(z)
        z = layers.add([z, residual])          # <- the whole idea
    z = layers.GlobalAveragePooling2D()(z)
    o = layers.Dense(10, activation="softmax")(z)
    m = keras.Model(i, o)
    m.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

for d in [2, 8, 20]:
    m = residual_net(d)
    h = m.fit(x[:15000], y[:15000], epochs=6, batch_size=128,
              validation_split=.2, verbose=0)
    results[("residual", d)] = max(h.history["val_accuracy"])
    print(f"residual, {d:2d} extra layers -> val acc {results[('residual', d)]:.4f}")"""),
            ("py", """import matplotlib.pyplot as plt

depths = [2, 8, 20]
plt.figure(figsize=(6.5, 4.2))
plt.plot(depths, [results[("plain", d)] for d in depths], "o-", label="plain")
plt.plot(depths, [results[("residual", d)] for d in depths], "s-", label="residual")
plt.xlabel("extra convolution layers"); plt.ylabel("best validation accuracy")
plt.legend(); plt.title("Residual connections keep deep networks trainable")
plt.show()"""),
            ("md",
             "`x = layers.add([x, residual])` gives the gradient a path back "
             "that **skips** the block entirely. It does not have to survive "
             "every multiplication — there is always a route home."),

            ("h2", "When the shapes do not match"),
            ("py", """# Case 1: the number of filters changes -- project with a 1x1 conv.
inputs = keras.Input(shape=(32, 32, 3))
z = layers.Conv2D(32, 3, activation="relu", padding="same")(inputs)
residual = z
z = layers.Conv2D(64, 3, activation="relu", padding="same")(z)
residual = layers.Conv2D(64, 1)(residual)      # no activation
z = layers.add([z, residual])
print("filters changed:", z.shape)

# Case 2: max pooling downsamples -- match it with strides on the shortcut.
inputs = keras.Input(shape=(32, 32, 3))
z = layers.Conv2D(32, 3, activation="relu", padding="same")(inputs)
residual = z
z = layers.Conv2D(64, 3, activation="relu", padding="same")(z)
z = layers.MaxPooling2D(2, padding="same")(z)
residual = layers.Conv2D(64, 1, strides=2)(residual)
z = layers.add([z, residual])
print("downsampled:    ", z.shape)"""),
            ("note",
             "The 1×1 projection carries **no activation**. Its job is to change "
             "shape, not to compute — putting a nonlinearity on the shortcut "
             "defeats the point of having a clean path."),

            ("h2", "A reusable block"),
            ("py", """def residual_block(x, filters, pooling=False):
    residual = x
    x = layers.Conv2D(filters, 3, activation="relu", padding="same")(x)
    x = layers.Conv2D(filters, 3, activation="relu", padding="same")(x)
    if pooling:
        x = layers.MaxPooling2D(2, padding="same")(x)
        residual = layers.Conv2D(filters, 1, strides=2)(residual)
    elif filters != residual.shape[-1]:
        residual = layers.Conv2D(filters, 1)(residual)
    return layers.add([x, residual])

inputs = keras.Input(shape=(32, 32, 3))
z = layers.Rescaling(1./255)(inputs)
z = residual_block(z, filters=32, pooling=True)
z = residual_block(z, filters=64, pooling=True)
z = residual_block(z, filters=128, pooling=False)
z = layers.GlobalAveragePooling2D()(z)
outputs = layers.Dense(1, activation="sigmoid")(z)
model = keras.Model(inputs, outputs)
model.summary()"""),
            ("md",
             "This is the shape of every modern ConvNet, and — as chapter 15 "
             "shows — of every Transformer block too. **Add, then normalize** is "
             "not a vision idea; it is a depth idea."),
        ],
        "takeaways": [
            "Past a certain depth, plain stacks stop training — the gradient does "
            "not survive the trip back.",
            "`add([x, residual])` gives it a path that skips the block.",
            "Project the shortcut with a **1×1 convolution and no activation** "
            "when shapes differ.",
            "The same pattern reappears in the Transformer block in chapter 15.",
        ],
    },

    {
        "file": "02_batchnorm_and_separable.ipynb",
        "title": "Batch normalization and separable convolutions",
        "lede": "Two patterns that cost almost nothing and change what is trainable — "
                "plus the ordering detail about BatchNormalization that most code "
                "gets wrong.",
        "needs": "CPU — about 4 minutes",
        "section": "03 — Batch normalization and 04 — Depthwise separable convolutions",
        "cells": [
            ("h2", "What batch normalization does"),
            ("py", """import numpy as np
import keras
from keras import layers
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
activations = rng.normal(loc=3.0, scale=2.5, size=(1000, 64)).astype("float32")

bn = layers.BatchNormalization()
normed = bn(activations, training=True).numpy()

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.4))
a1.hist(activations.ravel(), bins=60); a1.set_title(
    f"before: mean {activations.mean():.2f}, std {activations.std():.2f}")
a2.hist(normed.ravel(), bins=60); a2.set_title(
    f"after: mean {normed.mean():.2f}, std {normed.std():.2f}")
plt.tight_layout(); plt.show()"""),
            ("md",
             "Zero mean, unit variance, per feature, per batch. Chapter 6 said "
             "*normalize your inputs*; this normalizes the inputs to **every "
             "layer**, continuously, as the distribution shifts during training."),

            ("h2", "The ordering that most code gets wrong"),
            ("py", """# COMMON, and slightly wrong:
z = layers.Conv2D(32, 3, activation="relu")   # activation inside the conv
# ... then BatchNormalization after it

# BETTER:
inputs = keras.Input(shape=(32, 32, 3))
z = layers.Conv2D(32, 3, use_bias=False)(inputs)   # no activation, no bias
z = layers.BatchNormalization()(z)
z = layers.Activation("relu")(z)                   # activation AFTER
print("conv -> batchnorm -> activation:", z.shape)"""),
            ("md",
             "Two details:\n\n"
             "- **The activation goes after the normalization.** `relu` zeroes "
             "the negative half; normalizing afterwards is normalizing a "
             "truncated distribution. Doing it in this order gives `relu` a "
             "centred input, which is where it does the most work.\n"
             "- **`use_bias=False`.** BatchNormalization has its own centring "
             "parameter, so the convolution's bias is redundant — parameters "
             "with nothing to do."),

            ("h2", "Measuring whether it matters"),
            ("py", """from keras.datasets import cifar10
(x, y), (xt, yt) = cifar10.load_data()
x = x.astype("float32") / 255
xt = xt.astype("float32") / 255

def build(use_bn, lr=1e-2):
    keras.utils.set_random_seed(0)
    i = keras.Input(shape=(32, 32, 3))
    z = i
    for f in [32, 64, 128]:
        z = layers.Conv2D(f, 3, padding="same", use_bias=not use_bn)(z)
        if use_bn:
            z = layers.BatchNormalization()(z)
        z = layers.Activation("relu")(z)
        z = layers.MaxPooling2D(2)(z)
    z = layers.GlobalAveragePooling2D()(z)
    o = layers.Dense(10, activation="softmax")(z)
    m = keras.Model(i, o)
    m.compile(optimizer=keras.optimizers.SGD(learning_rate=lr),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return m

plt.figure(figsize=(7, 4.2))
for use_bn in [False, True]:
    h = build(use_bn).fit(x[:20000], y[:20000], epochs=10, batch_size=128,
                          validation_split=.2, verbose=0)
    plt.plot(h.history["val_accuracy"], lw=1.6,
             label="with BatchNorm" if use_bn else "without")
    print(f"{'with' if use_bn else 'without':8s} BN -> "
          f"best val acc {max(h.history['val_accuracy']):.4f}")
plt.xlabel("epoch"); plt.ylabel("validation accuracy"); plt.legend()
plt.title("BatchNorm at a deliberately aggressive learning rate (SGD 1e-2)")
plt.show()"""),
            ("md",
             "The gap widens with depth and with learning rate. **Batch "
             "normalization is what makes an aggressive learning rate "
             "survivable**, which is most of why it speeds training up."),

            ("h2", "Freezing a model that contains BatchNormalization"),
            ("warn",
             "The trap from chapter 8, in detail.** A frozen "
             "`BatchNormalization` layer still updates its running mean and "
             "variance during a forward pass in training mode — unless the "
             "layer itself is frozen. Setting `base.trainable = False` handles "
             "this correctly; freezing only the *weights* does not."),
            ("py", """base = keras.applications.VGG16(weights=None, include_top=False,
                                input_shape=(32, 32, 3))
base.trainable = False
print("trainable weights:", len(base.trainable_weights))
print("non-trainable:    ", len(base.non_trainable_weights))
print("\\nBatchNormalization layers hold 2 trainable + 2 non-trainable weights:")
print("  gamma, beta   (learned)")
print("  moving_mean, moving_variance   (statistics, not gradients)")"""),

            ("h2", "Separable convolutions"),
            ("py", """def count(layer_fn, shape=(32, 32, 64)):
    i = keras.Input(shape=shape)
    o = layer_fn(i)
    return keras.Model(i, o).count_params()

regular = count(lambda z: layers.Conv2D(128, 3, padding="same")(z))
separable = count(lambda z: layers.SeparableConv2D(128, 3, padding="same")(z))

print(f"Conv2D(128, 3)          {regular:>8,} parameters")
print(f"SeparableConv2D(128, 3) {separable:>8,} parameters")
print(f"{regular/separable:.1f}x fewer")"""),
            ("out", """Conv2D(128, 3)            73,856 parameters
SeparableConv2D(128, 3)    8,896 parameters
8.3x fewer"""),
            ("md",
             "A regular convolution learns spatial **and** channel patterns "
             "together. A separable one splits them: a depthwise convolution "
             "over each channel independently, then a 1×1 convolution to mix "
             "channels.\n\n"
             "The assumption — that spatial and channel structure are largely "
             "independent — is a **stronger prior**, and on natural images it "
             "holds. Chapter 12's YOLO and chapter 17's U-Net both rely on it."),

            ("h2", "Does the assumption cost accuracy?"),
            ("py", """def build_sep(separable):
    keras.utils.set_random_seed(0)
    Conv = layers.SeparableConv2D if separable else layers.Conv2D
    i = keras.Input(shape=(32, 32, 3))
    z = layers.Conv2D(32, 3, padding="same", activation="relu")(i)  # first stays regular
    for f in [64, 128]:
        z = Conv(f, 3, padding="same", use_bias=False)(z)
        z = layers.BatchNormalization()(z)
        z = layers.Activation("relu")(z)
        z = layers.MaxPooling2D(2)(z)
    z = layers.GlobalAveragePooling2D()(z)
    o = layers.Dense(10, activation="softmax")(z)
    m = keras.Model(i, o)
    m.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m

for sep in [False, True]:
    m = build_sep(sep)
    h = m.fit(x[:20000], y[:20000], epochs=10, batch_size=128,
              validation_split=.2, verbose=0)
    print(f"{'separable' if sep else 'regular  '}: "
          f"{m.count_params():>8,} params, "
          f"best val acc {max(h.history['val_accuracy']):.4f}")"""),
            ("md",
             "Comparable accuracy from a fraction of the parameters. Note that "
             "the **first** layer stays a regular convolution — with three input "
             "channels there is almost nothing to separate, and the assumption "
             "has no purchase."),
        ],
        "takeaways": [
            "Batch normalization keeps each layer's inputs centred as the "
            "distribution shifts during training.",
            "**Conv (no bias) → BatchNorm → Activation** is the right order, and "
            "most code gets it wrong.",
            "Freeze with `layer.trainable = False`, or the running statistics "
            "keep updating.",
            "Separable convolutions assume spatial and channel structure are "
            "independent — eight times fewer parameters, comparable accuracy.",
        ],
    },

    {
        "file": "03_mini_xception.ipynb",
        "title": "Putting the patterns together: a mini-Xception",
        "lede": "Residual connections, batch normalization, and separable convolutions "
                "in one architecture — the model the rest of the vision chapters build on.",
        "needs": "GPU recommended — about 15 minutes on CPU · needs the Kaggle cats-vs-dogs archive",
        "section": "05 — Putting it together",
        "cells": [
            ("h2", "The three patterns, assembled"),
            ("py", """import keras
from keras import layers

def mini_xception(input_shape=(180, 180, 3), num_classes=1):
    inputs = keras.Input(shape=input_shape)
    x = layers.Rescaling(1./255)(inputs)

    # A regular convolution first: three channels are not worth separating.
    x = layers.Conv2D(32, 5, use_bias=False)(x)

    for size in [32, 64, 128, 256, 512]:
        residual = x

        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same", use_bias=False)(x)

        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same", use_bias=False)(x)

        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)

        residual = layers.Conv2D(size, 1, strides=2, padding="same",
                                 use_bias=False)(residual)
        x = layers.add([x, residual])

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.5)(x)
    activation = "sigmoid" if num_classes == 1 else "softmax"
    outputs = layers.Dense(num_classes, activation=activation)(x)
    return keras.Model(inputs, outputs)

model = mini_xception()
print(f"{model.count_params():,} parameters, {len(model.layers)} layers")"""),
            ("md",
             "Five blocks, each: **normalize, activate, separable-convolve** — "
             "twice — then pool, then add the projected shortcut.\n\n"
             "Note the ordering inside the block: normalization and activation "
             "come **before** the convolution, not after. This is the "
             "*pre-activation* arrangement, and it keeps the residual path "
             "completely clean — nothing but additions from input to output."),

            ("h2", "Filter counts grow as the maps shrink"),
            ("py", """for l in model.layers:
    if isinstance(l, (layers.SeparableConv2D, layers.MaxPooling2D)):
        print(f"{l.__class__.__name__:18s} {str(l.output.shape):24s}")"""),
            ("md",
             "180 → 88 → 44 → 22 → 11 → 6, while filters go 32 → 512. "
             "**The same trade as chapter 8**, applied more aggressively."),

            ("h2", "Training it on cats and dogs"),
            ("py", """import pathlib
from keras.utils import image_dataset_from_directory

new_base_dir = pathlib.Path("cats_vs_dogs_small")
train_dataset = image_dataset_from_directory(
    new_base_dir / "train", image_size=(180, 180), batch_size=32)
validation_dataset = image_dataset_from_directory(
    new_base_dir / "validation", image_size=(180, 180), batch_size=32)
test_dataset = image_dataset_from_directory(
    new_base_dir / "test", image_size=(180, 180), batch_size=32)

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.2),
])

inputs = keras.Input(shape=(180, 180, 3))
x = data_augmentation(inputs)
outputs = mini_xception()(x)
model = keras.Model(inputs, outputs)

model.compile(loss="binary_crossentropy", optimizer="rmsprop",
              metrics=["accuracy"])
callbacks = [keras.callbacks.ModelCheckpoint("mini_xception.keras",
                                             save_best_only=True,
                                             monitor="val_loss")]
history = model.fit(train_dataset, epochs=60,
                    validation_data=validation_dataset,
                    callbacks=callbacks, verbose=2)"""),

            ("h2", "Against chapter 8's from-scratch model"),
            ("py", """import matplotlib.pyplot as plt
import numpy as np

h = history.history
plt.figure(figsize=(7, 4.4))
plt.plot(h["accuracy"], lw=1, label="training")
plt.plot(h["val_accuracy"], lw=1.7, label="validation")
plt.axhline(0.83, ls="--", c="k", lw=1,
            label="chapter 8, augmented, from scratch")
plt.xlabel("epoch"); plt.ylabel("accuracy"); plt.legend()
plt.title("Mini-Xception on the same 2,000 images")
plt.show()

best = keras.models.load_model("mini_xception.keras")
print(f"test accuracy: {best.evaluate(test_dataset, verbose=0)[1]:.3f}")"""),
            ("out", "test accuracy: ~0.88 to 0.90"),
            ("md",
             "About 90%, against 83% for chapter 8's plain stack on identical "
             "data. **Architecture is worth roughly seven points here** — and "
             "still not the 97% a pretrained backbone gives, which remains the "
             "chapter 8 lesson."),

            ("h2", "One block at a time: what each pattern contributes"),
            ("py", """import itertools

def variant(residual=True, bn=True, separable=True, blocks=(32, 64, 128)):
    keras.utils.set_random_seed(0)
    Conv = layers.SeparableConv2D if separable else layers.Conv2D
    i = keras.Input(shape=(180, 180, 3))
    x = layers.Rescaling(1./255)(i)
    x = layers.Conv2D(32, 5, use_bias=False)(x)
    for size in blocks:
        r = x
        if bn: x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = Conv(size, 3, padding="same", use_bias=False)(x)
        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)
        if residual:
            r = layers.Conv2D(size, 1, strides=2, padding="same",
                              use_bias=False)(r)
            x = layers.add([x, r])
    x = layers.GlobalAveragePooling2D()(x)
    o = layers.Dense(1, activation="sigmoid")(x)
    m = keras.Model(i, o)
    m.compile(loss="binary_crossentropy", optimizer="rmsprop",
              metrics=["accuracy"])
    return m

print("Run each of these for ~20 epochs and compare. Expect the ordering to")
print("hold even if the absolute numbers differ on your hardware:")
for name, kw in [("all three", {}),
                 ("no residual", {"residual": False}),
                 ("no batchnorm", {"bn": False}),
                 ("regular convolutions", {"separable": False})]:
    m = variant(**kw)
    print(f"  {name:22s} {m.count_params():>9,} parameters")"""),
            ("md",
             "Running the full comparison takes about an hour; the parameter "
             "counts alone are informative, and the exercise is worth doing once "
             "on your own hardware. **Ablation is how you find out which of your "
             "ideas were doing the work** — chapter 18 formalises it."),
        ],
        "takeaways": [
            "Mini-Xception is the three patterns composed: pre-activation, "
            "separable convolutions, projected residuals.",
            "Normalization and activation go **before** the convolution, keeping "
            "the residual path clean.",
            "Architecture is worth about seven points here — real, and smaller "
            "than pretraining.",
            "Ablate one pattern at a time to find out which of them was doing "
            "the work.",
        ],
    },
]
