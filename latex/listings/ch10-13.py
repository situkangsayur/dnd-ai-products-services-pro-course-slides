img_path = keras.utils.get_file(
    fname="elephant.jpg",
    origin="https://img-datasets.s3.amazonaws.com/elephant.jpg",
)

img = keras.utils.load_img(img_path)           # a PIL image
img_array = np.expand_dims(img, axis=0)        # to NumPy, plus a batch axis
