# AI for Professional — sumber slide, kode contoh, dan notebook

Repositori **sumber tunggal** untuk kelas

> **Designing and Building AI Products and Services: AI for Professional**
> ITB Team · Direktorat Pendidikan Profesional Berkelanjutan
> × PT Bank Rakyat Indonesia (Persero) Tbk

Setiap dek slide ditulis **satu kali** sebagai modul Python di `content/`, lalu
dirender ke dua bentuk sekaligus:

| Bentuk | Perender | Keluarannya |
|---|---|---|
| Beamer / PDF | `tools/gen_latex.py` | `latex/<id>.tex` → `latex/<id>.pdf` |
| Dek web | `tools/gen_web.py` | `../course-web-slides/<id>/` |

Alasannya sederhana: dua dek yang ditulis terpisah **pasti** akan menyimpang.
Dengan satu sumber, keduanya tidak bisa berbeda isi.

## Membangun

```bash
python3 tools/build.py            # semua dek: .tex + dek web
python3 tools/build.py --pdf      # sekalian jalankan latexmk
python3 tools/build.py ch02 ch03  # hanya dek tertentu
python3 tools/build.py --list     # daftar dek yang terdaftar
```

`--pdf` juga melaporkan **slide yang melimpah keluar halaman**. Itu bukan galat
LaTeX melainkan galat isi: slidenya kebanyakan. Kurangi bloknya, jangan
kecilkan fontnya.

Dek web ditulis ke repo tetangga `../course-web-slides/`. Kalau checkout-nya
tidak bersebelahan, tunjuk dengan `COURSE_WEB_SLIDES_DIR`.

## Isi

```
content/     satu modul Python per dek — SATU-SATUNYA tempat isi diedit
tools/       skema, perender web, perender LaTeX, penggerak build
latex/       itbpro.sty (tema Beamer ITB) + .tex dan .pdf hasil bangkitan
  listings/  potongan kode tiap slide, ditulis ulang tiap build — bisa dijalankan
notebooks/   notebook Jupyter per bab (venv: lihat notebooks/README.md)
sample-code/ proyek dan skrip yang terlalu besar untuk sekadar potongan slide
```

## Menulis dek baru

Tambahkan `content/<id>.py` yang mengekspor sebuah dict `DECK`. Skema lengkapnya
— jenis slide, jenis blok, markup inline — ada di `tools/schema.py`. `build.py`
menemukannya dari nama berkas, jadi tidak ada daftar yang perlu diperbarui.

Peraga ditulis dua kali dalam satu blok `fig`: `svg` untuk web, `tikz` untuk
LaTeX. Kalau salah satu dikosongkan, perender yang bersangkutan jatuh ke
keterangan gambarnya saja.

## Repositori tetangga

| Repo | Isinya |
|---|---|
| `dnd-ai-products-services-pro-course-web` | situs kursus |
| `dnd-ai-products-services-pro-course-slides` | **repo ini** |
| `dnd-ai-products-services-pro-course-web-slides` | dek web + PDF unduhan |
| `ai-agentic-demo` | proyek demo agentic AI (single & multi agent) |

## Sumber materi bab 1–20

Chollet & Watson, *Deep Learning with Python*, 3rd ed. (Manning, ISBN
9781633436589) — <https://deeplearningwithpython.io/>. Kode edisi ketiga ditulis
dengan Keras 3 dan berjalan di atas JAX, TensorFlow, atau PyTorch. Notebook
resmi penulis: <https://github.com/fchollet/deep-learning-with-python-notebooks>.
