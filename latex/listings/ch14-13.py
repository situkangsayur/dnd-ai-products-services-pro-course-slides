embedding_layer = layers.Embedding(max_tokens, 256, mask_zero=True)
embedding_layer.build((None,))
embedding_layer.set_weights(pretrained_embedding.get_weights())

inputs = keras.Input(shape=(max_length,), dtype="int32")
x = embedding_layer(inputs)
x = layers.Bidirectional(layers.LSTM(32))(x)
outputs = layers.Dense(1, activation="sigmoid")(layers.Dropout(0.5)(x))
