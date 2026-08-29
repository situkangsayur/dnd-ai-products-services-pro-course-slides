inputs = keras.Input(shape=(32, 32, 3))
x = layers.Conv2D(32, 3, activation="relu")(inputs)
residual = x

x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)
x = layers.MaxPooling2D(2, padding="same")(x)           # halves the spatial size

residual = layers.Conv2D(64, 1, strides=2)(residual)    # halve the residual too
x = layers.add([x, residual])
