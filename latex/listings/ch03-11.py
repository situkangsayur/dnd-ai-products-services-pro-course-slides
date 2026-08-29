import keras

class SimpleDense(keras.Layer):
    def __init__(self, units, activation=None):
        super().__init__()
        self.units = units
        self.activation = activation

    def build(self, input_shape):          # dipanggil sekali, saat masukan pertama tiba
        batch_dim, input_dim = input_shape
        self.W = self.add_weight(shape=(input_dim, self.units),
                                 initializer="random_normal")
        self.b = self.add_weight(shape=(self.units,), initializer="zeros")

    def call(self, inputs):
        y = keras.ops.matmul(inputs, self.W) + self.b
        return self.activation(y) if self.activation is not None else y

my_dense = SimpleDense(units=32, activation=keras.ops.relu)
output = my_dense(keras.ops.ones(shape=(2, 784)))
print(output.shape)
