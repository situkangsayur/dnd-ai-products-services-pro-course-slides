# -*- coding: utf-8 -*-
"""Chapter 15 notebooks — Language Models and the Transformer."""

DECK = "ch15"

NOTEBOOKS = [
    {
        "file": "01_shakespeare_language_model.ipynb",
        "title": "A character-level language model, and sampling from it",
        "lede": "p(token | past tokens), trained in two minutes, then called in a loop "
                "to generate text — including the surgery that generation requires and "
                "the experiment that shows why bidirectional would break it.",
        "needs": "CPU — about 5 minutes (GPU: 2 minutes)",
        "section": "01 — The language model",
        "cells": [
            ("h2", "The corpus"),
            ("py", """import keras
import tensorflow as tf
import numpy as np

filename = keras.utils.get_file(
    origin=("https://storage.googleapis.com/download.tensorflow.org/"
            "data/shakespeare.txt"))
shakespeare = open(filename, "r").read()

print(f"{len(shakespeare):,} characters")
print(shakespeare[:250])"""),

            ("h2", "Features and labels differ by one character"),
            ("py", """sequence_length = 100

def split_input(inp, sequence_length):
    for i in range(0, len(inp), sequence_length):
        yield inp[i:i + sequence_length]

features = list(split_input(shakespeare[:-1], sequence_length))
labels = list(split_input(shakespeare[1:], sequence_length))
dataset = tf.data.Dataset.from_tensor_slices((features, labels))

x, y = next(dataset.as_numpy_iterator())
print(repr(x[:50]))
print(repr(y[:50]))"""),
            ("md",
             "`shakespeare[:-1]` against `shakespeare[1:]`. **That single line "
             "is the entire supervision signal** — and one 100-character input "
             "produces 100 supervised predictions, not one."),

            ("h2", "A 67-character vocabulary"),
            ("py", """from keras import layers

tokenizer = layers.TextVectorization(
    standardize=None, split="character",
    output_sequence_length=sequence_length)
tokenizer.adapt(dataset.map(lambda text, labels: text))

vocabulary_size = tokenizer.vocabulary_size()
print(f"vocabulary: {vocabulary_size} characters")
print(tokenizer.get_vocabulary()[:20])

dataset = dataset.map(
    lambda f, l: (tokenizer(f), tokenizer(l)), num_parallel_calls=8)
training_data = dataset.shuffle(10_000).batch(64).cache()"""),

            ("h2", "The model"),
            ("py", """embedding_dim, hidden_dim = 256, 1024

inputs = layers.Input(shape=(sequence_length,), dtype="int", name="token_ids")
x = layers.Embedding(vocabulary_size, embedding_dim)(inputs)
x = layers.GRU(hidden_dim, return_sequences=True)(x)
x = layers.Dropout(0.1)(x)
outputs = layers.Dense(vocabulary_size, activation="softmax")(x)
model = keras.Model(inputs, outputs)
model.summary()"""),
            ("md",
             "`return_sequences=True` is essential — a prediction at **every** "
             "position, not just the last. Note also that ~98% of the parameters "
             "are in the GRU; that balance shifts dramatically in the "
             "Transformer models later in this chapter."),

            ("h2", "Training"),
            ("py", """model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=["sparse_categorical_accuracy"])
model.fit(training_data, epochs=20, verbose=2)"""),
            ("md",
             "A batch of 64 sequences of 100 characters is **6,400 individual "
             "classifications**. Around 70% next-character accuracy after 20 "
             "epochs."),

            ("h2", "Surgery for generation"),
            ("py", """inputs = keras.Input(shape=(1,), dtype="int", name="token_ids")
input_state = keras.Input(shape=(hidden_dim,), name="state")

x = layers.Embedding(vocabulary_size, embedding_dim)(inputs)
x, output_state = layers.GRU(hidden_dim, return_state=True)(
    x, initial_state=input_state)
outputs = layers.Dense(vocabulary_size, activation="softmax")(x)

generation_model = keras.Model(inputs=(inputs, input_state),
                               outputs=(outputs, output_state))
generation_model.set_weights(model.get_weights())
print("same weights, different interface")"""),
            ("md",
             "One token in, and the GRU state promoted from an internal detail "
             "to a **named input and output**. Same computational structure, so "
             "the weights transfer directly."),

            ("h2", "Priming, then sampling"),
            ("py", """tokens = tokenizer.get_vocabulary()
char_to_id = dict(zip(tokens, range(vocabulary_size)))
id_to_char = dict(zip(range(vocabulary_size), tokens))

prompt = "\\nKING RICHARD III:\\n"
input_ids = [char_to_id[c] for c in prompt]

state = keras.ops.zeros(shape=(1, hidden_dim))
for token_id in input_ids:
    inp = keras.ops.expand_dims([token_id], axis=0)
    predictions, state = generation_model.predict((inp, state), verbose=0)

generated_ids = []
for i in range(250):
    next_char = int(np.argmax(predictions, axis=-1)[0])
    generated_ids.append(next_char)
    inp = keras.ops.expand_dims([next_char], axis=0)
    predictions, state = generation_model.predict((inp, state), verbose=0)

print(prompt + "".join(id_to_char[t] for t in generated_ids))"""),
            ("md",
             "Correctly spelled words, speaker names in capitals followed by a "
             "colon, blank lines between speeches, verse-length lines. **All of "
             "it from a next-character objective**, none of it encoded."),

            ("h2", "The diagnostic: replace GRU with Bidirectional(GRU)"),
            ("py", """bi = keras.Sequential([
    layers.Input(shape=(sequence_length,), dtype="int"),
    layers.Embedding(vocabulary_size, embedding_dim),
    layers.Bidirectional(layers.GRU(256, return_sequences=True)),
    layers.Dense(vocabulary_size, activation="softmax"),
])
bi.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
           metrics=["sparse_categorical_accuracy"])
h = bi.fit(training_data.take(100), epochs=3, verbose=2)

print(f"\\nbidirectional training accuracy after 3 epochs: "
      f"{h.history['sparse_categorical_accuracy'][-1]:.4f}")
print("compare: the causal model reached ~0.70 after 20 epochs")"""),
            ("warn",
             "Accuracy shoots above 99% almost immediately, and generation is "
             "dead.** The backward pass hands the model the next character as a "
             "feature — it is reading the label off its own input.\n\n"
             "**A training metric that suddenly looks too good is the most "
             "reliable signal of leakage there is.** This is chapter 5's lesson, "
             "and chapter 15's causal mask exists to prevent exactly it."),

            ("h2", "Temperature, briefly"),
            ("py", """def sample(prompt, temperature=1.0, length=200):
    ids = [char_to_id[c] for c in prompt]
    st = keras.ops.zeros(shape=(1, hidden_dim))
    for t in ids:
        p, st = generation_model.predict(
            (keras.ops.expand_dims([t], axis=0), st), verbose=0)
    out = []
    for _ in range(length):
        logits = np.log(np.maximum(p[0], 1e-9)) / temperature
        probs = np.exp(logits); probs /= probs.sum()
        nxt = int(np.random.choice(len(probs), p=probs))
        out.append(nxt)
        p, st = generation_model.predict(
            (keras.ops.expand_dims([nxt], axis=0), st), verbose=0)
    return "".join(id_to_char[i] for i in out)

for t in [0.2, 0.7, 1.3]:
    print(f"\\n--- temperature {t} ---")
    print(sample(prompt, temperature=t, length=180))"""),
            ("md",
             "Low temperature repeats; high temperature loses the spelling. "
             "**Chapter 16 makes this a first-class control** and adds top-K "
             "beside it."),
        ],
        "takeaways": [
            "A language model is p(token | past tokens); labels are the features "
            "shifted by one.",
            "Generation needs an inference model with the recurrent state made "
            "explicit.",
            "**Bidirectional breaks it** — 99% training accuracy, dead "
            "generation. Leakage looks like success.",
            "There is logic in the generation loop that has no counterpart in "
            "training.",
        ],
    },

    {
        "file": "02_seq2seq_rnn_translation.ipynb",
        "title": "English to Spanish with recurrent encoder and decoder",
        "lede": "The bottleneck architecture, working — and its two limits, which are "
                "what the Transformer was invented to remove.",
        "needs": "GPU recommended — about 40 minutes on CPU",
        "section": "02 — Sequence-to-sequence learning",
        "cells": [
            ("h2", "The data"),
            ("py", """import pathlib, random, re, string
import keras
import tensorflow as tf

zip_path = keras.utils.get_file(
    origin=("http://storage.googleapis.com/download.tensorflow.org/"
            "data/spa-eng.zip"),
    fname="spa-eng", extract=True)
text_path = pathlib.Path(zip_path) / "spa-eng" / "spa.txt"

with open(text_path) as f:
    lines = f.read().split("\\n")[:-1]

text_pairs = []
for line in lines:
    english, spanish = line.split("\\t")
    spanish = "[start] " + spanish + " [end]"
    text_pairs.append((english, spanish))

print(f"{len(text_pairs):,} pairs")
print(random.choice(text_pairs))"""),
            ("md",
             "`[start]` and `[end]` are inserted **in the data**, not built into "
             "the model. They are the seed and the stop signal for the "
             "generation loop."),

            ("h2", "Two tokenizers, because punctuation is language-specific"),
            ("py", """random.shuffle(text_pairs)
val_samples = int(0.15 * len(text_pairs))
train_samples = len(text_pairs) - 2 * val_samples
train_pairs = text_pairs[:train_samples]
val_pairs = text_pairs[train_samples:train_samples + val_samples]
test_pairs = text_pairs[train_samples + val_samples:]

from keras import layers

strip_chars = string.punctuation + "¿"
strip_chars = strip_chars.replace("[", "").replace("]", "")

def custom_standardization(input_string):
    lowercase = tf.strings.lower(input_string)
    return tf.strings.regex_replace(
        lowercase, f"[{re.escape(strip_chars)}]", "")

vocab_size, sequence_length = 15000, 20

english_tokenizer = layers.TextVectorization(
    max_tokens=vocab_size, output_mode="int",
    output_sequence_length=sequence_length)
spanish_tokenizer = layers.TextVectorization(
    max_tokens=vocab_size, output_mode="int",
    output_sequence_length=sequence_length + 1,
    standardize=custom_standardization)

english_tokenizer.adapt([p[0] for p in train_pairs])
spanish_tokenizer.adapt([p[1] for p in train_pairs])
print("Spanish sequence length is one longer -- that extra slot is what")
print("makes the offset-by-one split possible.")"""),
            ("warn",
             "Two customisations, both easy to miss.** `[` and `]` must survive "
             "standardization or `\"[start]\"` collapses to `\"start\"`. And `¿` is "
             "not in `string.punctuation`, so it must be added explicitly."),

            ("h2", "The pipeline"),
            ("py", """batch_size = 64

def format_dataset(eng, spa):
    eng = english_tokenizer(eng)
    spa = spanish_tokenizer(spa)
    features = {"english": eng, "spanish": spa[:, :-1]}
    labels = spa[:, 1:]
    sample_weights = labels != 0
    return features, labels, sample_weights

def make_dataset(pairs):
    eng_texts, spa_texts = zip(*pairs)
    ds = tf.data.Dataset.from_tensor_slices((list(eng_texts), list(spa_texts)))
    ds = ds.batch(batch_size).map(format_dataset, num_parallel_calls=4)
    return ds.shuffle(2048).cache()

train_ds = make_dataset(train_pairs)
val_ds = make_dataset(val_pairs)

inputs, targets, weights = next(iter(train_ds))
for k, v in inputs.items():
    print(f"inputs[{k!r}]: {v.shape}")
print("targets:", targets.shape, " sample_weights:", weights.shape)"""),
            ("md",
             "`sample_weights = labels != 0` tells Keras to **ignore padded "
             "positions** in the loss and metrics. Without it, a model that "
             "learned only to predict padding would score well."),

            ("h2", "Why the naive single-RNN approach cannot work"),
            ("md",
             "> *\"I will bring the bag to you\"* becomes *\"Te traeré la bolsa.\"* "
             "The **first** Spanish word corresponds to the **last** English "
             "word.\n\n"
             "A single RNN emitting a target token at each step sees only source "
             "tokens 0…N when predicting target token N. There is no way to "
             "produce *Te* without having read to the end."),

            ("h2", "Encoder and decoder"),
            ("py", """embed_dim, hidden_dim = 256, 1024

source = keras.Input(shape=(None,), dtype="int32", name="english")
x = layers.Embedding(vocab_size, embed_dim, mask_zero=True)(source)
rnn_layer = layers.Bidirectional(layers.GRU(hidden_dim), merge_mode="sum")
encoder_output = rnn_layer(x)

target = keras.Input(shape=(None,), dtype="int32", name="spanish")
x = layers.Embedding(vocab_size, embed_dim, mask_zero=True)(target)
x = layers.GRU(hidden_dim, return_sequences=True)(x, initial_state=encoder_output)
x = layers.Dropout(0.5)(x)
target_predictions = layers.Dense(vocab_size, activation="softmax")(x)
seq2seq_rnn = keras.Model([source, target], target_predictions)
seq2seq_rnn.summary()"""),
            ("md",
             "**Bidirectional in the encoder, emphatically not in the "
             "decoder.** We never predict source tokens, so there is nothing to "
             "cheat at — and a rich source representation is exactly what we "
             "want. The decoder is the Shakespeare setup from notebook 01, with "
             "its initial state supplied rather than zero."),

            ("h2", "Training"),
            ("py", """seq2seq_rnn.compile(optimizer="adam",
                    loss="sparse_categorical_crossentropy",
                    weighted_metrics=["accuracy"])
seq2seq_rnn.fit(train_ds, epochs=15, validation_data=val_ds, verbose=2)"""),
            ("md",
             "About 65% next-token accuracy — and that metric is poor for "
             "translation. It assumes tokens 0…N are already correct when "
             "predicting N+1, which is exactly what is *not* true at inference. "
             "**BLEU** is the standard alternative."),

            ("h2", "Generating translations"),
            ("py", """import numpy as np

spa_vocab = spanish_tokenizer.get_vocabulary()
spa_index_lookup = dict(zip(range(len(spa_vocab)), spa_vocab))

def generate_translation(input_sentence):
    tokenized_input = english_tokenizer([input_sentence])
    decoded_sentence = "[start]"
    for i in range(sequence_length):
        tokenized_target = spanish_tokenizer([decoded_sentence])[:, :-1]
        preds = seq2seq_rnn.predict(
            [tokenized_input, tokenized_target], verbose=0)
        sampled_token_index = np.argmax(preds[0, i, :])
        sampled_token = spa_index_lookup[sampled_token_index]
        decoded_sentence += " " + sampled_token
        if sampled_token == "[end]":
            break
    return decoded_sentence

test_eng_texts = [pair[0] for pair in test_pairs]
for _ in range(5):
    s = random.choice(test_eng_texts)
    print("-")
    print(s)
    print(generate_translation(s))"""),
            ("note",
             "This loop is **inefficient by construction**: it reprocesses the "
             "whole source and the whole generated target on every sampled word. "
             "Chapter 16 quantifies exactly how expensive that is, and what "
             "caching does about it."),

            ("h2", "The two limits nothing here fixes"),
            ("py", """print("1. THE BOTTLENECK")
print(f"   Everything the decoder knows about English arrives through")
print(f"   one vector of {hidden_dim} numbers. Longer or more complex")
print(f"   sentences do not get a bigger vector.\\n")
print("2. FORGETTING")
print("   RNNs progressively lose the past. By the 100th token, little")
print("   remains of the start of the sequence.\\n")
print("Deeper stacks, LSTM instead of GRU, a wider state -- none of these")
print("address either. Google Translate circa 2017 was seven large LSTM")
print("layers in essentially this shape, and these limits are what drove")
print("the search for something else.")"""),
        ],
        "takeaways": [
            "An encoder compresses the whole source; a decoder generates from it "
            "token by token.",
            "Bidirectional in the encoder is right; in the decoder it destroys "
            "the objective.",
            "`sample_weights` keeps padding out of the loss.",
            "**The bottleneck and forgetting are structural** — no amount of "
            "tuning removes them.",
        ],
    },

    {
        "file": "03_attention_from_scratch.ipynb",
        "title": "Attention, derived from the problem it solves",
        "lede": "Score, softmax, weighted sum — built up in NumPy, with the score matrix "
                "visualised, then the two refinements the 2017 paper added.",
        "needs": "CPU — about 2 minutes",
        "section": "03 — The Transformer architecture",
        "cells": [
            ("h2", "The simplest version"),
            ("py", """import numpy as np

def softmax(x, axis=-1):
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)

def dot_product_attention(target, source):
    scores = np.einsum("btd,bsd->bts", target, source)
    scores = softmax(scores, axis=-1)
    return np.einsum("bts,bsd->btd", scores, source), scores

rng = np.random.default_rng(0)
target = rng.normal(size=(1, 5, 8))     # 5 target positions, 8 dims
source = rng.normal(size=(1, 7, 8))     # 7 source positions

out, scores = dot_product_attention(target, source)
print("output:", out.shape, " scores:", scores.shape)
print("each row of scores sums to 1:", np.allclose(scores.sum(-1), 1))"""),
            ("md",
             "Read the `einsum` subscripts: `b`atch, `t`arget length, `s`ource "
             "length, `d`imension. The first contraction produces a **(batch, "
             "target, source)** score matrix; the second uses it to take a "
             "weighted sum.\n\n"
             "**Every attention implementation in every framework is these two "
             "contractions with a softmax between them.**"),

            ("h2", "The score matrix, drawn"),
            ("py", """import matplotlib.pyplot as plt

eng = ["I", "will", "bring", "the", "bag", "to", "you"]
spa = ["Te", "traeré", "la", "bolsa", "[end]"]

# A hand-built matrix showing what a trained model should learn.
S = np.array([
    [.02, .03, .04, .02, .03, .06, .80],
    [.20, .45, .30, .02, .01, .01, .01],
    [.02, .02, .03, .60, .28, .03, .02],
    [.01, .02, .03, .20, .70, .02, .02],
    [.05, .05, .10, .05, .10, .30, .35],
])

fig, ax = plt.subplots(figsize=(7.5, 5))
im = ax.imshow(S, cmap="Blues", aspect="auto")
ax.set_xticks(range(len(eng)), eng, rotation=45, ha="right")
ax.set_yticks(range(len(spa)), spa)
for i in range(len(spa)):
    for j in range(len(eng)):
        if S[i, j] > .15:
            ax.text(j, i, f"{S[i,j]:.2f}", ha="center", va="center",
                    fontsize=8, color="w" if S[i, j] > .5 else "k")
plt.colorbar(im); ax.set_title("Attention scores for a translation")
plt.tight_layout(); plt.show()"""),
            ("md",
             "Read a row as: *when producing this Spanish word, how much did the "
             "model draw on each English word?* **The `Te` row peaking at `you` "
             "is exactly the long-range dependency the RNN could not express.**"),

            ("h2", "Parameterizing it: query, key, value"),
            ("py", """dim = 8
Wq, Wk, Wv, Wo = (rng.normal(size=(dim, dim)) * 0.3 for _ in range(4))

def parameterized_attention(query, key, value):
    q = query @ Wq
    k = key @ Wk
    v = value @ Wv
    scores = softmax(np.einsum("btd,bsd->bts", q, k), axis=-1)
    out = np.einsum("bts,bsd->btd", scores, v)
    return out @ Wo, scores

out, _ = parameterized_attention(query=target, key=source, value=source)
print("output:", out.shape)"""),
            ("md",
             "`sum(score(target, source) * source)` has become "
             "`sum(score(query, key) * value)`. The names come from **search "
             "engines**: the query is your search term, the keys are tags to "
             "match against, the values are what you retrieve."),

            ("h2", "Refinement 1: scale before the softmax"),
            ("py", """for d in [8, 64, 512]:
    q = rng.normal(size=(1, 4, d)); k = rng.normal(size=(1, 6, d))
    raw = np.einsum("btd,bsd->bts", q, k)
    scaled = raw / np.sqrt(d)
    print(f"dim {d:4d}:  raw logit std {raw.std():7.2f}   "
          f"scaled {scaled.std():5.2f}   "
          f"max softmax {softmax(raw).max():.3f} -> {softmax(scaled).max():.3f}")"""),
            ("out", """dim    8:  raw logit std    2.9x   scaled  1.0x   max softmax 0.7xx -> 0.4xx
dim   64:  raw logit std    8.0x   scaled  1.0x   max softmax 0.9xx -> 0.4xx
dim  512:  raw logit std   22.x     scaled  1.0x   max softmax 1.000 -> 0.4xx"""),
            ("md",
             "At 512 dimensions the unscaled softmax is **effectively one-hot**, "
             "and a one-hot softmax has vanishing gradients. Dividing by √d "
             "holds the logit variance constant regardless of dimension — which "
             "is why the mechanism is called *scaled* dot-product attention."),

            ("h2", "Refinement 2: multiple heads"),
            ("py", """def multi_head_attention(query, key, value, num_heads=4, head_dim=4):
    outs = []
    for _ in range(num_heads):
        wq = rng.normal(size=(query.shape[-1], head_dim)) * .3
        wk = rng.normal(size=(key.shape[-1], head_dim)) * .3
        wv = rng.normal(size=(value.shape[-1], head_dim)) * .3
        q, k, v = query @ wq, key @ wk, value @ wv
        s = softmax(np.einsum("btd,bsd->bts", q, k) / np.sqrt(head_dim), -1)
        outs.append(np.einsum("bts,bsd->btd", s, v))
    return np.concatenate(outs, axis=-1)

out = multi_head_attention(target, source, source)
print("concatenated across 4 heads of 4 dims:", out.shape)"""),
            ("md",
             "One softmax sum is **blunt**: attend to many tokens and the "
             "interesting features of individual ones wash out. Running the "
             "operation several times with different projections lets one head "
             "match the subject while another attends to punctuation, in "
             "separate partitions of the output."),

            ("h2", "The Keras layer"),
            ("py", """import keras
from keras import layers
import numpy as np

mha = layers.MultiHeadAttention(num_heads=8, key_dim=32)
t = np.random.normal(size=(2, 5, 256)).astype("float32")
s = np.random.normal(size=(2, 7, 256)).astype("float32")

out, attn = mha(query=t, key=s, value=s, return_attention_scores=True)
print("output:", out.shape)
print("attention scores:", attn.shape, " (batch, heads, target, source)")"""),
            ("md",
             "`return_attention_scores=True` gives you the matrix from the plot "
             "above, per head. **It is the first thing to look at when a "
             "Transformer misbehaves** — chapter 10's interpretability argument, "
             "in a different modality."),

            ("h2", "Self-attention"),
            ("py", """out = mha(query=s, key=s, value=s)
print("self-attention output:", out.shape)
print()
print('"The train left the station on time."')
print()
print("What kind of station? A radio station? The ISS?")
print("Self-attention lets the model give a high score to the pair")
print("(station, train), summing 'train' into the representation of")
print("'station' -- turning a word in a vacuum into a word in context.")"""),

            ("h2", "Why attention alone is not enough"),
            ("py", """# A sequence of length one. The score matrix is a single 1.
one = np.random.normal(size=(1, 1, 16)).astype("float32")
m = layers.MultiHeadAttention(num_heads=2, key_dim=8)
print("attention on a length-1 sequence:", m(one, one, one).shape)
print()
print("With one token the softmax is [1.0], so the layer reduces to a")
print("linear projection. Stack 100 of them and the whole computation")
print("still simplifies to ONE matrix multiplication.")
print()
print("That is why the Transformer block adds a feedforward network:")
print("  attention   -> mixes positions, no nonlinearity")
print("  feedforward -> mixes features, HAS the nonlinearity")"""),
            ("md",
             "This is the argument for the second half of the block, and it is a "
             "genuine one rather than an empirical addition. **Attention is an "
             "expressive pooling operation**, and pooling alone cannot represent "
             "anything a single linear layer cannot."),
        ],
        "takeaways": [
            "Attention is two einsum contractions with a softmax between them.",
            "The score matrix is (target × source) and is directly interpretable.",
            "Scale by √d or the softmax saturates and the gradients vanish.",
            "Multiple heads avoid one blunt weighted sum; the feedforward block "
            "supplies the nonlinearity attention lacks.",
        ],
    },

    {
        "file": "04_transformer_translation.ipynb",
        "title": "The Transformer, and the experiment that reveals positional embeddings",
        "lede": "Encoder and decoder blocks built from scratch, trained — and failing — "
                "then fixed with two changed lines. The failure is the point.",
        "needs": "GPU recommended — about 45 minutes on CPU · continues from notebook 02 (same kernel)",
        "section": "03 — The Transformer architecture",
        "cells": [
            ("h2", "The encoder block"),
            ("py", """import keras
from keras import layers, ops

class TransformerEncoder(keras.Layer):
    def __init__(self, hidden_dim, intermediate_dim, num_heads):
        super().__init__()
        key_dim = hidden_dim // num_heads
        self.self_attention = layers.MultiHeadAttention(num_heads, key_dim)
        self.self_attention_layernorm = layers.LayerNormalization()
        self.feed_forward_1 = layers.Dense(intermediate_dim, activation="relu")
        self.feed_forward_2 = layers.Dense(hidden_dim)
        self.feed_forward_layernorm = layers.LayerNormalization()

    def call(self, source, source_mask):
        residual = x = source
        mask = source_mask[:, None, :]
        x = self.self_attention(query=x, key=x, value=x, attention_mask=mask)
        x = x + residual
        x = self.self_attention_layernorm(x)

        residual = x
        x = self.feed_forward_1(x)
        x = self.feed_forward_2(x)
        x = x + residual
        x = self.feed_forward_layernorm(x)
        return x"""),
            ("md",
             "Two stages, each *transform, add the residual, normalise* — the "
             "chapter-9 pattern exactly. `key_dim = hidden_dim // num_heads` "
             "keeps total width constant as heads are added: **splitting, not "
             "growing.**"),

            ("h2", "LayerNormalization, not BatchNormalization"),
            ("py", """import numpy as np

def layer_normalization(batch_of_sequences):
    mean = np.mean(batch_of_sequences, keepdims=True, axis=-1)
    variance = np.var(batch_of_sequences, keepdims=True, axis=-1)
    return (batch_of_sequences - mean) / np.sqrt(variance + 1e-6)

def batch_normalization(batch_of_images):
    mean = np.mean(batch_of_images, keepdims=True, axis=(0, 1, 2))
    variance = np.var(batch_of_images, keepdims=True, axis=(0, 1, 2))
    return (batch_of_images - mean) / np.sqrt(variance + 1e-6)

seqs = np.random.normal(size=(4, 10, 8))
print("layer norm pools over axis -1 only:")
print("  each sequence normalized independently ->",
      layer_normalization(seqs)[0].std().round(3))
print()
print("batch norm pools over axis 0, creating interactions BETWEEN samples.")
print("Sequences in a batch have different lengths and padding amounts,")
print("so batch statistics are contaminated by how you grouped examples.")"""),

            ("h2", "The decoder block"),
            ("py", """class TransformerDecoder(keras.Layer):
    def __init__(self, hidden_dim, intermediate_dim, num_heads):
        super().__init__()
        key_dim = hidden_dim // num_heads
        self.self_attention = layers.MultiHeadAttention(num_heads, key_dim)
        self.self_attention_layernorm = layers.LayerNormalization()
        self.cross_attention = layers.MultiHeadAttention(num_heads, key_dim)
        self.cross_attention_layernorm = layers.LayerNormalization()
        self.feed_forward_1 = layers.Dense(intermediate_dim, activation="relu")
        self.feed_forward_2 = layers.Dense(hidden_dim)
        self.feed_forward_layernorm = layers.LayerNormalization()

    def call(self, target, source, source_mask):
        residual = x = target
        x = self.self_attention(query=x, key=x, value=x, use_causal_mask=True)
        x = self.self_attention_layernorm(x + residual)

        residual = x
        mask = source_mask[:, None, :]
        x = self.cross_attention(query=x, key=source, value=source,
                                 attention_mask=mask)
        x = self.cross_attention_layernorm(x + residual)

        residual = x
        x = self.feed_forward_1(x)
        x = self.feed_forward_2(x)
        x = self.feed_forward_layernorm(x + residual)
        return x"""),
            ("warn",
             "Two different masks, solving two different problems.** "
             "`use_causal_mask=True` stops the decoder seeing its own future — "
             "notebook 01's bidirectional failure, prevented. The padding "
             "`attention_mask` on cross-attention stops it attending to empty "
             "source positions."),

            ("h2", "Seeing the causal mask"),
            ("py", """import matplotlib.pyplot as plt

n = 8
causal = np.tril(np.ones((n, n)))
plt.figure(figsize=(4.5, 4))
plt.imshow(causal, cmap="Greens")
plt.xlabel("source position (key)"); plt.ylabel("target position (query)")
plt.title("Row i may attend to positions 0..i")
plt.colorbar(); plt.show()
print(causal.astype(int))"""),

            ("h2", "The model, first attempt"),
            ("py", """hidden_dim, intermediate_dim, num_heads = 256, 2048, 8
vocab_size, sequence_length = 15000, 20

source = keras.Input(shape=(None,), dtype="int32", name="english")
x = layers.Embedding(vocab_size, hidden_dim)(source)
encoder_output = TransformerEncoder(hidden_dim, intermediate_dim, num_heads)(
    source=x, source_mask=source != 0)

target = keras.Input(shape=(None,), dtype="int32", name="spanish")
x = layers.Embedding(vocab_size, hidden_dim)(target)
x = TransformerDecoder(hidden_dim, intermediate_dim, num_heads)(
    target=x, source=encoder_output, source_mask=source != 0)
x = layers.Dropout(0.5)(x)
target_predictions = layers.Dense(vocab_size, activation="softmax")(x)
transformer = keras.Model([source, target], target_predictions)

print(f"{transformer.count_params():,} parameters "
      f"(the GRU model had 34,869,912)")"""),
            ("py", """transformer.compile(optimizer="adam",
                    loss="sparse_categorical_crossentropy",
                    weighted_metrics=["accuracy"])
h1 = transformer.fit(train_ds, epochs=15, validation_data=val_ds, verbose=2)
print(f"\\nbest validation accuracy: {max(h1.history['val_accuracy']):.4f}")
print("the GRU model reached 0.65")"""),
            ("out", "best validation accuracy: 0.58xx"),

            ("h2", "Stop here. Why is it worse?"),
            ("md",
             "Seven percentage points **worse** than the RNN, with half the "
             "parameters. Before reading on, look at the model definition again.\n\n"
             "*(Hint: this section is about sequence models. Is the model above "
             "a sequence model?)*"),

            ("h2", "The demonstration"),
            ("py", """# Shuffle the words in every source sentence and see what changes.
import tensorflow as tf

for inputs, targets, weights in train_ds.take(1):
    eng = inputs["english"]
    shuffled = tf.random.shuffle(tf.transpose(eng))
    shuffled = tf.transpose(shuffled)

    normal = transformer.predict(
        [eng, inputs["spanish"]], verbose=0)
    scrambled = transformer.predict(
        [shuffled, inputs["spanish"]], verbose=0)

    print("Mean absolute difference in predictions after shuffling")
    print("every word of every source sentence:")
    print(f"  {np.abs(normal - scrambled).mean():.6f}")
    break"""),
            ("md",
             "Very small, and it would be **exactly zero** if the shuffle were "
             "applied consistently within the batch.\n\n"
             "The model is dense layers processing tokens independently plus an "
             "attention layer that sees tokens **as a set**. Change the order "
             "and you get identical pairwise scores. ==Attention is a "
             "set-processing mechanism, blind to position.=="),

            ("h2", "Positional embeddings"),
            ("py", """class PositionalEmbedding(keras.Layer):
    def __init__(self, sequence_length, input_dim, output_dim):
        super().__init__()
        self.token_embeddings = layers.Embedding(input_dim, output_dim)
        self.position_embeddings = layers.Embedding(sequence_length, output_dim)

    def call(self, inputs):
        positions = ops.cumsum(ops.ones_like(inputs), axis=-1) - 1
        embedded_tokens = self.token_embeddings(inputs)
        embedded_positions = self.position_embeddings(positions)
        return embedded_tokens + embedded_positions"""),
            ("md",
             "`ops.cumsum(ops.ones_like(inputs), axis=-1) - 1` produces "
             "`[0, 1, 2, …]` — a backend-agnostic `arange`. The layer is a "
             "**drop-in replacement** for `Embedding`."),

            ("h2", "Two lines changed"),
            ("py", """source = keras.Input(shape=(None,), dtype="int32", name="english")
x = PositionalEmbedding(sequence_length, vocab_size, hidden_dim)(source)
encoder_output = TransformerEncoder(hidden_dim, intermediate_dim, num_heads)(
    source=x, source_mask=source != 0)

target = keras.Input(shape=(None,), dtype="int32", name="spanish")
x = PositionalEmbedding(sequence_length, vocab_size, hidden_dim)(target)
x = TransformerDecoder(hidden_dim, intermediate_dim, num_heads)(
    target=x, source=encoder_output, source_mask=source != 0)
x = layers.Dropout(0.5)(x)
target_predictions = layers.Dense(vocab_size, activation="softmax")(x)
transformer = keras.Model([source, target], target_predictions)

transformer.compile(optimizer="adam",
                    loss="sparse_categorical_crossentropy",
                    weighted_metrics=["accuracy"])
import time
t0 = time.time()
h2 = transformer.fit(train_ds, epochs=30, validation_data=val_ds, verbose=2)
print(f"\\nbest validation accuracy: {max(h2.history['val_accuracy']):.4f}")
print(f"seconds per epoch: {(time.time()-t0)/30:.1f}")"""),
            ("out", "best validation accuracy: 0.67xx"),

            ("h2", "The three numbers, and the one that matters most"),
            ("py", """import matplotlib.pyplot as plt

plt.figure(figsize=(8, 4.4))
plt.plot(h1.history["val_accuracy"], lw=1.6, label="Transformer, no positions")
plt.plot(h2.history["val_accuracy"], lw=1.6, label="Transformer + positions")
plt.axhline(0.65, ls="--", c="k", lw=1.3, label="GRU seq2seq")
plt.xlabel("epoch"); plt.ylabel("validation accuracy"); plt.legend()
plt.title("Two lines changed")
plt.show()

print("GRU:                    0.65   34.9 M parameters")
print("Transformer, no pos:    0.58   14.4 M parameters")
print("Transformer + pos:      0.67   14.4 M parameters")
print()
print("And each epoch takes about a THIRD the time of the GRU --")
print("no looped state passing, so the whole attention computation")
print("happens in one go on a GPU.")"""),
            ("md",
             "**That speed-up is the consequential number**, not the accuracy. "
             "Parallelisable training is what made scaling to billions of "
             "parameters economically possible — chapter 16 is the "
             "consequence."),
        ],
        "takeaways": [
            "The encoder and decoder blocks are attention plus feedforward, each "
            "with add-and-norm.",
            "`use_causal_mask=True` on decoder self-attention; a padding mask on "
            "cross-attention.",
            "**Attention is order-blind** — shuffle the input and nothing "
            "changes.",
            "Positional embeddings cost two lines; the parallelisability is what "
            "changed the field.",
        ],
    },

    {
        "file": "05_finetuning_roberta.ipynb",
        "title": "Fine-tuning a pretrained Transformer",
        "lede": "124 million parameters, one epoch, and 93.7% on the problem where "
                "chapter 14 hit a 90% ceiling.",
        "needs": "GPU strongly recommended · downloads ~500 MB",
        "section": "04 — Classification with a pretrained Transformer",
        "cells": [
            ("h2", "Causal and masked language models"),
            ("md",
             "| | Causal LM | Masked LM |\n"
             "|---|---|---|\n"
             "| Distribution | p(token \\| **past**) | p(token \\| **surrounding**) |\n"
             "| Attention | causal-masked | bidirectional |\n"
             "| Good at | **generating** | **representing** |\n"
             "| Examples | GPT, Llama — chapter 16 | BERT, RoBERTa — here |\n\n"
             "BERT masks about **15% of tokens** and predicts the originals. No "
             "labels are needed, which is what made the training data available."),

            ("h2", "Loading RoBERTa"),
            ("py", """import keras
import keras_hub

tokenizer = keras_hub.models.Tokenizer.from_preset("roberta_base_en")
backbone = keras_hub.models.Backbone.from_preset("roberta_base_en")

print(f"{backbone.count_params():,} parameters")
backbone.summary()"""),
            ("md",
             "**RoBERTa used 160 GB of web text against BERT's 16 GB of "
             "Wikipedia** — same architecture, ten times the data, and an "
             "estimated few hundred thousand dollars of compute. Twelve encoder "
             "blocks, which is the stacking property we relied on in notebook 04."),

            ("h2", "The tokenizer, and why subwords are mandatory here"),
            ("py", """print(tokenizer("The quick brown fox"))
print()
print("vocabulary size:", tokenizer.vocabulary_size())
print()
for text in ["antidisestablishmentarianism", "keras", "COVID-19"]:
    ids = tokenizer(text)
    print(f"{text:32s} -> {len(ids)} tokens")"""),
            ("md",
             "A 50,000-term vocabulary handles **any** word, including ones "
             "coined after training. Character-level would make sequences far "
             "too long (attention costs grow with the square of length); "
             "word-level would need a vocabulary covering millions of web "
             "documents."),

            ("h2", "Packing, exactly as pretraining did"),
            ("py", """import tensorflow as tf
from keras.utils import text_dataset_from_directory
import pathlib

base_dir = pathlib.Path("aclImdb")
batch_size = 16       # 512-token sequences through 124M parameters

train_ds = text_dataset_from_directory(base_dir / "train", batch_size=batch_size)
val_ds = text_dataset_from_directory(base_dir / "val", batch_size=batch_size)
test_ds = text_dataset_from_directory(base_dir / "test", batch_size=batch_size)

def preprocess(text, label):
    packer = keras_hub.layers.StartEndPacker(
        sequence_length=512,
        start_value=tokenizer.start_token_id,
        end_value=tokenizer.end_token_id,
        pad_value=tokenizer.pad_token_id,
        return_padding_mask=True,
    )
    token_ids, padding_mask = packer(tokenizer(text))
    return {"token_ids": token_ids, "padding_mask": padding_mask}, label

train_p = train_ds.map(preprocess)
val_p = val_ds.map(preprocess)
test_p = test_ds.map(preprocess)

x, y = next(iter(train_p))
print({k: v.shape for k, v in x.items()}, y.shape)"""),
            ("warn",
             "Match the pretraining token order.** RoBERTa expects `<s>`, "
             "content, `</s>`, then `<pad>`. Getting this wrong does not error — "
             "it just trains more slowly and scores worse."),

            ("h2", "The classification head, and why token zero"),
            ("py", """from keras import layers

inputs = backbone.input
x = backbone(inputs)
x = x[:, 0, :]                              # the first token's representation
x = layers.Dropout(0.1)(x)
x = layers.Dense(768, activation="relu")(x)
x = layers.Dropout(0.1)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
classifier = keras.Model(inputs, outputs)
print(f"{classifier.count_params():,} parameters")"""),
            ("md",
             "Mean or max pooling would also work. Taking the first token works "
             "slightly better, and the reason is attention: **the first position "
             "in the final encoder layer can attend to every other position**. "
             "Rather than pooling with something coarse, attention pools "
             "contextually."),

            ("h2", "One epoch, at 5e-5"),
            ("py", """classifier.compile(
    optimizer=keras.optimizers.Adam(5e-5),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)
classifier.fit(train_p, validation_data=val_p, epochs=1, verbose=2)
print("\\ntest:", classifier.evaluate(test_p, verbose=0))"""),
            ("out", "test: [0.168, 0.9366]"),
            ("md",
             "**93.7% after a single epoch**, against the 90% ceiling of chapter "
             "14.\n\n"
             "`5e-5` is roughly twenty times smaller than Adam's default. Same "
             "discipline as chapter 8's fine-tuning, for the same reason: large "
             "updates destroy representations that cost $300,000 to learn."),

            ("h2", "What it cost"),
            ("py", """print(f"{'model':38s} {'accuracy':>9s} {'cost':>26s}")
print("-" * 76)
rows = [("bigram bag-of-words (ch14)", 0.902, "seconds, CPU"),
        ("sequence model + embeddings (ch14)", 0.90, "minutes, one GPU"),
        ("RoBERTa base, 1 epoch", 0.937, "124M params, ~1 GPU-hour"),
        ("RoBERTa large, fine-tuned", 0.95, "300M params")]
for name, acc, cost in rows:
    print(f"{name:38s} {acc:>9.3f} {cost:>26s}")
print()
print("Three points of accuracy for roughly four orders of magnitude")
print("of compute. Whether that is worth it is chapter 18's question,")
print("and it does not have a universal answer.")"""),

            ("h2", "Try the ablation that matters"),
            ("py", """import numpy as np

# Freeze the backbone entirely: train only the head.
backbone.trainable = False
frozen = keras.Model(inputs, outputs)
frozen.compile(optimizer=keras.optimizers.Adam(1e-3),
               loss="binary_crossentropy", metrics=["accuracy"])
print("trainable parameters with the backbone frozen:",
      f"{sum(int(np.prod(w.shape)) for w in frozen.trainable_weights):,}")
print()
print("Train this and compare. Feature extraction alone usually gets")
print("most of the way; fine-tuning the backbone buys the last points --")
print("the same ordering as chapter 8's vision models.")"""),
            ("md",
             "Chapter 16 takes this further with **LoRA**, which makes "
             "fine-tuning a billion-parameter model fit in 16 GB — a technique "
             "that only exists because full fine-tuning does not."),
        ],
        "takeaways": [
            "Masked LMs represent text; causal LMs generate it. RoBERTa is the "
            "former.",
            "Match the pretraining tokenizer **and** its packing format.",
            "Take the first token's representation — attention has already "
            "pooled contextually.",
            "One epoch at 5e-5 gives 93.7%, for about four orders of magnitude "
            "more compute than a bigram model.",
        ],
    },
]
