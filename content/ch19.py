# -*- coding: utf-8 -*-
"""Chapter 19 — The future of AI.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 19
(pp. 564-594), read from the book PDF.

The chapter with no code in it, and the one a professional audience most needs.
Where deep learning falls short and why scale does not fix it; what
intelligence is for; ARC-AGI as a benchmark built to resist memorization; and
the two poles of abstraction that any complete system will have to combine.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_STATIC_DB = """
flowchart LR
  T["<b>Training time</b><br/><small>parameters determined<br/>by gradient descent</small>"]
  F["<b>Frozen</b><br/><small>the database is static</small>"]
  I["<b>Inference time</b><br/><small>information retrieval only</small>"]
  G["Excellent at patterns<br/><b>similar to training data</b>"]
  B["Inherently poor at<br/><b>adaptation</b><br/><small>backward-looking</small>"]
  T --> F --> I
  I --> G
  I --> B
"""

MMD_FAMILIARITY = """
flowchart TB
  Q["Can an LLM solve<br/>this problem?"]
  C["<b>Not</b> a question of<br/>problem complexity"]
  F["<b>A question of familiarity</b><br/><small>does it map to something<br/>seen at training time?</small>"]
  R["They will break their teeth on<br/>any sufficiently <b>novel</b> problem,<br/>no matter how simple"]
  Q --> C
  Q --> F --> R
"""

MMD_PROMPT_LOOKUP = """
flowchart LR
  P["<b>Prompt</b><br/><small>&quot;How do you sort a list in Python?<br/>Answer like a pirate&quot;</small>"]
  A["An <b>address</b> in the<br/>interpolative database"]
  K["Retrieve knowledge<br/><small>list sorting</small>"]
  S["Retrieve and execute<br/>a style program<br/><small>answer like a pirate</small>"]
  O["Output"]
  P --> A
  A --> K --> O
  A --> S --> O
"""

MMD_MIRROR = """
flowchart LR
  R["Real world"]
  H["<b>Embodied human<br/>experience</b>"]
  C["Abstract concepts<br/>in the human mind"]
  D["Labelled data<br/>exemplifying<br/>those concepts"]
  M["<b>Machine learning model</b><br/><small>f(x)</small>"]
  R --> H --> C --> D --> M
  M -. "matches the training data" .-> D
  M -. "does NOT match the human<br/>mental model it came from" .-> C
  M -. "may not transfer to<br/>the real world" .-> R
"""

MMD_GENERALIZATION = """
flowchart TB
  A["<b>No generalization</b><br/><small>a Python dict; hardcoded<br/>if-then-else</small>"]
  B["<b>Local generalization</b><br/><small>deep nets: known unknowns,<br/>anticipated factors of variation</small>"]
  C["<b>Broad generalization</b><br/><small>unknown unknowns within<br/>one broad domain</small>"]
  D["<b>Extreme generalization</b><br/><small>radically novel situations,<br/>little or no new data</small>"]
  A --> B --> C --> D
"""

MMD_BRAIN = """
flowchart TB
  E["<b>Evolution as programmer</b><br/><small>DNA decoded as<br/>neural connectivity</small>"]
  A["<b>Brains as automatons</b><br/><small>hardcoded behavioural programs:<br/>if this, then that</small>"]
  C["Environments grew<br/><b>dynamic and unpredictable</b>"]
  I["<b>Brains optimized for<br/>adaptability itself</b><br/><small>rather than fitness to a<br/>fixed set of situations</small>"]
  E --> A --> C --> I
"""

MMD_KALEIDOSCOPE = """
flowchart TB
  W["The world <b>seems</b> to feature<br/>never-ending novelty"]
  S["But everything in that sea of<br/>complexity is <b>similar to<br/>everything else</b>"]
  A["A relatively small number of<br/><b>atoms of meaning</b>"]
  R["Everything around you is a<br/><b>recombination</b> of them"]
  K["A few seeds,<br/>endless variation"]
  W --> S --> A --> R --> K
"""

MMD_TWO_PARTS = """
flowchart LR
  E["Stream of<br/>experience or data"]
  ACQ["<b>Abstraction acquisition</b><br/><small>extract compact, reusable<br/>abstractions -- structures,<br/>principles, invariants</small>"]
  LIB["A collection of<br/>abstractions"]
  REC["<b>On-the-fly recombination</b><br/><small>select and recombine them<br/>in novel ways to model<br/>a new situation</small>"]
  M["A brand-new model,<br/>adapted to the situation"]
  E --> ACQ --> LIB --> REC --> M
"""

MMD_SHORTCUT = """
flowchart TB
  G["<b>Fix the task</b><br/><small>chess, Go, ImageNet,<br/>the bar exam</small>"]
  U["Uncertainty and novelty<br/>are <b>removed</b>"]
  N["The need for intelligence<br/>is removed with them"]
  S["An unintelligent solution to a<br/>specific task is always easier<br/>than solving intelligence"]
  T["<b>So that is the shortcut<br/>you take, 100% of the time</b>"]
  G --> U --> N --> S --> T
"""

MMD_RATIO = """
flowchart LR
  I["<b>Information available</b><br/><small>past experience +<br/>innate prior knowledge</small>"]
  R["<b>Efficiency ratio</b>"]
  O["<b>Future operating area</b><br/><small>the set of novel situations<br/>where appropriate behaviour<br/>can be produced</small>"]
  I --> R --> O
  R -. "a more intelligent agent handles a<br/>broader future from less past" .-> O
"""

MMD_TTA = """
flowchart TB
  P["<b>Classic deep learning</b><br/><small>parameters frozen<br/>after training</small>"]
  T["<b>Test-time adaptation</b><br/><small>active reasoning or learning<br/>during the test itself</small>"]
  TT["<b>Test-time training</b><br/><small>adjust parameters from the<br/>examples in the task,<br/>via gradient descent</small>"]
  SE["<b>Search methods</b><br/><small>chain-of-thought synthesis,<br/>or symbolic program synthesis</small>"]
  P -- "the missing component" --> T
  T --> TT
  T --> SE
"""

MMD_TWO_POLES = """
flowchart TB
  I["Instances"]
  V["<b>Value-centric analogy</b><br/><small>similarity comparison</small>"]
  P["<b>Program-centric analogy</b><br/><small>exact structural match</small>"]
  VP["Abstract <b>prototypes</b><br/><small>clusters averaged together</small>"]
  PP["Isomorphic <b>substructures</b><br/><small>subgraph isomorphism</small>"]
  VU["Perception, intuition<br/><small>immediate, fuzzy</small>"]
  PU["Reasoning, planning<br/><small>slow, exact, rigorous</small>"]
  I --> V --> VP --> VU
  I --> P --> PP --> PU
"""

MMD_PROGRAM_SYNTH = """
flowchart TB
  SPEC["<b>Specification</b><br/><small>input-output pairs</small>"]
  VOC["<b>Vocabulary of<br/>building blocks</b><br/><small>if, for, +=, ==, ...</small>"]
  SEARCH["<b>Discrete search</b><br/><small>genetic search, enumeration</small>"]
  CAND["Candidate programs"]
  TEST["Test against<br/>the specification"]
  OK["A valid program"]
  SPEC --> SEARCH
  VOC --> SEARCH --> CAND --> TEST --> OK
  TEST -. "no match: keep searching" .-> SEARCH
"""

MMD_HYBRID = """
flowchart TB
  LIB["<b>Global library of<br/>abstract subroutines</b><br/><small>geometric and algorithmic</small>"]
  META["<b>Perpetual meta-learner</b><br/><small>grows a task-level model<br/>across a variety of tasks</small>"]
  PROG["<b>Modular task-level program</b><br/><small>learned on the fly for<br/>one specific task</small>"]
  TASK["A task"]
  LIB -- "fetch relevant subroutines" --> META
  META -- "design choices" --> PROG
  PROG -- "actions" --> TASK
  TASK -- "data and feedback" --> PROG
  META -- "push reusable subroutines" --> LIB
"""

NB = []

DECK = {
    "id": "ch19",
    "kind": "chapter",
    "number": 19,
    "title": "The Future of AI",
    "subtitle": "Where deep learning falls short, why scale does not fix it, and what "
                "a system would need in order to handle a situation nobody "
                "anticipated.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 19",
    "source_url": chapter_url(19),
    "duration": "2.5 hours (2 sessions)",
    "presenter": [
        {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
        {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    ],
    "resources": chapter_resources(19),
    "objectives": [
        "State the **four structural limitations** of deep learning, and give a "
        "concrete failure for each.",
        "Explain why an LLM's success on a problem tracks **familiarity, not "
        "complexity**.",
        "Explain what **prompt engineering actually is** in terms of the "
        "interpolative database, and what its necessity implies.",
        "Argue why **scaling laws do not answer** any of these limitations.",
        "Distinguish **local, broad, and extreme generalization**, and place "
        "current systems on that spectrum.",
        "Define intelligence as an **efficiency ratio** between information "
        "available and future operating area.",
        "Explain what **ARC-AGI** measures, why it resisted a 50,000× scale-up, and "
        "what test-time adaptation changed in 2024.",
        "Compare the **two poles of abstraction** and say why a complete system "
        "needs both.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "The limitations of deep learning",
         "lead": "To use a tool well, be aware of its limitations, not just its strengths."},

        {
            "type": "slide",
            "kicker": "Section 19.1.1",
            "title": "A parametric curve is a database, and a static one",
            "blocks": [
                {"t": "p", "md": "Deep learning models are **big parametric curves fitted to "
                                 "large datasets**. That is the source of their power — easy to "
                                 "train, scaling well in both model and dataset size. It is also "
                                 "the source of significant weaknesses."},
                {"t": "mmd", "id": "ch19-static-db", "src": MMD_STATIC_DB,
                 "cap": "Chapter 15 called it an interpolative database. The word that matters "
                        "here is *static*."},
                {"t": "p", "md": "**The only thing you can do with a static database is "
                                 "information retrieval.** At inference time you had better hope "
                                 "the situations the model faces are inside the training "
                                 "distribution."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.1",
            "title": "The leopard-print sofa",
            "blocks": [
                {"t": "lead", "md": "A model trained on ImageNet will classify a **leopard-print "
                                    "sofa** as an actual leopard. Sofas were not part of its "
                                    "training data."},
                {"t": "p", "md": "This applies equally to the largest generative models. It is "
                                 "frequently claimed that LLMs perform **in-context learning** — "
                                 "picking up new skills from a few examples. There is "
                                 "overwhelming evidence that what they are actually doing is "
                                 "**fetching vector functions memorized during training** and "
                                 "reapplying them."},
                {"t": "p", "md": "By learning next-token prediction across a web-sized dataset, "
                                 "an LLM has collected millions of potentially useful mini "
                                 "text-processing programs, and can be prompted into reusing "
                                 "them. ==Show it something with no direct equivalent in its "
                                 "training data, and it is helpless.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.1 · the diagnosis",
            "title": "Familiarity, not complexity",
            "blocks": [
                {"t": "mmd", "id": "ch19-familiarity", "src": MMD_FAMILIARITY,
                 "cap": "Figure 19.1's puzzle is easy for you and unsolved by every "
                        "state-of-the-art model."},
                {"t": "p", "md": "This is the single most useful reframing in the chapter for "
                                 "anyone deciding where to deploy an LLM. **The question is never "
                                 "\"is this task hard?\" It is \"is this task familiar?\"**"},
            ],
            "notes": "Ask the room for a task from their own work that is trivially easy and "
                     "almost certainly absent from web text. That is the failure case they will "
                     "hit in production.",
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.1 · two well-known failures",
            "title": "Ten kilos of steel, and Monty Hall",
            "blocks": [
                {"t": "quote", "md": "*\"What's heavier, **10 kilos** of steel or one kilo of "
                                     "feathers?\"* — For months after ChatGPT's release, the "
                                     "answer was that **they weigh the same**.",
                 "cite": "Section 19.1.1"},
                {"t": "p", "md": "The question *\"one kilo of steel or one kilo of feathers?\"* "
                                 "appears many times online as a trick question, with that exact "
                                 "answer. The model repeated the memorized answer **without "
                                 "attending to the actual numbers** or what the query meant."},
                {"t": "p", "md": "The same happens with variations of the **Monty Hall problem**: "
                                 "the canonical answer comes out regardless of whether it makes "
                                 "sense in the altered context."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.1 · how these get fixed",
            "title": "Twenty-five thousand people playing whack-a-mole",
            "blocks": [
                {"t": "p", "md": "Those specific prompts were patched later — by **special-casing "
                                 "them**."},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "25,000+", "l": "people employed full time providing LLM training data"},
                    {"v": "one at a time", "l": "how failing prompts get patched"},
                ]},
                {"t": "band", "md": "LLM maintenance is a constant game of whack-a-mole where "
                                    "failing prompts are patched individually, **without "
                                    "addressing the underlying issue**. ==Even already-patched "
                                    "prompts will fail again if you make small changes to "
                                    "them.==", "style": "rose"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.2 · figure 19.3",
            "title": "Adversarial examples: a panda plus a gibbon gradient",
            "blocks": [
                {"t": "p", "md": "Chapter 10 showed gradient ascent in input space to generate "
                                 "inputs maximizing a ConvNet filter's activation. The same "
                                 "technique can **slightly modify an image to maximize the "
                                 "prediction for a chosen class**."},
                {"t": "p", "md": "Take a picture of a panda, add a gibbon class gradient, and the "
                                 "network classifies it as a gibbon. The change is "
                                 "**imperceptible to a human**."},
                {"t": "band", "md": "This evidences both the brittleness of these models and the "
                                    "==deep difference between their input-to-output mapping and "
                                    "human perception==. The two are not approximations of each "
                                    "other."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.2 · the text equivalent",
            "title": "Alice has N brothers and M sisters",
            "blocks": [
                {"t": "quote", "md": "*\"Alice has N brothers and she also has M sisters. How "
                                     "many sisters does Alice's brother have?\"*",
                 "cite": "The Alice in Wonderland riddle — Nezhurina et al., arXiv 2406.02061"},
                {"t": "p", "md": "The answer is **M + 1** — Alice's sisters plus Alice herself. "
                                 "With values commonly found in online instances of the riddle "
                                 "(N = 3, M = 2) an LLM generally answers correctly. **Tweak the "
                                 "values and you quickly get wrong answers.**"},
                {"t": "p", "md": "Changing place names, people's names in a paragraph, or "
                                 "variable names in a block of code can **significantly degrade** "
                                 "performance. None of those changes alters the problem."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.2 · what prompt engineering really is",
            "title": "Two framings of the same fact",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🌤", "h": "The optimistic framing", "style": "",
                     "p": "*Your models are better than you know! You just need to use them "
                          "right.* Adding **\"Please think step by step\"** can significantly "
                          "boost performance on reasoning tasks."},
                    {"ico": "🌧", "h": "The negative framing", "style": "warn",
                     "p": "For any query that seems to work, there is a range of **minor changes "
                          "that can tank performance**. To what extent does a model understand "
                          "something if a rewording breaks that understanding?"},
                ]},
                {"t": "mmd", "id": "ch19-prompt-lookup", "src": MMD_PROMPT_LOOKUP,
                 "cap": "A prompt is an address, not an instruction."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.2",
            "title": "Prompt engineering is search through latent space",
            "blocks": [
                {"t": "p", "md": "Because the knowledge and programs indexed by the LLM are "
                                 "**interpolative**, you can move around in latent space to "
                                 "nearby locations. *\"Explain Python list sorting, but answer "
                                 "like a buccaneer\"* points somewhere very similar — close, but "
                                 "not identical."},
                {"t": "p", "md": "There are thousands of variations, each giving a similar yet "
                                 "slightly different answer. **There is no a priori reason for "
                                 "your first naive prompt to be optimal.**"},
                {"t": "band", "md": "Prompt engineering is trial-and-error search for the lookup "
                                    "query that performs best. **It is no different from trying "
                                    "different keywords in a Google search.** If LLMs actually "
                                    "understood what you asked, ==there would be no need for this "
                                    "search process at all=="},
            ],
            "notes": "The logical argument here is the sharp one: the information conveyed about "
                     "your task does not change whether you write 'rewrite' or 'rephrase'. If "
                     "the output changes, something other than understanding is happening.",
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.3",
            "title": "Memorized programs do not generalize",
            "blocks": [
                {"t": "p", "md": "Suppose you only need a well-known program and you know exactly "
                                 "how to address it in latent space. **You still have a problem**: "
                                 "the programs deep learning models memorize often do not "
                                 "generalize. They work for some inputs and fail for others."},
                {"t": "p", "md": "This is especially true of programs encoding **discrete logic**. "
                                 "Train a Transformer on hundreds of thousands of digit-addition "
                                 "pairs like `\"4 3 5 7 + 8 9 3 6\"` and you reach very high "
                                 "accuracy — **very high, but not 100%**."},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "~70%", "l": "state-of-the-art LLM accuracy on digit addition"},
                    {"v": "which digits", "l": "accuracy depends on it — common digits do better"},
                ]},
                {"t": "p", "md": "Unless, that is, the model was explicitly hardcoded to execute "
                                 "`4357 + 8936` in Python."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.3 · why",
            "title": "Most programs cannot be expressed as a deep learning model",
            "blocks": [
                {"t": "p", "md": "A deep learning model is a **static chain of simple, continuous "
                                 "geometric transformations** mapping one vector space into "
                                 "another. That is a good fit for perceptual pattern recognition "
                                 "and a very poor fit for step-by-step discrete logic — concepts "
                                 "like **place value** or **carrying over**."},
                {"t": "band", "md": "A deep learning model can be interpreted as a kind of "
                                    "program. But inversely, **most programs cannot be expressed "
                                    "as deep learning models.** For most tasks either no network "
                                    "of reasonable size solves it, or one exists but is not "
                                    "learnable — the transform is too complex, or the data does "
                                    "not exist."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.4 · figure 19.4",
            "title": "A dim image in a mirror",
            "blocks": [
                {"t": "p", "md": "Our understanding of images, sounds, and language is grounded in "
                                 "**sensorimotor experience**. Models have no access to that, and "
                                 "so cannot understand their inputs in a human-relatable way."},
                {"t": "mmd", "id": "ch19-mirror", "src": MMD_MIRROR,
                 "cap": "What the model learns matches the training data — not the mental model "
                        "the data came from."},
                {"t": "p", "md": "**The models you create will take any shortcut available to fit "
                                 "their training data.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.1.4 · the risk",
            "title": "Theory of mind, applied where it does not belong",
            "blocks": [
                {"t": "p", "md": "A fundamental feature of humans is our **theory of mind** — our "
                                 "tendency to project intentions, beliefs, and knowledge onto the "
                                 "things around us. Draw a smiley face on a rock and it becomes "
                                 "*happy*, in our minds."},
                {"t": "p", "md": "Applied to deep learning, this leads us to believe a model that "
                                 "uses language **understands** the word sequences it generates "
                                 "the way we do. Then we are surprised when a slight departure "
                                 "from the training patterns produces something absurd."},
                {"t": "band", "md": "Never fall into the trap of believing neural networks "
                                    "understand the task they perform. **They were trained on a "
                                    "different, far narrower task than the one you wanted to "
                                    "teach them**: mapping training inputs to training targets, "
                                    "point by point.", "style": "rose"},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "Scale isn't all you need",
         "lead": "Four or five orders of magnitude larger, and the same problems."},

        {
            "type": "slide",
            "kicker": "Section 19.2",
            "title": "The prevailing narrative, and what it missed",
            "blocks": [
                {"t": "p", "md": "In early 2023, at peak LLM hype, GPT-4 had just been released "
                                 "— essentially a scaled-up GPT-3. Its improved performance "
                                 "seemed to suggest you could just keep going, and that AGI "
                                 "would spontaneously emerge from a GPT-5."},
                {"t": "p", "md": "Proponents pointed to **scaling laws**: an empirical "
                                 "relationship between model and dataset size and performance on "
                                 "specific tasks, suggesting that size reliably and predictably "
                                 "buys performance."},
                {"t": "band", "md": "The key thing scaling-law enthusiasts miss is that the "
                                    "benchmarks measuring \"performance\" are effectively "
                                    "**memorization tests** — the kind we give university "
                                    "students. LLMs do well by memorizing the answers, and "
                                    "==cramming more questions and answers in improves the score "
                                    "accordingly.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2 · the evidence",
            "title": "Seven years, four orders of magnitude, same problems",
            "blocks": [
                {"t": "lead", "md": "Scaling has produced **no progress** on inability to adapt "
                                    "to novelty, oversensitivity to phrasing, or the inability to "
                                    "infer generalizable programs — because these issues are "
                                    "inherent to **curve fitting**."},
                {"t": "p", "md": "Chollet began pointing out these problems in **2017**. We are "
                                 "still struggling with them, with models four or five orders of "
                                 "magnitude larger and more knowledgeable."},
                {"t": "band", "md": "**We have made no progress because the models are still the "
                                    "same.** They have been the same for over seven years: "
                                    "parametric curves fitted to a dataset by gradient descent, "
                                    "using the Transformer architecture."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2 · stated plainly",
            "title": "Three things stacking more layers will not solve",
            "blocks": [
                {"t": "steps", "items": [
                    "Models are **limited to interpolative programs memorized at training "
                    "time**. They cannot, on their own, synthesize brand-new programs at "
                    "inference time to adapt to substantially novel situations.",
                    "Even within known situations, those interpolative programs suffer "
                    "**generalization issues** — oversensitivity to phrasing and confounder "
                    "features.",
                    "Models are **limited in what they can represent**. Most programs you would "
                    "wish to learn cannot be expressed as a continuous geometric morphing of a "
                    "data manifold — algorithmic reasoning tasks in particular.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2.1",
            "title": "Why brains appeared, and what they were at first",
            "blocks": [
                {"t": "mmd", "id": "ch19-brain", "src": MMD_BRAIN,
                 "cap": "Brains appeared more than half a billion years ago as a way to store "
                        "and execute behavioural programs."},
                {"t": "p", "md": "Because the source code was **DNA**, decoded as neural "
                                 "connectivity, evolution could suddenly search over behaviour "
                                 "space in a largely unbounded way. Eyes, ears, mandibles, four "
                                 "legs, twenty-four legs — **brains handle any modality you "
                                 "throw at them**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2.2",
            "title": "Automatons and intelligent agents",
            "blocks": [
                {"t": "p", "md": "The field of AI has long suffered from **conflating intelligence "
                                 "with automation**."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "⚙", "h": "An automaton", "style": "",
                     "p": "Static, crafted to accomplish specific things in a specific context. "
                          "Expose it to something outside what it was programmed for — by hand, "
                          "by evolution, or by fitting on a dataset — and **it fails**."},
                    {"ico": "🧠", "h": "An intelligent agent", "style": "accent",
                     "p": "Adapts **on the fly** to novel, unexpected situations, using fluid "
                          "intelligence to find a way forward."},
                ]},
                {"t": "band", "md": "How do you tell a student who memorized three years of past "
                                    "exam questions from one who understands the subject? "
                                    "==You give them a brand-new problem.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2.2 · figure 19.6",
            "title": "The spectrum of generalization",
            "blocks": [
                {"t": "mmd", "id": "ch19-generalization", "src": MMD_GENERALIZATION,
                 "cap": "Deep nets generalize to *known unknowns* — factors of variation "
                        "anticipated during development and featured in the training data."},
                {"t": "p", "md": "Deep nets generalize **by interpolation on a manifold**, so any "
                                 "factor of variation in the input space must be captured by the "
                                 "manifold they learn. That is why basic **data augmentation** "
                                 "helps so much — and why nothing helps when the variation was "
                                 "never anticipated."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2.2 · two thought experiments",
            "title": "Landing a rocket, and crossing a road",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🚀", "h": "The rocket", "style": "warn",
                     "p": "A deep net needs **tens of thousands or millions of launch trials** — "
                          "a dense sampling of the input space. Humans build a physical model, "
                          "*rocket science*, and land it in one or a few tries."},
                    {"ico": "🚗", "h": "The road", "style": "warn",
                     "p": "A net controlling a body would have to **die many thousands of times** "
                          "to infer that cars are dangerous. Dropped into a new city, it would "
                          "relearn most of what it knows."},
                ]},
                {"t": "p", "md": "Humans learn safe behaviours **without dying even once** — "
                                 "thanks to the power of abstract modelling of novel situations."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2.3",
            "title": "What intelligence is for",
            "blocks": [
                {"t": "p", "md": "If the set of situations an organism faced were static and "
                                 "known, behaviour generation would be easy: evolution would find "
                                 "the right behaviours by trial and error and hardcode them into "
                                 "DNA. **Brains as automatons would already be optimal.**"},
                {"t": "p", "md": "But as organism and environmental complexity rose, situations "
                                 "became dynamic and unpredictable. **A day in your life is "
                                 "unlike any day you have experienced, and unlike any day "
                                 "experienced by any of your evolutionary ancestors.**"},
                {"t": "quote", "md": "Intelligence is the ability to **efficiently use the "
                                     "information at your disposal to produce successful "
                                     "behaviour in the face of an uncertain, ever-changing "
                                     "future.**",
                 "cite": "Section 19.2.3"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2.4",
            "title": "Seventy years of AI, on the same spectrum",
            "blocks": [
                {"t": "table",
                 "head": ["Era", "System", "Where on the spectrum"],
                 "widths": [18, 42, 40],
                 "rows": [
                     ["1960s-70s", "ELIZA; SHRDLU manipulating objects from language commands",
                      "**Pure automatons**"],
                     ["1990s-2000s", "Machine learning systems handling some uncertainty",
                      "**Local generalization**"],
                     ["2010s", "Deep learning: larger datasets, more expressive models",
                      "**Local generalization, expanded**"],
                     ["Today", "Self-driving cars; a robot that could make coffee in a random "
                      "kitchen", "**Toward broad generalization**"],
                 ]},
                {"t": "p", "md": "The last row is the **Woz test of intelligence** — enter a "
                                 "random kitchen and make a cup of coffee. Visible progress is "
                                 "being made, by **combining deep learning with painstakingly "
                                 "handcrafted abstract models of the world**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.2.4 · a proposed renaming",
            "title": "Artificial cognition, not artificial intelligence",
            "blocks": [
                {"t": "quote", "md": "The \"intelligence\" label in \"artificial intelligence\" has "
                                     "been a **category error**. It would be more accurate to "
                                     "call our field *artificial cognition*, with *cognitive "
                                     "automation* and *artificial intelligence* being two nearly "
                                     "independent subfields within it.",
                 "cite": "Section 19.2.4"},
                {"t": "p", "md": "In that subdivision, AI would be **a greenfield where almost "
                                 "everything remains to be discovered**."},
                {"t": "band", "md": "This is not meant to diminish deep learning. Cognitive "
                                    "automation is incredibly useful, and automating tasks from "
                                    "exposure to data alone is **far more practical and versatile "
                                    "than explicit programming**. ==Doing it well is a game "
                                    "changer for essentially every industry.=="},
            ],
            "notes": "Land this carefully for a professional audience. The chapter is not saying "
                     "the technology is oversold as a product. It is saying the word "
                     "'intelligence' is oversold as a description.",
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "How to build intelligence",
         "lead": "Abstraction acquisition, on-the-fly recombination, and a benchmark "
                 "designed to resist memorization."},

        {
            "type": "slide",
            "kicker": "Section 19.3.1",
            "title": "The kaleidoscope hypothesis",
            "blocks": [
                {"t": "p", "md": "If the future you faced were **truly** novel — sharing no "
                                 "common ground with anything you had seen — you would be unable "
                                 "to react, no matter how intelligent. **Intelligence works "
                                 "because nothing is ever truly without precedent.**"},
                {"t": "p", "md": "A person from the 17th century seeing a jet plane might "
                                 "describe *a large, loud metal bird that doesn't flap its "
                                 "wings*. A car is a **horseless carriage**. Electricity is like "
                                 "water in a pipe; spacetime is like a rubber sheet distorted by "
                                 "heavy objects."},
                {"t": "mmd", "id": "ch19-kaleidoscope", "src": MMD_KALEIDOSCOPE,
                 "cap": "A few beads of coloured glass, reflected by mirrors, produce endless "
                        "patterns."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.1",
            "title": "The analogies are not only in our heads",
            "blocks": [
                {"t": "p", "md": "Besides clear-cut explicit analogies, we make **smaller "
                                 "implicit ones every second, with every thought**. A new "
                                 "supermarket relates to similar stores. A new person reminds you "
                                 "of a few you have met. Even cloud shapes evoke an elephant, a "
                                 "ship, a fish."},
                {"t": "p", "md": "And **physical reality itself is full of isomorphisms**. "
                                 "Electromagnetism is analogous to gravity. Animals are "
                                 "structurally similar because of shared origins. Silica crystals "
                                 "resemble ice crystals."},
                {"t": "band", "md": "The number of unique **atoms of meaning** needed to describe "
                                    "the universe you live in is relatively small, and everything "
                                    "around you is a ==recombination of them=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.2",
            "title": "Intelligence in two parts",
            "blocks": [
                {"t": "mmd", "id": "ch19-two-parts", "src": MMD_TWO_PARTS,
                 "cap": "Extract the beads; recombine them on the fly into a model of the "
                        "situation in front of you."},
                {"t": "band", "md": "**The emphasis on efficiency is crucial.** If you need "
                                    "hundreds of thousands of hours of practice to acquire a "
                                    "skill, you are not very intelligent. If you need to "
                                    "enumerate every possible move on a chessboard to find the "
                                    "best one, you are not very intelligent."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.2 · the diagnosis",
            "title": "Deep learning has one half, and it is the wrong half",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🚫", "h": "No on-the-fly recombination", "style": "bad",
                     "p": "Models do a decent job of **acquiring** abstractions at training time "
                          "via gradient descent, but have **zero ability to recombine** what "
                          "they know at test time. They are a static database limited to "
                          "retrieval — missing half the picture, arguably the most important "
                          "half."},
                    {"ico": "🐢", "h": "Terribly inefficient", "style": "bad",
                     "p": "Gradient descent requires vast amounts of data to distill neat "
                          "abstractions — **many orders of magnitude more than humans**."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.3 · the shortcut rule",
            "title": "You get what you measure, and nothing else",
            "blocks": [
                {"t": "lead", "md": "**The shortcut rule**: optimize one success metric and you "
                                    "will achieve your goal — at the expense of everything in the "
                                    "system your metric did not cover."},
                {"t": "p", "md": "In 2009 Netflix ran a $1 million challenge for the best movie "
                                 "recommendation score. **It never used the winning system** — "
                                 "far too complex and compute intensive. The winners had "
                                 "optimized for prediction accuracy alone, at the expense of "
                                 "inference cost, maintainability, and explainability."},
                {"t": "p", "md": "The same holds in most Kaggle competitions: winning models can "
                                 "**rarely, if ever, be used in production**. ==Your creations "
                                 "are shaped by the incentives you give yourself.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.3 · the canonical example",
            "title": "Deep Blue, and what it taught us about the mind",
            "blocks": [
                {"t": "p", "md": "In the 1970s Allen Newell, concerned his field was making no "
                                 "progress toward a theory of cognition, proposed a new grand "
                                 "goal: **chess playing**. Chess in humans seemed to require "
                                 "perception, reasoning, analysis, memory, study from books. "
                                 "Surely a chess machine would need those too?"},
                {"t": "p", "md": "In 1997 Deep Blue beat Kasparov. Researchers then had to "
                                 "contend with the fact that it had **taught them little about "
                                 "human intelligence**. The A-star algorithm at its heart was "
                                 "not a model of the brain and could not generalize beyond "
                                 "similar board games."},
                {"t": "band", "md": "It turned out to be easier to build an AI that could only "
                                    "play chess than to build an artificial mind — **so that is "
                                    "the shortcut researchers took**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.3 · the structural argument",
            "title": "Fixing the task removes the need for intelligence",
            "blocks": [
                {"t": "mmd", "id": "ch19-shortcut", "src": MMD_SHORTCUT,
                 "cap": "The driving success metric of AI has been to solve specific tasks — "
                        "from chess to Go, MNIST to ImageNet, high school maths to the bar exam."},
                {"t": "p", "md": "Given near-infinite training data, even nearest-neighbour search "
                                 "can play video games with superhuman skill. Given near-infinite "
                                 "hand-written if-then-else statements, so can those — **until you "
                                 "make a small change to the rules, the kind a human adapts to "
                                 "instantly**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.3",
            "title": "There is no path from skills to intelligence",
            "blocks": [
                {"t": "lead", "md": "Humans can use general intelligence to acquire skill at any "
                                    "new task. **In reverse, there is no path from a collection "
                                    "of task-specific skills to general intelligence.**"},
                {"t": "p", "md": "By fixing the task you make it possible to describe precisely "
                                 "what needs to be done, and to **buy** more skill by adding data "
                                 "or hardcoded knowledge — without increasing generalization "
                                 "power at all."},
                {"t": "band", "md": "Human-like intelligence is not characterized by skill at any "
                                    "particular task. It is **the ability to adapt to novelty, to "
                                    "efficiently acquire new skills and master never-before-seen "
                                    "tasks**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.4",
            "title": "Intelligence as an efficiency ratio",
            "blocks": [
                {"t": "mmd", "id": "ch19-ratio", "src": MMD_RATIO,
                 "cap": "Fix the information available; measure performance on situations known "
                        "to be sufficiently different from it."},
                {"t": "band", "md": "To avoid cheating you must test only on tasks the system was "
                                    "not programmed or trained to handle — in fact, **tasks its "
                                    "creators could not have anticipated**.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.4 · figure 19.9",
            "title": "ARC-AGI",
            "blocks": [
                {"t": "p", "md": "In 2018-19 Chollet built the **Abstraction & Reasoning Corpus "
                                 "for Artificial General Intelligence**, a benchmark designed to "
                                 "capture that definition. It is approachable by both machines "
                                 "and humans, and looks like a human IQ test — Raven's "
                                 "progressive matrices."},
                {"t": "p", "md": "Each task is explained by three or four **input grid / output "
                                 "grid** examples. You are given a new input grid and have three "
                                 "tries to produce the correct output before moving on."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🆕", "h": "Only unseen tasks", "style": "accent",
                     "p": "**A game you cannot practise for.** Each task has its own unique logic "
                          "to be understood on the fly; memorizing strategies from past tasks "
                          "does not transfer."},
                    {"ico": "🧬", "h": "Controlled priors", "style": "accent",
                     "p": "All test takers start from **Core Knowledge priors** — the knowledge "
                          "systems humans are born with. Unlike an IQ test, tasks never involve "
                          "acquired knowledge such as English sentences."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.5",
            "title": "A 50,000× scale-up bought ten percentage points",
            "blocks": [
                {"t": "p", "md": "In 2024 Chollet and Mike Knoop founded the nonprofit **ARC "
                                 "Prize Foundation**, running a yearly competition with over $1 "
                                 "million in prizes."},
                {"t": "stats", "cols": 3, "items": [
                    {"v": "~50,000×", "l": "base LLM scale-up, GPT-2 (2019) to GPT-4.5 (2025)"},
                    {"v": "0% → ~10%", "l": "their ARC-AGI score over that period"},
                    {"v": "> 95%", "l": "what you, the reader, would score"},
                ]},
                {"t": "band", "md": "Most benchmarks saturated quickly in the age of LLMs, "
                                    "because they can be **hacked via memorization**. ARC-AGI was "
                                    "designed to resist it. ==Scale up 50,000× with no meaningful "
                                    "progress and that is a large warning sign that you need new "
                                    "ideas.==", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.6 · 2024",
            "title": "The narrative shift, and what caused it",
            "blocks": [
                {"t": "p", "md": "The 2023 bedrock dogma — *scale is all you need* — began giving "
                                 "way to *actually, we need on-the-fly recombination*. The ARC "
                                 "Prize results announced in December 2024 were illuminating: "
                                 "**the leading solutions did not come from scaling existing "
                                 "architectures**."},
                {"t": "mmd", "id": "ch19-tta", "src": MMD_TTA,
                 "cap": "Every single top entry in ARC Prize 2024 used test-time adaptation."},
                {"t": "p", "md": "TTA means the system performs **active reasoning or learning "
                                 "during the test itself**, using the specific problem "
                                 "information provided."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.6 · December 2024",
            "title": "o3, and the first signs of fluid intelligence",
            "blocks": [
                {"t": "p", "md": "Shortly after the competition, OpenAI previewed its **o3** "
                                 "test-time reasoning model and used ARC-AGI to showcase it."},
                {"t": "table",
                 "head": ["Compute setting", "ARC-AGI score", "Cost per task"],
                 "widths": [34, 30, 36],
                 "rows": [
                     ["Moderate", "**76%**", "about $200"],
                     ["High", "**88%** — above the human baseline", "over **$20,000**"],
                 ]},
                {"t": "p", "md": "For the first time, a model showed **signs of genuine fluid "
                                 "intelligence**. ARC-AGI was one of the only benchmarks at the "
                                 "time giving a clear signal that a paradigm shift was underway."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.7",
            "title": "Is AGI solved? Not quite — and here is why",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "💸", "h": "Efficiency is the point", "style": "warn",
                     "p": "Tens of thousands of dollars per puzzle. **Brute-forcing the solution "
                          "space with enormous compute is a shortcut that makes tasks possible "
                          "without requiring intelligence.** It felt more like cracking a code "
                          "with a supercomputer than nimble reasoning."},
                    {"ico": "🧩", "h": "Still stumped by easy tasks", "style": "warn",
                     "p": "o3 failed many tasks humans find **very easy** — even at the highest "
                          "compute settings."},
                ]},
                {"t": "band", "md": "**The entire point of intelligence is to achieve results "
                                    "with the least resources possible.** In principle you could "
                                    "solve ARC-AGI by enumerating every possible program until "
                                    "one fits the demonstrations. ==That would prove nothing.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.3.7 · March 2025",
            "title": "ARC-AGI-2: a benchmark that can tell degrees apart",
            "blocks": [
                {"t": "p", "md": "The 2019 version was intended to be **easy** — essentially a "
                                 "binary test. Either you have no fluid intelligence and score "
                                 "near zero, or you have some and immediately score very high. "
                                 "There was not much room in between."},
                {"t": "p", "md": "ARC-AGI-2 keeps the exact same format with significantly harder "
                                 "content: **longer reasoning chains, inherently more resistant "
                                 "to exhaustive search**, so that computational efficiency "
                                 "becomes critical to success."},
                {"t": "stats", "cols": 3, "items": [
                    {"v": "instant", "l": "typical human time on an ARC-AGI-1 task"},
                    {"v": "~5 min", "l": "average human time on ARC-AGI-2"},
                    {"v": "~0%", "l": "base LLM performance on ARC-AGI-2"},
                ]},
                {"t": "p", "md": "Even **o3's scores plummeted into the low double digits** under "
                                 "reasonable compute budgets. The challenge of efficient, "
                                 "human-like fluid intelligence is far from solved."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "04", "title": "The missing ingredients: search and symbols",
         "lead": "Two kinds of abstraction, and why any complete mind needs both."},

        {
            "type": "slide",
            "kicker": "Section 19.4.1",
            "title": "Two ways to compare things",
            "blocks": [
                {"t": "p", "md": "Abstraction acquisition starts with **comparing things to one "
                                 "another**. There are two distinct ways to do that, giving rise "
                                 "to two kinds of abstraction and two modes of thinking."},
                {"t": "mmd", "id": "ch19-two-poles", "src": MMD_TWO_POLES,
                 "cap": "Together, these two poles form the basis for all of our thoughts."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.1 · figure 19.12",
            "title": "Value-centric analogy: the beetles in your backyard",
            "blocks": [
                {"t": "p", "md": "You notice similarities. Similarity is implicitly a **smooth, "
                                 "continuous distance function** defining a latent manifold where "
                                 "instances live. Cluster the similar ones and merge them into "
                                 "**prototypes** capturing shared features."},
                {"t": "p", "md": "These prototypes are abstract — they look like no specific "
                                 "beetle you have seen. Meet a new beetle and you compare it to "
                                 "your handful of prototypes rather than to every beetle in your "
                                 "memory."},
                {"t": "band", "md": "This is pretty much a description of **unsupervised machine "
                                    "learning** — K-means, and in general all of modern machine "
                                    "learning. ==The ConvNet features visualized in chapter 10 "
                                    "were visual prototypes.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.1",
            "title": "It is also most of what you do without thinking",
            "blocks": [
                {"t": "lead", "md": "**If you can do a task without thinking about it, you are "
                                    "heavily relying on value-centric analogies.**"},
                {"t": "p", "md": "It underlies pattern recognition, perception, and intuition. "
                                 "Watching a film and subconsciously sorting the characters into "
                                 "*types* is value-centric abstraction."},
                {"t": "p", "md": "It is also exactly the kind of analogy-making that enables deep "
                                 "learning models to perform **local generalization** — which is "
                                 "the connection this chapter has been building toward."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.1 · figure 19.13",
            "title": "Program-centric analogy: refactoring",
            "blocks": [
                {"t": "p", "md": "In software engineering you write functions and classes that "
                                 "have a lot in common, and start asking: could there be a more "
                                 "abstract function that does the same job twice? An abstract "
                                 "base class both could inherit from?"},
                {"t": "p", "md": "You are **not** comparing them by how similar they look, the way "
                                 "you would compare two faces. You are asking whether parts of "
                                 "them have **exactly the same structure** — looking for a "
                                 "**subgraph isomorphism** between programs represented as graphs "
                                 "of operators."},
                {"t": "band", "md": "This is not exclusive to computer science or mathematics. It "
                                    "underlies reasoning, planning, and the general concept of "
                                    "**rigour** as opposed to intuition — any time you think "
                                    "about objects connected by a ==discrete network of "
                                    "relationships=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.2 · table 19.1",
            "title": "The two poles, side by side",
            "blocks": [
                {"t": "table",
                 "head": ["Value-centric abstraction", "Program-centric abstraction"],
                 "widths": [50, 50],
                 "rows": [
                     ["Relates things by **distance**", "Relates things by **exact structural "
                      "match**"],
                     ["Continuous, grounded in geometry", "Discrete, grounded in topology"],
                     ["Abstracts by *averaging* instances into prototypes",
                      "Abstracts by isolating isomorphic substructures"],
                     ["Underlies **perception and intuition**",
                      "Underlies **reasoning and planning**"],
                     ["Immediate, fuzzy, approximate", "Slow, exact, rigorous"],
                     ["Needs a lot of experience to be reliable",
                      "**Experience efficient** — can work from two instances"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.2",
            "title": "Nothing you do uses only one of them",
            "blocks": [
                {"t": "p", "md": "You would be hard pressed to find a task involving only one "
                                 "pole. Even *pure perception* — recognizing objects in a scene — "
                                 "involves implicit reasoning about the relationships between "
                                 "them."},
                {"t": "p", "md": "And even *pure reasoning* — finding the proof of a theorem — "
                                 "involves a good deal of intuition. **When a mathematician puts "
                                 "pen to paper they already have a fuzzy vision of the direction "
                                 "they are going.** The discrete steps are guided by high-level "
                                 "intuition."},
                {"t": "band", "md": "These two poles are complementary, and **it is their "
                                    "interleaving that enables extreme generalization**. No mind "
                                    "could be complete without both."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.3",
            "title": "Sorting five numbers, and classifying MNIST",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔢", "h": "Sorting, with deep learning", "style": "bad",
                     "p": "Possible with the right architecture, and **an exercise in "
                          "frustration**. Massive data, occasional mistakes on new numbers, and "
                          "a complete retrain to go from lists of 5 to lists of 10. A Python "
                          "sort is a few lines and works on **any** list."},
                    {"ico": "🖼", "h": "MNIST, with discrete reasoning", "style": "bad",
                     "p": "Hand-code closed-loop counts, centres of mass. After **thousands of "
                          "lines** you might reach 90% test accuracy. Fitting a parametric model "
                          "is simpler, uses the data better, and is far more robust."},
                ]},
                {"t": "band", "md": "So it is unlikely anyone will reduce reasoning to manifold "
                                    "interpolation, or perception to discrete reasoning. **The "
                                    "way forward is a unified framework incorporating both.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.4 · figure 19.14",
            "title": "Program synthesis, the missing piece",
            "blocks": [
                {"t": "mmd", "id": "ch19-program-synth", "src": MMD_PROGRAM_SYNTH,
                 "cap": "Highly reminiscent of machine learning — given input-output pairs, find "
                        "a program that generalizes."},
                {"t": "p", "md": "The difference: instead of learning **parameter values** inside "
                                 "a hardcoded program (a neural network), we **generate source "
                                 "code** through a discrete search process."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.4 · table 19.2",
            "title": "Machine learning against program synthesis",
            "blocks": [
                {"t": "table",
                 "head": ["", "Machine learning", "Program synthesis"],
                 "widths": [20, 40, 40],
                 "rows": [
                     ["Model", "A differentiable parametric function",
                      "A graph of operators from a programming language"],
                     ["Engine", "**Gradient descent**", "**Discrete search** (e.g. genetic "
                      "search)"],
                     ["Data", "Requires a lot to be reliable",
                      "**Data efficient** — works from a couple of examples"],
                 ]},
                {"t": "p", "md": "Until 2024, AI systems capable of genuine discrete reasoning "
                                 "were **all hardcoded by human programmers**. In the test-time "
                                 "adaptation era that is finally changing — and program synthesis "
                                 "is the branch to watch."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.5",
            "title": "Hybrids already exist, and they are hand-built",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "⚫", "h": "AlphaGo", "style": "accent",
                     "p": "**Most of the intelligence on display is hardcoded by human "
                          "programmers** — Monte Carlo Tree Search. Learning from data happens "
                          "only in specialized submodules: value and policy networks."},
                    {"ico": "🚙", "h": "A Waymo self-driving car", "style": "accent",
                     "p": "Maintains a literal **3D model of the world**, full of assumptions "
                          "hardcoded by engineers, constantly updated by deep learning perception "
                          "modules — powered by Keras."},
                ]},
                {"t": "p", "md": "In both, the combination of human-created discrete programs and "
                                 "learned continuous models unlocks performance **impossible with "
                                 "either alone**. Today the discrete parts are painstakingly "
                                 "hand-coded. In the future such systems may be fully learned."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.5 · a thought experiment",
            "title": "An RNN has one hardcoded for loop. What if it had more?",
            "blocks": [
                {"t": "p", "md": "RNNs have slightly fewer limitations than feedforward networks "
                                 "because they are more than a geometric transformation: they are "
                                 "**a geometric transformation applied repeatedly inside a for "
                                 "loop**. That loop is hardcoded by human developers — a built-in "
                                 "assumption."},
                {"t": "p", "md": "Now imagine a network augmented not with a single hardcoded loop "
                                 "and continuous-space memory, but with a large set of "
                                 "**programming primitives** it is free to manipulate: `if` "
                                 "branches, `while` statements, variable creation, disk storage, "
                                 "sorting operators, lists, graphs, hash tables."},
                {"t": "band", "md": "The space of programs such a network could represent would be "
                                    "far broader — and **some would generalize far better**. Such "
                                    "programs will not be differentiable end to end, so they must "
                                    "be generated by ==a combination of discrete program search "
                                    "and gradient descent=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.5 · the obstacle",
            "title": "Combinatorial explosion",
            "blocks": [
                {"t": "p", "md": "Program synthesis today is **tremendously inefficient**. To "
                                 "caricature: it tries every possible program in a search space "
                                 "until one matches the specification."},
                {"t": "p", "md": "As specification complexity rises, or the vocabulary of "
                                 "primitives expands, the set of possible programs grows **much "
                                 "faster than merely exponentially**. So today, program synthesis "
                                 "generates only very short programs. *You are not going to be "
                                 "generating a new OS for your computer anytime soon.*"},
                {"t": "band", "md": "The fix is to bring it closer to how humans write software. "
                                    "When you open your editor you are **not thinking about every "
                                    "possible program** — you have a handful of approaches in "
                                    "mind, cut down by understanding and past experience."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.5 · the resolution",
            "title": "Deep learning can guide the search",
            "blocks": [
                {"t": "p", "md": "Each specific program you want to generate is a fundamentally "
                                 "discrete object doing non-interpolative manipulation. But "
                                 "evidence so far indicates that **the space of all useful "
                                 "programs may look a lot like a continuous manifold**."},
                {"t": "p", "md": "A model trained on millions of successful program-generation "
                                 "episodes might develop **solid intuition about the path through "
                                 "program space** — just as an engineer has immediate intuition "
                                 "about the architecture of the script they are about to write."},
                {"t": "band", "md": "Human reasoning is itself heavily guided by value-centric "
                                    "abstraction — by pattern recognition and intuition. **The "
                                    "same should be true of program synthesis.** Expect increasing "
                                    "research interest over the next 10 to 20 years."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.6",
            "title": "What LLMs are missing, stated precisely",
            "blocks": [
                {"t": "p", "md": "Foundation models bring us closer to systems with enormous "
                                 "acquired knowledge and skills. But LLMs are missing "
                                 "**recombination**: they fetch and reapply memorized functions "
                                 "well, and cannot recombine them on the fly into new programs."},
                {"t": "p", "md": "They are in fact **entirely incapable of function composition**, "
                                 "as investigated by Dziri et al. And the functions they learn "
                                 "are not sufficiently abstract or modular to be recombined in "
                                 "the first place."},
                {"t": "band", "md": "Remember the low accuracy on adding large integers? "
                                    "==You would not want to build your next codebase on top of "
                                    "such brittle functions.==", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.6 · figure 19.16",
            "title": "A global library, and a perpetual meta-learner",
            "blocks": [
                {"t": "mmd", "id": "ch19-hybrid", "src": MMD_HYBRID,
                 "cap": "Subroutines may be geometric (pretrained deep learning modules) or "
                        "algorithmic (closer to the libraries engineers use today)."},
                {"t": "p", "md": "Think of software development: once an engineer solves HTTP "
                                 "queries in Python, they package it as a reusable library "
                                 "accessible to anyone on the planet. **Any single problem "
                                 "encountered would only need to be solved once** — making such "
                                 "systems constantly self-improving."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 19.4.7",
            "title": "The long-term vision, in four points",
            "blocks": [
                {"t": "steps", "items": [
                    "**Models will be more like programs**, going far beyond continuous "
                    "geometric transformations — closer to the abstract mental models humans "
                    "maintain, and capable of stronger generalization.",
                    "**They will blend algorithmic modules** providing formal reasoning, search, "
                    "and abstraction **with geometric modules** providing intuition and pattern "
                    "recognition. AlphaGo and self-driving cars are an early, hand-built example.",
                    "**They will be grown automatically** rather than hardcoded, from modular "
                    "parts in a global library evolved across thousands of previous tasks — "
                    "frequent problem-solving patterns turned into reusable subroutines.",
                    "**The search over combinations will be discrete** — program synthesis — "
                    "but heavily guided by a form of program-space intuition provided by deep "
                    "learning.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "What to carry into practice",
            "title": "Four things this chapter should change about your work",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "❓", "h": "Ask about familiarity, not difficulty", "style": "accent",
                     "p": "When scoping an LLM deployment, the question is whether the task "
                          "resembles something in web text — **not whether it is hard**."},
                    {"ico": "🧪", "h": "Test with perturbations", "style": "accent",
                     "p": "Change names, numbers, and phrasing that do not change the problem. "
                          "**If the answer changes, you have measured memorization.**"},
                    {"ico": "📏", "h": "Choose the metric carefully", "style": "accent",
                     "p": "The shortcut rule is not a research curiosity. Optimize one number "
                          "and you will get it, **at the expense of everything else** — as "
                          "Netflix did."},
                    {"ico": "🔀", "h": "Expect hybrids", "style": "accent",
                     "p": "The systems that work in the real world today combine learned "
                          "perception with hand-built discrete logic. **Design for that "
                          "combination**, not for an end-to-end network."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "**A deep learning model is a static interpolative database.** The only "
                    "operation it supports is retrieval.",
                    "**Success tracks familiarity, not complexity.** A trivially easy but novel "
                    "problem defeats every current model.",
                    "**Prompt engineering is search**, not communication. Its necessity is "
                    "evidence against understanding.",
                    "**Scale has not moved any of these limits** in seven years and four orders "
                    "of magnitude, because the model is unchanged.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter (2 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**Local, broad, and extreme generalization** are different things. Deep "
                    "learning does the first, and only for anticipated factors of variation.",
                    "**Fixing the task removes the need for intelligence** — and an unintelligent "
                    "solution is always the easier one, so it is the one you get.",
                    "**Intelligence is an efficiency ratio** between information available and "
                    "future operating area — which is what ARC-AGI measures.",
                    "**Test-time adaptation was the 2024 shift**: every top ARC Prize entry used "
                    "it, and o3 crossed the human baseline — at $20,000 a task.",
                    "**Two poles of abstraction**: value-centric for perception, program-centric "
                    "for reasoning. Deep learning has one of them.",
                    "**The way forward is a blend** — program synthesis for discrete structure, "
                    "deep learning to guide the search.",
                ]},
                {"t": "links", "items": [
                    {"k": "PAPER", "ic": "📄", "v": "Chollet, On the Measure of Intelligence (2019)",
                     "href": "https://arxiv.org/abs/1911.01547"},
                    {"k": "SITE", "ic": "🔗", "v": "ARC Prize",
                     "href": "https://arcprize.org/"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 20 — Conclusions",
                     "href": "../ch20/index.html"},
                ]},
            ],
        },
    ],
}
