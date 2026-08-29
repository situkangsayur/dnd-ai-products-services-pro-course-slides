"""Slide content schema for the ITB × BRI course decks.

One deck is authored ONCE, as a Python module under ``content/`` exporting a
``DECK`` dict. Two renderers consume it:

    tools/gen_web.py    ->  decks/<id>/slides.js   (web deck)
    tools/gen_latex.py  ->  latex/<id>.tex         (Beamer deck)

Authoring in Python rather than JSON buys triple-quoted strings, which is what
makes the long code listings in this course bearable to write.

--------------------------------------------------------------------------------
DECK
--------------------------------------------------------------------------------
    id          str   slug, e.g. "ch01"; becomes the deck folder and .tex name
    kind        str   "chapter" | "module"
    number      int   chapter number, or None for the standalone modules
    title       str   deck title
    subtitle    str   one line under the title
    source      str   provenance line shown on the cover and in the LaTeX colophon
    source_url  str   canonical URL for the source chapter
    duration    str   indicative session length, e.g. "90 menit"
    presenter   dict  {"name", "role"} — who delivers it
    resources   list  [{"kind","label","href"}]  kind: notebook|github|book|paper|tool
    objectives  list  of str — what the participant can do afterwards
    slides      list  of slide dicts (below)

--------------------------------------------------------------------------------
SLIDES
--------------------------------------------------------------------------------
Every slide is ``{"type": ..., "title": ...}`` plus type-specific keys.

    {"type": "title"}
        Rendered from the DECK header; no extra keys needed.

    {"type": "section", "num": "01", "title": "...", "lead": "..."}
        Divider slide.

    {"type": "slide", "kicker": "...", "title": "...", "blocks": [...],
     "notes": "..."}
        The workhorse. ``notes`` shows in the presenter console and becomes
        \\note{} in Beamer.

--------------------------------------------------------------------------------
BLOCKS  — the ``t`` key selects the kind
--------------------------------------------------------------------------------
    {"t":"p",       "md": "..."}                        paragraph
    {"t":"lead",    "md": "..."}                         larger intro paragraph
    {"t":"bullets", "items": ["...", ...]}
    {"t":"steps",   "items": ["...", ...]}               numbered
    {"t":"cards",   "cols": 3, "items":[
        {"ico":"🧠","h":"Heading","p":"body","tag":"label","style":"accent"}]}
        style: "" | accent | warn | good | bad
    {"t":"stats",   "items":[{"v":"3","l":"label"}], "cols": 4}
    {"t":"code",    "lang":"python", "file":"listing 2.1", "src":"..."}
    {"t":"out",     "src":"..."}                         program output
    {"t":"table",   "head":[...], "rows":[[...],...], "widths":[...]}
    {"t":"quote",   "md":"...", "cite":"..."}
    {"t":"band",    "md":"...", "style":"" | "amber" | "rose"}
    {"t":"fig",     "svg":"<svg .../>", "tikz":"...", "cap":"..."}
        ``svg`` renders on the web, ``tikz`` in LaTeX. Either may be omitted;
        the other renderer then falls back to the caption alone.
    {"t":"links",   "items":[{"k":"NOTEBOOK","v":"ch02_tensors.ipynb",
                              "href":"...", "pending": False}]}
    {"t":"cols",    "cols": [[block, ...], [block, ...]], "ratio": "1-1"}
        ratio: "1-1" | "2-1" | "1-2" | "3-2"

--------------------------------------------------------------------------------
INLINE MARKUP  (inside any ``md`` / list item / table cell)
--------------------------------------------------------------------------------
    **bold**            `code`            [label](href)
    *italic*            ==highlight==     --> becomes an em dash in LaTeX
"""

BLOCK_KINDS = {
    "p", "lead", "bullets", "steps", "cards", "stats", "code", "out",
    "table", "quote", "band", "fig", "links", "cols",
}

SLIDE_TYPES = {"title", "section", "slide"}

CARD_STYLES = {"", "accent", "warn", "good", "bad"}

RESOURCE_KINDS = {"notebook", "github", "book", "paper", "tool", "dataset", "site"}


def validate(deck):
    """Raise ValueError on anything the renderers cannot handle.

    Cheap structural checks only — this runs on every build so that a typo in a
    block name fails at generation time rather than silently dropping a slide.
    """
    errs = []
    did = deck.get("id", "<no id>")

    for key in ("id", "title", "slides"):
        if not deck.get(key):
            errs.append(f"{did}: missing required deck key {key!r}")

    for kind in (r.get("kind") for r in deck.get("resources", [])):
        if kind not in RESOURCE_KINDS:
            errs.append(f"{did}: unknown resource kind {kind!r}")

    def check_blocks(blocks, where):
        for j, b in enumerate(blocks):
            t = b.get("t")
            if t not in BLOCK_KINDS:
                errs.append(f"{did}: {where} block {j}: unknown kind {t!r}")
                continue
            if t == "cards":
                for c in b.get("items", []):
                    if c.get("style", "") not in CARD_STYLES:
                        errs.append(f"{did}: {where} card style {c.get('style')!r}")
            if t == "table":
                width = len(b.get("head", []))
                for r, row in enumerate(b.get("rows", [])):
                    if len(row) != width:
                        errs.append(
                            f"{did}: {where} table row {r} has {len(row)} cells, "
                            f"header has {width}")
            if t == "cols":
                for k, col in enumerate(b.get("cols", [])):
                    check_blocks(col, f"{where}>col{k}")

    for i, s in enumerate(deck.get("slides", [])):
        st = s.get("type")
        if st not in SLIDE_TYPES:
            errs.append(f"{did}: slide {i}: unknown type {st!r}")
            continue
        if st == "slide":
            if not s.get("title"):
                errs.append(f"{did}: slide {i}: missing title")
            check_blocks(s.get("blocks", []), f"slide {i}")

    if errs:
        raise ValueError("\n".join(errs))
    return True
