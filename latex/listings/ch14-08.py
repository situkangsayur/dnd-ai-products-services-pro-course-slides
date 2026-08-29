max_length = 600

text_vectorization = layers.TextVectorization(
    max_tokens=max_tokens,
    output_mode="int",           # integer token IDs, in order
    output_sequence_length=max_length,   # pad or truncate to a fixed length
)
