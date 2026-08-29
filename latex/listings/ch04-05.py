import keras
from keras import layers

model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),      # one probability, 0 to 1
])

model.compile(optimizer="adam",
              loss="binary_crossentropy",
              metrics=["accuracy"])
