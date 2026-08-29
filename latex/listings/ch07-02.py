inputs.shape        # (None, 3)  <- None = ukuran batch, bebas
inputs.dtype        # "float32"

features = layers.Dense(64, activation="relu")(inputs)
features.shape      # (None, 64)
