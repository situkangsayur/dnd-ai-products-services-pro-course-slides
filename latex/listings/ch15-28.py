scores = softmax(scores / math.sqrt(head_dim), axis=-1)
