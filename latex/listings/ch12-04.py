x, y = next(iter(val_dataset.rebatch(1)))
preds = model.predict(x)

boxes = preds["box"][0]
classes = np.argmax(preds["class"][0], axis=-1)      # most likely label per cell

draw_prediction(path, boxes, classes, cutoff=0.1)    # a LOW cutoff, deliberately
