import tensorflow as tf

x = tf.Variable(3.0)
with tf.GradientTape() as tape:
    y = 2 * x + 3

print(tape.gradient(y, x))      # dy/dx
