y_pred = matmul(x, W)
loss_value = loss(y_pred, y_true)

# For fixed x and y_true this is just  loss_value = f(W)
# grad(loss_value, W0) is a tensor SHAPED LIKE W, whose every coefficient says
# in which direction, and how strongly, the loss moves if you nudge that weight.
