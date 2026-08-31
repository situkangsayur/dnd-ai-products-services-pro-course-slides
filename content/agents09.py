# -*- coding: utf-8 -*-
"""Bab 9 — Masukan yang bukan teks: gambar, suara, dan apa yang berubah.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 9.

Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti hanya
URUTAN BABNYA. Isinya materi ajar sendiri, gambarnya digambar sendiri.

Kedalaman arsitektur penglihatan komputer ada di Bab 8–12 kelas ini. Dek ini
mengambil sudut pembangun agen: apa yang berubah pada BIAYA, pada BUKTI, dan
pada KEWAJIBAN begitu masukannya bukan teks lagi.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402
from diagrams import image_cost  # noqa: E402

B = BOOKS["agents"]


MMD_ENCODE = """
flowchart LR
  I["Gambar"] --> E["Penyandi penglihatan<br/><small>gambar → vektor</small>"]
  T["Teks"] --> ET["Penyandi teks<br/><small>token → vektor</small>"]
  E --> C["Penyambung<br/><small>menyamakan ruangnya</small>"]
  ET --> C
  C --> M["Model bahasa<br/><small>memperlakukan keduanya sebagai token</small>"]
"""

MMD_CONNECT = """
flowchart TB
  P["Proyeksi<br/><small>satu lapis linier<br/>vektor gambar → token</small>"]
  Q["Berbasis kueri<br/><small>sejumlah TETAP token<br/>yang menanyai gambar</small>"]
  F["Peleburan<br/><small>menyisipkan penglihatan<br/>ke dalam lapis model</small>"]
  P -->|"paling sederhana,<br/>token paling banyak"| Q
  Q -->|"token tetap,<br/>detail bisa terlewat"| F
  F -->|"paling kuat,<br/>paling mahal dilatih"| F
"""

MMD_MODALITIES = """
flowchart LR
  T["Teks"] --> ET["Penyandi teks"] --> R["Ruang vektor bersama"]
  I["Gambar"] --> EI["Penyandi penglihatan"] --> R
  A["Suara"] --> EA["Penyandi suara"] --> R
  V["Video"] --> EV["Bingkai + waktu"] --> R
  R --> M["Model bahasa"]
"""

MMD_PIPE = """
flowchart LR
  IMG["Foto dokumen"] --> T["ALAT: ekstraksi<br/><small>OCR + penataan</small>"]
  T --> D["Data terstruktur<br/><small>medan, angka, tanggal</small>"]
  D --> A["Agen menalar<br/><small>atas DATA, bukan atas piksel</small>"]
  IMG -. "jalan yang menggoda dan rapuh:<br/>minta model menjawab langsung dari gambar" .-> A
"""

MMD_EVIDENCE = """
flowchart TB
  Q["Pertanyaan"] --> A["Jawaban dari gambar"]
  A --> C{"Bisa ditunjuk<br/>di mana asalnya?"}
  C -->|"ya — kotak + nilai terbaca"| OK["Bisa diperiksa manusia"]
  C -->|"tidak — 'saya lihat begitu'"| NO["Tidak bisa diaudit"]
"""


DECK = {
    "id": "agents09",
    "kind": "chapter",
    "number": 9,
    "book": "agents",
    "title": "Masukan yang bukan teks",
    "subtitle": "Gambar, layar, dan suara — apa yang berubah pada biaya, pada "
                "apa yang bisa jadi bukti, dan pada kewajiban yang menyertainya.",
    "source": book_source(9, "agents"),
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
        "**Menghitung biaya token sebuah gambar** dan menjelaskan kenapa ia "
        "tumbuh menurut luas.",
        "**Menyebutkan tiga cara modalitas disambungkan** dan pertukarannya.",
        "**Merancang alur dokumen** yang menalar atas data terstruktur, bukan "
        "atas piksel — dan menyebutkan alasannya.",
        "**Menyebutkan apa yang bisa dan tidak bisa diandalkan** dari model "
        "penglihatan pada dokumen nyata.",
        "**Menjelaskan kenapa foto dokumen adalah data pribadi**, dan apa "
        "yang berubah pada rancangan karenanya.",
        "**Menyebutkan bentuk bukti** yang membuat jawaban dari gambar bisa "
        "diperiksa manusia.",
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "Apa yang sebenarnya berubah",
         "lead": "Gelungnya sama. Yang berubah biayanya, buktinya, dan kewajibannya."},

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Gelungnya tidak berubah sama sekali",
            "blocks": [
                {"t": "p", "md": "Agen yang menerima gambar tetap melakukan hal yang sama: "
                                 "memilih langkah, memanggil alat, membaca hasil, berhenti. "
                                 "Tidak ada mekanisme baru di Bab 1 sampai 8 yang jadi "
                                 "tidak berlaku."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "💸", "h": "Biayanya berubah",
                     "p": "Satu gambar bisa berharga ribuan token, dan ia masuk riwayat — "
                          "jadi dibayar ulang tiap giliran.",
                     "style": "accent"},
                    {"ico": "🧾", "h": "Buktinya berubah",
                     "p": "\\u201cSaya membaca itu di gambar\\u201d tidak bisa diperiksa "
                          "seperti hasil alat yang punya pengenal.",
                     "style": "accent"},
                    {"ico": "⚖", "h": "Kewajibannya berubah",
                     "p": "Foto dokumen hampir selalu data pribadi, dan sering data yang "
                          "diatur khusus.",
                     "style": "accent"},
                ]},
                {"t": "p", "md": "Ketiganya keputusan rekayasa, dan ketiganya diambil "
                                 "sebelum satu baris kode ditulis. Kedalaman arsitektur "
                                 "penglihatannya ada di **Bab 8–12** kelas ini."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dasar",
            "title": "Cara sebuah gambar sampai ke model bahasa",
            "blocks": [
                {"t": "mmd", "id": "agents09-encode", "src": MMD_ENCODE,
                 "cap": "Gambar jadi vektor, disamakan ruangnya dengan teks, lalu diperlakukan sebagai token."},
                {"t": "p", "md": "Gambar dipecah jadi petak, tiap petak jadi vektor lewat "
                                 "penyandi penglihatan, lalu sebuah **penyambung** "
                                 "memetakan vektor itu ke ruang yang sama dengan token "
                                 "teks. Sesudah titik itu, model bahasa memperlakukan "
                                 "keduanya sama."},
                {"t": "band",
                 "md": "Akibat praktis yang paling penting dari kalimat terakhir: "
                       "**gambar menempati ruang jendela konteks yang sama dengan teks**, "
                       "dan bersaing dengannya."},
            ],
        },

        {"type": "section", "num": "02", "title": "Biayanya",
         "lead": "Satu gambar bukan satu lampiran."},

        {
            "type": "slide",
            "kicker": "Biaya",
            "title": "Berapa token satu gambar",
            "blocks": [
                image_cost("agents09-imgcost",
                           cap="Dihitung dari asumsi ubin yang tercetak di gambarnya. "
                               "Langkahi menurut ukuran gambar.",
                           note="Angka per penyedia berbeda dan berubah; yang tidak berubah "
                                "adalah bentuknya — biaya tumbuh menurut LUAS, jadi "
                                "resolusi dua kali lipat berarti empat kali token."),
                {"t": "p", "md": "Satu foto dokumen berharga sekitar **3,3× halaman teks "
                                 "yang sama isinya** — dan lebih sulit dibaca modelnya. "
                                 "Itu dua kerugian sekaligus, dan keduanya bisa dihindari "
                                 "kalau teksnya memang tersedia."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Biaya",
            "title": "Gambar masuk riwayat, dan riwayat dibayar ulang",
            "blocks": [
                {"t": "p", "md": "Bab 2 sudah menghitungnya untuk teks: tiap giliran "
                                 "membayar ulang semua giliran sebelumnya. Untuk gambar, "
                                 "angka yang dibayar ulang itu ribuan token, bukan ratusan."},
                {"t": "steps", "items": [
                    {"h": "Keluarkan gambar dari riwayat begitu diekstrak",
                     "p": "Simpan hasil ekstraksinya — beberapa puluh token — dan buang "
                          "pikselnya dari konteks."},
                    {"h": "Turunkan resolusi ke yang benar-benar perlu",
                     "p": "Empat kali token untuk resolusi dua kali lipat. Sebagian besar "
                          "tugas tidak butuh resolusi penuh."},
                    {"h": "Potong ke bagian yang relevan",
                     "p": "Satu kotak tanda tangan tidak butuh seluruh halaman."},
                ]},
                {"t": "band",
                 "md": "Langkah pertama sendirian sering memotong biaya alur dokumen "
                       "**berkali lipat**, dan hampir tidak pernah dilakukan sebab gambar "
                       "terasa seperti lampiran, bukan seperti token."},
            ],
        },

        {"type": "section", "num": "03", "title": "Cara modalitas disambungkan",
         "lead": "Tiga pendekatan, dan pertukaran yang terasa di pemakaian."},

        {
            "type": "slide",
            "kicker": "Penyambung",
            "title": "Tiga cara, dari yang paling sederhana",
            "blocks": [
                {"t": "mmd", "id": "agents09-connect", "src": MMD_CONNECT,
                 "cap": "Proyeksi, berbasis kueri, dan peleburan."},
                {"t": "p", "md": "Ketiganya menyelesaikan masalah yang sama — membuat "
                                 "vektor gambar bisa dibaca model bahasa — dan berbeda pada "
                                 "**berapa token yang dihasilkan** dan **apa yang hilang**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penyambung",
            "title": "…dan pertukaran yang terasa di pemakaian",
            "blocks": [
                {"t": "table",
                 "head": ["Cara", "Token gambar", "Pertukarannya"],
                 "widths": [24, 24, 52],
                 "rows": [
                     ["Proyeksi", "Banyak, sebanding luas",
                      "Paling sederhana dan paling banyak dipakai; detail terjaga, biaya tinggi"],
                     ["Berbasis kueri", "**Tetap**",
                      "Biaya bisa diramalkan; detail halus bisa terlewat karena jumlah "
                      "tokennya tidak ikut naik"],
                     ["Peleburan", "Bervariasi",
                      "Paling kuat pada tugas yang menuntut penalaran gabungan; paling "
                      "mahal dilatih"],
                 ]},
                {"t": "p", "md": "Untuk pembangun agen, baris kedua yang paling terasa: "
                                 "**biaya yang bisa diramalkan** kadang lebih berharga "
                                 "daripada ketepatan sedikit lebih tinggi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penyambung",
            "title": "Suara dan video: bentuk masalah yang sama",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Suara**"},
                     {"t": "p", "md": "Disandikan jadi vektor lalu disambungkan dengan cara "
                                      "yang sama. Untuk hampir semua agen bisnis, jalur "
                                      "yang benar tetap: **transkripsikan dengan alat**, "
                                      "lalu bekerja atas teksnya."}],
                    [{"t": "p", "md": "**Video**"},
                     {"t": "p", "md": "Bingkai demi bingkai, jadi biayanya berlipat dengan "
                                      "durasi. Sampel beberapa bingkai kunci hampir selalu "
                                      "cukup, dan selisih biayanya besar."}],
                ]},
                {"t": "p", "md": "Pola yang sama muncul pada ketiga modalitas: **ubah jadi "
                                 "representasi yang lebih kecil dan lebih bisa diperiksa "
                                 "dengan alat, lalu nalarkan atas representasi itu.**"},
                {"t": "band",
                 "md": "Dan satu keuntungan yang jarang disebut: transkrip dan data "
                       "terstruktur **bisa disimpan, dicari, dan dikutip**. Piksel dan "
                       "gelombang tidak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penyandi",
            "title": "Kenapa penyandi gambar dan teks bisa bertemu sama sekali",
            "blocks": [
                {"t": "p", "md": "Pertanyaan yang wajar: bagaimana vektor dari piksel bisa "
                                 "berarti apa pun bagi model yang dilatih atas kata?"},
                {"t": "p", "md": "Jawabannya pelatihan berpasangan. Kalau banyak sekali "
                                 "pasangan gambar dan keterangannya dilatihkan bersama, "
                                 "dengan tujuan **mendekatkan pasangan yang cocok dan "
                                 "menjauhkan yang tidak**, kedua penyandi lama-lama "
                                 "menaruh \u201cseekor kucing\u201d dan gambar kucing di "
                                 "tempat yang berdekatan."},
                {"t": "band",
                 "md": "Akibat yang penting bagi pemakai: kemampuan itu **sekuat data "
                       "pasangannya**. Jenis dokumen yang jarang muncul di internet — "
                       "formulir bank Indonesia, misalnya — jauh lebih lemah daripada "
                       "foto sehari-hari, dan itu bukan sesuatu yang bisa diperbaiki "
                       "dengan prompt."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penyandi",
            "title": "Petak, dan kenapa detail kecil hilang",
            "blocks": [
                {"t": "p", "md": "Gambar dipecah jadi petak berukuran tetap, dan tiap petak "
                                 "jadi satu vektor. Teks kecil yang jatuh di dalam satu "
                                 "petak bersama banyak hal lain harus berbagi satu vektor "
                                 "dengan semuanya."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Akibatnya**"},
                     {"t": "bullets", "items": [
                         "Angka kecil pada tabel padat sering salah baca",
                         "Menaikkan resolusi benar-benar menolong — dan berlipat empat "
                         "biayanya",
                         "Memotong bagian yang relevan sering lebih baik daripada "
                         "menaikkan resolusi seluruh halaman",
                     ]}],
                    [{"t": "p", "md": "**Yang bisa dilakukan**"},
                     {"t": "bullets", "items": [
                         "Deteksi wilayah dulu, lalu potong dan perbesar",
                         "Untuk tabel: alat khusus, bukan model umum",
                         "Untuk teks: OCR sungguhan mengalahkan model bahasa",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Nasihat yang menghemat paling banyak waktu di alur dokumen: "
                       "==pakai alat yang memang dibuat untuk itu==. Model bahasa yang "
                       "melihat gambar bukan pengganti OCR."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Layar",
            "title": "Tangkapan layar: modalitas yang paling cepat tumbuh",
            "blocks": [
                {"t": "p", "md": "Agen yang mengoperasikan aplikasi lewat tangkapan layar "
                                 "menarik justru karena ia tidak butuh API — ia memakai "
                                 "antarmuka yang sudah ada, sama seperti manusia."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🔓", "h": "Kenapa menggoda",
                     "p": "Sistem lama tanpa API tiba-tiba bisa diotomatiskan tanpa "
                          "menunggu tim yang memeliharanya."},
                    {"ico": "⚠", "h": "Kenapa rapuh",
                     "p": "Antarmuka berubah dan agennya rusak diam-diam. Tidak ada kontrak "
                          "apa pun yang menjaganya.",
                     "style": "bad"},
                ]},
                {"t": "p", "md": "Dan biayanya besar: tiap langkah butuh satu tangkapan "
                                 "layar baru, jadi **satu tugas sepuluh langkah berarti "
                                 "sepuluh gambar** di dalam satu percakapan yang sama."},
                {"t": "band",
                 "md": "Urutan yang benar hampir selalu: **cari API-nya dulu, cari basis "
                       "datanya, baru pertimbangkan layar.** Yang terakhir adalah pilihan "
                       "ketika tidak ada pilihan lain."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Layar",
            "title": "Kalau memang harus lewat layar",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Batasi ke satu aplikasi, satu lingkungan",
                     "p": "Agen yang bisa mengeklik apa saja di mesin mana saja adalah "
                          "permukaan yang tidak bisa dijelaskan ke siapa pun."},
                    {"h": "Alat berupa aksi bernama, bukan “klik di 300,450”",
                     "p": "`buka_tagihan(id)` bisa diuji dan bertahan; koordinat piksel "
                          "rusak pada perubahan tata letak pertama."},
                    {"h": "Tangkapan layar terakhir saja di konteks",
                     "p": "Sepuluh tangkapan layar di riwayat adalah puluhan ribu token "
                          "yang dibayar berulang."},
                    {"h": "Selalu di balik persetujuan untuk tindakan yang menulis",
                     "p": "Sama seperti alat tulis mana pun. Klik yang mengirim uang tetap "
                          "klik yang mengirim uang."},
                ]},
            ],
        },

        {"type": "section", "num": "04", "title": "Bentuk yang bekerja di dunia nyata",
         "lead": "Alat dulu, penalaran belakangan."},

        {
            "type": "slide",
            "kicker": "Bentuk",
            "title": "Ekstrak dulu, nalarkan kemudian",
            "blocks": [
                {"t": "mmd", "id": "agents09-pipe", "src": MMD_PIPE,
                 "cap": "Jalan yang lurus dan rapuh digambar sebagai garis putus."},
                {"t": "p", "md": "Bab 3 sudah menyebut kesimpulannya: penalaran berlangkah "
                                 "di atas gambar masih jauh lebih lemah daripada di atas "
                                 "teks. Jadi jangan minta satu panggilan mengerjakan "
                                 "keduanya."},
                {"t": "band",
                 "md": "Bentuk yang bertahan: **alat mengubah gambar jadi data "
                       "terstruktur; agen menalar atas data itu.** Hasilnya lebih murah, "
                       "lebih tepat, dan — yang paling penting — bisa diperiksa."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bentuk",
            "title": "Apa yang bisa dan tidak bisa diandalkan",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✅", "h": "Cukup andal",
                     "p": "Menjelaskan isi gambar, membaca teks tercetak yang jelas, "
                          "mengenali jenis dokumen, menemukan bagian yang diminta.",
                     "style": "good"},
                    {"ico": "⚠", "h": "Sering meleset",
                     "p": "Membaca angka pada tabel padat, mencocokkan nilai dengan "
                          "kolomnya, tulisan tangan, stempel yang menimpa teks.",
                     "style": "bad"},
                    {"ico": "❌", "h": "Jangan diandalkan",
                     "p": "Menghitung jumlah benda, membandingkan posisi, dan aritmetika "
                          "atas angka yang dibacanya sendiri.",
                     "style": "bad"},
                    {"ico": "🧮", "h": "Serahkan ke kode",
                     "p": "Semua aritmetika. Model membaca angkanya; kode yang "
                          "menghitungnya.",
                     "style": "good"},
                ]},
                {"t": "p", "md": "Kartu ketiga penting untuk dokumen keuangan: model yang "
                                 "membaca dua belas angka dengan benar lalu menjumlahkannya "
                                 "**tetap bisa salah pada jumlahnya** — dan jumlah itu yang "
                                 "dipakai orang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bentuk",
            "title": "Ekstraksi yang bisa dipercaya menyebut keyakinannya",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Kembalikan nilai beserta lokasinya",
                     "p": "Kotak koordinat tempat nilai itu terbaca. Ini yang membuat "
                          "manusia bisa memeriksa dalam dua detik."},
                    {"h": "Bedakan kosong dari tidak terbaca",
                     "p": "Medan yang memang kosong dan medan yang gagal dibaca menuntut "
                          "tindakan yang berbeda sepenuhnya."},
                    {"h": "Sediakan ambang untuk minta bantuan",
                     "p": "Di bawah ambang, eskalasikan — jangan menebak. Bab 5: alat "
                          "menyerah dengan alasan adalah hasil yang sah."},
                    {"h": "Simpan gambarnya, bukan di konteks",
                     "p": "Di penyimpanan yang punya pemilik dan retensi, dengan pengenal "
                          "yang bisa dirujuk jejak."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dokumen",
            "title": "Tabel adalah kasus tersulit, dan yang paling sering dibutuhkan",
            "blocks": [
                {"t": "p", "md": "Membaca satu angka dari sebuah halaman relatif mudah. "
                                 "Membaca **tabel** menuntut dua hal sekaligus: mengenali "
                                 "nilainya, dan mengetahui nilai itu milik baris dan kolom "
                                 "yang mana."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔀", "h": "Kesalahan pergeseran",
                     "p": "Nilai benar, kolomnya salah. Ini yang paling berbahaya, sebab "
                          "hasilnya masuk akal dan salah.",
                     "style": "bad"},
                    {"ico": "🧩", "h": "Sel gabungan",
                     "p": "Judul yang membentang dua kolom, atau baris yang bersambung ke "
                          "halaman berikutnya."},
                    {"ico": "📄", "h": "Tabel lintas halaman",
                     "p": "Judul kolomnya ada di halaman sebelumnya, dan tiap halaman "
                          "diproses terpisah."},
                ]},
                {"t": "band",
                 "md": "Karena itu untuk tabel keuangan, **alat khusus pengurai tabel "
                       "mengalahkan model umum** — dan kalau tidak ada, minta model "
                       "mengembalikan nilai **beserta nama baris dan kolomnya**, supaya "
                       "pergeseran bisa ditangkap kode."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dokumen",
            "title": "Tulisan tangan, tanda tangan, dan stempel",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Tulisan tangan**"},
                     {"t": "p", "md": "Jauh lebih lemah daripada teks tercetak, dan lebih "
                                      "lemah lagi untuk angka. Untuk nilai yang menentukan "
                                      "keputusan, ini bukan jalur yang bisa dipercaya "
                                      "tanpa pemeriksaan manusia."}],
                    [{"t": "p", "md": "**Tanda tangan dan stempel**"},
                     {"t": "p", "md": "Mendeteksi **keberadaannya** masuk akal dan berguna. "
                                      "Menilai **keasliannya** adalah tugas yang berbeda "
                                      "sepenuhnya, dan bukan tugas model bahasa."}],
                ]},
                {"t": "band",
                 "md": "Perbedaan di kolom kanan pantas ditulis di dokumen rancangan: "
                       "\u201cada tanda tangan di kotak itu\u201d adalah temuan yang "
                       "berguna; ==\u201ctanda tangannya sah\u201d adalah klaim yang "
                       "tidak boleh dibuat sistem ini=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dokumen",
            "title": "Dokumen banyak halaman: satu keputusan yang menentukan biaya",
            "blocks": [
                {"t": "p", "md": "Berkas dua puluh halaman yang dikirim seluruhnya adalah "
                                 "puluhan ribu token — dan biasanya sembilan belas "
                                 "halamannya tidak relevan."},
                {"t": "steps", "items": [
                    {"h": "Klasifikasikan halaman dulu, dengan model kecil atau aturan",
                     "p": "Halaman mana yang memuat neraca, mana yang lampiran. Murah, "
                          "sekali, dan memotong sebagian besar biaya."},
                    {"h": "Proses halaman yang relevan saja, dengan resolusi penuh",
                     "p": "Anggaran resolusi dibelanjakan di tempat yang benar."},
                    {"h": "Simpan pemetaannya",
                     "p": "Nilai ini dari halaman 7 kotak sekian — itu kutipan yang bisa "
                          "diperiksa."},
                ]},
                {"t": "band",
                 "md": "Pola yang sama seperti pengambilan di Bab 4: **jaring lebar dengan "
                       "yang murah, saringan halus dengan yang mahal.** Bentuk yang muncul "
                       "lagi karena alasan yang sama."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Dokumen",
            "title": "Membandingkan dua pendekatan ekstraksi dengan angka",
            "blocks": [
                {"t": "table",
                 "head": ["Pendekatan", "Kuat pada", "Lemah pada"],
                 "widths": [26, 36, 38],
                 "rows": [
                     ["OCR + aturan", "Format tetap, volume besar, biaya nyaris nol",
                      "Variasi tata letak; tiap format baru butuh kerja"],
                     ["OCR + model bahasa", "Tata letak bervariasi, medan yang bernama",
                      "Biaya per dokumen; tetap perlu validasi"],
                     ["Model penglihatan langsung", "Dokumen yang tak terstruktur",
                      "Paling mahal, paling sulit diaudit, paling sering salah pada tabel"],
                     ["**Campuran**", "Kenyataan di kebanyakan sistem",
                      "Perlu memutuskan mana yang dipakai kapan"],
                 ]},
                {"t": "p", "md": "Keputusannya tidak perlu ditebak: **jalankan ketiganya "
                                 "pada dua puluh dokumen nyata** dan bandingkan ketepatan, "
                                 "biaya, dan laju eskalasi. Satu hari kerja, dan jawabannya "
                                 "tidak perlu diperdebatkan lagi."},
            ],
        },

        {"type": "section", "num": "05", "title": "Bukti dan kewajiban",
         "lead": "Dua hal yang berubah paling besar, dan paling sering terlambat dipikirkan."},

        {
            "type": "slide",
            "kicker": "Bukti",
            "title": "Jawaban dari gambar harus bisa ditunjuk",
            "blocks": [
                {"t": "mmd", "id": "agents09-evidence", "src": MMD_EVIDENCE,
                 "cap": "Satu pertanyaan yang memisahkan yang bisa diaudit dari yang tidak."},
                {"t": "p", "md": "Untuk teks, kutipan berarti pengenal potongan yang bisa "
                                 "diperiksa. Untuk gambar, bentuknya **lokasi** — halaman, "
                                 "kotak, dan nilai yang terbaca di situ. Tanpa itu, "
                                 "satu-satunya cara memeriksa adalah membuka dokumennya dan "
                                 "mencari sendiri — ==agennya tidak menghemat pekerjaan "
                                 "siapa pun=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Kewajiban",
            "title": "Foto dokumen hampir selalu data pribadi",
            "blocks": [
                {"t": "p", "md": "Satu foto KTP atau rekening koran memuat lebih banyak "
                                 "data pribadi daripada seluruh permintaan teks yang "
                                 "menyertainya — termasuk hal yang tidak diminta dan tidak "
                                 "dibutuhkan siapa pun."},
                {"t": "steps", "items": [
                    {"h": "Gambar tidak keluar perimeter",
                     "p": "Di demo, foto dari ponsel masuk ke penyimpanan bank dan berhenti "
                          "di situ. **Tidak ada jalur kode** yang bisa mengirimnya ke "
                          "penyedia model."},
                    {"h": "Kalau harus diproses model, batasi apa yang dikirim",
                     "p": "Potongan yang relevan, bukan halaman penuh. Yang tidak dikirim "
                          "tidak perlu dijelaskan."},
                    {"h": "Retensinya mengikuti dokumennya",
                     "p": "Bukan mengikuti umur log. Ini yang paling sering salah."},
                ]},
                {"t": "band",
                 "md": "Pertanyaan yang akan diajukan pemeriksa, dan yang harus dijawab "
                       "dengan **jalur kode**, bukan dengan kebijakan: *ke mana perginya "
                       "foto dokumen nasabah?*"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Kewajiban",
            "title": "Gambar juga bisa membawa perintah",
            "blocks": [
                {"t": "p", "md": "Bab 4 menyebut perintah yang menumpang di dalam teks yang "
                                 "dibaca agen. Hal yang sama berlaku untuk gambar: teks di "
                                 "dalam gambar dibaca model, dan **model tidak membedakan** "
                                 "teks yang isinya data dari teks yang isinya perintah."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🖼", "h": "Bentuk seranganya",
                     "p": "Sebuah dokumen yang memuat kalimat ditujukan kepada agen, "
                          "dicetak kecil atau ditempel di sudut halaman."},
                    {"ico": "🛡", "h": "Penanganannya sama",
                     "p": "Bukan di prompt. Di batas alat: apa yang boleh dipanggil sesudah "
                          "membaca sesuatu yang tidak tepercaya.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Dan satu tambahan khas gambar: kalau dokumennya berasal dari luar, "
                       "**perlakukan hasil ekstraksinya sebagai masukan tidak tepercaya** "
                       "— divalidasi, bukan diteruskan apa adanya."},
            ],
        },

        {"type": "section", "num": "05b", "title": "Modalitas lain",
         "lead": "Suara, video, dan pola yang sama muncul lagi."},

        {
            "type": "slide",
            "kicker": "Modalitas",
            "title": "Satu ruang, banyak pintu masuk",
            "blocks": [
                {"t": "mmd", "id": "agents09-modalities", "src": MMD_MODALITIES,
                 "cap": "Tiap modalitas punya penyandinya sendiri, semuanya bermuara ke satu ruang."},
                {"t": "p", "md": "Bentuknya seragam: tiap modalitas punya penyandi yang "
                                 "mengubahnya jadi vektor, lalu semuanya dipetakan ke ruang "
                                 "yang sama supaya model bahasa bisa memperlakukannya "
                                 "sebagai token."},
                {"t": "band",
                 "md": "Karena bentuknya seragam, **pertanyaan rekayasanya juga seragam**: "
                       "berapa token yang dihasilkan, apa yang hilang saat penyandian, dan "
                       "apakah hasilnya bisa dikutip."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Suara",
            "title": "Suara: hampir selalu transkripsikan dulu",
            "blocks": [
                {"t": "p", "md": "Model bisa menerima suara langsung, dan untuk sebagian "
                                 "tugas itu berguna — nada bicara, jeda, siapa yang "
                                 "berbicara. Untuk hampir semua agen bisnis, jalur yang "
                                 "benar tetap transkripsi lewat alat."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📝", "h": "Bisa disimpan dan dicari",
                     "p": "Transkrip masuk basis data, bisa dicari, bisa dikutip. Gelombang "
                          "suara tidak.",
                     "style": "good"},
                    {"ico": "💸", "h": "Jauh lebih murah",
                     "p": "Satu jam rapat sebagai teks adalah beberapa ribu token; sebagai "
                          "suara jauh lebih besar.",
                     "style": "good"},
                    {"ico": "🎙", "h": "Yang hilang",
                     "p": "Nada, keraguan, siapa berbicara. Kalau itu penting, catat "
                          "sebagai metadata — jangan bawa gelombangnya."},
                ]},
                {"t": "band",
                 "md": "Dan satu kewajiban yang sering terlewat: **rekaman suara orang "
                       "adalah data pribadi**, dan di banyak konteks perlu izin yang "
                       "berbeda dari izin memproses teksnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Video",
            "title": "Video: biaya berlipat dengan durasi, dan hampir selalu bisa dihindari",
            "blocks": [
                {"t": "p", "md": "Video disandikan sebagai rentetan bingkai, kadang dengan "
                                 "tambahan penanda waktu. Artinya biayanya adalah biaya "
                                 "gambar **dikalikan jumlah bingkai** — dan satu menit pada "
                                 "satu bingkai per detik sudah enam puluh gambar."},
                {"t": "steps", "items": [
                    {"h": "Ambil bingkai kunci, bukan semuanya",
                     "p": "Saat berubah, saat ada gerakan, atau satu per beberapa detik. "
                          "Sering satu bingkai per adegan sudah cukup."},
                    {"h": "Pisahkan suaranya dan transkripsikan",
                     "p": "Untuk sebagian besar video, transkrip menjawab lebih banyak "
                          "pertanyaan daripada bingkainya, dengan biaya jauh lebih kecil."},
                    {"h": "Simpan penanda waktu",
                     "p": "Supaya jawabannya bisa menunjuk detik keberapa — kutipan, dalam "
                          "bentuk waktu."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Modalitas",
            "title": "Apa yang hilang di tiap penyandian",
            "blocks": [
                {"t": "table",
                 "head": ["Modalitas", "Yang bertahan", "Yang hilang"],
                 "widths": [22, 38, 40],
                 "rows": [
                     ["Gambar", "Isi, tata letak kasar, teks besar",
                      "Angka kecil, hubungan baris-kolom, detail di bawah ukuran petak"],
                     ["Suara", "Kata-kata",
                      "Nada, keraguan, siapa berbicara — kecuali dicatat terpisah"],
                     ["Video", "Isi bingkai yang diambil",
                      "Semua yang terjadi di antara bingkai yang diambil"],
                     ["Tabel sebagai gambar", "Angkanya",
                      "**Hubungan angka dengan kolomnya** — dan itu yang dipakai"],
                 ]},
                {"t": "band",
                 "md": "Baris terakhir yang paling sering menyebabkan kesalahan yang tidak "
                       "terlihat: nilainya benar, kolomnya salah, dan hasilnya tetap "
                       "terlihat masuk akal."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Kewajiban",
            "title": "Apa yang boleh disimpan dari sebuah dokumen",
            "blocks": [
                {"t": "p", "md": "Godaan yang wajar sesudah ekstraksi berhasil: simpan "
                                 "semuanya, siapa tahu berguna. Itu cara paling cepat "
                                 "menciptakan basis data data pribadi yang tidak ada di "
                                 "rancangan siapa pun."},
                {"t": "table",
                 "head": ["Yang diekstrak", "Simpan?", "Alasannya"],
                 "widths": [30, 22, 48],
                 "rows": [
                     ["Angka yang dipakai keputusan", "Ya",
                      "Beserta lokasinya — ini bukti yang dibutuhkan pemeriksa"],
                     ["Jenis dan tanggal dokumen", "Ya",
                      "Metadata, dan diperlukan untuk retensi"],
                     ["Nama, alamat, nomor identitas", "**Tidak**",
                      "Agen tidak membutuhkannya; petugas melihatnya di sistem inti"],
                     ["Gambar aslinya", "Di penyimpanan dokumen",
                      "Dengan pemilik dan retensi dokumen, bukan retensi log"],
                 ]},
                {"t": "band",
                 "md": "Baris ketiga adalah keputusan rancangan, bukan pembatasan yang "
                       "merepotkan: **yang tidak disimpan tidak perlu dijaga, tidak perlu "
                       "dihapus, dan tidak bisa bocor.**"},
            ],
        },

        {"type": "section", "num": "06", "title": "Praktik",
         "lead": "Merancang, mengukur, dan menguji alur yang menerima gambar."},

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Urutan merancang alur dokumen",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Cari tahu apakah teksnya sudah ada",
                     "p": "PDF digital, hasil sistem lain, berkas asal. Kalau ada, "
                          "seluruh bab ini bisa dilewati."},
                    {"h": "Tulis alat ekstraksi, bukan prompt ekstraksi",
                     "p": "Keluarannya berskema, dengan lokasi dan tingkat keyakinan."},
                    {"h": "Nalarkan atas data terstrukturnya",
                     "p": "Di situ semua yang dipelajari tujuh bab sebelumnya berlaku "
                          "seperti biasa."},
                    {"h": "Simpan gambarnya di luar konteks",
                     "p": "Dengan pengenal, pemilik, dan retensi."},
                ]},
                {"t": "band",
                 "md": "Langkah pertama yang paling sering dilewat, dan paling sering "
                       "menghapus seluruh masalah: **banyak dokumen yang difoto sebenarnya "
                       "tersedia dalam bentuk teks di sistem lain.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Mengujinya: sebagian besar tidak butuh model",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📐", "h": "Uji skema ekstraksi",
                     "p": "Medan yang wajib ada, tipe yang benar, lokasi yang masuk akal. "
                          "Kode biasa.",
                     "style": "good"},
                    {"ico": "🖼", "h": "Kumpulan gambar tetap",
                     "p": "Dua puluh dokumen nyata dengan nilai yang benar sudah dicatat. "
                          "Ini kumpulan uji Bab 7, dalam bentuk gambar.",
                     "style": "good"},
                    {"ico": "🌫", "h": "Kasus yang buruk sengaja",
                     "p": "Miring, gelap, terpotong, stempel menimpa. Di sinilah sistem "
                          "menunjukkan apakah ia tahu ia tidak tahu."},
                    {"ico": "🔒", "h": "Uji jalur data",
                     "p": "Pastikan tidak ada jalur kode dari penyimpanan gambar ke "
                          "penyedia model. Uji struktural, seperti Bab 5.",
                     "style": "good"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Angka yang pantas dipantau pada alur bergambar",
            "blocks": [
                {"t": "table",
                 "head": ["Angka", "Sehat kalau", "Gejala kalau tidak"],
                 "widths": [28, 28, 44],
                 "rows": [
                     ["Token gambar per tugas", "Datar dan kecil",
                      "Naik → gambar tidak dikeluarkan dari riwayat"],
                     ["Laju ekstraksi gagal", "Stabil",
                      "Naik → mutu foto turun, atau jenis dokumen berubah"],
                     ["Laju eskalasi karena tak terbaca", "Ada, dan kecil",
                      "Nol → ambang keyakinannya tidak berfungsi"],
                     ["Selisih nilai terbaca lawan sistem", "Mendekati nol",
                      "Ada → ekstraksinya salah, atau dokumennya bukan yang dikira"],
                 ]},
                {"t": "p", "md": "Baris ketiga sekali lagi: **nol eskalasi bukan "
                                 "keberhasilan.** Dokumen yang buruk pasti ada; sistem yang "
                                 "tidak pernah mengeluh sedang menebak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Waktu tunggu pada alur bergambar",
            "blocks": [
                {"t": "p", "md": "Gambar menambah waktu di dua tempat sekaligus: mengunggah "
                                 "berkasnya, dan memproses masukan yang jauh lebih besar. "
                                 "Pada ponsel di jaringan lapangan, yang pertama sering "
                                 "lebih besar daripada yang kedua."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📶", "h": "Perkecil sebelum dikirim",
                     "p": "Di sisi ponsel, bukan di peladen. Resolusi yang cukup untuk "
                          "dibaca sering jauh di bawah resolusi kamera.",
                     "style": "good"},
                    {"ico": "🔄", "h": "Kerjakan yang lain sambil menunggu",
                     "p": "Ekstraksi dokumen tidak menghalangi pengambilan data lain — "
                          "itu langkah yang boleh sejajar."},
                ]},
                {"t": "band",
                 "md": "Dan satu hal yang lebih besar pengaruhnya daripada keduanya: "
                       "**tunjukkan apa yang sedang terjadi.** Layar yang menyebut "
                       "\u201cmembaca halaman 3 dari 5\u201d mengubah pengalaman menunggu "
                       "lebih banyak daripada penghematan satu detik."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Enam kegagalan khas alur bergambar",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🖼", "h": "Gambar menetap di riwayat",
                     "p": "Dibayar ulang tiap giliran. Penyebab pembengkakan biaya nomor "
                          "satu di alur dokumen.",
                     "style": "bad"},
                    {"ico": "🔢", "h": "Model menghitung sendiri",
                     "p": "Membaca dua belas angka dengan benar lalu salah menjumlahkannya.",
                     "style": "bad"},
                    {"ico": "🔀", "h": "Nilai bergeser kolom",
                     "p": "Masuk akal, dan salah. Tidak tertangkap tanpa nama baris dan "
                          "kolom.",
                     "style": "bad"},
                    {"ico": "🤫", "h": "Tak terbaca dianggap kosong",
                     "p": "Medan gagal dibaca diperlakukan seperti medan yang memang "
                          "kosong.",
                     "style": "bad"},
                    {"ico": "📤", "h": "Gambar keluar perimeter",
                     "p": "Dikirim ke penyedia model karena tidak ada yang melarangnya di "
                          "kode.",
                     "style": "bad"},
                    {"ico": "🎯", "h": "Resolusi penuh untuk semuanya",
                     "p": "Empat kali biaya untuk ketepatan yang sering tidak berubah.",
                     "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Kapan multi-modal adalah alat yang salah",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Pakai alat lain**"},
                     {"t": "bullets", "items": [
                         "Teksnya sudah ada di sistem lain",
                         "Formatnya tetap dan volumenya besar → OCR + aturan",
                         "Yang dibutuhkan hitungan → kode, selalu",
                         "Keasliannya yang dipertanyakan → bukan tugas model bahasa",
                     ]}],
                    [{"t": "p", "md": "**Di sinilah ia menang**"},
                     {"t": "bullets", "items": [
                         "Tata letak bervariasi dan medannya bernama",
                         "Dokumen yang tidak terstruktur",
                         "Menentukan jenis dokumen sebelum diproses",
                         "Menjelaskan isi gambar kepada manusia",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Kolom kiri baris pertama tetap yang paling sering benar dan paling "
                       "sering terlewat: **tanyakan dulu apakah dokumen itu pernah ada "
                       "dalam bentuk teks** sebelum membangun apa pun."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Yang dipakai demo, dan apa yang sengaja tidak ada di sana",
            "blocks": [
                {"t": "p", "md": "Aplikasi lapangan di demo memotret dokumen pengajuan. "
                                 "Yang menarik dari rancangannya bukan apa yang "
                                 "dilakukannya, melainkan **apa yang tidak mungkin "
                                 "dilakukannya.**"},
                {"t": "steps", "items": [
                    {"h": "Foto pergi ke penyimpanan bank, dan berhenti di situ",
                     "p": "Tidak ada jalur kode dari penyimpanan itu ke penyedia model "
                          "mana pun."},
                    {"h": "Agen menerima pengenal pengajuan, bukan gambar",
                     "p": "Alat yang dimilikinya tidak mengembalikan gambar, jadi ia tidak "
                          "bisa meneruskannya ke mana pun."},
                    {"h": "Klaimnya diuji, bukan dijanjikan",
                     "p": "`test_the_agents_tools_cannot_reach_personal_data` gagal kalau "
                          "seseorang menambahkan alat yang melanggarnya."},
                ]},
                {"t": "band",
                 "md": "Ini penerapan langsung prinsip Bab 1 pada modalitas baru: "
                       "**batas kemampuan ada di ketiadaan alat**, dan ketiadaan itu bisa "
                       "diuji."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Urutan memasangnya, dari yang paling murah",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Cari teksnya",
                     "p": "Kalau ada, selesai. Ini langkah yang paling sering menghapus "
                          "seluruh pekerjaan."},
                    {"h": "OCR sungguhan untuk teks tercetak",
                     "p": "Lebih murah dan lebih tepat daripada model bahasa untuk "
                          "pekerjaan ini."},
                    {"h": "Model penglihatan untuk yang tata letaknya bervariasi",
                     "p": "Dengan keluaran berskema, lokasi, dan tingkat keyakinan."},
                    {"h": "Manusia untuk yang di bawah ambang",
                     "p": "Dan hitung berapa sering itu terjadi — angka itu memberi tahu "
                          "apakah alurnya layak dipakai."},
                ]},
                {"t": "band",
                 "md": "Perhatikan bahwa dua langkah pertama tidak melibatkan model bahasa "
                       "sama sekali, dan keduanya menyelesaikan sebagian besar dokumen "
                       "yang benar-benar dihadapi bank."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Gelungnya sama; biaya, bukti, dan kewajibannya berubah",
                     "p": "Tidak ada mekanisme baru — hanya tiga hal yang jadi jauh lebih "
                          "besar."},
                    {"h": "Satu gambar bukan satu lampiran",
                     "p": "Foto dokumen ≈ 3,3× halaman teks yang sama, dan biayanya tumbuh "
                          "menurut luas."},
                    {"h": "Ekstrak dengan alat, nalarkan atas datanya",
                     "p": "Lebih murah, lebih tepat, dan satu-satunya bentuk yang bisa "
                          "diperiksa."},
                    {"h": "Jawaban dari gambar harus bisa ditunjuk",
                     "p": "Halaman, kotak, nilai. Tanpa itu tidak ada yang bisa diaudit."},
                    {"h": "Foto dokumen adalah data pribadi",
                     "p": "Dan pertanyaan \\u201cke mana perginya\\u201d harus dijawab "
                          "dengan jalur kode."},
                ]},
            ],
            "notes": "Pertanyaan penutup: dokumen yang kalian foto, apakah teksnya "
                     "sebenarnya sudah ada di suatu sistem? Jawabannya cukup sering ya, "
                     "dan itu menghapus seluruh bab ini.",
        },
    ],
}
