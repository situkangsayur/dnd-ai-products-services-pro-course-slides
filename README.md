# AI for Professional — sumber slide, kode contoh, dan notebook

Repositori **sumber tunggal** untuk kelas

> **Designing and Building AI Products and Services: AI for Professional**
> ITB Team · Direktorat Pendidikan Profesional Berkelanjutan

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
| `COURSE_NOTEBOOK_BASE` | `../../notebooks` | notebook yang sudah dirender, **relatif** terhadap halaman dek |
| `COURSE_SITE_URL` | `https://hendrikarisma.my.id/rs/ai-products-course` | akar situs; HANYA dipakai perender LaTeX |
| `COURSE_JUPYTER_BASE` | *(kosong)* | JupyterLab yang benar-benar hidup, mis. `http://10.100.21.22:8888` |
| `COURSE_JUPYTER_ROOT` | `notebooks` | letak notebook di dalam direktori kerja lab itu |

```bash
COURSE_JUPYTER_BASE=http://10.100.21.22:8888 python3 tools/build.py
```

**Kenapa bawaannya relatif.** Dulu alamat notebook itu URL mutlak ke peladen
yang dipublikasikan — artinya tiap chip di tiap slide adalah janji tentang satu
mesin, dan selama berkasnya belum ada di sana, semuanya 404. Sekarang notebook
**ikut situsnya**: `course-web/tools/build.py` memasang `site/notebooks/`, dan
tautan relatif itu benar di laptop, di `:5053`, dan di
`/rs/ai-products-course/` sekaligus. Tidak ada lagi langkah publikasi terpisah.

PDF beda urusannya: tautan relatif tidak punya arti di dalam PDF, karena tidak
ada halaman untuk dijadikan acuan. Jadi `gen_latex.py` memanggil
`course.absolute()` yang menyelesaikan tiap tautan relatif terhadap
`COURSE_SITE_URL` sebelum menuliskannya. Web dapat tautan portabel, cetakan
dapat tautan yang bisa diklik.

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
`backprop` · `attention_qkv` · `positional_encoding` · `dropout_net` ·
`residual` · `depth_vs_width` · `conv_compute` · `feature_maps` ·
`tensor_ranks` · `tensor_grid` · `geometric_ops` · `sgd_descent` ·
`sliding_window` · `bag_of_words` · `pixel_mask` · `coord_change` ·
`agent_loop` · `latent_space` · `output_heads` · `reuse_curve` ·
`phone_flow` · `mask_domains` · `box_vs_mask` · `nested_sets`.

Aturan pertama: **kalau isinya aritmetika, hitungkan.** `backprop` dan
`residual` sama-sama menampilkan angkanya sendiri — `residual` mengalikan lima
turunan dua kali, sekali tanpa jalan pintas dan sekali dengan, lalu menaruh
kedua hasilnya berdampingan. Kalimat "gradien jadi lebih besar" tidak
membuktikan apa pun; `0.0089` di sebelah `5.21` membuktikannya.

Aturan kedua: **kalau isinya proses, jalankan satu contohnya.** `agent_loop`
tidak menamai empat kotak gelung agen — ia memutar satu penilaian kredit
sungguhan di dalamnya, enam giliran, dengan anggaran langkah terisi satu sel
tiap giliran, dan berhenti di giliran ketujuh yang tidak ada karena perkakasnya
memang tidak ada. `latent_space` berjalan dari A ke B dan memperlihatkan
keluaran dekodernya berubah mulus, lalu satu titik di luar manifold yang
keluarannya kacau.

Aturan ketiga: **kalau tidak ada yang bisa diukur, hitung konsekuensinya dan
cetak asumsinya di gambar.** `reuse_curve` menggambar klaim Chollet soal
pustaka global — sistem yang belum ada, jadi tidak ada yang bisa diukur. Yang
ada adalah akibatnya: kalau satu tugas butuh enam subrutin dari ruang empat
puluh primitif, tugas ke-20 mensintesis 0,27 subrutin baru. Asumsinya dicetak
di atas kurvanya, sebab asumsi itulah yang mengerjakan seluruh pekerjaannya.

Aturan keempat: **kalau gambarnya mengklaim sesuatu, jangan biarkan gambarnya
membantah klaimnya.** Pita data di `latent_space` sengaja dibuat hampir lurus:
kalau melengkung, tali busur antara dua titiknya keluar dari pita di tengah —
dan cerita rapi "berjalan dari A ke B, tiap langkah sah" jadi salah persis di
tempat gambarnya mengklaimnya. Kegagalan itu nyata dan pantas dapat slide
sendiri; ia bukan slide ini.

Teksnya `<text>` SVG asli, jadi tidak bisa terpotong seperti label mermaid.
Dua palet dari satu builder: gelap untuk web, terang dicetak jadi PDF lewat
Chrome (sudah jadi dependensi build lewat `mmdc`).

## Web dan PDF harus sama persis

Satu isi, dua perender, dan **jumlah halamannya harus cocok dek per dek**:

```bash
python3 tools/build.py --pdf        # .tex + latex/*.pdf + course-web-slides/pdf/*.pdf
```

Dulu tidak cocok. Setiap PDF punya SATU halaman lebih banyak daripada dek
webnya, karena perender LaTeX memasang halaman *Session Objectives* sesudah
sampul dan perender web tidak. Selisih yang seragam di 22 dek itu tandanya
struktural, bukan isi — dan sekarang keduanya memasangnya. Pemeriksaannya satu
baris `pdfinfo` per dek; kalau ada yang meleset, yang salah biasanya blok yang
cuma dikenali salah satu perender.

## Mengukur dek di peramban

Tiga hal tidak bisa diperiksa dari sumbernya, sebab baru terjadi ketika
peramban menata halaman. Perkakasnya ada di `tools/`, lihat
[`tools/AUDIT.md`](tools/AUDIT.md):

```bash
python3 tools/clip.py  http://127.0.0.1:5053   # label mermaid yang terpotong
python3 tools/small.py http://127.0.0.1:5053   # figur yang tampil terlalu kecil
python3 tools/audit.py http://127.0.0.1:5053   # slide yang terpotong / bertindihan
```

Ketiganya harus **nol**. Dua jebakan yang sempat memberi jawaban salah di sini,
dan keduanya dicatat di AUDIT.md: slide tersembunyi berukuran nol, dan
mengukur KOTAK elemen bukan GAMBAR di dalamnya.

## Animasi dan simulasi

Metode yang diajarkan **diperlihatkan berjalan**, bukan dideskripsikan di dalam
kotak. Dua mekanisme, keduanya memakai bilah kendali yang sama:

* **Figur bertahap** — elemen SVG menandai dirinya `data-step="N"`; `deck.js`
  menyingkapnya satu per satu.
* **Kode yang dijalankan** — blok `code` boleh membawa `run`: daftar langkah
  berisi nomor baris, catatan, variabel, dan keluaran. Barisnya disorot dan
  keadaannya muncul di panel bawahnya.

Catatan yang mahal dipelajari: **slide bertahap punya lebih dari satu tata
letak.** Panel jejak `run` bertambah tinggi tiap langkah, jadi slide yang muat
di langkah 0 bisa melewati batas bawah di langkah terakhir. `deck.js`
memasang-ulang tiap langkah, dan `audit.py` menjalankan tiap bilah kendali
sampai habis sebelum mengukur.

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
