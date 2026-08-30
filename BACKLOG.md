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
| `mmd` (kotak-dan-panah) | 185 |
| `draw` (SVG digambar, dari `tools/diagrams.py`) | 18 |
| `img` | 4 |

Dek yang **sama sekali belum** punya peraga gambar: ch04, ch06, ch07, ch10,
ch12, ch13, ch16, ch17, ch18, ch19, ch20, `viny-llm`. Empat di antaranya
disebut langsung: `ch17#3`, `ch19#58`, `ch04#1`, dan banyak diagram vertikal di
`hendri-agentic`.

Bukan semua 185 harus jadi gambar. Graf ketergantungan, alur keputusan, dan
diagram penyebaran memang graf kotak — dan sesudah `figures.py` memutar
arahnya, semuanya terbaca. **Yang harus diganti adalah mermaid yang menggambar
sesuatu yang punya isi:** arsitektur model, bentuk data, operasi, urutan
perhitungan. Aturan pemilihannya satu kalimat: *kalau kotaknya bisa ditukar
isinya tanpa gambarnya jadi salah, itu bukan gambar — itu daftar.*

Kandidat berikutnya, berurutan:

- [ ] `ch17` — arsitektur urutan (sequence); yang menarik justru bentuk
      datanya berubah tiap langkah, dan itu yang hilang jadi kotak
- [ ] `hendri-agentic` — gelung agen: rencana → tindakan → amatan, dengan
      enam anggaran yang menghentikannya. Sekarang mermaid
- [ ] `ch19`/`ch20` — alur penyebaran; sebagian memang graf, periksa satu-satu
- [ ] `ch04` — pembagian latih/uji dan pengacakan batch, keduanya aritmetika
- [ ] `viny-llm` — ada `attention_qkv` di `ch15` yang bisa dipakai ulang

## 2 · Kode yang belum bisa dijalankan di slide — 291 dari 298

Blok `code` boleh membawa `run`: daftar langkah berisi nomor baris, catatan,
dan keadaan variabel. Baru **7 dari 298** yang punya.

Sudah: `ch01` gelung latih · `ch02` listing 2.1 + relu · `ch03` GradientTape +
langkah latih utuh · `ch04` K-fold · `ch12` IoU.

Prioritaskan listing yang **aritmetika**, bukan yang pemanggilan pustaka. Jejak
`run` ditulis tangan; angkanya harus benar, jadi hitung dulu.

- [ ] `ch11` Conv2DTranspose (kebalikan konvolusi — angkanya kecil, cocok)
- [ ] `ch14` n-gram dan pemotongan teks (chunking)
- [ ] `ch15` perhitungan perhatian (attention) satu kepala
- [ ] `ch16`/`ch17` penyusunan batch

## 3 · Slide kartu tanpa peraga — 128

128 slide berisi `cards`/`stats` dan tidak ada gambarnya. **Sebagian besar
memang begitu bentuknya** — tiga hal yang harus dipenuhi tidak jadi lebih jelas
kalau diberi gambar. Yang perlu diperiksa adalah yang kartunya cuma ikon:
gambar yang mewakili isi lebih baik daripada ikon, dan itu permintaan yang
sudah disampaikan.

Belum ada daftar yang disaring; membuat daftar itu sendiri satu pekerjaan.

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
