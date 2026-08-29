def dot_product_attention(target, source):
    scores = np.einsum("btd,bsd->bts", target, source)
    scores = softmax(scores, axis=-1)
    return np.einsum("bts,bsd->btd", scores, source)

dot_product_attention(target, source)
