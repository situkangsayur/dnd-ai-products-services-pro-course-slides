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
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(src.rstrip("\n") + "\n")
        _run_mmdc(src, svg_path, THEME_WEB)
        _make_svg_fluid(svg_path)
        _run_mmdc(src, pdf_path, THEME_TEX, pdf=True)
        manifest[fig_id] = digest
        _save_manifest(manifest)

    with open(svg_path, encoding="utf-8") as f:
        markup = f.read()
    # Drop the XML prolog/doctype; the SVG is inlined into an HTML document.
    markup = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", markup)
    markup = re.sub(r"^\s*<!DOCTYPE[^>]*>\s*", "", markup)
    return markup, f"figs/{fig_id}.tex.pdf"
