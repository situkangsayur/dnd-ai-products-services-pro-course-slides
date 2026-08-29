model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(4, activation="relu"),          # the bottleneck
    layers.Dense(46, activation="softmax"),
])
