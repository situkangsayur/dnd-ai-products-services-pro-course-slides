import keras_hub

model = keras_hub.models.Backbone.from_preset("xception_41_imagenet")
preprocessor = keras_hub.layers.ImageConverter.from_preset(
    "xception_41_imagenet", image_size=(180, 180))

for layer in model.layers:
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.SeparableConv2D)):
        print(layer.name)
