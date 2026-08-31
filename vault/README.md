# Vault export — for the p14s Obsidian vault

Markdown written for Obsidian, not for GitHub: `[[wikilinks]]` between notes,
frontmatter with tags, and one idea per file. Everything here is derived from
the Agentic AI module (`content/hendri_agentic.py`, 89 slides) and the
integrated demo (`ai-agentic-demo/integrated/`), condensed to the claims worth
keeping rather than the slides.

## Syncing it

The vault lives on **p14s**, and the destination is not `~/vault` — that path
does not exist there. It is a folder inside `MyNotes`, beside the BRI training
notes:

```
~/Documents/obsidian/MyNotes/my-research/phd/assisstance-and-lecturer/
    ai-professional-course/agentic-ai/     <- here
    bri-training-ai/                       <- the other course's notes
```

Copy the folder in whole; the notes only link to each other and to
`[[Agentic AI — index]]`, so nothing breaks if the surrounding vault differs.

```bash
DEST=~/Documents/obsidian/MyNotes/my-research/phd/assisstance-and-lecturer
ssh -p 1313 hendri@10.100.21.66 'echo ok'          # reachable? not always
rsync -av --delete -e 'ssh -p 1313' \
    course-slides/vault/agentic-ai/ \
    "hendri@10.100.21.66:$DEST/ai-professional-course/agentic-ai/"
```

Two things about that host, learned the tedious way: its login shell is
**fish**, so a `for` loop over SSH needs `bash -lc '…'`; and `--delete` is
deliberate here — the folder is a generated export, and a note left behind
after being renamed upstream is a broken wikilink nobody goes looking for.

## What is in it

| Note | The claim it carries |
|---|---|
| `Agentic AI — index.md` | The map. Start here. |
| `Workflow versus agent.md` | Who decides the next step |
| `The agent loop.md` | Plan, act, observe, check — and six ways to stop |
| `Tools are the permission boundary.md` | The model never touches anything |
| `When to split into multiple agents.md` | Three questions, and the cost table |
| `Components at three levels.md` | Minimum, best practice, production ready |
| `Tech stack and no-code.md` | Prototype in no-code, build in code |
| `MCP and A2A.md` | Inward against across |
| `Regulation — OJK, PDP, ISO.md` | Five instruments, one control set |
| `The SME credit demo.md` | The system, and what it proves |
| `Findings worth keeping.md` | Things that surprised me while building it |
| `Deck standard — adding a book.md` | The six checks a deck must pass, and what a second book costs |
