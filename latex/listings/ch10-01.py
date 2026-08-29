import keras

model = keras.models.load_model("convnet_from_scratch_with_augmentation.keras")

layer_outputs, layer_names = [], []
for layer in model.layers:
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.MaxPooling2D)):
        layer_outputs.append(layer.output)
        layer_names.append(layer.name)

activation_model = keras.Model(inputs=model.input, outputs=layer_outputs)
