query_dense = [layers.Dense(head_dim) for i in range(num_heads)]
key_dense = [layers.Dense(head_dim) for i in range(num_heads)]
value_dense = [layers.Dense(head_dim) for i in range(num_heads)]
output_dense = layers.Dense(head_dim * num_heads)

def multi_head_attention(query, key, value):
    head_outputs = []
    for i in range(num_heads):
        q = query_dense[i](query)
        k = key_dense[i](key)
        v = value_dense[i](value)
        scores = np.einsum("btd,bsd->bts", q, k)
        scores = softmax(scores / math.sqrt(head_dim), axis=-1)
        head_outputs.append(np.einsum("bts,bsd->btd", scores, v))
    outputs = ops.concatenate(head_outputs, axis=-1)
    return output_dense(outputs)
