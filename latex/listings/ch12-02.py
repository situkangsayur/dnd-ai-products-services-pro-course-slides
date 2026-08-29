with open(f"{annotations_path}/annotations/instances_train2017.json") as f:
    annotations = json.load(f)
images = {image["id"]: image for image in annotations["images"]}

def scale_box(box, width, height):
    scale = 1.0 / max(width, height)          # longest side becomes 1.0
    x, y, w, h = [v * scale for v in box]
    x += (height - width) * scale / 2 if height > width else 0    # centre the
    y += (width - height) * scale / 2 if width > height else 0    # short side
    return [x, y, w, h]

metadata = {}
for annotation in annotations["annotations"]:
    id = annotation["image_id"]
    metadata.setdefault(id, {"boxes": [], "labels": []})
    image = images[id]
    metadata[id]["boxes"].append(scale_box(annotation["bbox"],
                                           image["width"], image["height"]))
    metadata[id]["labels"].append(annotation["category_id"])
    metadata[id]["path"] = images_path + "/train2017/" + image["file_name"]
