import tensorflow as tf

tf.ones(shape=(2, 1))
tf.zeros(shape=(2, 1))
tf.constant([1.0, 2.0])            # KEKAL - tidak bisa ditugasi ulang

v = tf.Variable(initial_value=tf.random.normal(shape=(3, 1)))
v.assign(tf.ones((3, 1)))          # ganti seluruh nilainya
v[0, 0].assign(3.0)                # ganti sebagiannya
v.assign_add(tf.ones((3, 1)))      # += yang efisien

a = tf.ones((2, 2))
e = tf.matmul(a, tf.square(a))
f = tf.concat((a, e), axis=0)      # perhatikan: 'axis'
