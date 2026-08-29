model.compile(
    optimizer=keras.optimizers.RMSprop(
        learning_rate=1.0),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])
