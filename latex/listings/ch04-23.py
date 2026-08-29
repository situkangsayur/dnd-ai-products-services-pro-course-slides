mean = train_data.mean(axis=0)
std = train_data.std(axis=0)

x_train = (train_data - mean) / std
x_test = (test_data - mean) / std      # TRAINING statistics, not the test set's

y_train = train_targets / 100000       # scale the target to a sane range
y_test = test_targets / 100000
