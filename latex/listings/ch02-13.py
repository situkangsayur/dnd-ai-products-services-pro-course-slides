z = np.matmul(x, y)
z = x @ y            # bentuk singkat

# aturan kecocokan:
#   x.shape[1] == y.shape[0]
# hasilnya:
#   (x.shape[0], y.shape[1])

# (a, b, c, d) @ (d,)   -> (a, b, c)
# (a, b, c, d) @ (d, e) -> (a, b, c, e)
