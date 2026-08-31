# Menambahkan buku baru — fitur, standar, dan cetakannya

Dokumen ini menjawab satu pertanyaan: **datang satu buku lagi, apa yang harus
dikerjakan?** Isinya apa yang sudah disediakan sistemnya, standar yang harus
dipenuhi tiap dek, cetakan berkasnya, dan urutan langkahnya.

Angka di dokumen ini diukur pada keadaan 31 Agustus 2026: 22 dek, 1.173 slide,
27 gambar tangan, 181 mermaid, 16 blok kode berjejak.

---

## 0 · Baca ini dulu: sistemnya masih menganggap ada SATU buku

`tools/course.py` punya satu dict `BOOK` dan satu peta `CH_SLUG` yang memetakan
nomor bab ke slug URL. Dua puluh berkas di `content/` mengimpornya. Selama cuma
ada satu buku itu benar dan sederhana; **buku kedua membuatnya salah**, sebab
`chapter_url(7)` tidak lagi punya satu jawaban.

Yang harus diubah sebelum bab pertama buku kedua ditulis:

| Sekarang | Jadi |
|---|---|
| `BOOK = {...}` satu dict | `BOOKS = {"dlwp": {...}, "<slug-buku-2>": {...}}` |
| `CH_SLUG = {1: "..."}` | satu peta per buku, di dalam entri bukunya |
| `chapter_url(n)` | `chapter_url(book, n)` |
| `book_source(n)` | `book_source(book, n)` |
| `chapter_resources(n, nb)` | `chapter_resources(book, n, nb)` |
| `DECK["id"] = "ch07"` | `"dlwp07"` / `"<buku>NN"` — id harus unik lintas buku |

Biarkan `BOOK` tetap ada sebagai alias ke buku pertama sampai kedua puluh dek
lama dipindahkan, atau pindahkan semuanya sekali jalan — keduanya boleh, yang
tidak boleh adalah dua buku berbagi satu `CH_SLUG`.

**`DECK["kind"]`** sudah membedakan `chapter` dari `module`; buku kedua tetap
`chapter`. Urutan tampil di indeks: bab diurutkan menurut `number`, modul
menurut `MODULE_ORDER` di `tools/gen_index.py`. Untuk dua buku, urutkan
menurut `(buku, number)`.

---

## 1 · Yang sudah disediakan sistemnya

Satu isi, dua perender. `content/<id>.py` mengekspor `DECK`; `build.py`
menemukannya dari nama berkas — tidak ada daftar yang perlu diperbarui.

```
content/<id>.py ──┬── gen_web.py   → course-web-slides/<id>/slides.js
                  └── gen_latex.py → latex/<id>.tex → latex/<id>.pdf
                                                    → course-web-slides/pdf/<id>.pdf
```

**Tujuh belas jenis blok** (`tools/schema.py` memuat kontrak lengkapnya):
`p` `lead` `bullets` `steps` `cards` `stats` `code` `out` `table` `quote`
`band` `fig` `draw` `mmd` `img` `links` `cols`.

Markup inline di tiap `md`: `**tebal**` `` `kode` `` `*miring*` `==sorot==`
`[label](href)`.

Yang tidak perlu dibangun sendiri:

- **Arah mermaid dipilih otomatis.** Tulis `TB` atau `LR` mana pun yang masuk
  akal; `tools/figures.py` merender, mengukur skala tampilnya, dan membalik
  arahnya kalau versi baliknya lebih besar.
- **Gambar tangan** dari `tools/diagrams.py` — 27 generator, dua palet dari
  satu builder (gelap untuk web, terang dicetak jadi PDF lewat Chrome). Teksnya
  `<text>` SVG asli, jadi tidak bisa terpotong seperti label mermaid.
- **Simulator bertahap.** Elemen SVG menandai `data-step="N"`; `deck.js`
  menyingkapnya satu per satu dengan bilah kendali.
- **Jejak kode.** Blok `code` boleh membawa `run`: daftar `{"line", "note",
  "vars", "out"}`. Barisnya disorot, keadaannya muncul di panel bawahnya.
  Ditulis tangan, bukan dieksekusi.
- **Autofit.** Slide yang kepenuhan dikecilkan sampai muat, sampai lantai
  keterbacaan 0,58. Iteratif — melebarkan kotak membuat figur lebih tinggi.
- **Tautan notebook** lewat `notebook_url(n, nama)`. **Jangan pernah menulis
  href notebook dengan tangan**; yang ditulis tangan menunjuk `.ipynb` mentah,
  dan peramban mengunduhnya alih-alih membukanya.
- **Sumber daya bab** lewat `chapter_resources(n, [nb, ...])` — baris buku,
  notebook, indeks notebook, JupyterLab kalau dikonfigurasi, notebook resmi
  penulis kalau ada.

---

## 2 · Standar: apa yang harus benar sebelum dek dianggap selesai

Tiga lint jalan otomatis tiap build, dan tiga sapuan diukur di peramban. **Enam
angka ini harus nol.**

### Lint build — `python3 tools/build.py`

| Aturan | Artinya | Batas |
|---|---|---|
| `code-unexplained` | listing tanpa prosa sebelum DAN sesudahnya | — |
| `figure-unexplained` | gambar tanpa kata di dekatnya, dan slide berikutnya juga bukan penjelasannya | — |
| `slide-too-dense` | bobot badan slide di atas ambang | `MAX_WEIGHT = 34` |
| `deck-too-short` | dek bab terlalu pendek untuk menutup babnya | `≥ 34` slide isi |
| `too-few-figures` | dek bab terlalu sedikit peraga | `≥ max(6, slide/6)` |

Bobot itu taksiran "baris slide" per blok (`WEIGHT` di `schema.py`): satu
`cards` = 7, satu `draw` = 13, satu baris kode = 1,15. Kolom dihitung sebesar
kolom terberatnya, bukan jumlahnya.

### Sapuan peramban — harus nol semua

```bash
python3 -m http.server 5053 --directory ../course-web/site &
python3 tools/clip.py  http://127.0.0.1:5053   # label mermaid terpotong
python3 tools/small.py http://127.0.0.1:5053   # figur tampil < 55% ukuran gambarnya
python3 tools/audit.py http://127.0.0.1:5053   # slide terpotong / bertindihan
```

`audit.py` menjalankan tiap bilah kendali sampai habis sebelum mengukur, sebab
**slide bertahap punya lebih dari satu tata letak** — panel jejak bertambah
tinggi tiap langkah.

### Kesetaraan web dan PDF

Jumlah halaman PDF **harus** sama dengan jumlah slide web, dek per dek:

```bash
python3 tools/build.py --pdf
pdfinfo ../course-web-slides/pdf/<id>.pdf | grep Pages
```

Selisih yang seragam di banyak dek selalu tandanya struktural, bukan isi —
dulu setiap PDF punya satu halaman lebih karena perender LaTeX memasang halaman
*Session Objectives* dan perender web tidak.

---

## 3 · Cetakan `content/<id>.py`

```python
# -*- coding: utf-8 -*-
"""Bab N — <judul>.

Sumber: <penulis>, *<buku>*, bab N (hlm. x–y), dibaca dari PDF bukunya.

<Satu paragraf: apa yang sebenarnya diajarkan bab ini, bukan daftar isinya.>
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url, notebook_url  # noqa: E402
from diagrams import neural_net  # noqa: E402   ← hanya yang dipakai

NB = ["01_<topik>.ipynb", "02_<topik>.ipynb"]

MMD_<NAMA> = """
flowchart LR
  A["..."] --> B["..."]
"""

DECK = {
    "id": "chNN",                 # unik lintas buku — lihat §0
    "kind": "chapter",            # "chapter" | "module"
    "number": NN,
    "title": "<Judul bab>",
    "subtitle": "<satu kalimat: apa yang dibawa pulang pembaca>",
    "source": f"{BOOK['authors']}, {BOOK['title']} {BOOK['edition']} — bab NN",
    "source_url": chapter_url(NN),
    "duration": "3 jam (2 sesi)",
    "presenter": [{"name": "...", "role": "..."}],
    "resources": chapter_resources(NN, NB),
    "objectives": [
        "<kata kerja> ... ",        # 6–8 butir, tiap butir bisa diperiksa
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "<bagian>",
         "lead": "<satu kalimat>"},

        {
            "type": "slide",
            "kicker": "Section NN.1",
            "title": "<klaim, bukan topik>",
            "blocks": [
                {"t": "p", "md": "..."},
                {"t": "code", "lang": "python", "file": "listing NN.1",
                 "src": """x = 1""",
                 "run": [
                     {"line": 1, "note": "...", "vars": {"x": "1"}},
                 ]},
                {"t": "band", "md": "..."},
            ],
            "notes": "<untuk konsol penyaji>",
        },
    ],
}
```

Slide judul dan halaman **Session Objectives** dibangkitkan dari header — jangan
menulisnya sebagai slide.

---

## 4 · Urutan langkah untuk buku baru

1. **Ubah `course.py` jadi banyak buku** (§0). Kerjakan ini dulu; menundanya
   berarti menulis dua puluh berkas yang harus disunting lagi.
2. Tambahkan entri bukunya: judul, edisi, penulis, penerbit, ISBN, situs, repo
   kode, dan peta slug babnya.
3. Ambil gambar bukunya kalau ada PDF-nya: `python3 tools/bookfigs.py --pdf
   <buku>.pdf --list 8` lalu `--all-in 8`. Gambar buku dipakai lewat blok
   `img` dengan `"credit": True`.
4. Tulis `content/<id>.py` dari cetakan di §3, satu bab satu berkas.
5. Notebook per bab di `notebooks/<id>/`, lalu
   `python3 tools/build_notebooks.py` dan `python3 tools/nb_html.py`.
6. `python3 tools/build.py <id>` sampai lint bersih.
7. Jalankan tiga sapuan peramban sampai nol semua.
8. `python3 tools/build.py --pdf` dan periksa kesetaraan halaman.
9. Perbarui `MODULE_ORDER` / urutan indeks kalau perlu, lalu bangun situsnya:
   `cd ../course-web && python3 tools/build.py`.

---

## 5 · Kaidah menggambar — empat aturan, dan kapan TIDAK menggambar

1. **Kalau isinya aritmetika, hitungkan.** `0,0089` di sebelah `5,21`
   membuktikan sesuatu; "gradiennya jadi lebih besar" tidak.
2. **Kalau isinya proses, jalankan satu contohnya.** Gelung agen bukan empat
   kotak dan satu panah balik — itu gambar dari sebuah `while`.
3. **Kalau tidak ada yang bisa diukur, hitung konsekuensinya dan cetak
   asumsinya DI gambarnya.**
4. **Jangan biarkan gambarnya membantah klaimnya.** Slide berjudul "nested
   inside one another" yang digambar sebagai rantai atas-ke-bawah mengajarkan
   hal yang keliru, dan gambar biasanya menang atas kalimat.

**Dan kapan tidak usah menggambar.** Kalau kartunya bisa ditukar urutannya
tanpa slidenya jadi salah, itu **daftar** — "tiga jebakan", "empat cara ini
gagal", "di mana ia menang dan di mana ia menyakitkan". Gambar per butir cuma
hiasan, dan hiasan menambah tinggi yang dibayar dengan ukuran tampil. Dari 128
slide kartu tanpa peraga, hanya sekitar tujuh yang benar-benar butuh gambar,
dan semuanya slide etalase.

**Tinggi gambar ADALAH ukuran tampilnya.** Jangan mengulang kesimpulan di dalam
gambar kalau sudah ada di band sebelahnya; tata melebar, bukan meninggi; dan
kalau masih kekecilan, pecah slidenya — tidak ada batas jumlah slide.

---

## 6 · Jebakan yang sudah pernah memakan waktu

- **Hasil kosong bukan hasil bersih.** Sapuan pernah melaporkan 1.113 slide dan
  nol masalah untuk build berisi 1.169 — satu dek gagal diukur diam-diam.
  Baca daftar gagal sebelum totalnya, dan periksa jumlah slidenya.
- **Angka yang dideklarasikan bukan angka yang diukur.** Ambang tinggi figur
  dibaca dari stylesheet (480px) padahal peramban memberi ~270.
- **Sesekali LIHAT slidenya.** Bug terbesar yang pernah ada di sini —
  `transform-origin` yang mendorong tiap slide 300px ke kanan — tidak terlihat
  oleh satu pun metrik.
- **Slide tersembunyi berukuran nol.** Panggil `window.deck.show(i)` dulu.
- **Tunggu webfont** (`document.fonts.ready`), atau muncul pemotongan hantu.
- **Jangan menulis href notebook dengan tangan.** Sembilan belas keping pernah
  menunjuk `.ipynb` mentah dan mengunduh alih-alih membuka.

Rujukan: [`README.md`](README.md) untuk pemakaian sehari-hari,
[`tools/AUDIT.md`](tools/AUDIT.md) untuk perkakas ukurnya,
[`tools/schema.py`](tools/schema.py) untuk kontrak bloknya,
[`BACKLOG.md`](BACKLOG.md) untuk sisa pekerjaan.
