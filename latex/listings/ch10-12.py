import jax

grad_fn = jax.grad(compute_loss)          # differentiates w.r.t. its first argument

@jax.jit
def gradient_ascent_step(image, filter_index, learning_rate):
    grads = grad_fn(image, filter_index)
    grads = ops.normalize(grads)
    return image + learning_rate * grads
