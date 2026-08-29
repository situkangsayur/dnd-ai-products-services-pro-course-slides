batch = train_images[:128]        # batch 0
batch = train_images[128:256]     # batch 1

n = 3
batch = train_images[128 * n : 128 * (n + 1)]     # batch n
print(batch.shape)
