# -*- coding: utf-8 -*-
"""Bab 2 — Model bahasa, dilihat dari sisi orang yang membangun agen.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 2.

🚨 Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti
hanya URUTAN BABNYA. Isinya materi ajar yang ditulis sendiri, gambarnya
digambar sendiri, dan tidak ada blok `img` dari bukunya.

CATATAN PENYUNTINGAN KHUSUS DEK INI. Bab ini membahas Transformer, perhatian
diri, dan pelatihan model — dan kelas ini SUDAH punya 104 slide tentang itu di
`ch15`, plus modul LLM Viny. Menuliskannya lagi di sini berarti mengajarkan hal
yang sama dua kali dengan kata yang berbeda.

Jadi dek ini mengambil sudut yang tidak diambil ch15: **apa yang berubah pada
keputusan seorang pembangun agen**. Token sebagai satuan tagihan, konteks yang
dibayar ulang tiap giliran, singgahan prompt, panggilan alat sebagai perilaku
terlatih, dan cache KV sebagai sebab giliran panjang jadi mahal. Kedalaman
arsitekturnya ditunjuk ke ch15, bukan disalin ke sini.

Angka pada gambar `context_growth` dihitung di generatornya, bukan dikutip.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import context_growth, token_budget  # noqa: E402

B = BOOKS["agents"]


MMD_STATELESS = """
flowchart LR
  subgraph G2["Giliran 2 — permintaan yang BERBEDA"]
    direction TB
    R2["perintah sistem<br/>+ giliran 1<br/>+ giliran 2"] --> M2["Model"] --> J2["Jawaban 2"]
  end
  subgraph G1["Giliran 1"]
    direction TB
    R1["perintah sistem<br/>+ giliran 1"] --> M1["Model"] --> J1["Jawaban 1"]
  end
  G1 ~~~ G2
"""

MMD_TOOLCALL = """
flowchart LR
  S["Skema alat<br/><small>nama, kegunaan,<br/>parameter bertipe</small>"] --> M["Model"]
  M --> C["Panggilan alat<br/><small>terstruktur, belum dijalankan</small>"]
  C --> V["Kode Anda<br/><small>memeriksa, lalu menjalankan</small>"]
  V --> H["Hasil masuk konteks"]
  H --> M
"""

MMD_ROUNDTRIP = """
flowchart LR
  A["Kode Anda"] -->|"kirim SELURUH riwayat"| B["Model"]
  B -->|"panggilan alat"| A
  A -->|"jalankan"| C["Alat / sistem"]
  C -->|"hasil"| A
  A -->|"kirim SELURUH riwayat + hasil"| B
  B -->|"jawaban"| A
"""

MMD_TRAINING = """
flowchart LR
  A["Pra-latih<br/><small>meramal token berikutnya<br/>pada teks raksasa</small>"]
  B["SFT<br/><small>contoh percakapan<br/>yang ditulis manusia</small>"]
  C["RL dari umpan balik<br/><small>diberi imbalan atas<br/>jawaban yang lebih disukai</small>"]
  A --> B --> C
  A -. "tahu bahasa,<br/>belum tahu menjawab" .-> B
  B -. "tahu menjawab,<br/>belum tahu memilih" .-> C
"""


DECK = {
    "id": "agents02",
    "kind": "chapter",
    "number": 2,
    "book": "agents",
    "title": "Model bahasa, dari sisi pembangun agen",
    "subtitle": "Bukan cara kerja Transformer — itu ada di Bab 15. Ini bagian "
                "yang mengubah keputusan: token sebagai satuan tagihan, konteks "
                "yang dibayar ulang, dan panggilan alat sebagai perilaku terlatih.",
    "source": book_source(2, "agents"),
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
        "**Menghitung tagihan sebuah percakapan** dari panjang giliran dan "
        "jumlah giliran, dan menjelaskan kenapa ia tumbuh kuadrat.",
        "**Menyebutkan apa yang dipertahankan singgahan prompt** dan satu "
        "kebiasaan yang mematikannya tanpa peringatan.",
        "**Menjelaskan bahwa model tidak punya ingatan antar giliran**, dan "
        "menunjukkan di mana keadaan percakapan sebenarnya disimpan.",
        "**Menerangkan panggilan alat sebagai keluaran terstruktur** yang "
        "belum dijalankan, dan menunjuk baris tempat ia dijalankan.",
        "**Membedakan tiga tahap pelatihan** dan menyebutkan tahap mana yang "
        "membuat sebuah model bisa dipakai sebagai agen.",
        "**Menyebutkan tiga sifat model** yang harus diukur sebelum memilihnya "
        "untuk sebuah agen — dan mana yang tidak bisa dibaca dari papan skor.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Bab ini",
            "title": "Yang sengaja TIDAK diulang di sini",
            "blocks": [
                {"t": "p", "md": "Kelas ini sudah punya **104 slide** tentang Transformer, "
                                 "perhatian diri, dan penyandian posisi di **Bab 15**, plus "
                                 "modul LLM tersendiri. Bab ini tidak mengulangnya."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Sudah dibahas di tempat lain**"},
                     {"t": "bullets", "items": [
                         "Cara perhatian diri menghitung — Bab 15, dengan angkanya",
                         "Penyandian posisi, encoder lawan decoder — Bab 15",
                         "Pelatihan awal dan penyetelan halus — Bab 15–16",
                     ]}],
                    [{"t": "p", "md": "**Yang dibahas di sini**"},
                     {"t": "bullets", "items": [
                         "Token sebagai satuan tagihan, waktu, dan batas",
                         "Kenapa percakapan panjang mahal secara kuadrat",
                         "Panggilan alat sebagai keluaran terstruktur",
                         "Sifat model mana yang menentukan keberhasilan agen",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Aturannya sederhana: yang masuk ke sini hanya yang **mengubah "
                       "keputusan** saat membangun agen."},
            ],
        },

        {"type": "section", "num": "01", "title": "Token: satuan tagihan, waktu, dan batas",
         "lead": "Tiga hal yang berbeda, semuanya diukur dengan satuan yang sama."},

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Model tidak melihat kata, dan tidak melihat huruf",
            "blocks": [
                {"t": "p", "md": "Teks dipecah jadi **token** — potongan yang lebih besar "
                                 "dari huruf dan biasanya lebih kecil dari kata. Kata yang "
                                 "sering muncul jadi satu token; kata yang jarang pecah jadi "
                                 "beberapa."},
                {"t": "p", "md": "Kenapa ini penting bagi pembangun agen, bukan bagi ahli "
                                 "bahasa: **semua yang Anda bayar, semua yang Anda tunggu, "
                                 "dan semua batas yang Anda tabrak dihitung dalam token** — "
                                 "bukan dalam karakter, kalimat, atau permintaan."},
                {"t": "band",
                 "md": "Taksiran kasar yang cukup untuk perencanaan: **satu token ≈ 4 "
                       "karakter** untuk teks Inggris, dan lebih boros untuk bahasa "
                       "Indonesia serta untuk JSON — dan hasil alat Anda hampir selalu JSON."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Masukan dan keluaran tidak berharga sama, dan tidak berperilaku sama",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Token masukan** — perintah sistem, skema alat, "
                                      "seluruh riwayat, semua hasil alat. Dibaca sekaligus, "
                                      "sejajar, jadi cepat."},
                     {"t": "p", "md": "Di sebuah agen, inilah yang membengkak. Bukan "
                                      "jawabannya."}],
                    [{"t": "p", "md": "**Token keluaran** — yang ditulis model. Dihasilkan "
                                      "satu per satu, tiap token menunggu token sebelumnya, "
                                      "jadi **lambat**."},
                     {"t": "p", "md": "Lebih mahal per token, tapi di sebuah agen jumlahnya "
                                      "jauh lebih sedikit: panggilan alat itu pendek."}],
                ]},
                {"t": "p", "md": "Akibat praktisnya: **agen adalah beban masukan.** "
                                 "Mengoptimalkan panjang jawaban hampir tidak mengubah "
                                 "apa pun; memendekkan yang masuk mengubah semuanya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Percakapannya tumbuh lurus, tagihannya tidak",
            "blocks": [
                context_growth("agents02-context",
                               cap="Sepuluh giliran, dihitung dari perintah sistem 800 token "
                                   "dan 350 token per giliran. Langkahi: giliran pertama, "
                                   "lima pertama, lalu sepuluh.",
                               note="Model tidak mengingat apa pun antar panggilan, jadi "
                                    "seluruh riwayat dikirim ulang tiap giliran. Yang "
                                    "ditagihkan adalah jumlah dari semua konteks itu."),
                {"t": "p", "md": "Percakapan yang berakhir pada 3 950 token menagihkan "
                                 "**23 750** token masukan — enam kali lipat. Dan ini bukan "
                                 "sifat khusus agen; ini sifat percakapan mana pun. Yang "
                                 "khusus pada agen adalah **giliran per tugasnya banyak**, "
                                 "jadi ia berada jauh di kanan grafik itu."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Dua obatnya, dan yang kedua sering dirusak sendiri",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✂", "h": "Kurangi gilirannya",
                     "p": "Satu langkah yang dihapus menghemat lebih banyak daripada "
                          "seribu token yang dipangkas, sebab langkah itu dibayar ulang "
                          "oleh **semua** langkah sesudahnya.",
                     "style": "accent"},
                    {"ico": "💾", "h": "Singgahkan bagian yang tetap",
                     "p": "Perintah sistem, skema alat, dan teks kebijakan tidak berubah "
                          "antar giliran. Penyedia menagihnya jauh lebih murah kalau "
                          "awalannya **sama persis**.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Satu stempel waktu di dalam perintah sistem membuat awalannya "
                       "berbeda tiap kali, dan ==singgahannya mati tanpa satu pun pesan "
                       "galat==. Periksa `cache_read_input_tokens` bukan nol — jangan "
                       "percaya bahwa ia menyala."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Jendela konteks adalah dinding, bukan saran",
            "blocks": [
                {"t": "p", "md": "Tiap model punya batas jumlah token yang boleh masuk "
                                 "sekaligus. Melewatinya bukan menghasilkan jawaban yang "
                                 "lebih buruk — ia menghasilkan **galat**, atau diam-diam "
                                 "memotong bagian paling awal percakapan."},
                {"t": "p", "md": "Yang paling awal biasanya **perintah sistem dan batasan "
                                 "Anda**. Jadi kegagalannya berbentuk: agen bekerja normal "
                                 "selama sepuluh giliran, lalu pada giliran ke dua puluh "
                                 "mulai melanggar aturan yang sudah tidak ada lagi di "
                                 "konteksnya."},
                {"t": "band",
                 "md": "Karena itu memangkas riwayat harus jadi **keputusan yang Anda "
                       "tulis**, bukan akibat sampingan. Bab 4 membahas apa yang disimpan "
                       "dan apa yang dibuang."},
            ],
        },

        {"type": "section", "num": "02",
         "title": "Dari model bahasa ke mesin agen",
         "lead": "Tiga hal yang harus ada sebelum sebuah model bisa dipakai dalam gelung."},

        {
            "type": "slide",
            "kicker": "Dari model ke agen",
            "title": "Model tidak punya ingatan — riwayatnya yang punya",
            "blocks": [
                {"t": "mmd", "id": "agents02-stateless", "src": MMD_STATELESS,
                 "cap": "Dua giliran adalah dua permintaan yang sama sekali terpisah."},
                {"t": "p", "md": "Antara dua giliran, model **tidak menyimpan apa pun**. "
                                 "Yang membuatnya tampak mengingat adalah kode Anda "
                                 "mengirim ulang seluruh percakapan tiap kali. Keadaan "
                                 "percakapan ada di **daftar pesan milik Anda**, dan itu "
                                 "kabar baik: keadaan yang Anda pegang adalah keadaan yang "
                                 "bisa Anda periksa, potong, dan simpan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dari model ke agen",
            "title": "Perintah sistem: kontrak, bukan mantra",
            "blocks": [
                {"t": "p", "md": "Perintah sistem menetapkan peran, gaya, dan batasan. Ia "
                                 "berguna dan perlu ditulis dengan hati-hati — tetapi ia "
                                 "**bukan mekanisme keamanan**."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Yang pantas ditaruh di sana**"},
                     {"t": "bullets", "items": [
                         "Peran dan pembacanya",
                         "Format jawaban yang diharapkan",
                         "Kapan harus menyerah dan bertanya",
                         "Kebijakan yang harus dikutip, bukan diingat",
                     ]}],
                    [{"t": "p", "md": "**Yang tidak boleh hanya di sana**"},
                     {"t": "bullets", "items": [
                         "\u201cJangan pernah menghapus data\u201d \u2192 jangan beri alat hapus",
                         "\u201cJangan bocorkan data pribadi\u201d \u2192 jangan beri alat yang bisa membacanya",
                         "\u201cJangan menyetujui\u201d \u2192 jangan sediakan alat menyetujui",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Uji sederhana: kalau sebuah kalimat di perintah sistem hilang, "
                       "apakah sistemnya jadi tidak aman? Kalau ya, ==kalimat itu berada di "
                       "tempat yang salah==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dari model ke agen",
            "title": "Panggilan alat adalah keluaran terstruktur, bukan eksekusi",
            "blocks": [
                {"t": "mmd", "id": "agents02-toolcall", "src": MMD_TOOLCALL,
                 "cap": "Model menghasilkan niat; kode memutuskan apakah niat itu dijalankan."},
                {"t": "p", "md": "Model diberi **skema** tiap alat — namanya, kegunaannya, "
                                 "parameternya beserta tipe. Yang ia keluarkan hanyalah "
                                 "sebuah objek: nama alat dan argumen. Objek itu belum "
                                 "melakukan apa-apa."},
                {"t": "band",
                 "md": "Ini fakta arsitektural terpenting dalam seluruh modul, dan ia "
                       "muncul lagi di tiap bab: **model menuliskan niat, kode Anda yang "
                       "mengeksekusi.** Semua batas izin yang Anda punya berada di celah "
                       "itu."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dari model ke agen",
            "title": "Deskripsi alat adalah antarmuka, dan ditulis untuk pembaca yang aneh",
            "blocks": [
                {"t": "p", "md": "Satu-satunya yang dipakai model untuk memilih alat adalah "
                                 "**deskripsinya**. Bukan kodenya, bukan namanya saja. "
                                 "Deskripsi yang buruk menghasilkan agen yang tampak bodoh, "
                                 "dan orang biasanya menyalahkan modelnya."},
                {"t": "table",
                 "head": ["Ditulis begini", "Akibatnya", "Perbaikannya"],
                 "widths": [30, 36, 34],
                 "rows": [
                     ["`cari(q)` — mencari data",
                      "Dipanggil untuk apa saja, termasuk yang bukan urusannya",
                      "Sebut **apa** yang dicari dan **kapan** memakainya"],
                     ["Dua alat dengan deskripsi mirip",
                      "Dipilih acak antara keduanya",
                      "Gabungkan, atau bedakan dengan tegas"],
                     ["Parameter tanpa tipe atau contoh",
                      "Argumen ngawur, galat di dalam alat",
                      "Tipe ketat + satu contoh nilai"],
                     ["Deskripsi menyebut cara kerjanya",
                      "Tidak membantu memilih",
                      "Sebut **hasilnya**, bukan implementasinya"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dari model ke agen",
            "title": "Suhu: satu angka yang diam-diam menentukan keterulangan",
            "blocks": [
                {"t": "p", "md": "Model memilih token berikutnya dari sebaran peluang. "
                                 "**Suhu** mengatur seberapa berani pilihannya menyimpang "
                                 "dari yang paling mungkin."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🎯", "h": "Rendah (0–0,3)",
                     "p": "Nyaris sama tiap kali. Yang Anda mau untuk **memilih alat** dan "
                          "mengeluarkan JSON.",
                     "style": "good"},
                    {"ico": "⚖", "h": "Sedang (0,5–0,7)",
                     "p": "Untuk menyusun penjelasan yang enak dibaca, sesudah keputusannya "
                          "diambil."},
                    {"ico": "🎲", "h": "Tinggi (> 1)",
                     "p": "Untuk mencari ragam gagasan. Hampir tidak pernah untuk agen "
                          "yang menyentuh sistem nyata.",
                     "style": "bad"},
                ]},
                {"t": "band",
                 "md": "Dan satu jebakan pengujian: pada suhu tinggi, **kumpulan uji yang "
                       "lulus hari ini bisa gagal besok tanpa satu baris pun berubah**. "
                       "Kalau hasil uji Anda goyah, periksa angka ini sebelum menyalahkan "
                       "agennya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Hasil alat adalah JSON, dan JSON itu boros",
            "blocks": [
                {"t": "p", "md": "Teks prosa mendekati 4 karakter per token. JSON tidak: "
                                 "tanda kutip, kurung kurawal, koma, dan nama kunci yang "
                                 "berulang di tiap baris semuanya dihitung."},
                {"t": "p", "md": "Satu tabel 20 baris dengan 8 kolom bisa menghabiskan "
                                 "beberapa ribu token — dan karena ia masuk riwayat, ia "
                                 "**dibayar ulang di tiap giliran sesudahnya**. Ini "
                                 "penyebab pembengkakan biaya yang paling sering tidak "
                                 "terlihat, sebab yang dilihat orang adalah panjang "
                                 "jawabannya."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "✂", "h": "Kembalikan yang dipakai",
                     "p": "Alat yang mengembalikan seluruh baris ketika agen hanya butuh "
                          "satu angka membayar seribu token untuk satu.",
                     "style": "good"},
                    {"ico": "📄", "h": "Ringkas di sisi alat",
                     "p": "Peringkasan yang dilakukan **kode** gratis dan pasti; yang "
                          "dilakukan model berbayar dan bisa salah.",
                     "style": "good"},
                    {"ico": "🔁", "h": "Rujuk, jangan salin",
                     "p": "Simpan hasil besar di luar, kembalikan pengenalnya. Bab 4 "
                          "menyebut ini memori kerja."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Jendela konteks itu anggaran, dan sebagian sudah habis sebelum mulai",
            "blocks": [
                token_budget("agents02-budget",
                             cap="Jendela 128k, dibelanjakan: bagian tetap, lalu hasil alat "
                                 "yang menumpuk tiap giliran. Langkahi 5, 15, dan 30 giliran.",
                             note="Angkanya asumsi yang dicetak di gambarnya — perintah "
                                  "sistem 4k, dua belas skema alat 6k, hasil alat 2,4k per "
                                  "giliran. Ganti asumsinya dan gambarnya berubah."),
                {"t": "p", "md": "Sepuluh ribu token sudah terpakai **sebelum giliran "
                                 "pertama**, dan tiap alat baru memotong lagi. Itu sebabnya "
                                 "\u201ctambahkan saja satu alat lagi\u201d bukan keputusan "
                                 "gratis: ia memperkecil ruang kerja tiap giliran sesudahnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Token",
            "title": "Satu giliran agen adalah dua perjalanan penuh",
            "blocks": [
                {"t": "mmd", "id": "agents02-roundtrip", "src": MMD_ROUNDTRIP,
                 "cap": "Memanggil satu alat berarti mengirim seluruh riwayat dua kali."},
                {"t": "p", "md": "Model memutuskan alat mana yang dipanggil — itu satu "
                                 "permintaan. Hasilnya dibaca dan diubah jadi jawaban — itu "
                                 "permintaan kedua, dengan riwayat yang sekarang lebih "
                                 "panjang. **Satu panggilan alat berharga dua permintaan**, "
                                 "bukan satu."},
                {"t": "band",
                 "md": "Karena itu \u201cberapa alat yang dipanggil\u201d adalah ukuran "
                       "biaya yang lebih baik daripada \u201cberapa permintaan\u201d, dan "
                       "kenapa menggabungkan dua alat kecil jadi satu sering lebih hemat "
                       "daripada mengoptimalkan keduanya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Waktu",
            "title": "Waktu tunggu bukan satu angka",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Waktu ke token pertama** — dipengaruhi panjang "
                                      "masukan. Konteks panjang membuat jeda pertama terasa, "
                                      "dan inilah yang dirasakan pengguna sebagai "
                                      "\u201clambat\u201d."}],
                    [{"t": "p", "md": "**Waktu total** — dipengaruhi panjang keluaran, "
                                      "sebab token dihasilkan satu per satu. Di agen ini "
                                      "biasanya kecil; yang besar adalah **waktu alat**."}],
                ]},
                {"t": "p", "md": "Pada agen enam langkah, sebagian besar waktu dinding "
                                 "sering bukan milik model sama sekali — melainkan milik "
                                 "kueri basis data dan panggilan HTTP di dalam alat. "
                                 "Mengukur waktu model saja akan mengoptimalkan bagian yang "
                                 "salah."},
                {"t": "band",
                 "md": "Ukur per **giliran**, bukan per tugas: waktu model, waktu alat, dan "
                       "jumlah giliran. Tiga angka itu memberi tahu di mana waktunya pergi; "
                       "satu angka total tidak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Waktu",
            "title": "Mengalirkan jawaban tidak membuat agen lebih cepat",
            "blocks": [
                {"t": "p", "md": "Pengaliran (*streaming*) mengirim token begitu dihasilkan. "
                                 "Untuk obrolan itu besar pengaruhnya pada rasa: pengguna "
                                 "melihat sesuatu bergerak."},
                {"t": "p", "md": "Untuk agen, pengaruhnya jauh lebih kecil, dan sering "
                                 "**nol** — sebab yang keluar dari model bukan jawaban, "
                                 "melainkan panggilan alat yang harus **lengkap** sebelum "
                                 "bisa dijalankan. Tidak ada yang bisa dikerjakan dari "
                                 "separuh panggilan alat."},
                {"t": "band",
                 "md": "Yang benar-benar mengurangi rasa lambat pada agen: **menampilkan "
                       "alat mana yang sedang berjalan**. Itu sebabnya layar ketiga di demo "
                       "menyebut nama alatnya, bukan memutar lingkaran."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Keluaran terstruktur",
            "title": "Tiga cara memaksa bentuk, dengan tiga tingkat jaminan",
            "blocks": [
                {"t": "table",
                 "head": ["Cara", "Jaminannya", "Kapan dipakai"],
                 "widths": [26, 40, 34],
                 "rows": [
                     ["Diminta di prompt",
                      "Tidak ada. Sering benar, kadang tidak, dan gagalnya tidak seragam",
                      "Prototipe, atau model tanpa dukungan lain"],
                     ["Mode JSON penyedia",
                      "JSON-nya sah, **isinya belum tentu sesuai skema**",
                      "Ketika hanya butuh objek yang bisa diurai"],
                     ["Panggilan alat / skema ketat",
                      "Nama dan tipe parameter dijamin di sisi penyedia",
                      "Untuk agen — ini yang dipakai"],
                 ]},
                {"t": "p", "md": "Perbedaan baris kedua dan ketiga adalah perbedaan antara "
                                 "*bisa diurai* dan *bisa dipercaya*. Yang pertama menghindarkan "
                                 "galat penguraian; hanya yang kedua yang menghindarkan "
                                 "argumen yang masuk akal secara sintaks dan salah secara isi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Keluaran terstruktur",
            "title": "Validasi tetap di sisi Anda, dan gagalnya harus punya jalan",
            "blocks": [
                {"t": "p", "md": "Skema ketat menjamin **bentuk**, bukan **kebenaran**. "
                                 "`id_pelanggan` bertipe string yang berisi id milik orang "
                                 "lain tetap lolos skema."},
                {"t": "steps", "items": [
                    {"h": "Periksa di batas alat, sebelum efek apa pun",
                     "p": "Rentang, keberadaan, kepemilikan. Alat yang dipanggil dengan "
                          "argumen tidak sah harus **menolak**, bukan menebak maksudnya."},
                    {"h": "Kembalikan galat yang bisa dipakai model",
                     "p": "\u201cid tidak ditemukan\u201d membuatnya mencoba jalan lain. "
                          "\u201cGalat 500\u201d membuatnya mengulang hal yang sama."},
                    {"h": "Hitung berapa kali ini terjadi",
                     "p": "Laju penolakan skema adalah ukuran kualitas model yang paling "
                          "cepat memberi tahu Anda telah memilih model yang salah."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Keluaran terstruktur",
            "title": "Determinisme yang cukup untuk bisa diuji",
            "blocks": [
                {"t": "p", "md": "Kumpulan uji yang hasilnya berubah-ubah tanpa perubahan "
                                 "kode bukan kumpulan uji — ia sumber kebisingan yang "
                                 "membuat orang berhenti mempercayainya."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🌡", "h": "Suhu nol untuk jalur keputusan",
                     "p": "Pemilihan alat dan pengeluaran argumen tidak butuh keragaman. "
                          "Keragaman di sana namanya ketidakstabilan.",
                     "style": "good"},
                    {"ico": "🧪", "h": "Penyedia luring untuk menguji mesinnya",
                     "p": "Gelung, anggaran, penjaga, dan validasi alat tidak butuh model "
                          "sungguhan untuk diuji — dan uji yang tidak butuh jaringan akan "
                          "benar-benar dijalankan orang.",
                     "style": "good"},
                ]},
                {"t": "band",
                 "md": "Bahkan pada suhu nol, penyedia **tidak menjanjikan** keluaran yang "
                       "identik antar waktu. Uji yang mensyaratkan kalimat persis akan "
                       "rapuh; uji yang mensyaratkan **alat mana yang dipanggil** tidak."},
            ],
        },

        {"type": "section", "num": "03", "title": "Bagaimana ia jadi bisa disuruh",
         "lead": "Tiga tahap, dan hanya dua terakhir yang membuatnya berguna sebagai agen."},

        {
            "type": "slide",
            "kicker": "Pelatihan",
            "title": "Tiga tahap, tiga kemampuan yang berbeda",
            "blocks": [
                {"t": "mmd", "id": "agents02-training", "src": MMD_TRAINING,
                 "cap": "Tiap tahap menambah kemampuan yang tidak dimiliki tahap sebelumnya."},
                {"t": "p", "md": "**Pra-latih** memberinya bahasa dan pengetahuan dunia, "
                                 "dari meramal token berikutnya pada teks dalam jumlah "
                                 "raksasa. Model di tahap ini belum bisa disuruh — ia "
                                 "melanjutkan teks, tidak menjawab pertanyaan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pelatihan",
            "title": "Tahap yang membuatnya bisa dipakai dalam gelung",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Penyetelan terbimbing (SFT)**"},
                     {"t": "p", "md": "Dilatih pada contoh percakapan yang ditulis manusia: "
                                      "permintaan, dan jawaban yang pantas. Di sinilah ia "
                                      "belajar bentuk *menjawab*, dan di sini pula ia "
                                      "belajar bentuk **panggilan alat** — sebab contohnya "
                                      "berisi panggilan alat."}],
                    [{"t": "p", "md": "**Penguatan dari umpan balik**"},
                     {"t": "p", "md": "Manusia (atau model penilai) membandingkan dua "
                                      "jawaban; model diberi imbalan atas yang lebih "
                                      "disukai. Di sinilah ia belajar **menuruti batasan**, "
                                      "menolak, dan berhenti mengarang dengan percaya diri."}],
                ]},
                {"t": "band",
                 "md": "Kenapa ini penting bagi pembangun agen: **kepatuhan pada skema alat "
                       "dan pada instruksi adalah hasil pelatihan, bukan sifat bawaan "
                       "Transformer.** Dua model dengan arsitektur nyaris sama bisa sangat "
                       "berbeda di sini, dan itulah yang paling menentukan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pelatihan",
            "title": "Yang tidak diperbaiki oleh tahap mana pun",
            "blocks": [
                {"t": "p", "md": "Tidak satu pun dari ketiga tahap itu membuat model "
                                 "**tahu apa yang tidak diketahuinya**. Ia dilatih "
                                 "menghasilkan lanjutan yang masuk akal, dan lanjutan yang "
                                 "masuk akal tetap masuk akal ketika salah."},
                {"t": "steps", "items": [
                    {"h": "Akibat pertama: percaya diri bukan sinyal",
                     "p": "Nada yakin dihasilkan oleh pelatihan yang sama, entah isinya "
                          "benar atau tidak."},
                    {"h": "Akibat kedua: sumber harus dari alat",
                     "p": "Angka yang tidak berasal dari hasil alat adalah angka yang tidak "
                          "punya asal-usul. Itu sebabnya bab 5 memperlakukan alat sebagai "
                          "sumber bukti, bukan sekadar kemampuan."},
                    {"h": "Akibat ketiga: penilaian harus melihat jejak",
                     "p": "Keluaran yang benar dari alasan yang salah akan berulang. "
                          "Bab 7."},
                ]},
            ],
        },

        {"type": "section", "num": "04", "title": "Arsitektur, sejauh yang mengubah keputusan",
         "lead": "Kedalamannya di Bab 15. Di sini hanya bagian yang terasa di tagihan."},

        {
            "type": "slide",
            "kicker": "Arsitektur",
            "title": "Cache KV: kenapa token pertama lambat dan sisanya cepat",
            "blocks": [
                {"t": "p", "md": "Untuk menghasilkan token, model melihat seluruh token "
                                 "sebelumnya. Menghitung ulang semuanya tiap token akan "
                                 "sangat boros, jadi hasil antaranya **disimpan** — itulah "
                                 "cache KV."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Fase isi** — seluruh masukan diproses sekaligus. "
                                      "Sejajar, cepat per token, tapi inilah yang membuat "
                                      "token pertama terasa lama pada konteks panjang."}],
                    [{"t": "p", "md": "**Fase lanjut** — satu token per langkah, memakai "
                                      "cache. Murah dalam komputasi, tetapi cachenya "
                                      "**memakan memori** yang tumbuh bersama panjang "
                                      "konteks."}],
                ]},
                {"t": "band",
                 "md": "Yang terasa di produksi: konteks panjang bukan hanya lebih mahal "
                       "ditagih — ia juga **menurunkan jumlah permintaan bersamaan** yang "
                       "muat di satu GPU. Itu sebabnya penyedia membedakan harga menurut "
                       "panjang konteks."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Arsitektur",
            "title": "Campuran pakar: kenapa model besar bisa murah",
            "blocks": [
                {"t": "p", "md": "Sebagian model modern hanya menyalakan **sebagian kecil** "
                                 "parameternya untuk tiap token. Jumlah parameter totalnya "
                                 "besar; yang aktif per token jauh lebih kecil."},
                {"t": "p", "md": "Akibatnya satu angka yang sering dipakai membandingkan "
                                 "model — jumlah parameter — **berhenti berarti apa-apa** "
                                 "sebagai penanda biaya atau kecepatan. Dua model dengan "
                                 "angka yang sama bisa berbeda berkali lipat ongkosnya."},
                {"t": "band",
                 "md": "Aturan praktisnya: bandingkan model dengan **biaya per tugas yang "
                       "selesai**, diukur pada kumpulan uji Anda sendiri. Bukan dengan "
                       "jumlah parameter, dan bukan dengan harga per juta token."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Arsitektur",
            "title": "Ke mana mencari kedalamannya",
            "blocks": [
                {"t": "table",
                 "head": ["Kalau ingin tahu", "Lihat", "Yang ada di sana"],
                 "widths": [34, 22, 44],
                 "rows": [
                     ["Cara perhatian diri menghitung",
                      "**Bab 15**",
                      "Q·K·V pada kalimat nyata sampai persentase softmax, dan satu slide "
                      "yang membaca angkanya dengan jujur"],
                     ["Kenapa perlu proyeksi Q dan K",
                      "**Bab 15**",
                      "Jejak `run`: tanpa proyeksi, sebuah kata menghabiskan 60% "
                      "perhatiannya untuk dirinya sendiri"],
                     ["Penyandian posisi",
                      "**Bab 15**",
                      "Gambar yang menghitung sendiri"],
                     ["Menghasilkan teks, pengambilan sampel",
                      "**Bab 16**",
                      "Suhu, top-p, dan gelung pengambilan sampel"],
                 ]},
                {"t": "p", "md": "Dek ini sengaja berhenti di sini. Menuliskan ulang isi "
                                 "Bab 15 dengan kata yang berbeda akan menambah slide "
                                 "tanpa menambah apa pun yang bisa dipakai."},
            ],
        },

        {"type": "section", "num": "05", "title": "Memilih model untuk sebuah agen",
         "lead": "Papan skor menjawab pertanyaan yang berbeda dari pertanyaan Anda."},

        {
            "type": "slide",
            "kicker": "Memilih",
            "title": "Tiga sifat yang menentukan, dan hanya satu yang ada di papan skor",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🧩", "h": "Kepatuhan pada skema",
                     "p": "Seberapa sering ia mengeluarkan panggilan alat yang **sah** dan "
                          "argumen yang bertipe benar. Kegagalan di sini terlihat seperti "
                          "agen yang bodoh, padahal soal format.",
                     "style": "accent"},
                    {"ico": "🛑", "h": "Kemauan berhenti",
                     "p": "Seberapa sering ia mengatakan *tidak bisa* alih-alih menebak. "
                          "Model yang tidak pernah menyerah menghasilkan agen yang "
                          "berputar.",
                     "style": "accent"},
                    {"ico": "📏", "h": "Kepatuhan pada instruksi panjang",
                     "p": "Batasan di token ke-3 000 masih dituruti pada giliran ke-15? "
                          "Inilah yang paling cepat rusak saat konteks memanjang.",
                     "style": "accent"},
                ]},
                {"t": "p", "md": "Papan skor umum mengukur pengetahuan dan penalaran — "
                                 "berguna, tetapi bukan tiga hal di atas. Ketiganya harus "
                                 "**diukur pada kumpulan uji Anda sendiri**, dan itu satu "
                                 "sore kerja, bukan satu proyek."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memilih",
            "title": "Urutan yang menghemat paling banyak waktu",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Mulai dari model paling mampu yang ada",
                     "p": "Sampai agennya **benar**. Mengoptimalkan agen yang belum benar "
                          "hanya membuat kesalahannya lebih murah."},
                    {"h": "Baru turunkan, satu tingkat, dengan kumpulan uji di tangan",
                     "p": "Kalau angkanya bertahan, simpan penghematannya. Kalau tidak, "
                          "Anda baru saja mengetahui harga sebenarnya dari model yang lebih "
                          "murah."},
                    {"h": "Ukur biaya per tugas selesai, bukan per permintaan",
                     "p": "Model murah yang perlu dua kali lebih banyak giliran tidak "
                          "menghemat apa pun."},
                    {"h": "Pertimbangkan model lokal ketika datanya yang menentukan",
                     "p": "Bukan karena lebih murah — sering tidak. Karena ada data yang "
                          "tidak boleh keluar, dan itu keputusan kepatuhan, bukan teknis."},
                ]},
                {"t": "band",
                 "md": "`ai-agentic-demo` menjalankan kelimanya lewat satu antarmuka: "
                       "`echo` (luring), `ollama` (mesin sendiri), `gemini`, `anthropic`, "
                       "`openai` — jadi menukar model adalah satu argumen, bukan satu "
                       "penulisan ulang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memilih",
            "title": "Bahasa Indonesia lebih mahal per kalimat, dan itu bukan dugaan",
            "blocks": [
                {"t": "p", "md": "Pemenggal token pada kebanyakan model dilatih pada teks "
                                 "yang didominasi bahasa Inggris. Kata Inggris yang umum "
                                 "sering jadi **satu** token; kata Indonesia yang sama "
                                 "umumnya pecah jadi dua, tiga, atau lebih — terutama kata "
                                 "berimbuhan."},
                {"t": "p", "md": "Akibatnya langsung dan berlipat: kalimat yang sama "
                                 "artinya menghabiskan lebih banyak token, jadi lebih mahal, "
                                 "lebih cepat memenuhi jendela konteks, dan lebih lambat "
                                 "dihasilkan."},
                {"t": "band",
                 "md": "Jangan menaksir — **ukur pada teks Anda sendiri**. Ambil seratus "
                       "kalimat nyata dari domain Anda, hitung tokennya dengan pemenggal "
                       "model yang dipakai, dan pakai angka itu untuk perencanaan biaya. "
                       "Taksiran 4 karakter per token adalah taksiran untuk bahasa Inggris."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memilih",
            "title": "Jendela besar tidak berarti seluruhnya terpakai dengan baik",
            "blocks": [
                {"t": "p", "md": "Jendela satu juta token tidak berarti model memperhatikan "
                                 "satu juta token sama baiknya. Kemampuan menemukan "
                                 "informasi cenderung **paling baik di awal dan di akhir** "
                                 "konteks, dan paling lemah di tengah."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Akibat untuk penyusunan konteks**"},
                     {"t": "bullets", "items": [
                         "Taruh perintah dan batasan di **awal**",
                         "Taruh permintaan giliran ini di **akhir**",
                         "Jangan menaruh aturan penting di tengah tumpukan hasil alat",
                     ]}],
                    [{"t": "p", "md": "**Akibat untuk arsitektur**"},
                     {"t": "bullets", "items": [
                         "Konteks besar bukan pengganti pengambilan yang tepat",
                         "Memasukkan seluruh dokumen karena \u201cmuat\u201d "
                         "menurunkan ketepatan, bukan menaikkannya",
                         "Bab 4 membahas apa yang disimpan dan apa yang dicari lagi",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Uji ini murah dan jarang dilakukan: ==sisipkan satu fakta di "
                       "tengah konteks panjang dan tanyakan== — pada panjang yang benar-benar "
                       "Anda pakai, bukan pada panjang maksimum di brosur."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operasional",
            "title": "Model diperbarui, dan agen Anda berubah tanpa Anda menyentuhnya",
            "blocks": [
                {"t": "p", "md": "Nama model tanpa versi menunjuk ke sasaran yang bergerak. "
                                 "Penyedia memperbarui bobotnya; perilaku pemilihan alat, "
                                 "panjang jawaban, dan kepatuhan format ikut bergeser — "
                                 "tanpa satu baris pun berubah di sisi Anda."},
                {"t": "steps", "items": [
                    {"h": "Sematkan versinya di produksi",
                     "p": "Kalau penyedianya menyediakan pengenal versi, pakai. Kalau "
                          "tidak, catat tanggal dan jalankan kumpulan uji lebih sering."},
                    {"h": "Catat versi model pada tiap jejak",
                     "p": "Tanpa itu, \u201csejak kapan ini mulai salah\u201d tidak bisa "
                          "dijawab. Sama seperti versi model kredit dicatat pada tiap "
                          "rekomendasi di demo."},
                    {"h": "Jalankan kumpulan uji sebelum berpindah versi",
                     "p": "Perpindahan versi adalah perubahan perangkat lunak, dan pantas "
                          "diperlakukan seperti perubahan perangkat lunak."},
                ]},
                {"t": "band",
                 "md": "Ini kelas kegagalan yang tidak muncul di pengembangan dan hanya "
                       "muncul di produksi — dan gejalanya **selalu** terlihat seperti "
                       "\u201ctiba-tiba agennya jadi bodoh\u201d."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operasional",
            "title": "Batas laju: yang membatasi bukan kecepatan, melainkan token per menit",
            "blocks": [
                {"t": "p", "md": "Penyedia membatasi dua hal sekaligus: permintaan per "
                                 "menit dan **token per menit**. Agen dengan konteks panjang "
                                 "menabrak yang kedua jauh sebelum yang pertama."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Kenapa ini mengejutkan orang**"},
                     {"t": "p", "md": "Sepuluh pengguna bersamaan terdengar kecil. Sepuluh "
                                      "pengguna × enam giliran × konteks yang menumpuk bisa "
                                      "berarti ratusan ribu token per menit."}],
                    [{"t": "p", "md": "**Yang harus ada sebelum dipakai banyak orang**"},
                     {"t": "bullets", "items": [
                         "Antrean, bukan pengulangan langsung",
                         "Mundur bertahap ketika ditolak",
                         "Batas jumlah proses agen yang berjalan bersamaan",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Dan satu akibat desain: **memperpendek konteks menaikkan kapasitas**, "
                       "bukan hanya menurunkan biaya. Keduanya obat yang sama."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operasional",
            "title": "Model di mesin sendiri: kapan masuk akal",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔒", "h": "Ketika datanya yang menentukan",
                     "p": "Ada data yang tidak boleh keluar dari perimeter. Ini keputusan "
                          "**kepatuhan**, dan ia mengalahkan pertimbangan biaya maupun "
                          "kualitas.",
                     "style": "accent"},
                    {"ico": "💸", "h": "Bukan karena lebih murah",
                     "p": "Sering justru tidak, kalau pemakaiannya tidak rata: GPU menganggur "
                          "tetap dibayar, sedangkan API yang tidak dipanggil tidak.",
                     "style": "bad"},
                ]},
                {"t": "p", "md": "Yang berubah secara teknis: model terbuka umumnya lebih "
                                 "lemah pada **kepatuhan skema alat** dan lebih mudah "
                                 "berhenti terlalu awal. Itu bukan alasan menolaknya — itu "
                                 "alasan mengukurnya pada kumpulan uji Anda sebelum "
                                 "memutuskan."},
                {"t": "band",
                 "md": "Dijalankan sungguhan di demo dengan `qwen3:8b`: gelungnya benar, "
                       "tetapi **berhenti satu langkah lebih awal** tanpa memanggil alat "
                       "pengiriman rekomendasi. Kelemahan yang terukur, bukan yang ditebak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operasional",
            "title": "Enam angka yang pantas dicatat pada tiap proses",
            "blocks": [
                {"t": "table",
                 "head": ["Angka", "Yang diberitahukannya", "Gejala kalau memburuk"],
                 "widths": [24, 38, 38],
                 "rows": [
                     ["Token masukan per tugas", "Biaya sebenarnya",
                      "Naik pelan tanpa perubahan kode → riwayat tidak dipangkas"],
                     ["`cache_read` bukan nol", "Singgahan menyala",
                      "Jadi nol → ada yang menaruh sesuatu yang berubah di awalan"],
                     ["Giliran per tugas", "Panjang penalaran",
                      "Naik → alat berubah, atau deskripsinya jadi kabur"],
                     ["Laju penolakan skema", "Kecocokan model",
                      "Naik sesudah ganti model → modelnya, bukan agennya"],
                     ["Waktu alat lawan waktu model", "Ke mana waktu pergi",
                      "Waktu alat mendominasi → optimasi model tidak akan terasa"],
                     ["Laju eskalasi ke manusia", "Kejujuran sistem",
                      "Turun ke nol → curigai, jangan rayakan"],
                 ]},
                {"t": "p", "md": "Tidak satu pun dari enam ini menimbulkan **galat**. "
                                 "Semuanya bergeser diam-diam, dan hanya terlihat kalau "
                                 "dicatat sejak awal."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Token adalah satuan segalanya",
                     "p": "Tagihan, waktu tunggu, dan batas konteks — ketiganya diukur "
                          "dengan satuan yang sama, dan agen adalah beban **masukan**."},
                    {"h": "Percakapan sepuluh giliran menagih enam kali isinya",
                     "p": "Sebab tiap giliran membayar ulang semua giliran sebelumnya. "
                          "Mengurangi langkah mengalahkan memangkas kata."},
                    {"h": "Model tidak mengingat; daftar pesan Anda yang mengingat",
                     "p": "Itu kabar baik — keadaan yang Anda pegang bisa diperiksa dan "
                          "dipotong dengan sengaja."},
                    {"h": "Panggilan alat adalah niat, bukan eksekusi",
                     "p": "Semua batas izin hidup di celah antara model menuliskannya dan "
                          "kode Anda menjalankannya."},
                    {"h": "Pilih model dengan kumpulan uji Anda, bukan papan skor",
                     "p": "Kepatuhan skema, kemauan berhenti, dan kepatuhan instruksi "
                          "panjang tidak ada di sana."},
                ]},
            ],
            "notes": "Kalau waktunya mepet, tiga slide yang tidak boleh dilewat: "
                     "pertumbuhan konteks, panggilan alat sebagai keluaran terstruktur, "
                     "dan tiga sifat model. Sisanya bisa jadi bacaan.",
        },
    ],
}
