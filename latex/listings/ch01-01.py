import numpy as np

rng = np.random.default_rng(0)
X = rng.uniform(-1, 1, size=(200, 1))
Y = 2 * X + 1 + rng.normal(0, 0.05, size=(200, 1))   # the law, plus a little noise

# The weights start random -- exactly as the chapter says.
W, b = rng.normal(size=(1, 1)), np.zeros((1,))
print(f"before training:  W {W[0, 0]:+.3f}   b {b[0]:+.3f}")
