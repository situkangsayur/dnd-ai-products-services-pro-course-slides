"""Course-wide facts, in one place.

Everything here is either verified against a primary source (an ITB / ITERA
staff page, the book's own site, an official repository) or taken from the
planning notes in ``riset/bri-training-ai/``. When a fact is not yet settled,
it is marked ``pending`` rather than guessed at.
"""

COURSE = {
    "title": "Designing and Building AI Products and Services",
    "tagline": "AI for Professional",
    "by": "ITB Team",
    "org": "Institut Teknologi Bandung",
    "unit": "Directorate of Continuing Professional Education",
    "partner": "PT Bank Rakyat Indonesia (Persero) Tbk",
    "format": "Microcredential · hybrid · paid",
    # From BRI-diskusi-20-08-2026: 6 sks, 1 sks = 45 jam, dipecah
    # 15 jam kuliah + 15 jam exercise + 15 jam independent study per sks.
    "credits": "6 credits (equivalent to two master's-level courses)",
    "hours": "1 credit = 45 hours · 15 h lecture + 15 h exercise + 15 h independent study",
    "assessment": "Group assignments, presentations, and supervision. No written exam.",
    "start": "September 2026",
}

# ---------------------------------------------------------------- the team ---
# Prof. Bambang: https://stei.itb.ac.id/en/dosen/bambang-riyanto-trilaksono/
# Rahman:        https://if.itera.ac.id/dosen-rahman-indra-kesuma/
# Hendri:        https://hendrikarisma.my.id
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
        "aff": "Lecturer in Informatics Engineering, Institut Teknologi Sumatera (ITERA) · "
               "Artificial Intelligence and Data Engineering",
        "url": "https://if.itera.ac.id/dosen-rahman-indra-kesuma/",
        "topics": "Topic 2 — Machine Learning · Topic 3 — Deep Learning",
    },
    {
        "key": "viny",
        "name": "Viny",
        "role": "Teaching Assistant",
        "aff": "Doctoral candidate · research focus on large language models, "
               "fine-tuning, RAG, re-rankers, and guardrails",
        "url": "https://scholar.google.com/citations?user=hayqUI0AAAAJ&hl=en",
        "topics": "Topic 4 — LLMs, fine-tuning, and RAG",
        # Full name not yet confirmed; the Scholar profile blocks automated
        # fetching. Flagged so it is not read as a verified fact.
        "name_pending": True,
    },
    {
        "key": "hendri",
        "name": "Hendri Karisma, M.T.",
        "role": "Teaching Assistant",
        "aff": "VP of Engineering, Jejakin · Doctoral candidate, STEI ITB",
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


def chapter_resources(n, local_notebooks=()):
    """Standard resource row for a chapter deck."""
    res = [{"kind": "book", "label": f"Chapter {n} — full text",
            "href": chapter_url(n)}]
    for nb in local_notebooks:
        res.append({"kind": "notebook", "label": nb,
                    "href": f"../../notebooks/ch{n:02d}/{nb}"})
    up = official_nb_url(n)
    if up:
        res.append({"kind": "github", "label": "Author's official notebook", "href": up})
    return res
