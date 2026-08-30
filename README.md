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

## Alamat: notebook dan JupyterLab

Semua alamat yang ditunjuk slide ada di **satu tempat**, di blok konfigurasi
`tools/course.py`, dan tiap-tiapnya bisa ditimpa dari environment:

| Variabel | Bawaan | Untuk apa |
|---|---|---|
| `COURSE_NOTEBOOK_BASE` | `https://hendrikarisma.my.id/rs/ai-products-course/notebooks` | notebook yang sudah dirender |
| `COURSE_JUPYTER_BASE` | *(kosong)* | JupyterLab yang benar-benar hidup, mis. `http://10.100.21.22:8888` |
| `COURSE_JUPYTER_ROOT` | `notebooks` | letak notebook di dalam direktori kerja lab itu |

```bash
COURSE_JUPYTER_BASE=http://10.100.21.22:8888 python3 tools/build.py
```

**Notebook ditautkan sebagai HTML, bukan `.ipynb`.** Tautan ke berkas notebook
mentah tidak membuka notebook — ia mengunduh berkas, dan itu yang terjadi kalau
chip di slide diklik. Halaman yang bisa dibaca dibuat oleh:

```bash
python3 tools/nb_html.py          # notebooks/ -> notebooks-site/
```

Keluarannya berdiri sendiri (satu stylesheet, disisipkan, memakai palet dek)
dan punya `index.html` dengan jangkar per bab, sehingga dek bisa menunjuk
`index.html#ch07` dan mendarat di tempat yang benar.

**`COURSE_JUPYTER_BASE` sengaja kosong secara bawaan.** Menunjuk dek ke peladen
yang belum hidup lebih buruk daripada tidak menawarkan tautannya sama sekali,
sebab yang menemukannya adalah ruangan, di tengah sesi. Isi begitu labnya jalan;
chipnya muncul sendiri.

## Gambar: dua jalur, dan cara memilihnya

**Mermaid** (`{"t": "mmd"}`) untuk graf kotak-dan-panah. **Jangan pusing memilih
`TB` atau `LR`** — tulis yang paling masuk akal, karena `tools/figures.py`
memilihkan arahnya dengan MENGUKUR: dirender apa adanya, dan kalau bentuknya
terlalu tinggi untuk ruang yang diberikan slide, dirender ulang dengan arah
dibalik; yang paling mendekati rasio ruang figur yang menang. Diagram yang
memang lebih baik vertikal tetap vertikal, sebab versi baliknya kalah saat
diukur. Build melaporkan mana yang diputar dan mana yang **masih** tinggi.

**SVG yang digambar** (`{"t": "draw"}`, dari `tools/diagrams.py`) untuk apa pun
yang bukan graf kotak. Ada alasannya:

> Jaringan saraf itu bukan diagram alir. Yang menarik justru bahwa ada
> **neuron**, bahwa tiap neuron tersambung ke tiap neuron lapis berikutnya, dan
> bahwa bentuk datanya berubah sepanjang jalan. Digambar sebagai lima persegi
> panjang, semua itu hilang — dan slidenya tidak mengajarkan apa pun yang tidak
> bisa dikatakan dalam satu kalimat.

Generator yang ada: `neural_net` · `forward_pass` · `neuron_math` ·
`attention_qkv` · `dropout_net` · `conv_compute` · `feature_maps` ·
`tensor_ranks` · `tensor_grid` · `geometric_ops` · `sgd_descent` ·
`sliding_window` · `bag_of_words` · `pixel_mask`.

Teksnya `<text>` SVG asli, jadi tidak bisa terpotong seperti label mermaid.
Dua palet dari satu builder: gelap untuk web, terang dicetak jadi PDF lewat
Chrome (sudah jadi dependensi build lewat `mmdc`).

## Animasi dan simulasi

Metode yang diajarkan **diperlihatkan berjalan**, bukan dideskripsikan di dalam
kotak. Dua mekanisme, keduanya memakai bilah kendali yang sama:

* **Figur bertahap** — elemen SVG menandai dirinya `data-step="N"`; `deck.js`
  menyingkapnya satu per satu.
* **Kode yang dijalankan** — blok `code` boleh membawa `run`: daftar langkah
  berisi nomor baris, catatan, variabel, dan keluaran. Barisnya disorot dan
  keadaannya muncul di panel bawahnya.

Satu syarat mutlak: **diamnya harus tetap terbaca utuh.** PDF tidak punya
JavaScript, jadi makna yang hanya ada di gerakan adalah makna yang separuh
audiens tidak pernah terima. Jejak `run` juga ditulis tangan di sumber dek,
bukan dieksekusi — slide yang butuh runtime adalah slide yang gagal di ruangan
tanpa jaringan.

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
