# all of train/pos, train/neg AND train/unsup, labels discarded
pretrain_ds = keras.utils.text_dataset_from_directory(
    imdb_extract_dir / "train",
    labels=None,
    batch_size=batch_size,
)
