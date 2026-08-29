# -*- coding: utf-8 -*-
"""Chapter 10 notebooks — Interpreting What ConvNets Learn."""

DECK = "ch10"

NOTEBOOKS = [
    {
        "file": "01_intermediate_activations.ipynb",
        "title": "Visualizing intermediate activations",
        "lede": "What a ConvNet sees at each depth, on one photograph — from edges at "
                "the bottom to abstractions with no visual meaning at the top.",
        "needs": "CPU — about 2 minutes",
        "section": "01 — Visualizing intermediate activations",
        "cells": [
            ("h2", "A model, and an image it has never seen"),
            ("py", """import keras
import numpy as np
import matplotlib.pyplot as plt

# Use the model trained in chapter 8, or any convnet you have.
model = keras.models.load_model("convnet_from_scratch_with_augmentation.keras")
model.summary()"""),
            ("py", """img_path = keras.utils.get_file(
    fname="cat.jpg",
    origin="https://img-datasets.s3.amazonaws.com/cat.jpg")

def get_img_array(path, target_size):
    img = keras.utils.load_img(path, target_size=target_size)
    array = keras.utils.img_to_array(img)
    return np.expand_dims(array, axis=0)

img_tensor = get_img_array(img_path, target_size=(180, 180))
plt.imshow(img_tensor[0].astype("uint8")); plt.axis("off"); plt.show()"""),

            ("h2", "A model that returns every layer's output"),
            ("md",
             "This is the capability chapter 7 said subclassing throws away. A "
             "Functional model is a **graph**, so you can ask any node for its "
             "value."),
            ("py", """layer_outputs = []
layer_names = []
for layer in model.layers:
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.MaxPooling2D)):
        layer_outputs.append(layer.output)
        layer_names.append(layer.name)

activation_model = keras.Model(inputs=model.input, outputs=layer_outputs)
activations = activation_model.predict(img_tensor, verbose=0)

for name, act in zip(layer_names, activations):
    print(f"{name:20s} {act.shape}")"""),

            ("h2", "The first layer"),
            ("py", """first = activations[0]
fig, axes = plt.subplots(4, 8, figsize=(12, 6.4))
for ax, i in zip(axes.ravel(), range(min(32, first.shape[-1]))):
    ax.imshow(first[0, :, :, i], cmap="viridis")
    ax.set_title(f"ch {i}", fontsize=7); ax.axis("off")
plt.suptitle("First convolution layer — 32 channels", y=1.0)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Edge detectors, colour blobs, and one or two channels that are "
             "**almost blank** — filters that never learned anything useful. "
             "That is normal, and worth noticing: not every filter earns its "
             "place."),

            ("h2", "Every layer, side by side"),
            ("py", """images_per_row = 16
for layer_name, layer_activation in zip(layer_names, activations):
    n_features = layer_activation.shape[-1]
    size = layer_activation.shape[1]
    n_cols = n_features // images_per_row
    if n_cols < 1:
        continue
    display_grid = np.zeros(((size + 1) * n_cols - 1,
                             images_per_row * (size + 1) - 1))
    for col in range(n_cols):
        for row in range(images_per_row):
            channel_index = col * images_per_row + row
            channel_image = layer_activation[0, :, :, channel_index].copy()
            if channel_image.sum() != 0:
                channel_image -= channel_image.mean()
                channel_image /= (channel_image.std() + 1e-7)
                channel_image *= 64
                channel_image += 128
            channel_image = np.clip(channel_image, 0, 255).astype("uint8")
            display_grid[col * (size + 1): (col + 1) * size + col,
                         row * (size + 1): (row + 1) * size + row] = channel_image
    scale = 1. / size
    plt.figure(figsize=(scale * display_grid.shape[1],
                        scale * display_grid.shape[0]))
    plt.title(layer_name); plt.grid(False); plt.axis("off")
    plt.imshow(display_grid, aspect="auto", cmap="viridis")
plt.show()"""),

            ("h2", "Three things to read off these pictures"),
            ("md",
             "**The first layer is almost a collection of edge detectors.** It "
             "retains nearly all the information in the original image — you "
             "could reconstruct the cat from it.\n\n"
             "**Deeper layers become abstract and less visually "
             "interpretable.** They start encoding *cat ear*, *whisker texture* "
             "— concepts rather than pixels.\n\n"
             "**Sparsity increases with depth.** More and more channels are "
             "blank for any given input, because a filter that detects a "
             "specific thing is silent on images that do not contain it."),

            ("h2", "Measuring the sparsity claim"),
            ("py", """fracs = []
for name, act in zip(layer_names, activations):
    blank = (act[0].reshape(-1, act.shape[-1]).max(axis=0) == 0).mean()
    fracs.append(blank)
    print(f"{name:20s} {blank:5.1%} of channels are entirely zero")

plt.figure(figsize=(7, 3.6))
plt.plot(range(len(fracs)), fracs, "o-")
plt.xticks(range(len(fracs)), layer_names, rotation=45, ha="right")
plt.ylabel("fraction of dead channels"); plt.tight_layout()
plt.title("Sparsity increases with depth")
plt.show()"""),
            ("md",
             "This is what the chapter means by a network **distilling** its "
             "input: information about *what the image is* survives, while "
             "information about *what it looks like* is progressively discarded. "
             "A ConvNet is an information funnel, and the funnel is deliberate."),
        ],
        "takeaways": [
            "A Functional model lets you build a second model that outputs any "
            "intermediate layer.",
            "The first layer is nearly a lossless edge detector; deeper layers "
            "encode concepts.",
            "**Sparsity rises with depth** — specific detectors are silent on "
            "most inputs.",
            "The network discards appearance and keeps identity. That is the "
            "point, not a defect.",
        ],
    },

    {
        "file": "02_filter_visualisation.ipynb",
        "title": "What each filter responds to",
        "lede": "Gradient ascent in input space: synthesise the image that maximally "
                "excites a chosen filter, and read the network's visual vocabulary "
                "directly.",
        "needs": "CPU — about 4 minutes (GPU: 1 minute)",
        "section": "02 — Visualizing convnet filters",
        "cells": [
            ("h2", "A pretrained model, for a richer vocabulary"),
            ("py", """import keras
import numpy as np
import matplotlib.pyplot as plt

model = keras.applications.xception.Xception(
    weights="imagenet", include_top=False)

for layer in model.layers:
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.SeparableConv2D)):
        print(layer.name)"""),

            ("h2", "A feature extractor for one layer"),
            ("py", """layer_name = "block3_sepconv1"
layer = model.get_layer(name=layer_name)
feature_extractor = keras.Model(inputs=model.input, outputs=layer.output)

activation = feature_extractor(
    keras.applications.xception.preprocess_input(
        np.random.uniform(size=(1, 200, 200, 3)) * 255))
print("activation shape:", activation.shape)"""),

            ("h2", "The loss: mean activation of one filter"),
            ("py", """from keras import ops

def compute_loss(image, filter_index):
    activation = feature_extractor(image)
    # Avoid the border, where padding artifacts dominate.
    filter_activation = activation[:, 2:-2, 2:-2, filter_index]
    return ops.mean(filter_activation)"""),
            ("md",
             "**We are not minimising a loss here — we are maximising an "
             "activation.** The optimizer's direction is reversed, and the thing "
             "being updated is the *image*, not the weights."),

            ("h2", "Gradient ascent"),
            ("py", """import tensorflow as tf

@tf.function
def gradient_ascent_step(image, filter_index, learning_rate):
    with tf.GradientTape() as tape:
        tape.watch(image)
        loss = compute_loss(image, filter_index)
    grads = tape.gradient(loss, image)
    grads = tf.math.l2_normalize(grads)       # normalize: makes lr predictable
    image += learning_rate * grads
    return image

img_width = img_height = 200

def generate_filter_pattern(filter_index, iterations=30, learning_rate=10.):
    image = tf.random.uniform(minval=0.4, maxval=0.6,
                              shape=(1, img_width, img_height, 3))
    for _ in range(iterations):
        image = gradient_ascent_step(image, filter_index, learning_rate)
    return image[0].numpy()

def deprocess_image(image):
    image -= image.mean()
    image /= image.std() + 1e-5
    image *= 64
    image += 128
    image = np.clip(image, 0, 255).astype("uint8")
    return image[25:-25, 25:-25, :]

plt.figure(figsize=(4, 4))
plt.imshow(deprocess_image(generate_filter_pattern(filter_index=2)))
plt.axis("off"); plt.title(f"{layer_name}, filter 2"); plt.show()"""),
            ("note",
             "`l2_normalize` on the gradient is what makes a single learning "
             "rate work across layers of wildly different activation scales. "
             "Without it you would retune the step size for every layer."),

            ("h2", "A grid of filters"),
            ("py", """all_images = []
for filter_index in range(64):
    image = deprocess_image(generate_filter_pattern(filter_index))
    all_images.append(image)

margin, n = 5, 8
cropped = all_images[0].shape[0]
width = n * cropped + (n - 1) * margin
stitched = np.zeros((width, width, 3), dtype="uint8")
for i in range(n):
    for j in range(n):
        img = all_images[i * n + j]
        stitched[(cropped + margin) * i: (cropped + margin) * i + cropped,
                 (cropped + margin) * j: (cropped + margin) * j + cropped, :] = img

plt.figure(figsize=(11, 11))
plt.imshow(stitched); plt.axis("off")
plt.title(f"64 filters from {layer_name}")
plt.show()"""),

            ("h2", "The same, at three depths"),
            ("py", """for name in ["block2_sepconv1", "block4_sepconv1", "block10_sepconv1"]:
    layer = model.get_layer(name=name)
    feature_extractor = keras.Model(inputs=model.input, outputs=layer.output)
    imgs = [deprocess_image(generate_filter_pattern(i)) for i in range(8)]
    fig, axes = plt.subplots(1, 8, figsize=(14, 2))
    for ax, im in zip(axes, imgs):
        ax.imshow(im); ax.axis("off")
    fig.suptitle(name, y=1.05)
    plt.show()"""),
            ("md",
             "A clear progression:\n\n"
             "- **Early** — simple edges and colours, close to Gabor filters.\n"
             "- **Middle** — textures: feathers, eyes, foliage, grids.\n"
             "- **Late** — recognisable object parts: whole feathers, dog "
             "faces, bird beaks.\n\n"
             "**Nobody designed this hierarchy.** It falls out of "
             "backpropagation on labelled photographs, and it resembles the "
             "organisation of the primate visual cortex closely enough to be "
             "worth remarking on."),

            ("h2", "Dead filters"),
            ("py", """dead = []
for i in range(64):
    p = generate_filter_pattern(i, iterations=20)
    if p.std() < 1e-3:
        dead.append(i)
print(f"{len(dead)} of 64 filters produced a flat image: {dead}")"""),
            ("md",
             "Filters that never activate on anything. They are pure overhead, "
             "and their existence is one of the arguments for the pruning and "
             "quantization techniques in chapter 18."),
        ],
        "takeaways": [
            "Gradient **ascent** on the input synthesises what a filter is "
            "looking for.",
            "Normalize the gradient so one learning rate works at every depth.",
            "The hierarchy — edges, textures, object parts — is learned, not "
            "designed.",
            "Some filters are dead. Finding them is the first step toward "
            "pruning.",
        ],
    },

    {
        "file": "03_grad_cam.ipynb",
        "title": "Grad-CAM: which part of the image decided the answer",
        "lede": "A heatmap over the input showing where the evidence for a class came "
                "from — the most immediately useful debugging tool in this chapter.",
        "needs": "CPU — about 2 minutes",
        "section": "03 — Visualizing heatmaps of class activation",
        "cells": [
            ("h2", "A pretrained classifier and a test image"),
            ("py", """import keras
import numpy as np
import matplotlib.pyplot as plt

model = keras.applications.xception.Xception(weights="imagenet")

img_path = keras.utils.get_file(
    fname="elephant.jpg",
    origin="https://img-datasets.s3.amazonaws.com/elephant.jpg")

def get_img_array(img_path, target_size):
    img = keras.utils.load_img(img_path, target_size=target_size)
    array = keras.utils.img_to_array(img)
    array = np.expand_dims(array, axis=0)
    return keras.applications.xception.preprocess_input(array)

img_array = get_img_array(img_path, target_size=(299, 299))
preds = model.predict(img_array, verbose=0)
print(keras.applications.xception.decode_predictions(preds, top=3)[0])"""),
            ("out", """[('n02504458', 'African_elephant', 0.87...),
 ('n01871265', 'tusker', 0.08...),
 ('n02504013', 'Indian_elephant', 0.02...)]"""),

            ("h2", "The two pieces Grad-CAM needs"),
            ("py", """last_conv_layer_name = "block14_sepconv2_act"
classifier_layer_names = ["avg_pool", "predictions"]

last_conv_layer = model.get_layer(last_conv_layer_name)
last_conv_layer_model = keras.Model(model.inputs, last_conv_layer.output)

classifier_input = keras.Input(shape=last_conv_layer.output.shape[1:])
x = classifier_input
for layer_name in classifier_layer_names:
    x = model.get_layer(layer_name)(x)
classifier_model = keras.Model(classifier_input, x)"""),
            ("md",
             "The model is split at the **last convolutional layer**: the "
             "deepest place that still has spatial structure. Later than that "
             "and there is no *where* left to point at; earlier and the features "
             "are not class-specific enough to be informative."),

            ("h2", "The gradient of the class score, per channel"),
            ("py", """import tensorflow as tf

with tf.GradientTape() as tape:
    last_conv_layer_output = last_conv_layer_model(img_array)
    tape.watch(last_conv_layer_output)
    preds = classifier_model(last_conv_layer_output)
    top_pred_index = tf.argmax(preds[0])
    top_class_channel = preds[:, top_pred_index]

grads = tape.gradient(top_class_channel, last_conv_layer_output)
pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2)).numpy()
print("one importance weight per channel:", pooled_grads.shape)"""),
            ("md",
             "`pooled_grads[i]` answers: **how much does channel *i* matter to "
             "this class?** Weight each channel's activation map by that number "
             "and sum — the result is a map of where the evidence was."),

            ("h2", "The heatmap"),
            ("py", """last_conv_layer_output = last_conv_layer_output.numpy()[0]
for i in range(pooled_grads.shape[-1]):
    last_conv_layer_output[:, :, i] *= pooled_grads[i]
heatmap = np.mean(last_conv_layer_output, axis=-1)

heatmap = np.maximum(heatmap, 0)
heatmap /= np.max(heatmap)
plt.matshow(heatmap); plt.title("Raw heatmap (10x10)"); plt.show()"""),

            ("h2", "Superimposed"),
            ("py", """import matplotlib.cm as cm

img = keras.utils.load_img(img_path)
img = keras.utils.img_to_array(img)

hm = np.uint8(255 * heatmap)
jet = cm.get_cmap("jet")
jet_colors = jet(np.arange(256))[:, :3]
jet_heatmap = jet_colors[hm]

jet_heatmap = keras.utils.array_to_img(jet_heatmap)
jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
jet_heatmap = keras.utils.img_to_array(jet_heatmap)

superimposed = jet_heatmap * 0.4 + img
superimposed = keras.utils.array_to_img(superimposed)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
a1.imshow(keras.utils.load_img(img_path)); a1.axis("off"); a1.set_title("input")
a2.imshow(superimposed); a2.axis("off"); a2.set_title("Grad-CAM: African elephant")
plt.tight_layout(); plt.show()"""),
            ("md",
             "The heat concentrates on the **ears** — which is in fact the "
             "feature that separates African from Indian elephants. The model "
             "found the same discriminator a zoologist would name."),

            ("h2", "The same heatmap for the second-place class"),
            ("py", """def grad_cam(img_array, class_index):
    with tf.GradientTape() as tape:
        conv_out = last_conv_layer_model(img_array)
        tape.watch(conv_out)
        preds = classifier_model(conv_out)
        channel = preds[:, class_index]
    grads = tape.gradient(channel, conv_out)
    pooled = tf.reduce_mean(grads, axis=(0, 1, 2)).numpy()
    out = conv_out.numpy()[0]
    for i in range(pooled.shape[-1]):
        out[:, :, i] *= pooled[i]
    hm = np.mean(out, axis=-1)
    hm = np.maximum(hm, 0)
    return hm / (hm.max() + 1e-8)

preds = model.predict(img_array, verbose=0)
top3 = preds[0].argsort()[::-1][:3]
labels = keras.applications.xception.decode_predictions(preds, top=3)[0]

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
for ax, idx, (_, name, score) in zip(axes, top3, labels):
    ax.matshow(grad_cam(img_array, idx))
    ax.set_title(f"{name}  {score:.2f}", fontsize=10); ax.axis("off")
plt.tight_layout(); plt.show()"""),
            ("md",
             "Different classes, different evidence — *tusker* looks at the "
             "tusks. **This is the check that catches a model doing the right "
             "thing for the wrong reason**: a classifier that finds cows by "
             "looking at grass will show you the grass."),

            ("h2", "Use it on your own errors"),
            ("md",
             "The practical workflow: take the misclassified samples from your "
             "test set, run Grad-CAM on each, and look. In practice you will "
             "find one of three things — a genuinely hard image, a wrong label, "
             "or **the model attending to a background artifact**. Only the "
             "third is a modelling problem, and you cannot tell them apart from "
             "the confusion matrix."),
        ],
        "takeaways": [
            "Grad-CAM weights each channel of the last convolutional layer by "
            "how much it moved the class score.",
            "Split the model at the **last layer with spatial structure**.",
            "Different classes produce different heatmaps — the ears against the "
            "tusks.",
            "Run it on your errors; it distinguishes a hard image from a model "
            "looking at the wrong thing.",
        ],
    },

    {
        "file": "04_latent_space.ipynb",
        "title": "The latent space of a trained classifier",
        "lede": "Take the penultimate layer's output as an embedding, project it to two "
                "dimensions, and see the structure the network built without ever being "
                "asked to.",
        "needs": "CPU — about 3 minutes",
        "section": "04 — What the network has organised",
        "cells": [
            ("h2", "A classifier, and its penultimate layer"),
            ("py", """import keras
from keras import layers
from keras.datasets import fashion_mnist
import numpy as np

(x, y), (xt, yt) = fashion_mnist.load_data()
x = x.reshape(-1, 28, 28, 1).astype("float32") / 255
xt = xt.reshape(-1, 28, 28, 1).astype("float32") / 255
classes = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat",
           "Sandal", "Shirt", "Sneaker", "Bag", "Boot"]

inputs = keras.Input(shape=(28, 28, 1))
z = layers.Conv2D(32, 3, activation="relu")(inputs)
z = layers.MaxPooling2D(2)(z)
z = layers.Conv2D(64, 3, activation="relu")(z)
z = layers.MaxPooling2D(2)(z)
z = layers.Flatten()(z)
embedding = layers.Dense(32, activation="relu", name="embedding")(z)
outputs = layers.Dense(10, activation="softmax")(embedding)
model = keras.Model(inputs, outputs)

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(x, y, epochs=6, batch_size=128, validation_split=.1, verbose=2)
print("test:", model.evaluate(xt, yt, verbose=0)[1])"""),

            ("h2", "Extracting the embedding"),
            ("py", """encoder = keras.Model(model.input, model.get_layer("embedding").output)
emb = encoder.predict(xt[:4000], verbose=0)
labels = yt[:4000]
print("embedding:", emb.shape)"""),
            ("md",
             "Thirty-two numbers per garment. **The classifier was never asked "
             "to organise this space** — it was asked to get the label right, "
             "and the organisation is a by-product."),

            ("h2", "Projecting it"),
            ("py", """from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

pca = PCA(n_components=2).fit_transform(emb)
tsne = TSNE(n_components=2, init="pca", perplexity=30,
            random_state=0).fit_transform(emb)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6.4))
for ax, proj, name in [(a1, pca, "PCA"), (a2, tsne, "t-SNE")]:
    sc = ax.scatter(proj[:, 0], proj[:, 1], c=labels, cmap="tab10", s=6, alpha=.75)
    ax.set_title(f"{name} of the 32-d embedding"); ax.set_xticks([]); ax.set_yticks([])
handles = [plt.Line2D([], [], marker="o", ls="", color=plt.cm.tab10(i / 9),
                      label=classes[i]) for i in range(10)]
fig.legend(handles=handles, loc="lower center", ncol=10, fontsize=8.5,
           frameon=False, bbox_to_anchor=(0.5, -0.03))
plt.tight_layout(); plt.show()"""),

            ("h2", "Reading the structure"),
            ("md",
             "Three things are worth pointing out on the t-SNE panel.\n\n"
             "**Footwear clusters together** — sandal, sneaker, and boot sit "
             "adjacent, because they *are* adjacent. Nobody encoded that "
             "relation.\n\n"
             "**Shirt overlaps with T-shirt, pullover, and coat.** Those are "
             "genuinely confusable and the confusion matrix will show it. The "
             "geometry predicts the errors.\n\n"
             "**Bag and trouser sit apart from everything.** Distinctive shapes, "
             "distinctive region."),

            ("h2", "The geometry predicts the confusion matrix"),
            ("py", """from sklearn.metrics import confusion_matrix

pred = model.predict(xt[:4000], verbose=0).argmax(axis=1)
cm = confusion_matrix(labels, pred, normalize="true")

plt.figure(figsize=(7.5, 6.4))
plt.imshow(cm, cmap="Blues")
plt.xticks(range(10), classes, rotation=45, ha="right")
plt.yticks(range(10), classes)
plt.colorbar(label="fraction"); plt.title("Confusion matrix")
for i in range(10):
    for j in range(10):
        if cm[i, j] > 0.03 and i != j:
            plt.text(j, i, f"{cm[i,j]:.2f}", ha="center", va="center", fontsize=7)
plt.tight_layout(); plt.show()"""),
            ("md",
             "The off-diagonal mass sits exactly where the embedding clusters "
             "overlap. **The two pictures are the same fact seen twice**, and "
             "the embedding version tells you *why* — the model's representation "
             "does not separate those classes, so no decision boundary drawn on "
             "it can."),

            ("h2", "Nearest neighbours in the learned space"),
            ("py", """from sklearn.neighbors import NearestNeighbors

nn = NearestNeighbors(n_neighbors=6).fit(emb)
query_indices = [3, 17, 42, 77]

fig, axes = plt.subplots(len(query_indices), 6, figsize=(10, 1.8 * len(query_indices)))
for row, qi in enumerate(query_indices):
    _, idx = nn.kneighbors(emb[qi:qi+1])
    for col, j in enumerate(idx[0]):
        axes[row, col].imshow(xt[j, :, :, 0], cmap="gray_r")
        axes[row, col].axis("off")
        axes[row, col].set_title("query" if col == 0 else classes[labels[j]],
                                 fontsize=8)
plt.suptitle("Nearest neighbours in the 32-d embedding", y=1.0)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Similar garments, retrieved by distance in a space nobody designed "
             "for retrieval. **This is the same mechanism as chapter 15's "
             "embeddings and chapter 16's vector database** — a classifier "
             "trained on labels produces a usable similarity metric as a "
             "by-product, and that by-product is often more valuable than the "
             "labels."),
        ],
        "takeaways": [
            "The penultimate layer is an embedding you can use for retrieval and "
            "clustering.",
            "Its structure is emergent — the model was optimised for labels, not "
            "geometry.",
            "Overlapping clusters predict the confusion matrix, and explain it.",
            "The same idea scales up to chapter 15's embeddings and chapter 16's "
            "vector databases.",
        ],
    },
]
