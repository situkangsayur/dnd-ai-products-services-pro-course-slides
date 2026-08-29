all_mae_histories = []
for i in range(k):
    # ... penyiapan lipatan sama seperti sebelumnya ...
    history = model.fit(fold_x_train, fold_y_train,
                        validation_data=(fold_x_val, fold_y_val),
                        epochs=200, batch_size=16, verbose=0)
    all_mae_histories.append(history.history["val_mean_absolute_error"])

average_mae_history = [
    np.mean([h[i] for h in all_mae_histories]) for i in range(200)
]
