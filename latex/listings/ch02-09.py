test_digits = test_images[0:10]
predictions = model.predict(test_digits)

print(predictions[0].argmax())      # which class?
print(predictions[0].max())         # how confident?
print(test_labels[0])               # what was the truth?
