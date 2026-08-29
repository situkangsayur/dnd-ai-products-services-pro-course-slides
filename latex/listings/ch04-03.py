model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="adam",
              loss="binary_crossentropy",
              metrics=["accuracy"])

x_val, partial_x = x_train[:10000], x_train[10000:]
y_val, partial_y = y_train[:10000], y_train[10000:]

history = model.fit(
    partial_x, partial_y,
    epochs=20, batch_size=512,
    validation_data=(x_val, y_val))
