masks = outputs["masks"][0]
scores = outputs["iou_pred"][0]

best = int(np.argmax(scores))
mask = masks[best]
print(mask.shape, float(scores[best]))
