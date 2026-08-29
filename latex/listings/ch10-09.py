def deprocess_image(image):
    image -= ops.mean(image)
    image /= ops.std(image)
    image *= 64
    image += 128
    image = ops.clip(image, 0, 255).astype("uint8")
    return image[25:-25, 25:-25, :]     # crop the border artefacts
