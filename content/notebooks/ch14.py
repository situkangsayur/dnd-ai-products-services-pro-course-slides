# -*- coding: utf-8 -*-
"""Chapter 14 notebooks — Text Classification."""

DECK = "ch14"

NOTEBOOKS = [
    {
        "file": "01_tokenizers.ipynb",
        "title": "Three levels of tokenization, and the trade between them",
        "lede": "Character, word, and subword — built by hand, measured against each "
                "other, so that byte-pair encoding stops being a name and becomes a "
                "solution to a stated problem.",
        "needs": "CPU — about 2 minutes",
        "section": "01 — Preparing text data",
        "cells": [
            ("h2", "The simplest tokenizer there is"),
            ("py", """import re
import string

def standardize(text):
    text = text.lower()
    return "".join(c for c in text if c not in string.punctuation)

def tokenize(text):
    return standardize(text).split()

sentence = "The cat sat on the mat, and the mat was NOT amused."
print(tokenize(sentence))"""),
            ("md",
             "Lowercase, strip punctuation, split on whitespace. Every decision "
             "here is a **loss of information**, and each is defensible in some "
             "contexts and not others: lowercasing loses the distinction between "
             "*US* and *us*; stripping punctuation loses the question mark."),

            ("h2", "Character level"),
            ("py", """text = open(__file__).read() if False else (
    "the quick brown fox jumps over the lazy dog. " * 200)

chars = sorted(set(text))
print(f"vocabulary: {len(chars)} characters")
print(f"sequence length for one sentence: "
      f"{len('the quick brown fox jumps over the lazy dog.')}")"""),
            ("md",
             "**Tiny vocabulary, very long sequences.** Nothing is ever "
             "out-of-vocabulary — it can encode any string in any language — and "
             "the model has to learn spelling before it can learn meaning."),

            ("h2", "Word level"),
            ("py", """from keras.datasets import imdb

word_index = imdb.get_word_index()
print(f"vocabulary: {len(word_index):,} words")

# The long tail, which is where the trouble is.
import numpy as np
ranks = np.arange(1, len(word_index) + 1)
covered = {10_000: 0, 20_000: 0, 50_000: 0}
print("\\nTruncating the vocabulary drops the rare words:")
for k in covered:
    print(f"  keep the {k:,} most common -> "
          f"{len(word_index) - k:,} words become <UNK>")"""),
            ("md",
             "**Short sequences, huge vocabulary.** And the vocabulary is a "
             "long tail: keeping the top 10,000 words is standard and throws "
             "away 80,000 of them. Every discarded word becomes `<UNK>` — "
             "identical to every other discarded word."),

            ("h2", "Byte-pair encoding, built"),
            ("md",
             "The idea: start from characters, then repeatedly **merge the most "
             "frequent adjacent pair** into a new token. Common words end up as "
             "one token; rare words decompose into pieces."),
            ("py", """from collections import Counter

def get_stats(vocab):
    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[symbols[i], symbols[i + 1]] += freq
    return pairs

def merge_vocab(pair, vocab):
    out = {}
    bigram = re.escape(" ".join(pair))
    p = re.compile(r"(?<!\\S)" + bigram + r"(?!\\S)")
    for word in vocab:
        out[p.sub("".join(pair), word)] = vocab[word]
    return out

corpus = ("low low low low low lowest lowest newer newer newer newer "
          "newer newer wider wider wider new new")
vocab = Counter(corpus.split())
vocab = {" ".join(w) + " </w>": c for w, c in vocab.items()}

print("start:", list(vocab)[:3], "...\\n")
merges = []
for i in range(10):
    pairs = get_stats(vocab)
    if not pairs:
        break
    best = max(pairs, key=pairs.get)
    merges.append(best)
    vocab = merge_vocab(best, vocab)
    print(f"merge {i+1:2d}: {best[0]!r} + {best[1]!r} -> {''.join(best)!r}"
          f"   (seen {pairs[best]} times)")"""),
            ("py", """print("\\nfinal vocabulary:")
for w, c in vocab.items():
    print(f"  {w!r}  x{c}")"""),
            ("md",
             "`er</w>`, `low`, `new` emerge as units because they are frequent. "
             "**A word never seen before still encodes** — into pieces — which "
             "is what removes `<UNK>` from the picture entirely."),

            ("h2", "The trade, measured"),
            ("py", """sample = "internationalization pretokenization antidisestablishmentarianism"

print(f"{'scheme':12s} {'vocabulary':>12s} {'tokens for the sample':>24s}")
print("-" * 50)
print(f"{'character':12s} {len(set(sample)):>12,} {len(sample):>24}")
print(f"{'word':12s} {88584:>12,} {len(sample.split()):>24}")
print(f"{'subword':12s} {32000:>12,} {'~12 (estimated)':>24}")"""),
            ("md",
             "Subword sits between the two on **both** axes, which is why every "
             "model in chapters 15 through 17 uses it. It is not a compromise so "
             "much as a solution: short sequences *and* a small vocabulary *and* "
             "no unknown words."),

            ("h2", "TextVectorization"),
            ("py", """import keras
from keras import layers

text_vectorization = layers.TextVectorization(
    output_mode="int",
    max_tokens=20,
    output_sequence_length=10,
)

dataset = ["I write, erase, rewrite",
           "Erase again, and then",
           "A poppy blooms."]
text_vectorization.adapt(dataset)
print(text_vectorization.get_vocabulary())"""),
            ("py", """encoded = text_vectorization("I write, rewrite, and still rewrite again")
print("encoded:", encoded.numpy())

vocab = text_vectorization.get_vocabulary()
inverse = dict(enumerate(vocab))
print("decoded:", " ".join(inverse[int(i)] for i in encoded if int(i) != 0))"""),
            ("warn",
             "`adapt()` is fitting.** It learns the vocabulary from data, so it "
             "must see the training split only. Calling it on the full dataset "
             "puts test vocabulary into the model — chapter 5's leak, wearing a "
             "Keras layer."),

            ("h2", "Index 0 and index 1 are reserved"),
            ("py", """print(f"index 0: {vocab[0]!r}  (padding)")
print(f"index 1: {vocab[1]!r}  (out of vocabulary)")
print()
print("Sequences are padded to a fixed length with 0, and every unknown")
print("word collapses to 1. Both are information the model has to work")
print("around, and both are visible in the encoded output above.")"""),
        ],
        "takeaways": [
            "Character level: tiny vocabulary, very long sequences, no unknown "
            "words.",
            "Word level: short sequences, enormous vocabulary, a long tail that "
            "becomes `<UNK>`.",
            "**BPE merges frequent adjacent pairs**, getting both short sequences "
            "and a small vocabulary.",
            "`adapt()` fits on data — training split only.",
        ],
    },

    {
        "file": "02_bag_of_words_and_bigrams.ipynb",
        "title": "Bag-of-words, and what one word of context buys",
        "lede": "Throw word order away entirely and get 88% on IMDB. Then add bigrams "
                "and get 90%. Both numbers are more interesting than they look.",
        "needs": "CPU — about 3 minutes",
        "section": "02 — Sets: the bag-of-words approach",
        "cells": [
            ("h2", "The data, as raw text"),
            ("py", """import os, pathlib, shutil, random
import keras

# The book downloads aclImdb; adjust the path if you already have it.
base_dir = pathlib.Path("aclImdb")
if not base_dir.exists():
    zip_path = keras.utils.get_file(
        origin="https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz",
        fname="imdb", extract=True)
    base_dir = pathlib.Path(zip_path) / "aclImdb"
    shutil.rmtree(base_dir / "train" / "unsup", ignore_errors=True)

val_dir = base_dir / "val"
train_dir = base_dir / "train"
if not val_dir.exists():
    for category in ("neg", "pos"):
        os.makedirs(val_dir / category)
        files = os.listdir(train_dir / category)
        random.Random(1337).shuffle(files)
        num_val_samples = int(0.2 * len(files))
        for fname in files[-num_val_samples:]:
            shutil.move(train_dir / category / fname, val_dir / category / fname)

from keras.utils import text_dataset_from_directory
batch_size = 32
train_ds = text_dataset_from_directory(base_dir / "train", batch_size=batch_size)
val_ds = text_dataset_from_directory(base_dir / "val", batch_size=batch_size)
test_ds = text_dataset_from_directory(base_dir / "test", batch_size=batch_size)

for inputs, targets in train_ds:
    print("inputs.shape:", inputs.shape, inputs.dtype)
    print("first review:", inputs[0].numpy()[:200], "...")
    print("label:", targets[0].numpy())
    break"""),

            ("h2", "Unigrams, multi-hot"),
            ("py", """from keras import layers

text_vectorization = layers.TextVectorization(
    max_tokens=20000, output_mode="multi_hot")

text_only_train_ds = train_ds.map(lambda x, y: x)
text_vectorization.adapt(text_only_train_ds)      # training split only

binary_1gram_train_ds = train_ds.map(
    lambda x, y: (text_vectorization(x), y), num_parallel_calls=4)
binary_1gram_val_ds = val_ds.map(
    lambda x, y: (text_vectorization(x), y), num_parallel_calls=4)
binary_1gram_test_ds = test_ds.map(
    lambda x, y: (text_vectorization(x), y), num_parallel_calls=4)

for inputs, targets in binary_1gram_train_ds:
    print("inputs.shape:", inputs.shape)
    print("a single review:", inputs[0].numpy()[:20], "...")
    break"""),
            ("md",
             "A 20,000-vector of ones and zeros. **Word order is gone "
             "completely** — *dog bites man* and *man bites dog* are the same "
             "input."),

            ("h2", "The model, and a number to remember"),
            ("py", """def get_model(max_tokens=20000, hidden_dim=16):
    inputs = keras.Input(shape=(max_tokens,))
    x = layers.Dense(hidden_dim, activation="relu")(inputs)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs, outputs)
    model.compile(optimizer="rmsprop", loss="binary_crossentropy",
                  metrics=["accuracy"])
    return model

model = get_model()
cb = [keras.callbacks.ModelCheckpoint("binary_1gram.keras",
                                      save_best_only=True)]
model.fit(binary_1gram_train_ds.cache(),
          validation_data=binary_1gram_val_ds.cache(),
          epochs=10, callbacks=cb, verbose=2)

model = keras.models.load_model("binary_1gram.keras")
acc_1gram = model.evaluate(binary_1gram_test_ds, verbose=0)[1]
print(f"\\nunigram test accuracy: {acc_1gram:.3f}")"""),
            ("out", "unigram test accuracy: 0.88x"),
            ("md",
             "**Eighty-eight percent, with no word order at all.** That number "
             "is worth sitting with. Sentiment is largely carried by *which "
             "words appear*, and a great deal of what looks like language "
             "understanding is vocabulary statistics."),

            ("h2", "Bigrams"),
            ("py", """text_vectorization = layers.TextVectorization(
    ngrams=2, max_tokens=20000, output_mode="multi_hot")
text_vectorization.adapt(text_only_train_ds)

binary_2gram_train_ds = train_ds.map(
    lambda x, y: (text_vectorization(x), y), num_parallel_calls=4)
binary_2gram_val_ds = val_ds.map(
    lambda x, y: (text_vectorization(x), y), num_parallel_calls=4)
binary_2gram_test_ds = test_ds.map(
    lambda x, y: (text_vectorization(x), y), num_parallel_calls=4)

model = get_model()
cb = [keras.callbacks.ModelCheckpoint("binary_2gram.keras",
                                      save_best_only=True)]
model.fit(binary_2gram_train_ds.cache(),
          validation_data=binary_2gram_val_ds.cache(),
          epochs=10, callbacks=cb, verbose=2)

model = keras.models.load_model("binary_2gram.keras")
acc_2gram = model.evaluate(binary_2gram_test_ds, verbose=0)[1]
print(f"\\nbigram test accuracy: {acc_2gram:.3f}  "
      f"(+{acc_2gram - acc_1gram:.3f})")"""),
            ("out", "bigram test accuracy: 0.90x  (+0.02x)"),
            ("md",
             "Two points, from **one word of context**. `\"not good\"` is now a "
             "feature in its own right rather than *not* plus *good*.\n\n"
             "That is the entire argument for local order, and it is worth "
             "noting how small it is — which is what makes the sequence models "
             "in the next notebook a harder sell than they first appear."),

            ("h2", "TF-IDF"),
            ("py", """text_vectorization = layers.TextVectorization(
    ngrams=2, max_tokens=20000, output_mode="tf_idf")
text_vectorization.adapt(text_only_train_ds)

tfidf_train_ds = train_ds.map(lambda x, y: (text_vectorization(x), y),
                              num_parallel_calls=4)
tfidf_val_ds = val_ds.map(lambda x, y: (text_vectorization(x), y),
                          num_parallel_calls=4)
tfidf_test_ds = test_ds.map(lambda x, y: (text_vectorization(x), y),
                            num_parallel_calls=4)

model = get_model()
cb = [keras.callbacks.ModelCheckpoint("tfidf_2gram.keras",
                                      save_best_only=True)]
model.fit(tfidf_train_ds.cache(), validation_data=tfidf_val_ds.cache(),
          epochs=10, callbacks=cb, verbose=2)
acc_tfidf = keras.models.load_model("tfidf_2gram.keras").evaluate(
    tfidf_test_ds, verbose=0)[1]
print(f"\\nTF-IDF bigram test accuracy: {acc_tfidf:.3f}")"""),
            ("md",
             "**Term frequency divided by document frequency**: a word that "
             "appears in every review carries no signal; one that appears in "
             "this review and few others does. TF-IDF is decades older than deep "
             "learning and still competitive on short texts."),

            ("h2", "Which words the model relies on"),
            ("py", """import numpy as np
import matplotlib.pyplot as plt

tv = layers.TextVectorization(max_tokens=20000, output_mode="multi_hot")
tv.adapt(text_only_train_ds)
vocab = tv.get_vocabulary()

m = keras.models.load_model("binary_1gram.keras")
W1 = m.layers[1].get_weights()[0]      # (20000, 16)
W2 = m.layers[3].get_weights()[0]      # (16, 1)
influence = (W1 @ W2).ravel()

order = influence.argsort()
print("most negative words:")
for i in order[:12]:
    print(f"  {vocab[i]:16s} {influence[i]:+.3f}")
print("\\nmost positive words:")
for i in order[::-1][:12]:
    print(f"  {vocab[i]:16s} {influence[i]:+.3f}")"""),
            ("md",
             "A crude linearization — the network is not linear — but "
             "informative. Expect *worst*, *waste*, *awful* at one end and "
             "*excellent*, *perfect*, *wonderful* at the other. **If you see "
             "something surprising there, look at it**: that is where dataset "
             "artifacts hide."),
        ],
        "takeaways": [
            "Bag-of-words discards order entirely and still reaches 88% on "
            "sentiment.",
            "Bigrams add one word of context for two points — a small, real gain.",
            "TF-IDF downweights words that appear everywhere; still competitive "
            "on short texts.",
            "Inspecting the most influential words is cheap and finds dataset "
            "artifacts.",
        ],
    },

    {
        "file": "03_sequence_models.ipynb",
        "title": "Sequence models, and the trap of one-hot inputs",
        "lede": "A bidirectional LSTM that loses to bag-of-words, the diagnosis, and "
                "the embedding layer that fixes it.",
        "needs": "GPU recommended — about 30 minutes on CPU · continues from notebook 02 (same kernel)",
        "section": "03 — Sequences: the sequence model approach",
        "cells": [
            ("h2", "Integer sequences, not multi-hot"),
            ("py", """import keras
from keras import layers

max_length = 600
max_tokens = 20000
text_vectorization = layers.TextVectorization(
    max_tokens=max_tokens,
    output_mode="int",
    output_sequence_length=max_length,
)
text_vectorization.adapt(text_only_train_ds)

int_train_ds = train_ds.map(lambda x, y: (text_vectorization(x), y),
                            num_parallel_calls=4)
int_val_ds = val_ds.map(lambda x, y: (text_vectorization(x), y),
                        num_parallel_calls=4)
int_test_ds = test_ds.map(lambda x, y: (text_vectorization(x), y),
                          num_parallel_calls=4)

for x, y in int_train_ds:
    print(x.shape, x.dtype)
    break"""),

            ("h2", "The naive version: one-hot into an LSTM"),
            ("py", """from keras import ops

inputs = keras.Input(shape=(None,), dtype="int64")
embedded = ops.one_hot(inputs, num_classes=max_tokens)
x = layers.Bidirectional(layers.LSTM(32))(embedded)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(optimizer="rmsprop", loss="binary_crossentropy",
              metrics=["accuracy"])
model.summary()"""),
            ("warn",
             "Every timestep is a 20,000-dimensional vector.** 600 timesteps × "
             "20,000 = 12 million numbers per review, almost all of them zero. "
             "This will be extremely slow, and it is the point of the exercise."),
            ("py", """cb = [keras.callbacks.ModelCheckpoint("one_hot_bidir_lstm.keras",
                                      save_best_only=True)]
model.fit(int_train_ds, validation_data=int_val_ds, epochs=10,
          callbacks=cb, verbose=2)
acc = keras.models.load_model("one_hot_bidir_lstm.keras").evaluate(
    int_test_ds, verbose=0)[1]
print(f"\\none-hot LSTM test accuracy: {acc:.3f}   "
      f"(bag-of-bigrams was 0.90)")"""),
            ("out", "one-hot LSTM test accuracy: 0.87x   (bag-of-bigrams was 0.90)"),
            ("md",
             "**Slower, more complex, and worse.** Two reasons, and the second "
             "is the fixable one:\n\n"
             "- The input representation is enormous and sparse.\n"
             "- **One-hot vectors are all equidistant.** *excellent* and *good* "
             "are exactly as far apart as *excellent* and *refrigerator*. The "
             "representation asserts that all words are unrelated, which is "
             "false."),

            ("h2", "An Embedding layer"),
            ("py", """inputs = keras.Input(shape=(None,), dtype="int64")
embedded = layers.Embedding(input_dim=max_tokens, output_dim=256)(inputs)
x = layers.Bidirectional(layers.LSTM(32))(embedded)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(optimizer="rmsprop", loss="binary_crossentropy",
              metrics=["accuracy"])
model.summary()"""),
            ("md",
             "**256 dimensions instead of 20,000**, and the geometry is learned "
             "rather than imposed. An `Embedding` layer is a lookup table: token "
             "*i* returns row *i*, and those rows are trained by "
             "backpropagation like any other weights."),

            ("h2", "Masking, which is not optional"),
            ("py", """inputs = keras.Input(shape=(None,), dtype="int64")
embedded = layers.Embedding(input_dim=max_tokens, output_dim=256,
                            mask_zero=True)(inputs)
x = layers.Bidirectional(layers.LSTM(32))(embedded)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(optimizer="rmsprop", loss="binary_crossentropy",
              metrics=["accuracy"])

cb = [keras.callbacks.ModelCheckpoint("embeddings_bidir_lstm_masked.keras",
                                      save_best_only=True)]
model.fit(int_train_ds, validation_data=int_val_ds, epochs=10,
          callbacks=cb, verbose=2)
acc_masked = keras.models.load_model(
    "embeddings_bidir_lstm_masked.keras").evaluate(int_test_ds, verbose=0)[1]
print(f"\\nembedding + masking test accuracy: {acc_masked:.3f}")"""),
            ("out", "embedding + masking test accuracy: 0.87x — 0.88x"),
            ("md",
             "`mask_zero=True` tells every downstream layer to **skip the "
             "padding**. Without it, a 20-word review padded to 600 gives the "
             "LSTM 580 steps of nothing to process, and the state it arrives "
             "with has been diluted by all of them."),

            ("h2", "The scoreboard, and the honest reading"),
            ("py", """import matplotlib.pyplot as plt

results = [("bag-of-words (unigram)", 0.885),
           ("bag-of-bigrams", 0.902),
           ("TF-IDF bigrams", 0.897),
           ("one-hot bidir LSTM", 0.873),
           ("embedding bidir LSTM", 0.874),
           ("+ masking", acc_masked)]

names = [r[0] for r in results]; vals = [r[1] for r in results]
plt.figure(figsize=(8.5, 4))
plt.barh(names[::-1], vals[::-1],
         color=["#12b886" if v >= 0.9 else "#888" for v in vals][::-1])
plt.xlim(0.84, 0.92); plt.xlabel("test accuracy")
plt.title("On this dataset, bag-of-bigrams wins")
plt.tight_layout(); plt.show()"""),
            ("md",
             "**The bag-of-words model wins.** That is the honest result on "
             "IMDB, and the chapter says so.\n\n"
             "The rule the book gives is a ratio: **number of training samples "
             "divided by mean sample length**. Below about 1,500, bag-of-words "
             "wins. IMDB has 20,000 samples of ~230 words, giving 87 — well "
             "inside bag-of-words territory."),
            ("py", """import numpy as np

lengths = []
for x, _ in train_ds.take(50):
    lengths += [len(s.numpy().split()) for s in x]
ratio = 20000 / np.mean(lengths)
print(f"mean review length: {np.mean(lengths):.0f} words")
print(f"ratio: 20000 / {np.mean(lengths):.0f} = {ratio:.0f}")
print(f"\\nrule of thumb: below ~1500 -> bag-of-words; above -> sequence model")
print(f"this dataset: {ratio:.0f}  ->  {'bag-of-words' if ratio < 1500 else 'sequence model'}")"""),
        ],
        "takeaways": [
            "One-hot inputs assert that every word is equidistant from every "
            "other, which is false.",
            "`Embedding` learns a dense geometry instead — 256 dimensions rather "
            "than 20,000.",
            "**`mask_zero=True`** or the recurrent layer processes hundreds of "
            "padding steps.",
            "On IMDB, bag-of-bigrams wins. The samples-to-length ratio predicts "
            "which family to use.",
        ],
    },

    {
        "file": "04_pretraining_an_embedding.ipynb",
        "title": "Pretraining an embedding, and the geometry it learns",
        "lede": "Continuous bag-of-words on unlabelled text, then use of the result — "
                "and a look at the space itself, which is where the interest is.",
        "needs": "CPU — about 10 minutes",
        "section": "04 — Pretraining word embeddings",
        "cells": [
            ("h2", "The idea"),
            ("md",
             "Chapter 8's argument in a new modality. **Labelled data is "
             "scarce; unlabelled text is not.** Train an embedding on a task "
             "that needs no labels — predict a word from its neighbours — and "
             "reuse the geometry."),
            ("py", """import numpy as np
import keras
from keras import layers

# A corpus. Substitute anything larger you have; more text is strictly better.
from keras.datasets import imdb
word_index = imdb.get_word_index()
index_word = {v + 3: k for k, v in word_index.items()}
index_word.update({0: "<PAD>", 1: "<START>", 2: "<UNK>"})

(train_data, _), _ = imdb.load_data(num_words=10000)
print(f"{len(train_data):,} documents, "
      f"{sum(len(d) for d in train_data):,} tokens")"""),

            ("h2", "Building (context, target) pairs"),
            ("py", """WINDOW = 2
VOCAB = 10000

def cbow_pairs(sequences, window=WINDOW, limit=400_000):
    contexts, targets = [], []
    for seq in sequences:
        for i, target in enumerate(seq):
            lo, hi = max(0, i - window), min(len(seq), i + window + 1)
            ctx = [seq[j] for j in range(lo, hi) if j != i]
            if len(ctx) != 2 * window:
                continue
            contexts.append(ctx)
            targets.append(target)
            if len(targets) >= limit:
                return np.array(contexts), np.array(targets)
    return np.array(contexts), np.array(targets)

X, y = cbow_pairs(train_data)
print("contexts:", X.shape, " targets:", y.shape)
print("\\nexample:")
print("  context:", [index_word.get(i, '?') for i in X[100]])
print("  target: ", index_word.get(y[100], '?'))"""),
            ("md",
             "**No labels anywhere.** The supervision comes from the text's own "
             "structure, which is the definition of self-supervised learning and "
             "the same principle behind every model in chapters 15 to 17."),

            ("h2", "The CBOW model"),
            ("py", """EMBED = 128

inputs = keras.Input(shape=(2 * WINDOW,), dtype="int32")
emb = layers.Embedding(VOCAB, EMBED, name="embedding")(inputs)
x = layers.GlobalAveragePooling1D()(emb)     # average the context vectors
outputs = layers.Dense(VOCAB, activation="softmax")(x)
cbow = keras.Model(inputs, outputs)

cbow.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
             metrics=["accuracy"])
cbow.summary()"""),
            ("md",
             "Average the context embeddings, predict the missing word. The "
             "output layer is 10,000-wide and holds most of the parameters — "
             "**and it is thrown away**. The `Embedding` table is the artifact "
             "we are after."),

            ("h2", "Training"),
            ("py", """cbow.fit(X, y, epochs=5, batch_size=512, validation_split=0.05,
         verbose=2)"""),
            ("note",
             "Accuracy will be low — predicting one word out of 10,000 from four "
             "neighbours is genuinely hard. **The accuracy is not the "
             "objective**; the embedding table is."),

            ("h2", "Looking at the space"),
            ("py", """W = cbow.get_layer("embedding").get_weights()[0]
norms = np.linalg.norm(W, axis=1, keepdims=True) + 1e-9
Wn = W / norms

def nearest(word, k=8):
    idx = word_index.get(word)
    if idx is None or idx + 3 >= VOCAB:
        return f"{word!r} not in the vocabulary"
    i = idx + 3
    sims = Wn @ Wn[i]
    top = np.argsort(sims)[::-1][1:k+1]
    return [(index_word.get(j, "?"), round(float(sims[j]), 3)) for j in top]

for w in ["good", "terrible", "film", "actor", "three"]:
    print(f"{w:10s} ->", nearest(w, 6))"""),
            ("md",
             "The neighbours should be **semantically related, not "
             "orthographically similar**. Expect *good* near *great*, *decent*, "
             "*fine*; *three* near other numbers.\n\n"
             "Nothing told the model that numbers form a category. It fell out "
             "of the fact that numbers appear in similar contexts — which is "
             "the whole distributional hypothesis, demonstrated."),

            ("h2", "Projecting it"),
            ("py", """from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

words = ["good", "great", "excellent", "wonderful", "best",
         "bad", "terrible", "awful", "worst", "poor",
         "one", "two", "three", "four", "five",
         "he", "she", "they", "him", "her",
         "movie", "film", "story", "plot", "script"]
idxs = [word_index[w] + 3 for w in words if w in word_index
        and word_index[w] + 3 < VOCAB]
labels = [index_word[i] for i in idxs]

proj = TSNE(n_components=2, perplexity=6, init="pca",
            random_state=0).fit_transform(Wn[idxs])

plt.figure(figsize=(9, 7))
plt.scatter(proj[:, 0], proj[:, 1], s=30, c="#00539f")
for (x0, y0), lab in zip(proj, labels):
    plt.annotate(lab, (x0, y0), fontsize=10,
                 xytext=(4, 4), textcoords="offset points")
plt.title("A learned word geometry"); plt.xticks([]); plt.yticks([])
plt.show()"""),
            ("md",
             "Positive adjectives together, negative adjectives together, "
             "numbers together, pronouns together. **This geometry is what "
             "chapter 15 means by an embedding space**, and what its attention "
             "mechanism repeatedly refines."),

            ("h2", "Using it downstream"),
            ("py", """# Freeze the pretrained table and train only the classifier on top.
pretrained = layers.Embedding(VOCAB, EMBED, trainable=False,
                              name="pretrained_embedding")
pretrained.build((None,))
pretrained.set_weights([W])

inputs = keras.Input(shape=(None,), dtype="int32")
x = pretrained(inputs)
x = layers.Bidirectional(layers.LSTM(32))(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
clf = keras.Model(inputs, outputs)
clf.compile(optimizer="rmsprop", loss="binary_crossentropy",
            metrics=["accuracy"])
print(f"trainable parameters: {sum(np.prod(w.shape) for w in clf.trainable_weights):,}")
print(f"frozen (pretrained):  {np.prod(W.shape):,}")"""),
            ("md",
             "The chapter-8 procedure, exactly: **freeze, train the head, "
             "consider unfreezing later at a lower learning rate.**\n\n"
             "Pretrained embeddings help most when labelled data is scarce. On "
             "the full IMDB training set they help little — 20,000 labelled "
             "reviews is enough to learn a task-specific geometry. Try it with "
             "1,000 and the gap opens."),

            ("h2", "What chapter 15 changes about all this"),
            ("md",
             "One vector per word, fixed. *Bank* gets a single embedding whether "
             "it is a river bank or a savings bank.\n\n"
             "**Chapter 15's attention mechanism produces a different vector for "
             "each occurrence**, conditioned on its neighbours. That is the "
             "single largest step between this notebook and a modern language "
             "model — and the geometry you plotted above is the thing it "
             "refines, layer by layer."),
        ],
        "takeaways": [
            "CBOW learns an embedding from unlabelled text — self-supervision, "
            "as in chapters 15 to 17.",
            "The output layer holds most of the parameters and is discarded; the "
            "table is the artifact.",
            "The learned geometry groups words by **context**, which is the "
            "distributional hypothesis working.",
            "One vector per word is the limitation attention removes.",
        ],
    },
]
