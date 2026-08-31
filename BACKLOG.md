# Yang belum selesai

Angka di bawah ini **diukur**, bukan ditaksir — dihitung ulang dengan:

```bash
python3 tools/stats.py          # ringkasan isi 22 dek
python3 tools/clip.py  http://127.0.0.1:5053
python3 tools/small.py http://127.0.0.1:5053
python3 tools/audit.py http://127.0.0.1:5053
```

Keadaan per 30 Agustus 2026: **1.167 slide, 22 dek.** Tata letak bersih —
0 label terpotong, 0 figur tampil di bawah 55%, 0 slide terpotong atau
bertindihan. **Web dan PDF sekarang sama persis**: 1.167 slide web,
1.167 halaman PDF, dek per dek.

---

## 1 · Peraga masih kotak-dan-panah — 185 mermaid lawan 18 gambar

| | Jumlah |
|---|---|
| `mmd` (kotak-dan-panah) | 182 |
| `draw` (SVG digambar, dari `tools/diagrams.py`) | 25 |
| `img` | 4 |

Dek yang **sama sekali belum** punya peraga gambar: ch04, ch06, ch07, ch10,
ch12, ch13, ch16, ch18, ch19, ch20, `viny-llm`. Dua yang disebut langsung
sudah dikerjakan — `ch17` (ruang laten, dengan jalan dari A ke B dan satu titik
di luar manifold) dan `hendri-agentic` (gelung agen, dengan satu jalannya yang
sungguhan berputar di dalamnya), dan `ch04` (softmax lawan sigmoid, dihitung
pada logit yang sama). Semua slide yang pernah disebut langsung sudah dikerjakan.

Bukan semua 185 harus jadi gambar. Graf ketergantungan, alur keputusan, dan
diagram penyebaran memang graf kotak — dan sesudah `figures.py` memutar
arahnya, semuanya terbaca. **Yang harus diganti adalah mermaid yang menggambar
sesuatu yang punya isi:** arsitektur model, bentuk data, operasi, urutan
perhitungan. Aturan pemilihannya satu kalimat: *kalau kotaknya bisa ditukar
isinya tanpa gambarnya jadi salah, itu bukan gambar — itu daftar.*

Kandidat berikutnya, berurutan:

- [x] ~~`ch17` ruang laten~~ dan ~~`hendri-agentic` gelung agen~~ — selesai.
      Keduanya memakai kaidah yang sama: gambarnya menjalankan satu contoh
      sungguhan, bukan menamai bagian-bagiannya.
- [ ] `ch17` — arsitektur difusi: denoising itu gelung, dan gelungnya yang
      hilang kalau digambar sebagai rantai kotak
- [ ] `ch20` — alur penyebaran; sebagian memang graf, periksa satu-satu
- [ ] `ch04` — pembagian latih/uji dan pengacakan batch, keduanya aritmetika
- [ ] `viny-llm` — ada `attention_qkv` di `ch15` yang bisa dipakai ulang

## 2 · Kode yang belum bisa dijalankan di slide — 287 dari 298

Blok `code` boleh membawa `run`: daftar langkah berisi nomor baris, catatan,
dan keadaan variabel. Baru **11 dari 298** yang punya.

Sudah: `ch01` gelung latih · `ch02` listing 2.1 + relu · `ch03` GradientTape +
langkah latih utuh · `ch04` K-fold · `ch11` Conv2DTranspose · `ch12` IoU ·
`ch14` byte-pair encoding · `ch15` normalisasi lapis + perhatian
hasil-kali-titik.

Prioritaskan listing yang **aritmetika**, bukan yang pemanggilan pustaka. Jejak
`run` ditulis tangan; angkanya harus benar, jadi hitung dulu.

- [x] ~~`ch11` Conv2DTranspose~~ · ~~`ch15` normalisasi lapis~~ — selesai.
      Yang kedua sekaligus mencatat satu hal: listing di buku membagi dengan
      **variansi**, bukan akarnya, jadi keluarannya berpusat tapi variansinya
      0,53. Keras membagi dengan √(variansi + ε). Jejaknya menghitung keduanya.
- [ ] `ch16`/`ch17` penyusunan batch

## 3 · Slide kartu tanpa peraga — 128, dan cuma segelintir yang perlu gambar

Daftarnya sudah disaring, dan hasilnya lebih berguna daripada dugaan awal:

| | Jumlah |
|---|---|
| slide `cards`/`stats` tanpa peraga | 128 |
| …yang tiap kartunya berikon | 98 |
| …yang subjeknya benar-benar **visual** | ± 7 |

Judulnya yang menentukan. "Dua hal yang benar sekaligus", "tiga jebakan",
"di mana ia menang dan di mana ia menyakitkan", "empat cara ini gagal" —
semuanya **memang berbentuk kartu**, dan gambar tidak menambah apa pun.
Perintahnya: *kalau kartunya bisa ditukar urutannya tanpa slidenya jadi salah,
itu daftar, dan daftar memang begitu bentuknya.*

Yang benar-benar minta gambar adalah slide **etalase** — di mana sesuatu
dipakai, seperti apa bentuknya:

- [x] ~~`hendri-agentic` lima layar~~ — selesai, jadi `phone_flow`: enam bingkai
      telepon dengan isi skematis, dan yang keenam digambar sebagai **lubang**
      bergaris putus dengan silang. "Layar yang tidak ada" itu klaim tentang
      produknya dan pantas kelihatan sebagai celah, bukan cuma ditulis.
- [x] ~~`ch11#4` "Where it is actually used"~~ — selesai, jadi `mask_domains`:
      empat adegan 12×9 dan topengnya dijatuhkan ke atasnya. Satu operasi
      dilihat empat kali, bukan empat kata dilihat sekali.
- [ ] `ch12#1` "What detection is for"
- [ ] `ch01#41`/`#42` terobosan dan hal yang dulu dikira mustahil
- [ ] `ch06#1` "keras.datasets does not exist" (8 kartu)
- [ ] `ch19#22` "Landing a rocket, and crossing a road"

Sisanya jangan disentuh. Menambah gambar ke daftar yang memang daftar cuma
menambah tinggi, dan tinggi itu dibayar dengan ukuran tampil.

## 4 · Di luar dek

- [x] ~~`notebooks-site/` belum tayang~~ — **selesai lewat cara lain.**
      Notebook sekarang ikut situsnya: `course-web/tools/build.py` memasang
      `site/notebooks/`, dan tautannya relatif, jadi benar di laptop, di
      `:5053`, dan di `/rs/ai-products-course/` sekaligus. Tidak ada langkah
      publikasi terpisah lagi. PDF tetap dapat URL mutlak lewat
      `course.absolute()` + `COURSE_SITE_URL`.
- [ ] Aplikasi Flutter di `ai-agentic-demo/integrated/mobile/` **belum pernah
      dikompilasi** — tidak ada Flutter SDK di lingkungan ini. Sumbernya sudah
      diperiksa, tetapi anggarkan satu kali build sebelum dipakai.
- [ ] Berkas PDF Beamer dibangun sesuai permintaan (`build.py --pdf`), belum
      ada yang dibangkitkan ulang sesudah gambar-gambar terakhir.

## Yang jangan diulang

Tiga kesalahan pengukuran sudah dicatat di [`tools/AUDIT.md`](tools/AUDIT.md).
Yang terakhir baru: **hasil kosong bukan hasil bersih.** Sapuan ke-22 dek
mengembalikan satu entri per dek berisi nol slide, dan totalnya terbaca "0
masalah". Sekarang `audit.py` menolak hasil kosong dan berisik kalau ada dek
yang gagal diukur.
