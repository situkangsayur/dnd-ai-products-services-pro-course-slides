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

## Two traps, both of which produced wrong answers here

**A hidden slide measures as zero.** `display: none` gives every child no
dimensions, so a sweep that does not call `window.deck.show(i)` first reports a
clean bill of health for a deck full of clipped labels. Both scripts show each
slide before measuring it.

**Measure the drawing, not the element.** `preserveAspectRatio="meet"` fits the
drawing *inside* the element box, so a 1330px-wide element can contain a 157px
drawing. Measuring the element says the figure is fine; measuring the drawing
says it renders at 12%.

And one flake worth knowing: **wait for the webfonts.** Measuring before they
land reports phantom clipping — the fallback face is wider, every label
overflows, and the next run comes back clean. Both scripts await
`document.fonts.ready`.
