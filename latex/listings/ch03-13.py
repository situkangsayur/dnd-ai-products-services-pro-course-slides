import os
os.environ["KERAS_BACKEND"] = "jax"

import keras            # MUST come after
print(keras.backend.backend())
