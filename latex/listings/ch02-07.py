my_slice = train_images[10:100]          # 90 citra
print(my_slice.shape)

print(train_images[:, 14:, 14:].shape)   # pojok kanan-bawah 14x14
print(train_images[:, 7:-7, 7:-7].shape) # 14x14 di tengah

batch = train_images[:128]               # batch ke-0
batch = train_images[128:256]            # batch ke-1
n = 3
batch = train_images[128 * n : 128 * (n + 1)]
