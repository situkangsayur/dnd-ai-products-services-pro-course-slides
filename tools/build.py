#!/usr/bin/env python3
"""Build every deck: content/<id>.py  ->  decks/<id>/  +  latex/<id>.tex

    python3 tools/build.py               # all decks, web + latex sources
    python3 tools/build.py ch01 ch02     # just these
    python3 tools/build.py --pdf         # also run latexmk on each .tex
    python3 tools/build.py --list        # show what is registered

Content modules are discovered by filename, so adding content/ch07.py is all it
takes to add a deck.
"""

import argparse
import importlib.util
import re
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import gen_latex          # noqa: E402
import gen_web            # noqa: E402
import schema             # noqa: E402

# The course lives in four sibling repositories. This one (course-slides) holds
# the single source of truth under content/ and renders into two of them:
#   latex/          -> here, in this repo (Beamer sources + PDFs)
#   ../course-web-slides/<id>/  -> the web-deck repo
# WEB_DECKS can be pointed elsewhere with COURSE_WEB_SLIDES_DIR when the sibling
# checkout is not next to this one.
CONTENT = os.path.join(ROOT, "content")
LATEX = os.path.join(ROOT, "latex")
WEB_DECKS = os.environ.get(
    "COURSE_WEB_SLIDES_DIR",
    os.path.join(os.path.dirname(ROOT), "course-web-slides"))
PDF_OUT = os.path.join(WEB_DECKS, "pdf")


def load(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location("content_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "DECK"):
        raise ValueError(f"{path}: module defines no DECK")
    return mod.DECK


def discover(only):
    if not os.path.isdir(CONTENT):
        return []
    names = sorted(f for f in os.listdir(CONTENT)
                   if f.endswith(".py") and not f.startswith("_"))
    out = []
    for f in names:
        did = os.path.splitext(f)[0]
        if only and did not in only:
            continue
        out.append((did, os.path.join(CONTENT, f)))
    return out


OVERFULL = re.compile(r"Overfull \\vbox \((\d+(?:\.\d+)?)pt too high\) .*?at line (\d+)")


def build_pdf(texfile):
    """latexmk, quiet, from inside latex/ so itbpro.sty and the logo resolve.

    Also reports overfull vboxes. A slide that spills off the plate is a content
    problem -- too much on one frame -- and the only place it shows up is this
    warning, so it is surfaced rather than buried in the log.
    """
    r = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
         "-file-line-error", os.path.basename(texfile)],
        cwd=LATEX, capture_output=True, text=True)
    if r.returncode != 0:
        return False, (r.stdout or "")[-2500:], []
    log = os.path.join(LATEX, os.path.basename(texfile)[:-4] + ".log")
    spills = []
    if os.path.exists(log):
        with open(log, encoding="utf-8", errors="replace") as f:
            text = f.read()
        seen = set()
        for pt, line in OVERFULL.findall(text):
            if line not in seen:
                seen.add(line)
                spills.append((int(float(pt)), int(line)))
    return True, "", sorted(spills, reverse=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="deck ids to build (default: all)")
    ap.add_argument("--pdf", action="store_true", help="compile the .tex files too")
    ap.add_argument("--list", action="store_true", help="list registered decks")
    args = ap.parse_args()

    found = discover(set(args.ids))
    if args.list:
        for did, path in found:
            d = load(path)
            n = sum(1 for s in d["slides"])
            print(f"{did:22s} {n:3d} slides  {d['title']}")
        return 0

    if not found:
        print("No content modules found in content/ — nothing to build.")
        return 0

    fails = []
    overfull = []
    total_slides = 0
    for did, path in found:
        try:
            deck = load(path)
            schema.validate(deck)
            n = gen_web.write(deck, os.path.join(WEB_DECKS, deck["id"]))
            tex = gen_latex.write(deck, LATEX)
            total_slides += n
            line = (f"  {deck['id']:20s} {n:3d} slides  ->  "
                    f"latex/{deck['id']}.tex + course-web-slides/{deck['id']}/")
            if args.pdf:
                ok, err, spills = build_pdf(tex)
                if spills:
                    overfull.append((deck["id"], spills))
                if ok:
                    # Publish the PDF beside the web deck so the "download PDF"
                    # link on the course site resolves without a second build.
                    os.makedirs(PDF_OUT, exist_ok=True)
                    shutil.copy2(os.path.join(LATEX, deck["id"] + ".pdf"),
                                 os.path.join(PDF_OUT, deck["id"] + ".pdf"))
                if ok:
                    line += "  [pdf ok]"
                    if spills:
                        line += f"  [{len(spills)} slide melimpah]"
                else:
                    line += "  [PDF FAILED]"
                if not ok:
                    fails.append((deck["id"], err))
            print(line)
        except Exception as e:                      # noqa: BLE001 - report and continue
            fails.append((did, str(e)))
            print(f"  {did:20s} FAILED: {e}")

    print(f"\n{len(found)} deck(s), {total_slides} slides total.")
    if overfull:
        print("\nSlide yang melimpah keluar halaman (kurangi isinya):")
        for did, spills in overfull:
            for pt, line in spills:
                print(f"  {did}.tex baris {line:5d}  {pt:4d}pt")
    if fails:
        print(f"\n{len(fails)} failure(s):")
        for did, err in fails:
            print(f"\n--- {did} ---\n{err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
