# lintasan maju tanpa keadaan
outputs, non_trainable_weights = model.stateless_call(
    trainable_weights, non_trainable_weights, inputs)

def compute_loss_and_updates(trainable_variables, non_trainable_variables,
                             inputs, targets):
    outputs, non_trainable_variables = model.stateless_call(
        trainable_variables, non_trainable_variables, inputs, training=True)
    loss = loss_fn(targets, outputs)
    return loss, non_trainable_variables      # skalar DULU, sisanya jadi 'aux'

# jax.grad hanya menerima fungsi yang mengembalikan skalar -> pakai has_aux
grad_fn = jax.value_and_grad(compute_loss_and_updates, has_aux=True)
(loss, non_trainable_weights), gradients = grad_fn(
    trainable_variables, non_trainable_variables, inputs, targets)

# optimizer pun punya keadaan (momentum dll), jadi ada padanan tanpa-keadaannya
trainable_variables, optimizer_variables = optimizer.stateless_apply(
    optimizer_variables, gradients, trainable_variables)
