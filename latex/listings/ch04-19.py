predictions = model.predict(x_test)
predicted = predictions.argmax(axis=1)

print((predicted == test_labels).mean())          # overall accuracy
print(predictions[0].max())                       # confidence on the first one

import collections
print(collections.Counter(test_labels).most_common(3))   # class imbalance
