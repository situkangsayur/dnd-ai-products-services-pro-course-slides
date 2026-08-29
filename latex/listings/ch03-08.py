import os
os.environ["KERAS_BACKEND"] = "jax"

import keras          # HARUS setelah baris di atas
print(keras.backend.backend())
