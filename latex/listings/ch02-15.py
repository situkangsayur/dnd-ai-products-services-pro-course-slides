import tensorflow as tf

x = tf.Variable(3.0)
with tf.GradientTape() as tape:
    y = 2 * x + 3
print(tape.gradient(y, x))          # dy/dx = 2

# turunan kedua: pita bersarang
time = tf.Variable(0.0)
with tf.GradientTape() as outer_tape:
    with tf.GradientTape() as inner_tape:
        position = 4.9 * time ** 2
    speed = inner_tape.gradient(position, time)
acceleration = outer_tape.gradient(speed, time)
print(acceleration)                 # 9.8
