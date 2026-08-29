callbacks_list = [
    keras.callbacks.EarlyStopping(
        monitor="accuracy",     # must be among the model's metrics
        patience=1,             # stop if it has not improved for one epoch
    ),
    keras.callbacks.ModelCheckpoint(
        filepath="checkpoint_path.keras",
        monitor="val_loss",
        save_best_only=True,    # only overwrite when val_loss improves
    ),
]

model.fit(train_images, train_labels, epochs=10,
          callbacks=callbacks_list,
          validation_data=(val_images, val_labels))   # REQUIRED: val_* is monitored
