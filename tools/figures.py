"""Mermaid diagrams, rendered once and shared by both decks.

Why Mermaid rather than hand-drawn SVG/TikZ: it lays boxes out on a real graph
engine, so nodes come out the same size and on a common baseline. Hand-placed
rectangles drift -- different widths, ragged alignment -- and that reads as
sloppy on a projector.

One ``.mmd`` source per diagram produces two artefacts:

    figs/<id>.web.svg    dark palette, inlined into the web deck
    figs/<id>.tex.pdf    light palette, \\includegraphics'd into Beamer

Both are committed. ``mmdc`` (mermaid-cli) is only needed when a diagram's
source actually changes; a hash manifest skips everything else, so a normal
build never shells out to node.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGS = os.path.join(ROOT, "figs")
MANIFEST = os.path.join(FIGS, ".manifest.json")

# --------------------------------------------------------------------- themes
# The two palettes are the deck palettes, so a diagram never looks pasted in.
_SHARED_FLOW = {
    "curve": "basis",
    "nodeSpacing": 55,
    "rankSpacing": 60,
    "padding": 14,
    "useMaxWidth": True,
    "htmlLabels": True,
}

THEME_WEB = {
    "theme": "base",
    "themeVariables": {
        "fontFamily": "Inter, system-ui, sans-serif",
        "fontSize": "15px",
        "darkMode": True,
        "background": "transparent",
        "primaryColor": "#0E2A4E",
        "primaryTextColor": "#EAF2FF",
        "primaryBorderColor": "#22D3EE",
        "secondaryColor": "#123156",
        "secondaryTextColor": "#EAF2FF",
        "secondaryBorderColor": "#2C7BD4",
        "tertiaryColor": "#1A2F52",
        "tertiaryTextColor": "#EAF2FF",
        "tertiaryBorderColor": "#A78BFA",
        "lineColor": "#5FC9DE",
        "textColor": "#EAF2FF",
        "mainBkg": "#0E2A4E",
        "nodeBorder": "#22D3EE",
        "clusterBkg": "rgba(255,255,255,0.04)",
        "clusterBorder": "#3C6795",
        "edgeLabelBackground": "#04122B",
        "labelBoxBkgColor": "#0E2A4E",
        "labelBoxBorderColor": "#22D3EE",
        "labelTextColor": "#EAF2FF",
        "actorBkg": "#0E2A4E",
        "actorBorder": "#22D3EE",
        "actorTextColor": "#EAF2FF",
        "signalColor": "#EAF2FF",
        "signalTextColor": "#EAF2FF",
        "noteBkgColor": "#3A2E08",
        "noteTextColor": "#F0DFB4",
        "noteBorderColor": "#F5B301",
    },
    "flowchart": _SHARED_FLOW,
    "sequence": {"useMaxWidth": True, "wrap": True},
}

THEME_TEX = {
    "theme": "base",
    "themeVariables": {
        "fontFamily": "Inter, system-ui, sans-serif",
        "fontSize": "15px",
        "background": "transparent",
        "primaryColor": "#E8F2FC",
        "primaryTextColor": "#10203A",
        "primaryBorderColor": "#0050A0",
        "secondaryColor": "#F4F8FD",
        "secondaryTextColor": "#10203A",
        "secondaryBorderColor": "#2C7BD4",
        "tertiaryColor": "#F1ECFD",
        "tertiaryTextColor": "#10203A",
        "tertiaryBorderColor": "#7C5CD6",
        "lineColor": "#0E8FA8",
        "textColor": "#10203A",
        "mainBkg": "#E8F2FC",
        "nodeBorder": "#0050A0",
        "clusterBkg": "#F7FAFE",
        "clusterBorder": "#C3D6EA",
        "edgeLabelBackground": "#FFFFFF",
        "labelBoxBkgColor": "#E8F2FC",
        "labelBoxBorderColor": "#0050A0",
        "labelTextColor": "#10203A",
        "actorBkg": "#E8F2FC",
        "actorBorder": "#0050A0",
        "actorTextColor": "#10203A",
        "signalColor": "#10203A",
        "signalTextColor": "#10203A",
        "noteBkgColor": "#FFF6DC",
        "noteTextColor": "#5A4708",
        "noteBorderColor": "#B67A00",
    },
    "flowchart": _SHARED_FLOW,
    "sequence": {"useMaxWidth": True, "wrap": True},
}


def _load_manifest():
    try:
        with open(MANIFEST, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_manifest(m):
    os.makedirs(FIGS, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1, sort_keys=True)


def _run_mmdc(src, out_path, theme, pdf=False):
    cfg = json.dumps(theme)
    with tempfile.TemporaryDirectory() as td:
        mmd = os.path.join(td, "d.mmd")
        conf = os.path.join(td, "c.json")
        with open(mmd, "w", encoding="utf-8") as f:
            f.write(src)
        with open(conf, "w", encoding="utf-8") as f:
            f.write(cfg)
        cmd = ["mmdc", "-i", mmd, "-o", out_path, "-c", conf, "-b", "transparent"]
        if pdf:
            cmd.append("--pdfFit")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode != 0 or not os.path.exists(out_path):
            raise RuntimeError(
                f"mmdc failed for {os.path.basename(out_path)}:\n"
                f"{(r.stderr or r.stdout or '')[-1200:]}")


_SVG_SIZE = re.compile(r'<svg([^>]*?)>', re.S)


def _make_svg_fluid(path):
    """Strip the fixed width/height mermaid stamps on so the figure scales.

    Mermaid emits a pixel width; inside a slide we want it to fill the figure
    box and keep its aspect ratio instead.
    """
    with open(path, encoding="utf-8") as f:
        svg = f.read()

    def fix(m):
        attrs = m.group(1)
        attrs = re.sub(r'\swidth="[^"]*"', "", attrs)
        attrs = re.sub(r'\sheight="[^"]*"', "", attrs)
        if "preserveAspectRatio" not in attrs:
            attrs += ' preserveAspectRatio="xMidYMid meet"'
        return f"<svg{attrs}>"

    svg = _SVG_SIZE.sub(fix, svg, count=1)
    # mermaid inlines `max-width:...px` on the root; that caps the figure well
    # below the slide width on a projector.
    svg = re.sub(r'max-width:\s*[\d.]+px', "max-width:100%", svg)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return svg


# ----------------------------------------------- orientation, chosen by shape --
#
# A slide's figure area is much wider than it is tall -- roughly 1300 x 340.
# A `flowchart TB` with eight nodes comes out around 400 x 1000, and the browser
# does the only thing it can: it fits the whole drawing inside the box, which
# means scaling it to a quarter of its drawn size and letterboxing it with empty
# space on both sides. Nothing warns about this. The SVG is valid, the slide
# does not overflow, and the diagram is simply too small to read.
#
# Authors should not have to keep this in their heads. So the direction is
# chosen here, by measurement: render as authored, and if the result is too tall
# for the space it has to live in, render it the other way round and keep
# whichever shape suits the slide better. A diagram that is genuinely better
# vertical -- a deep chain that would become absurdly wide -- keeps its
# orientation, because the flipped version measures worse and loses.

# The figure area a slide actually offers, in CSS pixels. **Measured in a
# browser, not read off the stylesheet** -- the max-height in deck.css is an
# upper bound, and the slide's own padding, title and caption take their cut
# before the figure sees any of it. Reading 480 off the CSS and believing it
# left thirty tall diagrams undetected, because the real figure gets about 340.
SLIDE_FIG_W = 1320.0
# 270, not the 480 the stylesheet allows: the height a figure actually gets
# depends on what shares the slide with it. A figure alone measured 343; one
# with a caption and two paragraphs measured 258. A single constant cannot
# capture that, so take the tighter end -- being generous here means missing
# exactly the figures that are worst off, which is how thirty of them went
# undetected the first time.
SLIDE_FIG_H = 270.0
# Below this the drawing is being shrunk enough to hurt, and the other
# orientation is worth the second render.
WELL_ENOUGH = 0.55
# Reported after the build: diagrams still too tall even after trying.
AUTO_FLIPPED = []
STILL_TALL = []

_DIRECTION = re.compile(
    r"^(\s*(?:flowchart|graph)\s+)(TB|TD|BT|LR|RL)(\s*(?:;|$))", re.M)

_FLIP = {"TB": "LR", "TD": "LR", "BT": "RL", "LR": "TB", "RL": "BT"}


def _flip_direction(src):
    """The same diagram, laid out the other way. None if there is nothing to flip.

    Only the top-level direction is touched. A `direction` line inside a
    subgraph is the author saying something specific about that cluster, and
    overriding it would be second-guessing a decision that was made on purpose.
    """
    m = _DIRECTION.search(src)
    if not m:
        return None
    flipped = _FLIP.get(m.group(2))
    if not flipped:
        return None
    return src[:m.start()] + m.group(1) + flipped + m.group(3) + src[m.end():]


def _size(svg_path):
    """(width, height) from the viewBox, or None if it cannot be read."""
    try:
        with open(svg_path, encoding="utf-8") as f:
            head = f.read(4000)
    except OSError:
        return None
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', head)
    if not m:
        return None
    return (float(m.group(1)), float(m.group(2)))


def _rendered_scale(size):
    """How large the drawing will actually appear, 1.0 being its drawn size.

    This is the thing that matters, so compute it rather than a proxy: the
    browser fits the drawing inside the figure box, so the scale is whichever
    of the two constraints binds first.

    It needs the real dimensions, not the aspect ratio. Two drawings can share
    an aspect and render at completely different sizes, and an earlier version
    of this that scored aspect alone rated a diagram 18 times wider than tall as
    *marginally better* than one four times taller than wide — when both render
    at about half size and neither is readable.
    """
    if not size:
        return 0.0
    w, h = size
    if not w or not h:
        return 0.0
    return min(SLIDE_FIG_W / w, SLIDE_FIG_H / h, 1.0)


def _choose_source(fig_id, src, tmp_svg):
    """Render candidates and return the source whose shape suits the slide.

    Renders the authored version first. Only if that comes out tall does it pay
    for a second mmdc run, so a deck of well-shaped diagrams costs nothing.
    """
    _run_mmdc(src, tmp_svg, THEME_WEB)
    s0 = _size(tmp_svg)
    sc0 = _rendered_scale(s0)
    if s0 is None or sc0 >= WELL_ENOUGH:
        return src, sc0, False

    other = _flip_direction(src)
    if other is None:
        STILL_TALL.append((fig_id, f"{sc0:.0%}", "no direction to flip"))
        return src, sc0, False

    alt_svg = tmp_svg + ".alt.svg"
    try:
        _run_mmdc(other, alt_svg, THEME_WEB)
        sc1 = _rendered_scale(_size(alt_svg))
    except RuntimeError:
        sc1 = 0.0                      # a flip that will not render is not a flip

    if sc1 > sc0:
        shutil.move(alt_svg, tmp_svg)
        AUTO_FLIPPED.append((fig_id, f"{sc0:.0%}", f"{sc1:.0%}"))
        if sc1 < WELL_ENOUGH:
            STILL_TALL.append((fig_id, f"{sc1:.0%}",
                               "better flipped, still small -- split it"))
        return other, sc1, True

    if os.path.exists(alt_svg):
        os.remove(alt_svg)
    STILL_TALL.append((fig_id, f"{sc0:.0%}", "the other way round is worse"))
    return src, sc0, False


def render(fig_id, src, force=False):
    """Render one diagram; return (web_svg_markup, tex_pdf_relpath).

    Skips ``mmdc`` entirely when the source hash is unchanged and both
    artefacts are already on disk.
    """
    os.makedirs(FIGS, exist_ok=True)
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]
    svg_path = os.path.join(FIGS, f"{fig_id}.web.svg")
    pdf_path = os.path.join(FIGS, f"{fig_id}.tex.pdf")
    mmd_path = os.path.join(FIGS, f"{fig_id}.mmd")

    manifest = _load_manifest()
    fresh = (manifest.get(fig_id) == digest
             and os.path.exists(svg_path) and os.path.exists(pdf_path))

    if force or not fresh:
        if not shutil.which("mmdc"):
            raise RuntimeError(
                f"{fig_id}: diagram changed but mermaid-cli (mmdc) is not on PATH.\n"
                "  install:  npm i -g @mermaid-js/mermaid-cli")
        # Pick the orientation by measuring both, then render the PDF from
        # whichever won so the two artefacts never disagree.
        chosen, _, flipped = _choose_source(fig_id, src, svg_path)
        with open(mmd_path, "w", encoding="utf-8") as f:
            if flipped:
                f.write("%% direction chosen by tools/figures.py: this renders\n"
                        "%% better in the space a slide gives it. Edit the deck\n"
                        "%% source, not this file.\n")
            f.write(chosen.rstrip("\n") + "\n")
        _make_svg_fluid(svg_path)
        _run_mmdc(chosen, pdf_path, THEME_TEX, pdf=True)
        manifest[fig_id] = digest
        _save_manifest(manifest)

    with open(svg_path, encoding="utf-8") as f:
        markup = f.read()
    # Drop the XML prolog/doctype; the SVG is inlined into an HTML document.
    markup = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", markup)
    markup = re.sub(r"^\s*<!DOCTYPE[^>]*>\s*", "", markup)
    return markup, f"figs/{fig_id}.tex.pdf"


# ------------------------------------------------- hand-drawn figures (SVG) --
#
# Diagrams from tools/diagrams.py are authored as SVG directly, in two
# palettes. The dark one is inlined into the web deck as-is; the light one has
# to become a PDF for Beamer, and Chrome is already a build dependency (mmdc
# drives it), so it does the conversion rather than adding cairosvg or
# librsvg to the list of things that must be installed before the deck builds.

CHROME = os.environ.get("CHROME_BIN", "/usr/bin/google-chrome")

_VIEWBOX = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')


def _svg_to_pdf(svg_text, out_path):
    """Print one SVG to a PDF page cut exactly to the drawing.

    The page is sized from the viewBox rather than left at A4, so the figure
    arrives in LaTeX with no border to fight and ``includegraphics`` can scale
    it like any other image.
    """
    m = _VIEWBOX.search(svg_text)
    w, h = (float(m.group(1)), float(m.group(2))) if m else (1000.0, 600.0)
    win, hin = w / 96.0, h / 96.0

    html = (
        "<!doctype html><meta charset='utf-8'><style>"
        f"@page{{size:{win:.4f}in {hin:.4f}in;margin:0}}"
        "html,body{margin:0;padding:0;background:transparent}"
        f"svg{{display:block;width:{win:.4f}in;height:{hin:.4f}in}}"
        "</style>" + svg_text
    )
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "f.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(html)
        r = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--no-pdf-header-footer", f"--print-to-pdf={out_path}",
             "file://" + src],
            capture_output=True, text=True, timeout=180)
    if not os.path.exists(out_path):
        raise RuntimeError(f"chrome could not print {os.path.basename(out_path)}:\n"
                           f"{(r.stderr or r.stdout or '')[-800:]}")


def render_drawn(fig_id, web_svg, print_svg, force=False):
    """Cache a hand-drawn figure; return (web markup, tex pdf relpath).

    Same contract and same hash-skip as :func:`render`, so a build that changes
    no diagram never starts a browser.
    """
    os.makedirs(FIGS, exist_ok=True)
    digest = hashlib.sha256((web_svg + print_svg).encode("utf-8")).hexdigest()[:16]
    svg_path = os.path.join(FIGS, f"{fig_id}.web.svg")
    pdf_path = os.path.join(FIGS, f"{fig_id}.tex.pdf")

    manifest = _load_manifest()
    fresh = (manifest.get(fig_id) == digest
             and os.path.exists(svg_path) and os.path.exists(pdf_path))
    if force or not fresh:
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(web_svg)
        _svg_to_pdf(print_svg, pdf_path)
        manifest[fig_id] = digest
        _save_manifest(manifest)

    return web_svg, f"figs/{fig_id}.tex.pdf"
