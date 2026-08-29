import numpy as np

input_point = np.array([[580, 450]])     # coordinates of the point
input_label = np.array([1])              # 1 = foreground, 0 = background

outputs = model.predict({
    "images": ops.expand_dims(image, axis=0),
    "points": ops.expand_dims(input_point, axis=0),
    "labels": ops.expand_dims(input_label, axis=0),
})
