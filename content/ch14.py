# -*- coding: utf-8 -*-
"""Chapter 14 — Text classification.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 14
(pp. 381-425), read from the book PDF.

Tokenization from characters to byte-pair encoding, then the pivotal question:
is text a set or a sequence? Bag-of-words, bigrams, RNNs, and pretrained word
embeddings, all measured on the same IMDB benchmark.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_HISTORY = """
flowchart LR
  A["1950s<br/><b>Hand-written rules</b><br/><small>6 rules, 60 sentences,<br/>&quot;solved in five years&quot;</small>"]
  B["1960s - 1980s<br/><b>Rules persist</b><br/><small>no viable alternative,<br/>funding dries up</small>"]
  C["late 1980s<br/><b>Machine learning</b><br/><small>decision trees, then<br/>logistic regression</small>"]
  D["2015 onward<br/><b>Sequence models</b><br/><small>RNNs reborn,<br/>then Transformers</small>"]
  A --> B --> C --> D
"""

MMD_TOKENIZERS = """
flowchart TB
  C["<b>Character level</b><br/>tiny vocabulary<br/>encodes anything<br/><small>but very long sequences</small>"]
  W["<b>Word level</b><br/>short sequences<br/><small>but a huge vocabulary,<br/>and unknown words break it</small>"]
  S["<b>Subword (BPE)</b><br/>short sequences AND<br/>a small vocabulary<br/><small>used by ChatGPT and most<br/>models today</small>"]
  C --> S
  W --> S
"""

MMD_SETSEQ = """
flowchart TB
  Q["How should word order<br/>be represented?"]
  A["<b>Discard it</b><br/>text as an unordered set<br/><small>bag-of-words models</small>"]
  B["<b>Strictly sequential</b><br/>one word at a time<br/><small>recurrent models</small>"]
  C["<b>Hybrid</b><br/>order-agnostic, but with<br/>position injected<br/><small>the Transformer</small>"]
  Q --> A
  Q --> B
  Q --> C
"""

MMD_BOW = """
flowchart LR
  T["&quot;this movie made me cry&quot;"]
  I["Tokenize<br/><code>[0, 1, 3, 0, 5]</code>"]
  S["Discard order<br/><code>{0, 1, 3, 5}</code>"]
  M["Multi-hot<br/><code>[1, 1, 0, 1, 0, 1]</code>"]
  T --> I --> S --> M
"""

MMD_EMBED = """
flowchart TB
  subgraph O["One-hot vectors"]
    direction TB
    O1["Sparse"] --> O2["High-dimensional<br/><small>20,000 dims</small>"] --> O3["Hardcoded"]
    O3 --> O4["<b>All words orthogonal:<br/>&quot;movie&quot; unrelated to &quot;film&quot;</b>"]
  end
  subgraph E["Word embeddings"]
    direction TB
    E1["Dense"] --> E2["Lower-dimensional<br/><small>256 to 1,024 dims</small>"] --> E3["Learned from data"]
    E3 --> E4["<b>Geometry reflects meaning</b>"]
  end
  O ~~~ E
"""

MMD_CBOW = """
flowchart LR
  L["words to the left<br/><small>&quot;sail&quot;, &quot;wave&quot;</small>"] --> G["Guess the<br/>missing word"]
  R["words to the right<br/><small>&quot;mast&quot;</small>"] --> G
  G --> W["&quot;boat&quot;"]
  W -. "slide the window<br/>and repeat" .-> G
"""

MMD_LADDER14 = """
flowchart LR
  B["Bag of words<br/><small>order discarded</small>"]
  G["Bigrams<br/><small>a little local order,<br/>engineered by hand</small>"]
  S["Sequence model<br/><small>order learned<br/>from raw tokens</small>"]
  P["Pretrained embedding<br/><small>+ knowledge from<br/>unlabelled text</small>"]
  B --> G --> S --> P
"""


NB = ["01_tokenizers.ipynb", "02_bag_of_words_and_bigrams.ipynb",
      "03_sequence_models.ipynb", "04_pretraining_an_embedding.ipynb"]

DECK = {
    "id": "ch14",
    "kind": "chapter",
    "number": 14,
    "title": "Text Classification",
    "subtitle": "Tokenization, and the one question every NLP architecture answers "
                "differently: is a sentence a set of words, or a sequence of them?",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 14",
    "source_url": chapter_url(14),
    "duration": "3 hours (2 sessions)",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(14, local_notebooks=NB),
    "objectives": [
        "Explain why natural language is **messy in a way machine languages are not**, "
        "and why rule-based NLP failed.",
        "Compare **character, word, and subword** tokenization, and say what "
        "byte-pair encoding optimises.",
        "State the **set versus sequence** question and place bag-of-words, RNNs, "
        "and Transformers against it.",
        "Build a **bag-of-words** classifier with `TextVectorization`, and extend it "
        "with **bigrams**.",
        "Explain what a **word embedding** is, and why one-hot encoding makes a "
        "false assumption.",
        "**Pretrain** an embedding with an unsupervised task (CBOW), and use it for "
        "classification.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Section 14.1",
            "title": "Why \"natural\" language is a different kind of object",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Machine languages were designed.** An engineer "
                                         "wrote down formal rules first; people used the "
                                         "language once the rule set was complete."},
                    ],
                    [
                        {"t": "p", "md": "**Human language is the reverse.** Usage comes "
                                         "first; rules arise later, are formalised after the "
                                         "fact, and are ==often ignored or broken by its "
                                         "users=="},
                    ],
                ]},
                {"t": "band",
                 "md": "So machine-readable language is highly structured and rigorous, while "
                       "natural language is **messy — ambiguous, chaotic, sprawling, and "
                       "constantly in flux**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.1",
            "title": "The 1954 demo, and the decade it bought",
            "blocks": [
                {"t": "p", "md": "Researchers at IBM and Georgetown showed a system "
                                 "translating Russian into English using **six hardcoded "
                                 "grammar rules** and a lookup table of a couple of hundred "
                                 "entries, on **60 handpicked sentences**."},
                {"t": "band", "style": "amber",
                 "md": "The goal was to attract excitement and funding, and in that sense "
                       "**it was a huge success**. The authors claimed translation would be "
                       "solved within five years. ==Funding poured in for the better part of "
                       "a decade.=="},
            ],
            "notes": "Worth connecting back to chapter 1: the same pattern of a compelling "
                     "demo, an over-confident timeline, and a funding collapse.",
        },

        {
            "type": "slide",
            "kicker": "Section 14.1",
            "title": "…and why it did not generalise",
            "blocks": [
                {"t": "bullets", "items": [
                    "**Words change meaning dramatically depending on context.**",
                    "**Every grammar rule needed countless exceptions.**",
                    "Shining on a few handpicked examples was simple; building a robust system "
                    "that could compete with human translators ==was another matter==.",
                ]},
                {"t": "p", "md": "An influential US report a decade later picked apart the lack "
                                 "of progress, and the funding dried up. Yet handcrafted rules "
                                 "**remained dominant well into the 1990s** — because there "
                                 "was no viable alternative."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.1",
            "title": "The moment it became machine learning",
            "blocks": [
                {"t": "mmd", "id": "ch14-history", "src": MMD_HISTORY,
                 "cap": "Faster computers and more data in the late 1980s changed what was "
                        "possible."},
                {"t": "quote",
                 "md": "When you find yourself building systems that are big piles of ad hoc "
                       "rules … you're likely to start asking, \"Could I use a corpus of data "
                       "to automate the process of finding these rules?\" And just like that, "
                       "you've graduated to doing machine learning.",
                 "cite": "Chollet & Watson, section 14.1"},
            ],
        },

        {"type": "section", "num": "01", "title": "Preparing text data",
         "lead": "Tokenization: from characters to byte-pair encoding."},

        {
            "type": "slide",
            "kicker": "Section 14.2.1 · listing 14.1",
            "title": "The simplest tokenizer, written out",
            "blocks": [
                {"t": "p", "md": "Every tokenizer does the same three things: standardise, "
                                 "split, index. Here they are at character level, which makes "
                                 "the structure easy to see."},
                {"t": "code", "lang": "python", "file": "listing 14.1 — a character-level tokenizer",
                 "src": """class CharTokenizer:
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self.unk_id = vocabulary["[UNK]"]

    def standardize(self, inputs):
        return inputs.lower()

    def split(self, inputs):
        return re.findall(r".", inputs)

    def index(self, tokens):
        return [self.vocabulary.get(t, self.unk_id) for t in tokens]

    def __call__(self, inputs):
        return self.index(self.split(self.standardize(inputs)))"""},
                {"t": "p", "md": "The `[UNK]` fallback is the important detail: **anything "
                                 "outside the vocabulary becomes one shared token**, and how "
                                 "often that happens is a property of the tokenizer's design."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.2.1",
            "title": "Building a vocabulary, and capping it",
            "blocks": [
                {"t": "p", "md": "A tokenizer needs a vocabulary. Rather than mapping every "
                                 "distinct token to an index, it is capped at the most common "
                                 "ones — which is a modelling decision, not a technicality."},
                {"t": "code", "lang": "python", "file": "computing a capped vocabulary",
                 "src": """def compute_vocabulary(text_iterable, max_size, split_fn):
    counts = collections.Counter()
    for text in text_iterable:
        counts.update(split_fn(text.lower()))

    vocabulary = {"[UNK]": 0}                    # index 0 is always the fallback
    for token, _ in counts.most_common(max_size - 1):
        vocabulary[token] = len(vocabulary)
    return vocabulary"""},
                {"t": "band",
                 "md": "Capping the vocabulary is the same **feature selection** move as "
                       "chapter 5's `num_words=10000`: rare tokens carry little signal and "
                       "==invite the spurious correlations chapter 5 warned about=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.2.1",
            "title": "Word level: shorter sequences, a harder vocabulary problem",
            "blocks": [
                {"t": "p", "md": "Splitting on whitespace instead of on characters gives far "
                                 "shorter sequences — and immediately raises two questions the "
                                 "character tokenizer never had."},
                {"t": "code", "lang": "python", "file": "a word-level split",
                 "src": """class WordTokenizer(CharTokenizer):
    def standardize(self, inputs):
        inputs = inputs.lower()
        return "".join(c for c in inputs if c not in string.punctuation)

    def split(self, inputs):
        return re.findall(r"\w+", inputs)"""},
                {"t": "bullets", "items": [
                    "**How large should the vocabulary be?** English has hundreds of thousands "
                    "of word forms.",
                    "**What happens to a word you have never seen?** It becomes `[UNK]`, and "
                    "==all its meaning is gone==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.2.1 – 14.2.2",
            "title": "Three levels, and the trade-off between them",
            "blocks": [
                {"t": "mmd", "id": "ch14-tokenizers", "src": MMD_TOKENIZERS,
                 "cap": "Subword tokenization aims at the best of both."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.2.2",
            "title": "Tokenization as compression",
            "blocks": [
                {"t": "p", "md": "The book reframes the search for a good tokenizer as **the "
                                 "hunt for a good compression of the input**."},
                {"t": "bullets", "items": [
                    "**Shorter tokens** compress the overall length of each example.",
                    "**A smaller vocabulary** reduces the bytes needed to represent each token.",
                    "Achieve both and you feed the model ==short, information-rich sequences==.",
                ]},
                {"t": "band",
                 "md": "That analogy turned out to be powerful: one of the most effective "
                       "tricks of the last decade was **repurposing a 1990s lossless "
                       "compression algorithm — byte-pair encoding — for tokenization**. "
                       "It is used by ==ChatGPT and many other models to this day=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.2.2",
            "title": "How byte-pair encoding builds its vocabulary",
            "blocks": [
                {"t": "p", "md": "Start from characters, then repeatedly merge the most "
                                 "frequent adjacent pair into a new token."},
                {"t": "code", "lang": "python", "file": "the BPE idea, in outline",
                 "src": """# start: every character is a token
#   l o w e r   n e w e s t   w i d e s t

# merge the most frequent pair, repeatedly:
#   "e" + "s" -> "es"        n e w es t   w i d es t
#   "es" + "t" -> "est"      n e w est    w i d est
#   "l" + "o"  -> "lo"       lo w e r

# stop when the vocabulary reaches the target size"""},
                {"t": "band",
                 "md": "Common words end up as **single tokens**; rare words decompose into "
                       "**familiar pieces**. Nothing is ever `[UNK]`, because ==the character "
                       "level is always available as a fallback=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Sets versus sequences",
         "lead": "The pivotal question from which every NLP architecture springs."},

        {
            "type": "slide",
            "kicker": "Section 14.3",
            "title": "Representing a token is easy. Representing order is not.",
            "blocks": [
                {"t": "p", "md": "Individual tokens are **categorical features**, and we know "
                                 "how to handle those. The problematic question is how to "
                                 "encode **the ordering** of tokens."},
                {"t": "band",
                 "md": "Unlike the steps of a timeseries, **words in a sentence have no "
                       "natural, canonical order**. Different languages order similar words "
                       "very differently; within one language you can usually say the same "
                       "thing by reshuffling. ==Order clearly matters, but its relationship "
                       "to meaning is not straightforward.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.3",
            "title": "Three answers, three families of architecture",
            "blocks": [
                {"t": "mmd", "id": "ch14-setseq", "src": MMD_SETSEQ,
                 "cap": "RNNs and Transformers both take order into account, so both are "
                        "called sequence models."},
                {"t": "p", "md": "Historically most early NLP was bag-of-words. Interest in "
                                 "sequence models only rose in **2015**, with the rebirth of "
                                 "RNNs. **Both approaches remain relevant today.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.3.1",
            "title": "The benchmark: raw IMDB this time",
            "blocks": [
                {"t": "p", "md": "Chapters 4 and 5 used a **prevectorised** IMDB. Here the raw "
                                 "text is processed — as you would with any new text problem."},
                {"t": "code", "lang": "python", "file": "listing 14.8 — downloading raw IMDB",
                 "src": """zip_path = keras.utils.get_file(
    origin="https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz",
    fname="imdb",
    extract=True,
)
imdb_extract_dir = pathlib.Path(zip_path) / "aclImdb"

for path in imdb_extract_dir.glob("*/*"):
    if path.is_dir():
        print(path)"""},
                {"t": "out", "src": """aclImdb/train/pos
aclImdb/train/neg
aclImdb/train/unsup
aclImdb/test/pos
aclImdb/test/neg"""},
                {"t": "p", "md": "Note `train/unsup` — 25,000 **unlabelled** reviews. They are "
                                 "ignored at first and become essential in section 14.5.4."},
            ],
        },

        {"type": "section", "num": "03", "title": "Set models",
         "lead": "Throw order away, and see how far that gets you."},

        {
            "type": "slide",
            "kicker": "Section 14.4",
            "title": "Bag of words, in one picture",
            "blocks": [
                {"t": "mmd", "id": "ch14-bow", "src": MMD_BOW,
                 "cap": "Tokenize, discard order, multi-hot encode."},
                {"t": "p", "md": "The idea is simply to **assign a weight to every word**. "
                                 "*terrible* probably indicates a bad review; *riveting* "
                                 "probably indicates a good one."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.4.1 · listing 14.12",
            "title": "TextVectorization does all of it",
            "blocks": [
                {"t": "p", "md": "Keras has a preprocessing layer for this. Like several such "
                                 "layers it has an **`adapt()`** method that learns state — "
                                 "here, the vocabulary — by iterating over a dataset."},
                {"t": "code", "lang": "python", "file": "listing 14.12 — bag-of-words encoding",
                 "src": """from keras import layers

max_tokens = 20_000
text_vectorization = layers.TextVectorization(
    max_tokens=max_tokens,
    split="whitespace",         # word-level vocabulary
    output_mode="multi_hot",    # and multi-hot output, in one layer
)

train_ds_no_labels = train_ds.map(lambda x, y: x)
text_vectorization.adapt(train_ds_no_labels)"""},
                {"t": "band",
                 "md": "**20,000 words is a good starting point** for text classification. "
                       "Note `adapt()` is given the reviews **without labels** — it is "
                       "learning vocabulary, ==not learning the task=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.4.1",
            "title": "The model on top is tiny",
            "blocks": [
                {"t": "p", "md": "Once the text is a 20,000-long multi-hot vector, the "
                                 "classifier is the same kind of small dense network as "
                                 "chapter 4."},
                {"t": "code", "lang": "python", "file": "the bag-of-words classifier",
                 "src": """inputs = keras.Input(shape=(max_tokens,))
x = layers.Dense(16, activation="relu")(inputs)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])"""},
                {"t": "p", "md": "It performs respectably — which is the point. **A model that "
                                 "cannot tell *\"good, not bad\"* from *\"bad, not good\"* "
                                 "still does well on sentiment**, because long reviews carry "
                                 "plenty of unordered evidence."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.4.2",
            "title": "Bigrams: putting a little order back by hand",
            "blocks": [
                {"t": "p", "md": "A bigram is a pair of adjacent words treated as one token. "
                                 "It restores **local** order without any change to the model."},
                {"t": "code", "lang": "python", "file": "listing — bigram encoding",
                 "src": """text_vectorization = layers.TextVectorization(
    ngrams=2,                   # unigrams AND bigrams
    max_tokens=max_tokens,
    output_mode="multi_hot",
)"""},
                {"t": "band",
                 "md": "One argument, and the model improves: *\"not good\"* is now a token in "
                       "its own right. But the approach ==only scales to a local ordering of "
                       "a few words==, and it is feature engineering done by hand."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.4.1",
            "title": "Counts, or presence? A third output mode",
            "blocks": [
                {"t": "p", "md": "`multi_hot` records only whether a word appeared. "
                                 "`TextVectorization` offers two alternatives that weight it."},
                {"t": "table",
                 "head": ["`output_mode`", "What each position holds"],
                 "widths": [24, 76],
                 "rows": [
                     ["`\"multi_hot\"`", "**1 if the word appears**, 0 otherwise."],
                     ["`\"count\"`", "**How many times** it appears."],
                     ["`\"tf_idf\"`", "Its count, **discounted by how common the word is "
                      "across the whole corpus** — so *the* contributes almost nothing and a "
                      "distinctive word contributes a lot."],
                 ]},
                {"t": "band",
                 "md": "TF-IDF is decades older than deep learning and still competitive on "
                       "short texts. It is worth trying before ==anything with a recurrent "
                       "layer in it=="},
            ],
        },

        {"type": "section", "num": "04", "title": "Sequence models",
         "lead": "Stop engineering order. Show the model the raw sequence."},

        {
            "type": "slide",
            "kicker": "Section 14.5",
            "title": "The argument for moving on",
            "blocks": [
                {"t": "p", "md": "The bigram result showed that **sequence information "
                                 "matters**. But it was obtained by manually engineering "
                                 "features, and that approach has a low ceiling."},
                {"t": "band",
                 "md": "As so often in deep learning: rather than building the features "
                       "yourself, **expose the model to the raw word sequence and let it "
                       "learn the positional dependencies** — ==the same argument chapter 1 "
                       "made about feature engineering in general=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5",
            "title": "One wrinkle: batches have to be rectangular",
            "blocks": [
                {"t": "p", "md": "Reviews have different lengths, but a batch must be a "
                                 "rectangular tensor so the computation parallelises on a GPU."},
                {"t": "code", "lang": "python", "file": "padding and truncation",
                 "src": """max_length = 600

text_vectorization = layers.TextVectorization(
    max_tokens=max_tokens,
    output_mode="int",           # integer token IDs, in order
    output_sequence_length=max_length,   # pad or truncate to a fixed length
)"""},
                {"t": "band", "style": "amber",
                 "md": "Padding introduces a new problem the model has to be told about: "
                       "**those zeros are not words**. Getting this wrong means "
                       "==the model spends capacity learning about padding=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.1",
            "title": "A recurrent model on the raw sequence",
            "blocks": [
                {"t": "p", "md": "Chapter 13's machinery applies directly — a bidirectional "
                                 "LSTM, which here **does** help, because both directions of "
                                 "a sentence carry meaning."},
                {"t": "code", "lang": "python", "file": "a sequence model",
                 "src": """inputs = keras.Input(shape=(max_length,), dtype="int32")
x = layers.Embedding(input_dim=max_tokens, output_dim=256, mask_zero=True)(inputs)
x = layers.Bidirectional(layers.LSTM(32))(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)"""},
                {"t": "band",
                 "md": "**`mask_zero=True`** is the answer to the padding problem: it tells "
                       "every downstream layer to ==skip the padded positions entirely=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.1",
            "title": "What the sequence model buys, and what it costs",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📈", "h": "What it buys",
                     "p": "Word order is **learned rather than engineered**, so dependencies "
                          "longer than a bigram become reachable.", "style": "good"},
                    {"ico": "⏱", "h": "What it costs",
                     "p": "Far slower to train than a bag-of-words model, and it needs "
                          "**more data** to justify the extra parameters.", "style": "warn"},
                ]},
                {"t": "band",
                 "md": "The book's standing advice applies: **start with the cheap model**. "
                       "If bag-of-words is close to the sequence model on your data, "
                       "==the sequence model is not earning its cost=="},
            ],
        },

        {"type": "section", "num": "05", "title": "Word embeddings",
         "lead": "One-hot encoding makes an assumption that is plainly false."},

        {
            "type": "slide",
            "kicker": "Section 14.5.2",
            "title": "What one-hot encoding quietly assumes",
            "blocks": [
                {"t": "p", "md": "Choosing one-hot is a **feature engineering decision**: it "
                                 "injects an assumption about the structure of the feature "
                                 "space. One-hot vectors are all **orthogonal to one another** "
                                 "— the tokens are assumed independent."},
                {"t": "band", "style": "rose",
                 "md": "For words that assumption is **clearly wrong**. *\"Movie\"* and "
                       "*\"film\"* are interchangeable in most sentences, so their vectors "
                       "==should be the same vector, or close to it== — not at right angles."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.2",
            "title": "What an embedding is instead",
            "blocks": [
                {"t": "mmd", "id": "ch14-embed", "src": MMD_EMBED,
                 "cap": "Figure 14.3 — sparse, hardcoded, high-dimensional versus dense, "
                        "learned, and lower-dimensional."},
                {"t": "p", "md": "The goal: **the geometric relationship between two word "
                                 "vectors should reflect the semantic relationship between "
                                 "the words**. Related words close, unrelated words far apart."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.2",
            "title": "Directions in the space mean things",
            "blocks": [
                {"t": "p", "md": "Embeddings are not only dense but **structured**, and the "
                                 "structure is learned. The book's toy example places four "
                                 "words on a plane: *cat*, *dog*, *wolf*, *tiger*."},
                {"t": "bullets", "items": [
                    "The same vector takes you from **cat → tiger** and from **dog → wolf** — "
                    "a *from pet to wild animal* direction.",
                    "Another takes you from **dog → cat** and **wolf → tiger** — a *from "
                    "canine to feline* direction.",
                    "In real embedding spaces the classic examples are **gender** and "
                    "**plural** vectors: add *female* to *king* and you get ==*queen*==.",
                ]},
                {"t": "band",
                 "md": "Real word-embedding spaces typically feature **thousands** of such "
                       "interpretable directions."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.3",
            "title": "Is there one ideal embedding space?",
            "blocks": [
                {"t": "band",
                 "md": "The book's answer is careful: **possibly — but we have yet to compute "
                       "anything of the sort.** What is available in practice is an embedding "
                       "learned either ==jointly with your task, or on a large corpus "
                       "beforehand=="},
                {"t": "p", "md": "An `Embedding` layer trained with the classifier learns a "
                                 "space specialised to *this* task. That is often fine — and "
                                 "when labelled data is scarce, it is not."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.3",
            "title": "Choosing the embedding dimension",
            "blocks": [
                {"t": "p", "md": "The `output_dim` of an `Embedding` layer is a capacity "
                                 "decision, and the usual rule from chapter 5 applies in both "
                                 "directions."},
                {"t": "table",
                 "head": ["Dimension", "When it fits"],
                 "widths": [26, 74],
                 "rows": [
                     ["**Too small**", "An information bottleneck — the space cannot separate "
                      "words that mean different things. Chapter 4's 4-unit layer, again."],
                     ["**256 – 1,024**", "Typical for large vocabularies, and the range the "
                      "book works in."],
                     ["**Too large**", "More parameters than the data can constrain; the "
                      "embedding memorises rather than generalises."],
                 ]},
                {"t": "band",
                 "md": "For comparison: one-hot over this vocabulary would be **20,000 "
                       "dimensions**. An embedding ==packs more information into far fewer=="},
            ],
        },

        {"type": "section", "num": "06", "title": "Pretraining",
         "lead": "Where the unlabelled 25,000 reviews finally earn their place."},

        {
            "type": "slide",
            "kicker": "Section 14.5.4",
            "title": "Why pretraining took over NLP",
            "blocks": [
                {"t": "p", "md": "Once you move past small set-based models to sequence models "
                                 "with millions or billions of parameters, text models become "
                                 "**incredibly data-hungry** — and you are usually limited by "
                                 "**how many labelled examples you can find**."},
                {"t": "band",
                 "md": "The idea: **devise an unsupervised task that needs no labels**. "
                       "Pretraining data can be text from a similar domain, or even arbitrary "
                       "text in the right language. It learns general patterns, ==priming the "
                       "model before you specialise it=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.4",
            "title": "CBOW: guess the word from its neighbours",
            "blocks": [
                {"t": "mmd", "id": "ch14-cbow", "src": MMD_CBOW,
                 "cap": "Figure 14.6 — Continuous Bag of Words, from Mikolov et al. (2013)."},
                {"t": "p", "md": "If the surrounding bag contains *sail*, *wave*, and *mast*, "
                                 "you might guess *boat*. **No labels are needed** — the "
                                 "supervision comes from the text itself, which is exactly "
                                 "chapter 1's ==self-supervised learning=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.4",
            "title": "Where the extra data comes from",
            "blocks": [
                {"t": "p", "md": "Remember the `unsup/` directory that was skipped during "
                                 "dataset preparation? It holds **another 25,000 reviews** — "
                                 "the same size as the training set."},
                {"t": "code", "lang": "python", "file": "combining labelled and unlabelled text",
                 "src": """# all of train/pos, train/neg AND train/unsup, labels discarded
pretrain_ds = keras.utils.text_dataset_from_directory(
    imdb_extract_dir / "train",
    labels=None,
    batch_size=batch_size,
)"""},
                {"t": "band",
                 "md": "**Doubling the text costs nothing**, because the CBOW task does not "
                       "care whether a review is positive or negative — ==it only needs "
                       "words in context=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 14.5.5",
            "title": "Using the pretrained embedding",
            "blocks": [
                {"t": "p", "md": "The pretrained weights are loaded into the classifier's "
                                 "`Embedding` layer, which then either stays frozen or is "
                                 "fine-tuned — the same two options as chapter 8."},
                {"t": "code", "lang": "python", "file": "loading pretrained weights",
                 "src": """embedding_layer = layers.Embedding(max_tokens, 256, mask_zero=True)
embedding_layer.build((None,))
embedding_layer.set_weights(pretrained_embedding.get_weights())

inputs = keras.Input(shape=(max_length,), dtype="int32")
x = embedding_layer(inputs)
x = layers.Bidirectional(layers.LSTM(32))(x)
outputs = layers.Dense(1, activation="sigmoid")(layers.Dropout(0.5)(x))"""},
                {"t": "p", "md": "This is **transfer learning for text**, structurally "
                                 "identical to feature extraction from a pretrained ConvNet — "
                                 "==and it is the pattern the whole of chapter 15 builds on=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Sections 14.4 – 14.5",
            "title": "The four models, on one benchmark",
            "blocks": [
                {"t": "mmd", "id": "ch14-ladder", "src": MMD_LADDER14,
                 "cap": "Each step adds either more order information or more outside "
                        "knowledge."},
                {"t": "band",
                 "md": "And the practical caveat: **the bag-of-words model is close behind, "
                       "trains in seconds, and is trivial to explain**. On short texts, or "
                       "with little data, ==it is frequently the right answer=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Practice",
            "title": "Four ways text pipelines go wrong",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🕳", "h": "Padding treated as content",
                     "p": "Forgetting `mask_zero=True`. The model spends capacity modelling "
                          "zeros, and long reviews are penalised against short ones.",
                     "style": "bad"},
                    {"ico": "🔤", "h": "adapt() on the wrong data",
                     "p": "Calling `adapt()` on the full dataset builds the vocabulary from "
                          "**test text** — an information leak in the sense of chapter 5.",
                     "style": "bad"},
                    {"ico": "✂", "h": "Truncation that cuts the answer",
                     "p": "`output_sequence_length` shorter than the reviews means the ending "
                          "— often where sentiment resolves — is discarded.", "style": "warn"},
                    {"ico": "🌍", "h": "A tokenizer trained on the wrong language",
                     "p": "A vocabulary built on English text will decompose other languages "
                          "into near-characters, inflating sequence length enormously.",
                     "style": "warn"},
                ]},
            ],
            "notes": "The second one is the subtle one and the most common in submitted work: "
                     "adapt() is learning from data, so it obeys the same split discipline as "
                     "training does.",
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Natural language is messy by construction** — usage precedes rules, "
                    "which is why rule-based NLP failed for forty years.",
                    "**Tokenization is compression.** Byte-pair encoding gets short sequences "
                    "and a small vocabulary at once.",
                    "**Set or sequence** is the question every NLP architecture answers.",
                    "**Bag-of-words is a strong, cheap baseline.** Bigrams add local order for "
                    "one argument.",
                    "**One-hot assumes words are independent**, which is false. Embeddings "
                    "learn a space where geometry reflects meaning.",
                    "**Pretraining on unlabelled text** removes the labelled-data bottleneck.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "04_pretraining_an_embedding.ipynb",
                     "href": "../../course-slides/notebooks/ch14/04_pretraining_an_embedding.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 15 — Language models and the Transformer",
                     "href": "../ch15/index.html"},
                ]},
            ],
        },
    ],
}
