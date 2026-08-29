#!/usr/bin/env python3
"""Render every notebook spec under content/notebooks/ into notebooks/.

    python3 tools/build_notebooks.py            # all
    python3 tools/build_notebooks.py ch14 ch15  # some

Each spec module exports ``NOTEBOOKS``: a list of specs, plus ``DECK`` naming
the deck it accompanies. The filenames are cross-checked against the notebook
resources the decks declare, so a deck that links to a notebook nobody wrote --
or a notebook nothing links to -- is reported rather than shipped.
"""

import argparse
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import nbschema  # noqa: E402

SPECS = os.path.join(ROOT, "content", "notebooks")
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "notebooks")


def load(path, prefix):
    spec = importlib.util.spec_from_file_location(prefix + os.path.basename(path), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def deck_notebooks(deck_id):
    """The notebook filenames the deck itself advertises."""
    path = os.path.join(CONTENT, deck_id.replace("-", "_") + ".py")
    if not os.path.exists(path):
        return None, None
    d = load(path, "deck_").DECK
    names = [r["label"] for r in d.get("resources", []) if r.get("kind") == "notebook"]
    return d, names


def discover(only):
    out = []
    for name in sorted(os.listdir(SPECS)):
        if not name.endswith(".py") or name.startswith("_"):
            continue
        did = name[:-3]
        if only and did not in only:
            continue
        out.append((did, os.path.join(SPECS, name)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    args = ap.parse_args()

    found = discover(set(args.ids))
    if not found:
        print("No notebook specs found in content/notebooks/.")
        return 0

    problems, total = [], 0
    for did, path in found:
        mod = load(path, "nb_")
        deck_id = getattr(mod, "DECK", did)
        deck, declared = deck_notebooks(deck_id)
        if deck is None:
            problems.append(f"{did}: no deck content/{deck_id}.py to accompany")
            continue

        outdir = os.path.join(OUT, deck_id)
        written = []
        for nb in mod.NOTEBOOKS:
            nbschema.validate(nb, where=f"{did}: ")
            nbschema.write(nb, outdir, deck["id"], deck["title"], deck.get("number"))
            written.append(nb["file"])
        total += len(written)

        missing = [n for n in (declared or []) if n not in written]
        extra = [n for n in written if n not in (declared or [])]
        if missing:
            problems.append(f"{deck_id}: deck links to unwritten notebooks: "
                            + ", ".join(missing))
        if extra:
            problems.append(f"{deck_id}: notebooks nothing links to: " + ", ".join(extra))

        cells = sum(len(nb["cells"]) for nb in mod.NOTEBOOKS)
        code = sum(sum(1 for k, _ in nb["cells"] if k == "py") for nb in mod.NOTEBOOKS)
        print(f"  {deck_id:16s} {len(written)} notebooks  "
              f"{cells:3d} cells ({code} code)  ->  notebooks/{deck_id}/")

    print(f"\n{len(found)} chapter(s), {total} notebooks total.")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  " + p)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
