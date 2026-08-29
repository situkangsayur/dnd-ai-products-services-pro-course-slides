# -*- coding: utf-8 -*-
"""Bab 6 — The universal workflow of machine learning.

Sumber: Chollet & Watson, *Deep Learning with Python*, 3rd ed., bab 6
(hlm. 171-189). Ditulis dari naskah bukunya langsung.

Ini bab yang paling dekat dengan pekerjaan sehari-hari seorang praktisi:
perumusan masalah, pengumpulan data, etika, penyerahan ke produksi, pemantauan,
dan pergeseran konsep. Contoh ambang fraud di bagian 6.3.1 dipakai apa adanya
dari buku -- angka contoh buku, bukan angka organisasi mana pun.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


SVG_WORKFLOW = """
<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Alur kerja universal machine learning: tetapkan tugas, kembangkan model, serahkan">
  <defs>
    <marker id="wf" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.8)"/>
    </marker>
    <marker id="wb" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(245,179,1,.9)"/>
    </marker>
  </defs>

  <rect x="20" y="46" width="222" height="150" rx="12"
        fill="rgba(44,123,212,.12)" stroke="rgba(44,123,212,.6)" stroke-width="1.4"/>
  <text class="d-lbl" x="40" y="72" font-weight="700">1 &#183; Tetapkan tugas</text>
  <text class="d-sm" x="40" y="98">&#183; rumuskan persoalannya</text>
  <text class="d-sm" x="40" y="118">&#183; kumpulkan &amp; anotasi data</text>
  <text class="d-sm" x="40" y="138">&#183; pahami datanya</text>
  <text class="d-sm" x="40" y="158">&#183; pilih ukuran keberhasilan</text>
  <text class="d-sm" x="40" y="182" fill="#F5B301">bagian tersulit</text>

  <rect x="270" y="46" width="222" height="150" rx="12"
        fill="rgba(34,211,238,.12)" stroke="rgba(34,211,238,.6)" stroke-width="1.4"/>
  <text class="d-lbl" x="290" y="72" font-weight="700">2 &#183; Kembangkan model</text>
  <text class="d-sm" x="290" y="98">&#183; siapkan data</text>
  <text class="d-sm" x="290" y="118">&#183; pilih protokol evaluasi</text>
  <text class="d-sm" x="290" y="138">&#183; kalahkan tolok banding</text>
  <text class="d-sm" x="290" y="158">&#183; besarkan sampai overfit</text>
  <text class="d-sm" x="290" y="178">&#183; regularisasi &amp; setel</text>

  <rect x="520" y="46" width="222" height="150" rx="12"
        fill="rgba(123,217,73,.12)" stroke="rgba(123,217,73,.6)" stroke-width="1.4"/>
  <text class="d-lbl" x="540" y="72" font-weight="700">3 &#183; Serahkan</text>
  <text class="d-sm" x="540" y="98">&#183; jelaskan ke pemangku</text>
  <text class="d-sm" x="540" y="118">&#183; kirim model inferensi</text>
  <text class="d-sm" x="540" y="138">&#183; pantau di lapangan</text>
  <text class="d-sm" x="540" y="158">&#183; rawat &amp; kumpulkan data baru</text>

  <path class="d-arrow" d="M242,121 L266,121" marker-end="url(#wf)"/>
  <path class="d-arrow" d="M492,121 L516,121" marker-end="url(#wf)"/>

  <path d="M700,200 C700,244 200,244 132,244 L132,202"
        fill="none" stroke="rgba(245,179,1,.9)" stroke-width="1.8"
        stroke-dasharray="6 4" marker-end="url(#wb)"/>
  <text class="d-sm" x="330" y="262" fill="#F5B301">
    data baru dari produksi &#8212; menjadi bahan generasi model berikutnya
  </text>
  <text class="d-sm" x="20" y="290" fill="#7E93B4">
    Tidak ada model yang bertahan selamanya. Lingkarnya tidak pernah tertutup.
  </text>
</svg>
"""

TIKZ_WORKFLOW = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  ar/.style={-{Stealth[length=4pt]}, signal, line width=0.8pt},
  bk/.style={-{Stealth[length=4pt]}, amberbr, line width=0.9pt, dashed}]
  \node[draw=itbbluelt!70, fill=itbbluelt!10, rounded corners=5pt, minimum width=3.3cm,
        minimum height=2.2cm, anchor=north west, align=left] (a) at (0,0)
    {\textbf{1 $\cdot$ Tetapkan tugas}\\[3pt]
     $\cdot$ rumuskan persoalannya\\$\cdot$ kumpulkan \& anotasi data\\
     $\cdot$ pahami datanya\\$\cdot$ pilih ukuran keberhasilan\\[2pt]
     \textcolor{amber}{bagian tersulit}};
  \node[draw=signal!70, fill=signal!10, rounded corners=5pt, minimum width=3.3cm,
        minimum height=2.2cm, anchor=north west, align=left] (b) at (3.7,0)
    {\textbf{2 $\cdot$ Kembangkan model}\\[3pt]
     $\cdot$ siapkan data\\$\cdot$ pilih protokol evaluasi\\
     $\cdot$ kalahkan tolok banding\\$\cdot$ besarkan sampai overfit\\
     $\cdot$ regularisasi \& setel};
  \node[draw=lime!70, fill=limebr!10, rounded corners=5pt, minimum width=3.3cm,
        minimum height=2.2cm, anchor=north west, align=left] (c) at (7.4,0)
    {\textbf{3 $\cdot$ Serahkan}\\[3pt]
     $\cdot$ jelaskan ke pemangku\\$\cdot$ kirim model inferensi\\
     $\cdot$ pantau di lapangan\\$\cdot$ rawat \& kumpulkan data baru};
  \draw[ar] (a.east) -- (b.west);
  \draw[ar] (b.east) -- (c.west);
  \draw[bk] (c.south) -- ++(0,-0.5) -| (a.south);
  \node[text=amber, anchor=north] at (5.4,-2.75)
    {data baru dari produksi --- menjadi bahan generasi model berikutnya};
\end{tikzpicture}
"""

SVG_DRIFT = """
<svg viewBox="0 0 760 220" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Umur pakai model berbeda-beda menurut kecepatan pergeseran konsep">
  <line x1="120" y1="188" x2="720" y2="188" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>
  <text class="d-sm" x="420" y="212" text-anchor="middle" fill="#7E93B4">
    umur pakai sebelum model harus dilatih ulang
  </text>

  <text class="d-sm" x="112" y="52" text-anchor="end">deteksi fraud kartu</text>
  <rect x="120" y="36" width="70" height="22" rx="5"
        fill="rgba(251,113,133,.22)" stroke="rgba(251,113,133,.75)"/>
  <text class="d-mono" x="204" y="52" fill="#FB7185">hari</text>

  <text class="d-sm" x="112" y="94" text-anchor="end">perekomendasi musik</text>
  <rect x="120" y="78" width="160" height="22" rx="5"
        fill="rgba(245,179,1,.22)" stroke="rgba(245,179,1,.7)"/>
  <text class="d-mono" x="294" y="94" fill="#F5B301">minggu</text>

  <text class="d-sm" x="112" y="136" text-anchor="end">mesin pencari citra</text>
  <rect x="120" y="120" width="480" height="22" rx="5"
        fill="rgba(123,217,73,.20)" stroke="rgba(123,217,73,.65)"/>
  <text class="d-mono" x="614" y="136" fill="#7BD949">beberapa tahun (paling baik)</text>

  <text class="d-sm" x="120" y="172" fill="#F5B301">
    Pergeseran konsep paling tajam di konteks adversarial: pola kecurangan berubah nyaris tiap hari.
  </text>
</svg>
"""

TIKZ_DRIFT = r"""
\begin{tikzpicture}[font=\sffamily\tiny]
  \node[text=ink2, anchor=east] at (0,1.4) {deteksi fraud kartu};
  \node[draw=rose!75, fill=rosebr!22, rounded corners=2.5pt, minimum width=0.8cm,
        minimum height=0.34cm, anchor=west] at (0.15,1.4) {};
  \node[text=rose, anchor=west, font=\ttfamily\tiny] at (1.1,1.4) {hari};

  \node[text=ink2, anchor=east] at (0,0.8) {perekomendasi musik};
  \node[draw=amber!70, fill=amberbr!22, rounded corners=2.5pt, minimum width=1.9cm,
        minimum height=0.34cm, anchor=west] at (0.15,0.8) {};
  \node[text=amber, anchor=west, font=\ttfamily\tiny] at (2.2,0.8) {minggu};

  \node[text=ink2, anchor=east] at (0,0.2) {mesin pencari citra};
  \node[draw=lime!65, fill=limebr!20, rounded corners=2.5pt, minimum width=5.6cm,
        minimum height=0.34cm, anchor=west] at (0.15,0.2) {};
  \node[text=lime, anchor=west, font=\ttfamily\tiny] at (5.9,0.2) {beberapa tahun (paling baik)};

  \draw[rule] (0.15,-0.2) -- (8.6,-0.2);
  \node[text=ink3, anchor=north] at (4.4,-0.3) {umur pakai sebelum model harus dilatih ulang};
  \node[text=amber, anchor=west, align=left] at (-2.4,-1.0)
    {Pergeseran konsep paling tajam di konteks adversarial:\\pola kecurangan berubah nyaris tiap hari.};
\end{tikzpicture}
"""


NB = ["01_memahami_data_sebelum_model.ipynb", "02_pra_pemrosesan_umum.ipynb",
      "03_ekspor_dan_kuantisasi.ipynb"]

DECK = {
    "id": "ch06",
    "kind": "chapter",
    "number": 6,
    "title": "Alur Kerja Universal Machine Learning",
    "subtitle": "Anda tidak memulai dari kumpulan data. Anda memulai dari persoalan -- "
                "dan pekerjaan tersulitnya justru sebelum baris kode pertama.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- bab 6 (hlm. 171-189)",
    "source_url": chapter_url(6),
    "duration": "3 jam (2 sesi)",
    "presenter": {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Pengajar Utama"},
    "resources": chapter_resources(6, local_notebooks=NB),
    "objectives": [
        "Merumuskan sebuah persoalan bisnis menjadi **jenis tugas machine learning** "
        "yang tepat -- termasuk mengenali kapan machine learning **bukan** jawabannya.",
        "Menyebut **dua hipotesis** yang diam-diam Anda buat setiap kali memulai "
        "proyek, dan apa artinya bila keduanya salah.",
        "Merancang pengumpulan dan anotasi data yang **mewakili data produksi**, "
        "dan mengenali **bias pencuplikan**, **kebocoran target**, serta "
        "**pergeseran konsep**.",
        "Memilih ukuran keberhasilan, lalu memilih **aktivasi lapis akhir, fungsi "
        "rugi, dan metrik** yang sepadan dengannya.",
        "Menjalankan tiga tahap pengembangan model: **kalahkan tolok banding → "
        "besarkan sampai overfit → regularisasi dan setel**.",
        "Memilih cara penyerahan -- **REST API, di perangkat, atau di peramban** -- "
        "beserta pengoptimalan inferensinya (pemangkasan dan kuantisasi bobot).",
        "Menyusun **penetapan harapan pemangku kepentingan** dalam bahasa "
        "false-positive dan false-negative, bukan 'akurasi 98%'.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Pembuka",
            "title": "Di dunia nyata, `keras.datasets` tidak ada",
            "blocks": [
                {"t": "lead", "md": "Bayangkan Anda membuka jasa konsultasi machine learning "
                                    "sendiri. Proyeknya mulai berdatangan -- dan ==tidak "
                                    "satu pun datang bersama kumpulan datanya=="},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "🔍", "h": "Pencarian foto",
                     "p": "Ketik *wedding*, dapatkan semua foto pernikahan -- tanpa penandaan "
                          "manual."},
                    {"ico": "🚫", "h": "Spam & konten kasar",
                     "p": "Menandai kiriman pada aplikasi obrolan yang baru tumbuh."},
                    {"ico": "🎵", "h": "Perekomendasi musik",
                     "p": "Untuk pengguna radio daring."},
                    {"ico": "💳", "h": "Fraud kartu kredit",
                     "p": "Untuk sebuah situs niaga elektronik."},
                    {"ico": "📢", "h": "Click-through rate iklan",
                     "p": "Memutuskan iklan mana yang disajikan ke siapa, kapan."},
                    {"ico": "🍪", "h": "Kue cacat",
                     "p": "Menandai kue janggal di ban berjalan pabrik."},
                    {"ico": "🛰", "h": "Situs arkeologi",
                     "p": "Menebak lokasi situs yang belum diketahui dari citra satelit."},
                    {"ico": "🏦", "h": "…dan kasus Anda sendiri",
                     "p": "Yang akan dibawa ke tugas kelompok nanti.", "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Ketujuh contoh ini dipakai berulang sepanjang bab, dan tiap tahap "
                       "alur kerja diuji terhadap ketujuhnya. ==Perhatikan bahwa dua di "
                       "antaranya ternyata bukan persoalan deep learning sama sekali.=="},
            ],
            "notes": "Minta peserta memilih satu kasus dari organisasinya sendiri di awal "
                     "sesi lalu membawanya melewati setiap tahap di bab ini. Itu rangka "
                     "tugas kelompoknya.",
        },

        {
            "type": "slide",
            "kicker": "Peta bab",
            "title": "Tiga bagian, dan yang tersulit ada di depan",
            "blocks": [
                {"t": "fig", "svg": SVG_WORKFLOW, "tikz": TIKZ_WORKFLOW,
                 "cap": "Alur kerja universal -- dan panah balik yang membuatnya tidak "
                        "pernah benar-benar selesai."},
                {"t": "quote",
                 "md": "Pengembangan model hanyalah satu langkah dalam alur kerja machine "
                       "learning, dan menurut kami bukan yang tersulit. Yang paling sulit "
                       "adalah **merumuskan persoalan serta mengumpulkan, menganotasi, dan "
                       "membersihkan data**.",
                 "cite": "Chollet & Watson, bab 6.2"},
            ],
        },

        {"type": "section", "num": "01", "title": "Menetapkan tugas",
         "lead": "Anda tidak bisa bekerja baik tanpa memahami konteksnya secara mendalam."},

        {
            "type": "slide",
            "kicker": "Bagian 6.1.1",
            "title": "Empat pertanyaan yang harus ada di kepala",
            "blocks": [
                {"t": "steps", "items": [
                    "**Apa data masukannya? Apa yang hendak diramalkan?** Anda hanya bisa "
                    "belajar meramalkan sesuatu bila ada data latihnya. ==Ketersediaan data "
                    "biasanya jadi faktor pembatas di tahap ini.==",
                    "**Jenis tugas machine learning apa ini?** Biner? Multikelas? Regresi "
                    "skalar? Segmentasi citra? Perangkingan? Atau -- mungkin saja -- "
                    "**machine learning bukan cara terbaik**, dan analisis statistik biasa "
                    "lebih tepat.",
                    "**Seperti apa penyelesaian yang sudah ada?** Mungkin pelanggan sudah "
                    "punya algoritma buatan tangan dengan banyak `if` bersarang. Mungkin "
                    "ada manusia yang sekarang mengerjakannya secara manual. Pahami sistem "
                    "yang sudah berjalan.",
                    "**Adakah kendala khusus?** Aplikasi terenkripsi ujung-ke-ujung → model "
                    "harus hidup di ponsel pengguna. Kendala latensi ketat → model harus "
                    "jalan di perangkat tertanam di pabrik, bukan di server jauh.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "Perhatikan pertanyaan ketiga. Di banyak proyek nyata, "
                       "==tolok bandingnya bukan 'acak', melainkan sistem berbasis aturan "
                       "yang sudah berjalan bertahun-tahun== -- dan itu jauh lebih sulit "
                       "dikalahkan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.1",
            "title": "Ketujuh contoh, dipetakan ke jenis tugasnya",
            "blocks": [
                {"t": "table",
                 "head": ["Proyek", "Jenis tugasnya", "Catatan"],
                 "widths": [24, 30, 46],
                 "rows": [
                     ["Pencarian foto", "Klasifikasi **multikelas, multilabel**", "—"],
                     ["Spam", "Klasifikasi **biner**",
                      "Jadi **tiga kelas** kalau *konten kasar* dijadikan kelas tersendiri."],
                     ["Perekomendasi musik", "==Bukan deep learning==",
                      "Lebih baik ditangani **faktorisasi matriks** (collaborative filtering)."],
                     ["Fraud kartu kredit", "Klasifikasi **biner**", "—"],
                     ["Click-through rate", "**Regresi skalar**", "—"],
                     ["Kue cacat", "Klasifikasi **biner**",
                      "Tetapi butuh **deteksi objek** dulu untuk memotong kuenya dari citra "
                      "mentah. Catatan buku: teknik yang dikenal sebagai *anomaly detection* "
                      "==justru tidak cocok di sini=="],
                     ["Situs arkeologi", "**Perangkingan kemiripan citra**",
                      "Mengambil citra yang paling mirip situs yang sudah dikenal."],
                 ]},
                {"t": "band",
                 "md": "Dua pelajaran dari tabel ini: ada persoalan yang **bukan** deep "
                       "learning, dan ada persoalan yang **butuh dua model bertahap**. "
                       "Keduanya sering terlewat kalau langsung meloncat ke pemodelan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.1",
            "title": "Dua hipotesis yang selalu Anda buat diam-diam",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "1️⃣", "h": "Target bisa diramalkan dari masukan",
                     "p": "Bahwa hubungan itu memang ada.", "style": "accent"},
                    {"ico": "2️⃣", "h": "Data yang ada cukup informatif",
                     "p": "Untuk mempelajari hubungan antara masukan dan target itu.",
                     "style": "accent"},
                ]},
                {"t": "band", "style": "rose",
                 "md": "Sampai Anda punya model yang bekerja, keduanya **sekadar hipotesis** "
                       "yang menunggu dibuktikan atau digugurkan. Menyusun contoh X dan "
                       "target Y ==tidak berarti X memuat cukup informasi untuk meramal Y=="},
                {"t": "p", "md": "Contoh yang diberikan buku: meramalkan pergerakan saham "
                                 "dari riwayat harganya saja **tidak mungkin berhasil**, "
                                 "sebab riwayat harga tidak memuat banyak informasi yang "
                                 "meramalkan."},
                {"t": "p", "md": "Kalau setelah mencoba beberapa arsitektur yang masuk akal "
                                 "Anda tetap tidak bisa mengalahkan tolok banding sederhana, "
                                 "besar kemungkinan **jawaban atas pertanyaan Anda memang "
                                 "tidak ada di dalam data masukannya**. Kembali ke papan gambar."},
            ],
            "notes": "Ini slide yang menyelamatkan waktu paling banyak. Uji dua hipotesis ini "
                     "di rapat perumusan, bukan setelah tiga bulan pemodelan.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.1 · catatan etika",
            "title": "Teknologi tidak pernah netral",
            "blocks": [
                {"t": "p", "md": "Buku ini menyisipkan satu catatan etika, dan letaknya "
                                 "sengaja di tahap perumusan -- bukan di akhir. Contohnya: "
                                 "*\"membangun AI yang menilai tingkat dapat-dipercayanya "
                                 "seseorang dari foto wajahnya\"*."},
                {"t": "steps", "items": [
                    "**Kesahihannya sendiri meragukan** -- tidak jelas mengapa sifat "
                    "dapat-dipercaya akan tercermin di wajah seseorang.",
                    "Mengumpulkan datanya sama saja dengan **merekam bias dan prasangka "
                    "orang-orang yang melabeli fotonya**.",
                    "Model yang dilatih di atasnya hanya akan **menyandikan bias yang sama "
                    "ke dalam algoritma kotak hitam** -- yang justru memberinya lapisan "
                    "tipis keabsahan.",
                ]},
                {"t": "quote",
                 "md": "Di masyarakat yang sebagian besar belum melek teknologi seperti kita, "
                       "*\"algoritma AI mengatakan orang ini tidak bisa dipercaya\"* anehnya "
                       "terdengar lebih berbobot dan lebih objektif daripada *\"John Smith "
                       "mengatakan orang ini tidak bisa dipercaya\"* -- padahal yang pertama "
                       "adalah hampiran terpelajar atas yang kedua.",
                 "cite": "Chollet & Watson, bab 6.1.1"},
                {"t": "band", "style": "rose",
                 "md": "**Teknologi tidak pernah netral.** Kalau pekerjaan Anda berdampak "
                       "pada dunia, dampak itu punya arah moral: ==pilihan teknis juga "
                       "pilihan etis==. Selalu sengaja memilih nilai apa yang hendak "
                       "didukung pekerjaan Anda."},
            ],
            "notes": "Contoh yang mudah didekatkan ke peserta mana pun: penilaian kelayakan, "
                     "penetapan harga, dan penandaan pelanggan — semuanya bisa mencuci bias "
                     "historis lalu memberinya wajah objektif.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.2",
            "title": "Mengumpulkan data -- bagian termahal, dan yang paling berimbal hasil",
            "blocks": [
                {"t": "quote",
                 "md": "Kalau Anda punya tambahan 50 jam untuk sebuah proyek, kemungkinan "
                       "besar cara paling efektif membelanjakannya adalah **mengumpulkan "
                       "lebih banyak data**, bukan mencari perbaikan pemodelan yang "
                       "sedikit demi sedikit.",
                 "cite": "Chollet & Watson, bab 6.1.2"},
                {"t": "p", "md": "Titik bahwa **data lebih penting daripada algoritma** "
                                 "paling terkenal dikemukakan makalah peneliti Google tahun "
                                 "2009, *\"The Unreasonable Effectiveness of Data\"* -- "
                                 "judulnya memelesetkan buku Eugene Wigner 1960, *The "
                                 "Unreasonable Effectiveness of Mathematics in the Natural "
                                 "Sciences*. Itu ditulis **sebelum** deep learning populer, "
                                 "dan naiknya deep learning ==justru menambah== pentingnya data."},
                {"t": "table",
                 "head": ["Pilihan anotasi", "Untungnya", "Risikonya"],
                 "widths": [26, 36, 38],
                 "rows": [
                     ["**Anotasi sendiri**", "Kendali penuh atas mutu.",
                      "Lambat dan mahal dalam waktu."],
                     ["**Urun daya** (mis. Mechanical Turk)", "Murah dan berskala baik.",
                      "Anotasinya bisa ==cukup berderau=="],
                     ["**Perusahaan pelabelan khusus**", "Menghemat waktu dan biaya.",
                      "Melepaskan kendali."],
                 ]},
                {"t": "bullets", "items": [
                    "Apakah pelabelnya **harus ahli bidang**? Kucing vs anjing bisa siapa "
                    "saja; ras anjing perlu pengetahuan khusus; CT scan patah tulang "
                    "praktis menuntut gelar kedokteran.",
                    "Kalau perlu keahlian, **bisakah orang dilatih** untuk itu? Kalau tidak, "
                    "bagaimana Anda mengakses ahlinya?",
                    "**Apakah Anda sendiri paham** bagaimana ahli itu sampai pada anotasinya? "
                    "Kalau tidak, data Anda jadi kotak hitam dan rekayasa fitur manual "
                    "tertutup -- tidak fatal, tetapi membatasi.",
                    "Perangkat lunak anotasi yang produktif **menghemat sangat banyak waktu**; "
                    "layak diinvestasikan sejak awal proyek.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.2",
            "title": "Data yang tidak mewakili -- dosa besar",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Contoh dari buku.** Aplikasi pengenal masakan "
                                         "dari foto. Model dilatih dengan foto dari jejaring "
                                         "sosial berbagi gambar yang populer di kalangan "
                                         "penggemar kuliner. Akurasi uji jauh di atas 90%."},
                        {"t": "band", "style": "rose",
                         "md": "Setelah dirilis: **salah 8 dari 10 kali**. Foto unggahan "
                               "pengguna -- masakan acak, restoran acak, ponsel acak -- "
                               "==sama sekali tidak menyerupai== foto profesional yang "
                               "pencahayaannya bagus dan menggugah selera itu."},
                    ],
                    [
                        {"t": "p", "md": "**Aturannya**"},
                        {"t": "bullets", "items": [
                            "Bila mungkin, kumpulkan data **langsung dari lingkungan tempat "
                            "model akan dipakai**.",
                            "Model sentimen ulasan film dipakai pada ulasan IMDB baru -- "
                            "bukan pada ulasan restoran Yelp, bukan pada status Twitter.",
                            "Kalau melatih di data produksi tidak mungkin, **pahami betul "
                            "bedanya** dan koreksi perbedaan itu secara aktif.",
                        ]},
                    ],
                ]},
                {"t": "p", "md": "**Bias pencuplikan** adalah bentuknya yang paling licik: "
                                 "proses pengumpulan data berinteraksi dengan hal yang "
                                 "hendak Anda ramalkan. Contoh sejarahnya terkenal -- malam "
                                 "pemilu 1948, *Chicago Tribune* memasang tajuk **\"DEWEY "
                                 "DEFEATS TRUMAN\"**. Paginya Truman yang menang. Redakturnya "
                                 "memercayai survei telepon; padahal pengguna telepon pada "
                                 "1948 ==bukan cuplikan acak yang mewakili pemilih== -- "
                                 "mereka cenderung lebih kaya dan konservatif."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.2",
            "title": "Pergeseran konsep -- dan umur pakai model",
            "blocks": [
                {"t": "fig", "svg": SVG_DRIFT, "tikz": TIKZ_DRIFT,
                 "cap": "Angka-angka ini dari buku. Perhatikan bahwa deteksi fraud -- kasus yang "
                        "paling adversarial -- adalah yang paling cepat basi."},
                {"t": "bullets", "items": [
                    "**Pergeseran konsep** terjadi saat sifat data produksi berubah seiring "
                    "waktu, sehingga akurasi model merosot perlahan.",
                    "Kumpulan IMDB dikumpulkan pada 2011; model yang dilatih di atasnya "
                    "akan bekerja lebih buruk pada ulasan 2020 daripada ulasan 2012 -- "
                    "kosakata, ungkapan, dan genre film berubah.",
                    "Menangani pergeseran yang cepat menuntut **pengumpulan data, anotasi, "
                    "dan pelatihan ulang yang terus-menerus**.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "Kalimat penutupnya keras: memakai machine learning yang dilatih atas "
                       "data masa lalu untuk meramal masa depan berarti **mengandaikan masa "
                       "depan akan berkelakuan seperti masa lalu**. ==Sering kali tidak.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.3",
            "title": "Memahami data Anda -- daftar periksa sebelum melatih",
            "blocks": [
                {"t": "p", "md": "Memperlakukan kumpulan data sebagai kotak hitam adalah "
                                 "**praktik yang buruk**. Sebelum melatih apa pun, jelajahi "
                                 "dan gambarkan datanya."},
                {"t": "steps", "items": [
                    "Ada citra atau teks? **Lihat langsung** beberapa contohnya, berikut "
                    "labelnya.",
                    "Ada fitur numerik? **Gambar histogramnya** untuk merasakan rentang "
                    "nilai dan seberapa sering tiap nilai muncul.",
                    "Ada informasi lokasi? **Petakan**. Apakah ada pola yang muncul?",
                    "Ada sampel yang **nilainya hilang**? Itu harus ditangani saat penyiapan.",
                    "Tugas klasifikasi? **Cetak jumlah contoh tiap kelas.** Kalau tidak "
                    "seimbang, ketidakseimbangan itu harus diperhitungkan.",
                    "Periksa **kebocoran target**.",
                ]},
                {"t": "band", "style": "rose",
                 "md": "**Kebocoran target** -- adanya fitur yang memberi informasi tentang "
                       "target tetapi ==tidak akan tersedia di produksi==. Contoh buku: "
                       "melatih model atas rekam medis untuk meramal apakah seseorang akan "
                       "dirawat karena kanker, sementara rekamnya memuat fitur *\"orang ini "
                       "telah didiagnosis kanker\"*."},
                {"t": "p", "md": "Pertanyaan yang harus selalu Anda ajukan: **apakah setiap "
                                 "fitur dalam data saya akan tersedia dalam bentuk yang sama "
                                 "di produksi?**"},
            ],
            "notes": "Bentuk yang paling sering: kolom yang diisi BELAKANGAN oleh petugas — "
                     "status penanganan, kode penutupan, catatan tindak lanjut. Semuanya "
                     "belum ada saat model harus memutuskan.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.1.4",
            "title": "Memilih ukuran keberhasilan",
            "blocks": [
                {"t": "quote",
                 "md": "Untuk mengendalikan sesuatu, Anda harus bisa mengamatinya. Untuk "
                       "berhasil dalam sebuah proyek, Anda harus lebih dulu menetapkan apa "
                       "yang Anda maksud dengan berhasil.",
                 "cite": "Chollet & Watson, bab 6.1.4"},
                {"t": "table",
                 "head": ["Bentuk persoalan", "Metrik yang lazim"],
                 "widths": [40, 60],
                 "rows": [
                     ["Klasifikasi **seimbang**", "Akurasi, dan **AUC** dari kurva ROC."],
                     ["Kelas **tidak seimbang**, perangkingan, multilabel",
                      "**Presisi dan recall**, atau metrik yang menghitung "
                      "false positive / true positive / false negative / true negative."],
                     ["Bukan salah satu di atas",
                      "Tidak jarang Anda harus **menetapkan metrik sendiri**."],
                 ]},
                {"t": "band",
                 "md": "Metrik keberhasilan **menuntun semua pilihan teknis** sepanjang "
                       "proyek. Ia harus selaras langsung dengan sasaran yang lebih tinggi "
                       "-- yaitu ==keberhasilan bisnis pelanggan Anda==."},
                {"t": "p", "md": "Untuk merasakan keragaman metrik dan kaitannya dengan "
                                 "ranah persoalan, buku menyarankan menjelajahi kompetisi "
                                 "di [Kaggle](https://kaggle.com)."},
            ],
        },

        {"type": "section", "num": "02", "title": "Mengembangkan model",
         "lead": "Bagian yang paling banyak diajarkan tutorial -- dan bukan yang tersulit."},

        {
            "type": "slide",
            "kicker": "Bagian 6.2.1",
            "title": "Menyiapkan data: vektorisasi, normalisasi, nilai hilang",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Vektorisasi.** Semua masukan dan target harus "
                                         "berupa tensor bilangan titik-mengambang (atau, "
                                         "dalam kasus khusus, tensor bilangan bulat atau "
                                         "string). Suara, citra, teks -- semuanya diubah "
                                         "jadi tensor lebih dulu."},
                        {"t": "p", "md": "**Normalisasi nilai.** Tidak aman menyuapkan data "
                                         "bernilai relatif besar (bilangan bulat berdigit "
                                         "banyak, jauh lebih besar dari nilai awal bobot "
                                         "jaringan) atau data yang **heterogen** (satu fitur "
                                         "di 0-1, yang lain di 100-200). Itu memicu "
                                         "pembaruan gradien besar yang ==mencegah jaringan "
                                         "konvergen=="},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "dua sifat yang diinginkan",
                         "src": """# 1. Bernilai kecil - umumnya di rentang 0-1
# 2. Homogen - semua fitur kira-kira
#    dalam rentang yang sama

# praktik yang lebih ketat, sering
# menolong walau tidak selalu perlu:
x -= x.mean(axis=0)   # rerata 0
x /= x.std(axis=0)    # simpangan baku 1
# (x = matriks 2D (samples, features))"""},
                    ],
                ]},
                {"t": "table",
                 "head": ["Nilai hilang pada fitur…", "Yang dilakukan"],
                 "widths": [26, 74],
                 "rows": [
                     ["**Kategorik**",
                      "Aman membuat **kategori baru** yang berarti *nilainya hilang*. "
                      "Model akan belajar sendiri apa artinya terhadap target."],
                     ["**Numerik**",
                      "**Hindari mengisi nilai sembarang seperti 0** -- itu bisa menciptakan "
                      "ketakbersinambungan pada ruang laten. Pakai **rerata atau median** "
                      "fitur itu; atau latih model untuk menebak nilainya dari fitur lain."],
                 ]},
                {"t": "band", "style": "amber",
                 "md": "Jebakan yang halus: kalau Anda **mengharapkan** fitur kategorik "
                       "hilang di data uji tetapi jaringan dilatih tanpa satu pun nilai "
                       "hilang, jaringan ==tidak pernah belajar mengabaikannya==. Obatnya: "
                       "buat sampel latih buatan yang bolong -- salin beberapa sampel, lalu "
                       "buang fitur yang diperkirakan akan hilang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.2.3 · tabel 6.1",
            "title": "Kalahkan tolok banding: tiga hal yang perlu benar",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🧪", "h": "Rekayasa fitur",
                     "p": "Saring fitur yang tidak informatif (seleksi fitur), dan pakai "
                          "pengetahuan Anda tentang persoalan untuk membuat fitur baru.",
                     "style": "accent"},
                    {"ico": "🏛", "h": "Prior arsitektur yang benar",
                     "p": "Jaringan padat? ConvNet? Rekuren? Transformer? Atau -- apakah "
                          "deep learning memang pendekatan yang baik untuk tugas ini?",
                     "style": "accent"},
                    {"ico": "🎛", "h": "Konfigurasi pelatihan yang cukup baik",
                     "p": "Fungsi rugi apa? Ukuran batch dan learning rate berapa?",
                     "style": "accent"},
                ]},
                {"t": "table",
                 "head": ["Tugas", "Aktivasi lapis akhir", "Fungsi rugi", "Metrik"],
                 "widths": [26, 18, 26, 30],
                 "rows": [
                     ["Klasifikasi biner", "Sigmoid", "Binary crossentropy",
                      "Binary accuracy, ROC AUC"],
                     ["Multikelas, label tunggal", "Softmax", "Categorical crossentropy",
                      "Categorical accuracy, top-k, ROC AUC"],
                     ["Multikelas, multilabel", "Sigmoid", "Binary crossentropy",
                      "Binary accuracy, ROC AUC"],
                     ["Regresi", "Tidak ada", "Mean squared error", "Mean absolute error"],
                 ]},
                {"t": "band",
                 "md": "**Mengapa metriknya tidak langsung dioptimalkan?** Fungsi rugi harus "
                       "bisa dihitung hanya dari satu mini-batch (idealnya bahkan dari satu "
                       "titik data) dan harus **terdiferensialkan**. ROC AUC tidak memenuhi "
                       "keduanya, jadi yang dioptimalkan adalah ==pengganti==-nya, biasanya "
                       "crossentropy -- dengan harapan makin rendah crossentropy, makin "
                       "tinggi ROC AUC."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.2.4-6.2.5",
            "title": "Besarkan, lalu regularisasi",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**6.2.4 · Kembangkan model yang overfit**"},
                        {"t": "bullets", "items": [
                            "Tambah lapis.",
                            "Perbesar lapisnya.",
                            "Latih lebih banyak epoch.",
                        ]},
                        {"t": "band",
                         "md": "Model ideal berdiri **tepat di perbatasan** antara underfit "
                               "dan overfit. Untuk tahu di mana perbatasannya, ==Anda harus "
                               "melewatinya lebih dulu.=="},
                    ],
                    [
                        {"t": "p", "md": "**6.2.5 · Regularisasi dan setel** -- tahap yang "
                                         "makan waktu paling banyak"},
                        {"t": "bullets", "items": [
                            "Coba arsitektur berbeda; tambah atau kurangi lapis.",
                            "Tambahkan **dropout**.",
                            "Kalau modelnya kecil, tambahkan **regularisasi L1 atau L2**.",
                            "Coba hiperparameter lain -- jumlah unit per lapis, learning rate.",
                            "Bila perlu, ulangi **kurasi data atau rekayasa fitur**.",
                        ]},
                    ],
                ]},
                {"t": "band", "style": "rose",
                 "md": "Peringatan yang sama, sekali lagi: tiap kali Anda memakai umpan balik "
                       "validasi untuk menyetel model, informasi bocor ke dalam model. "
                       "Beberapa kali tidak apa-apa; **dilakukan sistematis selama banyak "
                       "iterasi, model akan overfit terhadap proses validasi itu sendiri** -- "
                       "walau tidak ada model yang dilatih langsung atas data validasi."},
                {"t": "p", "md": "Sebagian besar pekerjaan ini bisa diotomasi dengan perangkat "
                                 "penyetelan hiperparameter seperti **KerasTuner** (bab 18). "
                                 "Dan bila unjuk kerja di himpunan uji ternyata jauh lebih "
                                 "buruk daripada di validasi: prosedur validasi Anda tidak "
                                 "andal, atau Anda sudah overfit ke data validasi. "
                                 "==Pindah ke protokol yang lebih andal, misalnya K-lipat "
                                 "berulang.=="},
            ],
        },

        {"type": "section", "num": "03", "title": "Menyerahkan model",
         "lead": "Proyek tidak berakhir di notebook Colab yang bisa menyimpan model terlatih."},

        {
            "type": "slide",
            "kicker": "Bagian 6.3.1",
            "title": "Menetapkan harapan -- jangan bilang 'akurasi 98%'",
            "blocks": [
                {"t": "bullets", "items": [
                    "Harapan orang awam terhadap sistem AI sering **tidak realistis**: "
                    "mereka mengira sistem *memahami* tugasnya dan punya akal sehat "
                    "seperti manusia.",
                    "Obatnya: **tunjukkan contoh cara model itu gagal** -- terutama "
                    "kesalahan klasifikasi yang terasa mengejutkan.",
                    "Hindari pernyataan abstrak seperti *\"modelnya berakurasi 98%\"*, yang "
                    "==oleh kebanyakan orang dibulatkan ke 100%== dalam kepala mereka.",
                ]},
                {"t": "band",
                 "md": "Bicaralah dalam **laju false-negative dan false-positive**, lalu "
                       "terjemahkan ke angka harian yang bisa dibayangkan."},
                {"t": "quote",
                 "md": "Dengan setelan ini, model deteksi fraud akan punya laju "
                       "false-negative 5% dan false-positive 2,5%. Setiap hari, rata-rata "
                       "200 transaksi sah akan ditandai sebagai fraud dan dikirim ke "
                       "pemeriksaan manual, dan rata-rata 14 transaksi fraud akan terlewat. "
                       "Rata-rata 266 transaksi fraud akan tertangkap dengan benar.",
                 "cite": "Contoh penetapan harapan dari Chollet & Watson, bab 6.3.1"},
                {"t": "band", "style": "amber",
                 "md": "Bahas juga **pemilihan ambang** bersama pemangku kepentingan -- "
                       "ambang peluang yang berbeda menghasilkan laju false-negative dan "
                       "false-positive yang berbeda. Keputusan itu menyangkut pertukaran "
                       "yang ==hanya bisa ditangani dengan pemahaman mendalam atas konteks "
                       "bisnisnya=="},
            ],
            "notes": "Ini slide yang paling langsung bisa dipakai peserta besok pagi. "
                     "Latihan kelas: tulis ulang satu klaim akurasi dari proyek Anda ke "
                     "dalam bentuk kalimat di atas.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.3.2",
            "title": "Tiga cara menyerahkan model",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🌐", "h": "REST API",
                     "p": "Pakai bila: ada **akses internet andal**; **tidak ada kendala "
                          "latensi ketat** (pulang-pergi sekitar **500 ms**); dan data "
                          "masukannya **tidak sangat peka** -- sebab data harus tersedia "
                          "dalam bentuk terdekripsi di server.",
                     "tag": "pencari citra · perekomendasi · fraud · satelit", "style": "accent"},
                    {"ico": "📱", "h": "Di perangkat",
                     "p": "Pakai bila: **latensi ketat** atau **konektivitas rendah**; model "
                          "bisa dibuat cukup kecil; akurasi tertinggi **bukan** hal kritis; "
                          "dan data masukannya sangat peka sehingga tak boleh didekripsi "
                          "di server jauh.",
                     "tag": "spam terenkripsi · kue di pabrik", "style": "accent"},
                    {"ico": "🖥", "h": "Di peramban",
                     "p": "Pakai bila: ingin **memindahkan komputasi ke pengguna** (biaya "
                          "server turun tajam); data harus tetap di perangkat pengguna; "
                          "latensi ketat (hemat ~100 ms pulang-pergi jaringan); atau aplikasi "
                          "harus tetap jalan **tanpa koneksi**.",
                     "tag": "versi web & desktop aplikasi obrolan", "style": "accent"},
                ]},
                {"t": "band", "style": "rose",
                 "md": "Peringatan untuk penyerahan di peramban: seluruh model **diunduh ke "
                       "perangkat pengguna**. Pastikan tidak ada bagian model yang harus "
                       "dirahasiakan -- sebab dari model terlatih ==biasanya masih mungkin "
                       "memulihkan sebagian informasi tentang data pelatihannya==. Jangan "
                       "publikasikan model yang dilatih atas data peka."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.3.2",
            "title": "Mengekspor model: TensorFlow Serving dan ONNX",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "TensorFlow SavedModel",
                         "src": """model.export("path/to/location",
             format="tf_saved_model")

reloaded = tf.saved_model.load(
    "path/to/location")
predictions = reloaded.serve(input_data)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "ONNX",
                         "src": """model.export("path/to/location",
             format="onnx")

ort_session = onnxruntime.InferenceSession(
    "path/to/location")
predictions = ort_session.run(None, input_data)"""},
                    ],
                ]},
                {"t": "p", "md": "Keduanya bekerja dengan **mengangkat seluruh bobot model "
                                 "dan graf komputasinya keluar dari program Python**, "
                                 "sehingga bisa dilayani dari banyak lingkungan berbeda -- "
                                 "misalnya server C++. Kalau ini terdengar mirip mekanisme "
                                 "kompilasi di bab 3, ==memang begitu==: TensorFlow Serving "
                                 "pada dasarnya pustaka untuk melayani graf `tf.function` "
                                 "dengan sehimpunan bobot tersimpan."},
                {"t": "bullets", "items": [
                    "**TensorFlow Lite** -- inferensi di perangkat: Android, iOS, CPU ARM, "
                    "Raspberry Pi, dan sebagian mikrokontroler. Formatnya sama dengan "
                    "TensorFlow Serving. Runtime ONNX juga bisa jalan di perangkat bergerak.",
                    "**TensorFlow.js** -- menjalankan model di peramban; ia bahkan "
                    "mengimplementasikan hampir seluruh API Keras (nama kerjanya dulu "
                    "*WebKeras*). ONNX punya runtime JavaScript sendiri.",
                    "Pilihan lain: **layanan awan terkelola** seperti Cloud AI Platform, "
                    "yang mengurus pem-batch-an prediksi, penyeimbangan beban, dan penskalaan.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.3.2",
            "title": "Mengoptimalkan model untuk inferensi",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✂", "h": "Pemangkasan bobot (weight pruning)",
                     "p": "Tidak setiap koefisien pada tensor bobot menyumbang sama besar "
                          "terhadap prediksi. Dengan hanya menyimpan yang paling berarti, "
                          "jumlah parameter bisa **turun banyak** dengan ongkos kecil pada "
                          "metrik. Seberapa banyak dipangkas = kendali Anda atas pertukaran "
                          "ukuran lawan akurasi.", "style": "accent"},
                    {"ico": "🔢", "h": "Kuantisasi bobot (weight quantization)",
                     "p": "Model dilatih dengan bobot float32. Bobot itu bisa dikuantisasi "
                          "ke **int8**, menghasilkan model khusus-inferensi yang **empat "
                          "kali lebih kecil** tetapi tetap mendekati akurasi aslinya.",
                     "style": "accent"},
                ]},
                {"t": "code", "lang": "python", "file": "API kuantisasi bawaan Keras",
                 "src": """model.quantize("int8")     # tiap bobot dimampatkan jadi satu byte"""},
                {"t": "band",
                 "md": "Pengoptimalan ini **terutama penting** saat menyerahkan ke lingkungan "
                       "dengan kendala daya dan memori ketat -- ponsel dan perangkat tertanam "
                       "-- atau untuk aplikasi berlatensi rendah. Lakukan ==sebelum== "
                       "mengimpor ke TensorFlow.js atau mengekspor ke TensorFlow Lite."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 6.3.3-6.3.4",
            "title": "Memantau dan merawat -- pekerjaan yang tak berujung",
            "blocks": [
                {"t": "p", "md": "Anda sudah mengekspor model inferensi, memasangkannya ke "
                                 "aplikasi, dan menjalankan uji coba di data produksi. "
                                 "**Bahkan ini belum akhirnya.**"},
                {"t": "steps", "items": [
                    "**Uji A/B teracak.** Sebagian kasus lewat model baru, sebagian lagi "
                    "-- kelompok kendali -- tetap lewat proses lama. Setelah cukup banyak "
                    "kasus, selisih hasilnya ==bisa dikaitkan ke modelnya==, bukan ke "
                    "perubahan lain.",
                    "**Audit manual berkala** atas prediksi di data produksi. Infrastruktur "
                    "anotasi yang sama bisa dipakai ulang: kirim sebagian data produksi "
                    "untuk dianotasi manual, lalu bandingkan.",
                    "**Kalau audit manual mustahil**, cari jalur penilaian lain -- misalnya "
                    "survei pengguna, untuk sistem penandaan spam dan konten kasar.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "**Begitu model diluncurkan, Anda harus sudah bersiap melatih generasi "
                       "berikutnya yang akan menggantikannya.**"},
                {"t": "bullets", "items": [
                    "Awasi **perubahan pada data produksi**. Apakah ada fitur baru? Apakah "
                    "himpunan labelnya perlu diperluas atau diubah?",
                    "Terus kumpulkan dan anotasi data, dan **perbaiki jalur anotasi** dari "
                    "waktu ke waktu.",
                    "Beri perhatian khusus pada **sampel yang tampak sulit diklasifikasikan** "
                    "oleh model sekarang -- sampel itulah yang ==paling mungkin memperbaiki "
                    "unjuk kerja==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Ringkasan",
            "title": "Yang wajib terbawa dari bab 6",
            "blocks": [
                {"t": "steps", "items": [
                    "**Tetapkan tugasnya dulu.** Pahami konteks, tujuan akhir, dan kendalanya; "
                    "kumpulkan dan anotasi data; pilih cara mengukur keberhasilan.",
                    "Anda selalu membuat **dua hipotesis**. Sampai ada model yang bekerja, "
                    "keduanya belum terbukti.",
                    "**Pilihan teknis juga pilihan etis.** Teknologi tidak pernah netral.",
                    "**Data harus mewakili produksi.** Waspadai bias pencuplikan, kebocoran "
                    "target, dan pergeseran konsep.",
                    "**Kalahkan tolok banding → besarkan sampai overfit → regularisasi dan "
                    "setel.** Dalam urutan itu.",
                    "**Serahkan sesuai kendalanya**: REST API, di perangkat, atau di peramban "
                    "-- lalu pangkas dan kuantisasi untuk inferensi.",
                    "**Bicara dalam false-positive dan false-negative**, bukan persen akurasi.",
                    "**Tidak ada model yang bertahan selamanya.** Pantau, audit, dan siapkan "
                    "generasi berikutnya sejak hari peluncuran.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_ekspor_dan_kuantisasi.ipynb",
                     "href": "../../course-slides/notebooks/ch06/03_ekspor_dan_kuantisasi.ipynb"},
                    {"k": "BAB BERIKUT", "ic": "➡", "v": "Bab 7 — Menyelam ke Keras",
                     "href": "../ch07/index.html"},
                ]},
            ],
        },
    ],
}
