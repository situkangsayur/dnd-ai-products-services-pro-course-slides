conv_base = keras_hub.models.Backbone.from_preset(
    "xception_41_imagenet",
    trainable=False,
)

conv_base.trainable = True
print(len(conv_base.trainable_weights))     # before freezing
conv_base.trainable = False
print(len(conv_base.trainable_weights))     # after freezing
