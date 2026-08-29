def evaluate_naive_method(dataset):
    total_abs_err, samples_seen = 0.0, 0
    for samples, targets in dataset:
        # column 1 is temperature; un-normalise it back to degrees Celsius
        preds = samples[:, -1, 1] * std[1] + mean[1]
        total_abs_err += np.sum(np.abs(preds - targets))
        samples_seen += samples.shape[0]
    return total_abs_err / samples_seen

print(f"Validation MAE: {evaluate_naive_method(val_dataset):.2f}")
print(f"Test MAE: {evaluate_naive_method(test_dataset):.2f}")
