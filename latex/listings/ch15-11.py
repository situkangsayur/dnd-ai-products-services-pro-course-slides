tokens = tokenizer.get_vocabulary()
char_to_id = dict(zip(tokens, range(vocabulary_size)))
id_to_char = dict(zip(range(vocabulary_size), tokens))

prompt = "\nKING RICHARD III:\n"
input_ids = [char_to_id[c] for c in prompt]

state = keras.ops.zeros(shape=(1, hidden_dim))
for token_id in input_ids:
    inputs = keras.ops.expand_dims([token_id], axis=0)
    predictions, state = generation_model.predict((inputs, state), verbose=0)
