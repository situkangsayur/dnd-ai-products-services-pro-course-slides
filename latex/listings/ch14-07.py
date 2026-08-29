text_vectorization = layers.TextVectorization(
    ngrams=2,                   # unigrams AND bigrams
    max_tokens=max_tokens,
    output_mode="multi_hot",
)
