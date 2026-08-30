# -*- coding: utf-8 -*-
"""Chapter 16 — Text generation.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 16
(pp. 466-507), read from the book PDF.

The chapter that assembles an LLM from parts the course already has: the
decoder block of chapter 15, the language-model objective of chapter 15, and a
billion words of crawled text. Then sampling strategies, a pretrained Gemma,
instruction fine-tuning under LoRA, and the honest limits — hallucination,
prompt sensitivity, and a pretraining-data supply that is running out.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_HISTORY = """
flowchart LR
  A["1997<br/><b>LSTM</b><br/><small>Hochreiter &amp;<br/>Schmidhuber</small>"]
  B["2002<br/><b>Music generation</b><br/><small>Douglas Eck<br/>applies LSTM</small>"]
  C["2013<br/><b>Handwriting</b><br/><small>Alex Graves,<br/>mixture density RNNs</small>"]
  D["2018<br/><b>GPT-1</b><br/><small>pretraining +<br/>Transformer</small>"]
  E["2022<br/><b>ChatGPT</b><br/><small>GPT-3 + RLHF</small>"]
  A --> B --> C --> D --> E
"""

MMD_GPT_INGREDIENTS = """
flowchart TB
  A["<b>Unsupervised pretraining</b><br/><small>guess the next token</small>"]
  B["<b>The Transformer</b><br/><small>from the 2017 paper</small>"]
  C["<b>A lot of text</b><br/><small>thousands of<br/>self-published books</small>"]
  G["<b>GPT</b><br/>Generative Pretrained Transformer"]
  R["State of the art across<br/>a wide array of tasks<br/><small>with no per-task<br/>architecture changes</small>"]
  A --> G
  B --> G
  C --> G
  G --> R
"""

MMD_DECODER_ONLY = """
flowchart TB
  subgraph S["Chapter 15 - encoder/decoder"]
    direction TB
    E1["Encoder<br/><small>source sequence</small>"]
    D1["Decoder<br/><small>target sequence</small>"]
    E1 --> D1
  end
  subgraph G["Chapter 16 - decoder only"]
    direction TB
    X["<b>One sequence</b><br/><small>question and answer<br/>concatenated</small>"]
    D2["Decoder stack<br/><small>causal mask throughout</small>"]
    X --> D2
  end
  S --> G
"""

MMD_TIED_WEIGHTS = """
flowchart LR
  T["Token IDs"]
  E["<b>Embedding matrix</b><br/><small>(vocab_size, hidden_dim)</small>"]
  B["Decoder blocks"]
  H["Hidden states"]
  R["<b>Same matrix, transposed</b><br/><small>(hidden_dim, vocab_size)</small>"]
  L["Logits"]
  T --> E --> B --> H --> R --> L
  E -. "weights shared" .-> R
"""

MMD_SAMPLING = """
flowchart TB
  P["Model output:<br/>32,000 logits"]
  G["<b>Greedy</b><br/><small>argmax</small><br/>repeats itself"]
  R["<b>Random</b><br/><small>sample the whole<br/>distribution</small><br/>wanders off"]
  K["<b>Top-K</b><br/><small>sample the K best</small><br/>a middle ground"]
  P --> G
  P --> R
  P --> K
"""

MMD_TEMPERATURE = """
flowchart LR
  L["Logits"]
  D["Divide by<br/><b>temperature</b>"]
  S["Softmax"]
  O["Sample"]
  L --> D --> S --> O
  D -. "low T: peaks sharpen<br/>toward greedy" .-> S
  D -. "high T: distribution flattens<br/>toward noise" .-> S
"""

MMD_KVCACHE = """
flowchart TB
  A["Feedforward blocks<br/><small>each position in isolation</small>"]
  B["<b>Attention</b><br/><small>the only place information<br/>crosses positions</small>"]
  C["Past keys and values<br/><b>never change</b><br/><small>the causal mask<br/>forbids looking ahead</small>"]
  D["<b>Cache them</b><br/><small>the Transformer equivalent<br/>of an RNN state</small>"]
  E["Input shrinks from<br/>the whole sequence<br/>to <b>one token</b>"]
  A --> B
  B --> C --> D --> E
"""

MMD_LORA = """
flowchart TB
  I["Inputs"]
  W["<b>Pretrained kernel</b><br/><small>(hidden, hidden)</small><br/><b>FROZEN</b>"]
  AL["<b>Alpha</b><br/><small>(hidden, rank)</small>"]
  BE["<b>Beta</b><br/><small>(rank, hidden)</small>"]
  S["Add"]
  O["Outputs"]
  I --> W --> S
  I --> AL --> BE --> S
  S --> O
"""

MMD_RLHF = """
flowchart TB
  SFT["<b>1. Supervised fine-tuning</b><br/><small>handwritten prompts<br/>and responses</small>"]
  RANK["<b>2. Rank responses</b><br/><small>human evaluators order them<br/>most to least helpful</small>"]
  RM["<b>3. Reward model</b><br/><small>a smaller Transformer:<br/>sequence in, one float out</small>"]
  RL["<b>4. Reinforcement learning</b><br/><small>generate, score, update</small>"]
  IT["<b>5. Iterate</b>"]
  SFT --> RANK --> RM --> RL --> IT
  IT -. "new responses, new rankings" .-> RANK
"""

MMD_MULTIMODAL = """
flowchart TB
  T["Text tokens<br/><small>&quot;What is&quot;</small>"]
  TE["<b>Text embedding</b><br/><small>hard tokens</small>"]
  IM["Image"]
  IE["<b>Image encoder</b><br/><small>420 M parameters,<br/>256 patches</small>"]
  ST["<b>Soft tokens</b><br/><small>(256, 2560)</small>"]
  SEQ["One spliced sequence"]
  D["Decoder blocks"]
  T --> TE --> SEQ
  IM --> IE --> ST --> SEQ
  SEQ --> D
"""

MMD_RAG = """
flowchart LR
  Q["User question"]
  EMB["<b>Embed the query</b><br/><small>with an LLM</small>"]
  VDB["<b>Vector database</b><br/><small>documents keyed by<br/>their embeddings</small>"]
  CTX["Retrieved context"]
  PR["<b>Prompt</b><br/><small>question + context</small>"]
  LLM["LLM"]
  A["Grounded answer"]
  Q --> EMB --> VDB --> CTX --> PR --> LLM --> A
  Q --> PR
"""

MMD_COT = """
flowchart TB
  A["<b>1. Supervised examples</b><br/><small>problems with the<br/>working shown</small>"]
  B["<b>2. Generate</b><br/><small>with randomness, many<br/>responses per problem</small>"]
  C["<b>3. Check the answer</b><br/><small>string-parse the marker</small>"]
  D["<b>4. Fine-tune on the<br/>correct responses</b><br/><small>including the intermediate steps</small>"]
  A --> B --> C --> D
  D -. "repeat" .-> B
"""

MMD_SCALING = """
flowchart TB
  BUD["A fixed pretraining budget<br/><small>a million dollars of flops</small>"]
  M["Spend it on a<br/><b>bigger model</b>"]
  D["Spend it on<br/><b>more data</b>"]
  F["GPT-3 at 175 B was<br/><b>too big for its budget</b>"]
  T["Since then: parameter counts<br/>flatten, token counts climb"]
  BUD --> M --> F
  BUD --> D --> F
  F --> T
"""

MMD_FOUNDATION = """
flowchart TB
  DATA["Broad data at internet scale"]
  OBJ["<b>Self-supervised objective</b><br/><small>a reconstruction loss</small>"]
  FM["<b>Foundation model</b><br/><small>not specialised to<br/>any single task</small>"]
  T1["Classification"]
  T2["Chat"]
  T3["Retrieval"]
  T4["Image generation<br/><small>chapter 17</small>"]
  DATA --> FM
  OBJ --> FM
  FM --> T1
  FM --> T2
  FM --> T3
  FM --> T4
"""

NB = ["01_mini_gpt_data_pipeline.ipynb", "02_training_mini_gpt.ipynb",
      "03_sampling_strategies.ipynb", "04_gemma_generation.ipynb",
      "05_instruction_tuning_with_lora.ipynb"]

DECK = {
    "id": "ch16",
    "kind": "chapter",
    "number": 16,
    "title": "Text Generation",
    "subtitle": "Building a GPT from the parts we already have, then fine-tuning a "
                "billion-parameter model into a chatbot — and being honest about "
                "what none of it fixes.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 16",
    "source_url": chapter_url(16),
    "duration": "4 hours (3 sessions)",
    "presenter": [
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    ],
    "resources": chapter_resources(16, local_notebooks=NB),
    "objectives": [
        "Trace the line from **LSTM in 1997 to ChatGPT**, and name the three "
        "ingredients GPT combined.",
        "Explain why GPT is **decoder-only**, and what that costs and buys.",
        "Build a **mini-GPT**: data pipeline, tied embeddings, warmup schedule, "
        "and a logits-based loss.",
        "Implement and compare **greedy, random, temperature, and top-K** sampling, "
        "and say what each failure mode looks like.",
        "Explain **key-value caching** and why generation is slow without it.",
        "**Instruction fine-tune** a pretrained LLM, and use **LoRA** to make it fit "
        "in accelerator memory.",
        "Describe **RLHF, multimodal input, RAG, and chain-of-thought training** "
        "well enough to judge which one a given problem needs.",
        "State the **structural limits**: hallucination, prompt sensitivity, energy "
        "cost, and a pretraining-data supply that is running out.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "A brief history of sequence generation",
         "lead": "Twenty-five years from a recurrent cell to a consumer product."},

        {
            "type": "slide",
            "kicker": "Section 16.1",
            "title": "This was a niche subtopic until very recently",
            "blocks": [
                {"t": "p", "md": "Generating sequences from a model only hit the mainstream "
                                 "around **2016**. The techniques are much older than that."},
                {"t": "mmd", "id": "ch16-history", "src": MMD_HISTORY,
                 "cap": "Sometimes a good idea takes fifteen years to get started."},
                {"t": "p", "md": "Douglas Eck applied LSTM to **music generation** in 2002, "
                                 "became a researcher at Google Brain, and in 2016 started "
                                 "Magenta. Alex Graves pioneered recurrent networks for new "
                                 "kinds of sequence data — his 2013 work generating human-like "
                                 "**handwriting** from pen-position timeseries is seen by many "
                                 "as the turning point."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.1 · an aside worth keeping",
            "title": "The closest computers get to dreaming",
            "blocks": [
                {"t": "quote", "md": "*\"Generating sequential data is the closest computers get "
                                     "to dreaming.\"*",
                 "cite": "Alex Graves, in a commented-out line of a 2013 LaTeX file on arXiv"},
                {"t": "p", "md": "The line was never meant to be read. Chollet cites it as a "
                                 "significant inspiration behind starting Keras — which is to "
                                 "say that the framework this course is taught in has a remark "
                                 "hidden in a preprint somewhere in its lineage."},
                {"t": "p", "md": "Worth remembering when the field feels purely industrial. Much "
                                 "of what follows in this chapter came out of curiosity long "
                                 "before it came out of a product plan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.1 · 2018",
            "title": "GPT combined three things, and invented none of them",
            "blocks": [
                {"t": "p", "md": "A year after *Attention Is All You Need*, researchers at OpenAI "
                                 "published *Improving Language Understanding by Generative "
                                 "Pre-Training*. They combined:"},
                {"t": "mmd", "id": "ch16-gpt-ingredients", "src": MMD_GPT_INGREDIENTS,
                 "cap": "Generative Pretrained Transformer — three known ingredients, one "
                        "surprising result."},
                {"t": "band", "md": "**GPT came with no modelling or training advancements.** "
                                    "What was interesting is that such a general setup beat more "
                                    "involved, task-specific techniques — no complex text "
                                    "normalization, no per-benchmark architecture. Just "
                                    "==pretraining data and compute==."},
            ],
            "notes": "This is the slide to sit on for a professional audience. The lesson that "
                     "generality plus scale beats specialised engineering is the single most "
                     "consequential fact of the last decade of this field.",
        },

        {
            "type": "slide",
            "kicker": "Section 16.1 · four years",
            "title": "Then OpenAI scaled it with single-minded focus",
            "blocks": [
                {"t": "table",
                 "head": ["Model", "Year", "Parameters", "Training tokens"],
                 "widths": [20, 14, 30, 36],
                 "rows": [
                     ["GPT-1", "2018", "117 million", "1 billion"],
                     ["GPT-2", "2019", "1.5 billion", "more than 10 billion"],
                     ["GPT-3", "2020", "175 billion", "around half a trillion"],
                 ]},
                {"t": "p", "md": "**The architecture changed only slightly** across all three. "
                                 "What changed was the size of everything else — and with each "
                                 "leap in scale, the quality of the generative output shot up "
                                 "substantially."},
                {"t": "p", "md": "That is roughly a **1,500-fold** increase in parameters and a "
                                 "**500-fold** increase in tokens over four years, for the same "
                                 "design."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.1 · what emerged at each scale",
            "title": "Three models, three different ways of being used",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "1️⃣", "h": "GPT-1: fine-tune it", "style": "",
                     "p": "Generative capability was a **by-product**. Evaluation was by "
                          "attaching a dense classification head — exactly what we did to "
                          "RoBERTa in chapter 15."},
                    {"ico": "2️⃣", "h": "GPT-2: show it examples", "style": "accent",
                     "p": "Prompt with a handful of worked examples and get quality output "
                          "**with no fine-tuning at all**. This is *few-shot learning*."},
                    {"ico": "3️⃣", "h": "GPT-3: just describe it", "style": "accent",
                     "p": "Examples were often unnecessary. A plain text description of the "
                          "problem plus the input frequently sufficed."},
                ]},
                {"t": "p", "md": "*Few-shot learning* means teaching a model a new problem with "
                                 "only a handful of supervised examples — **far too few for "
                                 "standard gradient descent**. Nothing is being trained; the "
                                 "capability was already in the pretrained distribution."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.1 · few-shot, concretely",
            "title": "What a GPT-2 prompt looked like",
            "blocks": [
                {"t": "p", "md": "To get a French translation of the word *cheese*, you would "
                                 "prompt the model with a small pattern and let it continue:"},
                {"t": "out", "src": """Translate English to French:

sea otter => loutre de mer
peppermint => menthe poivrée
plush giraffe => peluche girafe
cheese =>"""},
                {"t": "p", "md": "By GPT-3, this was often enough:"},
                {"t": "out", "src": """Translate English to French:

cheese =>"""},
                {"t": "p", "md": "Nothing in the model was updated between the two. The "
                                 "difference is entirely in **what the larger pretrained "
                                 "distribution already contains**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.1 · the problems arrived with the capability",
            "title": "GPT-3's three unsolved problems, stated in 2020",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "👻", "h": "Hallucination", "style": "bad",
                     "p": "Output veers from accurate to **completely false with zero "
                          "indication**. Nothing in the output signals which is which."},
                    {"ico": "🎲", "h": "Prompt sensitivity", "style": "bad",
                     "p": "Seemingly minor rewording triggers **large jumps** in performance, "
                          "up or down. Behaviour is hard to predict."},
                    {"ico": "🧱", "h": "No adaptation", "style": "bad",
                     "p": "The model cannot adapt to problems that were not **extensively "
                          "featured** in its training data."},
                ]},
                {"t": "band", "md": "These were listed as open problems in 2020 and are ==still "
                                    "open==. Everything later in this chapter — instruction "
                                    "tuning, RLHF, RAG, chain-of-thought — reduces their "
                                    "severity. **None of them removes the problem.**",
                 "style": "rose"},
                {"t": "p", "md": "Nevertheless GPT-3's output was good enough to become the "
                                 "basis for ChatGPT, the first widespread consumer-facing "
                                 "generative model."},
            ],
            "notes": "For a professional audience this is the risk-register slide. Come back to "
                     "it after RAG and after the reasoning section, and mark honestly which "
                     "boxes have moved.",
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "Training a mini-GPT",
         "lead": "Forty-one million parameters, a billion tokens, and the exact blueprint "
                 "everyone else is using."},

        {
            "type": "slide",
            "kicker": "Section 16.2",
            "title": "The data: 1% of a colossal clean crawled corpus",
            "blocks": [
                {"t": "p", "md": "GPT-1 used **BooksCorpus** — self-published books added "
                                 "without the explicit permission of their authors. It has since "
                                 "been taken down by its publishers."},
                {"t": "p", "md": "We use **C4**, the Colossal Clean Crawled Corpus released by "
                                 "Google in 2020. At 750 GB it is far more than we can train on, "
                                 "so we take under 1%."},
                {"t": "code", "lang": "python", "file": "listing 16.1", "src": """import keras
import pathlib

extract_dir = keras.utils.get_file(
    fname="mini-c4",
    origin=(
        "https://hf.co/datasets/mattdangerw/mini-c4/resolve/main/mini-c4.zip"
    ),
    extract=True,
)
extract_dir = pathlib.Path(extract_dir) / "mini-c4\""""},
                {"t": "p", "md": "Fifty shards, each about 75 MB of raw text. One document per "
                                 "line, newlines escaped."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2 · a warning worth reading twice",
            "title": "This is the most compute-intensive chapter in the book",
            "blocks": [
                {"t": "stats", "cols": 3, "items": [
                    {"v": "~6 hours", "l": "mini-GPT on a free Colab T4"},
                    {"v": "~1 hour", "l": "the whole chapter on an A100"},
                    {"v": "1", "l": "runtime restart needed mid-notebook"},
                ]},
                {"t": "p", "md": "You will need to restart the Colab runtime partway through to "
                                 "free GPU memory before loading the larger pretrained model."},
                {"t": "band", "md": "You can always **read through** the expensive `fit()` calls "
                                    "and edit down the step count for quick experimentation. The "
                                    "learning is in the code, not in waiting for it.",
                 "style": "amber"},
                {"t": "p", "md": "And if you are running this a few years from now, there is a "
                                 "good chance these examples are child's play to the hardware in "
                                 "front of you."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2",
            "title": "What one document looks like",
            "blocks": [
                {"t": "p", "md": "As always, look at the data before designing anything around "
                                 "it."},
                {"t": "out", "src": """>>> with open(extract_dir / "shard0.txt", "r") as f:
>>>     print(f.readline().replace("\\\\n", "\\n")[:100])
Beginners BBQ Class Taking Place in Missoula!
Do you want to get better at making delicious BBQ? You"""},
                {"t": "p", "md": "Crawled web text: a headline, a newline, marketing copy. This "
                                 "is what the model's distribution will be made of, and it is "
                                 "worth holding that image when the output later looks like a "
                                 "==forum post that will not end==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2 · listing 16.2",
            "title": "SentencePiece: the same BPE, in C++",
            "blocks": [
                {"t": "p", "md": "Preprocessing this much text needs a fast tokenizer. The "
                                 "technique is exactly the byte-pair encoding we built in "
                                 "chapter 14; **SentencePiece** is a C++ implementation of it "
                                 "with a `detokenize()` that maps back to strings."},
                {"t": "code", "lang": "python", "file": "listing 16.2", "src": """import keras_hub
import numpy as np

vocabulary_file = keras.utils.get_file(
    origin="https://hf.co/mattdangerw/spiece/resolve/main/vocabulary.proto",
)
tokenizer = keras_hub.tokenizers.SentencePieceTokenizer(vocabulary_file)"""},
                {"t": "out", "src": """>>> tokenizer.tokenize("The quick brown fox.")
array([ 450, 4996, 17354, 1701, 29916, 29889], dtype=int32)
>>> tokenizer.detokenize([450, 4996, 17354, 1701, 29916, 29889])
"The quick brown fox." """},
                {"t": "p", "md": "A premade vocabulary of **32,000 terms**. KerasHub wraps the "
                                 "library as a Keras layer, so it composes with `tf.data`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2 · a design decision",
            "title": "GPT does not respect document boundaries",
            "blocks": [
                {"t": "p", "md": "When training GPT, the developers made **no attempt** to keep "
                                 "document boundaries from falling in the middle of a training "
                                 "sample. Documents are simply concatenated."},
                {"t": "p", "md": "Instead, a boundary is marked with a special token:"},
                {"t": "out", "src": """<|endoftext|>"""},
                {"t": "p", "md": "The model learns what a document boundary means from the token "
                                 "itself, rather than from how the data was cut. **Simplicity in "
                                 "the pipeline, paid for with one vocabulary entry.**"},
                {"t": "band", "md": "This is a recurring pattern in LLM engineering: when a "
                                    "structural constraint is expensive to enforce in data, "
                                    "==encode it as a token and let the model learn it==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2 · listing 16.3",
            "title": "The pipeline, with interleaved shards",
            "blocks": [
                {"t": "p", "md": "Each shard is read independently and the outputs are "
                                 "interleaved, so every CPU core can tokenize a different file "
                                 "at the same time."},
                {"t": "code", "lang": "python", "file": "listing 16.3", "src": """import tensorflow as tf

batch_size = 128
sequence_length = 256
suffix = np.array([tokenizer.token_to_id("<|endoftext|>")])

def read_file(filename):
    ds = tf.data.TextLineDataset(filename)
    ds = ds.map(lambda x: tf.strings.regex_replace(x, r"\\\\n", "\\n"))
    ds = ds.map(tokenizer, num_parallel_calls=8)
    return ds.map(lambda x: tf.concat([x, suffix], -1))

files = [str(file) for file in extract_dir.glob("*.txt")]
ds = tf.data.Dataset.from_tensor_slices(files)
ds = ds.interleave(read_file, cycle_length=32, num_parallel_calls=32)
ds = ds.rebatch(sequence_length + 1, drop_remainder=True)
ds = ds.map(lambda x: (x[:-1], x[1:]))
ds = ds.batch(batch_size).prefetch(8)"""},
                {"t": "p", "md": "`rebatch(sequence_length + 1)` windows the token stream into "
                                 "even 257-token samples; `x[:-1], x[1:]` is the offset-by-one "
                                 "split from chapter 15, unchanged."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2 · the numbers",
            "title": "Just under a billion tokens",
            "blocks": [
                {"t": "stats", "cols": 3, "items": [
                    {"v": "29,373", "l": "batches"},
                    {"v": "128 × 256", "l": "samples × tokens per batch"},
                    {"v": "~0.96 billion", "l": "tokens of training data"},
                ]},
                {"t": "code", "lang": "python", "src": """num_batches = 29373
num_val_batches = 500
num_train_batches = num_batches - num_val_batches

val_ds = ds.take(num_val_batches).repeat()
train_ds = ds.skip(num_val_batches).repeat()"""},
                {"t": "p", "md": "The batch count is not free to obtain: "
                                 "`ds.reduce(0, lambda c, _: c + 1)` will count it, but "
                                 "tokenizing a dataset this size takes **several minutes on a "
                                 "fast CPU**. The `prefetch(8)` at the end of the pipeline is "
                                 "what keeps the GPU from waiting on it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.1",
            "title": "GPT throws away the encoder",
            "blocks": [
                {"t": "p", "md": "The original GPT **simplifies** the sequence-to-sequence "
                                 "Transformer of chapter 15: no encoder, no cross-attention. "
                                 "Only the decoder stack remains, which means information can "
                                 "only travel left to right."},
                {"t": "mmd", "id": "ch16-decoder-only", "src": MMD_DECODER_ONLY,
                 "cap": "A question and its answer become one sequence, embedded by the same "
                        "parameters."},
                {"t": "p", "md": "A decoder-only model can still handle sequence-to-sequence "
                                 "problems like question answering — but the question and answer "
                                 "must be **combined into a single sequence**, and question "
                                 "tokens are treated no differently from answer tokens."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.1 · the trade",
            "title": "What the decoder-only bet costs, and what it buys",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📉", "h": "The cost: less expressive inputs", "style": "warn",
                     "p": "Given *\"Where is the capital of France?\"*, the representation of "
                          "**Where** cannot attend to **capital** or **France**. Even the input "
                          "is processed one-directionally."},
                    {"ico": "📈", "h": "The gain: no curation at all", "style": "good",
                     "p": "No need for datasets of input/output **pairs**. Everything is a "
                          "single sequence, so you can train on any text on the internet, at "
                          "any scale you can afford."},
                ]},
                {"t": "band", "md": "This is the trade that decided the field. Expressivity was "
                                    "sacrificed for ==an unbounded supply of training data==, "
                                    "and the data won."},
            ],
            "notes": "Contrast explicitly with RoBERTa from chapter 15, which kept "
                     "bidirectionality and is still the better choice when you only need to "
                     "represent text rather than generate it.",
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.1 · listing 16.4",
            "title": "The decoder block, minus cross-attention",
            "blocks": [
                {"t": "p", "md": "This is chapter 15's `TransformerDecoder` with the "
                                 "cross-attention layer removed and one addition: **dropout "
                                 "inside each block**."},
                {"t": "code", "lang": "python", "file": "listing 16.4", "src": """class TransformerDecoder(keras.Layer):
    def __init__(self, hidden_dim, intermediate_dim, num_heads):
        super().__init__()
        key_dim = hidden_dim // num_heads
        self.self_attention = layers.MultiHeadAttention(
            num_heads, key_dim, dropout=0.1
        )
        self.self_attention_layernorm = layers.LayerNormalization()
        self.feed_forward_1 = layers.Dense(intermediate_dim, activation="relu")
        self.feed_forward_2 = layers.Dense(hidden_dim)
        self.feed_forward_layernorm = layers.LayerNormalization()
        self.dropout = layers.Dropout(0.1)"""},
                {"t": "p", "md": "Chapter 15 used a **single** Transformer layer, so one dropout "
                                 "at the end of the model sufficed. Here we stack **eight**, and "
                                 "regularisation inside each block matters."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.1 · listing 16.4",
            "title": "Its forward pass has only two stages now",
            "blocks": [
                {"t": "p", "md": "With cross-attention gone, `call()` takes one input and runs "
                                 "two stages instead of three."},
                {"t": "code", "lang": "python", "file": "listing 16.4 - call", "src": """    def call(self, inputs):
        residual = x = inputs
        x = self.self_attention(query=x, key=x, value=x, use_causal_mask=True)
        x = self.dropout(x)
        x = x + residual
        x = self.self_attention_layernorm(x)

        residual = x
        x = self.feed_forward_1(x)
        x = self.feed_forward_2(x)
        x = self.dropout(x)
        x = x + residual
        x = self.feed_forward_layernorm(x)
        return x"""},
                {"t": "p", "md": "`use_causal_mask=True` is doing all the work that made the "
                                 "training objective valid in chapter 15. **It is the only thing "
                                 "standing between this model and reading its own labels.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.1 · listing 16.5",
            "title": "Tying the input and output projections",
            "blocks": [
                {"t": "p", "md": "The two biggest weights in a Transformer both deal with "
                                 "vocabulary space: the token embedding, shape "
                                 "**(vocab_size, hidden_dim)**, and the output projection, shape "
                                 "**(hidden_dim, vocab_size)**."},
                {"t": "p", "md": "They are transposes of each other in shape. It turns out that "
                                 "making them transposes of each other in **value** is a good "
                                 "idea — the final projection is a *reverse embedding*, mapping "
                                 "hidden space back to token space."},
                {"t": "mmd", "id": "ch16-tied", "src": MMD_TIED_WEIGHTS,
                 "cap": "One matrix, used forward at the input and transposed at the output."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.1 · listing 16.5",
            "title": "A `reverse` argument is all it takes",
            "blocks": [
                {"t": "p", "md": "Chapter 15's `PositionalEmbedding`, with one branch added to "
                                 "`call()`."},
                {"t": "code", "lang": "python", "file": "listing 16.5", "src": """from keras import ops

class PositionalEmbedding(keras.Layer):
    def __init__(self, sequence_length, input_dim, output_dim):
        super().__init__()
        self.token_embeddings = layers.Embedding(input_dim, output_dim)
        self.position_embeddings = layers.Embedding(sequence_length, output_dim)

    def call(self, inputs, reverse=False):
        if reverse:
            token_embeddings = self.token_embeddings.embeddings
            return ops.matmul(inputs, ops.transpose(token_embeddings))
        positions = ops.cumsum(ops.ones_like(inputs), axis=-1) - 1
        embedded_tokens = self.token_embeddings(inputs)
        embedded_positions = self.position_embeddings(positions)
        return embedded_tokens + embedded_positions"""},
                {"t": "p", "md": "With a 32,000-word vocabulary and 512 hidden dimensions, this "
                                 "saves **16 million parameters** — a substantial share of a "
                                 "41-million-parameter model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.1 · listing 16.6",
            "title": "Eight blocks, and the model is done",
            "blocks": [
                {"t": "p", "md": "Everything assembled. Note the single `embedding` object used "
                                 "twice — once forward, once reversed."},
                {"t": "code", "lang": "python", "file": "listing 16.6", "src": """keras.config.set_dtype_policy("mixed_float16")

vocab_size = tokenizer.vocabulary_size()
hidden_dim = 512
intermediate_dim = 2056
num_heads = 8
num_layers = 8

inputs = keras.Input(shape=(None,), dtype="int32", name="inputs")
embedding = PositionalEmbedding(sequence_length, vocab_size, hidden_dim)
x = embedding(inputs)
x = layers.LayerNormalization()(x)
for i in range(num_layers):
    x = TransformerDecoder(hidden_dim, intermediate_dim, num_heads)(x)
outputs = embedding(x, reverse=True)
mini_gpt = keras.Model(inputs, outputs)"""},
                {"t": "p", "md": "**41 million parameters** — large for this book, and tiny "
                                 "against models today that range from a couple of billion to "
                                 "trillions. `mixed_float16` trades some numerical fidelity for "
                                 "speed; chapter 18 explains it properly."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.2",
            "title": "Training a large Transformer is famously finicky",
            "blocks": [
                {"t": "p", "md": "The model is sensitive to parameter initialization and to the "
                                 "choice of optimizer. Stack many Transformer layers and it "
                                 "becomes easy to suffer **exploding gradients** — parameters "
                                 "update too quickly and the loss never converges."},
                {"t": "p", "md": "A trick that works well: ease **linearly** into the full "
                                 "learning rate over a number of warmup steps, so the earliest "
                                 "updates are small."},
                {"t": "code", "lang": "python", "file": "listing 16.7", "src": """class WarmupSchedule(keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self):
        self.rate = 2e-4
        self.warmup_steps = 1_000.0

    def __call__(self, step):
        step = ops.cast(step, dtype="float32")
        scale = ops.minimum(step / self.warmup_steps, 1.0)
        return self.rate * scale"""},
                {"t": "p", "md": "A thousand steps of ramp, then a flat 2e-4. Plot it before "
                                 "training — a schedule that is wrong is invisible in the loss "
                                 "curve until it is far too late."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.2 · listing 16.8",
            "title": "One pass over a billion tokens, in eight epochs",
            "blocks": [
                {"t": "p", "md": "Eight epochs, not because the data repeats, but so we can "
                                 "check validation loss and accuracy periodically during a "
                                 "single pass."},
                {"t": "code", "lang": "python", "file": "listing 16.8", "src": """num_epochs = 8
steps_per_epoch = num_train_batches // num_epochs
validation_steps = num_val_batches

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
    validation_steps=validation_steps,
)"""},
                {"t": "p", "md": "We use **3× fewer parameters** than GPT-1 and **100× fewer "
                                 "training steps**. Even so, this is the most computationally "
                                 "expensive training run in the entire book."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.2 · sidebar",
            "title": "What is a logit?",
            "blocks": [
                {"t": "p", "md": "The output projection has **no softmax activation**. Its "
                                 "outputs are unnormalized log probabilities — exponentiate each "
                                 "and normalise them to sum to 1, which is all softmax does, and "
                                 "you have probabilities."},
                {"t": "p", "md": "The common term for an unnormalized log probability is a "
                                 "**logit**, and logits are easier to work with when generating "
                                 "text — as the sampling section will show."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📊", "h": "Softmax in the model", "style": "",
                     "p": "`Dense(n, activation=\"softmax\")` plus "
                          "`SparseCategoricalCrossentropy()`. The model outputs probabilities."},
                    {"ico": "🔢", "h": "Softmax in the loss", "style": "accent",
                     "p": "`Dense(n)` plus "
                          "`SparseCategoricalCrossentropy(from_logits=True)`. The model outputs "
                          "logits — **more numerically stable, and easier to sample from**."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.2",
            "title": "36% — and the model is deliberately undertrained",
            "blocks": [
                {"t": "p", "md": "After training, the model predicts the next token correctly "
                                 "about **36%** of the time on the validation set. As always, "
                                 "next-token accuracy is a crude heuristic rather than a measure "
                                 "of usefulness."},
                {"t": "band", "md": "The validation loss is **still ticking down** after every "
                                    "epoch. This model is not converged and we know it — "
                                    "unsurprising with a hundred times fewer training steps than "
                                    "GPT-1. Training longer would help; it would also cost time "
                                    "and money.", "style": "amber"},
                {"t": "p", "md": "Being explicit about an undertrained model is itself a "
                                 "discipline. Most published curves stop where the budget ran "
                                 "out, not where the model stopped improving."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "Decoding and sampling strategies",
         "lead": "The model gives you a distribution. What you do with it is a separate design."},

        {
            "type": "slide",
            "kicker": "Section 16.2.3 · listing 16.9",
            "title": "The naive generation loop",
            "blocks": [
                {"t": "p", "md": "The same approach as the Shakespeare generator: feed a prompt, "
                                 "take the prediction at the last position, append, repeat."},
                {"t": "code", "lang": "python", "file": "listing 16.9", "src": """def generate(prompt, max_length=64):
    tokens = list(ops.convert_to_numpy(tokenizer(prompt)))
    prompt_length = len(tokens)
    for _ in range(max_length - prompt_length):
        prediction = mini_gpt(ops.convert_to_numpy([tokens]))
        prediction = ops.convert_to_numpy(prediction[0, -1])
        tokens.append(np.argmax(prediction).item())
    return tokenizer.detokenize(tokens)"""},
                {"t": "p", "md": "Correct, readable — and it takes **minutes** to produce 64 "
                                 "tokens. That is the puzzle to solve before anything else."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.3",
            "title": "What it produces, and why it is slow",
            "blocks": [
                {"t": "out", "src": """>>> prompt = "A piece of advice"
>>> generate(prompt)
A piece of advice, and the best way to get a feel for yourself is to get a sense
of what you are doing.
If you are a business owner, you can get a sense of what you are doing. You can
get a sense of what you are doing, and you can get a sense of what"""},
                {"t": "p", "md": "Two separate problems, and it is worth naming them apart. "
                                 "**One:** it repeats itself. **Two:** it took minutes, when "
                                 "training ran at 200,000 tokens per second on the same "
                                 "hardware."},
                {"t": "p", "md": "The second is a compilation problem. `fit()` and `predict()` "
                                 "compile the per-batch computation — `keras.ops` calls are "
                                 "lifted out of Python and optimised by the backend. Calling the "
                                 "model **directly** runs the forward pass live and "
                                 "==unoptimized at every step==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.3 · listing 16.10",
            "title": "Pad the input so the shape never changes",
            "blocks": [
                {"t": "p", "md": "`predict()` compiles for a **specific input shape**. Our "
                                 "sequence grows by one token each step, which would trigger "
                                 "recompilation every call. Pad to full length up front and the "
                                 "shape is constant."},
                {"t": "code", "lang": "python", "file": "listing 16.10", "src": """def compiled_generate(prompt, max_length=64):
    tokens = list(ops.convert_to_numpy(tokenizer(prompt)))
    prompt_length = len(tokens)
    tokens = tokens + [0] * (max_length - prompt_length)
    for i in range(prompt_length, max_length):
        prediction = mini_gpt.predict(np.array([tokens]), verbose=0)
        prediction = prediction[0, i - 1]
        tokens[i] = np.argmax(prediction).item()
    return tokenizer.detokenize(tokens)"""},
                {"t": "out", "src": """>>> import timeit
>>> tries = 10
>>> timeit.timeit(lambda: compiled_generate(prompt), number=tries) / tries
0.4866470648999893"""},
                {"t": "p", "md": "From minutes to **under half a second**. Same maths, same "
                                 "weights, same output — a pure engineering win."},
            ],
            "notes": "Worth flagging for anyone deploying: a large share of real-world inference "
                     "cost is lost to recompilation from variable shapes. It rarely shows up as "
                     "an error, only as a bill.",
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.3 · sidebar",
            "title": "One inefficiency remains. Can you spot it?",
            "blocks": [
                {"t": "p", "md": "Each call runs the model over the **entire** sequence, then "
                                 "throws away everything but one position. The sequence changes "
                                 "by a single token between steps."},
                {"t": "p", "md": "With the RNN in chapter 15 we kept the state and computed one "
                                 "token at a time. A causal Transformer has an equivalent notion "
                                 "of state — you just have to look for it."},
                {"t": "mmd", "id": "ch16-kvcache", "src": MMD_KVCACHE,
                 "cap": "Attention is the only place information crosses positions, and past "
                        "keys and values never change."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.3 · sidebar",
            "title": "Key-value caching, and why every real system has it",
            "blocks": [
                {"t": "p", "md": "For a query at a given position, attention scores come from "
                                 "dotting that query with **all previous key vectors**, and the "
                                 "output combines **all previous value vectors**. Past input is "
                                 "fixed, and the causal mask forbids looking ahead — so those "
                                 "vectors never change."},
                {"t": "p", "md": "Cache every key and value at every layer, and you have the "
                                 "Transformer equivalent of an RNN's state."},
                {"t": "band", "md": "Model input goes from *as long as the output* to **one "
                                    "token**. On a sequence thousands of tokens long this is a "
                                    "==thousandfold speed-up==. Any efficient implementation of "
                                    "generative sampling includes it.", "style": "amber"},
                {"t": "p", "md": "Implementing it is clunky — saving and reusing intermediate "
                                 "arrays from every attention layer — which is exactly why you "
                                 "should use a library that has already done it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4",
            "title": "The repetition is not a bug",
            "blocks": [
                {"t": "p", "md": "The model repeats *\"get a sense of what you are doing\"* over "
                                 "and over. This follows **directly from the training "
                                 "objective**."},
                {"t": "p", "md": "The model predicts the most likely next token across a billion "
                                 "words on many topics. Where there is no obvious continuation, "
                                 "an effective strategy is to guess **common words or repeated "
                                 "patterns** — and the model learns this almost immediately."},
                {"t": "band", "md": "Stop training very early and the model would generate the "
                                    "word `\"the\"` incessantly, because *the* is the most common "
                                    "word in English. Repetition is the objective ==working "
                                    "correctly==, being asked the wrong question."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4",
            "title": "The output is a distribution, not a token",
            "blocks": [
                {"t": "p", "md": "Throughout the generative loop we have taken the most likely "
                                 "token. But the output is not a token — it is a probability "
                                 "distribution across all **32,000** entries in the vocabulary."},
                {"t": "p", "md": "Taking the most likely output at each step is called **greedy "
                                 "search**. It is the most straightforward use of the "
                                 "predictions, and hardly the only one. Adding randomness lets "
                                 "us explore the learned distribution more broadly, and keeps us "
                                 "out of high-probability loops."},
                {"t": "mmd", "id": "ch16-sampling", "src": MMD_SAMPLING,
                 "cap": "Figure 16.3 — three strategies over the same distribution."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4",
            "title": "Refactor: make the strategy a parameter",
            "blocks": [
                {"t": "p", "md": "Pass a function that maps model predictions to a chosen token. "
                                 "Everything that follows is a different `sample_fn`."},
                {"t": "code", "lang": "python", "src": """def compiled_generate(prompt, sample_fn, max_length=64):
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
    return ops.argmax(preds)"""},
                {"t": "p", "md": "The sampling strategy is now a **first-class control** rather "
                                 "than a hardcoded `argmax` buried in a loop — which is how "
                                 "every serving framework exposes it too."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · random sampling",
            "title": "Sample the distribution directly",
            "blocks": [
                {"t": "p", "md": "`keras.random.categorical()` passes predictions through a "
                                 "softmax and samples the resulting distribution."},
                {"t": "code", "lang": "python", "src": """def random_sample(preds, temperature=1.0):
    preds = preds / temperature
    return keras.random.categorical(preds[None, :], num_samples=1)[0]"""},
                {"t": "out", "src": """>>> compiled_generate(prompt, random_sample)
A piece of advice, just read my knees and stick with getables and a hello to me.
However, the bar napkin doesn't last as long. I happen to be waking up close and
pull it up as I wanted too and I still get it, really, shouldn't be a reaction"""},
                {"t": "p", "md": "More diverse, and no longer stuck in loops — but now it "
                                 "**explores too much**. The output jumps around without "
                                 "continuity. We have traded one failure for its opposite."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · temperature",
            "title": "One number that sharpens or flattens the distribution",
            "blocks": [
                {"t": "p", "md": "Dividing the logits before the softmax rescales how peaked the "
                                 "distribution is."},
                {"t": "mmd", "id": "ch16-temperature", "src": MMD_TEMPERATURE,
                 "cap": "Temperature acts on the logits, before the softmax — not on the "
                        "probabilities after it."},
                {"t": "bullets", "items": [
                    "**Low temperature** makes all logits larger before the softmax, so the "
                    "most likely output becomes even more likely.",
                    "**High temperature** makes them smaller, so the distribution spreads out.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · temperature, observed",
            "title": "T = 2.0: not English any more",
            "blocks": [
                {"t": "p", "md": "The failure at high temperature is unmistakable."},
                {"t": "out", "src": """>>> from functools import partial
>>> compiled_generate(prompt, partial(random_sample, temperature=2.0))
A piece of advice tran writes using ignore unnecessary pivot - come without
introdu accounts indicugel per divuren sendSolis silen om transparent
Gill Guide pover integer song arrays coding LIST**...Allow index criteria
Draw Reference Ex artifactincluding lib tak Br basunker increases entirelytembre
Any TextView cardinal spiritual heavenToen"""},
                {"t": "p", "md": "Subword fragments, stray identifiers, tokens from other "
                                 "languages. At high temperature the distribution is flat enough "
                                 "that rare tokens win regularly, and **rare tokens in a 32,000 "
                                 "vocabulary are mostly debris**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · temperature, observed",
            "title": "T = 0.8 and T = 0.2: fluency against repetition",
            "blocks": [
                {"t": "out", "src": """>>> compiled_generate(prompt, partial(random_sample, temperature=0.8))
A piece of advice I wrote about the same thing today. I have been a writer for
two years now. I am writing this blog and I just wrote about it. I am writing
this blog and it was really interesting."""},
                {"t": "out", "src": """>>> compiled_generate(prompt, partial(random_sample, temperature=0.2))
A piece of advice, and a lot of people are saying that they have to be careful
about the way they think about it.
I think it's a good idea to have a good understanding of the way you think about
it.
I think it's a good idea to have a good understanding of the"""},
                {"t": "p", "md": "At low temperature the behaviour converges on **greedy search**, "
                                 "repeating patterns. Temperature is a dial between two known "
                                 "failure modes, not a fix for either."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · top-K",
            "title": "Restrict the choice to the K most likely tokens",
            "blocks": [
                {"t": "p", "md": "A different shaping technique: keep only the top *K* candidates "
                                 "and sample among them. `keras.ops.top_k` does the selection."},
                {"t": "code", "lang": "python", "src": """def top_k(preds, k=5, temperature=1.0):
    preds = preds / temperature
    top_preds, top_indices = ops.top_k(preds, k=k, sorted=False)
    choice = keras.random.categorical(top_preds[None, :], num_samples=1)[0]
    return ops.take_along_axis(top_indices, choice, axis=-1)"""},
                {"t": "band", "md": "**Temperature and top-K are not the same knob.** A low "
                                    "temperature makes likely tokens more likely but rules "
                                    "==nothing== out. Top-K sets the probability of everything "
                                    "outside the K candidates to ==zero=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · top-K, observed",
            "title": "K = 5, K = 20, and the two combined",
            "blocks": [
                {"t": "out", "src": """>>> compiled_generate(prompt, partial(top_k, k=5))
A piece of advice that I can't help it. I'm not going to be able to do anything
for a few months, but I'm trying to get a little better. It's a little too much.

>>> compiled_generate(prompt, partial(top_k, k=20))
A piece of advice and guidance from the Audi Bank in 2015. With all the above,
it's not just a bad idea, but it's very good to see that is going to be a great
year for you in 2017."""},
                {"t": "out", "src": """>>> compiled_generate(prompt, partial(top_k, k=5, temperature=0.5))
A piece of advice that you can use to get rid of the problem.
The first thing you need to do is to get the job done. It is important that you
have a plan that will help you get rid of it."""},
                {"t": "p", "md": "The two compose: sampling the top five candidates at a "
                                 "temperature of 0.5 is a common production default."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · what to take away",
            "title": "Sampling is a control, and there are more of them",
            "blocks": [
                {"t": "table",
                 "head": ["Strategy", "What it does", "Failure mode"],
                 "widths": [22, 44, 34],
                 "rows": [
                     ["**Greedy**", "Takes the argmax at every step",
                      "Repeats phrases indefinitely"],
                     ["**Random**", "Samples the full categorical distribution",
                      "Wanders, no continuity"],
                     ["**Temperature**", "Scales logits before the softmax",
                      "A dial between the two above"],
                     ["**Top-K**", "Zeroes everything outside K candidates",
                      "K too small collapses to greedy"],
                     ["**Beam search**", "Keeps several candidate chains alive at once",
                      "Expensive; can still be bland"],
                 ]},
                {"t": "p", "md": "With top-K our mini-GPT produces plausible English — with "
                                 "**little apparent utility**. That matches the GPT-1 result "
                                 "exactly: the generated output was a curiosity, and the "
                                 "state-of-the-art numbers came from fine-tuned classifiers."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.2.4 · the gap to today",
            "title": "What separates this from a modern LLM",
            "blocks": [
                {"t": "stats", "cols": 2, "items": [
                    {"v": "100×", "l": "more parameters needed"},
                    {"v": "1,000×", "l": "more training steps needed"},
                ]},
                {"t": "lead", "md": "And that is the entire gap. **The training recipe we just "
                                    "used is the exact blueprint everyone training LLMs uses "
                                    "today.**"},
                {"t": "p", "md": "The only missing pieces are a very large compute budget and "
                                 "some tricks for training across multiple machines — which "
                                 "chapter 18 covers. If we spent it, we would see the same leaps "
                                 "in quality OpenAI observed."},
            ],
            "notes": "This is the slide that reframes the whole chapter for a professional "
                     "audience: the barrier to building a frontier model is capital and "
                     "infrastructure, not undisclosed algorithms.",
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "04", "title": "Using a pretrained LLM",
         "lead": "A billion parameters, an instruction dataset, and a memory problem."},

        {
            "type": "slide",
            "kicker": "Section 16.3",
            "title": "Why almost nobody pretrains",
            "blocks": [
                {"t": "p", "md": "Given how prohibitively expensive pretraining is, most of the "
                                 "industry has centred on using models from a **short list of "
                                 "companies**. The concern is not only cost."},
                {"t": "stats", "cols": 3, "items": [
                    {"v": "1.3 million kWh", "l": "estimated to train Llama 2"},
                    {"v": "45,000", "l": "American households' daily power"},
                    {"v": "smaller than GPT-3", "l": "and this is the cheap case"},
                ]},
                {"t": "band", "md": "Generative model training is now a **large percentage of "
                                    "total data-centre power consumption** at big technology "
                                    "companies. If every organisation using an LLM pretrained "
                                    "its own, the energy use would be a noticeable percentage of "
                                    "==global consumption==.", "style": "rose"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.1 · listing 16.11",
            "title": "Loading Gemma 3, one billion parameters",
            "blocks": [
                {"t": "p", "md": "We use the smallest Gemma 3 variant — almost exactly a billion "
                                 "parameters, trained on roughly **2 trillion tokens**, two "
                                 "thousand times more than our mini-GPT."},
                {"t": "code", "lang": "python", "file": "listing 16.11", "src": """gemma_lm = keras_hub.models.CausalLM.from_preset(
    "gemma3_1b",
    dtype="float32",
)"""},
                {"t": "p", "md": "`CausalLM` is a high-level task API, like the `ImageClassifier` "
                                 "and `ImageSegmenter` of earlier chapters. It combines a "
                                 "tokenizer and a correctly initialised architecture into one "
                                 "Keras model, and loads matching weights."},
                {"t": "band", "md": "You must accept the **Gemma Terms of Use** on Kaggle before "
                                    "the weights will download, and authenticate with "
                                    "`kagglehub.login()`. The terms prohibit uses such as "
                                    "generating spam or hate speech — licence terms like this "
                                    "are becoming standard.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.1",
            "title": "Where a billion parameters actually sit",
            "blocks": [
                {"t": "out", "src": """>>> gemma_lm.summary()
Preprocessor: "gemma3_causal_lm_preprocessor"
│ gemma3_tokenizer (Gemma3Tokenizer)  │  Vocab size: 262,144 │

Model: "gemma3_causal_lm"
│ padding_mask (InputLayer)  │ (None, None)          │           0 │
│ token_ids (InputLayer)     │ (None, None)          │           0 │
│ gemma3_backbone            │ (None, None, 1152)    │ 999,885,952 │
│ token_embedding            │ (None, None, 262144)  │ 301,989,888 │
│  (ReversibleEmbedding)     │                       │             │
 Total params: 999,885,952 (3.72 GB)"""},
                {"t": "p", "md": "Two things worth reading closely. The vocabulary is **262,144** "
                                 "terms, eight times ours. And `ReversibleEmbedding` is the "
                                 "**tied embedding** we built by hand — 302 million of the "
                                 "billion parameters, counted once because input and output "
                                 "share them."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.1",
            "title": "It is a fancy autocomplete for the internet",
            "blocks": [
                {"t": "p", "md": "`CausalLM` provides `generate()`, compilable with the sampling "
                                 "strategies we just built."},
                {"t": "out", "src": """>>> gemma_lm.compile(sampler="greedy")
>>> gemma_lm.generate("A piece of advice", max_length=40)
A piece of advice from a former student of mine:
<blockquote>"I'm not sure if you've heard of it, but I've been told that the
best way to learn

>>> gemma_lm.generate("How can I make brownies?", max_length=40)
How can I make brownies?
[User 0001]
I'm trying to make brownies for my son's birthday party. I've never made
brownies before."""},
                {"t": "p", "md": "Far more coherent than mini-GPT — and **still not useful**. "
                                 "Asked how to make brownies, it wrote the *forum post asking "
                                 "the question*, because that is a likely continuation in "
                                 "crawled web text."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.1 · prompting",
            "title": "Change the prompt, change which part of the distribution you visit",
            "blocks": [
                {"t": "p", "md": "One way to fix the output is to prompt with a longer input that "
                                 "makes the desired continuation the likely one."},
                {"t": "out", "src": """>>> gemma_lm.generate(
>>>     "The following brownie recipe is easy to make in just a few "
>>>     "steps.\\n\\nYou can start by",
>>>     max_length=40,
>>> )
The following brownie recipe is easy to make in just a few steps.

You can start by melting the butter and sugar in a saucepan over medium heat.
Then add the eggs and vanilla extract"""},
                {"t": "band", "md": "It is tempting to imagine the model *interpreting* the "
                                    "prompt conversationally. **Nothing of the sort is going "
                                    "on.** We constructed a prompt for which an actual recipe is "
                                    "a more likely continuation than someone asking for help."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.1 · the honest assessment",
            "title": "Prompt engineering is useful and hard to control",
            "blocks": [
                {"t": "p", "md": "You can go much further: prompt with natural-language "
                                 "instructions about the role the model should fill "
                                 "(*\"You are a large language model that gives short, helpful "
                                 "answers\"*), or with a long list of topics to avoid."},
                {"t": "quote", "md": "If this all sounds a bit hand-wavy and hard to control, "
                                     "**that's a good assessment.** Attempting to visit different "
                                     "parts of a model's distribution through prompting is often "
                                     "useful, but predicting how a model will respond to a given "
                                     "prompt is very difficult.",
                 "cite": "Section 16.3.1"},
                {"t": "p", "md": "Treat prompts as **empirical artefacts**: version them, test "
                                 "them against a fixed evaluation set, and expect them to break "
                                 "when the model behind them changes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.1 · hallucination",
            "title": "There is always a most-likely next token",
            "blocks": [
                {"t": "p", "md": "A model will always say **something**. Finding regions of the "
                                 "distribution with no grounding in fact is easy:"},
                {"t": "out", "src": """>>> gemma_lm.generate(
>>>     "Tell me about the 542nd president of the United States.",
>>>     max_length=40,
>>> )
Tell me about the 542nd president of the United States.
The 542nd president of the United States was James A. Garfield."""},
                {"t": "p", "md": "Utter nonsense — and the model could not find a **more likely** "
                                 "way to complete the prompt. There is no mechanism by which it "
                                 "could decline; declining is itself just another continuation, "
                                 "and one this model was never trained to prefer."},
                {"t": "band", "md": "Hallucination and uncontrollable output are **fundamental** "
                                    "problems with language models. If there is a silver bullet, "
                                    "==we have yet to find it==.", "style": "rose"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.2",
            "title": "Instruction fine-tuning: bend the output, do not relearn the language",
            "blocks": [
                {"t": "p", "md": "Feed the model input/output pairs — a user instruction followed "
                                 "by a response — combined into a single sequence, with markers "
                                 "so it is clear where each ends."},
                {"t": "p", "md": "Then train with the **same next-token loss** used for "
                                 "pretraining. The precise markup does not matter, as long as it "
                                 "is consistent."},
                {"t": "band", "md": "We are not learning a latent space for language here — that "
                                    "was done over trillions of tokens. We are ==nudging the "
                                    "learned representation== to control the tone and content of "
                                    "the output."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.2 · listing 16.12",
            "title": "Dolly: 15,000 handwritten instruction-response pairs",
            "blocks": [
                {"t": "p", "md": "Databricks employees contributed 15,000 instructions with "
                                 "handwritten responses."},
                {"t": "code", "lang": "python", "file": "listing 16.12", "src": """import json

PROMPT_TEMPLATE = "[instruction]\\n{}[end]\\n[response]\\n"
RESPONSE_TEMPLATE = "{}[end]"

dataset_path = keras.utils.get_file(
    origin=(
        "https://hf.co/datasets/databricks/databricks-dolly-15k/"
        "resolve/main/databricks-dolly-15k.jsonl"
    ),
)

data = {"prompts": [], "responses": []}
with open(dataset_path) as file:
    for line in file:
        features = json.loads(line)
        if features["context"]:
            continue
        data["prompts"].append(PROMPT_TEMPLATE.format(features["instruction"]))
        data["responses"].append(RESPONSE_TEMPLATE.format(features["response"]))"""},
                {"t": "p", "md": "Examples carrying extra **context** are discarded here — "
                                 "those are the RAG-shaped ones, which return later."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.2",
            "title": "The template gives the examples a predictable shape",
            "blocks": [
                {"t": "out", "src": """>>> data["prompts"][0]
[instruction]
Which is a species of fish? Tope or Rope[end]
[response]

>>> data["responses"][0]
Tope[end]"""},
                {"t": "p", "md": "Gemma is not a sequence-to-sequence model like our translator. "
                                 "But by training on prompts with this structure and generating "
                                 "only what follows the `[response]` marker, we can **use it in "
                                 "a sequence-to-sequence setting**."},
                {"t": "code", "lang": "python", "src": """ds = tf.data.Dataset.from_tensor_slices(data).shuffle(2000).batch(2)
val_ds = ds.take(100)
train_ds = ds.skip(100)"""},
                {"t": "p", "md": "Batch size **2**. That number is about to become important."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.2",
            "title": "Inside the preprocessor",
            "blocks": [
                {"t": "p", "md": "`CausalLM` wraps two objects: a **preprocessor** layer and a "
                                 "**backbone** model. Preprocessing is automatic inside `fit()` "
                                 "and `predict()`, but running it by hand shows what it does."},
                {"t": "out", "src": """>>> preprocessor = gemma_lm.preprocessor
>>> preprocessor.sequence_length = 512
>>> batch = next(iter(train_ds))
>>> x, y, sample_weight = preprocessor(batch)
>>> x["token_ids"].shape
(2, 512)
>>> x["padding_mask"].shape
(2, 512)
>>> y.shape
(2, 512)
>>> sample_weight.shape
(2, 512)"""},
                {"t": "p", "md": "The padding mask tracks which inputs are padded zeros. The "
                                 "`sample_weight` tensor restricts the loss to **response "
                                 "tokens** — we do not care about loss on a fixed user prompt, "
                                 "and certainly not on padding."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.2",
            "title": "It is the same language-model setup underneath",
            "blocks": [
                {"t": "p", "md": "Print the token IDs beside the labels and the offset-by-one "
                                 "pattern from chapter 15 is visible unchanged."},
                {"t": "out", "src": """>>> x["token_ids"][0, :5], y[0, :5]
(Array([     2, 77074, 22768, 236842,    107], dtype=int32),
 Array([ 77074, 22768, 236842,    107,  24249], dtype=int32))"""},
                {"t": "p", "md": "Each label is the next token value. **Instruction tuning is "
                                 "not a new objective** — it is the pretraining objective, run "
                                 "on carefully chosen data with the loss masked to the parts we "
                                 "care about."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3",
            "title": "Why fit() would run out of memory right now",
            "blocks": [
                {"t": "p", "md": "We loaded the model and ran generation without trouble. So why "
                                 "would training crash on a 16 GB GPU?"},
                {"t": "table",
                 "head": ["What has to be in memory", "Size"],
                 "widths": [56, 44],
                 "rows": [
                     ["Model weights", "**3.7 GB**"],
                     ["Adam: gradients, velocity, momentum — 3 floats per parameter",
                      "**~11 GB**"],
                     ["Intermediate values in the forward pass", "a few GB"],
                     ["**Total**", "**over 16 GB**"],
                 ]},
                {"t": "band", "md": "This is the common shape of LLM training: because parameter "
                                    "counts are so large, **GPU throughput is a secondary "
                                    "concern to fitting the model in accelerator memory at "
                                    "all**.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3",
            "title": "Freezing saves optimizer state, not just gradients",
            "blocks": [
                {"t": "p", "md": "Earlier chapters froze parts of a model during fine-tuning. "
                                 "What went unmentioned: **frozen parameters need no optimizer "
                                 "variables at all**, because they never update. That is where "
                                 "the memory goes."},
                {"t": "p", "md": "Researchers have experimented extensively with which parameters "
                                 "to leave unfrozen in a Transformer. The answer, perhaps "
                                 "intuitively, is the ones in the **attention mechanism**."},
                {"t": "p", "md": "But the attention layers still hold hundreds of millions of "
                                 "parameters. ==Can we do better?=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3 · LoRA",
            "title": "Freeze the kernel, learn a low-rank correction",
            "blocks": [
                {"t": "p", "md": "In 2021 researchers at Microsoft proposed **LoRA** — Low-Rank "
                                 "Adaptation — specifically for this memory problem. Start from "
                                 "an ordinary linear projection:"},
                {"t": "code", "lang": "python", "src": """class Linear(keras.Layer):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.kernel = self.add_weight(shape=(input_dim, output_dim))

    def call(self, inputs):
        return ops.matmul(inputs, self.kernel)"""},
                {"t": "p", "md": "LoRA freezes `kernel` and adds a **low-rank decomposition** "
                                 "of the update alongside it: two matrices projecting down to "
                                 "an inner rank and back out."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3 · LoRA",
            "title": "Alpha and beta, and a rank in between",
            "blocks": [
                {"t": "p", "md": "Three weights instead of one."},
                {"t": "code", "lang": "python", "src": """class LoraLinear(keras.Layer):
    def __init__(self, input_dim, output_dim, rank):
        super().__init__()
        self.kernel = self.add_weight(
            shape=(input_dim, output_dim), trainable=False
        )
        self.alpha = self.add_weight(shape=(input_dim, rank))
        self.beta = self.add_weight(shape=(rank, output_dim))

    def call(self, inputs):
        frozen = ops.matmul(inputs, self.kernel)
        update = ops.matmul(ops.matmul(inputs, self.alpha), self.beta)
        return frozen + update"""},
                {"t": "mmd", "id": "ch16-lora", "src": MMD_LORA,
                 "cap": "Figure 16.4 — the low-rank decomposition holds far fewer parameters "
                        "than the kernel it corrects."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3 · the arithmetic",
            "title": "Four million parameters become thirty-two thousand",
            "blocks": [
                {"t": "stats", "cols": 3, "items": [
                    {"v": "2048 × 2048", "l": "kernel shape"},
                    {"v": "4,194,304", "l": "frozen parameters"},
                    {"v": "32,768", "l": "trainable, at rank 8"},
                ]},
                {"t": "p", "md": "The update does **not** have the expressive power of the "
                                 "original kernel — at the narrow middle, the entire update must "
                                 "pass through eight floats."},
                {"t": "band", "md": "That is the bet, and it holds: **during fine-tuning you no "
                                    "longer need the expressive power you needed during "
                                    "pretraining.** The representation is already built; you are "
                                    "only steering it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3 · listing 16.13",
            "title": "In KerasHub it is one line",
            "blocks": [
                {"t": "p", "md": "The LoRA authors suggest freezing the entire Transformer and "
                                 "adding LoRA weights only to the **query and key** projections "
                                 "in attention."},
                {"t": "code", "lang": "python", "file": "listing 16.13", "src": """gemma_lm.backbone.enable_lora(rank=8)"""},
                {"t": "p", "md": "The same thing written out layer by layer, which is what you "
                                 "would edit to add trainable parameters elsewhere:"},
                {"t": "code", "lang": "python", "file": "the verbose equivalent", "src": """gemma_lm.backbone.trainable = False
for i in range(gemma_lm.backbone.num_layers):
    layer = gemma_lm.backbone.get_layer(f"decoder_block_{i}")
    layer.attention.key_dense.trainable = True
    layer.attention.key_dense.enable_lora(rank=8)
    layer.attention.query_dense.trainable = True
    layer.attention.query_dense.enable_lora(rank=8)"""},
                {"t": "p", "md": "Written out this way you can see the two decisions the "
                                 "one-liner makes for you: **which layers** get LoRA, and at "
                                 "**what rank**. Adding it to the value projection, or to only "
                                 "the later blocks, is a one-line change from here."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3",
            "title": "A thousandfold cut in trainable parameters",
            "blocks": [
                {"t": "out", "src": """>>> gemma_lm.summary()
 Total params:         1,001,190,528 (3.73 GB)
 Trainable params:         1,304,576 (4.98 MB)
 Non-trainable params:   999,885,952 (3.72 GB)"""},
                {"t": "p", "md": "The weights still occupy 3.7 GB. But the **trainable** "
                                 "parameters are now 5 MB — which takes the optimizer state from "
                                 "many gigabytes down to megabytes."},
                {"t": "p", "md": "Note that total parameters went *up* slightly, from 999.9 M to "
                                 "1,001.2 M: the alpha and beta matrices are new weights. "
                                 "**LoRA adds parameters to the model and removes them from the "
                                 "optimizer** — and the optimizer was the problem."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3 · listing 16.14",
            "title": "Now the fine-tuning fits",
            "blocks": [
                {"t": "p", "md": "One epoch over roughly 7,000 instruction pairs, at the same "
                                 "small learning rate discipline used for RoBERTa in chapter 15."},
                {"t": "code", "lang": "python", "file": "listing 16.14", "src": """gemma_lm.compile(
    loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    optimizer=keras.optimizers.Adam(5e-5),
    weighted_metrics=[keras.metrics.SparseCategoricalAccuracy()],
)
gemma_lm.fit(train_ds, validation_data=val_ds, epochs=1)"""},
                {"t": "p", "md": "We reach **55%** accuracy at guessing the next word of the "
                                 "response, against 36% for mini-GPT. `weighted_metrics` is what "
                                 "makes the `sample_weight` mask reach the metric, so the score "
                                 "is over response tokens only."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3 · the result",
            "title": "It answers questions now",
            "blocks": [
                {"t": "out", "src": """>>> gemma_lm.generate(
...     "[instruction]\\nWhat is a proper noun?[end]\\n[response]\\n",
...     max_length=512,
... )
[instruction]
What is a proper noun?[end]
[response]
A proper noun is a word that refers to a specific person, place, or thing.
Proper nouns are usually capitalized and are used to identify specific
individuals, places, or things. Proper nouns are often used in formal writing
and are often used in titles, such as "The White House" or "The Eiffel
Tower."[end]"""},
                {"t": "p", "md": "Much better. The model now **responds** to a question rather "
                                 "than carrying on the thought of the prompt text — and it "
                                 "emits `[end]` when it is finished, because the training data "
                                 "taught it where responses stop."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.3.3 · the honest test",
            "title": "Have we solved hallucination? Not at all.",
            "blocks": [
                {"t": "out", "src": """>>> gemma_lm.generate(
...     "[instruction]\\nWho is the 542nd president of the United States?[end]\\n"
...     "[response]\\n",
...     max_length=512,
... )
[instruction]
Who is the 542nd president of the United States?[end]
[response]
The 542nd president of the United States was James A. Garfield.[end]"""},
                {"t": "p", "md": "Identical nonsense, now delivered in a helpful tone. "
                                 "**Instruction tuning changed the format of the answer, not its "
                                 "relationship to truth.**"},
                {"t": "band", "md": "One thing that helps: train on many instruction/response "
                                    "pairs where the desired response is *\"I don't know\"* or "
                                    "*\"As a language model, I cannot help you with that\"*. This "
                                    "teaches the model to avoid whole topics where it would "
                                    "answer badly — ==a behaviour, not an understanding==.",
                 "style": "amber"},
            ],
            "notes": "For a professional audience this is the slide that should govern any "
                     "deployment decision. Fluency and helpfulness are trainable. Correctness "
                     "is not, by this mechanism.",
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "05", "title": "Going further with LLMs",
         "lead": "RLHF, multimodality, retrieval, and models that show their working."},

        {
            "type": "slide",
            "kicker": "Section 16.4.1",
            "title": "Handwritten data has a ceiling, and it is human",
            "blocks": [
                {"t": "p", "md": "What we just did is called **supervised fine-tuning**: we "
                                 "curated, by hand, a list of prompts and responses we wanted."},
                {"t": "bullets", "items": [
                    "Manually written examples are **slow and expensive** to come by, and will "
                    "almost always become the bottleneck.",
                    "The approach is limited by the **human performance ceiling** on the task. "
                    "To beat human performance, we cannot supervise with human-written output.",
                ]},
                {"t": "p", "md": "The real thing to optimise is our **preference** for some "
                                 "responses over others. With a large enough sample of people "
                                 "this is perfectly well defined — the difficulty is translating "
                                 "*our preferences* into a loss function. That is what RLHF "
                                 "attempts."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.1",
            "title": "RLHF in five steps",
            "blocks": [
                {"t": "mmd", "id": "ch16-rlhf", "src": MMD_RLHF,
                 "cap": "The reward model is a proxy for human preference — a smaller "
                        "Transformer that reads a sequence and outputs one float."},
                {"t": "p", "md": "Responses to be ranked may be handwritten, generated by the "
                                 "model, or even written by other chatbots. Collecting rankings "
                                 "is expensive and slow — but **still faster than writing every "
                                 "desired response by hand**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.1 · listing 16.15",
            "title": "The simplest possible RLHF algorithm",
            "blocks": [
                {"t": "p", "md": "Do not be intimidated by *reinforcement learning*: it refers to "
                                 "any setup where a model learns by making predictions "
                                 "(**actions**) and receiving feedback (**rewards**). The "
                                 "model's own predictions become its training data."},
                {"t": "code", "lang": "python", "file": "listing 16.15", "src": """for prompts in dataset:
    responses = model.generate(prompts)
    rewards = reward_model.predict(responses)
    good_responses = []
    for response, score in zip(responses, rewards):
        if score > cutoff:
            good_responses.append(response)
    model.fit(good_responses)"""},
                {"t": "p", "md": "In practice you would **not discard** the bad responses — a "
                                 "bad response is a good signal about what not to do — and you "
                                 "would use specialised gradient updates over all responses. "
                                 "OpenAI used this setup to go from GPT-3's pretrained "
                                 "parameters to the first ChatGPT."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.1 · listing 16.16",
            "title": "An instruction-tuned checkpoint, four times larger",
            "blocks": [
                {"t": "p", "md": "Companies releasing pretrained models normally also release "
                                 "specialised **instruction-tuned** versions. Let us load one — "
                                 "4 billion parameters, the largest model in this book."},
                {"t": "code", "lang": "python", "file": "listing 16.16", "src": """gemma_lm = keras_hub.models.CausalLM.from_preset(
    "gemma3_instruct_4b",
    dtype="bfloat16",
)"""},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "float32 for training", "style": "",
                     "p": "4 bytes per parameter. 32-bit floats represent very small values, "
                          "which helps keep training **gradients stable**."},
                    {"ico": "💾", "h": "bfloat16 for inference", "style": "accent",
                     "p": "2 bytes per parameter. No training here, so no gradient-stability "
                          "concern — and **many gigabytes saved**."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.1",
            "title": "The template must match what the tuning used",
            "blocks": [
                {"t": "p", "md": "This checkpoint has its own prompt format. Again the exact text "
                                 "does not matter — **matching** it does."},
                {"t": "code", "lang": "python", "src": """PROMPT_TEMPLATE = (
    "<start_of_turn>user\\n"
    "{}<end_of_turn>\\n"
    "<start_of_turn>model\\n"
)"""},
                {"t": "out", "src": """>>> prompt = "Why can't you assign values in Jax tensors? Be brief!"
>>> gemma_lm.generate(PROMPT_TEMPLATE.format(prompt), max_length=512)
<start_of_turn>model
Jax tensors are designed for efficient automatic differentiation. Directly
assigning values disrupts this process, making it difficult to track gradients
correctly. Instead, Jax uses operations to modify tensor values, preserving the
differentiation pipeline.<end_of_turn>"""},
                {"t": "p", "md": "Pretrained on **14 trillion tokens**, then extensively tuned — "
                                 "supervised fine-tuning, RLHF, and distillation from a larger "
                                 "*teacher* model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.1 · the same trick question",
            "title": "It refuses the bait — and then invents the date",
            "blocks": [
                {"t": "out", "src": """>>> prompt = "Who is the 542nd president of the United States?"
>>> gemma_lm.generate(PROMPT_TEMPLATE.format(prompt), max_length=512)
<start_of_turn>model
This is a trick question! As of today, November 2, 2023, the United States has
only had 46 presidents. There hasn't been a 542nd president yet.
You're playing with a very large number!<end_of_turn>"""},
                {"t": "p", "md": "This is **not a new modelling technique**. It is the result of "
                                 "extensive training on trick questions like this one, with "
                                 "responses like this one."},
                {"t": "band", "md": "And look closely: having refused to hallucinate a president, "
                                    "the model **made up today's date**. Removing hallucinations "
                                    "is ==whack-a-mole==, and this example is the demonstration.",
                 "style": "rose"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.2",
            "title": "Multimodality is a sequence problem",
            "blocks": [
                {"t": "lead", "md": "The Transformer is not a text-specific model. It is a highly "
                                    "effective model for learning patterns in **sequence data**."},
                {"t": "p", "md": "So if we can coerce another data type into a sequence "
                                 "representation, we can feed it to a Transformer and train on "
                                 "it. That is the whole idea."},
                {"t": "mmd", "id": "ch16-multimodal", "src": MMD_MULTIMODAL,
                 "cap": "Figure 16.6 — hard text tokens and soft image tokens spliced into one "
                        "sequence."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.2 · hard and soft tokens",
            "title": "An image becomes 256 tokens that were never in a vocabulary",
            "blocks": [
                {"t": "p", "md": "The Gemma model we just loaded carries a separate "
                                 "**420-million-parameter image encoder**. It cuts an input image "
                                 "into 256 patches and encodes each as a vector of the same "
                                 "dimensionality as Gemma's hidden state."},
                {"t": "table",
                 "head": ["", "Hard tokens", "Soft tokens"],
                 "widths": [26, 37, 37],
                 "rows": [
                     ["Source", "A token ID", "The vision encoder's output"],
                     ["Possible values", "One row of the embedding matrix",
                      "**Any vector at all**"],
                     ["Count here", "As many as the text has", "256 per image"],
                     ["Loss", "Trained to predict them", "Loss is **zeroed** at these positions"],
                 ]},
                {"t": "p", "md": "Each image embeds as a **(256, 2560)** sequence, spliced into "
                                 "the text sequence after the token embedding layer."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.2",
            "title": "Asking questions about a picture",
            "blocks": [
                {"t": "p", "md": "The prompt is now a dictionary with two keys, and the "
                                 "preprocessor is told how many images to expect."},
                {"t": "code", "lang": "python", "src": """gemma_lm.preprocessor.max_images_per_prompt = 1
gemma_lm.preprocessor.sequence_length = 512

prompt = "What is going on in this image? Be concise!<start_of_image>"
gemma_lm.generate({
    "prompts": PROMPT_TEMPLATE.format(prompt),
    "images": [image],
})"""},
                {"t": "out", "src": """<start_of_turn>model
A snake wearing glasses is sitting in a leather armchair, surrounded by a large
bookshelf, and reading a book. It's a whimsical, slightly surreal image.
<end_of_turn>"""},
                {"t": "p", "md": "The special token `<start_of_image>` is expanded into 256 "
                                 "placeholder positions, which are then **replaced** by the soft "
                                 "tokens from the vision encoder."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.2 · sidebar",
            "title": "Foundation models",
            "blocks": [
                {"t": "p", "md": "Once a model handles images and audio, *large language model* "
                                 "becomes misleading. The umbrella term is **foundation model**: "
                                 "any model trained on broad data, generally with "
                                 "self-supervision at scale, that can be fine-tuned to a wide "
                                 "range of downstream tasks."},
                {"t": "mmd", "id": "ch16-foundation", "src": MMD_FOUNDATION,
                 "cap": "The hallmarks: a self-supervised reconstruction loss, and no "
                        "specialisation to a single task."},
                {"t": "p", "md": "This is a **striking and recent shift**. Rather than training "
                                 "from scratch on your own dataset, you are often better off "
                                 "getting a rich representation from a foundation model and "
                                 "specialising it — with the downside of running billions of "
                                 "parameters, which is ==hardly a fit for every application==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.3",
            "title": "Two reasons an LLM is not a search engine",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🤥", "h": "It makes things up", "style": "bad",
                     "p": "False *facts* that were not in the training data but could be "
                          "interpolated from it. This ranges from **misleading to dangerous**."},
                    {"ico": "📅", "h": "Its knowledge has a cutoff", "style": "bad",
                     "p": "At best, the date it was pretrained. Training is expensive and cannot "
                          "run continuously, so knowledge of the world just **stops**."},
                ]},
                {"t": "p", "md": "Nobody wants a search engine that can only tell you about "
                                 "things that happened six months ago. But if we treat the LLM "
                                 "as ==conversational software== that can handle any sequence "
                                 "data in a prompt, we can use it as the **interface** to "
                                 "information retrieved by more traditional search."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.3 · RAG",
            "title": "Retrieve first, then generate",
            "blocks": [
                {"t": "p", "md": "RAG takes a user question, runs a query to pull in additional "
                                 "text context — from a database, a search engine, anything — and "
                                 "puts that context **straight into the prompt**."},
                {"t": "out", "src": """Use the following pieces of context to answer the question.

Question: What are some good ways to improve sleep?

Context: {text from a medical journal on improving sleep}

Answer:"""},
                {"t": "mmd", "id": "ch16-rag", "src": MMD_RAG,
                 "cap": "A vector database keys documents by their embeddings and returns the "
                        "nearest ones to the query embedding."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.3 · what RAG buys",
            "title": "Three problems it addresses, and one it does not",
            "blocks": [
                {"t": "steps", "items": [
                    "It gives an obvious way to **work around the cutoff date** of the model.",
                    "It lets the model access **private data** — a company can use a "
                    "publicly-trained LLM as an interface to information it holds internally.",
                    "It helps **factually ground** the model: an LLM is much less likely to "
                    "invent facts on a topic when correct context sits in the prompt.",
                ]},
                {"t": "band", "md": "There is **no silver bullet that stops hallucination "
                                    "entirely.** RAG makes it less likely on topics you retrieved "
                                    "context for. It does nothing for topics you did not.",
                 "style": "rose"},
                {"t": "p", "md": "One pleasing detail: the vector database's *query*, *key*, and "
                                 "*value* vocabulary is not an accident — attention borrowed "
                                 "those terms **from database systems** in the first place."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.4",
            "title": "Grade-school maths defied progress for years",
            "blocks": [
                {"t": "p", "md": "For years LLMs were abysmal at maths problems and logic "
                                 "puzzles. A model might answer a problem from its training data "
                                 "perfectly — substitute a few names or numbers and it became "
                                 "evident it had **no grasp of what it was solving**."},
                {"t": "p", "md": "For most NLP problems the recipe was easy: more data, better "
                                 "benchmark score. Grade-school word problems did not respond to "
                                 "it."},
                {"t": "quote", "md": "In 2023 researchers at Google noticed that prompting the "
                                     "model with a few examples of *showing your work* made the "
                                     "model do the same — and that by attending to its own "
                                     "written-out steps, it reached correct solutions far more "
                                     "often. They called it **chain-of-thought prompting**.",
                 "cite": "Section 16.4.4"},
                {"t": "p", "md": "Another group found the examples were not even necessary: "
                                 "prompting with *\"Let's think step by step\"* was enough."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.4 · training it in",
            "title": "Chain-of-thought fine-tuning, in five steps",
            "blocks": [
                {"t": "p", "md": "Models like OpenAI's o1 and DeepSeek's r1 made headlines by "
                                 "training a model to *think out loud*. The approach is very "
                                 "close to RLHF."},
                {"t": "steps", "items": [
                    "Collect basic maths and reasoning problems with their desired answers.",
                    "Generate, **with randomness**, a number of responses to each.",
                    "Find responses with a correct answer by **string parsing** — prompt the "
                    "model to mark its final answer with a specific token.",
                    "Run supervised fine-tuning on the correct responses, **including all the "
                    "intermediate output**.",
                    "Repeat.",
                ]},
                {"t": "p", "md": "The answer check acts as the **environment**; the generated "
                                 "outputs are the **actions**. In practice you would use a more "
                                 "complex gradient step that learns from incorrect responses too."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.4 · observed",
            "title": "The same prompt, twice, with random sampling",
            "blocks": [
                {"t": "p", "md": "*Judy wrote a 2-page letter to 3 friends twice a week for 3 "
                                 "months. How many letters did she write?*"},
                {"t": "out", "src": """FIRST ATTEMPT
* Letters per week:  3 friends * 2 letters/week = 6 letters/week
* Letters per month: 6 letters/week * 4 weeks/month = 24 letters/month
* Letters in 3 months: 24 letters/month * 3 months = 72 letters
* Total letters: 72 letters * 2 = 144 letters
ANSWER: 144"""},
                {"t": "out", "src": """SECOND ATTEMPT
* Letters per week:  3 friends * 2 letters/week = 6 letters/week
* Letters per month: 6 letters/week * 4 weeks/month = 24 letters/month
* Total letters: 24 letters/month * 3 months = 72 letters
ANSWER: 72"""},
                {"t": "p", "md": "The first attempt got hung up on the **superfluous detail** "
                                 "that each letter has two pages. The second is right. Same "
                                 "model, same prompt, different sample — which is exactly why "
                                 "step 3 of the recipe is *check the answer*."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.4.4",
            "title": "Where else verifiable answers exist",
            "blocks": [
                {"t": "mmd", "id": "ch16-cot", "src": MMD_COT,
                 "cap": "The loop only closes where correctness can be checked automatically."},
                {"t": "p", "md": "The same idea applies wherever a text prompt has an obvious, "
                                 "**verifiable** answer. **Coding** is the important one: prompt "
                                 "the model for code, then actually run it to test the quality "
                                 "of the response."},
                {"t": "p", "md": "One trend is clear across all these domains: as a model learns "
                                 "harder questions, it spends **more and more time showing its "
                                 "work** before answering. Think of it as learning to search over "
                                 "its own potential solutions."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "06", "title": "Where are LLMs heading next?",
         "lead": "More parameters is the obvious answer. It is not quite the right one."},

        {
            "type": "slide",
            "kicker": "Section 16.5",
            "title": "A fixed budget buys flops, and you must choose how to spend them",
            "blocks": [
                {"t": "p", "md": "Given a fixed pretraining budget — say a million dollars — you "
                                 "are buying a fixed number of floating-point operations. You "
                                 "can spend them on **more data**, or on a **bigger model**."},
                {"t": "mmd", "id": "ch16-scaling", "src": MMD_SCALING,
                 "cap": "Recent research found GPT-3 was far too big for the compute it was "
                        "given."},
                {"t": "p", "md": "Training a **smaller model on more data** would have produced "
                                 "better performance. So model sizes have trended flatter while "
                                 "data sizes have trended up."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.5",
            "title": "Two reasons parameter counts stopped climbing",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📐", "h": "GPT-3 was undertrained", "style": "accent",
                     "p": "175 billion parameters against roughly half a trillion tokens. We now "
                          "know the balance was wrong."},
                    {"ico": "💰", "h": "Deployment cost", "style": "accent",
                     "p": "It is often worth sacrificing performance for a smaller model that "
                          "fits cheaper hardware. **A really good model does not help if it is "
                          "prohibitively expensive to run.**"},
                ]},
                {"t": "p", "md": "This does **not** mean scaling has stopped. More compute does "
                                 "generally give better performance, and we have yet to see any "
                                 "sign of an asymptote where next-token prediction levels off. "
                                 "Billions of dollars continue to go into finding out what "
                                 "emerges."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.5 · the supply problem",
            "title": "We are starting to run out of pretraining data",
            "blocks": [
                {"t": "p", "md": "Technology companies are having trouble finding more "
                                 "high-quality, public, **human-written** content to throw at "
                                 "pretraining."},
                {"t": "band", "md": "Models are starting to *eat their own tail* — training on a "
                                    "significant portion of content created by other LLMs, which "
                                    "brings a whole other set of concerns.", "style": "rose"},
                {"t": "p", "md": "This is one reason reinforcement learning is drawing so much "
                                 "attention. **If you can build a difficult, self-contained "
                                 "environment that generates new problems, you can keep training "
                                 "on the model's own output** — with no need to scrounge the web "
                                 "for more quality text."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 16.5 · the fundamental problem",
            "title": "None of this is a silver bullet",
            "blocks": [
                {"t": "quote", "md": "At the end of the day, the fundamental problem remains that "
                                     "LLMs are **wildly inefficient at learning compared to "
                                     "humans**. Model capabilities only come from training on "
                                     "many orders of magnitude more text than people will read "
                                     "in their lifetimes.",
                 "cite": "Section 16.5"},
                {"t": "p", "md": "As scaling continues, so will more fundamental research into "
                                 "models that learn quickly from limited data."},
                {"t": "p", "md": "Still — LLMs represent the ability to build **fluent natural "
                                 "language interfaces**, and that alone brings a massive shift "
                                 "in what can be accomplished with computing devices. This "
                                 "chapter laid out the basic recipe by which they get there."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Common failure modes",
            "title": "Four ways LLM work goes wrong in practice",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🐌", "h": "Uncompiled or reshaping generation", "style": "bad",
                     "p": "Calling the model directly, or letting the input shape change each "
                          "step, costs **two to three orders of magnitude** in speed. No error "
                          "is raised — only a bill."},
                    {"ico": "📝", "h": "Prompt template mismatch", "style": "bad",
                     "p": "An instruction-tuned checkpoint expects the exact template it was "
                          "tuned with. Use a different one and quality drops sharply, silently."},
                    {"ico": "💥", "h": "Full fine-tuning on a small GPU", "style": "warn",
                     "p": "Adam needs three extra floats per parameter. The model loads and "
                          "generates fine, then `fit()` dies on the first step. Use LoRA."},
                    {"ico": "🎭", "h": "Mistaking fluency for correctness", "style": "warn",
                     "p": "Instruction tuning and RLHF change the **form** of an answer. Neither "
                          "makes it true. Ground with retrieval, and verify where you can."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter (1 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**An LLM is three ingredients**: the Transformer architecture, a language "
                    "modelling task, and a large amount of unlabelled text.",
                    "**GPT is decoder-only** — expressivity traded for an unbounded supply of "
                    "training data, and the data won.",
                    "**Tied embeddings** use one matrix forward at the input and transposed at "
                    "the output, saving a large share of the parameters.",
                    "**Warmup** matters: large Transformers are sensitive to early updates, and "
                    "exploding gradients are the common failure.",
                    "**Sampling is a separate design** from the model. Greedy repeats, random "
                    "wanders, temperature dials between them, top-K rules tokens out.",
                    "**Key-value caching** turns generation from quadratic re-computation into "
                    "one token per step.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter (2 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**Instruction fine-tuning** is the pretraining objective on curated data "
                    "with the loss masked to responses — it bends output, it does not relearn "
                    "language.",
                    "**LoRA** freezes the kernel and learns a low-rank correction, cutting "
                    "trainable parameters a thousandfold and optimizer memory with them.",
                    "**RLHF** replaces handwritten answers with ranked preferences and a reward "
                    "model, which lifts the human performance ceiling.",
                    "**Multimodality is a sequence problem** — encode images as soft tokens and "
                    "splice them into the text sequence.",
                    "**RAG** puts retrieved context in the prompt, addressing the knowledge "
                    "cutoff and private data, and reducing but not removing hallucination.",
                    "**All LLMs hallucinate.** Fluency, helpfulness, and refusal are trainable "
                    "behaviours; truth is not one of them.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "05_instruction_tuning_with_lora.ipynb",
                     "href": "../../course-slides/notebooks/ch16/05_instruction_tuning_with_lora.ipynb"},
                    {"k": "PAPER", "ic": "📄", "v": "Hu et al., LoRA (2021)",
                     "href": "https://arxiv.org/abs/2106.09685"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 17 — Image generation",
                     "href": "../ch17/index.html"},
                ]},
            ],
        },
    ],
}
