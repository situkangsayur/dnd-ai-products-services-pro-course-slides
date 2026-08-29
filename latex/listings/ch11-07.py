# input (100, 100, 64)
Conv2D(128, 3, strides=2, padding="same")           # -> (50, 50, 128)

# input (50, 50, 128)
Conv2DTranspose(64, 3, strides=2, padding="same")   # -> (100, 100, 64)
