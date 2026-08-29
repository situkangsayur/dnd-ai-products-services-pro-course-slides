layers.Conv2D(output_depth, (window_height, window_width))

# the same kernel is reused for every patch, which is why the layer is
# translation invariant and why it has so few parameters
