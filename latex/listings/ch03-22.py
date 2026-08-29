predictions = model(new_inputs)                          # all at once
predictions = model.predict(new_inputs, batch_size=128)  # batched, returns NumPy
