# -*- coding: utf-8 -*-
"""Chapter 17 notebooks — Image Generation."""

DECK = "ch17"

NOTEBOOKS = [
    {
        "file": "01_vae_on_mnist.ipynb",
        "title": "A variational autoencoder, built",
        "lede": "Encoder to a distribution, a sampling layer, a decoder — and both "
                "halves of the loss, with an ablation showing what each one does.",
        "needs": "CPU — about 8 minutes (GPU: 2 minutes)",
        "section": "01 — Variational autoencoders",
        "cells": [
            ("h2", "First, a classical autoencoder, so the difference is visible"),
            ("py", """import keras
from keras import layers
from keras.datasets import mnist
import numpy as np
import matplotlib.pyplot as plt

(x_train, _), (x_test, _) = mnist.load_data()
x_train = np.expand_dims(x_train, -1).astype("float32") / 255
x_test = np.expand_dims(x_test, -1).astype("float32") / 255

keras.utils.set_random_seed(0)
inp = keras.Input(shape=(28, 28, 1))
z = layers.Conv2D(32, 3, activation="relu", strides=2, padding="same")(inp)
z = layers.Conv2D(64, 3, activation="relu", strides=2, padding="same")(z)
z = layers.Flatten()(z)
code = layers.Dense(2, name="code")(z)           # a POINT, not a distribution
z = layers.Dense(7 * 7 * 64, activation="relu")(code)
z = layers.Reshape((7, 7, 64))(z)
z = layers.Conv2DTranspose(64, 3, activation="relu", strides=2,
                           padding="same")(z)
z = layers.Conv2DTranspose(32, 3, activation="relu", strides=2,
                           padding="same")(z)
out = layers.Conv2D(1, 3, activation="sigmoid", padding="same")(z)
plain_ae = keras.Model(inp, out)
plain_ae.compile(optimizer="adam", loss="binary_crossentropy")
plain_ae.fit(x_train, x_train, epochs=10, batch_size=128, verbose=0)
print("plain autoencoder trained")"""),
            ("py", """plain_encoder = keras.Model(inp, code)
codes = plain_encoder.predict(x_test[:4000], verbose=0)

plt.figure(figsize=(6, 6))
plt.scatter(codes[:, 0], codes[:, 1], c=mnist.load_data()[1][1][:4000],
            cmap="tab10", s=5, alpha=.6)
plt.colorbar(); plt.title("Plain autoencoder: the 2-d code space")
plt.show()

# Decode a grid of points and see what is between the clusters.
dec_in = keras.Input(shape=(2,))
# Start just after the code layer -- by NAME, because layer indices shift between
# Keras versions (Keras 3 counts the InputLayer, Keras 2 did not).
start = plain_ae.layers.index(plain_ae.get_layer("code")) + 1
h = dec_in
for layer in plain_ae.layers[start:]:
    h = layer(h)
plain_decoder = keras.Model(dec_in, h)

grid = np.array([[x, y] for y in np.linspace(codes[:,1].max(), codes[:,1].min(), 8)
                        for x in np.linspace(codes[:,0].min(), codes[:,0].max(), 8)])
imgs = plain_decoder.predict(grid, verbose=0)
fig, axes = plt.subplots(8, 8, figsize=(7, 7))
for ax, im in zip(axes.ravel(), imgs):
    ax.imshow(im[:, :, 0], cmap="gray_r"); ax.axis("off")
plt.suptitle("Plain autoencoder: islands, and mush between them", y=1.0)
plt.tight_layout(); plt.show()"""),
            ("md",
             "**Islands of digits with regions between them that decode to "
             "nothing.** The space is not continuous, so sampling from it does "
             "not work — which is exactly why classical autoencoders fell out of "
             "fashion for generation."),

            ("h2", "The VAE encoder: two outputs, not one"),
            ("py", """latent_dim = 2

image_inputs = keras.Input(shape=(28, 28, 1))
x = layers.Conv2D(32, 3, activation="relu", strides=2, padding="same")(
    image_inputs)
x = layers.Conv2D(64, 3, activation="relu", strides=2, padding="same")(x)
x = layers.Flatten()(x)
x = layers.Dense(16, activation="relu")(x)
z_mean = layers.Dense(latent_dim, name="z_mean")(x)
z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)
encoder = keras.Model(image_inputs, [z_mean, z_log_var], name="encoder")
encoder.summary()"""),
            ("md",
             "**Strides, not pooling** — the same reason as chapter 11. The "
             "encoding has to support reconstructing a valid image, so *where* "
             "things are must survive."),

            ("h2", "The sampling layer"),
            ("py", """from keras import ops

class Sampler(keras.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seed_generator = keras.random.SeedGenerator()
        self.built = True

    def call(self, z_mean, z_log_var):
        batch_size = ops.shape(z_mean)[0]
        z_size = ops.shape(z_mean)[1]
        epsilon = keras.random.normal((batch_size, z_size),
                                      seed=self.seed_generator)
        return z_mean + ops.exp(0.5 * z_log_var) * epsilon"""),
            ("md",
             "`exp(0.5 * z_log_var)` turns a **log variance** into a standard "
             "deviation. Predicting the log keeps the encoder's output "
             "unconstrained — it may be negative — and the exponential makes it "
             "positive."),

            ("h2", "The decoder"),
            ("py", """latent_inputs = keras.Input(shape=(latent_dim,))
x = layers.Dense(7 * 7 * 64, activation="relu")(latent_inputs)
x = layers.Reshape((7, 7, 64))(x)
x = layers.Conv2DTranspose(64, 3, activation="relu", strides=2,
                           padding="same")(x)
x = layers.Conv2DTranspose(32, 3, activation="relu", strides=2,
                           padding="same")(x)
decoder_outputs = layers.Conv2D(1, 3, activation="sigmoid", padding="same")(x)
decoder = keras.Model(latent_inputs, decoder_outputs, name="decoder")
decoder.summary()"""),
            ("md",
             "A mirror of the encoder. `Dense(7*7*64)` produces exactly the "
             "coefficients the encoder's `Flatten` consumed — **reading it as a "
             "mirror is the quickest way to check it.**"),

            ("h2", "compute_loss, not train_step"),
            ("py", """class VAE(keras.Model):
    def __init__(self, encoder, decoder, **kwargs):
        super().__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.sampler = Sampler()
        self.reconstruction_loss_tracker = keras.metrics.Mean(
            name="reconstruction_loss")
        self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")

    def call(self, inputs):
        return self.encoder(inputs)

    def compute_loss(self, x, y, y_pred, sample_weight=None, training=True):
        z_mean, z_log_var = y_pred
        reconstruction = self.decoder(self.sampler(z_mean, z_log_var))
        reconstruction_loss = ops.mean(ops.sum(
            keras.losses.binary_crossentropy(x, reconstruction), axis=(1, 2)))
        kl_loss = -0.5 * (1 + z_log_var - ops.square(z_mean)
                          - ops.exp(z_log_var))
        total_loss = reconstruction_loss + ops.mean(kl_loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        return total_loss"""),
            ("md",
             "This is the first model in the course **not doing supervised "
             "learning** — the input is the target. Departing from supervised "
             "learning normally means a custom `train_step()`, which is "
             "**backend specific**. Overriding `compute_loss()` instead keeps "
             "the default `train_step` and runs unchanged on all three "
             "backends."),

            ("h2", "Training, with no loss and no targets"),
            ("py", """mnist_digits = np.concatenate([x_train, x_test], axis=0)

vae = VAE(encoder, decoder)
vae.compile(optimizer=keras.optimizers.Adam())     # note: no loss=
vae.fit(mnist_digits, epochs=30, batch_size=128, verbose=2)"""),
            ("note",
             "No `loss=` at compile time, and **no targets in `fit()`**. Both "
             "follow from `compute_loss()` supplying its own objective."),

            ("h2", "Watching the two loss terms"),
            ("py", """h = vae.history.history
plt.figure(figsize=(7, 4.2))
plt.plot(h["reconstruction_loss"], lw=1.6, label="reconstruction")
plt.plot(h["kl_loss"], lw=1.6, label="KL divergence")
plt.xlabel("epoch"); plt.legend(); plt.yscale("log")
plt.title("The two terms pull in different directions")
plt.show()"""),
            ("md",
             "Reconstruction wants the encoder to spread points out so it can "
             "tell them apart. KL wants them collapsed onto a unit normal. "
             "**The equilibrium between the two is the structured space.**"),

            ("h2", "The ablation: what each term does"),
            ("py", """class NoKL(VAE):
    def compute_loss(self, x, y, y_pred, sample_weight=None, training=True):
        z_mean, z_log_var = y_pred
        rec = self.decoder(self.sampler(z_mean, z_log_var))
        return ops.mean(ops.sum(
            keras.losses.binary_crossentropy(x, rec), axis=(1, 2)))

keras.utils.set_random_seed(0)
enc2 = keras.models.clone_model(encoder)
dec2 = keras.models.clone_model(decoder)
nokl = NoKL(enc2, dec2)
nokl.compile(optimizer=keras.optimizers.Adam())
nokl.fit(mnist_digits[:20000], epochs=10, batch_size=128, verbose=0)

fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))
for ax, model, title in [(axes[0], vae, "with KL term"),
                         (axes[1], nokl, "reconstruction only")]:
    m, _ = model.encoder.predict(x_test[:3000], verbose=0)
    ax.scatter(m[:, 0], m[:, 1], c=mnist.load_data()[1][1][:3000],
               cmap="tab10", s=5, alpha=.6)
    ax.set_title(title)
plt.suptitle("The KL term is what makes the space usable", y=1.0)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Without KL the encoder spreads points as far apart as it likes — "
             "reconstruction improves, and the space becomes **unsamplable**, "
             "which is the plain autoencoder again.\n\n"
             "**The regularizer is not a refinement here. It is the entire "
             "reason the model is generative.**"),
        ],
        "takeaways": [
            "A classical autoencoder's latent space has islands; the gaps decode "
            "to nothing.",
            "A VAE encodes to a **distribution**, samples from it, and adds a KL "
            "term.",
            "Override `compute_loss()` rather than `train_step()` to stay "
            "backend-agnostic.",
            "Ablate the KL term and the space becomes unsamplable — it is the "
            "reason the model is generative.",
        ],
    },

    {
        "file": "02_vae_latent_space_grid.ipynb",
        "title": "Walking the latent space",
        "lede": "The 30×30 grid of decoded digits, the concept vectors hiding in it, and "
                "the interpolation that pixel space could not do.",
        "needs": "CPU — about 2 minutes · needs the VAE from notebook 01",
        "section": "01 — Variational autoencoders",
        "cells": [
            ("h2", "The grid"),
            ("py", """import numpy as np
import matplotlib.pyplot as plt

n = 30
digit_size = 28
figure = np.zeros((digit_size * n, digit_size * n))

grid_x = np.linspace(-1, 1, n)
grid_y = np.linspace(-1, 1, n)[::-1]

for i, yi in enumerate(grid_y):
    for j, xi in enumerate(grid_x):
        z_sample = np.array([[xi, yi]])
        x_decoded = vae.decoder.predict(z_sample, verbose=0)
        digit = x_decoded[0].reshape(digit_size, digit_size)
        figure[i * digit_size:(i + 1) * digit_size,
               j * digit_size:(j + 1) * digit_size] = digit

plt.figure(figsize=(13, 13))
plt.imshow(figure, cmap="Greys_r")
plt.xticks([]); plt.yticks([])
plt.xlabel("z[0]"); plt.ylabel("z[1]")
plt.title("900 digits, none of which are in MNIST")
plt.show()"""),
            ("md",
             "**A completely continuous distribution.** One digit morphs into "
             "another as you follow any path. There are no gaps, and that is the "
             "KL term's doing.\n\n"
             "Specific directions have meaning — a direction for *four-ness*, "
             "one for *one-ness*. Nobody labelled them."),

            ("h2", "Finding a concept vector"),
            ("py", """import keras
from keras.datasets import mnist

(_, y_train), (x_test, y_test) = mnist.load_data()
_, (xt, yt) = mnist.load_data()
xt = np.expand_dims(xt, -1).astype("float32") / 255

z_mean, _ = vae.encoder.predict(xt[:6000], verbose=0)
labels = yt[:6000]

centroids = np.stack([z_mean[labels == d].mean(axis=0) for d in range(10)])
for d in range(10):
    print(f"digit {d}: centroid {centroids[d].round(3)}")

# A "concept vector": the direction from one digit's region to another's.
v = centroids[9] - centroids[4]
print(f"\\n4 -> 9 direction: {v.round(3)}")"""),
            ("py", """start = centroids[4]
steps = np.linspace(0, 1, 9)
imgs = vae.decoder.predict(
    np.stack([start + t * v for t in steps]), verbose=0)

fig, axes = plt.subplots(1, 9, figsize=(13, 1.9))
for ax, im, t in zip(axes, imgs, steps):
    ax.imshow(im[:, :, 0], cmap="gray_r"); ax.axis("off")
    ax.set_title(f"{t:.2f}", fontsize=8)
plt.suptitle("Walking the 4 -> 9 concept vector", y=1.12)
plt.show()"""),
            ("md",
             "The same *word arithmetic* idea as chapter 15's `V(king) − V(man) + "
             "V(woman)`, in pixels. **A direction in the space corresponds to a "
             "meaningful change**, and this is what chapter 17's slides mean by "
             "the space being *suitable to manipulation via concept vectors*."),

            ("h2", "The comparison that matters: pixel space against latent space"),
            ("py", """a_idx = np.where(yt == 4)[0][0]
b_idx = np.where(yt == 9)[0][0]
a, b = xt[a_idx], xt[b_idx]

# Pixel-space interpolation, from chapter 5's notebook 02.
alphas = np.linspace(0, 1, 9)
pixel = [(1 - t) * a + t * b for t in alphas]

# Latent-space interpolation.
za, _ = vae.encoder.predict(a[None], verbose=0)
zb, _ = vae.encoder.predict(b[None], verbose=0)
latent = vae.decoder.predict(
    np.stack([(1 - t) * za[0] + t * zb[0] for t in alphas]), verbose=0)

fig, axes = plt.subplots(2, 9, figsize=(13, 3.4))
for j, t in enumerate(alphas):
    axes[0, j].imshow(pixel[j][:, :, 0], cmap="gray_r"); axes[0, j].axis("off")
    axes[1, j].imshow(latent[j][:, :, 0], cmap="gray_r"); axes[1, j].axis("off")
axes[0, 0].set_title("pixel space", loc="left", fontsize=10)
axes[1, 0].set_title("latent space", loc="left", fontsize=10)
plt.tight_layout(); plt.show()"""),
            ("md",
             "**The top row is ghosts** — two digits superimposed, not a digit. "
             "The bottom row is valid digits all the way across.\n\n"
             "Chapter 5 showed the top row and promised the bottom one. This is "
             "the payoff, and it is the single clearest picture of what "
             "*representation learning* buys."),

            ("h2", "Where the classes actually sit"),
            ("py", """plt.figure(figsize=(8, 7))
sc = plt.scatter(z_mean[:, 0], z_mean[:, 1], c=labels, cmap="tab10",
                 s=5, alpha=.6)
for d in range(10):
    plt.annotate(str(d), centroids[d], fontsize=16, weight="bold",
                 ha="center", va="center",
                 bbox=dict(boxstyle="circle", fc="w", alpha=.8))
plt.colorbar(sc); plt.title("The latent space, labelled")
plt.show()"""),
            ("md",
             "Confusable digits are adjacent — 4, 9 and 7 share a region; 3, 5 "
             "and 8 share another. **The geometry predicts the confusions**, the "
             "same relationship chapter 10's notebook 04 found in a classifier's "
             "penultimate layer."),

            ("h2", "The limitation of two dimensions"),
            ("py", """print("A 2-d latent space is plottable, which is why it was chosen.")
print("It is also very tight: 784 pixels compressed to 2 numbers.")
print()
print("Try latent_dim = 8 or 32 in notebook 01 and compare:")
print("  - reconstruction quality will improve noticeably")
print("  - the grid visualization stops being possible")
print("  - t-SNE (chapter 10) becomes the way to look at it")
print()
print("Chapter 17's diffusion models work in a latent space of 16")
print("channels at 1/8 resolution -- thousands of dimensions.")"""),
        ],
        "takeaways": [
            "The decoded grid is continuous everywhere — that is the KL term's "
            "effect, visible.",
            "Directions in the space are **concept vectors**, the pixel analogue "
            "of chapter 15's word arithmetic.",
            "Latent interpolation gives valid digits where pixel interpolation "
            "gives ghosts.",
            "Two dimensions are plottable and tight; real models use thousands.",
        ],
    },

    {
        "file": "03_diffusion_unet_and_schedule.ipynb",
        "title": "The U-Net and the diffusion schedule",
        "lede": "The two pieces a diffusion model is made of, built and inspected before "
                "anything is trained.",
        "needs": "CPU — about 3 minutes",
        "section": "02 — Diffusion models",
        "cells": [
            ("h2", "The idea, stated once"),
            ("md",
             "An autoencoder can remove a **small** amount of noise. Repeat it "
             "in a loop and it can remove a **large** amount. Could it denoise "
             "an image made of *pure* noise?\n\n"
             "Yes — and doing so hallucinates a new image out of nothing. These "
             "should more accurately be called **reverse** diffusion models; "
             "*diffusion* is the forward process of adding noise until the image "
             "disperses."),

            ("h2", "The diffusion schedule"),
            ("py", """import keras
from keras import ops
import numpy as np
import matplotlib.pyplot as plt

def diffusion_schedule(diffusion_times, min_signal_rate=0.02,
                       max_signal_rate=0.95):
    start_angle = ops.cast(ops.arccos(max_signal_rate), "float32")
    end_angle = ops.cast(ops.arccos(min_signal_rate), "float32")
    diffusion_angles = start_angle + diffusion_times * (end_angle - start_angle)
    signal_rates = ops.cos(diffusion_angles)
    noise_rates = ops.sin(diffusion_angles)
    return noise_rates, signal_rates

t = ops.arange(0.0, 1.0, 0.01)
nr, sr = diffusion_schedule(t)
t = ops.convert_to_numpy(t)
nr = ops.convert_to_numpy(nr); sr = ops.convert_to_numpy(sr)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
a1.plot(t, nr, lw=2, label="noise rate")
a1.plot(t, sr, lw=2, label="signal rate")
a1.set_xlabel("diffusion time"); a1.legend(); a1.set_title("Cosine schedule")
a2.plot(nr, sr, lw=2)
a2.set_xlabel("noise rate"); a2.set_ylabel("signal rate")
a2.set_aspect("equal"); a2.set_title("noise^2 + signal^2 = 1")
plt.tight_layout(); plt.show()

print("identity holds:", np.allclose(nr**2 + sr**2, 1.0))"""),
            ("md",
             "**Diffusion time runs from 1 to 0**: 1 is maximal noise, 0 is "
             "almost all signal. The cosine choice maintains "
             "`noise² + signal² = 1`, so total energy is constant as the mix "
             "shifts.\n\n"
             "The two bounds keep the process away from its extremes — never "
             "quite pure signal (0.95), never quite pure noise (0.02). Both "
             "endpoints are numerically awkward and neither is needed."),

            ("h2", "Seeing it on a real image"),
            ("py", """from keras.datasets import cifar10
(x, _), _ = cifar10.load_data()
img = x[7].astype("float32") / 255
img = (img - img.mean()) / img.std()      # the noise has unit variance

rng = np.random.default_rng(0)
noise = rng.normal(size=img.shape).astype("float32")

times = [0.0, 0.25, 0.5, 0.75, 1.0]
fig, axes = plt.subplots(1, len(times), figsize=(15, 3.2))
for ax, tt in zip(axes, times):
    n_, s_ = diffusion_schedule(ops.array([[[[tt]]]]))
    # .item(): NumPy 2 refuses float() on a non-0-d array, and these are shape (1,1,1,1).
    n_ = ops.convert_to_numpy(n_).item(); s_ = ops.convert_to_numpy(s_).item()
    mixed = s_ * img + n_ * noise
    show = np.clip((mixed - mixed.min()) / (mixed.max() - mixed.min()), 0, 1)
    ax.imshow(show); ax.axis("off")
    ax.set_title(f"t = {tt}\\nsignal {s_:.2f}", fontsize=9)
plt.suptitle("The forward process — this is what the model learns to undo", y=1.06)
plt.tight_layout(); plt.show()"""),

            ("h2", "The residual block"),
            ("py", """from keras import layers

def residual_block(x, width):
    input_width = x.shape[3]
    if input_width == width:
        residual = x
    else:
        residual = layers.Conv2D(width, 1)(x)
    x = layers.BatchNormalization(center=False, scale=False)(x)
    x = layers.Conv2D(width, 3, padding="same", activation="swish")(x)
    x = layers.Conv2D(width, 3, padding="same")(x)
    return x + residual"""),
            ("md",
             "Chapter 9's pattern, with `swish` instead of `relu` and "
             "normalization that learns **neither** a scale nor a centre — the "
             "residual path carries those."),

            ("h2", "The U-Net"),
            ("py", """def get_model(image_size, widths, block_depth):
    noisy_images = keras.Input(shape=(image_size, image_size, 3))
    noise_rates = keras.Input(shape=(1, 1, 1))

    x = layers.Conv2D(widths[0], 1)(noisy_images)
    n = layers.UpSampling2D(image_size, interpolation="nearest")(noise_rates)
    x = layers.Concatenate()([x, n])

    skips = []
    for width in widths[:-1]:
        for _ in range(block_depth):
            x = residual_block(x, width)
            skips.append(x)
        x = layers.AveragePooling2D(pool_size=2)(x)

    for _ in range(block_depth):
        x = residual_block(x, widths[-1])

    for width in reversed(widths[:-1]):
        x = layers.UpSampling2D(size=2, interpolation="bilinear")(x)
        for _ in range(block_depth):
            x = layers.Concatenate()([x, skips.pop()])
            x = residual_block(x, width)

    pred_noise_masks = layers.Conv2D(3, 1, kernel_initializer="zeros")(x)
    return keras.Model([noisy_images, noise_rates], pred_noise_masks)

unet = get_model(image_size=128, widths=[32, 64, 96, 128], block_depth=2)
print(f"{unet.count_params():,} parameters")
print("input shapes:", [tuple(i.shape) for i in unet.inputs])
print("output shape:", tuple(unet.output.shape))"""),
            ("md",
             "Three details worth naming:\n\n"
             "**The scalar noise rate is upsampled to full image size** and "
             "concatenated as a channel — the standard way to feed a scalar "
             "condition to a convolutional network.\n\n"
             "**`skips.pop()`** pairs each upsampling block with its mirror on "
             "the way down. Last in, first out is exactly the pairing the "
             "architecture diagram shows.\n\n"
             "**`kernel_initializer=\"zeros\"`** on the last layer: the model "
             "predicts only zeros at initialization, so its default assumption "
             "before training is *no noise*."),

            ("h2", "The output is a noise mask, not an image"),
            ("py", """probe_img = np.zeros((1, 128, 128, 3), dtype="float32")
probe_rate = np.array([[[[0.5]]]], dtype="float32")
out = unet([probe_img, probe_rate])
print("output:", out.shape, " all zeros at init:",
      bool(np.abs(np.array(out)).max() < 1e-8))
print()
print("Predicting what to REMOVE is an easier target than predicting")
print("what remains -- and it is why the denoise() step in the next")
print("notebook is a subtraction rather than a reconstruction.")"""),

            ("h2", "Why the widths grow as the maps shrink"),
            ("py", """for l in unet.layers:
    if isinstance(l, (layers.AveragePooling2D, layers.UpSampling2D)):
        print(f"{l.__class__.__name__:18s} -> {tuple(l.output.shape[1:])}")"""),
            ("md",
             "128 → 64 → 32 → 16, then back. **The same space-for-semantics "
             "trade as every ConvNet in this course**, with the skip connections "
             "carrying the spatial detail that the downsampling discarded."),
        ],
        "takeaways": [
            "The cosine schedule keeps `noise² + signal² = 1` as the mix shifts "
            "from one to the other.",
            "The U-Net takes **two inputs** — the noisy image and the noise rate.",
            "Skip connections preserve the detail that downsampling loses.",
            "The model predicts the **noise mask**, which is an easier target "
            "than the clean image.",
        ],
    },

    {
        "file": "04_training_the_flower_diffuser.ipynb",
        "title": "Training a diffusion model on Oxford Flowers",
        "lede": "The training step in five operations, the generation loop that re-noises "
                "on purpose, and 8,189 photographs turned into flowers that do not exist.",
        "needs": "GPU required — about 90 minutes on a Colab T4 · continues from notebook 03 (same kernel)",
        "section": "02 — Diffusion models",
        "cells": [
            ("h2", "The dataset"),
            ("py", """import os
import keras

fpath = keras.utils.get_file(
    origin="https://www.robots.ox.ac.uk/~vgg/data/flowers/102/102flowers.tgz",
    extract=True)

batch_size, image_size = 32, 128
images_dir = os.path.join(fpath, "jpg")

dataset = keras.utils.image_dataset_from_directory(
    images_dir,
    labels=None,
    image_size=(image_size, image_size),
    crop_to_aspect_ratio=True,
)
dataset = dataset.rebatch(batch_size, drop_remainder=True)

import matplotlib.pyplot as plt
for batch in dataset.take(1):
    fig, axes = plt.subplots(2, 6, figsize=(13, 4.4))
    for ax, im in zip(axes.ravel(), batch):
        ax.imshow(im.numpy().astype("uint8")); ax.axis("off")
    plt.tight_layout(); plt.show()
    break"""),
            ("warn",
             "`crop_to_aspect_ratio=True`.** Resizing without it distorts every "
             "image, and **distortion in the training set becomes distortion in "
             "everything generated** — very hard to diagnose after the fact."),

            ("h2", "The model class"),
            ("py", """from keras import ops
import numpy as np

class DiffusionModel(keras.Model):
    def __init__(self, image_size, widths, block_depth, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.denoising_model = get_model(image_size, widths, block_depth)
        self.seed_generator = keras.random.SeedGenerator()
        self.loss = keras.losses.MeanAbsoluteError()
        self.normalizer = keras.layers.Normalization()

    def denoise(self, noisy_images, noise_rates, signal_rates):
        pred_noise_masks = self.denoising_model([noisy_images, noise_rates])
        pred_images = (noisy_images - noise_rates * pred_noise_masks) / signal_rates
        return pred_images, pred_noise_masks"""),
            ("md",
             "**Mean absolute error, not mean squared.** The noise mask is "
             "normally distributed; squared error would let a few extreme pixels "
             "dominate the gradient.\n\n"
             "The `denoise` arithmetic is the exact inverse of the mixing "
             "formula: `noisy = signal * image + noise * mask`, so "
             "`image = (noisy − noise * mask) / signal`."),

            ("h2", "The training step"),
            ("py", """class DiffusionModel(DiffusionModel):     # extend the class above
    def call(self, images):
        images = self.normalizer(images)
        noise_masks = keras.random.normal(
            (batch_size, self.image_size, self.image_size, 3),
            seed=self.seed_generator)
        diffusion_times = keras.random.uniform(
            (batch_size, 1, 1, 1), minval=0.0, maxval=1.0,
            seed=self.seed_generator)
        noise_rates, signal_rates = diffusion_schedule(diffusion_times)
        noisy_images = signal_rates * images + noise_rates * noise_masks
        pred_images, pred_noise_masks = self.denoise(
            noisy_images, noise_rates, signal_rates)
        return pred_images, pred_noise_masks, noise_masks

    def compute_loss(self, x, y, y_pred, sample_weight=None, training=True):
        _, pred_noise_masks, noise_masks = y_pred
        return self.loss(noise_masks, pred_noise_masks)"""),
            ("md",
             "Five operations: normalize, sample **random** diffusion times, "
             "compute the rates, add noise, denoise. The loss is one "
             "comparison — **all the difficulty is in the forward pass.**\n\n"
             "Random times matter: the model will be called at every point of "
             "the schedule during generation, so it must be trained across the "
             "full spectrum."),

            ("h2", "Generation"),
            ("py", """class DiffusionModel(DiffusionModel):
    def generate(self, num_images, diffusion_steps):
        noisy_images = keras.random.normal(
            (num_images, self.image_size, self.image_size, 3),
            seed=self.seed_generator)
        step_size = 1.0 / diffusion_steps
        for step in range(diffusion_steps):
            diffusion_times = ops.ones((num_images, 1, 1, 1)) - step * step_size
            noise_rates, signal_rates = diffusion_schedule(diffusion_times)
            pred_images, pred_noises = self.denoise(
                noisy_images, noise_rates, signal_rates)
            next_times = diffusion_times - step_size
            next_noise_rates, next_signal_rates = diffusion_schedule(next_times)
            noisy_images = (next_signal_rates * pred_images
                            + next_noise_rates * pred_noises)
        images = (self.normalizer.mean
                  + pred_images * self.normalizer.variance ** 0.5)
        return ops.clip(images, 0.0, 255.0)"""),
            ("md",
             "The surprising part: the model predicts the **whole** clean image "
             "at every step, and we then **deliberately add back** the noise "
             "appropriate to the next time index. Each iteration undoes slightly "
             "more than the last.\n\n"
             "`diffusion_steps` is a **generation-time** parameter — the same "
             "weights sample in 5 steps or 50, trading quality for speed."),

            ("h2", "A callback, because there is no metric"),
            ("py", """class VisualizationCallback(keras.callbacks.Callback):
    def __init__(self, diffusion_steps=20, num_rows=3, num_cols=6):
        self.diffusion_steps = diffusion_steps
        self.num_rows, self.num_cols = num_rows, num_cols

    def on_epoch_end(self, epoch=None, logs=None):
        generated = self.model.generate(
            num_images=self.num_rows * self.num_cols,
            diffusion_steps=self.diffusion_steps)
        fig, axes = plt.subplots(self.num_rows, self.num_cols,
                                 figsize=(self.num_cols * 2, self.num_rows * 2))
        for ax, im in zip(axes.ravel(), generated):
            ax.imshow(ops.convert_to_numpy(im).astype("uint8")); ax.axis("off")
        plt.suptitle(f"epoch {epoch}"); plt.tight_layout(); plt.show()
        plt.close()"""),
            ("md",
             "We have no proper metric for image quality, so the practical "
             "answer is to look. Chapter 7's callback API, doing something it "
             "was not obviously designed for."),

            ("h2", "Training"),
            ("py", """model = DiffusionModel(image_size, widths=[32, 64, 96, 128],
                       block_depth=2)
model.normalizer.adapt(dataset)          # DO NOT FORGET THIS

model.compile(
    optimizer=keras.optimizers.AdamW(
        learning_rate=keras.optimizers.schedules.InverseTimeDecay(
            initial_learning_rate=1e-3, decay_steps=1000, decay_rate=0.1),
        use_ema=True,
        ema_overwrite_frequency=100,
    ),
)

model.fit(
    dataset,
    epochs=100,
    callbacks=[
        VisualizationCallback(),
        keras.callbacks.ModelCheckpoint("diffusion_model.weights.h5",
                                        save_weights_only=True,
                                        save_best_only=True),
    ],
    verbose=2,
)"""),
            ("warn",
             "`model.normalizer.adapt(dataset)`.** Forget it and the noise and "
             "the images live on different scales; nothing works, and there is "
             "no error message.\n\n"
             "On Colab you may hit *\"Buffered data was truncated\"* because the "
             "logs contain images — chain five `fit(..., epochs=20)` calls in "
             "five cells instead."),

            ("h2", "Two optimizer settings, and what they do"),
            ("md",
             "**Learning rate decay** — `InverseTimeDecay` reduces the rate "
             "through training.\n\n"
             "**Exponential moving average** (Polyak averaging) — keep a running "
             "average of the weights and overwrite with it every 100 batches. "
             "Helps when the loss landscape is noisy, which a generative "
             "objective's is.\n\n"
             "Neither changes what the model can represent. Both change **which "
             "minimum it settles into**, and for a generative model that is the "
             "difference between plausible flowers and coloured smears."),

            ("h2", "Sampling at different step counts"),
            ("py", """model.load_weights("diffusion_model.weights.h5")

fig, axes = plt.subplots(1, 5, figsize=(16, 3.4))
for ax, steps in zip(axes, [3, 5, 10, 20, 50]):
    im = model.generate(num_images=1, diffusion_steps=steps)[0]
    ax.imshow(ops.convert_to_numpy(im).astype("uint8"))
    ax.set_title(f"{steps} steps"); ax.axis("off")
plt.suptitle("Same weights; only the number of denoising steps changes", y=1.04)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Three steps gives a blurred impression; fifty gives a sharp image. "
             "**The quality-versus-latency dial in a production image generator "
             "is exactly this parameter.**"),
        ],
        "takeaways": [
            "Five operations per training step; the loss is one comparison, and "
            "diffusion times must be sampled randomly.",
            "Generation predicts the clean image and then **re-noises** to the "
            "next schedule point.",
            "`normalizer.adapt()` is not optional and fails silently.",
            "`diffusion_steps` is the quality-versus-latency dial, chosen at "
            "generation time.",
        ],
    },

    {
        "file": "05_stable_diffusion_latent_walk.ipynb",
        "title": "Stable Diffusion, and a walk between two prompts",
        "lede": "A pretrained text-to-image model, negative prompts, and the slerp "
                "interpolation that is the best visual argument in the book for what a "
                "neural network is.",
        "needs": "GPU with 12 GB+ · large download",
        "section": "03 — Text-to-image models",
        "cells": [
            ("h2", "Loading it"),
            ("py", """import keras
import keras_hub

height, width = 512, 512
task = keras_hub.models.TextToImage.from_preset(
    "stable_diffusion_3_medium",
    image_shape=(height, width, 3),
    dtype="float16",
)
print(type(task).__name__)"""),
            ("md",
             "Like `CausalLM` in chapter 16, `TextToImage` is a high-level task "
             "class wrapping tokenization and the whole diffusion loop into one "
             "`generate()` call. `dtype=\"float16\"` halves the memory — chapter "
             "18 explains what that costs."),

            ("h2", "Generating"),
            ("py", """import matplotlib.pyplot as plt
import numpy as np

prompt = "A NASA astronaut riding an origami elephant in New York City"
image = task.generate(prompt)

plt.figure(figsize=(7, 7))
plt.imshow(image); plt.axis("off"); plt.title(prompt, fontsize=10)
plt.show()"""),
            ("md",
             "Look closely and you will find artifacts — the book's example has "
             "an elephant with duplicated tusks. **Two causes, and only one is "
             "fixable.**\n\n"
             "Drawing a human in a space suit on a paper elephant needs anatomy "
             "and physics the model lacks. But we are also using the "
             "**smallest** Stable Diffusion 3 release, about 3 billion "
             "parameters; the 9-billion version produces substantially fewer "
             "artifacts."),

            ("h2", "Negative prompts"),
            ("py", """fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6.6))
a1.imshow(task.generate(prompt)); a1.set_title("prompt only"); a1.axis("off")
a2.imshow(task.generate({"prompts": prompt,
                         "negative_prompts": "blue color"}))
a2.set_title('negative prompt: "blue color"'); a2.axis("off")
plt.tight_layout(); plt.show()"""),
            ("md",
             "There is nothing magic here. Train on **triplets** — "
             "`(image, positive_prompt, negative_prompt)` where the negative is "
             "words that do *not* describe the image — and the denoiser learns "
             "to move toward one and away from the other.\n\n"
             "**A control surface built entirely out of how the training data "
             "was labelled.**"),

            ("h2", "Watching the denoising happen"),
            ("py", """from PIL import Image

def display(images):
    return Image.fromarray(np.concatenate(images, axis=1))

steps = [5, 10, 15, 20, 25]
imgs = [task.generate(prompt, num_steps=s) for s in steps]

fig, axes = plt.subplots(1, len(steps), figsize=(18, 4))
for ax, im, s in zip(axes, imgs, steps):
    ax.imshow(im); ax.set_title(f"{s} steps"); ax.axis("off")
plt.tight_layout(); plt.show()"""),
            ("md",
             "**The same weights throughout** — only the number of times they "
             "were applied changed. Exactly the parameter from notebook 04, "
             "exposed on a production model."),

            ("h2", "Taking generate() apart"),
            ("py", """from keras import random, ops

def get_text_embeddings(prompt):
    token_ids = task.preprocessor.generate_preprocess([prompt])
    negative_token_ids = task.preprocessor.generate_preprocess([""])
    return task.backbone.encode_text_step(token_ids, negative_token_ids)

def denoise_with_text_embeddings(embeddings, num_steps=28, guidance_scale=7.0):
    latents = random.normal((1, height // 8, width // 8, 16))
    for step in range(num_steps):
        latents = task.backbone.denoise_step(
            latents, embeddings, step, num_steps, guidance_scale)
    return task.backbone.decode_step(latents)[0]

def scale_output(x):
    x = ops.convert_to_numpy(x)
    x = np.clip((x + 1.0) / 2.0, 0.0, 1.0)
    return np.round(x * 255.0).astype("uint8")

embeddings = get_text_embeddings(prompt)
print("latent shape:", (1, height // 8, width // 8, 16))
print("Stable Diffusion denoises in a COMPRESSED latent space and")
print("decodes to pixels only at the end -- which is what makes")
print("512x512 affordable.")"""),

            ("h2", "Four tensors, not one"),
            ("py", """print([tuple(np.array(x).shape) for x in embeddings])
print()
print("The authors pass BOTH the final embedded vector AND the last")
print("representation of the whole token sequence, for both the positive")
print("and the negative prompt:")
print("  [0] positive prompt's encoder sequence  (1, 154, 4096)")
print("  [1] negative prompt's encoder sequence  (1, 154, 4096)")
print("  [2] positive prompt's encoder vector    (1, 2048)")
print("  [3] negative prompt's encoder vector    (1, 2048)")"""),

            ("h2", "Spherical interpolation, and why not linear"),
            ("py", """def slerp(t, v1, v2):
    v1, v2 = ops.cast(v1, "float32"), ops.cast(v2, "float32")
    v1_norm = ops.linalg.norm(ops.ravel(v1))
    v2_norm = ops.linalg.norm(ops.ravel(v2))
    dot = ops.sum(v1 * v2 / (v1_norm * v2_norm))
    theta_0 = ops.arccos(dot)
    sin_theta_0 = ops.sin(theta_0)
    theta_t = theta_0 * t
    sin_theta_t = ops.sin(theta_t)
    s0 = ops.sin(theta_0 - theta_t) / sin_theta_0
    s1 = sin_theta_t / sin_theta_0
    return s0 * v1 + s1 * v2

# Why it matters: linear interpolation shrinks the norm.
a = np.random.normal(size=2048).astype("float32")
b = np.random.normal(size=2048).astype("float32")
lin = [(1-t) * a + t * b for t in np.linspace(0, 1, 9)]
sph = [np.array(slerp(float(t), a, b)) for t in np.linspace(0, 1, 9)]

plt.figure(figsize=(6.5, 4))
plt.plot(np.linspace(0, 1, 9), [np.linalg.norm(v) for v in lin], "o-",
         label="linear")
plt.plot(np.linspace(0, 1, 9), [np.linalg.norm(v) for v in sph], "s-",
         label="spherical")
plt.xlabel("t"); plt.ylabel("vector norm"); plt.legend()
plt.title("Linear interpolation cuts through the inside of the sphere")
plt.show()"""),
            ("md",
             "**The midpoint of a linear interpolation has a smaller norm than "
             "either endpoint** — it has left the surface. The text manifold is "
             "not actually spherical, but it is a smooth surface of vectors with "
             "roughly the same magnitude, and interpolating as if on a sphere is "
             "a much better approximation than as if on a line."),

            ("h2", "The walk"),
            ("py", """def interpolate_text_embeddings(e1, e2, start=0, stop=1, num=10):
    out = []
    for t in np.linspace(start, stop, num):
        out.append((slerp(float(t), e1[0], e2[0]),
                    e1[1],
                    slerp(float(t), e1[2], e2[2]),
                    e1[3]))
    return out

prompt1 = "A friendly dog looking up in a field of flowers"
prompt2 = ("A horrifying, tentacled creature hovering over a field of flowers")

e1 = get_text_embeddings(prompt1)
e2 = get_text_embeddings(prompt2)

images = []
for et in interpolate_text_embeddings(e1, e2, start=0.5, stop=0.6, num=9):
    images.append(scale_output(denoise_with_text_embeddings(et)))

fig, axes = plt.subplots(1, 9, figsize=(20, 2.6))
for ax, im in zip(axes, images):
    ax.imshow(im); ax.axis("off")
plt.suptitle("Nine images across one tenth of the path between two prompts",
             y=1.1)
plt.tight_layout(); plt.show()"""),
            ("md",
             "The walk runs from **0.5 to 0.6** out of [0, 1] — zoomed into the "
             "middle, right where the morph becomes visually obvious.\n\n"
             "> This might feel like magic the first time you try it, but there's "
             "nothing magic about it — **interpolation is fundamental to the way "
             "deep neural networks learn.**\n\n"
             "Chapter 15 argued this algebraically about embedding spaces. Here "
             "it is, frame by frame. **Same claim, two proofs** — and it is the "
             "note the book chooses to end its modelling on."),
        ],
        "takeaways": [
            "Stable Diffusion denoises in a compressed latent space and decodes "
            "at the end.",
            "Negative prompts are a control surface built from how the training "
            "data was labelled.",
            "Slerp stays on the manifold; linear interpolation cuts through the "
            "inside and loses meaning.",
            "**Deep networks are interpolation machines**, and this walk is the "
            "clearest picture of it in the course.",
        ],
    },
]
