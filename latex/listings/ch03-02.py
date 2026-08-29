input_var = tf.Variable(3.0)
with tf.GradientTape() as tape:
    result = tf.square(input_var)
gradient = tape.gradient(result, input_var)

# konstanta harus 'ditonton' dulu
c = tf.constant(3.0)
with tf.GradientTape() as tape:
    tape.watch(c)
    result = tf.square(c)
gradient = tape.gradient(result, c)
