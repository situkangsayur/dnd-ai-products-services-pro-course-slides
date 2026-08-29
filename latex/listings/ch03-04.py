@tf.function
def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)

@tf.function(jit_compile=True)     # XLA: more aggressive, slower first compile
def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)
