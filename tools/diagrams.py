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
from svgkit import PALETTES, arrow, circle, fmt, line, path, rect, svg, txt


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
                        # Same step as the layer it feeds, or the fan is on
                        # screen before the units at either end of it are.
                        out.append(line(xs[li - 1] + r_prev, y0,
                                        xs[li] - r_here, ys_here[ui],
                                        stroke=p.accent, sw=1.5, pal=p,
                                        opacity=0.95, step=li + 1))

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
                                      fill=p.ink3, stroke="none", sw=0,
                                      step=i + 1))

            out.append(txt(xs[i], top - 44, lbl, size=15, weight=600, pal=p,
                           fill=p.ink))
            out.append(txt(xs[i], top - 24,
                           sub or ("n = %s" % f"{n:,}".replace(",", " ")),
                           size=12.5, pal=p, fill=p.ink3, mono=not sub))
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
        out.append(txt(width / 2, height - 18,
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

        out.append(txt(width / 2, height - 18,
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


# ================================================ backpropagation, computed --

def backprop(fig_id, *, x=2.0, w=1.5, b=-1.2, target=0.5, cap="", note="",
             width=1140, height=520, full=False):
    """One tiny graph, forward then backward, with both sets of numbers.

    Backpropagation is usually drawn as a row of boxes with dashed arrows
    labelled ``d loss / d y``, which restates the chain rule without ever
    applying it. Here the forward pass carries real values and the backward
    pass carries real gradients, computed from them — so the sentence
    *"multiply the local derivatives along the path"* becomes something you can
    check with a calculator.

    The graph is ``loss = (relu(w·x + b) − target)²``, small enough that every
    number fits and every derivative is one line of school calculus.

    The default values keep the relu **active**. That matters: pick them so the
    unit is off and every gradient on the slide is zero, which is a real and
    important phenomenon and a hopeless first example — the reader sees a row of
    zeros and learns nothing about the chain. Show the chain working first, then
    turn one number negative and watch it die.
    """
    x1 = w * x                 # multiply
    x2 = x1 + b                # add
    y = max(0.0, x2)           # relu
    loss = (y - target) ** 2   # squared error

    # Backward, each factor local to its own node.
    dloss_dy = 2 * (y - target)
    dy_dx2 = 1.0 if x2 > 0 else 0.0
    dx2_dx1 = 1.0
    dx1_dw = x
    dloss_dx2 = dloss_dy * dy_dx2
    dloss_dx1 = dloss_dx2 * dx2_dx1
    dloss_dw = dloss_dx1 * dx1_dw

    def build(p):
        out = []
        nodes = [
            ("w", f"{fmt(w)}", "parameter", None),
            ("x1 = w·x", fmt(x1, 3), "multiply", f"∂x1/∂w = x = {fmt(x)}"),
            ("x2 = x1 + b", fmt(x2, 3), "add", "∂x2/∂x1 = 1"),
            ("y = relu(x2)", fmt(y, 3), "relu",
             f"∂y/∂x2 = {fmt(dy_dx2)}"),
            ("loss = (y−t)²", fmt(loss, 3), "squared error",
             f"∂loss/∂y = 2(y−t) = {fmt(dloss_dy, 3)}"),
        ]
        n = len(nodes)
        pad = 96
        step = (width - 2 * pad) / (n - 1)
        xs = [pad + i * step for i in range(n)]
        fy, by = 168, 336
        bw, bh = 150, 62

        out.append(txt(pad - 30, fy - bh, "forward →", size=13, weight=600,
                       pal=p, fill=p.accent, anchor="start"))
        out.append(txt(width - pad + 30, by + 58, "← backward", size=13,
                       weight=600, pal=p, fill=p.warm, anchor="end"))

        for i, (label, val, kind, deriv) in enumerate(nodes):
            cx = xs[i]
            out.append(rect(cx - bw / 2, fy - bh / 2, bw, bh, r=8, pal=p,
                            fill=p.accent_fill, stroke=p.accent, sw=1.6,
                            step=i + 1))
            out.append(txt(cx, fy - 11, label, size=13, mono=True, pal=p,
                           fill=p.ink, step=i + 1))
            out.append(txt(cx, fy + 12, val, size=15, weight=600, mono=True,
                           pal=p, fill=p.accent, step=i + 1))
            out.append(txt(cx, fy - bh / 2 - 14, kind, size=11.5, pal=p,
                           fill=p.ink3, step=i + 1))
            if i < n - 1:
                out.append(arrow(cx + bw / 2 + 4, fy, xs[i + 1] - bw / 2 - 4, fy,
                                 pal=p, stroke=p.accent, sw=1.6, step=i + 2))

        # ---- backward: one local derivative per hop, then the product -------
        grads = [(dloss_dw, "∂loss/∂w"), (dloss_dx1, "∂loss/∂x1"),
                 (dloss_dx2, "∂loss/∂x2"), (dloss_dy, "∂loss/∂y"), (1.0, "1")]
        for i in range(n - 1, 0, -1):
            cx = xs[i]
            st = n + (n - i)
            deriv = nodes[i][3]
            if deriv:
                mx = (xs[i] + xs[i - 1]) / 2
                out.append(arrow(cx - bw / 2 - 4, by, xs[i - 1] + bw / 2 + 4, by,
                                 pal=p, stroke=p.warm, sw=1.6, step=st))
                out.append(rect(mx - 84, by - 16, 168, 32, r=8, pal=p,
                                fill=p.warm_fill, stroke=p.warm, sw=1.2,
                                step=st))
                out.append(txt(mx, by, deriv, size=11.5, mono=True, pal=p,
                               fill=p.ink, step=st))
            # the gradient that has accumulated by this point
            out.append(txt(xs[i - 1], by + 34, f"{grads[i - 1][1]} = "
                                               f"{fmt(grads[i - 1][0], 3)}",
                           size=12, mono=True, pal=p, fill=p.warm, step=st))

        # link the two rows so it reads as one graph seen twice
        for i in range(n):
            out.append(line(xs[i], fy + bh / 2 + 4, xs[i], by - 26, pal=p,
                            stroke=p.faint, sw=0.9, dash="3 5"))

        last = 2 * n - 1
        out.append(txt(width / 2, height - 62,
                       f"∂loss/∂w  =  {fmt(dloss_dy, 3)} × {fmt(dy_dx2)} × "
                       f"{fmt(dx2_dx1)} × {fmt(dx1_dw)}  =  {fmt(dloss_dw, 3)}",
                       size=14.5, mono=True, pal=p, fill=p.ink, step=last))
        out.append(txt(width / 2, height - 38,
                       "Multiply the local derivatives along the path. That is the "
                       "chain rule, and applying it this way over a network is "
                       "backpropagation.",
                       size=13, pal=p, fill=p.accent, step=last))
        out.append(txt(width / 2, height - 14,
                       f"Each node only ever needs its OWN derivative — "
                       f"{fmt(dx1_dw)}, {fmt(dx2_dx1)}, {fmt(dy_dx2)} — and what "
                       f"arrived from the right.",
                       size=12.5, pal=p, fill=p.ink3, step=last))
        return svg(width, height, "".join(out), pal=p, steps=last,
                   sim_label="hop")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================================= residual connection, why --

def residual(fig_id, *, depth=5, cap="", note="", width=1280, height=468,
             full=False, seed=3):
    """Why the shortcut exists, in the only terms that explain it: the gradient.

    "It routes around destructive blocks" is true and does not say why that
    matters. What matters is the *product*: without a shortcut the gradient
    reaching layer 1 is every layer's derivative multiplied together, and a
    product of numbers below one goes to nothing. With a shortcut each block
    contributes ``1 + something``, so the product cannot collapse.

    So the figure computes both. Same blocks, same derivatives, two paths, and
    the two numbers at the end are three orders of magnitude apart.
    """
    import random
    rng = random.Random(seed)
    # Per-block local derivative. Below 1, which is the ordinary case once a
    # relu has zeroed part of the signal.
    d = [round(rng.uniform(0.25, 0.55), 2) for _ in range(depth)]

    plain = 1.0
    for v in d:
        plain *= v
    res = 1.0
    for v in d:
        res *= (1 + v)

    def build(p):
        out = []
        pad, bw, bh = 96, 128, 56
        step = (width - 2 * pad - bw) / (depth - 1)
        xs = [pad + i * step for i in range(depth)]
        y_plain, y_res = 132, 292

        for row, (yy, title, col, has_skip) in enumerate((
                (y_plain, "Plain stack", p.bad, False),
                (y_res, "With residual connections", p.good, True))):
            st = row + 1
            # The label goes above the row, not beside it: beside it and the
            # first block sits on top of it.
            # Clear the shortcut arcs and their "+ input" labels on the row
            # that has them, or the title lands underneath one.
            out.append(txt(56, yy - bh / 2 - (62 if has_skip else 40), title,
                           size=13.5, weight=600, pal=p, fill=col,
                           anchor="start", step=st))
            for i in range(depth):
                x = xs[i]
                out.append(rect(x, yy - bh / 2, bw, bh, r=8, pal=p,
                                fill=p.fill, stroke=p.line, sw=1.3, step=st))
                out.append(txt(x + bw / 2, yy - 8, f"block {i + 1}", size=12,
                               pal=p, fill=p.ink2, step=st))
                out.append(txt(x + bw / 2, yy + 12, f"∂ = {fmt(d[i])}", size=12,
                               mono=True, pal=p, fill=p.ink, step=st))
                if i < depth - 1:
                    out.append(arrow(x + bw + 3, yy, xs[i + 1] - 3, yy, pal=p,
                                     stroke=p.line, sw=1.4, step=st))
                if has_skip:
                    # The shortcut, drawn over the block it skips.
                    top = yy - bh / 2 - 26
                    out.append(path(
                        f"M{x - 2:.1f},{yy:.1f} C{x - 2:.1f},{top:.1f} "
                        f"{x + bw + 2:.1f},{top:.1f} {x + bw + 2:.1f},{yy:.1f}",
                        stroke=p.good, sw=1.6, pal=p, step=st))
                    out.append(txt(x + bw / 2, top - 8, "+ input", size=11,
                                   pal=p, fill=p.good, step=st))

        # ---- the two products ------------------------------------------
        gy = 366
        out.append(txt(56, gy, "gradient reaching block 1", size=13, weight=600,
                       pal=p, fill=p.ink3, anchor="start", step=3))
        out.append(txt(56, gy + 26,
                       "×".join(fmt(v) for v in d) + f"  =  {plain:.4f}",
                       size=13, mono=True, pal=p, fill=p.bad, anchor="start",
                       step=3))
        out.append(txt(56, gy + 50,
                       "×".join(f"(1+{fmt(v)})" for v in d)
                       + f"  =  {res:.2f}",
                       size=13, mono=True, pal=p, fill=p.good, anchor="start",
                       step=3))
        out.append(txt(width - 56, gy + 38,
                       f"{res / plain:,.0f}× larger".replace(",", " "),
                       size=20, weight=600, pal=p, fill=p.good, anchor="end",
                       step=3))
        out.append(txt(width / 2, height - 14,
                       "A product of numbers below one goes to nothing. Adding the "
                       "input makes every factor bigger than one, so it cannot.",
                       size=13, pal=p, fill=p.accent, step=3))
        return svg(width, height, "".join(out), pal=p, steps=3,
                   sim_label="stack")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ============================================= a better representation, drawn --

def coord_change(fig_id, *, cap="", note="", width=1240, height=470, full=False,
                 angle=32.0):
    """Chapter 1's whole argument: the same points, written down differently.

    Filled and hollow, not black and white: on a dark slide the book's "black
    points" render light, and a caption that argues with the picture is worse
    than no caption.

    Three panels over ONE dataset, and the points never move -- they are at the
    same pixel in all three. Only the axes drawn over them change, and with the
    new axes the rule that separates the colours is five characters long.

    Drawing this as a flowchart of three boxes would say "representation
    matters" without showing anything. The claim only lands when you can see
    that nothing about the data changed.
    """
    import math
    ph = math.radians(angle)
    eu = (math.cos(ph), math.sin(ph))      # the axis that separates them
    ev = (-math.sin(ph), math.cos(ph))

    # Authored in (u, v) so the separation is exact, then written down in raw
    # coordinates -- which is the only place the drawing ever reads them from.
    uv = [(-2.5, 1.4), (-1.6, -0.6), (-2.8, 0.2), (-1.3, 1.9), (-2.0, -1.6),
          (-1.2, -1.2), (-2.9, -0.9), (-1.7, 0.7),
          (1.4, 1.7), (2.4, 0.5), (1.2, -1.1), (2.7, -0.3), (1.8, -1.8),
          (2.1, 1.2), (1.3, 0.1), (2.5, -1.5)]
    lab = [0] * 8 + [1] * 8
    raw = [(u * eu[0] + v * ev[0], u * eu[1] + v * ev[1]) for u, v in uv]

    def build(p):
        out = []
        S, cy, half, box_top = 41.0, 232.0, 150.0, 82.0
        panels = (
            (78, "1 \u00b7 the data as it arrives",
             "no rule in x and y is short", False),
            (500, "2 \u00b7 the axes moved",
             "not one point moved \u2014 only the axes did", True),
            (922, "3 \u00b7 the rule that follows",
             "the filled points are those with u > 0", True),
        )
        for pi, (px, title, sub, rot) in enumerate(panels):
            st = pi + 1
            cx = px + half
            clip = f"{fig_id}-{p.name}-clip{pi}"
            out.append(
                f'<clipPath id="{clip}"><rect x="{px}" y="{box_top}" '
                f'width="{2 * half}" height="300" rx="10"/></clipPath>')
            out.append(txt(cx, 58, title, size=13.5, weight=600, pal=p,
                           fill=p.ink, step=st))
            out.append(rect(px, box_top, 2 * half, 300, r=10, pal=p, fill=p.fill,
                            stroke=p.line, sw=1.0, step=st))

            # Panel 3 shades the half-plane u > 0, clipped to the panel.
            if pi == 2:
                L = 460.0
                pts = []
                for a, b in ((L, L), (L, -L), (0, -L), (0, L)):
                    x = eu[0] * a + ev[0] * b
                    y = eu[1] * a + ev[1] * b
                    pts.append(f"{cx + x:.1f},{cy - y:.1f}")
                out.append(f'<polygon points="{" ".join(pts)}" fill="{p.good}" '
                           f'opacity="0.12" clip-path="url(#{clip})"'
                           f'{K.step_attr(st)}/>')

            axes = ((eu, "u", p.accent), (ev, "v", p.line)) if rot else \
                   (((1.0, 0.0), "x", p.line), ((0.0, 1.0), "y", p.line))
            for k, (d, name, col) in enumerate(axes):
                L = 132.0
                hot = rot and k == 0
                out.append(line(cx - d[0] * L, cy + d[1] * L,
                                cx + d[0] * L, cy - d[1] * L, pal=p,
                                stroke=col, sw=1.8 if hot else 1.0,
                                dash=None if hot else "3 4", step=st))
                out.append(txt(cx + d[0] * (L + 12), cy - d[1] * (L + 12) + 4,
                               name, size=12.5, mono=True, pal=p,
                               fill=col if hot else p.ink3, step=st))

            for (x, y), c in zip(raw, lab):
                out.append(circle(cx + x * S, cy - y * S, 6.5, pal=p,
                                  fill=p.ink if c else p.fill,
                                  stroke=p.ink, sw=1.5, step=st))

            out.append(txt(cx, 404, sub, size=11.5, pal=p, fill=p.ink3, step=st))

        out.append(txt(width / 2, height - 18,
                       "The points are at the same pixel in all three panels. "
                       "No model got smarter \u2014 the data got written down better.",
                       size=13.5, weight=600, pal=p, fill=p.accent, step=3))
        return svg(width, height, "".join(out), pal=p, steps=3,
                   sim_label="panel")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================================ the agent loop, actually run --

def agent_loop(fig_id, *, cap="", note="", width=1280, height=452, full=False,
               max_steps=8):
    """Plan, act, observe, check -- with a real run turning inside it.

    The loop drawn as four boxes and an arrow back is a picture of a `while`
    statement. What it leaves out is everything that matters: how many times it
    goes round, what each turn actually costs, and what makes it stop. So the
    ring is on the left and a real trace runs on the right -- one line per turn,
    with the step budget filling a cell at a time, ending on the turn that
    cannot happen because no tool for it exists.

    The trace is the SME credit assessment from ``ai-agentic-demo``: six turns,
    six tools, and a recommendation that a person still has to decide.
    """
    turns = [
        ("get_application",       "APP-2203 · Batik Ayu Mandiri"),
        ("get_transactions",      "12 months · 1 843 rows"),
        ("compute_risk_features", "DSCR 0.82 · 9 features"),
        ("score_credit",          "pd = 0.693"),
        ("lookup_policy",         "CP-04, CP-05, CP-06"),
        ("submit_recommendation", "queued for an officer"),
    ]

    def build(p):
        import math
        out = []
        cx, cy, r = 268.0, 244.0, 112.0
        stations = (("Plan", "what next?", -90), ("Act", "call a tool", 0),
                    ("Observe", "result enters\\nthe context", 90),
                    ("Check", "goal met?\\nbudget spent?", 180))

        # ---- the ring ---------------------------------------------------
        for i in range(4):
            a0 = math.radians(stations[i][2] + 16)
            a1 = math.radians(stations[(i + 1) % 4][2] - 16)
            x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
            x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
            out.append(path(f"M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 0 1 "
                            f"{x1:.1f},{y1:.1f}",
                            stroke=p.line, sw=1.5, pal=p, marker=True, step=1))
        for name, sub, ang in stations:
            a = math.radians(ang)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            out.append(circle(x, y, 46, pal=p, fill=p.fill, stroke=p.accent,
                              sw=1.6, step=1))
            lines = sub.split("\\n")
            out.append(txt(x, y - 6 - 5 * len(lines), name, size=14,
                           weight=600, pal=p, fill=p.ink, step=1))
            for k, ln in enumerate(lines):
                out.append(txt(x, y + 10 + 12 * k - 5 * (len(lines) - 1), ln,
                               size=10, pal=p, fill=p.ink3, step=1))

        out.append(txt(cx, 46, "the goal", size=11.5, pal=p, fill=p.ink3,
                       step=1))
        out.append(txt(cx, 66, "“Assess APP-2203.”", size=13,
                       weight=600, pal=p, fill=p.ink, step=1))
        out.append(arrow(cx, 80, cx, cy - r - 48, pal=p, stroke=p.line,
                         sw=1.4, step=1))
        out.append(arrow(cx - r - 46, cy, 104, cy, pal=p, stroke=p.good,
                         sw=1.6, step=7))
        out.append(txt(56, cy - 12, "done, or", size=11, pal=p, fill=p.good,
                       step=7))
        out.append(txt(56, cy + 22, "out of budget", size=11, pal=p,
                       fill=p.good, step=7))

        # ---- the trace ---------------------------------------------------
        tx, ty = 470.0, 88.0
        out.append(txt(tx, 52, "one real run", size=13.5, weight=600, pal=p,
                       fill=p.ink, anchor="start", step=1))
        for i, (tool, result) in enumerate(turns):
            st = i + 2
            y = ty + i * 38
            out.append(txt(tx, y, f"{i + 1}", size=12, mono=True, pal=p,
                           fill=p.ink3, anchor="start", step=st))
            out.append(txt(tx + 26, y, tool, size=13, mono=True, pal=p,
                           fill=p.accent, anchor="start", step=st))
            out.append(txt(tx + 262, y, "→", size=13, pal=p, fill=p.ink3,
                           anchor="start", step=st))
            out.append(txt(tx + 286, y, result, size=12.5, pal=p, fill=p.ink2,
                           anchor="start", step=st))

        # ---- the step budget, filling one cell per turn -------------------
        by = ty + len(turns) * 38 + 26
        out.append(txt(tx, by, "step budget", size=12, pal=p, fill=p.ink3,
                       anchor="start", step=1))
        # The whole budget is visible from the first step -- otherwise the row
        # starts with two lonely cells and reads as the budget, not as what is
        # left of it. Spent cells are painted OVER the empty ones as the run
        # goes, which is what the cumulative reveal makes easy.
        for i in range(max_steps):
            out.append(rect(tx + 108 + i * 30, by - 11, 22, 20, r=4, pal=p,
                            fill=p.fill, stroke=p.line, sw=1.2, step=1))
        for i in range(len(turns)):
            out.append(rect(tx + 108 + i * 30, by - 11, 22, 20, r=4, pal=p,
                            fill=p.accent, stroke=p.accent, sw=1.2,
                            step=i + 2))
        out.append(txt(tx + 108 + max_steps * 30 + 12, by,
                       f"{len(turns)} of {max_steps} — it stopped because "
                       f"it was finished, not because it ran out",
                       size=11.5, pal=p, fill=p.ink3, anchor="start", step=7))

        out.append(txt(tx, by + 40,
                       "Turn 7 would have been approve_credit.",
                       size=13.5, weight=600, pal=p, fill=p.good,
                       anchor="start", step=7))
        out.append(txt(tx, by + 62,
                       "There is no such tool in the registry, so there is no "
                       "seventh turn — and no prompt that can invent one.",
                       size=12.5, pal=p, fill=p.ink2, anchor="start", step=7))
        return svg(width, height, "".join(out), pal=p, steps=7,
                   sim_label="turn")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================================ the latent space, walked in --

def _mix(c1, c2, t):
    """Blend two ``#rrggbb`` colours. Anything else comes back as c1."""
    if not (c1.startswith("#") and c2.startswith("#") and len(c1) == len(c2) == 7):
        return c1
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def latent_space(fig_id, *, cap="", note="", width=1240, height=486, full=False,
                 n_steps=5, seed=11):
    """Why "the in-betweens of the training images" is a claim about geometry.

    The chain of boxes -- prompt, encoder, latent space, decoder, image -- says
    what the parts are called and nothing about what makes any of it work. What
    makes it work is that the training images land on a *region* of the space,
    and that every point of that region decodes to something valid. So walk a
    straight line between two of them and watch the decoded shape change
    continuously.

    The tiles are schematic on purpose: a hand-drawn SVG cannot show a
    photograph, and pretending otherwise would be the wrong kind of honest. The
    shape is a stand-in, and what the figure is really showing is that the
    interpolation is smooth -- and that it stops being smooth as soon as you
    step off the region the data covers, which is where the extra fingers come
    from.
    """
    import math
    import random
    rng = random.Random(seed)

    # The data manifold: a band, not a blob. That shape is the point -- most of
    # the space is NOT valid, which is what the off-manifold step says.
    #
    # The band is kept close to straight deliberately. An arc would look better
    # and would make the figure lie: the chord between two points of an arc
    # leaves the arc in the middle, so the tidy story "walk from A to B and
    # every step is valid" would be false exactly where the figure claims it.
    # That failure is real and worth a slide of its own; it is not this slide.
    def band(t):
        return 0.10 + 0.80 * t, 0.26 + 0.44 * t + 0.05 * math.sin(t * 5.2)

    cloud = []
    for _ in range(46):
        u, v = band(rng.uniform(0, 1))
        cloud.append((u + rng.gauss(0, 0.022), v + rng.gauss(0, 0.045)))
    A, B = band(0.08), band(0.92)
    OFF = (0.30, 0.86)

    def build(p):
        out = []
        px, py, pw, ph = 62.0, 86.0, 470.0, 300.0

        def XY(u, v):
            return px + u * pw, py + (1 - v) * ph

        out.append(txt(px, 56, "the latent space", size=13.5, weight=600,
                       pal=p, fill=p.ink, anchor="start", step=1))
        out.append(rect(px, py, pw, ph, r=10, pal=p, fill=p.fill,
                        stroke=p.line, sw=1.0, step=1))
        for u, v in cloud:
            x, y = XY(u, v)
            out.append(circle(x, y, 4, pal=p, fill=p.ink3, stroke="none",
                              sw=0, step=1))
        out.append(txt(px + pw / 2, py + ph + 22,
                       "each dot is one training image", size=11.5, pal=p,
                       fill=p.ink3, step=1))

        ax, ay = XY(*A)
        bx, by_ = XY(*B)
        for (x, y, lbl) in ((ax, ay, "A"), (bx, by_, "B")):
            out.append(circle(x, y, 8, pal=p, fill=p.accent, stroke=p.accent,
                              sw=1.5, step=2))
            out.append(txt(x, y - 18, lbl, size=13, weight=600, pal=p,
                           fill=p.accent, step=2))
        out.append(line(ax, ay, bx, by_, pal=p, stroke=p.accent, sw=1.4,
                        dash="5 4", step=3))
        for i in range(1, n_steps - 1):
            t = i / (n_steps - 1)
            out.append(circle(ax + (bx - ax) * t, ay + (by_ - ay) * t, 5,
                              pal=p, fill=p.fill, stroke=p.accent, sw=1.5,
                              step=3))

        ox, oy = XY(*OFF)
        out.append(circle(ox, oy, 8, pal=p, fill=p.bad, stroke=p.bad, sw=1.5,
                          step=5))
        out.append(txt(ox, oy - 18, "C", size=13, weight=600, pal=p, fill=p.bad,
                       step=5))
        out.append(txt(ox + 16, oy + 4, "no training image near here",
                       size=11, pal=p, fill=p.bad, anchor="start", step=5))

        # ---- what the decoder returns for each point ---------------------
        tw, gap = 96.0, 18.0
        gx, gy = 596.0, 96.0
        out.append(txt(gx, 56, "what the decoder returns", size=13.5,
                       weight=600, pal=p, fill=p.ink, anchor="start", step=1))
        for i in range(n_steps):
            t = i / (n_steps - 1)
            x = gx + i * (tw + gap)
            st = 4 if 0 < i < n_steps - 1 else 2
            out.append(rect(x, gy, tw, tw, r=8, pal=p, fill=p.fill,
                            stroke=p.line, sw=1.1, step=st))
            col = _mix(p.accent, p.warm, t)
            # Body and head both interpolate, so the tile changes continuously
            # rather than switching between two states.
            bw = 26 + 34 * t
            bh = 48 - 20 * t
            out.append(rect(x + tw / 2 - bw / 2, gy + tw - 14 - bh, bw, bh,
                            r=5, pal=p, fill=col, stroke="none", sw=0, step=st))
            out.append(circle(x + tw / 2, gy + tw - 20 - bh - (12 - 3 * t),
                              12 - 3 * t, pal=p, fill=col, stroke="none", sw=0,
                              step=st))
            lbl = "A" if i == 0 else ("B" if i == n_steps - 1 else f"t = {t:.2f}")
            out.append(txt(x + tw / 2, gy + tw + 18, lbl, size=11.5,
                           mono=i not in (0, n_steps - 1), pal=p,
                           fill=p.accent if i in (0, n_steps - 1) else p.ink3,
                           step=st))

        # C, off the manifold.
        cxx = gx
        cyy = gy + tw + 62
        out.append(rect(cxx, cyy, tw, tw, r=8, pal=p, fill=p.fill,
                        stroke=p.bad, sw=1.3, step=5))
        rng2 = __import__("random").Random(4)
        for _ in range(9):
            out.append(rect(cxx + rng2.uniform(8, 62), cyy + rng2.uniform(8, 62),
                            rng2.uniform(10, 30), rng2.uniform(8, 26), r=3,
                            pal=p, fill=p.bad, stroke="none", sw=0,
                            step=5))
        out.append(txt(cxx + tw / 2, cyy + tw + 18, "C", size=11.5, weight=600,
                       pal=p, fill=p.bad, step=5))
        out.append(txt(cxx + tw + 22, cyy + 34,
                       "Every point decodes to something. Only the points the "
                       "data covers", size=12.5, pal=p, fill=p.ink2,
                       anchor="start", step=5))
        out.append(txt(cxx + tw + 22, cyy + 54,
                       "decode to something valid — which is where the sixth "
                       "finger comes from.", size=12.5, pal=p, fill=p.ink2,
                       anchor="start", step=5))
        return svg(width, height, "".join(out), pal=p, steps=5,
                   sim_label="step")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ============================================ softmax or sigmoid, worked out --

def output_heads(fig_id, *, cap="", note="", width=1330, height=414, full=False):
    """The choice of output layer, decided by arithmetic instead of a table.

    "Softmax when exactly one class is true, sigmoid per class when several
    can be" is correct, memorisable, and teaches nothing about why. The why is
    one line of arithmetic: softmax divides by the sum over classes, so the
    classes compete for a fixed budget of one; sigmoid squashes each logit on
    its own, so they do not.

    So both are computed on the SAME logits, and the example is chosen to make
    the difference matter -- a photograph that really is both a cat and
    outdoors. Softmax has to split its belief between two true things. Sigmoid
    does not have to.
    """
    import math
    classes = ("cat", "dog", "outdoors")
    z = (2.4, -0.5, 2.1)
    truth = (True, False, True)

    ez = [math.exp(v) for v in z]
    Z = sum(ez)
    soft = [e / Z for e in ez]
    sig = [1 / (1 + math.exp(-v)) for v in z]

    def build(p):
        out = []
        colw, gap = 300.0, 84.0
        lx, rx = 92.0, 92.0 + colw + gap + 176.0
        rowh = 34.0

        # ---- the shared logits, in a ROW ----------------------------------
        # Three rows of two columns is the obvious layout and costs 90px of
        # height, which the figure then pays for in rendered scale. Across the
        # top it costs one line.
        out.append(txt(lx, 54, "one image, one set of logits", size=13.5,
                       weight=600, pal=p, fill=p.ink, anchor="start", step=1))
        for i, c in enumerate(classes):
            x = lx + i * 244
            out.append(rect(x, 74, 216, 46, r=8, pal=p, fill=p.fill,
                            stroke=p.good if truth[i] else p.line,
                            sw=1.4 if truth[i] else 1.0, step=1))
            out.append(txt(x + 16, 90, c, size=12.5, pal=p,
                           fill=p.good if truth[i] else p.ink3,
                           anchor="start", step=1))
            out.append(txt(x + 16, 108, f"z = {z[i]:+.1f}", size=12.5,
                           mono=True, pal=p, fill=p.ink, anchor="start",
                           step=1))
            if truth[i]:
                out.append(txt(x + 200, 99, "true", size=11, pal=p,
                               fill=p.good, anchor="end", step=1))
        out.append(txt(lx + 3 * 244 + 8, 99,
                       "the photograph is a cat, and it is outdoors — both",
                       size=12, pal=p, fill=p.ink3, anchor="start", step=1))

        # ---- the two heads ------------------------------------------------
        hy = 168.0
        for col, (name, formula, vals, tot, st, colr) in enumerate((
                ("softmax", "eᶻⁱ ⁄ Σⱼ eᶻʲ", soft, sum(soft), 2, p.bad),
                ("sigmoid, per class", "1 ⁄ (1 + e⁻ᶻ)", sig, sum(sig), 3,
                 p.good))):
            x = lx if col == 0 else rx
            out.append(txt(x, hy, name, size=14, weight=600, pal=p, fill=colr,
                           anchor="start", step=st))
            out.append(txt(x, hy + 22, formula, size=12.5, mono=True, pal=p,
                           fill=p.ink3, anchor="start", step=st))
            for i, c in enumerate(classes):
                y = hy + 56 + i * rowh
                out.append(txt(x, y, c, size=12.5, pal=p,
                               fill=p.ink2 if not truth[i] else p.ink,
                               anchor="start", step=st))
                bw = 128.0 * vals[i]
                out.append(rect(x + 108, y - 9, 128, 18, r=4, pal=p,
                                fill=p.fill, stroke=p.line, sw=1.0, step=st))
                out.append(rect(x + 108, y - 9, bw, 18, r=4, pal=p, fill=colr,
                                stroke="none", sw=0, step=st))
                out.append(txt(x + 248, y, f"{vals[i]:.3f}", size=12.5,
                               mono=True, pal=p, fill=p.ink, anchor="start",
                               step=st))
            y = hy + 56 + 3 * rowh + 6
            out.append(line(x, y - 12, x + 296, y - 12, pal=p, stroke=p.faint,
                            sw=1, step=st))
            out.append(txt(x, y + 6, "sum", size=12.5, pal=p, fill=p.ink3,
                           anchor="start", step=st))
            out.append(txt(x + 248, y + 6, f"{tot:.3f}", size=13.5, mono=True,
                           weight=600, pal=p, fill=colr, anchor="start",
                           step=st))
            out.append(txt(x, y + 30,
                           "always 1 — the classes share one budget"
                           if col == 0 else
                           "not 1, and nothing says it should be",
                           size=11.5, pal=p, fill=colr, anchor="start",
                           step=st))

        # The verdict is NOT repeated here. It is the band beside the figure on
        # the slide, and saying it twice costs 60px of drawing height, which
        # the figure pays for in rendered size.
        return svg(width, height, "".join(out), pal=p, steps=3,
                   sim_label="head")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================================ solve it once, reuse it after --

def reuse_curve(fig_id, *, cap="", note="", width=1290, height=430, full=False,
                pool=40, per_task=6, tasks=20):
    """What "any single problem would only need to be solved once" implies.

    This is a claim about a system nobody has built, so there is nothing to
    measure. What there is, is a consequence: if a task needs ``per_task``
    subroutines drawn from a space of ``pool`` abstract primitives, and the
    library keeps everything ever synthesised, then the work a new task needs
    is whatever is not in the library yet.

    That is computable, and the figure computes it rather than asserting it.
    The assumptions are printed ON the drawing, because they are doing all the
    work: change ``pool`` and the curve changes, which is the honest way to
    show a claim about a future architecture.
    """
    # Expected library size after t tasks, each drawing per_task of pool
    # primitives uniformly: pool * (1 - (1 - per_task/pool)^t).
    q = 1.0 - per_task / pool
    lib = [pool * (1.0 - q ** t) for t in range(tasks + 1)]
    new = [lib[t] - lib[t - 1] for t in range(1, tasks + 1)]

    def build(p):
        out = []
        bx, by, bw, bh = 82.0, 96.0, 900.0, 236.0
        step_x = bw / tasks
        unit = bh / per_task

        out.append(txt(bx, 52, "work per task, as the library fills", size=13.5,
                       weight=600, pal=p, fill=p.ink, anchor="start", step=1))
        out.append(txt(bx + 330, 52,
                       f"assumption: each task needs {per_task} subroutines, "
                       f"drawn from {pool} abstract primitives",
                       size=11.5, pal=p, fill=p.ink3, anchor="start", step=1))

        out.append(line(bx, by + bh, bx + bw, by + bh, pal=p, stroke=p.line,
                        sw=1.2, step=1))
        out.append(line(bx, by, bx, by + bh, pal=p, stroke=p.line, sw=1.2,
                        step=1))
        for k in range(per_task + 1):
            y = by + bh - k * unit
            out.append(txt(bx - 10, y + 4, str(k), size=10.5, mono=True, pal=p,
                           fill=p.ink3, anchor="end", step=1))
            if k:
                out.append(line(bx, y, bx + bw, y, pal=p, stroke=p.faint,
                                sw=0.7, dash="2 5", step=1))

        for t in range(tasks):
            x = bx + t * step_x + 3
            w = step_x - 6
            st = 1 if t == 0 else (2 if t < 5 else 3)
            n = new[t]
            r = per_task - n
            out.append(rect(x, by + bh - r * unit, w, r * unit, r=2, pal=p,
                            fill=p.good, stroke="none", sw=0, step=st))
            out.append(rect(x, by + bh - per_task * unit, w, n * unit, r=2,
                            pal=p, fill=p.warm, stroke="none", sw=0, step=st))
            if t in (0, 4, 9, 19):
                out.append(txt(x + w / 2, by + bh + 18, f"task {t + 1}",
                               size=10.5, pal=p, fill=p.ink3, step=st))

        # Legend, and the number the whole slide is about.
        ly = by + bh + 46
        for i, (col, lbl) in enumerate(((p.warm, "newly synthesised"),
                                        (p.good, "fetched from the library"))):
            out.append(rect(bx + i * 240, ly - 9, 14, 14, r=3, pal=p, fill=col,
                            stroke="none", sw=0, step=1))
            out.append(txt(bx + i * 240 + 22, ly, lbl, size=12, pal=p,
                           fill=p.ink2, anchor="start", step=1))

        rx = bx + bw + 42
        out.append(txt(rx, by + 26, "task 1", size=12, pal=p, fill=p.ink3,
                       anchor="start", step=1))
        out.append(txt(rx, by + 52, f"{new[0]:.1f} new", size=20, weight=600,
                       pal=p, fill=p.warm, anchor="start", step=1))
        out.append(txt(rx, by + 108, f"task {tasks}", size=12, pal=p,
                       fill=p.ink3, anchor="start", step=3))
        out.append(txt(rx, by + 134, f"{new[-1]:.2f} new", size=20, weight=600,
                       pal=p, fill=p.good, anchor="start", step=3))
        out.append(txt(rx, by + 176,
                       f"library: {lib[-1]:.0f} of {pool}", size=12.5, mono=True,
                       pal=p, fill=p.ink2, anchor="start", step=3))
        out.append(txt(bx, height - 18,
                       "The curve is the claim. It is also entirely a consequence "
                       "of the assumption printed above it — change the size of "
                       "the primitive space and it changes.",
                       size=12.5, pal=p, fill=p.accent, anchor="start", step=3))
        return svg(width, height, "".join(out), pal=p, steps=3,
                   sim_label="tasks")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ============================================== five screens, and a missing one --

def phone_flow(fig_id, screens, *, cap="", note="", width=1300, height=452,
               full=False):
    """A mobile flow drawn as phones, not as a row of emoji.

    ``screens`` is a list of ``(kind, title, caption)``. ``kind`` picks what is
    sketched inside the frame -- ``list``, ``detail``, ``progress``,
    ``result``, ``stamp``, or ``absent``. The last one draws a dashed frame
    with a strike through it, because "the screen that does not exist" is a
    claim about the product and deserves to be visible as a gap rather than
    stated in a caption.

    The sketches are schematic and say so. What they carry that six icons do
    not is the SHAPE of each screen -- a list is a list, a result is one big
    number with its sources under it -- and the fact that they are a sequence.
    """
    n = len(screens)

    def build(p):
        out = []
        pw, ph, gap = 168.0, 292.0, 22.0
        total = n * pw + (n - 1) * gap
        x0 = (width - total) / 2
        top = 76.0

        for i, (kind, title, sub) in enumerate(screens):
            st = i + 1
            x = x0 + i * (pw + gap)
            absent = kind == "absent"
            col = p.bad if absent else (p.accent if kind in ("result", "stamp")
                                        else p.line)
            out.append(rect(x, top, pw, ph, r=16, pal=p,
                            fill="none" if absent else p.fill, stroke=col,
                            sw=1.6 if absent else 1.2,
                            dash="6 5" if absent else None, step=st))
            # the notch, so it reads as a phone rather than a card
            if not absent:
                out.append(rect(x + pw / 2 - 22, top + 7, 44, 7, r=3.5, pal=p,
                                fill=p.line, stroke="none", sw=0, step=st))
            iy = top + 30
            ix, iw = x + 14, pw - 28

            def bar(y, w, h=11, c=None, r=3):
                out.append(rect(ix, y, w, h, r=r, pal=p, fill=c or p.line,
                                stroke="none", sw=0, step=st))

            if kind == "list":
                for k in range(4):
                    y = iy + 8 + k * 40
                    out.append(rect(ix, y, iw, 32, r=6, pal=p, fill=p.fill2,
                                    stroke=p.faint, sw=1, step=st))
                    bar(y + 8, iw * 0.62, 8, p.ink3)
                    bar(y + 20, iw * 0.34, 6, p.faint)
            elif kind == "detail":
                bar(iy + 10, iw * 0.7, 12, p.ink3)
                bar(iy + 30, iw * 0.45, 8, p.faint)
                out.append(rect(ix, iy + 52, iw, 96, r=8, pal=p, fill=p.fill2,
                                stroke=p.faint, sw=1, step=st))
                out.append(circle(x + pw / 2, iy + 100, 20, pal=p, fill="none",
                                  stroke=p.ink3, sw=1.6, step=st))
                out.append(circle(x + pw / 2, iy + 100, 8, pal=p, fill="none",
                                  stroke=p.ink3, sw=1.2, step=st))
                for k in range(3):
                    bar(iy + 164 + k * 16, iw * (0.9 - 0.18 * k), 7, p.faint)
            elif kind == "progress":
                bar(iy + 12, iw * 0.55, 9, p.ink3)
                out.append(rect(ix, iy + 34, iw, 12, r=6, pal=p, fill=p.fill2,
                                stroke=p.faint, sw=1, step=st))
                out.append(rect(ix, iy + 34, iw * 0.62, 12, r=6, pal=p,
                                fill=p.accent, stroke="none", sw=0, step=st))
                for k, w in enumerate((0.8, 0.66, 0.5)):
                    bar(iy + 62 + k * 20, iw * w, 7,
                        p.accent if k == 0 else p.faint)
                out.append(txt(x + pw / 2, iy + 150, "score_credit", size=10.5,
                               mono=True, pal=p, fill=p.accent, step=st))
                out.append(txt(x + pw / 2, iy + 168, "step 4 of 6", size=10,
                               pal=p, fill=p.ink3, step=st))
            elif kind == "result":
                out.append(rect(ix, iy + 8, iw, 58, r=8, pal=p,
                                fill=p.accent_fill, stroke=p.accent, sw=1.2,
                                step=st))
                out.append(txt(x + pw / 2, iy + 32, "pd = 0.693", size=16,
                               mono=True, weight=600, pal=p, fill=p.accent,
                               step=st))
                out.append(txt(x + pw / 2, iy + 52, "decline", size=11, pal=p,
                               fill=p.ink3, step=st))
                for k, lbl in enumerate(("CP-04", "CP-05", "CP-06")):
                    out.append(rect(ix, iy + 80 + k * 26, iw * 0.62, 19, r=5,
                                    pal=p, fill=p.fill2, stroke=p.faint, sw=1,
                                    step=st))
                    out.append(txt(ix + 8, iy + 93 + k * 26, lbl, size=10,
                                   mono=True, pal=p, fill=p.ink3,
                                   anchor="start", step=st))
                out.append(txt(ix, iy + 176, "view trace →", size=10.5, pal=p,
                               fill=p.accent, anchor="start", step=st))
            elif kind == "stamp":
                out.append(rect(ix, iy + 10, iw, 44, r=8, pal=p, fill=p.fill2,
                                stroke=p.good, sw=1.3, step=st))
                out.append(txt(x + pw / 2, iy + 32, "decided", size=13,
                               weight=600, pal=p, fill=p.good, step=st))
                out.append(txt(ix, iy + 74, "officer", size=10, pal=p,
                               fill=p.ink3, anchor="start", step=st))
                out.append(txt(ix, iy + 90, "OFF-114", size=11, mono=True,
                               pal=p, fill=p.ink2, anchor="start", step=st))
                out.append(txt(ix, iy + 116, "reason — required", size=10,
                               pal=p, fill=p.ink3, anchor="start", step=st))
                for k in range(3):
                    bar(iy + 128 + k * 15, iw * (0.95 - 0.2 * k), 7, p.faint)
            elif kind == "absent":
                # The strike stops short of the middle so the words sit in a
                # gap rather than on top of the lines.
                for y0, y1 in ((top + 34, top + ph / 2 - 30),
                               (top + ph / 2 + 30, top + ph - 34)):
                    out.append(line(x + 22, y0, x + pw - 22, y1, pal=p,
                                    stroke=p.bad, sw=1.6, step=st))
                    out.append(line(x + pw - 22, y0, x + 22, y1, pal=p,
                                    stroke=p.bad, sw=1.6, step=st))
                out.append(txt(x + pw / 2, top + ph / 2 - 6, "no such", size=12.5,
                               weight=600, pal=p, fill=p.bad, step=st))
                out.append(txt(x + pw / 2, top + ph / 2 + 12, "screen",
                               size=12.5, weight=600, pal=p, fill=p.bad,
                               step=st))

            out.append(txt(x + pw / 2, top - 22, title, size=12.5, weight=600,
                           pal=p, fill=p.bad if absent else p.ink, step=st))
            out.append(txt(x + pw / 2, top + ph + 24, sub, size=11, pal=p,
                           fill=p.ink3, step=st))
            # No arrow INTO an absent screen: it is not the next step in the
            # flow, it is the step that does not exist.
            nxt = screens[i + 1][0] if i < n - 1 else None
            if nxt and nxt != "absent":
                ax = x + pw + 3
                out.append(arrow(ax, top + ph / 2, ax + gap - 6, top + ph / 2,
                                 pal=p, stroke=p.faint, sw=1.3, step=st + 1))
        return svg(width, height, "".join(out), pal=p, steps=n,
                   sim_label="screen")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ========================================= where segmentation is used, shown --

def mask_domains(fig_id, *, cap="", note="", width=1300, height=336, full=False):
    """Four domains, and the same operation happening in all of them.

    "Where it is used" is a list, and a list of four emoji is what it usually
    gets. What the list is really about is that in each of these fields the
    DELIVERABLE is a mask -- a label with the same shape as the input -- and
    only the thing being delineated changes. So the figure draws the four
    scenes, then drops the masks onto them, which is one operation seen four
    times rather than four words seen once.

    The scenes are 12x9 cells and obviously schematic. That is the honest form
    here: a drawn SVG cannot show a photograph, and the claim being made is
    about the SHAPE of the output, which a grid shows better than a photo.
    """
    W, H = 12, 9

    def photo(x, y):
        # a subject standing against a background
        if 3 <= x <= 7 and y >= 2:
            return 1
        return 0

    # Order matters in all four of these: the specific thing has to be tested
    # before the ground it stands on, or the ground swallows it. Getting that
    # backwards is how the first draft drew a lesion made entirely of tissue.
    def driving(x, y):
        if 4 <= y <= 6 and 1 <= x <= 4:
            return 2                       # car
        if 3 <= y <= 6 and 8 <= x <= 9:
            return 3                       # person
        if y >= 6:
            return 1                       # road
        return 0                           # sky

    def robot(x, y):
        if 5 <= x <= 8 and 4 <= y <= 6:
            return 2                       # the graspable object
        if y >= 7:
            return 1                       # table
        return 0

    def scan(x, y):
        if (x - 7) ** 2 + (y - 3) ** 2 <= 2:
            return 2                       # lesion
        if (x - 6) ** 2 + (y - 4) ** 2 <= 9:
            return 1                       # tissue
        return 0

    doms = (
        ("Image and video editing", photo, {1}, "the subject, so the background can go"),
        ("Autonomous driving", driving, {1, 2, 3}, "road, vehicles, people — three classes"),
        ("Robotics", robot, {2}, "exactly where a graspable object begins"),
        ("Medical imaging", scan, {2}, "the lesion, not merely that there is one"),
    )

    def build(p):
        out = []
        cell = 15.0
        gw, gh = W * cell, H * cell
        gap = (width - 2 * 64 - 4 * gw) / 3
        top = 84.0
        # Colours are assigned PER TILE, in order of the classes that tile
        # masks. Class 1 means "road" in one scene and "the subject" in
        # another, so a global class-to-colour map would say they were the
        # same thing. A single-class tile is always the accent; the
        # three-class one is the only place a second and third colour mean
        # anything.
        wheel = (p.accent, p.good, p.warm)

        # Legend on one line at the top, clear of the tile titles.
        out.append(rect(64, 34, 13, 13, r=3, pal=p, fill=p.faint,
                        stroke="none", sw=0, step=1))
        out.append(txt(84, 45, "the input", size=12, pal=p, fill=p.ink3,
                       anchor="start", step=1))
        out.append(rect(184, 34, 13, 13, r=3, pal=p, fill=p.accent,
                        stroke="none", sw=0, step=2))
        out.append(txt(204, 45,
                       "the mask — a label with the same shape as the input",
                       size=12, pal=p, fill=p.accent, anchor="start", step=2))

        for i, (name, fn, mask_classes, what) in enumerate(doms):
            x0 = 64 + i * (gw + gap)
            colour = {c: wheel[k % len(wheel)]
                      for k, c in enumerate(sorted(mask_classes))}
            out.append(txt(x0 + gw / 2, top - 14, name, size=12.5, weight=600,
                           pal=p, fill=p.ink, step=1))
            for gy in range(H):
                for gx in range(W):
                    c = fn(gx, gy)
                    out.append(rect(x0 + gx * cell, top + gy * cell,
                                    cell - 1, cell - 1, r=1.5, pal=p,
                                    fill=p.fill2 if c == 0 else p.faint,
                                    stroke="none", sw=0, step=1))
            # The mask, painted over the same cells.
            for gy in range(H):
                for gx in range(W):
                    c = fn(gx, gy)
                    if c in mask_classes:
                        out.append(rect(x0 + gx * cell, top + gy * cell,
                                        cell - 1, cell - 1, r=1.5, pal=p,
                                        fill=colour[c], stroke="none", sw=0,
                                        step=2))
            out.append(rect(x0 - 2, top - 2, gw + 2, gh + 2, r=4, pal=p,
                            fill="none", stroke=p.line, sw=1.0, step=1))
            out.append(txt(x0 + gw / 2, top + gh + 26, what, size=11, pal=p,
                           fill=p.ink3, step=2))

        out.append(txt(width / 2, height - 18,
                       "One operation, four fields. What changes is not the "
                       "arithmetic — it is which pixels count as the answer.",
                       size=13.5, weight=600, pal=p, fill=p.accent, step=3))
        return svg(width, height, "".join(out), pal=p, steps=3,
                   sim_label="mask")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ============================================ a box costs five numbers, a mask --

def box_vs_mask(fig_id, *, cap="", note="", width=1300, height=440, full=False,
                res=512):
    """Why you would ever detect, when segmentation is a strict superset.

    Because the answer is a cost, and a cost can be counted. A box is four
    coordinates and a class: five numbers per object. A mask is one label per
    pixel, whatever the resolution is. Both answer *where*; one of them is four
    orders of magnitude smaller, and that number is what the last layer has to
    emit and what a person has to annotate.

    Drawn as the same scene twice so the comparison is like for like: the boxes
    sit over the picture, the mask replaces it.
    """
    W, H = 16, 12
    # (x0, y0, x1, y1, class) in grid cells; class 2 = vehicle, 3 = person
    objs = [(1, 5, 5, 8, 2), (9, 4, 13, 7, 2), (6, 4, 7, 8, 3)]
    n_obj = len(objs)
    per_box = 5                       # x, y, w, h, class
    box_numbers = n_obj * per_box
    mask_labels = res * res

    def build(p):
        out = []
        cell = 15.0
        gw, gh = W * cell, H * cell
        top = 96.0
        lx = 96.0
        rx = width - 96.0 - gw

        def scene(x0, step, with_mask):
            for gy in range(H):
                for gx in range(W):
                    ground = gy >= 8
                    hit = None
                    for (a, b, c, d, k) in objs:
                        if a <= gx <= c and b <= gy <= d:
                            hit = k
                    if with_mask and hit:
                        col = p.accent if hit == 2 else p.warm
                    elif with_mask and ground:
                        col = p.good
                    elif with_mask:
                        col = p.fill2
                    else:
                        col = p.faint if (hit or ground) else p.fill2
                    out.append(rect(x0 + gx * cell, top + gy * cell, cell - 1,
                                    cell - 1, r=1.5, pal=p, fill=col,
                                    stroke="none", sw=0, step=step))
            out.append(rect(x0 - 2, top - 2, gw + 2, gh + 2, r=4, pal=p,
                            fill="none", stroke=p.line, sw=1.0, step=step))

        scene(lx, 1, False)
        scene(rx, 3, True)

        # boxes over the left scene
        for i, (a, b, c, d, k) in enumerate(objs):
            out.append(rect(lx + a * cell - 2, top + b * cell - 2,
                            (c - a + 1) * cell + 2, (d - b + 1) * cell + 2,
                            r=3, pal=p, fill="none",
                            stroke=p.accent if k == 2 else p.warm, sw=2.0,
                            step=2))
            out.append(txt(lx + a * cell + 2, top + b * cell - 8,
                           "car" if k == 2 else "person", size=10, pal=p,
                           fill=p.accent if k == 2 else p.warm, anchor="start",
                           step=2))

        out.append(txt(lx + gw / 2, top - 30, "detection", size=14, weight=600,
                       pal=p, fill=p.ink, step=1))
        out.append(txt(rx + gw / 2, top - 30, "segmentation", size=14,
                       weight=600, pal=p, fill=p.ink, step=3))

        cy = top + gh + 34
        out.append(txt(lx + gw / 2, cy,
                       f"{n_obj} objects × (x, y, w, h, class)", size=12.5,
                       pal=p, fill=p.ink3, step=2))
        out.append(txt(lx + gw / 2, cy + 30, f"{box_numbers} numbers", size=22,
                       weight=600, pal=p, fill=p.accent, step=2))
        out.append(txt(rx + gw / 2, cy, f"{res} × {res} pixels, one label each",
                       size=12.5, pal=p, fill=p.ink3, step=3))
        out.append(txt(rx + gw / 2, cy + 30,
                       f"{mask_labels:,} labels".replace(",", " "), size=22,
                       weight=600, pal=p, fill=p.good, step=3))

        mx = (lx + gw + rx) / 2
        out.append(txt(mx, top + gh / 2 - 12,
                       f"{mask_labels // box_numbers:,}×".replace(",", " "),
                       size=26, weight=600, pal=p, fill=p.ink, step=4))
        out.append(txt(mx, top + gh / 2 + 14, "more output", size=12, pal=p,
                       fill=p.ink3, step=4))
        out.append(txt(mx, top + gh / 2 + 32, "for the same", size=12, pal=p,
                       fill=p.ink3, step=4))
        out.append(txt(mx, top + gh / 2 + 50, "question", size=12, pal=p,
                       fill=p.ink3, step=4))

        out.append(txt(width / 2, height - 18,
                       "Both answer the same question. One of them is what the "
                       "last layer has to emit — and what a person has to annotate, "
                       "by hand, for every training image.",
                       size=13, pal=p, fill=p.accent, step=4))
        return svg(width, height, "".join(out), pal=p, steps=4,
                   sim_label="cost")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ==================================================== nested, drawn as nested --

def nested_sets(fig_id, rings, *, cap="", note="", width=1220, height=414,
                full=False):
    """Sets inside sets, drawn as sets inside sets.

    ``rings`` runs outermost first: ``(label, gloss)``. The reason this
    generator exists is that the slide it was written for says the four terms
    are *nested inside one another* and drew them as a top-to-bottom chain of
    four boxes -- which is the shape of a pipeline, not of containment. A
    reader who trusts the picture over the sentence learns the wrong thing, and
    pictures usually win.

    Revealed outermost-in, so the narrowing is something you watch happen.
    """
    n = len(rings)

    def build(p):
        out = []
        pad_x, pad_y = 60.0, 56.0
        ow, oh = width - 2 * pad_x, height - pad_y - 70
        dx = ow / (2.0 * n + 1.2)
        # Vertical insets are NOT symmetric. Each ring needs a band across its
        # top wide enough for a label and a line of gloss, and a symmetric
        # inset makes that band the same height as the side margin -- which is
        # how the first version drew every gloss underneath the next ring.
        head, tail = 52.0, 16.0
        tints = (p.fill, p.fill2, p.accent_fill, p.warm_fill)
        edges = (p.line, p.ink3, p.accent, p.warm)

        for i, (label, gloss) in enumerate(rings):
            st = i + 1
            x = pad_x + i * dx
            y = pad_y + i * head
            w = ow - 2 * i * dx
            h = oh - i * (head + tail)
            out.append(rect(x, y, w, h, r=16, pal=p,
                            fill=tints[i % len(tints)],
                            stroke=edges[i % len(edges)],
                            sw=1.6 if i else 1.3, step=st))
            innermost = i == n - 1
            lx = x + w / 2 if innermost else x + 16
            anchor = "middle" if innermost else "start"
            ly = y + h / 2 - 6 if innermost else y + 25
            out.append(txt(lx, ly, label, size=14.5 if innermost else 13.5,
                           weight=600, pal=p, fill=edges[i % len(edges)],
                           anchor=anchor, step=st))
            if gloss:
                out.append(txt(lx, ly + 18, gloss, size=11, pal=p, fill=p.ink3,
                               anchor=anchor, step=st))

        out.append(txt(width / 2, height - 24,
                       "Every ring is a strict subset of the one around it. "
                       "A chain of four boxes says something else entirely.",
                       size=12.5, pal=p, fill=p.accent, step=n))
        return svg(width, height, "".join(out), pal=p, steps=n,
                   sim_label="ring")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ====================================== what a conversation actually costs --

def context_growth(fig_id, *, cap="", note="", width=1290, height=440,
                   full=False, system=800, per_turn=350, turns=10):
    """Why an agent's bill grows faster than its conversation.

    The whole history is resent on every turn, so the context at turn *n* is
    the system prompt plus everything said so far -- and the tokens BILLED are
    the sum of all of those, not the size of the final conversation. That is a
    quadratic against a linear, and it is the single arithmetic fact that most
    changes how somebody builds an agent.

    Drawn as bars for the context at each turn, with the running total beside
    them, because the gap between the last bar and the total is the whole
    point.
    """
    ctx = [system + per_turn * k for k in range(turns)]
    billed = []
    run = 0
    for c in ctx:
        run += c
        billed.append(run)

    def build(p):
        out = []
        bx, by, bw, bh = 92.0, 92.0, 780.0, 246.0
        step_x = bw / turns
        top = max(ctx)

        out.append(txt(bx, 54, "isi konteks pada tiap giliran", size=13.5,
                       weight=600, pal=p, fill=p.ink, anchor="start", step=1))
        out.append(line(bx, by + bh, bx + bw, by + bh, pal=p, stroke=p.line,
                        sw=1.2, step=1))
        out.append(line(bx, by, bx, by + bh, pal=p, stroke=p.line, sw=1.2,
                        step=1))

        for t in range(turns):
            x = bx + t * step_x + 4
            w = step_x - 8
            st = 1 if t == 0 else (2 if t < 5 else 3)
            # the fixed part, and what the conversation has added to it
            hs = bh * system / top
            hh = bh * (ctx[t] - system) / top
            # p.ink3, not p.line: on the PRINT palette `line` and `accent` are
            # the same colour, so a two-part bar drawn with them came out as
            # one solid block in the PDF while looking correct on the web.
            out.append(rect(x, by + bh - hs, w, hs, r=2, pal=p, fill=p.ink3,
                            stroke="none", sw=0, step=st))
            out.append(rect(x, by + bh - hs - hh, w, hh, r=2, pal=p,
                            fill=p.accent, stroke="none", sw=0, step=st))
            if t in (0, 4, turns - 1):
                out.append(txt(x + w / 2, by + bh + 18, f"giliran {t + 1}",
                               size=10.5, pal=p, fill=p.ink3, step=st))

        ly = by + bh + 46
        for i, (col, lbl) in enumerate(((p.ink3, "perintah sistem + alat — tetap"),
                                        (p.accent, "riwayat percakapan — tumbuh"))):
            out.append(rect(bx + i * 300, ly - 9, 13, 13, r=3, pal=p, fill=col,
                            stroke="none", sw=0, step=1))
            out.append(txt(bx + i * 300 + 20, ly, lbl, size=11.5, pal=p,
                           fill=p.ink2, anchor="start", step=1))

        rx = bx + bw + 52
        out.append(txt(rx, by + 24, "percakapan akhir", size=12, pal=p,
                       fill=p.ink3, anchor="start", step=3))
        out.append(txt(rx, by + 52, f"{ctx[-1]:,}".replace(",", " ") + " token",
                       size=19, weight=600, pal=p, fill=p.accent,
                       anchor="start", step=3))
        out.append(txt(rx, by + 104, "yang ditagihkan", size=12, pal=p,
                       fill=p.ink3, anchor="start", step=3))
        out.append(txt(rx, by + 132, f"{billed[-1]:,}".replace(",", " ") + " token",
                       size=19, weight=600, pal=p, fill=p.bad, anchor="start",
                       step=3))
        out.append(txt(rx, by + 180,
                       f"{billed[-1] / ctx[-1]:.1f}× lipat", size=22, weight=600,
                       pal=p, fill=p.bad, anchor="start", step=3))

        out.append(txt(width / 2, height - 18,
                       "Percakapannya tumbuh lurus; tagihannya tumbuh kuadrat. "
                       "Tiap giliran membayar ulang semua giliran sebelumnya.",
                       size=13, weight=600, pal=p, fill=p.accent, step=3))
        return svg(width, height, "".join(out), pal=p, steps=3,
                   sim_label="giliran")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# ================================== what actually fits in a context window --

def token_budget(fig_id, *, cap="", note="", width=1290, height=400, full=False,
                 window=128_000, parts=None, turns=(5, 15, 30)):
    """A context window is a budget, and most of it is spent before turn one.

    Drawn because "128k tokens" sounds like room for anything, and the number
    that matters is what is LEFT after the fixed costs -- and how fast the
    remainder disappears as the run gets longer. Both are arithmetic, so both
    are computed here rather than asserted.
    """
    parts = parts or [
        ("perintah sistem + kebijakan", 4_000),
        ("skema 12 alat", 6_000),
        ("hasil alat per giliran (rerata)", 2_400),
    ]
    fixed = parts[0][1] + parts[1][1]
    per_turn = parts[2][1]

    def build(p):
        out = []
        bx, by, bw, bh = 84.0, 104.0, 980.0, 46.0
        gap = 62.0
        # NOT p.line here: on the print palette `line` and `accent` are the
        # same colour, so any figure that stacks the two reads as one block in
        # the PDF while looking correct on the web. Three visibly distinct
        # fills, checked on both palettes.
        cols = (p.ink3, p.warm, p.accent)

        out.append(txt(bx, 56, f"jendela {window // 1000}k token, dibelanjakan",
                       size=13.5, weight=600, pal=p, fill=p.ink, anchor="start",
                       step=1))

        for row, n in enumerate(turns):
            y = by + row * (bh + gap)
            used = fixed + per_turn * n
            st = row + 1
            out.append(txt(bx, y - 10, f"setelah {n} giliran", size=12, pal=p,
                           fill=p.ink3, anchor="start", step=st))
            out.append(rect(bx, y, bw, bh, r=6, pal=p, fill=p.fill,
                            stroke=p.line, sw=1.1, step=st))
            x = bx
            for i, (lbl, size) in enumerate(parts):
                amount = size * (n if i == 2 else 1)
                w = bw * amount / window
                out.append(rect(x, y, w, bh, r=0, pal=p, fill=cols[i],
                                stroke="none", sw=0, step=st))
                x += w
            left = window - used
            out.append(txt(bx + bw + 14, y + bh / 2 + 4,
                           f"sisa {left:,}".replace(",", " "), size=12.5,
                           mono=True, pal=p,
                           fill=p.good if left > window * 0.4 else p.bad,
                           anchor="start", step=st))
            pct = 100.0 * used / window
            out.append(txt(bx + 10, y + bh / 2 + 4, f"{pct:.0f}% terpakai",
                           size=12, weight=600, pal=p, fill=p.ink, anchor="start",
                           step=st))

        ly = by + len(turns) * (bh + gap) - 18
        for i, (lbl, _) in enumerate(parts):
            out.append(rect(bx + i * 340, ly - 9, 13, 13, r=3, pal=p,
                            fill=cols[i], stroke="none", sw=0, step=1))
            out.append(txt(bx + i * 340 + 20, ly, lbl, size=11.5, pal=p,
                           fill=p.ink2, anchor="start", step=1))

        out.append(txt(width / 2, height - 16,
                       f"{fixed:,}".replace(",", " ")
                       + " token sudah terpakai sebelum giliran pertama — dan "
                         "tiap alat yang ditambahkan memotong lagi.",
                       size=13, weight=600, pal=p, fill=p.accent,
                       step=len(turns)))
        return svg(width, height, "".join(out), pal=p, steps=len(turns),
                   sim_label="giliran")

    return _block(fig_id, build, cap=cap, note=note, full=full)


# =========================== sampling N times, and what it actually buys --

def vote_tradeoff(fig_id, *, cap="", note="", width=1290, height=452, full=False,
                  p_single=0.6, samples=(1, 3, 5, 7, 9, 15, 21)):
    """Ask N times and take the majority: exactly how much does that buy?

    This one is real arithmetic rather than an illustrative curve. If a single
    attempt is right with probability ``p``, then majority-of-N is right with
    the sum of the binomial terms above N/2 -- computed here, not sketched.

    The assumption doing the work is **independence**, and it is printed on the
    drawing because it is false in practice: samples from the same model on the
    same prompt correlate, so the curve is an UPPER BOUND. A figure that showed
    this as an achievable target would be lying by omission.
    """
    from math import comb

    def maj(n):
        return sum(comb(n, k) * p_single ** k * (1 - p_single) ** (n - k)
                   for k in range(n // 2 + 1, n + 1))

    acc = [maj(n) for n in samples]

    def build(p):
        out = []
        bx, by, bw, bh = 96.0, 96.0, 900.0, 240.0
        step_x = bw / len(samples)
        lo, hi = p_single - 0.04, 1.0

        out.append(txt(bx, 52, "peluang benar setelah suara terbanyak dari N contoh",
                       size=13.5, weight=600, pal=p, fill=p.ink, anchor="start",
                       step=1))
        out.append(txt(bx + 560, 52,
                       f"asumsi: satu contoh benar {p_single * 100:.0f}%, "
                       f"dan contohnya SALING BEBAS",
                       size=11.5, pal=p, fill=p.bad, anchor="start", step=1))

        out.append(line(bx, by + bh, bx + bw, by + bh, pal=p, stroke=p.line,
                        sw=1.2, step=1))
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            v = lo + (hi - lo) * frac
            y = by + bh - bh * frac
            out.append(line(bx, y, bx + bw, y, pal=p, stroke=p.faint, sw=0.7,
                            dash="2 5", step=1))
            out.append(txt(bx - 10, y + 4, f"{v * 100:.0f}%", size=10.5,
                           mono=True, pal=p, fill=p.ink3, anchor="end", step=1))

        for i, n in enumerate(samples):
            x = bx + i * step_x + step_x * 0.22
            w = step_x * 0.56
            h = bh * (acc[i] - lo) / (hi - lo)
            st = 1 if i == 0 else (2 if n <= 5 else 3)
            out.append(rect(x, by + bh - h, w, h, r=3, pal=p,
                            fill=p.accent if i else p.ink3, stroke="none",
                            sw=0, step=st))
            out.append(txt(x + w / 2, by + bh - h - 10, f"{acc[i] * 100:.1f}",
                           size=11, mono=True, pal=p, fill=p.ink, step=st))
            out.append(txt(x + w / 2, by + bh + 18, f"N={n}", size=11,
                           mono=True, pal=p, fill=p.ink3, step=st))
            out.append(txt(x + w / 2, by + bh + 36, f"{n}× biaya", size=10,
                           pal=p, fill=p.bad if n > 5 else p.ink3, step=st))

        rx = bx + bw + 44
        gain_1_5 = (acc[2] - acc[0]) * 100
        gain_5_21 = (acc[-1] - acc[2]) * 100
        out.append(txt(rx, by + 40, "N=1 → 5", size=12, pal=p, fill=p.ink3,
                       anchor="start", step=2))
        out.append(txt(rx, by + 66, f"+{gain_1_5:.1f} poin", size=17, weight=600,
                       pal=p, fill=p.good, anchor="start", step=2))
        out.append(txt(rx, by + 86, "dengan biaya 5×", size=11, pal=p,
                       fill=p.ink3, anchor="start", step=2))
        out.append(txt(rx, by + 132, "N=5 → 21", size=12, pal=p, fill=p.ink3,
                       anchor="start", step=3))
        out.append(txt(rx, by + 158, f"+{gain_5_21:.1f} poin", size=17,
                       weight=600, pal=p, fill=p.bad, anchor="start", step=3))
        out.append(txt(rx, by + 178, "dengan biaya 21×", size=11, pal=p,
                       fill=p.ink3, anchor="start", step=3))

        out.append(txt(bx, height - 40,
                       "Kenaikannya melandai; biayanya tidak. Dan karena contoh dari "
                       "model yang sama berkorelasi, angka di atas adalah BATAS ATAS —",
                       size=12.5, pal=p, fill=p.ink2, anchor="start", step=3))
        out.append(txt(bx, height - 20,
                       "yang sebenarnya didapat selalu lebih kecil dari ini.",
                       size=12.5, weight=600, pal=p, fill=p.bad, anchor="start",
                       step=3))
        return svg(width, height, "".join(out), pal=p, steps=3, sim_label="N")

    return _block(fig_id, build, cap=cap, note=note, full=full)
