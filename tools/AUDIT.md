# Measuring the decks in a browser

Three things about a slide deck cannot be checked from the source, because they
only happen when a browser lays the page out:

| Script | Finds | Why the build cannot |
|---|---|---|
| `clip.py` | mermaid labels cut off inside their box | mermaid fixes the box size at render time; the page then re-flows the text inside it |
| `small.py` | figures rendering below 55% of drawn size | a tall figure is scaled to fit and letterboxed — the SVG is valid and the slide does not overflow |
| `audit.py` | slides whose content is truncated or overlapping | the fit pass runs in the browser |

```bash
python3 -m http.server 5053 --directory ../course-web/site &   # or the systemd unit
python3 tools/clip.py  http://127.0.0.1:5053
python3 tools/small.py http://127.0.0.1:5053
python3 tools/small.py http://127.0.0.1:5053 ch15,ch16        # just these
```

Needs Google Chrome on `PATH`; `cdp.py` drives it over the DevTools protocol
with a hand-written websocket client and no dependencies.

## Three traps, all of which produced wrong answers here

**A hidden slide measures as zero.** `display: none` gives every child no
dimensions, so a sweep that does not call `window.deck.show(i)` first reports a
clean bill of health for a deck full of clipped labels. Both scripts show each
slide before measuring it.

**Measure the drawing, not the element.** `preserveAspectRatio="meet"` fits the
drawing *inside* the element box, so a 1330px-wide element can contain a 157px
drawing. Measuring the element says the figure is fine; measuring the drawing
says it renders at 12%.

**A declared number is not a measured one.** `SLIDE_FIG_H` was first set to
480 by reading it off the stylesheet. The height a figure actually gets depends
on what shares the slide with it, and the browser was handing out about 270.
Thirty tall diagrams passed the check because the check was asking the wrong
question. It is the same mistake as the bug the harness was built to catch, one
level up: read the number off the page, never off the rule that produced it.

That trap has a sibling worth naming, because it hid for the whole build. The
fit pass widens `.sfit` to `(100/k)%` and then scales it by `k`, so the line
length survives the shrink. With `transform-origin: top center` the widened box
was scaled about its middle, which pushed every auto-fitted slide about 300px to
the right and hung the overhang off the edge of the screen. Nothing reported it:
`overflow_x` came back as 1px of rounding, and the figures inside were
letterboxed rather than cropped, so they measured as "fits". A screenshot found
it in one look. **Look at a slide occasionally; the metrics only answer the
question you thought to ask.** The origin is now `top left`.

The guard for that fourth trap has already paid for itself once: a later
sweep came back reporting **1 113 slides measured and zero problems** for a
build with 1 169 slides, and the line `MEASUREMENT FAILED for: ch01` under it.
Without that line the missing 56 slides would have been invisible — the totals
looked perfect. Read the failure list before the totals, and check that the
slide count is the one you expect.

And one flake worth knowing: **wait for the webfonts.** Measuring before they
land reports phantom clipping — the fallback face is wider, every label
overflows, and the next run comes back clean. Both scripts await
`document.fonts.ready`.
