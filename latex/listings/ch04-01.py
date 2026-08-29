from keras.datasets import imdb

(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=10000)

print(len(train_data), len(test_data))
print(train_data[0][:12])          # a review, as word indices
print(train_labels[0])             # 1 = positive, 0 = negative
