#!/usr/bin/env python3
"""Measure every mermaid label in every deck against the box it is drawn in.

mmdc writes a fixed-size foreignObject based on its own measurement, and the
browser then lays the text out again inside that fixed box. When the two
disagree the text is silently cut -- no error, no warning, and it only shows up
on a projector. So the check has to happen in a real browser.

    python3 clip.py http://127.0.0.1:5053              # every deck
    python3 clip.py http://127.0.0.1:5053 ch01,ch02    # just these
"""
import json
import sys
import time
import urllib.request

from cdp import launch

args = [a for a in sys.argv[1:] if not a.startswith("--")]
BASE = args[0] if args else "http://127.0.0.1:5053"
DECKS = args[1].split(",") if len(args) > 1 else None

# A hidden slide has no layout: display:none makes every child report zero, so
# a sweep that does not SHOW each slide first reports a clean bill of health for
# a deck full of clipped labels. Ask the deck to show each slide, measure, then
# put it back where it was.
MEASURE = r"""
(() => {
  const out = [];
  const back = window.deck ? window.deck.index : 0;
  const n = window.deck ? window.deck.total : 0;
  const slides = [...document.querySelectorAll('.slide')];
  for (let i = 0; i < n; i++) {
    window.deck.show(i);
    const sl = slides[i];
    if (!sl) continue;
    sl.querySelectorAll('foreignObject').forEach(fo => {
      const kid = fo.firstElementChild;
      if (!kid) return;
      const text = (kid.textContent || '').trim().replace(/\s+/g, ' ');
      if (!text) return;
      const haveW = parseFloat(fo.getAttribute('width')) || 0;
      const haveH = parseFloat(fo.getAttribute('height')) || 0;
      const needW = kid.scrollWidth, needH = kid.scrollHeight;
      const overW = needW - haveW, overH = needH - haveH;
      if (overW > 1.5 || overH > 1.5) {
        out.push({slide: i, text: text.slice(0, 44),
                  overW: Math.round(overW), overH: Math.round(overH)});
      }
    });
  }
  window.deck.show(back);
  return out;
})()
"""

proc, ws = launch(1440, 900)
try:
    # Without this the stylesheet is served from the browser cache and a CSS
    # fix appears to do nothing -- which is a very convincing way to conclude
    # the wrong thing about the bug.
    ws.call("Network.enable", {})
    ws.call("Network.setCacheDisabled", {"cacheDisabled": True})
    with urllib.request.urlopen(f"{BASE}/slides/decks.json", timeout=5) as f:
        manifest = json.load(f)
    ids = DECKS or [d["id"] for d in manifest["decks"]]

    total = 0
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
        r = ws.call("Runtime.evaluate",
                    {"expression": MEASURE, "returnByValue": True})
        rows = r["result"].get("value") or []
        total += len(rows)
        worst = max((x["overW"] for x in rows), default=0)
        worstH = max((x["overH"] for x in rows), default=0)
        flag = "" if not rows else f"   worst +{worst}w +{worstH}h"
        print(f"{did:16s} {len(rows):4d} clipped{flag}")
        for x in rows[:4]:
            print(f"      s{x['slide']:<3d} +{x['overW']}w +{x['overH']}h  {x['text']!r}")
    print(f"\nTOTAL {total} clipped labels")
finally:
    proc.terminate()
