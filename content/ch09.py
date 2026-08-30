# -*- coding: utf-8 -*-
"""Chapter 9 — ConvNet architecture patterns.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 9
(pp. 268-283), read from the book PDF.

Four best practices — modularity/hierarchy/reuse, residual connections, batch
normalisation, and depthwise separable convolutions — assembled into a mini
Xception that beats chapter 8's model with less than half the parameters.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402
from diagrams import depth_vs_width, residual  # noqa: E402


MMD_MHR = """
flowchart TB
  C["An amorphous soup<br/>of complexity"]
  M["<b>Modularity</b><br/>split it into modules"]
  H["<b>Hierarchy</b><br/>organise the modules"]
  R["<b>Reuse</b><br/>use the same module<br/>in several places"]
  S["A system you can<br/>reason about"]
  C --> M --> H --> R --> S
"""

MMD_VANISH = """
flowchart LR
  X["x"] --> F1["f1"] --> F2["f2"] --> F3["f3"] --> F4["f4"] --> Y["y"]
  Y -. "error signal" .-> F4
  F4 -. "+ noise" .-> F3
  F3 -. "+ more noise" .-> F2
  F2 -. "signal lost" .-> F1
"""

MMD_SEPARABLE = """
flowchart TB
  IN["Input feature map"]
  SP["Split channels"]
  D1["3 x 3 conv<br/>channel 1"]
  D2["3 x 3 conv<br/>channel 2"]
  D3["3 x 3 conv<br/>channel n"]
  CC["Concatenate"]
  PW["1 x 1 conv<br/><small>pointwise: mixes channels</small>"]
  OUT["Output feature map"]
  IN --> SP
  SP --> D1
  SP --> D2
  SP --> D3
  D1 --> CC
  D2 --> CC
  D3 --> CC
  CC --> PW --> OUT
"""

MMD_BLOCK = """
flowchart TB
  IN["Block input"]
  BN1["BatchNormalization"]
  A1["Activation relu"]
  S1["SeparableConv2D"]
  BN2["BatchNormalization"]
  A2["Activation relu"]
  S2["SeparableConv2D"]
  MP["MaxPooling2D<br/>stride 2"]
  ADD(("+"))
  OUT["Block output"]
  PROJ["Conv2D 1x1<br/>stride 2<br/><small>projects the residual</small>"]
  IN --> BN1 --> A1 --> S1 --> BN2 --> A2 --> S2 --> MP --> ADD --> OUT
  IN --> PROJ --> ADD
"""

MMD_VIT = """
flowchart TB
  Q{"How much data<br/>do you have?"}
  BIG["Vision Transformer<br/><small>better at using large data,<br/>captures long-range relations</small>"]
  SMALL["ConvNet<br/><small>spatial prior makes it<br/>far more data efficient</small>"]
  Q -- "massive, ImageNet scale or more" --> BIG
  Q -- "anything smaller" --> SMALL
"""


MMD_XCEPTION = """
flowchart TB
  I["299 x 299 x 3<br/>images"]
  E["Conv 32 stride 2<br/>Conv 64"]
  B1["Block 1<br/>SeparableConv 128 x2<br/>MaxPooling"]
  B2["Block 2<br/>SeparableConv 256 x2<br/>MaxPooling"]
  B3["Block 3<br/>SeparableConv 728 x2<br/>MaxPooling"]
  R1["Conv 1x1<br/>stride 2"]
  R2["Conv 1x1<br/>stride 2"]
  R3["Conv 1x1<br/>stride 2"]
  I --> E --> B1 --> B2 --> B3
  E --> R1 --> B2
  B1 --> R2 --> B3
  B2 --> R3 --> B3
"""

NB = ["01_residual_connections.ipynb", "02_batchnorm_and_separable.ipynb",
      "03_mini_xception.ipynb"]

DECK = {
    "id": "ch09",
    "kind": "chapter",
    "number": 9,
    "title": "ConvNet Architecture Patterns",
    "subtitle": "Four best practices that turn a working image model into a good "
                "one — and a mini Xception that beats the previous chapter's model "
                "with less than half the parameters.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 9",
    "source_url": chapter_url(9),
    "duration": "2.5 hours",
    "presenter": [
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    ],
    "resources": chapter_resources(9, local_notebooks=NB),
    "objectives": [
        "Explain architecture as a **choice of hypothesis space**, and why a good "
        "one reduces the search gradient descent has to do.",
        "Apply the **modularity–hierarchy–reuse** formula to read any published "
        "ConvNet.",
        "Explain the **vanishing gradient** problem and fix it with **residual "
        "connections**, including the 1×1 projection when shapes differ.",
        "Say what **batch normalisation** does, where to put it, and why "
        "`use_bias=False` accompanies it.",
        "Explain the assumption behind **depthwise separable convolutions**, and "
        "why they are not faster on a GPU despite using far fewer parameters.",
        "Assemble all four into a **mini Xception**, and read the resulting "
        "parameter-count and accuracy change.",
        "Say when a **Vision Transformer** is the better choice, and when it is not.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "Architecture is the choice of hypothesis space",
            "blocks": [
                {"t": "p", "md": "A model's architecture is the sum of the choices that went "
                                 "into it: which layers, configured how, connected in what "
                                 "arrangement. Those choices **define the hypothesis space** "
                                 "— the set of functions gradient descent may search."},
                {"t": "band",
                 "md": "Like feature engineering, a good hypothesis space **encodes prior "
                       "knowledge**. Using convolution layers means you already know that "
                       "the relevant patterns are ==translation invariant=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "Why it is often the difference between success and failure",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🚫", "h": "Bad choices cannot be trained away",
                     "p": "The model gets stuck at suboptimal metrics, and **no amount of "
                          "training data will save it**.", "style": "bad"},
                    {"ico": "✅", "h": "Good choices multiply your data",
                     "p": "Learning accelerates and the model uses the available data "
                          "efficiently, **reducing the need for a large dataset**.",
                     "style": "good"},
                ]},
                {"t": "quote",
                 "md": "A good model architecture is one that reduces the size of the search "
                       "space, or otherwise makes it easier to converge to a good point of the "
                       "search space.",
                 "cite": "Chollet & Watson, chapter 9 introduction"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Introduction",
            "title": "An honest note about how this knowledge is held",
            "blocks": [
                {"t": "p", "md": "Model architecture is **more an art than a science**. "
                                 "Experienced engineers assemble high-performing models on "
                                 "the first try; beginners struggle to build one that trains "
                                 "at all."},
                {"t": "band", "style": "amber",
                 "md": "The keyword is *intuitively*: **no one can give you a clear "
                       "explanation of what works and what does not**. Experts rely on "
                       "pattern matching acquired through practice."},
                {"t": "p", "md": "But it is not *only* intuition. As in any engineering "
                                 "discipline there are **best practices**, and this chapter is "
                                 "four of them. Remember, too, that gradient descent is "
                                 "==a pretty stupid search process== — it needs all the help "
                                 "it can get."},
            ],
        },

        {"type": "section", "num": "01", "title": "Modularity, hierarchy, and reuse",
         "lead": "The universal recipe for making a complex system simpler."},

        {
            "type": "slide",
            "kicker": "Section 9.1",
            "title": "The MHR formula",
            "blocks": [
                {"t": "mmd", "id": "ch09-mhr", "src": MMD_MHR,
                 "cap": "Figure 9.1 — the same recipe underlies a cathedral, your body, a "
                        "navy, and the Keras codebase."},
                {"t": "p", "md": "Software engineers already know this: an effective codebase "
                                 "is modular, hierarchical, and does not reimplement the same "
                                 "thing twice. Following those principles **is** software "
                                 "architecture."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.1",
            "title": "Deep learning is that recipe applied to optimisation",
            "blocks": [
                {"t": "bullets", "items": [
                    "Take a classic optimisation technique — **gradient descent over a "
                    "continuous function space**.",
                    "Structure the search space into **modules**: layers.",
                    "Organise them into a **deep hierarchy** — often just a stack, the "
                    "simplest kind.",
                    "**Reuse** whatever you can: convolutions are entirely about reusing the "
                    "same information at ==different spatial locations==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.1",
            "title": "Two patterns visible in every published ConvNet",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🧱", "h": "Repeated blocks",
                     "p": "Popular architectures are structured not merely into layers but "
                          "into **repeated groups of layers** — *blocks* or *modules*. "
                          "Xception repeats a SeparableConv – SeparableConv – MaxPooling "
                          "block.", "style": "accent"},
                    {"ico": "🔺", "h": "A feature pyramid",
                     "p": "Filter count **grows with depth** while feature-map size **shrinks**. "
                          "You saw 32 → 64 → 128 in chapter 8; the same pattern runs through "
                          "Xception.", "style": "accent"},
                ]},
                {"t": "p", "md": "Once you can see those two patterns, most architecture "
                                 "diagrams in papers become readable at a glance."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.1 · figure 9.2",
            "title": "Xception, read with those two patterns",
            "blocks": [
                {"t": "mmd", "id": "ch09-xception", "src": MMD_XCEPTION,
                 "cap": "Repeated blocks, growing depth, and a 1x1 projection carrying each "
                        "residual across the downsampling."},
                {"t": "p", "md": "The spatial sizes fall 299 → 149 → 74 → 37 while the depth "
                                 "climbs 3 → 32 → 128 → 256 → 728. Everything else on this "
                                 "diagram is ==the same block, repeated=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Residual connections",
         "lead": "The game of telephone, and how to stop playing it."},

        {
            "type": "slide",
            "kicker": "Section 9.2",
            "title": "Backpropagation as a game of telephone",
            "blocks": [
                {"t": "p", "md": "A message whispered from player to player ends up bearing "
                                 "little resemblance to the original. Backpropagation through "
                                 "a deep chain has the same problem."},
                {"t": "mmd", "id": "ch09-vanish", "src": MMD_VANISH,
                 "cap": "Each successive function introduces noise into the error signal "
                        "travelling backwards."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.2",
            "title": "The vanishing gradient problem",
            "blocks": [
                {"t": "p", "md": "To adjust `f1` you must percolate error information back "
                                 "through `f2`, `f3`, and `f4`. Each step adds noise."},
                {"t": "band", "style": "rose",
                 "md": "If the chain is too deep, that noise **overwhelms the gradient "
                       "information** and backpropagation stops working. ==The model will not "
                       "train at all.=="},
                {"t": "p", "md": "The fix is to force each function in the chain to be "
                                 "**non-destructive** — to retain a noiseless version of what "
                                 "came in."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.2",
            "title": "A residual connection is an information shortcut",
            "blocks": [
                residual("ch09-residual", depth=5,
                         cap="Figure 9.3 — the same five blocks, with and without the "
                             "shortcut, and the two gradients they produce."),
                {"t": "p", "md": "Same blocks, same derivatives — and the gradient reaching "
                                 "block 1 is hundreds of times larger. Introduced in 2015 "
                                 "with **ResNet** (He et al., Microsoft)."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.2 · listing 9.1",
            "title": "Three lines, and one condition",
            "blocks": [
                {"t": "p", "md": "In code it is almost trivial. Save the input, run the block, "
                                 "add the two."},
                {"t": "code", "lang": "python", "file": "listing 9.1 — a residual connection",
                 "src": """x = ...                        # some input tensor
residual = x                   # save a reference: this is the residual
x = block(x)                   # this block may be destructive or noisy - fine
x = add([x, residual])         # the output now always retains the full input"""},
                {"t": "band", "style": "amber",
                 "md": "The condition: adding requires **the block output and the residual to "
                       "have the same shape**. That fails as soon as the block changes the "
                       "filter count or pools — which is ==most real blocks=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.2 · listing 9.2",
            "title": "Case 1 — the block changes the filter count",
            "blocks": [
                {"t": "p", "md": "Project the residual with a **1×1 convolution and no "
                                 "activation**. It is a purely linear reshaping of the channel "
                                 "dimension."},
                {"t": "code", "lang": "python", "file": "listing 9.2 — projecting the residual",
                 "src": """inputs = keras.Input(shape=(32, 32, 3))
x = layers.Conv2D(32, 3, activation="relu")(inputs)
residual = x                                            # 32 filters

x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)   # now 64 filters
residual = layers.Conv2D(64, 1)(residual)               # 1x1 projection to match

x = layers.add([x, residual])"""},
                {"t": "p", "md": "`padding=\"same\"` in the block avoids the spatial shrinkage "
                                 "a convolution would otherwise cause, ==keeping the two "
                                 "shapes aligned=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.2 · listing 9.3",
            "title": "Case 2 — the block pools",
            "blocks": [
                {"t": "p", "md": "If the block halves the spatial size, the projection must "
                                 "halve it too. That is what `strides=2` on the 1×1 "
                                 "convolution is for."},
                {"t": "code", "lang": "python", "file": "listing 9.3 — matching a max pooling layer",
                 "src": """inputs = keras.Input(shape=(32, 32, 3))
x = layers.Conv2D(32, 3, activation="relu")(inputs)
residual = x

x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)
x = layers.MaxPooling2D(2, padding="same")(x)           # halves the spatial size

residual = layers.Conv2D(64, 1, strides=2)(residual)    # halve the residual too
x = layers.add([x, residual])"""},
                {"t": "band",
                 "md": "So the rule is a pair: **`padding=\"same\"` inside the block, "
                       "`strides` on the projection** to match whatever downsampling the "
                       "block performs."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.3.2",
            "title": "The same budget, spent two ways",
            "blocks": [
                depth_vs_width(
                    "ch09-depth-width",
                    cap="Parameter counts are computed from the layer sizes shown, not "
                        "chosen to make the point."),
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.2",
            "title": "Why \"deep and narrow beats broad and shallow\"",
            "blocks": [
                {"t": "p", "md": "Residual connections are what make that principle usable. "
                                 "Without them, depth is limited by how far a gradient can "
                                 "travel before the noise swallows it."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📏", "h": "Broad and shallow",
                     "p": "Few layers, each very wide. Many parameters, but only one or two "
                          "levels of representation — closer to the *shallow learning* of "
                          "chapter 1.", "style": "warn"},
                    {"ico": "📐", "h": "Deep and narrow",
                     "p": "Many layers, each modest. A **long hierarchy of representations**, "
                          "which is what deep learning is for — and now trainable, thanks to "
                          "the shortcuts.", "style": "good"},
                ]},
            ],
        },

        {"type": "section", "num": "03", "title": "Batch normalization",
         "lead": "Normalising not just the input, but every intermediate activation."},

        {
            "type": "slide",
            "kicker": "Section 9.3",
            "title": "The question that motivates it",
            "blocks": [
                {"t": "p", "md": "You already normalise data before feeding it in. But "
                                 "normalisation may be a concern **after every transformation "
                                 "the network performs**."},
                {"t": "code", "lang": "python", "file": "the familiar normalisation",
                 "src": """normalized_data = (data - np.mean(data, axis=...)) / np.std(data, axis=...)"""},
                {"t": "band",
                 "md": "Even if the data entering a `Dense` or `Conv2D` layer has zero mean "
                       "and unit variance, there is **no reason to expect the same of what "
                       "comes out**. So: ==could normalising intermediate activations help?=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.3",
            "title": "What BatchNormalization does",
            "blocks": [
                {"t": "table",
                 "head": ["Phase", "What it normalises with"],
                 "widths": [22, 78],
                 "rows": [
                     ["**Training**", "The mean and variance of **the current batch**."],
                     ["**Inference**", "An **exponential moving average** of the batchwise "
                      "mean and variance seen during training — because a big enough "
                      "representative batch may not be available at inference time."],
                 ]},
                {"t": "p", "md": "That moving average is exactly the **non-trainable weight** "
                                 "chapter 7 mentioned: `BatchNormalization` is the only "
                                 "built-in Keras layer that has one."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.3",
            "title": "Nobody is quite sure why it works",
            "blocks": [
                {"t": "p", "md": "Ioffe and Szegedy's 2015 paper suggested it works by "
                                 "*reducing internal covariate shift*. **No one really knows "
                                 "for sure.** There are various hypotheses and no certainties."},
                {"t": "quote",
                 "md": "You'll find that this is true of many things in deep learning — deep "
                       "learning is not an exact science but a set of ever-changing, "
                       "empirically derived engineering best practices.",
                 "cite": "Chollet & Watson, section 9.3"},
                {"t": "band", "style": "amber",
                 "md": "Worth saying aloud in a classroom: **\"we use it because it "
                       "measurably helps\"** is a legitimate engineering answer, and it is "
                       "==the honest one here=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.3",
            "title": "Where to put it, and one detail that follows",
            "blocks": [
                {"t": "p", "md": "The convention is convolution → batch norm → activation, "
                                 "with the bias term switched off."},
                {"t": "code", "lang": "python", "file": "the usual ordering",
                 "src": """x = layers.Conv2D(32, 3, use_bias=False)(x)     # no bias here
x = layers.BatchNormalization()(x)
x = layers.Activation("relu")(x)"""},
                {"t": "band",
                 "md": "`use_bias=False` because batch normalisation **already centres the "
                       "output** — the layer's own bias term would be immediately subtracted "
                       "away, so it is ==pure waste=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.3",
            "title": "And why chapter 8 said not to unfreeze it",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "During fine-tuning, unfreezing a `BatchNormalization` layer lets its "
                       "moving statistics be overwritten by a **small, unrepresentative** "
                       "batch of your new data — undoing the calibration the pretrained model "
                       "arrived at."},
                {"t": "p", "md": "That is the reason behind the rule you were given in chapter "
                                 "8 without explanation. **Leave batch normalisation frozen "
                                 "when fine-tuning.**"},
            ],
        },

        {"type": "section", "num": "04", "title": "Depthwise separable convolutions",
         "lead": "A stronger prior, and far fewer parameters."},

        {
            "type": "slide",
            "kicker": "Section 9.4",
            "title": "The assumption it encodes",
            "blocks": [
                {"t": "p", "md": "Regular convolution assumes patterns are **not tied to "
                                 "specific locations**. Depthwise separable convolution adds a "
                                 "second assumption."},
                {"t": "band",
                 "md": "That **spatial locations in intermediate activations are highly "
                       "correlated, but different channels are highly independent**. That "
                       "holds generally for the representations deep networks learn, so it "
                       "serves as ==a useful prior=="},
                {"t": "p", "md": "And the general principle behind it: **a model with stronger "
                                 "priors about the structure of its information is a better "
                                 "model — as long as the priors are accurate.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.4",
            "title": "How the operation splits in two",
            "blocks": [
                {"t": "mmd", "id": "ch09-separable", "src": MMD_SEPARABLE,
                 "cap": "Figure 9.4 — a depthwise convolution (independent spatial convolutions "
                        "per channel) followed by a pointwise 1×1 convolution that mixes "
                        "channels."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.4",
            "title": "The parameter arithmetic",
            "blocks": [
                {"t": "p", "md": "Take a 3×3 window with 64 input channels and 64 output "
                                 "channels, and count the trainable parameters both ways."},
                {"t": "table",
                 "head": ["Operation", "Parameter count", "Arithmetic"],
                 "widths": [34, 24, 42],
                 "rows": [
                     ["Regular convolution", "**36,864**", "3 × 3 × 64 × 64"],
                     ["Depthwise separable", "**4,672**", "3 × 3 × 64 + 64 × 64"],
                 ]},
                {"t": "band",
                 "md": "Roughly **eight times fewer**, with comparable representational power "
                       "— and the gap ==widens as filters or windows get larger==. Smaller "
                       "models that converge faster and overfit less."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.4",
            "title": "So it must be much faster. It is not.",
            "blocks": [
                {"t": "p", "md": "On CPU, where the implementation is parallelised C++, you do "
                                 "see a meaningful speedup. On GPU you are not running a "
                                 "simple CUDA implementation — you are running a **cuDNN "
                                 "kernel optimised down to each machine instruction**."},
                {"t": "band", "style": "amber",
                 "md": "Despite repeated requests to NVIDIA, depthwise separable convolutions "
                       "have not received nearly the same optimisation effort, so they remain "
                       "**about as fast as regular convolutions** — while using "
                       "==quadratically fewer parameters and operations=="},
                {"t": "p", "md": "Use them anyway: the lower parameter count means less "
                                 "overfitting risk, and the channel-independence assumption "
                                 "gives faster convergence and more robust representations."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.4",
            "title": "The wider lesson: hardware, software, and algorithms co-evolve",
            "blocks": [
                {"t": "p", "md": "What is a slight inconvenience here becomes an impassable "
                                 "wall elsewhere. The entire ecosystem is micro-optimised for "
                                 "a **specific set of algorithms** — ConvNets trained by "
                                 "backpropagation."},
                {"t": "band", "style": "rose",
                 "md": "Experiment with gradient-free optimisation or spiking neural networks "
                       "and your first CUDA implementations would be **orders of magnitude "
                       "slower** than a plain ConvNet, ==no matter how good the idea==. "
                       "Convincing others to adopt it would be a hard sell even if it were "
                       "plainly better."},
                {"t": "p", "md": "GPUs and CUDA enabled backprop-trained ConvNets → NVIDIA "
                                 "optimised for them → the research community consolidated "
                                 "behind them. **Taking a different path now would require a "
                                 "multiyear re-engineering of the whole ecosystem.**"},
            ],
            "notes": "A good slide for a discussion about technology strategy: the winning "
                     "technique is partly the one that got optimised first.",
        },

        {"type": "section", "num": "05", "title": "Putting it together",
         "lead": "A mini Xception, from the four practices."},

        {
            "type": "slide",
            "kicker": "Section 9.5",
            "title": "The six principles, collected",
            "blocks": [
                {"t": "steps", "items": [
                    "Organise the model into **repeated blocks** of layers — usually several "
                    "convolutions plus a max pooling layer.",
                    "**Filter count should increase as feature-map size decreases.**",
                    "**Deep and narrow beats broad and shallow.**",
                    "**Residual connections** around blocks let you train deeper networks.",
                    "**Batch normalisation** after convolution layers is often beneficial.",
                    "**`SeparableConv2D` instead of `Conv2D`** is more parameter efficient.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.5",
            "title": "One block, with all four practices in it",
            "blocks": [
                {"t": "mmd", "id": "ch09-block", "src": MMD_BLOCK,
                 "cap": "Batch norm, separable convolution, pooling, and a projected residual "
                        "— repeated five times with growing depth."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.5",
            "title": "…and the whole model is a loop",
            "blocks": [
                {"t": "p", "md": "Because the block is uniform, the model is a `for` loop. "
                                 "Note the first layer, and why it is not separable."},
                {"t": "code", "lang": "python", "file": "the mini Xception",
                 "src": """inputs = keras.Input(shape=(180, 180, 3))
x = layers.Rescaling(1.0 / 255)(inputs)

# A REGULAR Conv2D first: the separable assumption ("channels are largely
# independent") is false for RGB - red, green and blue are highly correlated.
x = layers.Conv2D(filters=32, kernel_size=5, use_bias=False)(x)

for size in [32, 64, 128, 256, 512]:
    residual = x
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.SeparableConv2D(size, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.SeparableConv2D(size, 3, padding="same", use_bias=False)(x)
    x = layers.MaxPooling2D(3, strides=2, padding="same")(x)
    residual = layers.Conv2D(size, 1, strides=2, padding="same", use_bias=False)(residual)
    x = layers.add([x, residual])"""},
                {"t": "band", "style": "amber",
                 "md": "That first-layer detail is easy to miss and worth stating: "
                       "**separable convolutions are wrong for the raw RGB input**, because "
                       "==colour channels in natural images are strongly correlated=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.5",
            "title": "The result: fewer parameters, better accuracy",
            "blocks": [
                {"t": "stats", "cols": 2, "items": [
                    {"v": "721,857", "l": "trainable parameters, mini Xception"},
                    {"v": "1,569,089", "l": "trainable parameters, chapter 8's model"},
                ]},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "90.8%", "l": "test accuracy, mini Xception"},
                    {"v": "83.9%", "l": "test accuracy, chapter 8's model"},
                ]},
                {"t": "band",
                 "md": "**Less than half the parameters, seven points better.** Following "
                       "architecture best practices has ==an immediate, sizeable effect==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.5",
            "title": "And note what was not done",
            "blocks": [
                {"t": "p", "md": "No hyperparameter search was run. The configuration comes "
                                 "**purely from the best practices above**, plus a small "
                                 "amount of intuition about model size."},
                {"t": "band",
                 "md": "Systematic hyperparameter tuning is **chapter 18**. The point here is "
                       "that ==seven points were available before tuning even started=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.5",
            "title": "Reusing chapter 8's setup unchanged",
            "blocks": [
                {"t": "p", "md": "Only the model definition changed. Data loading, "
                                 "augmentation, callbacks, and the training call are exactly "
                                 "those from section 8.2 — which is the point of having built "
                                 "them properly once."},
                {"t": "code", "lang": "python", "file": "the unchanged surroundings",
                 "src": """x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.25)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)

model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
history = model.fit(augmented_train_dataset, epochs=100,
                    validation_data=validation_dataset, callbacks=callbacks)"""},
                {"t": "band",
                 "md": "A useful habit that falls out of this: **keep the data pipeline and "
                       "the model definition separable**, so architecture experiments cost "
                       "==one edit, not a rewrite=="},
            ],
        },

        {"type": "section", "num": "06", "title": "Beyond convolution",
         "lead": "Vision Transformers, and when they are the wrong choice."},

        {
            "type": "slide",
            "kicker": "Section 9.6",
            "title": "What a Vision Transformer does",
            "blocks": [
                {"t": "p", "md": "The Transformer was developed to process text — it is "
                                 "fundamentally a **sequence-processing** architecture "
                                 "(chapter 15). A ViT applies it to images."},
                {"t": "bullets", "items": [
                    "It **splits the image into a 1D sequence of patches**.",
                    "Each patch becomes a flat vector.",
                    "The vector sequence is processed like a sentence — which lets it capture "
                    "**long-range relationships** between distant parts of the image, "
                    "==something ConvNets can struggle with==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.6",
            "title": "When to reach for one",
            "blocks": [
                {"t": "mmd", "id": "ch09-vit", "src": MMD_VIT,
                 "cap": "The authors' general experience, stated as a decision."},
                {"t": "bullets", "items": [
                    "ViTs **lack the spatial prior** of ConvNets — the patch-based 2D "
                    "structure encodes assumptions about local visual structure, which makes "
                    "ConvNets more data efficient.",
                    "For ViTs to shine **they need to be really large**, which makes them "
                    "unwieldy for anything smaller than ImageNet.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 9.6",
            "title": "The state of the contest",
            "blocks": [
                {"t": "band",
                 "md": "**The battle for image recognition supremacy is far from over**, and "
                       "ViTs have opened a new chapter. It may be that they replace ConvNets "
                       "in the long term."},
                {"t": "p", "md": "You will most likely meet the architecture in **large-scale "
                                 "generative image models** — chapter 17. For small-scale "
                                 "classification, ==ConvNets remain the better bet=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**Architecture is a choice of hypothesis space** — it encodes prior "
                    "knowledge, and bad choices cannot be trained away.",
                    "**Modularity, hierarchy, reuse.** Repeated blocks, and a pyramid of "
                    "growing depth against shrinking size.",
                    "**Residual connections** defeat vanishing gradients; project with a 1×1 "
                    "convolution when shapes differ.",
                    "**Batch normalisation** after convolutions, with `use_bias=False` — and "
                    "leave it frozen when fine-tuning.",
                    "**Depthwise separable convolutions** encode a stronger prior with ~8× "
                    "fewer parameters, even though the GPU will not run them faster.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "…and the number worth remembering",
            "blocks": [
                {"t": "band",
                 "md": "Assembling those four practices into a mini Xception took the same "
                       "dogs-vs-cats problem from **83.9% to 90.8%** while ==halving the "
                       "parameter count== — before any hyperparameter tuning."},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_mini_xception.ipynb",
                     "href": "../../course-slides/notebooks/ch09/03_mini_xception.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 10 — Interpreting what ConvNets learn",
                     "href": "../ch10/index.html"},
                ]},
            ],
        },
    ],
}
