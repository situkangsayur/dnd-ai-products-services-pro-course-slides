metric = keras.metrics.SparseCategoricalAccuracy()
targets = ops.array([0, 1, 2])
predictions = ops.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])
metric.update_state(targets, predictions)
print(f"result: {metric.result():.2f}")
