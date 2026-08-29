y_train = train_labels      # leave as integers
y_test = test_labels
# shape (8982,)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])
