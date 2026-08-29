"""Lift a figure straight out of the book PDF.

The book's own diagrams are better than anything worth redrawing by hand, so
where one exists we use it. They are vector art rather than embedded rasters,
which means ``pdfimages`` only yields fragments; the figure has to be cropped
out of a rendered page instead.

How a figure is located, given only "Figure 8.4":

  1. find the page whose text layer contains that caption
  2. read every word box on the page (``pdftotext -bbox-layout``)
  3. the caption's own box is the bottom of the crop
  4. walking up from the caption, the tallest vertical gap between text lines is
     the whitespace above the artwork -- that is the top of the crop
  5. render the page at high DPI and cut that band out, trimming white margins

Usage:

    python3 tools/bookfigs.py --pdf /path/to/book.pdf --list 8
    python3 tools/bookfigs.py --pdf /path/to/book.pdf 8.4 8.12 5.1
    python3 tools/bookfigs.py --pdf /path/to/book.pdf --all-in 5

Output lands in ``figs/book/figure-<n>-<m>.png``. Every figure carries the
book's attribution wherever it is shown; see ``BOOK_CREDIT``.
"""

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "figs", "book")

BOOK_CREDIT = ("Chollet & Watson, Deep Learning with Python, 3rd ed. "
               "(Manning) — reproduced for classroom use")

DPI = 220
_NS = {"x": "http://www.w3.org/1999/xhtml"}


def _page_words(pdf, page):
    """[(x0, y0, x1, y1, text)] in PDF points for one page."""
    r = subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", str(page), "-l", str(page), pdf, "-"],
        capture_output=True, text=True, check=True)
    root = ET.fromstring(r.stdout)
    words = []
    for w in root.iter():
        if not w.tag.endswith("word"):
            continue
        try:
            words.append((float(w.attrib["xMin"]), float(w.attrib["yMin"]),
                          float(w.attrib["xMax"]), float(w.attrib["yMax"]),
                          (w.text or "").strip()))
        except KeyError:
            continue
    pg = next(e for e in root.iter() if e.tag.endswith("page"))
    return words, float(pg.attrib["width"]), float(pg.attrib["height"])


def find_page(pdf, num):
    """PDF page number holding the caption 'Figure <num>'."""
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    pat = re.compile(rf"Figure\s+{re.escape(num)}(?![\d.])")
    for i, page in enumerate(txt.split("\f"), start=1):
        if pat.search(page):
            return i
    return None


def _caption_box(words, num):
    """Bounding box of the caption line 'Figure <num> ...'."""
    for i, (x0, y0, x1, y1, t) in enumerate(words):
        if t != "Figure":
            continue
        nxt = words[i + 1][4] if i + 1 < len(words) else ""
        if not nxt.startswith(num):
            continue
        # Extend across the caption's own line -- but only rightward from the
        # word "Figure". A side-column caption shares its baseline with body
        # text in the column to its left, and swallowing that text puts the
        # figure's left edge back at the page margin.
        line = [w for w in words if abs(w[1] - y0) < 4.0 and w[0] >= x0 - 2.0]
        return (min(w[0] for w in line), min(w[1] for w in line),
                max(w[2] for w in line), max(w[3] for w in line))
    return None


def _figure_band(words, cap):
    """(top, bottom) in points for the artwork above the caption.

    Only words in the caption's own column count. A full-width section heading
    sitting above a side-column figure would otherwise close the gap and drag
    the heading (and its neighbouring body text) into the crop.
    """
    cx0, cy0, cx1, cy1 = cap
    def same_column(w):
        return not (w[2] < cx0 - 6.0 or w[0] > cx1 + 6.0)
    words = [w for w in words if same_column(w)] or words
    above = sorted({round(w[3], 1) for w in words if w[3] <= cy0 - 1.0})
    if not above:
        return 40.0, cy1
    # widest vertical gap between consecutive text baselines above the caption
    best_gap, best_top = 0.0, above[0]
    for a, b in zip(above, above[1:]):
        gap = b - a
        if gap > best_gap:
            best_gap, best_top = gap, a
    if best_gap < 12.0:          # no clear band; fall back to a generous slab
        best_top = max(40.0, cy0 - 320.0)
    # Stop just above the printed caption: the slide supplies its own caption,
    # and including the book's leaves a half-clipped second line in the image.
    return best_top + 2.0, cy0 - 3.0


def _figure_band_below(words, cap, page_h):
    """(top, bottom) for artwork sitting *below* its caption."""
    cx0, cy0, cx1, cy1 = cap
    def same_column(w):
        return not (w[2] < cx0 - 6.0 or w[0] > cx1 + 6.0)
    col = [w for w in words if same_column(w)] or words
    below = sorted({round(w[1], 1) for w in col if w[1] >= cy1 + 1.0})
    if not below:
        return cy1 + 3.0, page_h - 40.0
    best_gap, best_bottom = 0.0, below[-1]
    for a, b in zip(below, below[1:]):
        if b - a > best_gap:
            best_gap, best_bottom = b - a, b
    if best_gap < 12.0:
        best_bottom = min(page_h - 40.0, cy1 + 320.0)
    return cy1 + 3.0, best_bottom - 2.0


def _caption_column(band, cap_x0, cap_x1):
    """Narrow a full-width band to the column of ink containing the caption.

    Columns are found by looking for gutters -- runs of near-blank pixel
    columns -- and keeping the ink region that overlaps the caption's own
    horizontal extent.
    """
    from PIL import Image
    g = band.convert("L")
    w, h = g.size
    if h == 0 or w == 0:
        return band
    px = g.load()
    step = max(1, h // 240)                      # sample rows; full scan is wasteful
    ink = []
    for x in range(w):
        dark = 0
        for y in range(0, h, step):
            if px[x, y] < 235:
                dark += 1
                if dark > 1:
                    break
        ink.append(dark > 1)

    gutter = max(12, w // 60)                    # a gap this wide separates columns
    runs, start = [], None
    blank = 0
    for x in range(w):
        if ink[x]:
            if start is None:
                start = x
            blank = 0
        else:
            if start is not None:
                blank += 1
                if blank >= gutter:
                    runs.append((start, x - blank))
                    start, blank = None, 0
    if start is not None:
        runs.append((start, w - 1))
    if not runs:
        return band

    # the run overlapping the caption wins; ties go to the widest
    best = max(runs, key=lambda r: (min(r[1], cap_x1) - max(r[0], cap_x0), r[1] - r[0]))
    x0, x1 = best
    if x1 - x0 < w * 0.12:                       # implausibly narrow -- keep the band
        return band
    return band.crop((max(0, x0 - 6), 0, min(w, x1 + 6), h))


def _score(img, words_px, offset):
    """How much of this crop is artwork rather than body text or blank paper.

    Returns (score, ink_ratio). Ink covered by a word box counts against the
    crop, so a band that caught a paragraph scores below one holding a diagram.
    """
    g = img.convert("L")
    w, h = g.size
    if w < 40 or h < 40:
        return -1.0, 0.0
    px = g.load()
    sx = max(1, w // 200)
    sy = max(1, h // 200)
    ink = 0
    text_ink = 0
    n = 0
    ox, oy = offset
    for y in range(0, h, sy):
        for x in range(0, w, sx):
            n += 1
            if px[x, y] < 235:
                ink += 1
                gx, gy = x + ox, y + oy
                for (wx0, wy0, wx1, wy1) in words_px:
                    if wx0 <= gx <= wx1 and wy0 <= gy <= wy1:
                        text_ink += 1
                        break
    if not n:
        return -1.0, 0.0
    ratio = ink / n
    if ratio < 0.004:                      # effectively a blank sheet
        return -1.0, ratio
    graphic = (ink - text_ink) / n
    return graphic, ratio


def _trim(img, pad=10):
    """Trim uniform white margin, then re-pad a little."""
    from PIL import Image, ImageChops
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img.convert("RGB"), bg.convert("RGB"))
    box = diff.getbbox()
    if not box:
        return img
    x0, y0, x1, y1 = box
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(img.width, x1 + pad), min(img.height, y1 + pad)
    return img.crop((x0, y0, x1, y1))


OVERRIDES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "bookfig_overrides.json")


def _override(num):
    """Hand-recorded page + crop box for figures the heuristic gets wrong.

    Box is [x0, y0, x1, y1] in PDF points, origin top-left. Recording them in a
    file (rather than fixing them by hand each time) keeps extraction
    reproducible for anyone who re-runs the build.
    """
    try:
        import json as _json
        with open(OVERRIDES, encoding="utf-8") as f:
            return _json.load(f).get(num)
    except (OSError, ValueError):
        return None


def extract(pdf, num, out_dir=OUT, dpi=DPI, page=None, full_page=False):
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    page = page or find_page(pdf, num)
    if not page:
        raise SystemExit(f"figure {num}: caption not found in {pdf}")

    ov = _override(num)
    if ov and not full_page:
        page = ov.get("page", page)

    words, pw, ph = _page_words(pdf, page)
    cap = _caption_box(words, num)
    if cap is None:
        raise SystemExit(f"figure {num}: caption box not found on page {page}")

    tmp = os.path.join(out_dir, f".page{page}")
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi),
                    "-f", str(page), "-l", str(page), pdf, tmp], check=True)
    rendered = next(p for p in sorted(os.listdir(out_dir))
                    if p.startswith(f".page{page}") and p.endswith(".png"))
    rendered = os.path.join(out_dir, rendered)

    img = Image.open(rendered)
    scale = img.height / ph
    words_px = [(w[0] * scale, w[1] * scale, w[2] * scale, w[3] * scale)
                for w in words]
    if full_page:
        crop = img
    elif ov and "box" in ov:
        x0, y0, x1, y1 = ov["box"]
        crop = img.crop((int(x0 * scale), int(y0 * scale),
                         int(x1 * scale), int(y1 * scale)))
    else:
        top, bottom = _figure_band(words, cap)
        # Captions are left-aligned with their artwork, so the caption's left
        # edge is the figure column's left edge. That alone separates a
        # side-column figure from the body text beside it, and costs nothing on
        # a full-width figure (whose caption starts at the left margin anyway).
        left = max(0, int(cap[0] * scale) - 10)

        # Most figures sit above their caption, but not all -- and the gap
        # heuristic occasionally lands in whitespace. Build both candidates and
        # keep whichever actually contains artwork.
        cands = []
        for t_pt, b_pt in ((top, bottom), _figure_band_below(words, cap, ph)):
            if b_pt - t_pt < 24.0:
                continue
            band = img.crop((left, int(t_pt * scale), img.width, int(b_pt * scale)))
            col = _caption_column(band, cap[0] * scale - left, cap[2] * scale - left)
            off = (left + (band.width - col.width) // 2, int(t_pt * scale))
            cands.append((_score(col, words_px, off)[0], col))
        if not cands:
            raise SystemExit(f"figure {num}: no usable band on page {page}")
        best_score, crop = max(cands, key=lambda c: c[0])
        if best_score <= 0.0:
            raise SystemExit(
                f"figure {num}: crop on page {page} is blank or all text "
                f"(score {best_score:.3f}); re-run with --page/--full-page and cut by hand")
    crop = _trim(crop)

    dest = os.path.join(out_dir, f"figure-{num.replace('.', '-')}.png")
    crop.save(dest, optimize=True)
    os.remove(rendered)
    print(f"figure {num}: page {page} -> {os.path.relpath(dest, ROOT)} "
          f"({crop.width}x{crop.height})")
    return dest


def list_chapter(pdf, chapter):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    nums = sorted({m.group(1) for m in
                   re.finditer(rf"Figure\s+({re.escape(str(chapter))}\.\d+)\b", txt)},
                  key=lambda s: int(s.split(".")[1]))
    for n in nums:
        print(f"  Figure {n}   page {find_page(pdf, n)}")
    return nums


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("figures", nargs="*", help="e.g. 8.4 8.12")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--list", metavar="CHAPTER")
    ap.add_argument("--all-in", metavar="CHAPTER")
    ap.add_argument("--dpi", type=int, default=DPI)
    ap.add_argument("--page", type=int, help="override page lookup")
    ap.add_argument("--full-page", action="store_true",
                    help="dump the whole page (to eyeball a bad crop)")
    a = ap.parse_args()

    if a.list:
        list_chapter(a.pdf, a.list)
        return 0
    figs = a.figures
    if a.all_in:
        figs = list_chapter(a.pdf, a.all_in)
    if not figs:
        ap.error("give figure numbers, --list, or --all-in")
    for n in figs:
        try:
            extract(a.pdf, n, dpi=a.dpi, page=a.page, full_page=a.full_page)
        except Exception as e:                      # noqa: BLE001 — keep going
            print(f"figure {n}: FAILED — {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
