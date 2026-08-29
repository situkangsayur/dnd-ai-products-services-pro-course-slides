def train_step(inputs, targets):
    predictions = model(inputs, training=True)
    loss = loss_fn(targets, predictions)
    loss.backward()                                     # isi nilai gradien
    gradients = [w.value.grad for w in model.trainable_weights]
    with torch.no_grad():                               # WAJIB di dalam no_grad()
        optimizer.apply(gradients, model.trainable_weights)
    model.zero_grad()                                   # WAJIB - backward() itu menumpuk
    return loss
