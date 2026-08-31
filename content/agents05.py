# -*- coding: utf-8 -*-
"""Bab 5 — Alat: membuatnya, memilihnya, membatasinya, dan protokolnya.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 5.

Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti hanya
URUTAN BABNYA. Isinya materi ajar sendiri, gambarnya digambar sendiri.

Bab ini yang paling dekat dengan `ai-agentic-demo`: enam alat lewat MCP, satu
alat tulis, dan tidak ada alat yang menyetujui kredit. Angka yang dikutip di
sini berasal dari repo itu, bukan dari buku.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import token_budget  # noqa: E402

B = BOOKS["agents"]


MMD_LIFECYCLE = """
flowchart LR
  D["Definisi alat<br/><small>nama, kegunaan, skema</small>"] --> S["Model memilih"]
  S --> C["Panggilan terstruktur"]
  C --> V{"Validasi<br/><small>tipe, rentang, izin</small>"}
  V -->|"tolak"| E["Galat yang bisa dipakai model"]
  V -->|"terima"| X["Eksekusi"]
  X --> O["Olah keluaran<br/><small>ringkas, potong, beri pengenal</small>"]
  O --> K["Masuk konteks"]
  E --> K
"""

MMD_RW = """
flowchart TB
  subgraph R["Alat BACA — boleh otonom"]
    R1["ambil data"]
    R2["cari kebijakan"]
    R3["hitung fitur risiko"]
  end
  subgraph W["Alat TULIS — butuh gerbang"]
    W1["kirim rekomendasi<br/><small>menulis ke antrean</small>"]
  end
  subgraph N["Yang TIDAK ADA"]
    N1["setujui kredit"]
  end
  R --> W
  W -. "tidak ada jalan ke sini" .-> N
"""

MMD_MCP = """
flowchart LR
  A["Agen<br/><small>klien MCP</small>"] <-->|"JSON-RPC"| S["Peladen MCP"]
  S --> T1["Alat"]
  S --> T2["Sumber daya"]
  S --> T3["Prompt"]
  T1 --> SYS["Sistem bank"]
  S -. "satu pintu:<br/>izin, pembatasan laju,<br/>pencatatan — sekali saja" .-> S
"""

MMD_SKILL = """
flowchart LR
  SK["SKILL.md<br/><small>kapan dipakai, cara memakai</small>"]
  RES["Berkas pendamping<br/><small>skrip, contoh, cetakan</small>"]
  AG["Agen"]
  SK -->|"dibaca saat relevan"| AG
  RES -->|"dipakai saat dijalankan"| AG
  SK -. "dimuat kalau perlu,<br/>bukan selalu di konteks" .-> AG
"""

MMD_LEARN = """
flowchart LR
  IC["Di dalam konteks<br/><small>skema + contoh di prompt</small>"]
  SFT["Penyetelan terbimbing<br/><small>contoh panggilan alat</small>"]
  RL["Penguatan<br/><small>imbalan kalau panggilannya berhasil</small>"]
  IC -->|"tanpa melatih apa pun"| SFT
  SFT -->|"butuh data panggilan"| RL
  IC -. "yang dipakai 95% proyek" .-> IC
"""


DECK = {
    "id": "agents05",
    "kind": "chapter",
    "number": 5,
    "book": "agents",
    "title": "Alat: membuatnya, memilihnya, membatasinya",
    "subtitle": "Alat adalah satu-satunya jalan agen menyentuh dunia — jadi "
                "di situlah seluruh kemampuannya, seluruh biayanya, dan "
                "seluruh batas izinnya berada.",
    "source": book_source(5, "agents"),
    "source_url": "",
    "duration": "3 jam (2 sesi)",
    "presenter": [
        {"name": "Hendri Karisma", "role": "Instructor"},
    ],
    "resources": [
        {"kind": "site", "label": "Course home", "href": "../../index.html"},
        {"kind": "github", "label": "ai-agentic-demo — enam alat lewat MCP",
         "href": "https://github.com/situkangsayur/ai-agentic-demo"},
        {"kind": "book",
         "label": f"{B['authors']}, {B['title']} ({B['publisher']}, {B['edition']})",
         "href": B["site"]},
    ],
    "objectives": [
        "**Menulis definisi alat** yang bisa dipilih dengan benar oleh model, "
        "dan menyebutkan empat cara definisi yang buruk merusak agen.",
        "**Menghitung ongkos konteks dari daftar alat**, dan menyebutkan "
        "kapan menambah alat justru menurunkan kemampuan.",
        "**Memisahkan alat baca dari alat tulis**, dan menjelaskan kenapa "
        "batas izin berada di ketiadaan alat, bukan di prompt.",
        "**Menjelaskan apa yang dipecahkan MCP** dan apa yang tidak — serta "
        "pertanyaan tata kelola yang muncul bersamanya.",
        "**Menyebutkan tiga cara model belajar memakai alat**, dan mana yang "
        "dipakai hampir semua proyek.",
        "**Merancang penanganan galat alat** yang membuat agen mencoba jalan "
        "lain alih-alih mengulang hal yang sama.",
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "Alat adalah batas sistemnya",
         "lead": "Semua yang bisa dilakukan agen ada di daftar ini. Tidak ada yang lain."},

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Daftar alat adalah pernyataan kemampuan yang paling jujur",
            "blocks": [
                {"t": "p", "md": "Model menghasilkan niat; kode menjalankannya. Karena itu "
                                 "pertanyaan **apa yang bisa dilakukan sistem ini** punya "
                                 "jawaban yang tepat dan bisa dibaca: daftar alat yang "
                                 "terdaftar, dan tidak ada yang lain."},
                {"t": "p", "md": "Ini sifat yang jarang dimiliki sistem berbasis model. "
                                 "Untuk hampir semua pertanyaan lain — apakah ia akan "
                                 "berhalusinasi, apakah ia akan patuh — jawabannya "
                                 "statistik. Untuk pertanyaan ini, jawabannya **daftar**."},
                {"t": "band",
                 "md": "Dan karena ia daftar, ia bisa **diuji**: `pytest -k "
                       "test_the_agent_has_no_tool_that_approves_credit` gagal kalau "
                       "seseorang menambahkan alat tulis kedua. Klaim di slide dan "
                       "perilaku kode tidak bisa berpisah."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Lima tahap, dan kegagalan bisa terjadi di kelimanya",
            "blocks": [
                {"t": "mmd", "id": "agents05-lifecycle", "src": MMD_LIFECYCLE,
                 "cap": "Dari definisi sampai hasilnya masuk konteks — dengan gerbang di tengah."},
                {"t": "p", "md": "Orang cenderung memikirkan \\u201cpemanggilan alat\\u201d "
                                 "sebagai satu hal. Sebenarnya lima: **mendefinisikan**, "
                                 "**memilih**, **memanggil**, **memvalidasi**, dan "
                                 "**mengolah keluarannya**. Empat dari lima itu kode Anda, "
                                 "dan di situlah sebagian besar perbaikan berada."},
            ],
        },

        {"type": "section", "num": "02", "title": "Mendefinisikan",
         "lead": "Deskripsi alat adalah antarmuka, dan pembacanya bukan manusia."},

        {
            "type": "slide",
            "kicker": "Definisi",
            "title": "Yang dibaca model hanyalah deskripsinya",
            "blocks": [
                {"t": "p", "md": "Model tidak melihat kode alat Anda. Ia melihat nama, "
                                 "kalimat kegunaan, dan skema parameter. Itu saja yang "
                                 "dipakainya untuk memutuskan kapan memanggil dan dengan "
                                 "argumen apa."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "Sebut hasilnya, bukan caranya",
                     "p": "\\u201cmengembalikan rasio kemampuan bayar dari 12 bulan mutasi "
                          "rekening\\u201d — bukan \\u201cmenjalankan kueri agregasi\\u201d.",
                     "style": "good"},
                    {"ico": "⏰", "h": "Sebut KAPAN memakainya",
                     "p": "Satu kalimat tentang kondisi pemakaian menghilangkan sebagian "
                          "besar panggilan yang salah sasaran.",
                     "style": "good"},
                    {"ico": "📐", "h": "Tipe ketat, plus satu contoh",
                     "p": "Contoh nilai lebih berguna daripada satu paragraf penjelasan "
                          "tipe."},
                    {"ico": "🚫", "h": "Sebut apa yang TIDAK dilakukannya",
                     "p": "\\u201cTidak mengembalikan data pribadi\\u201d menutup satu "
                          "kelas percobaan sebelum terjadi."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Definisi",
            "title": "Empat cara definisi yang buruk merusak agen",
            "blocks": [
                {"t": "table",
                 "head": ["Penyakit", "Gejalanya di jejak", "Obatnya"],
                 "widths": [24, 40, 36],
                 "rows": [
                     ["Terlalu umum", "Alat itu dipanggil untuk hampir semua hal",
                      "Persempit namanya dan sebut domainnya"],
                     ["Dua alat mirip", "Dipilih bergantian tanpa pola",
                      "Gabungkan, atau bedakan dengan tegas di kalimat pertama"],
                     ["Parameter kabur", "Argumen ngawur, galat di dalam alat",
                      "Tipe ketat, enumerasi, contoh nilai"],
                     ["Tidak menyebut kegagalan", "Agen mengulang panggilan yang sama",
                      "Jelaskan bentuk galat yang mungkin kembali"],
                 ]},
                {"t": "band",
                 "md": "Semua gejala di kolom tengah terlihat seperti **model yang bodoh**, "
                       "dan hampir semuanya sebenarnya ==masalah antarmuka yang Anda "
                       "tulis=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Definisi",
            "title": "Ongkos yang dibayar tiap giliran, untuk tiap alat",
            "blocks": [
                token_budget("agents05-toolcost",
                             parts=[("perintah sistem + kebijakan", 3_000),
                                    ("skema alat", 500),
                                    ("hasil alat per giliran", 2_000)],
                             turns=(4, 10, 20),
                             cap="Jendela 128k dengan enam alat. Langkahi 4, 10, dan 20 "
                                 "giliran.",
                             note="Skema alat ikut dikirim di TIAP giliran. Enam alat "
                                  "sekitar 3 000 token; dua puluh lima alat sekitar "
                                  "12 500 — dan itu sebelum satu pun hasil masuk."),
                {"t": "p", "md": "Skema alat adalah bagian **tetap** dari konteks, jadi ia "
                                 "disinggahkan dengan baik — tetapi ia tetap memakan ruang "
                                 "jendela, dan ruang itu tidak bisa dipakai untuk hasil "
                                 "alat maupun riwayat."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Definisi",
            "title": "Menambah alat bukan penambahan yang netral",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Yang bertambah**"},
                     {"t": "bullets", "items": [
                         "Token skema, tiap giliran",
                         "Peluang salah pilih di antara alat yang mirip",
                         "Permukaan yang harus divalidasi dan diamankan",
                         "Satu hal lagi yang bisa gagal dan harus dipantau",
                     ]}],
                    [{"t": "p", "md": "**Yang diharapkan**"},
                     {"t": "bullets", "items": [
                         "Satu kemampuan baru",
                     ]}],
                ]},
                {"t": "p", "md": "Karena itu pertanyaan sebelum menambahkan alat bukan "
                                 "*apakah ini berguna* — hampir semuanya berguna — "
                                 "melainkan **kegagalan mana yang sedang saya perbaiki, dan "
                                 "apakah alat yang sudah ada bisa diperluas alih-alih "
                                 "ditambah.**"},
                {"t": "band",
                 "md": "Pola yang berulang: **menggabungkan dua alat kecil jadi satu sering "
                       "lebih baik daripada mengoptimalkan keduanya**, sebab ia mengurangi "
                       "giliran sekaligus mengurangi kebingungan memilih."},
            ],
        },

        {"type": "section", "num": "03", "title": "Memilih, memanggil, memvalidasi",
         "lead": "Tiga tahap, dan gerbangnya ada di tahap ketiga."},

        {
            "type": "slide",
            "kicker": "Gerbang",
            "title": "Validasi bukan penanganan galat; ia batas izin",
            "blocks": [
                {"t": "p", "md": "Antara panggilan yang dihasilkan model dan efek yang "
                                 "terjadi di dunia, ada satu tempat yang seluruhnya milik "
                                 "kode Anda. Semua yang ingin Anda jamin harus berada di "
                                 "situ."},
                {"t": "steps", "items": [
                    {"h": "Bentuk dan tipe",
                     "p": "Dijamin penyedia kalau memakai skema ketat — tetap periksa, "
                          "sebab penyedia bisa berubah."},
                    {"h": "Rentang dan keberadaan",
                     "p": "Nilai yang masuk akal, pengenal yang benar-benar ada."},
                    {"h": "**Kepemilikan**",
                     "p": "Apakah pengguna INI berhak atas data itu. Ini yang paling sering "
                          "hilang, dan yang paling mahal hilangnya."},
                    {"h": "Batas laju dan anggaran",
                     "p": "Alat yang sama dipanggil dua puluh kali dalam satu proses adalah "
                          "gelung, bukan kemajuan."},
                ]},
                {"t": "band",
                 "md": "Perhatikan tahap ketiga: izin diperiksa terhadap **pengguna akhir**, "
                       "bukan terhadap layanan. Agen yang berjalan dengan kredensial "
                       "layanan bisa membaca segalanya kalau tidak ada yang menyaringnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Gerbang",
            "title": "Galat yang berguna membuat agen mencoba jalan lain",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Galat yang buruk**"},
                     {"t": "bullets", "items": [
                         "`Error 500`",
                         "`null`",
                         "Melempar pengecualian yang menghentikan proses",
                     ]},
                     {"t": "p", "md": "Agen tidak tahu apa yang harus berbeda, jadi ia "
                                      "mengulang hal yang sama."}],
                    [{"t": "p", "md": "**Galat yang berguna**"},
                     {"t": "bullets", "items": [
                         "`id tidak ditemukan — periksa formatnya: APP-2201`",
                         "`rentang tanggal maksimum 12 bulan`",
                         "`butuh hasil analisis dulu; panggil compute_risk_features`",
                     ]},
                     {"t": "p", "md": "Ketiganya memberi tahu **apa yang harus diubah**."}],
                ]},
                {"t": "band",
                 "md": "Ini salah satu perbaikan dengan hasil terbesar per jam kerja di "
                       "seluruh modul, dan hampir tidak pernah dikerjakan: **tulis pesan "
                       "galat alat untuk pembaca yang akan mencoba lagi.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Gerbang",
            "title": "Baca dan tulis bukan risiko yang sama",
            "blocks": [
                {"t": "mmd", "id": "agents05-rw", "src": MMD_RW,
                 "cap": "Lima alat baca, satu alat tulis, dan satu yang sengaja tidak ada."},
                {"t": "p", "md": "Alat baca bisa salah dan hasilnya jawaban yang keliru — "
                                 "buruk, tetapi bisa diperbaiki. Alat tulis yang salah "
                                 "meninggalkan **efek**, dan sebagian efek tidak bisa "
                                 "ditarik."},
                {"t": "band",
                 "md": "Karena itu pemisahannya bukan gaya penataan kode: alat baca boleh "
                       "otonom, alat tulis lewat gerbang, dan tindakan yang tidak boleh "
                       "terjadi **tidak diberi alat sama sekali**. Perubahan sehari, dan "
                       "keamanan naik jauh."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Gerbang",
            "title": "Mengolah keluaran: pekerjaan yang sering dilewatkan",
            "blocks": [
                {"t": "p", "md": "Apa yang dikembalikan alat masuk ke konteks dan dibayar "
                                 "ulang di tiap giliran sesudahnya. Mengembalikan "
                                 "\\u201csemua yang ada\\u201d adalah keputusan yang mahal "
                                 "dan biasanya diambil tanpa disadari."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🎯", "h": "Kembalikan jawabannya",
                     "p": "Rasio yang diminta, bukan 1 843 baris yang menghasilkannya.",
                     "style": "good"},
                    {"ico": "🔖", "h": "Beri pengenal untuk yang besar",
                     "p": "Simpan di luar, kembalikan rujukannya, sediakan alat untuk "
                          "membacanya kalau memang perlu."},
                    {"ico": "✂", "h": "Potong dengan batas yang jelas",
                     "p": "Dan **katakan** bahwa dipotong — hasil terpotong yang menyamar "
                          "sebagai hasil lengkap menghasilkan kesimpulan yang salah."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memilih",
            "title": "Ketika alatnya terlalu banyak untuk dimuat sekaligus",
            "blocks": [
                {"t": "p", "md": "Pada sistem yang matang, jumlah alat tumbuh. Lima puluh "
                                 "alat berarti sekitar 25 000 token skema di tiap giliran — "
                                 "dan model yang harus memilih di antara lima puluh "
                                 "kemungkinan memilih lebih buruk daripada di antara enam."},
                {"t": "steps", "items": [
                    {"h": "Kelompokkan menurut tugas, bukan menurut sistem asalnya",
                     "p": "Pengguna dan model memikirkan pekerjaan, bukan peta layanan "
                          "internal Anda."},
                    {"h": "Muat kelompok yang relevan saja",
                     "p": "Satu langkah pemilihan kelompok di depan gelung — bisa dengan "
                          "aturan, bisa dengan pengklasifikasi kecil."},
                    {"h": "Atau jadikan pencarian alat sebagai alat",
                     "p": "Satu alat yang mencari alat lain. Menambah satu giliran, "
                          "menghemat ribuan token di semua giliran."},
                ]},
                {"t": "band",
                 "md": "Perhatikan bahwa ketiganya masalah **pengambilan**, persis seperti "
                       "Bab 4 — dan itu bukan kebetulan: memilih alat dari lima puluh dan "
                       "memilih potongan dari lima puluh ribu adalah bentuk masalah yang "
                       "sama."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memilih",
            "title": "Alat yang dibuat agen sendiri",
            "blocks": [
                {"t": "p", "md": "Ada pola yang menarik dan pantas dipahami sebelum "
                                 "dicoba: agen menulis kodenya sendiri untuk sebuah tugas "
                                 "berulang, lalu menyimpannya sebagai alat baru untuk "
                                 "dipakai lain kali."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Yang menarik**"},
                     {"t": "p", "md": "Tugas yang tadinya butuh lima langkah jadi satu "
                                      "panggilan, dan biaya berikutnya turun jauh."}],
                    [{"t": "p", "md": "**Yang harus dijawab dulu**"},
                     {"t": "p", "md": "Siapa yang meninjau alat itu? Di mana ia berjalan? "
                                      "Apa izinnya? Alat yang dibuat sendiri oleh sistem "
                                      "adalah **kode baru di produksi tanpa peninjau**."}],
                ]},
                {"t": "band",
                 "md": "Bentuk yang bisa dipertanggungjawabkan: agen boleh **mengusulkan** "
                       "alat, manusia menyetujuinya, dan ia masuk lewat jalur yang sama "
                       "dengan kode lain. Yang tidak bisa: alat baru langsung bisa "
                       "dieksekusi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Kode sebagai alat",
            "title": "Alat yang menjalankan kode adalah kelasnya sendiri",
            "blocks": [
                {"t": "p", "md": "Memberi agen kemampuan menjalankan kode adalah cara "
                                 "tercepat membuatnya berguna, dan cara tercepat membuatnya "
                                 "berbahaya. Ia bukan satu alat lagi di daftar — ia alat "
                                 "yang bisa **menjadi** alat apa pun."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🧮", "h": "Kenapa menggoda",
                     "p": "Aritmetika yang pasti, pengolahan data, format yang rapi — "
                          "semuanya hal yang model buruk mengerjakannya sendiri."},
                    {"ico": "🚪", "h": "Kenapa berbahaya",
                     "p": "Jaringan, berkas, kredensial di lingkungan, dan proses lain di "
                          "mesin yang sama.",
                     "style": "bad"},
                ]},
                {"t": "band",
                 "md": "Aturan yang tidak bisa ditawar: **kalau agen menjalankan kode, kode "
                       "itu berjalan di tempat yang terisolasi** — tanpa jaringan kecuali "
                       "yang diizinkan, tanpa kredensial, dengan batas waktu dan memori, "
                       "dan di proses yang boleh dimatikan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Kode sebagai alat",
            "title": "Berlapis, dan jujur soal apa yang tidak ditutupnya",
            "blocks": [
                {"t": "table",
                 "head": ["Lapis", "Menahan", "TIDAK menahan"],
                 "widths": [26, 36, 38],
                 "rows": [
                     ["Daftar impor yang diizinkan", "Kesalahan yang tidak disengaja",
                      "Kode yang sengaja mencari celah"],
                     ["Batas waktu dan memori", "Gelung tak berujung, kehabisan memori",
                      "Kebocoran data dalam satu detik"],
                     ["Tanpa jaringan", "Pengiriman data keluar",
                      "Apa pun yang sudah ada di dalam sandbox"],
                     ["Kontainer / proses terpisah", "Sebagian besar hal",
                      "Celah pada mesin virtual atau kernel"],
                 ]},
                {"t": "band",
                 "md": "Kolom ketiga itu yang membuat daftar ini berguna. Sandbox yang "
                       "dijelaskan sebagai \u201caman\u201d membuat orang berhenti "
                       "berpikir; sandbox yang menyebut ==apa yang tidak ditutupnya== "
                       "membuat orang menaruh data sensitif di tempat lain."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pengulangan",
            "title": "Alat tulis harus aman dipanggil dua kali",
            "blocks": [
                {"t": "p", "md": "Agen mengulang. Jaringan gagal, jawaban tidak terbaca, "
                                 "gelung mencoba lagi. Kalau alat tulis Anda tidak aman "
                                 "dipanggil dua kali dengan argumen yang sama, cepat atau "
                                 "lambat sesuatu akan terkirim dua kali."},
                {"t": "steps", "items": [
                    {"h": "Beri kunci idempotensi pada tiap panggilan tulis",
                     "p": "Panggilan kedua dengan kunci yang sama mengembalikan hasil "
                          "pertama, bukan membuat entri baru."},
                    {"h": "Kunci keputusan yang sudah diambil",
                     "p": "Di demo, keputusan kedua atas antrean yang sama ditolak, dan "
                          "penolakannya menyebut siapa yang memutuskan pertama."},
                    {"h": "Jangan mengandalkan agen untuk tidak mengulang",
                     "p": "Deteksi pengulangan di anggaran adalah jaring pengaman, bukan "
                          "jaminan."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pengulangan",
            "title": "Alat baca pun punya bentuk kegagalan yang khas",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔁", "h": "Dipanggil berulang identik",
                     "p": "Hampir selalu tanda galatnya tidak informatif, atau hasilnya "
                          "tidak dipahami. Anggaran pengulangan menangkapnya."},
                    {"ico": "🐢", "h": "Lambat dan tidak dibatasi",
                     "p": "Satu kueri tanpa batas waktu bisa menahan seluruh proses agen. "
                          "Batas waktu per alat, bukan hanya per proses."},
                    {"ico": "📦", "h": "Mengembalikan terlalu banyak",
                     "p": "Membanjiri konteks, dan dibayar ulang tiap giliran sesudahnya."},
                ]},
                {"t": "p", "md": "Ketiganya terlihat di jejak dan tidak satu pun menimbulkan "
                                 "galat. Ini pola yang berulang di seluruh modul: **yang "
                                 "merusak sistem agen jarang melempar pengecualian.**"},
            ],
        },

        {"type": "section", "num": "04", "title": "Bagaimana model belajar memakai alat",
         "lead": "Tiga cara, dan hampir semua proyek memakai yang pertama."},

        {
            "type": "slide",
            "kicker": "Belajar",
            "title": "Tiga cara, dengan biaya yang sangat berbeda",
            "blocks": [
                {"t": "mmd", "id": "agents05-learn", "src": MMD_LEARN,
                 "cap": "Dari yang tidak melatih apa pun sampai yang butuh data panggilan."},
                {"t": "p", "md": "**Di dalam konteks** — skema dikirim bersama permintaan, "
                                 "dan model memakai kemampuan yang sudah dilatihkan "
                                 "padanya. Tanpa pelatihan, tanpa data yang perlu "
                                 "dikumpulkan — dan inilah yang dipakai hampir semua "
                                 "sistem produksi. Dua cara lainnya masuk akal hanya kalau "
                                 "alat Anda sangat khusus **dan** Anda sudah punya ribuan "
                                 "contoh panggilan yang benar."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Belajar",
            "title": "Apa yang sebenarnya diperbaiki oleh pelatihan",
            "blocks": [
                {"t": "table",
                 "head": ["Masalah", "Diperbaiki pelatihan?", "Yang sebenarnya bekerja"],
                 "widths": [30, 22, 48],
                 "rows": [
                     ["Salah memilih di antara alat mirip", "Kadang",
                      "Perbaiki deskripsinya dulu — jauh lebih murah"],
                     ["Argumen salah tipe", "Ya", "Atau: skema ketat, gratis"],
                     ["Lupa memanggil alat sama sekali", "Ya",
                      "Atau: sebut kondisi pemakaian di deskripsi"],
                     ["Memanggil alat yang tidak ada", "Ya",
                      "Atau: validasi menolaknya — sudah wajib"],
                     ["Berhenti terlalu awal", "Ya",
                      "Ini yang paling sulit diperbaiki tanpa pelatihan"],
                 ]},
                {"t": "p", "md": "Perhatikan kolom ketiga: **empat dari lima punya "
                                 "perbaikan yang tidak butuh melatih apa pun.** Melatih "
                                 "model untuk memakai alat adalah jawaban yang benar jauh "
                                 "lebih jarang daripada yang dikira."},
            ],
        },

        {"type": "section", "num": "05", "title": "Protokol: satu pintu, bukan dua puluh",
         "lead": "Yang dipecahkan MCP, dan pertanyaan yang dibawanya."},

        {
            "type": "slide",
            "kicker": "MCP",
            "title": "Masalah yang dipecahkannya adalah masalah perkalian",
            "blocks": [
                {"t": "p", "md": "Tanpa protokol bersama, tiap kerangka kerja agen "
                                 "menyambung ke tiap sistem dengan caranya sendiri. Lima "
                                 "kerangka kerja dan sepuluh sistem berarti lima puluh "
                                 "penyambung yang ditulis dan dirawat terpisah."},
                {"t": "p", "md": "Protokol mengubah perkalian jadi penjumlahan: tiap sistem "
                                 "menyediakan **satu** peladen, tiap kerangka kerja bicara "
                                 "**satu** bahasa. Ini pola lama — sama seperti driver "
                                 "basis data — dan berhasil karena alasan yang sama."},
                {"t": "band",
                 "md": "Perhatikan bahwa ini keuntungan **rekayasa**, bukan keuntungan "
                       "kecerdasan. MCP tidak membuat agen lebih pintar; ia membuat "
                       "penyambungannya berhenti jadi pekerjaan yang berlipat."},
            ],
        },

        {
            "type": "slide",
            "kicker": "MCP",
            "title": "Satu pintu, dan itu keuntungan keamanan yang sebenarnya",
            "blocks": [
                {"t": "mmd", "id": "agents05-mcp", "src": MMD_MCP,
                 "cap": "Alat, sumber daya, dan prompt di balik satu peladen."},
                {"t": "p", "md": "Kalau semua akses agen ke sistem bank melewati satu "
                                 "peladen, maka **izin, pembatasan laju, dan pencatatan "
                                 "hidup di satu tempat** — ditulis sekali, diaudit sekali, "
                                 "diperbaiki sekali."},
                {"t": "band",
                 "md": "Dan pertanyaan tata kelola yang lahir bersamanya, yang lebih baik "
                       "dijawab sekarang daripada di bawah tekanan: **siapa yang boleh "
                       "menambahkan alat ke peladen itu?** Itu pertanyaan risiko, bukan "
                       "pertanyaan teknis."},
            ],
        },

        {
            "type": "slide",
            "kicker": "MCP",
            "title": "Tiga hal yang disediakannya, dan bedanya",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔧", "h": "Alat",
                     "p": "Sesuatu yang **dijalankan** dan bisa punya efek. Inilah yang "
                          "butuh gerbang.",
                     "style": "accent"},
                    {"ico": "📄", "h": "Sumber daya",
                     "p": "Sesuatu yang **dibaca** — dokumen, berkas, catatan. Tidak punya "
                          "efek, tetapi tetap bisa membawa perintah yang menumpang."},
                    {"ico": "📝", "h": "Prompt",
                     "p": "Cetakan yang bisa dipakai ulang. Membantu keseragaman; bukan "
                          "mekanisme keamanan."},
                ]},
                {"t": "p", "md": "Pemisahan ini berguna justru saat menilai risiko: "
                                 "**sumber daya tidak perlu gerbang persetujuan, tetapi "
                                 "tetap perlu diperlakukan sebagai masukan yang tidak "
                                 "tepercaya.** Keduanya sering dicampur."},
            ],
        },

        {
            "type": "slide",
            "kicker": "MCP",
            "title": "Yang TIDAK dipecahkan protokol",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎭", "h": "Mutu deskripsi alat",
                     "p": "Protokol mengangkut skema; ia tidak membuat skema Anda jelas. "
                          "Alat yang deskripsinya kabur tetap dipilih dengan salah.",
                     "style": "bad"},
                    {"ico": "🔓", "h": "Keputusan izin",
                     "p": "Protokol memberi tempat memasang pemeriksaan; ia tidak "
                          "memutuskan siapa boleh apa.",
                     "style": "bad"},
                    {"ico": "💉", "h": "Perintah yang menumpang di data",
                     "p": "Hasil yang dikembalikan peladen tetap masuk ke konteks yang "
                          "sama dengan perintah.",
                     "style": "bad"},
                    {"ico": "💸", "h": "Ongkos konteks",
                     "p": "Skema tetap dikirim tiap giliran. Dua puluh lima alat lewat MCP "
                          "sama mahalnya dengan dua puluh lima alat tanpa MCP.",
                     "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Transport",
            "title": "Satu detail transport yang menentukan bentuk penyebaran",
            "blocks": [
                {"t": "p", "md": "Peladen MCP bisa berjalan sebagai **anak proses** yang "
                                 "bicara lewat stdio, atau sebagai **layanan HTTP**. "
                                 "Bedanya kelihatan sepele dan tidak."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**stdio** — klien memiliki prosesnya. Ketika "
                                      "prosesnya mati, alatnya ikut mati. Cocok untuk "
                                      "demo, kelas, dan alat lokal."}],
                    [{"t": "p", "md": "**HTTP** — peladennya berdiri sendiri, bisa "
                                      "diskalakan, dipantau, dan direstart terpisah dari "
                                      "agen yang memakainya. Ini bentuk produksinya."}],
                ]},
                {"t": "band",
                 "md": "Demo di repo memakai stdio, dan dokumennya menyebut itu dengan "
                       "jujur beserta akibatnya — sebab **kegagalan yang tidak disebutkan "
                       "akan ditemukan orang lain pada saat yang paling buruk.**"},
            ],
        },

        {"type": "section", "num": "06", "title": "Keterampilan sebagai berkas",
         "lead": "Pola yang lebih baru: kemampuan yang dimuat kalau perlu."},

        {
            "type": "slide",
            "kicker": "Skills",
            "title": "Kalau alat itu kata kerja, keterampilan itu prosedur",
            "blocks": [
                {"t": "mmd", "id": "agents05-skill", "src": MMD_SKILL,
                 "cap": "Satu berkas yang menjelaskan kapan dan bagaimana, plus berkas pendampingnya."},
                {"t": "p", "md": "Alat adalah satu tindakan. **Keterampilan** adalah cara "
                                 "mengerjakan sesuatu yang butuh beberapa tindakan, "
                                 "ditulis sebagai berkas — kapan dipakai, bagaimana "
                                 "urutannya, dan berkas pendamping yang dipakai saat "
                                 "menjalankannya."},
                {"t": "band",
                 "md": "Kelebihan bentuknya justru pada konteks: **dimuat hanya ketika "
                       "relevan.** Lima puluh keterampilan tidak memakan ruang jendela, "
                       "sedangkan lima puluh alat memakan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Skills",
            "title": "Kapan sesuatu pantas jadi keterampilan, bukan alat",
            "blocks": [
                {"t": "table",
                 "head": ["Kalau...", "Jadikan", "Alasannya"],
                 "widths": [40, 20, 40],
                 "rows": [
                     ["Satu tindakan, satu hasil", "Alat",
                      "Model perlu memanggilnya, bukan membacanya"],
                     ["Prosedur beberapa langkah", "Keterampilan",
                      "Yang dibutuhkan adalah urutannya, bukan satu panggilan"],
                     ["Jarang dipakai, panjang penjelasannya", "Keterampilan",
                      "Tidak membebani konteks kalau tidak dipakai"],
                     ["Butuh gerbang persetujuan", "**Alat**",
                      "Gerbang dipasang pada eksekusi, dan keterampilan tidak dieksekusi"],
                 ]},
                {"t": "band",
                 "md": "Baris terakhir yang penting untuk keamanan: keterampilan "
                       "**menjelaskan** cara melakukan sesuatu, tetapi tetap harus memanggil "
                       "alat untuk melakukannya — jadi batas izinnya tidak berpindah."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Skills",
            "title": "Bentuknya sederhana, dan itu kekuatannya",
            "blocks": [
                {"t": "p", "md": "Sebuah keterampilan pada dasarnya satu berkas teks: "
                                 "kapan ia relevan, langkah-langkahnya, dan rujukan ke "
                                 "berkas pendamping. Tidak ada kerangka kerja, tidak ada "
                                 "pendaftaran, tidak ada skema."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Akibat yang baik**"},
                     {"t": "bullets", "items": [
                         "Ditulis orang yang tahu prosedurnya, bukan hanya programmer",
                         "Ditinjau seperti dokumen biasa",
                         "Diversikan di git bersama kode",
                     ]}],
                    [{"t": "p", "md": "**Akibat yang harus dijaga**"},
                     {"t": "bullets", "items": [
                         "Teks yang masuk konteks tetap **masukan tidak tepercaya**",
                         "Keterampilan dari sumber luar sama saja dengan menjalankan "
                         "kode dari sumber luar",
                         "Tanpa peninjauan, ia jalan pintas ke perilaku baru",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Kaidah yang sama seperti alat: **yang menentukan bukan bentuk "
                       "berkasnya, melainkan siapa yang boleh menambahkannya.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Merancang",
            "title": "Alat dirancang untuk agen, bukan disalin dari API yang ada",
            "blocks": [
                {"t": "p", "md": "Godaan yang wajar: sudah ada REST API, jadikan saja tiap "
                                 "titik akhirnya satu alat. Hasilnya biasanya agen yang "
                                 "buruk, sebab API dirancang untuk **program yang tahu apa "
                                 "yang diinginkannya**, bukan untuk pemanggil yang sedang "
                                 "mencari tahu."},
                {"t": "table",
                 "head": ["API yang ada", "Masalahnya bagi agen", "Alat yang lebih baik"],
                 "widths": [28, 36, 36],
                 "rows": [
                     ["`GET /transactions?page=1`", "Agen harus mengurus halaman demi "
                      "halaman", "`ringkasan_mutasi(id, bulan)` — satu panggilan, satu "
                      "jawaban"],
                     ["Lima titik akhir untuk satu tugas", "Lima giliran, lima kesempatan "
                      "salah", "Satu alat yang menyusunnya di sisi peladen"],
                     ["Mengembalikan seluruh objek", "Membanjiri konteks",
                      "Kembalikan medan yang diminta saja"],
                     ["Galat HTTP mentah", "Tidak memberi tahu apa yang harus diubah",
                      "Pesan yang menyebut perbaikannya"],
                 ]},
                {"t": "band",
                 "md": "Aturan praktisnya: **satu alat = satu pertanyaan yang masuk akal "
                       "ditanyakan manusia.** Kalau agen harus memanggil tiga alat untuk "
                       "menjawab satu pertanyaan, alatnya yang salah bentuk."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Merancang",
            "title": "Alat yang mengembalikan bukti, bukan hanya nilai",
            "blocks": [
                {"t": "p", "md": "Kalau jawabannya akan dipertanggungjawabkan, angka saja "
                                 "tidak cukup. Alat sebaiknya mengembalikan **nilai beserta "
                                 "asal-usulnya**: dari mana, kapan, dan versi apa."},
                {"t": "steps", "items": [
                    {"h": "Nilai, sumber, dan waktu",
                     "p": "\u201cDSCR 0,82, dihitung dari 12 bulan mutasi sampai "
                          "2026-07-31\u201d bisa diperiksa. \u201cDSCR 0,82\u201d tidak."},
                    {"h": "Versi model atau aturan",
                     "p": "Skor yang keluar dari model harus membawa versi modelnya, "
                          "supaya setahun lagi bisa ditelusuri."},
                    {"h": "Pengenal untuk yang besar",
                     "p": "Bukan seluruh datanya — rujukan yang bisa dibuka pemeriksa."},
                ]},
                {"t": "band",
                 "md": "Inilah yang membuat rekomendasi di demo bisa diperiksa: tiap angka "
                       "menunjuk panggilan yang menghasilkannya, dan tiap klausul dicetak "
                       "penuh. Bukan karena promptnya meminta begitu."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Merancang",
            "title": "Satu alat yang hampir selalu pantas ada",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🙋", "h": "Bertanya kepada manusia",
                     "p": "Alat yang tugasnya menghentikan proses dan meminta keputusan. "
                          "Tanpa ini, satu-satunya cara agen menghadapi ketidakpastian "
                          "adalah menebak.",
                     "style": "accent"},
                    {"ico": "🏳", "h": "Menyerah dengan alasan",
                     "p": "Mengembalikan \u201ctidak bisa diselesaikan, karena X\u201d "
                          "sebagai hasil yang sah. Sistem yang tidak punya cara menyerah "
                          "akan mengarang.",
                     "style": "accent"},
                ]},
                {"t": "p", "md": "Keduanya terasa seperti mengakui kekalahan, dan keduanya "
                                 "menaikkan mutu sistem lebih banyak daripada kebanyakan "
                                 "penyetelan prompt. Laju eskalasi yang **nol** hampir "
                                 "selalu tanda ada yang salah, bukan tanda keberhasilan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Menguji",
            "title": "Alat bisa diuji tanpa model sama sekali",
            "blocks": [
                {"t": "p", "md": "Ini bagian yang paling menyenangkan dari memindahkan "
                                 "seluruh kemampuan ke alat: **alat adalah fungsi biasa**, "
                                 "dan fungsi biasa diuji dengan cara biasa."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "✅", "h": "Uji benar",
                     "p": "Masukan sah, keluaran yang diharapkan. Tidak butuh model, tidak "
                          "butuh jaringan.",
                     "style": "good"},
                    {"ico": "🚫", "h": "Uji tolak",
                     "p": "Argumen tidak sah harus ditolak, bukan ditebak maksudnya. "
                          "Termasuk uji kepemilikan.",
                     "style": "good"},
                    {"ico": "🔒", "h": "Uji struktural",
                     "p": "\u201cTidak ada alat yang bisa menyetujui\u201d dan "
                          "\u201calat agen tidak bisa mencapai data pribadi\u201d — "
                          "diperiksa tiap commit.",
                     "style": "good"},
                ]},
                {"t": "band",
                 "md": "Uji ketiga itu yang membedakan kontrol dari klaim. Ia gagal kalau "
                       "seseorang menambahkan alat yang melanggarnya — termasuk Anda "
                       "sendiri, enam bulan lagi, sedang terburu-buru."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Menguji",
            "title": "Yang tidak bisa diuji tanpa model, dan cara menanganinya",
            "blocks": [
                {"t": "p", "md": "Yang tidak bisa diuji tanpa model adalah **apakah model "
                                 "memilih alat yang tepat**. Itu bukan uji unit; itu "
                                 "penilaian, dan bab 7 membahasnya."},
                {"t": "steps", "items": [
                    {"h": "Pisahkan dua jenis pengujian sejak awal",
                     "p": "Uji mesin (gelung, anggaran, validasi, alat) berjalan luring dan "
                          "harus selalu hijau. Penilaian model berjalan terpisah dan "
                          "hasilnya berupa angka, bukan lulus/gagal."},
                    {"h": "Jangan gabungkan keduanya di CI yang sama",
                     "p": "Uji yang kadang merah karena modelnya sedang berubah-ubah akan "
                          "membuat orang berhenti mempercayai seluruh CI."},
                    {"h": "Pakai penyedia luring untuk uji mesin",
                     "p": "Uji yang butuh kunci API adalah uji yang tidak dijalankan orang."},
                ]},
            ],
        },

        {"type": "section", "num": "07", "title": "Praktik",
         "lead": "Urutan membangun, dan cara mengetahui alat mana yang bermasalah."},

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Urutan membangun daftar alat",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Mulai dari alat baca saja",
                     "p": "Agen yang hanya bisa membaca sudah berguna, dan tidak bisa "
                          "merusak apa pun sementara Anda belajar bentuk kegagalannya."},
                    {"h": "Tambahkan satu alat tulis, dengan gerbang",
                     "p": "Satu. Dan tuliskan alasannya di tempat yang akan dibaca orang "
                          "lain."},
                    {"h": "Tuliskan alat yang SENGAJA tidak ada",
                     "p": "Beserta ujinya. Ini yang membuat batasnya bertahan sesudah Anda "
                          "pindah proyek."},
                    {"h": "Baru pertimbangkan protokol",
                     "p": "MCP masuk akal ketika ada lebih dari satu klien atau lebih dari "
                          "satu sistem. Untuk satu agen dan satu basis data, ia lapisan "
                          "tambahan tanpa imbalan."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Angka per alat yang memberi tahu mana yang bermasalah",
            "blocks": [
                {"t": "table",
                 "head": ["Angka per alat", "Kalau tinggi berarti", "Tindakan"],
                 "widths": [26, 38, 36],
                 "rows": [
                     ["Laju galat validasi", "Skema atau deskripsinya kabur",
                      "Perbaiki deskripsi sebelum apa pun"],
                     ["Dipanggil lalu hasilnya tidak dipakai", "Salah sasaran",
                      "Persempit kondisi pemakaian"],
                     ["Panggilan berulang identik", "Galatnya tidak informatif",
                      "Tulis pesan galat yang menyebut apa yang harus berubah"],
                     ["Waktu jalan", "Alatnya, bukan modelnya",
                      "Optimasi di sisi alat; model tidak akan menolong"],
                     ["Ukuran keluaran", "Konteks dibanjiri",
                      "Ringkas di sisi alat, kembalikan pengenal"],
                 ]},
                {"t": "p", "md": "Kelimanya per **alat**, bukan per sistem. Rata-rata "
                                 "seluruh sistem hampir selalu menyembunyikan satu alat yang "
                                 "menyebabkan sebagian besar masalah."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Daftar alat adalah pernyataan kemampuan",
                     "p": "Satu-satunya pertanyaan tentang sistem berbasis model yang "
                          "jawabannya daftar, bukan statistik."},
                    {"h": "Deskripsi alat adalah antarmuka",
                     "p": "Sebagian besar yang terlihat seperti model bodoh adalah "
                          "antarmuka yang ditulis buruk."},
                    {"h": "Menambah alat tidak netral",
                     "p": "Token tiap giliran, kebingungan memilih, dan permukaan yang "
                          "harus diamankan — untuk satu kemampuan."},
                    {"h": "Baca dan tulis dipisah; yang terlarang tidak diberi alat",
                     "p": "Batas yang bisa dibujuk bukan batas."},
                    {"h": "Galat alat ditulis untuk pembaca yang akan mencoba lagi",
                     "p": "Perbaikan dengan hasil terbesar per jam kerja, dan hampir tidak "
                          "pernah dikerjakan."},
                ]},
            ],
            "notes": "Latihan yang bagus untuk kelas: ambil satu alat di sistem mereka dan "
                     "tulis ulang deskripsinya mengikuti empat kaidah tadi. Perbaikan "
                     "biasanya langsung terlihat di jejak.",
        },
    ],
}
