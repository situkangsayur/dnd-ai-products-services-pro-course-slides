from keras_hub.layers import TokenAndPositionEmbedding
from keras_hub.layers import TransformerDecoder, TransformerEncoder

encoder_inputs = keras.Input(shape=(src_seq_length,), dtype="int64")
x = TokenAndPositionEmbedding(vocab_size, src_seq_length, embed_dim)(
    encoder_inputs
)
encoder_outputs = TransformerEncoder(intermediate_dim, num_heads)(x)

decoder_inputs = keras.Input(shape=(tgt_seq_length,), dtype="int64")
x = TokenAndPositionEmbedding(vocab_size, tgt_seq_length, embed_dim)(
    decoder_inputs
)
x = TransformerDecoder(intermediate_dim, num_heads)(x, encoder_outputs)
decoder_outputs = layers.Dense(vocab_size, activation="softmax")(x)

transformer = keras.Model([encoder_inputs, decoder_inputs], decoder_outputs)
