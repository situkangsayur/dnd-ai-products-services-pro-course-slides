predictions = model.predict(x_test)
print(predictions[:5].ravel())

positive = predictions > 0.5        # the threshold is a CHOICE, not a given
print(positive[:5].ravel())
