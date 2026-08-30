#!/usr/bin/env python3
"""Render the notebooks to browsable HTML, plus an index.

    python3 tools/nb_html.py                 # notebooks/ -> notebooks-site/
    python3 tools/nb_html.py --out /tmp/nb   # somewhere else

**Why this exists.** A link to a ``.ipynb`` does not open a notebook, it
downloads a file — which is what happens today when somebody clicks a notebook
chip on a slide. Whatever a link on a slide points at has to *render* in the
browser the audience already has open.

**Why not nbconvert.** It is the obvious tool and it is not installed, and this
repository's rule is that a normal build shells out to nothing it does not
already need. The notebooks here carry no stored outputs by design, so the job
is markdown cells and code cells — a couple of hundred lines, no dependency,
and no version of nbconvert to keep working.

The output is self-contained: one stylesheet, inlined, in the deck's palette so
the notebooks and the slides look like one course.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB_DIR = os.path.join(ROOT, "notebooks")
OUT_DIR = os.path.join(ROOT, "notebooks-site")

sys.path.insert(0, os.path.join(ROOT, "tools"))


def E(s):
    return html.escape(str(s), quote=False)


# ------------------------------------------------------------------ markdown --

_INLINE = [
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{E(m.group(1))}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)"), lambda m: f"<em>{m.group(1)}</em>"),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"),
     lambda m: f'<a href="{E(m.group(2))}">{m.group(1)}</a>'),
]


def inline(text):
    """Inline markup, with code spans protected from the rest.

    Order matters and the usual bug is doing it in the wrong one: run bold
    before code and `**` inside a code span turns into markup. Code is pulled
    out first and put back last.
    """
    holds = []

    def hold(m):
        holds.append(f"<code>{E(m.group(1))}</code>")
        return f"\x00{len(holds) - 1}\x00"

    text = re.sub(r"`([^`]+)`", hold, text)
    text = E(text)
    for pattern, repl in _INLINE[1:]:
        text = pattern.sub(repl, text)
    return re.sub(r"\x00(\d+)\x00", lambda m: holds[int(m.group(1))], text)


def markdown(src):
    """Enough markdown for a teaching notebook, and no more."""
    out, lines = [], src.split("\n")
    i, in_list = 0, None
    while i < len(lines):
        ln = lines[i]

        if ln.startswith("```"):
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            out.append(f'<pre class="md-code">{E(chr(10).join(body))}</pre>')
            i += 1
            continue

        h = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if h:
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            lvl = len(h.group(1))
            out.append(f"<h{lvl}>{inline(h.group(2))}</h{lvl}>")
            i += 1
            continue

        li = re.match(r"^\s*([-*])\s+(.*)$", ln)
        ol = re.match(r"^\s*(\d+)\.\s+(.*)$", ln)
        if li or ol:
            want = "ul" if li else "ol"
            if in_list != want:
                if in_list:
                    out.append(f"</{in_list}>")
                out.append(f"<{want}>")
                in_list = want
            out.append(f"<li>{inline((li or ol).group(2))}</li>")
            i += 1
            continue

        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

        if not ln.strip():
            i += 1
            continue

        if ln.startswith("> "):
            out.append(f"<blockquote>{inline(ln[2:])}</blockquote>")
            i += 1
            continue

        para = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|\s*[-*]\s|\s*\d+\.\s|>\s|```)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    if in_list:
        out.append(f"</{in_list}>")
    return "\n".join(out)


# ---------------------------------------------------------------------- page --

CSS = """
:root{--bg:#123A6B;--bg2:#1B4E8C;--card:rgba(255,255,255,.07);
--line:rgba(180,216,255,.30);--ink:#F4F8FF;--ink2:#C9DAF2;--ink3:#93AACB;
--sig:#22D3EE;--lime:#7BD949;
--mono:'JetBrains Mono',ui-monospace,'SF Mono',Menlo,monospace;
--sans:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif}
*{box-sizing:border-box}
body{margin:0;background:linear-gradient(180deg,var(--bg),var(--bg2) 60%,var(--bg));
color:var(--ink);font:400 16px/1.68 var(--sans);min-height:100vh}
.wrap{max-width:920px;margin:0 auto;padding:38px 22px 90px}
header{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:26px}
.kick{font:600 11.5px var(--sans);letter-spacing:.16em;text-transform:uppercase;
color:var(--sig)}
h1{font:700 30px/1.2 var(--sans);margin:6px 0 4px;letter-spacing:-.02em}
h2{font:600 22px/1.3 var(--sans);margin:30px 0 10px}
h3{font:600 18px/1.35 var(--sans);margin:24px 0 8px}
p{color:var(--ink2)}
a{color:var(--sig)}
ul,ol{color:var(--ink2)}
blockquote{margin:14px 0;padding:10px 16px;border-left:3px solid var(--sig);
background:var(--card);border-radius:0 8px 8px 0;color:var(--ink2)}
code{font:400 .92em var(--mono);background:rgba(255,255,255,.10);
padding:1px 5px;border-radius:4px}
pre{font:400 13.5px/1.6 var(--mono);background:rgba(0,0,0,.30);
border:1px solid var(--line);border-radius:10px;padding:14px 16px;
overflow-x:auto;color:var(--ink)}
pre code{background:none;padding:0}
.cell{margin:16px 0}
.cell-in{position:relative}
.cell-in::before{content:"In";position:absolute;left:-40px;top:14px;
font:600 11px var(--mono);color:var(--ink3)}
.out{font:400 13px/1.55 var(--mono);white-space:pre-wrap;color:var(--lime);
background:rgba(0,0,0,.22);border-radius:8px;padding:10px 14px;margin-top:8px}
.nav{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}
.nav a{font-size:13.5px;text-decoration:none;border:1px solid var(--line);
padding:5px 12px;border-radius:999px;color:var(--ink2)}
.nav a:hover{color:var(--ink);background:var(--card)}
.ch{margin:28px 0 8px;padding-top:22px;border-top:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.nb{display:block;text-decoration:none;border:1px solid var(--line);
border-radius:12px;padding:14px 16px;background:var(--card)}
.nb:hover{border-color:var(--sig)}
.nb b{display:block;color:var(--ink);font:600 15px var(--sans);margin-bottom:3px}
.nb span{color:var(--ink3);font-size:12.5px}
footer{margin-top:50px;padding-top:16px;border-top:1px solid var(--line);
color:var(--ink3);font-size:13px}
@media(max-width:640px){.cell-in::before{display:none}.wrap{padding:24px 14px 60px}}
"""

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style>
</head><body><div class="wrap">
<header>
  <div class="kick">{kick}</div>
  <h1>{h1}</h1>
  {sub}
</header>
{nav}
{body}
<footer>{footer}</footer>
</div></body></html>
"""


def render_notebook(path, rel_home="../index.html"):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    cells = []
    title = os.path.basename(path)
    sub = ""
    for k, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            if k == 0:
                m = re.match(r"^#\s+(.*)$", src.split("\n")[0])
                if m:
                    title = m.group(1)
                    rest = "\n".join(src.split("\n")[1:]).strip()
                    if rest:
                        sub = f"<p>{inline(rest.split(chr(10))[0])}</p>"
                    continue
            cells.append(f'<div class="cell">{markdown(src)}</div>')
        else:
            outs = []
            for o in cell.get("outputs", []) or []:
                txt = "".join(o.get("text", []) or [])
                if txt:
                    outs.append(f'<div class="out">{E(txt)}</div>')
            cells.append(f'<div class="cell cell-in"><pre>{E(src)}</pre>'
                         + "".join(outs) + "</div>")

    return PAGE.format(
        title=E(title) + " · AI for Professional",
        css=CSS,
        kick="Notebook",
        h1=E(title),
        sub=sub,
        nav=f'<div class="nav"><a href="{rel_home}">&larr; All notebooks</a></div>',
        body="\n".join(cells),
        footer="AI for Professional · ITB · Directorate of Continuing "
               "Professional Education")


def build(out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    chapters = {}
    for ch in sorted(os.listdir(NB_DIR)):
        d = os.path.join(NB_DIR, ch)
        if not os.path.isdir(d):
            continue
        made = []
        os.makedirs(os.path.join(out_dir, ch), exist_ok=True)
        for name in sorted(os.listdir(d)):
            if not name.endswith(".ipynb"):
                continue
            html_name = name[:-6] + ".html"
            page = render_notebook(os.path.join(d, name))
            with open(os.path.join(out_dir, ch, html_name), "w",
                      encoding="utf-8") as f:
                f.write(page)
            made.append((html_name, name))
        if made:
            chapters[ch] = made

    # The index the slides link to. Each chapter carries an id so a deck can
    # point at `index.html#ch07` and land in the right place.
    body = []
    for ch, made in chapters.items():
        n = ch.replace("ch", "").lstrip("0") or "0"
        body.append(f'<h2 class="ch" id="{ch}">Chapter {n}</h2><div class="grid">')
        for html_name, orig in made:
            stem = orig[:-6].replace("_", " ")
            stem = re.sub(r"^(\d+)\s", r"\1 · ", stem)
            body.append(f'<a class="nb" href="{ch}/{html_name}">'
                        f'<b>{E(stem)}</b><span>{E(orig)}</span></a>')
        body.append("</div>")

    total = sum(len(v) for v in chapters.values())
    index = PAGE.format(
        title="Notebooks · AI for Professional",
        css=CSS,
        kick="AI for Professional · ITB",
        h1="Notebooks",
        sub=f"<p>{total} notebooks across {len(chapters)} chapters. Each one "
            f"runs top to bottom; none carries stored output, so what you see "
            f"is what you will write.</p>",
        nav="",
        body="\n".join(body),
        footer="Generated by tools/nb_html.py from notebooks/ — do not edit "
               "these pages by hand.")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    return total, len(chapters)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_DIR)
    a = ap.parse_args()
    n, c = build(a.out)
    print(f"{n} notebooks in {c} chapters -> {a.out}/")
    print(f"  index: {os.path.join(a.out, 'index.html')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
