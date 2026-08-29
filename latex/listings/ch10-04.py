images_per_row = 16

for layer_name, layer_activation in zip(layer_names, activations):
    n_features = layer_activation.shape[-1]
    size = layer_activation.shape[1]
    n_cols = n_features // images_per_row
    display_grid = np.zeros(((size + 1) * n_cols - 1,
                             images_per_row * (size + 1) - 1))
    for col in range(n_cols):
        for row in range(images_per_row):
            channel_image = standardise(
                layer_activation[0, :, :, col * images_per_row + row])
            display_grid[col * (size + 1): (col + 1) * size + col,
                         row * (size + 1): (row + 1) * size + row] = channel_image
