a = tf.ones((2, 2))
b = tf.square(a)                   # element-wise
c = tf.sqrt(a)                     # element-wise
d = b + c                          # element-wise
e = tf.matmul(a, b)                # matrix product
f = tf.concat((a, b), axis=0)      # note: 'axis'

def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)
