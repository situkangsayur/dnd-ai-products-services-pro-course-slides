import tensorflow as tf

tf.ones(shape=(2, 1))
tf.constant([1.0, 2.0])            # IMMUTABLE — cannot be assigned into

v = tf.Variable(initial_value=tf.random.normal(shape=(3, 1)))
v.assign(tf.ones((3, 1)))          # replace the whole value
v[0, 0].assign(3.0)                # replace part of it
v.assign_add(tf.ones((3, 1)))      # an efficient +=
