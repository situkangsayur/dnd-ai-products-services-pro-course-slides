# -*- coding: utf-8 -*-
"""Bab 4 — Ingatan: apa yang disimpan, apa yang dicari lagi, apa yang dibuang.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 4.

Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti hanya
URUTAN BABNYA. Isinya materi ajar sendiri, gambarnya digambar sendiri.

Gambar `memory_decay` menghitung pemangkatan asumsinya sendiri; asumsinya
dicetak di gambar sebab bentuk eksponensialnya yang jadi pelajaran, bukan
angkanya.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import chunking, memory_decay  # noqa: E402

B = BOOKS["agents"]


MMD_TIERS = """
flowchart LR
  W["Ingatan kerja<br/><small>giliran ini saja —<br/>hasil alat mentah</small>"]
  S["Ingatan jangka pendek<br/><small>percakapan ini —<br/>daftar pesan</small>"]
  L["Ingatan jangka panjang<br/><small>di luar konteks —<br/>diambil saat perlu</small>"]
  W --> S
  S -->|"disaring, bukan disalin"| L
  L -->|"dicari kembali"| S
"""

MMD_HYBRID = """
flowchart LR
  A["Perintah sistem<br/><small>selalu ada</small>"]
  B["Giliran awal<br/><small>tujuan &amp; batasan</small>"]
  C["Bagian tengah<br/><small>diringkas</small>"]
  D["N giliran terakhir<br/><small>utuh</small>"]
  A --> B --> C --> D
"""

MMD_RAG = """
flowchart LR
  Q["Pertanyaan"] --> E["Diubah jadi vektor"]
  E --> S["Dicari yang mirip"]
  S --> K["Potongan teratas"]
  K --> M["Model menjawab<br/><small>hanya dari potongan ini</small>"]
  K -. "yang tidak terambil<br/>tidak bisa dijawab" .-> M
"""

MMD_AGENTIC = """
flowchart TB
  G["Pertanyaan"] --> M["Model"]
  M -->|"memutuskan APA yang dicari"| T["Alat pencarian"]
  T --> O["Hasil"]
  O --> M
  M -->|"kurang — cari lagi<br/>dengan kata berbeda"| T
  M -->|"cukup"| A["Jawaban + kutipan"]
"""

MMD_POISON = """
flowchart LR
  U["Dokumen / tiket / halaman"] -->|"dibaca agen"| C["Konteks"]
  C --> M["Model"]
  M -->|"menuruti kalimat<br/>yang ada DI DALAM data"| X["Tindakan yang tidak diminta"]
  C -. "ingatan yang menyimpannya<br/>membuatnya berulang esok hari" .-> C
"""


DECK = {
    "id": "agents04",
    "kind": "chapter",
    "number": 4,
    "book": "agents",
    "title": "Ingatan: yang disimpan, yang dicari lagi, yang dibuang",
    "subtitle": "Model tidak mengingat apa pun. Semua yang tampak seperti "
                "ingatan adalah keputusan rekayasa — dan tiap keputusannya "
                "punya harga yang bisa dihitung.",
    "source": book_source(4, "agents"),
    "source_url": "",
    "duration": "3 jam (2 sesi)",
    "presenter": [
        {"name": "Hendri Karisma", "role": "Instructor"},
    ],
    "resources": [
        {"kind": "site", "label": "Course home", "href": "../../index.html"},
        {"kind": "book",
         "label": f"{B['authors']}, {B['title']} ({B['publisher']}, {B['edition']})",
         "href": B["site"]},
    ],
    "objectives": [
        "**Menyebutkan tiga lapis ingatan** dan menentukan apa yang pantas "
        "disimpan di masing-masing.",
        "**Membandingkan memangkas dan meringkas**, dan menyebutkan kerugian "
        "yang tidak terlihat dari yang kedua.",
        "**Menjelaskan pengambilan sebagai ALAT**, bukan sebagai langkah "
        "praproses — dan menyebutkan akibatnya pada jejak dan kutipan.",
        "**Menyebutkan empat operasi rekayasa konteks** dan menerapkannya pada "
        "satu gelung yang terlalu panjang.",
        "**Menyebutkan dua kelas serangan** yang muncul begitu agen menyimpan "
        "ingatan, dan penanganannya di batas alat.",
        "**Memutuskan apa yang TIDAK boleh disimpan**, dengan alasan yang bisa "
        "dipertahankan di depan pemeriksa.",
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "Tiga lapis, dan tidak satu pun gratis",
         "lead": "Yang tampak seperti ingatan selalu keputusan seseorang."},

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Yang disebut ingatan sebenarnya daftar pesan Anda",
            "blocks": [
                {"t": "p", "md": "Bab 2 sudah menyebutkannya dan bab ini dibangun di "
                                 "atasnya: **model tidak menyimpan apa pun antar panggilan.** "
                                 "Yang membuatnya tampak mengingat adalah kode Anda yang "
                                 "mengirim ulang riwayatnya."},
                {"t": "p", "md": "Itu berarti seluruh perilaku \\u201cmengingat\\u201d pada "
                                 "sistem Anda adalah **rekayasa** — apa yang dimasukkan, "
                                 "apa yang dibuang, dan apa yang dicari kembali. Tidak ada "
                                 "yang otomatis, dan tidak ada yang gratis."},
                {"t": "band",
                 "md": "Kabar baiknya: keadaan yang Anda pegang adalah keadaan yang bisa "
                       "Anda **periksa, potong, uji, dan pertanggungjawabkan**. Ingatan "
                       "yang ada di dalam bobot model tidak punya satu pun dari sifat itu."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Tiga lapis, dengan umur dan harga yang berbeda",
            "blocks": [
                {"t": "mmd", "id": "agents04-tiers", "src": MMD_TIERS,
                 "cap": "Semakin ke kanan, semakin murah disimpan dan semakin mahal diambil."},
                {"t": "p", "md": "**Ingatan kerja** hidup satu giliran: hasil alat mentah, "
                                 "yang biasanya besar dan hampir seluruhnya tidak perlu "
                                 "dibawa ke giliran berikutnya. **Jangka pendek** adalah "
                                 "percakapan ini. **Jangka panjang** ada di luar konteks "
                                 "dan hanya masuk ketika dicari."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Pertanyaan yang memutuskan lapis mana",
            "blocks": [
                {"t": "table",
                 "head": ["Pertanyaan", "Kalau ya", "Contoh"],
                 "widths": [38, 26, 36],
                 "rows": [
                     ["Dipakai lagi di giliran berikutnya?", "Jangka pendek",
                      "Nomor rekening yang sedang dibahas"],
                     ["Dipakai lagi minggu depan?", "Jangka panjang",
                      "Preferensi pengguna, keputusan yang pernah diambil"],
                     ["Hanya untuk menghasilkan satu angka?", "Ingatan kerja",
                      "1 843 baris transaksi → satu rasio"],
                     ["Bisa dihitung ulang kapan saja?", "**Jangan disimpan**",
                      "Apa pun yang alat bisa berikan lagi"],
                 ]},
                {"t": "band",
                 "md": "Baris terakhir yang paling sering dilanggar. Menyimpan sesuatu yang "
                       "bisa diambil ulang berarti menukar ==biaya token yang pasti dengan "
                       "risiko data basi=="},
            ],
        },

        {"type": "section", "num": "02", "title": "Jangka pendek: memangkas atau meringkas",
         "lead": "Dua cara, dua kerugian — dan hanya satu yang kelihatan."},

        {
            "type": "slide",
            "kicker": "Jangka pendek",
            "title": "Memangkas: kehilangan yang jujur",
            "blocks": [
                {"t": "p", "md": "Cara paling sederhana menjaga konteks tetap muat: simpan "
                                 "N giliran terakhir, buang sisanya. Murah, pasti, dan "
                                 "mudah diuji."},
                {"t": "p", "md": "Kerugiannya juga pasti, dan itu kekuatannya: Anda tahu "
                                 "persis apa yang hilang. Masalahnya muncul ketika yang "
                                 "hilang adalah **batasan yang disebut di awal** — "
                                 "\\u201cjangan hubungi nasabah lewat surel\\u201d yang "
                                 "diucapkan pada giliran kedua tidak ada lagi pada giliran "
                                 "kedua puluh."},
                {"t": "band",
                 "md": "Bentuk kegagalannya khas dan mudah dikenali: agen bekerja benar "
                       "selama sepuluh giliran, lalu mulai **melanggar aturan yang sudah "
                       "tidak ada di konteksnya**. Itu bukan model yang lupa; itu jendela "
                       "yang menggeser."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka pendek",
            "title": "Meringkas: kehilangan yang tidak terlihat",
            "blocks": [
                memory_decay("agents04-decay",
                             cap="Peringkasan yang diulang, dihitung pemangkatannya. "
                                 "Langkahi: asli, dua kali pertama, lalu enam kali.",
                             note="Yang jadi pelajaran bukan angka 85% — itu asumsi yang "
                                  "dicetak di gambarnya. Yang jadi pelajaran adalah "
                                  "bentuknya: eksponensial, berapa pun angkanya."),
                {"t": "p", "md": "Meringkas terasa lebih baik daripada memangkas — tidak "
                                 "ada yang dibuang, semuanya \\u201cmasih ada\\u201d. Tetapi "
                                 "peringkasan berikutnya bekerja atas **ringkasan**, bukan "
                                 "atas aslinya, sehingga apa pun yang hilang tiap kali "
                                 "dipangkatkan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka pendek",
            "title": "Yang paling dulu hilang dari sebuah ringkasan",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔢", "h": "Angka dan pengenal",
                     "p": "\\u201cRasio 0,82\\u201d jadi \\u201crasionya rendah\\u201d. "
                          "Setelah itu tidak ada cara memulihkannya, dan tidak ada yang "
                          "tahu itu terjadi.",
                     "style": "bad"},
                    {"ico": "🚫", "h": "Batasan yang bersyarat",
                     "p": "\\u201cBoleh, KECUALI kalau nasabahnya di bawah 21\\u201d "
                          "cenderung jadi \\u201cboleh\\u201d.",
                     "style": "bad"},
                    {"ico": "❓", "h": "Yang belum diputuskan",
                     "p": "Ringkasan cenderung menutup pertanyaan yang masih terbuka, "
                          "sebab teks yang rapi terbaca lebih baik."},
                    {"ico": "🕐", "h": "Urutan waktu",
                     "p": "Mana yang lebih dulu sering hilang, dan itu penting justru saat "
                          "menelusuri kesalahan."},
                ]},
                {"t": "p", "md": "Perhatikan polanya: yang hilang duluan justru yang "
                                 "**paling menentukan keputusan**. Prosa yang menjelaskan "
                                 "bertahan; angka dan pengecualian tidak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka pendek",
            "title": "Bentuk campuran yang biasanya menang",
            "blocks": [
                {"t": "mmd", "id": "agents04-hybrid", "src": MMD_HYBRID,
                 "cap": "Yang tetap, yang diringkas, dan yang utuh — masing-masing punya alasan."},
                {"t": "steps", "items": [
                    {"h": "Perintah sistem tidak pernah diringkas",
                     "p": "Ia bagian tetap, dan ia yang membuat singgahan prompt bekerja."},
                    {"h": "Giliran pertama disimpan utuh",
                     "p": "Di situ tujuan dan batasan disebut. Inilah yang paling sering "
                          "hilang dan paling mahal hilangnya."},
                    {"h": "Bagian tengah diringkas, satu kali",
                     "p": "Ringkas dari **aslinya** kalau masih ada, bukan dari ringkasan "
                          "sebelumnya. Itu yang mematahkan pemangkatan di gambar tadi."},
                    {"h": "Beberapa giliran terakhir utuh",
                     "p": "Di situ konteks langsung berada, dan di situ ketepatan paling "
                          "terasa."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka pendek",
            "title": "Simpan aslinya, ringkas dari sana",
            "blocks": [
                {"t": "p", "md": "Satu perubahan kecil yang menghapus sebagian besar "
                                 "masalah di gambar tadi: **simpan percakapan aslinya di "
                                 "luar konteks**, dan buat tiap ringkasan dari yang asli, "
                                 "bukan dari ringkasan sebelumnya."},
                {"t": "p", "md": "Penyimpanannya murah — teks di basis data, bukan token di "
                                 "konteks. Yang mahal adalah konteks, dan itu tidak "
                                 "bertambah."},
                {"t": "band",
                 "md": "Dengan begitu kerugiannya berhenti berlipat: ia jadi kerugian "
                       "**satu kali** dari sumber lengkap, bukan kerugian berulang dari "
                       "salinan yang makin tipis."},
            ],
        },

        {"type": "section", "num": "03", "title": "Jangka panjang: mengambil, bukan mengingat",
         "lead": "Dan kenapa pengambilan itu alat, bukan langkah praproses."},

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Bentuk dasarnya, dan satu kalimat yang menentukan segalanya",
            "blocks": [
                {"t": "mmd", "id": "agents04-rag", "src": MMD_RAG,
                 "cap": "Pertanyaan jadi vektor, dicari yang mirip, potongan teratas masuk konteks."},
                {"t": "p", "md": "Mekanismenya sudah dibahas di **Bab 14** kelas ini — "
                                 "penyematan, kemiripan, indeks. Yang penting di sini satu "
                                 "kalimat: **model hanya bisa menjawab dari potongan yang "
                                 "terambil.** Apa pun yang tidak terambil, untuk keperluan "
                                 "jawaban itu, tidak ada."},
                {"t": "band",
                 "md": "Karena itu mutu sistem semacam ini hampir seluruhnya ditentukan "
                       "oleh **mutu pengambilannya**, bukan oleh kepintaran modelnya — dan "
                       "di situlah waktu perbaikan sebaiknya dihabiskan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Pengambilan sebagai alat mengubah tiga hal",
            "blocks": [
                {"t": "mmd", "id": "agents04-agentic", "src": MMD_AGENTIC,
                 "cap": "Agen memutuskan apa yang dicari, membaca hasilnya, dan boleh mencari lagi."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Praproses**: satu pencarian, dengan kata-kata "
                                      "pengguna apa adanya, sebelum model melihat apa pun."},
                     {"t": "p", "md": "Kalau kata pengguna buruk, hasilnya buruk, dan tidak "
                                      "ada kesempatan kedua."}],
                    [{"t": "p", "md": "**Alat**: model menyusun kata pencariannya sendiri, "
                                      "membaca hasilnya, dan boleh mencari lagi dengan "
                                      "istilah berbeda."},
                     {"t": "p", "md": "Lebih mahal — tiap pencarian satu giliran — dan jauh "
                                      "lebih tahan terhadap pertanyaan yang dirumuskan "
                                      "buruk."}],
                ]},
                {"t": "band",
                 "md": "Dan yang paling penting untuk sistem yang diawasi: sebagai alat, "
                       "tiap pengambilan **tercatat di jejak** — apa yang dicari, apa yang "
                       "kembali, dan potongan mana yang dipakai."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Kutipan bukan hiasan; ia satu-satunya cara memeriksa",
            "blocks": [
                {"t": "p", "md": "Jawaban yang menyebut sumbernya bisa diperiksa dalam "
                                 "hitungan detik. Jawaban yang tidak, hanya bisa dipercaya "
                                 "atau tidak."},
                {"t": "steps", "items": [
                    {"h": "Kutip potongan, bukan dokumen",
                     "p": "\\u201cKebijakan kredit\\u201d tidak bisa diperiksa; "
                          "\\u201cklausul CP-04, paragraf 2\\u201d bisa."},
                    {"h": "Periksa kutipannya dengan kode",
                     "p": "Kalau pengenal yang dikutip tidak ada di hasil pengambilan, itu "
                          "karangan — dan kode Anda bisa mengetahuinya tanpa model."},
                    {"h": "Simpan potongannya di jejak",
                     "p": "Agar setahun kemudian pertanyaan \\u201catas dasar apa\\u201d "
                          "punya jawaban, bukan rekonstruksi."},
                ]},
                {"t": "band",
                 "md": "Demo kredit UMKM melakukan persis ini: tiap rekomendasi membawa "
                       "klausul yang dipakai, dicetak penuh, dan uji akan gagal kalau "
                       "klausul yang dikutip tidak ada."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Apa yang pantas jadi ingatan jangka panjang",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "✅", "h": "Fakta yang stabil",
                     "p": "Preferensi, keputusan yang pernah diambil beserta alasannya, "
                          "hasil yang mahal dihitung ulang.",
                     "style": "good"},
                    {"ico": "⚠", "h": "Perlu kedaluwarsa",
                     "p": "Apa pun yang bisa berubah di sistem lain. Simpan pengenalnya, "
                          "ambil nilainya saat dipakai."},
                    {"ico": "🚫", "h": "Jangan sama sekali",
                     "p": "Data pribadi yang tidak dibutuhkan agen, kredensial, dan apa pun "
                          "yang retensinya diatur — kecuali retensi itu ikut diterapkan.",
                     "style": "bad"},
                ]},
                {"t": "p", "md": "Kartu ketiga bukan nasihat kehati-hatian umum. Ingatan "
                                 "adalah **basis data baru** yang sering lahir tanpa "
                                 "pemilik, tanpa kebijakan retensi, dan tanpa seorang pun "
                                 "menyadari ia sudah berisi data pribadi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Di mana teks dipotong menentukan apa yang bisa ditemukan",
            "blocks": [
                chunking("agents04-chunk",
                         cap="Satu kalimat, tiga cara memotong. Langkahi: ukuran tetap, "
                             "tumpang tindih, lalu menurut struktur.",
                         note="Fakta yang butuh dua sisi potongan tidak bisa dijawab dari "
                              "sisi mana pun — dan kegagalan itu tidak menimbulkan galat, "
                              "hanya jawaban yang salah."),
                {"t": "p", "md": "Pemotongan biasanya digambar sebagai deretan kotak "
                                 "seukuran, yang memperlihatkan mekanismenya dan "
                                 "menyembunyikan satu-satunya hal yang penting: **kalimat "
                                 "yang maknanya melintasi batas potongan hilang dari kedua "
                                 "sisinya.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Memilih cara memotong, tanpa mencoba semuanya",
            "blocks": [
                {"t": "table",
                 "head": ["Bentuk dokumen", "Cara yang cocok", "Alasannya"],
                 "widths": [30, 30, 40],
                 "rows": [
                     ["Kebijakan, peraturan, kontrak", "Menurut struktur",
                      "Klausul memang unit maknanya, dan nomornya jadi kutipan"],
                     ["Manual, dokumentasi", "Menurut judul bagian",
                      "Satu bagian menjawab satu pertanyaan"],
                     ["Percakapan, tiket", "Per giliran atau per pesan",
                      "Batas alaminya sudah ada"],
                     ["Prosa panjang tanpa struktur", "Tetap + tumpang tindih",
                      "Tidak ada batas alami; tumpang tindih membeli jaminan"],
                     ["Tabel dan lembar kerja", "**Jangan dipotong sebagai teks**",
                      "Jadikan alat kueri, bukan potongan untuk dicari kemiripannya"],
                 ]},
                {"t": "band",
                 "md": "Baris terakhir yang paling sering dilanggar dan paling mahal: "
                       "==tabel yang diubah jadi potongan teks kehilangan justru sifat yang "
                       "membuatnya berguna==, yaitu bisa dihitung."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Kemiripan bukan relevansi",
            "blocks": [
                {"t": "p", "md": "Pencarian vektor menemukan yang **mirip secara makna**. "
                                 "Itu bukan hal yang sama dengan yang **menjawab "
                                 "pertanyaan**, dan bedanya muncul dengan cara yang khas."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔁", "h": "Parafrase pertanyaan",
                     "p": "Potongan yang mengulang pertanyaan dengan kata lain skornya "
                          "tinggi, isinya tidak menjawab apa pun.",
                     "style": "bad"},
                    {"ico": "🔢", "h": "Angka dan kode",
                     "p": "Kemiripan makna buruk untuk nomor klausul, kode produk, dan "
                          "pengenal — di situ pencarian kata kunci menang telak.",
                     "style": "bad"},
                    {"ico": "🚫", "h": "Negasi",
                     "p": "\u201cboleh\u201d dan \u201ctidak boleh\u201d sangat mirip "
                          "secara vektor, dan berlawanan artinya.",
                     "style": "bad"},
                ]},
                {"t": "band",
                 "md": "Obat yang paling sering cukup: **gabungkan pencarian kata kunci "
                       "dengan pencarian vektor**, lalu urutkan ulang hasil gabungannya. "
                       "Ini rekayasa pencarian biasa, dan ia mengalahkan penggantian model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Jangka panjang",
            "title": "Ambil banyak, saring ketat",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Ambil lebih banyak daripada yang akan dipakai",
                     "p": "Pencarian awal murah dan tidak perlu tepat — tugasnya memastikan "
                          "jawabannya **ada di dalam** kumpulan yang diambil."},
                    {"h": "Urutkan ulang dengan model yang lebih teliti",
                     "p": "Membaca pertanyaan dan potongan bersama-sama, bukan "
                          "membandingkan dua vektor. Lebih mahal per potongan, dan hanya "
                          "dijalankan pada yang sedikit."},
                    {"h": "Masukkan hanya yang teratas",
                     "p": "Bab 2: konteks yang penuh menurunkan ketepatan. Yang tidak "
                          "masuk bukan kerugian, ia penghematan ganda."},
                ]},
                {"t": "band",
                 "md": "Pola ini — **jaring lebar lalu saringan halus** — sama dengan "
                       "deteksi objek di Bab 12: usulan banyak, lalu penyaringan. Bentuk "
                       "yang sama muncul lagi karena alasan yang sama."},
            ],
        },

        {"type": "section", "num": "04", "title": "Rekayasa konteks",
         "lead": "Empat operasi, dan konteks sebagai spesifikasi."},

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Empat operasi, dan itu saja",
            "blocks": [
                {"t": "table",
                 "head": ["Operasi", "Pertanyaannya", "Kesalahan yang biasa"],
                 "widths": [20, 40, 40],
                 "rows": [
                     ["Melacak", "Apa yang sudah terjadi dan di mana disimpan?",
                      "Tidak ada yang disimpan di luar konteks, jadi tidak ada yang bisa "
                      "diambil ulang"],
                     ["Memilih", "Apa yang masuk ke giliran ini?",
                      "Memasukkan semua yang muat, sebab \\u201cmasih ada ruang\\u201d"],
                     ["Memampatkan", "Bagaimana memperkecil tanpa kehilangan yang penting?",
                      "Meringkas ringkasan — lihat gambar tadi"],
                     ["Mengurutkan", "Apa di awal, apa di akhir?",
                      "Menaruh aturan penting di tengah tumpukan hasil alat"],
                 ]},
                {"t": "band",
                 "md": "Keempatnya keputusan **kode**, bukan keputusan model. Kalau tidak "
                       "ada yang menuliskannya, keempatnya tetap terjadi — hanya saja "
                       "secara kebetulan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Memilih: yang muat bukan berarti pantas masuk",
            "blocks": [
                {"t": "p", "md": "Godaan terbesar dari jendela konteks yang besar adalah "
                                 "memasukkan semuanya. Bab 2 sudah menyebut sebabnya itu "
                                 "buruk: ketepatan menemukan informasi **menurun** pada "
                                 "konteks yang penuh, terutama di bagian tengah."},
                {"t": "p", "md": "Jadi memilih bukan penghematan biaya semata — ia "
                                 "**menaikkan mutu jawaban**. Sepuluh potongan yang tepat "
                                 "mengalahkan seratus potongan yang mengandung sepuluh itu."},
                {"t": "band",
                 "md": "Uji yang mudah dan jarang dilakukan: jalankan kumpulan uji Anda "
                       "dengan potongan yang diambil dikurangi separuh. Kalau angkanya "
                       "tidak turun, ==separuh konteks Anda selama ini hanya biaya=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Mengurutkan: awal dan akhir adalah tempat istimewa",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Taruh di awal**"},
                     {"t": "bullets", "items": [
                         "Peran dan batasan",
                         "Definisi yang dipakai sepanjang percakapan",
                         "Skema alat",
                     ]}],
                    [{"t": "p", "md": "**Taruh di akhir**"},
                     {"t": "bullets", "items": [
                         "Permintaan giliran ini",
                         "Hasil alat yang baru saja kembali",
                         "Pengingat format keluaran",
                     ]}],
                ]},
                {"t": "p", "md": "Dan konsekuensi yang sering terlewat: menaruh pengingat "
                                 "format di **akhir** bekerja jauh lebih baik daripada "
                                 "menaruhnya di perintah sistem, ketika percakapannya sudah "
                                 "panjang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Konteks adalah spesifikasinya",
            "blocks": [
                {"t": "p", "md": "Pada sistem berbasis model, yang menentukan perilaku bukan "
                                 "kode yang Anda tulis, melainkan **konteks yang Anda "
                                 "susun**. Itu spesifikasi sistemnya, dan ia dirakit ulang "
                                 "tiap giliran."},
                {"t": "steps", "items": [
                    {"h": "Kalau ia dirakit, ia bisa diuji",
                     "p": "Rakit konteks untuk kasus uji, dan periksa isinya sebelum "
                          "dikirim. Itu uji unit biasa, dan tidak butuh model."},
                    {"h": "Kalau ia spesifikasi, ia pantas ditinjau",
                     "p": "Perubahan pada penyusun konteks pantas dibaca orang lain, "
                          "seperti perubahan kode."},
                    {"h": "Kalau ia berubah tiap giliran, ia pantas dicatat",
                     "p": "Jejak harus memuat konteks yang dipakai, bukan hanya jawabannya."},
                ]},
                {"t": "band",
                 "md": "Cara paling cepat memperbaiki agen yang mengecewakan hampir selalu "
                       "**memperbaiki apa yang masuk ke konteksnya**, bukan mengganti "
                       "modelnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Ingatan kerja: jangan biarkan hasil alat menetap",
            "blocks": [
                {"t": "p", "md": "Hasil alat sering besar dan hampir seluruhnya sekali "
                                 "pakai. Membiarkannya menetap di riwayat berarti "
                                 "membayarnya ulang di tiap giliran sesudahnya — Bab 2 "
                                 "menghitung berapa lipat itu."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Pola yang mahal**"},
                     {"t": "p", "md": "Alat mengembalikan 1 843 baris transaksi; semuanya "
                                      "masuk riwayat; enam giliran berikutnya membayarnya "
                                      "lagi dan lagi."}],
                    [{"t": "p", "md": "**Pola yang murah**"},
                     {"t": "p", "md": "Alat menghitung di sisinya sendiri dan mengembalikan "
                                      "rasio yang diminta. Baris mentahnya disimpan di luar "
                                      "konteks, dengan pengenal, kalau-kalau perlu."}],
                ]},
                {"t": "band",
                 "md": "Aturan yang mudah diingat: **alat mengembalikan jawaban, bukan "
                       "bahan.** Kalau agen harus menghitung sendiri dari data mentah, "
                       "itu tanda pekerjaan berada di tempat yang salah."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Siapa yang memutuskan sesuatu layak diingat",
            "blocks": [
                {"t": "p", "md": "Ada tiga cara, dan pilihannya menentukan seberapa besar "
                                 "ingatan Anda tumbuh serta seberapa bisa dipercaya isinya."},
                {"t": "table",
                 "head": ["Siapa", "Cara kerjanya", "Pertukarannya"],
                 "widths": [22, 40, 38],
                 "rows": [
                     ["Aturan kode", "Simpan hal yang jenisnya sudah ditentukan",
                      "Bisa diramalkan dan diuji; melewatkan yang tak terduga"],
                     ["Model", "Agen memanggil alat \u201cingat ini\u201d",
                      "Menangkap yang tak terduga; tumbuh cepat dan bisa salah"],
                     ["Manusia", "Pengguna menandai sesuatu untuk diingat",
                      "Paling tepat, paling jarang dipakai"],
                 ]},
                {"t": "band",
                 "md": "Yang paling sering berhasil: **kode untuk yang wajib, model untuk "
                       "yang opsional, dan batas jumlah** — supaya \u201cingat ini\u201d "
                       "tidak berubah jadi tempat pembuangan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Melupakan adalah fitur, bukan kekurangan",
            "blocks": [
                {"t": "p", "md": "Ingatan yang hanya bertambah akan berubah jadi tumpukan "
                                 "yang isinya saling bertentangan: preferensi lama dan baru, "
                                 "keputusan yang sudah dicabut, fakta yang sudah berubah di "
                                 "sistem lain."},
                {"t": "steps", "items": [
                    {"h": "Beri tanggal pada semuanya",
                     "p": "Tanpa waktu, tidak ada cara memilih antara dua ingatan yang "
                          "bertentangan."},
                    {"h": "Perbarui, jangan menumpuk",
                     "p": "Ingatan baru tentang hal yang sama harus **mengganti** yang "
                          "lama, bukan berdiri di sebelahnya."},
                    {"h": "Kedaluwarsakan yang bisa basi",
                     "p": "Apa pun yang sumbernya sistem lain punya umur. Simpan "
                          "pengenalnya, ambil nilainya."},
                    {"h": "Sediakan penghapusan yang sungguhan",
                     "p": "Termasuk dari indeks pencarian. Ingatan yang terhapus dari basis "
                          "data tapi masih ada di indeks belum terhapus."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rekayasa konteks",
            "title": "Ingatan bersama antar agen menciptakan masalah baru",
            "blocks": [
                {"t": "p", "md": "Begitu ada lebih dari satu agen, muncul pertanyaan yang "
                                 "tidak ada pada satu agen: **konteks siapa yang dilihat "
                                 "siapa?** Bab 8 membahasnya penuh; di sini cukup bentuk "
                                 "masalahnya."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📋", "h": "Semuanya melihat semuanya",
                     "p": "Paling sederhana, dan konteksnya membengkak paling cepat. Tiap "
                          "agen membayar percakapan agen lain."},
                    {"ico": "✉", "h": "Hanya lewat pesan",
                     "p": "Tiap agen punya konteks sendiri dan bertukar ringkasan. Lebih "
                          "murah, dan kehilangan detail di tiap penyerahan.",
                     "style": "accent"},
                    {"ico": "🗄", "h": "Papan bersama",
                     "p": "Keadaan disimpan di luar, tiap agen membaca yang perlu. Paling "
                          "bisa diskalakan, paling banyak kodenya."},
                ]},
                {"t": "band",
                 "md": "Perhatikan bahwa ketiganya soal **ingatan**, bukan soal kecerdasan. "
                       "Sebagian besar kesulitan sistem banyak-agen ternyata kesulitan "
                       "konteks."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Ongkos",
            "title": "Ingatan tidak gratis, dan ongkosnya bukan hanya token",
            "blocks": [
                {"t": "table",
                 "head": ["Ongkos", "Kapan terasa", "Yang sering terlewat"],
                 "widths": [24, 34, 42],
                 "rows": [
                     ["Penyematan", "Saat menulis dan saat mencari",
                      "Menyematkan ulang seluruh korpus setiap ganti model penyemat"],
                     ["Penyimpanan", "Tumbuh pelan",
                      "Indeks vektor jauh lebih besar daripada teksnya"],
                     ["Waktu pengambilan", "Tiap giliran",
                      "Menambah satu perjalanan pulang-pergi ke tiap langkah"],
                     ["Token konteks", "Tiap giliran sesudahnya",
                      "Potongan yang diambil dibayar ulang seperti riwayat"],
                     ["**Kewajiban hukum**", "Saat diperiksa",
                      "Basis data baru berisi data orang, sering tanpa pemilik"],
                 ]},
                {"t": "p", "md": "Baris terakhir bukan ongkos teknis, dan justru itu yang "
                                 "paling sering tidak dianggarkan siapa pun."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Ongkos",
            "title": "Kapan tidak perlu ingatan sama sekali",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "Tugas satu kali yang berdiri sendiri",
                     "p": "Menilai satu pengajuan, meringkas satu dokumen. Semua yang "
                          "dibutuhkan bisa diambil dengan alat saat itu juga.",
                     "style": "good"},
                    {"ico": "🔄", "h": "Yang bisa diambil ulang kapan saja",
                     "p": "Kalau alat bisa memberikannya lagi, menyimpannya hanya menukar "
                          "biaya pasti dengan risiko basi.",
                     "style": "good"},
                ]},
                {"t": "p", "md": "Demo kredit UMKM tidak punya ingatan lintas percakapan "
                                 "sama sekali, dan itu **keputusan**, bukan kelalaian: tiap "
                                 "penilaian berdiri sendiri, semua bahannya diambil lewat "
                                 "alat, dan tidak ada satu pun data nasabah yang menetap di "
                                 "luar sistem intinya."},
                {"t": "band",
                 "md": "Pertanyaan yang pantas ditanyakan sebelum memasang ingatan: "
                       "**kegagalan mana yang sedang saya perbaiki?** Kalau tidak ada "
                       "jawabannya, yang sedang dipasang adalah basis data baru tanpa "
                       "alasan."},
            ],
        },

        {"type": "section", "num": "05", "title": "Ingatan sebagai permukaan serangan",
         "lead": "Dua hal yang baru muncul begitu sistem mulai mengingat."},

        {
            "type": "slide",
            "kicker": "Risiko",
            "title": "Perintah yang menumpang di dalam data yang dibaca",
            "blocks": [
                {"t": "mmd", "id": "agents04-poison", "src": MMD_POISON,
                 "cap": "Hasil alat masuk ke konteks yang sama dengan perintah — dan terlihat sama."},
                {"t": "p", "md": "Agen membaca dokumen, tiket, atau halaman. Isinya bisa "
                                 "memuat kalimat yang ditujukan kepada **agennya**, bukan "
                                 "kepada pembacanya. Selama hasil alat masuk ke konteks yang "
                                 "sama dengan perintah, keduanya tidak terbedakan."},
                {"t": "band",
                 "md": "Penanganannya **bukan** di prompt. Ia di batas alat: apa yang boleh "
                       "dipanggil sesudah membaca sesuatu yang tidak tepercaya, dan apakah "
                       "alat tulis termasuk di dalamnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Risiko",
            "title": "Dan ingatan membuatnya bertahan sampai besok",
            "blocks": [
                {"t": "p", "md": "Tanpa ingatan, serangan semacam itu berakhir ketika "
                                 "percakapannya berakhir. Dengan ingatan jangka panjang, "
                                 "kalimat yang disisipkan bisa **tersimpan** — dan muncul "
                                 "lagi pada percakapan berikutnya, dengan pengguna yang "
                                 "berbeda."},
                {"t": "steps", "items": [
                    {"h": "Jangan simpan teks mentah dari sumber tidak tepercaya",
                     "p": "Simpan fakta yang sudah diekstrak dan divalidasi, bukan "
                          "paragrafnya."},
                    {"h": "Beri asal-usul pada tiap ingatan",
                     "p": "Dari percakapan mana, dari dokumen mana, ditulis kapan. Tanpa "
                          "itu, tidak ada cara mencabutnya."},
                    {"h": "Sediakan cara menghapus",
                     "p": "Ingatan yang tidak bisa dihapus adalah kewajiban hukum yang "
                          "tidak bisa dipenuhi."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Risiko",
            "title": "Ingatan bersama antar pengguna adalah keputusan, bukan fitur",
            "blocks": [
                {"t": "p", "md": "Ingatan yang dibagi antar pengguna terdengar efisien: "
                                 "sistem belajar sekali, semua orang menikmatinya. Ia juga "
                                 "jalur kebocoran yang paling langsung."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "👤", "h": "Per pengguna, bawaan",
                     "p": "Ingatan diberi batas pemilik, dan pencarian selalu tersaring "
                          "menurut pemiliknya — di **kode**, bukan di prompt.",
                     "style": "good"},
                    {"ico": "🌐", "h": "Bersama, kalau memang perlu",
                     "p": "Hanya untuk pengetahuan yang memang milik organisasi: kebijakan, "
                          "prosedur, definisi. Bukan untuk apa pun yang berasal dari "
                          "percakapan seseorang."},
                ]},
                {"t": "band",
                 "md": "Uji yang harus lulus sebelum tayang: **buat ingatan sebagai "
                       "pengguna A, lalu cari sebagai pengguna B.** Kalau kembali, "
                       "sistemnya belum siap."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Risiko",
            "title": "Data pribadi yang masuk lewat pintu belakang",
            "blocks": [
                {"t": "p", "md": "Sistem yang dirancang tanpa data pribadi bisa "
                                 "mengumpulkannya sendiri lewat ingatan: pengguna menyebut "
                                 "nama, nomor, atau kondisi kesehatan di tengah percakapan, "
                                 "dan mekanisme \u201cingat hal penting\u201d menyimpannya "
                                 "dengan patuh."},
                {"t": "steps", "items": [
                    {"h": "Saring saat menulis, bukan saat membaca",
                     "p": "Sekali tersimpan, ia sudah ada di cadangan dan di indeks. "
                          "Penyaringan di sisi baca datang terlambat."},
                    {"h": "Simpan kategori, bukan nilainya",
                     "p": "\u201cpelanggan memilih dihubungi lewat telepon\u201d cukup; "
                          "nomor teleponnya tidak perlu ada di ingatan agen."},
                    {"h": "Perlakukan ingatan sebagai sistem yang didaftarkan",
                     "p": "Punya pemilik, punya kebijakan retensi, dan muncul di daftar "
                          "sistem yang memproses data pribadi — atau ia tidak boleh ada."},
                ]},
                {"t": "band",
                 "md": "Ini kelanjutan langsung dari prinsip di Bab 1: **batas kemampuan "
                       "ada di kode.** Ingatan yang tidak bisa menyimpan nomor telepon "
                       "lebih kuat daripada ingatan yang diminta tidak menyimpannya."},
            ],
        },

        {"type": "section", "num": "06", "title": "Mengukur dan memperbaiki",
         "lead": "Ingatan yang tidak diukur akan membesar sampai jadi masalah."},

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Empat angka yang memberi tahu ingatan Anda bermasalah",
            "blocks": [
                {"t": "table",
                 "head": ["Angka", "Sehat kalau", "Gejala kalau tidak"],
                 "widths": [28, 32, 40],
                 "rows": [
                     ["Token konteks per giliran", "Datar",
                      "Naik terus → tidak ada yang memangkas"],
                     ["Potongan diambil lawan dipakai", "Sebagian besar dipakai",
                      "Banyak diambil, sedikit dikutip → pengambilan terlalu longgar"],
                     ["Peringkasan per percakapan", "Nol atau satu",
                      "Berulang → pemangkatan di gambar tadi sedang terjadi"],
                     ["Ingatan tersimpan per pengguna", "Tumbuh pelan lalu datar",
                      "Tumbuh terus → tidak ada yang kedaluwarsa"],
                 ]},
                {"t": "p", "md": "Tidak satu pun dari empat ini menimbulkan galat. "
                                 "Semuanya bergeser pelan, dan gejalanya di permukaan "
                                 "selalu sama: **agennya terasa makin bodoh dan makin "
                                 "mahal.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Mengujinya tanpa model",
            "blocks": [
                {"t": "p", "md": "Sebagian besar kegagalan ingatan bisa ditangkap uji biasa, "
                                 "sebab yang diuji adalah **penyusun konteks**, bukan "
                                 "modelnya."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🧪", "h": "Uji isi konteks",
                     "p": "Beri riwayat panjang buatan; pastikan batasan dari giliran "
                          "pertama masih ada di konteks giliran ke-30.",
                     "style": "good"},
                    {"ico": "🔒", "h": "Uji batas pemilik",
                     "p": "Simpan sebagai A, cari sebagai B, harapkan kosong. Ini uji "
                          "keamanan, dan ia deterministik.",
                     "style": "good"},
                    {"ico": "📉", "h": "Uji pemangkatan",
                     "p": "Ringkas sepuluh kali; periksa apakah angka penting masih ada. "
                          "Kalau hilang, arsitekturnya yang salah."},
                    {"ico": "🧾", "h": "Uji kutipan",
                     "p": "Pengenal yang dikutip harus ada di hasil pengambilan. Ini "
                          "pemeriksaan kode, bukan penilaian model."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Urutan memperbaikinya, dari yang paling sering berhasil",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Perbaiki apa yang masuk sebelum menambah apa pun",
                     "p": "Sebagian besar keluhan \\u201cagennya lupa\\u201d adalah konteks "
                          "yang salah disusun, bukan ingatan yang kurang."},
                    {"h": "Simpan aslinya di luar konteks",
                     "p": "Ini satu perubahan yang mematahkan pemangkatan peringkasan."},
                    {"h": "Jadikan pengambilan sebagai alat",
                     "p": "Sekaligus memberi Anda jejak dan kutipan — dua hal yang "
                          "dibutuhkan bab 7."},
                    {"h": "Baru tambahkan ingatan jangka panjang",
                     "p": "Dengan pemilik, asal-usul, dan kedaluwarsa sejak hari pertama. "
                          "Menambahkannya belakangan berarti memigrasi data pribadi."},
                ]},
                {"t": "band",
                 "md": "Perhatikan bahwa tiga langkah pertama **tidak menambah komponen "
                       "baru**. Ingatan jangka panjang adalah yang terakhir dipasang, dan "
                       "sering ternyata tidak diperlukan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Tidak ada ingatan; yang ada keputusan rekayasa",
                     "p": "Dan itu kabar baik: yang Anda susun bisa diperiksa, diuji, dan "
                          "dipertanggungjawabkan."},
                    {"h": "Memangkas kehilangan dengan jujur, meringkas tidak",
                     "p": "Ringkasan atas ringkasan memangkatkan kerugiannya. Simpan "
                          "aslinya, ringkas dari sana."},
                    {"h": "Yang tidak terambil tidak bisa dijawab",
                     "p": "Mutu sistem pengambilan ada di pengambilannya, bukan di "
                          "modelnya."},
                    {"h": "Konteks adalah spesifikasinya",
                     "p": "Dirakit tiap giliran, jadi bisa diuji tiap giliran."},
                    {"h": "Ingatan adalah basis data baru",
                     "p": "Dengan pemilik, retensi, dan cara menghapus — atau ia jadi "
                          "kewajiban yang tidak bisa dipenuhi."},
                ]},
            ],
            "notes": "Pertanyaan penutup: dari sistem yang kalian bangun, apa yang "
                     "sebenarnya perlu diingat lintas percakapan? Jawabannya hampir selalu "
                     "jauh lebih sedikit daripada yang disimpan.",
        },
    ],
}
