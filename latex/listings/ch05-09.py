model = keras.Sequential([layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
history_small_model = model.fit(train_images, train_labels,
                                epochs=20, batch_size=128, validation_split=0.2)

# catatan: saat melatih model besar, kecilkan batch_size agar memori tidak jebol
#          (batch_size=32 pada versi 3 x 2048 unit)
