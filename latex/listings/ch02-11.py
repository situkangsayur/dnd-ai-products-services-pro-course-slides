(train_images, train_labels), _ = mnist.load_data()

print(train_images.ndim)     # rank: how many axes
print(train_images.shape)    # shape: how long each axis is
print(train_images.dtype)    # dtype: what the entries are
