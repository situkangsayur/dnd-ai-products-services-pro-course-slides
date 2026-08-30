# -*- coding: utf-8 -*-
"""Chapter 12 — Object detection.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 12
(pp. 329-350), read from the book PDF.

Two-stage versus single-stage detectors, a simplified YOLO built from scratch
on COCO, and a pretrained RetinaNet. The chapter is honest that the from-scratch
model stays undertrained -- and says why that is still worth doing.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_TWOSTAGE = """
flowchart LR
  I["Input image"]
  R["<b>Stage 1</b><br/>Region proposal<br/><small>a few thousand overlapping<br/>object-like boxes</small>"]
  C["<b>Stage 2</b><br/>ConvNet classifier<br/><small>classify each proposal</small>"]
  F["Discard low scores,<br/>refine the survivors"]
  O["Final detections"]
  I --> R --> C --> F --> O
"""

MMD_SINGLESTAGE = """
flowchart LR
  I["Input image"]
  B["ConvNet backbone"]
  H["Detection head<br/><small>boxes AND labels,<br/>predicted jointly</small>"]
  O["Final detections"]
  I --> B --> H --> O
"""

MMD_YOLOGRID = """
flowchart TB
  IMG["Image divided into<br/>an S x S grid"]
  D["Each grid cell predicts"]
  B["1 bounding box<br/><small>4 numbers</small>"]
  CF["1 confidence score<br/><small>1 number</small>"]
  CL["Class probabilities<br/><small>91 numbers</small>"]
  IMG --> D
  D --> B
  D --> CF
  D --> CL
"""

MMD_YOLOHEAD = """
flowchart LR
  A["Backbone output<br/><code>14 x 14 x 2048</code><br/><small>401,408 floats</small>"]
  B["Strided Conv2D 512<br/><code>6 x 6 x 512</code><br/><small>18,432 floats</small>"]
  C["Flatten + Dense 2048<br/>+ Dropout 0.5"]
  D["Dense 6*6*96<br/>then Reshape<br/><code>6 x 6 x 96</code>"]
  E["box: <code>[..., :5]</code>"]
  F["class: <code>[..., 5:]</code><br/>softmax"]
  A --> B --> C --> D
  D --> E
  D --> F
"""

MMD_CONF = """
flowchart TB
  Q{"Does this grid cell<br/>contain an object?"}
  Z["Target confidence = 0"]
  I["Target confidence =<br/><b>IoU</b> between the predicted<br/>box and the true box"]
  Q -- "no" --> Z
  Q -- "yes" --> I
  I -. "as boxes improve,<br/>so does the target" .-> I
"""

MMD_SCALE = """
flowchart TB
  subgraph Y["Our YOLO"]
    direction TB
    Y1["Use only the FINAL<br/>backbone output"] --> Y2["Features map to large<br/>areas of the image"]
    Y2 --> Y3["Poor at small objects"]
  end
  subgraph R["RetinaNet"]
    direction TB
    R1["Use features from<br/>SEVERAL depths"] --> R2["Fine and coarse features<br/>available together"]
    R2 --> R3["Handles small and large<br/>objects at once"]
  end
  Y ~~~ R
"""


MMD_COCO = """
flowchart LR
  Z1["train2017.zip<br/><small>18 GB of images,<br/>no labels</small>"]
  Z2["annotations.zip<br/><small>one JSON:<br/>image IDs and boxes</small>"]
  J["Join on image ID"]
  S["Rescale every box<br/>to a unit square"]
  M["metadata:<br/>boxes, labels, path<br/>per image"]
  Z1 --> J
  Z2 --> J
  J --> S --> M
"""

MMD_GRIDCOORD = """
flowchart LR
  A["Box in image coordinates<br/><code>x, y, w, h</code> in [0,1]"]
  B["to_grid()"]
  C["Cell index <code>(ix, iy)</code><br/>+ offset within the cell"]
  D["from_grid()"]
  A --> B --> C
  C --> D --> A
"""

NB = ["01_coco_and_boxes.ipynb", "02_yolo_from_scratch.ipynb",
      "03_pretrained_retinanet.ipynb"]

DECK = {
    "id": "ch12",
    "kind": "chapter",
    "number": 12,
    "title": "Object Detection",
    "subtitle": "Boxes and labels, predicted together — a simplified YOLO built from "
                "scratch, and a pretrained detector that generalises to a pointillist "
                "painting.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 12",
    "source_url": chapter_url(12),
    "duration": "2.5 hours",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(12, local_notebooks=NB),
    "objectives": [
        "Say when to use **detection rather than segmentation**, on both compute and "
        "labelling grounds.",
        "Distinguish **two-stage (R-CNN)** from **single-stage (YOLO, RetinaNet, "
        "SSD)** detectors, and name the trade-off.",
        "Build a **YOLO detection head** on a pretrained backbone, and read the "
        "shape of its grid output.",
        "Explain why the **confidence target is an IoU score** rather than a 0/1 "
        "flag.",
        "Run a **pretrained RetinaNet**, and explain why it handles small and large "
        "objects better.",
        "Say why single-stage detectors are **more robust to unfamiliar inputs** "
        "than two-stage ones.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "What detection is for",
            "blocks": [
                {"t": "p", "md": "A detector draws boxes around objects and labels them, so "
                                 "you know not just **which** objects are present but "
                                 "**where**."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔢", "h": "Counting",
                     "p": "How many instances of an object are in this image."},
                    {"ico": "🎞", "h": "Tracking",
                     "p": "Run detection on every frame to follow objects over time."},
                    {"ico": "✂", "h": "Cropping",
                     "p": "Cut out the region containing an object and send a "
                          "higher-resolution patch to a classifier or an OCR model."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "If segmentation is a superset, why detect at all?",
            "blocks": [
                {"t": "p", "md": "A fair question: given an instance mask you can already "
                                 "compute the smallest box containing it. **Segmentation is a "
                                 "strict superset of detection.**"},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "⚡", "h": "Computational cost",
                     "p": "A good detector typically runs **much faster** than a segmentation "
                          "model.", "style": "good"},
                    {"ico": "🏷", "h": "Labelling cost",
                     "p": "Segmentation needs **pixel-precise masks**, far more "
                          "time-consuming to produce than bounding boxes.", "style": "good"},
                ]},
                {"t": "band",
                 "md": "So the rule: **always use a detector if you do not need pixel-level "
                       "information** — for instance if all you want is ==to count things=="},
            ],
        },

        {"type": "section", "num": "01", "title": "Two-stage vs single-stage",
         "lead": "Two broad families, and why one of them won."},

        {
            "type": "slide",
            "kicker": "Section 12.1.1",
            "title": "Two-stage: propose, then classify",
            "blocks": [
                {"t": "mmd", "id": "ch12-twostage", "src": MMD_TWOSTAGE,
                 "cap": "Figure 12.2 — an R-CNN extracts region proposals, then classifies "
                        "each one with a ConvNet."},
                {"t": "p", "md": "The first stage is **not very smart**: it produces boxes "
                                 "around areas that merely *look object-like*. The second "
                                 "stage decides what, if anything, is in each one."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.1.1",
            "title": "Why that is expensive",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "It works well, but it requires classifying **thousands of patches for "
                       "every single image**. That rules it out for most real-time "
                       "applications and for embedded systems."},
                {"t": "p", "md": "The book's practical take is blunt: you rarely need R-CNN at "
                                 "all. **With a large server GPU you are usually better off "
                                 "with a segmentation model** like SAM; **if you are "
                                 "resource-constrained you want a single-stage detector**. "
                                 "==Neither case points at a two-stage model.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.1.2",
            "title": "Single-stage: predict both at once",
            "blocks": [
                {"t": "mmd", "id": "ch12-singlestage", "src": MMD_SINGLESTAGE,
                 "cap": "One model jointly predicts box coordinates and labels."},
                {"t": "p", "md": "The main families are **RetinaNet**, **SSD** (Single Shot "
                                 "MultiBox Detector), and the **YOLO** family — *You Only Look "
                                 "Once*, named after the meme on purpose."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.1.2",
            "title": "The trade-off, and the state of play",
            "blocks": [
                {"t": "bullets", "items": [
                    "Single-stage detectors are **significantly faster and more efficient** "
                    "than two-stage ones, with a **minor potential trade-off in accuracy**.",
                    "**YOLO is arguably the most popular object detection model there is**, "
                    "especially for real-time applications.",
                    "A new version appears roughly every year — and interestingly, "
                    "==each new version tends to come from a different organisation==.",
                ]},
                {"t": "p", "md": "There were twelve YOLO versions at the time of writing. This "
                                 "chapter recreates **the original from 2015**, which is "
                                 "simpler to work with."},
            ],
        },

        {"type": "section", "num": "02", "title": "Training a YOLO model from scratch",
         "lead": "COCO, a grid, and a loss with an unusual target."},

        {
            "type": "slide",
            "kicker": "Section 12.2",
            "title": "An honest warning before starting",
            "blocks": [
                {"t": "band",
                 "md": "Building a detector is **an undertaking** — not because anything in it "
                       "is theoretically complex, but because there is ==a lot of code just "
                       "to manipulate bounding boxes and predicted output=="},
                {"t": "p", "md": "The dataset is **COCO** — *Common Objects in Context* — one "
                                 "of the best-known detection datasets. It ships object "
                                 "labels, bounding boxes, and full segmentation masks; this "
                                 "chapter uses only the boxes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.1 · listing 12.1",
            "title": "Downloading COCO",
            "blocks": [
                {"t": "p", "md": "Two archives: the images, and a JSON of annotations. At "
                                 "**18 GB** this is the largest dataset in the book — though "
                                 "the book notes it is not large by modern standards."},
                {"t": "code", "lang": "python", "file": "listing 12.1 — the 2017 COCO dataset",
                 "src": """images_path = keras.utils.get_file(
    "coco",
    "http://images.cocodataset.org/zips/train2017.zip",
    extract=True,
)
annotations_path = keras.utils.get_file(
    "annotations",
    "http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
    extract=True,
)"""},
                {"t": "p", "md": "The first gives an **unlabelled directory of images**; the "
                                 "second gives all the metadata. They have to be joined."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.1",
            "title": "Joining images to their boxes",
            "blocks": [
                {"t": "mmd", "id": "ch12-coco", "src": MMD_COCO,
                 "cap": "COCO associates each image file with an ID, and each bounding box "
                        "with one of those IDs."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.1 · listing 12.2",
            "title": "…and normalising the coordinates while you are at it",
            "blocks": [
                {"t": "p", "md": "Boxes arrive as pixel coordinates from the top-left corner. "
                                 "Rescaling them into a unit square means the rest of the code "
                                 "**never has to check an image's size**."},
                {"t": "code", "lang": "python", "file": "listing 12.2 — parsing the annotations",
                 "src": """with open(f"{annotations_path}/annotations/instances_train2017.json") as f:
    annotations = json.load(f)
images = {image["id"]: image for image in annotations["images"]}

def scale_box(box, width, height):
    scale = 1.0 / max(width, height)          # longest side becomes 1.0
    x, y, w, h = [v * scale for v in box]
    x += (height - width) * scale / 2 if height > width else 0    # centre the
    y += (width - height) * scale / 2 if width > height else 0    # short side
    return [x, y, w, h]

"""},
                {"t": "band",
                 "md": "The two centring lines matter: images are not square, so scaling by "
                       "the longest side leaves letterboxing — and the boxes have to be "
                       "==shifted by half that gap== or every prediction is offset."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.1 · listing 12.2",
            "title": "…and collating it per image",
            "blocks": [
                {"t": "p", "md": "COCO stores one row per *annotation*, not per image, so the "
                                 "boxes belonging to one picture have to be gathered together."},
                {"t": "code", "lang": "python", "file": "aggregating by image ID",
                 "src": """metadata = {}
for annotation in annotations["annotations"]:
    id = annotation["image_id"]
    metadata.setdefault(id, {"boxes": [], "labels": []})
    image = images[id]
    metadata[id]["boxes"].append(
        scale_box(annotation["bbox"], image["width"], image["height"]))
    metadata[id]["labels"].append(annotation["category_id"])
    metadata[id]["path"] = images_path + "/train2017/" + image["file_name"]

metadata = list(metadata.values())"""},
                {"t": "p", "md": "The result is one record per image carrying **its boxes, its "
                                 "labels, and its file path** — which is what the target-array "
                                 "builder consumes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.2",
            "title": "The core idea: a grid of small predictors",
            "blocks": [
                {"t": "mmd", "id": "ch12-yologrid", "src": MMD_YOLOGRID,
                 "cap": "Figure 12.4 — each grid cell emits a box, a confidence, and a class "
                        "distribution."},
                {"t": "p", "md": "The original paper predicted several boxes per cell; this "
                                 "version keeps **one box per cell** for simplicity."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.2",
            "title": "Why a confidence score is needed at all",
            "blocks": [
                {"t": "p", "md": "Objects are not evenly distributed across a grid. **Most "
                                 "cells contain nothing**, and the model needs a way to say so."},
                {"t": "band",
                 "md": "So each cell also outputs a **confidence**: high where an object is "
                       "detected, near zero where there is none. ==Most cells should report "
                       "near-zero confidence==, and that is the correct behaviour, not a "
                       "failure."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.2 · listing 12.5",
            "title": "The backbone: ResNet, not Xception",
            "blocks": [
                {"t": "p", "md": "Same KerasHub pattern as chapter 8, with two deliberate "
                                 "changes: a different architecture, and a larger input size."},
                {"t": "code", "lang": "python", "file": "listing 12.5 — loading ResNet",
                 "src": """image_size = 448

backbone = keras_hub.models.Backbone.from_preset("resnet_50_imagenet")
preprocessor = keras_hub.layers.ImageConverter.from_preset(
    "resnet_50_imagenet",
    image_size=(image_size, image_size),
)"""},
                {"t": "bullets", "items": [
                    "**ResNet** is structurally similar to Xception but downsamples with "
                    "**strides instead of pooling** — and chapter 11 established that strides "
                    "preserve location, which detection needs.",
                    "**448 × 448** rather than 180 × 180: ==input size matters a great deal== "
                    "for detection, because small objects vanish at low resolution.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.2 · listing 12.6",
            "title": "The detection head",
            "blocks": [
                {"t": "p", "md": "The head proposed in the YOLO paper is simple: take the "
                                 "backbone output, push it through two dense layers, then "
                                 "split the result."},
                {"t": "code", "lang": "python", "file": "listing 12.6 — attaching the head",
                 "src": """grid_size, num_labels = 6, 91

inputs = keras.Input(shape=(image_size, image_size, 3))
x = backbone(inputs)
x = layers.Conv2D(512, (3, 3), strides=(2, 2))(x)      # shrink the feature map
x = layers.Flatten()(x)
x = layers.Dense(2048, activation="relu", kernel_initializer="glorot_normal")(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(grid_size * grid_size * (num_labels + 5))(x)
x = layers.Reshape((grid_size, grid_size, num_labels + 5))(x)

box_predictions = x[..., :5]                            # 4 box numbers + confidence
class_predictions = layers.Activation("softmax")(x[..., 5:])
model = keras.Model(inputs, {"box": box_predictions, "class": class_predictions})"""},
                {"t": "p", "md": "The `+ 5` is four box coordinates plus one confidence. "
                                 "Everything after that is the class distribution."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.2",
            "title": "Following the shapes through the head",
            "blocks": [
                {"t": "mmd", "id": "ch12-yolohead", "src": MMD_YOLOHEAD,
                 "cap": "The strided convolution exists purely to get the float count down to "
                        "something a dense layer can accept."},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "401,408", "l": "floats per image out of the backbone"},
                    {"v": "18,432", "l": "after the strided convolution"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.2",
            "title": "One design choice worth noticing",
            "blocks": [
                {"t": "band",
                 "md": "Because the **entire feature map is flattened** before the dense "
                       "layers, every grid detector can see features from **the whole image**. "
                       "There is ==no locality constraint=="},
                {"t": "p", "md": "That is deliberate: **large objects will not stay contained "
                                 "inside a single grid cell**, so a cell responsible for one "
                                 "needs to see beyond its own square."},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "77.8 M", "l": "total parameters"},
                    {"v": "297 MB", "l": "model size"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.3",
            "title": "Aligning the labels with the grid",
            "blocks": [
                {"t": "p", "md": "The model is simple; the data preparation is where the work "
                                 "is. Targets have to be rearranged into the same 6 × 6 grid "
                                 "the model predicts."},
                {"t": "band",
                 "md": "The assignment rule: **each grid detector is responsible for any box "
                       "whose centre falls inside its cell**. A box straddling several cells "
                       "still belongs to ==exactly one of them=="},
                {"t": "p", "md": "This is why the box format matters: the coordinates are "
                                 "stored as centre-x, centre-y, width, height, so the cell "
                                 "assignment is a direct lookup."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.3",
            "title": "Two coordinate systems, and the pair of functions between them",
            "blocks": [
                {"t": "mmd", "id": "ch12-gridcoord", "src": MMD_GRIDCOORD,
                 "cap": "The model predicts positions relative to a cell; the labels arrive "
                        "relative to the image."},
                {"t": "p", "md": "**`x` and `y` are relative to the grid cell** (0 to 1 within "
                                 "it), while **`w` and `h` stay relative to the whole image**. "
                                 "The widths and heights need no conversion; ==only the "
                                 "centres do=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.3",
            "title": "…written out",
            "blocks": [
                {"t": "p", "md": "Two small functions, exact inverses of one another — one to "
                                 "prepare targets, one to read predictions back."},
                {"t": "code", "lang": "python", "file": "converting to and from the grid",
                 "src": """def to_grid(box):
    x, y, w, h = box
    cx, cy = (x + w / 2) * grid_size, (y + h / 2) * grid_size   # centre, in cells
    ix, iy = int(cx), int(cy)                                   # which cell
    return (ix, iy), (cx - ix, cy - iy, w, h)                   # offset within it

def from_grid(loc, box):
    (xi, yi), (x, y, w, h) = loc, box
    x = (xi + x) / grid_size - w / 2
    y = (yi + y) / grid_size - h / 2
    return (x, y, w, h)"""},
                {"t": "band", "style": "amber",
                 "md": "Getting one of these subtly wrong is the classic detection bug: the "
                       "loss still falls, the boxes still appear, and they are ==consistently "
                       "in the wrong place=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.3 · listing 12.7",
            "title": "Building the two target arrays",
            "blocks": [
                {"t": "p", "md": "One array holds the class map, the other the boxes with "
                                 "their confidence — and the confidence in the **labels** is "
                                 "always exactly 1 or 0."},
                {"t": "code", "lang": "python", "file": "listing 12.7 — creating the targets",
                 "src": """class_array = np.zeros((len(metadata), grid_size, grid_size))
box_array = np.zeros((len(metadata), grid_size, grid_size, 5))

for index, sample in enumerate(metadata):
    for box, label in zip(sample["boxes"], sample["labels"]):
        (x, y, w, h) = box
        left, right = math.floor(x * grid_size), math.ceil((x + w) * grid_size)
        bottom, top = math.floor(y * grid_size), math.ceil((y + h) * grid_size)
        class_array[index, bottom:top, left:right] = label     # every cell it covers
        loc, grid_box = to_grid(box)
        box_array[index, loc[1], loc[0]] = (*grid_box, 1.0)    # only the CENTRE cell"""},
                {"t": "band",
                 "md": "Note the asymmetry: **the class map marks every cell the box "
                       "overlaps**, while **the box array marks only the cell containing its "
                       "centre**. Overlapping boxes are ==deliberately not handled==, to keep "
                       "the example readable."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.4",
            "title": "Two losses, summed",
            "blocks": [
                {"t": "p", "md": "The model has two outputs, so it needs two losses — exactly "
                                 "the multi-output pattern from chapter 7, where **Keras sums "
                                 "them during training**."},
                {"t": "table",
                 "head": ["Output", "Loss", "Note"],
                 "widths": [20, 34, 46],
                 "rows": [
                     ["**class**", "`sparse_categorical_crossentropy`", "Entirely ordinary."],
                     ["**box**", "Sum-squared error, custom",
                      "Computed **only for grid cells that actually contain a box** in the "
                      "labels."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.4",
            "title": "The clever part: what confidence is trained against",
            "blocks": [
                {"t": "mmd", "id": "ch12-conf", "src": MMD_CONF,
                 "cap": "The confidence target is not a flag — it is a measure of how good "
                        "the box currently is."},
                {"t": "p", "md": "The authors wanted confidence to reflect **not just the "
                                 "presence of an object but how good the predicted box is**. "
                                 "So as the model gets better at locating boxes, ==the IoU "
                                 "rises and the learned confidence rises with it=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.4 · listing 12.10",
            "title": "Computing IoU for a batch of boxes",
            "blocks": [
                {"t": "p", "md": "Chapter 11 used IoU as a metric; here it has to be "
                                 "differentiable and run inside the loss, so it is written "
                                 "with `keras.ops`."},
                {"t": "code", "lang": "python", "file": "listing 12.10 — intersection area",
                 "src": """from keras import ops

def unpack(box):
    return box[..., 0], box[..., 1], box[..., 2], box[..., 3]

def intersection(box1, box2):
    cx1, cy1, w1, h1 = unpack(box1)
    cx2, cy2, w2, h2 = unpack(box2)
    left   = ops.maximum(cx1 - w1 / 2, cx2 - w2 / 2)
    bottom = ops.maximum(cy1 - h1 / 2, cy2 - h2 / 2)
    right  = ops.minimum(cx1 + w1 / 2, cx2 + w2 / 2)
    top    = ops.minimum(cy1 + h1 / 2, cy2 + h2 / 2)
    return ops.maximum(0.0, right - left) * ops.maximum(0.0, top - bottom)""",
                 "run": [
                     {"line": 7, "note": "Two boxes, centre-width-height. Box 1 is "
                                         "the prediction.",
                      "vars": {"cx1,cy1": "5.0, 5.0", "w1,h1": "4.0, 4.0"}},
                     {"line": 8, "note": "Box 2 is the ground truth, offset to the "
                                         "upper right.",
                      "vars": {"cx2,cy2": "6.0, 6.0", "w2,h2": "4.0, 4.0"}},
                     {"line": 9, "note": "The intersection's left edge is the "
                                         "**rightmost** of the two left edges: "
                                         "max(3, 4).",
                      "vars": {"left": "4.0"}},
                     {"line": 11, "note": "…and its right edge is the leftmost of "
                                          "the two right edges: min(7, 8). Same "
                                          "trick, mirrored.",
                      "vars": {"right": "7.0"}},
                     {"line": 13, "note": "3 × 3 = 9. The `maximum(0.0, …)` is what "
                                          "makes disjoint boxes score zero instead "
                                          "of a negative area — try cx2 = 20.",
                      "vars": {"width": "3.0", "height": "3.0",
                               "intersection": "9.0"}},
                     {"line": 13, "note": "Union = 16 + 16 − 9 = 23, so IoU = 9/23 "
                                          "= 0.39. Below the 0.5 threshold: this "
                                          "prediction would not count as a match.",
                      "vars": {"union": "23.0", "IoU": "0.391"}},
                 ]},
                {"t": "band",
                 "md": "The `ops.maximum(0.0, ...)` at the end is what handles **boxes that "
                       "do not overlap at all**: a negative width would otherwise produce "
                       "==a spurious positive area=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.4 · listing 12.13",
            "title": "Running it, and reading the prediction",
            "blocks": [
                {"t": "p", "md": "Predictions come back as a grid, so drawing them means "
                                 "taking an argmax for the label at each cell and filtering "
                                 "by confidence."},
                {"t": "code", "lang": "python", "file": "listing 12.13 — visualising a prediction",
                 "src": """x, y = next(iter(val_dataset.rebatch(1)))
preds = model.predict(x)

boxes = preds["box"][0]
classes = np.argmax(preds["class"][0], axis=-1)      # most likely label per cell

draw_prediction(path, boxes, classes, cutoff=0.1)    # a LOW cutoff, deliberately"""},
                {"t": "p", "md": "The cutoff is set low because, as the next slide says "
                                 "plainly, ==the model is not a very good detector yet=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.4",
            "title": "The chapter says so out loud",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "Training takes **over an hour on a free Colab GPU**, and the model is "
                       "**still undertrained** — the validation loss is still falling when it "
                       "stops. It is starting to understand box locations and labels, "
                       "==but it is not accurate=="},
                {"t": "p", "md": "This is worth dwelling on: the book publishes a result that "
                                 "does not work well, and explains why. **The purpose of the "
                                 "exercise is to feel how detection training behaves**, not "
                                 "to produce a usable COCO detector."},
            ],
            "notes": "A good teaching moment about honest reporting — most tutorials would "
                     "quietly show only the one image that looks convincing.",
        },

        {
            "type": "slide",
            "kicker": "Section 12.2.4",
            "title": "What would actually be needed",
            "blocks": [
                {"t": "steps", "items": [
                    "**Train for more epochs** — the loss had not converged.",
                    "**Use the whole COCO dataset**, not the subset.",
                    "**Data augmentation** — translating and rotating both the images "
                    "**and their boxes**.",
                    "**Improve the class probability map** for overlapping boxes.",
                    "**Predict multiple boxes per grid location**, with a larger output grid.",
                ]},
                {"t": "band",
                 "md": "Together those approach the original YOLO training recipe. Doing it "
                       "properly would take ==a large amount of compute and time==, which is "
                       "the honest reason to reach for a pretrained detector instead."},
            ],
        },

        {"type": "section", "num": "03", "title": "A pretrained RetinaNet",
         "lead": "The same principles, with one important architectural difference."},

        {
            "type": "slide",
            "kicker": "Section 12.3",
            "title": "The difference that matters: scale",
            "blocks": [
                {"t": "mmd", "id": "ch12-scale", "src": MMD_SCALE,
                 "cap": "RetinaNet uses its ConvNet differently, to handle small and large "
                        "objects simultaneously."},
                {"t": "p", "md": "In our YOLO we used only the **final** backbone output. "
                                 "Those features map to large areas of the input, so they are "
                                 "==not very effective at finding small objects=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.3",
            "title": "Loading it, and the box format argument",
            "blocks": [
                {"t": "p", "md": "One line to instantiate — and one argument worth "
                                 "understanding, because box formats are a persistent source "
                                 "of silent errors."},
                {"t": "code", "lang": "python", "file": "loading RetinaNet",
                 "src": """detector = keras_hub.models.ObjectDetector.from_preset(
    "retinanet_resnet50_fpn_v2_coco",
    bounding_box_format="rel_xywh",     # same format as our YOLO, so the same
)                                       # drawing utilities work unchanged

predictions = detector.predict(image)"""},
                {"t": "band",
                 "md": "`rel` means **relative to the image size** — coordinates in [0, 1]. "
                       "Most Keras models and layers that handle boxes accept this argument, "
                       "and ==setting it wrongly produces boxes in the wrong place with no "
                       "error at all=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.3",
            "title": "What comes back",
            "blocks": [
                {"t": "p", "md": "Four outputs, structurally similar to the YOLO model's — "
                                 "with a fixed ceiling of 100 detections per image."},
                {"t": "code", "lang": "python", "file": "inspecting the prediction",
                 "src": """[(k, v.shape) for k, v in predictions.items()]
# [("boxes", (1, 100, 4)),
#  ("confidence", (1, 100)),
#  ("labels", (1, 100)),
#  ("num_detections", (1,))]

predictions["boxes"][0][0]"""},
                {"t": "out", "src": "array([0.53, 0.00, 0.81, 0.29], dtype=float32)"},
                {"t": "p", "md": "`num_detections` is the one to read first — the arrays are "
                                 "padded to 100, so **the rest is not meaningful**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.3 · listing 12.15",
            "title": "Drawing the detections",
            "blocks": [
                {"t": "p", "md": "Iterate only up to `num_detections`, and translate the "
                                 "numeric COCO label into a name."},
                {"t": "code", "lang": "python", "file": "listing 12.15 — running inference",
                 "src": """fig, ax = plt.subplots(dpi=300)
draw_image(ax, path)

num_detections = predictions["num_detections"][0]
for i in range(num_detections):
    box = predictions["boxes"][0][i]
    label = predictions["labels"][0][i]
    label_name = keras_hub.utils.coco_id_to_name(label)
    draw_box(ax, box, label_name, label_to_color(label))

plt.show()"""},
                {"t": "p", "md": "That is the whole of using a pretrained detector: load, "
                                 "predict, draw."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.3",
            "title": "The pointillist painting test",
            "blocks": [
                {"t": "band",
                 "md": "RetinaNet generalises to **a pointillist painting** with ease, despite "
                       "never having been trained on that style. Paintings and photographs "
                       "differ enormously at the pixel level but ==share a similar structure "
                       "at a high level=="},
                {"t": "p", "md": "And the book draws an architectural conclusion from it: this "
                                 "is **an advantage of single-stage detectors**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 12.3",
            "title": "Why single-stage is more robust to novelty",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔍", "h": "Two-stage",
                     "p": "Forced to classify **small patches in isolation** — which is extra "
                          "difficult when a small patch of pixels looks nothing like the "
                          "training data.", "style": "warn"},
                    {"ico": "🖼", "h": "Single-stage",
                     "p": "Can draw on features from **the entire input**, so it is more "
                          "robust to novel test-time inputs.", "style": "good"},
                ]},
                {"t": "p", "md": "Which connects back to chapter 5: robustness comes from "
                                 "==having more context to interpolate from==, not from "
                                 "having seen this exact style before."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Detection when you do not need pixels** — it is cheaper to run and far "
                    "cheaper to label than segmentation.",
                    "**Two-stage proposes then classifies**; **single-stage predicts boxes and "
                    "labels jointly** and is faster.",
                    "**YOLO divides the image into a grid**, and each cell predicts a box, a "
                    "confidence, and a class distribution.",
                    "**Confidence is trained against IoU**, not a 0/1 flag — so it measures "
                    "*how good* the box is, not only whether something is there.",
                    "**Input resolution matters** for detection, far more than for "
                    "classification.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "…and the two things worth carrying further",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📉", "h": "An honest negative result",
                     "p": "The from-scratch model **stays undertrained**, and the chapter says "
                          "so. Training a real COCO detector takes serious compute — which is "
                          "the argument for pretrained models, stated with evidence.",
                     "style": "warn"},
                    {"ico": "🖼", "h": "Robustness has a structural cause",
                     "p": "RetinaNet handles a painting it never saw because it reads the "
                          "**whole image**, and uses features from **several depths**.",
                     "style": "good"},
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_pretrained_retinanet.ipynb",
                     "href": "../../course-slides/notebooks/ch12/03_pretrained_retinanet.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 13 — Timeseries forecasting",
                     "href": "../ch13/index.html"},
                ]},
            ],
        },
    ],
}
