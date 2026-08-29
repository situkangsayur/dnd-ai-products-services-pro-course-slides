inputs = keras.Input(shape=(32, 32, 3))
x = layers.Conv2D(32, 3, activation="relu")(inputs)
residual = x                                            # 32 filters

x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)   # now 64 filters
residual = layers.Conv2D(64, 1)(residual)               # 1x1 projection to match

x = layers.add([x, residual])
