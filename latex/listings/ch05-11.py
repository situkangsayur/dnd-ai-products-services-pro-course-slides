model = keras.Sequential([layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
history_small = model.fit(train_images, train_labels,
                          epochs=20, batch_size=128, validation_split=0.2)
