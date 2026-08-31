# -*- coding: utf-8 -*-
"""Bab 8 — Sistem banyak agen: kapan memecah, dan apa harganya.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 8.

Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti hanya
URUTAN BABNYA. Isinya materi ajar sendiri, gambarnya digambar sendiri.

Gambar `split_cost` dibuat SESUDAH penulisnya menduga yang sebaliknya dan
dikoreksi oleh hitungannya sendiri. Dugaan "memecah pasti lebih mahal" salah
untuk serah-terima yang kecil, sebab tagihan tumbuh kuadrat dan memecah
percakapan memecah kuadratnya. Asumsinya dicetak di gambar.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import split_cost  # noqa: E402

B = BOOKS["agents"]


MMD_PATTERNS = """
flowchart TB
  subgraph S["Penyelia"]
    direction LR
    SU["Penyelia"] --> A1["Agen A"]
    SU --> A2["Agen B"]
    A1 --> SU
    A2 --> SU
  end
  subgraph P["Berantai"]
    direction LR
    P1["Agen 1"] --> P2["Agen 2"] --> P3["Agen 3"]
  end
  subgraph G["Kelompok"]
    direction LR
    G1["Agen A"] <--> G2["Agen B"]
    G2 <--> G3["Agen C"]
    G1 <--> G3
  end
  S ~~~ P ~~~ G
"""

MMD_HANDOFF = """
flowchart LR
  A["Agen 1<br/><small>konteks penuh:<br/>12 000 token</small>"]
  H["Serah-terima<br/><small>ringkasan</small>"]
  B["Agen 2<br/><small>hanya melihat ini</small>"]
  A --> H --> B
  H -. "apa pun yang tidak masuk ke sini<br/>TIDAK ADA bagi agen 2" .-> H
"""

MMD_A2A = """
flowchart LR
  subgraph IN["Ke dalam — MCP"]
    AG["Agen"] --> MCP["Peladen alat"] --> SYS[("Sistem")]
  end
  subgraph AC["Menyilang — antar agen"]
    A1["Agen A"] <--> A2["Agen B<br/><small>milik tim lain</small>"]
  end
  IN ~~~ AC
"""

MMD_HANDOFF_SHAPE = """
flowchart LR
  H["Serah-terima"] --> F1["Temuan<br/><small>+ sumbernya</small>"]
  H --> F2["Angka<br/><small>+ alat asalnya</small>"]
  H --> F3["Yang masih terbuka"]
  H --> F4["Yang diminta berikutnya"]
  H -. "medannya TETAP —<br/>prosa bebas selalu membengkak" .-> H
"""

MMD_DEBUG = """
flowchart TB
  F["Hasil akhirnya salah"] --> Q1{"Agen mana<br/>yang terakhir benar?"}
  Q1 --> Q2{"Serah-terimanya<br/>membawa yang perlu?"}
  Q2 -->|"tidak"| FIX1["Perbaiki isi serah-terima"]
  Q2 -->|"ya"| FIX2["Perbaiki agen sesudahnya"]
  Q1 -. "tanpa jejak per agen,<br/>pertanyaan ini tidak bisa dijawab" .-> Q1
"""


DECK = {
    "id": "agents08",
    "kind": "chapter",
    "number": 8,
    "book": "agents",
    "title": "Sistem banyak agen",
    "subtitle": "Kapan memecah pekerjaan jadi beberapa agen benar-benar "
                "menolong — dan variabel yang menentukan harganya, yang "
                "hampir tidak pernah diukur.",
    "source": book_source(8, "agents"),
    "source_url": "",
    "duration": "3 jam (2 sesi)",
    "presenter": [
        {"name": "Hendri Karisma", "role": "Instructor"},
    ],
    "resources": [
        {"kind": "site", "label": "Course home", "href": "../../index.html"},
        {"kind": "github",
         "label": "ai-agentic-demo — empat kasus multi-agent, dengan tabel biayanya",
         "href": "https://github.com/situkangsayur/ai-agentic-demo"},
        {"kind": "book",
         "label": f"{B['authors']}, {B['title']} ({B['publisher']}, {B['edition']})",
         "href": B["site"]},
    ],
    "objectives": [
        "**Menerapkan tiga pertanyaan** yang memutuskan sebuah pekerjaan "
        "pantas dipecah jadi beberapa agen.",
        "**Menghitung biaya memecah**, dan menyebutkan variabel yang "
        "sebenarnya menentukannya.",
        "**Menyebutkan tiga pola orkestrasi** dan bentuk kegagalan khas "
        "masing-masing.",
        "**Menjelaskan apa yang hilang di tiap serah-terima**, dan cara "
        "membatasinya.",
        "**Membedakan protokol ke dalam dari protokol menyilang**, dan "
        "pertanyaan kepercayaan yang muncul pada yang kedua.",
        "**Menelusuri kegagalan pada sistem banyak agen** dengan jejak per "
        "agen.",
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "Kapan memecah",
         "lead": "Tiga pertanyaan, dan bagan organisasi bukan salah satunya."},

        {
            "type": "slide",
            "kicker": "Memutuskan",
            "title": "Tiga bentuk yang membuat pemecahan masuk akal",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔀", "h": "Benar-benar sejajar",
                     "p": "Sub-tugas yang tidak saling membutuhkan hasil. Menilai lima "
                          "pemasok, meringkas dua puluh dokumen. Ini satu-satunya "
                          "pemecahan yang tidak perlu dibela.",
                     "style": "good"},
                    {"ico": "🔒", "h": "Batas izin",
                     "p": "Satu agen boleh membaca data sensitif, satu lagi boleh menulis, "
                          "dan tak satu pun boleh keduanya. Pemisahannya **keamanan**, "
                          "bukan efisiensi.",
                     "style": "good"},
                    {"ico": "🧰", "h": "Kumpulan alat yang tak berhubungan",
                     "p": "Kalau satu daftar alat sudah terlalu besar dan terbelah rapi "
                          "jadi dua yang tak saling pakai.",
                     "style": "good"},
                ]},
                {"t": "p", "md": "Yang **tidak** ada di daftar ini: meniru struktur tim "
                                 "manusia. \\u201cPeneliti, penulis, kritikus\\u201d rapi di "
                                 "papan tulis dan tidak menjawab satu pun dari tiga "
                                 "pertanyaan di atas."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memutuskan",
            "title": "Uji yang paling cepat: apakah mereka butuh konteks yang sama?",
            "blocks": [
                {"t": "p", "md": "Kalau dua \\u201cagen\\u201d membutuhkan sebagian besar "
                                 "konteks yang sama untuk bekerja, memecahnya berarti "
                                 "**mengirim konteks itu dua kali** dan kehilangan sebagian "
                                 "di antaranya."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Tanda pemecahan yang salah**"},
                     {"t": "bullets", "items": [
                         "Serah-terimanya hampir sepanjang percakapannya",
                         "Agen kedua sering meminta hal yang sudah diketahui agen pertama",
                         "Keduanya memakai daftar alat yang sama",
                     ]}],
                    [{"t": "p", "md": "**Tanda pemecahan yang benar**"},
                     {"t": "bullets", "items": [
                         "Serah-terimanya pendek dan bentuknya tetap",
                         "Daftar alatnya berbeda",
                         "Salah satunya bisa berjalan tanpa yang lain",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Uji satu kalimat: **kalau serah-terimanya harus panjang supaya "
                       "agen berikutnya bisa bekerja, keduanya sebenarnya satu agen** yang "
                       "sedang dipaksa berbicara lewat surat."},
            ],
        },

        {"type": "section", "num": "02", "title": "Harganya, dihitung",
         "lead": "Dan jawabannya bukan yang saya duga sebelum menghitungnya."},

        {
            "type": "slide",
            "kicker": "Biaya",
            "title": "Dugaan yang wajar, dan hitungan yang membantahnya",
            "blocks": [
                split_cost("agents08-splitcost",
                           cap="Satu agen lawan tiga agen yang membaginya, dihitung. "
                               "Langkahi menurut ukuran serah-terima.",
                           note="Dibuat sesudah penulisnya menduga sebaliknya. Tagihan "
                                "tumbuh kuadrat terhadap panjang percakapan, jadi memecah "
                                "satu percakapan panjang jadi tiga yang pendek memecah "
                                "kuadratnya."),
                {"t": "p", "md": "\\u201cMemecah pasti lebih mahal, karena ada biaya "
                                 "koordinasi\\u201d — masuk akal, dan **salah** untuk "
                                 "serah-terima yang kecil. Dengan serah-terima 600 token, "
                                 "tiga agen justru lebih murah di semua panjang tugas."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Biaya",
            "title": "Variabel yang menentukan, dan yang tidak diukur siapa pun",
            "blocks": [
                {"t": "p", "md": "Yang menentukan bukan jumlah agennya, melainkan "
                                 "**ukuran serah-terimanya**. Serah-terima kecil memecah "
                                 "kuadrat dan menghemat; serah-terima besar dibawa ke "
                                 "setiap agen sesudahnya dan membengkak."},
                {"t": "table",
                 "head": ["Serah-terima", "6 langkah", "12 langkah", "Artinya"],
                 "widths": [24, 20, 20, 36],
                 "rows": [
                     ["600 token", "0,93×", "0,81×", "Memecah menghemat, makin panjang "
                      "makin hemat"],
                     ["1 500 token", "1,07×", "0,92×", "Bergantung panjang tugasnya"],
                     ["3 000 token", "1,31×", "1,11×", "Memecah mahal — dan inilah yang "
                      "biasanya terjadi"],
                 ]},
                {"t": "band",
                 "md": "Baris ketiga yang paling sering nyata, sebab serah-terima cenderung "
                       "membengkak: setiap kali agen berikutnya kekurangan informasi, orang "
                       "menambahkan sesuatu ke ringkasannya — ==dan tidak pernah "
                       "mengurangi=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Biaya",
            "title": "Yang benar-benar mahal bukan tokennya",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📉", "h": "Informasi yang hilang di serah-terima",
                     "p": "Ini kerugian yang sesungguhnya, dan ia tidak muncul di tagihan "
                          "mana pun. Bab 4 sudah menghitung bentuknya: peringkasan "
                          "kehilangan angka dan pengecualian lebih dulu.",
                     "style": "bad"},
                    {"ico": "🔍", "h": "Sulit ditelusuri",
                     "p": "Satu jejak jadi tiga jejak, dan pertanyaan \\u201cdi mana "
                          "salahnya\\u201d butuh membaca ketiganya beserta "
                          "sambungannya.",
                     "style": "bad"},
                    {"ico": "⏱", "h": "Waktu dinding bertambah",
                     "p": "Kecuali kalau agennya benar-benar berjalan sejajar — dan "
                          "sebagian besar pemecahan tidak."},
                    {"ico": "🧩", "h": "Lebih banyak yang bisa gagal",
                     "p": "Tiga gelung, tiga anggaran, tiga cara berhenti di tempat yang "
                          "salah."},
                ]},
                {"t": "p", "md": "Karena itu argumen melawan pemecahan yang berlebihan "
                                 "tetap berlaku — hanya saja **alasannya bukan biaya "
                                 "token**, dan menyebut alasan yang salah membuat "
                                 "perdebatannya tidak selesai."},
            ],
        },

        {"type": "section", "num": "03", "title": "Pola orkestrasi",
         "lead": "Tiga bentuk, tiga cara gagal."},

        {
            "type": "slide",
            "kicker": "Pola",
            "title": "Tiga bentuk yang mencakup hampir semua sistem nyata",
            "blocks": [
                {"t": "mmd", "id": "agents08-patterns", "src": MMD_PATTERNS,
                 "cap": "Penyelia, berantai, dan kelompok. Yang ketiga paling menarik "
                        "dibaca dan paling jarang pantas dipakai di produksi: tanpa "
                        "pemilik keputusan, tidak ada yang bertanggung jawab "
                        "menghentikannya."},
                {"t": "table",
                 "head": ["Pola", "Cocok untuk", "Kegagalan khasnya"],
                 "widths": [20, 40, 40],
                 "rows": [
                     ["Penyelia", "Sub-tugas sejajar dengan satu pemilik hasil",
                      "Penyelia jadi leher botol dan konteksnya membengkak"],
                     ["Berantai", "Tahapan yang urutannya tetap",
                      "Kesalahan di tahap awal dibangun oleh semua tahap sesudahnya"],
                     ["Kelompok", "Diskusi terbuka tanpa pemilik jelas",
                      "Tidak ada yang menghentikannya; biaya sulit diramalkan"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pola",
            "title": "Penyelia adalah kode, bukan agen — kalau bisa",
            "blocks": [
                {"t": "p", "md": "Pertanyaan yang jarang ditanyakan: apakah penyelianya "
                                 "perlu berupa model sama sekali? Kalau urutan dan "
                                 "syaratnya sudah diketahui, penyelia terbaik adalah "
                                 "**fungsi biasa**."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Penyelia berupa kode**"},
                     {"t": "bullets", "items": [
                         "Deterministik dan gratis",
                         "Bisa diuji seperti kode biasa",
                         "Tidak bisa dibujuk",
                     ]}],
                    [{"t": "p", "md": "**Penyelia berupa model**"},
                     {"t": "bullets", "items": [
                         "Perlu kalau pembagian kerjanya benar-benar bervariasi",
                         "Menambah satu gelung, satu anggaran, satu tempat gagal",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Ini bentuk lain dari uji di Bab 1: **kalau langkahnya sudah "
                       "diketahui, yang Anda butuhkan alur tetap** — dan itu berlaku juga "
                       "untuk lapisan koordinasinya."},
            ],
        },

        {"type": "section", "num": "04", "title": "Serah-terima",
         "lead": "Satu-satunya jalan informasi berpindah, dan tempat sebagian besar hilang."},

        {
            "type": "slide",
            "kicker": "Serah-terima",
            "title": "Agen berikutnya hanya melihat apa yang Anda kirimkan",
            "blocks": [
                {"t": "mmd", "id": "agents08-handoff", "src": MMD_HANDOFF,
                 "cap": "Konteks penuh tinggal di agen pertama; agen kedua melihat ringkasannya."},
                {"t": "p", "md": "Ini pengulangan Bab 4 dalam bentuk yang lebih tajam: apa "
                                 "pun yang tidak masuk ke serah-terima **tidak ada** bagi "
                                 "agen berikutnya — dan tidak ada mekanisme yang "
                                 "memberitahunya bahwa sesuatu hilang."},
                {"t": "band",
                 "md": "Yang paling sering hilang tetap yang sama: **angka, pengecualian, "
                       "dan hal yang belum diputuskan.** Ketiganya justru yang paling "
                       "menentukan keputusan berikutnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Serah-terima",
            "title": "Bentuk serah-terima yang tidak membengkak",
            "blocks": [
                {"t": "mmd", "id": "agents08-hshape", "src": MMD_HANDOFF_SHAPE,
                 "cap": "Empat medan yang tetap — bukan prosa bebas."},
                {"t": "p", "md": "Prosa bebas selalu membengkak, sebab tiap kali agen "
                                 "berikutnya kekurangan sesuatu, orang menambahkan satu "
                                 "kalimat lagi — dan tidak pernah mengurangi. Medan yang "
                                 "tetap membuat pertumbuhan itu **terlihat**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Serah-terima",
            "title": "…dan empat aturan yang menjaganya tetap kecil",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Terstruktur, bukan prosa",
                     "p": "Medan yang tetap: temuan, angka beserta sumbernya, yang masih "
                          "terbuka, dan apa yang diminta dari agen berikutnya."},
                    {"h": "Rujukan, bukan salinan",
                     "p": "Hasil alat yang besar tinggal di tempatnya; kirimkan "
                          "pengenalnya, dan beri agen berikutnya alat untuk membacanya."},
                    {"h": "Batasi ukurannya, dan pantau",
                     "p": "Kalau serah-terima tumbuh dari rilis ke rilis, pemecahannya "
                          "sedang menuju baris ketiga tabel biaya tadi."},
                    {"h": "Tulis apa yang TIDAK diketahui",
                     "p": "Ketidakpastian yang tidak diteruskan berubah jadi kepastian "
                          "palsu: agen kedua yang tidak diberi tahu bahwa sebuah angka "
                          "adalah taksiran akan memperlakukannya sebagai fakta."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Peran",
            "title": "Memberi agen “peran” lebih jarang menolong daripada yang dikira",
            "blocks": [
                {"t": "p", "md": "Pola yang paling banyak disalin: beri tiap agen persona "
                                 "— peneliti, penulis, kritikus — dengan harapan spesialisasi "
                                 "menghasilkan mutu."},
                {"t": "p", "md": "Yang sebenarnya membuat agen berperilaku berbeda bukan "
                                 "kalimat perannya, melainkan **alat yang dimilikinya dan "
                                 "konteks yang dilihatnya**. Dua agen dengan alat dan "
                                 "konteks identik akan berperilaku hampir sama, betapapun "
                                 "berbeda kalimat perannya."},
                {"t": "band",
                 "md": "Uji yang menyelesaikan perdebatan ini dengan cepat: **tukar kalimat "
                       "peran di antara dua agen dan jalankan lagi.** Kalau hasilnya nyaris "
                       "sama, perannya tidak sedang mengerjakan apa pun."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Peran",
            "title": "Spesialisasi yang benar-benar bekerja",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🧰", "h": "Alat yang berbeda",
                     "p": "Agen yang hanya punya alat baca benar-benar tidak bisa menulis. "
                          "Ini spesialisasi yang berupa struktur.",
                     "style": "good"},
                    {"ico": "👁", "h": "Konteks yang berbeda",
                     "p": "Agen yang tidak melihat data pribadi tidak bisa membocorkannya. "
                          "Juga struktur.",
                     "style": "good"},
                    {"ico": "💬", "h": "Kalimat peran saja",
                     "p": "Mempengaruhi gaya, hampir tidak mempengaruhi keputusan — dan "
                          "bisa dibujuk.",
                     "style": "bad"},
                ]},
                {"t": "p", "md": "Pola yang sama muncul di tiap bab modul ini: **yang "
                                 "menentukan perilaku adalah apa yang mungkin dilakukan, "
                                 "bukan apa yang diminta.** Peran adalah permintaan; alat "
                                 "adalah kemungkinan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Komunikasi",
            "title": "Sinkron atau tidak, dan siapa yang menunggu siapa",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Berurutan (sinkron)**"},
                     {"t": "p", "md": "Agen berikutnya menunggu yang sebelumnya. Mudah "
                                      "ditelusuri, mudah dibatasi, dan waktunya menumpuk."},
                     {"t": "p", "md": "Ini yang benar untuk hampir semua alur kerja bisnis."}],
                    [{"t": "p", "md": "**Sejajar (asinkron)**"},
                     {"t": "p", "md": "Beberapa berjalan bersamaan lalu hasilnya disatukan. "
                                      "Menghemat waktu dinding, dan menciptakan pertanyaan "
                                      "urutan."},
                     {"t": "p", "md": "Hanya aman kalau semuanya **alat baca**."}],
                ]},
                {"t": "band",
                 "md": "Aturan yang tidak bisa ditawar: **jangan menjalankan dua alat tulis "
                       "secara sejajar.** Kalau keduanya menyentuh keadaan yang sama, "
                       "hasilnya bergantung pada urutan yang tidak Anda kendalikan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Komunikasi",
            "title": "Keadaan bersama adalah tempat bug berkumpul",
            "blocks": [
                {"t": "p", "md": "Begitu beberapa agen menulis ke tempat yang sama — antrean, "
                                 "papan catatan, ingatan bersama — sistem Anda punya semua "
                                 "masalah yang dikenal sistem terdistribusi, ditambah satu "
                                 "komponen yang tidak deterministik."},
                {"t": "steps", "items": [
                    {"h": "Satu penulis per bagian keadaan",
                     "p": "Kalau dua agen boleh menulis hal yang sama, tentukan siapa yang "
                          "menang — di kode, sebelum kejadian."},
                    {"h": "Tulis dengan kunci idempotensi",
                     "p": "Bab 5 sudah menyebutnya, dan di sini ia jadi wajib, bukan "
                          "dianjurkan."},
                    {"h": "Beri urutan yang bisa dibaca",
                     "p": "Stempel waktu dan pengenal proses di tiap tulisan, atau "
                          "rekonstruksi kejadian jadi mustahil."},
                ]},
                {"t": "band",
                 "md": "Temuan yang tercatat di repo demo persis dari kelas ini: antrean "
                       "yang semula sebuah dict berjalan sempurna sampai peladen alat jadi "
                       "proses sendiri — **kotaknya benar, panahnya benar, dan keadaannya "
                       "ada di tempat yang salah.**"},
            ],
        },

        {"type": "section", "num": "05", "title": "Protokol antar agen",
         "lead": "Ke dalam dan menyilang adalah dua masalah yang berbeda."},

        {
            "type": "slide",
            "kicker": "Protokol",
            "title": "Ke dalam sistem sendiri, dan menyilang ke milik orang lain",
            "blocks": [
                {"t": "mmd", "id": "agents08-a2a", "src": MMD_A2A,
                 "cap": "Dua arah, dua pertanyaan kepercayaan yang berbeda."},
                {"t": "p", "md": "Protokol alat (Bab 5) menjawab \\u201cbagaimana agen "
                                 "memanggil sistem saya\\u201d. Protokol antar agen "
                                 "menjawab \\u201cbagaimana agen saya bicara dengan agen "
                                 "**yang bukan milik saya**\\u201d — dan itu pertanyaan "
                                 "yang berbeda sepenuhnya."},
                {"t": "band",
                 "md": "Perbedaannya bukan teknis melainkan **kepercayaan**: di dalam "
                       "sistem sendiri, Anda tahu apa yang ada di ujung sana. Menyilang, "
                       "yang datang kembali adalah masukan tidak tepercaya dari pihak yang "
                       "tidak Anda kendalikan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Protokol",
            "title": "Pertanyaan yang harus dijawab sebelum agen bicara ke luar",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🪪", "h": "Atas nama siapa?",
                     "p": "Identitas pengguna akhir harus ikut, atau agen di seberang tidak "
                          "bisa memeriksa izin apa pun.",
                     "style": "accent"},
                    {"ico": "📤", "h": "Apa yang boleh keluar?",
                     "p": "Serah-terima ke agen pihak lain adalah **perpindahan data**, "
                          "dengan semua kewajiban yang menyertainya.",
                     "style": "accent"},
                    {"ico": "🛑", "h": "Siapa yang menghentikannya?",
                     "p": "Gelung yang melintasi dua organisasi punya dua anggaran yang "
                          "tidak saling tahu."},
                    {"ico": "🧾", "h": "Siapa yang menyimpan jejaknya?",
                     "p": "Kalau keputusan diambil bersama, buktinya harus bisa disatukan "
                          "kembali."},
                ]},
                {"t": "p", "md": "Untuk bank dan lembaga yang diawasi, keempatnya "
                                 "**mendahului** pertanyaan teknis mana pun tentang format "
                                 "pesan — dan jawaban ketiganya jarang ada di spesifikasi "
                                 "protokol."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Protokol",
            "title": "Menemukan agen lain, dan mempercayainya",
            "blocks": [
                {"t": "p", "md": "Begitu agen boleh bicara ke luar, muncul dua pertanyaan "
                                 "yang tidak ada di dalam sistem sendiri: **bagaimana ia "
                                 "tahu agen lain itu ada**, dan **kenapa ia percaya pada "
                                 "jawabannya.**"},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📇", "h": "Menemukan",
                     "p": "Daftar kemampuan yang bisa dibaca mesin — apa yang bisa "
                          "dikerjakan agen itu, dengan masukan apa. Bentuknya mirip skema "
                          "alat, dan alasannya sama."},
                    {"ico": "🔐", "h": "Mempercayai",
                     "p": "Jawaban dari agen pihak lain adalah **masukan tidak tepercaya**, "
                          "setara hasil pengambilan dokumen. Ia divalidasi, bukan "
                          "diteruskan.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Kesalahan yang mudah dibuat dan mahal: memperlakukan jawaban agen "
                       "mitra sebagai fakta karena ia datang lewat saluran resmi. "
                       "==Saluran yang resmi tidak membuat isinya benar=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Protokol",
            "title": "Batas organisasi mengubah pertanyaannya jadi pertanyaan kontrak",
            "blocks": [
                {"t": "p", "md": "Di dalam satu perusahaan, \u201cagen A memanggil agen "
                                 "B\u201d adalah keputusan arsitektur. Melintasi "
                                 "perusahaan, ia keputusan **hukum** yang kebetulan "
                                 "diwujudkan dengan kode."},
                {"t": "table",
                 "head": ["Pertanyaan", "Di dalam", "Menyilang"],
                 "widths": [28, 34, 38],
                 "rows": [
                     ["Data apa yang keluar?", "Kebijakan internal",
                      "Perjanjian pemrosesan data, dan catatannya"],
                     ["Siapa bertanggung jawab?", "Satu tim",
                      "Harus tertulis sebelum sambungan pertama"],
                     ["Kalau salah?", "Perbaiki dan jalankan lagi",
                      "Siapa yang menanggung kerugiannya?"],
                     ["Jejaknya di mana?", "Satu tempat",
                      "Dua tempat, dan harus bisa disatukan"],
                 ]},
                {"t": "band",
                 "md": "Untuk lembaga yang diawasi, keempat baris kanan ini **mendahului** "
                       "pilihan protokol — dan tidak satu pun dijawab oleh spesifikasi "
                       "teknis mana pun."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Simulasi",
            "title": "Perilaku yang muncul, dan cara membacanya dengan benar",
            "blocks": [
                {"t": "p", "md": "Sekelompok agen dengan aturan sederhana bisa menghasilkan "
                                 "pola yang tidak diprogramkan siapa pun — pembagian kerja, "
                                 "pengulangan, bahkan sesuatu yang terlihat seperti "
                                 "kesepakatan."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Kesimpulan yang sah**"},
                     {"t": "p", "md": "Aturan yang saya beri menghasilkan pola ini pada "
                                      "sistem ini. Itu temuan tentang **rancangan saya**."}],
                    [{"t": "p", "md": "**Kesimpulan yang tidak sah**"},
                     {"t": "p", "md": "Pola ini akan muncul pada manusia, atau pada sistem "
                                      "lain, atau berarti agennya \u201cmemahami\u201d "
                                      "sesuatu."}],
                ]},
                {"t": "band",
                 "md": "Perbedaan keduanya bukan kehati-hatian akademis. Sistem yang "
                       "dibangun di atas kesimpulan kolom kanan akan **gagal justru pada "
                       "kasus yang paling penting**, sebab dasarnya tidak pernah ada."},
            ],
        },

        {"type": "section", "num": "06", "title": "Simulasi dan riset",
         "lead": "Arah yang menarik, dan garis yang memisahkannya dari produksi."},

        {
            "type": "slide",
            "kicker": "Simulasi",
            "title": "Banyak agen sebagai alat penelitian, bukan sebagai produk",
            "blocks": [
                {"t": "p", "md": "Sebagian penggunaan paling menarik dari sistem banyak "
                                 "agen bukan menyelesaikan tugas, melainkan **mensimulasikan "
                                 "perilaku**: sekelompok agen dengan tujuan berbeda "
                                 "dijalankan bersama, lalu polanya diamati."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Yang berguna dari sana**"},
                     {"t": "bullets", "items": [
                         "Menguji rancangan pasar atau kebijakan sebelum diterapkan",
                         "Membangkitkan kasus uji yang tidak terpikir",
                         "Melihat perilaku yang muncul dari aturan sederhana",
                     ]}],
                    [{"t": "p", "md": "**Yang tidak boleh disimpulkan**"},
                     {"t": "bullets", "items": [
                         "Bahwa manusia akan berperilaku begitu",
                         "Bahwa hasilnya bisa dipakai sebagai bukti",
                         "Bahwa \\u201cagen sepakat\\u201d berarti sesuatu itu benar",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Kesepakatan antar agen yang dibangun dari model yang sama adalah "
                       "**kesepakatan antara satu model dan dirinya sendiri**. Bab 3 sudah "
                       "menyebut bentuk kekeliruan yang sama pada suara terbanyak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Riset",
            "title": "Agen riset mendalam: bentuk yang paling banyak dipakai orang",
            "blocks": [
                {"t": "p", "md": "Satu penerapan banyak agen yang benar-benar berguna dan "
                                 "sudah dipakai luas: memecah satu pertanyaan riset jadi "
                                 "beberapa pencarian yang berjalan **sejajar**, lalu "
                                 "menyatukan hasilnya."},
                {"t": "p", "md": "Perhatikan bahwa ini persis bentuk pertama di daftar "
                                 "\\u201ckapan memecah\\u201d: sub-tugas yang benar-benar "
                                 "tidak saling membutuhkan. Ia berhasil karena alasan yang "
                                 "bisa disebut, bukan karena banyak agen terdengar hebat."},
                {"t": "band",
                 "md": "Dan syarat mutunya sama seperti bab 4: **tiap temuan membawa "
                       "sumbernya.** Ringkasan riset tanpa kutipan yang bisa diperiksa "
                       "adalah prosa yang meyakinkan, bukan riset."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Riset",
            "title": "Model teori pikiran, dan kenapa hati-hati membacanya",
            "blocks": [
                {"t": "p", "md": "Sebagian penelitian menguji apakah agen bisa "
                                 "memperhitungkan **apa yang diketahui agen lain** — "
                                 "informasi yang dimiliki pihak lain berbeda dari yang "
                                 "dimilikinya sendiri."},
                {"t": "p", "md": "Ini berguna secara teknis: agen yang menyusun serah-terima "
                                 "harus memperkirakan apa yang belum diketahui penerimanya. "
                                 "Itu masalah rekayasa yang nyata, dan bisa diperbaiki "
                                 "dengan bentuk pesan yang tetap."},
                {"t": "band",
                 "md": "Yang perlu hati-hati adalah bahasanya. Sistem yang lulus uji "
                       "semacam itu **memodelkan informasi**, dan menyebutnya "
                       "\u201cmemahami orang lain\u201d menggeser harapan pemakainya ke "
                       "tempat yang tidak didukung apa pun."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Kerangka kerja",
            "title": "Memilih kerangka kerja, dan pertanyaan yang lebih penting",
            "blocks": [
                {"t": "p", "md": "Ada banyak kerangka kerja untuk merangkai beberapa agen, "
                                 "dan pilihannya jauh kurang menentukan daripada yang "
                                 "diperdebatkan orang."},
                {"t": "table",
                 "head": ["Yang biasanya ditanyakan", "Yang lebih menentukan", "Kenapa"],
                 "widths": [30, 34, 36],
                 "rows": [
                     ["Kerangka kerja mana?", "Bentuk serah-terimanya",
                      "Menentukan biaya dan mutu; kerangka kerja tidak"],
                     ["Bagaimana polanya?", "Apakah memang perlu dipecah",
                      "Pola terbaik untuk pemecahan yang salah tetap salah"],
                     ["Bisa asinkron?", "Apakah ada alat tulis di dalamnya",
                      "Sejajar aman untuk baca, berbahaya untuk tulis"],
                     ["Ada UI-nya?", "Apakah jejaknya per agen",
                      "Tanpa itu, tidak ada yang bisa ditelusuri"],
                 ]},
                {"t": "band",
                 "md": "Dan satu sifat yang pantas diperiksa pada kerangka kerja mana pun: "
                       "**bisakah Anda melihat konteks persis yang dikirim ke model di tiap "
                       "giliran?** Kalau tidak, Anda tidak bisa memperbaiki hal yang paling "
                       "sering perlu diperbaiki."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Menguji",
            "title": "Menguji sistem banyak agen: uji sambungannya, bukan hanya ujungnya",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔗", "h": "Uji tiap serah-terima sendiri",
                     "p": "Beri agen kedua serah-terima buatan dan periksa apakah ia bisa "
                          "bekerja. Ini uji unit, deterministik, tanpa model.",
                     "style": "good"},
                    {"ico": "🧩", "h": "Uji tiap agen sendiri",
                     "p": "Dengan alat tiruan. Kegagalan jadi bisa diatribusikan sebelum "
                          "sistemnya dirangkai.",
                     "style": "good"},
                    {"ico": "🔁", "h": "Uji ujung-ke-ujung, lebih jarang",
                     "p": "Mahal dan lambat, dan hanya berguna kalau dua uji di atas sudah "
                          "hijau."},
                    {"ico": "🚧", "h": "Uji kegagalan sebagian",
                     "p": "Apa yang terjadi kalau agen kedua gagal? Sistem harus punya "
                          "jawaban, bukan menggantung."},
                ]},
                {"t": "p", "md": "Kartu keempat yang paling sering hilang. Pada satu agen, "
                                 "kegagalan berarti proses berhenti. Pada tiga agen, "
                                 "kegagalan di tengah bisa meninggalkan **pekerjaan "
                                 "setengah jadi yang sudah punya efek.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Menguji",
            "title": "Kegagalan sebagian adalah masalah yang baru muncul di sini",
            "blocks": [
                {"t": "p", "md": "Satu agen yang berhenti di tengah biasanya belum "
                                 "melakukan apa-apa yang permanen. Tiga agen berantai bisa "
                                 "berhenti **sesudah** agen pertama menulis sesuatu."},
                {"t": "steps", "items": [
                    {"h": "Tunda semua tulisan sampai akhir, kalau bisa",
                     "p": "Kumpulkan niat, lakukan di satu titik. Ini menghapus seluruh "
                          "kelas masalah."},
                    {"h": "Kalau tidak bisa, sediakan pembatalan",
                     "p": "Dan ujilah pembatalannya — jalur yang tidak pernah diuji adalah "
                          "jalur yang tidak berfungsi."},
                    {"h": "Catat sampai mana yang sudah terjadi",
                     "p": "Supaya manusia yang menyelesaikan tahu harus mulai dari mana."},
                ]},
                {"t": "band",
                 "md": "Ini alasan lain kenapa demo kredit menaruh **satu** alat tulis di "
                       "ujung: pekerjaan setengah jadi yang punya efek adalah bentuk "
                       "kegagalan yang paling mahal dipulihkan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tata kelola",
            "title": "Anggaran harus ada di tingkat sistem, bukan per agen",
            "blocks": [
                {"t": "p", "md": "Tiga agen dengan anggaran delapan langkah masing-masing "
                                 "adalah sistem dengan anggaran dua puluh empat langkah — "
                                 "dan hampir tidak ada yang menuliskannya seperti itu."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎚", "h": "Anggaran menyeluruh",
                     "p": "Batas langkah, token, biaya, dan waktu untuk **seluruh proses**, "
                          "dibagikan ke agen-agennya.",
                     "style": "accent"},
                    {"ico": "🛑", "h": "Satu tombol berhenti",
                     "p": "Menghentikan proses harus menghentikan semua agennya, termasuk "
                          "yang sedang berjalan sejajar.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Tanpa keduanya, batas yang Anda kira sudah dipasang sebenarnya "
                       "**dikalikan jumlah agen** — dan itu ditemukan pada tagihan, bukan "
                       "pada rancangan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Riset",
            "title": "Menyatukan temuan dari beberapa pencarian",
            "blocks": [
                {"t": "p", "md": "Bagian tersulit dari agen riset bukan mencarinya, "
                                 "melainkan **menyatukan** hasilnya: beberapa temuan yang "
                                 "sebagian tumpang tindih, sebagian bertentangan, dan "
                                 "sebagian dari sumber yang jauh lebih lemah daripada "
                                 "lainnya."},
                {"t": "steps", "items": [
                    {"h": "Bawa sumbernya sampai akhir",
                     "p": "Temuan tanpa asal-usul tidak bisa ditimbang, dan tidak bisa "
                          "diperiksa pembaca."},
                    {"h": "Sebutkan pertentangan, jangan diratakan",
                     "p": "Dua sumber yang berbeda kesimpulan adalah informasi. Ringkasan "
                          "yang memilih salah satunya diam-diam membuang informasi itu."},
                    {"h": "Bedakan tidak ditemukan dari tidak ada",
                     "p": "\u201cTidak ada hasil\u201d sering berarti kata pencariannya "
                          "yang kurang tepat — dan itu kesimpulan yang sangat berbeda."},
                ]},
                {"t": "band",
                 "md": "Langkah kedua yang membedakan ringkasan riset yang berguna dari "
                       "prosa yang meyakinkan: **yang berguna menyebutkan di mana "
                       "sumbernya tidak sepakat.**"},
            ],
        },

        {"type": "section", "num": "07", "title": "Menjalankannya",
         "lead": "Menelusuri kegagalan, dan angka yang berubah artinya."},

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Menelusuri kegagalan pada tiga agen",
            "blocks": [
                {"t": "mmd", "id": "agents08-debug", "src": MMD_DEBUG,
                 "cap": "Dua pertanyaan yang menyempitkan masalah — kalau jejaknya ada per agen."},
                {"t": "p", "md": "Pada satu agen, jejaknya satu berkas dan urutannya jelas. "
                                 "Pada tiga agen, pertanyaan pertama selalu sama: **agen "
                                 "mana yang terakhir punya informasi yang benar?** Kalau "
                                 "informasinya benar di agen 1 dan salah di agen 2, "
                                 "serah-terimanya yang bermasalah."},
                {"t": "band",
                 "md": "Karena itu jejak per agen **plus isi tiap serah-terima** bukan "
                       "kemewahan pada sistem banyak agen — tanpa keduanya, satu-satunya "
                       "cara menelusuri adalah menjalankan ulang dan menebak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Angka yang berubah artinya begitu ada lebih dari satu agen",
            "blocks": [
                {"t": "table",
                 "head": ["Angka", "Pada satu agen", "Pada banyak agen"],
                 "widths": [24, 36, 40],
                 "rows": [
                     ["Giliran per tugas", "Panjang penalaran",
                      "Harus dipecah per agen, atau tidak berarti apa-apa"],
                     ["Biaya per tugas", "Langsung",
                      "Jumlahkan semuanya, termasuk penyelia"],
                     ["Laju berhasil", "Satu angka",
                      "Bisa tinggi di tiap agen dan rendah untuk sistemnya — "
                      "0,9³ = 0,73"],
                     ["Waktu dinding", "Jumlah langkah",
                      "Bergantung apakah benar-benar sejajar"],
                 ]},
                {"t": "band",
                 "md": "Baris ketiga yang paling sering mengejutkan: **tiga agen yang "
                       "masing-masing berhasil 90% menghasilkan sistem yang berhasil "
                       "73%.** Bab 7 menghitung bentuk yang sama dengan nama pass^k."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Urutan yang menghemat perdebatan",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Mulai dengan satu agen, selalu",
                     "p": "Sampai ia benar-benar tidak cukup, dan sampai jejaknya "
                          "menunjukkan **kenapa**."},
                    {"h": "Kalau memecah, mulai dari batas izin",
                     "p": "Pemecahan yang alasannya keamanan tidak perlu dibela dengan "
                          "angka — ia menghasilkan jaminan yang tidak bisa didapat cara "
                          "lain."},
                    {"h": "Ukur serah-terimanya sejak hari pertama",
                     "p": "Ukurannya, dan apa yang hilang di dalamnya. Ini variabel yang "
                          "menentukan biaya dan mutu sekaligus."},
                    {"h": "Bandingkan dengan satu agen yang punya semua alat",
                     "p": "Di repo demo, `agentdemo compare research_review` melakukan "
                          "persis ini dan mencetak selisih tokennya."},
                ]},
                {"t": "band",
                 "md": "Langkah keempat yang membuat perdebatan selesai: **jalankan "
                       "keduanya dan cetak angkanya.** Pemecahan yang benar akan menang "
                       "pada angka; yang salah akan kalah, dan itu selesai dalam satu sore."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Menggabungkan kembali jadi satu agen",
            "blocks": [
                {"t": "p", "md": "Pemecahan bukan keputusan yang tidak bisa dibatalkan, dan "
                                 "menggabungkan kembali sering merupakan perbaikan terbesar "
                                 "yang tersedia — tetapi jarang dipertimbangkan, sebab ia "
                                 "terasa seperti mundur."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📏", "h": "Tanda sudah waktunya digabung",
                     "p": "Serah-terimanya hampir sepanjang percakapannya; agen kedua "
                          "sering meminta ulang; daftar alat keduanya bertumpang tindih."},
                    {"ico": "✅", "h": "Yang biasanya membaik setelah digabung",
                     "p": "Mutu naik (tidak ada yang hilang di serah-terima), penelusuran "
                          "jadi sederhana, dan satu anggaran menggantikan tiga.",
                     "style": "good"},
                ]},
                {"t": "band",
                 "md": "Ukurannya sama seperti waktu memutuskan memecah: **jalankan "
                       "keduanya pada kumpulan uji yang sama dan cetak tiga angkanya.** "
                       "Keputusan yang diambil dengan angka tidak perlu diperdebatkan dua "
                       "kali."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Lima kegagalan khas, dan tandanya",
            "blocks": [
                {"t": "table",
                 "head": ["Kegagalan", "Tandanya", "Perbaikannya"],
                 "widths": [26, 38, 36],
                 "rows": [
                     ["Serah-terima membengkak", "Ukurannya naik tiap rilis",
                      "Bentuk terstruktur dengan medan tetap"],
                     ["Penyelia jadi leher botol", "Konteks penyelia paling besar",
                      "Jadikan penyelianya kode kalau urutannya tetap"],
                     ["Kerja ganda", "Dua agen memanggil alat yang sama",
                      "Hasil dibagikan lewat rujukan, bukan diambil ulang"],
                     ["Tidak ada yang menghentikan", "Proses panjang tanpa pemilik",
                      "Anggaran menyeluruh + satu tombol berhenti"],
                     ["Kesalahan menular", "Agen 1 salah, sisanya membangun di atasnya",
                      "Pemeriksaan di serah-terima, bukan hanya di ujung"],
                 ]},
                {"t": "p", "md": "Kelimanya terlihat pada dua hal yang sama: **jejak per "
                                 "agen dan isi tiap serah-terima.** Kalau keduanya ada, "
                                 "menelusuri sistem banyak agen tidak jauh lebih sulit "
                                 "daripada satu agen."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Apa yang dilaporkan tentang sistem banyak agen",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Laju berhasil SISTEM, bukan per agen",
                     "p": "Tiga agen 90% menghasilkan 73%. Angka per agen terdengar bagus "
                          "dan tidak menjawab pertanyaan siapa pun."},
                    {"h": "Biaya total, termasuk penyelia",
                     "p": "Koordinasi sering tidak masuk hitungan karena tidak terasa "
                          "seperti pekerjaan."},
                    {"h": "Ukuran serah-terima dari waktu ke waktu",
                     "p": "Ini peringatan dini yang paling murah untuk biaya dan mutu "
                          "sekaligus."},
                    {"h": "Perbandingan dengan satu agen",
                     "p": "Pertanyaan pertama yang akan diajukan orang yang membayar, dan "
                          "pantas sudah punya jawabannya."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Yang dipakai di demo, dan alasannya",
            "blocks": [
                {"t": "p", "md": "Repo demo punya empat kasus banyak-agen, dan masing-masing "
                                 "ada untuk **menunjukkan satu hal yang bisa diperiksa** — "
                                 "bukan untuk memperlihatkan bahwa banyak agen itu bagus."},
                {"t": "table",
                 "head": ["Kasus", "Yang ditunjukkannya"],
                 "widths": [30, 70],
                 "rows": [
                     ["`parallel_triage`",
                      "Fan-out ketika sub-tugas benar-benar tidak saling berhubungan — "
                      "satu-satunya pemecahan yang tidak perlu dibela"],
                     ["`research_review`",
                      "Pembagian rapi peneliti/penulis/kritikus, **diukur** terhadap satu "
                      "agen dengan alat yang sama, token dicetak"],
                     ["`cross_permission`",
                      "Pemecahan sebagai batas keamanan: agen penyelidik tidak punya alat "
                      "tulis di daftarnya"],
                     ["`escalation`",
                      "Penyerahan ke manusia: keadaan apa yang ikut, dan bagaimana "
                      "pekerjaannya kembali"],
                 ]},
                {"t": "band",
                 "md": "Baris kedua yang paling banyak mengubah pikiran orang di kelas, "
                       "sebab hasilnya dicetak: **pembagian yang paling rapi di papan tulis "
                       "kalah pada tabel biaya.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Tiga bentuk yang membenarkan pemecahan",
                     "p": "Sejajar sungguhan, batas izin, alat yang tak berhubungan. Bagan "
                          "organisasi bukan salah satunya."},
                    {"h": "Biayanya ditentukan serah-terima, bukan jumlah agen",
                     "p": "Serah-terima 600 token menghemat; 3 000 token membuat mahal. "
                          "Dan serah-terima cenderung membengkak."},
                    {"h": "Yang benar-benar mahal adalah informasi yang hilang",
                     "p": "Ia tidak muncul di tagihan mana pun, dan ia yang membuat "
                          "hasilnya memburuk."},
                    {"h": "0,9 × 0,9 × 0,9 = 0,73",
                     "p": "Tiga agen yang bagus bisa menghasilkan sistem yang tidak."},
                    {"h": "Bandingkan dengan satu agen, dengan angka",
                     "p": "Satu sore kerja, dan perdebatannya selesai."},
                ]},
            ],
            "notes": "Kalau ada satu latihan untuk kelas: minta mereka menyebut pemecahan "
                     "yang sedang mereka rencanakan, lalu tanyakan berapa besar "
                     "serah-terimanya. Yang tidak bisa menjawab biasanya belum perlu "
                     "memecah.",
        },
    ],
}
