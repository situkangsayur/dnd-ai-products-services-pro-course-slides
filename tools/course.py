"""Course-wide facts, in one place.

Everything here is either verified against a primary source (an ITB / ITERA
staff page, the book's own site, an official repository) or taken from the
planning notes in ``riset/bri-training-ai/``. When a fact is not yet settled,
it is marked ``pending`` rather than guessed at.
"""

import os as _os

COURSE = {
    "title": "Designing and Building AI Products and Services",
    "tagline": "AI for Professional",
    "by": "ITB Team",
    "org": "Institut Teknologi Bandung",
    # "Berkelanjutan" is SUSTAINABLE, not continuous. The English rendering
    # people reach for -- "Continuing Professional Education", after the CPD
    # convention -- is the wrong word for this directorate's name, and it is on
    # every deck cover and every notebook footer, so it is worth getting right.
    "unit": "Directorate of Sustainable Professional Education",
    "format": "Microcredential · hybrid · paid",
    # 6 sks, 1 sks = 45 jam, dipecah
    # 15 jam kuliah + 15 jam exercise + 15 jam independent study per sks.
    "credits": "6 credits (equivalent to two master's-level courses)",
    "hours": "1 credit = 45 hours · 15 h lecture + 15 h exercise + 15 h independent study",
    "assessment": "Group assignments, presentations, and supervision. No written exam.",
    "start": "September 2026",
}

# ---------------------------------------------------------------- the team ---
# Prof. Bambang: https://stei.itb.ac.id/en/dosen/bambang-riyanto-trilaksono/
# Rahman:        https://if.itera.ac.id/dosen-rahman-indra-kesuma/
# Viny:          https://untar.ac.id/en/leaders/study-programs/viny-christanti/
#                https://scholar.google.com/citations?user=hayqUI0AAAAJ
# Hendri:        https://hendrikarisma.my.id
#
# Two corrections made 2026-08-30, both from the person concerned:
#   * Viny's full name and affiliation were confirmed and are no longer pending.
#     Untar's own leadership page writes her as "Viny Christanti Mawardi,
#     S.Kom., M.Kom." and lists her as head of the Informatics Engineering
#     study programme in the Faculty of Information Technology.
#   * Doctoral standing differs across the three assistants and the words are
#     not interchangeable: "candidate" means the qualifying stage has been
#     passed. Rahman and Viny are Doctoral Candidates at STEI ITB; Hendri is a
#     Doctoral Student there. Getting somebody's own standing wrong on their own
#     course page is exactly the kind of small error an audience notices.
#   * The doctoral line comes first in all three affiliations. It is the thing
#     they share, it is why they are teaching on this course, and burying it
#     behind a job title made three colleagues look like three unrelated people.
TEAM = [
    {
        "key": "bambang",
        "name": "Prof. Bambang Riyanto Trilaksono",
        "role": "Lead Instructor",
        "aff": "Professor, School of Electrical Engineering and Informatics (STEI) ITB · "
               "Head of the Control and Computer Systems Research Group · "
               "co-founder of the ITB Center for Artificial Intelligence",
        "url": "https://stei.itb.ac.id/en/dosen/bambang-riyanto-trilaksono/",
        "topics": "Concepts, theory, and modelling (morning sessions)",
    },
    {
        "key": "rahman",
        "name": "Rahman Indra Kesuma, S.Kom., M.Cs.",
        "role": "Teaching Assistant",
        "aff": "Doctoral Candidate, STEI ITB · Lecturer in Informatics "
               "Engineering, Institut Teknologi Sumatera (ITERA) · artificial "
               "intelligence and data engineering",
        "url": "https://if.itera.ac.id/dosen-rahman-indra-kesuma/",
        "topics": "Topic 2 — Machine Learning · Topic 3 — Deep Learning",
    },
    {
        "key": "viny",
        "name": "Viny Christanti Mawardi, S.Kom., M.Kom.",
        "role": "Teaching Assistant",
        "aff": "Doctoral Candidate, STEI ITB · Head of the Informatics "
               "Engineering study programme, Faculty of Information Technology, "
               "Universitas Tarumanagara (Untar) · information retrieval and "
               "natural language processing",
        "url": "https://untar.ac.id/en/leaders/study-programs/viny-christanti/",
        "topics": "Topic 4 — LLMs, fine-tuning, and RAG",
    },
    {
        "key": "hendri",
        "name": "Hendri Karisma, M.T.",
        "role": "Teaching Assistant",
        "aff": "Doctoral Student, STEI ITB · VP of Engineering, Jejakin · "
               "Lecturer in Informatics, STMIK Tazkia",
        "url": "https://hendrikarisma.my.id",
        "topics": "Topic 6 — Agentic AI",
    },
]

# ---------------------------------------------------------------- the book ---
BOOK = {
    "title": "Deep Learning with Python",
    "edition": "Third Edition",
    "authors": "François Chollet & Matthew Watson",
    "publisher": "Manning Publications",
    "isbn": "9781633436589",
    "site": "https://deeplearningwithpython.io/",
    "chapters_url": "https://deeplearningwithpython.io/chapters/",
    "code_repo": "https://github.com/fchollet/deep-learning-with-python-notebooks",
    "note": "The third-edition code is written with Keras 3 and runs on top of "
            "JAX, TensorFlow, or PyTorch.",
}

CH_SLUG = {
    1: "chapter01_what-is-deep-learning",
    2: "chapter02_mathematical-building-blocks",
    3: "chapter03_introduction-to-ml-frameworks",
    4: "chapter04_classification-and-regression",
    5: "chapter05_fundamentals-of-ml",
    6: "chapter06_universal-workflow-of-ml",
    7: "chapter07_deep-dive-keras",
    8: "chapter08_image-classification",
    9: "chapter09_convnet-architecture-patterns",
    10: "chapter10_interpreting-what-convnets-learn",
    11: "chapter11_image-segmentation",
    12: "chapter12_object-detection",
    13: "chapter13_timeseries-forecasting",
    14: "chapter14_text-classification",
    15: "chapter15_language-models-and-the-transformer",
    16: "chapter16_text-generation",
    17: "chapter17_image-generation",
    18: "chapter18_best-practices-for-the-real-world",
    19: "chapter19_future_of_ai",
    20: "chapter20_conclusion",
}

# Chapters the official repository ships a notebook for. Chapters 1, 6, 19 and
# 20 carry no code in the book itself, so there is nothing upstream to link to.
CH_HAS_OFFICIAL_NB = set(CH_SLUG) - {1, 6, 19, 20}


def chapter_url(n):
    return BOOK["site"].rstrip("/") + "/chapters/" + CH_SLUG[n]


def official_nb_url(n):
    if n not in CH_HAS_OFFICIAL_NB:
        return None
    return f"{BOOK['code_repo']}/blob/master/{CH_SLUG[n]}.ipynb"


def book_source(n):
    return (f"Chollet & Watson, \\emph{{Deep Learning with Python}} 3e, bab {n}"
            if False else
            f"Chollet & Watson, Deep Learning with Python 3e — bab {n}")


# ============================================================== deployment ====
# Every address the decks point at, in one place, each overridable from the
# environment. They appear on all twenty chapter decks, so correcting one in
# twenty content files afterwards is how half of them end up stale.
#
#     COURSE_NOTEBOOK_BASE=https://example.org/nb \
#     COURSE_JUPYTER_BASE=http://10.100.21.22:8888 \
#     python3 tools/build.py
#
# Set any of them empty to fall back to relative paths and drop the chip, which
# is what you want when reading the decks straight off a checkout with no site
# and no server in front of them.

# Rendered, browsable notebooks. **HTML, not .ipynb**: a link to a raw notebook
# does not open a notebook, it downloads a file. Built by tools/nb_html.py.
NOTEBOOK_BASE = _os.environ.get(
    "COURSE_NOTEBOOK_BASE",
    "https://hendrikarisma.my.id/rs/ai-products-course/notebooks").rstrip("/")

# A live JupyterLab the participants can actually run the notebook in. Empty by
# default: pointing a deck at a server that is not up is worse than not
# offering the link, because the audience finds out mid-session. Set it once
# the lab is running, e.g. COURSE_JUPYTER_BASE=http://10.100.21.22:8888
JUPYTER_BASE = _os.environ.get("COURSE_JUPYTER_BASE", "").rstrip("/")

# Where the notebooks live inside that lab's working directory. JupyterLab
# addresses files by path from the directory it was started in, so this has to
# match how the server was launched, not where the files are on your laptop.
JUPYTER_ROOT = _os.environ.get("COURSE_JUPYTER_ROOT", "notebooks").strip("/")


def notebook_url(n, name):
    """Link to one notebook of chapter ``n``, as something a browser will open.

    **Published as HTML, not as .ipynb.** A link to a raw notebook does not open
    a notebook, it downloads a file -- which is what a chip on a slide used to
    do. The rendered pages come from ``tools/nb_html.py``; the layout mirrors
    the repository, so the path is derived rather than listed.

    Falls back to the relative ``.ipynb`` path when no base URL is configured,
    which is what you want when reading a checkout with no site in front of it.
    """
    if not NOTEBOOK_BASE:
        return f"../../notebooks/ch{n:02d}/{name}"
    page = name[:-6] + ".html" if name.endswith(".ipynb") else name
    return f"{NOTEBOOK_BASE}/ch{n:02d}/{page}"


def jupyter_url(n, name):
    """Open one notebook in a running JupyterLab, or None if none is configured.

    JupyterLab's own URL scheme: ``/lab/tree/<path>`` relative to the directory
    the server was started in. Returns None rather than a guess when no lab is
    configured, and the caller drops the chip -- a dead link on a slide is
    discovered by the room, not by you.
    """
    if not JUPYTER_BASE:
        return None
    root = f"{JUPYTER_ROOT}/" if JUPYTER_ROOT else ""
    return f"{JUPYTER_BASE}/lab/tree/{root}ch{n:02d}/{name}"


def notebook_index_url(n=None):
    """The notebook index, anchored at a chapter when one is given."""
    if not NOTEBOOK_BASE:
        return "../../notebooks/"
    anchor = f"#ch{n:02d}" if n else ""
    return f"{NOTEBOOK_BASE}/index.html{anchor}"


def chapter_resources(n, local_notebooks=()):
    """Standard resource row for a chapter deck."""
    res = [{"kind": "book", "label": f"Chapter {n} — full text",
            "href": chapter_url(n)}]
    for nb in local_notebooks:
        res.append({"kind": "notebook", "label": nb,
                    "href": notebook_url(n, nb)})
    if local_notebooks:
        res.append({"kind": "notebook",
                    "label": f"All chapter {n} notebooks",
                    "href": notebook_index_url(n)})
        lab = jupyter_url(n, local_notebooks[0])
        if lab:
            res.append({"kind": "lab",
                        "label": "Run it — JupyterLab", "href": lab})
    up = official_nb_url(n)
    if up:
        res.append({"kind": "github", "label": "Author's official notebook", "href": up})
    return res


def presenters(deck):
    """The people delivering a deck, always as a list.

    A chapter can be taught by two people, and the cover has to say so. Older
    decks carry a single dict; both shapes are accepted here rather than
    migrated, because the content files are the source of truth and churning
    twenty of them to change a data shape is churn for its own sake.
    """
    p = deck.get("presenter")
    if not p:
        return []
    return list(p) if isinstance(p, list) else [p]


def presenter_names(deck, sep=" \u00b7 "):
    return sep.join(x.get("name", "") for x in presenters(deck) if x.get("name"))


def presenter_roles(deck):
    """Distinct roles, in order of appearance."""
    seen, out = set(), []
    for x in presenters(deck):
        r = x.get("role", "")
        if r and r not in seen:
            seen.add(r)
            out.append(r)
    return " \u00b7 ".join(out)
