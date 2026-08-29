callbacks_list = [
    keras.callbacks.EarlyStopping(
        monitor="accuracy",     # dipantau, jadi harus ada di metrics model
        patience=1,             # berhenti bila tak membaik lebih dari satu epoch
    ),
    keras.callbacks.ModelCheckpoint(
        filepath="checkpoint_path.keras",
        monitor="val_loss",
        save_best_only=True,    # berkas tidak ditimpa kecuali val_loss membaik
    ),
]

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_images, train_labels, epochs=10,
          callbacks=callbacks_list,
          validation_data=(val_images, val_labels))   # WAJIB, karena val_* dipantau
