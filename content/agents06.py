# -*- coding: utf-8 -*-
"""Bab 6 — Rencana dan refleksi: memecah tugas, dan memperbaiki diri.

Mengikuti urutan bab Grootendorst & Alammar, *An Illustrated Guide to AI
Agents* (O'Reilly, early release), bab 6.

Lihat catatan di kepala content/agents01.py: dari buku ini yang diikuti hanya
URUTAN BABNYA. Isinya materi ajar sendiri, gambarnya digambar sendiri.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOKS, book_source  # noqa: E402

B = BOOKS["agents"]


# Dua subgraf yang masing-masing DIRECTION LR, ditumpuk oleh flowchart TB.
# Kebalikannya (LR luar, TB dalam) membuat tiap subgraf setinggi empat simpul
# dan seluruh gambarnya jadi rasio 48% — mengecil sampai tidak terbaca.
MMD_PLANFIRST = """
flowchart TB
  subgraph A["Tanpa rencana"]
    direction LR
    A1["Tujuan"] --> A2["Langkah 1"] --> A3["Langkah 2"] --> A4["… entah sampai kapan"]
  end
  subgraph B["Dengan rencana eksplisit"]
    direction LR
    B1["Tujuan"] --> B2["Rencana: 4 langkah"] --> B3["Kerjakan, tandai selesai"] --> B4["Rencana habis = selesai"]
  end
  A ~~~ B
"""

MMD_REFLECT = """
flowchart LR
  D["Draf"] --> K["Kritik<br/><small>panggilan model kedua</small>"]
  K --> R["Revisi<br/><small>panggilan model ketiga</small>"]
  R --> C{"Cukup?"}
  C -->|"belum"| K
  C -->|"ya"| O["Keluaran"]
  C -. "tanpa syarat henti,<br/>ini gelung tak berujung" .-> C
"""

MMD_SIGNAL = """
flowchart TB
  S1["Sinyal dari DUNIA<br/><small>uji gagal, skema ditolak,<br/>kebijakan dilanggar</small>"]
  S2["Sinyal dari MODEL<br/><small>“sepertinya kurang lengkap”</small>"]
  S1 --> G["Perbaikan yang terarah"]
  S2 --> H["Perubahan yang belum tentu perbaikan"]
"""

MMD_REPLAN = """
flowchart LR
  P["Rencana"] --> E["Kerjakan langkah"]
  E --> O["Amatan"]
  O --> C{"Rencananya masih<br/>masuk akal?"}
  C -->|"ya"| E
  C -->|"tidak"| RP["Susun ulang rencana<br/><small>dengan anggaran susun-ulang</small>"]
  RP --> E
"""

MMD_DECOMP = """
flowchart TB
  T["Tugas besar"] --> Q{"Bisa dipetakan<br/>ke satu alat?"}
  Q -->|"ya"| A["Kerjakan"]
  Q -->|"tidak"| S["Pecah jadi bagian<br/><small>tiap bagian: satu alat, satu hasil</small>"]
  S --> Q
  S -. "kalau pecahannya tetap tidak<br/>bisa dipetakan, alatnya yang kurang" .-> S
"""

MMD_REACT = """
flowchart LR
  P["Pikir<br/><small>apa yang kurang?</small>"] --> A["Tindak<br/><small>panggil alat</small>"]
  A --> O["Amati<br/><small>hasilnya</small>"]
  O --> P
  O --> D["Cukup — jawab"]
"""

MMD_LEVELS = """
flowchart LR
  L0["Tanpa rencana<br/><small>pilih langkah demi langkah</small>"]
  L1["Rencana di awal<br/><small>disusun sekali</small>"]
  L2["Rencana + susun ulang<br/><small>diperbarui saat amatan berubah</small>"]
  L0 --> L1 --> L2
  L0 -. "cukup untuk sebagian besar tugas" .-> L0
"""


DECK = {
    "id": "agents06",
    "kind": "chapter",
    "number": 6,
    "book": "agents",
    "title": "Rencana dan refleksi",
    "subtitle": "Memecah tugas sebelum mengerjakannya, dan memperbaiki hasil "
                "sesudahnya — beserta harga keduanya, yang bisa dihitung.",
    "source": book_source(6, "agents"),
    "source_url": "",
    "duration": "3 jam (2 sesi)",
    "presenter": [
        {"name": "Hendri Karisma", "role": "Instructor"},
    ],
    "resources": [
        {"kind": "site", "label": "Course home", "href": "../../index.html"},
        {"kind": "github", "label": "ai-agentic-demo",
         "href": "https://github.com/situkangsayur/ai-agentic-demo"},
        {"kind": "book",
         "label": f"{B['authors']}, {B['title']} ({B['publisher']}, {B['edition']})",
         "href": B["site"]},
    ],
    "objectives": [
        "**Membedakan tiga tingkat perencanaan**, dan menyebutkan kapan yang "
        "paling sederhana sudah cukup.",
        "**Menghitung biaya satu gelung refleksi**, dan menyebutkan syarat "
        "henti yang harus dipasang sebelum menyalakannya.",
        "**Membedakan sinyal dari dunia dan sinyal dari model**, dan "
        "menjelaskan kenapa hanya yang pertama menghasilkan perbaikan terarah.",
        "**Menyebutkan kapan menyusun ulang rencana**, dan kenapa itu perlu "
        "anggarannya sendiri.",
        "**Menyebutkan tiga cara refleksi memperburuk hasil**.",
        "**Merancang perbaikan berkelanjutan yang aman**: apa yang boleh "
        "berubah sendiri dan apa yang harus lewat manusia.",
    ],
    "slides": [
        {"type": "title"},

        {"type": "section", "num": "01", "title": "Merencanakan",
         "lead": "Memecah tugas sebelum mengerjakannya — dan kapan itu justru merugikan."},

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Gelung tanpa rencana tidak tahu kapan ia hampir selesai",
            "blocks": [
                {"t": "mmd", "id": "agents06-planfirst", "src": MMD_PLANFIRST,
                 "cap": "Sama-sama berlangkah; hanya satu yang punya gagasan tentang akhirnya."},
                {"t": "p", "md": "Gelung dasar memilih satu langkah pada satu waktu. Itu "
                                 "cukup untuk banyak tugas, dan punya satu kelemahan yang "
                                 "khas: **tidak ada apa pun di dalamnya yang tahu berapa "
                                 "banyak pekerjaan yang tersisa.** Ia berhenti karena "
                                 "tujuannya tercapai, atau karena anggarannya habis."},
                {"t": "band",
                 "md": "Rencana eksplisit menambahkan satu hal sederhana: **daftar langkah "
                       "yang bisa ditandai selesai.** Dari situ muncul kemajuan yang bisa "
                       "dilaporkan, dan syarat henti yang bukan sekadar anggaran."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Tiga tingkat, dan yang pertama sering sudah cukup",
            "blocks": [
                {"t": "mmd", "id": "agents06-levels", "src": MMD_LEVELS,
                 "cap": "Naik satu tingkat hanya kalau tingkat sebelumnya terbukti gagal."},
                {"t": "table",
                 "head": ["Tingkat", "Cocok kalau", "Harganya"],
                 "widths": [24, 40, 36],
                 "rows": [
                     ["Tanpa rencana", "Langkahnya sedikit dan alatnya jelas",
                      "Tidak ada tambahan"],
                     ["Rencana di awal", "Langkahnya banyak, urutannya penting",
                      "Satu panggilan model tambahan"],
                     ["Rencana + susun ulang", "Amatan sering mengubah arah",
                      "Satu panggilan tiap kali disusun ulang"],
                 ]},
                {"t": "band",
                 "md": "Kesalahan yang paling sering: memasang tingkat ketiga sejak awal "
                       "karena terdengar canggih. **Naiklah satu tingkat hanya setelah "
                       "jejak menunjukkan tingkat sebelumnya gagal**, dan gagal dengan cara "
                       "yang rencana bisa perbaiki."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Rencana yang berguna punya tiga sifat",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "✅", "h": "Bisa ditandai selesai",
                     "p": "Tiap langkah punya kriteria yang jelas. \\u201cPahami "
                          "masalahnya\\u201d tidak bisa ditandai; \\u201cambil mutasi 12 "
                          "bulan\\u201d bisa.",
                     "style": "good"},
                    {"ico": "🔧", "h": "Menyebut alat",
                     "p": "Langkah yang tidak bisa dipetakan ke alat mana pun adalah "
                          "langkah yang tidak bisa dikerjakan.",
                     "style": "good"},
                    {"ico": "📏", "h": "Sedikit",
                     "p": "Rencana dua belas langkah biasanya berarti tugasnya belum "
                          "dipahami, bukan berarti tugasnya besar.",
                     "style": "good"},
                ]},
                {"t": "p", "md": "Kartu kedua yang paling sering dilanggar. Rencana yang "
                                 "berisi langkah tanpa alat menghasilkan agen yang "
                                 "**mengarang kemajuan**: ia menandai langkah selesai "
                                 "padahal tidak ada yang terjadi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Menyusun ulang, dan kenapa itu butuh anggarannya sendiri",
            "blocks": [
                {"t": "mmd", "id": "agents06-replan", "src": MMD_REPLAN,
                 "cap": "Amatan boleh mengubah rencana — tetapi tidak tanpa batas."},
                {"t": "p", "md": "Rencana yang disusun sebelum apa pun diketahui pasti akan "
                                 "salah pada sebagian tugas. Membiarkannya diperbarui saat "
                                 "amatan masuk adalah perbaikan yang nyata."},
                {"t": "band",
                 "md": "Dan ia menciptakan gelung baru yang bisa berputar: **susun rencana, "
                       "kerjakan satu langkah, susun ulang, kerjakan satu langkah…** "
                       "Anggaran penyusunan ulang harus dipasang terpisah dari anggaran "
                       "langkah, atau agen bisa sibuk merencanakan tanpa mengerjakan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Ketika rencana justru merugikan",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "Tugas satu atau dua langkah",
                     "p": "Menyusun rencana untuk sesuatu yang selesai dalam satu panggilan "
                          "alat adalah biaya murni.",
                     "style": "bad"},
                    {"ico": "🌫", "h": "Ketika hasil langkah pertama menentukan segalanya",
                     "p": "Rencana yang disusun sebelum melihat data akan salah, dan "
                          "kesalahannya \\u201cresmi\\u201d — agen cenderung mengikutinya.",
                     "style": "bad"},
                    {"ico": "🧱", "h": "Rencana jadi belenggu",
                     "p": "Agen menandai langkah selesai supaya rencananya habis, bukan "
                          "supaya tugasnya beres.",
                     "style": "bad"},
                    {"ico": "💸", "h": "Konteks bertambah",
                     "p": "Rencana ikut di konteks tiap giliran, dan tiap versi barunya "
                          "menambah lagi."},
                ]},
                {"t": "band",
                 "md": "Kartu ketiga bentuk kegagalan yang halus dan nyata: **rencana "
                       "berubah dari alat bantu jadi definisi keberhasilan.** Terlihat di "
                       "jejak sebagai langkah yang ditandai selesai tanpa panggilan alat "
                       "apa pun."},
            ],
        },

        {"type": "section", "num": "01b", "title": "Memecah dan mengurutkan",
         "lead": "Dua pekerjaan berbeda yang sering dianggap satu."},

        {
            "type": "slide",
            "kicker": "Memecah",
            "title": "Uji yang menentukan sebuah pecahan sudah cukup kecil",
            "blocks": [
                {"t": "mmd", "id": "agents06-decomp", "src": MMD_DECOMP,
                 "cap": "Pecah sampai tiap bagian bisa dipetakan ke satu alat."},
                {"t": "p", "md": "Memecah tugas terdengar seperti keterampilan yang kabur. "
                                 "Sebenarnya ia punya uji yang tegas: **sebuah bagian sudah "
                                 "cukup kecil kalau ia bisa dipetakan ke satu alat dan satu "
                                 "hasil yang bisa diperiksa.** Dan kalau masih ada bagian "
                                 "yang tidak bisa dipetakan ke alat mana pun, yang kurang "
                                 "bukan pemecahannya — ==alatnya yang kurang==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memecah",
            "title": "Dua arah memecah, dan yang salah menghasilkan rencana yang tak terpakai",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Menurut kegiatan** — \u201canalisis, lalu "
                                      "evaluasi, lalu simpulkan\u201d."},
                     {"t": "p", "md": "Terdengar rapi, dan tiap langkahnya tidak bisa "
                                      "ditandai selesai maupun dipetakan ke alat. Ini "
                                      "rencana yang akan dipatuhi secara formalitas."}],
                    [{"t": "p", "md": "**Menurut hasil antara** — \u201cdapatkan mutasi 12 "
                                      "bulan; hitung rasio; ambil klausul yang berlaku\u201d."},
                     {"t": "p", "md": "Tiap langkah punya keluaran yang konkret, punya "
                                      "alatnya, dan gagalnya kelihatan."}],
                ]},
                {"t": "band",
                 "md": "Cara cepat memeriksa rencana yang dihasilkan agen: **bisakah tiap "
                       "langkah gagal dengan cara yang bisa disebutkan?** Kalau tidak, "
                       "langkah itu tidak melakukan apa-apa."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Mengurutkan",
            "title": "Pikir, tindak, amati — dan kenapa urutannya penting",
            "blocks": [
                {"t": "mmd", "id": "agents06-react", "src": MMD_REACT,
                 "cap": "Menuliskan alasan sebelum bertindak membuat alasannya jadi bagian dari perhitungan."},
                {"t": "p", "md": "Model menuliskan apa yang kurang, memanggil alat, lalu "
                                 "membaca hasilnya. Alasannya bukan estetika — **teks yang "
                                 "ditulis jadi konteks untuk langkah berikutnya**, jadi "
                                 "alasan yang ditulis lebih dulu ikut menentukan "
                                 "pilihannya. Karena itu meminta penjelasan ==sesudah== "
                                 "alat dipanggil menghasilkan pembenaran, bukan alasan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Mengurutkan",
            "title": "Bentuk jejak yang membuat sisanya mungkin",
            "blocks": [
                {"t": "p", "md": "Kalau tiap giliran mencatat empat hal yang sama, hampir "
                                 "semua yang dibahas di bab 7 jadi bisa dikerjakan tanpa "
                                 "tambahan apa pun."},
                {"t": "table",
                 "head": ["Dicatat", "Dipakai untuk", "Kalau tidak ada"],
                 "widths": [22, 40, 38],
                 "rows": [
                     ["Alasan singkat", "Menelusuri kenapa alat itu dipilih",
                      "Hanya bisa menebak"],
                     ["Panggilan + argumen", "Menghitung ulang, menguji, mengaudit",
                      "Tidak ada bukti apa yang terjadi"],
                     ["Hasil (atau pengenalnya)", "Memeriksa angka di jawaban",
                      "Angka tanpa asal-usul"],
                     ["Anggaran terpakai", "Melihat bentuk proses, bukan hanya hasilnya",
                      "Biaya jadi kejutan bulanan"],
                 ]},
                {"t": "band",
                 "md": "Empat kolom ini yang membuat demo bisa menjawab pertanyaan "
                       "\u201catas dasar apa\u201d setahun kemudian — dan itu satu-satunya "
                       "bentuk penjelasan yang bertahan di depan pemeriksa."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Mengurutkan",
            "title": "Tiga cara pola ini dipasang, dari yang paling murah",
            "blocks": [
                {"t": "table",
                 "head": ["Cara", "Yang dibutuhkan", "Kapan pantas"],
                 "widths": [24, 38, 38],
                 "rows": [
                     ["Lewat prompt", "Tidak ada",
                      "Hampir selalu — model modern sudah dilatih untuk ini"],
                     ["Penyetelan terbimbing", "Ribuan jejak yang benar",
                      "Kalau domainnya sangat khusus dan polanya sering meleset"],
                     ["Penguatan", "Pemeriksa otomatis + infrastruktur",
                      "Jarang, dan hampir tidak pernah di luar penyedia model"],
                 ]},
                {"t": "p", "md": "Perhatikan kolom terakhir. Untuk hampir semua tim, "
                                 "pertanyaannya bukan **cara mana** — melainkan apakah "
                                 "deskripsi alat dan bentuk jejaknya sudah cukup baik, "
                                 "sebab keduanya memperbaiki hal yang sama dengan biaya "
                                 "yang jauh lebih kecil."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Rencana yang ditunjukkan adalah kontrak dengan penggunanya",
            "blocks": [
                {"t": "p", "md": "Rencana punya kegunaan yang sering terlewat karena bukan "
                                 "soal teknis: ia bisa **ditunjukkan sebelum dikerjakan**. "
                                 "Pengguna melihat empat langkah, menyetujui atau "
                                 "mengoreksi, lalu agen berjalan."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Menyetujui rencana**"},
                     {"t": "p", "md": "Satu keputusan, di depan, ketika biayanya masih nol. "
                                      "Pengguna melihat maksud sistem sebelum ada efek."}],
                    [{"t": "p", "md": "**Menyetujui tiap langkah**"},
                     {"t": "p", "md": "Enam keputusan, tiap kali menunggu. Bab 1 sudah "
                                      "menyebut akibatnya: persetujuan yang terlalu sering "
                                      "berubah jadi klik otomatis."}],
                ]},
                {"t": "band",
                 "md": "Untuk tugas yang punya efek, ini sering **bentuk pengawasan yang "
                       "paling bisa dijalankan**: satu tinjauan yang benar-benar dibaca, "
                       "bukan enam yang tidak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Kenapa langkah yang lebih sedikit hampir selalu menang",
            "blocks": [
                {"t": "p", "md": "Bab 1 menghitungnya: sembilan langkah yang masing-masing "
                                 "benar 95% menghasilkan sistem yang benar sekitar **63%**. "
                                 "Rencana yang panjang bukan tanda ketelitian — ia "
                                 "perkalian peluang gagal."},
                {"t": "steps", "items": [
                    {"h": "Gabungkan langkah yang selalu berurutan",
                     "p": "Kalau dua langkah tidak pernah dipakai terpisah, keduanya satu "
                          "alat yang belum ditulis."},
                    {"h": "Pindahkan yang pasti ke kode",
                     "p": "Aritmetika, penyaringan, pemformatan. Tidak ada langkah rencana "
                          "yang pantas dipakai untuk hal yang deterministik."},
                    {"h": "Periksa di tengah, bukan hanya di ujung",
                     "p": "Satu pemeriksaan setelah langkah ketiga memotong rantai "
                          "kesalahan sebelum ia berlipat."},
                ]},
                {"t": "band",
                 "md": "Ukuran yang berguna dan jarang dipakai: **rerata langkah per tugas "
                       "yang berhasil.** Kalau ia naik dari waktu ke waktu tanpa perubahan "
                       "kode, ada yang bergeser di hulu."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Rencana yang ditulis manusia mengalahkan rencana yang disusun model",
            "blocks": [
                {"t": "p", "md": "Untuk tugas yang **berulang dan bentuknya tetap**, "
                                 "menyusun rencana dengan model tiap kali adalah biaya "
                                 "berulang untuk jawaban yang sudah diketahui."},
                {"t": "table",
                 "head": ["Bentuk tugas", "Rencananya", "Alasannya"],
                 "widths": [30, 26, 44],
                 "rows": [
                     ["Berulang, langkahnya tetap", "**Ditulis, jadi kode**",
                      "Deterministik, gratis, bisa diuji seperti kode biasa"],
                     ["Berulang, urutannya bervariasi", "Cetakan + isian",
                      "Kerangka tetap, bagian yang berubah diisi model"],
                     ["Benar-benar baru tiap kali", "Disusun model",
                      "Di sinilah biayanya sepadan"],
                 ]},
                {"t": "band",
                 "md": "Baris pertama itu tempat sebagian besar pekerjaan bisnis berada, "
                       "dan ia mengembalikan kita ke Bab 1: **kalau langkahnya sudah "
                       "diketahui, yang Anda butuhkan alur tetap, bukan agen.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Rencana",
            "title": "Langkah yang tidak saling bergantung boleh berjalan bersamaan",
            "blocks": [
                {"t": "p", "md": "Rencana membuat satu hal jadi terlihat yang tidak terlihat "
                                 "pada gelung langkah-demi-langkah: **langkah mana yang "
                                 "tidak butuh hasil langkah lain.**"},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Berurutan wajib**"},
                     {"t": "p", "md": "Hitung rasio → ambil kebijakan yang sesuai rasio. "
                                      "Yang kedua butuh yang pertama."}],
                    [{"t": "p", "md": "**Boleh bersamaan**"},
                     {"t": "p", "md": "Ambil data pengajuan, ambil mutasi rekening, ambil "
                                      "riwayat kredit. Tidak ada yang menunggu."}],
                ]},
                {"t": "p", "md": "Menjalankan yang kedua bersamaan memotong waktu dinding "
                                 "tanpa mengurangi token — biayanya sama, jawabannya sama, "
                                 "dan pengalamannya jauh berbeda."},
                {"t": "band",
                 "md": "Syaratnya satu, dan Bab 8 kembali ke sana: **hanya untuk alat "
                       "baca.** Menjalankan alat tulis bersamaan menciptakan pertanyaan "
                       "urutan yang tidak ada jawabannya."},
            ],
        },

        {"type": "section", "num": "02", "title": "Refleksi",
         "lead": "Memeriksa hasil sendiri — dan berapa panggilan yang dibayar untuk itu."},

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Bentuk dasarnya, dan harganya",
            "blocks": [
                {"t": "mmd", "id": "agents06-reflect", "src": MMD_REFLECT,
                 "cap": "Draf, kritik, revisi — dan pertanyaan yang menentukan: cukup?"},
                {"t": "table",
                 "head": ["Putaran refleksi", "Panggilan model", "Biaya relatif"],
                 "widths": [34, 33, 33],
                 "rows": [
                     ["0 — langsung jawab", "1", "1×"],
                     ["1", "3", "**3×**"],
                     ["2", "5", "5×"],
                     ["3", "7", "7×"],
                 ]},
                {"t": "p", "md": "Tiap putaran menambah dua panggilan: satu untuk mengkritik, "
                                 "satu untuk merevisi. Dan tiap panggilan membawa seluruh "
                                 "riwayat yang sudah bertambah — jadi biayanya naik lebih "
                                 "cepat daripada kolom ketiga."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Sinyalnya menentukan apakah ini perbaikan atau perubahan",
            "blocks": [
                {"t": "mmd", "id": "agents06-signal", "src": MMD_SIGNAL,
                 "cap": "Dua sumber kritik, dan hanya satu yang tahu sesuatu."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Sinyal dari dunia** — uji yang gagal, skema yang "
                                      "ditolak, klausul kebijakan yang dilanggar, hitungan "
                                      "yang tidak cocok."},
                     {"t": "p", "md": "Ini memberi tahu **apa** yang salah, jadi revisinya "
                                      "terarah. Di sinilah refleksi benar-benar bekerja."}],
                    [{"t": "p", "md": "**Sinyal dari model sendiri** — model diminta menilai "
                                      "jawabannya sendiri."},
                     {"t": "p", "md": "Model yang tidak tahu jawabannya salah saat menulis "
                                      "juga tidak tahu saat memeriksa. Yang dihasilkan "
                                      "sering **perubahan**, bukan perbaikan."}],
                ]},
                {"t": "band",
                 "md": "Aturan yang menghemat banyak uang: **nyalakan refleksi kalau ada "
                       "pemeriksa; pikir dua kali kalau kritiknya datang dari model yang "
                       "sama.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Tiga cara refleksi memperburuk",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔄", "h": "Berputar tanpa henti",
                     "p": "Kritik selalu bisa menemukan sesuatu. Tanpa syarat henti, "
                          "gelungnya hanya berhenti karena anggaran.",
                     "style": "bad"},
                    {"ico": "📉", "h": "Merevisi yang sudah benar",
                     "p": "Jawaban benar diubah jadi salah karena kritik menuntut "
                          "perubahan. Ini nyata dan sering.",
                     "style": "bad"},
                    {"ico": "🎭", "h": "Yakin yang bertambah, bukan benar",
                     "p": "Jawaban yang sudah melewati tiga revisi terbaca jauh lebih "
                          "meyakinkan, tanpa jaminan lebih tepat.",
                     "style": "bad"},
                ]},
                {"t": "band",
                 "md": "Kartu kedua yang paling merugikan dan paling mudah diukur: "
                       "**bandingkan hasil dengan dan tanpa refleksi pada kumpulan uji yang "
                       "sama.** Kalau ada kasus yang tadinya benar lalu jadi salah, "
                       "refleksinya sedang merusak."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Syarat henti yang harus dipasang sebelum menyalakannya",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Batas putaran, selalu",
                     "p": "Dua biasanya cukup. Tiga jarang menambah apa pun yang bisa "
                          "diukur."},
                    {"h": "Berhenti kalau pemeriksa sudah lulus",
                     "p": "Kalau kriterianya objektif, lulus berarti selesai — tidak perlu "
                          "bertanya apakah masih bisa lebih baik."},
                    {"h": "Berhenti kalau revisinya tidak berubah banyak",
                     "p": "Dua revisi yang nyaris sama berarti gelungnya sudah selesai "
                          "meskipun kritiknya belum kehabisan kata."},
                    {"h": "Simpan versi terbaik, bukan versi terakhir",
                     "p": "Kalau ada pemeriksa yang memberi skor, ambil yang tertinggi. "
                          "Versi terakhir belum tentu versi terbaik."},
                ]},
                {"t": "band",
                 "md": "Langkah keempat sering terlewat dan gratis: tanpa itu, satu revisi "
                       "buruk di akhir membuang seluruh kerja tiga putaran sebelumnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Memperbaiki draf, atau mengingat kegagalan — dua hal berbeda",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Memperbaiki draf**"},
                     {"t": "p", "md": "Kritik dan revisi berlaku pada satu keluaran, lalu "
                                      "dibuang. Tidak ada yang tersisa untuk tugas "
                                      "berikutnya."},
                     {"t": "p", "md": "Murah dipasang, dan cocok untuk keluaran yang punya "
                                      "pemeriksa."}],
                    [{"t": "p", "md": "**Mengingat kegagalan**"},
                     {"t": "p", "md": "Ketika sebuah percobaan gagal, catatan tentang "
                                      "*kenapa* disimpan dan ikut dibaca pada percobaan "
                                      "berikutnya."},
                     {"t": "p", "md": "Lebih kuat pada tugas yang boleh dicoba beberapa "
                                      "kali — dan membawa semua pertanyaan ingatan dari "
                                      "Bab 4."}],
                ]},
                {"t": "band",
                 "md": "Yang kedua sering disalahpahami sebagai \u201cagen yang belajar\u201d. "
                       "Tidak ada bobot yang berubah; yang berubah **isi konteks pada "
                       "percobaan berikutnya**, dan itu bisa dihapus."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Kalau ada pemeriksa, refleksi berubah sifat",
            "blocks": [
                {"t": "p", "md": "Bab 3 menyebut syaratnya: memeriksa harus lebih mudah "
                                 "daripada menjawab. Ketika syarat itu terpenuhi, gelung "
                                 "refleksi berhenti jadi tebakan dan jadi **perbaikan "
                                 "terarah**."},
                {"t": "steps", "items": [
                    {"h": "Jalankan pemeriksanya, bukan tanyakan pendapat model",
                     "p": "Uji yang gagal, skema yang ditolak, klausul yang dilanggar — "
                          "semuanya menyebut apa yang salah."},
                    {"h": "Berikan pesan kegagalannya apa adanya",
                     "p": "Pesan pemeriksa lebih berguna daripada ringkasan tentangnya."},
                    {"h": "Berhenti begitu lulus",
                     "p": "Kriteria objektif berarti tidak perlu bertanya apakah masih bisa "
                          "lebih baik."},
                ]},
                {"t": "band",
                 "md": "Perhatikan bahwa ini persis bentuk yang sudah dipakai pengembang "
                       "perangkat lunak: **jalankan uji, baca kegagalannya, perbaiki, "
                       "ulangi.** Yang berubah hanya siapa yang menulis perbaikannya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Mengukur apakah refleksi Anda menghasilkan sesuatu",
            "blocks": [
                {"t": "table",
                 "head": ["Bandingkan", "Yang dilihat", "Kesimpulan kalau buruk"],
                 "widths": [26, 36, 38],
                 "rows": [
                     ["Tanpa vs 1 putaran", "Tugas benar, biaya, waktu",
                      "Kalau ketepatan tetap, matikan — 3× biaya untuk nol"],
                     ["Kasus yang berubah arah", "Benar → salah",
                      "Ada berarti refleksinya merusak, bukan sekadar tidak menolong"],
                     ["Putaran ke-2 vs ke-1", "Selisihnya",
                      "Hampir selalu kecil; batas dua sudah cukup"],
                     ["Panjang keluaran", "Bertambah tiap putaran?",
                      "Revisi yang hanya memanjangkan bukan revisi"],
                 ]},
                {"t": "p", "md": "Baris kedua yang paling sering mengejutkan tim yang "
                                 "memasang refleksi karena \u201cpasti lebih baik\u201d: "
                                 "**ada kasus yang tadinya benar dan jadi salah**, dan tanpa "
                                 "perbandingan berpasangan itu tidak akan pernah terlihat."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Kritik dari model yang berbeda, bukan dari model yang sama",
            "blocks": [
                {"t": "p", "md": "Kalau kritik memang harus datang dari model, memakai "
                                 "**model yang berbeda** dari yang menulis lebih masuk akal "
                                 "daripada memakai yang sama."},
                {"t": "p", "md": "Alasannya sederhana: kesalahan yang datang dari cara "
                                 "sebuah model memandang masalah cenderung tidak terlihat "
                                 "oleh model itu sendiri, dan lebih mungkin terlihat oleh "
                                 "model yang dilatih berbeda."},
                {"t": "band",
                 "md": "Tetapi hitung dulu ongkosnya: ini menambah **satu penyedia lagi** "
                       "untuk dipantau, dibayar, dan diperbarui. Sering kali pemeriksa "
                       "berupa kode memberi manfaat yang sama dengan harga jauh lebih "
                       "murah — dan hasilnya pasti."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Refleksi",
            "title": "Kapan refleksi jelas sepadan",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🧪", "h": "Keluarannya bisa dijalankan",
                     "p": "Kode, kueri, konfigurasi. Pemeriksanya objektif dan kegagalannya "
                          "menyebut barisnya.",
                     "style": "good"},
                    {"ico": "📐", "h": "Keluarannya harus memenuhi bentuk",
                     "p": "Skema, format laporan, kelengkapan medan. Bisa diperiksa kode, "
                          "dan revisinya terarah.",
                     "style": "good"},
                    {"ico": "💬", "h": "Prosa bebas tanpa kriteria",
                     "p": "Di sini refleksi menghasilkan teks yang berbeda, bukan lebih "
                          "benar — dan tiga kali lebih mahal.",
                     "style": "bad"},
                ]},
                {"t": "p", "md": "Pola yang muncul lagi: **manfaat refleksi hampir "
                                 "seluruhnya berasal dari ada atau tidaknya pemeriksa**, "
                                 "bukan dari kecanggihan gelungnya."},
            ],
        },

        {"type": "section", "num": "03", "title": "Sistem yang memperbaiki diri",
         "lead": "Dan garis yang memisahkan itu dari sistem yang berubah tanpa diawasi."},

        {
            "type": "slide",
            "kicker": "Perbaikan diri",
            "title": "Tiga hal berbeda yang sering disebut dengan satu nama",
            "blocks": [
                {"t": "table",
                 "head": ["Yang berubah", "Umur perubahannya", "Risikonya"],
                 "widths": [30, 30, 40],
                 "rows": [
                     ["Jawaban, dalam satu tugas", "Satu proses",
                      "Rendah — refleksi biasa"],
                     ["Ingatan / catatan", "Antar percakapan",
                      "Sedang — bisa membawa kesalahan ke pengguna lain"],
                     ["**Bobot model**", "Permanen",
                      "Tinggi — dan hampir tidak pernah yang dimaksud orang"],
                 ]},
                {"t": "p", "md": "Ketika orang berkata \\u201cagen yang belajar\\u201d, yang "
                                 "hampir selalu dimaksud adalah baris pertama atau kedua. "
                                 "Baris ketiga menuntut jalur pelatihan, data, dan "
                                 "peninjauan — dan mengubah sistem yang sudah divalidasi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Perbaikan diri",
            "title": "Yang boleh berubah sendiri, dan yang tidak",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Boleh, dengan catatan**"},
                     {"t": "bullets", "items": [
                         "Catatan tentang preferensi pengguna",
                         "Hasil yang mahal dihitung ulang, dengan kedaluwarsa",
                         "Urutan alat yang terbukti lebih cepat",
                     ]}],
                    [{"t": "p", "md": "**Lewat manusia, selalu**"},
                     {"t": "bullets", "items": [
                         "Alat baru atau izin baru",
                         "Aturan kebijakan",
                         "Apa pun yang mengubah batas kemampuan",
                     ]}],
                ]},
                {"t": "band",
                 "md": "Garisnya sama dengan Bab 1 dan tidak bergerak: **sistem boleh "
                       "memperbaiki caranya bekerja; ia tidak boleh memperluas apa yang "
                       "boleh dilakukannya.** Yang kedua adalah keputusan orang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Perbaikan diri",
            "title": "Perbaikan yang paling andal tidak melibatkan model sama sekali",
            "blocks": [
                {"t": "p", "md": "Pola yang jauh lebih sering berhasil daripada sistem yang "
                                 "melatih dirinya: **kumpulkan jejak, temukan pola "
                                 "kegagalan, perbaiki alat dan deskripsinya, jalankan lagi "
                                 "kumpulan uji.**"},
                {"t": "steps", "items": [
                    {"h": "Jejak menunjukkan langkah mana yang paling sering gagal",
                     "p": "Biasanya satu atau dua alat menyumbang sebagian besar kegagalan."},
                    {"h": "Perbaikannya biasanya teks, bukan bobot",
                     "p": "Deskripsi alat, pesan galat, urutan konteks. Semuanya bisa "
                          "ditinjau dan dibatalkan."},
                    {"h": "Kumpulan uji mengatakan apakah berhasil",
                     "p": "Dan menyimpannya sebagai kasus baru mencegah kegagalan yang sama "
                          "kembali."},
                ]},
                {"t": "band",
                 "md": "Ini membosankan, dan itu kelebihannya: **tiap perubahannya bisa "
                       "dibaca, ditinjau, dan dikembalikan** — tiga sifat yang tidak "
                       "dimiliki sistem yang memperbarui bobotnya sendiri."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Perbaikan diri",
            "title": "Melatih diri dari soal yang dibuatnya sendiri",
            "blocks": [
                {"t": "p", "md": "Arah penelitian yang menarik dan pantas dipahami sebelum "
                                 "dipercaya: sistem membuat soal untuk dirinya sendiri, "
                                 "mencoba menjawabnya, memeriksa jawabannya, dan belajar "
                                 "dari yang benar — tanpa data berlabel dari manusia."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [{"t": "p", "md": "**Kenapa bisa bekerja**"},
                     {"t": "p", "md": "Pada domain yang jawabannya bisa diperiksa mesin — "
                                      "matematika, kode — memeriksa memang lebih mudah "
                                      "daripada menjawab, jadi imbalannya bisa dihitung "
                                      "tanpa manusia."}],
                    [{"t": "p", "md": "**Kenapa belum tentu berlaku pada Anda**"},
                     {"t": "p", "md": "Soal yang dibuat sistem cenderung mirip yang sudah "
                                      "bisa dijawabnya, dan tanpa pemeriksa objektif "
                                      "seluruh gelungnya kehilangan jangkarnya."}],
                ]},
                {"t": "band",
                 "md": "Pertanyaan yang memisahkan yang bisa dipakai dari yang belum: "
                       "**apakah domain Anda punya pemeriksa yang tidak melibatkan model?** "
                       "Kalau tidak, sistem yang melatih dirinya sedang menilai dirinya "
                       "dengan alat ukur buatannya sendiri."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Memasang rencana dan refleksi tanpa merusak yang sudah jalan",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Pasang jejaknya dulu",
                     "p": "Empat kolom tadi. Tanpa itu, tidak ada cara mengetahui apakah "
                          "rencana atau refleksi menolong."},
                    {"h": "Tambahkan satu, ukur, baru tambahkan yang lain",
                     "p": "Menyalakan keduanya sekaligus membuat perubahan angka tidak bisa "
                          "diatribusikan."},
                    {"h": "Batasi sejak menit pertama",
                     "p": "Anggaran langkah, anggaran susun-ulang, batas putaran refleksi. "
                          "Ketiganya lebih mudah dipasang sekarang daripada sesudah "
                          "tagihan pertama."},
                    {"h": "Simpan kasus yang berubah arah",
                     "p": "Kasus yang jadi salah setelah refleksi adalah kasus uji terbaik "
                          "yang akan Anda dapatkan."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Empat bentuk kegagalan, dan tandanya di jejak",
            "blocks": [
                {"t": "table",
                 "head": ["Kegagalan", "Tandanya di jejak", "Perbaikannya"],
                 "widths": [26, 38, 36],
                 "rows": [
                     ["Merencanakan tanpa mengerjakan",
                      "Banyak susun-ulang, sedikit panggilan alat",
                      "Anggaran susun-ulang terpisah"],
                     ["Menandai selesai tanpa bukti",
                      "Langkah selesai tanpa panggilan alat di antaranya",
                      "Kriteria selesai harus menyebut alat"],
                     ["Refleksi berputar",
                      "Panjang keluaran naik, isinya berputar",
                      "Batas putaran, dan simpan versi terbaik"],
                     ["Rencana jadi belenggu",
                      "Amatan jelas bertentangan, rencana tetap diikuti",
                      "Izinkan susun ulang, dengan anggarannya"],
                 ]},
                {"t": "p", "md": "Keempatnya terlihat di kolom yang sama — **jejak per "
                                 "giliran** — dan tidak satu pun menimbulkan galat. Pola "
                                 "yang sama seperti bab-bab sebelumnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Kapan tidak usah memasang keduanya",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🎯", "h": "Tugasnya pendek dan jelas",
                     "p": "Dua sampai tiga panggilan alat, urutannya sudah tertentu. "
                          "Rencana dan refleksi hanya menambah biaya dan tempat gagal.",
                     "style": "good"},
                    {"ico": "🧾", "h": "Sudah ada pemeriksa di jalur utama",
                     "p": "Kalau validasi dan aturan kebijakan sudah menolak yang salah, "
                          "sebagian besar manfaat refleksi sudah didapat lebih murah.",
                     "style": "good"},
                ]},
                {"t": "p", "md": "Demo kredit UMKM tidak memakai rencana eksplisit maupun "
                                 "gelung refleksi. Urutannya tetap, tiap langkah punya "
                                 "alatnya, dan pemeriksaannya kode — jadi keduanya akan "
                                 "menambah biaya tanpa menambah apa pun yang bisa diukur."},
                {"t": "band",
                 "md": "Ini kesimpulan yang berulang di seluruh modul, dan pantas diulang: "
                       "**mekanisme yang lebih canggih hampir selalu kalah oleh alat yang "
                       "dirancang lebih baik.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Menilai mutu rencana tanpa menilai jawabannya",
            "blocks": [
                {"t": "p", "md": "Rencana bisa dinilai sendiri, terpisah dari hasil "
                                 "akhirnya — dan itu berguna, sebab rencana yang buruk "
                                 "kadang tetap menghasilkan jawaban benar secara kebetulan."},
                {"t": "table",
                 "head": ["Pertanyaan", "Diperiksa dengan", "Kalau gagal"],
                 "widths": [34, 30, 36],
                 "rows": [
                     ["Tiap langkah punya alat?", "Kode — cocokkan dengan daftar alat",
                      "Rencananya mengandung langkah kosong"],
                     ["Tiap langkah bisa ditandai selesai?", "Kode — ada kriteria?",
                      "Akan ditandai selesai tanpa bukti"],
                     ["Langkahnya sedikit?", "Hitung",
                      "Peluang gagalnya berlipat"],
                     ["Urutannya mungkin?", "Kode — periksa ketergantungan",
                      "Langkah butuh hasil yang belum ada"],
                 ]},
                {"t": "band",
                 "md": "Keempatnya **pemeriksaan kode**, bukan penilaian model — jadi "
                       "keempatnya bisa jadi uji yang berjalan tiap commit, dan tidak "
                       "butuh jaringan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Rencana dan refleksi menambah dua anggaran baru",
            "blocks": [
                {"t": "p", "md": "Bab 1 menyebut enam cara gelung harus bisa berhenti. "
                                 "Memasang rencana dan refleksi menambahkan dua lagi, dan "
                                 "keduanya sering lupa dipasang justru karena terasa "
                                 "seperti fitur, bukan risiko."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🗺", "h": "Anggaran susun-ulang",
                     "p": "Berapa kali rencana boleh diganti dalam satu proses. Tanpa ini, "
                          "agen bisa sibuk merencanakan tanpa pernah mengerjakan.",
                     "style": "accent"},
                    {"ico": "🔁", "h": "Anggaran putaran refleksi",
                     "p": "Berapa kali kritik-revisi boleh berjalan. Kritik selalu bisa "
                          "menemukan sesuatu, jadi tanpa batas ia tidak akan berhenti "
                          "sendiri.",
                     "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Keduanya harus **terpisah** dari anggaran langkah. Kalau digabung, "
                       "proses yang boros merencanakan akan kehabisan langkah sebelum "
                       "mengerjakan apa pun — dan gejalanya terbaca seperti tugasnya "
                       "terlalu sulit."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Praktik",
            "title": "Urutan yang menghemat waktu, sekali lagi dari belakang",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Alat yang baik dulu",
                     "p": "Sebagian besar tugas yang \u201cbutuh perencanaan\u201d "
                          "sebenarnya butuh satu alat yang mengerjakan tiga langkah "
                          "sekaligus."},
                    {"h": "Jejak per giliran",
                     "p": "Tanpa itu, semua yang di bab ini hanya bisa dinilai dari "
                          "perasaan."},
                    {"h": "Pemeriksa, kalau domainnya punya",
                     "p": "Ini yang menentukan apakah refleksi akan berguna atau hanya "
                          "mahal."},
                    {"h": "Baru rencana, baru refleksi",
                     "p": "Satu per satu, dengan pengukuran di antaranya."},
                ]},
                {"t": "band",
                 "md": "Kalau urutan ini diikuti, sebagian tim menemukan bahwa mereka "
                       "**tidak pernah sampai ke langkah keempat** — dan sistemnya sudah "
                       "cukup baik. Itu hasil yang benar, bukan pekerjaan yang belum "
                       "selesai."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Penutup",
            "title": "Yang dibawa pulang dari bab ini",
            "blocks": [
                {"t": "steps", "items": [
                    {"h": "Rencana memberi gagasan tentang akhir",
                     "p": "Tapi naik tingkat hanya setelah jejak menunjukkan tingkat "
                          "sebelumnya gagal."},
                    {"h": "Satu putaran refleksi berharga tiga panggilan",
                     "p": "Dan tiap panggilan membawa riwayat yang lebih panjang, jadi "
                          "biayanya naik lebih cepat daripada hitungan panggilannya."},
                    {"h": "Refleksi bekerja kalau kritiknya datang dari dunia",
                     "p": "Model yang tidak tahu jawabannya salah saat menulis juga tidak "
                          "tahu saat memeriksa."},
                    {"h": "Simpan versi terbaik, bukan versi terakhir",
                     "p": "Gratis, dan menyelamatkan kerja beberapa putaran."},
                    {"h": "Sistem boleh memperbaiki caranya, bukan memperluas izinnya",
                     "p": "Garis yang sama sejak Bab 1, dan ia tidak bergerak."},
                ]},
            ],
            "notes": "Latihan: ambil satu tugas di sistem mereka, jalankan dengan dan tanpa "
                     "satu putaran refleksi, dan hitung tiga angka. Sering hasilnya "
                     "mengejutkan yang mengusulkannya.",
        },
    ],
}
