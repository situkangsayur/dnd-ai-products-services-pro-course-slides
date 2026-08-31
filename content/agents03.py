# -*- coding: utf-8 -*-
"""Bab 3 — Model penalar, dan kapan penalaran itu layak dibayar.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 3.

Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti hanya
URUTAN BABNYA. Isinya materi ajar sendiri, gambarnya digambar sendiri.

Angka pada gambar `vote_tradeoff` dihitung persis dari sebaran binomial di
generatornya. Asumsi kebebasannya DICETAK di gambar, sebab asumsi itu salah di
dunia nyata dan membuat angkanya jadi batas atas, bukan target.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import vote_tradeoff  # noqa: E402

B = BOOKS["agents"]


MMD_COMPUTE = """
flowchart LR
  subgraph L["Komputasi saat LATIH — sekali, mahal, tetap"]
    direction TB
    D["Data + GPU"] --> W["Bobot"]
  end
  subgraph U["Komputasi saat PAKAI — tiap permintaan, bisa diatur"]
    direction TB
    Q["Pertanyaan"] --> T["Berpikir lebih lama"] --> A["Jawaban"]
  end
  W --> U
"""

MMD_VERIFIER = """
flowchart LR
  M["Model"] -->|"N calon jawaban"| V{"Pemeriksa"}
  V -->|"lolos"| OK["Dipakai"]
  V -->|"gagal semua"| STOP["Menyerah / eskalasi"]
  V -. "yang membuat ini bekerja:<br/>memeriksa lebih mudah<br/>daripada menjawab" .-> M
"""

MMD_BUDGET = """
flowchart TB
  Q["Permintaan masuk"] --> C{"Butuh penalaran?"}
  C -->|"tugas rutin,<br/>alat sudah jelas"| F["Model cepat<br/><small>tanpa penalaran</small>"]
  C -->|"ambigu, banyak<br/>batasan, perlu rencana"| R["Model penalar<br/><small>anggaran berpikir dibatasi</small>"]
  F --> OUT["Jawaban"]
  R --> OUT
"""

MMD_WHERE = """
flowchart LR
  P["Penalaran DI DALAM model<br/><small>token berpikir, satu panggilan</small>"]
  A["Penalaran DI DALAM gelung agen<br/><small>banyak giliran, alat, amatan</small>"]
  P -. "keduanya memecah masalah jadi langkah —<br/>bedanya apakah langkahnya bisa dilihat,<br/>diukur, dan dihentikan" .- A
"""

MMD_FAIL = """
flowchart TB
  S["Penalaran panjang"] --> A["Lebih banyak langkah<br/>untuk salah di salah satunya"]
  S --> B["Lebih yakin pada<br/>jalan yang keliru"]
  S --> C["Lebih mahal dan lambat"]
  A --> D["Jawaban salah yang<br/>terdengar sangat meyakinkan"]
  B --> D
"""


DECK = {
    "id": "agents03",
    "kind": "chapter",
    "number": 3,
    "book": "agents",
    "title": "Model penalar, dan kapan penalaran layak dibayar",
    "subtitle": "Memindahkan komputasi dari waktu latih ke waktu pakai — apa "
                "yang dibelinya, berapa harganya, dan kenapa agen sudah "
                "melakukan sebagian dari itu.",
    "source": book_source(3, "agents"),
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
        "**Membedakan komputasi saat latih dari komputasi saat pakai**, dan "
        "menyebutkan mana yang bisa diatur setelah model dikirim.",
        "**Menghitung apa yang dibeli oleh pengambilan N contoh**, dan "
        "menyebutkan asumsi yang membuat hitungan itu jadi batas atas.",
        "**Menjelaskan kenapa pemeriksa mengalahkan penambahan contoh**, dan "
        "menyebutkan syarat sebuah tugas punya pemeriksa.",
        "**Menyebutkan berapa token yang dibayar tapi tidak terlihat** pada "
        "model penalar, dan akibatnya pada agen berlangkah banyak.",
        "**Memutuskan kapan TIDAK memakai model penalar** di dalam gelung "
        "agen, dengan alasan yang bisa diukur.",
        "**Menyebutkan tiga cara penalaran panjang justru memperburuk** hasil.",
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "Dua tempat menaruh komputasi",
         "lead": "Satu dibayar sekali di depan, satu dibayar tiap permintaan."},

        {
            "type": "slide",
            "kicker": "Pergeseran",
            "title": "Yang berubah bukan modelnya, melainkan kapan usahanya dikeluarkan",
            "blocks": [
                {"t": "mmd", "id": "agents03-compute", "src": MMD_COMPUTE,
                 "cap": "Bobot dibayar sekali; berpikir dibayar tiap kali."},
                {"t": "p", "md": "Selama bertahun-tahun, cara menaikkan kemampuan adalah "
                                 "**membesarkan pelatihannya**: lebih banyak data, lebih "
                                 "banyak parameter, lebih banyak GPU. Hasilnya bobot yang "
                                 "tetap — pintar atau tidak, ia sama saja untuk tiap "
                                 "permintaan."},
                {"t": "band",
                 "md": "Yang berubah: sebagian usaha dipindah ke **saat pemakaian**. Model "
                       "yang sama diberi kesempatan berpikir lebih lama pada soal yang "
                       "lebih sulit — dan itu berarti biayanya jadi ==sesuatu yang Anda "
                       "atur per permintaan==, bukan sesuatu yang sudah tetap."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pergeseran",
            "title": "Kenapa ini kabar baik bagi orang yang membangun sistem",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Komputasi saat latih** adalah keputusan orang lain. "
                                      "Anda menerimanya sebagaimana adanya, dan satu-satunya "
                                      "kendali Anda adalah memilih model."}],
                    [{"t": "p", "md": "**Komputasi saat pakai** adalah keputusan Anda, per "
                                      "permintaan. Soal mudah dijawab murah; soal sulit "
                                      "diberi anggaran lebih besar."}],
                ]},
                {"t": "p", "md": "Ini pola yang sudah dikenal di tempat lain: cache yang "
                                 "murah untuk yang sering, jalur mahal untuk yang jarang. "
                                 "Yang baru adalah **kualitas jawaban** kini ikut jadi "
                                 "sesuatu yang bisa dibeli dengan uang di saat pemakaian."},
                {"t": "band",
                 "md": "Dan kabar buruknya, yang muncul di sisa bab ini: yang dibeli "
                       "**melandai**, sedangkan yang dibayar tidak."},
            ],
        },

        {"type": "section", "num": "02", "title": "Cara termurah dulu",
         "lead": "Sebelum membayar model penalar, ada yang bisa dicoba dengan harga nol."},

        {
            "type": "slide",
            "kicker": "Prompt",
            "title": "Meminta langkahnya adalah pengungkit yang paling murah",
            "blocks": [
                {"t": "p", "md": "Meminta model menuliskan langkah-langkahnya sebelum "
                                 "menjawab menaikkan ketepatan pada soal berlangkah banyak — "
                                 "dan harganya hanya token keluaran tambahan."},
                {"t": "p", "md": "Alasannya masuk akal begitu diingat bahwa model "
                                 "menghasilkan satu token dari semua token sebelumnya: "
                                 "**langkah yang ditulis menjadi bagian dari konteks untuk "
                                 "langkah berikutnya.** Ia bukan penjelasan setelah "
                                 "keputusan — ia bagian dari perhitungannya."},
                {"t": "band",
                 "md": "Karena itu penjelasan yang diminta **sesudah** jawaban keluar "
                       "adalah hal yang berbeda sama sekali: itu karangan tentang keputusan "
                       "yang sudah diambil, dan ==tidak boleh dibaca sebagai alasan "
                       "sebenarnya=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Prompt",
            "title": "Di dalam agen, sebagian besar ini sudah terjadi",
            "blocks": [
                {"t": "mmd", "id": "agents03-where", "src": MMD_WHERE,
                 "cap": "Dua tempat penalaran bisa terjadi, dan hanya satu yang bisa dilihat."},
                {"t": "p", "md": "Gelung agen **sudah** memecah masalah jadi langkah. "
                                 "Bedanya dengan penalaran di dalam model bukan ada atau "
                                 "tidaknya langkah, melainkan **apakah langkah itu bisa "
                                 "dilihat, diukur, dan dihentikan** — dan akibatnya, "
                                 "menaruh model penalar di dalam gelung kadang berarti "
                                 "membayar dua kali untuk hal yang sama."},
            ],
        },

        {"type": "section", "num": "03", "title": "Bertanya berkali-kali",
         "lead": "Dan berapa persisnya itu membeli sesuatu."},

        {
            "type": "slide",
            "kicker": "Banyak contoh",
            "title": "Ambil N jawaban, pakai yang terbanyak",
            "blocks": [
                {"t": "p", "md": "Kalau satu jawaban bisa salah, ambil beberapa dan pilih "
                                 "yang paling sering muncul. Gagasannya tua dan masuk akal: "
                                 "kesalahan acak cenderung berbeda-beda, jawaban benar "
                                 "cenderung sama."},
                {"t": "p", "md": "Yang jarang dihitung orang adalah **berapa banyak** itu "
                                 "membeli. Untungnya itu bukan soal selera — kalau tiap "
                                 "contoh benar dengan peluang *p* dan contohnya saling "
                                 "bebas, peluang suara terbanyak benar adalah jumlah suku "
                                 "binomial di atas N/2. Bisa dihitung persis."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Banyak contoh",
            "title": "Dihitung, bukan ditaksir — dan asumsinya dicetak",
            "blocks": [
                vote_tradeoff("agents03-vote",
                              cap="Peluang benar setelah suara terbanyak dari N contoh, "
                                  "dihitung dari sebaran binomial. Langkahi: satu contoh, "
                                  "sampai lima, lalu semuanya.",
                              note="Asumsi kebebasan itu yang mengerjakan seluruh "
                                   "pekerjaannya, dan ia salah di dunia nyata — contoh dari "
                                   "model yang sama pada prompt yang sama berkorelasi. "
                                   "Jadi kurva ini batas atas."),
                {"t": "p", "md": "Dari 1 ke 5 contoh: **+8,3 poin** dengan biaya 5×. Dari 5 "
                                 "ke 21: **+14,3 poin** dengan biaya 21×. Kenaikannya "
                                 "melandai, biayanya tidak — dan karena contohnya "
                                 "berkorelasi, yang benar-benar didapat selalu lebih kecil "
                                 "dari angka itu."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Banyak contoh",
            "title": "Satu syarat yang membuatnya bisa dipakai sama sekali",
            "blocks": [
                {"t": "p", "md": "Suara terbanyak hanya berarti kalau jawabannya **bisa "
                                 "dibandingkan**. Untuk angka atau label, mudah. Untuk "
                                 "paragraf, dua jawaban benar bisa berbeda kata sepenuhnya "
                                 "dan tidak ada suara yang bisa dihitung."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔢", "h": "Cocok",
                     "p": "Angka, klasifikasi, pilihan alat, keputusan ya/tidak.",
                     "style": "good"},
                    {"ico": "🧩", "h": "Perlu usaha",
                     "p": "Keluaran terstruktur — bandingkan medannya, bukan teksnya."},
                    {"ico": "📝", "h": "Tidak cocok",
                     "p": "Prosa bebas. Suara terbanyak di sini hampir selalu berarti "
                          "membandingkan gaya, bukan kebenaran.",
                     "style": "bad"},
                ]},
                {"t": "band",
                 "md": "Di dalam agen, yang paling sering pantas divoting justru bukan "
                       "jawabannya, melainkan **pilihan alat dan argumennya** — dan itu "
                       "kebetulan hal yang paling mudah dibandingkan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pemeriksa",
            "title": "Pemeriksa mengalahkan penambahan contoh, kalau ada",
            "blocks": [
                {"t": "mmd", "id": "agents03-verifier", "src": MMD_VERIFIER,
                 "cap": "Menghasilkan banyak calon jadi berguna begitu ada yang bisa menolak."},
                {"t": "p", "md": "Suara terbanyak menebak mana yang benar dari **kesepakatan**. "
                                 "Pemeriksa mengetahuinya dari **pengujian**. Kalau tugasnya "
                                 "punya pemeriksa — kode yang dijalankan, hitungan yang "
                                 "dicocokkan, skema yang divalidasi, kebijakan yang "
                                 "diperiksa — maka menghasilkan lima calon dan menolak yang "
                                 "gagal jauh lebih kuat daripada memilih yang paling populer."},
                {"t": "band",
                 "md": "Syaratnya satu, dan itu syarat yang tegas: **memeriksa harus lebih "
                       "mudah daripada menjawab.** Kalau memeriksanya sama sulitnya, Anda "
                       "baru saja menggandakan masalahnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pemeriksa",
            "title": "Apa yang bisa jadi pemeriksa dalam sistem sungguhan",
            "blocks": [
                {"t": "table",
                 "head": ["Pemeriksa", "Menolak apa", "Ongkosnya"],
                 "widths": [26, 44, 30],
                 "rows": [
                     ["Menjalankan kodenya", "Kode yang tidak jalan atau gagal uji",
                      "Sandbox — dan itu bukan hal sepele"],
                     ["Validasi skema", "Argumen alat yang salah bentuk atau tipe",
                      "Hampir nol, dan wajib ada"],
                     ["Hitung ulang dengan kode", "Aritmetika yang dikarang model",
                      "Nol, dan mengejutkan jarang dipakai"],
                     ["Cocokkan dengan hasil alat", "Angka yang tidak ada asal-usulnya",
                      "Rendah — butuh jejak yang rapi"],
                     ["Aturan kebijakan sebagai kode", "Keputusan yang melanggar syarat",
                      "Sedang — tapi harus ada juga untuk audit"],
                 ]},
                {"t": "p", "md": "Perhatikan bahwa empat dari lima **bukan model**. Pemeriksa "
                                 "terbaik biasanya kode biasa, dan itu sebabnya bab ini "
                                 "berakhir pada nasihat yang membosankan: tulis "
                                 "pemeriksanya dulu."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Hukum skala",
            "title": "Kenapa membesarkan pelatihan berhenti jadi jawaban tunggal",
            "blocks": [
                {"t": "p", "md": "Selama satu dekade, hubungannya rapi: lebih banyak data "
                                 "dan parameter menghasilkan model yang lebih baik, dengan "
                                 "cara yang bisa diramalkan. Itu yang membuat perlombaan "
                                 "ukuran masuk akal."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📉", "h": "Hasilnya melandai",
                     "p": "Kenaikan yang sama menuntut lipatan sumber daya yang makin "
                          "besar."},
                    {"ico": "📚", "h": "Datanya terbatas",
                     "p": "Teks berkualitas tinggi bukan sumber daya tak terbatas, dan "
                          "bagian termudahnya sudah dipakai."},
                    {"ico": "💸", "h": "Ongkosnya di depan",
                     "p": "Salah taruhan pada pelatihan berarti berbulan-bulan dan "
                          "biaya besar yang tidak bisa ditarik."},
                ]},
                {"t": "p", "md": "Komputasi saat pakai tidak menggantikan itu — ia menambah "
                                 "**sumbu kedua**. Dan sumbu kedua ini punya sifat yang "
                                 "menarik bagi orang yang membangun produk: ia bisa diatur "
                                 "sesudah semuanya dikirim."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Hukum skala",
            "title": "Dua sumbu, dan yang kedua milik Anda",
            "blocks": [
                {"t": "table",
                 "head": ["", "Komputasi saat latih", "Komputasi saat pakai"],
                 "widths": [22, 39, 39],
                 "rows": [
                     ["Dibayar", "Sekali, di depan", "Tiap permintaan"],
                     ["Diputuskan oleh", "Penyedia model", "**Anda**, per permintaan"],
                     ["Bisa diubah", "Tidak, tanpa melatih ulang", "Ya, dengan satu parameter"],
                     ["Kalau salah", "Berbulan-bulan hilang", "Satu permintaan lebih mahal"],
                     ["Batasnya", "Data dan uang", "Kesabaran pengguna dan tagihan"],
                 ]},
                {"t": "band",
                 "md": "Untuk pembangun agen, baris ketiga yang paling penting: **ini "
                       "satu-satunya tuas kualitas yang Anda pegang sendiri** tanpa "
                       "mengganti model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Melatihnya",
            "title": "Cara pertama: tunjukkan contoh penalaran yang bagus",
            "blocks": [
                {"t": "p", "md": "Kalau model dilatih pada kumpulan contoh yang jawabannya "
                                 "disertai langkah-langkah, ia belajar menghasilkan langkah "
                                 "itu sendiri — tanpa diminta lewat prompt."},
                {"t": "p", "md": "Yang mengejutkan dari arah penelitian ini adalah **berapa "
                                 "sedikit contoh yang dibutuhkan**. Ribuan contoh penalaran "
                                 "yang dipilih dengan cermat bisa mengalahkan ratusan ribu "
                                 "contoh yang dikumpulkan asal — kualitas dan keberagaman "
                                 "mengalahkan jumlah."},
                {"t": "band",
                 "md": "Pelajaran yang berlaku juga untuk kumpulan uji Anda sendiri: "
                       "==dua puluh kasus yang dipilih baik lebih berguna daripada dua ribu "
                       "kasus yang dikumpulkan sembarangan=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Melatihnya",
            "title": "Cara kedua: beri imbalan pada jawaban yang benar, bukan pada caranya",
            "blocks": [
                {"t": "p", "md": "Pendekatan yang lebih mengejutkan: jangan tunjukkan cara "
                                 "menalar sama sekali. Beri saja soal yang jawabannya bisa "
                                 "**diperiksa otomatis**, biarkan model mencoba, dan beri "
                                 "imbalan ketika jawabannya benar."},
                {"t": "steps", "items": [
                    {"h": "Yang membuatnya bekerja adalah pemeriksanya",
                     "p": "Matematika dan pemrograman punya jawaban yang bisa dicek mesin. "
                          "Di situlah metode ini paling berhasil, dan bukan kebetulan."},
                    {"h": "Perilaku memeriksa ulang muncul sendiri",
                     "p": "Model mulai mengoreksi dirinya di tengah jalan tanpa pernah "
                          "diberi contoh cara melakukannya — sebab itu menaikkan peluang "
                          "jawabannya benar."},
                    {"h": "Panjang penalarannya ikut tumbuh sendiri",
                     "p": "Bukan karena ditargetkan, melainkan karena berpikir lebih lama "
                          "kebetulan berkorelasi dengan benar pada soal-soal itu."},
                ]},
                {"t": "band",
                 "md": "Batasnya jadi jelas begitu polanya dilihat: metode ini **butuh "
                       "domain yang bisa diperiksa mesin.** Untuk tugas yang benarnya "
                       "subjektif, tidak ada imbalan yang bisa dihitung."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Melatihnya",
            "title": "Kenapa dua tahap, bukan satu",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Imbalan saja** menghasilkan penalaran yang efektif "
                                      "tetapi sering kacau dibaca: berpindah bahasa di "
                                      "tengah, mengulang, atau menulis dalam bentuk yang "
                                      "tidak berguna bagi manusia."},
                     {"t": "p", "md": "Wajar — tidak ada dalam imbalannya yang meminta "
                                      "supaya bisa dibaca."}],
                    [{"t": "p", "md": "**Contoh dulu, baru imbalan** menghasilkan penalaran "
                                      "yang rapi dan tetap efektif: contoh mengajarkan "
                                      "bentuknya, imbalan mengajarkan mana yang berhasil."},
                     {"t": "p", "md": "Ini pola yang sama dengan bab 2: SFT mengajarkan "
                                      "bentuk, RL mengajarkan pilihan."}],
                ]},
                {"t": "band",
                 "md": "Bagi pemakai, akibatnya praktis: **jejak penalaran yang bisa dibaca "
                       "bukan sifat alami model** — ia hasil tahap pelatihan yang sengaja "
                       "ditambahkan. Jangan menganggapnya jaminan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Melatihnya",
            "title": "Memaksa berpikir lebih lama, dari luar",
            "blocks": [
                {"t": "p", "md": "Ada trik yang sangat sederhana dan bekerja mengejutkan "
                                 "baik: ketika model hendak berhenti berpikir, **jangan "
                                 "biarkan** — sisipkan penanda yang membuatnya melanjutkan, "
                                 "beberapa kali."},
                {"t": "p", "md": "Kebalikannya juga bekerja: memotong penalaran pada batas "
                                 "token tertentu dan memaksa jawaban keluar. Dua-duanya "
                                 "menjadikan panjang berpikir sebagai **tombol yang bisa "
                                 "diputar saat pemakaian**, bukan sifat model."},
                {"t": "band",
                 "md": "Inilah bentuk paling murni dari gagasan bab ini: satu bobot yang "
                       "sama, kualitas yang berbeda-beda, ditentukan oleh berapa banyak "
                       "komputasi yang Anda izinkan per permintaan."},
            ],
        },

        {"type": "section", "num": "04b", "title": "Arah yang sedang dikerjakan",
         "lead": "Tiga hal yang belum selesai, dan pantas dilihat sebelum bertaruh padanya."},

        {
            "type": "slide",
            "kicker": "Arah riset",
            "title": "Penalaran yang lebih hemat",
            "blocks": [
                {"t": "p", "md": "Masalah paling nyata dari model penalar adalah **borosnya**, "
                                 "dan sebagian besarnya terbuang: model sering terus berpikir "
                                 "pada soal yang sudah jelas jawabannya sejak awal."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🎚", "h": "Berhenti kalau sudah yakin",
                     "p": "Menghentikan penalaran begitu jawabannya stabil, bukan setelah "
                          "anggaran habis."},
                    {"ico": "🔀", "h": "Arahkan per permintaan",
                     "p": "Soal mudah ke model cepat, soal sulit ke model penalar — "
                          "keputusan dibuat sebelum menjawab."},
                    {"ico": "🗜", "h": "Penalaran yang lebih padat",
                     "p": "Melatih model menalar dengan token lebih sedikit untuk hasil "
                          "yang sama."},
                ]},
                {"t": "p", "md": "Yang kedua bisa Anda lakukan **hari ini**, tanpa menunggu "
                                 "penelitian: sebuah pengklasifikasi kecil di depan gelung "
                                 "yang memilih model mana yang dipakai. Itu rekayasa biasa."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Arah riset",
            "title": "Menalar tanpa menuliskannya",
            "blocks": [
                {"t": "p", "md": "Menulis penalaran dalam bentuk kata memaksa model "
                                 "menyalurkan pikirannya lewat saluran yang sempit: satu "
                                 "token pada satu waktu, dan hanya yang bisa diucapkan."},
                {"t": "p", "md": "Arah penelitian yang sedang dikerjakan membiarkan model "
                                 "menalar di dalam **ruang vektornya sendiri** dan hanya "
                                 "mengeluarkan hasil akhirnya. Lebih hemat, dan mungkin "
                                 "lebih kuat."},
                {"t": "band",
                 "md": "Tetapi perhatikan harganya bagi orang yang membangun sistem "
                       "bertanggung jawab: **penalaran yang tidak berbentuk kata adalah "
                       "penalaran yang tidak bisa dibaca, diaudit, atau dibantah.** Untuk "
                       "keputusan yang diawasi regulator, itu bukan pertukaran yang netral."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Arah riset",
            "title": "Menalar atas gambar, bukan hanya atas teks",
            "blocks": [
                {"t": "p", "md": "Penalaran berlangkah pada masukan gambar masih jauh lebih "
                                 "lemah daripada pada teks. Model bisa menjelaskan isi "
                                 "sebuah gambar dengan baik, dan tetap gagal pada soal yang "
                                 "menuntut beberapa langkah **di atas** isi itu."},
                {"t": "p", "md": "Ini penting untuk agen yang bekerja di lapangan — membaca "
                                 "faktur, layar, foto dokumen — dan bab 9 kembali ke sana. "
                                 "Untuk sekarang cukup satu kesimpulan praktis."},
                {"t": "band",
                 "md": "Kalau tugasnya menuntut penalaran di atas gambar, **ubah dulu "
                       "gambarnya jadi data terstruktur dengan alat**, lalu nalarkan atas "
                       "datanya. Jangan meminta satu panggilan mengerjakan keduanya."},
            ],
        },

        {"type": "section", "num": "04", "title": "Model yang dilatih untuk menalar",
         "lead": "Dan tagihan yang tidak terlihat di layar."},

        {
            "type": "slide",
            "kicker": "Model penalar",
            "title": "Penalaran yang dilatih, bukan yang diminta",
            "blocks": [
                {"t": "p", "md": "Alih-alih meminta model menuliskan langkahnya lewat "
                                 "prompt, model bisa **dilatih** untuk melakukannya sendiri "
                                 "— diberi imbalan ketika jalur penalaran yang panjang "
                                 "berujung pada jawaban benar."},
                {"t": "p", "md": "Hasilnya model yang, diberi soal sulit, menghabiskan "
                                 "ratusan sampai ribuan token untuk dirinya sendiri sebelum "
                                 "mengeluarkan jawaban. Pada soal matematika, pemrograman, "
                                 "dan perencanaan berlangkah banyak, bedanya nyata."},
                {"t": "band",
                 "md": "Dan satu temuan yang layak diingat karena berlawanan dengan dugaan: "
                       "**perilaku memeriksa ulang dan mengoreksi diri bisa muncul dari "
                       "pelatihan imbalan saja**, tanpa seorang pun menuliskan contoh cara "
                       "memeriksa ulang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Model penalar",
            "title": "Token yang Anda bayar dan tidak pernah Anda lihat",
            "blocks": [
                {"t": "p", "md": "Token penalaran adalah **token keluaran**. Ditagih seperti "
                                 "token keluaran, dihasilkan selambat token keluaran, dan "
                                 "pada banyak penyedia **tidak ditampilkan** kepada Anda."},
                {"t": "table",
                 "head": ["Satu tugas", "Token keluaran", "Yang terlihat"],
                 "widths": [34, 30, 36],
                 "rows": [
                     ["Model biasa", "300", "300 — semuanya"],
                     ["Model penalar", "2 800", "300 — sisanya **89% tak terlihat**"],
                     ["Agen 6 langkah, model biasa", "1 800", "1 800"],
                     ["Agen 6 langkah, model penalar", "**16 800**", "1 800"],
                 ]},
                {"t": "band",
                 "md": "Asumsinya dicetak supaya bisa diganti: 300 token jawaban, 2 500 "
                       "token berpikir per langkah. Yang tidak berubah adalah bentuknya — "
                       "==di dalam gelung agen, biaya penalaran dikalikan jumlah langkah=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Model penalar",
            "title": "Anggaran berpikir adalah tombol, dan pantas dipakai",
            "blocks": [
                {"t": "mmd", "id": "agents03-budget", "src": MMD_BUDGET,
                 "cap": "Tidak semua permintaan pantas mendapat anggaran berpikir yang sama."},
                {"t": "p", "md": "Sebagian besar penyedia model penalar menyediakan cara "
                                 "membatasi berapa banyak token boleh dipakai untuk "
                                 "berpikir. Memakainya bukan penghematan receh: pada agen, "
                                 "ia berlipat dengan jumlah langkah."},
                {"t": "band",
                 "md": "Pola yang paling sering menang di produksi: **model cepat untuk "
                       "memilih alat, model penalar hanya untuk langkah yang benar-benar "
                       "sulit.** Memilih alat jarang butuh penalaran panjang; ia butuh "
                       "kepatuhan pada skema."},
            ],
        },

        {"type": "section", "num": "05", "title": "Ketika penalaran memperburuk",
         "lead": "Tiga cara, dan semuanya terlihat seperti keberhasilan sampai diperiksa."},

        {
            "type": "slide",
            "kicker": "Batas",
            "title": "Berpikir lebih lama bukan berarti lebih benar",
            "blocks": [
                {"t": "mmd", "id": "agents03-fail", "src": MMD_FAIL,
                 "cap": "Tiga jalan dari penalaran panjang menuju kesalahan yang meyakinkan."},
                {"t": "p", "md": "Penalaran panjang menambah **jumlah langkah yang bisa "
                                 "salah**. Satu kekeliruan di langkah ketiga akan dibangun "
                                 "di atasnya oleh sepuluh langkah berikutnya, dan hasil "
                                 "akhirnya terdengar jauh lebih meyakinkan daripada tebakan "
                                 "langsung — sebab ia datang dengan alasan."},
                {"t": "band",
                 "md": "Ini alasan lain kenapa penilaian harus melihat **jejaknya**: "
                       "jawaban yang benar dari penalaran yang keliru dan jawaban yang "
                       "benar dari penalaran yang benar terlihat sama di kolom hasil."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Batas",
            "title": "Tugas yang justru dirugikan oleh penalaran panjang",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔍", "h": "Pencarian fakta sederhana",
                     "p": "Jawabannya ada di hasil alat. Berpikir lama hanya menambah "
                          "kesempatan mengarang penjelasan yang tidak diminta.",
                     "style": "bad"},
                    {"ico": "🧰", "h": "Memilih alat yang sudah jelas",
                     "p": "Kalau hanya satu alat yang masuk akal, penalaran panjang adalah "
                          "biaya murni.",
                     "style": "bad"},
                    {"ico": "⚡", "h": "Apa pun yang berhadapan dengan pengguna",
                     "p": "Jeda beberapa detik per langkah × enam langkah adalah "
                          "pengalaman yang buruk, betapapun bagus jawabannya."},
                    {"ico": "🧾", "h": "Keluaran berformat ketat",
                     "p": "Penalaran panjang menaikkan peluang menyimpang dari format yang "
                          "diminta, bukan menurunkannya."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Batas",
            "title": "Cara memutuskannya tanpa berdebat",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Jalankan kumpulan uji Anda dengan kedua model",
                     "p": "Model cepat dan model penalar, konfigurasi lain sama persis."},
                    {"h": "Catat tiga angka, bukan satu",
                     "p": "Tugas yang selesai benar, biaya per tugas selesai, dan waktu "
                          "dinding per tugas. Ketepatan saja akan selalu memenangkan model "
                          "penalar."},
                    {"h": "Kalau selisih ketepatannya kecil, sudah selesai",
                     "p": "Ambil yang murah. Selisih dua poin jarang sepadan dengan biaya "
                          "sembilan kali lipat."},
                    {"h": "Kalau besar, jangan pukul rata",
                     "p": "Cari langkah **mana** yang membaik. Biasanya satu atau dua, dan "
                          "hanya itu yang perlu model penalar."},
                ]},
                {"t": "band",
                 "md": "Yang membuat langkah keempat mungkin: jejak per giliran. Tanpa itu, "
                       "satu-satunya keputusan yang bisa diambil adalah keputusan pukul "
                       "rata untuk seluruh sistem."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Pertanyaan yang selalu muncul",
            "title": "Kalau modelnya sudah bisa menalar, masih perlu gelung agen?",
            "blocks": [
                {"t": "p", "md": "Pertanyaan yang wajar, dan jawabannya bukan soal "
                                 "kecerdasan. Penalaran di dalam model dan gelung agen "
                                 "memecahkan **masalah yang berbeda**, dan hanya salah "
                                 "satunya bisa menyentuh dunia."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Yang bisa dilakukan penalaran sendiri**"},
                     {"t": "bullets", "items": [
                         "Memecah soal jadi langkah, di dalam satu panggilan",
                         "Memeriksa ulang hitungannya sendiri",
                         "Menyusun rencana sebelum menjawab",
                     ]}],
                    [{"t": "p", "md": "**Yang tetap butuh gelung**"},
                     {"t": "bullets", "items": [
                         "Mengambil data yang belum ada di konteks",
                         "Melakukan sesuatu yang punya efek",
                         "Berhenti karena anggaran habis",
                         "Meninggalkan jejak yang bisa diaudit",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Penalaran membuat **tiap langkah** lebih baik. Gelung yang membuat "
                       "langkahnya ada sama sekali — dan yang membuatnya bisa dihentikan, "
                       "dibatasi, dan diperiksa. ==Tidak ada jumlah penalaran yang "
                       "menggantikan sebuah alat=="},
            ],
        },

        {"type": "section", "num": "06", "title": "Memakainya di dalam sistem",
         "lead": "Enam hal yang berubah begitu model penalar masuk ke gelung."},

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Penalaran dan singgahan prompt tidak saling membantu",
            "blocks": [
                {"t": "p", "md": "Singgahan prompt menghemat pada bagian **masukan** yang "
                                 "tidak berubah. Token penalaran adalah **keluaran**, "
                                 "dihasilkan baru tiap permintaan, dan tidak ada bagian "
                                 "darinya yang bisa disinggahkan."},
                {"t": "p", "md": "Akibatnya, dua pengungkit biaya terbesar Anda bekerja di "
                                 "sisi yang berbeda: singgahan menekan biaya masukan, "
                                 "anggaran berpikir menekan biaya keluaran. Keduanya perlu "
                                 "dipasang, dan salah satunya saja meninggalkan setengah "
                                 "penghematan di meja."},
                {"t": "band",
                 "md": "Cara cepat melihat mana yang jadi masalah Anda: bandingkan token "
                       "masukan dan keluaran per tugas. Kalau keluarannya besar, itu "
                       "penalaran; kalau masukannya besar, itu riwayat yang tidak dipangkas."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Penalaran dan keluaran berformat ketat saling menarik",
            "blocks": [
                {"t": "p", "md": "Model penalar diberi imbalan untuk sampai pada jawaban "
                                 "benar, bukan untuk patuh pada format. Pada tugas yang "
                                 "menuntut JSON dengan skema ketat, penalaran panjang "
                                 "kadang **menurunkan** kepatuhan format."},
                {"t": "steps", "items": [
                    {"h": "Pisahkan berpikir dari mengeluarkan",
                     "p": "Biarkan ia menalar, lalu minta panggilan alat sebagai langkah "
                          "tersendiri. Dua panggilan yang masing-masing sederhana lebih "
                          "andal daripada satu yang mengerjakan keduanya."},
                    {"h": "Validasi tetap wajib",
                     "p": "Bab 2 sudah menyebutkan ini, dan penalaran tidak mengubahnya: "
                          "skema menjamin bentuk, bukan kebenaran."},
                    {"h": "Catat laju penolakan skema per model",
                     "p": "Kalau naik sesudah berpindah ke model penalar, Anda baru saja "
                          "menemukan biaya tersembunyinya."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Jejak penalaran bukan bukti alasan",
            "blocks": [
                {"t": "p", "md": "Menggoda sekali memperlakukan jejak penalaran sebagai "
                                 "penjelasan yang bisa diaudit: ia berbentuk alasan, "
                                 "berurutan, dan terbaca masuk akal."},
                {"t": "p", "md": "Tetapi tidak ada yang menjamin bahwa jejak itu **sebab** "
                                 "dari jawabannya. Model bisa sampai pada jawaban karena "
                                 "satu hal dan menuliskan urutan langkah yang berbeda — "
                                 "dan itu tetap terbaca meyakinkan."},
                {"t": "band",
                 "md": "Untuk keputusan yang diawasi, yang bisa diaudit adalah **panggilan "
                       "alat dan hasilnya** — itu peristiwa yang benar-benar terjadi. "
                       "Jejak penalaran berguna untuk memperbaiki sistem; ia ==bukan alat "
                       "bukti=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Menilainya: tiga angka, dan satu yang menyesatkan",
            "blocks": [
                {"t": "table",
                 "head": ["Ukuran", "Yang diberitahukannya", "Jebakannya"],
                 "widths": [26, 40, 34],
                 "rows": [
                     ["Tugas selesai benar", "Yang sebenarnya Anda beli",
                      "Harus per tugas, bukan per panggilan"],
                     ["Biaya per tugas selesai", "Harga sebenarnya",
                      "Harga per juta token menyembunyikan token tak terlihat"],
                     ["Waktu dinding per tugas", "Apakah bisa dipakai orang",
                      "Rerata menyembunyikan ekor; lihat sebarannya"],
                     ["**Ketepatan per panggilan**", "Terlihat paling bagus",
                      "**Selalu memenangkan model penalar**, dan tidak menjawab "
                      "pertanyaan Anda"],
                 ]},
                {"t": "p", "md": "Baris terakhir itu sebabnya perbandingan model sering "
                                 "berakhir dengan keputusan yang salah: ukuran yang paling "
                                 "mudah diambil adalah ukuran yang paling tidak relevan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Bentuk yang biasanya menang di produksi",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🏃", "h": "Model cepat di gelung",
                     "p": "Memilih alat, membaca hasil, memutuskan langkah berikutnya. "
                          "Butuh kepatuhan skema, bukan penalaran panjang.",
                     "style": "good"},
                    {"ico": "🧠", "h": "Model penalar di satu titik",
                     "p": "Langkah yang benar-benar sulit — menyusun rencana, atau "
                          "memutuskan kasus yang ambigu. Satu panggilan, dengan anggaran.",
                     "style": "accent"},
                    {"ico": "🧮", "h": "Kode untuk yang pasti",
                     "p": "Aritmetika, aturan kebijakan, validasi. Tidak ada model yang "
                          "perlu menalar tentang hal yang bisa dihitung.",
                     "style": "good"},
                ]},
                {"t": "band",
                 "md": "Perhatikan bahwa ini bentuk yang sama dengan demo kredit UMKM: "
                       "**model klasik untuk angkanya, kode untuk kebijakannya, model "
                       "bahasa untuk memutuskan apa yang dicari dan bagaimana "
                       "menjelaskannya.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Kesalahan yang paling sering terjadi saat mengadopsinya",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🌍", "h": "Memakainya untuk seluruh gelung",
                     "p": "Membayar penalaran pada enam langkah padahal hanya satu yang "
                          "membutuhkannya. Ini kesalahan yang paling mahal dan paling "
                          "mudah dihindari.",
                     "style": "bad"},
                    {"ico": "🙈", "h": "Tidak mengukur token tak terlihat",
                     "p": "Tagihan naik sembilan kali lipat dan tidak ada di dasbor mana "
                          "pun, sebab yang dicatat hanya jawaban yang terlihat.",
                     "style": "bad"},
                    {"ico": "📜", "h": "Menjadikan jejak penalaran sebagai alat bukti",
                     "p": "Terbaca meyakinkan, tidak dijamin sebagai sebab. Yang bisa "
                          "diaudit adalah panggilan alat.",
                     "style": "bad"},
                    {"ico": "🎯", "h": "Membandingkan dengan ukuran yang salah",
                     "p": "Ketepatan per panggilan selalu memenangkan model penalar dan "
                          "tidak pernah menjawab apakah sistemnya jadi lebih baik.",
                     "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Titik awal yang masuk akal, sebelum diukur",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Mulai tanpa model penalar sama sekali",
                     "p": "Bangun gelungnya, alatnya, dan kumpulan ujinya. Banyak sistem "
                          "berhenti di sini dan sudah cukup."},
                    {"h": "Cari langkah yang paling sering salah",
                     "p": "Dari jejaknya, bukan dari perasaan. Biasanya satu langkah "
                          "menyumbang sebagian besar kegagalan."},
                    {"h": "Ganti langkah itu saja",
                     "p": "Model penalar dengan anggaran berpikir yang dibatasi, hanya di "
                          "titik itu."},
                    {"h": "Ukur tiga angka sebelum dan sesudah",
                     "p": "Kalau biaya per tugas selesai naik lebih cepat daripada "
                          "ketepatannya, kembalikan."},
                ]},
                {"t": "band",
                 "md": "Urutan ini terdengar lambat dan sebenarnya paling cepat: ia "
                       "menghindari satu-satunya kesalahan yang mahal, yaitu memakai model "
                       "penalar di mana-mana lalu mencari tahu belakangan bahwa hanya satu "
                       "langkah yang membutuhkannya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Satu hal yang tidak diperbaiki oleh penalaran, sekuat apa pun",
            "blocks": [
                {"t": "p", "md": "Model penalar tetap tidak tahu apa yang tidak "
                                 "diketahuinya. Penalaran yang panjang di atas fakta yang "
                                 "salah menghasilkan kesimpulan yang salah **dengan lebih "
                                 "banyak dukungan** — bukan lebih sedikit."},
                {"t": "p", "md": "Itu sebabnya bab berikutnya bukan tentang membuat model "
                                 "berpikir lebih baik, melainkan tentang **memberinya bahan "
                                 "yang benar**: apa yang diingat, apa yang dicari lagi, dan "
                                 "apa yang dibuang."},
                {"t": "band",
                 "md": "Urutan yang benar hampir selalu: perbaiki bahannya dulu, baru "
                       "pertimbangkan menaikkan kemampuan menalarnya. Terbalik dari yang "
                       "biasanya dicoba orang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Kualitas kini bisa dibeli saat pemakaian",
                     "p": "Dan karena itu ia jadi keputusan per permintaan, bukan sifat "
                          "tetap sistem."},
                    {"h": "Yang dibeli melandai, yang dibayar tidak",
                     "p": "1 → 5 contoh: +8,3 poin dengan biaya 5×. 5 → 21: +14,3 poin "
                          "dengan biaya 21×. Dan itu pun batas atas."},
                    {"h": "Pemeriksa mengalahkan contoh tambahan",
                     "p": "Asal memeriksa lebih mudah daripada menjawab — dan pemeriksa "
                          "terbaik biasanya kode biasa."},
                    {"h": "Sembilan dari sepuluh token penalaran tidak terlihat",
                     "p": "Dan di dalam gelung agen, ia dikalikan jumlah langkah."},
                    {"h": "Penalaran panjang punya arah gagalnya sendiri",
                     "p": "Jawaban salah yang datang dengan alasan panjang lebih sulit "
                          "ditolak daripada tebakan singkat."},
                ]},
            ],
            "notes": "Pertanyaan penutup yang bagus untuk kelas: di sistem kalian, langkah "
                     "mana yang benar-benar butuh penalaran? Hampir selalu jawabannya satu "
                     "atau dua langkah, bukan seluruh gelung.",
        },
    ],
}
