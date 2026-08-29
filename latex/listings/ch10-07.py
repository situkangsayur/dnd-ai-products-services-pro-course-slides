@tf.function
def gradient_ascent_step(image, filter_index, learning_rate):
    with tf.GradientTape() as tape:
        tape.watch(image)                     # the image is not a Variable, so watch it
        loss = compute_loss(image, filter_index)
    grads = tape.gradient(loss, image)        # gradient w.r.t. the IMAGE
    grads = ops.normalize(grads)              # the "gradient normalization trick"
    image += learning_rate * grads            # PLUS: we are ascending, not descending
    return image
