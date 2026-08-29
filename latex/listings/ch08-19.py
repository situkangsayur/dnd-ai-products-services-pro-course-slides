model.compile(
    loss="binary_crossentropy",
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),    # note: 1e-5
    metrics=["accuracy"],
)

callbacks = [keras.callbacks.ModelCheckpoint(
    filepath="fine_tuning.keras", save_best_only=True, monitor="val_loss")]

history = model.fit(augmented_train_dataset, epochs=30,
                    validation_data=validation_dataset, callbacks=callbacks)
