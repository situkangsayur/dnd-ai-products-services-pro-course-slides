tensorboard = keras.callbacks.TensorBoard(log_dir="/full_path_to_your_log_dir")
model.fit(train_images, train_labels, epochs=10,
          validation_data=(val_images, val_labels),
          callbacks=[tensorboard])
