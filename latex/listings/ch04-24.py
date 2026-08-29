def get_model():
    model = keras.Sequential([
        layers.Dense(64, activation="relu"),
        layers.Dense(64, activation="relu"),
        layers.Dense(1),                    # NO activation — free to predict any value
    ])
    model.compile(optimizer="adam",
                  loss="mean_squared_error",
                  metrics=["mean_absolute_error"])
    return model
