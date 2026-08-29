my_dense = SimpleDense(units=32, activation=keras.ops.relu)

input_tensor = keras.ops.ones(shape=(2, 784))
output_tensor = my_dense(input_tensor)
print(output_tensor.shape)
