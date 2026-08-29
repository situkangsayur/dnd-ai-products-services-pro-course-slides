# Course notebooks

One folder per deck, one notebook per topic, 67 in all. They are **generated**
from specs under `content/notebooks/` — see `tools/build_notebooks.py`.

## Running them

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r notebooks/requirements.txt
jupyter lab notebooks/
```

Every notebook opens with what it needs and roughly how long it takes, and links
back to the slides it accompanies. Where a cell is expensive, the expected
output is written into the notebook as **markdown**, so you can read through it
without running it.

## Two conventions worth knowing

**No stored outputs.** A committed notebook here has no execution counts and no
output blobs. What you see on opening is what the author wrote; what appears
after you run it is what your machine produced. In teaching material those two
should never be confused — and it keeps the diffs reviewable.

**Expected output is markdown, not a fake result.** When a notebook shows what a
cell should print, it does so in a fenced block labelled *Expected output*, never
as a stored cell output pretending to be yours.

## Rebuilding

```bash
python3 tools/build_notebooks.py          # all
python3 tools/build_notebooks.py ch15     # one chapter
```

The build cross-checks the filenames against the notebook links each deck
declares. A deck that links to a notebook nobody wrote, or a notebook nothing
links to, is reported rather than shipped.
