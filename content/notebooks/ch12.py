# -*- coding: utf-8 -*-
"""Chapter 12 notebooks — Object Detection."""

DECK = "ch12"

NOTEBOOKS = [
    {
        "file": "01_coco_and_boxes.ipynb",
        "title": "Boxes, formats, and IoU",
        "lede": "Before any model: the four box formats you will meet, the conversions "
                "between them, and the one metric the whole field is built on.",
        "needs": "CPU — about 2 minutes",
        "section": "01 — The object detection task",
        "cells": [
            ("h2", "Four ways to write the same box"),
            ("py", """import numpy as np

# One box around an object, written four ways.
xyxy = np.array([100., 150., 300., 400.])          # x_min, y_min, x_max, y_max
xywh = np.array([100., 150., 200., 250.])          # x_min, y_min, width, height
cxcywh = np.array([200., 275., 200., 250.])        # centre_x, centre_y, w, h
rel_xyxy = xyxy / np.array([640., 480., 640., 480.])   # normalized to [0, 1]

print(f"xyxy      {xyxy}")
print(f"xywh      {xywh}")
print(f"cxcywh    {cxcywh}")
print(f"rel_xyxy  {rel_xyxy.round(4)}")"""),
            ("warn",
             "This is where most object-detection bugs live.** COCO uses `xywh`, "
             "Pascal VOC uses `xyxy`, YOLO uses normalized `cxcywh`, and none of "
             "them will tell you when you have mixed them up — the boxes will "
             "simply be in the wrong place."),

            ("h2", "Conversions, written once"),
            ("py", """def xywh_to_xyxy(b):
    x, y, w, h = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack([x, y, x + w, y + h], axis=-1)

def cxcywh_to_xyxy(b):
    cx, cy, w, h = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], axis=-1)

def xyxy_to_cxcywh(b):
    x0, y0, x1, y1 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack([(x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0], axis=-1)

assert np.allclose(xywh_to_xyxy(xywh), xyxy)
assert np.allclose(cxcywh_to_xyxy(cxcywh), xyxy)
assert np.allclose(xyxy_to_cxcywh(xyxy), cxcywh)
print("all round-trips agree")"""),
            ("note",
             "Write the assertions. They cost nothing and they catch the "
             "conversion bug at the moment you introduce it rather than three "
             "hours later, in a picture."),

            ("h2", "Drawing them"),
            ("py", """import matplotlib.pyplot as plt
import matplotlib.patches as patches

rng = np.random.default_rng(0)
img = rng.random((480, 640, 3)) * 0.3 + 0.5

boxes = np.array([[100., 150., 300., 400.],
                  [350., 100., 560., 260.],
                  [420., 300., 600., 450.]])
labels = ["cat", "dog", "chair"]

fig, ax = plt.subplots(figsize=(8, 6))
ax.imshow(img)
for b, lab in zip(boxes, labels):
    x0, y0, x1, y1 = b
    ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, y1 - y0,
                                   fill=False, edgecolor="#ff7a1a", lw=2))
    ax.text(x0, y0 - 6, lab, color="#ff7a1a", fontsize=11, weight="bold")
ax.axis("off"); plt.show()"""),

            ("h2", "IoU: the metric everything rests on"),
            ("py", """def iou(a, b):
    \"\"\"Intersection over union, xyxy format.\"\"\"
    x0 = np.maximum(a[..., 0], b[..., 0])
    y0 = np.maximum(a[..., 1], b[..., 1])
    x1 = np.minimum(a[..., 2], b[..., 2])
    y1 = np.minimum(a[..., 3], b[..., 3])
    inter = np.clip(x1 - x0, 0, None) * np.clip(y1 - y0, 0, None)
    area_a = (a[..., 2] - a[..., 0]) * (a[..., 3] - a[..., 1])
    area_b = (b[..., 2] - b[..., 0]) * (b[..., 3] - b[..., 1])
    return inter / (area_a + area_b - inter + 1e-9)

truth = np.array([100., 150., 300., 400.])
for name, pred in [("perfect", truth),
                   ("slightly off", truth + 15),
                   ("half overlap", np.array([200., 150., 400., 400.])),
                   ("no overlap", np.array([400., 100., 550., 250.]))]:
    print(f"{name:14s} IoU {iou(pred, truth):.3f}")"""),
            ("out", """perfect        IoU 1.000
slightly off   IoU 0.7xx
half overlap   IoU 0.3xx
no overlap     IoU 0.000"""),

            ("h2", "Seeing what an IoU threshold means"),
            ("py", """fig, axes = plt.subplots(1, 5, figsize=(15, 3.4))
for ax, shift in zip(axes, [0, 20, 45, 75, 110]):
    pred = truth + shift
    ax.imshow(img)
    for b, c, lab in [(truth, "#12b886", "truth"), (pred, "#c0392b", "pred")]:
        x0, y0, x1, y1 = b
        ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, y1 - y0,
                                       fill=False, edgecolor=c, lw=2))
    ax.set_title(f"IoU {iou(pred, truth):.2f}", fontsize=11); ax.axis("off")
plt.suptitle("The standard threshold is 0.5. Is that strict enough for you?", y=1.03)
plt.tight_layout(); plt.show()"""),
            ("md",
             "**IoU 0.5 is a loose box.** It is the field's convention, not a "
             "law — and whether it is adequate depends entirely on what the box "
             "is used for downstream. A robot gripper needs 0.9; a photo-tagging "
             "feature does not."),

            ("h2", "Non-maximum suppression"),
            ("py", """def nms(boxes, scores, threshold=0.5):
    order = np.argsort(scores)[::-1]
    keep = []
    while len(order):
        i = order[0]
        keep.append(i)
        if len(order) == 1:
            break
        rest = order[1:]
        overlaps = np.array([iou(boxes[i], boxes[j]) for j in rest])
        order = rest[overlaps < threshold]
    return keep

# A detector fires several times on the same object.
raw = np.array([[100., 150., 300., 400.],
                [108., 158., 305., 405.],
                [ 95., 145., 298., 396.],
                [350., 100., 560., 260.]])
scores = np.array([0.92, 0.88, 0.79, 0.85])

kept = nms(raw, scores)
print(f"{len(raw)} raw detections -> {len(kept)} after NMS: {kept}")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
for ax, idx, title in [(a1, range(len(raw)), "raw detections"),
                       (a2, kept, "after NMS")]:
    ax.imshow(img)
    for i in idx:
        x0, y0, x1, y1 = raw[i]
        ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, y1 - y0,
                                       fill=False, edgecolor="#ff7a1a", lw=2))
        ax.text(x0, y0 - 6, f"{scores[i]:.2f}", color="#ff7a1a", fontsize=10)
    ax.set_title(title); ax.axis("off")
plt.tight_layout(); plt.show()"""),
            ("md",
             "Every dense detector produces overlapping duplicates by "
             "construction. **NMS is not a refinement — it is part of the "
             "output**, and its threshold is a real hyperparameter that trades "
             "missed adjacent objects against duplicate boxes."),
        ],
        "takeaways": [
            "Four box formats exist and none of them announce themselves. Write "
            "the conversions once, with assertions.",
            "IoU is the metric everything else is defined on top of.",
            "The conventional 0.5 threshold is looser than it sounds — look at "
            "the picture.",
            "NMS is part of a detector's output, and its threshold is a real "
            "trade-off.",
        ],
    },

    {
        "file": "02_yolo_from_scratch.ipynb",
        "title": "A single-stage detector, from scratch",
        "lede": "The YOLO idea in its simplest form: a grid, a fixed number of "
                "predictions per cell, and one loss combining classification with "
                "regression.",
        "needs": "GPU recommended — about 30 minutes on CPU",
        "section": "02 — Building a detector",
        "cells": [
            ("h2", "The central idea"),
            ("md",
             "Chapter 8's classifier answers *what is in this image*. A detector "
             "must answer *what, and where, and how many* — and the last part is "
             "what makes the output shape awkward, because it varies per image.\n\n"
             "**YOLO's answer: fix the output shape.** Divide the image into a "
             "grid; each cell predicts a fixed number of boxes and a class "
             "distribution. The number of predictions is now constant, and the "
             "problem becomes an ordinary supervised one."),
            ("py", """import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

IMG, GRID = 256, 8
CELL = IMG // GRID

rng = np.random.default_rng(1)
img = rng.random((IMG, IMG, 3)) * 0.25 + 0.6
box = np.array([70., 90., 190., 210.])
cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2

fig, ax = plt.subplots(figsize=(6.5, 6.5))
ax.imshow(img)
for k in range(1, GRID):
    ax.axhline(k * CELL, color="w", lw=.6)
    ax.axvline(k * CELL, color="w", lw=.6)
ax.add_patch(patches.Rectangle((box[0], box[1]), box[2]-box[0], box[3]-box[1],
                               fill=False, edgecolor="#ff7a1a", lw=2.5))
gx, gy = int(cx // CELL), int(cy // CELL)
ax.add_patch(patches.Rectangle((gx*CELL, gy*CELL), CELL, CELL,
                               facecolor="#12b886", alpha=.35))
ax.plot(cx, cy, "o", c="#12b886", ms=9)
ax.set_title(f"The object's centre falls in cell ({gx}, {gy})\\n"
             f"— that cell is responsible for predicting it")
ax.axis("off"); plt.show()"""),

            ("h2", "The output tensor"),
            ("py", """NUM_CLASSES = 3
BOXES_PER_CELL = 2

# Per cell: for each box, (x, y, w, h, objectness); plus one class distribution.
per_cell = BOXES_PER_CELL * 5 + NUM_CLASSES
print(f"output shape: ({GRID}, {GRID}, {per_cell})")
print(f"  {BOXES_PER_CELL} boxes x (x, y, w, h, objectness) = "
      f"{BOXES_PER_CELL * 5}")
print(f"  + {NUM_CLASSES} class scores")
print(f"total predictions per image: {GRID * GRID * BOXES_PER_CELL}")"""),
            ("md",
             "**128 candidate boxes for every image, always** — most of them "
             "predicting *nothing here*. That imbalance is the central "
             "difficulty of single-stage detection and the thing the loss has to "
             "handle."),

            ("h2", "Encoding a target"),
            ("py", """def encode(boxes, classes, grid=GRID, img_size=IMG,
           num_classes=NUM_CLASSES):
    target = np.zeros((grid, grid, 5 + num_classes), dtype="float32")
    cell = img_size / grid
    for b, c in zip(boxes, classes):
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        gx, gy = int(cx // cell), int(cy // cell)
        target[gy, gx, 0] = (cx - gx * cell) / cell     # offset WITHIN the cell
        target[gy, gx, 1] = (cy - gy * cell) / cell
        target[gy, gx, 2] = (b[2] - b[0]) / img_size    # size relative to image
        target[gy, gx, 3] = (b[3] - b[1]) / img_size
        target[gy, gx, 4] = 1.0                          # objectness
        target[gy, gx, 5 + c] = 1.0
    return target

t = encode([box], [1])
print("cells containing an object:", int(t[..., 4].sum()), "of", GRID * GRID)
print("that cell's vector:", t[gy, gx].round(3))"""),
            ("md",
             "Two different normalizations, and mixing them is a classic bug:\n"
             "- **Centre** is an offset *within its cell*, in [0, 1].\n"
             "- **Size** is relative to the *whole image*, in [0, 1].\n\n"
             "The first keeps the regression local and easy; the second lets one "
             "cell predict a box larger than itself."),

            ("h2", "The model"),
            ("py", """import keras
from keras import layers

def detector(grid=GRID, boxes_per_cell=BOXES_PER_CELL,
             num_classes=NUM_CLASSES, img_size=IMG):
    inputs = keras.Input(shape=(img_size, img_size, 3))
    x = layers.Rescaling(1./255)(inputs)
    for f in [32, 64, 128, 256, 512]:
        x = layers.Conv2D(f, 3, padding="same", use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.MaxPooling2D(2)(x)
    # 256 -> 8 after five halvings; the spatial grid IS the output grid.
    x = layers.Conv2D(256, 3, padding="same", activation="relu")(x)
    outputs = layers.Conv2D(boxes_per_cell * 5 + num_classes, 1)(x)
    return keras.Model(inputs, outputs)

model = detector()
print("output shape:", model.output.shape)
print(f"{model.count_params():,} parameters")"""),
            ("md",
             "**The backbone's spatial grid is the output grid.** No `Flatten`, "
             "no `Dense` — the last layer is a 1×1 convolution producing the "
             "per-cell vector. Everything from chapters 8 and 9 applies "
             "unchanged."),

            ("h2", "The loss: three terms, deliberately unequal"),
            ("py", """from keras import ops

LAMBDA_COORD = 5.0     # boxes matter more than the many empty cells
LAMBDA_NOOBJ = 0.5     # ...and empty cells must not drown everything

def detection_loss(y_true, y_pred, num_classes=NUM_CLASSES):
    obj = y_true[..., 4:5]                       # 1 where an object is
    noobj = 1.0 - obj

    xy_loss = ops.sum(obj * ops.square(y_true[..., 0:2] - y_pred[..., 0:2]))
    wh_loss = ops.sum(obj * ops.square(
        ops.sqrt(ops.maximum(y_true[..., 2:4], 1e-6))
        - ops.sqrt(ops.maximum(y_pred[..., 2:4], 1e-6))))
    obj_loss = ops.sum(obj * ops.square(y_true[..., 4:5] - y_pred[..., 4:5]))
    noobj_loss = ops.sum(noobj * ops.square(y_true[..., 4:5] - y_pred[..., 4:5]))
    cls_loss = ops.sum(obj * ops.square(
        y_true[..., 5:5+num_classes] - y_pred[..., 5:5+num_classes]))

    return (LAMBDA_COORD * (xy_loss + wh_loss)
            + obj_loss + LAMBDA_NOOBJ * noobj_loss + cls_loss)"""),
            ("md",
             "Three details that are all responses to the same imbalance:\n\n"
             "**`obj` masks almost every term.** Coordinates are only penalised "
             "where there is an object to have coordinates.\n\n"
             "**`LAMBDA_NOOBJ = 0.5`.** With 126 empty cells against 2 full "
             "ones, the objectness term would otherwise be dominated by cells "
             "learning to say *nothing here*, and the model would learn nothing "
             "else.\n\n"
             "**The square root on width and height.** A 10-pixel error on a "
             "20-pixel box matters far more than on a 200-pixel box; the square "
             "root compresses the large end so both are penalised comparably."),

            ("h2", "Decoding predictions back to boxes"),
            ("py", """def decode(pred, grid=GRID, img_size=IMG, num_classes=NUM_CLASSES,
           threshold=0.5):
    cell = img_size / grid
    boxes, scores, classes = [], [], []
    for gy in range(grid):
        for gx in range(grid):
            v = pred[gy, gx]
            if v[4] < threshold:
                continue
            cx = (gx + v[0]) * cell
            cy = (gy + v[1]) * cell
            w, h = v[2] * img_size, v[3] * img_size
            boxes.append([cx - w/2, cy - h/2, cx + w/2, cy + h/2])
            scores.append(float(v[4]))
            classes.append(int(np.argmax(v[5:5+num_classes])))
    return np.array(boxes), np.array(scores), np.array(classes)

b, s, c = decode(t)          # decode the target we encoded above
print("recovered:", b.round(1), "class", c, "score", s)
print("original: ", box)"""),
            ("md",
             "Encode then decode should return what you started with. **Test "
             "that round-trip before training anything** — an encoding bug is "
             "invisible in the loss curve and fatal in the output."),

            ("h2", "What this simple version does not have"),
            ("md",
             "| Missing | Why real detectors add it |\n"
             "|---|---|\n"
             "| **Anchor boxes** | Objects have characteristic shapes; "
             "predicting an offset from a prior beats predicting from scratch. |\n"
             "| **Multi-scale features** | One grid means one object size. FPNs "
             "detect at several resolutions. |\n"
             "| **Focal loss** | A principled replacement for `LAMBDA_NOOBJ` — "
             "downweights easy negatives continuously. |\n"
             "| **IoU-based losses** | GIoU and CIoU optimise the metric you "
             "actually report, rather than a proxy. |\n\n"
             "Notebook 03 uses a pretrained detector that has all four."),
        ],
        "takeaways": [
            "A grid with a fixed number of predictions per cell turns a "
            "variable-length output into a fixed one.",
            "Centre offsets are per-cell; sizes are per-image. Do not mix them.",
            "The loss must downweight empty cells or it learns only to say "
            "*nothing here*.",
            "Test the encode/decode round-trip before training — that bug is "
            "invisible in the loss.",
        ],
    },

    {
        "file": "03_pretrained_retinanet.ipynb",
        "title": "A pretrained detector, and reading its output honestly",
        "lede": "RetinaNet from KerasHub in three lines, then the part that matters: "
                "what the confidence threshold is actually trading, and how to choose "
                "it for your problem rather than the demo's.",
        "needs": "GPU recommended · downloads weights",
        "section": "03 — Using a pretrained detector",
        "cells": [
            ("h2", "Loading it"),
            ("py", """import keras
import keras_hub
import numpy as np
import matplotlib.pyplot as plt

detector = keras_hub.models.ObjectDetector.from_preset(
    "retinanet_resnet50_fpn_coco")
print(type(detector).__name__)"""),
            ("md",
             "Trained on COCO: 80 classes, 330,000 images. The same argument as "
             "chapters 8 and 11 — **whatever you train this week will not "
             "compete with this**, and the interesting question is what to do "
             "with it."),

            ("h2", "Running it"),
            ("py", """image_path = keras.utils.get_file(
    origin="https://img-datasets.s3.amazonaws.com/elephant.jpg")
image = np.array(keras.utils.load_img(image_path))

preds = detector.predict(image[np.newaxis, ...], verbose=0)
print({k: np.array(v).shape for k, v in preds.items()})"""),
            ("py", """import matplotlib.patches as patches

COCO = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
        "truck", "boat", "traffic light"]   # first ten; full list in the docs

def draw(image, boxes, classes, scores, threshold=0.5, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 7))
    ax.imshow(image)
    n = 0
    for b, c, s in zip(boxes, classes, scores):
        if s < threshold:
            continue
        n += 1
        x0, y0, x1, y1 = b
        ax.add_patch(patches.Rectangle((x0, y0), x1-x0, y1-y0, fill=False,
                                       edgecolor="#ff7a1a", lw=2))
        ax.text(x0, y0 - 6, f"{int(c)} {s:.2f}", color="#ff7a1a",
                fontsize=9, weight="bold")
    ax.set_title(f"threshold {threshold}: {n} detections")
    ax.axis("off")
    return ax

boxes = np.array(preds["boxes"][0])
classes = np.array(preds["classes"][0])
scores = np.array(preds["confidence"][0])
draw(image, boxes, classes, scores, 0.5)
plt.show()"""),

            ("h2", "The threshold is a decision, not a default"),
            ("py", """fig, axes = plt.subplots(1, 4, figsize=(19, 5))
for ax, t in zip(axes, [0.1, 0.3, 0.5, 0.8]):
    draw(image, boxes, classes, scores, t, ax=ax)
plt.tight_layout(); plt.show()"""),
            ("md",
             "Low threshold: everything found, plus things that are not there. "
             "High threshold: only what it is sure about, and it misses.\n\n"
             "**There is no correct value.** The right one depends on what a "
             "false positive costs against what a false negative costs, in your "
             "application — which is a business question wearing a "
             "hyperparameter's clothes."),

            ("h2", "The precision-recall curve, which is the honest picture"),
            ("py", """# With ground truth available you would sweep the threshold and plot
# precision against recall. Here is the shape of that computation.
def precision_recall(pred_boxes, pred_scores, true_boxes, iou_threshold=0.5):
    def iou(a, b):
        x0 = np.maximum(a[0], b[:, 0]); y0 = np.maximum(a[1], b[:, 1])
        x1 = np.minimum(a[2], b[:, 2]); y1 = np.minimum(a[3], b[:, 3])
        inter = np.clip(x1-x0, 0, None) * np.clip(y1-y0, 0, None)
        aa = (a[2]-a[0]) * (a[3]-a[1])
        bb = (b[:, 2]-b[:, 0]) * (b[:, 3]-b[:, 1])
        return inter / (aa + bb - inter + 1e-9)

    order = np.argsort(pred_scores)[::-1]
    matched = np.zeros(len(true_boxes), bool)
    tp, fp = [], []
    for i in order:
        if len(true_boxes) == 0:
            fp.append(1); tp.append(0); continue
        overlaps = iou(pred_boxes[i], true_boxes)
        j = overlaps.argmax()
        if overlaps[j] >= iou_threshold and not matched[j]:
            matched[j] = True; tp.append(1); fp.append(0)
        else:
            tp.append(0); fp.append(1)
    tp, fp = np.cumsum(tp), np.cumsum(fp)
    recall = tp / max(len(true_boxes), 1)
    precision = tp / np.maximum(tp + fp, 1)
    return precision, recall

print("Supply your own ground-truth boxes to plot this properly.")
print("mAP is the area under this curve, averaged over classes and")
print("over IoU thresholds from 0.5 to 0.95 -- which is why a single")
print("mAP number tells you much less than the curve it came from.")"""),

            ("h2", "Fine-tuning on your own classes"),
            ("py", """# The chapter-8 pattern, unchanged: keep the backbone, replace the head.
backbone = detector.backbone
backbone.trainable = False

print("backbone parameters:", f"{backbone.count_params():,}")
print("\\nThe procedure is the one from chapter 8:")
print("  1. freeze the backbone")
print("  2. train the new detection head to convergence")
print("  3. unfreeze the top of the backbone")
print("  4. retrain both at a much lower learning rate")"""),
            ("md",
             "One detail specific to detection: **your classes need boxes, not "
             "just labels**, and boxes are expensive to annotate. Chapter 11's "
             "SAM is the practical answer — use it to propose masks, derive "
             "boxes from them, and correct rather than draw."),

            ("h2", "What to check before deploying a detector"),
            ("md",
             "- **The threshold**, chosen from your own cost of a false positive "
             "against a false negative.\n"
             "- **The NMS threshold** — too aggressive and adjacent objects "
             "merge; too loose and you ship duplicates.\n"
             "- **The size distribution** of your objects against the model's "
             "training distribution. A detector trained on COCO is not tuned for "
             "objects that occupy 2% of the frame.\n"
             "- **What happens with zero objects.** The empty case is the one "
             "least often tested and most often encountered.\n"
             "- **Latency at your batch size**, warmed up — chapter 16's lesson "
             "about timing the compiler applies here too."),
        ],
        "takeaways": [
            "A pretrained detector is three lines and beats anything you will "
            "train this week.",
            "The confidence threshold is a cost decision, not a default.",
            "mAP hides the precision-recall curve it came from; look at the "
            "curve.",
            "Fine-tuning follows the chapter-8 procedure — but boxes are "
            "expensive, so consider SAM for annotation.",
        ],
    },
]
