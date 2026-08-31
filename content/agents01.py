# -*- coding: utf-8 -*-
"""Bab 1 — Pengantar: apa yang membuat sesuatu disebut agen.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 1.

🚨 CARA DEK INI DITULIS, DAN KENAPA BERBEDA DARI DEK ch01–ch20.

Buku pertama (Chollet & Watson) teksnya dipublikasikan bebas oleh penulisnya,
jadi dek-dek itu ditulis dari bukunya dan menautkan bab penuhnya. Buku ini
TIDAK: teksnya di balik langganan O'Reilly, dan situsnya menolak akses
otomatis. Jadi yang diikuti dari buku ini hanya **urutan babnya** — data
bibliografis — sementara isinya materi ajar yang ditulis sendiri dan gambarnya
digambar sendiri lewat tools/diagrams.py.

Konsekuensi yang harus dijaga saat menyunting: jangan menambahkan blok `img`
dengan `credit: True` ke dek buku ini, dan jangan menulis `source_url` — tidak
ada URL bab yang bisa dibuka pembaca tanpa langganan, dan tautan yang berakhir
di dinding langganan terbaca sebagai tautan rusak.

Klaim angka di dek ini berasal dari jejak nyata `ai-agentic-demo` (kasus
penilaian kredit UMKM) — bukan dari bukunya.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import agent_loop, nested_sets, reuse_curve  # noqa: E402

B = BOOKS["agents"]


# =============================================================================
#  Peraga mermaid. Yang bisa diukur atau dijalankan digambar dengan generator
#  SVG di tools/diagrams.py; sisanya mermaid, supaya kotaknya seukuran dan
#  berdiri di garis dasar yang sama.
# =============================================================================

MMD_PIPELINE_VS_AGENT = """
flowchart TB
  subgraph PIPA["Alur tetap — jalannya ditulis programmer"]
    direction LR
    I1["Masukan"] --> S1["Langkah 1"] --> S2["Langkah 2"] --> S3["Langkah 3"] --> O1["Keluaran"]
  end
  subgraph AGEN["Agen — jalannya dipilih saat berjalan"]
    direction LR
    I2["Tujuan"] --> M["Model memilih<br/>langkah berikutnya"]
    M --> T["Alat dipanggil"]
    T --> OB["Hasilnya dibaca"]
    OB --> M
    M --> O2["Selesai / menyerah"]
  end
  PIPA ~~~ AGEN
"""

MMD_PARTS = """
flowchart LR
  G["Tujuan"] --> ORK["Orkestrator<br/><small>gelung, anggaran, penghentian</small>"]
  ORK <--> MOD["Model<br/><small>memilih langkah</small>"]
  ORK <--> ALT["Alat<br/><small>satu-satunya jalan ke dunia luar</small>"]
  ORK <--> MEM["Memori<br/><small>apa yang sudah terjadi</small>"]
  ORK --> HSL["Hasil + jejak"]
"""

MMD_STOP = """
flowchart TB
  A["Giliran berikutnya"] --> C1{"Tujuan tercapai?"}
  C1 -- ya --> SEL["Selesai"]
  C1 -- tidak --> C2{"Anggaran langkah habis?"}
  C2 -- ya --> MEN["Berhenti, laporkan sejauh mana"]
  C2 -- tidak --> C3{"Ada alat untuk langkah ini?"}
  C3 -- tidak --> MEN
  C3 -- ya --> A
"""

MMD_GAGAL = """
flowchart LR
  MOD["Model salah pilih"] --> G1["Alat yang salah dipanggil"]
  ALT["Alat gagal"] --> G2["Galat dibaca sebagai fakta"]
  MEM["Memori bocor"] --> G3["Konteks lama mencemari giliran baru"]
  ORK["Orkestrator tak berhenti"] --> G4["Gelung tak berujung, tagihan naik"]
"""


DECK = {
    "id": "agents01",
    "kind": "chapter",
    "number": 1,
    "book": "agents",
    "title": "Pengantar: apa yang membuat sesuatu disebut agen",
    "subtitle": "Satu sifat yang memisahkan agen dari alur tetap — dan kenapa "
                "membedakannya menentukan biaya, pengujian, dan siapa yang "
                "bertanggung jawab kalau salah.",
    "source": book_source(1, "agents"),
    # Sengaja kosong: bukunya berlangganan. Lihat catatan di kepala berkas.
    "source_url": "",
    "duration": "3 jam (2 sesi)",
    "presenter": [
        {"name": "Hendri Karisma", "role": "Instructor"},
    ],
    "resources": [
        {"kind": "site", "label": "Course home", "href": "../../index.html"},
        {"kind": "github", "label": "ai-agentic-demo — kasus single-agent dan multi-agent",
         "href": "https://github.com/hendrikarisma/ai-agentic-demo"},
        {"kind": "book",
         "label": f"{B['authors']}, {B['title']} ({B['publisher']}, {B['edition']})",
         "href": B["site"]},
    ],
    "objectives": [
        "**Menyebutkan satu sifat** yang memisahkan agen dari alur tetap, dan menguji "
        "sebuah sistem terhadap sifat itu.",
        "**Menggambar gelung agen** beserta yang membuatnya BERHENTI — bukan hanya "
        "empat kotak dan satu panah balik.",
        "**Menamai empat bagian** yang menyusun agen, dan menyebutkan cara masing-masing "
        "gagal secara berbeda.",
        "**Menjelaskan otonomi sebagai tingkatan**, bukan sakelar, dan menempatkan satu "
        "sistem nyata pada tingkatannya.",
        "**Menyebutkan tiga keadaan** ketika agen adalah pilihan yang salah, dan "
        "menghitung kapan biayanya tidak kembali.",
        "**Menjelaskan kenapa agen dinilai dari JEJAKNYA**, bukan dari keluaran akhirnya.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Peta bab",
            "title": "Enam pertanyaan, dan yang keenam yang paling sering dilewat",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "◎", "h": "Apa itu agen",
                     "p": "Satu sifat, bukan daftar ciri. Kata ini dipakai untuk terlalu "
                          "banyak hal.", "tag": "§1"},
                    {"ico": "↻", "h": "Gelungnya",
                     "p": "Dan yang membuatnya **berhenti** — bagian yang biasanya hilang "
                          "dari gambar.", "tag": "§2"},
                    {"ico": "⬒", "h": "Empat bagian",
                     "p": "Model, alat, memori, orkestrator. Tiap bagian gagal dengan cara "
                          "yang berbeda.", "tag": "§3"},
                    {"ico": "▤", "h": "Otonomi",
                     "p": "Tingkatan, bukan sakelar. Pertanyaannya: siapa menyetujui apa.",
                     "tag": "§4"},
                    {"ico": "⊘", "h": "Kapan jangan",
                     "p": "Tiga keadaan yang membuat agen jadi pilihan yang mahal dan salah.",
                     "tag": "§5"},
                    {"ico": "⌕", "h": "Menilainya",
                     "p": "Dinilai dari **jejaknya**. Keluaran benar dari alasan yang salah "
                          "tetap kegagalan.", "tag": "§6"},
                ]},
            ],
            "notes": "Buka dengan meminta dua orang mendefinisikan 'agen' dalam satu "
                     "kalimat. Sebaran jawabannya adalah alasan bab ini ada.",
        },

        # ── §1 ────────────────────────────────────────────────────────────
        {"type": "section", "num": "01",
         "title": "Apa yang membuat sesuatu disebut agen",
         "lead": "Kata ini dipakai untuk chatbot, untuk skrip, dan untuk hal yang "
                 "benar-benar berbeda. Ketiganya tidak sama."},

        {
            "type": "slide",
            "kicker": "Bagian 1.1",
            "title": "Istilah yang menanggung terlalu banyak beban",
            "blocks": [
                {"t": "p", "md": "Dalam enam bulan terakhir, **agen** dipakai untuk "
                                 "menyebut: sebuah chatbot dengan tombol, sebuah skrip yang "
                                 "memanggil satu API, sebuah alur kerja bercabang, dan "
                                 "sebuah sistem yang memutuskan sendiri langkah "
                                 "berikutnya."},
                {"t": "p", "md": "Hanya yang terakhir yang membawa konsekuensi teknik yang "
                                 "berbeda. Tiga sisanya sudah punya nama, dan nama lamanya "
                                 "lebih tepat."},
                {"t": "band", "md": "Kalau semua disebut agen, ==tidak ada yang bisa "
                                    "dijanjikan tentang salah satunya=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.1",
            "title": "Empat lingkaran, dan yang terdalam yang kita bicarakan",
            "blocks": [
                nested_sets("agents01-nested", [
                    ("Perangkat lunak", "menjalankan yang ditulis"),
                    ("Aplikasi LLM", "model menghasilkan teks di dalam alur tetap"),
                    ("Agen", "model memilih langkah berikutnya"),
                    ("Multi-agen", "beberapa agen membagi pekerjaan"),
                ], cap="Bersarang, bukan berjajar — tiap lingkaran di dalamnya tetap "
                       "semua yang di luarnya."),
            ],
            "notes": "Slide ini yang difoto orang. Biarkan tampil saat membahas dua "
                     "slide berikutnya.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.2",
            "title": "Satu sifat, dan hanya satu",
            "blocks": [
                {"t": "lead", "md": "Sebuah sistem adalah **agen** bila **urutan langkahnya "
                                    "ditentukan saat berjalan, oleh sistemnya sendiri** — "
                                    "bukan ditulis lebih dulu oleh programmernya."},
                {"t": "p", "md": "Semua ciri lain yang biasa disebut — memakai alat, punya "
                                 "memori, berulang, otonom — adalah **akibat** dari sifat "
                                 "ini, bukan definisinya. Sebuah alur tetap juga boleh "
                                 "memanggil alat dan menyimpan keadaan; ia tetap bukan agen."},
                {"t": "band", "md": "Uji cepatnya: ==bisakah Anda menggambar diagram alirnya "
                                    "sebelum dijalankan?== Kalau bisa, itu alur tetap."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.2",
            "title": "Perbedaannya terlihat begitu digambar",
            "blocks": [
                {"t": "mmd", "id": "agents01-pipeline-vs-agent", "src": MMD_PIPELINE_VS_AGENT,
                 "cap": "Di atas: jalannya sudah ada sebelum data masuk. Di bawah: "
                        "jalannya baru ada setelah gilirannya berjalan."},
                {"t": "p", "md": "Perhatikan panah balik di bagan bawah. Itu bukan hiasan — "
                                 "**itu satu-satunya perbedaannya**, dan dari situ semua "
                                 "biaya tambahan berasal."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.3",
            "title": "Kenapa pembedaan ini bukan soal istilah",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Alur tetap** bisa diuji habis. Jalannya berhingga, "
                                         "dan tiap jalan bisa punya kasus ujinya."},
                        {"t": "p", "md": "**Agen** tidak. Jumlah jalannya tidak diketahui "
                                         "sebelum dijalankan, jadi pengujiannya berubah dari "
                                         "*memeriksa keluaran* jadi *memeriksa perilaku*."},
                    ],
                    [
                        {"t": "cards", "cols": 1, "items": [
                            {"ico": "⏱", "h": "Biaya tak lagi tetap",
                             "p": "Satu permintaan bisa jadi 3 giliran atau 30. Anggaran "
                                  "harus jadi bagian rancangannya.", "style": "bad"},
                            {"ico": "⚖", "h": "Tanggung jawab bergeser",
                             "p": "Kalau langkahnya dipilih mesin, **yang harus dicatat "
                                  "adalah alasannya** — bukan hanya hasilnya.",
                             "style": "bad"},
                        ]},
                    ],
                ]},
            ],
        },

        # ── §2 ────────────────────────────────────────────────────────────
        {"type": "section", "num": "02",
         "title": "Gelungnya — dan yang membuatnya berhenti",
         "lead": "Empat kotak dan satu panah balik adalah gambar dari sebuah `while`. "
                 "Yang penting justru yang ditinggalkannya."},

        {
            "type": "slide",
            "kicker": "Bagian 2.1",
            "title": "Satu jalannya, bukan bentuk umumnya",
            "blocks": [
                agent_loop("agents01-loop",
                           cap="Cincinnya di kiri; satu jalan sungguhan di kanan — enam "
                               "giliran, enam alat, dan giliran ketujuh yang tidak terjadi "
                               "karena tidak ada alat untuknya.",
                           note="Jejak dari kasus penilaian kredit UMKM di ai-agentic-demo."),
            ],
            "notes": "Jalankan bilah kendalinya sampai habis. Yang harus diperhatikan "
                     "peserta adalah sel anggaran yang terisi, bukan cincinnya.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.1",
            "title": "Gambar gelung yang tidak menyebut penghentiannya mengajarkan yang salah",
            "blocks": [
                {"t": "p", "md": "Hampir semua gambar gelung agen berhenti di panah balik. "
                                 "Yang tidak digambar: **berapa kali ia berputar, apa "
                                 "biayanya tiap putaran, dan apa yang membuatnya berhenti**."},
                {"t": "p", "md": "Ketiganya justru yang menentukan apakah sistemnya bisa "
                                 "dijalankan di produksi. Sebuah gelung tanpa syarat henti "
                                 "yang eksplisit **akan** berputar tanpa henti pada masukan "
                                 "yang tidak terduga — bukan mungkin, akan."},
                {"t": "band", "md": "Pertanyaan pertama dalam tinjauan rancangan agen: "
                                    "==apa yang membuatnya berhenti?=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.2",
            "title": "Tiga syarat henti, dan dua di antaranya sering lupa dipasang",
            "blocks": [
                {"t": "mmd", "id": "agents01-stop", "src": MMD_STOP,
                 "cap": "Hanya cabang paling kiri yang biasanya diimplementasikan."},
                {"t": "p", "md": "Cabang **anggaran langkah** dan **tidak ada alat untuk "
                                 "langkah ini** adalah yang menyelamatkan tagihan dan "
                                 "menyelamatkan pengguna dari jawaban yang dikarang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.2",
            "title": "Anggaran langkah bukan pembatas — ia bagian dari kontraknya",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "⛔", "h": "Tanpa anggaran",
                     "p": "Gelung yang tersesat berputar sampai kuota API habis. Gejalanya "
                          "muncul di tagihan, bukan di log.", "style": "bad"},
                    {"ico": "⏳", "h": "Anggaran terlalu ketat",
                     "p": "Tugas yang sah dipotong di tengah, dan hasilnya terlihat seperti "
                          "model yang bodoh.", "style": "warn"},
                    {"ico": "✔", "h": "Anggaran yang dilaporkan",
                     "p": "Berhenti, lalu **katakan sejauh mana ia sampai**. Itu hasil yang "
                          "bisa dipakai orang.", "style": "good"},
                ]},
                {"t": "p", "md": "Yang ketiga membutuhkan satu hal yang sering tidak ada: "
                                 "agen harus bisa mengembalikan **hasil separuh** yang jujur, "
                                 "bukan hanya berhasil atau galat."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.3",
            "title": "Bagian yang paling mahal bukan berpikirnya",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "Intuisi yang salah: yang mahal adalah panggilan "
                                         "model. Pada gelung nyata, **yang mahal adalah "
                                         "membaca hasil alat** — dan memasukkannya kembali "
                                         "ke konteks giliran berikutnya."},
                        {"t": "p", "md": "Satu tabel 1.843 baris tidak masuk ke konteks. "
                                         "Yang masuk harus **ringkasan yang dihitung**, dan "
                                         "siapa yang meringkasnya adalah keputusan rancangan."},
                    ],
                    [
                        {"t": "stats", "items": [
                            {"v": "1 843", "l": "baris transaksi diambil"},
                            {"v": "9", "l": "fitur yang benar-benar masuk konteks"},
                            {"v": "6", "l": "giliran sampai rekomendasi"},
                        ]},
                    ],
                ]},
                {"t": "band", "md": "Kalau alat mengembalikan data mentah ke model, "
                                    "==alatnya belum selesai dirancang=="},
            ],
        },

        # ── §3 ────────────────────────────────────────────────────────────
        {"type": "section", "num": "03",
         "title": "Empat bagian",
         "lead": "Model, alat, memori, orkestrator. Tiap bagian gagal dengan cara yang "
                 "berbeda, dan itulah kenapa memisahkannya berguna."},

        {
            "type": "slide",
            "kicker": "Bagian 3.1",
            "title": "Yang menyusun sebuah agen",
            "blocks": [
                {"t": "mmd", "id": "agents01-parts", "src": MMD_PARTS,
                 "cap": "Orkestrator di tengah — bukan model. Model adalah salah satu "
                        "bagian, bukan sistemnya."},
                {"t": "p", "md": "Menaruh **model** di tengah adalah kekeliruan gambar yang "
                                 "paling sering: yang memegang gelung, anggaran, dan "
                                 "penghentian adalah kode biasa, dan itu bagian yang bisa "
                                 "diuji dengan cara biasa."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.2",
            "title": "Model: memilih, bukan mengeksekusi",
            "blocks": [
                {"t": "p", "md": "Tugas model dalam agen jauh lebih sempit daripada dalam "
                                 "chatbot: ia **memilih langkah berikutnya dan argumennya**. "
                                 "Ia tidak menjalankan apa pun."},
                {"t": "p", "md": "Konsekuensinya baik: kesalahan model jadi **kesalahan "
                                 "pilihan** yang terlihat di jejak, bukan kesalahan hasil "
                                 "yang tersembunyi di dalam kalimat."},
                {"t": "band", "md": "Model yang lebih besar mengurangi salah pilih; "
                                    "==ia tidak mengurangi akibat dari salah pilih=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.3",
            "title": "Alat: satu-satunya jalan ke dunia luar",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔒", "h": "Alat adalah batas keamanan",
                     "p": "Apa pun yang tidak punya alat, **tidak bisa dilakukan agen**. "
                          "Itu jaminan yang kuat — dan alasan daftar alat harus ditinjau "
                          "seperti daftar izin.", "style": "good"},
                    {"ico": "📝", "h": "Deskripsi alat adalah kode",
                     "p": "Model memilih berdasarkan deskripsinya. Deskripsi yang kabur "
                          "menghasilkan pemanggilan yang salah, dan itu **bug di teks**, "
                          "bukan di model.", "style": "warn"},
                    {"ico": "⚠", "h": "Galat harus jadi galat",
                     "p": "Alat yang mengembalikan `\"tidak ditemukan\"` sebagai teks biasa "
                          "akan dibaca model sebagai **fakta**. Galat harus bertanda.",
                     "style": "bad"},
                    {"ico": "↩", "h": "Idempoten kalau bisa",
                     "p": "Gelung boleh mengulang. Alat yang menulis dua kali karena "
                          "diulang adalah kerusakan yang tidak terlihat di keluaran.",
                     "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.4",
            "title": "Memori: yang sudah terjadi, bukan yang diketahui",
            "blocks": [
                {"t": "p", "md": "Dua hal berbeda sering disebut memori: **riwayat giliran** "
                                 "(apa yang sudah dilakukan agen ini, sekarang) dan "
                                 "**pengetahuan** (apa yang bisa dicari dari luar). "
                                 "Menyatukan keduanya membuat keduanya rusak."},
                {"t": "p", "md": "Riwayat giliran tumbuh setiap putaran dan **harus punya "
                                 "batas**. Pengetahuan tidak tumbuh dan diambil sesuai "
                                 "kebutuhan — itu urusan bab tersendiri nanti."},
                {"t": "band", "md": "Konteks yang dibiarkan tumbuh bebas adalah alasan "
                                    "paling umum sebuah agen ==jadi lebih bodoh di giliran "
                                    "kesepuluh daripada di giliran pertama=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.5",
            "title": "Orkestrator: bagian yang paling membosankan, dan paling menentukan",
            "blocks": [
                {"t": "p", "md": "Orkestrator memegang gelung, anggaran, penanganan galat, "
                                 "dan pencatatan jejak. Ia **kode biasa** — tidak ada model "
                                 "di dalamnya."},
                {"t": "p", "md": "Karena itu ia juga satu-satunya bagian yang bisa diuji "
                                 "dengan pengujian unit biasa, dan bagian yang paling "
                                 "sering diabaikan karena terlihat sepele."},
                {"t": "band", "md": "Kalau orkestratornya tipis, ==setiap masalah produksi "
                                    "akan terlihat seperti masalah model==, dan tidak ada "
                                    "yang bisa diperbaiki"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.6",
            "title": "Empat bagian, empat cara gagal",
            "blocks": [
                {"t": "mmd", "id": "agents01-gagal", "src": MMD_GAGAL,
                 "cap": "Gejalanya berbeda, jadi perbaikannya juga berbeda."},
                {"t": "p", "md": "Nilai dari memisahkan empat bagian ini bukan kerapian "
                                 "arsitektur — ia **mempersempit tempat mencari** ketika "
                                 "ada yang salah."},
            ],
        },

        # ── §4 ────────────────────────────────────────────────────────────
        {"type": "section", "num": "04",
         "title": "Otonomi adalah tingkatan",
         "lead": "Pertanyaannya bukan 'otonom atau tidak', melainkan siapa menyetujui apa, "
                 "dan pada langkah yang mana."},

        {
            "type": "slide",
            "kicker": "Bagian 4.1",
            "title": "Lima tingkat, dan tempat kebanyakan sistem produksi berada",
            "blocks": [
                {"t": "table",
                 "head": ["Tingkat", "Siapa memilih langkah", "Siapa menyetujui tindakan"],
                 "rows": [
                     ["0 · Alur tetap", "programmer", "—"],
                     ["1 · Saran", "model", "orang, tiap langkah"],
                     ["2 · Terbatas", "model", "orang, hanya tindakan menulis"],
                     ["3 · Diawasi", "model", "orang, hanya di luar kebijakan"],
                     ["4 · Otonom", "model", "tak ada"],
                 ]},
                {"t": "p", "md": "Hampir semua sistem yang benar-benar berjalan di lingkungan "
                                 "beregulasi ada di **tingkat 2**. Tingkat 4 jarang jadi "
                                 "tujuan; ia biasanya jadi akibat dari tidak memutuskan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.2",
            "title": "Tindakan baca dan tindakan tulis bukan hal yang sama",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "cards", "cols": 1, "items": [
                            {"ico": "👁", "h": "Baca",
                             "p": "Salah baca menghasilkan jawaban yang buruk. Bisa diulang.",
                             "style": "good"},
                        ]},
                    ],
                    [
                        {"t": "cards", "cols": 1, "items": [
                            {"ico": "✍", "h": "Tulis",
                             "p": "Salah tulis mengubah dunia. **Tidak selalu bisa dibatalkan** "
                                  "— dan agen tidak tahu bedanya kecuali diberi tahu.",
                             "style": "bad"},
                        ]},
                    ],
                ]},
                {"t": "p", "md": "Cara paling murah menaikkan keamanan sebuah agen: **pisahkan "
                                 "daftar alatnya jadi baca dan tulis**, lalu minta persetujuan "
                                 "hanya untuk yang menulis. Perubahan sehari, bukan proyek."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.3",
            "title": "Persetujuan yang terlalu sering sama dengan tidak ada persetujuan",
            "blocks": [
                {"t": "p", "md": "Kalau orang harus menyetujui dua puluh langkah per "
                                 "permintaan, ia akan menekan *setuju* tanpa membaca. "
                                 "Ini bukan kelemahan orangnya — ini rancangan yang "
                                 "membebankan perhatian melebihi yang tersedia."},
                {"t": "band", "md": "Persetujuan harus **jarang dan bermakna**: "
                                    "==satu keputusan yang dibaca lebih baik daripada dua "
                                    "puluh yang dilewati=="},
            ],
        },

        # ── §5 ────────────────────────────────────────────────────────────
        {"type": "section", "num": "05",
         "title": "Kapan agen adalah pilihan yang salah",
         "lead": "Bagian yang paling sering hilang dari materi tentang agen — dan yang "
                 "paling menghemat uang."},

        {
            "type": "slide",
            "kicker": "Bagian 5.1",
            "title": "Tiga keadaan yang membuat agen jadi jawaban yang mahal",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "▦", "h": "Langkahnya sudah diketahui",
                     "p": "Kalau Anda bisa menggambar diagram alirnya, tulis diagram alirnya. "
                          "Agen menambah ketidakpastian tanpa menambah kemampuan.",
                     "style": "bad"},
                    {"ico": "⚡", "h": "Latensinya ketat",
                     "p": "Enam giliran berarti enam kali tunggu. Sebuah alur tetap "
                          "menyelesaikannya dalam satu.", "style": "bad"},
                    {"ico": "🎯", "h": "Kesalahan tidak boleh terjadi",
                     "p": "Agen menurunkan **rata-rata** kesalahan, bukan **kasus "
                          "terburuknya**. Kalau yang penting kasus terburuk, agen tidak "
                          "menolong.", "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.2",
            "title": "Kapan biayanya kembali",
            "blocks": [
                reuse_curve("agents01-reuse",
                            cap="Ongkos di muka sebuah agen dibayar oleh **jumlah variasi "
                                "tugas**, bukan jumlah panggilan.",
                            note="Satu tugas berulang: alur tetap menang. Banyak tugas "
                                 "serupa yang jalannya berbeda-beda: agen mulai menang."),
            ],
            "notes": "Tekankan sumbu datarnya: yang membuat agen sepadan adalah RAGAM "
                     "tugas, bukan volume. Volume tinggi dengan satu bentuk tugas justru "
                     "kasus terbaik untuk alur tetap.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.3",
            "title": "Jalan tengah yang sering terlewat",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Mulai dari alur tetap",
                     "p": "Tulis jalannya. Anda akan tahu bentuk masalahnya dengan biaya "
                          "yang jauh lebih murah."},
                    {"h": "Cari cabang yang meledak",
                     "p": "Biasanya hanya **satu atau dua** langkah yang butuh keputusan; "
                          "sisanya tetap."},
                    {"h": "Taruh agen HANYA di cabang itu",
                     "p": "Gelungnya kecil, anggarannya kecil, jejaknya bisa dibaca."},
                    {"h": "Perluas hanya kalau terbukti perlu",
                     "p": "Dan setiap perluasan membawa anggaran serta syarat hentinya "
                          "sendiri."},
                ]},
                {"t": "band", "md": "Sebagian besar sistem yang berhasil bukan agen "
                                    "seluruhnya — ia ==alur tetap dengan satu simpul yang "
                                    "diagenkan=="},
            ],
        },

        # ── §6 ────────────────────────────────────────────────────────────
        {"type": "section", "num": "06",
         "title": "Menilai agen",
         "lead": "Keluaran yang benar dari alasan yang salah tetap kegagalan — dan ia "
                 "akan berulang."},

        {
            "type": "slide",
            "kicker": "Bagian 6.1",
            "title": "Kenapa memeriksa keluaran akhir tidak cukup",
            "blocks": [
                {"t": "p", "md": "Sebuah agen bisa menghasilkan rekomendasi yang benar "
                                 "sambil memanggil alat yang salah, membaca galat sebagai "
                                 "fakta, dan kebetulan sampai ke jawaban yang sama."},
                {"t": "p", "md": "Pada kumpulan uji, itu terlihat **lulus**. Di produksi, "
                                 "kondisi kebetulannya hilang dan kegagalannya muncul tanpa "
                                 "peringatan."},
                {"t": "band", "md": "Yang dinilai adalah **jejaknya**: alat mana, dengan "
                                    "argumen apa, dan ==apakah langkah itu masuk akal "
                                    "berdasarkan yang diketahui saat itu=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.2",
            "title": "Empat hal yang harus dicatat tiap giliran",
            "blocks": [
                {"t": "p", "md": "Jejak yang berguna bukan log. Log mencatat apa yang "
                                 "terjadi; jejak mencatat **apa yang dipilih dan kenapa** — "
                                 "dan hanya kolom terakhir yang membuat 'benar karena "
                                 "kebetulan' bisa dibedakan dari 'benar'."},
                {"t": "code", "lang": "python", "file": "bentuk catatan jejak",
                 "src": '''jejak.append({
    "giliran": n,                    # ke berapa, dari anggaran berapa
    "alat": nama_alat,               # yang DIPILIH, termasuk saat gagal
    "argumen": argumen,              # apa adanya, sebelum dinormalkan
    "hasil": ringkas(keluaran),      # ringkasan, bukan data mentah
    "alasan": alasan_model,          # kenapa langkah ini
})''',
                 "run": [
                     {"line": 3, "note": "Alat yang dipilih dicatat walau pemanggilannya "
                                         "gagal — kegagalan memilih dan kegagalan "
                                         "menjalankan adalah dua bug berbeda.",
                      "vars": {"nama_alat": "'score_credit'"}},
                     {"line": 4, "note": "Argumen mentah, sebelum dinormalkan: normalisasi "
                                         "yang menyembunyikan argumen buruk juga "
                                         "menyembunyikan sebabnya.",
                      "vars": {"argumen": "{'app_id': 'APP-2203'}"}},
                     {"line": 6, "note": "Alasan dicatat sebagai teks. Inilah satu-satunya "
                                         "kolom yang membuat 'benar karena kebetulan' bisa "
                                         "dibedakan dari 'benar'.",
                      "vars": {"alasan_model": "'DSCR di bawah ambang, perlu skor'"}},
                 ]},
                {"t": "p", "md": "Struktur ini yang membuat jejaknya bisa dibaca **orang "
                                 "non-teknis** — auditor, petugas kredit — dan itu sering "
                                 "jadi syarat, bukan tambahan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.3",
            "title": "Tiga ukuran yang berguna, dan satu yang menyesatkan",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✔", "h": "Tingkat penyelesaian",
                     "p": "Berapa persen tugas selesai **dalam anggaran**. Menyebut angka "
                          "tanpa anggarannya tidak berarti apa-apa.", "style": "good"},
                    {"ico": "🎯", "h": "Ketepatan pemilihan alat",
                     "p": "Dari semua giliran, berapa yang memanggil alat yang benar. "
                          "Diukur di jejak.", "style": "good"},
                    {"ico": "⏱", "h": "Giliran per tugas",
                     "p": "Sebarannya, bukan reratanya — ekornya yang membuat tagihan.",
                     "style": "good"},
                    {"ico": "⚠", "h": "Kepuasan pengguna saja",
                     "p": "Naik ketika agen menjawab dengan percaya diri, termasuk saat "
                          "salah. Berguna, tapi **tidak boleh berdiri sendiri**.",
                     "style": "bad"},
                ]},
            ],
        },

        {"type": "section", "num": "05b", "title": "Agen terkecil yang masih agen",
         "lead": "Kalau semua hiasannya dilepas, yang tersisa selusin baris."},

        {
            "type": "slide",
            "kicker": "Inti",
            "title": "Selusin baris, dan tidak ada kerangka kerja",
            "blocks": [
                {"t": "p", "md": "Ini seluruh mesinnya. Bukan versi sederhana dari sesuatu "
                                 "yang lebih besar — inilah yang dijalankan kerangka kerja "
                                 "mana pun, dengan tambahan pencatatan dan penanganan galat."},
                {"t": "code", "lang": "python", "file": "agen minimum",
                 "src": """def jalankan(tujuan, alat, model, maks_langkah=8):
    riwayat = [{"peran": "tujuan", "isi": tujuan}]
    for langkah in range(maks_langkah):
        pilihan = model.pilih(riwayat, daftar=alat.skema())
        if pilihan.selesai:
            return pilihan.jawaban, riwayat
        if pilihan.nama not in alat:
            riwayat.append({"peran": "galat", "isi": "alat tidak ada"})
            continue
        hasil = alat[pilihan.nama](**pilihan.argumen)
        riwayat.append({"peran": "amatan", "isi": hasil})
    return None, riwayat            # anggaran habis, bukan selesai""",
                 "run": [
                     {"line": 4, "note": "Model **memilih**, dan hanya memilih. Yang "
                                         "dikembalikannya sebuah niat, bukan sebuah efek.",
                      "vars": {"langkah": "0", "pilihan": "ambil_data(id=…)"}},
                     {"line": 9, "note": "Baris ini yang membuat batas kemampuannya nyata: "
                                         "nama yang tidak ada di `alat` **tidak akan pernah "
                                         "dieksekusi**, seberapa pun yakinnya model.",
                      "vars": {"alat": "5 baca, 1 tulis"}},
                     {"line": 11, "note": "Baris 11 satu-satunya tempat dunia luar tersentuh. "
                                          "Setiap izin yang dimiliki sistem ini ada di sini.",
                      "vars": {"hasil": "1 843 baris"}},
                     {"line": 12, "note": "Amatan masuk ke riwayat, dan gelungnya berputar. "
                                          "Inilah keseluruhan \"agennya\".",
                      "vars": {"riwayat": "3 entri"}},
                     {"line": 13, "note": "Dan ini penyelamat yang paling sering dilupakan: "
                                          "keluar karena **anggaran habis**, dikembalikan "
                                          "sebagai `None` — bukan sebagai jawaban yang "
                                          "kelihatan seperti jawaban.",
                      "vars": {"keluar": "maks_langkah"}},
                 ]},
                {"t": "p", "md": "Perhatikan yang **tidak** ada: tidak ada prompt yang "
                                 "meminta agar berhati-hati, dan tidak ada daftar larangan. "
                                 "Batasnya ada di `alat`, dan itu struktur data biasa."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Inti",
            "title": "Yang ditambahkan sesudahnya, berurutan",
            "blocks": [
                {"t": "p", "md": "Dari selusin baris itu, tiap tambahan menjawab satu "
                                 "kegagalan yang sudah terlihat — bukan satu fitur yang "
                                 "kedengarannya bagus."},
                {"t": "table",
                 "head": ["Tambahan", "Kegagalan yang dijawabnya", "Bab"],
                 "widths": [26, 50, 24],
                 "rows": [
                     ["Jejak tiap giliran", "Tidak bisa tahu *kenapa* jawabannya begitu",
                      "bab 7"],
                     ["Anggaran selain langkah", "Berhenti berputar, tapi tagihannya sudah "
                      "terlanjur", "bab 7"],
                     ["Memori", "Mengulang pekerjaan yang sudah dilakukannya sendiri",
                      "bab 4"],
                     ["Rencana eksplisit", "Langkah kesembilan melupakan tujuan awalnya",
                      "bab 6"],
                     ["Persetujuan pada alat tulis", "Efek yang tidak bisa dibatalkan",
                      "bab 5"],
                 ]},
                {"t": "band",
                 "md": "Urutan ini bukan selera. Menambahkan memori sebelum ada jejak "
                       "berarti ==menambah tempat bug bersembunyi sebelum punya cara "
                       "melihatnya=="},
            ],
        },

        {"type": "section", "num": "06",
         "title": "Membangunnya dengan bertanggung jawab",
         "lead": "Bagian yang paling mudah ditunda, dan paling mahal kalau ditunda."},

        {
            "type": "slide",
            "kicker": "Tanggung jawab",
            "title": "Kemampuan bertambah, tanggung jawabnya tidak otomatis ikut",
            "blocks": [
                {"t": "p", "md": "Sebuah model yang salah menjawab menghasilkan **kalimat "
                                 "yang salah**. Sebuah agen yang salah menjawab bisa "
                                 "menghasilkan **tindakan yang salah** — surel terkirim, "
                                 "baris terhapus, dana berpindah. Yang berubah bukan "
                                 "tingkat kesalahannya, melainkan apa yang terjadi "
                                 "sesudahnya."},
                {"t": "p", "md": "Karena itu pertanyaan pertama sebelum menambah alat bukan "
                                 "*apakah modelnya cukup pandai*, melainkan **seberapa jauh "
                                 "akibatnya kalau ia keliru**, dan **siapa yang menanggung "
                                 "akibat itu** — hampir tidak pernah orang yang membangunnya."},
                {"t": "band",
                 "md": "Aturan yang menyelamatkan paling banyak waktu: ==ukur jangkauan "
                       "ledakannya sebelum menambah alat==, bukan sesudah insiden pertama."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tanggung jawab",
            "title": "Empat pertanyaan yang harus punya jawaban tertulis",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "Apa yang tidak boleh ia lakukan?",
                     "p": "Ditulis sebagai **alat yang tidak ada di daftarnya**, bukan "
                          "sebagai kalimat larangan di prompt. Larangan bisa dibujuk; "
                          "alat yang tidak ada tidak bisa dipanggil.",
                     "style": "accent"},
                    {"ico": "👤", "h": "Siapa yang bertanggung jawab atas keputusannya?",
                     "p": "Kalau jawabannya \"sistemnya\", berarti belum ada jawabannya. "
                          "Harus ada nama, dan namanya tercatat pada keputusan itu."},
                    {"ico": "🔍", "h": "Bagaimana orang tahu ini agen?",
                     "p": "Pengguna yang mengira sedang bicara dengan orang akan memberi "
                          "kepercayaan yang tidak ia berikan kalau tahu."},
                    {"ico": "🧾", "h": "Apa yang tersimpan, dan berapa lama?",
                     "p": "Jejaknya berisi data yang dilihat agen. Retensinya harus "
                          "cocok dengan retensi data itu, bukan dengan umur lognya."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tanggung jawab",
            "title": "Dua kegagalan yang bentuknya khas agen",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Perintah yang menumpang di dalam data.** Agen "
                                      "membaca halaman, berkas, atau tiket — dan isinya "
                                      "berisi kalimat yang ditujukan kepada *dia*, bukan "
                                      "kepada pembacanya."},
                     {"t": "p", "md": "Ini bukan soal model yang mudah dibujuk. Selama "
                                      "hasil alat masuk ke konteks yang sama dengan "
                                      "perintah, keduanya kelihatan sama. Penanganannya "
                                      "di **batas alatnya**: apa yang boleh dipanggil "
                                      "sesudah membaca sesuatu yang tidak tepercaya."}],
                    [{"t": "p", "md": "**Kesalahan yang bertumpuk.** Sembilan langkah "
                                      "benar 95% masing-masing bukan sistem yang benar "
                                      "95% — ia benar sekitar **63%**."},
                     {"t": "p", "md": "Karena itu jumlah langkah bukan detail teknis. "
                                      "Tiap langkah tambahan mengalikan peluang gagalnya, "
                                      "dan satu-satunya penawarnya adalah **memeriksa di "
                                      "tengah jalan**, bukan di ujungnya."}],
                ]},
                {"t": "band",
                 "md": "0,95⁹ ≈ 0,63. Angka itu sebabnya agen dengan sedikit langkah "
                       "hampir selalu mengalahkan agen dengan banyak langkah."},
            ],
        },

        {"type": "section", "num": "07", "title": "Tiga spesialisasi",
         "lead": "Dan peta sisa buku ini."},

        {
            "type": "slide",
            "kicker": "Peta",
            "title": "Tiga arah, dan masing-masing punya babnya sendiri",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "👥", "h": "Banyak agen",
                     "p": "Beberapa agen dengan peran dan alat berbeda. Menarik di papan "
                          "tulis, mahal di tabel biaya — dan **bab 8** menghitungnya.",
                     "style": "accent"},
                    {"ico": "🖼", "h": "Multi-modal",
                     "p": "Masukannya bukan cuma teks: gambar, layar, dokumen. Yang "
                          "berubah bukan gelungnya, melainkan apa yang bisa jadi bukti. "
                          "**Bab 9**.",
                     "style": "accent"},
                    {"ico": "⌨", "h": "Agen kode",
                     "p": "Kode adalah alat yang paling kuat dan paling tajam: ia bisa "
                          "melakukan apa pun yang bisa dilakukan kode. **Bab 10**.",
                     "style": "accent"},
                ]},
                {"t": "p", "md": "Ketiganya bukan jenis agen yang berbeda. Ketiganya "
                                 "**gelung yang sama** dengan ruang tindakan yang berbeda — "
                                 "yang berubah selalu alatnya, bukan mesinnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Peta",
            "title": "Urutan babnya bukan urutan membangunnya",
            "blocks": [
                {"t": "p", "md": "Buku ini bergerak dari bagian ke sistem: model (bab 2–3), "
                                 "lalu yang ditambahkan padanya — memori (4), alat (5), "
                                 "rencana (6) — lalu cara menilainya (7), lalu ketiga "
                                 "spesialisasi (8–10)."},
                {"t": "steps", "items": [
                    {"h": "Membangunnya justru dari belakang",
                     "p": "Kumpulan uji dulu — sebelum agennya ada. Dua puluh kasus nyata "
                          "dengan hasil yang sudah diketahui, ditulis selagi masih jujur "
                          "tentang apa artinya benar."},
                    {"h": "Lalu alat, lalu batasnya",
                     "p": "Alat baca dulu. Alat tulis belakangan, dan tiap satu dengan "
                          "alasan tertulis."},
                    {"h": "Gelungnya paling akhir",
                     "p": "Bagian yang paling menarik dibaca adalah bagian yang paling "
                          "sedikit menentukan keberhasilannya."},
                ]},
                {"t": "band",
                 "md": "Kalau urutan membangunnya dibalik mengikuti urutan babnya, yang "
                       "terjadi biasanya: gelung yang bagus, alat seadanya, dan tidak ada "
                       "cara mengetahui apakah semuanya bekerja."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Satu sifat",
                     "p": "Agen memilih urutan langkahnya **saat berjalan**. Sisanya akibat."},
                    {"h": "Gelung tanpa syarat henti akan berputar",
                     "p": "Anggaran dan 'tidak ada alat untuk ini' adalah dua penyelamat "
                          "yang paling sering lupa dipasang."},
                    {"h": "Orkestrator adalah kode biasa",
                     "p": "Kalau ia tipis, semua masalah akan terlihat seperti masalah model."},
                    {"h": "Otonomi itu tingkatan",
                     "p": "Pisahkan alat baca dari alat tulis. Perubahan sehari, keamanan "
                          "naik banyak."},
                    {"h": "Nilai dari jejaknya",
                     "p": "Keluaran benar dari alasan yang salah akan berulang, dan tidak "
                          "akan tertangkap kumpulan uji."},
                ]},
            ],
            "notes": "Tutup dengan pertanyaan: dari sistem yang sedang kalian bangun, "
                     "bagian mana yang benar-benar butuh memilih langkahnya sendiri? "
                     "Jawabannya hampir selalu lebih kecil daripada dugaan awal.",
        },
    ],
}
