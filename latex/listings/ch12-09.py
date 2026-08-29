detector = keras_hub.models.ObjectDetector.from_preset(
    "retinanet_resnet50_fpn_v2_coco",
    bounding_box_format="rel_xywh",     # same format as our YOLO, so the same
)                                       # drawing utilities work unchanged

predictions = detector.predict(image)
