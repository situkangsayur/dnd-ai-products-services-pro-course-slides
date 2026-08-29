num_batches = 29373
num_val_batches = 500
num_train_batches = num_batches - num_val_batches

val_ds = ds.take(num_val_batches).repeat()
train_ds = ds.skip(num_val_batches).repeat()
