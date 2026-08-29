def compute_loss(state, inputs, targets):
    W, b = state
    predictions = jnp.matmul(inputs, W) + b
    return jnp.mean(jnp.square(targets - predictions))

grad_fn = jax.value_and_grad(compute_loss)      # function -> gradient function
loss, grads = grad_fn((W, b), inputs, targets)  # grads mirrors the shape of state
