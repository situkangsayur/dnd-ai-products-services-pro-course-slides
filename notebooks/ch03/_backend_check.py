
import os, sys
os.environ["KERAS_BACKEND"] = sys.argv[1]
import keras
from keras import layers
from keras.datasets import mnist

(x, y), (xt, yt) = mnist.load_data()
x = x.reshape(-1, 784).astype("float32") / 255
xt = xt.reshape(-1, 784).astype("float32") / 255

keras.utils.set_random_seed(1337)
m = keras.Sequential([layers.Dense(128, activation="relu"),
                      layers.Dense(10, activation="softmax")])
m.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
          metrics=["accuracy"])
m.fit(x, y, epochs=2, batch_size=128, verbose=0)
print(sys.argv[1], m.evaluate(xt, yt, verbose=0)[1])
