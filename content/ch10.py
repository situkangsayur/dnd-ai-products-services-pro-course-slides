# -*- coding: utf-8 -*-
"""Chapter 10 — Interpreting what ConvNets learn.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 10
(pp. 284-310), read from the book PDF.

Four techniques, from cheapest to most involved: intermediate activations,
filter visualisation by gradient ascent, Grad-CAM heatmaps, and latent-space
projection. The chapter's claim is that ConvNets are *not* black boxes.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_FOUR = """
flowchart TB
  A["<b>1 · Intermediate activations</b><br/>how successive layers<br/>transform an input"]
  B["<b>2 · Filter visualisation</b><br/>what pattern each<br/>filter responds to"]
  C["<b>3 · Class activation maps</b><br/>which part of the image<br/>drove the decision"]
  D["<b>4 · Latent space</b><br/>which inputs the model<br/>finds semantically similar"]
  A --> B --> C --> D
"""

MMD_DISTILL = """
flowchart LR
  IN["Raw RGB pixels"]
  L1["Early layers<br/><small>edge detectors,<br/>almost all information retained</small>"]
  L2["Middle layers<br/><small>textures, parts;<br/>more filters blank</small>"]
  L3["Late layers<br/><small>abstract concepts;<br/>most filters blank</small>"]
  OUT["Class<br/><small>cat or dog</small>"]
  IN --> L1 --> L2 --> L3 --> OUT
"""

MMD_ASCENT = """
flowchart LR
  R["Random image<br/><small>uniform noise</small>"]
  L["Loss = mean activation<br/>of one chosen filter"]
  G["Gradient of that loss<br/>with respect to the IMAGE"]
  U["Move the image<br/>UP the gradient"]
  P["The pattern that filter<br/>responds to most"]
  R --> L --> G --> U
  U -. "30 iterations" .-> L
  U --> P
"""

MMD_GRADCAM = """
flowchart TB
  FM["Feature map of the<br/>last convolution layer<br/><small>how strongly each channel<br/>fires, at each location</small>"]
  GR["Gradient of the class score<br/>with respect to each channel<br/><small>how important each<br/>channel is to the class</small>"]
  W["Weight every channel<br/>by its importance"]
  HM["Heatmap<br/><small>how strongly the image<br/>activates the class, per location</small>"]
  FM --> W
  GR --> W
  W --> HM
"""

MMD_LATENT = """
flowchart LR
  I["Images"] --> M["Model, up to the layer<br/>before the classifier"]
  M --> A["Activation vectors<br/><small>coordinates on the manifold</small>"]
  A --> T["t-SNE / UMAP<br/><small>project to 2D</small>"]
  T --> P["A plot you can read:<br/>clusters, outliers,<br/>ambiguous samples"]
"""

MMD_DESCENT_ASCENT = """
flowchart TB
  subgraph T["Ordinary training"]
    direction TB
    T1["Image is FIXED"] --> T2["Adjust the WEIGHTS"] --> T3["Lower the loss"]
  end
  subgraph V["Filter visualisation"]
    direction TB
    V1["Weights are FIXED"] --> V2["Adjust the IMAGE"] --> V3["Raise the activation"]
  end
  T ~~~ V
"""


MMD_PIPELINE = """
flowchart LR
  Q["A question about<br/>the model"] --> T["Pick the technique"]
  T --> R["Run it on<br/>specific inputs"]
  R --> F["A finding:<br/>spurious feature,<br/>bad label, ambiguity"]
  F --> A["Act: fix the data,<br/>change the model,<br/>or accept and document"]
  A -. "next question" .-> Q
"""

NB = ["01_intermediate_activations.ipynb", "02_filter_visualisation.ipynb",
      "03_grad_cam.ipynb", "04_latent_space.ipynb"]

DECK = {
    "id": "ch10",
    "kind": "chapter",
    "number": 10,
    "title": "Interpreting What ConvNets Learn",
    "subtitle": "Four ways to open the box — and the argument that for ConvNets, "
                "the box was never as closed as people say.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 10",
    "source_url": chapter_url(10),
    "duration": "2.5 hours",
    "presenter": [
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    ],
    "resources": chapter_resources(10, local_notebooks=NB),
    "objectives": [
        "Build a **multi-output model** that returns intermediate activations, and "
        "read what each depth of layer is doing.",
        "Explain **information distillation** and the rising sparsity of activations "
        "with depth.",
        "Visualise what a filter responds to using **gradient ascent in input "
        "space**, and say how it differs from ordinary training.",
        "Produce a **Grad-CAM heatmap** and use it to explain — or debug — a "
        "particular classification.",
        "Project a model's **latent space** to two dimensions to find outliers and "
        "semantically ambiguous samples.",
        "Say which technique answers which question, so the right one is reached "
        "for in a real investigation.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "The black-box claim, examined",
            "blocks": [
                {"t": "p", "md": "It is often said that deep learning models are black boxes: "
                                 "they learn representations that are difficult to extract and "
                                 "present in human-readable form."},
                {"t": "band",
                 "md": "Partially true for **certain types** of model. **Definitely not true "
                       "for ConvNets** — their representations are highly amenable to "
                       "visualisation, largely because they are ==representations of visual "
                       "concepts=="},
                {"t": "p", "md": "Since 2013 a wide array of techniques has been developed. "
                                 "This chapter covers the four most accessible and useful."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "Why this matters beyond curiosity",
            "blocks": [
                {"t": "p", "md": "The motivating question the chapter opens with is a clinical "
                                 "one: **if a model and a human expert disagree, which of you "
                                 "is seeing the truck?**"},
                {"t": "band",
                 "md": "This is especially relevant where deep learning **complements human "
                       "expertise** rather than replacing it — medical imaging being the "
                       "example the book names. ==An unexplained disagreement is not usable "
                       "in that setting.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "The four techniques, and what each answers",
            "blocks": [
                {"t": "mmd", "id": "ch10-four", "src": MMD_FOUR,
                 "cap": "Roughly in order of effort. The first uses your own small ConvNet; "
                        "the next two use a pretrained Xception."},
            ],
        },

        {"type": "section", "num": "01", "title": "Visualising intermediate activations",
         "lead": "What each layer does to one particular image."},

        {
            "type": "slide",
            "kicker": "Section 10.1",
            "title": "What we are looking at",
            "blocks": [
                {"t": "p", "md": "The **activation** of a layer is simply what it outputs for a "
                                 "given input. Visualising activations shows how one input is "
                                 "decomposed into the filters the network learned."},
                {"t": "band",
                 "md": "Feature maps have three dimensions — width, height, and channels. "
                       "Because **each channel encodes a relatively independent feature**, "
                       "the right way to look at them is ==one channel at a time, as a 2D "
                       "image=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.1 · listing 10.3",
            "title": "A model whose outputs are the layers themselves",
            "blocks": [
                {"t": "p", "md": "This is the first genuinely multi-output model in the book: "
                                 "one input, nine outputs — one per layer activation. Chapter "
                                 "7's Functional API is what makes it a two-line job."},
                {"t": "code", "lang": "python", "file": "listing 10.3 — the activation model",
                 "src": """import keras

model = keras.models.load_model("convnet_from_scratch_with_augmentation.keras")

layer_outputs, layer_names = [], []
for layer in model.layers:
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.MaxPooling2D)):
        layer_outputs.append(layer.output)
        layer_names.append(layer.name)

activation_model = keras.Model(inputs=model.input, outputs=layer_outputs)"""},
                {"t": "p", "md": "This works **only because the model is Functional**. A "
                                 "subclassed model has no graph to reach into — exactly the "
                                 "trade-off chapter 7 described."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.1 · listing 10.4–10.5",
            "title": "Running it, and plotting one channel",
            "blocks": [
                {"t": "p", "md": "Calling `predict()` now returns a **list** of arrays rather "
                                 "than a single one — one per layer."},
                {"t": "code", "lang": "python", "file": "listing 10.4–10.5 — activations",
                 "src": """activations = activation_model.predict(img_tensor)   # a list of nine arrays

first_layer_activation = activations[0]
print(first_layer_activation.shape)

import matplotlib.pyplot as plt
plt.matshow(first_layer_activation[0, :, :, 5], cmap="viridis")   # the sixth channel"""},
                {"t": "out", "src": "(1, 178, 178, 32)"},
                {"t": "band",
                 "md": "That channel turns out to be a **diagonal edge detector** — though "
                       "your own channels will differ, since the specific filters a layer "
                       "learns are ==not deterministic=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.1",
            "title": "Three things visible in the full grid",
            "blocks": [
                {"t": "steps", "items": [
                    "**The first layer is a collection of edge detectors.** At that stage the "
                    "activations retain almost all the information in the original picture.",
                    "**Higher layers become increasingly abstract** and less visually "
                    "interpretable — encoding concepts like *cat ear* and *cat eye*. They "
                    "carry less about the image's appearance and more about its class.",
                    "**Sparsity increases with depth.** In the first layer every filter fires; "
                    "further up, more and more are blank — meaning ==that filter's pattern is "
                    "not present in this image==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.1",
            "title": "A deep network is an information distillation pipeline",
            "blocks": [
                {"t": "mmd", "id": "ch10-distill", "src": MMD_DISTILL,
                 "cap": "Irrelevant information is filtered out; useful information is "
                        "magnified and refined."},
                {"t": "p", "md": "This is **a universal characteristic** of the representations "
                                 "deep networks learn, not something particular to this model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.1",
            "title": "The bicycle test",
            "blocks": [
                {"t": "p", "md": "The book offers a striking analogy. After looking at a scene "
                                 "for a few seconds you can remember which abstract objects "
                                 "were in it — bicycle, tree — but not their specific "
                                 "appearance."},
                {"t": "band",
                 "md": "Try drawing a generic bicycle from memory right now. You have seen "
                       "thousands, and you will almost certainly ==not get it remotely "
                       "right==. The effect is real, and it is the same distillation: your "
                       "brain abstracted the input and discarded the detail."},
            ],
            "notes": "Actually do this in the room — 60 seconds, everyone draws a bicycle. "
                     "It lands the point better than any slide can.",
        },

        {
            "type": "slide",
            "kicker": "Section 10.1 · listing 10.6",
            "title": "Stitching every channel into one grid",
            "blocks": [
                {"t": "p", "md": "Plotting one channel is a spot check. To see the whole "
                                 "picture, every channel of every layer is tiled into a single "
                                 "canvas, layer by layer."},
                {"t": "code", "lang": "python", "file": "listing 10.6 — the display loop",
                 "src": """images_per_row = 16

for layer_name, layer_activation in zip(layer_names, activations):
    n_features = layer_activation.shape[-1]
    size = layer_activation.shape[1]
    n_cols = n_features // images_per_row
    display_grid = np.zeros(((size + 1) * n_cols - 1,
                             images_per_row * (size + 1) - 1))
    for col in range(n_cols):
        for row in range(images_per_row):
            channel_image = standardise(
                layer_activation[0, :, :, col * images_per_row + row])
            display_grid[col * (size + 1): (col + 1) * size + col,
                         row * (size + 1): (row + 1) * size + row] = channel_image"""},
                {"t": "p", "md": "One canvas per layer, sixteen channels to a row. The next "
                                 "slide explains the standardisation in the middle of that "
                                 "loop, which is the part that makes the result readable."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.1 · listing 10.6",
            "title": "Why each channel is standardised first",
            "blocks": [
                {"t": "band",
                 "md": "The per-channel standardisation matters: without it the faint "
                       "channels are invisible next to the strong ones, and ==the rising "
                       "sparsity is exactly what you came to see=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Visualising ConvNet filters",
         "lead": "Gradient ascent in input space."},

        {
            "type": "slide",
            "kicker": "Section 10.2",
            "title": "The idea: train the image instead of the weights",
            "blocks": [
                {"t": "mmd", "id": "ch10-descent-ascent", "src": MMD_DESCENT_ASCENT,
                 "cap": "Same machinery, opposite target — and the sign is flipped."},
                {"t": "p", "md": "Start from a blank (noisy) input and apply gradient descent "
                                 "to the **image**, maximising the response of one chosen "
                                 "filter. The result is the input that filter likes best."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2 · listing 10.7–10.8",
            "title": "Setting up: a pretrained model, and its layer names",
            "blocks": [
                {"t": "p", "md": "The same Xception backbone as chapter 8. First, find out what "
                                 "the convolution layers are called, so their outputs can be "
                                 "retrieved."},
                {"t": "code", "lang": "python", "file": "listing 10.7–10.8 — model and layer names",
                 "src": """import keras_hub

model = keras_hub.models.Backbone.from_preset("xception_41_imagenet")
preprocessor = keras_hub.layers.ImageConverter.from_preset(
    "xception_41_imagenet", image_size=(180, 180))

for layer in model.layers:
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.SeparableConv2D)):
        print(layer.name)"""},
                {"t": "out", "src": """block2_sepconv1
block3_sepconv1
block4_sepconv1
...
block14_sepconv2"""},
                {"t": "p", "md": "The names follow Xception's block structure from chapter 9, "
                                 "which makes it easy to sample **shallow, middle, and deep** "
                                 "layers for comparison."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2",
            "title": "The loss: one filter's mean activation",
            "blocks": [
                {"t": "p", "md": "Build a feature extractor that stops at the chosen layer, "
                                 "then define a loss that is simply the mean activation of one "
                                 "filter — with the borders trimmed to avoid edge artefacts."},
                {"t": "code", "lang": "python", "file": "the loss to maximise",
                 "src": """layer_name = "block3_sepconv1"
layer = model.get_layer(name=layer_name)
feature_extractor = keras.Model(inputs=model.input, outputs=layer.output)

def compute_loss(image, filter_index):
    activation = feature_extractor(image)
    filter_activation = activation[:, 2:-2, 2:-2, filter_index]   # trim the border
    return ops.mean(filter_activation)"""},
                {"t": "p", "md": "Note what this loss is a function of: **the image**. That is "
                                 "the whole trick."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2.1 · listing 10.11",
            "title": "One ascent step, in TensorFlow",
            "blocks": [
                {"t": "p", "md": "This is the book's second low-level gradient loop — the "
                                 "first was chapter 2. Two details differ from a training step."},
                {"t": "code", "lang": "python", "file": "listing 10.11 — gradient ascent step",
                 "src": """@tf.function
def gradient_ascent_step(image, filter_index, learning_rate):
    with tf.GradientTape() as tape:
        tape.watch(image)                     # the image is not a Variable, so watch it
        loss = compute_loss(image, filter_index)
    grads = tape.gradient(loss, image)        # gradient w.r.t. the IMAGE
    grads = ops.normalize(grads)              # the "gradient normalization trick"
    image += learning_rate * grads            # PLUS: we are ascending, not descending
    return image"""},
                {"t": "band",
                 "md": "`tape.watch(image)` is required because only `Variable`s are watched "
                       "automatically — exactly the rule chapter 3 gave. And the `+=` is what "
                       "makes it ==ascent rather than descent=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2.2 – 10.2.3",
            "title": "The same step in PyTorch and JAX",
            "blocks": [
                {"t": "p", "md": "Nothing conceptually new — this is chapter 3's three gradient "
                                 "idioms applied to a different variable."},
                {"t": "table",
                 "head": ["Backend", "How the gradient is obtained"],
                 "widths": [22, 78],
                 "rows": [
                     ["**TensorFlow**", "`tape.watch(image)`, then `tape.gradient(loss, image)`."],
                     ["**PyTorch**", "`loss.backward()`, then read `image.grad`."],
                     ["**JAX**", "Transform the loss function with `jax.grad`, differentiating "
                      "with respect to the image argument."],
                 ]},
                {"t": "p", "md": "Whichever backend you use, ==the image is the thing being "
                                 "differentiated==, and that is the only unusual part."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2.4 · listing 10.14",
            "title": "The loop that produces one filter's pattern",
            "blocks": [
                {"t": "p", "md": "Start from uniform noise centred on 0.5 — Xception expects "
                                 "inputs in [0, 1] — and take thirty large steps."},
                {"t": "code", "lang": "python", "file": "listing 10.14 — generating a pattern",
                 "src": """img_width = img_height = 200

def generate_filter_pattern(filter_index):
    iterations = 30
    learning_rate = 10.0
    image = keras.random.uniform(
        minval=0.4, maxval=0.6, shape=(1, img_width, img_height, 3))
    for i in range(iterations):
        image = gradient_ascent_step(image, filter_index, learning_rate)
    return image[0]"""},
                {"t": "band",
                 "md": "A learning rate of **10.0** would be absurd for training weights. Here "
                       "it is fine, because ==we are not trying to converge to a minimum== — "
                       "only to move the image somewhere the filter likes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2.4 · listing 10.15",
            "title": "…and turning the result back into an image",
            "blocks": [
                {"t": "p", "md": "The output is a float array whose values are not in [0, 255], "
                                 "so it has to be standardised and clipped before it can be "
                                 "displayed."},
                {"t": "code", "lang": "python", "file": "listing 10.15 — deprocess_image",
                 "src": """def deprocess_image(image):
    image -= ops.mean(image)
    image /= ops.std(image)
    image *= 64
    image += 128
    image = ops.clip(image, 0, 255).astype("uint8")
    return image[25:-25, 25:-25, :]     # crop the border artefacts"""},
                {"t": "p", "md": "The final crop removes the edge artefacts that gradient "
                                 "ascent tends to accumulate at the borders."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2.4",
            "title": "What the filter banks look like, layer by layer",
            "blocks": [
                {"t": "table",
                 "head": ["Depth", "Example layer", "What the filters encode"],
                 "widths": [20, 26, 54],
                 "rows": [
                     ["**Early**", "`block2_sepconv1`",
                      "Simple **directional edges and colours** — sometimes coloured edges."],
                     ["**Middle**", "`block4_sepconv1`",
                      "Simple **textures** made from combinations of edges and colours."],
                     ["**Deep**", "`block8_sepconv1`",
                      "Textures found in natural images: **feathers, eyes, leaves**."],
                 ]},
                {"t": "band",
                 "md": "Chollet's analogy: each layer learns a **filter bank** such that its "
                       "inputs can be expressed as a combination of those filters — ==similar "
                       "to how a Fourier transform decomposes a signal onto cosines=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2.2 · listing 10.12",
            "title": "The PyTorch version, written out",
            "blocks": [
                {"t": "p", "md": "Worth seeing in full, because the image has to be marked as "
                                 "requiring a gradient — which is not something you normally "
                                 "do to an input."},
                {"t": "code", "lang": "python", "file": "listing 10.12 — ascent step in PyTorch",
                 "src": """import torch

def gradient_ascent_step(image, filter_index, learning_rate):
    image = image.clone().detach().requires_grad_(True)   # the image needs a gradient
    loss = compute_loss(image, filter_index)
    loss.backward()
    grads = image.grad
    grads = ops.normalize(grads)
    return image + learning_rate * grads"""},
                {"t": "band",
                 "md": "`requires_grad_(True)` on an **input tensor** is the PyTorch "
                       "equivalent of `tape.watch(image)` — both say *differentiate with "
                       "respect to this, even though it is not a parameter*."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.2.3 · listing 10.13",
            "title": "…and the JAX version",
            "blocks": [
                {"t": "p", "md": "In JAX the loss function is transformed, so the thing being "
                                 "differentiated is simply whichever argument comes first."},
                {"t": "code", "lang": "python", "file": "listing 10.13 — ascent step in JAX",
                 "src": """import jax

grad_fn = jax.grad(compute_loss)          # differentiates w.r.t. its first argument

@jax.jit
def gradient_ascent_step(image, filter_index, learning_rate):
    grads = grad_fn(image, filter_index)
    grads = ops.normalize(grads)
    return image + learning_rate * grads"""},
                {"t": "p", "md": "Because `compute_loss(image, filter_index)` takes the image "
                                 "first, `jax.grad` differentiates with respect to it "
                                 "==without any extra ceremony at all=="},
            ],
        },

        {"type": "section", "num": "03", "title": "Class activation heatmaps",
         "lead": "Which part of this picture made the model say that?"},

        {
            "type": "slide",
            "kicker": "Section 10.3",
            "title": "What a CAM is, and what it is for",
            "blocks": [
                {"t": "p", "md": "A **class activation heatmap** is a 2D grid of scores for a "
                                 "specific output class, computed at every location of an "
                                 "input image, saying how important that location is to that "
                                 "class."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🐞", "h": "Debugging a decision",
                     "p": "Particularly a **misclassification** — the field is called model "
                          "interpretability.", "style": "accent"},
                    {"ico": "📍", "h": "Locating an object",
                     "p": "The heatmap tells you **where** in the frame the evidence was.",
                     "style": "accent"},
                ]},
                {"t": "p", "md": "For a dogs-vs-cats model you could generate one heatmap for "
                                 "*cat* and another for *dog* over the same picture."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.3",
            "title": "Grad-CAM, in one sentence",
            "blocks": [
                {"t": "mmd", "id": "ch10-gradcam", "src": MMD_GRADCAM,
                 "cap": "Weight *how strongly each channel fires here* by *how much this "
                        "channel matters to the class*."},
                {"t": "p", "md": "The result is a spatial map of **how intensely the input "
                                 "image activates the class**. The implementation follows "
                                 "Selvaraju et al."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.3 · listing 10.17",
            "title": "The worked example: two African elephants",
            "blocks": [
                {"t": "p", "md": "The book uses a photograph of an adult elephant and a calf, "
                                 "fed to a pretrained Xception classifier."},
                {"t": "code", "lang": "python", "file": "listing 10.17 — preparing the image",
                 "src": """img_path = keras.utils.get_file(
    fname="elephant.jpg",
    origin="https://img-datasets.s3.amazonaws.com/elephant.jpg",
)

img = keras.utils.load_img(img_path)           # a PIL image
img_array = np.expand_dims(img, axis=0)        # to NumPy, plus a batch axis"""},
                {"t": "p", "md": "Everything that follows asks the same question of this "
                                 "picture: **which pixels made it say *African elephant*?**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.3.1 – 10.3.3",
            "title": "Getting the gradient of the top class",
            "blocks": [
                {"t": "p", "md": "Two things are needed: the output of the last convolution "
                                 "layer, and the gradient of the winning class score with "
                                 "respect to that output."},
                {"t": "code", "lang": "python", "file": "the TensorFlow version",
                 "src": """with tf.GradientTape() as tape:
    last_conv_layer_output = last_conv_layer_model(preprocessed_image)
    tape.watch(last_conv_layer_output)
    preds = classifier_model(last_conv_layer_output)
    top_pred_index = ops.argmax(preds[0])
    top_class_channel = preds[:, top_pred_index]

grads = tape.gradient(top_class_channel, last_conv_layer_output)"""},
                {"t": "p", "md": "PyTorch and JAX versions differ only in the gradient idiom, "
                                 "exactly as in the filter visualisation."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.3.4 · listing 10.23",
            "title": "Pooling and weighting to get the heatmap",
            "blocks": [
                {"t": "p", "md": "Average the gradient over space to get one importance number "
                                 "per channel, scale each channel by it, then average across "
                                 "channels."},
                {"t": "code", "lang": "python", "file": "listing 10.23 — building the heatmap",
                 "src": """# one number per channel: how important that channel is to the top class
pooled_grads = np.mean(grads, axis=(0, 1, 2))

last_conv_layer_output = last_conv_layer_output[0].copy()
for i in range(pooled_grads.shape[-1]):
    last_conv_layer_output[:, :, i] *= pooled_grads[i]      # weight each channel

heatmap = np.mean(last_conv_layer_output, axis=-1)          # average across channels"""},
                {"t": "band",
                 "md": "Three lines of arithmetic and no new machinery — Grad-CAM is "
                       "==a weighted average, not a new model=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.3.4 · listing 10.24–10.25",
            "title": "Normalising and superimposing it",
            "blocks": [
                {"t": "p", "md": "Clip the negatives, scale to [0, 1], recolour with a "
                                 "colormap, and lay it over the original at 40% opacity."},
                {"t": "code", "lang": "python", "file": "listing 10.24–10.25 — display",
                 "src": """heatmap = np.maximum(heatmap, 0)
heatmap /= np.max(heatmap)

heatmap = np.uint8(255 * heatmap)
jet_colors = cm.get_cmap("jet")(np.arange(256))[:, :3]
jet_heatmap = keras.utils.array_to_img(jet_colors[heatmap])
jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
jet_heatmap = keras.utils.img_to_array(jet_heatmap)

superimposed_img = jet_heatmap * 0.4 + img
keras.utils.array_to_img(superimposed_img).save("elephant_cam.jpg")"""},
                {"t": "p", "md": "The result is the picture with the evidence highlighted — "
                                 "the artefact you would actually show a domain expert."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.3.4",
            "title": "The two questions it answers",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "❓", "h": "Why did it say African elephant?",
                     "p": "Because **these pixels** carried the evidence. If they are the "
                          "wrong pixels, you have found a spurious correlation.",
                     "style": "accent"},
                    {"ico": "📌", "h": "Where is the elephant?",
                     "p": "The heatmap localises the object without ever having been trained "
                          "to do detection.", "style": "accent"},
                ]},
                {"t": "band",
                 "md": "The first question is the one that matters in review: a model that is "
                       "right **for the wrong reasons** passes every accuracy check and "
                       "==fails the first time the background changes=="},
            ],
        },

        {"type": "section", "num": "04", "title": "Visualising the latent space",
         "lead": "Which inputs does the model consider similar?"},

        {
            "type": "slide",
            "kicker": "Section 10.4",
            "title": "Every model embeds its inputs in a latent space",
            "blocks": [
                {"t": "p", "md": "All deep learning models work by embedding inputs in a "
                                 "**latent space** — a manifold where points close together "
                                 "represent semantically similar inputs. On that manifold the "
                                 "classes become separable, and ==that separability is what "
                                 "makes classification possible=="},
                {"t": "p", "md": "This is chapter 5's manifold hypothesis, now made visible."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.4",
            "title": "How to look at it",
            "blocks": [
                {"t": "mmd", "id": "ch10-latent", "src": MMD_LATENT,
                 "cap": "Take the activations of one layer as coordinates, then project them "
                        "down to two dimensions."},
                {"t": "p", "md": "Any layer can be used — **each encodes a different latent "
                                 "space**, and they become progressively more semantically "
                                 "organised with depth. The usual choice is the layer just "
                                 "before the classifier."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.4",
            "title": "What it is actually good for",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔍", "h": "Finding outliers",
                     "p": "Points sitting far from every cluster are usually **mislabelled or "
                          "corrupt** — the noisy data of chapter 5.", "style": "accent"},
                    {"ico": "🌗", "h": "Finding ambiguity",
                     "p": "Points between two clusters are the samples the model finds "
                          "**semantically ambiguous** — chapter 5's ambiguous features.",
                     "style": "accent"},
                    {"ico": "🧹", "h": "Improving the dataset",
                     "p": "Both findings feed straight back into **cleaning the training set "
                          "and refining the evaluation set**.", "style": "good"},
                ]},
                {"t": "band",
                 "md": "Which makes this the technique that closes the loop: it is an "
                       "interpretation tool whose output is ==a concrete list of samples to "
                       "go and look at=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 10.4",
            "title": "Projecting it, in practice",
            "blocks": [
                {"t": "p", "md": "The activations are high-dimensional, so a dimensionality "
                                 "reduction step is needed before anything can be plotted."},
                {"t": "code", "lang": "python", "file": "recording and projecting activations",
                 "src": """embedding_model = keras.Model(inputs=model.input,
                              outputs=model.layers[-2].output)   # before the classifier
embeddings = embedding_model.predict(dataset)

from sklearn.manifold import TSNE
projected = TSNE(n_components=2, init="pca").fit_transform(embeddings)

plt.scatter(projected[:, 0], projected[:, 1], c=labels, s=4, cmap="coolwarm")"""},
                {"t": "band",
                 "md": "Colour the points by their **label**, not by the prediction. A point "
                       "whose colour disagrees with its neighbourhood is ==either mislabelled "
                       "or genuinely hard== — and both are worth knowing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Practice",
            "title": "Interpretation is a loop, not a report",
            "blocks": [
                {"t": "mmd", "id": "ch10-pipeline", "src": MMD_PIPELINE,
                 "cap": "The output of every technique here is meant to change something."},
                {"t": "band", "style": "amber",
                 "md": "A heatmap that nobody acts on is decoration. The value is in the third "
                       "and fourth boxes: **a finding, and a decision** — even when the "
                       "decision is to accept the behaviour and write it down."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Practice",
            "title": "And what these techniques do not give you",
            "blocks": [
                {"t": "bullets", "items": [
                    "They explain **this model on this input**. They are not a general "
                    "statement about the model's behaviour on data it has not seen.",
                    "A convincing heatmap is **not proof of a correct decision** — a model can "
                    "look at the right region and still be wrong.",
                    "None of them turn the model into a set of rules you can audit line by "
                    "line. They make it ==inspectable, not transparent==.",
                ]},
                {"t": "p", "md": "Which is worth saying plainly when a stakeholder asks "
                                 "whether the model can be \"explained\": these techniques "
                                 "answer a narrower question than the one usually being asked."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "Which technique answers which question",
            "blocks": [
                {"t": "table",
                 "head": ["Question you are asking", "Technique"],
                 "widths": [52, 48],
                 "rows": [
                     ["*What is each layer doing to my input?*",
                      "**Intermediate activations** (§10.1)"],
                     ["*What pattern does this filter respond to?*",
                      "**Gradient ascent in input space** (§10.2)"],
                     ["*Which part of the image drove this decision?*",
                      "**Grad-CAM heatmap** (§10.3)"],
                     ["*Which samples does my model confuse, and which are junk?*",
                      "**Latent-space projection** (§10.4)"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**ConvNets are not black boxes.** Their representations are visual, and "
                    "therefore visualisable.",
                    "**A deep network is an information distillation pipeline**: less about "
                    "appearance, more about class, with rising sparsity at depth.",
                    "**Gradient ascent trains the image, not the weights** — same machinery, "
                    "opposite target.",
                    "**Grad-CAM is a weighted average**, and it answers *why here?* as well "
                    "as *where?*",
                    "**Latent-space projection finds the samples to go and inspect** — "
                    "outliers and ambiguous cases.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_grad_cam.ipynb",
                     "href": "../../course-slides/notebooks/ch10/03_grad_cam.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 11 — Image segmentation",
                     "href": "../ch11/index.html"},
                ]},
            ],
        },
    ],
}
