keras.utils.plot_model(model, "ticket_classifier.png")

# far more useful while debugging:
keras.utils.plot_model(model, "ticket_classifier_with_shape_info.png",
                       show_shapes=True, show_layer_names=True)

print(model.layers[3].output)
