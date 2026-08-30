# -*- coding: utf-8 -*-
"""Chapter 11 — Image segmentation.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 11
(pp. 308-330), read from the book PDF.

Two halves: build an encoder-decoder segmentation model from scratch, then use
Segment Anything — a pretrained model you prompt rather than fine-tune.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_TASKS = """
flowchart TB
  A["<b>Image classification</b><br/>image in, label out<br/><small>Google Photos search:<br/>20,000+ classes</small>"]
  B["<b>Image segmentation</b><br/>a class for every pixel<br/><small>Zoom or Meet replacing<br/>your background</small>"]
  C["<b>Object detection</b><br/>boxes plus classes<br/><small>a car watching for<br/>pedestrians and signs</small>"]
  A ~~~ B ~~~ C
"""

MMD_FLAVOURS = """
flowchart TB
  S["<b>Semantic</b><br/>every pixel gets a class<br/><small>both cats are just &quot;cat&quot;</small>"]
  I["<b>Instance</b><br/>individual objects separated<br/><small>&quot;cat 1&quot; and &quot;cat 2&quot;</small>"]
  P["<b>Panoptic</b><br/>both at once<br/><small>a class AND an instance<br/>for every pixel</small>"]
  S --> I --> P
"""

MMD_ENCDEC = """
flowchart LR
  IN["Input<br/><code>200 x 200 x 3</code>"]
  E1["Conv stride 2<br/><code>100 x 100 x 64</code>"]
  E2["Conv stride 2<br/><code>50 x 50 x 128</code>"]
  E3["Conv stride 2<br/><code>25 x 25 x 256</code>"]
  D1["ConvTranspose<br/><code>50 x 50 x 256</code>"]
  D2["ConvTranspose<br/><code>100 x 100 x 128</code>"]
  D3["ConvTranspose<br/><code>200 x 200 x 64</code>"]
  OUT["Conv softmax<br/><code>200 x 200 x 3</code>"]
  IN --> E1 --> E2 --> E3 --> D1 --> D2 --> D3 --> OUT
"""

MMD_POOLVSTRIDE = """
flowchart TB
  subgraph MP["Max pooling — fine for classification"]
    direction TB
    M1["Take a 2 x 2 window"] --> M2["Return one value"]
    M2 --> M3["<b>Which of the four positions<br/>it came from is destroyed</b>"]
  end
  subgraph ST["Strided convolution — needed for segmentation"]
    direction TB
    S1["Slide the kernel<br/>with stride 2"] --> S2["Downsample by learning"]
    S2 --> S3["<b>Location information<br/>is retained</b>"]
  end
  MP ~~~ ST
"""

MMD_IOU = """
flowchart LR
  A["Predicted mask"] --> I["Intersection<br/><small>where they overlap</small>"]
  B["Ground truth mask"] --> I
  A --> U["Union<br/><small>everything covered by either</small>"]
  B --> U
  I --> R["IoU = intersection / union<br/><small>1 = perfect, 0 = complete miss</small>"]
  U --> R
"""

MMD_SAM = """
flowchart LR
  IMG["Image"] --> IE["Image encoder<br/><small>like Xception:<br/>a small image embedding</small>"]
  PR["Prompt<br/><small>a point, or a box</small>"] --> PE["Prompt encoder<br/><small>to an embedded vector</small>"]
  IE --> MD["Mask decoder"]
  PE --> MD
  MD --> M1["mask + score"]
  MD --> M2["mask + score"]
  MD --> M3["mask + score"]
"""

MMD_SAMLOOP = """
flowchart LR
  H["Human experts segment<br/>a small dataset"] --> M0["Train an initial model"]
  M0 --> A["Model pre-segments<br/>new images"]
  A --> C["Humans correct<br/>and add annotations"]
  C --> M1["Retrain on more data"]
  M1 -. "repeat, with less<br/>human effort each round" .-> A
"""


MMD_MASK = """
flowchart LR
  I["Input image<br/><code>Abyssinian_1.jpg</code><br/><small>RGB, 3 channels</small>"]
  M["Segmentation mask<br/><code>Abyssinian_1.png</code><br/><small>1 channel, integer per pixel</small>"]
  L1["1 = foreground"]
  L2["2 = background"]
  L3["3 = contour"]
  I -. "same size,<br/>same name" .-> M
  M --> L1
  M --> L2
  M --> L3
"""

NB = ["01_segmentation_from_scratch.ipynb", "02_conv2dtranspose.ipynb",
      "03_segment_anything.ipynb"]

DECK = {
    "id": "ch11",
    "kind": "chapter",
    "number": 11,
    "title": "Image Segmentation",
    "subtitle": "A class for every pixel — built from scratch as an encoder-decoder, "
                "then handed to a pretrained model you prompt rather than train.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 11",
    "source_url": chapter_url(11),
    "duration": "2.5 hours",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(11, local_notebooks=NB),
    "objectives": [
        "Place **classification, segmentation, and detection** — the three tasks "
        "almost all computer vision reduces to.",
        "Distinguish **semantic, instance, and panoptic** segmentation.",
        "Build an **encoder-decoder** segmentation model, and explain why the "
        "output must match the input's spatial size.",
        "Say why segmentation uses **strided convolutions instead of max pooling**.",
        "Explain what **`Conv2DTranspose`** does and how it undoes a strided "
        "convolution.",
        "Compute and interpret **Intersection over Union**, and configure the Keras "
        "metric correctly for sparse targets.",
        "Use **Segment Anything** with point and box prompts, without fine-tuning "
        "anything.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Section 11.1",
            "title": "Three tasks almost everything reduces to",
            "blocks": [
                {"t": "mmd", "id": "ch11-tasks", "src": MMD_TASKS,
                 "cap": "Figure 11.1 — classification, segmentation, and detection."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.1",
            "title": "…and the more specialised ones beyond them",
            "blocks": [
                {"t": "p", "md": "Computer vision also covers **image similarity scoring, "
                                 "keypoint detection** (facial features, for instance), **pose "
                                 "estimation, 3D mesh estimation**, and **depth estimation**."},
                {"t": "band",
                 "md": "But classification, segmentation, and detection are the foundation "
                       "every engineer should know: ==almost all computer vision applications "
                       "boil down to one of these three=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.1.1",
            "title": "Three flavours of segmentation",
            "blocks": [
                {"t": "mmd", "id": "ch11-flavours", "src": MMD_FLAVOURS,
                 "cap": "Figure 11.2 — panoptic is the most informative of the three."},
                {"t": "p", "md": "All of them assign a class **to each pixel**, partitioning "
                                 "the image into zones — *background* and *foreground*, or "
                                 "*road*, *car*, and *sidewalk*."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.1.1",
            "title": "Where it is actually used",
            "blocks": [
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "🎬", "h": "Image and video editing",
                     "p": "Background replacement, object removal, compositing."},
                    {"ico": "🚗", "h": "Autonomous driving",
                     "p": "Road, lane, and obstacle segmentation at pixel precision."},
                    {"ico": "🤖", "h": "Robotics",
                     "p": "Knowing exactly where a graspable object begins and ends."},
                    {"ico": "🩻", "h": "Medical imaging",
                     "p": "Delineating an organ or a lesion rather than merely detecting it."},
                ]},
            ],
        },

        {"type": "section", "num": "01", "title": "Training a segmentation model from scratch",
         "lead": "An encoder that compresses, and a decoder that puts it back."},

        {
            "type": "slide",
            "kicker": "Section 11.2.1",
            "title": "What a label looks like when the label is an image",
            "blocks": [
                {"t": "mmd", "id": "ch11-mask", "src": MMD_MASK,
                 "cap": "A segmentation mask is the equivalent of a label: same size as the "
                        "input, one channel, one integer per pixel."},
                {"t": "p", "md": "The dataset is **Oxford-IIIT Pets**: 7,390 pictures of cat "
                                 "and dog breeds, each with a foreground-background mask."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.1",
            "title": "Pairing images with their masks",
            "blocks": [
                {"t": "p", "md": "Inputs are JPGs in `images/`; each mask is a PNG of the same "
                                 "name in `annotations/trimaps/`. Sorting both lists is what "
                                 "keeps them aligned."},
                {"t": "code", "lang": "python", "file": "building the two path lists",
                 "src": """import pathlib

input_dir = pathlib.Path("images")
target_dir = pathlib.Path("annotations/trimaps")

input_img_paths = sorted(input_dir.glob("*.jpg"))
target_paths = sorted(target_dir.glob("[!.]*.png"))    # skips spurious dot-files

print(len(input_img_paths), len(target_paths))"""},
                {"t": "out", "src": "7390 7390"},
                {"t": "band", "style": "amber",
                 "md": "The `[!.]` in the glob is not cosmetic: the trimaps directory contains "
                       "hidden files, and including them would ==silently offset every "
                       "image-mask pair after the first one=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.1",
            "title": "Shuffling two lists in lockstep",
            "blocks": [
                {"t": "p", "md": "The paths arrive sorted by breed, so they must be shuffled — "
                                 "but images and masks have to stay paired. The trick is the "
                                 "same seed, twice."},
                {"t": "code", "lang": "python", "file": "loading into memory",
                 "src": """img_size = (200, 200)
num_imgs = len(input_img_paths)

random.Random(1337).shuffle(input_img_paths)     # the SAME seed in both calls
random.Random(1337).shuffle(target_paths)        # keeps the pairing intact

def path_to_target(path):
    img = img_to_array(load_img(path, target_size=img_size, color_mode="grayscale"))
    return img.astype("uint8") - 1               # labels 1,2,3 -> 0,1,2

input_imgs = np.zeros((num_imgs,) + img_size + (3,), dtype="float32")
targets = np.zeros((num_imgs,) + img_size + (1,), dtype="uint8")
for i in range(num_imgs):
    input_imgs[i] = path_to_input_image(input_img_paths[i])
    targets[i] = path_to_target(target_paths[i])"""},
                {"t": "band",
                 "md": "Two details worth naming: the labels are shifted from **1, 2, 3 to "
                       "0, 1, 2** because the loss expects zero-based classes, and the whole "
                       "dataset is loaded into memory because ==7,390 images at 200×200 "
                       "comfortably fits=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.1",
            "title": "Looking at a mask before training on it",
            "blocks": [
                {"t": "p", "md": "Chapter 6 insisted on looking at your data. For masks that "
                                 "needs a small transformation, because values of 1, 2 and 3 "
                                 "are all indistinguishable black on screen."},
                {"t": "code", "lang": "python", "file": "making a mask visible",
                 "src": """def display_target(target_array):
    # 1,2,3 -> 0,127,254 : black, grey, near-white
    normalized_array = (target_array.astype("uint8") - 1) * 127
    plt.axis("off")
    plt.imshow(normalized_array[:, :, 0])

img = img_to_array(load_img(target_paths[9], color_mode="grayscale"))
display_target(img)"""},
                {"t": "p", "md": "The result shows the animal in black, the background in "
                                 "near-white, and a grey contour band between them — "
                                 "==the third class, which is easy to forget exists=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "The shape of the problem",
            "blocks": [
                {"t": "mmd", "id": "ch11-encdec", "src": MMD_ENCDEC,
                 "cap": "Down three times by a factor of two, then back up three times."},
                {"t": "p", "md": "The first half is an ordinary classification-style ConvNet: "
                                 "it **compresses** the image into a small feature map where "
                                 "each location carries information about a large chunk of the "
                                 "original."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "The model, in one function",
            "blocks": [
                {"t": "p", "md": "Note two things: `padding=\"same\"` everywhere, and the "
                                 "absence of any pooling layer."},
                {"t": "code", "lang": "python", "file": "the encoder half",
                 "src": """from keras.layers import Rescaling, Conv2D, Conv2DTranspose

def get_model(img_size, num_classes):
    inputs = keras.Input(shape=img_size + (3,))
    x = Rescaling(1.0 / 255)(inputs)

    x = Conv2D(64, 3, strides=2, activation="relu", padding="same")(x)
    x = Conv2D(64, 3, activation="relu", padding="same")(x)
    x = Conv2D(128, 3, strides=2, activation="relu", padding="same")(x)
    x = Conv2D(128, 3, activation="relu", padding="same")(x)
    x = Conv2D(256, 3, strides=2, padding="same", activation="relu")(x)
    x = Conv2D(256, 3, activation="relu", padding="same")(x)
    # ends at (25, 25, 256)"""},
                {"t": "p", "md": "Familiar so far — growing filter counts, shrinking spatial "
                                 "size. **Except** that every downsample is a stride rather "
                                 "than a pooling layer."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "…and the decoder half",
            "blocks": [
                {"t": "p", "md": "The second half mirrors the first, reversing each stride to "
                                 "climb back to the input's spatial size."},
                {"t": "code", "lang": "python", "file": "the decoder half",
                 "src": """    x = Conv2DTranspose(256, 3, activation="relu", padding="same")(x)
    x = Conv2DTranspose(256, 3, strides=2, activation="relu", padding="same")(x)
    x = Conv2DTranspose(128, 3, activation="relu", padding="same")(x)
    x = Conv2DTranspose(128, 3, strides=2, activation="relu", padding="same")(x)
    x = Conv2DTranspose(64, 3, activation="relu", padding="same")(x)
    x = Conv2DTranspose(64, 3, strides=2, activation="relu", padding="same")(x)

    outputs = Conv2D(num_classes, 3, activation="softmax", padding="same")(x)
    return keras.Model(inputs, outputs)

model = get_model(img_size=img_size, num_classes=3)"""},
                {"t": "p", "md": "Three strided convolutions down, three strided transposed "
                                 "convolutions up — ==the counts have to match== or the output "
                                 "will not align with the mask."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "What that last layer is doing",
            "blocks": [
                {"t": "band",
                 "md": "The final layer is a **per-pixel softmax**: for every one of the "
                       "200×200 output positions it produces a distribution over the three "
                       "classes. ==Classification, repeated 40,000 times.=="},
                {"t": "p", "md": "Which is why `padding=\"same\"` appears on every layer: any "
                                 "border trimming would leave the output a different size "
                                 "from the mask it is being compared against."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "Why no max pooling here",
            "blocks": [
                {"t": "mmd", "id": "ch11-poolvstride", "src": MMD_POOLVSTRIDE,
                 "cap": "The trade-off that was invisible in chapter 8 becomes decisive here."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "The rule that follows from it",
            "blocks": [
                {"t": "p", "md": "2×2 max pooling returns one scalar per window with **zero "
                                 "knowledge of which of the four positions it came from**. "
                                 "For classification that loss is harmless. For segmentation "
                                 "it is fatal — the output *is* a map of locations."},
                {"t": "band",
                 "md": "So the general rule the book states: **use strides instead of max "
                       "pooling in any model that cares about feature location** — including "
                       "==the generative models of chapter 17=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "Conv2DTranspose: a convolution that learns to upsample",
            "blocks": [
                {"t": "p", "md": "The encoder leaves a `(25, 25, 256)` feature map, but the "
                                 "output must be `(200, 200, 3)`. Something has to reverse the "
                                 "downsampling."},
                {"t": "code", "lang": "python", "file": "the two are inverses",
                 "src": """# input (100, 100, 64)
Conv2D(128, 3, strides=2, padding="same")           # -> (50, 50, 128)

# input (50, 50, 128)
Conv2DTranspose(64, 3, strides=2, padding="same")   # -> (100, 100, 64)"""},
                {"t": "band",
                 "md": "So a stack of `Conv2D` with strides, mirrored by a stack of "
                       "`Conv2DTranspose` with the same strides, ==returns you to the "
                       "original spatial size== — which is exactly what the model above does."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "Measuring it: Intersection over Union",
            "blocks": [
                {"t": "mmd", "id": "ch11-iou", "src": MMD_IOU,
                 "cap": "Accuracy per pixel would be dominated by the background; IoU is not."},
                {"t": "p", "md": "It can be computed per class or averaged across classes, and "
                                 "it is the standard measure of how well a predicted mask "
                                 "matches the ground truth."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "Configuring the Keras metric correctly",
            "blocks": [
                {"t": "p", "md": "Keras has IoU built in, but two arguments have to match your "
                                 "data — and getting them wrong produces a silently "
                                 "meaningless number."},
                {"t": "code", "lang": "python", "file": "the IoU metric",
                 "src": """foreground_iou = keras.metrics.IoU(
    num_classes=3,
    target_class_ids=(0,),      # which class to score: 0 = foreground
    name="foreground_iou",
    sparse_y_true=True,         # our targets are integer class IDs
    sparse_y_pred=False,        # but our predictions are a dense softmax
)"""},
                {"t": "band", "style": "amber",
                 "md": "`sparse_y_true=True` with `sparse_y_pred=False` is the combination "
                       "you almost always want here: **targets are integers, predictions are "
                       "probabilities**. ==Mismatching them does not raise an error.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "Compiling and fitting it",
            "blocks": [
                {"t": "p", "md": "From here it is the ordinary workflow: sparse categorical "
                                 "crossentropy, because the targets are integer class IDs per "
                                 "pixel."},
                {"t": "code", "lang": "python", "file": "training the segmentation model",
                 "src": """model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=[foreground_iou])

callbacks = [keras.callbacks.ModelCheckpoint("segmentation.keras",
                                             save_best_only=True)]

history = model.fit(train_dataset, epochs=50,
                    validation_data=validation_dataset, callbacks=callbacks)"""},
                {"t": "p", "md": "Everything you learned in chapters 6 and 7 applies unchanged "
                                 "— only the model's output shape and the metric are new."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "Splitting, and what the arrays look like",
            "blocks": [
                {"t": "p", "md": "A thousand samples are reserved for validation. Because both "
                                 "arrays were shuffled with the same seed, a plain slice is "
                                 "enough."},
                {"t": "code", "lang": "python", "file": "the split",
                 "src": """num_val_samples = 1000
train_input_imgs = input_imgs[:-num_val_samples]
train_targets = targets[:-num_val_samples]
val_input_imgs = input_imgs[-num_val_samples:]
val_targets = targets[-num_val_samples:]

print(train_input_imgs.shape, train_targets.shape)"""},
                {"t": "out", "src": "(6390, 200, 200, 3) (6390, 200, 200, 1)"},
                {"t": "band",
                 "md": "Note the target shape: **one channel, not three**. The input is RGB; "
                       "the target is ==a single integer per pixel=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.2.2",
            "title": "Predicting, and reading the output",
            "blocks": [
                {"t": "p", "md": "The model outputs probabilities per class per pixel, so "
                                 "turning that into a picture means taking an argmax along "
                                 "the channel axis."},
                {"t": "code", "lang": "python", "file": "predicting a mask",
                 "src": """model = keras.models.load_model("segmentation.keras")

test_image = val_input_imgs[4]
mask = model.predict(np.expand_dims(test_image, 0))[0]

predicted_mask = np.argmax(mask, axis=-1)      # (200, 200): a class per pixel
print(mask.shape, predicted_mask.shape)"""},
                {"t": "out", "src": "(200, 200, 3) (200, 200)"},
                {"t": "p", "md": "That `argmax` is the segmentation equivalent of the "
                                 "`predictions[0].argmax()` from chapter 2 — ==performed once "
                                 "per pixel instead of once per image=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Using a pretrained segmentation model",
         "lead": "Segment Anything: prompt it, do not train it."},

        {
            "type": "slide",
            "kicker": "Section 11.3",
            "title": "What SAM is",
            "blocks": [
                {"t": "p", "md": "The **Segment Anything Model**, from Meta AI, released April "
                                 "2023. Trained on **11 million images** and their masks, "
                                 "covering **over 1 billion object instances**."},
                {"t": "band",
                 "md": "The main innovation: it is **not limited to a predefined set of object "
                       "classes**. You segment a new kind of object simply by giving an "
                       "example of what you are looking for — ==and you do not need to "
                       "fine-tune it first=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.2",
            "title": "The dataset and the model were built together",
            "blocks": [
                {"t": "mmd", "id": "ch11-samloop", "src": MMD_SAMLOOP,
                 "cap": "The partially trained model was used to help label the data it would "
                        "later be trained on."},
                {"t": "p", "md": "The goal of SA-1B is **fully segmented images**: every object "
                                 "given a unique mask. Each image carries around **100 masks "
                                 "on average**, and some have over **500**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.2",
            "title": "Three components, trained together",
            "blocks": [
                {"t": "mmd", "id": "ch11-sam", "src": MMD_SAM,
                 "cap": "Figure 11.8 — image encoder, prompt encoder, mask decoder. The "
                        "decoder emits several candidate masks, each with a score."},
                {"t": "p", "md": "The image encoder is **something you already know how to "
                                 "build** — it is much like the Xception of chapters 8 and 9. "
                                 "The prompt encoder and mask decoder use techniques from "
                                 "later chapters."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.2",
            "title": "How the training triples are generated",
            "blocks": [
                {"t": "p", "md": "The model is trained on **(image, prompt, mask)** triples, "
                                 "and the way they are produced is strikingly simple."},
                {"t": "steps", "items": [
                    "For a given image, **choose a random mask** from its annotations.",
                    "**Randomly choose** whether to create a box prompt or a point prompt.",
                    "For a **point prompt**, pick a random pixel inside the mask.",
                    "For a **box prompt**, draw a box around all points inside the mask.",
                ]},
                {"t": "band",
                 "md": "That can be repeated indefinitely, sampling **many triples from each "
                       "image** — which is how 11 million images become ==a far larger number "
                       "of training examples=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.4",
            "title": "Two kinds of prompt",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📍", "h": "Point prompts",
                     "p": "Select a point and let the model segment the object it belongs to. "
                          "Points are **labelled**: 1 for foreground, 0 for background.",
                     "style": "accent"},
                    {"ico": "🔲", "h": "Box prompts",
                     "p": "Draw an approximate box around an object — **it does not need to "
                          "be precise** — and let the model segment what is inside.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "In ambiguous cases, pass **several labelled points** rather than one: "
                       "points labelled 1 say what to include, points labelled 0 say "
                       "==what to leave out=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.4",
            "title": "Prompting it with a single point",
            "blocks": [
                {"t": "p", "md": "The book uses a photograph of a bowl of fruit and asks for "
                                 "whatever object lies under one chosen pixel."},
                {"t": "code", "lang": "python", "file": "a point prompt",
                 "src": """import numpy as np

input_point = np.array([[580, 450]])     # coordinates of the point
input_label = np.array([1])              # 1 = foreground, 0 = background

outputs = model.predict({
    "images": ops.expand_dims(image, axis=0),
    "points": ops.expand_dims(input_point, axis=0),
    "labels": ops.expand_dims(input_label, axis=0),
})"""},
                {"t": "band",
                 "md": "One point, no training, no class list — and SAM returns a mask for "
                       "the peach that point landed on. ==That is the shift this section is "
                       "about.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.4",
            "title": "Reading the output",
            "blocks": [
                {"t": "p", "md": "The decoder returns **several candidate masks with scores**, "
                                 "because a point is genuinely ambiguous: it might mean the "
                                 "peach, the bowl, or the whole arrangement."},
                {"t": "code", "lang": "python", "file": "picking a mask",
                 "src": """masks = outputs["masks"][0]
scores = outputs["iou_pred"][0]

best = int(np.argmax(scores))
mask = masks[best]
print(mask.shape, float(scores[best]))"""},
                {"t": "band", "style": "amber",
                 "md": "Taking the top-scoring mask is the default, but the ambiguity is real "
                       "information: **if the three candidates disagree wildly, the prompt "
                       "itself was ambiguous** — and ==an extra background point usually "
                       "resolves it=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3",
            "title": "From scratch, or pretrained?",
            "blocks": [
                {"t": "table",
                 "head": ["", "From scratch (§11.2)", "Segment Anything (§11.3)"],
                 "widths": [22, 39, 39],
                 "rows": [
                     ["**What you need**", "A labelled mask for every training image.",
                      "One point or box, at inference time."],
                     ["**Classes**", "Fixed at training time.",
                      "**None** — it segments whatever you point at."],
                     ["**Training cost**", "A full training run.", "Zero."],
                     ["**When it wins**",
                      "You need a **specific, repeatable** class set — medical structures, "
                      "industrial defects — and you have the masks.",
                      "You need **generic** object masks, or you have no labelled data at "
                      "all."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.1",
            "title": "Loading SAM",
            "blocks": [
                {"t": "p", "md": "Like the classifiers in chapter 8, it comes from KerasHub "
                                 "with a matching preprocessor — the model expects images at "
                                 "a particular size and range."},
                {"t": "code", "lang": "python", "file": "instantiating Segment Anything",
                 "src": """import keras_hub

model = keras_hub.models.SAMImageSegmenter.from_preset("sam_huge_sa1b")

path = keras.utils.get_file(
    origin="https://s3.amazonaws.com/keras.io/img/book/fruits.jpg")
image = np.array(keras.utils.load_img(path))"""},
                {"t": "p", "md": "No training data, no class list, no fine-tuning step — "
                                 "==the next thing that happens is a prediction=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3",
            "title": "Why a promptable model changes the workflow",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📚", "h": "The old shape",
                     "p": "Decide your classes → collect masks for each → train → the model "
                          "can segment **those classes and no others**.", "style": "warn"},
                    {"ico": "👉", "h": "The new shape",
                     "p": "Point at the thing → get a mask. The class set is **decided at "
                          "inference time**, by the person using it.", "style": "good"},
                ]},
                {"t": "band",
                 "md": "That is the same move as prompting a language model, arriving in "
                       "vision — and it is why chapter 1 grouped **foundation models** as a "
                       "category rather than a technique."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 11.3.4",
            "title": "Refining an ambiguous prompt",
            "blocks": [
                {"t": "p", "md": "A single point on a peach might mean the peach, the bowl, "
                                 "or the whole still life. Extra labelled points resolve it."},
                {"t": "code", "lang": "python", "file": "adding a background point",
                 "src": """input_point = np.array([[580, 450],      # on the peach   -> include
                        [300, 800]])     # on the table   -> exclude
input_label = np.array([1, 0])           # 1 = foreground, 0 = background

outputs = model.predict({
    "images": ops.expand_dims(image, axis=0),
    "points": ops.expand_dims(input_point, axis=0),
    "labels": ops.expand_dims(input_label, axis=0),
})"""},
                {"t": "band",
                 "md": "This is the practical loop with SAM: **prompt, look, add a point, "
                       "prompt again**. It is closer to ==using a selection tool== than to "
                       "training a model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Practice",
            "title": "Where segmentation quietly goes wrong",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔀", "h": "Images and masks drift apart",
                     "p": "Two lists sorted or shuffled differently. Nothing errors — the "
                          "model simply learns nothing, and the loss curve looks like a "
                          "capacity problem.", "style": "bad"},
                    {"ico": "🏷", "h": "Off-by-one labels",
                     "p": "Masks numbered 1..N fed to a loss expecting 0..N-1. The last class "
                          "is never predicted and the first is never learned.", "style": "bad"},
                    {"ico": "⚖", "h": "Accuracy instead of IoU",
                     "p": "If 90% of pixels are background, a model predicting *background* "
                          "everywhere scores 90% accuracy and **zero** foreground IoU.",
                     "style": "warn"},
                    {"ico": "📐", "h": "Padding mismatch",
                     "p": "One layer without `padding=\"same\"` and the output no longer "
                          "matches the mask's size.", "style": "warn"},
                ]},
            ],
            "notes": "All four show up in the lab. The first two are the ones that look like "
                     "modelling problems and are not.",
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Classification, segmentation, detection** — almost every vision "
                    "application is one of these three.",
                    "**Semantic, instance, panoptic** — increasing amounts of information "
                    "per pixel.",
                    "A segmentation model is an **encoder-decoder**: compress, then restore "
                    "the original spatial size.",
                    "**Strides, not max pooling**, whenever location matters — pooling "
                    "destroys position within the window.",
                    "**`Conv2DTranspose` learns to upsample**, undoing a strided convolution.",
                    "**IoU, not accuracy** — and check `sparse_y_true` / `sparse_y_pred` "
                    "against your data.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "…and the shift that SAM represents",
            "blocks": [
                {"t": "band",
                 "md": "A pretrained model that is **prompted rather than trained**, with no "
                       "predefined class list. It is the first model in this book that works "
                       "that way — and ==the pattern returns in every chapter from 15 "
                       "onwards=="},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_segment_anything.ipynb",
                     "href": "../../course-slides/notebooks/ch11/03_segment_anything.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 12 — Object detection",
                     "href": "../ch12/index.html"},
                ]},
            ],
        },
    ],
}
