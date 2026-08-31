"""The deck gallery at course-web-slides/index.html, plus decks.json.

Two outputs, from one pass over the built decks:

    course-web-slides/index.html   the gallery every deck's "Course" button
                                   links back to
    course-web-slides/decks.json   a manifest the separate course-web repo
                                   reads, so the two sites never disagree
                                   about what exists

A partial build (``build.py ch07``) merges into the manifest rather than
replacing it, so building one deck never makes the other twenty disappear from
the gallery.
"""

import json
import os

from inline import html as ih, esc_html
from course import COURSE, TEAM, BOOKS, DEFAULT_BOOK, presenter_names

MANIFEST = "decks.json"


def _entry(deck, n_slides):
    """One manifest record. Deliberately small -- the gallery and the course
    site both render from this, so anything not here is not shared."""
    return {
        "id": deck["id"],
        "kind": deck.get("kind", "chapter"),
        # Dek bab menyatakan buku asalnya; modul mandiri menyatakan pemiliknya.
        # Keduanya masuk manifes karena galeri DAN situs kursus merender dari
        # sini — apa pun yang tidak ada di sini tidak ikut terbagi.
        "book": deck.get("book", DEFAULT_BOOK if deck.get("number") is not None else None),
        "owner": deck.get("owner"),
        "number": deck.get("number"),
        "title": deck["title"],
        "subtitle": deck.get("subtitle", ""),
        "duration": deck.get("duration", ""),
        "presenter": deck.get("presenter", {}),
        "source": deck.get("source", ""),
        "source_url": deck.get("source_url", ""),
        "objectives": deck.get("objectives", []),
        "resources": deck.get("resources", []),
        "slides": n_slides,
        "sections": [s["title"] for s in deck["slides"] if s.get("type") == "section"],
    }


def load_manifest(outdir):
    path = os.path.join(outdir, MANIFEST)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {d["id"]: d for d in json.load(f)["decks"]}


# The standalone modules run in teaching order, not alphabetical order: the
# LLM module comes before the agentic one, because agentic AI is built on top
# of what the LLM module covers. Anything not listed falls in after these.
MODULE_ORDER = ["viny-llm", "hendri-agentic"]


def _sort_key(d):
    """Chapters in book order, then the modules in teaching order."""
    if d.get("number") is not None:
        return (0, d["number"], "")
    did = d["id"]
    rank = MODULE_ORDER.index(did) if did in MODULE_ORDER else len(MODULE_ORDER)
    return (1, rank, did)


def _card(d):
    num = d.get("number")
    label = f"Chapter {num}" if num is not None else "Module"
    who = presenter_names(d)
    secs = d.get("sections") or []
    sec_html = ""
    if secs:
        items = "".join(f"<li>{esc_html(s)}</li>" for s in secs)
        sec_html = f'<ul class="ix-secs">{items}</ul>'
    return f"""
<a class="ix-card{' module' if num is None else ''}" href="{d['id']}/index.html">
  <div class="ix-head">
    <span class="ix-num">{esc_html(label)}</span>
    <span class="ix-count">{d['slides']} slides</span>
  </div>
  <h3>{esc_html(d['title'])}</h3>
  <p class="ix-sub">{ih(d.get('subtitle', ''))}</p>
  {sec_html}
  <div class="ix-foot">
    <span class="ix-who">{esc_html(who)}</span>
    <span class="ix-dur">{esc_html(d.get('duration', ''))}</span>
  </div>
</a>"""


def _pdf_row(d):
    return (f'<a class="ix-pdf" href="pdf/{d["id"]}.pdf">'
            f'<span>{esc_html(d["title"])}</span><span>PDF</span></a>')


CSS = """
:root{
  --ink:#0b1020; --ink2:#1b2440; --ink3:#5a668a;
  --paper:#f6f7fb; --card:#ffffff; --rule:#e3e7f2;
  --itb:#00539f; --itb2:#0a7cc4; --signal:#ff7a1a; --lime:#12b886;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--paper); color:var(--ink);
  font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  -webkit-font-smoothing:antialiased;
}
a{color:inherit;text-decoration:none}
.ix-wrap{max-width:1180px;margin:0 auto;padding:0 26px 80px}
.ix-hero{
  background:linear-gradient(135deg,var(--ink) 0%,#132a52 55%,var(--itb) 100%);
  color:#fff; padding:54px 0 46px; margin-bottom:38px;
  border-bottom:3px solid var(--signal);
}
.ix-hero .ix-wrap{padding-bottom:0}
.ix-badge{
  display:inline-block; font-size:11px; letter-spacing:.16em; text-transform:uppercase;
  font-weight:700; color:#8fd0ff; margin-bottom:14px;
}
.ix-hero h1{
  font-family:Sora,Inter,sans-serif; font-weight:800; font-size:clamp(28px,4.4vw,52px);
  line-height:1.06; margin:0 0 10px; letter-spacing:-.02em;
}
.ix-hero h2{
  font-family:Sora,Inter,sans-serif; font-weight:500; font-size:clamp(15px,2vw,21px);
  color:#b9d4ee; margin:0 0 22px;
}
.ix-meta{display:flex;flex-wrap:wrap;gap:10px 26px;font-size:13px;color:#c9dcf0}
.ix-meta b{color:#fff;font-weight:600}
h2.ix-h{
  font-family:Sora,Inter,sans-serif; font-size:13px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--ink3); font-weight:700;
  margin:44px 0 16px; padding-bottom:9px; border-bottom:1px solid var(--rule);
}
.ix-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px}
.ix-card{
  background:var(--card); border:1px solid var(--rule); border-radius:13px;
  padding:19px 20px 15px; display:flex; flex-direction:column;
  transition:transform .13s ease, box-shadow .13s ease, border-color .13s ease;
}
.ix-card:hover{
  transform:translateY(-2px); border-color:#c3d6ee;
  box-shadow:0 10px 26px rgba(11,16,32,.09);
}
.ix-card.module{border-left:3px solid var(--signal)}
.ix-h .ix-sub{font-weight:400;font-size:.62em;color:var(--muted);letter-spacing:0}
.ix-owner{margin:14px 0 8px;font-size:.82rem;font-weight:600;color:var(--signal);
          letter-spacing:.04em;text-transform:uppercase}
.ix-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px}
.ix-num{
  font-size:10.5px; font-weight:800; letter-spacing:.13em; text-transform:uppercase;
  color:var(--itb);
}
.ix-card.module .ix-num{color:var(--signal)}
.ix-count{font-size:10.5px;color:var(--ink3);font-variant-numeric:tabular-nums}
.ix-card h3{
  font-family:Sora,Inter,sans-serif; font-size:17px; font-weight:700;
  line-height:1.25; margin:0 0 7px; letter-spacing:-.01em;
}
.ix-sub{font-size:12.8px;line-height:1.5;color:var(--ink3);margin:0 0 11px}
.ix-secs{margin:0 0 12px;padding:0 0 0 15px;font-size:11.6px;color:var(--ink3);line-height:1.65}
.ix-secs li{margin:0}
.ix-foot{
  margin-top:auto; padding-top:11px; border-top:1px solid var(--rule);
  display:flex; justify-content:space-between; gap:10px;
  font-size:11px; color:var(--ink3);
}
.ix-who{font-weight:600;color:var(--ink2)}
.ix-pdfs{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:8px}
.ix-pdf{
  display:flex; justify-content:space-between; gap:12px; align-items:center;
  background:var(--card); border:1px solid var(--rule); border-radius:8px;
  padding:9px 13px; font-size:12.5px;
}
.ix-pdf:hover{border-color:var(--itb2);color:var(--itb)}
.ix-pdf span:last-child{
  font-size:10px; font-weight:800; letter-spacing:.1em; color:var(--signal);
}
.ix-note{
  font-size:12.5px; line-height:1.65; color:var(--ink3);
  background:var(--card); border:1px solid var(--rule); border-left:3px solid var(--itb2);
  border-radius:8px; padding:14px 17px; margin-top:16px;
}
footer.ix-foot-bar{
  margin-top:52px; padding-top:20px; border-top:1px solid var(--rule);
  font-size:11.5px; color:var(--ink3); display:flex; flex-wrap:wrap;
  gap:8px 22px; justify-content:space-between;
}
@media (max-width:760px){
  .ix-wrap{padding:0 18px 56px}
  .ix-hero{padding:34px 0 30px}
  .ix-grid{grid-template-columns:1fr}
  .ix-pdfs{grid-template-columns:1fr}
  .ix-meta{gap:8px 16px;font-size:12px}
  footer.ix-foot-bar{flex-direction:column;gap:8px}
}
"""


def write(decks, outdir):
    """``decks`` is a list of (deck dict, slide count). Returns the deck count
    written to the manifest, which may exceed len(decks) after a partial build."""
    os.makedirs(outdir, exist_ok=True)

    merged = load_manifest(outdir)
    for deck, n in decks:
        merged[deck["id"]] = _entry(deck, n)
    ordered = sorted(merged.values(), key=_sort_key)

    with open(os.path.join(outdir, MANIFEST), "w", encoding="utf-8") as f:
        # `books` ikut dikirim: repo course-web menampilkan label buku di
        # tabel silabus, dan menuliskan judul buku di dua repo adalah cara
        # paling cepat membuat keduanya berbeda.
        json.dump({"course": COURSE, "team": TEAM, "books": BOOKS,
                   "decks": ordered},
                  f, indent=2, ensure_ascii=False)

    chapters = [d for d in ordered if d.get("number") is not None]
    modules = [d for d in ordered if d.get("number") is None]
    total = sum(d["slides"] for d in ordered)

    # Dikelompokkan PER BUKU, bukan satu judul "Book chapters".
    #
    # Dengan satu buku keduanya terlihat sama, dan itulah yang membuat versi
    # lama bertahan lama. Begitu buku kedua masuk, satu judul tunggal akan
    # menumpuk bab dari dua buku berbeda dalam satu kisi, tanpa apa pun di
    # layar yang menunjukkan bab 5 yang mana milik buku yang mana.
    by_book = {}
    for d in chapters:
        by_book.setdefault(d.get("book") or DEFAULT_BOOK, []).append(d)

    book_html = ""
    for key, ds in by_book.items():
        b = BOOKS.get(key, {})
        judul = b.get("title", key)
        sub = " · ".join(x for x in (b.get("edition"), b.get("authors")) if x)
        book_html += (
            f'<h2 class="ix-h">{esc_html(judul)}'
            f'{f" <span class=\'ix-sub\'>{esc_html(sub)}</span>" if sub else ""}</h2>'
            f'<div class="ix-grid">{"".join(_card(d) for d in ds)}</div>')

    # Modul non-buku dikelompokkan per pemilik: yang membedakannya dari bab
    # bukan sekadar "berdiri sendiri", melainkan bahwa ISINYA ditulis sendiri.
    mod_html = ""
    if modules:
        by_owner = {}
        for d in modules:
            by_owner.setdefault(d.get("owner") or "", []).append(d)
        mod_html = '<h2 class="ix-h">Bukan dari buku <span class="ix-sub">materi tulisan sendiri</span></h2>'
        for owner, ds in by_owner.items():
            label = f'<div class="ix-owner">{esc_html(owner)}</div>' if owner else ""
            mod_html += label + f'<div class="ix-grid">{"".join(_card(d) for d in ds)}</div>' 

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Slide decks · {esc_html(COURSE['title'])} · ITB</title>
<meta name="description" content="Every slide deck for {esc_html(COURSE['title'])} -- {esc_html(COURSE['tagline'])}.">
<link rel="icon" type="image/png" href="_engine/assets/itb-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<header class="ix-hero">
  <div class="ix-wrap">
    <div class="ix-badge">{esc_html(COURSE['org'])} · {esc_html(COURSE['unit'])}</div>
    <h1>{esc_html(COURSE['title'])}</h1>
    <h2>{esc_html(COURSE['tagline'])} — by {esc_html(COURSE['by'])}</h2>
    <div class="ix-meta">
      <span><b>{len(ordered)}</b> decks</span>
      <span><b>{total}</b> slides</span>
      <span><b>{len(chapters)}</b> book chapters{f" · {len(by_book)} books" if len(by_book) > 1 else ""}</span>
      <span>{esc_html(COURSE['credits'])}</span>
    </div>
  </div>
</header>

<div class="ix-wrap">

  {book_html}

  {mod_html}

  <h2 class="ix-h">Download as PDF</h2>
  <div class="ix-pdfs">{"".join(_pdf_row(d) for d in ordered)}</div>
  <p class="ix-note">
    The PDFs are built from the same source as the web decks, so the two can
    never drift apart. Each is produced by LaTeX and is the version to use when
    projecting from a machine without a browser, or when a printed handout is
    needed.
  </p>

  <footer class="ix-foot-bar">
    <span>{esc_html(COURSE['org'])} · {esc_html(COURSE['unit'])}</span>
    <span>{esc_html(COURSE['credits'])}</span>
  </footer>

</div>
</body>
</html>
"""
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return len(ordered)
