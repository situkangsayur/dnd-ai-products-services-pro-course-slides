x = layers.Conv2D(32, 3, use_bias=False)(x)     # no bias here
x = layers.BatchNormalization()(x)
x = layers.Activation("relu")(x)
