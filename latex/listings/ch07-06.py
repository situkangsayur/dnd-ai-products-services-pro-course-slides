keras.utils.plot_model(
    model, "ticket_classifier.png")

# versi yang jauh lebih menolong
# saat mengawakutu:
keras.utils.plot_model(
    model,
    "ticket_classifier_with_shape_info.png",
    show_shapes=True,
    show_layer_names=True)
