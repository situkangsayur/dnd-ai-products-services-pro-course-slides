test_digits = test_images[0:10]
predictions = model.predict(test_digits)
print(predictions[0].argmax(), predictions[0].max(), test_labels[0])
