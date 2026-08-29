random_train_labels = train_labels[:]        # salin
np.random.shuffle(random_train_labels)       # putus semua hubungan masukan-target

model = keras.Sequential([
    layers.Dense(512, activation="relu"),
    layers.Dense(10, activation="softmax"),
])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_images, random_train_labels,
          epochs=100, batch_size=128, validation_split=0.2)
