k, num_epochs, all_scores = 4, 50, []
num_val_samples = len(x_train) // k

for i in range(k):
    fold_x_val = x_train[i * num_val_samples : (i + 1) * num_val_samples]
    fold_y_val = y_train[i * num_val_samples : (i + 1) * num_val_samples]
    fold_x_train = np.concatenate(
        [x_train[: i * num_val_samples], x_train[(i + 1) * num_val_samples :]], axis=0)
    fold_y_train = np.concatenate(
        [y_train[: i * num_val_samples], y_train[(i + 1) * num_val_samples :]], axis=0)

    model = get_model()                 # a FRESH model every fold
    model.fit(fold_x_train, fold_y_train, epochs=num_epochs, batch_size=16, verbose=0)
    val_loss, val_mae = model.evaluate(fold_x_val, fold_y_val, verbose=0)
    all_scores.append(val_mae)
