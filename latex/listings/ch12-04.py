image_size = 448

backbone = keras_hub.models.Backbone.from_preset("resnet_50_imagenet")
preprocessor = keras_hub.layers.ImageConverter.from_preset(
    "resnet_50_imagenet",
    image_size=(image_size, image_size),
)
