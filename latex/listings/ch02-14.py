x = np.array([[0., 1.],
              [2., 3.],
              [4., 5.]])          # (3, 2)

np.reshape(x, (6,))               # (6,)
np.reshape(x, (2, 3))             # (2, 3)

x = np.zeros((300, 20))
np.transpose(x).shape             # (20, 300)
