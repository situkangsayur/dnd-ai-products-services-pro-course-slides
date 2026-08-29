y_train = train_labels     # biarkan bulat
y_test = test_labels
# bentuknya (8982,)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])
