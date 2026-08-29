z = np.matmul(x, y)
z = x @ y                      # the same thing, shorter

# compatibility:  x.shape[1] == y.shape[0]
# result shape:  (x.shape[0], y.shape[1])

# (a, b, c, d) @ (d,)    -> (a, b, c)
# (a, b, c, d) @ (d, e)  -> (a, b, c, e)
