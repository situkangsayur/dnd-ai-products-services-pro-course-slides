#!/usr/bin/env python3
"""Compare a local vault file against the copy on p14s, structurally.

Loosening the prose of a note must not move a heading, drop a table row, break a
mermaid fence, or lose a link. Rewriting a long document by hand does all four
sooner or later, and none of them are visible in a skim. So count the things
that carry meaning, before and after, and report only what moved -- leaving a
diff that is purely prose.

    python3 structcheck.py 03-arsitektur-agent-dan-tools.md

Run it from the directory holding the edited copies. Headings are allowed to
differ: a heading is prose too, and loosening it is the point. Everything else
changing is a bug in the edit.
"""
import os
import re
import subprocess
import sys

def profile(text):
    return {
        "headings": [l.strip() for l in text.splitlines() if l.startswith("#")],
        "table_rows": sum(1 for l in text.splitlines()
                          if l.strip().startswith("|") and not re.match(r"^\|[\s:|-]+\|$", l.strip())),
        "fences": text.count("```"),
        "mermaid": text.count("```mermaid"),
        "links": sorted(re.findall(r"\]\((https?://[^)\s]+)\)", text)),
        "backticked": sorted(set(re.findall(r"`([^`\n]+)`", text))),
        "checkboxes": text.count("- [ ]") + text.count("- [x]"),
    }

for name in sys.argv[1:]:
    remote = os.environ.get(
        "VAULT_REMOTE_DIR",
        "Documents/obsidian/MyNotes/my-research/phd/"
        "assisstance-and-lecturer/bri-training-ai")
    old = subprocess.run(["ssh", "-o", "BatchMode=yes",
                          os.environ.get("VAULT_HOST", "p14s"),
                          f"cat '{remote}/{name}'"],
                         capture_output=True, text=True).stdout
    new = open(name, encoding="utf-8").read()
    a, b = profile(old), profile(new)
    problems = []
    if a["headings"] != b["headings"]:
        lost = [h for h in a["headings"] if h not in b["headings"]]
        added = [h for h in b["headings"] if h not in a["headings"]]
        problems.append(f"headings changed: -{len(lost)} +{len(added)}")
        for h in (lost + added)[:6]:
            problems.append(f"    {h[:80]}")
    for k in ("table_rows", "fences", "mermaid", "checkboxes"):
        if a[k] != b[k]:
            problems.append(f"{k}: {a[k]} -> {b[k]}")
    lost_links = set(a["links"]) - set(b["links"])
    if lost_links:
        problems.append(f"links lost: {sorted(lost_links)[:5]}")
    lost_code = set(a["backticked"]) - set(b["backticked"])
    if lost_code:
        problems.append(f"code spans lost ({len(lost_code)}): {sorted(lost_code)[:8]}")
    print(f"{name}: {'OK' if not problems else 'CHECK'}")
    for p in problems:
        print("   " + p)
