from keras.datasets import california_housing

(train_data, train_targets), (test_data, test_targets) = (
    california_housing.load_data(version="small"))
# 480 latih, 120 uji, 8 fitur numerik per distrik

mean = train_data.mean(axis=0)
std = train_data.std(axis=0)
x_train = (train_data - mean) / std
x_test = (test_data - mean) / std      # PAKAI statistik data LATIH, bukan uji

y_train = train_targets / 100000       # skalakan target ke rentang yang wajar
y_test = test_targets / 100000
