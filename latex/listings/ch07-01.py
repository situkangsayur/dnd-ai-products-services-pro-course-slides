inputs = keras.Input(shape=(3,),
                     name="my_input")
features = layers.Dense(
    64, activation="relu")(inputs)
outputs = layers.Dense(
    10, activation="softmax")(features)

model = keras.Model(
    inputs=inputs, outputs=outputs,
    name="my_functional_model")
