conv_base.trainable = True
for layer in conv_base.layers[:-4]:
    layer.trainable = False
