"""Notebook spec schema, and the .ipynb writer.

Notebooks are authored the same way the decks are: as Python data under
``content/notebooks/``, rendered by a tool. The reason is the same too --
``.ipynb`` is a JSON file with execution counts and output blobs in it, which
makes hand-editing tedious and code review nearly useless. Authoring the source
and generating the artifact keeps the diffs readable.

--------------------------------------------------------------------------------
A notebook spec
--------------------------------------------------------------------------------
    file        str   the filename, e.g. "01_tokenizers.ipynb"
    title       str   H1 of the notebook
    lede        str   one paragraph under the title
    needs       str   what it takes to run: "CPU - 2 min", "GPU - 45 min", ...
    section     str   which deck section this notebook belongs to (shown in the
                      header, so a participant can find the matching slides)
    cells       list  of (kind, body) tuples -- see below
    takeaways   list  of str, rendered as the closing checklist

--------------------------------------------------------------------------------
Cell kinds
--------------------------------------------------------------------------------
    ("md",   "markdown source")        a prose cell
    ("h2",   "A heading")              shorthand for a markdown "## " cell
    ("py",   "code")                   a code cell
    ("note", "text")                   a callout, rendered as a blockquote
    ("warn", "text")                   a callout that should stop you
    ("out",  "text")                   expected output, shown as a fenced block
                                       in markdown rather than as a fake result

``out`` deliberately renders as *markdown*, never as a stored cell output. A
committed notebook in this course has no execution counts and no output blobs:
what you see when you open it is what the author wrote, and what appears after
you run it is what your machine actually produced. Those two should never be
confused, least of all in teaching material.
"""

import json
import os

CELL_KINDS = {"md", "h2", "py", "note", "warn", "out"}


def validate(nb, where=""):
    errs = []
    for key in ("file", "title", "cells"):
        if not nb.get(key):
            errs.append(f"{where}{nb.get('file', '?')}: missing {key!r}")
    if not str(nb.get("file", "")).endswith(".ipynb"):
        errs.append(f"{where}{nb.get('file')}: filename must end in .ipynb")
    for i, cell in enumerate(nb.get("cells", [])):
        if not isinstance(cell, (tuple, list)) or len(cell) != 2:
            errs.append(f"{where}{nb['file']} cell {i}: expected (kind, body)")
            continue
        if cell[0] not in CELL_KINDS:
            errs.append(f"{where}{nb['file']} cell {i}: unknown kind {cell[0]!r}")
    if errs:
        raise ValueError("\n".join(errs))


def _md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(src)}


def _code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": _lines(src)}


def _lines(src):
    """nbformat wants a list of lines, each keeping its own newline except the
    last. Splitting this way keeps git diffs line-by-line rather than one giant
    changed string."""
    text = src.strip("\n")
    if not text:
        return []
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]


def _header(nb, deck_id, deck_title, chapter):
    where = f"Chapter {chapter}" if chapter is not None else "Module"
    bits = [f"# {nb['title']}", ""]
    if nb.get("lede"):
        bits += [nb["lede"], ""]
    meta = []
    if nb.get("needs"):
        meta.append(f"**Runs on:** {nb['needs']}")
    meta.append(f"**Slides:** [{where} — {deck_title}]"
                f"(../../../course-web-slides/{deck_id}/index.html)")
    if nb.get("section"):
        meta.append(f"**Section:** {nb['section']}")
    bits += [" &nbsp;·&nbsp; ".join(meta), "",
             "---"]
    return "\n".join(bits)


def _footer(nb):
    if not nb.get("takeaways"):
        return None
    items = "\n".join(f"- {t}" for t in nb["takeaways"])
    return f"---\n\n## What to take away\n\n{items}\n"


def render(nb, deck_id, deck_title, chapter):
    """Spec -> nbformat 4.4 dict, with no outputs and no execution counts."""
    cells = [_md(_header(nb, deck_id, deck_title, chapter))]
    for kind, body in nb["cells"]:
        if kind == "py":
            cells.append(_code(body))
        elif kind == "h2":
            cells.append(_md("## " + body.strip()))
        elif kind == "note":
            cells.append(_md("> **Note** — " + body.strip()))
        elif kind == "warn":
            cells.append(_md("> ⚠️ **" + body.strip()))
        elif kind == "out":
            cells.append(_md("Expected output:\n\n```\n" + body.strip("\n") + "\n```"))
        else:
            cells.append(_md(body))
    foot = _footer(nb)
    if foot:
        cells.append(_md(foot))

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3 (course venv)",
                           "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }


def write(nb, outdir, deck_id, deck_title, chapter):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, nb["file"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(render(nb, deck_id, deck_title, chapter), f,
                  indent=1, ensure_ascii=False)
        f.write("\n")
    return path
