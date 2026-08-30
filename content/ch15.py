# -*- coding: utf-8 -*-
"""Chapter 15 — Language models and the Transformer.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 15
(pp. 421-465), read from the book PDF.

The pivot chapter of the whole book. A language model is defined, built, and
made to generate; sequence-to-sequence learning is built on RNNs and then torn
down; attention is derived from first principles and assembled into the
Transformer; and finally a 124-million-parameter pretrained encoder is
fine-tuned in a single epoch.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url, notebook_url  # noqa: E402
from diagrams import attention_qkv, positional_encoding  # noqa: E402


MMD_LM_LOOP = """
flowchart LR
  P["Prompt<br/><code>KING RICHARD III:</code>"]
  M["<b>Language model</b><br/><small>p(token | past tokens)</small>"]
  D["Distribution<br/>over the vocabulary<br/><small>67 characters</small>"]
  S["Pick one<br/><small>argmax, or sample</small>"]
  O["Append to<br/>the sequence"]
  P --> M --> D --> S --> O
  O -- "feed back as input" --> M
"""

MMD_INTRACTABLE = """
flowchart TB
  A["<b>Option A</b><br/>classify over all<br/>output sequences<br/><small>20,000<sup>4</sup> = 160 quadrillion<br/>for four words alone</small>"]
  B["<b>Option B</b><br/>predict one token,<br/>then loop<br/><small>20,000 outputs,<br/>any length of text</small>"]
  A --> X["Intractable"]
  B --> Y["The language model"]
"""

MMD_SEQ2SEQ = """
flowchart TB
  subgraph T["Training phase"]
    direction LR
    TE["<b>Encoder</b><br/><small>how, is, the, weather, today</small>"]
    TD["<b>Decoder</b><br/><small>[start], qué, tiempo, hace, hoy</small>"]
    TO["<small>qué, tiempo, hace, hoy, [end]</small>"]
    TE --> TD --> TO
  end
  subgraph I["Inference phase"]
    direction LR
    IE["<b>Encoder</b><br/><small>how, is, the, weather, today</small>"]
    ID["<b>Decoder</b><br/><small>[start]</small>"]
    IO["<small>qué</small>"]
    IE --> ID --> IO
  end
  T --> I
"""

MMD_RNN_BOTTLENECK = """
flowchart LR
  S["Source sequence<br/><small>how is the weather today</small>"]
  E["<b>Encoder RNN</b><br/><small>Bidirectional GRU</small>"]
  V["One state vector<br/><small>1,024 numbers</small>"]
  D["<b>Decoder RNN</b><br/><small>initial_state = V</small>"]
  O["Target sequence<br/><small>qué tiempo hace hoy</small>"]
  S --> E --> V --> D --> O
"""

MMD_ATTENTION_IDEA = """
flowchart TB
  Q["<b>Query</b><br/>the target vector<br/>we are decoding now"]
  K["<b>Keys</b><br/>every vector in<br/>the source sequence"]
  V["<b>Values</b><br/>the same source vectors,<br/>separately projected"]
  SC["<b>Scores</b><br/><small>dot-product, then softmax</small>"]
  W["<b>Weighted sum</b><br/><small>one output vector</small>"]
  Q --> SC
  K --> SC
  SC --> W
  V --> W
"""

MMD_SEARCH = """
flowchart LR
  Q["<b>Query</b><br/><small>&quot;dogs on the beach&quot;</small>"]
  K1["<b>Key</b><br/><small>beach, tree, boat</small><br/>match 0.5"]
  K2["<b>Key</b><br/><small>beach, dog, tree</small><br/>match 1.0"]
  K3["<b>Key</b><br/><small>dog</small><br/>match 0.5"]
  V["<b>Values</b><br/>the images themselves,<br/>ranked by match"]
  Q --> K1 --> V
  Q --> K2 --> V
  Q --> K3 --> V
"""

MMD_ENCODER = """
flowchart TB
  I["Source embeddings"]
  A["<b>Multi-head self-attention</b><br/><small>query = key = value = x</small>"]
  R1["Add residual"]
  N1["LayerNormalization"]
  F1["Dense(intermediate_dim, relu)"]
  F2["Dense(hidden_dim)"]
  R2["Add residual"]
  N2["LayerNormalization"]
  O["Same shape as the input<br/><small>so blocks stack</small>"]
  I --> A --> R1 --> N1 --> F1 --> F2 --> R2 --> N2 --> O
"""

MMD_DECODER = """
flowchart TB
  I["Target embeddings"]
  A["<b>Masked self-attention</b><br/><small>use_causal_mask=True</small>"]
  N1["Add and norm"]
  X["<b>Cross-attention</b><br/><small>query = target,<br/>key = value = encoder output</small>"]
  N2["Add and norm"]
  F["<b>Feedforward</b><br/><small>two Dense layers</small>"]
  N3["Add and norm"]
  O["Next-token predictions"]
  I --> A --> N1 --> X --> N2 --> F --> N3 --> O
"""

MMD_ORDER_BLIND = """
flowchart TB
  A["Dense layers<br/><small>process each token<br/>independently</small>"]
  B["Attention<br/><small>looks at tokens<br/>as a set</small>"]
  C["<b>Nothing in the model<br/>knows about order</b>"]
  D["Shuffle every word in<br/>every English sentence"]
  E["Identical attention scores.<br/>Identical accuracy."]
  A --> C
  B --> C
  C --> D --> E
"""

MMD_POSEMB = """
flowchart TB
  T["Token IDs<br/><code>[12, 907, 3, 44]</code>"]
  TE["<b>Token embedding</b><br/><small>what the word means</small>"]
  P["Positions<br/><code>[0, 1, 2, 3]</code>"]
  PE["<b>Position embedding</b><br/><small>where the word sits</small>"]
  S["<b>Add them</b><br/><small>position-aware embedding</small>"]
  T --> TE --> S
  P --> PE --> S
"""

MMD_LM_KINDS = """
flowchart TB
  C["<b>Causal LM</b><br/>p(token | past tokens)<br/><small>one direction only<br/>generates text</small>"]
  M["<b>Masked LM</b><br/>p(token | surrounding tokens)<br/><small>bidirectional<br/>represents text</small>"]
  CG["GPT, Llama<br/><small>chapter 16</small>"]
  MG["BERT, RoBERTa<br/><small>this chapter</small>"]
  C --> CG
  M --> MG
"""

MMD_BACKBONE = """
flowchart LR
  TK["<b>Tokenizer</b><br/><small>roberta_base_en</small>"]
  BB["<b>Backbone</b><br/><small>12 encoder blocks,<br/>124 M parameters</small>"]
  H1["Classification head"]
  H2["Span-extraction head"]
  H3["Token-tagging head"]
  TK --> BB
  BB --> H1
  BB --> H2
  BB --> H3
"""

MMD_WHY_EFFECTIVE = """
flowchart TB
  E0["Embedding space 0<br/><small>tokens in isolation</small>"]
  A1["<b>Attention</b><br/><small>recombine, weighted by<br/>how close vectors already are</small>"]
  E1["Embedding space 1<br/><small>tokens in context</small>"]
  A2["<b>Attention</b>"]
  E2["Embedding space 2<br/><small>richer context</small>"]
  EN["... 12, 32, 80 spaces deep"]
  E0 --> A1 --> E1 --> A2 --> E2 --> EN
"""

MMD_MULTIHEAD = """
flowchart TB
  X["One target token"]
  H1["<b>Head 1</b><br/><small>learns to match<br/>the subject</small>"]
  H2["<b>Head 2</b><br/><small>learns to attend<br/>to punctuation</small>"]
  H3["<b>Head 3</b><br/><small>...</small>"]
  H8["<b>Head 8</b><br/><small>...</small>"]
  C["<b>Concatenate</b><br/><small>separate partitions of<br/>the output vector</small>"]
  O["Dense projection<br/><small>head_dim x num_heads</small>"]
  X --> H1 --> C
  X --> H2 --> C
  X --> H3 --> C
  X --> H8 --> C
  C --> O
"""

MMD_CAUSAL = """
flowchart TB
  P["Predicting target<br/>position <b>i</b>"]
  A["May attend to<br/>positions 0 ... i"]
  B["May <b>not</b> attend to<br/>positions i+1 ..."]
  R["Information flows<br/>forward only<br/><small>as in an RNN</small>"]
  W["Without the mask:<br/>the model reads<br/>its own label"]
  P --> A --> R
  P --> B --> R
  B -. "omit the mask" .-> W
"""

MMD_FINETUNE = """
flowchart LR
  D["Unlabelled web text<br/><small>160 GB</small>"]
  PT["<b>Pretraining</b><br/><small>masked language modelling,<br/>1,024 GPUs, ~1 day</small>"]
  BB["<b>Backbone</b><br/><small>124 M parameters</small>"]
  IM["Labelled IMDb reviews<br/><small>20,000 samples</small>"]
  FT["<b>Fine-tuning</b><br/><small>1 epoch, lr = 5e-5</small>"]
  R["93.7% test accuracy"]
  D --> PT --> BB
  BB --> FT
  IM --> FT --> R
"""

NB = ["01_shakespeare_language_model.ipynb", "02_seq2seq_rnn_translation.ipynb",
      "03_attention_from_scratch.ipynb", "04_transformer_translation.ipynb",
      "05_finetuning_roberta.ipynb"]

DECK = {
    "id": "ch15",
    "kind": "chapter",
    "number": 15,
    "title": "Language Models and the Transformer",
    "subtitle": "From predicting one character of Shakespeare to fine-tuning a "
                "124-million-parameter pretrained encoder — and the one mechanism "
                "that made the difference.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 15",
    "source_url": chapter_url(15),
    "duration": "4 hours (3 sessions)",
    "presenter": [
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    ],
    "resources": chapter_resources(15, local_notebooks=NB),
    "objectives": [
        "Define a **language model** as p(token | past tokens), and explain why "
        "predicting one token at a time makes text generation tractable at all.",
        "Build and **sample from** an autoregressive character-level model, "
        "including the inference loop that has no counterpart in training.",
        "Build **sequence-to-sequence** translation with RNNs, and state the two "
        "limits that killed the approach.",
        "Derive **attention** from the problem it solves — score, softmax, "
        "weighted sum — and read query/key/value fluently.",
        "Assemble the **Transformer encoder and decoder** blocks, and explain "
        "every part: residuals, layer normalization, causal masking, feedforward.",
        "Explain why the Transformer **needs positional embeddings**, and what "
        "happens numerically when you leave them out.",
        "**Fine-tune a pretrained RoBERTa** on a classification task with KerasHub.",
        "Explain what attention is doing **geometrically**, and why interpolation "
        "produces both generalization and hallucination.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "The language model",
         "lead": "One idea, small enough to fit on a line: p(token | past tokens)."},

        {
            "type": "slide",
            "kicker": "Section 15.1",
            "title": "Classification was the easy case",
            "blocks": [
                {"t": "lead", "md": "The previous chapter classified movie reviews. Text went "
                                    "**in**; a single floating-point number came **out**."},
                {"t": "p", "md": "That output shape is unusually forgiving. Binary "
                                 "classification needs one number. *N*-way classification "
                                 "needs *N*. Both are small, fixed, and known in advance."},
                {"t": "p", "md": "Question answering and translation are not like that. They "
                                 "need a model that ==generates text as output==. Just as we "
                                 "needed tokenizers and embeddings to handle text on the way "
                                 "**in**, we need new machinery to produce it on the way **out**."},
                {"t": "band", "md": "We do not start from scratch. An integer sequence is "
                                    "still the natural numeric representation for text — we "
                                    "**detokenize** by running the mapping in reverse."},
            ],
            "notes": "Set up the asymmetry deliberately. Students who did chapter 14 will "
                     "assume text generation is a small extension of text classification. "
                     "It is not — the output space is the whole problem.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.1",
            "title": "The obvious approach does not survive arithmetic",
            "blocks": [
                {"t": "p", "md": "The simplest option is to train a direct classifier over the "
                                 "space of **all possible output sequences**. Let us count how "
                                 "many classes that would be."},
                {"t": "stats", "cols": 3, "items": [
                    {"v": "20,000", "l": "vocabulary size"},
                    {"v": "160 quadrillion", "l": "possible 4-word sequences"},
                    {"v": "> atoms in the universe", "l": "possible 20-word sequences"},
                ]},
                {"t": "p", "md": "Twenty thousand to the fourth power is 1.6 × 10¹⁷. No model "
                                 "design rescues this — the output layer alone would overwhelm "
                                 "any compute budget that will ever exist."},
                {"t": "mmd", "id": "ch15-intractable", "src": MMD_INTRACTABLE,
                 "cap": "Two ways to produce a sequence, and only one of them is finite."},
            ],
            "notes": "Have them do the multiplication out loud. The point is not the number, "
                     "it is that the number ends the discussion — this is a case where "
                     "back-of-the-envelope arithmetic eliminates an entire design.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.1 · definition",
            "title": "A language model predicts one token at a time",
            "blocks": [
                {"t": "lead", "md": "A **language model** learns a straightforward but deep "
                                    "probability distribution: ==p(token | past tokens)=="},
                {"t": "p", "md": "Given every token observed up to a point, it outputs a "
                                 "probability distribution over all tokens that could come "
                                 "next. With a 20,000-word vocabulary, the model needs to "
                                 "produce **20,000 numbers** — not 160 quadrillion."},
                {"t": "p", "md": "And yet, by predicting the next token repeatedly, feeding "
                                 "each prediction back in as input, we have built a model that "
                                 "can generate text of ==any length at all==."},
                {"t": "mmd", "id": "ch15-lm-loop", "src": MMD_LM_LOOP,
                 "cap": "The autoregressive loop: the output at one step is the input at the next."},
            ],
            "notes": "This slide is the whole chapter in miniature, and arguably the whole "
                     "second half of the book. Everything from here — the Transformer, "
                     "chapter 16's LLMs, chapter 17's diffusion analogues — is engineering "
                     "on top of this one definition.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1 · listing 15.1",
            "title": "A concrete case: Shakespeare, one character at a time",
            "blocks": [
                {"t": "p", "md": "To make the idea concrete we train the smallest useful "
                                 "language model: one that predicts the **next character**. "
                                 "The training corpus is a collection of Shakespeare's plays "
                                 "and sonnets."},
                {"t": "code", "lang": "python", "file": "listing 15.1", "src": """import keras

filename = keras.utils.get_file(
    origin=(
        "https://storage.googleapis.com/download.tensorflow.org/"
        "data/shakespeare.txt"
    ),
)
shakespeare = open(filename, "r").read()"""},
                {"t": "p", "md": "A character-level model keeps the whole example small enough "
                                 "to train in about two minutes, while demonstrating every "
                                 "mechanism a billion-parameter model uses."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1",
            "title": "What the corpus looks like",
            "blocks": [
                {"t": "p", "md": "Before designing anything, look at the data — the habit from "
                                 "chapter 6 applies here exactly as it did to images."},
                {"t": "out", "src": """>>> shakespeare[:250]
First Citizen:
Before we proceed any further, hear me speak.

All:
Speak, speak.

First Citizen:
You are all resolved rather to die than to famish?

All:
Resolved. resolved.

First Citizen:
First, you know Caius Marcius is chief enemy to the people."""},
                {"t": "p", "md": "Note what the model will have to learn: speaker names in "
                                 "capitals, a colon, a newline, then verse. **None of that is "
                                 "given to it.** It is all structure to be discovered from "
                                 "next-character prediction alone."},
            ],
            "notes": "Point at the structure explicitly. When the generated sample appears "
                     "later with correct speaker-name formatting, students should remember "
                     "that nobody encoded that rule.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1 · listing 15.2",
            "title": "Features and labels differ by exactly one character",
            "blocks": [
                {"t": "p", "md": "We chunk the text into equal-length pieces, as we did with "
                                 "weather measurements in chapter 13. Because the tokenizer is "
                                 "character-level, we can chunk the **raw string** directly."},
                {"t": "code", "lang": "python", "file": "listing 15.2", "src": """import tensorflow as tf

sequence_length = 100

def split_input(input, sequence_length):
    for i in range(0, len(input), sequence_length):
        yield input[i : i + sequence_length]

features = list(split_input(shakespeare[:-1], sequence_length))
labels = list(split_input(shakespeare[1:], sequence_length))
dataset = tf.data.Dataset.from_tensor_slices((features, labels))"""},
                {"t": "band", "md": "`shakespeare[:-1]` against `shakespeare[1:]` — the labels "
                                    "are the features **shifted one step into the future**. "
                                    "That single line is the entire supervision signal."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1",
            "title": "The offset, seen in one sample",
            "blocks": [
                {"t": "p", "md": "Print an (x, y) pair and the shift is visible directly."},
                {"t": "out", "src": """>>> x, y = next(dataset.as_numpy_iterator())
>>> x[:50], y[:50]
(b"First Citizen:\\nBefore we proceed any further, hear",
 b"irst Citizen:\\nBefore we proceed any further, hear ")"""},
                {"t": "p", "md": "At every position in the sequence, the label is the **next** "
                                 "character. One 100-character input yields ==100 supervised "
                                 "predictions==, not one — which is why this trains quickly "
                                 "despite the tiny corpus."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1 · listing 15.3",
            "title": "A character-level vocabulary needs 67 entries",
            "blocks": [
                {"t": "p", "md": "`TextVectorization` from chapter 14 does the job, with "
                                 "`split=\"character\"` instead of the default whitespace "
                                 "splitting, and no standardization — case and punctuation are "
                                 "passed through unaltered."},
                {"t": "code", "lang": "python", "file": "listing 15.3", "src": """from keras import layers

tokenizer = layers.TextVectorization(
    standardize=None,
    split="character",
    output_sequence_length=sequence_length,
)
tokenizer.adapt(dataset.map(lambda text, labels: text))"""},
                {"t": "out", "src": """>>> vocabulary_size = tokenizer.vocabulary_size()
>>> vocabulary_size
67"""},
                {"t": "p", "md": "Sixty-seven symbols cover the complete works. Compare the "
                                 "20,000-word vocabulary of chapter 14 — this is the "
                                 "**vocabulary/sequence-length trade-off** in its extreme form."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1 · listing 15.4",
            "title": "The model: embed, recur, project",
            "blocks": [
                {"t": "p", "md": "An RNN is the natural fit here: its recurrent state carries "
                                 "information about past characters forward to the prediction "
                                 "of the current one. A single GRU keeps the model small."},
                {"t": "code", "lang": "python", "file": "listing 15.4", "src": """embedding_dim = 256
hidden_dim = 1024

inputs = layers.Input(shape=(sequence_length,), dtype="int", name="token_ids")
x = layers.Embedding(vocabulary_size, embedding_dim)(inputs)
x = layers.GRU(hidden_dim, return_sequences=True)(x)
x = layers.Dropout(0.1)(x)
outputs = layers.Dense(vocabulary_size, activation="softmax")(x)
model = keras.Model(inputs, outputs)"""},
                {"t": "p", "md": "`return_sequences=True` is essential: we want a prediction at "
                                 "**every position**, not just at the end. The final `Dense` "
                                 "outputs a distribution over all 67 possible next characters."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1",
            "title": "Four million parameters, and where they sit",
            "blocks": [
                {"t": "out", "src": """>>> model.summary()
Model: "functional"
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Layer (type)              ┃ Output Shape        ┃     Param # ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ token_ids (InputLayer)    │ (None, 100)         │           0 │
│ embedding (Embedding)     │ (None, 100, 256)    │      17,152 │
│ gru (GRU)                 │ (None, 100, 1024)   │   3,938,304 │
│ dropout (Dropout)         │ (None, 100, 1024)   │           0 │
│ dense (Dense)             │ (None, 100, 67)     │      68,675 │
└───────────────────────────┴─────────────────────┴─────────────┘
 Total params: 4,024,131 (15.35 MB)"""},
                {"t": "p", "md": "Almost **98% of the parameters are in the GRU**. In the "
                                 "Transformer models later in this chapter the balance shifts "
                                 "dramatically — worth remembering the shape of this table."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.1 · listing 15.5",
            "title": "It is still classification — 6,400 of them per batch",
            "blocks": [
                {"t": "p", "md": "Nothing about the compile step is new. The loss is ordinary "
                                 "categorical crossentropy; the optimizer is the Adam default "
                                 "from chapter 3."},
                {"t": "code", "lang": "python", "file": "listing 15.5", "src": """model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["sparse_categorical_accuracy"],
)
model.fit(training_data, epochs=20)"""},
                {"t": "p", "md": "The model still solves a classification problem — it just "
                                 "makes one classification per **token**. A batch of 64 samples "
                                 "with 100 characters each produces ==6,400 individual labels==."},
                {"t": "p", "md": "Keras averages loss and accuracy first across each sequence, "
                                 "then across the batch. After 20 epochs the model predicts "
                                 "the next character correctly about **70%** of the time."},
            ],
            "notes": "70% next-character accuracy sounds unimpressive until you note that "
                     "English text at character level has an entropy such that this is quite "
                     "good for a two-minute training run on a 1 MB corpus.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.2",
            "title": "Generation needs surgery on the trained model",
            "blocks": [
                {"t": "lead", "md": "A model called in a feedback loop, where its output at one "
                                    "step becomes its input at the next, is called "
                                    "**autoregressive**."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🏋", "h": "During training", "style": "",
                     "p": "Fixed sequence length of 100 tokens. The GRU's state is handled "
                          "**implicitly** inside the layer call."},
                    {"ico": "🔮", "h": "During generation", "style": "accent",
                     "p": "One token at a time, and the GRU state must be **explicitly** "
                          "returned so it can be passed back in on the next call."},
                ]},
                {"t": "p", "md": "The computational structure is identical, so we build a "
                                 "second model with modified inputs and outputs and "
                                 "==copy the weights across==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.2 · listing 15.6",
            "title": "The inference model, with state made explicit",
            "blocks": [
                {"t": "p", "md": "Two changes to the architecture: the input is a single token "
                                 "rather than a hundred, and the GRU's state is promoted from an "
                                 "internal detail to a **named input and a named output**."},
                {"t": "code", "lang": "python", "file": "listing 15.6", "src": """inputs = keras.Input(shape=(1,), dtype="int", name="token_ids")
input_state = keras.Input(shape=(hidden_dim,), name="state")

x = layers.Embedding(vocabulary_size, embedding_dim)(inputs)
x, output_state = layers.GRU(hidden_dim, return_state=True)(
    x, initial_state=input_state
)
outputs = layers.Dense(vocabulary_size, activation="softmax")(x)

generation_model = keras.Model(
    inputs=(inputs, input_state),
    outputs=(outputs, output_state),
)
generation_model.set_weights(model.get_weights())"""},
                {"t": "p", "md": "`shape=(1,)` — one character in. `return_state=True` plus an "
                                 "`initial_state` input — the recurrent state now travels "
                                 "**through the function signature** rather than inside the layer."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.2 · listing 15.7",
            "title": "Priming: replaying a prompt to reach the right state",
            "blocks": [
                {"t": "p", "md": "Before generating we must **prime** the GRU with the prompt "
                                 "— feed it in one character at a time so the state matches "
                                 "what the model would have seen had the prompt occurred "
                                 "during training."},
                {"t": "code", "lang": "python", "file": "listing 15.7", "src": """tokens = tokenizer.get_vocabulary()
char_to_id = dict(zip(tokens, range(vocabulary_size)))
id_to_char = dict(zip(range(vocabulary_size), tokens))

prompt = "\\nKING RICHARD III:\\n"
input_ids = [char_to_id[c] for c in prompt]

state = keras.ops.zeros(shape=(1, hidden_dim))
for token_id in input_ids:
    inputs = keras.ops.expand_dims([token_id], axis=0)
    predictions, state = generation_model.predict((inputs, state), verbose=0)"""},
                {"t": "p", "md": "When the last character of the prompt goes in, the returned "
                                 "state summarises the ==entire prompt==, and the returned "
                                 "prediction is already the distribution for the first "
                                 "generated character."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.2 · listing 15.8",
            "title": "The sampling loop",
            "blocks": [
                {"t": "p", "md": "With a primed state and a first prediction in hand, generation "
                                 "is a loop over three operations — and the whole loop lives "
                                 "outside the model."},
                {"t": "code", "lang": "python", "file": "listing 15.8", "src": """import numpy as np

generated_ids = []
max_length = 250
for i in range(max_length):
    next_char = int(np.argmax(predictions, axis=-1)[0])
    generated_ids.append(next_char)
    inputs = keras.ops.expand_dims([next_char], axis=0)
    predictions, state = generation_model.predict((inputs, state), verbose=0)

output = "".join([id_to_char[token_id] for token_id in generated_ids])
print(prompt + output)"""},
                {"t": "p", "md": "Three lines of substance: take the most likely character, "
                                 "append it, feed it back. The state persists across "
                                 "iterations and carries everything the model knows about "
                                 "what it has already written."},
            ],
            "notes": "argmax here is the crudest possible sampling strategy. Chapter 16 "
                     "replaces it with temperature sampling, top-k, and nucleus sampling — "
                     "flag that this is a placeholder.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.2",
            "title": "What two minutes of training produces",
            "blocks": [
                {"t": "out", "src": """KING RICHARD III:
Stay, men! hear me speak.

FRIAR LAURENCE:
Thou wouldst have done thee here that he hath made for them?

BUCKINGHAM:
What straight shall stop his dismal threatening son,
Thou bear them both. Here comes the king;
Though I be good to put a wife to him,"""},
                {"t": "p", "md": "Not the next great tragedy. But look at what a "
                                 "**next-character** objective produced: correctly spelled "
                                 "words, speaker names in capitals followed by a colon and a "
                                 "newline, blank lines between speeches, and roughly "
                                 "verse-length lines."},
                {"t": "band", "md": "We trained on the narrow problem of guessing one "
                                    "character. We are using it for the far broader problem of "
                                    "==open-ended text generation==. That gap is the point.",
                 "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.2 · a diagnostic worth running",
            "title": "Replace GRU with Bidirectional(GRU) and watch it break",
            "blocks": [
                {"t": "p", "md": "This whole setup works **only because** a recurrent network "
                                 "passes information forward. Try the substitution and observe "
                                 "the failure mode."},
                {"t": "table",
                 "head": ["What you change", "Training accuracy", "Generation"],
                 "widths": [42, 28, 30],
                 "rows": [
                     ["`GRU(hidden_dim, return_sequences=True)`", "≈ 70% after 20 epochs",
                      "Shakespeare-like text"],
                     ["`Bidirectional(GRU(...))`", "**above 99% immediately**",
                      "**stops working entirely**"],
                 ]},
                {"t": "p", "md": "With a bidirectional layer, information from the *next* token "
                                 "reaches the prediction of the current one. The model reads "
                                 "the label off its own input — the problem becomes trivial, "
                                 "and nothing generalisable is learned."},
                {"t": "band", "md": "A training metric that suddenly looks *too good* is the "
                                    "most reliable signal of leakage there is. Chapter 5's "
                                    "lesson, in a new costume.", "style": "rose"},
            ],
            "notes": "Make them actually run this in the notebook. Seeing 99% accuracy paired "
                     "with garbage output is worth more than any amount of explanation about "
                     "causal masking later in the chapter.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.1.2 · what is new here",
            "title": "There is now logic that exists only at inference time",
            "blocks": [
                {"t": "lead", "md": "Every model so far in this book answered `model.predict()`. "
                                    "This one does not."},
                {"t": "bullets", "items": [
                    "There is an entire **loop**, and a non-trivial amount of logic, that "
                    "exists **only at inference time**.",
                    "State looping inside the GRU cell happens during both training and "
                    "inference — that part is symmetric.",
                    "But at **no point during training** do we feed the model's own predicted "
                    "labels back to it as input. That happens only when generating.",
                ]},
                {"t": "p", "md": "This asymmetry — training on ground-truth prefixes, "
                                 "generating from self-produced prefixes — has a name in the "
                                 "literature (*exposure bias*) and is one reason generated "
                                 "text degrades over long outputs."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "Sequence-to-sequence learning",
         "lead": "Two sequences, one model: translation, and the encoder/decoder template."},

        {
            "type": "slide",
            "kicker": "Section 15.2",
            "title": "The encoder/decoder template",
            "blocks": [
                {"t": "p", "md": "**Sequence-to-sequence** (seq2seq) modelling takes a source "
                                 "text as fixed input and generates a target sequence. "
                                 "Translation is the classic case; question answering is another."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📥", "h": "Encoder", "style": "accent",
                     "p": "Turns the **whole** source sequence into an intermediate "
                          "representation. It may look forward and backward freely."},
                    {"ico": "📤", "h": "Decoder", "style": "accent",
                     "p": "The language-model setup from section 15.1, with one addition: it "
                          "also sees the encoder's representation of the source."},
                ]},
                {"t": "mmd", "id": "ch15-seq2seq", "src": MMD_SEQ2SEQ,
                 "cap": "Figure 15.1 — during training the decoder sees the true target prefix; "
                        "during inference it sees only what it has generated so far."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.1",
            "title": "English to Spanish: 118,000 sentence pairs",
            "blocks": [
                {"t": "p", "md": "The dataset is a plain text file, one example per line: an "
                                 "English sentence, a tab, then the Spanish. Downloading and "
                                 "parsing it takes a dozen lines."},
                {"t": "code", "lang": "python", "src": """import pathlib

zip_path = keras.utils.get_file(
    origin=(
        "http://storage.googleapis.com/download.tensorflow.org/data/spa-eng.zip"
    ),
    fname="spa-eng",
    extract=True,
)
text_path = pathlib.Path(zip_path) / "spa-eng" / "spa.txt"

with open(text_path) as f:
    lines = f.read().split("\\n")[:-1]

text_pairs = []
for line in lines:
    english, spanish = line.split("\\t")
    spanish = "[start] " + spanish + " [end]"
    text_pairs.append((english, spanish))"""},
                {"t": "p", "md": "The one non-obvious line is the wrapping of every Spanish "
                                 "sentence in `[start]` and `[end]`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.1",
            "title": "The seed and the stop signal live in the data",
            "blocks": [
                {"t": "p", "md": "Look at what one parsed pair contains."},
                {"t": "out", "src": """>>> import random
>>> random.choice(text_pairs)
("Who is in this room?", "[start] ¿Quién está en esta habitación? [end]")"""},
                {"t": "p", "md": "`[start]` is what we feed the decoder to begin generating; "
                                 "`[end]` is what tells the generation loop to stop. They are "
                                 "==inserted in the data, not built into the model== — which is "
                                 "why the tokenizer must be told not to strip square brackets."},
                {"t": "p", "md": "Splitting is the usual three-way shuffle: 70% train, 15% "
                                 "validation, 15% test, taken over the pairs rather than over "
                                 "the sentences, so no English sentence appears in two splits."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.1 · listing 15.9",
            "title": "Two tokenizers, because punctuation is language-specific",
            "blocks": [
                {"t": "p", "md": "Two customisations are needed, and both are the kind of "
                                 "detail that silently ruins a translation model."},
                {"t": "bullets", "items": [
                    "The characters `[` and `]` are stripped by default. We must **keep** "
                    "them, so the token `\"[start]\"` stays distinct from the word `\"start\"`.",
                    "Spanish uses `¿`, which is not in `string.punctuation`. The Spanish "
                    "tokenizer needs it added to the strip set explicitly.",
                ]},
                {"t": "code", "lang": "python", "file": "listing 15.9", "src": """import string, re

strip_chars = string.punctuation + "¿"
strip_chars = strip_chars.replace("[", "").replace("]", "")

def custom_standardization(input_string):
    lowercase = tf.strings.lower(input_string)
    return tf.strings.regex_replace(lowercase, f"[{re.escape(strip_chars)}]", "")"""},
                {"t": "band", "md": "For a non-toy translator you would treat punctuation as "
                                    "**separate tokens** rather than stripping it — otherwise "
                                    "the model can never produce correctly punctuated output."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.1 · listing 15.9",
            "title": "The two vectorizers, and why their lengths differ",
            "blocks": [
                {"t": "p", "md": "With the standardization function in place, the two "
                                 "`TextVectorization` layers are near-identical — except for "
                                 "one number that is easy to miss."},
                {"t": "code", "lang": "python", "file": "listing 15.9 (cont.)", "src": """vocab_size = 15000
sequence_length = 20

english_tokenizer = layers.TextVectorization(
    max_tokens=vocab_size,
    output_mode="int",
    output_sequence_length=sequence_length,
)
spanish_tokenizer = layers.TextVectorization(
    max_tokens=vocab_size,
    output_mode="int",
    output_sequence_length=sequence_length + 1,
    standardize=custom_standardization,
)

english_tokenizer.adapt([pair[0] for pair in train_pairs])
spanish_tokenizer.adapt([pair[1] for pair in train_pairs])"""},
                {"t": "p", "md": "The Spanish sequence is ==one token longer==: 20 tokens of "
                                 "input and 20 of label, cut from 21. And `adapt()` runs on "
                                 "`train_pairs` only — never on validation or test text."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.1 · listing 15.10",
            "title": "Shifting the target, and masking the padding",
            "blocks": [
                {"t": "p", "md": "The pipeline must return `(inputs, target, sample_weights)`, "
                                 "where `inputs` is a dictionary with two keys — the tokenized "
                                 "English and the tokenized Spanish."},
                {"t": "code", "lang": "python", "file": "listing 15.10", "src": """def format_dataset(eng, spa):
    eng = english_tokenizer(eng)
    spa = spanish_tokenizer(spa)
    features = {"english": eng, "spanish": spa[:, :-1]}
    labels = spa[:, 1:]
    sample_weights = labels != 0
    return features, labels, sample_weights"""},
                {"t": "p", "md": "`spa[:, :-1]` is the decoder's input; `spa[:, 1:]` is its "
                                 "label. The same tensor, offset by one — exactly the "
                                 "Shakespeare setup, with the encoder input added alongside."},
                {"t": "band", "md": "`sample_weights = labels != 0` tells Keras to **ignore "
                                    "padded positions** when computing loss and metrics. "
                                    "Without it, a model that learns only to predict padding "
                                    "would score well."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.1",
            "title": "What comes out of the pipeline",
            "blocks": [
                {"t": "out", "src": """>>> inputs, targets, sample_weights = next(iter(train_ds))
>>> print(inputs["english"].shape)
(64, 20)
>>> print(inputs["spanish"].shape)
(64, 20)
>>> print(targets.shape)
(64, 20)
>>> print(sample_weights.shape)
(64, 20)"""},
                {"t": "p", "md": "Four aligned tensors of the same shape. Two go in as a "
                                 "dictionary of named inputs, one is the label, one is the "
                                 "per-position weight. Every seq2seq pipeline in this chapter "
                                 "has this shape."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.2",
            "title": "Why the naive single-RNN approach cannot work",
            "blocks": [
                {"t": "p", "md": "The easiest thing to try is one RNN reading source tokens and "
                                 "emitting target tokens at each step:"},
                {"t": "code", "lang": "python", "src": """inputs = keras.Input(shape=(sequence_length,), dtype="int32")
x = layers.Embedding(input_dim=vocab_size, output_dim=128)(inputs)
x = layers.LSTM(32, return_sequences=True)(x)
outputs = layers.Dense(vocab_size, activation="softmax")(x)
model = keras.Model(inputs, outputs)"""},
                {"t": "p", "md": "Because of the step-by-step nature of RNNs, this model sees "
                                 "only source tokens 0…N when predicting target token N."},
                {"t": "quote", "md": "*\"I will bring the bag to you\"* becomes *\"Te traeré la "
                                     "bolsa.\"* The **first** Spanish word corresponds to the "
                                     "**last** English word. There is no way to emit it without "
                                     "having read to the end of the source.",
                 "cite": "Section 15.2.2"},
            ],
            "notes": "Any bilingual student will have an example of their own here — Indonesian "
                     "to English word-order shifts work just as well. Ask for one.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.2 · figure 15.2",
            "title": "So read the whole source first",
            "blocks": [
                {"t": "p", "md": "A human translator reads the entire source sentence before "
                                 "beginning. The proper seq2seq setup does the same: an encoder "
                                 "RNN compresses the whole source into a **single vector**, "
                                 "which becomes the decoder's initial state."},
                {"t": "mmd", "id": "ch15-rnn-bottleneck", "src": MMD_RNN_BOTTLENECK,
                 "cap": "Figure 15.2 — everything the decoder knows about English arrives "
                        "through one 1,024-dimensional vector."},
                {"t": "p", "md": "Instead of the zero initial state used in the Shakespeare "
                                 "generator, the decoder starts from a state that ==encodes the "
                                 "source sentence==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.2 · listings 15.11-15.12",
            "title": "Encoder bidirectional, decoder emphatically not",
            "blocks": [
                {"t": "p", "md": "Both halves are a few lines of Keras, but one design decision "
                                 "differs between them and it is the decisive one."},
                {"t": "code", "lang": "python", "file": "listing 15.11 - encoder", "src": """embed_dim = 256
hidden_dim = 1024

source = keras.Input(shape=(None,), dtype="int32", name="english")
x = layers.Embedding(vocab_size, embed_dim, mask_zero=True)(source)
rnn_layer = layers.GRU(hidden_dim)
rnn_layer = layers.Bidirectional(rnn_layer, merge_mode="sum")
encoder_output = rnn_layer(x)"""},
                {"t": "code", "lang": "python", "file": "listing 15.12 - decoder", "src": """target = keras.Input(shape=(None,), dtype="int32", name="spanish")
x = layers.Embedding(vocab_size, embed_dim, mask_zero=True)(target)
rnn_layer = layers.GRU(hidden_dim, return_sequences=True)
x = rnn_layer(x, initial_state=encoder_output)
x = layers.Dropout(0.5)(x)
target_predictions = layers.Dense(vocab_size, activation="softmax")(x)
seq2seq_rnn = keras.Model([source, target], target_predictions)"""},
                {"t": "band", "md": "**Bidirectional in the encoder is a good idea** — we never "
                                    "predict source tokens, so there is nothing to cheat at. "
                                    "**Bidirectional in the decoder would break training** for "
                                    "exactly the reason the Shakespeare experiment showed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.2",
            "title": "Thirty-five million parameters, and where they went",
            "blocks": [
                {"t": "out", "src": """>>> seq2seq_rnn.summary()
│ embedding_1 (Embedding)  │ (None, None, 256)  │   3,840,000 │
│ embedding_2 (Embedding)  │ (None, None, 256)  │   3,840,000 │
│ bidirectional            │ (None, 1024)       │   7,876,608 │
│ gru_2 (GRU)              │ (None, None, 1024) │   3,938,304 │
│ dropout_1 (Dropout)      │ (None, None, 1024) │           0 │
│ dense_1 (Dense)          │ (None, None, 15000)│  15,375,000 │
 Total params: 34,869,912 (133.02 MB)"""},
                {"t": "p", "md": "The output `Dense` alone is 15 million parameters — 1,024 "
                                 "hidden units times a 15,000-word vocabulary. **The vocabulary "
                                 "projection dominates**, which is a constant of language "
                                 "modelling at every scale."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.2",
            "title": "65% — and why that number should not be trusted",
            "blocks": [
                {"t": "p", "md": "Training is unremarkable — `weighted_metrics` rather than "
                                 "`metrics` so that the sample weights we built actually reach "
                                 "the accuracy calculation."},
                {"t": "code", "lang": "python", "src": """seq2seq_rnn.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    weighted_metrics=["accuracy"],
)
seq2seq_rnn.fit(train_ds, epochs=15, validation_data=val_ds)"""},
                {"t": "p", "md": "We reach **65% next-token accuracy**. But next-token accuracy "
                                 "is a poor metric for translation, and it is worth being "
                                 "precise about why."},
                {"t": "bullets", "items": [
                    "It assumes the correct target tokens 0…N are **already known** when "
                    "predicting token N+1. At inference, they are not — you generate them.",
                    "It punishes a perfectly good translation that happens to use a different "
                    "word order from the reference.",
                    "The standard alternative is **BLEU**, which compares against a set of "
                    "high-quality reference translations and tolerates misalignment.",
                ]},
            ],
            "notes": "This connects straight back to chapter 6's rule about choosing a metric "
                     "that measures success rather than what is convenient to compute.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.2 · listing 15.13",
            "title": "What the RNN translator actually produces",
            "blocks": [
                {"t": "out", "src": """-
I will tell you tomorrow.
[start] te lo voy mañana a decir [end]
-
I think they're happy.
[start] yo creo que son felices [end]"""},
                {"t": "p", "md": "Decent for a toy, and still making basic mistakes — the first "
                                 "example has the adverb wedged into the middle of the verb "
                                 "phrase."},
                {"t": "band", "md": "This inference loop is also **inefficient**: it reprocesses "
                                    "the entire source and the entire generated target every "
                                    "time it samples one new word. A real system caches the "
                                    "state that has not changed.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.2.2 · the limit",
            "title": "Two limits that no amount of tuning removes",
            "blocks": [
                {"t": "p", "md": "You can stack deeper recurrent layers, swap GRU for LSTM, "
                                 "widen the state. None of it addresses the following."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🍾", "h": "The bottleneck", "style": "bad",
                     "p": "The **entire** source representation must fit in the encoder's state "
                          "vector, which caps the size and complexity of sentence you can "
                          "translate at all."},
                    {"ico": "🕳", "h": "Forgetting", "style": "bad",
                     "p": "RNNs progressively forget the past. By the 100th token, little "
                          "information about the start of the sequence remains."},
                ]},
                {"t": "p", "md": "Recurrent networks dominated seq2seq in the mid-2010s — "
                                 "**Google Translate circa 2017 was a stack of seven large LSTM "
                                 "layers**, essentially the model we just built. These two "
                                 "limits are what drove the search for something else."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "The Transformer architecture",
         "lead": "Attention is derived from the problem it solves, then made into everything."},

        {
            "type": "slide",
            "kicker": "Section 15.3 · 2017",
            "title": "The finding is in the title",
            "blocks": [
                {"t": "quote", "md": "**Attention Is All You Need**",
                 "cite": "Vaswani et al., NeurIPS 2017 — arxiv.org/abs/1706.03762"},
                {"t": "p", "md": "The authors were working on translation systems like the one "
                                 "we just built. Attention itself was not new — it had been in "
                                 "NLP systems for a couple of years. The **surprise** was that "
                                 "it was useful enough to be the *only* mechanism passing "
                                 "information across a sequence."},
                {"t": "p", "md": "No recurrent layers at all. This finding unleashed a "
                                 "revolution in natural language processing, and then beyond it "
                                 "— vision, audio, protein structure, and the models in "
                                 "chapters 16 and 17."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3 · the intuition",
            "title": "A thought experiment about this book",
            "blocks": [
                {"t": "lead", "md": "Suppose you had to build a weather-prediction model using "
                                    "only this textbook."},
                {"t": "bullets", "items": [
                    "You might read the whole book cover to cover — over 100,000 words, far "
                    "longer than any sequence we have handled.",
                    "But when you actually wrote the code, you would pay **special attention** "
                    "to the timeseries chapter, and within it to a few specific listings.",
                    "You would not be worried about the details of image convolutions.",
                ]},
                {"t": "p", "md": "Humans are **selective and contextual** about where they pull "
                                 "information from. An RNN has no mechanism to refer back "
                                 "directly — all information must pass through the cell state, "
                                 "in a loop, through every intervening position."},
                {"t": "band", "md": "It is like finishing the book, closing it, and writing the "
                                    "weather model ==entirely from memory==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1",
            "title": "Score every source vector against the current target",
            "blocks": [
                {"t": "p", "md": "Return to the translation RNN. When predicting a single token "
                                 "we have one vector for the target position, and a **sequence** "
                                 "of vectors for the source words."},
                {"t": "p", "md": "The goal: give the model a way to score every source vector "
                                 "by its relevance to the word being predicted. Assume for a "
                                 "moment a function `score(target_vector, source_vector)`."},
                {"t": "mmd", "id": "ch15-attention-idea", "src": MMD_ATTENTION_IDEA,
                 "cap": "Figure 15.4 — attention assigns a relevance score to each source "
                        "vector, for each target vector."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1",
            "title": "The scoring function is a dot product, and the sum is a softmax",
            "blocks": [
                {"t": "p", "md": "Two design choices, both made for the simplest available "
                                 "reason. **Score** by dot product — vectors close in an "
                                 "embedding space score high. **Normalise** with a softmax, so "
                                 "the scores for a given target sum to 1 and the weighted sum "
                                 "has predictable magnitude."},
                {"t": "code", "lang": "python", "src": """def dot_product_attention(target, source):
    scores = np.einsum("btd,bsd->bts", target, source)
    scores = softmax(scores, axis=-1)
    return np.einsum("bts,bsd->btd", scores, source)

dot_product_attention(target, source)"""},
                {"t": "p", "md": "The `einsum` subscripts spell out the shapes: `b`atch, "
                                 "`t`arget length, `s`ource length, `d`imension. The first "
                                 "contraction produces a **(batch, target, source) score "
                                 "matrix**; the second uses it to take a weighted sum."},
            ],
            "notes": "If einsum is unfamiliar, write the two operations out as loops on the "
                     "board once. Every attention implementation in every framework is these "
                     "two contractions with a softmax between them.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1 · figure 15.5",
            "title": "The score matrix is two-dimensional",
            "blocks": [
                {"t": "p", "md": "When both target and source are sequences, the attention "
                                 "scores form a **matrix**: one row per target word, one column "
                                 "per source word."},
                {"t": "table",
                 "head": ["target ↓ / source →", "I", "will", "bring", "the", "bag", "to", "you"],
                 "widths": [22, 11, 11, 11, 11, 11, 11, 12],
                 "rows": [
                     ["Te", "·", "·", "·", "·", "·", "·", "**0.8**"],
                     ["traeré", "0.2", "**0.5**", "**0.3**", "·", "·", "·", "·"],
                     ["la", "·", "·", "·", "**0.6**", "0.3", "·", "·"],
                     ["bolsa", "·", "·", "·", "0.2", "**0.7**", "·", "·"],
                     ["[end]", "·", "·", "·", "·", "·", "0.3", "0.4"],
                 ]},
                {"t": "p", "md": "Read a row as: *when producing this Spanish word, how much did "
                                 "the model draw on each English word?* The `Te` row peaking at "
                                 "`you` is exactly the long-range dependency the RNN could not "
                                 "express."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1",
            "title": "Give the model parameters: query, key, value",
            "blocks": [
                {"t": "p", "md": "The hypothesis space gets much richer if we project both "
                                 "source and target with `Dense` layers first, letting the model "
                                 "find a shared space in which relevant vectors are close."},
                {"t": "code", "lang": "python", "src": """query_dense = layers.Dense(dim)
key_dense = layers.Dense(dim)
value_dense = layers.Dense(dim)
output_dense = layers.Dense(dim)

def parameterized_attention(query, key, value):
    query = query_dense(query)
    key = key_dense(key)
    value = value_dense(value)
    scores = np.einsum("btd,bsd->bts", query, key)
    scores = softmax(scores, axis=-1)
    outputs = np.einsum("bts,bsd->btd", scores, value)
    return output_dense(outputs)

parameterized_attention(query=target, key=source, value=source)"""},
                {"t": "p", "md": "`sum(score(target, source) * source)` has become "
                                 "`sum(score(query, key) * value)`. The three-argument form is "
                                 "more general: in rare cases you want different vectors for "
                                 "**scoring** and for **summing**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1 · figure 15.6",
            "title": "The names come from search engines",
            "blocks": [
                {"t": "p", "md": "Imagine a tool that looks up photos in a database."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔍", "h": "Query", "style": "accent",
                     "p": "Your search term. In attention: the target vector for the position "
                          "currently being decoded."},
                    {"ico": "🏷", "h": "Keys", "style": "accent",
                     "p": "The photo tags used to match against the query. In attention: the "
                          "projected source vectors that get scored."},
                    {"ico": "🖼", "h": "Values", "style": "accent",
                     "p": "The photos themselves — what you actually retrieve. In attention: "
                          "the projected source vectors that get summed."},
                ]},
                {"t": "mmd", "id": "ch15-search", "src": MMD_SEARCH,
                 "cap": "Figure 15.6 — the query is compared to keys, and the match scores rank "
                        "the values."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1 · refinement 1",
            "title": "Scale the scores before the softmax",
            "blocks": [
                {"t": "p", "md": "When input vectors get long, dot products get large. Large "
                                 "logits push the softmax toward a one-hot output, where its "
                                 "**gradients vanish** — training becomes unstable."},
                {"t": "p", "md": "The fix is one division:"},
                {"t": "code", "lang": "python", "src": """scores = softmax(scores / math.sqrt(head_dim), axis=-1)"""},
                {"t": "p", "md": "Scaling by the square root of the vector length works well for "
                                 "any vector size — the variance of a dot product of "
                                 "*d*-dimensional vectors grows with *d*, so dividing by √*d* "
                                 "holds it roughly constant. This is why the mechanism is called "
                                 "==scaled dot-product attention==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1 · refinement 2",
            "title": "One softmax sum is too blunt",
            "blocks": [
                {"t": "p", "md": "The weighted sum is powerful — a direct connection across "
                                 "distant parts of a sequence. It is also **blunt**: if the "
                                 "model attends to many tokens at once, the interesting "
                                 "features of individual source tokens get washed out in the "
                                 "combined representation."},
                {"t": "p", "md": "The trick that works: run the whole attention operation "
                                 "**several times in parallel**, with different parameters. "
                                 "Each run is an *attention head*."},
                {"t": "band", "md": "By projecting query and key differently, one head might "
                                    "learn to match the **subject** of the source sentence, "
                                    "while another attends to **punctuation**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1 · refinement 2",
            "title": "Several heads, then one projection",
            "blocks": [
                {"t": "p", "md": "The heads do not vote and they do not average. Each writes "
                                 "into **its own slice** of the output vector, the slices are "
                                 "concatenated, and one dense layer afterwards is what decides "
                                 "how to combine them — which is why the combination is learned "
                                 "rather than fixed."},
                {"t": "mmd", "id": "ch15-multihead", "src": MMD_MULTIHEAD,
                 # A fan of four heads between two single nodes is squarish
                 # whichever way round it is drawn — neither orientation wins,
                 # and the renderer says so. So give it the room instead.
                 "full": True,
                 "cap": "Figure 15.7 — each head attends to different parts of the source, in "
                        "separate partitions of the eventual output vector."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1",
            "title": "Self-attention, computed on one sentence",
            "blocks": [
                attention_qkv(
                    "ch15-qkv-run", ["the", "cat", "sat", "on", "it"], focus=4,
                    cap="One query — the word “it” — against every key in the sentence. "
                        "Press play to walk the five stages."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1",
            "title": "Reading the five stages",
            "blocks": [
                {"t": "steps", "items": [
                    "**Three matrices, one embedding.** `Wq`, `Wk` and `Wv` turn each "
                    "token's embedding into a query, a key and a value. They are "
                    "learned, and they are the *only* parameters in an attention head.",
                    "**The query is dotted against every key.** That gives one raw score "
                    "per token — how well “it” matches each word, including itself. "
                    "Dividing by `sqrt(d)` keeps the scores in a range softmax can use.",
                    "**Softmax turns scores into proportions.** They are positive and "
                    "they sum to 100%. Nothing is discarded: every token gets a share, "
                    "and a low share is still a share.",
                    "**The output is the value vectors, mixed in those proportions.** "
                    "==The new vector for “it” is literally built out of the other "
                    "words in the sentence.== That is the whole mechanism.",
                ]},
                {"t": "band", "md": "This is one **head**. Multi-head attention runs "
                                    "several of these in parallel with different `Wq`, "
                                    "`Wk`, `Wv`, so each can specialise — one on syntax, "
                                    "another on which noun a pronoun refers to — and "
                                    "concatenates the results."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1 · figure 15.7",
            "title": "Multi-head attention, written out",
            "blocks": [
                {"t": "p", "md": "Every projection becomes a **list** of projections, one per "
                                 "head, and the per-head outputs are concatenated at the end."},
                {"t": "code", "lang": "python", "src": """query_dense = [layers.Dense(head_dim) for i in range(num_heads)]
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
    return output_dense(outputs)"""},
                {"t": "p", "md": "Each head produces a `head_dim`-wide output; concatenating "
                                 "`num_heads` of them and projecting once gives the layer's "
                                 "output. In practice the loop is one batched matmul."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.1",
            "title": "In Keras, this is one layer",
            "blocks": [
                {"t": "p", "md": "Everything on the previous three slides is a reusable layer, "
                                 "and Keras ships it."},
                {"t": "code", "lang": "python", "src": """multi_head_attention = keras.layers.MultiHeadAttention(
    num_heads=num_heads,
    head_dim=head_dim,
)
multi_head_attention(query=target, key=source, value=source)"""},
                {"t": "p", "md": "We derived it by hand first for a reason: `MultiHeadAttention` "
                                 "is the single most consequential layer in modern deep "
                                 "learning, and reading its arguments — `query`, `key`, "
                                 "`value`, `attention_mask`, `use_causal_mask` — is a skill "
                                 "the rest of this course assumes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.2 · self-attention",
            "title": "Now point the mechanism at its own input",
            "blocks": [
                {"t": "p", "md": "So far attention has passed information **between** two "
                                 "sequences. But nothing stops us from letting a sequence "
                                 "attend to itself:"},
                {"t": "code", "lang": "python", "src": """multi_head_attention(query=source, key=source, value=source)"""},
                {"t": "p", "md": "This is **self-attention**. Each token attends to every token "
                                 "in its own sequence, including itself, producing a "
                                 "representation of the word ==in context==."},
                {"t": "quote", "md": "*\"The train left the station on time.\"* What kind of "
                                     "station? A radio station? The International Space "
                                     "Station? Self-attention lets the model give a high score "
                                     "to the pair (**station**, **train**), summing the "
                                     "representation of *train* into that of *station*.",
                 "cite": "Section 15.3.2"},
            ],
            "notes": "This is the slide where the architecture stops being a translation trick "
                     "and becomes a general representation-learning mechanism. Every encoder "
                     "model in chapters 15-17 is built on this line of code.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.2 · the missing ingredient",
            "title": "Attention alone collapses to a matrix multiplication",
            "blocks": [
                {"t": "p", "md": "Self-attention sounds like what an RNN does. Can we simply "
                                 "swap the recurrent layers for `MultiHeadAttention`? "
                                 "**Almost — but not quite.**"},
                {"t": "p", "md": "`MultiHeadAttention` combines *linear* projections of source "
                                 "elements. That is all it does. It is a very expressive "
                                 "**pooling** operation, and pooling is not enough."},
                {"t": "band", "md": "Consider a sequence of length one. The score matrix is a "
                                    "single 1, and the layer reduces to a linear projection. "
                                    "You could stack **100** such layers and still simplify the "
                                    "whole computation to ==one matrix multiplication==.",
                 "style": "rose"},
                {"t": "p", "md": "Every recurrent cell eventually passes each token's vector "
                                 "through a dense projection with an activation. The Transformer "
                                 "adds this back in the simplest possible way: a feedforward "
                                 "network of **two Dense layers with a nonlinearity between them**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.2",
            "title": "The division of labour inside a Transformer block",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔗", "h": "Attention", "style": "accent",
                     "p": "Passes information **across** the sequence. Mixes positions. "
                          "Contains no nonlinearity."},
                    {"ico": "🧮", "h": "Feedforward", "style": "accent",
                     "p": "Updates the representation of **each item independently**. Mixes "
                          "features, not positions. Contains the nonlinearity."},
                ]},
                {"t": "p", "md": "Two more ingredients come straight from the ConvNet chapters: "
                                 "**residual connections** and **normalization**, both of which "
                                 "chapter 9 established as essential to training anything deep."},
                {"t": "mmd", "id": "ch15-encoder", "src": MMD_ENCODER,
                 "cap": "The encoder block: attend, add, norm; feed forward, add, norm."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.2 · listing 15.14",
            "title": "The encoder block: what it holds",
            "blocks": [
                {"t": "p", "md": "Five sub-layers: one attention, two dense, two normalization."},
                {"t": "code", "lang": "python", "file": "listing 15.14 - constructor", "src": """class TransformerEncoder(keras.Layer):
    def __init__(self, hidden_dim, intermediate_dim, num_heads):
        super().__init__()
        key_dim = hidden_dim // num_heads
        self.self_attention = layers.MultiHeadAttention(num_heads, key_dim)
        self.self_attention_layernorm = layers.LayerNormalization()
        self.feed_forward_1 = layers.Dense(intermediate_dim, activation="relu")
        self.feed_forward_2 = layers.Dense(hidden_dim)
        self.feed_forward_layernorm = layers.LayerNormalization()"""},
                {"t": "p", "md": "`key_dim = hidden_dim // num_heads` keeps the total width "
                                 "constant as heads are added — eight heads of 32 dimensions "
                                 "rather than one head of 256. **Splitting, not growing.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.2 · listing 15.14",
            "title": "The encoder block: what it does",
            "blocks": [
                {"t": "p", "md": "Two stages, each of the form *transform, add the residual, "
                                 "normalise* — the shape of every Transformer block ever "
                                 "written."},
                {"t": "code", "lang": "python", "file": "listing 15.14 - call", "src": """    def call(self, source, source_mask):
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
        return x"""},
                {"t": "p", "md": "Input and output have the **same shape**, so blocks stack — "
                                 "each one building a progressively more expressive "
                                 "representation of the source sentence. RoBERTa, later in this "
                                 "chapter, stacks twelve."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.2 · a deliberate choice",
            "title": "LayerNormalization, not BatchNormalization",
            "blocks": [
                {"t": "p", "md": "The normalization here is **not** the `BatchNormalization` "
                                 "used in image models. Write both out and the reason is "
                                 "immediate."},
                {"t": "code", "lang": "python", "file": "layer normalization", "src": """# input shape: (batch_size, sequence_length, embedding_dim)
def layer_normalization(batch_of_sequences):
    mean = np.mean(batch_of_sequences, keepdims=True, axis=-1)
    variance = np.var(batch_of_sequences, keepdims=True, axis=-1)
    return (batch_of_sequences - mean) / variance"""},
                {"t": "code", "lang": "python", "file": "batch normalization", "src": """# input shape: (batch_size, height, width, channels)
def batch_normalization(batch_of_images):
    mean = np.mean(batch_of_images, keepdims=True, axis=(0, 1, 2))
    variance = np.var(batch_of_images, keepdims=True, axis=(0, 1, 2))
    return (batch_of_images - mean) / variance"""},
                {"t": "p", "md": "`BatchNormalization` pools over **axis 0**, creating "
                                 "interactions between samples in a batch. "
                                 "`LayerNormalization` pools only over the last axis, "
                                 "normalising each sequence ==independently== — which is what "
                                 "variable-length sequence data requires."},
            ],
            "notes": "Ask why interactions between samples are harmful here specifically. "
                     "Answer: sequences in a batch have wildly different lengths and padding "
                     "amounts, so batch statistics are contaminated by how you happened to "
                     "group examples.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.2 · masking",
            "title": "The padding mask, and its shape",
            "blocks": [
                {"t": "p", "md": "`attention_mask` is a Boolean tensor broadcast to the shape of "
                                 "the attention scores — **(batch_size, target_length, "
                                 "source_length)**. Where it is false, the score is zeroed and "
                                 "that source token contributes nothing."},
                {"t": "p", "md": "We use it to stop any token from attending to **padding**, "
                                 "which carries no information."},
                {"t": "code", "lang": "python", "src": """# source_mask marks the non-padding tokens: (batch_size, source_length)
source_mask = source != 0

# upranked inside the layer to broadcast across every target position
mask = source_mask[:, None, :]   # (batch_size, 1, source_length)"""},
                {"t": "p", "md": "The `None` in the middle is the whole trick: one mask, "
                                 "broadcast across every row of the score matrix, because "
                                 "*which source tokens are padding* does not depend on which "
                                 "target position is asking."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.3",
            "title": "The decoder attends twice",
            "blocks": [
                {"t": "p", "md": "The decoder block is almost identical to the encoder, with one "
                                 "addition: it must also see the **encoder's output**. So it "
                                 "uses attention twice."},
                {"t": "steps", "items": [
                    "**Self-attention** over the target sequence, so each target position can "
                    "use information from other target positions — masked so it can only look "
                    "backward.",
                    "**Cross-attention**, whose query is the target and whose key and value are "
                    "the encoder output — this is what brings information across from the "
                    "source language.",
                    "**Feedforward**, same as the encoder.",
                ]},
                {"t": "mmd", "id": "ch15-decoder", "src": MMD_DECODER,
                 "cap": "The decoder block: masked self-attention, then cross-attention, then "
                        "feedforward — each with add-and-norm."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.3 · listing 15.15",
            "title": "The decoder block: what it holds",
            "blocks": [
                {"t": "p", "md": "The constructor is the encoder's, plus a second "
                                 "`MultiHeadAttention` and its normalization layer."},
                {"t": "code", "lang": "python", "file": "listing 15.15 - constructor", "src": """class TransformerDecoder(keras.Layer):
    def __init__(self, hidden_dim, intermediate_dim, num_heads):
        super().__init__()
        key_dim = hidden_dim // num_heads
        self.self_attention = layers.MultiHeadAttention(num_heads, key_dim)
        self.self_attention_layernorm = layers.LayerNormalization()
        self.cross_attention = layers.MultiHeadAttention(num_heads, key_dim)
        self.cross_attention_layernorm = layers.LayerNormalization()
        self.feed_forward_1 = layers.Dense(intermediate_dim, activation="relu")
        self.feed_forward_2 = layers.Dense(hidden_dim)
        self.feed_forward_layernorm = layers.LayerNormalization()"""},
                {"t": "p", "md": "Nine attributes, three of them `LayerNormalization` — one "
                                 "per residual junction. Counting normalization layers is a "
                                 "quick way to check a Transformer implementation by eye."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.3 · listing 15.15",
            "title": "The decoder block: what it does",
            "blocks": [
                {"t": "p", "md": "Three stages, each of the form *transform, add the residual, "
                                 "normalise*. The two attention calls receive **different masks**."},
                {"t": "code", "lang": "python", "file": "listing 15.15 - call", "src": """    def call(self, target, source, source_mask):
        residual = x = target
        x = self.self_attention(query=x, key=x, value=x, use_causal_mask=True)
        x = self.self_attention_layernorm(x + residual)

        residual = x
        mask = source_mask[:, None, :]
        x = self.cross_attention(
            query=x, key=source, value=source, attention_mask=mask
        )
        x = self.cross_attention_layernorm(x + residual)

        residual = x
        x = self.feed_forward_1(x)
        x = self.feed_forward_2(x)
        x = self.feed_forward_layernorm(x + residual)
        return x"""},
                {"t": "p", "md": "`use_causal_mask=True` on self-attention stops the decoder "
                                 "seeing its own future. The padding `attention_mask` on "
                                 "cross-attention stops it attending to empty source positions. "
                                 "**Different problems, different masks.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.3 · the causal mask",
            "title": "Attention is bidirectional by default — which would be fatal",
            "blocks": [
                {"t": "p", "md": "In self-attention, **any** position can attend to **any** "
                                 "other. Without special care, the decoder would see the token "
                                 "it is trying to predict — the same cheat as the "
                                 "`Bidirectional(GRU)` experiment in section 15.1."},
                {"t": "p", "md": "The fix is a lower-triangular attention mask:"},
                {"t": "out", "src": """[
    [1, 0, 0, 0, 0],
    [1, 1, 0, 0, 0],
    [1, 1, 1, 0, 0],
    [1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1],
]"""},
                {"t": "p", "md": "Row *i* is the mask for target position *i*. Row 0: the first "
                                 "token may attend only to itself. Row 1: the second may attend "
                                 "to the first and itself. And so on — the same forward-only "
                                 "information flow an RNN gets for free from its structure."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.3 · the causal mask",
            "title": "One argument, and a bug you will not be warned about",
            "blocks": [
                {"t": "p", "md": "Read the mask row by row and the rule is plain: position *i* "
                                 "may look at everything up to and including itself, and nothing "
                                 "after."},
                {"t": "mmd", "id": "ch15-causal", "src": MMD_CAUSAL,
                 "cap": "The same forward-only information flow an RNN gets free from its "
                        "structure, imposed here by hand."},
                {"t": "band", "md": "In Keras this is one argument: `use_causal_mask=True`. "
                                    "==Forgetting it is one of the most common and most silent "
                                    "bugs in hand-written Transformer code==.",
                 "style": "rose"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.4 · listing 15.16",
            "title": "Assembling the translator: the encoder half",
            "blocks": [
                {"t": "p", "md": "Same structure as the RNN model, GRU layers replaced. The "
                                 "feedforward block scales **up** to 2048 before the "
                                 "nonlinearity and back down to 256 after — a large "
                                 "intermediate dimension that works well in practice."},
                {"t": "code", "lang": "python", "file": "listing 15.16 - encoder", "src": """hidden_dim = 256
intermediate_dim = 2048
num_heads = 8

source = keras.Input(shape=(None,), dtype="int32", name="english")
x = layers.Embedding(vocab_size, hidden_dim)(source)
encoder_output = TransformerEncoder(hidden_dim, intermediate_dim, num_heads)(
    source=x,
    source_mask=source != 0,
)"""},
                {"t": "p", "md": "`source != 0` computes the padding mask inline — no separate "
                                 "layer, just a Boolean tensor built from the input."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.4 · listing 15.16",
            "title": "Assembling the translator: the decoder half",
            "blocks": [
                {"t": "p", "md": "The decoder takes both the target embeddings and the encoder "
                                 "output, and the same source mask is handed to it again."},
                {"t": "code", "lang": "python", "file": "listing 15.16 - decoder", "src": """target = keras.Input(shape=(None,), dtype="int32", name="spanish")
x = layers.Embedding(vocab_size, hidden_dim)(target)
x = TransformerDecoder(hidden_dim, intermediate_dim, num_heads)(
    target=x,
    source=encoder_output,
    source_mask=source != 0,
)
x = layers.Dropout(0.5)(x)
target_predictions = layers.Dense(vocab_size, activation="softmax")(x)
transformer = keras.Model([source, target], target_predictions)"""},
                {"t": "p", "md": "One encoder block and one decoder block — the 2017 paper used "
                                 "**six of each**. Everything else, down to the final softmax "
                                 "over the Spanish vocabulary, is unchanged from the GRU model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.4",
            "title": "Fourteen million parameters — less than half the RNN",
            "blocks": [
                {"t": "out", "src": """>>> transformer.summary()
│ embedding_5 (Embedding)  │ (None, None, 256)   │   3,840,000 │
│ transformer_encoder_1    │ (None, None, 256)   │   1,315,072 │
│ embedding_6 (Embedding)  │ (None, None, 256)   │   3,840,000 │
│ transformer_decoder_1    │ (None, None, 256)   │   1,578,752 │
│ dropout_9 (Dropout)      │ (None, None, 256)   │           0 │
│ dense_11 (Dense)         │ (None, None, 15000) │   3,855,000 │
 Total params: 14,428,824 (55.04 MB)"""},
                {"t": "p", "md": "34.9 M for the RNN against **14.4 M** here. The encoder and "
                                 "decoder blocks together are under 3 M parameters — the "
                                 "embeddings and the vocabulary projection dominate, as always."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.4 · a deliberate failure",
            "title": "58%. Worse than the RNN. Can you spot why?",
            "blocks": [
                {"t": "p", "md": "The compile and fit calls are identical to the RNN model's, "
                                 "so the two numbers are directly comparable."},
                {"t": "code", "lang": "python", "src": """transformer.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    weighted_metrics=["accuracy"],
)
transformer.fit(train_ds, epochs=15, validation_data=val_ds)"""},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "65%", "l": "GRU seq2seq"},
                    {"v": "58%", "l": "Transformer, first attempt"},
                ]},
                {"t": "p", "md": "Seven percentage points **worse**. Either the architecture is "
                                 "not what it was hyped up to be, or something is missing from "
                                 "the implementation."},
                {"t": "band", "md": "Stop here. Give the room two minutes with the code on the "
                                    "previous slide before turning over.", "style": "amber"},
            ],
            "notes": "Do not rush this. The reveal only lands if people have genuinely tried "
                     "to find it. Hint if needed: 'this section is about sequence models — is "
                     "the model we just built a sequence model?'",
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.4 · the reveal",
            "title": "What we built is not a sequence model at all",
            "blocks": [
                {"t": "lead", "md": "It is composed of dense layers that process tokens "
                                    "independently, and an attention layer that looks at tokens "
                                    "**as a set**."},
                {"t": "p", "md": "Change the order of the tokens and you get identical pairwise "
                                 "attention scores and identical context-aware representations. "
                                 "Shuffle every word of every English source sentence and the "
                                 "model ==would not notice==. You would get the same accuracy."},
                {"t": "mmd", "id": "ch15-order-blind", "src": MMD_ORDER_BLIND,
                 "cap": "Attention is a set-processing mechanism: it sees relationships between "
                        "pairs, and is blind to where in the sequence they sit."},
                {"t": "p", "md": "For RNNs, order-awareness came free from the layer's "
                                 "computation. For the Transformer, we must **inject positional "
                                 "information into the embeddings themselves**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5",
            "title": "Positional embedding: add where to what",
            "blocks": [
                {"t": "p", "md": "The idea is simple. Each input embedding gets two components: "
                                 "the usual **word vector**, which represents the word "
                                 "independently of context, and a **position vector**, which "
                                 "represents where the word sits in this sentence."},
                {"t": "mmd", "id": "ch15-posemb", "src": MMD_POSEMB,
                 "cap": "Two embedding tables, added together. The model works out how to use "
                        "the extra information."},
                {"t": "p", "md": "The most obvious scheme — concatenate the raw integer position "
                                 "— is a poor one: positions can be large integers, and neural "
                                 "networks dislike large input values and discrete input "
                                 "distributions."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5 · positional encoding",
            "title": "The sinusoids, and the pattern they make",
            "blocks": [
                positional_encoding(
                    "ch15-posenc-waves",
                    cap="Left: three of the actual waves. Right: every dimension for "
                        "every position. Both computed from the formula, not drawn to "
                        "look right."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5 · two schemes",
            "title": "Sinusoidal, or learned",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "〰", "h": "Sinusoidal (the 2017 paper)", "style": "",
                     "p": "Add a vector of values in [-1, 1] that varies **cyclically** with "
                          "position, built from cosine functions. Clever: it characterises any "
                          "integer in a large range using only small values."},
                    {"ico": "🎓", "h": "Learned (what we use)", "style": "accent",
                     "p": "Learn positional vectors the same way we learn word embeddings — an "
                          "`Embedding` table indexed by position. **Simpler and more "
                          "effective** in practice."},
                ]},
                {"t": "p", "md": "The learned scheme has one cost: it fixes a **maximum sequence "
                                 "length** at build time, since the table has one row per "
                                 "position. Sinusoidal encodings extrapolate; learned ones do "
                                 "not."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5 · listing 15.17",
            "title": "The PositionalEmbedding layer",
            "blocks": [
                {"t": "p", "md": "Two `Embedding` tables in one layer: one indexed by token, "
                                 "one indexed by position. The `call()` adds them."},
                {"t": "code", "lang": "python", "file": "listing 15.17", "src": """from keras import ops

class PositionalEmbedding(keras.Layer):
    def __init__(self, sequence_length, input_dim, output_dim):
        super().__init__()
        self.token_embeddings = layers.Embedding(input_dim, output_dim)
        self.position_embeddings = layers.Embedding(sequence_length, output_dim)

    def call(self, inputs):
        positions = ops.cumsum(ops.ones_like(inputs), axis=-1) - 1
        embedded_tokens = self.token_embeddings(inputs)
        embedded_positions = self.position_embeddings(positions)
        return embedded_tokens + embedded_positions"""},
                {"t": "p", "md": "`ops.cumsum(ops.ones_like(inputs), axis=-1) - 1` produces "
                                 "`[0, 1, 2, …]` for every sequence in the batch — a "
                                 "backend-agnostic way to write `arange` that works under "
                                 "TensorFlow, PyTorch, and JAX alike."},
                {"t": "p", "md": "The layer is a **drop-in replacement** for `Embedding`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5 · listing 15.18",
            "title": "Two lines changed",
            "blocks": [
                {"t": "p", "md": "Here is the whole model again. Compare it against listing "
                                 "15.16 and find the difference before reading the note "
                                 "underneath."},
                {"t": "code", "lang": "python", "file": "listing 15.18", "src": """source = keras.Input(shape=(None,), dtype="int32", name="english")
x = PositionalEmbedding(sequence_length, vocab_size, hidden_dim)(source)
encoder_output = TransformerEncoder(hidden_dim, intermediate_dim, num_heads)(
    source=x,
    source_mask=source != 0,
)

target = keras.Input(shape=(None,), dtype="int32", name="spanish")
x = PositionalEmbedding(sequence_length, vocab_size, hidden_dim)(target)
x = TransformerDecoder(hidden_dim, intermediate_dim, num_heads)(
    target=x,
    source=encoder_output,
    source_mask=source != 0,
)
x = layers.Dropout(0.5)(x)
target_predictions = layers.Dense(vocab_size, activation="softmax")(x)
transformer = keras.Model([source, target], target_predictions)"""},
                {"t": "p", "md": "Everything else is untouched. `layers.Embedding` became "
                                 "`PositionalEmbedding`, twice."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5",
            "title": "67% — and a third of the epoch time",
            "blocks": [
                {"t": "stats", "cols": 3, "items": [
                    {"v": "65%", "l": "GRU seq2seq, 34.9 M params"},
                    {"v": "58%", "l": "Transformer without positions"},
                    {"v": "67%", "l": "Transformer with positions, 14.4 M params"},
                ]},
                {"t": "p", "md": "A noticeable improvement on the GRU — and all the more so "
                                 "given that this model has **half the parameters**."},
                {"t": "p", "md": "There is a second thing to notice about the training run: each "
                                 "epoch takes about ==one third== the time. With attention there "
                                 "is no looped state passing, so on a GPU or TPU the entire "
                                 "attention computation happens **in one go**."},
                {"t": "band", "md": "That speed-up is not a minor convenience. It is the "
                                    "property that made scaling to billions of parameters "
                                    "economically possible — the subject of chapter 16."},
            ],
            "notes": "This is the causal chain worth stating out loud: parallelisable training "
                     "→ affordable scaling → large pretrained models → everything from 2018 "
                     "onward. Not accuracy on this toy task.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5 · listing 15.19",
            "title": "The Transformer's translations",
            "blocks": [
                {"t": "out", "src": """-
I'll see you at the library tomorrow.
[start] te veré en la biblioteca mañana [end]
-
Do you know how to ride a bicycle?
[start] sabes montar en bici [end]
-
Tom didn't want to do their dirty work.
[start] tom no quería hacer su trabajo [end]
-
Is he back already?
[start] ya ha vuelto [end]"""},
                {"t": "p", "md": "Subjectively much better than the GRU translations. It is "
                                 "still a toy model — but it is a **better toy model**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.3.5 · an honest caveat",
            "title": "None of these choices is provably optimal",
            "blocks": [
                {"t": "p", "md": "After all this implementation detail one might reasonably "
                                 "protest that it seems arbitrary. So many small decisions taken "
                                 "on faith. How could we know this configuration is optimal?"},
                {"t": "lead", "md": "**The answer is simple — it is not.**"},
                {"t": "bullets", "items": [
                    "Many improvements to attention, normalization, and positional embeddings "
                    "have been proposed since 2017.",
                    "Much current research replaces attention with something **less "
                    "computationally complex**, as sequence lengths grow very long.",
                    "Something will eventually supplant the Transformer — possibly before you "
                    "finish this course.",
                ]},
                {"t": "band", "md": "The field moves **empirically**. Attention grew out of an "
                                    "attempt to augment RNNs; after years of guessing and "
                                    "checking by a great many people, it gave rise to the "
                                    "Transformer. There is little reason to think that process "
                                    "is done."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "04", "title": "Classification with a pretrained Transformer",
         "lead": "124 million parameters, one epoch of fine-tuning, and a three-point jump."},

        {
            "type": "slide",
            "kicker": "Section 15.4",
            "title": "Two properties that invited scaling",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "⚡", "h": "Faster to train", "style": "good",
                     "p": "No loops during training, which is always good on a GPU or TPU. The "
                          "whole sequence is processed at once."},
                    {"ico": "🍽", "h": "Data hungry", "style": "accent",
                     "p": "We saw this ourselves: the RNN plateaued on validation after about "
                          "5 epochs; the Transformer was **still improving after 30**."},
                ]},
                {"t": "p", "md": "These observations prompted many to try scaling the "
                                 "Transformer up — more data, more layers, more parameters — "
                                 "with strikingly good results."},
                {"t": "p", "md": "The result was a distinctive shift in the field toward **large "
                                 "pretrained models** that can cost millions to train but "
                                 "perform noticeably better across a wide range of text problems."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.1 · BERT",
            "title": "Masked language modelling",
            "blocks": [
                {"t": "p", "md": "**BERT** — Bidirectional Encoder Representations from "
                                 "Transformers — appeared a year after *Attention Is All You "
                                 "Need*. Its structure was **exactly the encoder** of the "
                                 "translation Transformer we just built."},
                {"t": "p", "md": "But BERT was 100 to 300 million parameters, against our 14 "
                                 "million. That needs a great deal of training data, so the "
                                 "authors used a variant of the language-model objective."},
                {"t": "steps", "items": [
                    "Take a sequence of text and replace about **15% of tokens** with a special "
                    "`[MASK]` token.",
                    "Train the model to predict the **original** value of each masked token.",
                    "Note what is *not* needed: **any labels at all**. For any text sequence you "
                    "can choose random tokens and mask them.",
                ]},
                {"t": "band", "md": "A causal language model learns p(token | **past** tokens). "
                                    "A masked language model learns p(token | **surrounding** "
                                    "tokens)."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.1 · the two families",
            "title": "Encoder or decoder — a choice that follows from the objective",
            "blocks": [
                {"t": "mmd", "id": "ch15-lm-kinds", "src": MMD_LM_KINDS,
                 "cap": "The objective determines the masking, the masking determines what the "
                        "model is good for."},
                {"t": "table",
                 "head": ["", "Causal LM", "Masked LM"],
                 "widths": [26, 37, 37],
                 "rows": [
                     ["Distribution", "p(token \\| past)", "p(token \\| surrounding)"],
                     ["Attention", "Causal-masked, one direction", "Bidirectional"],
                     ["Good at", "**Generating** text in a loop", "**Representing** text richly"],
                     ["Examples", "GPT, Llama — chapter 16", "BERT, RoBERTa — this section"],
                 ]},
                {"t": "p", "md": "Pretrained word embeddings were already common practice when "
                                 "BERT appeared — chapter 14 did exactly that. Pretraining a "
                                 "whole Transformer gave something more powerful: an embedding "
                                 "for a word ==in the context of the words around it==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.2 · RoBERTa",
            "title": "Same architecture, ten times the data",
            "blocks": [
                {"t": "p", "md": "We will use **RoBERTa** — Robustly Optimized BERT — rather "
                                 "than BERT itself. It made minor architectural simplifications, "
                                 "but the notable change was the training data."},
                {"t": "stats", "cols": 3, "items": [
                    {"v": "16 GB", "l": "BERT — mainly Wikipedia"},
                    {"v": "160 GB", "l": "RoBERTa — text from across the web"},
                    {"v": "~$300k", "l": "estimated training cost at the time"},
                ]},
                {"t": "p", "md": "Because of the extra data, RoBERTa performs noticeably better "
                                 "**at an equivalent parameter count**. That relationship — data "
                                 "quantity buying quality at fixed model size — is the "
                                 "central empirical fact of the pretraining era."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.2",
            "title": "Three things you need to use a pretrained model",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔡", "h": "A matching tokenizer", "style": "accent",
                     "p": "Text must be tokenized **exactly** as it was during pretraining. If "
                          "words map to different indices, the learned representations are "
                          "meaningless."},
                    {"ico": "🏗", "h": "A matching architecture", "style": "accent",
                     "p": "The internal maths must be recreated exactly. Ours nearly matches "
                          "`TransformerEncoder` already — but *nearly* is not enough."},
                    {"ico": "⚖", "h": "The pretrained weights", "style": "accent",
                     "p": "Produced by training for about a day on **1,024 GPUs** over billions "
                          "of words."},
                ]},
                {"t": "p", "md": "Recreating the first two by hand would be possible but "
                                 "time-consuming and error-prone. As in chapter 8, we use "
                                 "**KerasHub** instead."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.2 · listing 15.20",
            "title": "Two lines to load a pretrained Transformer",
            "blocks": [
                {"t": "p", "md": "KerasHub exposes pretrained checkpoints through a single "
                                 "constructor, `from_preset()`, named by a string identifier."},
                {"t": "code", "lang": "python", "file": "listing 15.20", "src": """import keras_hub

tokenizer = keras_hub.models.Tokenizer.from_preset("roberta_base_en")
backbone = keras_hub.models.Backbone.from_preset("roberta_base_en")"""},
                {"t": "p", "md": "`from_preset()` loads weights, configuration, and tokenizer "
                                 "assets together — which is precisely what keeps the three "
                                 "requirements on the previous slide consistent with one "
                                 "another."},
                {"t": "out", "src": """>>> tokenizer("The quick brown fox")
Array([ 133, 2119, 6219, 23602], dtype=int32)"""},
                {"t": "p", "md": "RoBERTa's tokenizer is close to the subword tokenizer built in "
                                 "chapter 14, with tweaks to handle Unicode from any language."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.2 · why subwords are mandatory here",
            "title": "The tokenization decision, at 160 GB",
            "blocks": [
                {"t": "table",
                 "head": ["Choice", "What goes wrong at this scale"],
                 "widths": [26, 74],
                 "rows": [
                     ["**Character level**",
                      "Input sequences become far too long, making the model much more "
                      "expensive to train — attention cost grows with the *square* of length."],
                     ["**Word level**",
                      "Covering the distinct words across millions of web documents blows up "
                      "the vocabulary, making the front `Embedding` layer unworkably large."],
                     ["**Subword (BPE)**",
                      "Handles **any** word with a 50,000-term vocabulary. This is why every "
                      "large model uses it."],
                 ]},
                {"t": "p", "md": "The trade-off from chapter 14 has not changed — but the "
                                 "pressure on both ends is far greater, which is what makes the "
                                 "middle option not merely convenient but ==required=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.2 · what is a backbone",
            "title": "A model without a head",
            "blocks": [
                {"t": "p", "md": "Chapter 8 used *backbone* for a vision network mapping images "
                                 "to a latent space — a model without a prediction head. In "
                                 "KerasHub the term covers any pretrained model **not yet "
                                 "specialised for a task**."},
                {"t": "p", "md": "What we loaded maps an input sequence to an output sequence of "
                                 "shape **(batch_size, sequence_length, 768)**. It is not set up "
                                 "for any particular loss function."},
                {"t": "mmd", "id": "ch15-backbone", "src": MMD_BACKBONE,
                 "cap": "One backbone, many heads: classifying sentences, extracting spans, "
                        "tagging parts of speech."},
                {"t": "band", "md": "Think of it as attaching different heads to a screwdriver "
                                    "— a Phillips head for one task, a flat head for another."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.2",
            "title": "124 million parameters, twelve blocks deep",
            "blocks": [
                {"t": "out", "src": """>>> backbone.summary()
Model: "roberta_backbone"
│ token_ids (InputLayer)      │ (None, None)      │          0 │
│ embeddings                  │ (None, None, 768) │ 38,996,736 │
│  (TokenAndPositionEmbedding)│                   │            │
│ embeddings_layer_norm       │ (None, None, 768) │      1,536 │
│ padding_mask (InputLayer)   │ (None, None)      │          0 │
│ transformer_layer_0         │ (None, None, 768) │  7,087,872 │
│ transformer_layer_1         │ (None, None, 768) │  7,087,872 │
│ ...                         │ ...               │        ... │
│ transformer_layer_11        │ (None, None, 768) │  7,087,872 │
 Total params: 124,052,736 (473.22 MB)"""},
                {"t": "p", "md": "Twelve identical encoder blocks stacked — exactly the "
                                 "stacking property we noted when the `TransformerEncoder` "
                                 "preserved its input shape. This is the **smallest** RoBERTa "
                                 "checkpoint, and the largest model used anywhere in this book "
                                 "so far."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.3 · listing 15.21",
            "title": "Packing tokens the way pretraining did",
            "blocks": [
                {"t": "p", "md": "RoBERTa expects sequences packed in a specific form: an `<s>` "
                                 "token, the content, an `</s>` token, then `<pad>` tokens."},
                {"t": "out", "src": """[
    ["<s>", "the", "quick", "brown", "fox", "jumped", ".", "</s>"],
    ["<s>", "the", "panda", "slept", ".", "</s>", "<pad>", "<pad>"],
]"""},
                {"t": "code", "lang": "python", "file": "listing 15.21", "src": """def preprocess(text, label):
    packer = keras_hub.layers.StartEndPacker(
        sequence_length=512,
        start_value=tokenizer.start_token_id,
        end_value=tokenizer.end_token_id,
        pad_value=tokenizer.pad_token_id,
        return_padding_mask=True,
    )
    token_ids, padding_mask = packer(tokenizer(text))
    return {"token_ids": token_ids, "padding_mask": padding_mask}, label

preprocessed_train_ds = train_ds.map(preprocess)"""},
                {"t": "p", "md": "Matching the pretraining token ordering as closely as possible "
                                 "makes the model train **faster and more accurately**. The IMDb "
                                 "loading code from chapter 14 is reused unchanged."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.3",
            "title": "One preprocessed batch",
            "blocks": [
                {"t": "out", "src": """>>> next(iter(preprocessed_train_ds))
({"token_ids": <tf.Tensor: shape=(16, 512), dtype=int32, numpy=
  array([[    0,  713,   56, ...,    1,   1,  1],
         [    0, 1121,    5, ...,  101,  24,  2],
         ...,
         [    0,  734,    8, ...,    1,   1,  1]], dtype=int32)>,
  "padding_mask": <tf.Tensor: shape=(16, 512), dtype=bool, numpy=
  array([[ True,  True,  True, ..., False, False, False],
         [ True,  True,  True, ...,  True,  True,  True],
         ...,
         [ True,  True,  True, ..., False, False, False]])>},
 <tf.Tensor: shape=(16,), dtype=int32, numpy=array([0, 1, ...])>)"""},
                {"t": "p", "md": "Batch size is now **16**, not the 32 or 64 used earlier — a "
                                 "124-million-parameter model with 512-token sequences is a "
                                 "different memory proposition. Rows ending in `1` are padded; "
                                 "the `padding_mask` marks exactly where."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.3 · sidebar",
            "title": "Where does pretraining data come from?",
            "blocks": [
                {"t": "table",
                 "head": ["Model", "Pretraining data"],
                 "widths": [24, 76],
                 "rows": [
                     ["The first Transformer (2017)",
                      "A well-known English-German translation set, **4 million sentence pairs**."],
                     ["BERT (2018)",
                      "A dump of English Wikipedia plus a dataset of **7,000 self-published books**."],
                     ["GPT-2 (2019)",
                      "Scraped by following **outgoing links from Reddit**."],
                     ["Llama (latest)",
                      "\"**15 trillion tokens** of data from publicly available sources.\""],
                 ]},
                {"t": "p", "md": "The short answer is: the internet. The other answer is that "
                                 "this has increasingly become a **secret** — companies often do "
                                 "not release the data or the precise mixture of sources."},
                {"t": "band", "md": "When possible, pay close attention to where a model's data "
                                    "came from. It shapes both the **biases** and the "
                                    "**performance** of everything built on top of it.",
                 "style": "amber"},
            ],
            "notes": "This sidebar is where governance, procurement, and legal questions enter "
                     "the technical curriculum. Chapter 18 returns to it; chapter 16 shows how "
                     "much the exact data mixture matters.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.4 · listing 15.22",
            "title": "The classification head, and why it uses token zero",
            "blocks": [
                {"t": "p", "md": "The backbone outputs a whole sequence, shape (batch, length, "
                                 "768). To predict one label we must condense that to a single "
                                 "vector per sample."},
                {"t": "code", "lang": "python", "file": "listing 15.22", "src": """inputs = backbone.input
x = backbone(inputs)
x = x[:, 0, :]
x = layers.Dropout(0.1)(x)
x = layers.Dense(768, activation="relu")(x)
x = layers.Dropout(0.1)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
classifier = keras.Model(inputs, outputs)"""},
                {"t": "p", "md": "`x[:, 0, :]` takes the **first token's** representation. Mean "
                                 "or max pooling would also work, but this works slightly better "
                                 "— and the reason is the nature of attention."},
                {"t": "band", "md": "The first position in the final encoder layer can attend to "
                                    "**every** other position and pull information from them. "
                                    "So rather than pooling with something coarse like an "
                                    "average, attention pools ==contextually==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.4 · listing 15.23",
            "title": "One epoch, and a very small learning rate",
            "blocks": [
                {"t": "p", "md": "One detail in this compile call carries almost all of the "
                                 "risk, and it is the optimizer's learning rate."},
                {"t": "code", "lang": "python", "file": "listing 15.23", "src": """classifier.compile(
    optimizer=keras.optimizers.Adam(5e-5),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)
classifier.fit(
    preprocessed_train_ds,
    validation_data=preprocessed_val_ds,
)"""},
                {"t": "p", "md": "`5e-5` is roughly **twenty times smaller** than Adam's "
                                 "default. This is the fine-tuning discipline from chapter 8, "
                                 "unchanged: large updates would destroy the representations "
                                 "that cost $300,000 to learn."},
                {"t": "out", "src": """>>> classifier.evaluate(preprocessed_test_ds)
[0.168127179145813, 0.9366399645805359]"""},
                {"t": "p", "md": "**93.7% test accuracy after a single epoch**, against the 90% "
                                 "ceiling reached in chapter 14."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.4.4 · the scoreboard",
            "title": "What the last two chapters bought, in one table",
            "blocks": [
                {"t": "p", "md": "Four models, one dataset. Read the third column with the "
                                 "second: the accuracy climbs by four points and the cost by "
                                 "about four **orders of magnitude**."},
                {"t": "table",
                 "head": ["Model", "IMDb test accuracy", "Cost"],
                 "widths": [40, 26, 34],
                 "rows": [
                     ["Bigram bag-of-words (chapter 14)", "≈ 89%", "seconds, on a CPU"],
                     ["Sequence model with pretrained embeddings", "≈ 90%", "minutes, one GPU"],
                     ["**RoBERTa base**, fine-tuned 1 epoch", "**93.7%**", "124 M params, one GPU-hour"],
                     ["RoBERTa large, fine-tuned", "**> 95%**", "300 M params"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.5",
            "title": "…and where that accuracy actually came from",
            "blocks": [
                {"t": "mmd", "id": "ch15-finetune", "src": MMD_FINETUNE,
                 "cap": "Where the accuracy actually came from: months of unlabelled "
                        "pretraining, then one epoch on 20,000 labelled reviews."},
                {"t": "p", "md": "This is a far more expensive model to run than the bigram "
                                 "classifier, and the clear benefit has to be weighed against "
                                 "that. **Chapter 18 makes that trade-off explicit**; for now, "
                                 "note that the three points cost roughly four orders of "
                                 "magnitude in compute."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "05", "title": "What makes the Transformer effective?",
         "lead": "A geometric answer, by way of a model from 2013."},

        {
            "type": "slide",
            "kicker": "Section 15.5 · 2013",
            "title": "Word2Vec, and the magic vectors",
            "blocks": [
                {"t": "p", "md": "At Google in 2013, Tomas Mikolov and colleagues built a "
                                 "pretrained embedding called **Word2Vec**, much like the "
                                 "continuous bag-of-words embedding of chapter 14. The objective "
                                 "turned **correlation** relationships between words into "
                                 "**distance** relationships in an embedding space."},
                {"t": "p", "md": "The resulting space did more than capture similarity. It "
                                 "showed a kind of emergent *word arithmetic*:"},
                {"t": "quote", "md": "V(king) − V(man) + V(woman) ≈ V(queen)",
                 "cite": "A gender vector nobody trained for"},
                {"t": "p", "md": "There were dozens of such vectors — a plural vector, a vector "
                                 "from wild animals to their closest pet equivalent. **The model "
                                 "had not been trained for any of this explicitly.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.5",
            "title": "How much a 2013 toy and a 2024 model have in common",
            "blocks": [
                {"t": "p", "md": "On the surface, nothing could seem further from Word2Vec than "
                                 "a large pretrained Transformer that generates fluent language "
                                 "on any topic. And yet:"},
                {"t": "table",
                 "head": ["", "Word2Vec", "Transformer"],
                 "widths": [34, 33, 33],
                 "rows": [
                     ["Goal", "Embed tokens in a vector space", "Embed tokens in a vector space"],
                     ["Learning principle", "Tokens that co-occur end up close",
                      "Tokens that co-occur end up close"],
                     ["Distance function", "Cosine distance", "Cosine distance"],
                     ["Dimensionality", "~1,000 per word", "1,000 to 10,000 per word"],
                 ]},
                {"t": "p", "md": "You might object: a Transformer is trained to predict missing "
                                 "words, not to group tokens in a space. How does that objective "
                                 "relate to maximising dot-products between co-occurring tokens? "
                                 "==The answer is the attention mechanism.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.5 · the geometric account",
            "title": "Attention is embedding-space refinement",
            "blocks": [
                {"t": "lead", "md": "Attention learns a new embedding space by **linearly "
                                    "recombining** embeddings from a prior space, weighted "
                                    "toward tokens that are already close."},
                {"t": "p", "md": "Because the weighting is a dot product, tokens with high "
                                 "similarity contribute most to each other's new representation. "
                                 "Over training, this **pulls already-close vectors together** — "
                                 "turning correlation relationships into proximity relationships."},
                {"t": "mmd", "id": "ch15-why-effective", "src": MMD_WHY_EFFECTIVE,
                 "cap": "A Transformer learns a series of incrementally refined embedding "
                        "spaces, each recombining elements of the previous one."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.5 · two properties",
            "title": "Continuous, and interpolative",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "〰", "h": "Semantically continuous", "style": "accent",
                     "p": "Moving a little in the embedding space changes the human-facing "
                          "meaning only a little. Word2Vec's space had this property too."},
                    {"ico": "🔀", "h": "Semantically interpolative", "style": "accent",
                     "p": "The midpoint between two points represents the **intermediate "
                          "meaning** — a direct consequence of each space being built by "
                          "interpolating vectors from the previous one."},
                ]},
                {"t": "p", "md": "This is not entirely unlike the brain. The key learning "
                                 "principle there is **Hebbian learning** — *neurons that fire "
                                 "together, wire together*. Correlations between firing events "
                                 "become proximity in the network."},
                {"t": "band", "md": "The Transformer, Word2Vec, and the brain all turn "
                                    "correlation relationships into vector-proximity "
                                    "relationships. All three are ==maps of a space of "
                                    "information==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.5 · the difference in degree",
            "title": "Vector programs, not vector functions",
            "blocks": [
                {"t": "p", "md": "Word2Vec is to today's language models as a logistic "
                                 "regression on MNIST pixels is to a state-of-the-art vision "
                                 "model. It was not even a deep network — a single shallow "
                                 "layer. Today's Transformers stack dozens of attention and "
                                 "feedforward layers with parameter counts in the billions."},
                {"t": "p", "md": "With that representation power, and a more refined "
                                 "autoregressive objective, we are no longer confined to "
                                 "**linear** transformations like a gender vector."},
                {"t": "table",
                 "head": ["Word2Vec could store", "A large Transformer can store"],
                 "widths": [46, 54],
                 "rows": [
                     ["`plural(cat) -> cats`",
                      "`write_this_in_style_of_shakespeare(\"...poem...\")`"],
                     ["`male_to_female(king) -> queen`", "and **millions** of such programs"],
                 ]},
                {"t": "p", "md": "These are so complex that it is more accurate to call them "
                                 "**vector programs** than vector functions — highly nonlinear "
                                 "maps of the latent space onto itself. Not Python programs: no "
                                 "symbolic statements, no step-by-step data processing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 15.5 · the database analogy",
            "title": "A database you can retrieve more from than you put in",
            "blocks": [
                {"t": "p", "md": "You can see a Transformer as a database: it stores information "
                                 "you retrieve via the tokens you pass in. Two differences "
                                 "matter enormously."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📈", "h": "It is continuous", "style": "accent",
                     "p": "Not discrete entries but a **curve**. You can move along it to "
                          "nearby points and interpolate between them — so you can retrieve "
                          "much more than was put in."},
                    {"ico": "⚙", "h": "It stores programs", "style": "accent",
                     "p": "RoBERTa holds facts, places, people, dates, relationships — but "
                          "**primarily** it is a database of vector programs."},
                ]},
                {"t": "band", "md": "Interpolation is the same mechanism behind both outcomes: "
                                    "it leads to **generalization**, and it leads to "
                                    "**hallucination**. Not all of what you retrieve will be "
                                    "accurate or meaningful.", "style": "rose"},
            ],
            "notes": "This is the single most useful sentence in the chapter for a professional "
                     "audience. Hallucination is not a bug to be patched out; it is the same "
                     "property that makes the model useful, observed from the other side.",
        },

        {
            "type": "slide",
            "kicker": "Section 15.5 · the honest limit",
            "title": "Interpolation is not synthesis",
            "blocks": [
                {"t": "p", "md": "In the next chapter we push these models to billions of "
                                 "parameters and trillions of words. Their output can feel like "
                                 "magic — like an intelligent operator sitting inside, pulling "
                                 "the strings."},
                {"t": "quote", "md": "These models are **fundamentally interpolative**. Thanks "
                                     "to attention, they learn an interpolative embedding space "
                                     "for a significant chunk of all text written in English. "
                                     "Wandering that space leads to interesting, unexpected "
                                     "generalizations — but it cannot synthesize something "
                                     "fundamentally new with anything close to genuine, "
                                     "human-level intelligence.",
                 "cite": "Section 15.5, closing"},
                {"t": "p", "md": "Keep this claim in mind through chapters 16 and 19, where it "
                                 "is tested against much larger models and much stronger claims."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Common failure modes",
            "title": "Four ways Transformer code goes quietly wrong",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🕰", "h": "No causal mask on the decoder", "style": "bad",
                     "p": "Training accuracy shoots up, generation produces nothing coherent. "
                          "The model is reading its own label. `use_causal_mask=True`."},
                    {"ico": "📍", "h": "No positional embedding", "style": "bad",
                     "p": "The model trains, converges, and scores several points too low with "
                          "no error message. It is treating your sentences as **bags of words**."},
                    {"ico": "🔤", "h": "Tokenizer mismatched to weights", "style": "warn",
                     "p": "Fine-tuning a pretrained backbone with the wrong tokenizer produces "
                          "near-random performance. Load both from the **same preset**."},
                    {"ico": "🚿", "h": "Default learning rate on fine-tuning", "style": "warn",
                     "p": "Adam's default is ~20× too large for a pretrained backbone and will "
                          "wash out the representations in the first few batches."},
                ]},
                {"t": "p", "md": "Three of these four produce **no exception and no warning** — "
                                 "only a number that is worse than it should be. That is what "
                                 "makes them worth memorising."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**A language model learns p(token | past tokens)** — and generates text of "
                    "any length by being called in a loop, output becoming input.",
                    "**A masked language model** learns p(token | surrounding tokens), which is "
                    "better for representing text than for generating it.",
                    "**Seq2seq** splits into an encoder that represents the source and a "
                    "decoder that predicts the target one token at a time.",
                    "**Attention** scores by dot product, normalises by softmax, and returns a "
                    "weighted sum — giving direct access to any position in a sequence.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter (2 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**The Transformer block** is attention (mixes positions, no nonlinearity) "
                    "plus feedforward (mixes features, has the nonlinearity), with residuals "
                    "and layer normalization around both.",
                    "**Attention is order-blind**, so positional embeddings are not optional — "
                    "leaving them out costs several points and raises no error.",
                    "**Pretraining then fine-tuning** beat training from scratch decisively: "
                    "93.7% in one epoch against a 90% ceiling.",
                    "**Attention turns correlation into proximity**, building interpolative "
                    "embedding spaces — the source of both generalization and hallucination.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_attention_from_scratch.ipynb",
                     "href": notebook_url(15, "03_attention_from_scratch.ipynb")},
                    {"k": "PAPER", "ic": "📄", "v": "Vaswani et al., Attention Is All You Need",
                     "href": "https://arxiv.org/abs/1706.03762"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 16 — Text generation",
                     "href": "../ch16/index.html"},
                ]},
            ],
        },
    ],
}
