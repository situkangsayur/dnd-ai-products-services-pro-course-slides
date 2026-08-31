#!/usr/bin/env python3
"""Measure real layout of every slide, in Chrome, over CDP.

Nothing here trusts a stylesheet reading. It loads each deck, walks every
slide, and reports three measured facts per slide:

    overflow_y  content taller than the slide box  -> text is cut or scrolls
    overflow_x  content wider than the box         -> text runs off the side
    overlaps    two block rectangles that intersect -> text on top of text

That last one is what "kotak-kotaknya crossing" means, and it is not something
you can see by reading CSS.
"""
import json, os, socket, subprocess, sys, time, urllib.request, base64, struct, threading

CHROME = "/usr/bin/google-chrome"
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5053"
DECKS = sys.argv[2].split(",") if len(sys.argv) > 2 else None
VIEWPORT = sys.argv[3] if len(sys.argv) > 3 else "1440x900"
W, H = (int(x) for x in VIEWPORT.split("x"))

def free_port():
    s = socket.socket(); s.bind(("", 0)); p = s.getsockname()[1]; s.close(); return p

PORT = free_port()
proc = subprocess.Popen(
    [CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
     "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
     f"--window-size={W},{H}", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait_devtools():
    """Attach to a PAGE target, not the browser target.

    The browser-level endpoint does not implement Page.* or Runtime.*, which
    fails with a confusing "'Page.enable' wasn't found" rather than anything
    about targets.
    """
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=1) as r:
                targets = json.load(r)
            pages = [t for t in targets if t.get("type") == "page"]
            if pages:
                return pages[0]["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.25)
    raise SystemExit("chrome devtools did not come up")

# --- minimal websocket client (no deps) ------------------------------------
class WS:
    def __init__(self, url):
        _, rest = url.split("://", 1)
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.s = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(("GET /" + path + " HTTP/1.1\r\n"
                        f"Host: {hostport}\r\nUpgrade: websocket\r\n"
                        "Connection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\n"
                        "Sec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self.id = 0

    def _recv(self, n):
        while len(self.buf) < n:
            self.buf += self.s.recv(65536)
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, obj):
        data = json.dumps(obj).encode()
        hdr = bytearray([0x81])
        mask = os.urandom(4)
        n = len(data)
        if n < 126: hdr.append(0x80 | n)
        elif n < 1 << 16: hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
        else: hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
        hdr += mask
        self.s.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def recv(self):
        b0, b1 = self._recv(2)
        n = b1 & 0x7F
        if n == 126: n = struct.unpack(">H", self._recv(2))[0]
        elif n == 127: n = struct.unpack(">Q", self._recv(8))[0]
        return json.loads(self._recv(n))

    def call(self, method, params=None):
        self.id += 1
        mid = self.id
        self.send({"id": mid, "method": method, "params": params or {}})
        while True:
            msg = self.recv()
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result", {})

ws = WS(wait_devtools())
ws.call("Page.enable"); ws.call("Runtime.enable")

MEASURE = r"""
(() => {
  const out = [];
  const deck = document.getElementById('deck');
  const slides = [...document.querySelectorAll('.slide')];
  const total = slides.length;
  for (let i = 0; i < total; i++) {
    // Drive the real navigation path: toggling .active by hand skips the
    // fit-to-height pass and measures a layout no viewer ever sees.
    if (window.deck && window.deck.show) window.deck.show(i);
    else {
      slides.forEach(s => s.classList.remove('active'));
      slides[i].classList.add('active');
    }
    const s = slides[i];

    /* Advance every simulator and run trace to its LAST step before measuring.
       A stepped figure and a code trace both change the slide's height as they
       run -- a run-trace panel can add four lines of note -- and a sweep that
       only ever sees step 0 reports a slide as fitting when its final step
       pushes the last line past the bottom edge. Found by stepping one slide
       by hand; the harness had said it was clean.

       Measured at the END rather than at every step because that is where the
       content is tallest: the reveal is cumulative, and the run panel is
       re-rendered rather than appended to, so the last step is the worst case
       for the figure and very nearly always for the panel too. */
    s.querySelectorAll('.sim-bar').forEach(bar => {
      const btns = [...bar.querySelectorAll('button')];
      const next = btns[btns.length - 1];
      if (!next) return;
      for (let k = 0; k < 24; k++) next.click();
    });

    const box = s.getBoundingClientRect();
    const cs = getComputedStyle(s);
    const padT = parseFloat(cs.paddingTop), padB = parseFloat(cs.paddingBottom);
    const padL = parseFloat(cs.paddingLeft), padR = parseFloat(cs.paddingRight);
    const availH = box.height - padT - padB;
    const availW = box.width - padL - padR;

    const host = s.querySelector('.sfit') || s;
    const kids = [...host.children].filter(el => {
      const r = el.getBoundingClientRect();
      const st = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && st.position !== 'absolute'
             && st.position !== 'fixed';
    });
    let contentH = 0, maxW = 0;
    kids.forEach(el => {
      const r = el.getBoundingClientRect();
      contentH = Math.max(contentH, r.bottom - (box.top + padT));
      maxW = Math.max(maxW, r.width);
    });
    // getBoundingClientRect already reflects the fit transform, so this is
    // the real painted overflow, not the pre-scale one.
    const availHreal = box.height - padT - padB;

    // real overlap between sibling block rects
    const rects = kids.map(el => ({ el: el.className || el.tagName,
                                    r: el.getBoundingClientRect() }));
    const overlaps = [];
    for (let a = 0; a < rects.length; a++)
      for (let b = a + 1; b < rects.length; b++) {
        const A = rects[a].r, B = rects[b].r;
        const ox = Math.min(A.right, B.right) - Math.max(A.left, B.left);
        const oy = Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top);
        if (ox > 1 && oy > 1)
          overlaps.push([rects[a].el, rects[b].el, Math.round(oy)]);
      }

    // absolutely-positioned furniture sitting on top of content
    const furniture = [...s.querySelectorAll('.snum, .sbrand')];
    let furnitureHit = 0;
    furniture.forEach(f => {
      const F = f.getBoundingClientRect();
      kids.forEach(el => {
        const R = el.getBoundingClientRect();
        const ox = Math.min(F.right, R.right) - Math.max(F.left, R.left);
        const oy = Math.min(F.bottom, R.bottom) - Math.max(F.top, R.top);
        if (ox > 1 && oy > 1) furnitureHit++;
      });
    });

    out.push({
      i,
      title: (s.querySelector('h1,h2') || {}).textContent?.slice(0, 60) || '',
      overflow_y: Math.round(contentH - availH),
      overflow_x: Math.round(maxW - availW),
      // NOT scrollHeight: a CSS transform does not change layout, so the
      // scroll box still reports the pre-shrink height and every fitted slide
      // looks broken. The fit pass sets .overflowing on the only slides that
      // genuinely do not fit -- those still too tall at MIN_SCALE.
      unfittable: s.classList.contains('overflowing') ? 1 : 0,
      fit: +(getComputedStyle(s.querySelector('.sfit')).transform
             .match(/matrix\(([\d.]+)/)?.[1] ?? 1),
      overlaps, furnitureHit,
    });
  }
  return out;
})()
"""

def audit(url):
    """Measure one deck, and refuse to call an empty answer a clean one.

    A fixed sleep after navigate was enough for one deck and not enough for
    twenty-two in a row: the sweep came back with an entry per deck and zero
    slides in each, and every total read as zero. An empty measurement is a
    failure to measure, not a pass.
    """
    ws.call("Page.navigate", {"url": url})
    # Wait for the slide count to STOP CHANGING, not merely to become non-zero.
    # A deck caught mid-render has one slide in the DOM and satisfies "> 0", so
    # the old guard let a 43-slide deck through as a 1-slide measurement --
    # which then reported zero problems and looked like a pass.
    last, stable = -1, 0
    for _ in range(80):
        time.sleep(0.25)
        r = ws.call("Runtime.evaluate",
                    {"expression": "document.querySelectorAll('.slide').length",
                     "returnByValue": True})
        n = r["result"].get("value") or 0
        if n and n == last:
            stable += 1
            if stable >= 3:
                break
        else:
            stable = 0
        last = n
    else:
        raise RuntimeError(f"slide count never settled (last={last}): {url}")
    ws.call("Runtime.evaluate",
            {"expression": "document.fonts.ready", "awaitPromise": True})
    time.sleep(0.4)
    r = ws.call("Runtime.evaluate",
                {"expression": MEASURE, "returnByValue": True,
                 "awaitPromise": True})
    out = r["result"].get("value") or []
    if not out:
        raise RuntimeError("measured zero slides: " + url)
    return out

with urllib.request.urlopen(f"{BASE}/slides/decks.json", timeout=5) as f:
    manifest = json.load(f)
ids = DECKS or [d["id"] for d in manifest["decks"]]

report, failed = {}, []
for did in ids:
    try:
        report[did] = audit(f"{BASE}/slides/{did}/index.html")
    except Exception as e:
        report[did] = [{"error": str(e)}]
        failed.append(did)

print(json.dumps(report))
if failed:
    print("MEASUREMENT FAILED for: " + ", ".join(failed), file=sys.stderr)
proc.terminate()
