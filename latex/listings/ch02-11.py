X = np.random.random((64, 3, 32, 10))
y = np.random.random((32, 10))
z = np.maximum(X, y)          # y disiarkan; hasilnya (64, 3, 32, 10)
print(z.shape)
