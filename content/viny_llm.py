# -*- coding: utf-8 -*-
"""Module deck — Large Language Models (TEMPLATE).

Structure only. The content is authored separately by the module owner, who may
deliver it as PDF or PPTX instead; this file exists so that (a) the course site
has a real deck to link to from day one, and (b) if the module is authored here,
every slide type it will plausibly need is already demonstrated and rendering
correctly in both outputs.

Every slide below is either scaffolding or a worked demonstration of one block
kind. Slides carrying no final content are marked with a PENDING band, so that
an unfinished deck cannot be mistaken for a finished one on screen.

To fill this in: replace the PENDING bands and the placeholder prose. Delete
any scaffold slide that turns out not to be needed. The deck lints as a
``module``, so there is no minimum slide count to satisfy.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import COURSE  # noqa: E402


PENDING = ("**Content pending.** This slide is scaffolding — the structure is fixed, "
           "the material is authored separately by the module owner.")

MMD_ARC = """
flowchart TB
  A["<b>Section outline</b><br/><small>replace with the module's<br/>own structure</small>"]
  B["Pretraining"]
  C["Adaptation<br/><small>fine-tuning, LoRA, RLHF</small>"]
  D["Retrieval<br/><small>RAG, re-rankers</small>"]
  E["Serving and guardrails"]
  A --> B --> C --> D --> E
"""

MMD_RAG = """
flowchart LR
  Q["Query"]
  R["<b>Retriever</b><br/><small>dense, sparse, or hybrid</small>"]
  K["Top-k candidates"]
  RR["<b>Re-ranker</b><br/><small>cross-encoder over<br/>query and candidate</small>"]
  C["Ordered context"]
  G["<b>Generator</b>"]
  A["Grounded answer"]
  Q --> R --> K --> RR --> C --> G --> A
  Q --> RR
"""


RESOURCES = [
    {"kind": "site", "label": "Course home", "href": "../../index.html"},
]

DECK = {
    "id": "viny-llm",
    "kind": "module",
    "number": None,
    # Bukan dari buku — isinya ditulis sendiri. Pemiliknya masuk manifes
    # supaya galeri bisa mengelompokkannya, bukan sekadar menyebutnya
    # "standalone".
    "owner": "Viny",

    "title": "Large Language Models",
    "subtitle": "Fine-tuning, retrieval, re-ranking, and guardrails — the practitioner's "
                "layer on top of chapters 15 and 16.",
    "source": "Module material for " + COURSE["title"],
    "source_url": "https://scholar.google.com/citations?user=hayqUI0AAAAJ&hl=en",
    "duration": "3 hours (2 sessions)",
    "presenter": {"name": "Viny Christanti Mawardi, S.Kom., M.Kom.",
                  "role": "Teaching Assistant"},
    "resources": RESOURCES,
    "objectives": [
        "*Objectives pending — to be written by the module owner.*",
        "Placeholder: explain the **pretraining / adaptation / retrieval** division "
        "of labour.",
        "Placeholder: choose between **full fine-tuning, LoRA, and prompting** for a "
        "given problem.",
        "Placeholder: build a **retrieval pipeline** with a re-ranker and measure it.",
        "Placeholder: specify **guardrails** for a production deployment.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "About this deck",
            "title": "This is a template, not the module",
            "blocks": [
                {"t": "band", "md": "**This deck is scaffolding.** The structure, theme, and "
                                    "rendering are fixed; the material is authored separately by "
                                    "the module owner and may be delivered as PDF or PPTX "
                                    "instead.", "style": "amber"},
                {"t": "p", "md": "It exists so the course site has a real deck to link to from "
                                 "day one, and so that — if the module is authored here — every "
                                 "block kind it will plausibly need is already demonstrated and "
                                 "verified in both the LaTeX and the web output."},
                {"t": "p", "md": "Slides carrying no final content are marked with an amber band, "
                                 "so that an unfinished deck **cannot be mistaken for a finished "
                                 "one** on screen."},
            ],
            "notes": "Delete this slide once the module has real content.",
        },

        {
            "type": "slide",
            "kicker": "Where this module sits",
            "title": "On top of chapters 15 and 16",
            "blocks": [
                {"t": "p", "md": "Chapter 15 built the Transformer and fine-tuned an encoder. "
                                 "Chapter 16 built a mini-GPT, sampled from it, and "
                                 "instruction-tuned a pretrained model under LoRA."},
                {"t": "p", "md": "This module takes all of that as given and covers the "
                                 "**practitioner's layer**: what you do when the model is "
                                 "someone else's, the data is yours, and the answer has to be "
                                 "right."},
                {"t": "mmd", "id": "viny-arc", "src": MMD_ARC,
                 "cap": "Placeholder outline — replace with the module's own structure."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "Pretraining and adaptation",
         "lead": "Section lead pending."},

        {
            "type": "slide",
            "kicker": "Section 01",
            "title": "Adaptation options, side by side",
            "blocks": [
                {"t": "p", "md": "A comparison table is usually the right opening for this "
                                 "material. The row structure below is a suggestion; the "
                                 "entries are placeholders."},
                {"t": "table",
                 "head": ["Approach", "When it fits", "What it costs"],
                 "widths": [26, 38, 36],
                 "rows": [
                     ["**Prompting**", "*pending*", "*pending*"],
                     ["**Few-shot prompting**", "*pending*", "*pending*"],
                     ["**LoRA fine-tuning**", "*pending*", "*pending*"],
                     ["**Full fine-tuning**", "*pending*", "*pending*"],
                     ["**Continued pretraining**", "*pending*", "*pending*"],
                 ]},
                {"t": "band", "md": PENDING, "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 01 · block demo",
            "title": "Code and output render like this",
            "blocks": [
                {"t": "p", "md": "A code block always needs prose before and after it — the "
                                 "build lints for this, and the check applies to module decks "
                                 "too."},
                {"t": "code", "lang": "python", "file": "placeholder", "src": """import keras_hub

backbone = keras_hub.models.Backbone.from_preset("...")
backbone.enable_lora(rank=8)"""},
                {"t": "out", "src": """ Total params:         ...
 Trainable params:     ...
 Non-trainable params: ..."""},
                {"t": "p", "md": "Program output uses the `out` block, which renders in a "
                                 "distinct panel so a result is never mistaken for source."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "Retrieval and re-ranking",
         "lead": "Section lead pending."},

        {
            "type": "slide",
            "kicker": "Section 02",
            "title": "Where the re-ranker sits",
            "blocks": [
                {"t": "p", "md": "Chapter 16 introduced RAG as *retrieve, then put it in the "
                                 "prompt*. The practitioner's version has one more stage, and it "
                                 "is usually where the quality comes from."},
                {"t": "mmd", "id": "viny-rag", "src": MMD_RAG,
                 "cap": "The retriever optimises recall cheaply; the re-ranker optimises "
                        "precision expensively, over far fewer candidates."},
                {"t": "band", "md": PENDING, "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 02 · block demo",
            "title": "Cards, stats, and quotes render like this",
            "blocks": [
                {"t": "stats", "cols": 3, "items": [
                    {"v": "—", "l": "recall@k, pending"},
                    {"v": "—", "l": "nDCG, pending"},
                    {"v": "—", "l": "latency, pending"},
                ]},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔍", "h": "Dense retrieval", "style": "accent", "p": "*pending*"},
                    {"ico": "🔤", "h": "Sparse retrieval", "style": "accent", "p": "*pending*"},
                    {"ico": "🔗", "h": "Hybrid", "style": "accent", "p": "*pending*"},
                ]},
                {"t": "quote", "md": "A pull quote renders like this — useful for a definition "
                                     "or a finding worth stopping on.",
                 "cite": "Attribution line"},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "Guardrails and evaluation",
         "lead": "Section lead pending."},

        {
            "type": "slide",
            "kicker": "Section 03",
            "title": "What has to be checked, and where",
            "blocks": [
                {"t": "steps", "items": [
                    "*Step one — pending.*",
                    "*Step two — pending.*",
                    "*Step three — pending.*",
                ]},
                {"t": "band", "md": PENDING, "style": "amber"},
                {"t": "p", "md": "Numbered steps use the `steps` block; unordered points use "
                                 "`bullets`. Both wrap correctly in the LaTeX output at any "
                                 "length."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "Summary slide — pending",
            "blocks": [
                {"t": "steps", "items": [
                    "*Takeaway one — pending.*",
                    "*Takeaway two — pending.*",
                    "*Takeaway three — pending.*",
                ]},
                {"t": "links", "items": [
                    {"k": "BACK", "ic": "⬅", "v": "Chapter 16 — Text generation",
                     "href": "../ch16/index.html"},
                    {"k": "NEXT", "ic": "➡", "v": "Agentic AI",
                     "href": "../hendri-agentic/index.html"},
                ]},
            ],
        },
    ],
}
