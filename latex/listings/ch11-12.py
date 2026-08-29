model = keras.models.load_model("segmentation.keras")

test_image = val_input_imgs[4]
mask = model.predict(np.expand_dims(test_image, 0))[0]

predicted_mask = np.argmax(mask, axis=-1)      # (200, 200): a class per pixel
print(mask.shape, predicted_mask.shape)
