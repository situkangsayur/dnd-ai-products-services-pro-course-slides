import keras_hub

conv_base = keras_hub.models.Backbone.from_preset("xception_41_imagenet")

preprocessor = keras_hub.layers.ImageConverter.from_preset(
    "xception_41_imagenet",
    image_size=(180, 180),
)
