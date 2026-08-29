print(train_images[10:100].shape)          # 90 images
print(train_images[:, 14:, 14:].shape)     # bottom-right 14x14 corner
print(train_images[:, 7:-7, 7:-7].shape)   # centre 14x14, via negative indices
