"""Primitives for hand-drawn figures, in two palettes.

Mermaid is right for a graph of boxes and wrong for everything else. A neural
network is not a flowchart: the interesting part is that there are *neurons*,
that every one of them is connected to every one in the next layer, and that
the shapes change as data moves along. Drawn as five rounded rectangles, all of
that disappears and the slide teaches nothing it could not have said in a
sentence.

So these figures are drawn. Every generator here returns a self-contained SVG
that says what it is about: real circles for neurons, real numbers in the cells
of a tensor, a window that actually slides along real text.

Two palettes, from one call. The web deck is dark and the printed PDF is light,
and a figure that only works on one of them is a figure that will embarrass
somebody at a printer. ``build(pal)`` is called twice and the two results are
cached side by side.

Animation is web only, expressed as SMIL/CSS inside the SVG, and every animated
figure is authored so its **static** state -- what the PDF shows -- is already
the complete picture. An animation that carries meaning the still frame lacks
is an animation that half the audience never sees.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape


@dataclass(frozen=True)
class Palette:
    """Colours and type, resolved once so a generator never branches on theme."""

    name: str
    ink: str          # primary text
    ink2: str         # secondary text
    ink3: str         # captions, axis labels
    line: str         # structural strokes
    faint: str        # hairlines, grid
    fill: str         # panel/cell background
    fill2: str        # alternate cell
    accent: str       # the thing being pointed at
    accent_fill: str
    warm: str         # a second highlight, for "before/after" pairs
    warm_fill: str
    good: str
    bad: str
    mono: str = "ui-monospace, 'JetBrains Mono', 'SF Mono', Menlo, monospace"
    sans: str = "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"


WEB = Palette(
    name="web",
    ink="#EAF2FF", ink2="#B6C9E4", ink3="#8FA6C6",
    line="#5FC9DE", faint="rgba(160,205,255,0.22)",
    fill="rgba(255,255,255,0.055)", fill2="rgba(255,255,255,0.10)",
    accent="#22D3EE", accent_fill="rgba(34,211,238,0.16)",
    warm="#F5B301", warm_fill="rgba(245,179,1,0.15)",
    good="#7BD949", bad="#FB7185",
)

PRINT = Palette(
    name="print",
    ink="#10203A", ink2="#33465F", ink3="#5A6B82",
    line="#0E8FA8", faint="rgba(16,32,58,0.22)",
    fill="#F2F7FC", fill2="#E4EEF8",
    accent="#0E8FA8", accent_fill="#DCF1F6",
    warm="#B67A00", warm_fill="#FFF3D6",
    good="#4A8B26", bad="#D14257",
)

PALETTES = (WEB, PRINT)


# --------------------------------------------------------------- primitives --

def esc(s) -> str:
    return escape(str(s), quote=True)


def step_attr(step):
    """``data-step="N"`` — the hook the deck's simulator drives.

    An element carrying a step is hidden until the simulation reaches it. The
    numbering starts at 1; step 0, or no attribute at all, means "always
    visible" -- the axes, the curve, the labels. Static renders (the PDF) ignore
    the attribute entirely and show the finished picture, which is why every
    animated figure has to be legible with every step revealed at once.
    """
    return "" if not step else f' data-step="{int(step)}"'


def txt(x, y, s, *, size=13, fill=None, anchor="middle", weight=400,
        mono=False, pal=None, opacity=None, cls="", baseline="middle",
        italic=False, step=0):
    """One line of SVG text.

    Native ``<text>``, never HTML in a foreignObject. That choice is the whole
    reason these figures cannot suffer the clipping bug that mermaid labels do:
    SVG text has no box to be cut off by, and it scales with the drawing
    instead of being re-laid-out by whatever stylesheet the page happens to
    have.
    """
    p = pal or WEB
    style = (f"font:{'italic ' if italic else ''}{weight} {size}px "
             f"{p.mono if mono else p.sans}")
    extra = f' opacity="{opacity}"' if opacity is not None else ""
    klass = f' class="{cls}"' if cls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'dominant-baseline="{baseline}" fill="{fill or p.ink}" '
            f'style="{style}"{extra}{klass}{step_attr(step)}>{esc(s)}</text>')


def rect(x, y, w, h, *, r=6, fill="none", stroke=None, sw=1.2, pal=None,
         dash=None, cls="", opacity=None, step=0):
    p = pal or WEB
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    k = f' class="{cls}"' if cls else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" fill="{fill}" stroke="{stroke or p.faint}" '
            f'stroke-width="{sw}"{d}{o}{k}{step_attr(step)}/>')


def line(x1, y1, x2, y2, *, stroke=None, sw=1.2, pal=None, dash=None,
         opacity=None, cls="", cap="round", step=0):
    p = pal or WEB
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    k = f' class="{cls}"' if cls else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke or p.faint}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}"{d}{o}{k}{step_attr(step)}/>')


def circle(cx, cy, r, *, fill=None, stroke=None, sw=1.4, pal=None, cls="",
           opacity=None, step=0):
    p = pal or WEB
    o = f' opacity="{opacity}"' if opacity is not None else ""
    k = f' class="{cls}"' if cls else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill or p.fill}" stroke="{stroke or p.line}" '
            f'stroke-width="{sw}"{o}{k}{step_attr(step)}/>')


def path(d, *, fill="none", stroke=None, sw=1.4, pal=None, dash=None,
         cls="", opacity=None, marker=False, step=0):
    p = pal or PALETTES[0]
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    k = f' class="{cls}"' if cls else ""
    m = f' marker-end="url(#arw-{p.name})"' if marker else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke or p.line}" '
            f'stroke-width="{sw}"{ds}{o}{k}{m}{step_attr(step)}/>')


def arrow(x1, y1, x2, y2, *, stroke=None, sw=1.6, pal=None, dash=None,
          opacity=None, cls="", step=0):
    """A straight arrow with a head. The head is a marker defined in `defs`."""
    p = pal or WEB
    return path(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}",
                stroke=stroke or p.line, sw=sw, pal=p, dash=dash,
                opacity=opacity, cls=cls, marker=True, step=step)


def defs(pal, extra=""):
    """Arrow markers, one per palette so the colours never cross over."""
    return (
        f'<defs><marker id="arw-{pal.name}" viewBox="0 0 10 10" refX="9" '
        f'refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M0,1 L9,5 L0,9 z" fill="{pal.line}"/></marker>'
        f'{extra}</defs>'
    )


def svg(w, h, body, *, pal=None, style="", cls="dfig", steps=0, sim_label=""):
    """Wrap a body in a viewBox'd SVG that scales to its container.

    ``steps`` marks the figure as a simulation: the deck gives it a control bar
    and reveals the ``data-step`` elements one at a time. The PDF has no
    JavaScript and simply shows all of them, so a stepped figure must still read
    correctly fully revealed.
    """
    p = pal or WEB
    sim = (f' data-sim="{int(steps)}"' if steps else "")
    lab = f' data-sim-label="{esc(sim_label)}"' if sim_label else ""
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'preserveAspectRatio="xMidYMid meet" role="img"{sim}{lab} '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'{defs(p)}<style>{style}</style>{body}</svg>')


# ------------------------------------------------------------------ helpers --

def fmt(v, places=2):
    """Numbers as a reader would write them, not as float repr does.

    ``0.30000000000000004`` on a slide is a distraction that costs a minute of
    the session and teaches nothing.
    """
    if isinstance(v, str):
        return v
    if isinstance(v, int) or float(v).is_integer():
        return str(int(v))
    s = f"{float(v):.{places}f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def wrap(s, width):
    """Greedy wrap for caption strips inside a figure."""
    out, cur = [], ""
    for word in str(s).split():
        if len(cur) + len(word) + 1 <= width:
            cur = f"{cur} {word}".strip()
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out
