# -*- coding: utf-8 -*-
"""Chapter 1 — What is deep learning?

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 1
(pp. 3-16). Written from the book PDF, not from the summary pages on the
book's website -- those are abridged and, in at least one place, wrong about
the numbers.

The chapter carries no code of its own. The one listing here is a teaching
prop: the smallest thing that shows a rule being *produced* rather than
written, which is the chapter's central claim.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


# =============================================================================
#  Diagrams. Mermaid rather than hand-placed SVG: the layout is computed, so
#  boxes come out the same size and on a shared baseline.
# =============================================================================

MMD_PARADIGM = """
flowchart LR
  subgraph CLASSIC["Classical programming"]
    direction LR
    R1["Rules"] --> P1["Program"]
    D1["Data"] --> P1
    P1 --> A1["Answers"]
  end
  subgraph ML["Machine learning"]
    direction LR
    D2["Data"] --> T2["Training"]
    A2["Answers"] --> T2
    T2 --> R2["Rules"]
  end
  CLASSIC ~~~ ML
"""

MMD_LAYERS = """
flowchart LR
  IN["Input<br/>28 x 28 pixels"] --> L1["Layer 1<br/>edges"]
  L1 --> L2["Layer 2<br/>corners"]
  L2 --> L3["Layer 3<br/>parts"]
  L3 --> L4["Layer 4<br/>digits"]
  L4 --> OUT["Output<br/>P(0..9)"]
"""

MMD_LOOP = """
flowchart LR
  X["Input X"] --> LAYER["Layer<br/>data transformation"]
  W["Weights W"] --- LAYER
  LAYER --> YP["Prediction Y'"]
  YP --> LOSS["Loss function"]
  Y["True target Y"] --> LOSS
  LOSS --> OPT["Optimizer"]
  OPT -. "update weights" .-> W
"""

MMD_SCOPE = """
flowchart TB
  AI["Artificial intelligence<br/><small>since the 1950s</small>"]
  SYM["Symbolic AI<br/><small>hand-coded rules</small>"]
  MLB["Machine learning<br/><small>rules learned from data</small>"]
  DL["Deep learning<br/><small>successive layers</small>"]
  SHAL["Shallow learning<br/><small>one or two layers</small>"]
  AI --> SYM
  AI --> MLB
  MLB --> DL
  MLB --> SHAL
"""

MMD_INGREDIENTS = """
flowchart LR
  I1["1. Input data<br/>sound, images, rows"]
  I2["2. Expected outputs<br/>transcripts, labels"]
  I3["3. A quality measure<br/>distance to the target"]
  I1 --> T["Learning<br/>adjust until the<br/>measure improves"]
  I2 --> T
  I3 --> T
  T --> R["A rule that<br/>generalises"]
"""

MMD_WAVES = """
flowchart LR
  W1["2013 - 2017<br/><b>Perception</b><br/>image, speech,<br/>handwriting"]
  W2["2017 - 2022<br/><b>Language</b><br/>translation, NLP,<br/>the Transformer"]
  W3["2022 - now<br/><b>Generative</b><br/>chat, code,<br/>image synthesis"]
  W1 --> W2 --> W3
"""


# =============================================================================
#  Deck
# =============================================================================

NB = ["01_the_ml_paradigm.ipynb"]
FIG = "figs/book/figure-1-1.png"

DECK = {
    "id": "ch01",
    "kind": "chapter",
    "number": 1,
    "title": "What Is Deep Learning?",
    "subtitle": "Putting AI, machine learning, and deep learning in their right "
                "places -- then separating what the field has actually achieved "
                "from what it has merely promised.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- chapter 1",
    "source_url": chapter_url(1),
    "duration": "90 minutes",
    "presenter": {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    "resources": chapter_resources(1, local_notebooks=NB),
    "objectives": [
        "Place **AI, machine learning, and deep learning** in the correct "
        "relationship -- which contains which, and since when.",
        "Explain the **inversion**: classical programming outputs answers, "
        "machine learning outputs rules.",
        "Name the **three things** every machine learning system needs, and say "
        "what breaks when one of them is missing.",
        "Describe how deep learning works through **weights, a loss function, "
        "and backpropagation** -- without deriving a single equation.",
        "Separate **what deep learning has demonstrably done** from **what is "
        "still a claim**, and name what triggered the two previous AI winters.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Roadmap",
            "title": "What this chapter is for",
            "blocks": [
                {"t": "lead", "md": "Chapter 1 teaches no code at all. Its job is more "
                                    "basic: to make sure everyone in the room uses the "
                                    "same words for the same things."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🗺", "h": "Definitions and history",
                     "p": "Three nested circles -- AI, ML, DL -- plus one branch that is "
                          "**not** machine learning at all.",
                     "tag": "1.1 – 1.5"},
                    {"ico": "⚙", "h": "How it works",
                     "p": "Representations, weights, loss, backpropagation. Chollet "
                          "explains it with **three figures**, not equations.",
                     "tag": "1.6 – 1.7"},
                    {"ico": "⚖", "h": "Achievement vs hype",
                     "p": "What deep learning has **already** done, and why the field went "
                          "cold twice before.",
                     "tag": "1.8 – 1.12"},
                ]},
            ],
            "notes": "Open by asking the room to define AI and machine learning in one "
                     "sentence each. The spread of answers you get is the reason this "
                     "chapter exists.",
        },

        {"type": "section", "num": "01",
         "title": "AI, machine learning, deep learning",
         "lead": "Three terms the press uses interchangeably. They are nested."},

        {
            "type": "slide",
            "kicker": "Section 1.1",
            "title": "Three nested circles, not three synonyms",
            "blocks": [
                {"t": "img", "src": FIG, "credit": True, "max_h": "44vh",
                 "cap": "Figure 1.1 — deep learning is a subfield of machine learning, "
                        "which is a subfield of AI."},
                {"t": "p", "md": "The nesting is the whole point: every deep learning system "
                                 "is a machine learning system, and every machine learning "
                                 "system is an AI system -- ==but not the other way round=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.2",
            "title": "…and one branch that sits outside machine learning",
            "blocks": [
                {"t": "mmd", "id": "ch01-scope", "src": MMD_SCOPE,
                 "cap": "Symbolic AI is inside AI but outside machine learning. Shallow "
                        "learning is inside machine learning but outside deep learning."},
            ],
            "notes": "This is the slide people photograph. Leave it up while you talk "
                     "through the next two.",
        },

        {
            "type": "slide",
            "kicker": "Section 1.2",
            "title": "Symbolic AI: what it was, and where it stopped",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Artificial intelligence** was born in the 1950s. "
                                         "The working definition: *the effort to automate "
                                         "intellectual tasks normally performed by humans*."},
                        {"t": "p", "md": "For roughly thirty years the dominant approach was "
                                         "**symbolic AI**: programmers wrote the rules by "
                                         "hand, and the machine executed them."},
                    ],
                    [
                        {"t": "cards", "cols": 1, "items": [
                            {"ico": "♟", "h": "Where it worked",
                             "p": "Well-defined, logical problems. Chess is the canonical win.",
                             "style": "good"},
                            {"ico": "🌫", "h": "Where it collapsed",
                             "p": "**Fuzzy** problems -- recognising an image, understanding "
                                  "speech. Nobody can write down those rules, because nobody "
                                  "is aware of using them.", "style": "bad"},
                        ]},
                    ],
                ]},
                {"t": "band",
                 "md": "Machine learning rose from the 1990s onward precisely because "
                       "==the fuzzy problems were the ones left over=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.2",
            "title": "The question that opened the field, in 1843",
            "blocks": [
                {"t": "quote",
                 "md": "The Analytical Engine has no pretensions whatever to originate "
                       "anything. It can do whatever we know how to order it to perform.",
                 "cite": "Ada Lovelace, 1843 — on Charles Babbage's machine"},
                {"t": "p", "md": "Lovelace's objection is the oldest question in the field, "
                                 "and it is not rhetorical: **can a machine ever produce "
                                 "something we did not put into it?**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.2",
            "title": "…and the claim that answered it, in 1956",
            "blocks": [
                {"t": "quote",
                 "md": "Every aspect of learning or any other feature of intelligence can in "
                       "principle be so precisely described that a machine can be made to "
                       "simulate it.",
                 "cite": "John McCarthy et al., the Dartmouth workshop proposal, 1956"},
                {"t": "band",
                 "md": "These two statements are 113 years apart and they disagree. Machine "
                       "learning is a **partial** answer to Lovelace: the machine does "
                       "produce something we never wrote down -- ==the rules=="},
            ],
            "notes": "Connect forward to the audit question that always comes up later: if "
                     "we did not write the rule, who is accountable for it?",
        },

        {"type": "section", "num": "02", "title": "The inversion",
         "lead": "What used to be the output becomes the input."},

        {
            "type": "slide",
            "kicker": "Section 1.3",
            "title": "Machine learning runs programming backwards",
            "blocks": [
                {"t": "mmd", "id": "ch01-paradigm", "src": MMD_PARADIGM,
                 "cap": "Figure 1.2 — classical programming is fed rules and data and emits "
                        "answers; machine learning is fed data and answers and emits rules."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.3",
            "title": "The consequence people underestimate",
            "blocks": [
                {"t": "band",
                 "md": "A machine learning system is **trained, not programmed**. If you have "
                       "no worked examples, there is ==nothing to train==, no matter how good "
                       "the architecture is."},
                {"t": "p", "md": "This is why the hardest part of most projects turns out to "
                                 "be the dataset rather than the model. Chapter 6 is devoted "
                                 "to that problem."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.4",
            "title": "Three things every ML system needs",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📥", "h": "1 · Input data points",
                     "p": "Sound files for speech recognition; photographs for image tagging. "
                          "This is what gets transformed.", "style": "accent"},
                    {"ico": "🎯", "h": "2 · Examples of expected output",
                     "p": "Human transcripts for the sound files; tags such as *dog* or *cat* "
                          "for the pictures.", "style": "accent"},
                    {"ico": "📏", "h": "3 · A way to measure quality",
                     "p": "The distance between what the algorithm currently says and what it "
                          "should say. This is the **feedback signal**.", "style": "accent"},
                ]},
                {"t": "p", "md": "That adjustment step, driven by the feedback signal, is "
                                 "==exactly what the word *learning* means here=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.4",
            "title": "The three, drawn as one pipeline",
            "blocks": [
                {"t": "mmd", "id": "ch01-ingredients", "src": MMD_INGREDIENTS,
                 "cap": "All three feed the same adjustment step. Remove any one of them and "
                        "the arrow into it disappears."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.4",
            "title": "Lose one, and it stops being machine learning",
            "blocks": [
                {"t": "table",
                 "head": ["Missing ingredient", "What you actually have", "What follows"],
                 "widths": [24, 30, 46],
                 "rows": [
                     ["Expected outputs", "Raw data with no labels",
                      "Not supervised learning. Either label it, or move to unsupervised "
                      "or self-supervised methods."],
                     ["A quality measure", "Data and labels, no agreed metric",
                      "The model can be trained but **not judged** — and this is the most "
                      "common way real projects fail."],
                     ["Representative inputs", "Examples unlike production conditions",
                      "It works on the laptop and fails in the field. Chapters 5 and 6 give "
                      "this its proper names."],
                 ]},
            ],
            "notes": "Ask the room to test one of their own use cases against all three. "
                     "The third one is missing far more often than people expect.",
        },

        {
            "type": "slide",
            "kicker": "Section 1.4",
            "title": "Representation: the idea that runs through the whole book",
            "blocks": [
                {"t": "p", "md": "A **representation** is simply a different way of encoding "
                                 "the same data. The same photograph can be encoded as RGB "
                                 "or as HSV -- identical content, different axes."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "bullets", "items": [
                            "*Select all red pixels* — easy in **RGB**.",
                            "*Make the image less saturated* — easy in **HSV**.",
                        ]},
                    ],
                    [
                        {"t": "band",
                         "md": "Same picture, same task difficulty changed entirely. So "
                               "machine learning is ==the search for a representation that "
                               "makes the task easy=="},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.4 · figures 1.3–1.4",
            "title": "The worked example: change the axes, and the rule appears",
            "blocks": [
                {"t": "steps", "items": [
                    "**Raw data.** White points and black points scattered in an (x, y) plane. "
                    "No simple rule separates them.",
                    "**Coordinate change.** Move the origin, rotate the axes. Nothing about "
                    "the data changed -- only how it is written down.",
                    "**Better representation.** The rule is now one sentence: *black points "
                    "are those with x > 0*.",
                ]},
                {"t": "band",
                 "md": "No model got smarter. Only the representation changed -- and that is "
                       "the work that used to be called ==feature engineering== and was done "
                       "by hand."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.4",
            "title": "Why hand-written rules do not scale",
            "blocks": [
                {"t": "p", "md": "We designed that coordinate change ourselves. Fine for a toy. "
                                 "But could you write explicit image transformations that "
                                 "separate a 6 from an 8, or a 1 from a 7, ==across every "
                                 "kind of handwriting=="},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✍", "h": "Possible — up to a point",
                     "p": "Rules such as *count the closed loops*, or vertical and horizontal "
                          "pixel histograms, do a decent job on handwritten digits.",
                     "style": "warn"},
                    {"ico": "💥", "h": "But brittle, and miserable to maintain",
                     "p": "Every new handwriting sample that breaks your carefully reasoned "
                          "rules forces a new transformation and a new rule — **and you must "
                          "check it against every rule you already wrote**.", "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.4",
            "title": "Hypothesis space: what the algorithm is allowed to search",
            "blocks": [
                {"t": "p", "md": "Machine learning algorithms are **not creative** about "
                                 "finding these transformations. They search a predefined set "
                                 "of operations -- and that set is called the "
                                 "**hypothesis space**."},
                {"t": "band",
                 "md": "In the two-dimensional example, the hypothesis space was ==the space "
                       "of all possible coordinate changes=="},
                {"t": "p", "md": "Choosing a model architecture, in later chapters, is exactly "
                                 "the act of choosing a hypothesis space."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.4",
            "title": "The whole field, in one sentence",
            "blocks": [
                {"t": "quote",
                 "md": "Machine learning is searching for useful representations and rules "
                       "over some input data, within a predefined space of possibilities, "
                       "using guidance from a feedback signal.",
                 "cite": "Chollet & Watson, section 1.4"},
                {"t": "p", "md": "That one idea covers a startling range of tasks -- from "
                                 "autonomous driving to answering questions in natural "
                                 "language."},
            ],
        },

        {"type": "section", "num": "03", "title": "The \"deep\" in deep learning",
         "lead": "Not deeper understanding. Just more layers."},

        {
            "type": "slide",
            "kicker": "Section 1.5",
            "title": "\"Deep\" is a statement about architecture, nothing more",
            "blocks": [
                {"t": "quote",
                 "md": "The \"deep\" in \"deep learning\" isn't a reference to any kind of "
                       "deeper understanding achieved by the approach; rather, it stands for "
                       "this idea of successive layers of representations.",
                 "cite": "Chollet & Watson, section 1.5"},
                {"t": "p", "md": "The number of layers is the model's **depth**. Modern "
                                 "networks run to tens or hundreds of them."},
            ],
            "notes": "Correct the most common misconception in the room right here: 'deep' "
                     "does not mean the machine understands anything more deeply.",
        },

        {
            "type": "slide",
            "kicker": "Section 1.5",
            "title": "Each layer moves the data one step closer to the answer",
            "blocks": [
                {"t": "mmd", "id": "ch01-layers", "src": MMD_LAYERS,
                 "cap": "Figures 1.5–1.6 — a four-layer network for digit classification. "
                        "Intermediate representations get further from the pixels and closer "
                        "to the answer."},
                {"t": "p", "md": "Chollet calls this **information distillation**: irrelevant "
                                 "information is filtered out, relevant information is "
                                 "amplified. All the layers are learned ==at once, "
                                 "automatically==, from the training data."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.5",
            "title": "Two better names the field never adopted",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "bullets", "items": [
                            "*layered representations learning*",
                            "*hierarchical representations learning*",
                        ]},
                        {"t": "p", "md": "Either would have been more accurate. **Deep** won "
                                         "on history, not on precision."},
                    ],
                    [
                        {"t": "band", "style": "amber",
                         "md": "Its opposite has a name too: **shallow learning**, which "
                               "learns only one or two layers of representation -- for "
                               "instance a pixel histogram followed by a classification rule."},
                    ],
                ]},
            ],
        },

        {"type": "section", "num": "04", "title": "How deep learning actually works",
         "lead": "Three figures, and not one equation."},

        {
            "type": "slide",
            "kicker": "Section 1.6 · figure 1.7",
            "title": "Step 1 — weights parameterise what a layer does",
            "blocks": [
                {"t": "p", "md": "What a layer does to its input is stored in its **weights**, "
                                 "which are just numbers. They are also called the layer's "
                                 "**parameters**."},
                {"t": "band",
                 "md": "Learning, then, means ==finding values for every weight== such that "
                       "the network maps its example inputs to their correct targets. A "
                       "large network has tens of millions of them."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.6 · figure 1.8",
            "title": "Step 2 — the loss function measures how far off you are",
            "blocks": [
                {"t": "p", "md": "The **loss function** takes the network's prediction and the "
                                 "true target, and computes a distance score. It is also "
                                 "called the *objective function* or *cost function*."},
                {"t": "band",
                 "md": "That single number is the entire feedback signal. ==Everything the "
                       "network learns, it learns from that one score.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.6 · figure 1.9",
            "title": "Step 3 — backpropagation turns the score into an adjustment",
            "blocks": [
                {"t": "p", "md": "The loss score is used as a feedback signal to nudge the "
                                 "weights in the direction that lowers the loss a little. "
                                 "This adjustment is the job of the **backpropagation "
                                 "algorithm**."},
                {"t": "band", "style": "amber",
                 "md": "The weights start out **random**, so the first outputs are nonsense "
                       "and the first loss is high. What makes it work is ==repetition of the "
                       "loop==, not a lucky starting point."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.6",
            "title": "The three figures, joined into one loop",
            "blocks": [
                {"t": "mmd", "id": "ch01-loop", "src": MMD_LOOP,
                 "cap": "Figures 1.7–1.9 combined: weights parameterise the layer, the loss "
                        "scores the prediction against the target, and the optimizer uses "
                        "that score to move the weights."},
                {"t": "p", "md": "This is called the **training loop**, repeated over "
                                 "thousands of examples. Chapter 2 takes every box in this "
                                 "picture apart."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Teaching prop · 1 of 3",
            "title": "The same loop, small enough to read in one sitting",
            "blocks": [
                {"t": "p", "md": "Chapter 1 carries no code. But the entire diagram above fits "
                                 "in a few lines of NumPy, and seeing it run removes any "
                                 "suspicion that something magical is going on."},
                {"t": "p", "md": "We generate data from a law we choose -- `y = 2x + 1` -- and "
                                 "then ==throw the law away==. The program never sees it. The "
                                 "question is whether it can recover it."},
                {"t": "code", "lang": "python", "file": "setup — data from a law we then hide",
                 "src": """import numpy as np

rng = np.random.default_rng(0)
X = rng.uniform(-1, 1, size=(200, 1))
Y = 2 * X + 1 + rng.normal(0, 0.05, size=(200, 1))   # the law, plus a little noise

# The weights start random -- exactly as the chapter says.
W, b = rng.normal(size=(1, 1)), np.zeros((1,))
print(f"before training:  W {W[0, 0]:+.3f}   b {b[0]:+.3f}")"""},
                {"t": "out", "src": "before training:  W +0.126   b +0.000"},
            ],
            "notes": "Run it live if you can. Point out that nothing in the code contains the "
                     "numbers 2 and 1.",
        },

        {
            "type": "slide",
            "kicker": "Teaching prop · 2 of 3",
            "title": "Four lines that are the three figures",
            "blocks": [
                {"t": "p", "md": "Each numbered comment below points at one of the three "
                                 "figures we just walked through. Nothing else is happening."},
                {"t": "code", "lang": "python", "file": "the training loop itself",
                 "src": """for step in range(600):
    Y_pred = X @ W + b                  # the layer: a data transformation (fig 1.7)
    loss = np.mean((Y_pred - Y) ** 2)   # the loss: how far off are we? (fig 1.8)

    grad = 2.0 * (Y_pred - Y) / len(X)  # gradient of the loss (fig 1.9)
    W -= 0.5 * (X.T @ grad)             # step downhill
    b -= 0.5 * grad.sum()

    if step % 200 == 0:
        print(f"step {step:3d}  loss {loss:.5f}  W {W[0, 0]:+.3f}  b {b[0]:+.3f}")"""},
                {"t": "band",
                 "md": "Forward pass, loss, gradient, update. ==Every training loop in this "
                       "book is that shape==, however large the model gets."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Teaching prop · 3 of 3",
            "title": "What comes out is the rule itself",
            "blocks": [
                {"t": "out", "src": """step   0  loss 4.02891  W +0.126  b +0.000
step 200  loss 0.00932  W +1.842  b +0.968
step 400  loss 0.00268  W +1.972  b +0.997
done      loss 0.00251  W +1.994  b +1.000"""},
                {"t": "band",
                 "md": "The weights travel from random to ==W ≈ 2, b ≈ 1== -- the law that "
                       "generated the data, which we never wrote down. That is *rules as "
                       "output* from figure 1.2, made concrete."},
                {"t": "bullets", "items": [
                    "Not one line told the program the answer was 2 and 1.",
                    "It was given only **data, answers, and a measure of loss** — the three "
                    "required ingredients.",
                    "Chapter 2 swaps this NumPy for tensors and automatic differentiation. "
                    "The shape of the loop ==does not change==.",
                ]},
            ],
        },

        {"type": "section", "num": "05", "title": "Why deep learning won",
         "lead": "Three properties, and one change that left the alternatives behind."},

        {
            "type": "slide",
            "kicker": "Section 1.7",
            "title": "Property 1 — simplicity",
            "blocks": [
                {"t": "p", "md": "Deep learning automates what used to be the most crucial "
                                 "step in the workflow: **feature engineering**."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Shallow learning** transformed the input into one "
                                         "or two representation spaces -- not expressive "
                                         "enough for most problems. So humans went to great "
                                         "lengths to hand-engineer good representations first."},
                    ],
                    [
                        {"t": "band",
                         "md": "Deep learning learns **all** the features in one pass. "
                               "Elaborate multistage pipelines get replaced by ==a single, "
                               "end-to-end model=="},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.7",
            "title": "Property 2 — scalability",
            "blocks": [
                {"t": "bullets", "items": [
                    "Highly amenable to **parallelisation on GPUs** and specialised hardware, "
                    "so it rides Moore's law directly.",
                    "Trained by iterating over **small batches**, which means dataset size is "
                    "==no longer an upper bound==.",
                    "The only real bottleneck is available parallel compute — and that "
                    "barrier keeps moving.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.7",
            "title": "Property 3 — versatility and reusability",
            "blocks": [
                {"t": "p", "md": "Unlike most earlier approaches, a deep learning model can be "
                                 "trained on **additional data without restarting from "
                                 "scratch** -- which makes continuous online learning viable "
                                 "for large production models."},
                {"t": "band",
                 "md": "Trained models are also **repurposable**. That is the idea behind "
                       "==foundation models==: very large models trained on enormous data, "
                       "reusable across many new tasks with little retraining, or none."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.7",
            "title": "The cost of that power",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "The property that makes it strong -- **representations it discovers "
                       "for itself** -- is exactly the property that makes it hard to explain. "
                       "Chapter 10 returns to this for image models."},
                {"t": "p", "md": "In regulated settings, explainability is not an academic "
                                 "preference. It is a requirement, and it has to be designed "
                                 "for rather than retrofitted."},
            ],
        },

        {"type": "section", "num": "06", "title": "The age of generative AI",
         "lead": "What changed in 2022, and what actually made it possible."},

        {
            "type": "slide",
            "kicker": "Section 1.8",
            "title": "Self-supervised learning removed the labelling bottleneck",
            "blocks": [
                {"t": "p", "md": "Generative models learn to **reconstruct** the content fed "
                                 "into them: recover a sharp image from a noisy one, predict "
                                 "the next word in a sentence."},
                {"t": "band",
                 "md": "So the targets are taken **from the input itself**. That is "
                       "==self-supervised learning==, and it is what lets these models use "
                       "vast amounts of *unlabelled* data."},
                {"t": "p", "md": "Doing away with manual annotation -- the bottleneck of every "
                                 "earlier generation of machine learning -- unlocked a scale "
                                 "never seen before."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.8",
            "title": "The scale that resulted",
            "blocks": [
                {"t": "stats", "cols": 4, "items": [
                    {"v": "10¹¹", "l": "order of parameters in a foundation model"},
                    {"v": "> 1 PB", "l": "order of training data"},
                    {"v": "$10s M", "l": "order of cost to train one"},
                    {"v": "2022", "l": "the year it entered public awareness"},
                ]},
                {"t": "p", "md": "These models behave like a **fuzzy database of human "
                                 "knowledge**. Because they have already memorised so much, "
                                 "they solve new problems by **prompting** -- no "
                                 "special-purpose programming, no retraining."},
                {"t": "band", "style": "amber",
                 "md": "It is newer in public attention than in research: the earliest text "
                       "generation experiments date to the **1990s**, and the first edition "
                       "of this book, in 2017, already had a chapter on generative models."},
            ],
        },

        {"type": "section", "num": "07", "title": "What has actually been achieved",
         "lead": "The record, before the argument about the forecasts."},

        {
            "type": "slide",
            "kicker": "Section 1.9",
            "title": "Three waves in a single decade",
            "blocks": [
                {"t": "mmd", "id": "ch01-waves", "src": MMD_WAVES,
                 "cap": "Perception matured first, language second, generation third."},
                {"t": "band",
                 "md": "Useful for planning: the capabilities that matured **earliest** are "
                       "the cheapest and most reliable to deploy today. The newest ones are "
                       "==the most expensive and the least settled=="},
            ],
            "notes": "This slide often redirects a budget conversation. Ask which wave the "
                     "participant's actual use case belongs to.",
        },

        {
            "type": "slide",
            "kicker": "Section 1.9",
            "title": "Breakthroughs on problems that had long resisted machines",
            "blocks": [
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "💬", "h": "Conversation", "p": "ChatGPT, Gemini, Claude."},
                    {"ico": "⌨", "h": "Code assistance", "p": "GitHub Copilot and its kin."},
                    {"ico": "🖼", "h": "Photorealistic images", "p": "Generated from text."},
                    {"ico": "👁", "h": "Human-level perception",
                     "p": "Image classification, speech transcription, handwriting."},
                    {"ico": "🌐", "h": "Translation & speech", "p": "Both dramatically improved."},
                    {"ico": "🚗", "h": "Autonomous driving",
                     "p": "Deployed to the public in Phoenix, San Francisco, Los Angeles and "
                          "Austin as of 2025."},
                    {"ico": "♟", "h": "Superhuman play", "p": "Go, chess, and poker."},
                    {"ico": "📺", "h": "Recommenders", "p": "YouTube, Netflix, Spotify."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.9",
            "title": "And problems thought impossible a few years ago",
            "blocks": [
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "📜", "h": "Ancient manuscripts",
                     "p": "Tens of thousands in the Vatican Secret Archive, transcribed "
                          "automatically.", "style": "good"},
                    {"ico": "🌱", "h": "Plant disease",
                     "p": "Detected and classified in the field with an ordinary smartphone.",
                     "style": "good"},
                    {"ico": "🩺", "h": "Medical imaging",
                     "p": "Assisting oncologists and radiologists with interpretation.",
                     "style": "good"},
                    {"ico": "🌊", "h": "Natural disasters",
                     "p": "Predicting floods, hurricanes, and even earthquakes.",
                     "style": "good"},
                ]},
                {"t": "band",
                 "md": "This list is ==not a forecast==. Every item on it is already running. "
                       "That is what separates it from the next section."},
            ],
        },

        {"type": "section", "num": "08", "title": "Beware the short-term hype",
         "lead": "Twice before, the field promised too much and lost its funding."},

        {
            "type": "slide",
            "kicker": "Section 1.10",
            "title": "What was promised in 2023, and what happened",
            "blocks": [
                {"t": "bullets", "items": [
                    "Soon after GPT-4, pundits claimed **nobody would need to work** and that "
                    "mass unemployment was a year away.",
                    "Others promised economic productivity would rise **10× to 100×**.",
                    "Two years later: US unemployment remains low, and productivity is far "
                    "from any such explosion.",
                ]},
                {"t": "band",
                 "md": "To be fair to the technology: by mid-2025 generative AI was earning "
                       "**tens of billions of dollars a year** -- extremely impressive for an "
                       "industry that ==did not exist three years earlier=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.11",
            "title": "The gap that has to close somehow",
            "blocks": [
                {"t": "stats", "cols": 2, "items": [
                    {"v": "> $200 bn", "l": "annual AI investment, mostly data centres and GPUs"},
                    {"v": "≈ $30 bn", "l": "annual revenue generated against it"},
                ]},
                {"t": "quote",
                 "md": "AI is currently being judged by executives and investors not by what "
                       "it has accomplished, but by what we are told it might soon become "
                       "able to do — much of which will durably stay out of reach of existing "
                       "technologies. Something will have to give.",
                 "cite": "Chollet & Watson, section 1.11"},
            ],
            "notes": "These are the book's figures, and they are the ones to quote in a "
                     "budget meeting — not the $100bn/$10bn numbers circulating elsewhere.",
        },

        {
            "type": "slide",
            "kicker": "Section 1.10",
            "title": "The order is the opposite of what people assume",
            "blocks": [
                {"t": "lead", "md": "It is tempting to think the practical success of "
                                    "generative AI produced the belief in near-term AGI. "
                                    "==It was the other way round=="},
                {"t": "steps", "items": [
                    "**2013** — fears among tech elites that AGI was a few years out. The "
                    "candidate was **DeepMind**, a London startup later acquired by Google.",
                    "**2015** — that belief drove the founding of **OpenAI**, intended as an "
                    "open-source counterweight to DeepMind.",
                    "**2016** — OpenAI's recruiting pitch was that it would achieve **AGI by "
                    "2020**. Only a minority in the industry believed that timeline.",
                    "**Early 2023** — a significant fraction of Bay Area engineers were "
                    "convinced AGI was one or two years away.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "OpenAI was critical in kick-starting generative AI. So in a peculiar "
                       "twist, **the belief in near-term AGI fuelled the rise of generative "
                       "AI**, not the reverse."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.11",
            "title": "Winter, the first time",
            "blocks": [
                {"t": "quote",
                 "md": "Within a generation … the problem of creating \"artificial "
                       "intelligence\" will substantially be solved.",
                 "cite": "Marvin Minsky, 1967"},
                {"t": "quote",
                 "md": "In from three to eight years we will have a machine with the general "
                       "intelligence of an average human being.",
                 "cite": "Marvin Minsky, 1970"},
                {"t": "p", "md": "When those expectations failed to materialise, researchers "
                                 "and government funding turned away, and the **first AI "
                                 "winter** began."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.11",
            "title": "Winter, the second time — and where we are now",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**The 1980s: expert systems.** A few early successes "
                                         "triggered a wave of investment; by around 1985 "
                                         "companies were spending **over $1 billion a year**."},
                        {"t": "p", "md": "By the early 1990s these systems had proven expensive "
                                         "to maintain, difficult to scale, and limited in "
                                         "scope. Interest died."},
                    ],
                    [
                        {"t": "band",
                         "md": "**Now.** Chollet's own view: a full-scale retreat like the "
                               "1990s is unlikely -- AI has already demonstrated "
                               "world-changing value. ==If there is a winter, it should be "
                               "very mild.== But some air will have to come out."},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.10",
            "title": "Cognitive automation is not intelligence",
            "blocks": [
                {"t": "quote",
                 "md": "Despite its name, today's \"artificial intelligence\" is more "
                       "accurately described as \"cognitive automation\" — the encoding and "
                       "operationalization of human skills and knowledge.",
                 "cite": "Chollet & Watson, section 1.10"},
                {"t": "p", "md": "It excels at problems with narrowly defined requirements, or "
                                 "where ample precise examples exist. It is about **enhancing "
                                 "the capabilities of computers**, not replicating human minds."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.10",
            "title": "The cartoon and the living being",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**AI is like a cartoon character; intelligence is "
                                         "like a living being.** A cartoon, however realistic, "
                                         "can only act out the scenes it was drawn for."},
                        {"t": "p", "md": "*\"If the cartoon is drawn with sufficient realism "
                                         "and covers sufficiently many scenes, what's the "
                                         "difference?\"*"},
                    ],
                    [
                        {"t": "band", "style": "rose",
                         "md": "The difference is **adaptability**. Intelligence is the ability "
                               "to face the unknown, adapt to it, and learn from it. "
                               "Automation, even at its best, can only handle situations it "
                               "has been trained on."},
                    ],
                ]},
                {"t": "p", "md": "That is why building robust automation is so hard: it "
                                 "requires accounting for ==every possible scenario=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.10",
            "title": "What follows for anything you put into production",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "If a system can only handle what it was trained on, then **monitoring "
                       "for data drift is not an optional feature** -- it is a condition of "
                       "the system remaining fit to use. Chapter 6 and chapter 18 return to "
                       "this."},
                {"t": "p", "md": "And the reassuring corollary: do not worry about AI suddenly "
                                 "becoming self-aware. Today's technology is not headed that "
                                 "way. *\"It's like expecting a better clock to lead to time "
                                 "travel — they're just different things altogether.\"*"},
            ],
        },

        {"type": "section", "num": "09", "title": "The promise of AI",
         "lead": "The short-term forecasts deflate. The long-term change still arrives."},

        {
            "type": "slide",
            "kicker": "Section 1.12",
            "title": "A 2017 forecast, scored in 2025",
            "blocks": [
                {"t": "table",
                 "head": ["Written in 2017", "Where it stands in 2025"],
                 "widths": [36, 64],
                 "rows": [
                     ["AI as your assistant, even your friend",
                      "**Tens of millions** use chatbots as daily assistants. Hundreds of "
                      "thousands interact with AI \"friends\" in apps such as Character.ai."],
                     ["It will answer your questions and help educate your kids",
                      "Question-answering and homework assistance turned out to be the "
                      "**top two** applications."],
                     ["It will drive you from point A to point B",
                      "Fully autonomous driving is deployed at scale in Phoenix, San "
                      "Francisco, Los Angeles, and Austin."],
                     ["It will help scientists make breakthroughs",
                      "**AlphaFold** predicts protein structures. Terence Tao expects AI to "
                      "be a reliable co-author in mathematical research around 2026."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 1.12",
            "title": "Two things that are true at the same time",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📉", "h": "The short-term hype will deflate",
                     "p": "The forecasts of 2023 have not held, and the investment-to-revenue "
                          "gap has to close.", "style": "warn"},
                    {"ico": "📈", "h": "The long-term change still comes",
                     "p": "Across medicine, science, industry, and daily life — the direction "
                          "was right even where the timing was wrong.", "style": "good"},
                ]},
                {"t": "band",
                 "md": "Holding both at once is uncomfortable, and it is ==exactly what makes "
                       "planning in this field difficult=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**AI ⊃ machine learning ⊃ deep learning.** Symbolic AI is inside AI and "
                    "outside machine learning.",
                    "**Machine learning inverts programming**: data and answers in, rules out.",
                    "**Three required ingredients** — inputs, example outputs, and a measure "
                    "of quality. The third goes missing most often.",
                    "**\"Deep\" means many layers of representation**, not deeper understanding.",
                    "**Weights, loss, backpropagation** — the training loop chapter 2 takes apart.",
                    "**The achievements are real; the forecasts have repeatedly not been.** "
                    "This is cognitive automation, not yet intelligence.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_the_ml_paradigm.ipynb",
                     "href": "../../course-slides/notebooks/ch01/01_the_ml_paradigm.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 2 — Mathematical building blocks",
                     "href": "../ch02/index.html"},
                    {"k": "BOOK CODE", "ic": "⌥", "v": "fchollet/deep-learning-with-python-notebooks",
                     "href": BOOK["code_repo"]},
                ]},
            ],
            "notes": "If time runs out, these six lines are the ones to read aloud.",
        },
    ],
}
