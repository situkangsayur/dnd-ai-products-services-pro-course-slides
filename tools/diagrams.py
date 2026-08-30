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


# ========================================================== feature-map stacks --

def feature_maps(fig_id, stages, *, cap="", note="", width=1080, height=440,
                 full=False, animate=True, title_gap=False):
    """Feature maps drawn at their real relative size.

    ``stages`` is a list of ``(label, h, w, channels)``. A convolutional stack
    is a story about **shape** -- the map gets smaller while it gets deeper --
    and a row of equal rectangles labelled `50 x 50 x 128` tells that story only
    to somebody who already knows it. Here the slab's height is the spatial
    size and its depth is the channel count, both to scale, so the trade is
    visible: the picture narrows and thickens.

    Used for encoder/decoder stacks especially, where the hourglass shape *is*
    the architecture.
    """
    norm = [(s[0], float(s[1]), float(s[2]), int(s[3])) for s in stages]
    max_sp = max(max(h, w) for _, h, w, _ in norm)
    max_ch = max(c for *_, c in norm)

    def build(p):
        out = []
        n = len(norm)
        pad = 74
        slot = (width - 2 * pad) / n
        mid = height / 2 - 6
        max_h = height * 0.44          # pixels for the largest spatial side
        max_d = 54                     # pixels for the deepest channel count

        for i, (lbl, h, w, c) in enumerate(norm):
            cx = pad + slot * (i + 0.5)
            sh = max_h * (h / max_sp)
            # Depth on a square root: channels run 3 -> 256 and a linear scale
            # makes the first slab a hairline nobody can see.
            dep = 10 + (max_d - 10) * (c / max_ch) ** 0.5
            x, y = cx - dep / 2 - 14, mid - sh / 2
            st = i + 1

            # Back face and the connecting edges, drawn first: an isometric
            # slab reads as a volume, a rectangle reads as an image.
            out.append(rect(x + dep, y - dep * 0.55, 30, sh, r=3, pal=p,
                            fill=p.fill2, stroke=p.faint, sw=1, opacity=0.75,
                            step=st))
            for (ax, ay, bx, by) in (
                    (x, y, x + dep, y - dep * 0.55),
                    (x + 30, y, x + dep + 30, y - dep * 0.55),
                    (x, y + sh, x + dep, y + sh - dep * 0.55),
                    (x + 30, y + sh, x + dep + 30, y + sh - dep * 0.55)):
                out.append(line(ax, ay, bx, by, pal=p, stroke=p.faint, sw=0.9,
                                opacity=0.75, step=st))
            out.append(rect(x, y, 30, sh, r=3, pal=p, fill=p.accent_fill,
                            stroke=p.accent, sw=1.5, step=st))

            out.append(txt(cx, mid + max_h / 2 + 34, lbl, size=12.5,
                           weight=600, pal=p, fill=p.ink, step=st))
            out.append(txt(cx, mid + max_h / 2 + 54,
                           f"{int(h)}×{int(w)}×{c}", size=12, mono=True, pal=p,
                           fill=p.accent, step=st))

            if i < n - 1:
                nx = pad + slot * (i + 1.5)
                out.append(arrow(cx + 34, mid, nx - 38, mid, pal=p,
                                 stroke=p.line, sw=1.4, opacity=0.8,
                                 step=st + 1))

        # A ruler for the two quantities that are trading against each other.
        out.append(txt(30, mid, "spatial", size=11.5, pal=p, fill=p.ink3,
                       anchor="start", italic=True))
        out.append(txt(30, mid + 16, "size ↕", size=11.5, pal=p, fill=p.ink3,
                       anchor="start", italic=True))
        out.append(txt(width - 30, mid, "channels", size=11.5, pal=p,
                       fill=p.ink3, anchor="end", italic=True))
        out.append(txt(width - 30, mid + 16, "= depth", size=11.5, pal=p,
                       fill=p.ink3, anchor="end", italic=True))
        return svg(width, height, "".join(out), pal=p,
                   steps=n if animate else 0, sim_label="stage")

    return _block(fig_id, build, cap=cap, note=note, full=full)


def conv_compute(fig_id, *, image, kernel, cap="", note="", full=False,
                 at=(0, 0), width=1020, height=430):
    """One convolution, computed cell by cell, with the sum written out.

    The operation is nine multiplications and an addition. Said that way it is
    obvious; drawn as a box labelled "Conv2D" it is magic. This puts the kernel
    on the image, highlights the nine cells it covers, and shows the products
    and their total -- so a reader can check the arithmetic and then never have
    to take a convolution on faith again.
    """
    ih, iw = len(image), len(image[0])
    kh, kw = len(kernel), len(kernel[0])
    r0, c0 = at

    def build(p):
        out = []
        cell = 40
        gap = 3
        x0, y0 = 60, 108

        out.append(txt(x0, 62, "input", size=13.5, weight=600, pal=p,
                       anchor="start", fill=p.ink3))
        for i in range(ih):
            for j in range(iw):
                x, y = x0 + j * (cell + gap), y0 + i * (cell + gap)
                hot = r0 <= i < r0 + kh and c0 <= j < c0 + kw
                out.append(rect(x, y, cell, cell, r=4, pal=p,
                                fill=p.accent_fill if hot else p.fill,
                                stroke=p.accent if hot else p.faint,
                                sw=1.6 if hot else 1,
                                step=1 if hot else 0))
                out.append(txt(x + cell / 2, y + cell / 2, fmt(image[i][j]),
                               size=12.5, mono=True, pal=p,
                               fill=p.accent if hot else p.ink2))

        kx = x0 + iw * (cell + gap) + 68
        out.append(txt(kx, 62, "kernel", size=13.5, weight=600, pal=p,
                       anchor="start", fill=p.ink3))
        for i in range(kh):
            for j in range(kw):
                x, y = kx + j * (cell + gap), y0 + i * (cell + gap)
                out.append(rect(x, y, cell, cell, r=4, pal=p, fill=p.warm_fill,
                                stroke=p.warm, sw=1.4, step=2))
                out.append(txt(x + cell / 2, y + cell / 2, fmt(kernel[i][j]),
                               size=12.5, mono=True, pal=p, fill=p.warm,
                               step=2))

        # the arithmetic
        terms, total = [], 0.0
        for i in range(kh):
            for j in range(kw):
                a, b = image[r0 + i][c0 + j], kernel[i][j]
                total += a * b
                if b:
                    terms.append(f"{fmt(a)}×{fmt(b)}")
        sx = x0
        sy = y0 + ih * (cell + gap) + 46
        out.append(txt(sx, sy, " + ".join(terms) + f"  =  {fmt(total)}",
                       size=14, mono=True, pal=p, anchor="start", fill=p.ink,
                       step=3))
        out.append(txt(sx, sy + 26,
                       "Nine multiplications and an addition. That is the whole "
                       "operation; everything else is where you slide it to next.",
                       size=12.5, pal=p, anchor="start", fill=p.ink2, step=4))

        ox = kx + kw * (cell + gap) + 74
        out.append(txt(ox, 62, "output", size=13.5, weight=600, pal=p,
                       anchor="start", fill=p.ink3))
        out.append(rect(ox, y0, cell + 16, cell + 16, r=5, pal=p,
                        fill=p.accent_fill, stroke=p.accent, sw=1.8, step=3))
        out.append(txt(ox + (cell + 16) / 2, y0 + (cell + 16) / 2, fmt(total),
                       size=16, weight=600, mono=True, pal=p, fill=p.ink,
                       step=3))
        out.append(txt(ox, y0 + cell + 44, "one cell of the", size=11.5, pal=p,
                       anchor="start", fill=p.ink3, step=3))
        out.append(txt(ox, y0 + cell + 62, "feature map", size=11.5, pal=p,
                       anchor="start", fill=p.ink3, step=3))
        return svg(width, height, "".join(out), pal=p, steps=4,
                   sim_label="stage")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ============================================================= forward pass --

def forward_pass(fig_id, *, inputs, layers, cap="", note="", width=1120,
                 height=520, full=False, seed=2, labels=None, out_labels=None,
                 softmax=True):
    """A network computing, with the numbers it actually computes.

    This is the figure the rest of the deck kept gesturing at. ``layers`` is a
    list of widths, e.g. ``[5, 3]`` for one hidden layer of five units and an
    output of three. Weights are drawn from a seeded generator, so the picture
    is reproducible and the arithmetic in it is real: every activation shown
    was computed from the inputs and weights on screen.

    What is drawn, and why each part is there:

    * **Edges carry their weight.** Colour is the sign -- warm for positive,
      rose for negative -- and thickness is the magnitude. A network is a
      picture of numbers, and a diagram in one uniform grey hides the only
      thing that varies.
    * **Signals move.** A dot travels each edge, so the direction of a forward
      pass is something you watch rather than infer from arrowheads. Pure SMIL,
      so it works in any browser with no script.
    * **Neurons hold their activation**, printed and shown as a fill level. A
      relu unit that came out at zero is visibly empty, which is the fastest
      way to see what "dead unit" means.
    * **It steps.** Input, then the first set of edges, then the activations
      they produce, and so on -- the order the arithmetic happens in.
    """
    import math
    import random

    rng = random.Random(seed)
    sizes = [len(inputs)] + list(layers)
    W, B = [], []
    for a, b in zip(sizes, sizes[1:]):
        W.append([[round(rng.uniform(-1.2, 1.2), 2) for _ in range(a)]
                  for _ in range(b)])
        B.append([round(rng.uniform(-0.4, 0.4), 2) for _ in range(b)])

    acts = [list(inputs)]
    for li, (w, bs) in enumerate(zip(W, B)):
        prev = acts[-1]
        last = li == len(W) - 1
        z = [sum(wi * x for wi, x in zip(row, prev)) + bb
             for row, bb in zip(w, bs)]
        if last and softmax:
            m = max(z)
            e = [math.exp(v - m) for v in z]
            tot = sum(e)
            acts.append([v / tot for v in e])
        else:
            acts.append([max(0.0, v) for v in z])

    def build(p):
        out = []
        pad_x, top, bot = 130, 168, 118
        n_layers = len(sizes)
        step_x = (width - 2 * pad_x) / max(n_layers - 1, 1)
        xs = [pad_x + i * step_x for i in range(n_layers)]
        span = height - top - bot
        R = 21

        ys = []
        for k in sizes:
            ys.append([top + span * (j + 0.5) / k for j in range(k)])

        amax = max(max(abs(v) for v in a) for a in acts) or 1.0

        # --- edges, per layer -------------------------------------------------
        for li in range(n_layers - 1):
            st = li * 2 + 2
            for j, y1 in enumerate(ys[li + 1]):
                for i, y0 in enumerate(ys[li]):
                    wgt = W[li][j][i]
                    x0, x1 = xs[li] + R, xs[li + 1] - R
                    col = p.warm if wgt >= 0 else p.bad
                    out.append(line(x0, y0, x1, y1, pal=p, stroke=col,
                                    sw=0.5 + 2.4 * abs(wgt) / 1.2,
                                    opacity=0.22 + 0.5 * abs(wgt) / 1.2,
                                    step=st))
                    # A signal travelling the edge. Duration varies a little
                    # per edge so the dots do not march in lockstep, which
                    # reads as a machine rather than a flow.
                    if p.name == "web":
                        dur = 1.5 + ((i * 7 + j * 13) % 9) * 0.11
                        out.append(
                            f'<circle r="3" fill="{col}" opacity="0.9"'
                            f' data-step="{st}">'
                            f'<animateMotion dur="{dur:.2f}s" repeatCount="indefinite"'
                            f' path="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}"/>'
                            f'</circle>')

        # --- units ------------------------------------------------------------
        for li, (k, yy) in enumerate(zip(sizes, ys)):
            st = li * 2 + 1
            name = (labels[li] if labels and li < len(labels)
                    else ("input" if li == 0
                          else "output" if li == n_layers - 1
                          else f"hidden {li}"))
            act_name = ("" if li == 0
                        else ("softmax" if (li == n_layers - 1 and softmax)
                              else "relu"))
            out.append(txt(xs[li], top - 56, name, size=15, weight=600, pal=p,
                           fill=p.ink, step=st))
            if act_name:
                out.append(txt(xs[li], top - 34, act_name, size=12, mono=True,
                               pal=p, fill=p.ink3, step=st))

            for j, y in enumerate(yy):
                v = acts[li][j]
                frac = min(1.0, abs(v) / amax)
                # Fill level = how strongly this unit fired. An empty circle is
                # a unit that output zero, and that is worth seeing.
                out.append(circle(xs[li], y, R, pal=p, fill=p.fill,
                                  stroke=p.line, sw=1.4, step=st))
                if frac > 0.02:
                    out.append(circle(xs[li], y, R * (0.35 + 0.65 * frac),
                                      pal=p, fill=p.accent_fill,
                                      stroke=p.accent, sw=1.6, step=st))
                out.append(txt(xs[li], y, fmt(v, 2), size=11.5, mono=True,
                               pal=p, fill=p.ink, step=st))

            if li == n_layers - 1 and out_labels:
                for j, y in enumerate(yy):
                    if j < len(out_labels):
                        out.append(txt(xs[li] + R + 14, y, out_labels[j],
                                       size=12.5, pal=p, fill=p.ink2,
                                       anchor="start", step=st))

        # --- the sum for one unit, written out --------------------------------
        if n_layers > 1 and sizes[1] > 0:
            terms = " + ".join(f"{fmt(x, 2)}·{fmt(w, 2)}"
                               for x, w in zip(acts[0], W[0][0]))
            z0 = sum(x * w for x, w in zip(acts[0], W[0][0])) + B[0][0]
            out.append(txt(width / 2, height - 62,
                           f"top hidden unit:  z = {terms} + {fmt(B[0][0], 2)}"
                           f" = {fmt(z0, 3)}",
                           size=13, mono=True, pal=p, fill=p.ink2, step=2))
            out.append(txt(width / 2, height - 40,
                           f"relu(z) = max(0, {fmt(z0, 3)}) = "
                           f"{fmt(max(0.0, z0), 3)}",
                           size=13, mono=True, pal=p, fill=p.accent, step=3))

        # Direction, said out loud. "Which way does it go" is the first question
        # anyone asks of a network diagram, and arrowheads on 20 crossing edges
        # do not answer it.
        band_y = top - 92
        out.append(line(xs[0], band_y, xs[-1], band_y, pal=p,
                        stroke=p.faint, sw=1, dash="5 6"))
        out.append(arrow(width / 2 - 62, band_y, width / 2 + 62, band_y, pal=p,
                         stroke=p.accent, sw=1.6))
        out.append(txt(xs[0], band_y - 17, "INPUT enters here", size=12,
                       weight=600, pal=p, fill=p.accent))
        out.append(txt(xs[-1], band_y - 17, "OUTPUT leaves here",
                       size=12, weight=600, pal=p, fill=p.accent))
        out.append(txt(width / 2, band_y - 17, "forward pass", size=11.5,
                       pal=p, fill=p.ink3, italic=True))

        out.append(txt(width / 2, height - 16,
                       "Warm edges are positive weights, rose are negative; "
                       "thickness is magnitude. A hollow neuron output zero.",
                       size=12, pal=p, fill=p.ink3))
        return svg(width, height, "".join(out), pal=p,
                   steps=(n_layers - 1) * 2 + 1, sim_label="stage")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================================== attention: Q, K, V, in full --

def attention_qkv(fig_id, tokens, *, focus=2, cap="", note="", width=1180,
                  height=620, full=False, seed=11, d=4):
    """Self-attention computed on real tokens, one query at a time.

    The question this answers is the one nobody's box diagram answers: *what
    actually happens to my sentence inside an attention head?* So it walks the
    arithmetic for a single query token, with real vectors:

      1. every token becomes an embedding;
      2. three learned matrices turn each embedding into a **query**, a **key**
         and a **value**;
      3. the focus token's query is dotted against **every** key, giving a raw
         score per token;
      4. softmax turns the scores into weights that sum to 1;
      5. the output is the value vectors, mixed in those proportions.

    Step 5 is the punchline and the reason attention is worth the trouble: the
    new vector for "it" is literally built out of the other words in the
    sentence, in proportions the model chose.
    """
    import math
    import random

    rng = random.Random(seed)
    n = len(tokens)
    emb = [[round(rng.uniform(-1, 1), 2) for _ in range(d)] for _ in range(n)]
    Wq = [[round(rng.uniform(-0.9, 0.9), 2) for _ in range(d)] for _ in range(d)]
    Wk = [[round(rng.uniform(-0.9, 0.9), 2) for _ in range(d)] for _ in range(d)]
    Wv = [[round(rng.uniform(-0.9, 0.9), 2) for _ in range(d)] for _ in range(d)]

    def mat(v, M):
        return [round(sum(v[k] * M[r][k] for k in range(d)), 2) for r in range(d)]

    Q = [mat(e, Wq) for e in emb]
    K = [mat(e, Wk) for e in emb]
    V = [mat(e, Wv) for e in emb]

    q = Q[focus]
    raw = [sum(a * b for a, b in zip(q, k)) / math.sqrt(d) for k in K]
    m = max(raw)
    ex = [math.exp(r - m) for r in raw]
    tot = sum(ex)
    att = [e / tot for e in ex]
    outv = [round(sum(att[i] * V[i][j] for i in range(n)), 3) for j in range(d)]

    def build(p):
        out = []
        # The row labels on the left are the widest thing in the figure and
        # they set the margin. Sizing the columns first and discovering that
        # afterwards is how "= Wq · x" ends up half off the page.
        left = 176
        col_w = (width - left - 40) / n
        x_of = lambda i: left + col_w * (i + 0.5)
        y_tok, y_qkv, y_score, y_bar, y_out = 76, 150, 330, 386, 512

        # --- tokens -----------------------------------------------------------
        for i, t in enumerate(tokens):
            hot = i == focus
            x = x_of(i)
            out.append(rect(x - col_w / 2 + 8, y_tok - 18, col_w - 16, 36, r=7,
                            pal=p, fill=p.accent_fill if hot else p.fill,
                            stroke=p.accent if hot else p.faint,
                            sw=1.8 if hot else 1, step=1))
            out.append(txt(x, y_tok, t, size=14,
                           weight=600 if hot else 400, pal=p,
                           fill=p.accent if hot else p.ink, step=1))
        out.append(txt(left - 22, y_tok, "tokens", size=12.5, pal=p, fill=p.ink3,
                       anchor="end", step=1))

        # --- q / k / v --------------------------------------------------------
        rows = (("q", Q, p.accent), ("k", K, p.warm), ("v", V, p.good))
        for r, (nm, M, col) in enumerate(rows):
            yy = y_qkv + r * 46
            out.append(txt(left - 22, yy, f"{nm} = W{nm} · x", size=12.5, mono=True,
                           pal=p, fill=col, anchor="end", step=2))
            for i in range(n):
                x = x_of(i)
                hot = (nm == "q" and i == focus)
                out.append(rect(x - col_w / 2 + 8, yy - 15, col_w - 16, 30,
                                r=5, pal=p,
                                fill=p.accent_fill if hot else p.fill,
                                stroke=col if hot else p.faint,
                                sw=1.6 if hot else 0.9, step=2))
                out.append(txt(x, yy, "[" + " ".join(fmt(z, 1) for z in M[i])
                               + "]", size=10.5, mono=True, pal=p,
                               fill=p.ink2, step=2))

        # --- scores -----------------------------------------------------------
        qx = x_of(focus)
        out.append(txt(left - 22, y_score,
                       f"q(“{tokens[focus]}”) · k", size=12.5,
                       mono=True, pal=p, fill=p.ink3, anchor="end", step=3))
        for i in range(n):
            x = x_of(i)
            out.append(arrow(qx, y_qkv + 15, x, y_score - 20, pal=p,
                             stroke=p.accent, sw=1.1, opacity=0.5, step=3))
            out.append(txt(x, y_score, fmt(raw[i], 2), size=12.5, mono=True,
                           pal=p, fill=p.ink, step=3))

        # --- softmax weights, as bars ----------------------------------------
        out.append(txt(left - 22, y_bar + 22, "softmax", size=12.5, mono=True, pal=p,
                       fill=p.ink3, anchor="end", step=4))
        bar_h = 74
        for i in range(n):
            x = x_of(i)
            h = max(2.0, bar_h * att[i])
            out.append(rect(x - 26, y_bar + 46 - h, 52, h, r=4, pal=p,
                            fill=p.accent_fill, stroke=p.accent, sw=1.5,
                            step=4))
            out.append(txt(x, y_bar + 60, f"{att[i]*100:.0f}%", size=12,
                           weight=600, mono=True, pal=p, fill=p.accent,
                           step=4))
        out.append(txt(width - 60, y_bar + 60, "sums to 100%", size=11.5,
                       pal=p, fill=p.ink3, anchor="end", step=4))

        # --- the mix ----------------------------------------------------------
        out.append(txt(left - 22, y_out, "output", size=12.5, mono=True, pal=p,
                       fill=p.good, anchor="end", step=5))
        for i in range(n):
            out.append(arrow(x_of(i), y_bar + 72, width / 2, y_out - 22, pal=p,
                             stroke=p.good, sw=0.6 + 2.6 * att[i],
                             opacity=0.30 + 0.6 * att[i], step=5))
        out.append(rect(width / 2 - 128, y_out - 18, 256, 36, r=8, pal=p,
                        fill=p.accent_fill, stroke=p.accent, sw=1.8, step=5))
        out.append(txt(width / 2, y_out, "[" + "  ".join(fmt(z, 2) for z in outv)
                       + "]", size=12.5, mono=True, pal=p, fill=p.ink, step=5))
        mixed = " + ".join(f"{att[i]*100:.0f}%·v({tokens[i]})"
                           for i in sorted(range(n), key=lambda i: -att[i])[:3])
        out.append(txt(width / 2, y_out + 34,
                       f"new vector for “{tokens[focus]}” = {mixed} + …",
                       size=12.5, pal=p, fill=p.ink2, step=5))
        out.append(txt(width / 2, y_out + 58,
                       "The word's new meaning is built out of the other words, "
                       "in proportions the model chose.",
                       size=12.5, pal=p, fill=p.accent, step=5))
        return svg(width, height, "".join(out), pal=p, steps=5,
                   sim_label="stage")

    return _block(fig_id, build, cap=cap, note=note, full=full)


def dropout_net(fig_id, *, rate=0.5, cap="", note="", width=1060, height=470,
                full=False, seed=5, sizes=(5, 6, 6, 3)):
    """Dropout, applied to a network you can see it happening to.

    Two passes side by side: the same network, the same weights, different
    units switched off. A row of boxes describing dropout is accurate and
    forgettable; two networks with different holes in them makes the point in
    one look -- and makes the *reason* visible too, because the surviving paths
    are different each time, so no single unit can be relied on.
    """
    import random

    rng = random.Random(seed)
    keeps = []
    for pass_i in range(2):
        pk = []
        for li, k in enumerate(sizes):
            if li == 0 or li == len(sizes) - 1:
                pk.append([True] * k)          # never drop input or output
            else:
                row = [rng.random() > rate for _ in range(k)]
                if not any(row):
                    row[rng.randrange(k)] = True
                pk.append(row)
        keeps.append(pk)

    def build(p):
        out = []
        half = width / 2
        R = 12
        top, bot = 106, 92
        span = height - top - bot

        for pass_i in range(2):
            ox = pass_i * half
            keep = keeps[pass_i]
            xs = [ox + 86 + (half - 172) * i / (len(sizes) - 1)
                  for i in range(len(sizes))]
            ys = [[top + span * (j + 0.5) / k for j in range(k)]
                  for k in sizes]
            st = pass_i + 1

            out.append(txt(ox + half / 2, 44,
                           f"Training pass {pass_i + 1}", size=15, weight=600,
                           pal=p, fill=p.ink, step=st))
            out.append(txt(ox + half / 2, 66,
                           f"rate = {rate} — half the hidden units are off",
                           size=12, pal=p, fill=p.ink3, step=st))

            for li in range(len(sizes) - 1):
                for i, y0 in enumerate(ys[li]):
                    for j, y1 in enumerate(ys[li + 1]):
                        live = keep[li][i] and keep[li + 1][j]
                        out.append(line(xs[li] + R, y0, xs[li + 1] - R, y1,
                                        pal=p,
                                        stroke=p.line if live else p.faint,
                                        sw=0.8 if live else 0.5,
                                        opacity=0.5 if live else 0.10,
                                        step=st))
            for li, k in enumerate(sizes):
                for j, y in enumerate(ys[li]):
                    on = keep[li][j]
                    out.append(circle(xs[li], y, R, pal=p,
                                      fill=p.accent_fill if on else "none",
                                      stroke=p.accent if on else p.faint,
                                      sw=1.5 if on else 1,
                                      opacity=1 if on else 0.35, step=st))
                    if not on:
                        # A full cross, not a slash: at projector distance a
                        # single stroke reads as an edge passing behind the
                        # unit rather than as the unit being off.
                        out.append(line(xs[li] - 7, y - 7, xs[li] + 7, y + 7,
                                        pal=p, stroke=p.bad, sw=1.6,
                                        opacity=0.9, step=st))
                        out.append(line(xs[li] + 7, y - 7, xs[li] - 7, y + 7,
                                        pal=p, stroke=p.bad, sw=1.6,
                                        opacity=0.9, step=st))

        out.append(line(half, 88, half, height - 76, pal=p, stroke=p.faint,
                        sw=1, dash="4 6"))

        out.append(txt(width / 2, height - 52,
                       "Same network, same weights — different units switched "
                       "off each pass.", size=13.5, pal=p, fill=p.ink2))
        out.append(txt(width / 2, height - 28,
                       "So no unit can rely on any particular other one being "
                       "there. That is the whole mechanism.",
                       size=13, pal=p, fill=p.accent))
        out.append(txt(width / 2, height - 6,
                       "At test time nothing is dropped; the activations were "
                       "already scaled up by 1/(1−rate) during training.",
                       size=12, pal=p, fill=p.ink3))
        return svg(width, height, "".join(out), pal=p, steps=2,
                   sim_label="pass")

    return _block(fig_id, build, cap=cap, note=note, full=full)
# Appended to tools/diagrams.py after the figure rebuild finishes.


def pixel_mask(fig_id, *, cap="", note="", width=1040, height=440, full=False):
    """An image and its per-pixel label, side by side, at pixel resolution.

    Segmentation is the one task where **the label is the same shape as the
    input**, and that sentence lands only once somebody has seen the two grids
    next to each other. Four cards with emoji on them describe where
    segmentation is used; this shows what it *is*.

    The scene is deliberately tiny -- 12x9 -- so every cell is visible and the
    class of every pixel can be pointed at.
    """
    W, H = 12, 9
    # 0 sky, 1 road, 2 car, 3 person
    scene = [[0] * W for _ in range(H)]
    for y in range(6, H):
        for x in range(W):
            scene[y][x] = 1
    for y in range(4, 7):
        for x in range(2, 6):
            scene[y][x] = 2
    for y in range(3, 7):
        for x in range(8, 10):
            scene[y][x] = 3

    def build(p):
        names = ["sky", "road", "car", "person"]
        cols = [p.fill2, p.ink3, p.accent, p.warm]
        out = []
        cell = 26
        gap = 2
        gw = W * (cell + gap)

        def grid(x0, y0, painter, step):
            g = []
            for y in range(H):
                for x in range(W):
                    cx, cy = x0 + x * (cell + gap), y0 + y * (cell + gap)
                    fill, label = painter(x, y)
                    g.append(rect(cx, cy, cell, cell, r=2, pal=p, fill=fill,
                                  stroke=p.faint, sw=0.5, step=step))
                    if label is not None:
                        g.append(txt(cx + cell / 2, cy + cell / 2, str(label),
                                     size=10, mono=True, pal=p, fill=p.ink,
                                     step=step))
            return "".join(g)

        left, right, top = 60, 60 + gw + 120, 96
        out.append(txt(left, 56, "the input image", size=14.5, weight=600,
                       pal=p, anchor="start", fill=p.ink, step=1))
        out.append(grid(left, top,
                        lambda x, y: (cols[scene[y][x]], None), 1))
        out.append(txt(left, top + H * (cell + gap) + 26,
                       f"shape ({H}, {W}, 3) — three colour channels",
                       size=12, mono=True, pal=p, anchor="start", fill=p.accent,
                       step=1))

        out.append(txt(right, 56, "the label", size=14.5, weight=600, pal=p,
                       anchor="start", fill=p.ink, step=2))
        out.append(grid(right, top,
                        lambda x, y: (cols[scene[y][x]], scene[y][x]), 2))
        out.append(txt(right, top + H * (cell + gap) + 26,
                       f"shape ({H}, {W}, 1) — one class id per pixel",
                       size=12, mono=True, pal=p, anchor="start", fill=p.accent,
                       step=2))

        out.append(arrow(left + gw + 24, top + H * (cell + gap) / 2,
                         right - 24, top + H * (cell + gap) / 2,
                         pal=p, stroke=p.line, sw=1.6, step=2))

        lx = left
        ly = height - 52
        for i, (nm, c) in enumerate(zip(names, cols)):
            x = lx + i * 150
            out.append(rect(x, ly - 11, 22, 22, r=4, pal=p, fill=c,
                            stroke=p.faint, sw=0.8, step=3))
            out.append(txt(x + 30, ly, f"{i} · {nm}", size=12.5, pal=p,
                           anchor="start", fill=p.ink2, step=3))

        out.append(txt(width / 2, height - 16,
                       "Classification gives one label per image. Segmentation "
                       "gives one label per pixel — the output is the same size "
                       "as the input.",
                       size=13, pal=p, fill=p.accent, step=3))
        return svg(width, height, "".join(out), pal=p, steps=3,
                   sim_label="stage")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ==================================================== positional encoding --

def positional_encoding(fig_id, *, positions=12, dims=16, cap="", note="",
                        width=1120, height=520, full=False):
    """The sinusoids, and the pattern they make. Both, because neither alone lands.

    "Add a sine wave of a different frequency per dimension" is a sentence that
    passes and teaches nothing. Two pictures do the work:

    * **Left** — three of the actual waves, at three of the actual frequencies.
      The first dimension turns over every couple of positions; the last barely
      moves across the whole sentence. That spread is the entire trick.
    * **Right** — every dimension for every position as a heat map, which is
      the picture people remember, and which only makes sense once you have
      seen where the stripes come from.

    Values are computed, not drawn to look right: this is the formula from
    *Attention Is All You Need*, and the figure is what it produces.
    """
    import math

    def pe(pos, i):
        k = i // 2
        angle = pos / (10000 ** (2 * k / dims))
        return math.sin(angle) if i % 2 == 0 else math.cos(angle)

    grid = [[pe(p, i) for i in range(dims)] for p in range(positions)]

    def build(p):
        out = []
        # ---- left: three waves ------------------------------------------
        lx, lw = 74, 460
        ly, lh = 108, 220
        out.append(txt(lx, 56, "the waves themselves", size=14.5, weight=600,
                       pal=p, anchor="start", fill=p.ink))
        out.append(line(lx, ly + lh / 2, lx + lw, ly + lh / 2, pal=p,
                        stroke=p.faint, sw=1, dash="3 4"))

        picks = [(0, p.accent, "dim 0 — fastest"),
                 (6, p.warm, "dim 6"),
                 (dims - 2, p.good, f"dim {dims - 2} — slowest")]
        # The waves are plotted over a longer stretch than the heat map shows.
        # Over twelve positions the middle frequency barely bends, and a wave
        # drawn as a straight sloping line looks like a mistake rather than
        # like a slow wave -- which is the opposite of the point.
        wave_span = positions * 8
        for k, (d, col, lab) in enumerate(picks):
            pts = []
            for s in range(241):
                pos = s * wave_span / 240
                v = pe(pos, d)
                pts.append((lx + lw * s / 240, ly + lh / 2 - v * (lh / 2 - 12)))
            dpath = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                             for i, (x, y) in enumerate(pts))
            out.append(f'<path d="{dpath}" fill="none" stroke="{col}" '
                       f'stroke-width="2" opacity="0.95" '
                       f'data-step="{k + 1}"/>')
            out.append(txt(lx + 6, ly + lh + 44 + k * 18, f"— {lab}", size=12,
                           pal=p, fill=col, anchor="start", step=k + 1))

        out.append(txt(lx + lw, ly + lh + 22, "position →", size=12, pal=p,
                       anchor="end", fill=p.ink3))
        out.append(txt(lx - 10, ly + 8, "+1", size=11, mono=True, pal=p,
                       fill=p.ink3, anchor="end"))
        out.append(txt(lx - 10, ly + lh - 8, "−1", size=11, mono=True, pal=p,
                       fill=p.ink3, anchor="end"))

        # ---- right: the heat map ----------------------------------------
        gx, gy = 640, 108
        cw, ch = 26, 20
        out.append(txt(gx, 56, "every dimension, every position", size=14.5,
                       weight=600, pal=p, anchor="start", fill=p.ink))
        for r in range(positions):
            for c in range(dims):
                v = grid[r][c]
                # +1 warm, -1 accent, 0 nearly invisible: the sign is the
                # information, so encode it as hue rather than as brightness.
                col = p.warm if v >= 0 else p.accent
                out.append(rect(gx + c * cw, gy + r * ch, cw - 2, ch - 2, r=2,
                                pal=p, fill=col, stroke="none", sw=0,
                                opacity=0.12 + 0.78 * abs(v), step=4))
        out.append(txt(gx + dims * cw / 2, gy + positions * ch + 22,
                       "dimension →", size=12, pal=p, fill=p.ink3, step=4))
        out.append(txt(gx - 12, gy + positions * ch / 2, "position", size=12,
                       pal=p, fill=p.ink3, anchor="end", step=4))

        out.append(txt(width / 2, height - 54,
                       "Each dimension is a wave of a different frequency, so "
                       "every position gets a different combination.",
                       size=13.5, pal=p, fill=p.ink2, step=5))
        out.append(txt(width / 2, height - 30,
                       "Nothing is learned here, and nothing needs to be — the "
                       "values come from a formula, so position 5000 works even "
                       "if training never saw one.",
                       size=13, pal=p, fill=p.accent, step=5))
        return svg(width, height, "".join(out), pal=p, steps=5,
                   sim_label="stage")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# =============================================== depth against width, drawn --

def depth_vs_width(fig_id, *, broad=(64, 512, 10), deep=(64, 96, 96, 96, 96, 10),
                   cap="", note="", width=1100, height=500, full=False):
    """Two networks with a similar parameter budget, spent differently.

    The claim — *deep and narrow beats broad and shallow* — is about the number
    of **successive** transformations, and a pair of cards cannot show that
    because the thing being compared is a shape. Drawn side by side with the
    parameter counts computed underneath, the argument makes itself: the broad
    network has one place where representation can change, the deep one has
    four, and they cost about the same.
    """
    def params(sizes):
        return sum(a * b + b for a, b in zip(sizes, sizes[1:]))

    def build(p):
        out = []
        half = width / 2
        top, bot = 118, 128
        span = height - top - bot
        R = 9

        for k, (sizes, title, blurb) in enumerate((
                (broad, "Broad and shallow",
                 "one hidden layer — one place where the representation changes"),
                (deep, "Deep and narrow",
                 f"{len(deep) - 2} hidden layers — a hierarchy, each built on the last"))):
            ox = k * half
            n = len(sizes)
            xs = [ox + 78 + (half - 156) * i / (n - 1) for i in range(n)]
            drawn = [min(s, 7) for s in sizes]
            ys = [[top + span * (j + 0.5) / d for j in range(d)] for d in drawn]
            st = k + 1

            out.append(txt(ox + half / 2, 46, title, size=16, weight=600, pal=p,
                           fill=p.ink, step=st))
            out.append(txt(ox + half / 2, 70, blurb, size=12, pal=p,
                           fill=p.ink3, step=st))

            for i in range(n - 1):
                for y0 in ys[i]:
                    for y1 in ys[i + 1]:
                        out.append(line(xs[i] + R, y0, xs[i + 1] - R, y1,
                                        pal=p, stroke=p.faint, sw=0.55,
                                        opacity=0.5, step=st))
            for i, (d, yy) in enumerate(zip(drawn, ys)):
                hidden = 0 < i < n - 1
                for y in yy:
                    out.append(circle(xs[i], y, R, pal=p,
                                      fill=p.accent_fill if hidden else p.fill,
                                      stroke=p.accent if hidden else p.line,
                                      sw=1.3, step=st))
                if sizes[i] > d:
                    mid = (yy[len(yy) // 2 - 1] + yy[len(yy) // 2]) / 2
                    for off in (-7, 0, 7):
                        out.append(circle(xs[i], mid + off, 1.6, pal=p,
                                          fill=p.ink3, stroke="none", sw=0,
                                          step=st))
                out.append(txt(xs[i], height - bot + 26, str(sizes[i]),
                               size=12, mono=True, pal=p, fill=p.ink2, step=st))

            # The point of the figure: the same budget, spent differently.
            out.append(txt(ox + half / 2, height - bot + 58,
                           f"{params(sizes):,} parameters".replace(",", " "),
                           size=15, weight=600, mono=True, pal=p, fill=p.accent,
                           step=st))
            levels = len(sizes) - 2
            out.append(txt(ox + half / 2, height - bot + 82,
                           f"{levels} level{'s' if levels != 1 else ''} of "
                           f"representation", size=12.5, pal=p,
                           fill=p.warm if levels > 1 else p.ink3, step=st))

        out.append(line(half, 36, half, height - 40, pal=p, stroke=p.faint,
                        sw=1, dash="4 6"))
        out.append(txt(width / 2, height - 14,
                       "Roughly the same cost. The one on the right can build a "
                       "representation on top of a representation, four times over.",
                       size=13, pal=p, fill=p.ink2, step=2))
        return svg(width, height, "".join(out), pal=p, steps=2, sim_label="net")

    return _block(fig_id, build, cap=cap, note=note, full=full)
