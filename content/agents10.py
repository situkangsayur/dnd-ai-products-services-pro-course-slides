# -*- coding: utf-8 -*-
"""Bab 10 — Agen kode: alat paling tajam, dan cara memegangnya.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 10.

Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti hanya
URUTAN BABNYA. Isinya materi ajar sendiri, gambarnya digambar sendiri.

Gambar `repo_context` menghitung dua asumsinya sendiri dan mencetak keduanya di
gambar; angkanya bukan kutipan.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import repo_context  # noqa: E402

B = BOOKS["agents"]


MMD_WHYCODE = """
flowchart LR
  Q["Pertanyaan atas data"] --> C["Model MENULIS kode"]
  C --> R["Kode DIJALANKAN"]
  R --> A["Jawaban"]
  A -. "yang membuatnya berbeda:<br/>jawabannya dihitung, bukan ditebak;<br/>dan kodenya bisa dibaca ulang" .-> A
"""

MMD_TOOLS = """
flowchart TB
  subgraph B["Baca — murah, aman"]
    direction LR
    S["cari kode"] --- L["baca berkas"] --- M["peta repo"]
  end
  subgraph T["Tulis — butuh gerbang"]
    direction LR
    E["sunting berkas"] --- X["jalankan perintah"]
  end
  B --> T
"""

MMD_FIND = """
flowchart LR
  P["Peta repo<br/><small>2% jendela</small>"] --> S["Cari<br/><small>nama, simbol, teks</small>"]
  S --> R["Baca 3–5 berkas<br/><small>yang benar-benar relevan</small>"]
  R --> W["Kerjakan"]
  W -. "gagal? cari lagi dengan<br/>istilah berbeda" .-> S
"""

MMD_LOOP = """
flowchart LR
  I["Masalah"] --> E["Sunting"]
  E --> T["Jalankan uji"]
  T -->|"merah"| E
  T -->|"hijau"| D["Selesai"]
  T -. "pemeriksa objektif — inilah yang<br/>membuat refleksi bekerja di sini" .-> T
"""

MMD_AGENTLESS = """
flowchart LR
  subgraph F["Alur tetap"]
    direction LR
    F1["Cari berkas"] --> F2["Usulkan tambalan"] --> F3["Jalankan uji"] --> F4["Pilih yang lulus"]
  end
  subgraph A["Agen bebas"]
    direction LR
    A1["Tujuan"] --> A2["Model memilih<br/>langkah berikutnya"] --> A2
  end
  F ~~~ A
"""


DECK = {
    "id": "agents10",
    "kind": "chapter",
    "number": 10,
    "book": "agents",
    "title": "Agen kode",
    "subtitle": "Kode adalah alat yang bisa menjadi alat apa pun — itu "
                "sebabnya ia paling berguna, dan itu sebabnya ia satu-satunya "
                "yang butuh dinding sungguhan.",
    "source": book_source(10, "agents"),
    "source_url": "",
    "duration": "3 jam (2 sesi)",
    "presenter": [
        {"name": "Hendri Karisma", "role": "Instructor"},
    ],
    "resources": [
        {"kind": "site", "label": "Course home", "href": "../../index.html"},
        {"kind": "github", "label": "ai-agentic-demo — kasus code_analysis",
         "href": "https://github.com/situkangsayur/ai-agentic-demo"},
        {"kind": "book",
         "label": f"{B['authors']}, {B['title']} ({B['publisher']}, {B['edition']})",
         "href": B["site"]},
    ],
    "objectives": [
        "**Menjelaskan kenapa menulis kode mengubah sifat jawaban** — dari "
        "ditebak jadi dihitung, dan dari tak terbaca jadi bisa diperiksa.",
        "**Menyebutkan lima jenis alat kode** dan memisahkan yang baca dari "
        "yang menulis.",
        "**Menghitung kenapa seluruh repo tidak muat**, dan menjelaskan pola "
        "peta-cari-baca.",
        "**Menyebutkan lapis sandbox** beserta apa yang TIDAK ditutupnya.",
        "**Membandingkan alur tetap dengan agen bebas** untuk tugas rekayasa "
        "perangkat lunak.",
        "**Menyebutkan risiko khas** agen kode yang tidak muncul pada agen "
        "lain.",
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "Kenapa kode",
         "lead": "Bukan karena penggunanya programmer."},

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Menulis kode mengubah sifat jawabannya",
            "blocks": [
                {"t": "mmd", "id": "agents10-whycode", "src": MMD_WHYCODE,
                 "cap": "Jawaban yang dihitung, dengan cara menghitung yang bisa dibaca ulang."},
                {"t": "p", "md": "Ketika model menjawab pertanyaan data secara langsung, "
                                 "jawabannya adalah **tebakan yang masuk akal**. Ketika ia "
                                 "menulis kode yang lalu dijalankan, jawabannya **hasil "
                                 "perhitungan** — dan cara menghitungnya ada di layar untuk "
                                 "diperiksa."},
                {"t": "band",
                 "md": "Ini alasan yang sama kenapa modul ini terus mengulang *serahkan "
                       "aritmetika ke kode*. Bedanya di sini: **kodenya ditulis saat itu "
                       "juga**, untuk pertanyaan yang belum pernah ada sebelumnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Penggunanya sering justru bukan programmer",
            "blocks": [
                {"t": "p", "md": "Pemakaian agen kode yang paling banyak menambah nilai "
                                 "sering bukan menulis perangkat lunak, melainkan "
                                 "**menjawab pertanyaan atas data** untuk orang yang tidak "
                                 "menulis kode."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Yang dilihat pengguna**"},
                     {"t": "p", "md": "\\u201cBerapa rata-rata tunggakan nasabah kategori B "
                                      "tahun lalu, dipisah per wilayah?\\u201d — lalu sebuah "
                                      "tabel dan grafik."}],
                    [{"t": "p", "md": "**Yang terjadi**"},
                     {"t": "p", "md": "Agen menulis kueri dan beberapa baris pengolahan, "
                                      "menjalankannya, dan menyusun hasilnya. Kodenya "
                                      "tersimpan di jejak."}],
                ]},
                {"t": "band",
                 "md": "Dan itu yang membuatnya bisa dipertanggungjawabkan: **kalau "
                       "angkanya dipertanyakan, kodenya bisa dibaca.** Jawaban langsung "
                       "dari model tidak punya sifat itu."},
            ],
        },

        {"type": "section", "num": "02", "title": "Alatnya",
         "lead": "Lima jenis, dan garis yang memisahkan dua kelompok."},

        {
            "type": "slide",
            "kicker": "Alat",
            "title": "Lima jenis alat kode, dan garisnya",
            "blocks": [
                {"t": "mmd", "id": "agents10-tools", "src": MMD_TOOLS,
                 "cap": "Membaca aman dan murah; menulis dan menjalankan tidak."},
                {"t": "table",
                 "head": ["Alat", "Kelompok", "Catatan"],
                 "widths": [24, 18, 58],
                 "rows": [
                     ["Peta repo", "Baca", "Struktur repo dalam beberapa ribu token"],
                     ["Cari kode", "Baca", "Berdasarkan nama, simbol, atau teks — bukan "
                      "kemiripan makna"],
                     ["Baca berkas", "Baca", "Sebagian berkas, dengan nomor baris"],
                     ["Sunting berkas", "**Tulis**", "Butuh gerbang, dan harus bisa "
                      "dibatalkan"],
                     ["Jalankan perintah", "**Tulis**", "Paling berbahaya: ia bisa jadi "
                      "alat apa pun"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Alat",
            "title": "Kueri basis data sebagai alat, dan batas yang harus menyertainya",
            "blocks": [
                {"t": "p", "md": "Memberi agen kemampuan menulis kueri sangat kuat untuk "
                                 "pertanyaan analitis — dan membawa risiko yang bentuknya "
                                 "sudah dikenal orang basis data."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "👁", "h": "Hanya baca, selalu",
                     "p": "Akun terpisah yang benar-benar tidak punya izin menulis. Bukan "
                          "janji di prompt — izin di basis datanya.",
                     "style": "good"},
                    {"ico": "⏱", "h": "Batas waktu dan baris",
                     "p": "Kueri tanpa batas bisa menahan basis data produksi. Batasi di "
                          "sisi peladen, bukan di kueri.",
                     "style": "good"},
                    {"ico": "🔒", "h": "Tampilan, bukan tabel mentah",
                     "p": "Agen melihat tampilan yang sudah menyaring kolom pribadi. Yang "
                          "tidak terlihat tidak bisa bocor.",
                     "style": "good"},
                    {"ico": "🧾", "h": "Kuerinya masuk jejak",
                     "p": "Ini bukti terbaik yang bisa Anda punya untuk angka mana pun yang "
                          "dilaporkan.",
                     "style": "good"},
                ]},
            ],
        },

        {"type": "section", "num": "03", "title": "Menemukan yang relevan",
         "lead": "Sebab seluruh repo tidak akan pernah muat."},

        {
            "type": "slide",
            "kicker": "Konteks",
            "title": "Seratus berkas sudah melewati jendela",
            "blocks": [
                repo_context("agents10-repo",
                             cap="Seluruh isi berkas lawan peta satu baris per berkas, "
                                 "dihitung. Langkahi menurut ukuran repo.",
                             note="Dua asumsinya dicetak di gambar. Yang tidak bergantung "
                                  "pada asumsi adalah selisih dua orde besaran antara "
                                  "membaca semuanya dan membaca petanya."),
                {"t": "p", "md": "\\u201cMasukkan saja seluruh kode ke konteks\\u201d berhenti "
                                 "bekerja hampir seketika. Petanya dua orde besaran lebih "
                                 "kecil — dan itulah yang membuat pola **peta → cari → baca "
                                 "beberapa** jadi satu-satunya yang bisa diskalakan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Konteks",
            "title": "Peta, cari, baca sedikit",
            "blocks": [
                {"t": "mmd", "id": "agents10-find", "src": MMD_FIND,
                 "cap": "Tiga langkah, dan hanya langkah terakhir yang mahal."},
                {"t": "p", "md": "Dua langkah pertama murah dan bisa diulang; hanya langkah "
                                 "ketiga yang memakan konteks. Itu sebabnya urutannya "
                                 "penting."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Konteks",
            "title": "…dan apa yang dikerjakan tiap langkah",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Peta memberi tahu apa yang ADA",
                     "p": "Nama berkas, kelas, fungsi utama. Cukup untuk memutuskan ke mana "
                          "harus mencari."},
                    {"h": "Pencarian menyempitkan",
                     "p": "Berdasarkan nama simbol atau teks — dan di sini pencarian teks "
                          "biasa **mengalahkan** pencarian kemiripan makna, sebab nama "
                          "fungsi adalah nama, bukan konsep."},
                    {"h": "Baca tiga sampai lima berkas",
                     "p": "Itu yang masuk konteks. Sisanya tidak pernah dibaca, dan itu "
                          "bukan kerugian."},
                ]},
                {"t": "band",
                 "md": "Pola yang persis sama dengan Bab 4 dan Bab 9: **jaring lebar dengan "
                       "yang murah, saringan halus dengan yang mahal.** Ia muncul untuk "
                       "ketiga kalinya karena alasan yang sama."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Konteks",
            "title": "Memadatkan konteks tanpa kehilangan yang menentukan",
            "blocks": [
                {"t": "p", "md": "Sesi kerja yang panjang akan memenuhi jendela. Bab 4 sudah "
                                 "menyebut bahayanya meringkas berulang; untuk kode ada "
                                 "beberapa hal yang **tidak boleh** hilang dalam pemadatan."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📌", "h": "Harus bertahan",
                     "p": "Tujuan awal, berkas yang sedang disunting, hasil uji terakhir, "
                          "dan keputusan yang sudah diambil beserta alasannya.",
                     "style": "good"},
                    {"ico": "🗑", "h": "Boleh hilang",
                     "p": "Isi berkas yang sudah dibaca (bisa dibaca ulang), keluaran "
                          "perintah yang sudah tidak relevan, jalan buntu yang sudah "
                          "ditinggalkan."},
                ]},
                {"t": "band",
                 "md": "Aturan yang membedakan keduanya sama seperti Bab 4: **apa yang bisa "
                       "diambil ulang dengan alat boleh dibuang; apa yang hanya ada di "
                       "percakapan harus dipertahankan.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Konteks",
            "title": "Menjaga singgahan tetap hidup di sesi kode",
            "blocks": [
                {"t": "p", "md": "Bab 2 menyebut singgahan prompt sebagai penghematan "
                                 "terbesar yang tersedia. Pada agen kode ia lebih penting "
                                 "lagi, sebab sesinya panjang dan bagian tetapnya besar — "
                                 "perintah sistem, skema alat, dan peta repo."},
                {"t": "steps", "items": [
                    {"h": "Taruh yang tetap di depan, dan jangan diutak-atik",
                     "p": "Peta repo yang disusun ulang tiap giliran membunuh singgahan "
                          "tanpa satu pun pesan galat."},
                    {"h": "Tambahkan di belakang, jangan menyisipkan di tengah",
                     "p": "Menyisipkan sesuatu di tengah mengubah awalan semua yang "
                          "sesudahnya."},
                    {"h": "Periksa angkanya, jangan percaya",
                     "p": "`cache_read_input_tokens` harus bukan nol. Kalau jadi nol, "
                          "sesuatu di awalan berubah."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Alat",
            "title": "Menyunting: tambalan, bukan tulis ulang",
            "blocks": [
                {"t": "p", "md": "Ada dua cara alat suntingan bisa dirancang, dan pilihannya "
                                 "mengubah banyak hal sekaligus."},
                {"t": "table",
                 "head": ["Cara", "Biaya token", "Risikonya"],
                 "widths": [28, 26, 46],
                 "rows": [
                     ["Kembalikan seluruh berkas", "Besar — dua kali isi berkas",
                      "Bagian yang tidak disentuh bisa ikut berubah tanpa disadari"],
                     ["**Tambalan berupa diff**", "Kecil — hanya yang berubah",
                      "Bisa gagal diterapkan kalau berkasnya bergeser; itu **kegagalan "
                      "yang kelihatan**"],
                 ]},
                {"t": "band",
                 "md": "Baris kedua lebih baik karena alasan yang tidak langsung terlihat: "
                       "**diff yang gagal diterapkan adalah galat**, sedangkan tulis ulang "
                       "yang diam-diam mengubah baris lain adalah bug yang lolos ke "
                       "tinjauan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Alat",
            "title": "Mencari kode: teks mengalahkan makna",
            "blocks": [
                {"t": "p", "md": "Bab 4 menyebut kelemahan pencarian kemiripan makna untuk "
                                 "angka dan pengenal. Pada kode, kelemahan itu jadi "
                                 "menentukan: **nama fungsi adalah nama, bukan konsep.**"},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔤", "h": "Cari teks persis",
                     "p": "Nama simbol, pemanggilan, string galat. Cepat, pasti, dan "
                          "hampir selalu yang benar.",
                     "style": "good"},
                    {"ico": "🌳", "h": "Cari menurut struktur",
                     "p": "Definisi, pemanggil, penurunan kelas. Lebih tepat lagi kalau "
                          "bahasanya mendukung.",
                     "style": "good"},
                    {"ico": "🧭", "h": "Cari kemiripan makna",
                     "p": "Berguna untuk \u201cdi mana logika kredit?\u201d dan buruk "
                          "untuk \u201cdi mana `hitung_dscr` dipanggil?\u201d"},
                ]},
                {"t": "band",
                 "md": "Bentuk yang paling sering benar: **cari teks dulu; kemiripan makna "
                       "hanya kalau pencarian teks tidak menemukan apa-apa** — dan "
                       "sebutkan dalam deskripsi alatnya kapan masing-masing dipakai."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Alat",
            "title": "Membaca berkas: sebagian, dengan nomor baris",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Kembalikan potongan, bukan berkas penuh",
                     "p": "Berkas 2 000 baris masuk konteks satu kali dan dibayar berkali "
                          "kali. Sebagian besar tugas butuh tiga puluh baris."},
                    {"h": "Sertakan nomor barisnya",
                     "p": "Supaya tambalan bisa merujuk lokasi, dan supaya jejaknya bisa "
                          "dibaca ulang."},
                    {"h": "Sebutkan kalau dipotong",
                     "p": "Berkas terpotong yang menyamar sebagai berkas penuh menghasilkan "
                          "kesimpulan yang salah tentang apa yang ada di dalamnya."},
                ]},
                {"t": "band",
                 "md": "Ketiganya pengulangan aturan Bab 5 tentang mengolah keluaran alat, "
                       "diterapkan pada bentuk data yang paling sering membanjiri konteks "
                       "agen kode."},
            ],
        },

        {"type": "section", "num": "04", "title": "Dinding",
         "lead": "Satu-satunya alat di modul ini yang butuh isolasi sungguhan."},

        {
            "type": "slide",
            "kicker": "Sandbox",
            "title": "Alat yang bisa menjadi alat apa pun",
            "blocks": [
                {"t": "p", "md": "Semua alat lain di modul ini punya batas yang jelas: "
                                 "`ambil_data` mengambil data. Alat yang menjalankan kode "
                                 "tidak punya batas seperti itu — **ia bisa melakukan apa "
                                 "pun yang bisa dilakukan kode** di lingkungan tempat ia "
                                 "berjalan."},
                {"t": "band",
                 "md": "Karena itu pertanyaan keamanannya berubah bentuk. Untuk alat lain: "
                       "*apa yang boleh dipanggil?* Untuk alat kode: **di mana ia berjalan, "
                       "dan apa yang bisa dijangkau dari sana?**"},
                {"t": "p", "md": "Dan itu pertanyaan infrastruktur, bukan pertanyaan prompt "
                                 "— dijawab dengan proses terpisah, jaringan yang ditutup, "
                                 "dan lingkungan yang tidak memuat kredensial apa pun."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Sandbox",
            "title": "Berlapis, dan jujur soal yang tidak ditutupnya",
            "blocks": [
                {"t": "table",
                 "head": ["Lapis", "Menahan", "TIDAK menahan"],
                 "widths": [24, 36, 40],
                 "rows": [
                     ["Tanpa kredensial di lingkungan", "Pemakaian kunci yang bocor",
                      "Kunci yang ada di dalam kode yang dibacanya"],
                     ["Jaringan ditutup", "Pengiriman data keluar",
                      "Apa pun yang sudah ada di dalam sandbox"],
                     ["Batas waktu dan memori", "Gelung tak berujung",
                      "Kerusakan yang selesai dalam satu detik"],
                     ["Proses / kontainer terpisah", "Sebagian besar hal",
                      "Celah pada kernel atau salah konfigurasi"],
                     ["Berkas hanya-baca", "Perubahan yang tidak disengaja",
                      "Pembacaan berkas yang seharusnya tidak terbaca"],
                 ]},
                {"t": "band",
                 "md": "Kolom ketiga yang membuat tabel ini berguna. **Sandbox yang "
                       "dijelaskan sebagai \\u201caman\\u201d membuat orang berhenti "
                       "berpikir**; yang menyebut batasnya membuat orang menaruh data "
                       "sensitif di tempat lain."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Sandbox",
            "title": "Menjalankan perintah bukan hal yang sama dengan menjalankan kode",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Penerjemah kode**"},
                     {"t": "p", "md": "Satu bahasa, pustaka yang bisa dibatasi, keluaran "
                                      "yang bentuknya diketahui. Bisa dikurung relatif "
                                      "rapat."}],
                    [{"t": "p", "md": "**Baris perintah**"},
                     {"t": "p", "md": "Seluruh sistem operasi, termasuk hal yang tidak "
                                      "terpikir saat merancang. Daftar perintah yang "
                                      "diizinkan lebih masuk akal daripada daftar yang "
                                      "dilarang."}],
                ]},
                {"t": "band",
                 "md": "Kalau harus memilih satu untuk dimulai, mulai dari **penerjemah "
                       "kode tanpa jaringan**. Ia mencakup sebagian besar kegunaan analitis "
                       "dengan permukaan yang jauh lebih kecil."},
            ],
        },

        {"type": "section", "num": "05", "title": "Untuk rekayasa perangkat lunak",
         "lead": "Di sini pemeriksanya sudah ada, dan itu mengubah segalanya."},

        {
            "type": "slide",
            "kicker": "Rekayasa",
            "title": "Gelung yang punya pemeriksa objektif",
            "blocks": [
                {"t": "mmd", "id": "agents10-loop", "src": MMD_LOOP,
                 "cap": "Sunting, jalankan uji, ulangi — dan ujinya yang menentukan berhenti."},
                {"t": "p", "md": "Bab 3 dan Bab 6 menyebut syarat refleksi bekerja: harus "
                                 "ada pemeriksa yang lebih mudah daripada menjawab. "
                                 "Pemrograman adalah domain yang **sudah punya itu sejak "
                                 "awal** — uji yang dijalankan, penyusun yang mengeluh, "
                                 "linter yang menolak."},
                {"t": "band",
                 "md": "Itu sebabnya agen kode terasa jauh lebih berhasil daripada agen di "
                       "domain lain, dan **bukan karena modelnya lebih pandai soal kode**. "
                       "Ia bekerja di tempat yang jawabannya bisa diperiksa mesin."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa",
            "title": "Alur tetap sering mengalahkan agen bebas",
            "blocks": [
                {"t": "mmd", "id": "agents10-agentless", "src": MMD_AGENTLESS,
                 "cap": "Empat langkah tetap, lawan gelung yang memilih sendiri."},
                {"t": "p", "md": "Untuk perbaikan bug yang bentuknya berulang — temukan "
                                 "berkas, usulkan beberapa tambalan, jalankan uji, ambil "
                                 "yang lulus — **alur tetap sering mengungguli agen bebas**, "
                                 "dengan biaya lebih kecil dan hasil yang bisa diramalkan."},
                {"t": "band",
                 "md": "Ini pengulangan pesan Bab 1 pada domain yang paling banyak "
                       "menghasilkan demo agen: ==kalau langkahnya sudah diketahui, yang "
                       "Anda butuhkan alur tetap==, dan itu tetap berlaku di sini."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa",
            "title": "Membaca angka tolok ukur kode dengan curiga",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔎", "h": "Kontaminasi",
                     "p": "Repo publik dan isunya kemungkinan besar ada di data latih. "
                          "Angka tinggi pada isu lama tidak berarti banyak.",
                     "style": "bad"},
                    {"ico": "🧪", "h": "Ujinya yang menilai",
                     "p": "\\u201cBerhasil\\u201d berarti uji yang ada lulus — bukan bahwa "
                          "perbaikannya benar. Tambalan yang mematikan ujinya juga lulus.",
                     "style": "bad"},
                    {"ico": "🔁", "h": "Berapa percobaan?",
                     "p": "pass@k dengan k besar (Bab 7) membuat angka melonjak tanpa "
                          "keandalan bertambah.",
                     "style": "bad"},
                    {"ico": "📦", "h": "Bukan repo Anda",
                     "p": "Basis kode besar yang lama, tanpa uji, dengan konvensi sendiri "
                          "adalah masalah yang berbeda.",
                     "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa",
            "title": "Basis kode yang sudah ada adalah masalah yang berbeda",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Proyek baru**"},
                     {"t": "p", "md": "Tidak ada konvensi yang harus dipatuhi, tidak ada "
                                      "kode lama yang bisa rusak, dan uji ditulis bersamaan. "
                                      "Di sinilah demo terlihat mengesankan."}],
                    [{"t": "p", "md": "**Basis kode yang berumur**"},
                     {"t": "p", "md": "Konvensi tak tertulis, kaitan yang tidak terlihat, "
                                      "uji yang menutup sebagian kecil saja. Di sinilah "
                                      "pekerjaan sebenarnya berada."}],
                ]},
                {"t": "p", "md": "Yang paling menolong pada kolom kanan bukan model yang "
                                 "lebih pandai, melainkan **konteks yang lebih baik**: "
                                 "berkas panduan konvensi, peta modul, dan contoh perubahan "
                                 "serupa yang pernah diterima."},
                {"t": "band",
                 "md": "Pola yang sama dengan seluruh modul: **perbaiki apa yang masuk ke "
                       "konteks sebelum mengganti modelnya.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa",
            "title": "Perubahan yang menyentuh banyak berkas",
            "blocks": [
                {"t": "p", "md": "Perubahan satu berkas relatif mudah. Perubahan yang harus "
                                 "konsisten di sepuluh berkas adalah tempat agen paling "
                                 "sering gagal separuh jalan — dan separuh jalan pada kode "
                                 "berarti **repo yang tidak bisa dibangun**."},
                {"t": "steps", "items": [
                    {"h": "Kumpulkan seluruh tambalan dulu, terapkan di akhir",
                     "p": "Sama seperti Bab 8: tunda tulisan sampai semuanya siap, supaya "
                          "kegagalan sebagian tidak meninggalkan keadaan setengah jadi."},
                    {"h": "Jalankan pembangunan dan uji sesudah semuanya diterapkan",
                     "p": "Bukan sesudah tiap berkas — itu memberi sinyal yang menyesatkan."},
                    {"h": "Kalau gagal, kembalikan semuanya",
                     "p": "Cabang terpisah membuat ini satu perintah, bukan satu "
                          "penyelamatan."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa",
            "title": "Meninjau kode yang ditulis agen",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔍", "h": "Baca diff-nya, bukan ringkasannya",
                     "p": "Ringkasan yang ditulis agen menjelaskan apa yang **dimaksudkannya**. "
                          "Diff menunjukkan apa yang **dilakukannya**.",
                     "style": "accent"},
                    {"ico": "🧪", "h": "Periksa apakah ujinya ikut berubah",
                     "p": "Uji yang disesuaikan supaya lulus adalah temuan, bukan detail.",
                     "style": "accent"},
                    {"ico": "🗑", "h": "Perhatikan yang DIHAPUS",
                     "p": "Penanganan galat dan pemeriksaan yang hilang jarang terlihat di "
                          "ringkasan mana pun."},
                    {"ico": "📏", "h": "Tolak perubahan yang terlalu besar",
                     "p": "Diff yang tidak bisa dibaca dalam sepuluh menit tidak akan "
                          "ditinjau dengan sungguh-sungguh — oleh siapa pun."},
                ]},
                {"t": "band",
                 "md": "Kartu terakhir sering menentukan apakah agen kode benar-benar "
                       "menghemat waktu: **perubahan kecil yang sering mengalahkan "
                       "perubahan besar yang jarang**, sebab hanya yang pertama benar-benar "
                       "ditinjau."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa",
            "title": "Merencanakan sebelum menyunting",
            "blocks": [
                {"t": "p", "md": "Bab 6 menyebut rencana berguna kalau tiap langkahnya bisa "
                                 "dipetakan ke alat dan ditandai selesai. Pada kode, "
                                 "syarat itu mudah dipenuhi — dan rencananya bisa "
                                 "ditunjukkan sebelum ada perubahan apa pun."},
                {"t": "steps", "items": [
                    {"h": "Sebutkan berkas yang akan disentuh",
                     "p": "Sebelum menyentuhnya. Peninjau bisa menghentikan arah yang salah "
                          "ketika biayanya masih nol."},
                    {"h": "Sebutkan uji yang harus lulus",
                     "p": "Kalau tidak ada ujinya, langkah pertama adalah menulis ujinya."},
                    {"h": "Sebutkan apa yang TIDAK akan diubah",
                     "p": "Ini yang paling menenangkan peninjau, dan paling jarang "
                          "dituliskan."},
                ]},
                {"t": "band",
                 "md": "Bentuk pengawasan yang paling bisa dijalankan tetap sama seperti "
                       "Bab 6: **satu tinjauan rencana yang benar-benar dibaca, bukan "
                       "sepuluh persetujuan yang diklik.**"},
            ],
        },

        {"type": "section", "num": "06", "title": "Melatih model kode",
         "lead": "Satu gelung yang berjalan karena pemeriksanya gratis."},

        {
            "type": "slide",
            "kicker": "Melatih",
            "title": "Data buatan yang bisa diperiksa sendiri",
            "blocks": [
                {"t": "p", "md": "Kode punya sifat yang jarang: **benar atau tidaknya bisa "
                                 "diperiksa mesin, gratis, dan berkali-kali.** Itu membuat "
                                 "gelung yang tidak mungkin di domain lain jadi mungkin di "
                                 "sini."},
                {"t": "steps", "items": [
                    {"h": "Bangkitkan soal dan calon jawabannya",
                     "p": "Dari repo yang ada, atau dari soal yang disusun model sendiri."},
                    {"h": "Jalankan ujinya",
                     "p": "Yang lulus disimpan, yang gagal dibuang. Tidak ada manusia yang "
                          "perlu menilai."},
                    {"h": "Latih pada yang lulus, ulangi",
                     "p": "Model membaik, soal yang bisa diselesaikannya bertambah, dan "
                          "putaran berikutnya menghasilkan data yang lebih baik."},
                ]},
                {"t": "band",
                 "md": "Bab 3 menyebut batas gelung semacam ini, dan batas itu berlaku di "
                       "sini juga: **ia hanya sekuat pemeriksanya**, dan soal yang "
                       "dibangkitkan cenderung mirip yang sudah bisa dijawab."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Melatih",
            "title": "Kenapa gelung itu berhenti bekerja di luar kode",
            "blocks": [
                {"t": "p", "md": "Gelung data buatan tadi terlihat seperti resep umum, dan "
                                 "ia bukan. Ia bergantung pada satu sifat yang jarang: "
                                 "**pemeriksa yang gratis, otomatis, dan tidak bisa "
                                 "dibujuk.**"},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Punya pemeriksa seperti itu**"},
                     {"t": "bullets", "items": [
                         "Kode — uji dijalankan",
                         "Matematika — hasilnya dicocokkan",
                         "Kueri — dibandingkan dengan jawaban yang diketahui",
                     ]}],
                    [{"t": "p", "md": "**Tidak punya**"},
                     {"t": "bullets", "items": [
                         "Menilai kelayakan kredit",
                         "Meringkas dokumen",
                         "Menjawab pertanyaan kebijakan",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Untuk kolom kanan, yang menggantikan pemeriksa otomatis adalah "
                       "**kumpulan uji yang ditulis manusia** — Bab 7 — dan tidak ada "
                       "jalan pintas yang menghindarinya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Risiko",
            "title": "Kode yang berjalan bukan kode yang benar",
            "blocks": [
                {"t": "p", "md": "Gelung sunting-uji berhenti ketika ujinya hijau. Itu "
                                 "syarat yang jelas dan **bukan** definisi kebenaran — ia "
                                 "hanya sekuat cakupan ujinya."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "\U0001F573", "h": "Yang tidak diuji",
                     "p": "Perilaku yang tidak punya uji bisa rusak tanpa satu pun lampu "
                          "merah menyala.",
                     "style": "bad"},
                    {"ico": "\U0001F3AF", "h": "Kasus tepi",
                     "p": "Uji yang ada biasanya menutup jalur bahagia. Kasus tepi justru "
                          "yang paling sering rusak.",
                     "style": "bad"},
                    {"ico": "\u26A1", "h": "Sifat non-fungsional",
                     "p": "Kinerja, penggunaan memori, dan keamanan hampir tidak pernah "
                          "punya uji.",
                     "style": "bad"},
                ]},
                {"t": "band",
                 "md": "Karena itu tinjauan manusia tetap wajib, dan pertanyaannya bukan "
                       "\u201capakah ujinya lulus\u201d melainkan **\u201capa yang bisa "
                       "rusak dan tidak akan ketahuan\u201d**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Menyimpan konteks proyek supaya tidak diulang tiap sesi",
            "blocks": [
                {"t": "p", "md": "Hal yang sama dijelaskan berulang tiap sesi — konvensi, "
                                 "cara menjalankan uji, bagian mana yang rapuh — adalah "
                                 "biaya yang bisa dihapus sekali."},
                {"t": "steps", "items": [
                    {"h": "Satu berkas panduan di repo",
                     "p": "Konvensi, perintah yang dipakai, dan hal yang tidak boleh "
                          "disentuh. Ditinjau seperti kode, diversikan seperti kode."},
                    {"h": "Taruh di bagian tetap konteks",
                     "p": "Supaya ikut disinggahkan, bukan dikirim ulang sebagai pesan baru "
                          "tiap kali."},
                    {"h": "Perbarui ketika agen salah menebak",
                     "p": "Tiap kesalahan yang berasal dari konvensi yang tidak tertulis "
                          "adalah satu baris yang kurang di berkas itu."},
                ]},
                {"t": "band",
                 "md": "Langkah ketiga yang membuatnya membaik sendiri: **berkas panduan "
                       "yang tumbuh dari kesalahan nyata** jauh lebih berguna daripada yang "
                       "ditulis sekaligus di awal."},
            ],
        },

        {"type": "section", "num": "07", "title": "Risiko dan praktik",
         "lead": "Yang khas agen kode, dan tidak muncul pada agen lain."},

        {
            "type": "slide",
            "kicker": "Risiko",
            "title": "Empat risiko yang khas agen kode",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔑", "h": "Rahasia di dalam kode",
                     "p": "Agen yang membaca repo membaca juga kunci yang tertinggal di "
                          "sana — dan bisa memasukkannya ke konteks, lalu ke jejak.",
                     "style": "bad"},
                    {"ico": "📦", "h": "Ketergantungan yang ditambahkannya",
                     "p": "`pip install` sesuatu yang namanya mirip pustaka asli adalah "
                          "kelas serangan tersendiri.",
                     "style": "bad"},
                    {"ico": "🧪", "h": "Menyesuaikan uji, bukan kode",
                     "p": "Cara tercepat membuat uji hijau adalah mengubah ujinya. Ini "
                          "terjadi, dan tertangkap hanya kalau diff-nya dibaca.",
                     "style": "bad"},
                    {"ico": "🗑", "h": "Perubahan yang merusak diam-diam",
                     "p": "Menghapus penanganan galat supaya lulus uji terlihat seperti "
                          "penyederhanaan.",
                     "style": "bad"},
                ]},
                {"t": "p", "md": "Keempatnya punya satu penawar yang sama dan membosankan: "
                                 "**setiap perubahan lewat tinjauan manusia, sebagai diff "
                                 "yang dibaca** — persis seperti kode dari orang lain."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Risiko",
            "title": "Rahasia: cegah di dua tempat, bukan satu",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Jangan ada rahasia di repo",
                     "p": "Ini seharusnya sudah benar sebelum ada agen, dan agen membuat "
                          "akibatnya lebih cepat terasa."},
                    {"h": "Saring saat masuk konteks",
                     "p": "Pola kunci yang dikenali dibuang sebelum masuk — sebab yang "
                          "masuk konteks akan masuk jejak."},
                    {"h": "Saring saat masuk jejak",
                     "p": "Jejak disimpan lama dan dibaca banyak orang. Ini tempat "
                          "kebocoran yang paling sering tidak terpikir."},
                ]},
                {"t": "band",
                 "md": "Perhatikan langkah ketiga: **jejak yang dirancang untuk audit bisa "
                       "berubah jadi tempat penyimpanan rahasia** kalau tidak ada yang "
                       "menyaringnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Urutan memasang agen kode dengan aman",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Mulai dari baca saja",
                     "p": "Peta, cari, baca. Agen yang menjelaskan basis kode sudah berguna "
                          "dan tidak bisa merusak apa pun."},
                    {"h": "Tambahkan penerjemah kode tanpa jaringan",
                     "p": "Ini membuka sebagian besar kegunaan analitis dengan permukaan "
                          "terkecil."},
                    {"h": "Baru sunting berkas, dengan diff yang ditinjau",
                     "p": "Dan tidak pernah langsung ke cabang utama."},
                    {"h": "Baris perintah paling akhir, dengan daftar yang diizinkan",
                     "p": "Kalau memang diperlukan. Banyak sistem berhenti sebelum ini dan "
                          "sudah cukup."},
                ]},
                {"t": "band",
                 "md": "Urutan ini sama bentuknya dengan Bab 5: **alat baca dulu, alat "
                       "tulis satu per satu dengan alasan tertulis.** Yang berubah cuma "
                       "seberapa tajam alatnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Yang ada di demo, dan apa yang jujur disebutkan tentangnya",
            "blocks": [
                {"t": "p", "md": "Repo demo punya satu kasus yang menjalankan kode di balik "
                                 "sandbox berlapis — dan dokumennya menyebut **apa yang "
                                 "tidak ditutup lapisan-lapisan itu**, bukan menyatakannya "
                                 "aman."},
                {"t": "p", "md": "Itu keputusan penulisan yang disengaja, dan pantas "
                                 "ditiru: pembaca yang diberi tahu batasnya akan menaruh "
                                 "data sensitif di tempat lain. Pembaca yang diberi tahu "
                                 "\\u201caman\\u201d tidak akan."},
                {"t": "band",
                 "md": "Sama seperti aplikasi selulernya, yang dokumennya menyebut versi "
                       "Flutter yang dipakai untuk membangunnya dan apa yang belum diuji. "
                       "**Klaim yang bisa diperiksa mengalahkan klaim yang menenangkan.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Berapa biayanya, dan di mana biayanya",
            "blocks": [
                {"t": "p", "md": "Agen kode adalah beban konteks yang berat: peta repo, "
                                 "berkas yang dibaca, keluaran uji, dan diff — semuanya "
                                 "masuk riwayat dan dibayar ulang tiap giliran."},
                {"t": "table",
                 "head": ["Sumber biaya", "Besar kalau", "Obatnya"],
                 "widths": [26, 34, 40],
                 "rows": [
                     ["Berkas yang dibaca", "Dibaca penuh, bukan sebagian",
                      "Potongan bernomor baris"],
                     ["Keluaran uji", "Seluruh keluaran masuk, termasuk yang lulus",
                      "Kembalikan yang gagal saja"],
                     ["Peta repo", "Repo besar",
                      "Peta per direktori, dimuat saat diperlukan"],
                     ["Iterasi", "Gelung sunting-uji berputar banyak",
                      "Anggaran putaran, dan uji yang lebih cepat"],
                 ]},
                {"t": "band",
                 "md": "Baris kedua yang paling mudah diperbaiki dan paling sering "
                       "terlewat: **keluaran uji yang lulus tidak memberi informasi apa "
                       "pun**, dan bisa ribuan token."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Angka yang memberi tahu agen kode Anda sehat",
            "blocks": [
                {"t": "table",
                 "head": ["Angka", "Sehat kalau", "Gejala kalau tidak"],
                 "widths": [28, 30, 42],
                 "rows": [
                     ["Diff yang diterima tanpa perubahan", "Naik pelan",
                      "Turun → konteksnya memburuk, bukan modelnya"],
                     ["Putaran sunting-uji per tugas", "Kecil dan stabil",
                      "Naik → ujinya lambat, atau galatnya tidak informatif"],
                     ["Berkas dibaca per tugas", "Sedikit",
                      "Banyak → pencariannya tidak menemukan yang tepat"],
                     ["Uji yang ikut berubah", "**Nol**",
                      "Bukan nol → periksa satu per satu, ini bukan detail"],
                 ]},
                {"t": "p", "md": "Baris terakhir pantas jadi pemeriksaan otomatis: "
                                 "**tandai tiap diff yang menyentuh berkas uji**, dan minta "
                                 "alasan tertulis. Sering sah; kadang tidak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Kapan agen kode adalah alat yang salah",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🧭", "h": "Keputusan arsitektur",
                     "p": "Pilihan yang akibatnya bertahun-tahun dan pertukarannya tidak "
                          "bisa diuji. Agen bisa menuliskan pilihannya; ia tidak bisa "
                          "menanggungnya.",
                     "style": "bad"},
                    {"ico": "🔍", "h": "Kode yang tidak dipahami siapa pun",
                     "p": "Kalau tidak ada manusia yang bisa meninjau hasilnya, "
                          "kecepatannya tidak berarti apa-apa.",
                     "style": "bad"},
                    {"ico": "🚨", "h": "Perbaikan darurat di produksi",
                     "p": "Tekanan waktu adalah keadaan terburuk untuk meninjau diff dengan "
                          "sungguh-sungguh.",
                     "style": "bad"},
                    {"ico": "✅", "h": "Di sinilah ia menang",
                     "p": "Perubahan berulang, migrasi mekanis, menulis uji, menjelaskan "
                          "kode yang sudah ada, dan analisis data.",
                     "style": "good"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup modul",
            "title": "Sepuluh bab, satu kalimat yang paling sering berlaku",
            "blocks": [
                {"t": "p", "md": "Kalau hanya satu hal yang dibawa dari sepuluh bab ini: "
                                 "**batas kemampuan sebuah agen ada di alat yang "
                                 "dimilikinya** — dan itu satu-satunya hal tentang sistem "
                                 "berbasis model yang jawabannya berupa daftar, bukan "
                                 "statistik."},
                {"t": "steps", "items": [
                    {"h": "Karena itu bisa diuji",
                     "p": "Satu uji yang gagal kalau seseorang menambahkan alat yang "
                          "melanggar batasnya."},
                    {"h": "Karena itu bisa dijelaskan",
                     "p": "Kepada pemeriksa, kepada atasan, kepada orang yang menanggung "
                          "akibatnya."},
                    {"h": "Karena itu bertahan",
                     "p": "Prompt bisa diubah siapa saja; alat yang tidak ada tetap tidak "
                          "ada."},
                ]},
                {"t": "band",
                 "md": "Sisanya — memori, rencana, refleksi, banyak agen, multi-modal — "
                       "semuanya menambah kemampuan. **Tidak satu pun mengubah kalimat di "
                       "atas.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Kode mengubah jawaban dari ditebak jadi dihitung",
                     "p": "Dan cara menghitungnya tersimpan untuk diperiksa."},
                    {"h": "Seluruh repo tidak akan muat; petanya muat",
                     "p": "Peta → cari → baca beberapa. Pola yang sama seperti Bab 4 dan 9."},
                    {"h": "Ini satu-satunya alat yang butuh dinding sungguhan",
                     "p": "Dan dindingnya harus menyebutkan apa yang tidak ditutupnya."},
                    {"h": "Ia berhasil karena pemeriksanya sudah ada",
                     "p": "Bukan karena modelnya lebih pandai soal kode."},
                    {"h": "Alur tetap masih sering menang",
                     "p": "Pesan Bab 1, di domain yang paling banyak menghasilkan demo "
                          "agen."},
                ]},
            ],
            "notes": "Penutup modul: dari sepuluh bab ini, satu kalimat yang paling sering "
                     "berlaku — batas kemampuan sebuah agen ada di alat yang dimilikinya, "
                     "dan itu satu-satunya hal tentang sistem berbasis model yang "
                     "jawabannya bisa berupa daftar.",
        },
    ],
}
