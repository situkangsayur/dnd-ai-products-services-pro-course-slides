from keras.utils import to_categorical

y_train = to_categorical(train_labels)
y_test = to_categorical(test_labels)
# shape (8982, 46)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"])
