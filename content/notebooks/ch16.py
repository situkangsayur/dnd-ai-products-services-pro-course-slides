# -*- coding: utf-8 -*-
"""Chapter 16 notebooks — Text Generation."""

DECK = "ch16"

NOTEBOOKS = [
    {
        "file": "01_mini_gpt_data_pipeline.ipynb",
        "title": "A billion tokens, and the pipeline that feeds them",
        "lede": "Interleaved shards, a fast tokenizer, and the design decision GPT made "
                "about document boundaries.",
        "needs": "CPU — 10 minutes, mostly tokenizing · ~4 GB of disk",
        "section": "01 — Training a mini-GPT",
        "cells": [
            ("h2", "The corpus"),
            ("py", """import keras
import pathlib

extract_dir = keras.utils.get_file(
    fname="mini-c4",
    origin=("https://hf.co/datasets/mattdangerw/mini-c4/resolve/main/"
            "mini-c4.zip"),
    extract=True)
extract_dir = pathlib.Path(extract_dir) / "mini-c4"

shards = sorted(extract_dir.glob("*.txt"))
print(f"{len(shards)} shards")
print(f"first shard: {shards[0].stat().st_size / 1e6:.0f} MB")"""),
            ("md",
             "**C4** — the Colossal Clean Crawled Corpus, 750 GB in full. We "
             "take under 1%. GPT-1 used BooksCorpus, self-published books added "
             "without their authors' permission; it has since been taken down by "
             "its publishers."),

            ("h2", "What one document looks like"),
            ("py", """with open(shards[0], "r") as f:
    print(f.readline().replace("\\\\n", "\\n")[:300])"""),
            ("md",
             "Crawled web text: a headline, a newline, marketing copy. **Hold "
             "that image** — it is what the model's distribution will be made "
             "of, and it explains the output later in this chapter."),

            ("h2", "SentencePiece"),
            ("py", """import keras_hub
import numpy as np

vocabulary_file = keras.utils.get_file(
    origin="https://hf.co/mattdangerw/spiece/resolve/main/vocabulary.proto")
tokenizer = keras_hub.tokenizers.SentencePieceTokenizer(vocabulary_file)

print(tokenizer.tokenize("The quick brown fox."))
print(tokenizer.detokenize([450, 4996, 17354, 1701, 29916, 29889]))
print(f"\\nvocabulary: {tokenizer.vocabulary_size():,}")"""),
            ("md",
             "Exactly the byte-pair encoding from chapter 14's notebook 01, "
             "implemented in C++ and with a `detokenize()`. **Same technique, "
             "different engineering** — which is the right reason to reach for a "
             "library."),

            ("h2", "Document boundaries as a token"),
            ("py", """eot = tokenizer.token_to_id("<|endoftext|>")
print(f"<|endoftext|> is token {eot}")
print()
print("GPT makes NO attempt to keep document boundaries out of the middle")
print("of a training sample. Documents are concatenated and the boundary")
print("is marked with this token.")
print()
print("Simplicity in the pipeline, paid for with one vocabulary entry --")
print("and a recurring pattern: when a structural constraint is expensive")
print("to enforce in data, encode it as a token and let the model learn it.")"""),

            ("h2", "The pipeline"),
            ("py", """import tensorflow as tf

batch_size = 128
sequence_length = 256
suffix = np.array([eot])

def read_file(filename):
    ds = tf.data.TextLineDataset(filename)
    ds = ds.map(lambda x: tf.strings.regex_replace(x, r"\\\\n", "\\n"))
    ds = ds.map(tokenizer, num_parallel_calls=8)
    return ds.map(lambda x: tf.concat([x, suffix], -1))

files = [str(f) for f in shards]
ds = tf.data.Dataset.from_tensor_slices(files)
ds = ds.interleave(read_file, cycle_length=32, num_parallel_calls=32)
ds = ds.rebatch(sequence_length + 1, drop_remainder=True)
ds = ds.map(lambda x: (x[:-1], x[1:]))
ds = ds.batch(batch_size).prefetch(8)

for x, y in ds.take(1):
    print("inputs: ", x.shape)
    print("targets:", y.shape)
    print("\\noffset by one, exactly as in chapter 15:")
    print(" x[0][:8] =", x[0][:8].numpy())
    print(" y[0][:8] =", y[0][:8].numpy())
    break"""),
            ("md",
             "**`interleave`** lets every CPU core tokenize a different shard "
             "simultaneously. **`rebatch(257)`** windows the token stream into "
             "even samples. **`prefetch(8)`** keeps batches ready so the GPU "
             "never waits — chapter 18 returns to this as the thing that turns "
             "eight expensive GPUs into eight expensive idle GPUs."),

            ("h2", "The size of it"),
            ("py", """num_batches = 29373        # counted once; see the note below
num_val_batches = 500
num_train_batches = num_batches - num_val_batches

val_ds = ds.take(num_val_batches).repeat()
train_ds = ds.skip(num_val_batches).repeat()

print(f"{num_batches:,} batches x {batch_size} samples x "
      f"{sequence_length} tokens")
print(f"= {num_batches * batch_size * sequence_length / 1e9:.2f} billion tokens")
print()
print("Counting it yourself:  ds.reduce(0, lambda c, _: c + 1)")
print("...but tokenizing a dataset this size takes several minutes on a")
print("fast CPU, so the number is hardcoded above.")"""),

            ("h2", "Sanity-check the pipeline before spending six hours on it"),
            ("py", """for x, y in train_ds.take(1):
    sample = x[0].numpy()
    print("decoded first sample:\\n")
    text = tokenizer.detokenize(sample)
    text = text.numpy().decode() if hasattr(text, "numpy") else str(text)
    print(text[:600])
    print("\\n---")
    print("does it contain a document boundary?",
          bool((sample == eot).any()))
    break"""),
            ("md",
             "**Read the decoded text before training.** A pipeline bug here — "
             "a wrong regex, a misaligned offset — costs six hours of GPU time "
             "and produces a model that trains happily on nonsense."),
        ],
        "takeaways": [
            "`interleave` parallelises tokenization across shards; `prefetch` "
            "keeps the accelerator fed.",
            "GPT concatenates documents and marks boundaries with a token rather "
            "than respecting them in the data.",
            "The offset-by-one split is chapter 15's, unchanged.",
            "Decode a sample and read it before starting an expensive run.",
        ],
    },

    {
        "file": "02_training_mini_gpt.ipynb",
        "title": "Forty-one million parameters, and the tricks that make them train",
        "lede": "Decoder-only blocks, tied embeddings, warmup, and a logits-based loss — "
                "the most compute-intensive run in the whole course.",
        "needs": "GPU required — ~6 hours on a Colab T4, ~1 hour on an A100 · continues from notebook 01 (same kernel)",
        "section": "01 — Training a mini-GPT",
        "cells": [
            ("h2", "The decoder block, minus cross-attention"),
            ("py", """import keras
from keras import layers, ops

class TransformerDecoder(keras.Layer):
    def __init__(self, hidden_dim, intermediate_dim, num_heads):
        super().__init__()
        key_dim = hidden_dim // num_heads
        self.self_attention = layers.MultiHeadAttention(
            num_heads, key_dim, dropout=0.1)
        self.self_attention_layernorm = layers.LayerNormalization()
        self.feed_forward_1 = layers.Dense(intermediate_dim, activation="relu")
        self.feed_forward_2 = layers.Dense(hidden_dim)
        self.feed_forward_layernorm = layers.LayerNormalization()
        self.dropout = layers.Dropout(0.1)

    def call(self, inputs):
        residual = x = inputs
        x = self.self_attention(query=x, key=x, value=x, use_causal_mask=True)
        x = self.dropout(x)
        x = self.self_attention_layernorm(x + residual)

        residual = x
        x = self.feed_forward_1(x)
        x = self.feed_forward_2(x)
        x = self.dropout(x)
        x = self.feed_forward_layernorm(x + residual)
        return x"""),
            ("md",
             "Chapter 15's decoder with cross-attention removed and dropout "
             "added **inside** each block — chapter 15 stacked one layer and got "
             "away with one dropout at the end; here we stack eight.\n\n"
             "`use_causal_mask=True` is the only thing standing between this "
             "model and reading its own labels."),

            ("h2", "Tied embeddings"),
            ("py", """class PositionalEmbedding(keras.Layer):
    def __init__(self, sequence_length, input_dim, output_dim):
        super().__init__()
        self.token_embeddings = layers.Embedding(input_dim, output_dim)
        self.position_embeddings = layers.Embedding(sequence_length, output_dim)

    def call(self, inputs, reverse=False):
        if reverse:
            token_embeddings = self.token_embeddings.embeddings
            return ops.matmul(inputs, ops.transpose(token_embeddings))
        positions = ops.cumsum(ops.ones_like(inputs), axis=-1) - 1
        return (self.token_embeddings(inputs)
                + self.position_embeddings(positions))

vocab_size, hidden_dim = 32000, 512
saved = vocab_size * hidden_dim
print(f"one matrix used twice saves {saved:,} parameters")
print(f"= {saved / 41_000_000:.0%} of a 41M-parameter model")"""),
            ("md",
             "The two largest weights in a Transformer are both "
             "vocabulary-shaped: the token embedding **(vocab, hidden)** and the "
             "output projection **(hidden, vocab)**. They are transposes in "
             "shape; making them transposes in **value** works well.\n\n"
             "Think of the output as a *reverse embedding*: hidden space back to "
             "token space."),

            ("h2", "The model"),
            ("py", """keras.config.set_dtype_policy("mixed_float16")

intermediate_dim, num_heads, num_layers = 2056, 8, 8
sequence_length = 256

inputs = keras.Input(shape=(None,), dtype="int32", name="inputs")
embedding = PositionalEmbedding(sequence_length, vocab_size, hidden_dim)
x = embedding(inputs)
x = layers.LayerNormalization()(x)
for _ in range(num_layers):
    x = TransformerDecoder(hidden_dim, intermediate_dim, num_heads)(x)
outputs = embedding(x, reverse=True)
mini_gpt = keras.Model(inputs, outputs)

print(f"{mini_gpt.count_params():,} parameters")
print("GPT-1 had 117 million; GPT-3 had 175 billion.")"""),
            ("note",
             "`mixed_float16` trades some numerical fidelity for roughly 2× "
             "speed. Chapter 18 explains what it is doing and why loss scaling "
             "goes with it."),

            ("h2", "Warmup"),
            ("py", """import matplotlib.pyplot as plt
import numpy as np

class WarmupSchedule(keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self):
        self.rate = 2e-4
        self.warmup_steps = 1_000.0

    def __call__(self, step):
        step = ops.cast(step, dtype="float32")
        scale = ops.minimum(step / self.warmup_steps, 1.0)
        return self.rate * scale

schedule = WarmupSchedule()
xs = range(0, 5000, 50)
ys = [float(ops.convert_to_numpy(schedule(s))) for s in xs]
plt.figure(figsize=(6.5, 3.6))
plt.plot(xs, ys, lw=1.8)
plt.xlabel("train step"); plt.ylabel("learning rate")
plt.title("Linear warmup over 1,000 steps, then flat")
plt.show()"""),
            ("md",
             "Stack many Transformer layers and **exploding gradients** are "
             "easy to hit — parameters update too fast and the loss never "
             "converges. A linear ramp keeps the earliest updates small.\n\n"
             "**Plot the schedule before training.** A wrong schedule is "
             "invisible in the loss curve until it is far too late."),

            ("h2", "What is a logit?"),
            ("py", """print("The output projection has NO softmax activation.")
print()
print("Its outputs are unnormalized log probabilities. Exponentiate and")
print("normalize -- which is all softmax does -- and you get probabilities.")
print()
print("  softmax IN THE MODEL:  Dense(n, activation='softmax')")
print("                       + SparseCategoricalCrossentropy()")
print()
print("  softmax IN THE LOSS:   Dense(n)")
print("                       + SparseCategoricalCrossentropy(from_logits=True)")
print()
print("The second is more numerically stable and far easier to sample from,")
print("which is what the next notebook needs.")"""),

            ("h2", "Training"),
            ("py", """num_epochs = 8
num_train_batches, num_val_batches = 28873, 500
steps_per_epoch = num_train_batches // num_epochs

mini_gpt.compile(
    optimizer=keras.optimizers.Adam(schedule),
    loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)
mini_gpt.fit(
    train_ds,
    validation_data=val_ds,
    epochs=num_epochs,
    steps_per_epoch=steps_per_epoch,
    validation_steps=num_val_batches,
    callbacks=[keras.callbacks.ModelCheckpoint("mini_gpt.keras",
                                               save_best_only=True)],
    verbose=2,
)"""),
            ("warn",
             "This is the most computationally expensive run in the book.** "
             "Six hours on a free Colab T4. Set it going and take a break — or "
             "cut `steps_per_epoch` for a quick experiment and accept a worse "
             "model."),

            ("h2", "The honest reading of the result"),
            ("md",
             "About **36% next-token accuracy** — and the validation loss is "
             "**still falling** after the last epoch.\n\n"
             "This model is not converged and we know it. That is unsurprising "
             "with a hundred times fewer training steps than GPT-1, and it is "
             "worth stating plainly: most published curves stop where the budget "
             "ran out, not where the model stopped improving.\n\n"
             "**The gap to a modern LLM is 100× the parameters and 1,000× the "
             "steps — and nothing else.** The recipe above is the one everyone "
             "is using."),
        ],
        "takeaways": [
            "Decoder-only: chapter 15's block with cross-attention removed and "
            "dropout added inside.",
            "Tied embeddings use one matrix forward and transposed, saving a "
            "large share of the parameters.",
            "Warmup prevents exploding gradients; plot the schedule before "
            "training.",
            "`from_logits=True` is more stable and much easier to sample from.",
        ],
    },

    {
        "file": "03_sampling_strategies.ipynb",
        "title": "Greedy, random, temperature, top-K",
        "lede": "The model gives you a distribution over 32,000 tokens. What you do with "
                "it is a separate design decision — with two opposite failure modes and "
                "a dial between them.",
        "needs": "GPU recommended — needs the model from notebook 02",
        "section": "02 — Sampling strategies",
        "cells": [
            ("h2", "The naive loop, and why it is slow"),
            ("py", """import keras
from keras import ops
import numpy as np
import time

mini_gpt = keras.models.load_model("mini_gpt.keras")

def generate(prompt, max_length=64):
    tokens = list(ops.convert_to_numpy(tokenizer(prompt)))
    prompt_length = len(tokens)
    for _ in range(max_length - prompt_length):
        prediction = mini_gpt(ops.convert_to_numpy([tokens]))
        prediction = ops.convert_to_numpy(prediction[0, -1])
        tokens.append(np.argmax(prediction).item())
    return tokenizer.detokenize(tokens)

prompt = "A piece of advice"
t0 = time.time()
print(generate(prompt))
print(f"\\n{time.time()-t0:.1f} seconds")"""),
            ("md",
             "**Minutes**, for 64 tokens — while training ran at 200,000 tokens "
             "per second on the same hardware.\n\n"
             "`fit()` and `predict()` compile the per-batch computation. Calling "
             "the model directly runs the forward pass live and unoptimized at "
             "every step."),

            ("h2", "Padding so the shape never changes"),
            ("py", """def compiled_generate(prompt, max_length=64):
    tokens = list(ops.convert_to_numpy(tokenizer(prompt)))
    prompt_length = len(tokens)
    tokens = tokens + [0] * (max_length - prompt_length)
    for i in range(prompt_length, max_length):
        prediction = mini_gpt.predict(np.array([tokens]), verbose=0)
        prediction = prediction[0, i - 1]
        tokens[i] = np.argmax(prediction).item()
    return tokenizer.detokenize(tokens)

import timeit
tries = 5
compiled_generate(prompt)          # warm up: the first call compiles
t = timeit.timeit(lambda: compiled_generate(prompt), number=tries) / tries
print(f"{t:.3f} seconds per generation")"""),
            ("out", "about 0.5 seconds — from minutes"),
            ("warn",
             "`predict()` compiles for a **specific input shape**.** A sequence "
             "that grows by one token each step triggers recompilation every "
             "call. Padding to full length keeps the shape constant.\n\n"
             "A large share of real-world inference cost is lost to exactly "
             "this, and it never appears as an error — only as a bill."),

            ("h2", "The inefficiency that remains"),
            ("md",
             "Each call runs the model over the **whole** sequence and discards "
             "everything but one position, when the sequence changed by one "
             "token.\n\n"
             "Attention is the only place information crosses positions. Past "
             "keys and values never change — the causal mask forbids looking "
             "ahead. **Cache them and you have the Transformer equivalent of an "
             "RNN state**: input shrinks from the whole sequence to one token, "
             "which on a long generation is a thousandfold speed-up.\n\n"
             "Implementing it means saving and reusing intermediate arrays from "
             "every attention layer — which is exactly why you should use a "
             "library that has already done it."),

            ("h2", "Making the strategy a parameter"),
            ("py", """def compiled_generate(prompt, sample_fn, max_length=64):
    tokens = list(ops.convert_to_numpy(tokenizer(prompt)))
    prompt_length = len(tokens)
    tokens = tokens + [0] * (max_length - prompt_length)
    for i in range(prompt_length, max_length):
        prediction = mini_gpt.predict(np.array([tokens]), verbose=0)
        prediction = prediction[0, i - 1]
        next_token = ops.convert_to_numpy(sample_fn(prediction))
        tokens[i] = np.array(next_token).item()
    return tokenizer.detokenize(tokens)

def greedy_search(preds):
    return ops.argmax(preds)

print(compiled_generate(prompt, greedy_search))"""),
            ("md",
             "**The repetition is not a bug.** The model predicts the most "
             "likely next token across a billion words on many topics; where "
             "there is no obvious continuation, guessing common words or "
             "repeated patterns is an effective strategy, and it learns that "
             "almost immediately.\n\n"
             "Stop training very early and it would emit `\"the\"` forever."),

            ("h2", "Random sampling"),
            ("py", """def random_sample(preds, temperature=1.0):
    preds = preds / temperature
    return keras.random.categorical(preds[None, :], num_samples=1)[0]

print(compiled_generate(prompt, random_sample))"""),
            ("md",
             "No longer stuck in loops — and now it **explores too much**. The "
             "output jumps around without continuity. One failure traded for its "
             "opposite."),

            ("h2", "Temperature"),
            ("py", """from functools import partial
import matplotlib.pyplot as plt

# What temperature does to a distribution, before generating anything.
logits = np.array([3.0, 2.5, 2.0, 1.0, 0.5, 0.0, -1.0, -2.0])
fig, axes = plt.subplots(1, 4, figsize=(15, 3))
for ax, T in zip(axes, [0.2, 0.5, 1.0, 2.0]):
    p = np.exp(logits / T); p /= p.sum()
    ax.bar(range(len(p)), p)
    ax.set_title(f"T = {T}   max {p.max():.2f}"); ax.set_ylim(0, 1)
plt.suptitle("Temperature acts on the LOGITS, before the softmax", y=1.04)
plt.tight_layout(); plt.show()"""),
            ("py", """for T in [2.0, 0.8, 0.2]:
    print(f"\\n--- temperature {T} ---")
    print(compiled_generate(prompt, partial(random_sample, temperature=T)))"""),
            ("md",
             "**T = 2.0** — subword fragments, stray identifiers, other "
             "languages. The distribution is flat enough that rare tokens win "
             "regularly, and rare tokens in a 32,000 vocabulary are mostly "
             "debris.\n\n"
             "**T = 0.2** — converges on greedy search, repeating patterns.\n\n"
             "Temperature is a **dial between two known failure modes**, not a "
             "fix for either."),

            ("h2", "Top-K"),
            ("py", """def top_k(preds, k=5, temperature=1.0):
    preds = preds / temperature
    top_preds, top_indices = ops.top_k(preds, k=k, sorted=False)
    choice = keras.random.categorical(top_preds[None, :], num_samples=1)[0]
    return ops.take_along_axis(top_indices, choice, axis=-1)

for k in [5, 20]:
    print(f"\\n--- top-{k} ---")
    print(compiled_generate(prompt, partial(top_k, k=k)))

print("\\n--- top-5, temperature 0.5 (a common production default) ---")
print(compiled_generate(prompt, partial(top_k, k=5, temperature=0.5)))"""),
            ("md",
             "**Temperature and top-K are not the same knob.** A low temperature "
             "makes likely tokens more likely but rules **nothing** out. Top-K "
             "sets everything outside the K candidates to **zero**. They "
             "compose."),

            ("h2", "The four, side by side"),
            ("py", """print(f"{'strategy':16s} {'what it does':44s} {'failure mode'}")
print("-" * 100)
rows = [("Greedy", "argmax at every step", "repeats phrases indefinitely"),
        ("Random", "samples the full categorical distribution", "wanders, no continuity"),
        ("Temperature", "scales logits before the softmax", "a dial between the two above"),
        ("Top-K", "zeroes everything outside K candidates", "K too small collapses to greedy"),
        ("Beam search", "keeps several candidate chains alive", "expensive; can still be bland")]
for a, b, c in rows:
    print(f"{a:16s} {b:44s} {c}")"""),
        ],
        "takeaways": [
            "Calling the model directly is unoptimized; `predict()` with a "
            "**constant input shape** is two orders of magnitude faster.",
            "Key-value caching is the remaining win, and the reason to use a "
            "serving library.",
            "Greedy repeats, random wanders, temperature dials between them, "
            "top-K rules tokens out.",
            "Repetition is the training objective working correctly, asked the "
            "wrong question.",
        ],
    },

    {
        "file": "04_gemma_generation.ipynb",
        "title": "A billion-parameter pretrained model, and what it is actually doing",
        "lede": "Gemma 3, prompted three ways — and the hallucination that survives all "
                "of them.",
        "needs": "GPU recommended · ~4 GB download · Kaggle login required",
        "section": "03 — Using a pretrained LLM",
        "cells": [
            ("h2", "Accepting the terms, then loading"),
            ("py", """# You must accept the Gemma Terms of Use at
#   https://www.kaggle.com/models/keras/gemma3
# and generate an API key at https://www.kaggle.com/settings
import kagglehub
kagglehub.login()"""),
            ("py", """import keras
import keras_hub

gemma_lm = keras_hub.models.CausalLM.from_preset(
    "gemma3_1b",
    dtype="float32",
)
gemma_lm.summary()"""),
            ("md",
             "Almost exactly a billion parameters, trained on roughly **2 "
             "trillion tokens** — two thousand times more than our mini-GPT.\n\n"
             "Two things in the summary are worth reading closely: a vocabulary "
             "of **262,144** terms, and a `ReversibleEmbedding` holding 302 "
             "million of the billion parameters — the tied embedding we built by "
             "hand, counted once."),

            ("h2", "It is a fancy autocomplete for the internet"),
            ("py", """gemma_lm.compile(sampler="greedy")

for prompt in ["A piece of advice",
               "How can I make brownies?"]:
    print(f"--- {prompt!r} ---")
    print(gemma_lm.generate(prompt, max_length=40))
    print()"""),
            ("md",
             "Far more coherent than mini-GPT, and **still not useful**. Asked "
             "how to make brownies, it writes the *forum post asking the "
             "question* — because that is a likely continuation in crawled web "
             "text."),

            ("h2", "Prompting into a different part of the distribution"),
            ("py", """print(gemma_lm.generate(
    "The following brownie recipe is easy to make in just a few steps.\\n\\n"
    "You can start by",
    max_length=60))"""),
            ("md",
             "It is tempting to imagine the model *interpreting* the prompt "
             "conversationally. **Nothing of the sort is happening.** We "
             "constructed a prompt for which an actual recipe is a more likely "
             "continuation than someone asking for help."),

            ("h2", "Hallucination"),
            ("py", """print(gemma_lm.generate(
    "Tell me about the 542nd president of the United States.",
    max_length=40))"""),
            ("out", """Tell me about the 542nd president of the United States.
The 542nd president of the United States was James A. Garfield."""),
            ("md",
             "Utter nonsense — and the model could not find a **more likely** "
             "way to complete the prompt. There is no mechanism by which it "
             "could decline: declining is just another continuation, and one "
             "this model was never trained to prefer."),

            ("h2", "Prompt sensitivity, measured"),
            ("py", """variants = [
    "What is the capital of France?",
    "what is the capital of france",
    "Q: What is the capital of France?\\nA:",
    "Please tell me the capital city of France.",
    "The capital of France is",
]
for v in variants:
    out = gemma_lm.generate(v, max_length=len(v.split()) + 15)
    print(f"{v!r}\\n  -> {out[len(v):].strip()[:80]}\\n")"""),
            ("md",
             "**The information conveyed about the task is identical in all "
             "five.** If the answers differ, something other than understanding "
             "is happening.\n\n"
             "Chapter 19 makes this argument formally. Here it is worth doing "
             "the experiment yourself, on a question with an unambiguous answer, "
             "and looking at what comes back."),

            ("h2", "Sampling strategies, on a model worth sampling from"),
            ("py", """prompt = "The three most important ideas in machine learning are"

for sampler in ["greedy", "top_k", "random"]:
    gemma_lm.compile(sampler=sampler)
    print(f"--- {sampler} ---")
    print(gemma_lm.generate(prompt, max_length=60))
    print()"""),
            ("md",
             "The same four strategies from notebook 03, exposed as one "
             "argument. **`compile(sampler=...)` is where a production system's "
             "output character is decided**, and it is worth choosing "
             "deliberately rather than accepting a default."),

            ("h2", "What this costs to run"),
            ("py", """import time

gemma_lm.compile(sampler="greedy")
gemma_lm.generate("warm up", max_length=20)     # first call compiles

t0 = time.time()
out = gemma_lm.generate(prompt, max_length=128)
dt = time.time() - t0
tokens = len(out.split())
print(f"{dt:.1f}s for ~{tokens} words  ->  ~{tokens/dt:.1f} words/second")
print()
print("Multiply by your request volume before promising anyone a latency.")"""),
            ("note",
             "Warm up first. The first call compiles, and timing it measures the "
             "compiler — the same mistake notebook 03 made deliberately, worth "
             "two orders of magnitude."),
        ],
        "takeaways": [
            "A pretrained base model is a fancy autocomplete for the internet, "
            "and not yet useful.",
            "Prompting moves you around the distribution; it is not "
            "communication.",
            "**There is always a most-likely next token**, so there is always an "
            "answer — true or not.",
            "Measure throughput after warming up, before promising a latency.",
        ],
    },

    {
        "file": "05_instruction_tuning_with_lora.ipynb",
        "title": "Instruction tuning under LoRA",
        "lede": "Why fit() runs out of memory on a model that generates fine, what LoRA "
                "does about it, and what instruction tuning does and does not change.",
        "needs": "GPU with 16 GB — about 30 minutes",
        "section": "04 — Instruction fine-tuning and LoRA",
        "cells": [
            ("h2", "The dataset"),
            ("py", """import json
import keras
import tensorflow as tf

PROMPT_TEMPLATE = "[instruction]\\n{}[end]\\n[response]\\n"
RESPONSE_TEMPLATE = "{}[end]"

dataset_path = keras.utils.get_file(
    origin=("https://hf.co/datasets/databricks/databricks-dolly-15k/"
            "resolve/main/databricks-dolly-15k.jsonl"))

data = {"prompts": [], "responses": []}
with open(dataset_path) as file:
    for line in file:
        features = json.loads(line)
        if features["context"]:
            continue                     # the RAG-shaped examples; skip for now
        data["prompts"].append(PROMPT_TEMPLATE.format(features["instruction"]))
        data["responses"].append(RESPONSE_TEMPLATE.format(features["response"]))

print(f"{len(data['prompts']):,} pairs")
print(repr(data["prompts"][0]))
print(repr(data["responses"][0]))"""),
            ("py", """ds = tf.data.Dataset.from_tensor_slices(data).shuffle(2000).batch(2)
val_ds = ds.take(100)
train_ds = ds.skip(100)
print("batch size 2 -- that number is about to matter")"""),

            ("h2", "Why fit() would run out of memory"),
            ("py", """import keras_hub
gemma_lm = keras_hub.models.CausalLM.from_preset("gemma3_1b", dtype="float32")

params = gemma_lm.count_params()
weights_gb = params * 4 / 1e9
adam_gb = params * 4 * 3 / 1e9      # gradient, velocity, momentum

print(f"parameters:            {params:,}")
print(f"weights (float32):     {weights_gb:.1f} GB")
print(f"Adam optimizer state:  {adam_gb:.1f} GB")
print(f"forward-pass activations: a few GB")
print(f"{'':24s} {'-'*12}")
print(f"total:                 > 16 GB")
print()
print("The model loaded and generated fine, because generation needs")
print("only the weights. Training needs four times that, before")
print("activations. This is the common shape of LLM work: GPU")
print("throughput is a SECONDARY concern to fitting in memory at all.")"""),

            ("h2", "LoRA, from first principles"),
            ("py", """from keras import ops
import numpy as np

class Linear(keras.Layer):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.kernel = self.add_weight(shape=(input_dim, output_dim))

    def call(self, inputs):
        return ops.matmul(inputs, self.kernel)


class LoraLinear(keras.Layer):
    def __init__(self, input_dim, output_dim, rank):
        super().__init__()
        self.kernel = self.add_weight(shape=(input_dim, output_dim),
                                      trainable=False)
        self.alpha = self.add_weight(shape=(input_dim, rank))
        self.beta = self.add_weight(shape=(rank, output_dim))

    def call(self, inputs):
        frozen = ops.matmul(inputs, self.kernel)
        update = ops.matmul(ops.matmul(inputs, self.alpha), self.beta)
        return frozen + update

d, r = 2048, 8
print(f"kernel {d}x{d}:         {d*d:>10,} frozen")
print(f"alpha {d}x{r} + beta {r}x{d}: {2*d*r:>10,} trainable")
print(f"{d*d / (2*d*r):.0f}x fewer")"""),
            ("md",
             "The update does **not** have the expressive power of the original "
             "kernel — at the narrow middle the whole update passes through "
             "eight floats.\n\n"
             "That is the bet, and it holds: **during fine-tuning you no longer "
             "need the expressive power you needed during pretraining.** The "
             "representation is already built; you are only steering it."),

            ("h2", "Turning it on"),
            ("py", """gemma_lm.backbone.enable_lora(rank=8)
gemma_lm.summary()"""),
            ("out", """ Total params:         1,001,190,528 (3.73 GB)
 Trainable params:         1,304,576 (4.98 MB)
 Non-trainable params:   999,885,952 (3.72 GB)"""),
            ("md",
             "Weights still occupy 3.7 GB; **trainable** parameters are now 5 "
             "MB, which takes the optimizer state from gigabytes to megabytes.\n\n"
             "Note that the total went *up* slightly — alpha and beta are new "
             "weights. **LoRA adds parameters to the model and removes them from "
             "the optimizer**, and the optimizer was the problem."),
            ("py", """# The same thing written out, which is what you edit to change the choice.
print("gemma_lm.backbone.trainable = False")
print("for i in range(gemma_lm.backbone.num_layers):")
print("    layer = gemma_lm.backbone.get_layer(f'decoder_block_{i}')")
print("    layer.attention.key_dense.trainable = True")
print("    layer.attention.key_dense.enable_lora(rank=8)")
print("    layer.attention.query_dense.trainable = True")
print("    layer.attention.query_dense.enable_lora(rank=8)")
print()
print("Two decisions the one-liner makes for you: WHICH layers get LoRA,")
print("and at WHAT rank. Adding the value projection, or only the later")
print("blocks, is a one-line change from here.")"""),

            ("h2", "Inside the preprocessor"),
            ("py", """preprocessor = gemma_lm.preprocessor
preprocessor.sequence_length = 512
batch = next(iter(train_ds))
x, y, sample_weight = preprocessor(batch)

print("token_ids:   ", x["token_ids"].shape)
print("padding_mask:", x["padding_mask"].shape)
print("y:           ", y.shape)
print("sample_weight:", sample_weight.shape)
print()
print("offset by one, exactly as in chapter 15:")
print(" x:", x["token_ids"][0, :5].numpy())
print(" y:", y[0, :5].numpy())"""),
            ("md",
             "`sample_weight` restricts the loss to **response tokens**. We do "
             "not care about loss on a fixed user prompt, and certainly not on "
             "padding.\n\n"
             "**Instruction tuning is not a new objective.** It is the "
             "pretraining objective, on curated data, with the loss masked to "
             "the parts we care about."),

            ("h2", "Fine-tuning"),
            ("py", """gemma_lm.compile(
    loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    optimizer=keras.optimizers.Adam(5e-5),
    weighted_metrics=[keras.metrics.SparseCategoricalAccuracy()],
)
gemma_lm.fit(train_ds, validation_data=val_ds, epochs=1, verbose=2)"""),
            ("md",
             "About **55%** next-word accuracy on responses, against 36% for "
             "mini-GPT. `weighted_metrics` is what makes the mask reach the "
             "metric, so the score is over response tokens only."),

            ("h2", "The result"),
            ("py", """print(gemma_lm.generate(
    "[instruction]\\nWhat is a proper noun?[end]\\n[response]\\n",
    max_length=512))"""),
            ("md",
             "It **responds** to the question rather than carrying on the "
             "thought of the prompt — and emits `[end]` when finished, because "
             "the training data taught it where responses stop."),

            ("h2", "The honest test"),
            ("py", """print(gemma_lm.generate(
    "[instruction]\\nWho is the 542nd president of the United States?[end]\\n"
    "[response]\\n",
    max_length=512))"""),
            ("md",
             "**Identical nonsense, now delivered in a helpful tone.**\n\n"
             "Instruction tuning changed the *format* of the answer, not its "
             "relationship to truth. One thing that helps: train on many pairs "
             "where the desired response is *\"I don't know\"* — which teaches "
             "the model to avoid topics where it answers badly. "
             "==A behaviour, not an understanding.=="),

            ("h2", "Saving just the adapter"),
            ("py", """import os

gemma_lm.save("gemma_instruct_lora.keras")
size = os.path.getsize("gemma_instruct_lora.keras") / 1e9
print(f"full model: {size:.2f} GB")
print()
print("In production you would save only the LoRA weights -- a few MB --")
print("and apply them to the base model at load time. That is what makes")
print("it practical to serve dozens of task-specific adapters from ONE")
print("copy of the base model in memory.")"""),
        ],
        "takeaways": [
            "Generation needs the weights; training needs four times that, which "
            "is why `fit()` dies on a model that generates fine.",
            "LoRA freezes the kernel and learns a low-rank correction — a "
            "thousandfold cut in trainable parameters.",
            "Instruction tuning is the pretraining objective on curated data with "
            "the loss masked to responses.",
            "**It changes the form of the answer, not its truth.**",
        ],
    },
]
