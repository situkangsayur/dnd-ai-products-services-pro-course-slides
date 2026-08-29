def model(inputs, W, b):
    return jnp.matmul(inputs, W) + b

def compute_loss(state, inputs, targets):
    W, b = state
    predictions = model(inputs, W, b)
    return jnp.mean(jnp.square(targets - predictions))

grad_fn = jax.value_and_grad(compute_loss)   # fungsi -> fungsi gradien

@jax.jit
def training_step(inputs, targets, W, b):
    loss, grads = grad_fn((W, b), inputs, targets)
    grad_W, grad_b = grads
    W = W - grad_W * 0.1
    b = b - grad_b * 0.1
    return loss, W, b                        # keadaan WAJIB dikembalikan
