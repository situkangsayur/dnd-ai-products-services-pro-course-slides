# 1. Take small values  - most values in the 0-1 range
# 2. Be homogeneous     - all features on roughly the same scale

# The stricter, common practice:
x -= x.mean(axis=0)     # each feature centred on 0
x /= x.std(axis=0)      # each feature with unit standard deviation
