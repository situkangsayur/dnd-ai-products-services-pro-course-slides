"""Render a DECK dict to a web deck: decks/<id>/{index.html,slides.js}.

Run through tools/build.py rather than directly.
"""

import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import figures
from course import presenter_names
from inline import html as ih, esc_html

RATIO_CLS = {"1-1": "g2", "2-1": "g21", "1-2": "g12", "3-2": "g32"}


# ----------------------------------------------------------------- blocks ----

def _cards(b):
    cols = b.get("cols") or min(len(b.get("items", [])) or 1, 3)
    out = [f'<div class="grid g{cols}">']
    for c in b.get("items", []):
        style = c.get("style", "")
        cls = "card" + (" " + style if style else "")
        out.append(f'<div class="{cls}">')
        if c.get("ico"):
            out.append(f'<span class="ico">{esc_html(c["ico"])}</span>')
        if c.get("h"):
            out.append(f'<h3>{ih(c["h"])}</h3>')
        if c.get("p"):
            out.append(f'<p>{ih(c["p"])}</p>')
        if c.get("tag"):
            tstyle = c.get("tagstyle", "")
            out.append(f'<span class="tag {tstyle}">{esc_html(c["tag"])}</span>')
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def _stats(b):
    items = b.get("items", [])
    cols = b.get("cols") or min(len(items) or 1, 4)
    out = [f'<div class="grid g{cols}">']
    for s in items:
        out.append('<div class="stat">'
                   f'<div class="v">{ih(s.get("v", ""))}</div>'
                   f'<div class="l">{ih(s.get("l", ""))}</div></div>')
    out.append("</div>")
    return "".join(out)


def _code(b):
    head = ""
    if b.get("file") or b.get("lang"):
        head = ('<div class="code-head">'
                f'<span class="code-file">{esc_html(b.get("file", ""))}</span>'
                f'<span class="code-lang">{esc_html(b.get("lang", "python"))}</span>'
                "</div>")
    src = esc_html(b.get("src", "").strip("\n"))
    nohl = " data-nohl" if b.get("lang") not in (None, "python", "py") else ""
    return f'<div class="code">{head}<pre{nohl}>{src}</pre></div>'


def _table(b):
    out = ['<div class="tbl-wrap"><table class="tbl"><thead><tr>']
    for h in b.get("head", []):
        out.append(f"<th>{ih(h)}</th>")
    out.append("</tr></thead><tbody>")
    for row in b.get("rows", []):
        out.append("<tr>" + "".join(f"<td>{ih(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _links(b):
    out = ['<div class="links">']
    for l in b.get("items", []):
        pending = l.get("pending")
        cls = "lnk pending" if pending else "lnk"
        href = "#" if pending else l.get("href", "#")
        tgt = "" if pending else ' target="_blank" rel="noopener"'
        ic = l.get("ic", "🔗")
        out.append(f'<a class="{cls}" href="{href}"{tgt}>'
                   f'<span class="ic">{esc_html(ic)}</span>'
                   f'<span><span class="k">{esc_html(l.get("k", ""))}</span>'
                   f'<span class="v">{esc_html(l.get("v", ""))}</span></span></a>')
    out.append("</div>")
    return "".join(out)


def render_block(b):
    t = b["t"]
    if t == "p":
        return f"<p>{ih(b['md'])}</p>"
    if t == "lead":
        return f'<p class="sub">{ih(b["md"])}</p>'
    if t == "bullets":
        return "<ul>" + "".join(f"<li>{ih(i)}</li>" for i in b["items"]) + "</ul>"
    if t == "steps":
        return "<ol>" + "".join(f"<li>{ih(i)}</li>" for i in b["items"]) + "</ol>"
    if t == "cards":
        return _cards(b)
    if t == "stats":
        return _stats(b)
    if t == "code":
        return _code(b)
    if t == "out":
        return f'<div class="out">{esc_html(b["src"].strip(chr(10)))}</div>'
    if t == "table":
        return _table(b)
    if t == "quote":
        cite = f'<cite>{ih(b["cite"])}</cite>' if b.get("cite") else ""
        return f'<div class="quote"><p>{ih(b["md"])}</p>{cite}</div>'
    if t == "band":
        style = b.get("style", "")
        return f'<div class="band {style}"><p>{ih(b["md"])}</p></div>'
    if t == "fig":
        svg = b.get("svg", "")
        cap = f'<figcaption>{ih(b["cap"])}</figcaption>' if b.get("cap") else ""
        if not svg:
            return f'<div class="band"><p>{ih(b.get("cap", ""))}</p></div>'
        return f'<figure class="fig">{svg}{cap}</figure>'
    if t == "draw":
        markup, _ = figures.render_drawn(b["id"], b["svg"], b["print"])
        cap = f'<figcaption>{ih(b["cap"])}</figcaption>' if b.get("cap") else ""
        # A figure marked `full` owns the slide. Shrinking a tall diagram to
        # share a slide is how a diagram becomes unreadable, and the deck has
        # no page budget -- if it needs the room, give it the room.
        klass = "fig fig-draw" + (" fig-full" if b.get("full") else "")
        return f'<figure class="{klass}">{b["svg"]}{cap}</figure>'
    if t == "mmd":
        markup, _ = figures.render(b["id"], b["src"])
        cap = f'<figcaption>{ih(b["cap"])}</figcaption>' if b.get("cap") else ""
        return f'<figure class="fig fig-mmd">{markup}{cap}</figure>'
    if t == "img":
        if not os.path.exists(os.path.join(_ROOT, b["src"])):
            return ('<div class="band amber"><p>%s <i>(figure not extracted; run '
                    'tools/bookfigs.py)</i></p></div>' % ih(b.get("cap", "")))
        cap = ih(b.get("cap", ""))
        if b.get("credit"):
            cap += ('<span class="credit">Chollet &amp; Watson, '
                    '<i>Deep Learning with Python</i>, 3rd ed. (Manning)</span>')
        cap = f"<figcaption>{cap}</figcaption>" if cap else ""
        style = f' style="max-height:{b["max_h"]}"' if b.get("max_h") else ""
        return (f'<figure class="fig fig-img">'
                f'<img src="../{esc_html(b["src"])}" alt="{esc_html(b.get("cap", ""))}"{style}>'
                f'{cap}</figure>')
    if t == "links":
        return _links(b)
    if t == "cols":
        cls = RATIO_CLS.get(b.get("ratio", "1-1"), "g2")
        inner = "".join("<div>" + "".join(render_block(x) for x in col) + "</div>"
                        for col in b["cols"])
        return f'<div class="grid {cls}">{inner}</div>'
    raise ValueError(f"unknown block {t!r}")


# ----------------------------------------------------------------- slides ----

def _title_slide(deck):
    d = deck
    who = presenter_names(d)
    meta = []
    if d.get("duration"):
        meta.append(f'<span class="chip"><b>Duration</b> {esc_html(d["duration"])}</span>')
    if who:
        label = "Instructors" if " \u00b7 " in who else "Instructor"
        meta.append(f'<span class="chip"><b>{label}</b> {esc_html(who)}</span>')
    if d.get("source"):
        meta.append(f'<span class="chip"><b>Source</b> {esc_html(d["source"])}</span>')

    kicker = d.get("kicker") or (
        f"Chapter {d['number']}" if d.get("number") else "Module")
    res = ""
    if d.get("resources"):
        res = _links({"items": [
            {"k": r["kind"].upper(), "v": r["label"], "href": r["href"],
             "ic": {"notebook": "📓", "github": "⌥", "book": "📘", "paper": "📄",
                    "tool": "🛠", "dataset": "🗃", "site": "🌐"}.get(r["kind"], "🔗"),
             "pending": r.get("pending", False)}
            for r in d["resources"]]})

    return {
        "title": "Cover",
        "cls": "s-title",
        "html": (
            '<div class="cobrand">'
            '<img src="../_engine/assets/itb-logo.png" alt="ITB">'
            '<div class="co-txt"><b>Institut Teknologi Bandung</b><br>'
            'Directorate of Continuing Professional Education'
            # The cohort partner is named only on decks that declare one. The
            # book chapters are reused across cohorts and institutions, so they
            # deliberately carry no partner branding.
            + (f'<br><span style="opacity:.7">in partnership with {esc_html(d["partner"])}</span>'
               if d.get("partner") else "")
            + "</div>"
            "</div>"
            f'<div class="kicker">{esc_html(kicker)}</div>'
            f'<h1>{ih(d["title"])}</h1>'
            f'<p class="sub">{ih(d.get("subtitle", ""))}</p>'
            f'<div class="meta">{"".join(meta)}</div>'
            + res
        ),
    }


def _section_slide(s):
    lead = f'<p class="sub">{ih(s["lead"])}</p>' if s.get("lead") else ""
    return {
        "title": s["title"],
        "cls": "s-section",
        "html": (f'<div class="secnum">{esc_html(s.get("num", ""))}</div>'
                 f'<h1>{ih(s["title"])}</h1>{lead}'),
        "notes": s.get("notes", ""),
    }


def _content_slide(s):
    parts = []
    if s.get("kicker"):
        parts.append(f'<div class="kicker">{esc_html(s["kicker"])}</div>')
    parts.append(f'<h2>{ih(s["title"])}</h2>')
    for b in s.get("blocks", []):
        parts.append(render_block(b))
    return {
        "title": s["title"],
        "cls": s.get("cls", ""),
        "html": "".join(parts),
        "notes": s.get("notes", ""),
    }


def build_slides(deck):
    out = []
    for s in deck["slides"]:
        if s["type"] == "title":
            out.append(_title_slide(deck))
        elif s["type"] == "section":
            out.append(_section_slide(s))
        else:
            out.append(_content_slide(s))
    return out


# ------------------------------------------------------------------ files ----

INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · AI for Professional · ITB</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/png" href="../_engine/assets/itb-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../_engine/css/deck.css">
</head>
<body>

<header id="toolbar">
  <div class="tb-left">
    <img src="../_engine/assets/itb-logo.png" alt="ITB" class="tb-logo">
    <span class="tb-sep"></span>
    <span class="tb-event">{brand}</span>
  </div>
  <div class="tb-right">
    <a class="tb-btn home" href="../index.html" title="Back to the course index">⌂ Course</a>
    <button id="present-btn" class="tb-btn" title="Full screen on this display (F5) — the clicker works here">▶ Present</button>
    <button id="presenter-btn" class="tb-btn" title="Presenter view — opens a second window for the projector">⧉ Presenter</button>
    <button id="pdf-btn" class="tb-btn" title="Print / save as PDF (P)">⬇ PDF</button>
    <button id="overview-btn" class="tb-btn" title="Slide overview (O)">▦</button>
  </div>
</header>

<div id="progress"><div id="progress-fill"></div></div>

<main id="deck" aria-live="polite"></main>

<div id="overview" class="hidden"><div id="overview-grid"></div></div>

<nav id="controls">
  <button id="prev" class="ctrl-btn" aria-label="Previous">‹</button>
  <span id="counter">1 / 1</span>
  <button id="next" class="ctrl-btn" aria-label="Next">›</button>
</nav>

<script src="slides.js"></script>
<script src="../_engine/js/deck.js"></script>
</body>
</html>
"""


def write(deck, outdir):
    slides = build_slides(deck)
    os.makedirs(outdir, exist_ok=True)

    brand = deck.get("brand") or (
        "AI for Professional · ITB"
        + (f" · Ch {deck['number']} — {deck['title']}" if deck.get("number")
           else f" · {deck['title']}"))

    meta = {
        "id": deck["id"],
        "title": deck["title"],
        "subtitle": deck.get("subtitle", ""),
        "brand": brand,
        "course": "Designing and Building AI Products and Services: AI for Professional",
    }

    js = ["/* GENERATED by tools/gen_web.py — edit content/%s.py instead. */" % deck["id"],
          "const DECK = " + json.dumps(meta, ensure_ascii=False, indent=2) + ";",
          "const SLIDES = " + json.dumps(slides, ensure_ascii=False, indent=2) + ";"]
    with open(os.path.join(outdir, "slides.js"), "w", encoding="utf-8") as f:
        f.write("\n".join(js) + "\n")

    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX.format(
            title=esc_html(deck["title"]),
            desc=esc_html(deck.get("subtitle", "")),
            brand=esc_html(brand)))

    return len(slides)
