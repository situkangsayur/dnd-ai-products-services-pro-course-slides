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
    "unit": "Direktorat Pendidikan Profesional Berkelanjutan",
    "partner": "PT Bank Rakyat Indonesia (Persero) Tbk",
    "format": "Microcredential · hybrid · berbayar",
    # From BRI-diskusi-20-08-2026: 6 sks, 1 sks = 45 jam, dipecah
    # 15 jam kuliah + 15 jam exercise + 15 jam independent study per sks.
    "credits": "6 sks (setara 2 mata kuliah S2)",
    "hours": "1 sks = 45 jam · 15 jam kuliah + 15 jam exercise + 15 jam studi mandiri",
    "assessment": "Tugas kelompok + presentasi + pendampingan. Tidak ada ujian tertulis.",
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
        "role": "Pengajar Utama",
        "aff": "Guru Besar STEI ITB · Ketua KK Sistem Kendali dan Komputer · "
               "salah satu pendiri Pusat AI ITB",
        "url": "https://stei.itb.ac.id/en/dosen/bambang-riyanto-trilaksono/",
        "topics": "Konsep, teori, dan pemodelan (sesi pagi)",
    },
    {
        "key": "rahman",
        "name": "Rahman Indra Kesuma, S.Kom., M.Cs.",
        "role": "Asisten Pengajar",
        "aff": "Dosen Teknik Informatika, Institut Teknologi Sumatera (ITERA) · "
               "Artificial Intelligence dan Data Engineering",
        "url": "https://if.itera.ac.id/dosen-rahman-indra-kesuma/",
        "topics": "Topik 2 — Machine Learning · Topik 3 — Deep Learning",
    },
    {
        "key": "viny",
        "name": "Viny",
        "role": "Asisten Pengajar",
        "aff": "Kandidat Doktor · fokus riset Large Language Model, "
               "fine-tuning, RAG, re-ranker, dan guardrail",
        "url": "https://scholar.google.com/citations?user=hayqUI0AAAAJ&hl=en",
        "topics": "Topik 4 — LLM, fine-tuning, dan RAG",
        # Nama lengkap belum dikonfirmasi; profil Scholar memblokir pengambilan
        # otomatis. Tandai agar tidak terbaca sebagai fakta terverifikasi.
        "name_pending": True,
    },
    {
        "key": "hendri",
        "name": "Hendri Karisma, M.T.",
        "role": "Asisten Pengajar",
        "aff": "VP of Engineering, Jejakin · Kandidat Doktor STEI ITB",
        "url": "https://hendrikarisma.my.id",
        "topics": "Topik 6 — Agentic AI",
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
    "note": "Kode edisi ke-3 ditulis dengan Keras 3 dan dapat dijalankan di atas "
            "JAX, TensorFlow, atau PyTorch.",
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
    res = [{"kind": "book", "label": f"Bab {n} — teks penuh",
            "href": chapter_url(n)}]
    for nb in local_notebooks:
        res.append({"kind": "notebook", "label": nb,
                    "href": f"../../notebooks/ch{n:02d}/{nb}"})
    up = official_nb_url(n)
    if up:
        res.append({"kind": "github", "label": "Notebook resmi penulis", "href": up})
    return res
