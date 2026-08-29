import numpy as np

# Data mainan: y = 2x + 1, ditambah sedikit derau.
rng = np.random.default_rng(0)
X = rng.uniform(-1, 1, size=(200, 1))
Y = 2 * X + 1 + rng.normal(0, 0.05, size=(200, 1))

# 1) Bobot -- mula-mula acak, persis seperti kata bab ini.
W, b = rng.normal(size=(1, 1)), np.zeros((1,))

for step in range(600):
    Y_pred = X @ W + b                  # lapis: transformasi data
    loss = np.mean((Y_pred - Y) ** 2)   # 2) fungsi rugi: seberapa jauh melesetnya

    # 3) gradien rugi terhadap bobot -- inti backpropagation
    grad = 2.0 * (Y_pred - Y) / len(X)
    W -= 0.5 * (X.T @ grad)             # geser ke arah yang menurunkan rugi
    b -= 0.5 * grad.sum()

    if step % 200 == 0:
        print(f"step {step:3d}  loss {loss:.5f}  W {W[0, 0]:+.3f}  b {b[0]:+.3f}")

print(f"selesai    loss {loss:.5f}  W {W[0, 0]:+.3f}  b {b[0]:+.3f}")
