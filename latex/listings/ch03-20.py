history = model.fit(
    training_inputs, training_targets,
    epochs=5, batch_size=16,
    validation_data=(val_inputs, val_targets),
)
print(history.history.keys())

loss_and_metrics = model.evaluate(val_inputs, val_targets, batch_size=128)
predictions = model.predict(new_inputs, batch_size=128)
