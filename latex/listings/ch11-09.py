model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=[foreground_iou])

callbacks = [keras.callbacks.ModelCheckpoint("segmentation.keras",
                                             save_best_only=True)]

history = model.fit(train_dataset, epochs=50,
                    validation_data=validation_dataset, callbacks=callbacks)
