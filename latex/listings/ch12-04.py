grid_size, num_labels = 6, 91

inputs = keras.Input(shape=(image_size, image_size, 3))
x = backbone(inputs)
x = layers.Conv2D(512, (3, 3), strides=(2, 2))(x)      # shrink the feature map
x = layers.Flatten()(x)
x = layers.Dense(2048, activation="relu", kernel_initializer="glorot_normal")(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(grid_size * grid_size * (num_labels + 5))(x)
x = layers.Reshape((grid_size, grid_size, num_labels + 5))(x)

box_predictions = x[..., :5]                            # 4 box numbers + confidence
class_predictions = layers.Activation("softmax")(x[..., 5:])
model = keras.Model(inputs, {"box": box_predictions, "class": class_predictions})
