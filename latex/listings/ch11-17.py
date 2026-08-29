input_point = np.array([[580, 450],      # on the peach   -> include
                        [300, 800]])     # on the table   -> exclude
input_label = np.array([1, 0])           # 1 = foreground, 0 = background

outputs = model.predict({
    "images": ops.expand_dims(image, axis=0),
    "points": ops.expand_dims(input_point, axis=0),
    "labels": ops.expand_dims(input_label, axis=0),
})
