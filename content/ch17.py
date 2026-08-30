# -*- coding: utf-8 -*-
"""Chapter 17 — Image generation.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 17
(pp. 508-537), read from the book PDF.

Latent spaces of images, built two ways. A variational autoencoder makes the
space continuous by construction; a diffusion model reaches the same place by
denoising in a loop. Then Stable Diffusion, and a walk between two prompts that
is the best visual argument in the book for what a neural network actually is.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_LATENT = """
flowchart LR
  L["<b>Latent image space</b><br/><small>low-dimensional<br/>vector space</small>"]
  P["A point<br/><small>a vector</small>"]
  D["<b>Decoder / generator</b>"]
  I["A valid image<br/><small>that has never<br/>been seen before</small>"]
  L --> P --> D --> I
"""

MMD_T2I = """
flowchart LR
  T["Text prompt<br/><small>&quot;horse riding a bike<br/>on the moon&quot;</small>"]
  TE["<b>Text encoder</b>"]
  LS["<b>Latent text/image space</b>"]
  ID["<b>Image decoder</b>"]
  IM["Generated image"]
  T --> TE --> LS --> ID --> IM
"""

MMD_AUTOENCODER = """
flowchart LR
  X["Original input<br/><small>x</small>"]
  E["<b>Encoder</b>"]
  C["Compressed<br/>representation<br/><small>the code</small>"]
  D["<b>Decoder</b>"]
  Y["Reconstructed input<br/><small>x'</small>"]
  X --> E --> C --> D --> Y
  X -. "is also the target" .-> Y
"""

MMD_VAE = """
flowchart LR
  I["Input image"]
  E["<b>Encoder</b>"]
  M["z_mean<br/><small>and z_log_var</small>"]
  S["<b>Sample</b><br/><small>z = mean + exp(0.5 * log_var) * epsilon</small>"]
  D["<b>Decoder</b>"]
  R["Reconstructed image"]
  I --> E --> M --> S --> D --> R
"""

MMD_VAE_LOSS = """
flowchart TB
  T["<b>Two losses, added</b>"]
  R["<b>Reconstruction loss</b><br/><small>binary crossentropy</small><br/>forces the decoded sample<br/>to match the input"]
  K["<b>Regularization loss</b><br/><small>Kullback-Leibler divergence</small><br/>nudges the encoder output<br/>toward a normal distribution<br/>centred on zero"]
  E["A latent space that is<br/><b>continuous and well-rounded</b>"]
  T --> R --> E
  T --> K --> E
"""

MMD_DIFFUSION_IDEA = """
flowchart TB
  A["An autoencoder can remove<br/><b>a small amount</b> of noise"]
  B["Repeat it in a loop to remove<br/><b>a large amount</b> of noise"]
  C["Could you denoise an image<br/>made of <b>pure noise</b>?"]
  D["<b>Yes.</b><br/>New images, hallucinated<br/>out of nothing"]
  A --> B --> C --> D
"""

MMD_REVERSE_DIFFUSION = """
flowchart LR
  N["t = 1.0<br/><b>Pure noise</b><br/><small>max noise, min signal</small>"]
  A["t = 0.75"]
  B["t = 0.5"]
  C["t = 0.25"]
  I["t = 0.0<br/><b>An image</b><br/><small>min noise, max signal</small>"]
  N --> A --> B --> C --> I
"""

MMD_UNET = """
flowchart TB
  IN["<b>Two inputs</b><br/><small>noisy image 128x128<br/>+ noise rate</small>"]
  DOWN["<b>Downsampling stage</b><br/><small>128 -&gt; 64 -&gt; 32 -&gt; 16<br/>widths 32, 64, 96</small>"]
  MID["<b>Middle stage</b><br/><small>16x16, constant size<br/>width 128</small>"]
  UP["<b>Upsampling stage</b><br/><small>16 -&gt; 32 -&gt; 64 -&gt; 128<br/>widths 96, 64, 32</small>"]
  OUT["<b>Predicted noise mask</b><br/><small>not a denoised image</small>"]
  IN --> DOWN --> MID --> UP --> OUT
  DOWN -. "concatenative skip connections<br/>preserve image detail" .-> UP
"""

MMD_TRAIN_STEP = """
flowchart TB
  A["<b>1.</b> Normalize the images"]
  B["<b>2.</b> Sample random<br/>diffusion times<br/><small>the full spectrum, 0 to 1</small>"]
  C["<b>3.</b> Compute noise rates<br/>and signal rates<br/><small>from the schedule</small>"]
  D["<b>4.</b> Add noise<br/><small>signal * image + noise * mask</small>"]
  E["<b>5.</b> Denoise"]
  F["Loss = mean absolute error<br/>between the <b>real</b> noise mask<br/>and the <b>predicted</b> one"]
  A --> B --> C --> D --> E --> F
"""

MMD_GENERATE = """
flowchart TB
  N["Start from pure noise<br/><small>diffusion_times = 1.0</small>"]
  D["<b>denoise()</b><br/><small>predict the noise mask,<br/>subtract it</small>"]
  S["Step forward:<br/>t = t - 1/diffusion_steps"]
  R["Re-noise to the<br/><b>next</b> schedule point"]
  O["Denormalize to [0, 255]"]
  N --> D --> S --> R
  R -. "loop diffusion_steps times" .-> D
  R --> O
"""

MMD_T2I_TRAIN = """
flowchart TB
  P["Prompt<br/><small>a short description<br/>of the image</small>"]
  TE["<b>Pretrained text encoder</b><br/><small>a Transformer encoder,<br/>like RoBERTa</small>"]
  EMB["Text embeddings"]
  NI["Noisy image"]
  DN["<b>Denoising model</b><br/><small>two inputs now</small>"]
  OUT["Predicted noise mask"]
  P --> TE --> EMB --> DN
  NI --> DN --> OUT
"""

MMD_T2I_STEPS = """
flowchart LR
  A["<b>1. Encode</b><br/><small>tokenize the prompt,<br/>embed it</small>"]
  B["<b>2. Denoise</b><br/><small>pure noise to latents,<br/>conditioned on the text</small>"]
  C["<b>3. Decode and scale</b><br/><small>[-1, 1] back to [0, 255]</small>"]
  A --> B --> C
"""

MMD_SLERP = """
flowchart TB
  M["The text manifold<br/><small>smooth, all vectors of<br/>roughly the same magnitude</small>"]
  L["<b>Linear interpolation</b><br/><small>cuts through the inside<br/>of the sphere</small>"]
  S["<b>Spherical interpolation</b><br/><small>stays on the surface</small>"]
  B["Off the manifold:<br/>embeddings lose meaning<br/>for the denoiser"]
  G["On the manifold:<br/>every intermediate point<br/>is a meaningful prompt"]
  M --> L --> B
  M --> S --> G
"""

NB = ["01_vae_on_mnist.ipynb", "02_vae_latent_space_grid.ipynb",
      "03_diffusion_unet_and_schedule.ipynb", "04_training_the_flower_diffuser.ipynb",
      "05_stable_diffusion_latent_walk.ipynb"]

DECK = {
    "id": "ch17",
    "kind": "chapter",
    "number": 17,
    "title": "Image Generation",
    "subtitle": "Two ways to build a latent space of images — one by construction, "
                "one by denoising in a loop — and a walk between two prompts that "
                "shows what a neural network really is.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 17",
    "source_url": chapter_url(17),
    "duration": "3.5 hours (3 sessions)",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(17, local_notebooks=NB),
    "objectives": [
        "Explain what a **latent space of images** is, and why sampling from one "
        "produces images nobody has drawn.",
        "Describe a **classical autoencoder** and say why its latent space is not "
        "useful for generation.",
        "Build a **VAE**: encoder to a mean and variance, a sampling layer, a "
        "decoder — and both halves of its loss.",
        "Customise training with **compute_loss()** rather than train_step(), and "
        "say why that keeps the code backend-agnostic.",
        "Explain **reverse diffusion** as a denoising autoencoder in a loop, and "
        "define diffusion time and the diffusion schedule.",
        "Build a **U-Net denoiser** that predicts a noise mask, and train it on the "
        "Oxford Flowers dataset.",
        "Use a pretrained **Stable Diffusion** text-to-image model, with negative "
        "prompts and a controllable step count.",
        "Interpolate between two prompts with **slerp**, and explain why spherical "
        "interpolation beats linear.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "Latent spaces of images",
         "lead": "The one idea underneath every image generator."},

        {
            "type": "slide",
            "kicker": "Section 17.1.1",
            "title": "A space where every point is a valid image",
            "blocks": [
                {"t": "lead", "md": "The key idea of image generation: develop a "
                                    "**low-dimensional latent space** — a vector space, like "
                                    "everything else in deep learning — in which any point maps "
                                    "to an image that looks like the real thing."},
                {"t": "p", "md": "The module that realises the mapping, taking a latent point "
                                 "and outputting a grid of pixels, is called a **generator**, or "
                                 "sometimes a **decoder**."},
                {"t": "mmd", "id": "ch17-latent", "src": MMD_LATENT,
                 "cap": "Figure 17.1 — once the space is learned, sample from it and decode."},
                {"t": "p", "md": "What comes out are the ==in-betweens of the training images==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.1",
            "title": "Add text conditioning and you get a brush",
            "blocks": [
                {"t": "p", "md": "**Text conditioning** maps a space of natural-language prompts "
                                 "into the latent space, giving language-guided image "
                                 "generation. This category is called **text-to-image models**."},
                {"t": "mmd", "id": "ch17-t2i", "src": MMD_T2I,
                 "cap": "Figure 17.2 — a prompt lands somewhere in the joint space, and the "
                        "decoder renders it."},
                {"t": "p", "md": "Interpolating between many training images lets such models "
                                 "generate **infinite combinations of visual concepts**, "
                                 "including many nobody had explicitly come up with. A horse "
                                 "riding a bike on the moon? You got it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.1 · the honest caveat",
            "title": "The latent space does not model the physical world",
            "blocks": [
                {"t": "p", "md": "Like every deep learning model, the latent space encodes no "
                                 "consistent model of physics. You will occasionally see hands "
                                 "with extra fingers, incoherent lighting, garbled objects. "
                                 "Coherence is an area of active research."},
                {"t": "band", "md": "Despite having seen tens of thousands of images of people "
                                    "riding bikes, the model does not understand in a human "
                                    "sense what riding a bike *means* — pedalling, steering, "
                                    "balance. Which is why your horse is ==unlikely to be "
                                    "depicted pedalling with its hind legs== the way a human "
                                    "artist would draw it.", "style": "amber"},
                {"t": "p", "md": "This is chapter 15's interpolation argument, arriving in a "
                                 "different modality. **Nothing about pixels changes it.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.1 · the landscape",
            "title": "Three families, and why one is missing",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🌫", "h": "Diffusion models", "style": "accent",
                     "p": "The architecture behind **nearly all commercial image generation "
                          "services today**. Section 17.2."},
                    {"ico": "🎛", "h": "Variational autoencoders", "style": "accent",
                     "p": "Highly structured, controllable latent spaces. Not the first choice "
                          "for fidelity, but still in use. Section 17.1."},
                    {"ico": "⚔", "h": "GANs", "style": "",
                     "p": "Covered in previous editions of this book. They have **gradually "
                          "fallen out of fashion** and been all but replaced by diffusion."},
                ]},
                {"t": "p", "md": "Note also that none of this is image-specific. You could "
                                 "develop latent spaces of **sound or music** with the same "
                                 "models — pictures are simply where the most interesting "
                                 "results have been obtained so far."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "Variational autoencoders",
         "lead": "A little statistical magic that forces a latent space to be continuous."},

        {
            "type": "slide",
            "kicker": "Section 17.1.2",
            "title": "Start with the classical autoencoder",
            "blocks": [
                {"t": "p", "md": "An autoencoder maps an image to a latent vector space via an "
                                 "**encoder**, and decodes it back to the same dimensions via a "
                                 "**decoder**. It is trained with the input images as targets — "
                                 "it learns to reconstruct its own input."},
                {"t": "mmd", "id": "ch17-autoencoder", "src": MMD_AUTOENCODER,
                 "cap": "Figure 17.3 — the target is the input. This is self-supervised learning."},
                {"t": "p", "md": "By constraining the **code** — most commonly to be low "
                                 "dimensional and sparse — the encoder becomes a way of "
                                 "compressing the input into fewer bits."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.2",
            "title": "And note that classical autoencoders do not work well",
            "blocks": [
                {"t": "lead", "md": "In practice they lead to latent spaces that are neither "
                                    "useful nor nicely structured. **They are not much good at "
                                    "compression either.** For these reasons they have largely "
                                    "fallen out of fashion."},
                {"t": "p", "md": "VAEs augment the autoencoder with a little statistical magic "
                                 "that forces it to learn **continuous, highly structured** "
                                 "latent spaces — and that turns out to be a powerful tool for "
                                 "image generation."},
                {"t": "p", "md": "VAEs were discovered simultaneously by **Kingma and Welling** "
                                 "in December 2013 and by **Rezende, Mohamed, and Wierstra** in "
                                 "January 2014. They mix deep learning with Bayesian inference, "
                                 "and remain in use in research a decade later."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.2 · the mechanism",
            "title": "Encode to a distribution, not to a point",
            "blocks": [
                {"t": "p", "md": "Instead of compressing an input into a **fixed code**, a VAE "
                                 "turns the image into the parameters of a statistical "
                                 "distribution: a **mean** and a **variance**."},
                {"t": "p", "md": "The assumption is that the image was generated by a statistical "
                                 "process, and that the randomness of that process should be "
                                 "accounted for during encoding and decoding."},
                {"t": "mmd", "id": "ch17-vae", "src": MMD_VAE,
                 "cap": "Figure 17.4 — the encoder outputs two vectors; a point is sampled from "
                        "the distribution they define; the decoder reconstructs from that point."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.2 · three steps",
            "title": "The mechanism, stated precisely",
            "blocks": [
                {"t": "steps", "items": [
                    "An **encoder** turns `input_img` into two parameters in the latent space, "
                    "`z_mean` and `z_log_variance`.",
                    "A point is **randomly sampled** from the latent normal distribution assumed "
                    "to have generated the image: "
                    "`z = z_mean + exp(z_log_variance) * epsilon`, where `epsilon` is a random "
                    "tensor of small values.",
                    "A **decoder** maps that point back to the original input image.",
                ]},
                {"t": "band", "md": "Because `epsilon` is random, **every point close to where "
                                    "`input_img` was encoded decodes to something similar to "
                                    "`input_img`.** That is what forces the latent space to be "
                                    "==continuously meaningful==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.2 · why continuity matters",
            "title": "Continuity plus low dimensionality gives you concept vectors",
            "blocks": [
                {"t": "p", "md": "Any two close points in the latent space decode to highly "
                                 "similar images. Combine that continuity with a **low "
                                 "dimensional** space and every direction is forced to encode a "
                                 "meaningful axis of variation in the data."},
                {"t": "p", "md": "The result is a very structured space, highly suitable to "
                                 "manipulation via **concept vectors** — the same *word "
                                 "arithmetic* idea from chapter 15, now over faces and objects "
                                 "rather than words."},
                {"t": "p", "md": "This is why VAEs remain relevant even where diffusion produces "
                                 "better images: when **interpretability, control over the "
                                 "latent space, and reconstruction** matter, they are still the "
                                 "right tool."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.2 · the loss",
            "title": "Two losses, pulling in different directions",
            "blocks": [
                {"t": "mmd", "id": "ch17-vae-loss", "src": MMD_VAE_LOSS,
                 "cap": "Reconstruction alone would collapse to a classical autoencoder; "
                        "regularization alone would ignore the data."},
                {"t": "p", "md": "The regularization term is the **Kullback-Leibler divergence**, "
                                 "which nudges the distribution of the encoder output toward a "
                                 "well-rounded normal distribution centred on 0 — a sensible "
                                 "prior about the structure of the space being modelled."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · listing 17.1",
            "title": "The encoder: a ConvNet with two heads",
            "blocks": [
                {"t": "p", "md": "A simple ConvNet mapping a 28 × 28 MNIST digit to two "
                                 "two-dimensional vectors. Note the **strides** for "
                                 "downsampling, not max pooling."},
                {"t": "code", "lang": "python", "file": "listing 17.1", "src": """import keras
from keras import layers

latent_dim = 2

image_inputs = keras.Input(shape=(28, 28, 1))
x = layers.Conv2D(32, 3, activation="relu", strides=2, padding="same")(
    image_inputs
)
x = layers.Conv2D(64, 3, activation="relu", strides=2, padding="same")(x)
x = layers.Flatten()(x)
x = layers.Dense(16, activation="relu")(x)
z_mean = layers.Dense(latent_dim, name="z_mean")(x)
z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)
encoder = keras.Model(image_inputs, [z_mean, z_log_var], name="encoder")"""},
                {"t": "p", "md": "Strides are preferable to max pooling for **any model that "
                                 "cares where things are in the image** — as chapter 11's "
                                 "segmentation example did, and as this one does, since the "
                                 "encoding must support reconstructing a valid image."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3",
            "title": "Sixty-nine thousand parameters, and a two-dimensional output",
            "blocks": [
                {"t": "out", "src": """>>> encoder.summary()
Model: "encoder"
│ input_layer (InputLayer) │ (None, 28, 28, 1)  │      0 │
│ conv2d (Conv2D)          │ (None, 14, 14, 32) │    320 │
│ conv2d_1 (Conv2D)        │ (None, 7, 7, 64)   │ 18,496 │
│ flatten (Flatten)        │ (None, 3136)       │      0 │
│ dense (Dense)            │ (None, 16)         │ 50,192 │
│ z_mean (Dense)           │ (None, 2)          │     34 │
│ z_log_var (Dense)        │ (None, 2)          │     34 │
 Total params: 69,076 (269.83 KB)"""},
                {"t": "p", "md": "The whole of MNIST is being pushed through a **two-number** "
                                 "bottleneck. That is deliberate: a 2D latent space is one we "
                                 "can plot in full, which is the point of this example."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · listing 17.2",
            "title": "The sampling layer",
            "blocks": [
                {"t": "p", "md": "One custom layer applies the VAE sampling formula. It needs a "
                                 "seed generator to use `keras.random` inside `call()`."},
                {"t": "code", "lang": "python", "file": "listing 17.2", "src": """from keras import ops

class Sampler(keras.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seed_generator = keras.random.SeedGenerator()
        self.built = True

    def call(self, z_mean, z_log_var):
        batch_size = ops.shape(z_mean)[0]
        z_size = ops.shape(z_mean)[1]
        epsilon = keras.random.normal(
            (batch_size, z_size), seed=self.seed_generator
        )
        return z_mean + ops.exp(0.5 * z_log_var) * epsilon"""},
                {"t": "p", "md": "`exp(0.5 * z_log_var)` converts a **log variance** to a "
                                 "standard deviation. Predicting the log rather than the "
                                 "variance itself keeps the encoder's output unconstrained — it "
                                 "may be negative, and the exponential makes it positive."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · listing 17.3",
            "title": "The decoder mirrors the encoder",
            "blocks": [
                {"t": "p", "md": "Reshape the latent vector to image dimensions, then reverse "
                                 "each encoder operation with `Conv2DTranspose`."},
                {"t": "code", "lang": "python", "file": "listing 17.3", "src": """latent_inputs = keras.Input(shape=(latent_dim,))
x = layers.Dense(7 * 7 * 64, activation="relu")(latent_inputs)
x = layers.Reshape((7, 7, 64))(x)
x = layers.Conv2DTranspose(64, 3, activation="relu", strides=2, padding="same")(x)
x = layers.Conv2DTranspose(32, 3, activation="relu", strides=2, padding="same")(x)
decoder_outputs = layers.Conv2D(1, 3, activation="sigmoid", padding="same")(x)
decoder = keras.Model(latent_inputs, decoder_outputs, name="decoder")"""},
                {"t": "p", "md": "The `Dense(7 * 7 * 64)` produces exactly the number of "
                                 "coefficients the encoder's `Flatten` consumed — the "
                                 "architecture is a **mirror**, and reading it that way is the "
                                 "quickest way to check it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3",
            "title": "compute_loss() instead of train_step()",
            "blocks": [
                {"t": "p", "md": "This is the first model in the book that is **not doing "
                                 "supervised learning** — an autoencoder is self-supervised, "
                                 "using its inputs as targets. Departing from supervised "
                                 "learning normally means subclassing `Model` and writing a "
                                 "custom `train_step()`."},
                {"t": "band", "md": "But `train_step()` contents are **backend specific** — "
                                    "`GradientTape` under TensorFlow, `loss.backward()` under "
                                    "PyTorch. Overriding `compute_loss()` instead keeps the "
                                    "default `train_step()` and stays ==backend agnostic==."},
                {"t": "code", "lang": "python", "file": "the signature", "src": """compute_loss(x, y, y_pred, sample_weight=None, training=True)"""},
                {"t": "p", "md": "`x` is the input, `y` the target — **None** here, since our "
                                 "dataset has no targets — and `y_pred` is the output of "
                                 "`call()`. The method returns a scalar, and may also update "
                                 "metric state."},
            ],
            "notes": "Worth pausing on. This is a small API decision with a large practical "
                     "consequence: it is the difference between code that runs on three "
                     "backends and code that runs on one.",
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · listing 17.4",
            "title": "The VAE model: constructor",
            "blocks": [
                {"t": "p", "md": "Encoder, decoder, sampler, and two metrics to track the loss "
                                 "components separately over each epoch."},
                {"t": "code", "lang": "python", "file": "listing 17.4 - constructor", "src": """class VAE(keras.Model):
    def __init__(self, encoder, decoder, **kwargs):
        super().__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.sampler = Sampler()
        self.reconstruction_loss_tracker = keras.metrics.Mean(
            name="reconstruction_loss"
        )
        self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")

    def call(self, inputs):
        return self.encoder(inputs)"""},
                {"t": "p", "md": "Note that `call()` returns only the **encoder output** — the "
                                 "two latent parameters. Sampling and decoding happen inside the "
                                 "loss, because that is where the reconstruction is needed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · listing 17.4",
            "title": "The VAE model: the loss",
            "blocks": [
                {"t": "p", "md": "Both terms, written out. `x` is the original image; `y_pred` "
                                 "carries the latent parameters."},
                {"t": "code", "lang": "python", "file": "listing 17.4 - compute_loss", "src": """    def compute_loss(self, x, y, y_pred, sample_weight=None, training=True):
        original = x
        z_mean, z_log_var = y_pred
        reconstruction = self.decoder(self.sampler(z_mean, z_log_var))
        reconstruction_loss = ops.mean(
            ops.sum(
                keras.losses.binary_crossentropy(x, reconstruction), axis=(1, 2)
            )
        )
        kl_loss = -0.5 * (
            1 + z_log_var - ops.square(z_mean) - ops.exp(z_log_var)
        )
        total_loss = reconstruction_loss + ops.mean(kl_loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        return total_loss"""},
                {"t": "p", "md": "The reconstruction loss is **summed over the spatial "
                                 "dimensions** (axes 1 and 2) and averaged over the batch. The "
                                 "KL term is the closed-form divergence between the encoder's "
                                 "distribution and a unit normal."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · listing 17.5",
            "title": "Training with no loss and no targets",
            "blocks": [
                {"t": "p", "md": "Because `compute_loss()` already handles the loss, we pass no "
                                 "`loss` at compile time — which in turn means passing **no "
                                 "target data** to `fit()`."},
                {"t": "code", "lang": "python", "file": "listing 17.5", "src": """import numpy as np

(x_train, _), (x_test, _) = keras.datasets.mnist.load_data()
mnist_digits = np.concatenate([x_train, x_test], axis=0)
mnist_digits = np.expand_dims(mnist_digits, -1).astype("float32") / 255

vae = VAE(encoder, decoder)
vae.compile(optimizer=keras.optimizers.Adam())
vae.fit(mnist_digits, epochs=30, batch_size=128)"""},
                {"t": "p", "md": "We concatenate the training and test splits: there is no test "
                                 "set to protect here, because there is **nothing being "
                                 "evaluated against held-out labels**. We want the latent space "
                                 "to see every digit there is."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · listing 17.6",
            "title": "Walking the latent space on a grid",
            "blocks": [
                {"t": "p", "md": "With a 2D latent space we can plot the whole thing: sample "
                                 "points linearly on a grid and decode each one."},
                {"t": "code", "lang": "python", "file": "listing 17.6", "src": """import matplotlib.pyplot as plt

n = 30
digit_size = 28
figure = np.zeros((digit_size * n, digit_size * n))
grid_x = np.linspace(-1, 1, n)
grid_y = np.linspace(-1, 1, n)[::-1]

for i, yi in enumerate(grid_y):
    for j, xi in enumerate(grid_x):
        z_sample = np.array([[xi, yi]])
        x_decoded = vae.decoder.predict(z_sample)
        digit = x_decoded[0].reshape(digit_size, digit_size)
        figure[
            i * digit_size : (i + 1) * digit_size,
            j * digit_size : (j + 1) * digit_size,
        ] = digit

plt.imshow(figure, cmap="Greys_r")"""},
                {"t": "p", "md": "Nine hundred digits, none of which are in MNIST."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.1.3 · figure 17.5",
            "title": "What the grid shows",
            "blocks": [
                {"t": "lead", "md": "A **completely continuous** distribution of the different "
                                    "digit classes, with one digit morphing into another as you "
                                    "follow a path through the latent space."},
                {"t": "p", "md": "Specific directions in the space have meaning: there is a "
                                 "direction for *four-ness*, one for *one-ness*, and so on. "
                                 "Nobody labelled them. They fall out of the continuity "
                                 "constraint."},
                {"t": "band", "md": "This is the payoff for the whole VAE construction. A "
                                    "classical autoencoder's latent space would show **islands "
                                    "of digits separated by regions that decode to nothing** — "
                                    "the KL term is what fills the gaps.", "style": "amber"},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "Diffusion models",
         "lead": "A denoising autoencoder in a loop — and the architecture behind nearly "
                 "every commercial image generator today."},

        {
            "type": "slide",
            "kicker": "Section 17.2",
            "title": "Denoising is the one task autoencoders excel at",
            "blocks": [
                {"t": "p", "md": "A long-standing application of autoencoders: feed in an input "
                                 "with a small amount of noise — a low-quality JPEG, say — and "
                                 "get back a cleaned-up version."},
                {"t": "p", "md": "In the late 2010s this gave rise to successful **image "
                                 "super-resolution** models, which have shipped in every major "
                                 "smartphone camera app for years."},
                {"t": "band", "md": "These models are **not** recovering lost detail hidden in "
                                    "the input, like the *enhance* scene in *Blade Runner*. They "
                                    "are making educated guesses — ==hallucinating== a "
                                    "higher-resolution version of what you gave them."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2 · a cautionary example",
            "title": "The moon that was not there",
            "blocks": [
                {"t": "p", "md": "With some AI-enhanced cameras you can photograph something "
                                 "**vaguely moon-like** — a printout of a severely blurred moon "
                                 "image — and find a crisp picture of the moon's craters in your "
                                 "camera roll."},
                {"t": "p", "md": "A great deal of detail that simply was not present in the "
                                 "printout gets straight-up hallucinated, because the "
                                 "super-resolution model is **overfitted to moon photography**."},
                {"t": "band", "md": "So, unlike Rick Deckard, ==definitely do not use this "
                                    "technique for forensics==.", "style": "rose"},
                {"t": "p", "md": "Worth keeping for any professional audience: an enhancement "
                                 "model's output is **evidence of the model's priors**, not "
                                 "evidence about the scene."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2 · the key insight",
            "title": "If a little noise, why not all of it?",
            "blocks": [
                {"t": "mmd", "id": "ch17-diffusion-idea", "src": MMD_DIFFUSION_IDEA,
                 "cap": "The arresting idea that early denoising successes led researchers to."},
                {"t": "p", "md": "These should more accurately be called **reverse diffusion** "
                                 "models — *diffusion* refers to the forward process of "
                                 "gradually adding noise to an image until it disperses into "
                                 "nothing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2 · figure 17.7",
            "title": "Reverse diffusion, one step at a time",
            "blocks": [
                {"t": "mmd", "id": "ch17-reverse", "src": MMD_REVERSE_DIFFUSION,
                 "cap": "Figure 17.7 — turning pure noise into an image via repeated denoising."},
                {"t": "quote", "md": "*\"Every block of stone has a statue inside it and it is "
                                     "the task of the sculptor to discover it.\"* — Well, **every "
                                     "square of white noise has an image inside it, and it is "
                                     "the task of the diffusion model to discover it.**",
                 "cite": "Michelangelo, and section 17.2"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.1",
            "title": "Oxford Flowers: 8,189 images, 102 species",
            "blocks": [
                {"t": "p", "md": "A small dataset, which is what makes this example trainable in "
                                 "an afternoon."},
                {"t": "code", "lang": "python", "src": """import os

fpath = keras.utils.get_file(
    origin="https://www.robots.ox.ac.uk/~vgg/data/flowers/102/102flowers.tgz",
    extract=True,
)

batch_size = 32
image_size = 128
images_dir = os.path.join(fpath, "jpg")

dataset = keras.utils.image_dataset_from_directory(
    images_dir,
    labels=None,
    image_size=(image_size, image_size),
    crop_to_aspect_ratio=True,
)
dataset = dataset.rebatch(batch_size, drop_remainder=True)"""},
                {"t": "p", "md": "Two arguments matter. `labels=None` — we want images only. "
                                 "`crop_to_aspect_ratio=True` — resizing without it would "
                                 "**distort** the images, and distortion in the training set "
                                 "becomes distortion in everything generated."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.2",
            "title": "The denoiser predicts the noise, not the image",
            "blocks": [
                {"t": "p", "md": "The same denoising model is reused at every iteration of the "
                                 "loop, erasing a little noise each time. To make its job "
                                 "easier, we **tell it how much noise to expect** — the "
                                 "`noise_rates` input."},
                {"t": "band", "md": "And rather than outputting a denoised image, the model "
                                    "outputs a **predicted noise mask**, which we subtract from "
                                    "the input. ==Predicting what to remove is an easier target "
                                    "than predicting what remains.=="},
                {"t": "p", "md": "For the architecture we use a **U-Net** — a ConvNet originally "
                                 "developed for image segmentation, and last seen in chapter 11."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.2 · figure 17.9",
            "title": "Three stages, with skip connections across",
            "blocks": [
                {"t": "mmd", "id": "ch17-unet", "src": MMD_UNET,
                 "cap": "Figure 17.9 — a 1:1 mapping between downsampling and upsampling blocks."},
                {"t": "p", "md": "Each upsampling block is the inverse of a downsampling block, "
                                 "and **concatenative residual connections** run from each "
                                 "downsampling block to its partner. These avoid the loss of "
                                 "image detail across successive down- and upsampling."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.2",
            "title": "The residual block",
            "blocks": [
                {"t": "p", "md": "A utility applying two convolutions with a residual connection, "
                                 "projecting the shortcut with a 1 × 1 convolution when the "
                                 "widths do not match."},
                {"t": "code", "lang": "python", "src": """def residual_block(x, width):
    input_width = x.shape[3]
    if input_width == width:
        residual = x
    else:
        residual = layers.Conv2D(width, 1)(x)
    x = layers.BatchNormalization(center=False, scale=False)(x)
    x = layers.Conv2D(width, 3, padding="same", activation="swish")(x)
    x = layers.Conv2D(width, 3, padding="same")(x)
    x = x + residual
    return x"""},
                {"t": "p", "md": "This is the pattern from chapter 9, unchanged — with `swish` "
                                 "in place of `relu`, and normalization that does **not** learn "
                                 "a scale or centre, since the residual path carries those."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.2",
            "title": "The U-Net: two inputs, and the way down",
            "blocks": [
                {"t": "p", "md": "The two inputs are merged first, then the downsampling stage "
                                 "saves each block's output on a stack."},
                {"t": "code", "lang": "python", "file": "get_model - inputs and downsampling", "src": """def get_model(image_size, widths, block_depth):
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
        x = layers.AveragePooling2D(pool_size=2)(x)"""},
                {"t": "p", "md": "The scalar noise rate is **upsampled to the full image size** "
                                 "and concatenated as an extra channel — the standard way to "
                                 "feed a scalar condition to a convolutional network."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.2",
            "title": "The U-Net: the middle, and the way back up",
            "blocks": [
                {"t": "p", "md": "The upsampling loop runs the widths in reverse, popping one "
                                 "skip connection per block."},
                {"t": "code", "lang": "python", "file": "get_model - middle and upsampling", "src": """    for _ in range(block_depth):
        x = residual_block(x, widths[-1])

    for width in reversed(widths[:-1]):
        x = layers.UpSampling2D(size=2, interpolation="bilinear")(x)
        for _ in range(block_depth):
            x = layers.Concatenate()([x, skips.pop()])
            x = residual_block(x, width)

    pred_noise_masks = layers.Conv2D(3, 1, kernel_initializer="zeros")(x)
    return keras.Model([noisy_images, noise_rates], pred_noise_masks)"""},
                {"t": "p", "md": "`skips.pop()` pairs each upsampling block with its mirror on "
                                 "the way down — **last in, first out** is exactly the pairing "
                                 "the architecture diagram shows."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.2 · two details worth stealing",
            "title": "Zero initialization, and widening as you downsample",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "0️⃣", "h": "kernel_initializer=\"zeros\"", "style": "accent",
                     "p": "The last layer predicts **only zeros** after initialization — so the "
                          "model's default assumption before training is *no noise*. A "
                          "deliberately chosen, harmless starting point."},
                    {"ico": "📊", "h": "widths=[32, 64, 96, 128]", "style": "accent",
                     "p": "Layers get **wider as the feature map shrinks**, and narrower again "
                          "as it grows back. The same trade as every ConvNet in chapter 9."},
                ]},
                {"t": "p", "md": "You would instantiate with "
                                 "`get_model(image_size=128, widths=[32, 64, 96, 128], "
                                 "block_depth=2)`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.3",
            "title": "Diffusion time and the diffusion schedule",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "⏱", "h": "Diffusion time", "style": "accent",
                     "p": "The index of the current step, here a **continuous value between 1 "
                          "and 0**. 1 is maximal noise and minimal signal; 0 is almost all "
                          "signal and no noise."},
                    {"ico": "📉", "h": "Diffusion schedule", "style": "accent",
                     "p": "The relationship between the current time and how much noise and "
                          "signal are present. We use a **cosine schedule**."},
                ]},
                {"t": "p", "md": "The cosine choice is not arbitrary: it maintains the identity "
                                 "==noise_rates² + signal_rates² == 1==, so total energy stays "
                                 "constant as the mix shifts from one to the other."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.3 · listing 17.7",
            "title": "The schedule, in seven lines",
            "blocks": [
                {"t": "p", "md": "Map diffusion time to an angle, then take the cosine and sine "
                                 "of it. The Pythagorean identity does the rest."},
                {"t": "code", "lang": "python", "file": "listing 17.7", "src": """def diffusion_schedule(
    diffusion_times,
    min_signal_rate=0.02,
    max_signal_rate=0.95,
):
    start_angle = ops.cast(ops.arccos(max_signal_rate), "float32")
    end_angle = ops.cast(ops.arccos(min_signal_rate), "float32")
    diffusion_angles = start_angle + diffusion_times * (end_angle - start_angle)
    signal_rates = ops.cos(diffusion_angles)
    noise_rates = ops.sin(diffusion_angles)
    return noise_rates, signal_rates"""},
                {"t": "p", "md": "The two bounds keep the process away from its extremes: never "
                                 "quite pure signal (0.95), never quite pure noise (0.02). Both "
                                 "endpoints are numerically awkward, and neither is needed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.4",
            "title": "What the DiffusionModel needs to hold",
            "blocks": [
                {"t": "p", "md": "The denoising autoencoder is one attribute. Two more things "
                                 "are needed alongside it."},
                {"t": "bullets", "items": [
                    "**A loss function** — mean absolute error, that is "
                    "`mean(abs(real_noise_mask - predicted_noise_mask))`.",
                    "**An image normalization layer** — the noise we add has unit variance and "
                    "zero mean, so the images must be normalized the same way for their value "
                    "ranges to match.",
                ]},
                {"t": "code", "lang": "python", "src": """class DiffusionModel(keras.Model):
    def __init__(self, image_size, widths, block_depth, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.denoising_model = get_model(image_size, widths, block_depth)
        self.seed_generator = keras.random.SeedGenerator()
        self.loss = keras.losses.MeanAbsoluteError()
        self.normalizer = keras.layers.Normalization()"""},
                {"t": "p", "md": "Mean absolute error rather than mean squared error: the noise "
                                 "mask is normally distributed, and **squared error would let a "
                                 "few extreme pixels dominate** the gradient."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.4",
            "title": "The denoise method",
            "blocks": [
                {"t": "p", "md": "Call the model for a predicted noise mask, then use it to "
                                 "reconstruct the clean image — the one place the model's output "
                                 "is turned back into pixels."},
                {"t": "code", "lang": "python", "src": """    def denoise(self, noisy_images, noise_rates, signal_rates):
        pred_noise_masks = self.denoising_model([noisy_images, noise_rates])
        pred_images = (
            noisy_images - noise_rates * pred_noise_masks
        ) / signal_rates
        return pred_images, pred_noise_masks"""},
                {"t": "p", "md": "Read the arithmetic as the inverse of the mixing formula: "
                                 "`noisy = signal * image + noise * mask`, so "
                                 "`image = (noisy − noise * mask) / signal`. **Two lines that "
                                 "undo each other exactly.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.4",
            "title": "The training step, in five operations",
            "blocks": [
                {"t": "mmd", "id": "ch17-train-step", "src": MMD_TRAIN_STEP,
                 "cap": "Random diffusion times are essential: the model must be trained across "
                        "the full spectrum, because it will be called at every point of it."},
                {"t": "p", "md": "`call()` returns three things — the predicted images, the "
                                 "predicted noise masks, and the **actual** noise masks it "
                                 "applied. The last two are what `compute_loss()` compares."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.4",
            "title": "call() and compute_loss(), written out",
            "blocks": [
                {"t": "p", "md": "The same pattern as the VAE: forward pass in `call()`, "
                                 "comparison in the loss."},
                {"t": "code", "lang": "python", "src": """    def call(self, images):
        images = self.normalizer(images)
        noise_masks = keras.random.normal(
            (batch_size, self.image_size, self.image_size, 3),
            seed=self.seed_generator,
        )
        diffusion_times = keras.random.uniform(
            (batch_size, 1, 1, 1), minval=0.0, maxval=1.0,
            seed=self.seed_generator,
        )
        noise_rates, signal_rates = diffusion_schedule(diffusion_times)
        noisy_images = signal_rates * images + noise_rates * noise_masks
        pred_images, pred_noise_masks = self.denoise(
            noisy_images, noise_rates, signal_rates
        )
        return pred_images, pred_noise_masks, noise_masks

    def compute_loss(self, x, y, y_pred, sample_weight=None, training=True):
        _, pred_noise_masks, noise_masks = y_pred
        return self.loss(noise_masks, pred_noise_masks)"""},
                {"t": "p", "md": "Note how small the loss is. **All the difficulty is in the "
                                 "forward pass**, and the objective itself is one comparison."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.5",
            "title": "Generation: start from noise and walk the schedule down",
            "blocks": [
                {"t": "mmd", "id": "ch17-generate", "src": MMD_GENERATE,
                 "cap": "Each iteration denoises fully, then re-noises to the next schedule "
                        "point — a smaller step than the one just undone."},
                {"t": "p", "md": "That re-noising is the part that surprises people. The model "
                                 "predicts the **whole** clean image at every step; we then "
                                 "deliberately add back the amount of noise appropriate to the "
                                 "next time index, and ask again."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.5",
            "title": "The generation loop: one step",
            "blocks": [
                {"t": "p", "md": "Start from pure noise, then walk the schedule down one step "
                                 "at a time."},
                {"t": "code", "lang": "python", "file": "generate - the loop", "src": """    def generate(self, num_images, diffusion_steps):
        noisy_images = keras.random.normal(
            (num_images, self.image_size, self.image_size, 3),
            seed=self.seed_generator,
        )
        step_size = 1.0 / diffusion_steps
        for step in range(diffusion_steps):
            diffusion_times = ops.ones((num_images, 1, 1, 1)) - step * step_size
            noise_rates, signal_rates = diffusion_schedule(diffusion_times)
            pred_images, pred_noises = self.denoise(
                noisy_images, noise_rates, signal_rates
            )"""},
                {"t": "p", "md": "`diffusion_steps` is a **generation-time** parameter — the "
                                 "same weights sample in 5 steps or 50."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.5",
            "title": "The generation loop: re-noise and finish",
            "blocks": [
                {"t": "p", "md": "Having predicted the clean image, we deliberately add back the "
                                 "noise appropriate to the **next** time index."},
                {"t": "code", "lang": "python", "file": "generate - re-noise and denormalize", "src": """            next_diffusion_times = diffusion_times - step_size
            next_noise_rates, next_signal_rates = diffusion_schedule(
                next_diffusion_times
            )
            noisy_images = (
                next_signal_rates * pred_images + next_noise_rates * pred_noises
            )

        images = (
            self.normalizer.mean + pred_images * self.normalizer.variance**0.5
        )
        return ops.clip(images, 0.0, 255.0)"""},
                {"t": "p", "md": "The final two lines **undo the normalization** — multiply by "
                                 "the standard deviation, add the mean, clip to [0, 255]. The "
                                 "model works in normalized space throughout; only the very last "
                                 "step returns to pixels."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.6",
            "title": "There is no metric, so look at the pictures",
            "blocks": [
                {"t": "p", "md": "We have no proper metric for image quality here. The practical "
                                 "answer is a callback that generates a grid at the end of every "
                                 "epoch so you can judge for yourself."},
                {"t": "code", "lang": "python", "src": """class VisualizationCallback(keras.callbacks.Callback):
    def __init__(self, diffusion_steps=20, num_rows=3, num_cols=6):
        self.diffusion_steps = diffusion_steps
        self.num_rows = num_rows
        self.num_cols = num_cols

    def on_epoch_end(self, epoch=None, logs=None):
        generated_images = self.model.generate(
            num_images=self.num_rows * self.num_cols,
            diffusion_steps=self.diffusion_steps,
        )
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                i = row * self.num_cols + col
                plt.subplot(self.num_rows, self.num_cols, i + 1)
                img = ops.convert_to_numpy(generated_images[i]).astype("uint8")
                plt.imshow(img)
                plt.axis("off")
        plt.show()"""},
                {"t": "p", "md": "This is chapter 7's callback API doing something it was not "
                                 "obviously designed for, and doing it well."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.7",
            "title": "Two optimizer options that matter here",
            "blocks": [
                {"t": "p", "md": "We use **AdamW**, with two settings turned on to stabilise "
                                 "training and improve image quality."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📉", "h": "Learning rate decay", "style": "accent",
                     "p": "An `InverseTimeDecay` schedule gradually reduces the rate through "
                          "training."},
                    {"ico": "🔁", "h": "Exponential moving average", "style": "accent",
                     "p": "Also called **Polyak averaging**. Keep a running average of the "
                          "weights, and every 100 batches overwrite the weights with it. Helps "
                          "when the loss landscape is noisy."},
                ]},
                {"t": "code", "lang": "python", "src": """model.compile(
    optimizer=keras.optimizers.AdamW(
        learning_rate=keras.optimizers.schedules.InverseTimeDecay(
            initial_learning_rate=1e-3, decay_steps=1000, decay_rate=0.1,
        ),
        use_ema=True,
        ema_overwrite_frequency=100,
    ),
)"""},
                {"t": "p", "md": "Neither option changes what the model can represent. Both "
                                 "change **which minimum it settles into**, which for a "
                                 "generative model is the difference between plausible flowers "
                                 "and coloured smears."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.7",
            "title": "Fit it, and do not forget to adapt the normalizer",
            "blocks": [
                {"t": "p", "md": "Two lines to instantiate, one to train — and one step in "
                                 "between that is easy to skip."},
                {"t": "code", "lang": "python", "src": """model = DiffusionModel(image_size, widths=[32, 64, 96, 128], block_depth=2)
model.normalizer.adapt(dataset)

model.fit(
    dataset,
    epochs=100,
    callbacks=[
        VisualizationCallback(),
        keras.callbacks.ModelCheckpoint(
            filepath="diffusion_model.weights.h5",
            save_weights_only=True,
            save_best_only=True,
        ),
    ],
)"""},
                {"t": "band", "md": "`model.normalizer.adapt(dataset)` computes the mean and "
                                    "variance the normalization needs. **Forget it and the noise "
                                    "and the images live on different scales**, and nothing "
                                    "works — with no error message.", "style": "rose"},
                {"t": "p", "md": "100 epochs is about **90 minutes on a free Colab T4**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.2.7 · figure 17.12",
            "title": "Flowers that do not exist",
            "blocks": [
                {"t": "lead", "md": "After 100 epochs on 8,189 photographs, the model produces "
                                    "**convincing flowers**, and keeps improving if you keep "
                                    "training."},
                {"t": "p", "md": "It is worth measuring what that took against what it "
                                 "produced: a U-Net of a few million parameters, a dataset small "
                                 "enough to download over coffee, and ninety minutes of a free "
                                 "GPU."},
                {"t": "p", "md": "The next step to unlocking the real potential is **text "
                                 "conditioning** — which turns this into a model that produces "
                                 "images matching a given caption."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "04", "title": "Text-to-image models",
         "lead": "One extra input to the denoiser, and a walk through the space between "
                 "two prompts."},

        {
            "type": "slide",
            "kicker": "Section 17.3",
            "title": "Give the denoiser a second input",
            "blocks": [
                {"t": "p", "md": "Take a pretrained **text encoder** — a Transformer encoder "
                                 "like RoBERTa from chapter 15 — that maps text to vectors in a "
                                 "continuous space. Then train a diffusion model on "
                                 "**(prompt, image)** pairs."},
                {"t": "mmd", "id": "ch17-t2i-train", "src": MMD_T2I_TRAIN,
                 "cap": "The denoising model now takes noisy_images and text_embeddings."},
                {"t": "p", "md": "This gives a considerable **leg up** on the flower denoiser: "
                                 "instead of removing noise with no additional information, the "
                                 "model gets a textual representation of the final image to "
                                 "guide it."},

            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3 · listing 17.8",
            "title": "Stable Diffusion in a few lines",
            "blocks": [
                {"t": "p", "md": "We will not train one from scratch — you have all the "
                                 "ingredients, but it is expensive and slow. We use a pretrained "
                                 "model from KerasHub instead."},
                {"t": "code", "lang": "python", "file": "listing 17.8", "src": """import keras_hub

height, width = 512, 512
task = keras_hub.models.TextToImage.from_preset(
    "stable_diffusion_3_medium",
    image_shape=(height, width, 3),
    dtype="float16",
)

prompt = "A NASA astronaut riding an origami elephant in New York City"
task.generate(prompt)"""},
                {"t": "p", "md": "Like `CausalLM` last chapter, `TextToImage` is a **high-level "
                                 "task class** — it wraps tokenization and the whole diffusion "
                                 "process into one `generate()` call. `dtype=\"float16\"` is a "
                                 "memory trick explained properly in chapter 18."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3",
            "title": "What that one call is doing",
            "blocks": [
                {"t": "p", "md": "Three stages hide behind `generate()`, and we will need all "
                                 "three separately later in this section."},
                {"t": "mmd", "id": "ch17-t2i-steps", "src": MMD_T2I_STEPS,
                 "cap": "Encode the prompt, denoise conditioned on it, rescale the output."},
                {"t": "p", "md": "The middle stage is **exactly the flower model** — the same "
                                 "loop over a diffusion schedule, with one extra input to the "
                                 "denoiser. Everything the previous section built is still here."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3 · negative prompts",
            "title": "Steering away from something",
            "blocks": [
                {"t": "p", "md": "Stable Diffusion adds a second **negative prompt** input, used "
                                 "to steer the process away from certain text. There is nothing "
                                 "magic about it."},
                {"t": "p", "md": "Train on **triplets** — `(image, positive_prompt, "
                                 "negative_prompt)`, where the positive describes the image and "
                                 "the negative is a series of words that do not. Feed both "
                                 "embeddings to the denoiser and it learns to move toward one "
                                 "and away from the other."},
                {"t": "code", "lang": "python", "src": """task.generate(
    {
        "prompts": prompt,
        "negative_prompts": "blue color",
    }
)"""},
                {"t": "p", "md": "The result is the same scene with the blue removed — a control "
                                 "surface built entirely out of **how the training data was "
                                 "labelled**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3 · sidebar",
            "title": "About those duplicated tusks",
            "blocks": [
                {"t": "p", "md": "Look closely at the output and you will find visual artifacts "
                                 "— in the book's example, an elephant with duplicated tusks. "
                                 "Two separate causes, and only one is fixable."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🧠", "h": "Unavoidable", "style": "warn",
                     "p": "Drawing a human in a space suit sitting on a paper elephant would "
                          "require understanding **anatomy and physics** the model lacks. It "
                          "interpolates from training data with no real understanding of the "
                          "objects."},
                    {"ico": "📏", "h": "Easily fixable", "style": "good",
                     "p": "We are using the **smallest** Stable Diffusion 3 release — about 3 "
                          "billion parameters. A 9-billion-parameter version produces "
                          "substantially fewer artifacts. It is omitted only to keep the "
                          "example accessible."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3 · figure 17.15",
            "title": "Watching the denoising happen",
            "blocks": [
                {"t": "p", "md": "`num_steps` exposes the loop count from section 17.2 as a "
                                 "generation parameter. Render the same prompt at several "
                                 "settings and the process becomes visible."},
                {"t": "code", "lang": "python", "src": """import numpy as np
from PIL import Image

def display(images):
    return Image.fromarray(np.concatenate(images, axis=1))

display([task.generate(prompt, num_steps=x) for x in [5, 10, 15, 20, 25]])"""},
                {"t": "p", "md": "At 5 steps the image is a blurred impression; by 25 it is "
                                 "sharp. **The same weights throughout** — only the number of "
                                 "times they were applied changed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3.1 · listing 17.9",
            "title": "Taking generate() apart",
            "blocks": [
                {"t": "p", "md": "To walk the latent space we need the three stages separately: "
                                 "encode the prompt, denoise conditioned on it, rescale the "
                                 "output."},
                {"t": "code", "lang": "python", "file": "listing 17.9", "src": """def get_text_embeddings(prompt):
    token_ids = task.preprocessor.generate_preprocess([prompt])
    negative_token_ids = task.preprocessor.generate_preprocess([""])
    return task.backbone.encode_text_step(token_ids, negative_token_ids)

def denoise_with_text_embeddings(embeddings, num_steps=28, guidance_scale=7.0):
    latents = random.normal((1, height // 8, width // 8, 16))
    for step in range(num_steps):
        latents = task.backbone.denoise_step(
            latents, embeddings, step, num_steps, guidance_scale,
        )
    return task.backbone.decode_step(latents)[0]"""},
                {"t": "p", "md": "Note the latents are **1/8 the image size** per dimension: "
                                 "Stable Diffusion denoises in a compressed space and decodes to "
                                 "pixels only at the end."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3.1",
            "title": "The embedding is four tensors, not one",
            "blocks": [
                {"t": "out", "src": """>>> [x.shape for x in embeddings]
[(1, 154, 4096), (1, 154, 4096), (1, 2048), (1, 2048)]"""},
                {"t": "p", "md": "Rather than passing only the final embedded vector, the Stable "
                                 "Diffusion authors pass **both** the final output vector and "
                                 "the last representation of the entire token sequence — more "
                                 "information for the denoiser to work with. Twice over, for "
                                 "positive and negative:"},
                {"t": "bullets", "items": [
                    "The positive prompt's **encoder sequence** — (1, 154, 4096)",
                    "The negative prompt's **encoder sequence** — (1, 154, 4096)",
                    "The positive prompt's **encoder vector** — (1, 2048)",
                    "The negative prompt's **encoder vector** — (1, 2048)",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3.1 · listing 17.10",
            "title": "Interpolating on a sphere, not a line",
            "blocks": [
                {"t": "p", "md": "To walk between two prompts we interpolate their embeddings — "
                                 "with **slerp**, spherical linear interpolation, a function "
                                 "used in computer graphics for decades."},
                {"t": "code", "lang": "python", "file": "listing 17.10", "src": """def slerp(t, v1, v2):
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
    return s0 * v1 + s1 * v2"""},
                {"t": "p", "md": "The maths is not the point. **The motivation is.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3.1 · figure 17.16",
            "title": "Why linear interpolation goes wrong",
            "blocks": [
                {"t": "p", "md": "Imagine the text manifold as a sphere and two prompts as points "
                                 "on it. Interpolating **linearly** between them lands you "
                                 "**inside** the sphere — off its surface."},
                {"t": "mmd", "id": "ch17-slerp", "src": MMD_SLERP,
                 "cap": "Figure 17.16 — spherical interpolation keeps us close to the surface of "
                        "the manifold."},
                {"t": "p", "md": "The manifold is of course not actually spherical. But it is a "
                                 "smooth surface of numbers all of roughly the same magnitude — "
                                 "it is **sphere-like**, and interpolating as if on a sphere is "
                                 "a better approximation than interpolating as if on a line."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3.1",
            "title": "Interpolating the embeddings",
            "blocks": [
                {"t": "p", "md": "Only the two **positive** tensors are interpolated; the "
                                 "negative ones stay fixed, since we are not using them."},
                {"t": "code", "lang": "python", "src": """def interpolate_text_embeddings(e1, e2, start=0, stop=1, num=10):
    embeddings = []
    for t in np.linspace(start, stop, num):
        embeddings.append(
            (
                slerp(t, e1[0], e2[0]),
                e1[1],
                slerp(t, e1[2], e2[2]),
                e1[3],
            )
        )
    return embeddings"""},
                {"t": "p", "md": "Elements 1 and 3 — the negative prompt's sequence and vector — "
                                 "are passed through unchanged from the first embedding."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3.1 · figure 17.17",
            "title": "A dog becomes something else entirely",
            "blocks": [
                {"t": "p", "md": "Two prompts sharing a setting and differing in their subject, "
                                 "with nine images generated along the path between them."},
                {"t": "code", "lang": "python", "src": """prompt1 = "A friendly dog looking up in a field of flowers"
prompt2 = ("A horrifying, tentacled creature hovering over a field of "
           "flowers")

e1 = get_text_embeddings(prompt1)
e2 = get_text_embeddings(prompt2)

images = []
for et in interpolate_text_embeddings(e1, e2, start=0.5, stop=0.6, num=9):
    image = denoise_with_text_embeddings(et)
    images.append(scale_output(image))
display(images)"""},
                {"t": "p", "md": "The walk runs from **0.5 to 0.6** out of a full [0, 1] range — "
                                 "zoomed into the middle of the interpolation, right where the "
                                 "morph becomes visually obvious. Nine images across a "
                                 "**one-tenth** slice of the path."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 17.3.1 · the closing argument",
            "title": "Interpolation machines",
            "blocks": [
                {"t": "quote", "md": "This might feel like magic the first time you try it, but "
                                     "there's nothing magic about it — **interpolation is "
                                     "fundamental to the way deep neural networks learn.**",
                 "cite": "Section 17.3.1"},
                {"t": "p", "md": "This is the last substantive model in the book, and a "
                                 "deliberately chosen visual metaphor to end on. Deep neural "
                                 "networks are **interpolation machines**: they map complex, "
                                 "real-world probability distributions onto low-dimensional "
                                 "manifolds."},
                {"t": "band", "md": "We can exploit that fact even for input as complex as human "
                                    "language and output as complex as natural images — which is "
                                    "==exactly the claim chapter 15 made about attention==, "
                                    "arrived at from the other end."},
            ],
            "notes": "Tie the two together explicitly. Chapter 15 argued the point algebraically "
                     "about embedding spaces; this chapter shows it, frame by frame. Same claim, "
                     "two proofs.",
        },

        {
            "type": "slide",
            "kicker": "Common failure modes",
            "title": "Four ways generative image work goes wrong",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📐", "h": "Forgetting normalizer.adapt()", "style": "bad",
                     "p": "The noise has unit variance; unnormalized images do not. Training "
                          "runs, loss moves, and the output is **noise**. No error is raised."},
                    {"ico": "🖼", "h": "Resizing without crop_to_aspect_ratio", "style": "bad",
                     "p": "Distortion in the training set becomes distortion in every generated "
                          "image, and it is very hard to diagnose after the fact."},
                    {"ico": "➖", "h": "Linear interpolation of embeddings", "style": "warn",
                     "p": "Lands off the manifold. The midpoints decode to mush rather than to "
                          "intermediate concepts. Use **slerp**."},
                    {"ico": "🔬", "h": "Treating enhancement as evidence", "style": "warn",
                     "p": "Super-resolution invents detail from its priors. The moon-crater "
                          "example is the standing warning: **never for forensics**."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Image generation means learning a latent space** that captures "
                    "statistical information about a dataset — sample it, decode it, and you "
                    "get images nobody has drawn.",
                    "**A classical autoencoder's latent space is not useful**; a VAE's is, "
                    "because encoding to a distribution plus a KL term forces continuity.",
                    "**VAEs give structured, controllable latent spaces** — good for editing, "
                    "concept vectors, and reconstruction, if not for fidelity.",
                    "**Override compute_loss(), not train_step()**, when leaving supervised "
                    "learning — it keeps the code working on all three backends.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter (2 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**Diffusion is a denoising autoencoder in a loop**, predicting the noise "
                    "mask rather than the clean image.",
                    "**The schedule is the design**: diffusion time runs from 1 to 0, and a "
                    "cosine relationship keeps signal² + noise² = 1 throughout.",
                    "**A U-Net with skip connections** is the denoiser — the same architecture "
                    "as chapter 11's segmentation model, given a second scalar input.",
                    "**Text-to-image is one extra input** to the denoiser. Everything else is "
                    "the flower model.",
                    "**Interpolation is what these models do.** Slerp between two prompts and "
                    "you can watch it happen, frame by frame.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "05_stable_diffusion_latent_walk.ipynb",
                     "href": "../../course-slides/notebooks/ch17/05_stable_diffusion_latent_walk.ipynb"},
                    {"k": "PAPER", "ic": "📄", "v": "Kingma & Welling, Auto-Encoding Variational Bayes",
                     "href": "https://arxiv.org/abs/1312.6114"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 18 — Best practices for the real world",
                     "href": "../ch18/index.html"},
                ]},
            ],
        },
    ],
}
