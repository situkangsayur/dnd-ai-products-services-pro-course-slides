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
    "table", "quote", "band", "fig", "mmd", "img", "links", "cols",
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


# =============================================================================
#  Quality rules
#  These are not style preferences; each one encodes a failure we actually hit
#  while authoring, and each is checked on every build so it cannot come back.
# =============================================================================

# Blocks that count as explanation around a listing.
PROSE_KINDS = {"p", "lead", "bullets", "steps", "band", "quote",
               "table", "cards", "stats", "out", "fig"}

# Rough visual weight of one block, in "lines of slide". Tuned against the
# rendered decks: a slide over MAX_WEIGHT overflows or has to be shrunk so far
# that the room can no longer read it.
WEIGHT = {
    "p": 3.2, "lead": 3.6, "bullets": 2.0, "steps": 2.4, "cards": 7.0,
    "stats": 5.0, "code": 1.15, "out": 1.15, "table": 2.2, "quote": 5.0,
    "band": 3.6, "fig": 12.0, "mmd": 13.0, "img": 13.0, "links": 3.0,
}
MAX_WEIGHT = 34.0          # above this a slide is too dense: split it
HEADROOM_WEIGHT = 6.0      # below this it is too thin: merge or add substance


def _flatten(blocks):
    out = []
    for b in blocks:
        if b.get("t") == "cols":
            for col in b.get("cols", []):
                out.extend(_flatten(col))
        else:
            out.append(b)
    return out


def _weight(blocks):
    """Estimated vertical weight of a slide body.

    Columns are counted at the weight of their heaviest column, since they sit
    side by side rather than stacking.
    """
    total = 0.0
    for b in blocks:
        t = b.get("t")
        if t == "cols":
            total += max((_weight(col) for col in b.get("cols", [])), default=0.0)
        elif t == "code":
            total += WEIGHT["code"] * (b.get("src", "").count("\n") + 3)
        elif t == "out":
            total += WEIGHT["out"] * (b.get("src", "").count("\n") + 3)
        elif t == "bullets":
            total += WEIGHT["bullets"] * len(b.get("items", []))
        elif t == "steps":
            total += WEIGHT["steps"] * len(b.get("items", []))
        elif t == "table":
            total += WEIGHT["table"] * (len(b.get("rows", [])) + 1.6)
        elif t == "cards":
            rows = -(-len(b.get("items", [])) // (b.get("cols") or 3))
            total += WEIGHT["cards"] * rows
        elif t == "stats":
            rows = -(-len(b.get("items", [])) // (b.get("cols") or 4))
            total += WEIGHT["stats"] * rows
        else:
            total += WEIGHT.get(t, 2.0)
    return total


def lint(deck, strict=False):
    """Return a list of quality warnings for one deck.

    Rules
      code-unexplained  a listing with no prose before AND after it. A slide
                        that drops code on the room with no lead-in and no
                        takeaway teaches nothing.
      slide-too-dense   body weight over MAX_WEIGHT; it will be scaled down
                        past readability. Split it.
      deck-too-short    a book chapter under MIN_CHAPTER_SLIDES; the chapter is
                        almost certainly not covered.
      no-figure         a content-heavy chapter deck with too few diagrams.
    """
    warns = []
    did = deck.get("id", "?")
    slides = [s for s in deck.get("slides", []) if s.get("type") == "slide"]

    for i, s in enumerate(slides):
        blocks = s.get("blocks", [])
        seq = _flatten(blocks)
        kinds = [b.get("t") for b in seq]

        for j, t in enumerate(kinds):
            if t != "code":
                continue
            before = any(k in PROSE_KINDS for k in kinds[:j])
            after = any(k in PROSE_KINDS for k in kinds[j + 1:])
            if not before or not after:
                missing = []
                if not before:
                    missing.append("no lead-in")
                if not after:
                    missing.append("no follow-through")
                warns.append(
                    f"{did}: code-unexplained  \"{s.get('title', '')[:46]}\" ({', '.join(missing)})")
                break

        w = _weight(blocks)
        if w > MAX_WEIGHT:
            warns.append(f"{did}: slide-too-dense   \"{s.get('title', '')[:46]}\" "
                         f"(weight {w:.0f} > {MAX_WEIGHT:.0f})")

    if deck.get("kind") == "chapter":
        if len(slides) < MIN_CHAPTER_SLIDES:
            warns.append(f"{did}: deck-too-short    {len(slides)} content slides "
                         f"(< {MIN_CHAPTER_SLIDES})")
        figs = sum(1 for s in slides for b in _flatten(s.get("blocks", []))
                   if b.get("t") in ("fig", "mmd", "img"))
        want = max(6, len(slides) // 6)
        if figs < want:
            warns.append(f"{did}: too-few-figures   {figs} diagrams (want >= {want})")

    return warns


MIN_CHAPTER_SLIDES = 34
