# -*- coding: utf-8 -*-
"""Chapter 20 — Conclusions.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 20
(pp. 595-608), read from the book PDF.

The synthesis deck. Everything the course has covered, arranged so that a
participant who has forgotten the details can still reconstruct the decisions:
which architecture for which data, what the workflow is, what the limits are,
and where to go next.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_NESTING = """
flowchart TB
  AI["<b>Artificial intelligence</b><br/><small>all attempts to automate human<br/>cognitive processes -- from a<br/>spreadsheet to a humanoid robot</small>"]
  ML["<b>Machine learning</b><br/><small>developing programs purely from<br/>exposure to training data</small>"]
  DL["<b>Deep learning</b><br/><small>long chains of geometric<br/>transformations, structured as layers</small>"]
  GEN["<b>Generative AI</b><br/><small>self-supervised, billions of<br/>parameters, samples new inputs</small>"]
  AI --> ML --> DL --> GEN
"""

MMD_LEARNING = """
flowchart LR
  D["Training data"]
  L["<b>Layers</b><br/><small>parameterized by weights</small>"]
  P["Predictions"]
  LOSS["<b>Loss function</b><br/><small>measures how wrong</small>"]
  G["<b>Gradient descent</b><br/><small>the chain is differentiable</small>"]
  D --> L --> P --> LOSS --> G
  G -- "update the weights" --> L
"""

MMD_UNCRUMPLE = """
flowchart LR
  A["<b>Crumpled paper ball</b><br/><small>the manifold of the input data</small>"]
  B["One movement<br/><small>= one layer's simple<br/>geometric transformation</small>"]
  C["The full gesture sequence<br/><small>= the model's complex<br/>transformation</small>"]
  D["<b>An uncrumpled sheet</b><br/><small>the target space</small>"]
  A --> B --> C --> D
"""

MMD_ENABLERS = """
flowchart TB
  ALG["<b>Algorithmic innovation</b><br/><small>two decades from backpropagation,<br/>then accelerating after 2012;<br/>the Transformer in 2017</small>"]
  DATA["<b>Large amounts of data</b><br/><small>a by-product of the consumer internet<br/>and Moore's law for storage</small>"]
  HW["<b>Cheap parallel hardware</b><br/><small>gaming GPUs, then chips designed<br/>for deep learning from the ground up</small>"]
  SW["<b>A software stack</b><br/><small>CUDA, TensorFlow / JAX / PyTorch<br/>for autodiff, Keras for access</small>"]
  R["<b>The revolution</b><br/><small>slowly at first, and then suddenly</small>"]
  ALG --> R
  DATA --> R
  HW --> R
  SW --> R
"""

MMD_WORKFLOW = """
flowchart TB
  A["<b>1. Define the problem</b><br/><small>what data, what prediction?</small>"]
  B["<b>2. Choose a measure of success</b><br/><small>often domain-specific</small>"]
  C["<b>3. Prepare the validation process</b><br/><small>train / validation / test,<br/>with no label leakage</small>"]
  D["<b>4. Vectorize and preprocess</b>"]
  E["<b>5. Beat a common-sense baseline</b><br/><small>this may not be possible</small>"]
  F["<b>6. Overfit, then regularize</b><br/><small>tune on validation only</small>"]
  G["<b>7. Deploy and monitor</b><br/><small>findings feed the next iteration</small>"]
  A --> B --> C --> D --> E --> F --> G
  G -. "refine" .-> A
"""

MMD_LIMITS = """
flowchart TB
  P["<b>Vast interpolative databases<br/>of patterns</b>"]
  S["Pattern-matching strength"]
  W["<b>...is also the core weakness</b>"]
  W1["Struggle to adapt<br/>to <b>novelty</b>"]
  W2["Sensitive to <b>phrasing</b><br/>and other distractors"]
  W3["Cannot learn generalizable<br/><b>algorithms</b>"]
  P --> S --> W
  W --> W1
  W --> W2
  W --> W3
"""

MMD_AHEAD = """
flowchart TB
  H["<b>Hybrid models</b><br/><small>learned algorithmic modules for<br/>reasoning + deep learning modules<br/>for perception</small>"]
  G["<b>Guided program search</b><br/><small>deep learning intuition navigating<br/>combinatorial program space</small>"]
  M["<b>Modular recombination<br/>and lifelong learning</b><br/><small>libraries of reusable components,<br/>fetched and recombined on the fly</small>"]
  T["<b>Human-like fluid intelligence</b><br/><small>continuous pattern recognition +<br/>discrete symbolic programs +<br/>on-the-fly adaptation</small>"]
  H --> T
  G --> T
  M --> T
"""

MMD_KEEPGOING = """
flowchart LR
  K["<b>Kaggle</b><br/><small>practice on real problems;<br/>tuning, ensembling, and<br/>avoiding validation overfitting</small>"]
  A["<b>arXiv</b><br/><small>the field publishes in the open,<br/>before peer review</small>"]
  E["<b>The Keras ecosystem</b><br/><small>keras.io guides and examples,<br/>the source, KerasHub</small>"]
  Y["<b>Your next model</b>"]
  K --> Y
  A --> Y
  E --> Y
"""

NB = []

DECK = {
    "id": "ch20",
    "kind": "chapter",
    "number": 20,
    "title": "Conclusions",
    "subtitle": "Everything this course covered, arranged so you can reconstruct the "
                "decisions rather than remember the details — and where to go next.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 20",
    "source_url": chapter_url(20),
    "duration": "2 hours (1 session)",
    "presenter": [
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    ],
    "resources": chapter_resources(20),
    "objectives": [
        "Place **AI, machine learning, deep learning, and generative AI** correctly "
        "inside one another.",
        "State in one paragraph **what a deep learning model is** and how learning "
        "happens.",
        "Name the **four enabling factors** behind the current revolution, and why "
        "no single one of them explains it.",
        "Run the **universal workflow** from problem definition to deployment, and "
        "say what each step protects against.",
        "Pick the right **architecture family** for a given pair of input and output "
        "modalities.",
        "Write the correct **final layer, activation, and loss** for each of the five "
        "standard task types from memory.",
        "State the **three structural limitations** honestly to a non-technical "
        "stakeholder.",
        "Keep learning after this course: **Kaggle, arXiv, and the Keras ecosystem**.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "Key concepts in review",
         "lead": "If you ever need a quick refresher, this is the section to reread."},

        {
            "type": "slide",
            "kicker": "Section 20.1.1",
            "title": "Four terms, nested inside one another",
            "blocks": [
                {"t": "p", "md": "Deep learning is not synonymous with artificial intelligence, "
                                 "or even with machine learning. The distinctions matter, and "
                                 "they are routinely blurred in public discussion."},
                {"t": "mmd", "id": "ch20-nesting", "src": MMD_NESTING,
                 "cap": "Each term is a proper subset of the one above it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.1 · the definitions",
            "title": "Said precisely",
            "blocks": [
                {"t": "table",
                 "head": ["Term", "Definition"],
                 "widths": [24, 76],
                 "rows": [
                     ["**AI**",
                      "An ancient, broad field: **all attempts to automate human cognitive "
                      "processes** — from an Excel spreadsheet to a humanoid robot."],
                     ["**Machine learning**",
                      "Automatically developing programs (**models**) purely from exposure to "
                      "training data. Took off in the 1990s, dominant by the 2000s."],
                     ["**Deep learning**",
                      "Models that are **long chains of geometric transformations**, structured "
                      "into layers parameterized by weights."],
                     ["**Generative AI**",
                      "Deep learning models that generate text, images, video, or sound — very "
                      "large, trained **self-supervised** to reconstruct corrupted input."],
                 ]},
                {"t": "p", "md": "The self-supervised objective is what lets generative models "
                                 "learn sophisticated **maps of their input space** — embedding "
                                 "manifolds that can then be sampled from."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.2",
            "title": "Why deep learning is not on equal footing with the alternatives",
            "blocks": [
                {"t": "p", "md": "In a few years, deep learning achieved breakthroughs across "
                                 "tasks historically perceived as extremely difficult — "
                                 "especially **machine perception**: extracting useful "
                                 "information from images, video, and sound."},
                {"t": "p", "md": "Given sufficient training data, appropriately labelled, deep "
                                 "learning can extract from perceptual data **almost anything a "
                                 "human could**. It is sometimes said to have *solved perception* "
                                 "— true only for a fairly narrow definition of perception."},
                {"t": "band", "md": "This singlehandedly brought about the **third and by far the "
                                    "largest AI summer**: a period of intense interest, "
                                    "investment, and hype. We are in the middle of it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.2 · why this summer is different",
            "title": "The hype may recede; the impact will not",
            "blocks": [
                {"t": "p", "md": "In stark contrast with previous AI summers, deep learning has "
                                 "provided **enormous business value** to companies large and "
                                 "small, and become a consumer success: human-level speech "
                                 "recognition, chatbot assistants, photorealistic image "
                                 "generation, human-level machine translation."},
                {"t": "quote", "md": "Deep learning could be analogous to **the internet**: "
                                     "overly hyped for a few years, but in the longer term still "
                                     "a major revolution that will transform our economy and "
                                     "our lives.",
                 "cite": "Section 20.1.2"},
                {"t": "band", "md": "One reason for optimism: **even with no further technological "
                                    "progress in the next decade, deploying existing algorithms "
                                    "to every applicable problem would be a game changer for most "
                                    "industries.** Short-term expectations are overoptimistic; "
                                    "the full deployment will likely take decades."},
            ],
            "notes": "This is the framing to give a professional audience about their own "
                     "roadmap. The value is not in waiting for the next model — it is in "
                     "applying what already exists to problems nobody has applied it to yet.",
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.3",
            "title": "The most surprising thing is how simple it is",
            "blocks": [
                {"t": "p", "md": "Fifteen years ago nobody expected such results on machine "
                                 "perception and natural language from **simple parametric "
                                 "models trained with gradient descent**. It turns out all you "
                                 "need is sufficiently large models, trained on sufficiently many "
                                 "examples."},
                {"t": "quote", "md": "*\"It's not complicated, it's just a lot of it.\"*",
                 "cite": "Richard Feynman, on the universe — quoted in section 20.1.3"},
                {"t": "mmd", "id": "ch20-learning", "src": MMD_LEARNING,
                 "cap": "The knowledge of a model is stored in its weights; learning is finding "
                        "good values for them."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.3",
            "title": "In deep learning, everything is a vector",
            "blocks": [
                {"t": "p", "md": "Inputs and targets are first **vectorized** — turned into an "
                                 "input vector space and a target vector space. Each layer "
                                 "operates one simple geometric transformation. Together the "
                                 "chain forms one complex transformation, broken into simple "
                                 "steps."},
                {"t": "p", "md": "That transformation must be **differentiable**, which is what "
                                 "lets gradient descent learn its parameters. Intuitively: the "
                                 "morphing from inputs to outputs must be **smooth and "
                                 "continuous** — a significant constraint, and the source of "
                                 "every limitation in chapter 19."},
                {"t": "mmd", "id": "ch20-uncrumple", "src": MMD_UNCRUMPLE,
                 "cap": "Deep learning models are mathematical machines for uncrumpling "
                        "complicated manifolds of high-dimensional data."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.3 · the two core ideas",
            "title": "Meaning as geometry",
            "blocks": [
                {"t": "lead", "md": "The whole thing hinges on two ideas: that **meaning derives "
                                    "from the pairwise relationships between things** — words in "
                                    "a language, pixels in an image — and that **those "
                                    "relationships can be captured by a distance function**."},
                {"t": "p", "md": "Whether the brain implements meaning via geometric spaces is an "
                                 "entirely separate question. Vector spaces are computationally "
                                 "efficient, but other data structures for intelligence are "
                                 "easily envisioned — **graphs** in particular."},
                {"t": "p", "md": "Neural networks originally emerged from the idea of using "
                                 "graphs to encode meaning; the surrounding field was called "
                                 "**connectionism**. That is the only reason for the name today."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.3 · a naming complaint worth taking seriously",
            "title": "They are neither neural nor networks",
            "blocks": [
                {"t": "band", "md": "*Neural network* exists **purely for historical reasons**. "
                                    "It is an extremely misleading name — these are neither "
                                    "neural nor networks, and they have ==hardly anything to do "
                                    "with the brain==.", "style": "amber"},
                {"t": "p", "md": "More appropriate names, all of which emphasise that continuous "
                                 "geometric space manipulation is at the core:"},
                {"t": "bullets", "items": [
                    "**Layered representations learning**",
                    "**Hierarchical representations learning**",
                    "**Deep differentiable models**",
                    "**Chained geometric transforms**",
                ]},
                {"t": "p", "md": "This is not pedantry. The brain metaphor is precisely what "
                                 "invites the anthropomorphizing that chapter 19 warned against."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.4",
            "title": "Four enabling factors, no single breakthrough",
            "blocks": [
                {"t": "p", "md": "The revolution did not start with one invention. Like any "
                                 "revolution it is the product of an accumulation of enabling "
                                 "factors — **slowly at first, and then suddenly**."},
                {"t": "mmd", "id": "ch20-enablers", "src": MMD_ENABLERS,
                 "cap": "Remove any one of the four and the last decade does not happen."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.4 · two details worth keeping",
            "title": "Where the data and the hardware came from",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🌐", "h": "The data", "style": "accent",
                     "p": "A by-product of the **consumer internet** and Moore's law applied to "
                          "storage media. Today, state-of-the-art language models are trained on "
                          "**a large fraction of the entire internet**."},
                    {"ico": "🎮", "h": "The hardware", "style": "accent",
                     "p": "First **gaming GPUs**, then chips designed from the ground up for "
                          "deep learning. NVIDIA's CEO took note of the boom early and bet the "
                          "company's future on it."},
                ]},
                {"t": "p", "md": "And on top of both, a stack of software: **CUDA**, then "
                                 "**TensorFlow, JAX, and PyTorch** doing automatic "
                                 "differentiation, then **Keras** making the whole thing "
                                 "accessible to most people."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.4 · the direction of travel",
            "title": "A tool in every developer's toolbox",
            "blocks": [
                {"t": "lead", "md": "In the future, deep learning will not be used only by "
                                    "researchers and engineers with an academic profile. **It "
                                    "will be a tool in the toolbox of every developer, much like "
                                    "web technology today.**"},
                {"t": "p", "md": "Everyone needs to build intelligent apps. Just as every business "
                                 "today needs a website, **every product will need to "
                                 "intelligently make sense of user-generated data**."},
                {"t": "p", "md": "Bringing that about requires tools that make deep learning "
                                 "radically easy to use and accessible to anyone with basic "
                                 "coding ability. ==Keras has been the first major step in that "
                                 "direction==, and it is why this course is taught in it."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "The universal workflow",
         "lead": "The hard part is everything before the model, and everything after it."},

        {
            "type": "slide",
            "kicker": "Section 20.1.5",
            "title": "Keras cannot help you with the hard part",
            "blocks": [
                {"t": "p", "md": "Having an extremely powerful tool for mapping any input space "
                                 "to any target space is great. But the difficult part of the "
                                 "workflow is **often everything that comes before** designing "
                                 "and training the model — and for production models, everything "
                                 "that comes after."},
                {"t": "band", "md": "Understanding the problem domain well enough to determine "
                                    "**what to predict, from what data, and how to measure "
                                    "success** is a prerequisite for any successful application. "
                                    "==It is not something advanced tools can help you with.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.5 · from chapter 6",
            "title": "The workflow, end to end",
            "blocks": [
                {"t": "mmd", "id": "ch20-workflow", "src": MMD_WORKFLOW,
                 "cap": "Seven steps, of which only one is about the model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.5",
            "title": "What each step protects against",
            "blocks": [
                {"t": "table",
                 "head": ["Step", "The failure it prevents"],
                 "widths": [34, 66],
                 "rows": [
                     ["Define the problem",
                      "Building a model for a prediction nobody needs, or that the data cannot "
                      "support."],
                     ["Choose a measure of success",
                      "Optimizing a convenient number instead of a useful one — the shortcut "
                      "rule from chapter 19."],
                     ["Prepare the validation process",
                      "**Label leakage.** With temporal prediction, validation and test data "
                      "must be *posterior* to the training data."],
                     ["Beat a common-sense baseline",
                      "Spending months on a problem where machine learning does not work at all."],
                     ["Overfit, then regularize",
                      "Regularizing a model that was never big enough to fit the data in the "
                      "first place."],
                     ["Keep a separate test set",
                      "**Validation-set overfitting** from hyperparameter tuning. This is the "
                      "entire purpose of the third split."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.5 · the step people skip",
            "title": "Deployment is part of the workflow, not after it",
            "blocks": [
                {"t": "p", "md": "Deploy the final model in production — as a web API, inside a "
                                 "JavaScript or C++ application, on an embedded device."},
                {"t": "lead", "md": "Then **keep monitoring its performance on real-world data**, "
                                    "and use those findings to refine the next iteration."},
                {"t": "p", "md": "The arrow from deployment back to problem definition is the "
                                 "one that turns a project into a system. Chapter 19's warning "
                                 "about distribution shift is not a research concern: "
                                 "**production data drifts away from your training set from the "
                                 "day you ship.**"},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "Key network architectures",
         "lead": "An architecture encodes assumptions about the structure of the data."},

        {
            "type": "slide",
            "kicker": "Section 20.1.6",
            "title": "An architecture is a hypothesis space",
            "blocks": [
                {"t": "lead", "md": "A network architecture **encodes assumptions about the "
                                    "structure of the data** — a hypothesis space within which "
                                    "the search for a good model proceeds."},
                {"t": "p", "md": "Whether an architecture works on a problem depends **entirely** "
                                 "on the match between the structure of the data and the "
                                 "assumptions of the architecture. That is the single question "
                                 "to ask when choosing one."},
                {"t": "band", "md": "These types combine easily into larger multimodal models. "
                                    "**Deep learning layers are LEGO bricks for information "
                                    "processing.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · table 20.1",
            "title": "Input, output, architecture",
            "blocks": [
                {"t": "table",
                 "head": ["Input", "Output", "Model"],
                 "widths": [30, 40, 30],
                 "rows": [
                     ["Vector data", "Class probability, regression value",
                      "**Densely connected network**"],
                     ["Timeseries data", "Class probability, regression value",
                      "**RNN, Transformer**"],
                     ["Images", "Class probability, regression value", "**ConvNet**"],
                     ["Text", "Class probability, regression value", "**Transformer**"],
                     ["Text, images", "Text", "**Transformer**"],
                     ["Text, images", "Images", "**VAE, diffusion model**"],
                 ]},
                {"t": "p", "md": "Six rows covering the whole course. If you remember nothing "
                                 "else from this deck, **remember this table** — it turns a "
                                 "vague problem statement into a starting architecture."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · densely connected networks",
            "title": "No assumed structure at all",
            "blocks": [
                {"t": "p", "md": "A stack of `Dense` layers, for vector data where each sample is "
                                 "a vector of numerical or categorical attributes. They assume "
                                 "**no specific structure** in the input features — every unit "
                                 "connects to every other, so the layer maps relationships "
                                 "between **any** two features."},
                {"t": "p", "md": "Contrast a 2D convolution layer, which only looks at **local** "
                                 "relationships. The absence of assumptions is both the strength "
                                 "and the weakness."},
                {"t": "p", "md": "They are also the **final classification or regression stage** "
                                 "of most networks: the ConvNets of chapter 8 and the recurrent "
                                 "networks of chapter 13 all end in one or two `Dense` layers."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · the five endings",
            "title": "Last layer, activation, and loss — from memory",
            "blocks": [
                {"t": "table",
                 "head": ["Task", "Last layer", "Loss"],
                 "widths": [32, 34, 34],
                 "rows": [
                     ["**Binary classification**", "`Dense(1, activation=\"sigmoid\")`",
                      "`binary_crossentropy`"],
                     ["**Single-label, multiclass**",
                      "`Dense(n, activation=\"softmax\")`",
                      "`categorical_crossentropy` (one-hot targets)"],
                     ["**Single-label, integer targets**",
                      "`Dense(n, activation=\"softmax\")`",
                      "`sparse_categorical_crossentropy`"],
                     ["**Multilabel, multiclass**",
                      "`Dense(n, activation=\"sigmoid\")`",
                      "`binary_crossentropy` (k-hot targets)"],
                     ["**Regression**", "`Dense(n)` — **no activation**",
                      "`mean_squared_error`"],
                 ]},
                {"t": "band", "md": "The multilabel row is the one people get wrong. **Sigmoid, "
                                    "not softmax** — softmax forces the outputs to sum to one, "
                                    "which is exactly what you do not want when a sample can "
                                    "have several classes.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · densely connected networks",
            "title": "The same three lines, three different endings",
            "blocks": [
                {"t": "p", "md": "The body of the network is identical in all three cases. Only "
                                 "the last layer and the loss change."},
                {"t": "code", "lang": "python", "file": "binary classification", "src": """inputs = keras.Input(shape=(num_input_features,))
x = layers.Dense(32, activation="relu")(inputs)
x = layers.Dense(32, activation="relu")(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)
model.compile(optimizer="rmsprop", loss="binary_crossentropy")"""},
                {"t": "code", "lang": "python", "file": "single-label multiclass", "src": """outputs = layers.Dense(num_classes, activation="softmax")(x)
model = keras.Model(inputs, outputs)
model.compile(optimizer="rmsprop", loss="categorical_crossentropy")"""},
                {"t": "p", "md": "Targets should be **0 or 1** for the first, **one-hot** for the "
                                 "second — or integers, with `sparse_categorical_crossentropy`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · Transformers",
            "title": "A sequence-to-sequence Transformer, from KerasHub layers",
            "blocks": [
                {"t": "p", "md": "Everything chapter 15 built by hand exists as a layer. This "
                                 "shape covers machine translation and question answering alike."},
                {"t": "code", "lang": "python", "src": """from keras_hub.layers import TokenAndPositionEmbedding
from keras_hub.layers import TransformerDecoder, TransformerEncoder

encoder_inputs = keras.Input(shape=(src_seq_length,), dtype="int64")
x = TokenAndPositionEmbedding(vocab_size, src_seq_length, embed_dim)(
    encoder_inputs
)
encoder_outputs = TransformerEncoder(intermediate_dim, num_heads)(x)

decoder_inputs = keras.Input(shape=(tgt_seq_length,), dtype="int64")
x = TokenAndPositionEmbedding(vocab_size, tgt_seq_length, embed_dim)(
    decoder_inputs
)
x = TransformerDecoder(intermediate_dim, num_heads)(x, encoder_outputs)
decoder_outputs = layers.Dense(vocab_size, activation="softmax")(x)

transformer = keras.Model([encoder_inputs, decoder_inputs], decoder_outputs)"""},
                {"t": "p", "md": "`TokenAndPositionEmbedding` is the tied token-plus-position "
                                 "layer from chapters 15 and 16. **If you are processing a single "
                                 "sequence, delete the decoder half** and keep the encoder."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · ConvNets",
            "title": "The same transformation, applied everywhere",
            "blocks": [
                {"t": "p", "md": "Convolution layers look at **spatially local patterns** by "
                                 "applying the same geometric transformation to different patches "
                                 "of an input tensor. The result is **translation invariant**, "
                                 "which makes convolution layers highly data efficient and "
                                 "modular."},
                {"t": "p", "md": "The idea applies to any dimensionality: `Conv1D` for continuous "
                                 "sequences, `Conv2D` for images, `Conv3D` for volumes. "
                                 "`SeparableConv2D` is a leaner, more efficient alternative."},
                {"t": "p", "md": "ConvNets are stacks of convolution and pooling layers. Pooling "
                                 "**downsamples spatially** — required to keep feature maps a "
                                 "reasonable size as feature counts grow, and to let later "
                                 "convolutions see a greater spatial extent."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · ConvNets",
            "title": "A typical image classifier, and what to add when it goes deep",
            "blocks": [
                {"t": "p", "md": "Four separable convolutions, one pooling stage, a global pool, "
                                 "and a dense head."},
                {"t": "code", "lang": "python", "src": """inputs = keras.Input(shape=(height, width, channels))
x = layers.SeparableConv2D(32, 3, activation="relu")(inputs)
x = layers.SeparableConv2D(64, 3, activation="relu")(x)
x = layers.MaxPooling2D(2)(x)
x = layers.SeparableConv2D(64, 3, activation="relu")(x)
x = layers.SeparableConv2D(128, 3, activation="relu")(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(32, activation="relu")(x)
outputs = layers.Dense(num_classes, activation="softmax")(x)
model = keras.Model(inputs, outputs)"""},
                {"t": "p", "md": "The `GlobalAveragePooling2D` turns spatial feature maps into "
                                 "vectors, which the `Dense` layers then classify. When building "
                                 "a **very deep** ConvNet, add **batch normalization** and "
                                 "**residual connections** — the two patterns from chapter 9 "
                                 "that keep gradient information flowing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · Transformers",
            "title": "Context awareness for a set of vectors",
            "blocks": [
                {"t": "p", "md": "A Transformer looks at a **set** of vectors and uses neural "
                                 "attention to transform each into a representation that is aware "
                                 "of the context provided by the others."},
                {"t": "p", "md": "When the set is an ordered sequence, **positional encoding** "
                                 "adds order awareness — giving a model that handles both global "
                                 "context and word order, and processes long paragraphs far more "
                                 "effectively than RNNs or 1D ConvNets."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📥", "h": "TransformerEncoder", "style": "accent",
                     "p": "Turns an input vector sequence into a **context-aware, order-aware** "
                          "output sequence. If you are processing a single sequence, this is all "
                          "you need."},
                    {"ico": "📤", "h": "TransformerDecoder", "style": "accent",
                     "p": "Takes the encoder output **and** a target sequence, and predicts what "
                          "comes next in the target."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.1.6 · the remaining families",
            "title": "RNNs, VAEs, and diffusion models",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔁", "h": "Recurrent networks", "style": "",
                     "p": "Process sequences one step at a time, carrying state forward. Still "
                          "the natural fit for **timeseries** — chapter 13 showed a small GRU "
                          "beating a much larger model."},
                    {"ico": "🎛", "h": "VAEs", "style": "",
                     "p": "Encode to a **distribution** rather than a point, giving a continuous, "
                          "structured latent space. Good where control and interpretability "
                          "matter more than fidelity."},
                    {"ico": "🌫", "h": "Diffusion models", "style": "accent",
                     "p": "A denoising autoencoder **in a loop**, turning pure noise into an "
                          "image. Behind nearly every commercial image generator today."},
                ]},
                {"t": "p", "md": "All of these combine. A multimodal model splices an image "
                                 "encoder's output into a text sequence; a text-to-image model "
                                 "feeds a Transformer's embeddings to a diffusion denoiser. "
                                 "**The bricks fit together.**"},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "04", "title": "Limitations, and what might lie ahead",
         "lead": "State these plainly. They are the most useful thing you can tell a "
                 "stakeholder."},

        {
            "type": "slide",
            "kicker": "Section 20.2",
            "title": "Strength and weakness are the same property",
            "blocks": [
                {"t": "p", "md": "Layers plug together to map essentially anything to anything — "
                                 "given appropriate training data, and given that the mapping is "
                                 "achievable by a **continuous geometric transformation of "
                                 "reasonable complexity**."},
                {"t": "mmd", "id": "ch20-limits", "src": MMD_LIMITS,
                 "cap": "Here is the catch: the mapping is often not learnable in a way that "
                        "generalizes."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.2 · the three limits, for a stakeholder",
            "title": "How to say this without hedging",
            "blocks": [
                {"t": "steps", "items": [
                    "**They struggle to adapt to novelty.** Parameters are fixed after training, "
                    "so the model can only retrieve or replicate patterns similar to its "
                    "training data. Outside that distribution, performance degrades drastically "
                    "— *no matter how simple the underlying task*.",
                    "**They are sensitive to phrasing and other distractors.** Minor rewording "
                    "in a prompt, or imperceptible perturbation in an image, changes the answer "
                    "— which indicates the absence of robust, human-like understanding.",
                    "**They often cannot learn generalizable algorithms.** The continuous, "
                    "geometric nature of these models makes them ill-suited to exact, discrete, "
                    "step-by-step procedures. They approximate such processes by interpolation.",
                ]},
                {"t": "band", "md": "And always resist the temptation to anthropomorphize. "
                                    "Performance is built on **pointwise statistical patterns**, "
                                    "not human-like experiential grounding — which is why it is "
                                    "brittle at any deviation from the training data.",
                 "style": "rose"},
            ],
            "notes": "This slide is the one to rehearse. Being able to state these three limits "
                     "calmly, without either overselling or dismissing the technology, is the "
                     "most valuable professional skill this course teaches.",
        },

        {
            "type": "slide",
            "kicker": "Section 20.2 · where scaling got us",
            "title": "Five years of exponential scaling, and an open problem",
            "blocks": [
                {"t": "p", "md": "The narrative that scaling model size and data would produce "
                                 "general intelligence has proven **insufficient**. Scaling "
                                 "improves benchmarks that amount to memorization tests; it does "
                                 "not address limits that stem from **fitting static, "
                                 "interpolative curves to data**."},
                {"t": "p", "md": "By 2024 this spurred the transition to **test-time adaptation** "
                                 "— search or fine-tuning during inference. It yielded major "
                                 "breakthroughs, including o3 surpassing the human baseline on "
                                 "ARC-AGI-1."},
                {"t": "band", "md": "But **at extreme computational cost**. Efficient, human-like "
                                    "adaptation remains a completely open problem, and the "
                                    "slightly harder **ARC-AGI-2 remains completely unsolved**. "
                                    "==We still need conceptual advances beyond scaling or "
                                    "brute-force search.==", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.3",
            "title": "Three developments worth watching",
            "blocks": [
                {"t": "mmd", "id": "ch20-ahead", "src": MMD_AHEAD,
                 "cap": "Deep learning excels at value-centric abstraction and lacks "
                        "program-centric abstraction. Human intelligence integrates both."},
                {"t": "p", "md": "The last of the three is the one with the clearest analogy to "
                                 "software engineering: **libraries of reusable, modular "
                                 "components** acquired from experience, fetched and recombined "
                                 "into a model adapted to the situation at hand."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "05", "title": "Staying up to date",
         "lead": "What you learned here will not stay relevant forever."},

        {
            "type": "slide",
            "kicker": "Section 20.4",
            "title": "The field moves at a frenetic pace",
            "blocks": [
                {"t": "p", "md": "Modern deep learning is only a few years old, despite a long, "
                                 "slow prehistory stretching back decades. With exponentially "
                                 "increasing financial resources and research headcount since "
                                 "2013, the field is now moving very fast."},
                {"t": "lead", "md": "**What you have learned in this course will not stay relevant "
                                    "forever, and it is not all you will need for the rest of "
                                    "your career.**"},
                {"t": "mmd", "id": "ch20-keepgoing", "src": MMD_KEEPGOING,
                 "cap": "Three free resources, and what each one is actually good for."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.4.1",
            "title": "Kaggle: the only real way to learn is practice",
            "blocks": [
                {"t": "p", "md": "An array of constantly renewed data science competitions, many "
                                 "involving deep learning, prepared by companies wanting novel "
                                 "solutions to their hardest problems. Fairly large monetary "
                                 "prizes for top entrants."},
                {"t": "p", "md": "Participating in a few — perhaps as part of a team — makes you "
                                 "familiar with the practical side of the advanced practices in "
                                 "chapter 18:"},
                {"t": "bullets", "items": [
                    "**Hyperparameter tuning** at a scale where it actually matters.",
                    "**Avoiding validation-set overfitting** when the leaderboard is watching.",
                    "**Model ensembling**, and finding out first-hand that diversity beats "
                    "individual quality.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.4.2",
            "title": "arXiv: the field publishes in the open",
            "blocks": [
                {"t": "p", "md": "Deep learning research takes place **completely in the open**. "
                                 "Papers are freely accessible as soon as they are finalized, and "
                                 "much of the related software is open source."},
                {"t": "p", "md": "Researchers upload to arXiv shortly after completion, to plant a "
                                 "flag without waiting months for conference acceptance. **This "
                                 "is what lets the field move so fast** — every new finding is "
                                 "immediately available to build on."},
                {"t": "band", "md": "The downside: the sheer volume makes it impossible to skim, "
                                    "and papers are **not peer-reviewed**, so identifying what is "
                                    "both important and high quality is hard and getting harder. "
                                    "==Use Google Scholar to track publications by authors you "
                                    "trust.==", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 20.4.3",
            "title": "The Keras ecosystem",
            "blocks": [
                {"t": "p", "md": "With over **2.5 million users** as of early 2025 and still "
                                 "growing, Keras has a large ecosystem of tutorials, guides, and "
                                 "open source projects."},
                {"t": "links", "items": [
                    {"k": "DOCS", "ic": "📘", "v": "keras.io — the main reference",
                     "href": "https://keras.io"},
                    {"k": "GUIDES", "ic": "🧭", "v": "keras.io/guides — extensive developer guides",
                     "href": "https://keras.io/guides"},
                    {"k": "EXAMPLES", "ic": "💡", "v": "keras.io/examples — dozens of high-quality code examples",
                     "href": "https://keras.io/examples"},
                    {"k": "SOURCE", "ic": "🐙", "v": "github.com/keras-team/keras",
                     "href": "https://github.com/keras-team/keras"},
                    {"k": "HUB", "ic": "🧩", "v": "github.com/keras-team/keras-hub",
                     "href": "https://github.com/keras-team/keras-hub"},
                ]},
                {"t": "p", "md": "The examples in particular are worth reading before you write "
                                 "anything from scratch — most of what you need has a "
                                 "**maintained, tested reference implementation** there already."},
            ],
        },

        {
            "type": "slide",
            "kicker": "The course, in one view",
            "title": "Twenty chapters, six ideas",
            "blocks": [
                {"t": "table",
                 "head": ["Chapters", "The idea"],
                 "widths": [16, 84],
                 "rows": [
                     ["1-3", "**Learning is gradient descent on a differentiable chain of "
                      "geometric transformations.** Everything else is engineering."],
                     ["4-7", "**Generalization is the whole problem**, and the workflow exists "
                      "to protect it — splits, baselines, overfit-then-regularize."],
                     ["8-12", "**Structure in the data buys you assumptions in the "
                      "architecture.** Convolution is translation invariance made into a layer."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "The course, in one view",
            "title": "Twenty chapters, six ideas (2 of 2)",
            "blocks": [
                {"t": "table",
                 "head": ["Chapters", "The idea"],
                 "widths": [16, 84],
                 "rows": [
                     ["13-14", "**Order is a design decision.** Set or sequence is the question "
                      "every architecture answers differently."],
                     ["15-17", "**Attention turns correlation into proximity**, and interpolative "
                      "spaces generate both generalization and hallucination."],
                     ["18-20", "**Scale, precision, and honesty.** What each lever costs, and "
                      "what none of them fixes."],
                 ]},
                {"t": "p", "md": "The through-line from chapter 5 to chapter 19 is a single "
                                 "claim, restated at increasing scale: **these models "
                                 "interpolate**. Everything they do well and everything they do "
                                 "badly follows from that."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Common failure modes",
            "title": "Four mistakes that survive the whole course",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🕳", "h": "Label leakage into validation", "style": "bad",
                     "p": "Random splits on temporal data; preprocessing fitted on the full "
                          "dataset; `adapt()` called before the split. Every metric afterwards "
                          "is fiction."},
                    {"ico": "📉", "h": "Regularizing before overfitting", "style": "bad",
                     "p": "You cannot tell whether a model is too small or too regularized until "
                          "you have seen it **overfit once**. Get there first."},
                    {"ico": "🎯", "h": "A convenient metric, not a useful one", "style": "warn",
                     "p": "The shortcut rule applies to your project too. Netflix never shipped "
                          "the model that won its own competition."},
                    {"ico": "🗣", "h": "Anthropomorphizing the model", "style": "warn",
                     "p": "Believing the model *understands* leads directly to deploying it "
                          "where its distribution does not reach — and to being surprised."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Applying this after the course",
            "title": "Where to start, in your own organization",
            "blocks": [
                {"t": "steps", "items": [
                    "**Find a problem where the data already exists.** The workflow's first step "
                    "is the one most projects skip, and data collection is what kills most of "
                    "them.",
                    "**Write down the measure of success before the model.** If you cannot state "
                    "it in one sentence, the project is not ready.",
                    "**Build the common-sense baseline first.** It costs an afternoon and "
                    "occasionally ends the project — which is a good outcome, found early.",
                    "**Prefer a pretrained backbone.** Chapters 8, 15, and 16 all made the same "
                    "point: fine-tuning beats training from scratch, decisively.",
                    "**Plan for monitoring on day one.** Distribution shift is not a research "
                    "concern; it starts the day you deploy.",
                ]},
            ],
            "notes": "Close the technical part of the course here. This is the slide participants "
                     "will photograph.",
        },

        {
            "type": "slide",
            "kicker": "Section 20.5 · final words",
            "title": "Go on learning, questioning, and researching",
            "blocks": [
                {"t": "quote", "md": "Learning is a lifelong journey, especially in the field of "
                                     "AI, where we have far more unknowns on our hands than "
                                     "certitudes. So please go on learning, questioning, and "
                                     "researching. **Never stop.** Because even given the progress "
                                     "made so far, most of the fundamental questions in AI remain "
                                     "unanswered. **Many haven't even been properly asked yet.**",
                 "cite": "Chollet & Watson, Deep Learning with Python, closing words"},
                {"t": "links", "items": [
                    {"k": "BOOK", "ic": "📖", "v": "deeplearningwithpython.io",
                     "href": "https://deeplearningwithpython.io/"},
                    {"k": "MODULE", "ic": "🤖", "v": "Agentic AI — cases, tech stack, and demos",
                     "href": "../hendri-agentic/index.html"},
                ]},
            ],
        },
    ],
}
