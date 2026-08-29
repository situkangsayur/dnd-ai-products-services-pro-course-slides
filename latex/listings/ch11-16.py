import keras_hub

model = keras_hub.models.SAMImageSegmenter.from_preset("sam_huge_sa1b")

path = keras.utils.get_file(
    origin="https://s3.amazonaws.com/keras.io/img/book/fruits.jpg")
image = np.array(keras.utils.load_img(path))
