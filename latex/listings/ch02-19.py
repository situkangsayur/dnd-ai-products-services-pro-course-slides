model = NaiveSequential([
    NaiveDense(input_size=28 * 28, output_size=512, activation=ops.relu),
    NaiveDense(input_size=512, output_size=10, activation=ops.softmax),
])
fit(model, train_images, train_labels, epochs=10, batch_size=128)

predictions = model(test_images)
predicted_labels = ops.argmax(predictions, axis=1)
matches = predicted_labels == test_labels
print(f"accuracy: {ops.mean(matches):.2f}")
