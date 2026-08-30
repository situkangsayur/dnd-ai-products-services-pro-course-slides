"""A tiny Chrome DevTools Protocol client — no dependencies.

Split out of audit.py because importing that module ran the whole audit as a
side effect. A file that does work at import time cannot be reused, which is
the entire reason this one exists.
"""
import base64, json, os, socket, struct, subprocess, time, urllib.request


def free_port():
    s = socket.socket(); s.bind(("", 0)); p = s.getsockname()[1]; s.close()
    return p


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



def launch(width=1200, height=900):
    """Start headless Chrome and attach to a PAGE target."""
    port = free_port()
    proc = subprocess.Popen(
        ["/usr/bin/google-chrome", "--headless=new",
         f"--remote-debugging-port={port}", "--no-sandbox", "--disable-gpu",
         "--hide-scrollbars", f"--window-size={width},{height}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(80):
        try:
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/json/list", timeout=1) as r:
                pages = [t for t in json.load(r) if t.get("type") == "page"]
            if pages:
                ws = WS(pages[0]["webSocketDebuggerUrl"])
                ws.call("Page.enable"); ws.call("Runtime.enable")
                return proc, ws
        except Exception:
            pass
        time.sleep(0.25)
    proc.terminate()
    raise SystemExit("chrome devtools did not come up")
