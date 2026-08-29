def compute_vocabulary(text_iterable, max_size, split_fn):
    counts = collections.Counter()
    for text in text_iterable:
        counts.update(split_fn(text.lower()))

    vocabulary = {"[UNK]": 0}                    # index 0 is always the fallback
    for token, _ in counts.most_common(max_size - 1):
        vocabulary[token] = len(vocabulary)
    return vocabulary
