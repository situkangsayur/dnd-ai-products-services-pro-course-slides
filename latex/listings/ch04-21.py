from keras.datasets import california_housing

(train_data, train_targets), (test_data, test_targets) = (
    california_housing.load_data(version="small"))

print(train_data.shape, test_data.shape)
print(train_targets[:4])
