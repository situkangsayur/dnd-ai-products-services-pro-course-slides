model.compile(
    optimizer=keras.optimizers.RMSprop(
        learning_rate=1e-2),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])
