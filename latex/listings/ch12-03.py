metadata = {}
for annotation in annotations["annotations"]:
    id = annotation["image_id"]
    metadata.setdefault(id, {"boxes": [], "labels": []})
    image = images[id]
    metadata[id]["boxes"].append(
        scale_box(annotation["bbox"], image["width"], image["height"]))
    metadata[id]["labels"].append(annotation["category_id"])
    metadata[id]["path"] = images_path + "/train2017/" + image["file_name"]

metadata = list(metadata.values())
