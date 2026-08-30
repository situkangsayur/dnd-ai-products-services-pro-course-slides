"""Figure generators: networks with neurons in them, tensors with numbers in them.

Each generator returns a ready-to-use ``draw`` block::

    from diagrams import neural_net
    neural_net("ch02-mnist-net",
               layers=[("Input", 784), ("Dense relu", 512), ("Dense softmax", 10)],
               cap="Every unit in a layer is connected to every unit in the next.")

The block carries two SVGs, one per palette, and the build turns the light one
into a PDF for Beamer. Nothing here needs mermaid and nothing here can be
clipped: the text is native SVG, so there is no fixed-size HTML box for a
stylesheet to overflow.

**Representative drawing.** A layer of 512 units cannot be drawn as 512 circles
and should not be drawn as one rectangle labelled "512". These generators draw
the first few, an ellipsis, and the last one, with the real count on the axis --
so the picture is honest about the size and still shows what a unit is.
"""

from __future__ import annotations

import svgkit as K
from svgkit import PALETTES, arrow, circle, fmt, line, rect, svg, txt


def _block(fig_id, build, cap="", note="", full=False):
    """Run ``build(pal)`` once per palette and package the result."""
    return {
        "t": "draw",
        "id": fig_id,
        "svg": build(PALETTES[0]),
        "print": build(PALETTES[1]),
        "cap": cap,
        "note": note,
        "full": full,
    }


# ============================================================ neural networks --

def neural_net(fig_id, layers, *, cap="", note="", max_dots=6, show_edges=True,
               animate=True, highlight=None, width=980, height=430,
               full=False):
    """A layered network drawn as units and connections.

    ``layers`` is a list of ``(label, count)`` or ``(label, count, sublabel)``.
    Counts are real: the drawing shows the first few units, an ellipsis, and the
    last, with ``n = 512`` written underneath. That is what makes it a picture
    of a 512-unit layer rather than a picture of six circles.

    ``highlight`` is an optional ``(layer_index, unit_index)`` whose incoming
    connections are drawn on top and in the accent colour -- the one unit whose
    arithmetic the next slide works through.
    """
    norm = []
    for spec in layers:
        lbl, n = spec[0], spec[1]
        sub = spec[2] if len(spec) > 2 else ""
        norm.append((lbl, int(n), sub))

    def build(p):
        pad_x, top, bot = 92, 96, 86
        usable_h = height - top - bot
        n_layers = len(norm)
        step = (width - 2 * pad_x) / max(n_layers - 1, 1)
        xs = [pad_x + i * step for i in range(n_layers)]

        # Positions per layer: at most `max_dots` drawn units, with a gap where
        # the ellipsis goes when the real count exceeds what we draw.
        drawn, gaps = [], []
        for _, n, _ in norm:
            k = min(n, max_dots)
            elided = n > max_dots
            r = 15 if k <= 6 else 12
            span = usable_h
            ys = ([top + span * (j + 0.5) / k for j in range(k)] if k > 1
                  else [top + span / 2])
            drawn.append((ys, r))
            gaps.append(elided)

        out = []

        # Connections first, so units sit on top of them.
        if show_edges:
            for i in range(n_layers - 1):
                ys0, r0 = drawn[i]
                ys1, r1 = drawn[i + 1]
                for y0 in ys0:
                    for y1 in ys1:
                        out.append(line(xs[i] + r0, y0, xs[i + 1] - r1, y1,
                                        stroke=p.faint, sw=0.7, pal=p,
                                        opacity=0.55, step=i + 2))

        # The one unit whose sum the next slide computes.
        if highlight is not None:
            li, ui = highlight
            if 0 < li < n_layers:
                ys_prev, r_prev = drawn[li - 1]
                ys_here, r_here = drawn[li]
                if ui < len(ys_here):
                    for y0 in ys_prev:
                        out.append(line(xs[li - 1] + r_prev, y0,
                                        xs[li] - r_here, ys_here[ui],
                                        stroke=p.accent, sw=1.5, pal=p,
                                        opacity=0.95))

        # Units.
        for i, ((lbl, n, sub), (ys, r)) in enumerate(zip(norm, drawn)):
            is_first, is_last = i == 0, i == n_layers - 1
            col = p.accent if (is_last or is_first) else p.line
            fillc = p.accent_fill if (is_last or is_first) else p.fill
            for j, y in enumerate(ys):
                hot = highlight is not None and highlight == (i, j)
                out.append(circle(xs[i], y, r, pal=p,
                                  fill=p.accent_fill if hot else fillc,
                                  stroke=p.accent if hot else col,
                                  sw=2.2 if hot else 1.4,
                                  step=i + 1))
            if gaps[i]:
                # The ellipsis is the honest part of the drawing: it says
                # "there are more of these, and we are not pretending
                # otherwise".
                mid = (ys[len(ys) // 2 - 1] + ys[len(ys) // 2]) / 2 if len(ys) > 1 else ys[0]
                for d in (-9, 0, 9):
                    out.append(circle(xs[i], mid + d, 1.9, pal=p,
                                      fill=p.ink3, stroke="none", sw=0))

            out.append(txt(xs[i], top - 44, lbl, size=15, weight=600, pal=p,
                           fill=p.ink))
            out.append(txt(xs[i], top - 24,
                           sub or ("n = %s" % f"{n:,}".replace(",", " ")),
                           size=12.5, pal=p, fill=p.ink3, mono=not sub))
            if not sub:
                pass
            out.append(txt(xs[i], height - bot + 34,
                           f"unit 1 … unit {n:,}".replace(",", " ")
                           if n > max_dots else
                           " · ".join(f"u{j+1}" for j in range(n)),
                           size=11.5, pal=p, fill=p.ink3, mono=True))

        # Shape ribbon along the bottom: what a batch actually looks like here.
        ribbon_y = height - 30
        out.append(line(pad_x - 40, ribbon_y, width - pad_x + 40, ribbon_y,
                        stroke=p.faint, sw=1, pal=p, dash="4 5"))
        for i, (lbl, n, _) in enumerate(norm):
            out.append(txt(xs[i], ribbon_y + 16, f"(batch, {n})",
                           size=12, pal=p, fill=p.ink2, mono=True))

        return svg(width, height, "".join(out), pal=p,
                   steps=n_layers if animate else 0, sim_label="layer")

    return _block(fig_id, build, cap=cap, note=note, full=full)


def neuron_math(fig_id, *, inputs, weights, bias, act="relu", cap="", note="",
                width=940, height=330, full=False):
    """One unit, with the arithmetic written out.

    The companion to :func:`neural_net`: that one shows there are thousands of
    these, this one shows what exactly one of them does, with numbers a reader
    can check on paper. Between them there is no step where the audience has to
    take the mechanism on trust.
    """
    def build(p):
        out = []
        cx, cy, r = width * 0.56, 132, 42
        n = len(inputs)
        x_in = 108
        ys = [56 + (196 * (i + 0.5) / n) for i in range(n)]

        for i, (xv, w) in enumerate(zip(inputs, weights)):
            out.append(rect(x_in - 46, ys[i] - 15, 56, 30, r=6, pal=p,
                            fill=p.fill, stroke=p.faint))
            out.append(txt(x_in - 18, ys[i], fmt(xv), size=14, mono=True, pal=p))
            out.append(txt(x_in - 62, ys[i], f"x{i+1}", size=12.5, pal=p,
                           fill=p.ink3, anchor="end", italic=True))
            out.append(arrow(x_in + 12, ys[i], cx - r - 4, cy, pal=p,
                             stroke=p.line, sw=1.3))
            # The weight rides on the wire, which is where it belongs: a weight
            # is a property of the connection, not of either end.
            mx, my = (x_in + 12 + cx - r) / 2, (ys[i] + cy) / 2
            out.append(rect(mx - 30, my - 12, 60, 22, r=11, pal=p,
                            fill=p.fill2, stroke=p.faint, sw=0.9))
            out.append(txt(mx, my - 1, f"w{i+1}={fmt(w)}", size=11.5, mono=True,
                           pal=p, fill=p.ink2))

        out.append(circle(cx, cy, r, pal=p, fill=p.accent_fill,
                          stroke=p.accent, sw=2))
        out.append(txt(cx, cy - 9, "Σ", size=22, weight=600, pal=p,
                       fill=p.accent))
        out.append(txt(cx, cy + 15, act, size=12, mono=True, pal=p, fill=p.ink2))
        out.append(txt(cx, cy + r + 22, f"bias {fmt(bias)}", size=12, mono=True,
                       pal=p, fill=p.ink3))

        z = sum(x * w for x, w in zip(inputs, weights)) + bias
        a = max(0.0, z) if act == "relu" else z
        out.append(arrow(cx + r + 6, cy, width - 150, cy, pal=p,
                         stroke=p.accent, sw=1.8))
        out.append(rect(width - 146, cy - 22, 118, 44, r=8, pal=p,
                        fill=p.accent_fill, stroke=p.accent, sw=1.6))
        out.append(txt(width - 87, cy, fmt(a, 3), size=18, weight=600,
                       mono=True, pal=p, fill=p.ink))
        out.append(txt(width - 87, cy - 34, "output", size=12, pal=p,
                       fill=p.ink3))

        # The sum, spelled out. This is the line people photograph.
        terms = " + ".join(f"{fmt(x)}×{fmt(w)}"
                           for x, w in zip(inputs, weights))
        out.append(txt(width / 2, height - 46,
                       f"z = {terms} + {fmt(bias)} = {fmt(z, 3)}",
                       size=14, mono=True, pal=p, fill=p.ink2))
        out.append(txt(width / 2, height - 22,
                       f"{act}(z) = max(0, {fmt(z, 3)}) = {fmt(a, 3)}"
                       if act == "relu" else f"{act}(z) = {fmt(a, 3)}",
                       size=14, mono=True, pal=p, fill=p.accent))
        return svg(width, height, "".join(out), pal=p)

    return _block(fig_id, build, cap=cap, note=note, full=full)


# =================================================================== tensors --

def tensor_ranks(fig_id, *, cap="", note="", width=1000, height=360,
                 full=False):
    """Rank 0 to rank 3, drawn with the actual numbers in the cells.

    The usual version of this slide is four labelled rectangles, which tells a
    reader who already knows what a tensor is that they were right. Someone who
    does not know needs to *see* that a matrix is rows of vectors and that a
    rank-3 tensor is a stack of matrices.
    """
    def build(p):
        out = []
        cell, gap = 34, 4
        cols_x = [70, 258, 470, 742]
        base_y = 132

        def grid(x, y, data, *, depth=0):
            """Draw back-to-front so the front slice is the one you read.

            The stacked copies behind it are what makes a rank-3 tensor look
            like a stack rather than a matrix with a shadow, so they are offset
            down and to the right -- away from the reader, the way a pile of
            paper sits."""
            g = []
            for k in range(depth, -1, -1):
                ox, oy = k * 16, k * 14
                for i, row in enumerate(data):
                    for j, v in enumerate(row):
                        cx = x + ox + j * (cell + gap)
                        cy = y + oy + i * (cell + gap)
                        g.append(rect(cx, cy, cell, cell, r=4, pal=p,
                                      fill=p.fill if k == 0 else p.fill2,
                                      stroke=p.faint,
                                      sw=1.2 if k == 0 else 0.8,
                                      opacity=1 if k == 0 else 0.5))
                        if k == 0:
                            g.append(txt(cx + cell / 2, cy + cell / 2, fmt(v),
                                         size=12.5, mono=True, pal=p,
                                         fill=p.ink))
            return "".join(g)

        specs = [
            ("Rank 0 — scalar", "shape ()", [[7]], 0,
             "a single number"),
            ("Rank 1 — vector", "shape (4,)", [[7, 2, 9, 4]], 0,
             "a row of numbers"),
            ("Rank 2 — matrix", "shape (3, 4)",
             [[7, 2, 9, 4], [1, 8, 3, 6], [5, 0, 2, 7]], 0,
             "rows of vectors"),
            ("Rank 3 — tensor", "shape (2, 3, 4)",
             [[7, 2, 9, 4], [1, 8, 3, 6], [5, 0, 2, 7]], 1,
             "a stack of matrices"),
        ]
        # Every column shares one baseline for its title, its grid and its
        # blurb. Ragged baselines read as carelessness from the back of a room.
        blurb_y = base_y + 3 * (cell + gap) + 46
        for x, (title, shape, data, depth, blurb) in zip(cols_x, specs):
            out.append(txt(x, 44, title, size=15, weight=600, pal=p,
                           anchor="start", fill=p.ink))
            out.append(txt(x, 66, shape, size=12.5, mono=True, pal=p,
                           anchor="start", fill=p.accent))
            out.append(grid(x, base_y, data, depth=depth))
            out.append(txt(x, blurb_y, blurb, size=12.5, pal=p,
                           anchor="start", fill=p.ink3))

        out.append(txt(width / 2, height - 22,
                       "Rank is how many indices it takes to reach one number: "
                       "t, t[i], t[i][j], t[i][j][k].",
                       size=13, pal=p, fill=p.ink2))
        return svg(width, height, "".join(out), pal=p)

    return _block(fig_id, build, cap=cap, note=note, full=full)


def tensor_grid(fig_id, data, *, title="", shape=None, dtype=None, cap="",
                note="", highlight=None, cell=38, full=False, legend=""):
    """One tensor, drawn as its numbers, with an optional highlighted cell."""
    rows = len(data)
    cols = max(len(r) for r in data)

    def build(p):
        gap = 5
        w = 120 + cols * (cell + gap)
        h = 130 + rows * (cell + gap)
        out = []
        if title:
            out.append(txt(60, 40, title, size=16, weight=600, pal=p,
                           anchor="start", fill=p.ink))
        sh = shape or f"({rows}, {cols})"
        out.append(txt(60, 64, f"shape {sh}" + (f" · {dtype}" if dtype else ""),
                       size=12.5, mono=True, pal=p, anchor="start",
                       fill=p.accent))
        # Index rulers, so "row 1, column 2" means something on the picture.
        for j in range(cols):
            out.append(txt(60 + j * (cell + gap) + cell / 2, 88, str(j),
                           size=11, mono=True, pal=p, fill=p.ink3))
        for i, row in enumerate(data):
            y = 100 + i * (cell + gap)
            out.append(txt(48, y + cell / 2, str(i), size=11, mono=True, pal=p,
                           fill=p.ink3, anchor="end"))
            for j, v in enumerate(row):
                x = 60 + j * (cell + gap)
                hot = highlight is not None and (i, j) in highlight
                out.append(rect(x, y, cell, cell, r=5, pal=p,
                                fill=p.accent_fill if hot else p.fill,
                                stroke=p.accent if hot else p.faint,
                                sw=1.8 if hot else 1))
                out.append(txt(x + cell / 2, y + cell / 2, fmt(v), size=13,
                               mono=True, pal=p,
                               fill=p.accent if hot else p.ink))
        if legend:
            out.append(txt(60, h - 30, legend, size=12.5, pal=p, anchor="start",
                           fill=p.ink2))
        return svg(w, h, "".join(out), pal=p)

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================================================= geometry --

def geometric_ops(fig_id, *, cap="", note="", width=1080, height=400,
                  full=False):
    """The four transforms, applied to an actual shape.

    "Multiply by a rotation matrix → rotation" is a true sentence and a useless
    picture. Here the same little arrow-shape is drawn faintly in its original
    position and solidly after the transform, with the matrix that did it
    printed underneath, so the words *translation*, *rotation*, *scaling* and
    *affine* attach to something the eye can check.
    """
    import math

    # A wedge, not a square: a square looks the same after a 90 degree rotation
    # and after a reflection, which defeats the whole point of the figure.
    SHAPE = [(0, 0), (1.0, 0), (1.0, 0.45), (0.55, 0.45), (0.55, 1.0), (0, 1.0)]

    def build(p):
        out = []
        panel_w, gap = 232, 24
        x0 = 40
        unit = 40          # pixels per unit of the little coordinate system

        def apply(mat, off, pts):
            (a, b), (c, d) = mat
            ox, oy = off
            return [(a * x + b * y + ox, c * x + d * y + oy) for x, y in pts]

        def poly(pts, px, py, *, solid, pal):
            # y grows downward in SVG and upward in mathematics; flip once,
            # here, rather than mentally in every coordinate below.
            d = " ".join(
                f"{'M' if i == 0 else 'L'}{px + x * unit:.1f},{py - y * unit:.1f}"
                for i, (x, y) in enumerate(pts)) + " Z"
            return (f'<path d="{d}" fill="{pal.accent_fill if solid else "none"}" '
                    f'stroke="{pal.accent if solid else pal.faint}" '
                    f'stroke-width="{1.9 if solid else 1.2}" '
                    f'{"" if solid else "stroke-dasharray=\'4 4\'"}/>')

        cases = [
            ("Translation", "y = x + b",
             ((1, 0), (0, 1)), (0.9, 0.5), "add a vector"),
            ("Rotation", "y = R · x",
             ((math.cos(0.6), -math.sin(0.6)), (math.sin(0.6), math.cos(0.6))),
             (0, 0), "multiply by a rotation matrix"),
            ("Scaling", "y = D · x",
             ((1.5, 0), (0, 0.6)), (0, 0), "multiply by a diagonal matrix"),
            ("Affine", "y = W · x + b",
             ((1.1, 0.45), (0.15, 0.9)), (0.5, 0.25),
             "any matrix, then a vector"),
        ]

        for i, (title, formula, mat, off, blurb) in enumerate(cases):
            # The origin sits in from the panel edge, low enough that a
            # rotated shape still has room to swing without leaving the card.
            px = x0 + i * (panel_w + gap) + 54
            py = 244
            cx = px - 54 + panel_w / 2
            out.append(rect(px - 54, 62, panel_w, 252, r=10, pal=p,
                            fill=p.fill, stroke=p.faint, sw=1))
            out.append(txt(cx, 40, title, size=15,
                           weight=600, pal=p, fill=p.ink))
            # Axes, so "it moved" is measurable rather than impressionistic.
            out.append(line(px - 42, py, px + 140, py, stroke=p.faint, sw=1,
                            pal=p))
            out.append(line(px, py + 22, px, py - 152, stroke=p.faint, sw=1,
                            pal=p))
            out.append(poly(SHAPE, px, py, solid=False, pal=p))
            out.append(poly(apply(mat, off, SHAPE), px, py, solid=True, pal=p))
            out.append(txt(cx, 288, formula, size=13.5,
                           mono=True, pal=p, fill=p.accent))
            out.append(txt(cx, 307, blurb, size=11.5, pal=p, fill=p.ink3))

        out.append(txt(width / 2, height - 26,
                       "Dashed: before.  Solid: after.  Every layer in a network "
                       "does the last one — a matrix, then a vector.",
                       size=13, pal=p, fill=p.ink2))
        return svg(width, height, "".join(out), pal=p)

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================================== gradient descent, stepped --

def sgd_descent(fig_id, *, cap="", note="", lr=0.28, start=-2.45, steps=7,
                width=1020, height=430, full=False, animate=True):
    """Gradient descent walked down a real curve, with the arithmetic per step.

    The version of this slide everyone has seen is a smooth ball rolling into a
    valley, which shows that optimisation goes downhill and nothing else. What
    a reader actually needs is the *update*: where the slope was measured, how
    big the step was, and why the steps get smaller near the bottom. So the
    curve is real, the derivative is real, and the first few updates are
    printed as sums that can be checked by hand.

    The loss is f(w) = w^2/4 + sin(2w)/2 + 1 -- convex enough to converge, bumpy
    enough that the path is not a straight slide.
    """
    import math

    def f(w):
        return w * w / 4 + math.sin(2 * w) / 2 + 1

    def df(w):
        return w / 2 + math.cos(2 * w)

    # Walk it once, in Python, so the drawing and the numbers cannot disagree.
    path = []
    w = start
    for _ in range(steps):
        g = df(w)
        path.append((w, f(w), g))
        w = w - lr * g
    path.append((w, f(w), df(w)))

    def build(p):
        out = []
        left, right, top, bot = 92, width - 340, 66, 128
        w_lo, w_hi = -3.0, 3.0
        ys = [f(w_lo + (w_hi - w_lo) * i / 200) for i in range(201)]
        f_lo, f_hi = min(ys) - 0.15, max(ys) + 0.25

        def X(w):
            return left + (w - w_lo) / (w_hi - w_lo) * (right - left)

        def Y(v):
            return top + (f_hi - v) / (f_hi - f_lo) * (height - bot - top)

        # axes
        out.append(line(left - 18, Y(f_lo), right + 16, Y(f_lo), pal=p,
                        stroke=p.faint, sw=1.1))
        out.append(line(X(0), top - 10, X(0), Y(f_lo) + 12, pal=p,
                        stroke=p.faint, sw=1.1, dash="3 4"))
        out.append(txt(right + 20, Y(f_lo) + 2, "w", size=13, pal=p,
                       fill=p.ink3, anchor="start", italic=True))
        out.append(txt(left - 30, top + 6, "loss", size=13, pal=p, fill=p.ink3,
                       anchor="end"))

        # the curve
        d = " ".join(
            f"{'M' if i == 0 else 'L'}{X(w_lo + (w_hi - w_lo) * i / 200):.1f},"
            f"{Y(f(w_lo + (w_hi - w_lo) * i / 200)):.1f}" for i in range(201))
        out.append(f'<path d="{d}" fill="none" stroke="{p.line}" '
                   f'stroke-width="2" opacity="0.85"/>')

        # the minimum, so "downhill" has a destination
        wm = min((w_lo + (w_hi - w_lo) * i / 200 for i in range(201)), key=f)
        out.append(line(X(wm), Y(f(wm)), X(wm), Y(f_lo), pal=p, stroke=p.faint,
                        sw=1, dash="2 4"))
        out.append(txt(X(wm), Y(f_lo) + 22, "minimum", size=11.5, pal=p,
                       fill=p.ink3))

        # The walk, one simulation step per update: the tangent appears, then
        # the arrow that follows from it, then the point it lands on. That
        # order is the algorithm, so it is the order the figure reveals.
        for i, (wv, fv, g) in enumerate(path):
            x, y = X(wv), Y(fv)
            if i < len(path) - 1:
                nx, ny = X(path[i + 1][0]), Y(path[i + 1][1])
                out.append(arrow(x, y, nx, ny, pal=p, stroke=p.warm, sw=1.6,
                                 opacity=0.9, step=i + 1))
                # The tangent is the whole mechanism: the step is the slope,
                # scaled. Draw it in DATA space and map through X/Y -- doing the
                # trigonometry in pixels gets the aspect ratio wrong and the
                # tangents come out near-vertical, which is worse than omitting
                # them.
                dw = 0.34
                out.append(line(X(wv - dw), Y(fv - g * dw),
                                X(wv + dw), Y(fv + g * dw),
                                pal=p, stroke=p.accent, sw=1.3, opacity=0.8,
                                step=i + 1))
            out.append(circle(x, y, 6.5 if i else 8, pal=p,
                              fill=p.warm_fill if i else p.accent_fill,
                              stroke=p.warm if i else p.accent, sw=1.8,
                              step=i if i else 0))
            if i == 0:
                out.append(txt(x, y - 20, "start", size=11.5, pal=p,
                               fill=p.accent))

        # the arithmetic, beside the curve rather than under it
        px = right + 42
        out.append(txt(px, top + 6, "w ← w − lr · dL/dw", size=14, mono=True,
                       pal=p, fill=p.ink, anchor="start"))
        out.append(txt(px, top + 28, f"lr = {fmt(lr)}", size=12.5, mono=True,
                       pal=p, fill=p.ink3, anchor="start"))
        for i, (wv, fv, g) in enumerate(path[:5]):
            y = top + 60 + i * 26
            nxt = wv - lr * g
            out.append(txt(px, y, f"{fmt(wv, 3)} − {fmt(lr)}·{fmt(g, 3)}"
                                  f" = {fmt(nxt, 3)}",
                           size=12.5, mono=True, pal=p, fill=p.ink2,
                           anchor="start", step=i + 1))
        out.append(txt(px, top + 60 + 5 * 26 + 8, "…", size=13, mono=True,
                       pal=p, fill=p.ink3, anchor="start"))

        out.append(txt(width / 2, height - 30,
                       "The step shrinks on its own as the slope flattens — "
                       "nothing in the rule schedules that.",
                       size=13, pal=p, fill=p.ink2))

        return svg(width, height, "".join(out), pal=p,
                   steps=(len(path) - 1) if animate else 0,
                   sim_label="update")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ============================================ text: n-grams, chunks, windows --

def sliding_window(fig_id, tokens, *, n=3, stride=1, cap="", note="",
                   label="n-gram", width=1040, full=False, animate=True,
                   max_windows=5):
    """A window that actually slides along actual text.

    n-grams and chunking are the same picture with different labels, and both
    are usually taught as a definition plus an example list. Drawn, the thing
    that matters becomes obvious in one look: **the windows overlap**, which is
    why a chunk boundary can cut a sentence in half and why overlap costs you
    storage.
    """
    toks = list(tokens)
    starts = list(range(0, max(len(toks) - n + 1, 1), stride))[:max_windows]

    def build(p):
        out = []
        cw, gap = 108, 6
        x0, y0 = 60, 92
        row_h = 46

        out.append(txt(x0, 44, f"{label}, n = {n}"
                              + (f", stride {stride}" if stride != 1 else ""),
                       size=15, weight=600, pal=p, anchor="start", fill=p.ink))

        # the text itself, once, as the ruler everything else lines up with
        for j, t in enumerate(toks):
            x = x0 + j * (cw + gap)
            out.append(rect(x, y0, cw, 34, r=5, pal=p, fill=p.fill,
                            stroke=p.faint))
            out.append(txt(x + cw / 2, y0 + 17, t, size=13, pal=p, fill=p.ink))
            out.append(txt(x + cw / 2, y0 - 12, str(j), size=10.5, mono=True,
                           pal=p, fill=p.ink3))

        # one row per window, so the overlap is visible as a staircase
        for i, s in enumerate(starts):
            y = y0 + 58 + i * row_h
            x = x0 + s * (cw + gap)
            w = n * cw + (n - 1) * gap
            st = i + 1
            out.append(rect(x - 4, y - 4, w + 8, 34, r=7, pal=p,
                            fill=p.accent_fill, stroke=p.accent, sw=1.6,
                            step=st))
            for k in range(n):
                if s + k < len(toks):
                    out.append(txt(x + k * (cw + gap) + cw / 2, y + 13,
                                   toks[s + k], size=12.5, pal=p, fill=p.ink,
                                   step=st))
            out.append(txt(x0 - 16, y + 13, f"{i+1}", size=11.5, mono=True,
                           pal=p, fill=p.ink3, anchor="end", step=st))
            joined = " ".join(toks[s:s + n])
            out.append(txt(x0 + len(toks) * (cw + gap) + 16, y + 13,
                           f'"{joined}"', size=12.5, mono=True, pal=p,
                           fill=p.ink2, anchor="start", step=st))

        h = y0 + 58 + len(starts) * row_h + 58
        overlap = max(n - stride, 0)
        out.append(txt(x0, h - 30,
                       f"Each window shares {overlap} token(s) with the next. "
                       f"That overlap is what stops a boundary from cutting an "
                       f"idea in half — and what you pay for twice.",
                       size=12.5, pal=p, anchor="start", fill=p.ink2))

        w_total = x0 + len(toks) * (cw + gap) + 260
        return svg(max(width, w_total), h, "".join(out), pal=p,
                   steps=len(starts) if animate else 0,
                   sim_label="window")

    return _block(fig_id, build, cap=cap, note=note, full=full)


def bag_of_words(fig_id, sentence, *, cap="", note="", width=1000, height=400,
                 full=False):
    """A sentence turned into counts, with the order visibly thrown away.

    The name says what it does and the picture usually does not. Here the words
    are lifted out of the sentence and dropped into a bag, and the vector under
    it is the actual count vector — so the loss (word order) is something the
    reader sees happen rather than something they are told about.
    """
    words = [w.strip(".,").lower() for w in sentence.split()]
    vocab = sorted(set(words))
    counts = {v: words.count(v) for v in vocab}

    def build(p):
        out = []
        out.append(txt(60, 44, "The sentence", size=14, weight=600, pal=p,
                       anchor="start", fill=p.ink3))
        x = 60
        for w in words:
            wd = 16 + 8.4 * len(w)
            out.append(rect(x, 60, wd, 32, r=6, pal=p, fill=p.fill,
                            stroke=p.faint))
            out.append(txt(x + wd / 2, 76, w, size=13, pal=p, fill=p.ink))
            x += wd + 7

        out.append(arrow(width / 2, 108, width / 2, 146, pal=p,
                         stroke=p.accent, sw=1.8))
        out.append(txt(width / 2 + 14, 128, "count, and forget the order",
                       size=12, pal=p, fill=p.ink3, anchor="start"))

        out.append(txt(60, 178, "The vector", size=14, weight=600, pal=p,
                       anchor="start", fill=p.ink3))
        cw, gap = 96, 6
        for j, v in enumerate(vocab):
            cx = 60 + j * (cw + gap)
            hot = counts[v] > 1
            out.append(rect(cx, 196, cw, 40, r=5, pal=p,
                            fill=p.accent_fill if hot else p.fill,
                            stroke=p.accent if hot else p.faint,
                            sw=1.6 if hot else 1))
            out.append(txt(cx + cw / 2, 216, str(counts[v]), size=16,
                           weight=600, mono=True, pal=p,
                           fill=p.accent if hot else p.ink))
            out.append(txt(cx + cw / 2, 252, v, size=11.5, pal=p, fill=p.ink3))

        out.append(txt(60, height - 76,
                       f"shape ({len(vocab)},) — one slot per vocabulary word, "
                       f"and this vocabulary has {len(vocab)}.",
                       size=13, mono=True, pal=p, anchor="start", fill=p.ink2))
        out.append(txt(60, height - 48,
                       "Reverse it and you cannot: "
                       + " ".join(f"{v}×{counts[v]}" for v in vocab[:5])
                       + " … has no order left in it.",
                       size=13, pal=p, anchor="start", fill=p.ink2))
        out.append(txt(60, height - 22,
                       "“the cat sat on the mat” and “the mat sat "
                       "on the cat” give the identical vector. That is the "
                       "whole limitation, in one line.",
                       size=13, pal=p, anchor="start", fill=p.warm))
        return svg(max(width, 60 + len(vocab) * (cw + gap) + 60), height,
                   "".join(out), pal=p)

    return _block(fig_id, build, cap=cap, note=note, full=full)
