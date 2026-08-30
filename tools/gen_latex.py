"""Render a DECK dict to a Beamer deck: latex/<id>.tex.

Pairs with latex/itbpro.sty. Run through tools/build.py rather than directly.
"""

import os

import figures
import schema

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from course import presenter_names, presenter_roles
from course import absolute  # noqa: E402
from inline import tex as it, esc_tex, tex_url

RES_LABEL = {
    "notebook": "Notebook", "github": "Repo", "book": "Book",
    "paper": "Paper", "tool": "Tool", "dataset": "Dataset", "site": "Site",
}

CARD_ENV = {"": "icard", "accent": "icardaccent", "warn": "icardwarn",
            "good": "icardgood", "bad": "icardbad"}

BAND_COLOR = {"": "signal", "amber": "amber", "rose": "rose"}

RATIO_FRAC = {"1-1": (0.485, 0.485), "2-1": (0.645, 0.325),
              "1-2": (0.325, 0.645), "3-2": (0.575, 0.395)}


def _minipages(fracs, bodies):
    """Lay bodies side by side. Beamer columns misbehave inside tcolorbox, so
    plain minipages are used throughout."""
    out = []
    for i, (f, body) in enumerate(zip(fracs, bodies)):
        sep = "\\hfill\n" if i else ""
        out.append(f"{sep}\\begin{{minipage}}[t]{{{f}\\textwidth}}\n"
                   f"{body}\n\\end{{minipage}}%")
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------- blocks ----

def _cards(b):
    items = b.get("items", [])
    cols = b.get("cols") or min(len(items) or 1, 3)
    gap = 0.012
    frac = round((1.0 - gap * (cols - 1)) / cols, 4)
    out = []
    for i, c in enumerate(items):
        env = CARD_ENV.get(c.get("style", ""), "icard")
        body = []
        if c.get("h"):
            body.append(r"\cardh{%s}" % it(c["h"]))
        if c.get("p"):
            body.append(it(c["p"]))
        if c.get("tag"):
            body.append(r"\cardtag{%s}" % it(c["tag"]))
        cell = (f"\\begin{{{env}}}\n" + "\n".join(body) + f"\n\\end{{{env}}}")
        sep = "" if i % cols == 0 else "\\hfill\n"
        out.append(f"{sep}\\begin{{minipage}}[t]{{{frac}\\textwidth}}\n{cell}\n\\end{{minipage}}%")
        if i % cols == cols - 1 and i != len(items) - 1:
            out.append("\n\n\\vskip 4pt\n")
    return "\n".join(out) + "\n"


def _stats(b):
    items = b.get("items", [])
    cols = b.get("cols") or min(len(items) or 1, 4)
    frac = round((1.0 - 0.012 * (cols - 1)) / cols, 4)
    out = []
    for i, s in enumerate(items):
        sep = "" if i % cols == 0 else "\\hfill\n"
        out.append(f"{sep}\\begin{{minipage}}[t]{{{frac}\\textwidth}}\n"
                   f"\\istat{{{it(s.get('v', ''))}}}{{{it(s.get('l', ''))}}}\n"
                   f"\\end{{minipage}}%")
        if i % cols == cols - 1 and i != len(items) - 1:
            out.append("\n\n\\vskip 4pt\n")
    return "\n".join(out) + "\n"


def _table(b):
    head = b.get("head", [])
    widths = b.get("widths")
    if widths:
        total = sum(widths)
        spec = "".join(">{\\raggedright\\arraybackslash}p{%s\\textwidth}" % round(w / total * 0.94, 4)
                       for w in widths)
    else:
        n = len(head)
        spec = "".join(">{\\raggedright\\arraybackslash}p{%s\\textwidth}" % round(0.94 / n, 4)
                       for _ in range(n))
    rows = [" & ".join(r"\thead{%s}" % it(h) for h in head) + r" \\ \midrule"]
    for row in b.get("rows", []):
        cells = [it(c) for c in row]
        # A first cell beginning with "[" would be swallowed by the preceding
        # \\ as its optional vertical-space argument -- a cell reading "[end]"
        # aborts the build with "Missing number, treated as zero".
        if cells and cells[0].startswith("["):
            cells[0] = "{}" + cells[0]
        rows.append(" & ".join(cells) + r" \\")
    return (f"\\begin{{itable}}{{{spec}}}\n" + "\n".join(rows) + "\n\\end{itable}\n")


def _links(b):
    out = []
    for l in b.get("items", []):
        v = esc_tex(l.get("v", ""))
        if l.get("pending"):
            out.append(r"\reslink{%s}{%s}{}" % (esc_tex(l.get("k", "")), v + r"~\textit{(menyusul)}"))
        else:
            out.append(r"\reslink{%s}{%s}{%s}" % (
                esc_tex(l.get("k", "")), v,
                tex_url(absolute(l.get("href", "")))))
    return "\\vskip 4pt\n" + "\n".join(out) + "\n\\vskip 2pt\n"


EXT = {"python": "py", "py": "py", "bash": "sh", "sh": "sh", "json": "json",
       "yaml": "yaml", "text": "txt"}

# Filled per deck by build(); listings are written next to the .tex.
_SIDECAR = {"dir": None, "deck": None, "n": 0, "written": []}


def _sidecar(src, ext):
    r"""Write one listing to latex/listings/ and return its \input-able path.

    Keeping code in real files is what lets these frames avoid [fragile] (and
    therefore keep [shrink]); it also means every listing on a slide exists as a
    file a participant can actually run.
    """
    _SIDECAR["n"] += 1
    name = f"{_SIDECAR['deck']}-{_SIDECAR['n']:02d}.{ext}"
    path = os.path.join(_SIDECAR["dir"], name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src.rstrip("\n") + "\n")
    _SIDECAR["written"].append(path)
    return "listings/" + name


def _code(b):
    lang = b.get("lang", "python")
    label = b.get("file", "")
    rel = _sidecar(b.get("src", "").strip("\n"), EXT.get(lang, "txt"))
    return "\\icode{%s}{%s}{%s}\n" % (lang, esc_tex(label), rel)


def render_block(b, depth=0):
    t = b["t"]
    if t == "p":
        return "{\\fontsize{9.4}{12.6}\\selectfont\\color{fg2}%s\\par}\\vskip 4pt\n" % it(b["md"])
    if t == "lead":
        return r"\leadpar{%s}" % it(b["md"]) + "\n"
    if t == "bullets":
        items = "\n".join(r"\item %s" % it(i) for i in b["items"])
        return "\\begin{ibullets}\n%s\n\\end{ibullets}\n" % items
    if t == "steps":
        items = "\n".join(r"\item %s" % it(i) for i in b["items"])
        return "\\begin{isteps}\n%s\n\\end{isteps}\n" % items
    if t == "cards":
        return _cards(b)
    if t == "stats":
        return _stats(b)
    if t == "code":
        return _code(b)
    if t == "out":
        return "\\ioutput{%s}\n" % _sidecar(b["src"].strip("\n"), "txt")
    if t == "table":
        return _table(b)
    if t == "quote":
        cite = r"\quotecite{%s}" % it(b["cite"]) if b.get("cite") else ""
        return "\\begin{iquote}\n\\quotetext{%s}%s\n\\end{iquote}\n" % (it(b["md"]), cite)
    if t == "band":
        col = BAND_COLOR.get(b.get("style", ""), "signal")
        return "\\begin{iband}[%s]\n%s\n\\end{iband}\n" % (col, it(b["md"]))
    if t == "fig":
        tikz = b.get("tikz")
        cap = (r"\vskip 3pt{\color{ink3}\fontsize{7.4}{9.4}\selectfont %s\par}" % it(b["cap"])
               if b.get("cap") else "")
        if tikz:
            return ("\\begin{center}\n\\adjustbox{max width=\\linewidth,max totalheight=0.52\\textheight}{%\n"
                    f"{tikz}\n}}\n\\end{{center}}\n{cap}\n")
        # No TikZ authored for this figure: keep the caption so the frame still
        # says what the audience is meant to be looking at.
        return "\\begin{iband}[signal]\n%s\n\\end{iband}\n" % it(b.get("cap", ""))
    if t == "draw":
        _, pdf = figures.render_drawn(b["id"], b["svg"], b["print"])
        cap = (r"\vskip 3pt{\color{ink3}\fontsize{7.4}{9.4}\selectfont %s\par}" % it(b["cap"])
               if b.get("cap") else "")
        h = "0.74" if b.get("full") else "0.56"
        return ("\\begin{center}\n"
                f"\\includegraphics[width=0.97\\linewidth,"
                f"height={h}\\textheight,keepaspectratio]{{{pdf}}}\n"
                "\\end{center}\n" + cap + "\n")
    if t == "mmd":
        _, pdf = figures.render(b["id"], b["src"])
        cap = (r"\vskip 3pt{\color{ink3}\fontsize{7.4}{9.4}\selectfont %s\par}" % it(b["cap"])
               if b.get("cap") else "")
        h = "0.74" if b.get("full") else "0.60"
        return ("\\begin{center}\n"
                "\\includegraphics[width=0.92\\linewidth,height=%s\\textheight,"
                "keepaspectratio]{%s}\n\\end{center}\n%s\n" % (h, pdf, cap))
    if t == "img":
        # Book figures are derived from a PDF that is not in the repository, so
        # a fresh clone may not have them yet. Degrade to the caption rather
        # than failing the whole build.
        if not os.path.exists(os.path.join(_ROOT, b["src"])):
            return ("\\begin{iband}[amber]\n%s\n\\end{iband}\n"
                    % (it(b.get("cap", "")) +
                       r"~\textit{(figure not extracted; run tools/bookfigs.py)}"))
        cap = it(b.get("cap", ""))
        if b.get("credit"):
            cap += (r"~\textcolor{ink3}{\footnotesize---~Chollet \& Watson, "
                    r"\emph{Deep Learning with Python}, 3rd ed. (Manning)}")
        cap = (r"\vskip 3pt{\color{ink3}\fontsize{7.4}{9.4}\selectfont %s\par}" % cap
               if b.get("cap") else "")
        return ("\\begin{center}\n"
                "\\includegraphics[width=0.92\\linewidth,height=0.60\\textheight,"
                "keepaspectratio]{%s}\n\\end{center}\n%s\n" % (b["src"], cap))
    if t == "links":
        return _links(b)
    if t == "cols":
        fr = RATIO_FRAC.get(b.get("ratio", "1-1"), RATIO_FRAC["1-1"])
        bodies = ["".join(render_block(x, depth + 1) for x in col) for col in b["cols"]]
        return _minipages(fr, bodies)
    raise ValueError(f"unknown block {t!r}")


# ----------------------------------------------------------------- frames ----

PREAMBLE = r"""%% GENERATED by tools/gen_latex.py -- edit content/{id}.py instead.
%% Build:  latexmk -pdf {id}.tex     (or: pdflatex {id}.tex, twice)
\documentclass[aspectratio=169,11pt,t]{{beamer}}
\usepackage{{itbpro}}

\coursetitle{{{title}}}
\coursesubtitle{{{subtitle}}}
\coursekicker{{{kicker}}}
\coursesource{{{source}}}
\courseduration{{{duration}}}
\coursepresenter{{{pname}}}{{{prole}}}
\coursebrand{{{brand}}}
{partner}
\title{{{title}}}
\author{{{pname}}}
\date{{}}

\begin{{document}}
"""


def _frame(s):
    """One content frame.

    ``shrink`` rather than ``allowframebreaks``: these decks are dense, and a
    slide that spills should be scaled down to fit rather than silently split
    across two pages where the audience only ever sees the first half.
    """
    kicker = (r"\framekicker{%s}" % esc_tex(s["kicker"])) if s.get("kicker") else ""
    blocks = s.get("blocks", [])
    body = "".join(render_block(b) for b in blocks)
    note = ""
    if s.get("notes"):
        note = "\n\\note{%s}" % it(s["notes"])
    flags = list(s.get("opts", "").split(",")) if s.get("opts") else []
    # Every content frame may shrink to fit. (The "Dimension too large" failures
    # this once seemed to cause were really the footline progress bar dividing
    # by the frame count; see itbpro.sty.)
    flags.append("shrink=25")
    flags = [f for f in flags if f]
    # An empty option list -- `\begin{frame}[]` -- makes beamer fail while
    # scanning the frame's arguments, so omit the brackets entirely.
    opts = ("[" + ",".join(flags) + "]") if flags else ""
    return (f"{kicker}\n\\begin{{frame}}{opts}{{{it(s['title'])}}}\n{body}"
            f"\\end{{frame}}{note}\n\n")


def build(deck, listings_dir=None):
    d = deck
    _SIDECAR["dir"] = listings_dir
    _SIDECAR["deck"] = d["id"]
    _SIDECAR["n"] = 0
    _SIDECAR["written"] = []
    if listings_dir:
        os.makedirs(listings_dir, exist_ok=True)
    kicker = d.get("kicker") or (f"Chapter {d['number']}" if d.get("number") else "Module")
    brand = d.get("brand") or (
        "AI for Professional \\textperiodcentered\\ ITB"
        + (f" \\textperiodcentered\\ Ch {d['number']}" if d.get("number") else ""))

    out = [PREAMBLE.format(
        id=d["id"],
        title=it(d["title"]),
        subtitle=it(d.get("subtitle", "")),
        kicker=esc_tex(kicker),
        source=it(d.get("source", "")),
        duration=esc_tex(d.get("duration", "")),
        partner="",  # the cover carries no partner line -- see itbpro.sty
        pname=esc_tex(presenter_names(d)),
        prole=esc_tex(presenter_roles(d)),
        brand=brand,
    )]

    out.append("\\covertitle\n\n")

    # Objectives + resources, once, right after the cover.
    if d.get("objectives"):
        items = "\n".join(r"\item %s" % it(o) for o in d["objectives"])
        res = ""
        if d.get("resources"):
            res = "\n\\vskip 6pt\n" + _links({"items": [
                {"k": RES_LABEL.get(r["kind"], r["kind"]), "v": r["label"],
                 "href": r["href"], "pending": r.get("pending", False)}
                for r in d["resources"]]})
        out.append(
            "\\framekicker{Learning outcomes}\n"
            "\\begin{frame}[shrink=25]{Session Objectives}\n"
            "\\leadpar{By the end of this session, participants can:}\n"
            f"\\begin{{isteps}}\n{items}\n\\end{{isteps}}\n{res}"
            "\\end{frame}\n\n")

    for s in d["slides"]:
        if s["type"] == "title":
            continue                      # the cover is emitted above
        if s["type"] == "section":
            out.append("\\coursesection{%s}{%s}{%s}\n\n" % (
                esc_tex(s.get("num", "")), it(s["title"]), it(s.get("lead", ""))))
        else:
            out.append(_frame(s))

    out.append("\\end{document}\n")
    return "".join(out)


def write(deck, outdir):
    os.makedirs(outdir, exist_ok=True)
    listings_dir = os.path.join(outdir, "listings")
    # Drop this deck's stale sidecars first, so a removed code block does not
    # leave an orphan file behind that later looks like live sample code.
    if os.path.isdir(listings_dir):
        for f in os.listdir(listings_dir):
            if f.startswith(deck["id"] + "-"):
                os.remove(os.path.join(listings_dir, f))
    body = build(deck, listings_dir)
    path = os.path.join(outdir, deck["id"] + ".tex")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    return path
