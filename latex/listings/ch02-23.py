x = np.array([[0., 1.],
              [2., 3.],
              [4., 5.]])          # shape (3, 2)

print(np.reshape(x, (6,)).shape)     # flattened
print(np.reshape(x, (2, 3)).shape)   # regrouped

print(np.transpose(np.zeros((300, 20))).shape)   # rows and columns exchanged
