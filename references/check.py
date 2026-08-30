#!/usr/bin/env python3
"""Re-fetch every link in REFERENCES.md and report what moved.

A reference list rots quietly: a regulator reorganises its site, a vendor
renames a page, and the citation still *looks* fine. This walks every URL in
the document and reports the ones that no longer resolve, so the rot is visible
rather than discovered by a participant mid-session.

It deliberately does not fail on a paywall or a bot-check: a 403 from iso.org
means the standard is still there and still costs money, which is what the
document already says.

    python3 check.py            # check every link
    python3 check.py --pdf      # also verify the local PDFs still parse
"""

import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "REFERENCES.md")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# A 403 from these is the expected answer, not a broken link.
EXPECT_BLOCKED = ("iso.org", "pearson.com")


def links(text):
    seen = {}
    for m in re.finditer(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", text):
        seen.setdefault(m.group(2), m.group(1))
    return seen


def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA},
                                 method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):          # HEAD refused; try a ranged GET
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": UA, "Range": "bytes=0-2048"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    return r.status, ""
            except Exception as e2:
                return getattr(e2, "code", 0), str(e2)[:60]
        return e.code, e.reason
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"[:70]


def main():
    with open(DOC, encoding="utf-8") as f:
        text = f.read()

    found = links(text)
    print(f"{len(found)} link(s) in REFERENCES.md\n")

    problems = 0
    for url, label in sorted(found.items()):
        status, note = check(url)
        blocked = any(d in url for d in EXPECT_BLOCKED)
        if 200 <= status < 400:
            mark = "ok  "
        elif status in (401, 403) and blocked:
            mark = "wall"                  # paywalled, as documented
        else:
            mark = "FAIL"
            problems += 1
        print(f"  {mark} {status or '---':>4}  {label[:44]:44s} {url[:60]}")
        if mark == "FAIL" and note:
            print(f"            {note}")

    if "--pdf" in sys.argv:
        print()
        pdfs = sorted(os.listdir(os.path.join(HERE, "pdf")))
        for name in pdfs:
            path = os.path.join(HERE, "pdf", name)
            with open(path, "rb") as f:
                head = f.read(5)
            size = os.path.getsize(path) / 1e6
            ok = head == b"%PDF-"
            if not ok:
                problems += 1
            print(f"  {'ok  ' if ok else 'FAIL'}  {size:6.1f} MB  {name}")

    print()
    if problems:
        print(f"{problems} link(s) or file(s) need attention.")
        return 1
    print("everything resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
