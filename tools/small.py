#!/usr/bin/env python3
"""Find figures that render too small to read.

A tall diagram on a wide slide is capped by max-height and shrinks until it
fits. The build cannot see that -- the SVG is fine, the slide does not
overflow, and nothing warns. It only shows up as a lecturer squinting.

So measure the rendered size against the size the figure was drawn at. A
figure rendering below about 55% of its natural width is one nobody at the back
of the room can read.

    python3 small.py http://127.0.0.1:5053           # every deck
"""
import json
import re
import sys
import time
import urllib.request

from cdp import launch

args = [a for a in sys.argv[1:] if not a.startswith("--")]
BASE = args[0] if args else "http://127.0.0.1:5053"
DECKS = args[1].split(",") if len(args) > 1 else None

MEASURE = r"""
(() => {
  const out = [];
  const n = window.deck ? window.deck.total : 0;
  const slides = [...document.querySelectorAll('.slide')];
  const back = window.deck ? window.deck.index : 0;
  for (let i = 0; i < n; i++) {
    window.deck.show(i);
    const sl = slides[i];
    if (!sl) continue;
    sl.querySelectorAll('.fig svg').forEach(svg => {
      const vb = (svg.getAttribute('viewBox') || '').split(/\s+/);
      const natW = parseFloat(vb[2]) || 0, natH = parseFloat(vb[3]) || 0;
      if (!natW) return;
      const r = svg.getBoundingClientRect();
      if (!r.width) return;
      // preserveAspectRatio="meet" fits the drawing INSIDE the element box, so
      // a tall figure in a wide box is letterboxed: the element is 1330 wide
      // and the drawing inside it is 157. Measuring the element says the
      // figure is fine. The scale that matters is the smaller of the two.
      const ratio = Math.min(r.width / natW, r.height / natH);
      const tall = natH / natW;
      out.push({slide: i + 1,
                title: (sl.querySelector('h2') || {}).textContent || '',
                natW: Math.round(natW), natH: Math.round(natH),
                w: Math.round(r.width), h: Math.round(r.height),
                ratio: +ratio.toFixed(2), tall: +tall.toFixed(2)});
    });
  }
  window.deck.show(back);
  return out;
})()
"""

proc, ws = launch(1440, 900)
try:
    ws.call("Network.enable", {})
    ws.call("Network.setCacheDisabled", {"cacheDisabled": True})
    with urllib.request.urlopen(f"{BASE}/slides/decks.json", timeout=5) as f:
        manifest = json.load(f)
    ids = DECKS or [d["id"] for d in manifest["decks"]]

    worst = []
    for did in ids:
        ws.call("Page.navigate", {"url": f"{BASE}/slides/{did}/index.html"})
        time.sleep(1.6)
        # Wait for the webfonts. Measuring before they land reports phantom
        # clipping: the fallback face is wider, every label overflows, and the
        # next run comes back clean -- which is a very good way to spend twenty
        # minutes chasing a regression that was never there.
        ws.call("Runtime.evaluate",
                {"expression": "document.fonts.ready.then(()=>true)",
                 "awaitPromise": True, "returnByValue": True})
        time.sleep(0.4)
        rows = (ws.call("Runtime.evaluate",
                        {"expression": MEASURE, "returnByValue": True})
                ["result"].get("value") or [])
        small = [r for r in rows if r["ratio"] < 0.55]
        print(f"{did:16s} {len(rows):3d} figures, {len(small):3d} rendering small")
        for r in sorted(small, key=lambda r: r["ratio"])[:6]:
            print(f"      #{r['slide']:<3d} {r['ratio']:.2f}x  "
                  f"{r['w']}x{r['h']} of {r['natW']}x{r['natH']} "
                  f"(aspect {r['tall']})  {r['title'][:40]}")
        worst += [(did, r) for r in small]
    print(f"\nTOTAL {len(worst)} figures rendering below 55% of drawn size")
finally:
    proc.terminate()
