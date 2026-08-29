for step in range(600):
    Y_pred = X @ W + b                  # the layer: a data transformation (fig 1.7)
    loss = np.mean((Y_pred - Y) ** 2)   # the loss: how far off are we? (fig 1.8)

    grad = 2.0 * (Y_pred - Y) / len(X)  # gradient of the loss (fig 1.9)
    W -= 0.5 * (X.T @ grad)             # step downhill
    b -= 0.5 * grad.sum()

    if step % 200 == 0:
        print(f"step {step:3d}  loss {loss:.5f}  W {W[0, 0]:+.3f}  b {b[0]:+.3f}")
