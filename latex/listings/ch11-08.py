foreground_iou = keras.metrics.IoU(
    num_classes=3,
    target_class_ids=(0,),      # which class to score: 0 = foreground
    name="foreground_iou",
    sparse_y_true=True,         # our targets are integer class IDs
    sparse_y_pred=False,        # but our predictions are a dense softmax
)
