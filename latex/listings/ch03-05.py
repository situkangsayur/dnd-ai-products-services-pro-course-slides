learning_rate = 0.1

@tf.function(jit_compile=True)
def training_step(inputs, targets, W, b):
    with tf.GradientTape() as tape:
        predictions = model(inputs, W, b)
        loss = mean_squared_error(predictions, targets)
    grad_wrt_W, grad_wrt_b = tape.gradient(loss, [W, b])
    W.assign_sub(grad_wrt_W * learning_rate)      # in-place: W is a Variable
    b.assign_sub(grad_wrt_b * learning_rate)
    return loss

for step in range(40):
    loss = training_step(inputs, targets, W, b)
