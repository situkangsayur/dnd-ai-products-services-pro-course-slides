from keras.regularizers import l2
from keras import regularizers

model = keras.Sequential([
    layers.Dense(16, kernel_regularizer=l2(0.002), activation="relu"),
    layers.Dense(16, kernel_regularizer=l2(0.002), activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])

# pilihan lain:
regularizers.l1(0.001)                     # L1
regularizers.l1_l2(l1=0.001, l2=0.001)     # L1 dan L2 sekaligus
