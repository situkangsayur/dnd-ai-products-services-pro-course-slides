class_array = np.zeros((len(metadata), grid_size, grid_size))
box_array = np.zeros((len(metadata), grid_size, grid_size, 5))

for index, sample in enumerate(metadata):
    for box, label in zip(sample["boxes"], sample["labels"]):
        (x, y, w, h) = box
        left, right = math.floor(x * grid_size), math.ceil((x + w) * grid_size)
        bottom, top = math.floor(y * grid_size), math.ceil((y + h) * grid_size)
        class_array[index, bottom:top, left:right] = label     # every cell it covers
        loc, grid_box = to_grid(box)
        box_array[index, loc[1], loc[0]] = (*grid_box, 1.0)    # only the CENTRE cell
