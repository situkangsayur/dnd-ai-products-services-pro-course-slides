import keras_hub

height, width = 512, 512
task = keras_hub.models.TextToImage.from_preset(
    "stable_diffusion_3_medium",
    image_shape=(height, width, 3),
    dtype="float16",
)

prompt = "A NASA astronaut riding an origami elephant in New York City"
task.generate(prompt)
