# Vault export — for the p14s Obsidian vault

Markdown written for Obsidian, not for GitHub: `[[wikilinks]]` between notes,
frontmatter with tags, and one idea per file. Everything here is derived from
the Agentic AI module (`content/hendri_agentic.py`, 89 slides) and the
integrated demo (`ai-agentic-demo/integrated/`), condensed to the claims worth
keeping rather than the slides.

## Syncing it

The vault lives on p14s. Copy the folder in whole; the notes only link to each
other and to `[[Agentic AI — index]]`, so nothing breaks if the surrounding
vault is different.

```bash
rsync -av --delete course-slides/vault/agentic-ai/ \
    -e 'ssh -p 1313' hendri@10.100.21.66:~/vault/agentic-ai/
```

Check the host is reachable first — it has not always been:

```bash
ssh -p 1313 hendri@10.100.21.66 'echo ok'
```

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
