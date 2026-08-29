# -*- coding: utf-8 -*-
"""Bab 5 — Fundamentals of machine learning.

Sumber: Chollet & Watson, *Deep Learning with Python*, 3rd ed., bab 5
(hlm. 136-170). Ditulis dari naskah bukunya langsung, bukan ringkasan.

Bab ini yang mengubah "punya model yang jalan" menjadi "punya model yang boleh
dipakai orang lain". Bagian 5.2.3 (kebocoran waktu dan data kembar) adalah
bagian yang paling sering menyelamatkan sebuah proyek dari kegagalan diam-diam.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


SVG_CANON = """
<svg viewBox="0 0 760 280" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Kurva overfitting kanonis: underfitting, robust fit, overfitting">
  <line x1="72" y1="232" x2="712" y2="232" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>
  <line x1="72" y1="24"  x2="72"  y2="232" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>
  <text class="d-sm" x="392" y="262" text-anchor="middle" fill="#7E93B4">waktu pelatihan</text>
  <text class="d-sm" x="26"  y="130" fill="#7E93B4" transform="rotate(-90 26 130)">rugi</text>

  <rect x="72"  y="24" width="150" height="208" fill="rgba(44,123,212,.10)"/>
  <rect x="222" y="24" width="120" height="208" fill="rgba(123,217,73,.10)"/>
  <rect x="342" y="24" width="370" height="208" fill="rgba(251,113,133,.09)"/>

  <text class="d-sm" x="147" y="46" text-anchor="middle" fill="#2C7BD4">underfitting</text>
  <text class="d-sm" x="282" y="46" text-anchor="middle" fill="#7BD949">robust fit</text>
  <text class="d-sm" x="527" y="46" text-anchor="middle" fill="#FB7185">overfitting</text>

  <path d="M72,64 C170,128 250,170 350,192 C460,212 580,222 712,226"
        fill="none" stroke="#22D3EE" stroke-width="2.4"/>
  <path d="M72,76 C150,132 220,158 282,164"
        fill="none" stroke="#FB7185" stroke-width="2.4"/>
  <path d="M282,164 C400,158 560,116 712,58"
        fill="none" stroke="#FB7185" stroke-width="2.4"/>

  <line x1="282" y1="24" x2="282" y2="232"
        stroke="rgba(245,179,1,.75)" stroke-width="1.4" stroke-dasharray="5 4"/>
  <circle cx="282" cy="164" r="5" fill="#F5B301"/>

  <rect x="470" y="240" width="16" height="3" fill="#22D3EE"/>
  <text class="d-sm" x="494" y="246">kurva latih</text>
  <rect x="586" y="240" width="16" height="3" fill="#FB7185"/>
  <text class="d-sm" x="610" y="246">kurva validasi</text>

  <text class="d-sm" x="72" y="272" fill="#F5B301">
    Gambar 5.1 &#8212; pola ini muncul pada SETIAP jenis model dan SETIAP kumpulan data
  </text>
</svg>
"""

TIKZ_CANON = r"""
\begin{tikzpicture}[font=\sffamily\tiny]
  \fill[itbbluelt!8]  (0,0) rectangle (2.6,3.2);
  \fill[limebr!10]    (2.6,0) rectangle (4.0,3.2);
  \fill[rosebr!9]     (4.0,0) rectangle (9.6,3.2);
  \draw[rule, line width=0.8pt] (0,0) -- (9.6,0);
  \draw[rule, line width=0.8pt] (0,0) -- (0,3.2);
  \node[text=ink3, anchor=north] at (4.8,-0.15) {waktu pelatihan};
  \node[text=ink3, rotate=90, anchor=south] at (-0.35,1.6) {rugi};
  \node[text=itbblue] at (1.3,3.0) {underfitting};
  \node[text=lime]    at (3.3,3.0) {robust fit};
  \node[text=rose]    at (6.6,3.0) {overfitting};
  \draw[signal, line width=1.2pt]
    (0,2.75) .. controls (1.6,1.75) and (3.0,1.1) .. (5.0,0.72)
             .. controls (7.0,0.42) and (8.4,0.26) .. (9.6,0.2);
  \draw[rose, line width=1.2pt] (0,2.6) .. controls (1.4,1.7) and (2.4,1.28) .. (3.3,1.18);
  \draw[rose, line width=1.2pt] (3.3,1.18) .. controls (5.2,1.3) and (7.6,2.1) .. (9.6,3.05);
  \draw[amberbr, line width=0.9pt, dashed] (3.3,0) -- (3.3,3.2);
  \fill[amberbr] (3.3,1.18) circle (2.2pt);
  \node[text=amber, anchor=west] at (0,-0.6)
    {Gambar 5.1 --- pola ini muncul pada SETIAP jenis model dan SETIAP kumpulan data};
\end{tikzpicture}
"""

SVG_MANIFOLD = """
<svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Interpolasi pada manifold laten versus interpolasi linear di ruang induk">
  <rect x="30" y="24" width="330" height="176" rx="12" class="d-box"/>
  <text class="d-sm" x="46" y="46" fill="#7E93B4">ruang induk (semua larik 28&#215;28)</text>
  <path d="M70,160 C130,64 240,64 320,148"
        fill="none" stroke="rgba(34,211,238,.8)" stroke-width="2.4"/>
  <circle cx="86"  cy="141" r="6" fill="#22D3EE"/>
  <circle cx="306" cy="133" r="6" fill="#22D3EE"/>
  <circle cx="196" cy="86"  r="5" fill="#7BD949"/>
  <line x1="86" y1="141" x2="306" y2="133"
        stroke="rgba(251,113,133,.85)" stroke-width="1.8" stroke-dasharray="5 4"/>
  <circle cx="196" cy="137" r="5" fill="#FB7185"/>
  <text class="d-sm" x="196" y="76"  text-anchor="middle" fill="#7BD949">angka sah</text>
  <text class="d-sm" x="196" y="160" text-anchor="middle" fill="#FB7185">bukan angka</text>
  <text class="d-sm" x="46" y="188" fill="#22D3EE">manifold laten</text>

  <rect x="392" y="24" width="338" height="176" rx="12" class="d-box"/>
  <text class="d-sm" x="410" y="46" fill="#22D3EE">interpolasi pada manifold</text>
  <text class="d-sm" x="410" y="66">titik antara tetap angka yang sah</text>
  <text class="d-sm" x="410" y="98" fill="#FB7185">interpolasi linear</text>
  <text class="d-sm" x="410" y="118">rerata piksel dua angka</text>
  <text class="d-sm" x="410" y="136">biasanya BUKAN angka</text>
  <line x1="410" y1="152" x2="712" y2="152" stroke="rgba(140,190,255,.2)"/>
  <text class="d-sm" x="410" y="176" fill="#F5B301">Gambar 5.8 &#8212; keduanya sama sekali berbeda</text>

  <text class="d-sm" x="30" y="228" fill="#7E93B4">
    256^784 larik mungkin &#8212; jauh lebih banyak dari jumlah atom di alam semesta.
  </text>
  <text class="d-sm" x="30" y="244" fill="#7E93B4">
    Yang benar-benar berupa tulisan tangan hanya menempati sepetak kecil, dan petak itu bersinambung.
  </text>
</svg>
"""

TIKZ_MANIFOLD = r"""
\begin{tikzpicture}[font=\sffamily\tiny]
  \node[draw=rule, fill=papertint, rounded corners=4pt, minimum width=4.6cm,
        minimum height=2.5cm] (p) at (0,0) {};
  \node[text=ink3, anchor=north west] at ($(p.north west)+(0.15,-0.1)$)
    {ruang induk (semua larik $28\times28$)};
  \draw[signal, line width=1.1pt] (-1.7,-0.75) .. controls (-0.8,0.5) and (0.8,0.5) .. (1.75,-0.55);
  \fill[signal] (-1.55,-0.5) circle (2.4pt);
  \fill[signal] (1.6,-0.42) circle (2.4pt);
  \fill[lime]   (0.0,0.22) circle (2.0pt);
  \draw[rose, line width=0.9pt, dashed] (-1.55,-0.5) -- (1.6,-0.42);
  \fill[rose]   (0.0,-0.46) circle (2.0pt);
  \node[text=lime, anchor=south] at (0,0.32) {angka sah};
  \node[text=rose, anchor=north] at (0,-0.56) {bukan angka};
  \node[text=signal, anchor=south west] at ($(p.south west)+(0.15,0.1)$) {manifold laten};

  \node[draw=rule, fill=papertint, rounded corners=4pt, minimum width=4.8cm,
        minimum height=2.5cm, anchor=west] (q) at (2.7,0) {};
  \node[anchor=north west, align=left, text=ink2] at ($(q.north west)+(0.18,-0.12)$)
    {\textcolor{signal}{\bfseries interpolasi pada manifold}\\
     titik antara tetap angka yang sah\\[3pt]
     \textcolor{rose}{\bfseries interpolasi linear}\\
     rerata piksel dua angka\\
     biasanya BUKAN angka};
  \node[text=amber, anchor=south west] at ($(q.south west)+(0.18,0.1)$)
    {Gambar 5.8 --- keduanya sama sekali berbeda};

  \node[text=ink3, anchor=north west, align=left] at (-2.4,-1.45)
    {$256^{784}$ larik mungkin --- jauh lebih banyak dari jumlah atom di alam semesta.\\
     Yang benar-benar berupa tulisan tangan hanya menempati sepetak kecil, dan petak itu bersinambung.};
\end{tikzpicture}
"""

SVG_SPLIT = """
<svg viewBox="0 0 760 200" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Pembagian latih, validasi, uji, dan arah kebocoran informasi">
  <rect x="30" y="40" width="380" height="34" rx="7"
        fill="rgba(34,211,238,.16)" stroke="rgba(34,211,238,.6)" stroke-width="1.3"/>
  <text class="d-sm" x="220" y="62" text-anchor="middle">latih &#8212; model dipasangkan ke sini</text>

  <rect x="418" y="40" width="180" height="34" rx="7"
        fill="rgba(245,179,1,.16)" stroke="rgba(245,179,1,.6)" stroke-width="1.3"/>
  <text class="d-sm" x="508" y="62" text-anchor="middle">validasi</text>

  <rect x="606" y="40" width="124" height="34" rx="7"
        fill="rgba(123,217,73,.16)" stroke="rgba(123,217,73,.6)" stroke-width="1.3"/>
  <text class="d-sm" x="668" y="62" text-anchor="middle">uji</text>

  <path d="M508,84 C508,104 260,104 240,104" fill="none"
        stroke="rgba(245,179,1,.85)" stroke-width="1.6" stroke-dasharray="5 4"/>
  <text class="d-sm" x="300" y="122" fill="#F5B301">
    tiap kali hiperparameter disetel, sedikit informasi validasi BOCOR ke model
  </text>

  <rect x="30" y="140" width="700" height="46" rx="10"
        fill="rgba(123,217,73,.06)" stroke="rgba(123,217,73,.35)" stroke-width="1.2"/>
  <text class="d-sm" x="50" y="162" fill="#7BD949">
    Data uji dipakai SEKALI, di akhir. Kalau ada satu saja setelan yang dipilih
  </text>
  <text class="d-sm" x="50" y="180" fill="#7BD949">
    berdasarkan skor uji, ukuran generalisasi Anda sudah cacat.
  </text>
</svg>
"""

TIKZ_SPLIT = r"""
\begin{tikzpicture}[font=\sffamily\tiny]
  \node[draw=signal!60, fill=signal!16, rounded corners=3pt, minimum width=4.8cm,
        minimum height=0.5cm, text=ink] (tr) at (0,0) {latih --- model dipasangkan ke sini};
  \node[draw=amber!60, fill=amberbr!16, rounded corners=3pt, minimum width=2.3cm,
        minimum height=0.5cm, text=ink, anchor=west] (va) at (2.55,0) {validasi};
  \node[draw=lime!60, fill=limebr!16, rounded corners=3pt, minimum width=1.6cm,
        minimum height=0.5cm, text=ink, anchor=west] (te) at (5.0,0) {uji};
  \draw[amberbr, line width=0.9pt, dashed] (va.south) .. controls +(0,-0.5) and +(0,-0.5) .. (0.4,-0.25);
  \node[text=amber, anchor=west] at (-0.6,-0.95)
    {tiap kali hiperparameter disetel, sedikit informasi validasi BOCOR ke model};
  \node[draw=lime!45, fill=limebr!7, rounded corners=4pt, minimum width=9.0cm,
        minimum height=0.75cm, text=lime, align=left, anchor=north west] at (-2.4,-1.35)
    {~Data uji dipakai SEKALI, di akhir. Kalau ada satu saja setelan yang dipilih\\
     ~berdasarkan skor uji, ukuran generalisasi Anda sudah cacat.};
\end{tikzpicture}
"""

SVG_DROPOUT = """
<svg viewBox="0 0 760 200" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Dropout 50 persen pada matriks aktivasi, lalu diskalakan">
  <text class="d-sm" x="30" y="26" fill="#7E93B4">keluaran lapis</text>
  <g class="d-mono" font-family="JetBrains Mono, monospace" font-size="12" fill="#EAF2FF">
    <text x="34" y="56">0.3  0.2  1.5  0.0</text>
    <text x="34" y="80">0.6  0.1  0.0  0.3</text>
    <text x="34" y="104">0.2  1.9  0.3  1.2</text>
    <text x="34" y="128">0.7  0.5  1.0  0.0</text>
  </g>
  <rect x="24" y="38" width="172" height="102" rx="8" class="d-box"/>

  <text class="d-sm" x="216" y="88" fill="#F5B301">50% dropout</text>
  <path d="M212,96 L262,96" stroke="rgba(245,179,1,.85)" stroke-width="1.6"/>

  <g font-family="JetBrains Mono, monospace" font-size="12">
    <text x="286" y="56"  fill="#FB7185">0.0</text><text x="322" y="56"  fill="#EAF2FF">0.2  1.5</text><text x="404" y="56" fill="#FB7185">0.0</text>
    <text x="286" y="80"  fill="#EAF2FF">0.6  0.1</text><text x="368" y="80" fill="#FB7185">0.0</text><text x="404" y="80" fill="#EAF2FF">0.3</text>
    <text x="286" y="104" fill="#FB7185">0.0</text><text x="322" y="104" fill="#EAF2FF">1.9  0.3</text><text x="404" y="104" fill="#FB7185">0.0</text>
    <text x="286" y="128" fill="#EAF2FF">0.7</text><text x="322" y="128" fill="#FB7185">0.0  0.0  0.0</text>
  </g>
  <rect x="276" y="38" width="172" height="102" rx="8" class="d-box-a"/>

  <text class="d-lbl" x="470" y="94" fill="#7BD949">&#215; 2</text>

  <rect x="512" y="38" width="218" height="102" rx="8"
        fill="rgba(123,217,73,.10)" stroke="rgba(123,217,73,.5)" stroke-width="1.3"/>
  <text class="d-sm" x="532" y="64">diskalakan naik saat LATIH,</text>
  <text class="d-sm" x="532" y="84">supaya saat UJI matriksnya</text>
  <text class="d-sm" x="532" y="104">tidak perlu diubah sama sekali</text>
  <text class="d-mono" x="532" y="126" fill="#7BD949">layer_output /= 0.5</text>

  <text class="d-sm" x="30" y="172" fill="#F5B301">
    Gambar 5.21 &#8212; laju dropout lazimnya 0,2 sampai 0,5
  </text>
  <text class="d-sm" x="30" y="190" fill="#7E93B4">
    Saat uji tidak ada unit yang dijatuhkan.
  </text>
</svg>
"""

TIKZ_DROPOUT = r"""
\begin{tikzpicture}[font=\sffamily\tiny]
  \node[draw=rule, fill=papertint, rounded corners=3pt, minimum width=2.6cm,
        minimum height=1.5cm, text=ink, font=\ttfamily\tiny, align=left] (a) at (0,0)
    {0.3~~0.2~~1.5~~0.0\\0.6~~0.1~~0.0~~0.3\\0.2~~1.9~~0.3~~1.2\\0.7~~0.5~~1.0~~0.0};
  \node[text=ink3, anchor=south] at (a.north) {keluaran lapis};
  \node[text=amber] at (1.85,0.2) {50\% dropout};
  \draw[amberbr, line width=0.9pt, -{Stealth[length=4pt]}] (1.4,-0.15) -- (2.35,-0.15);
  \node[draw=signal!60, fill=signal!9, rounded corners=3pt, minimum width=2.6cm,
        minimum height=1.5cm, text=ink, font=\ttfamily\tiny, align=left] (b) at (3.9,0)
    {\textcolor{rose}{0.0}~~0.2~~1.5~~\textcolor{rose}{0.0}\\
     0.6~~0.1~~\textcolor{rose}{0.0}~~0.3\\
     \textcolor{rose}{0.0}~~1.9~~0.3~~\textcolor{rose}{0.0}\\
     0.7~~\textcolor{rose}{0.0}~~\textcolor{rose}{0.0}~~\textcolor{rose}{0.0}};
  \node[text=lime, font=\small] at (5.5,0) {$\times 2$};
  \node[draw=lime!50, fill=limebr!10, rounded corners=3pt, minimum width=3.3cm,
        minimum height=1.5cm, text=ink2, align=left, anchor=west] at (6.1,0)
    {diskalakan naik saat LATIH,\\supaya saat UJI matriksnya\\tidak perlu diubah sama sekali\\[2pt]
     \textcolor{lime}{\ttfamily layer\_output /= 0.5}};
  \node[text=amber, anchor=west] at (-1.5,-1.15)
    {Gambar 5.21 --- laju dropout lazimnya 0,2 sampai 0,5. Saat uji tidak ada unit yang dijatuhkan.};
\end{tikzpicture}
"""


NB = ["01_korelasi_semu_dan_derau.ipynb", "02_label_diacak_manifold.ipynb",
      "03_protokol_evaluasi.ipynb", "04_kapasitas_model.ipynb",
      "05_regularisasi_l2_dropout.ipynb"]

DECK = {
    "id": "ch05",
    "kind": "chapter",
    "number": 5,
    "title": "Dasar-Dasar Machine Learning",
    "subtitle": "Ketegangan antara optimalisasi dan generalisasi -- mengapa ia tak "
                "terhindarkan, bagaimana mengukurnya, dan apa saja yang benar-benar "
                "menolong.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- bab 5 (hlm. 136-170)",
    "source_url": chapter_url(5),
    "duration": "3 jam (2 sesi)",
    "presenter": {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Pengajar Utama"},
    "resources": chapter_resources(5, local_notebooks=NB),
    "objectives": [
        "Merumuskan **ketegangan optimalisasi vs generalisasi**, dan menyebut tiga "
        "penyebab overfitting: data berderau, fitur ambigu, dan fitur langka.",
        "Menjelaskan **hipotesis manifold** dan mengapa generalisasi deep learning "
        "adalah *interpolasi*, bukan penalaran.",
        "Memilih protokol evaluasi yang tepat -- **hold-out, K-lipat, K-lipat "
        "berulang** -- dan menghindari tiga jebakannya.",
        "Menetapkan **tolok banding akal sehat** sebelum melatih apa pun.",
        "Mendiagnosis tiga kegagalan pelatihan: **tidak mulai, tidak menggeneralisasi, "
        "tidak bisa overfit** -- dan tahu obat masing-masing.",
        "Menerapkan **kurasi data, rekayasa fitur, early stopping, pengurangan "
        "kapasitas, regularisasi bobot, dan dropout**, serta tahu kapan masing-masing "
        "yang tepat.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Peta bab",
            "title": "Dari 'modelnya jalan' ke 'modelnya boleh dipakai'",
            "blocks": [
                {"t": "lead", "md": "Bab 4 memperkenalkan overfitting sebagai kejadian. "
                                    "Bab 5 menjadikannya ==kerangka berpikir==, dan hampir "
                                    "semua praktik baik di sisa buku ini adalah cara "
                                    "menangani satu ketegangan yang sama."},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "🎯", "h": "5.1 · Generalisasi",
                     "p": "Apa yang menyebabkan overfitting, dan mengapa deep learning "
                          "bisa menggeneralisasi sama sekali.", "style": "accent"},
                    {"ico": "📐", "h": "5.2 · Menilai model",
                     "p": "Tiga protokol, tolok banding akal sehat, dan tiga jebakan yang "
                          "membatalkan penilaian.", "style": "accent"},
                    {"ico": "🔧", "h": "5.3 · Memperbaiki fit",
                     "p": "Tiga kegagalan pelatihan dan obatnya. Sasarannya: **bisa** "
                          "overfit dulu.", "style": "accent"},
                    {"ico": "🛡", "h": "5.4 · Memperbaiki generalisasi",
                     "p": "Kurasi data, rekayasa fitur, early stopping, dan tiga cara "
                          "regularisasi.", "style": "accent"},
                ]},
                {"t": "quote",
                 "md": "Persoalan pokok dalam machine learning adalah ketegangan antara "
                       "**optimalisasi** dan **generalisasi**. Tujuannya jelas generalisasi "
                       "yang baik -- tetapi Anda tidak mengendalikan generalisasi; yang bisa "
                       "Anda lakukan hanya memasangkan model ke data latihnya.",
                 "cite": "Chollet & Watson, bab 5.1"},
            ],
            "notes": "Kalimat kuncinya: 'Anda tidak mengendalikan generalisasi.' Semua "
                     "teknik di bab ini adalah cara tidak langsung — tak satu pun mengatur "
                     "generalisasi secara langsung.",
        },

        {"type": "section", "num": "01", "title": "Generalisasi: tujuan machine learning",
         "lead": "Mengapa overfitting terjadi di setiap persoalan, tanpa kecuali."},

        {
            "type": "slide",
            "kicker": "Bagian 5.1.1",
            "title": "Kurva kanonis -- dan ia berlaku universal",
            "blocks": [
                {"t": "fig", "svg": SVG_CANON, "tikz": TIKZ_CANON,
                 "cap": "Gambar 5.1 -- di awal, optimalisasi dan generalisasi berjalan "
                        "searah. Setelah sekian iterasi, keduanya berpisah."},
                {"t": "bullets", "items": [
                    "**Underfit** -- masih ada kemajuan yang bisa diraih; model belum "
                    "menangkap semua pola yang relevan.",
                    "**Robust fit** -- titik terbaik. Sempit, dan hanya terlihat lewat "
                    "metrik validasi.",
                    "**Overfit** -- model mulai mempelajari pola yang ==khas data latih== "
                    "tetapi menyesatkan pada data baru.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.1.1",
            "title": "Tiga penyebab overfitting",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🌫", "h": "1 · Data berderau",
                     "p": "Masukan tak sah (citra MNIST hitam seluruhnya), dan yang lebih "
                          "buruk: masukan sah yang **salah label**. Model yang memaksa "
                          "mencakup pencilan ini akan salah pada data mirip.",
                     "style": "warn"},
                    {"ico": "🌗", "h": "2 · Fitur ambigu",
                     "p": "Data bersih pun bisa berderau bila persoalannya memang tak "
                          "pasti. Pisang *mentah* vs *matang* tak punya batas objektif; "
                          "tekanan udara yang sama kadang diikuti hujan, kadang tidak.",
                     "style": "warn"},
                    {"ico": "🔍", "h": "3 · Fitur langka & korelasi semu",
                     "p": "Kata *cherimoya* muncul sekali, kebetulan di ulasan negatif → "
                          "model memberinya bobot besar. **Tidak perlu langka-langka amat**: "
                          "kata yang muncul 100 kali dengan 54% positif sudah cukup.",
                     "style": "bad"},
                ]},
                {"t": "band", "style": "rose",
                 "md": "Selisih 54% lawan 46% itu bisa saja ==kebetulan statistik murni==. "
                       "Model tetap akan memakainya. Chollet menyebut ini **salah satu "
                       "sumber overfitting yang paling umum**."},
            ],
            "notes": "Contoh setara di data operasional: kode cabang atau jam transaksi "
                     "yang kebetulan berkorelasi dengan label di data historis.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.1.1 · listing 5.1-5.3",
            "title": "Percobaan: tambahkan derau murni, akurasi turun",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 5.1 — dua kumpulan pembanding",
                 "src": """(train_images, train_labels), _ = mnist.load_data()
train_images = train_images.reshape((60000, 28 * 28)).astype("float32") / 255

# 784 kanal derau putih ditempelkan - separuh data kini derau
train_images_with_noise_channels = np.concatenate(
    [train_images, np.random.random((len(train_images), 784))], axis=1)

# pembanding: 784 kanal nol, sama-sama tidak informatif
train_images_with_zeros_channels = np.concatenate(
    [train_images, np.zeros((len(train_images), 784))], axis=1)"""},
                {"t": "cols", "ratio": "3-2", "cols": [
                    [
                        {"t": "p", "md": "Kandungan informasinya **identik** pada kedua "
                                         "kumpulan. Manusia tidak akan terpengaruh sama "
                                         "sekali oleh penambahan ini."},
                        {"t": "band", "style": "rose",
                         "md": "Tetapi akurasi validasi model yang dilatih dengan kanal "
                               "derau berakhir ==sekitar satu poin persen lebih rendah== -- "
                               "murni akibat korelasi semu. Makin banyak kanal derau, makin "
                               "jauh merosotnya."},
                    ],
                    [
                        {"t": "stats", "cols": 1, "items": [
                            {"v": "−1 poin", "l": "akurasi validasi, hanya karena derau ditempelkan"},
                        ]},
                    ],
                ]},
                {"t": "p", "md": "Obatnya: **seleksi fitur**. Hitung skor kegunaan tiap "
                                 "fitur -- misalnya *mutual information* antara fitur dan "
                                 "label -- lalu simpan yang di atas ambang. Membatasi IMDB "
                                 "ke 10.000 kata tersering di bab 4 adalah bentuk kasarnya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.1.2 · listing 5.4",
            "title": "Model bisa memasangkan diri ke APA SAJA",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 5.4 — label diacak",
                 "src": """random_train_labels = train_labels[:]        # salin
np.random.shuffle(random_train_labels)       # putus semua hubungan masukan-target

model = keras.Sequential([
    layers.Dense(512, activation="relu"),
    layers.Dense(10, activation="softmax"),
])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_images, random_train_labels,
          epochs=100, batch_size=128, validation_split=0.2)"""},
                {"t": "out", "src": """rugi latih  : turun terus, mulus
akurasi validasi: bertahan di ~10%  (= tolok banding acak untuk 10 kelas)"""},
                {"t": "band", "style": "amber",
                 "md": "Rugi latih tetap turun walau **tidak ada hubungan apa pun** antara "
                       "masukan dan label. Model hanya ==menghafal, seperti kamus Python==. "
                       "Jadi: kemampuan memasangkan diri bukan bukti bahwa persoalannya "
                       "bisa diselesaikan."},
                {"t": "p", "md": "Kalau begitu, mengapa deep learning menggeneralisasi sama "
                                 "sekali? Jawabannya, kata Chollet, **sedikit sekali "
                                 "berkaitan dengan modelnya**, dan banyak berkaitan dengan "
                                 "struktur informasi di dunia nyata."},
            ],
            "notes": "Ini slide diagnostik yang paling berguna: kalau rugi latih turun tapi "
                     "validasi mandek di tolok banding, persoalannya bukan model — datanya "
                     "memang tidak memuat jawabannya.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.1.2",
            "title": "Hipotesis manifold",
            "blocks": [
                {"t": "fig", "svg": SVG_MANIFOLD, "tikz": TIKZ_MANIFOLD,
                 "cap": "Gambar 5.7-5.8 -- angka tulisan tangan membentuk manifold di dalam "
                        "ruang semua larik 28×28 yang mungkin."},
                {"t": "quote",
                 "md": "Hipotesis manifold menyatakan bahwa semua data alami terletak pada "
                       "manifold berdimensi rendah di dalam ruang berdimensi tinggi tempat "
                       "ia disandikan.",
                 "cite": "Chollet & Watson, bab 5.1.2"},
                {"t": "bullets", "items": [
                    "**Manifold** = subruang berdimensi lebih rendah yang secara setempat "
                    "menyerupai ruang linear. Kurva mulus di bidang adalah manifold 1D "
                    "dalam ruang 2D.",
                    "Ia **bersinambung**: ubah satu sampel sedikit, ia tetap angka yang "
                    "sama. Dua angka mana pun dihubungkan oleh ==lintasan mulus==.",
                    "Berlaku untuk MNIST, wajah manusia, bentuk pohon, suara manusia, "
                    "bahkan bahasa alami.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.1.2",
            "title": "Interpolasi -- dan batasnya",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Yang bisa dilakukan model**"},
                        {"t": "bullets", "items": [
                            "Memahami titik yang belum pernah dilihat dengan **mengaitkannya "
                            "ke titik terdekat** di manifold.",
                            "Memahami keseluruhan ruang hanya dari sebagian sampelnya -- "
                            "*mengisi bagian yang kosong*.",
                            "Chollet menyebutnya **generalisasi setempat**.",
                        ]},
                    ],
                    [
                        {"t": "p", "md": "**Yang tidak bisa**"},
                        {"t": "bullets", "items": [
                            "**Generalisasi ekstrem** -- yang manusia lakukan setiap hari.",
                            "Anda bisa berpindah seminggu di NYC, seminggu di Shanghai, "
                            "seminggu di Bangalore ==tanpa ribuan kali seumur hidup "
                            "berlatih untuk tiap kota==.",
                            "Itu ditopang abstraksi, model simbolik, penalaran, logika, "
                            "akal sehat -- yang kita sebut **nalar**, bukan intuisi.",
                        ]},
                    ],
                ]},
                {"t": "band",
                 "md": "Peringatan Chollet: interpolasi hanya ==puncak gunung es==. "
                       "Menganggap interpolasi sama dengan seluruh generalisasi adalah "
                       "kekeliruan. Bab 19 kembali ke sini."},
                {"t": "p", "md": "Perhatikan juga: interpolasi **pada manifold laten** "
                                 "berbeda dari interpolasi linear di ruang induk. Rerata "
                                 "piksel dua angka MNIST biasanya ==bukan angka yang sah==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.1.2",
            "title": "Mengapa deep learning bekerja -- dan syaratnya",
            "blocks": [
                {"t": "p", "md": "Model deep learning pada dasarnya adalah **kurva berdimensi "
                                 "sangat tinggi** yang mulus dan bersinambung (ia harus "
                                 "terdiferensialkan), dipasangkan ke titik data secara "
                                 "bertahap lewat penurunan gradien."},
                {"t": "steps", "items": [
                    "Kurva itu punya cukup parameter untuk memasangkan diri ke **apa saja** "
                    "-- kalau dibiarkan cukup lama, ia murni menghafal.",
                    "Tetapi data yang dipasangkan **bukan titik-titik terpencar**; ia "
                    "membentuk manifold berdimensi rendah yang sangat terstruktur.",
                    "Karena pemasangannya berlangsung ==bertahap dan mulus==, ada titik di "
                    "tengah pelatihan saat kurva model kira-kira menghampiri manifold "
                    "alami data itu (gambar 5.10).",
                ]},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "〰", "h": "Sifat 1 · pemetaan mulus dan bersinambung",
                     "p": "Wajib, karena harus terdiferensialkan. Kemulusan itu justru yang "
                          "membantu menghampiri manifold laten.", "style": "good"},
                    {"ico": "🏗", "h": "Sifat 2 · prior arsitektur",
                     "p": "Strukturnya mencerminkan 'bentuk' informasi pada datanya -- "
                          "terutama pada model citra (bab 8-12) dan model deret (bab 13).",
                     "style": "good"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.1.3",
            "title": "Data latih adalah yang terpenting",
            "blocks": [
                {"t": "quote",
                 "md": "Satu-satunya yang akan Anda temukan di dalam model deep learning "
                       "adalah apa yang Anda masukkan ke dalamnya: prior yang tersandi di "
                       "arsitekturnya, dan data yang dipakai melatihnya.",
                 "cite": "Chollet & Watson, bab 5.1.3"},
                {"t": "bullets", "items": [
                    "Kemampuan menggeneralisasi lebih merupakan akibat **struktur alami "
                    "data** ketimbang sifat model.",
                    "Deep learning adalah pemasangan kurva, jadi ia butuh **pencuplikan "
                    "yang padat** atas ruang masukannya -- terutama di dekat batas keputusan "
                    "(gambar 5.11).",
                    "Cuplikan jarang → kurva yang dipelajari tidak cocok dengan ruang laten, "
                    "dan ==interpolasinya salah==.",
                    "Karena itu: **cara terbaik memperbaiki model adalah melatihnya dengan "
                    "lebih banyak data, atau data yang lebih baik**.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "Kalau menambah data tidak mungkin, pilihan terbaik berikutnya adalah "
                       "==membatasi banyaknya informasi yang boleh disimpan model==, atau "
                       "menambah kekangan pada kemulusan kurvanya. Itulah **regularisasi**, "
                       "dan itu isi bagian 5.4.4."},
            ],
        },

        {"type": "section", "num": "02", "title": "Menilai model machine learning",
         "lead": "Anda hanya bisa mengendalikan yang bisa Anda amati."},

        {
            "type": "slide",
            "kicker": "Bagian 5.2.1",
            "title": "Mengapa dua himpunan tidak cukup",
            "blocks": [
                {"t": "fig", "svg": SVG_SPLIT, "tikz": TIKZ_SPLIT,
                 "cap": "Menyetel hiperparameter berdasarkan skor validasi adalah bentuk "
                        "pembelajaran juga -- dan karenanya bisa overfit ke himpunan validasi."},
                {"t": "bullets", "items": [
                    "**Hiperparameter** (jumlah lapis, ukuran lapis) berbeda dari "
                    "**parameter** (bobot). Yang pertama Anda setel; yang kedua dipelajari.",
                    "Tiap kali Anda menyetel satu hiperparameter berdasarkan skor validasi, "
                    "==sedikit informasi tentang data validasi bocor ke model==.",
                    "Sekali dua kali tidak apa-apa. Diulang berkali-kali, himpunan validasi "
                    "berhenti menjadi ukuran yang jujur.",
                    "Karena itu perlu himpunan ketiga: **data uji**, yang modelnya belum "
                    "pernah menyentuhnya, bahkan tidak langsung.",
                ]},
            ],
            "notes": "Untuk audit internal, ini bagian yang perlu dituliskan sebagai "
                     "prosedur: siapa boleh melihat data uji, dan berapa kali.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.2.1 · listing 5.5-5.6",
            "title": "Tiga protokol evaluasi",
            "blocks": [
                {"t": "table",
                 "head": ["Protokol", "Cara kerjanya", "Kapan dipakai", "Biayanya"],
                 "widths": [22, 34, 26, 18],
                 "rows": [
                     ["**Hold-out sederhana**",
                      "Sisihkan sebagian sebagai uji; sisanya dibagi latih dan validasi.",
                      "Data banyak.",
                      "1 model"],
                     ["**K-lipat**",
                      "Bagi jadi K bagian sama besar; tiap bagian sekali jadi validasi; "
                      "skornya dirata-ratakan.",
                      "Skor sangat berayun bergantung belahan.",
                      "K model"],
                     ["**K-lipat berulang, diacak**",
                      "Jalankan K-lipat P kali, acak ulang tiap kali.",
                      "Data sedikit dan penilaian harus setepat mungkin.",
                      "P × K model"],
                 ]},
                {"t": "code", "lang": "python", "file": "listing 5.6 — inti K-lipat",
                 "src": """k = 3
num_validation_samples = len(data) // k
np.random.shuffle(data)
validation_scores = []
for fold in range(k):
    validation_data = data[num_validation_samples * fold :
                           num_validation_samples * (fold + 1)]
    training_data = np.concatenate(
        [data[: num_validation_samples * fold],
         data[num_validation_samples * (fold + 1) :]])
    model = get_model()              # instans BARU, belum terlatih, tiap lipatan
    model.fit(training_data, ...)
    validation_scores.append(model.evaluate(validation_data, ...))

validation_score = np.average(validation_scores)
model = get_model()
model.fit(data, ...)                 # model akhir: dilatih di SEMUA data non-uji
test_score = model.evaluate(test_data, ...)"""},
                {"t": "band",
                 "md": "Perhatikan `model = get_model()` di dalam gelung: tiap lipatan wajib "
                       "memakai ==instans yang benar-benar baru==. Memakai ulang model yang "
                       "sudah terlatih membatalkan seluruh penilaian."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.2.2",
            "title": "Tolok banding akal sehat: altimeter roket yang tak terlihat",
            "blocks": [
                {"t": "quote",
                 "md": "Melatih model deep learning itu seperti menekan tombol yang "
                       "meluncurkan roket di dunia paralel. Anda tak bisa mendengarnya, tak "
                       "bisa melihatnya. Satu-satunya umpan balik yang Anda punya adalah "
                       "metrik validasi -- seperti altimeter pada roket yang tak terlihat itu.",
                 "cite": "Chollet & Watson, bab 5.2.2"},
                {"t": "table",
                 "head": ["Persoalan", "Tolok banding akal sehat", "Alasannya"],
                 "widths": [26, 22, 52],
                 "rows": [
                     ["MNIST", "**> 0,10**", "Penebak acak atas 10 kelas seimbang."],
                     ["IMDB", "**> 0,50**", "Dua kelas, seimbang 50:50."],
                     ["Reuters", "**≈ 0,18-0,19**", "46 kelas, tetapi sebarannya tidak rata."],
                     ["Biner 90:10", "**> 0,90**", "Penebak yang selalu menjawab kelas A "
                      "sudah dapat 0,90. Anda harus melampauinya."],
                 ]},
                {"t": "band", "style": "rose",
                 "md": "Kalau Anda **tidak bisa mengalahkan penyelesaian sepele**, model Anda "
                       "tidak berharga. Mungkin modelnya salah, atau -- dan ini yang sering "
                       "-- ==persoalannya memang tidak bisa didekati dengan machine learning==. "
                       "Kembali ke papan gambar."},
            ],
            "notes": "Slide ini yang paling sering menyelamatkan anggaran. Minta peserta "
                     "menuliskan tolok banding untuk kasusnya sendiri SEBELUM melatih apa pun.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.2.3",
            "title": "Tiga jebakan yang membatalkan penilaian",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🎲", "h": "1 · Keterwakilan data",
                     "p": "Data terurut menurut kelas, lalu 80% pertama diambil sebagai "
                          "latih → latih hanya berisi kelas 0-7, uji hanya 8-9. "
                          "*Kelihatannya konyol, tetapi mengejutkan seringnya.* "
                          "**Obatnya: acak sebelum membelah.**", "style": "warn"},
                    {"ico": "⏳", "h": "2 · Anak panah waktu",
                     "p": "Meramal masa depan dari masa lalu? **Jangan diacak.** "
                          "Mengacak menciptakan ==kebocoran waktu==: model dilatih dengan "
                          "data dari masa depan. Semua data uji harus lebih baru dari "
                          "data latih.", "style": "bad"},
                    {"ico": "👯", "h": "3 · Data kembar",
                     "p": "Titik data yang muncul dua kali -- lazim pada data dunia nyata. "
                          "Setelah diacak, salinannya tersebar ke latih dan validasi: "
                          "Anda menguji di atas data latih sendiri. **Yang terburuk dari "
                          "semuanya.**", "style": "bad"},
                ]},
                {"t": "band", "style": "amber",
                 "md": "Pada data transaksional, jebakan **2 dan 3** hampir selalu muncul bersamaan: "
                       "derenya bersifat temporal, dan subjek yang sama muncul "
                       "berkali-kali. Membelah secara acak per baris ==melanggar keduanya=="
                       " dalam satu langkah."},
            ],
        },

        {"type": "section", "num": "03", "title": "Memperbaiki fit",
         "lead": "Untuk mencapai fit yang pas, Anda harus overfit dulu."},

        {
            "type": "slide",
            "kicker": "Bagian 5.3",
            "title": "Tiga kegagalan, tiga obat",
            "blocks": [
                {"t": "quote",
                 "md": "Untuk mencapai fit yang sempurna, Anda harus overfit lebih dulu. "
                       "Karena Anda tidak tahu di mana batasnya, Anda harus melewatinya "
                       "untuk menemukannya.",
                 "cite": "Chollet & Watson, bab 5.3"},
                {"t": "table",
                 "head": ["Gejalanya", "Artinya", "Yang dicoba"],
                 "widths": [30, 28, 42],
                 "rows": [
                     ["**Pelatihan tidak mulai** -- rugi latih tidak turun",
                      "Setelan penurunan gradien salah.",
                      "Setel **learning rate** (turunkan atau naikkan) dan **ukuran batch**. "
                      "Yang lain dibiarkan tetap."],
                     ["**Mulai, tetapi tidak menggeneralisasi** -- tolok banding tak terkalahkan",
                      "Ada yang salah secara mendasar.",
                      "Mungkin datanya **tidak memuat informasi** untuk meramal targetnya; "
                      "atau **prior arsitekturnya salah** untuk jenis data ini."],
                     ["**Menggeneralisasi, tetapi tidak bisa overfit**",
                      "Kapasitas kurang.",
                      "Tambah lapis, perbesar lapis, atau pakai **jenis lapis yang lebih "
                      "cocok**."],
                 ]},
                {"t": "band", "style": "rose",
                 "md": "Kegagalan kedua adalah **situasi terburuk** dalam machine learning: "
                       "ia menandakan ada yang salah secara mendasar, dan ==sering tidak "
                       "mudah dikenali apanya==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.3.1 · listing 5.7-5.8",
            "title": "Learning rate: satu angka yang menghentikan segalanya",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "listing 5.7 — terlalu besar",
                         "src": """model.compile(
    optimizer=keras.optimizers.RMSprop(
        learning_rate=1.0),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])
model.fit(train_images, train_labels,
          epochs=10, batch_size=128,
          validation_split=0.2)"""},
                        {"t": "out", "src": """akurasi mentok di 20%-40%
dan tidak mau lewat dari situ"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 5.8 — wajar",
                         "src": """model.compile(
    optimizer=keras.optimizers.RMSprop(
        learning_rate=1e-2),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])
model.fit(train_images, train_labels,
          epochs=10, batch_size=128,
          validation_split=0.2)"""},
                        {"t": "out", "src": """model sekarang bisa dilatih"""},
                    ],
                ]},
                {"t": "bullets", "items": [
                    "Learning rate **terlalu tinggi** → pembaruan melampaui jauh titik yang "
                    "pas; hasilnya seperti di kiri.",
                    "**Terlalu rendah** → pelatihan begitu lambat sampai ==tampak macet==, "
                    "padahal sebetulnya jalan.",
                    "**Perbesar ukuran batch** → gradien lebih informatif dan kurang berisik "
                    "(ragamnya lebih rendah).",
                ]},
                {"t": "band",
                 "md": "Semua parameter ini saling bergantung. Chollet menyarankan: cukup "
                       "setel ==learning rate dan ukuran batch saja==, sisanya biarkan tetap."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.3.3 · listing 5.9",
            "title": "Kapasitas: terlalu kecil, pas, terlalu besar",
            "blocks": [
                {"t": "table",
                 "head": ["Model", "Arsitektur", "Yang terjadi", "Gambar"],
                 "widths": [22, 30, 36, 12],
                 "rows": [
                     ["**Kapasitas kurang**", "`Dense(10, softmax)` saja -- regresi logistik",
                      "Rugi validasi turun ke 0,26 lalu **diam di situ**. Bisa fit, tetapi "
                      "==tidak bisa jelas-jelas overfit==.", "5.14"],
                     ["**Kapasitas pas**", "2 × `Dense(128, relu)`",
                      "Fit cepat, mulai overfit **setelah 8 epoch**. Persis seperti seharusnya.",
                      "5.15"],
                     ["**Kapasitas berlebih**", "3 × `Dense(2048, relu)`",
                      "Overfit **langsung sejak awal**; rugi latih hampir nol dengan cepat, "
                      "rugi validasi berisik.", "5.16"],
                 ]},
                {"t": "code", "lang": "python", "file": "listing 5.9 — kapasitas kurang",
                 "src": """model = keras.Sequential([layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
history_small_model = model.fit(train_images, train_labels,
                                epochs=20, batch_size=128, validation_split=0.2)

# catatan: saat melatih model besar, kecilkan batch_size agar memori tidak jebol
#          (batch_size=32 pada versi 3 x 2048 unit)"""},
                {"t": "band",
                 "md": "Alur kerjanya: **mulai dari sedikit lapis dan parameter, lalu "
                       "besarkan sampai rugi validasi berhenti membaik**. Tidak ada rumus "
                       "ajaib untuk menebak ukuran yang benar -- ==harus dicoba, di himpunan "
                       "validasi, bukan di himpunan uji==."},
            ],
        },

        {"type": "section", "num": "04", "title": "Memperbaiki generalisasi",
         "lead": "Lima cara, berurut dari yang paling berdampak."},

        {
            "type": "slide",
            "kicker": "Bagian 5.4.1",
            "title": "Kurasi data -- imbal hasil terbesar, dan sering dilewati",
            "blocks": [
                {"t": "quote",
                 "md": "Deep learning adalah pemasangan kurva, bukan sihir.",
                 "cite": "Chollet & Watson, bab 5.4.1"},
                {"t": "band",
                 "md": "Mengeluarkan lebih banyak tenaga dan uang untuk **pengumpulan data** "
                       "hampir selalu memberi imbal hasil ==jauh lebih besar== daripada "
                       "jumlah yang sama untuk mengembangkan model yang lebih baik."},
                {"t": "steps", "items": [
                    "**Pastikan datanya cukup.** Anda butuh pencuplikan yang padat atas ruang "
                    "masukan-silang-keluaran. Persoalan yang tampak mustahil kadang jadi bisa "
                    "diselesaikan begitu datanya lebih banyak.",
                    "**Kecilkan galat pelabelan.** Lihat sendiri masukannya untuk mencari "
                    "kejanggalan; periksa ulang labelnya.",
                    "**Bersihkan data dan tangani nilai yang hilang.** (Bab 6 membahasnya.)",
                    "**Lakukan seleksi fitur** kalau fiturnya banyak dan Anda belum yakin "
                    "mana yang berguna.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "Batasnya jelas: kalau persoalannya **terlalu berderau atau pada "
                       "dasarnya diskret** -- misalnya mengurutkan senarai -- deep learning "
                       "==tidak akan menolong==, seberapa pun datanya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.4.2",
            "title": "Rekayasa fitur: contoh jam dinding",
            "blocks": [
                {"t": "table",
                 "head": ["Tingkat", "Masukannya", "Yang dibutuhkan"],
                 "widths": [26, 38, 36],
                 "rows": [
                     ["**Data mentah**", "Kisi piksel citra jam",
                      "ConvNet, dan sumber daya komputasi yang tidak sedikit."],
                     ["**Fitur lebih baik**", "Koordinat (x, y) ujung tiap jarum",
                      "Algoritma machine learning sederhana sudah cukup."],
                     ["**Lebih baik lagi**", "Sudut θ tiap jarum (koordinat polar)",
                      "==Tidak perlu machine learning sama sekali== -- cukup pembulatan "
                      "dan pencarian di kamus."],
                 ]},
                {"t": "p", "md": "Itulah inti rekayasa fitur: **membuat persoalan lebih mudah "
                                 "dengan menyatakannya secara lebih sederhana**. Membuat "
                                 "manifold latennya lebih mulus, lebih sederhana, lebih rapi. "
                                 "Ia menuntut pemahaman mendalam atas persoalannya."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🪶", "h": "Tetap berguna — alasan 1",
                     "p": "Fitur yang baik menyelesaikan persoalan **dengan sumber daya "
                          "lebih sedikit**. Memakai ConvNet untuk membaca jam dinding itu "
                          "konyol.", "style": "good"},
                    {"ico": "📉", "h": "Tetap berguna — alasan 2",
                     "p": "Fitur yang baik menyelesaikan persoalan dengan **data jauh lebih "
                          "sedikit**. Kemampuan model menemukan fiturnya sendiri bergantung "
                          "pada tersedianya banyak data latih.", "style": "good"},
                ]},
                {"t": "band",
                 "md": "Sebelum deep learning, rekayasa fitur adalah **bagian terpenting** "
                       "alur kerja machine learning. Solusi MNIST dulu dibangun dari fitur "
                       "yang ditulis tangan: jumlah gelung pada citra angka, tinggi tiap "
                       "angka, histogram nilai piksel."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.4.3",
            "title": "Early stopping",
            "blocks": [
                {"t": "p", "md": "Model deep learning **selalu berparameter berlebihan**: "
                                 "derajat kebebasannya jauh melebihi yang minimal diperlukan. "
                                 "Itu bukan masalah, sebab Anda ==tidak pernah memasangkannya "
                                 "sampai penuh==. Pelatihan selalu dihentikan jauh sebelum "
                                 "rugi latih minimum tercapai."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Cara di bab 4** -- latih lebih lama dari perlu "
                                         "untuk menemukan epoch terbaik, lalu latih model "
                                         "baru tepat sebanyak epoch itu."},
                        {"t": "band", "style": "amber",
                         "md": "Lazim, tetapi menuntut ==pekerjaan berulang== yang kadang "
                               "mahal."},
                    ],
                    [
                        {"t": "p", "md": "**Cara yang lebih baik** -- simpan model tiap akhir "
                                         "epoch, lalu pakai yang terbaik. Di Keras ini "
                                         "dikerjakan callback `EarlyStopping`, yang "
                                         "menghentikan pelatihan begitu metrik validasi "
                                         "berhenti membaik **sambil mengingat keadaan model "
                                         "terbaik**."},
                        {"t": "band",
                         "md": "Callback dibahas penuh di **bab 7**."},
                    ],
                ]},
                {"t": "p", "md": "Menemukan titik persis saat fit paling bisa "
                                 "digeneralisasi -- batas antara kurva underfit dan overfit "
                                 "-- adalah **salah satu hal paling ampuh** yang bisa Anda "
                                 "lakukan untuk memperbaiki generalisasi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.4.4 · listing 5.10-5.12",
            "title": "Regularisasi 1: kecilkan modelnya",
            "blocks": [
                {"t": "p", "md": "Kalau model punya sumber daya penghafalan yang terbatas, ia "
                                 "==terpaksa mempelajari representasi terpadat yang punya "
                                 "daya ramal== -- persis jenis representasi yang kita "
                                 "inginkan."},
                {"t": "table",
                 "head": ["Versi", "Lapis antara", "Mulai overfit", "Perilakunya", "Gambar"],
                 "widths": [18, 20, 16, 34, 12],
                 "rows": [
                     ["**Acuan**", "2 × `Dense(16)`", "epoch 4", "Titik banding.", "—"],
                     ["**Lebih kecil**", "2 × `Dense(4)`", "epoch 6",
                      "Mulai overfit lebih lambat, dan **memburuknya lebih pelan**.", "5.18"],
                     ["**Jauh lebih besar**", "2 × `Dense(512)`", "epoch 1",
                      "Overfit hampir seketika dan jauh lebih parah; rugi validasinya juga "
                      "lebih berisik.", "5.19"],
                 ]},
                {"t": "band", "style": "amber",
                 "md": "Tidak ada rumus ajaib untuk ukuran yang benar. Alur kerjanya: "
                       "**mulai dari sedikit, besarkan sampai imbal hasil rugi validasi "
                       "mengecil** -- dan lakukan itu di ==himpunan validasi, tentu saja, "
                       "bukan himpunan uji==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.4.4 · listing 5.13-5.14",
            "title": "Regularisasi 2: kekang bobotnya (L1 / L2)",
            "blocks": [
                {"t": "quote",
                 "md": "Pisau cukur Occam: diberi dua penjelasan atas suatu hal, yang paling "
                       "mungkin benar adalah yang paling sederhana -- yang paling sedikit "
                       "andaiannya.",
                 "cite": "Prinsip yang dipakai Chollet untuk membenarkan regularisasi bobot"},
                {"t": "code", "lang": "python", "file": "listing 5.13-5.14",
                 "src": """from keras.regularizers import l2
from keras import regularizers

model = keras.Sequential([
    layers.Dense(16, kernel_regularizer=l2(0.002), activation="relu"),
    layers.Dense(16, kernel_regularizer=l2(0.002), activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])

# pilihan lain:
regularizers.l1(0.001)                     # L1
regularizers.l1_l2(l1=0.001, l2=0.001)     # L1 dan L2 sekaligus"""},
                {"t": "table",
                 "head": ["Jenis", "Biaya yang ditambahkan ke rugi", "Efeknya"],
                 "widths": [16, 46, 38],
                 "rows": [
                     ["**L1**", "Sebanding dengan **nilai mutlak** koefisien bobot (norma L1).",
                      "Mendorong bobot menjadi **jarang** (banyak yang nol)."],
                     ["**L2**", "Sebanding dengan **kuadrat** koefisien bobot (norma L2).",
                      "Mendorong semua bobot menjadi kecil. Disebut juga **weight decay** -- "
                      "namanya beda, matematikanya sama."],
                 ]},
                {"t": "band",
                 "md": "`l2(0.002)` berarti tiap koefisien menambahkan "
                       "`0.002 * nilai_bobot ** 2` ke rugi total. Denda ini hanya "
                       "ditambahkan **saat latih**, jadi ==rugi saat latih akan tampak jauh "
                       "lebih tinggi daripada saat uji== -- dan itu normal, bukan bug."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.4.4 · listing 5.15",
            "title": "Regularisasi 3: dropout",
            "blocks": [
                {"t": "fig", "svg": SVG_DROPOUT, "tikz": TIKZ_DROPOUT,
                 "cap": "Gambar 5.21 -- dropout pada matriks aktivasi saat latih, dengan "
                        "penskalaan dikerjakan saat latih juga."},
                {"t": "code", "lang": "python", "file": "listing 5.15 — dropout pada model IMDB",
                 "src": """model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(16, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(1, activation="sigmoid"),
])"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.4.4",
            "title": "Dari mana ide dropout datang -- kisah Hinton dan bank",
            "blocks": [
                {"t": "quote",
                 "md": "Saya pergi ke bank saya. Tellernya berganti terus dan saya tanya "
                       "salah satunya kenapa. Dia bilang tidak tahu, tetapi mereka memang "
                       "sering dipindah-pindah. Saya kira itu pasti karena menipu bank "
                       "memerlukan kerja sama antar-pegawai. Dari situ saya sadar bahwa "
                       "membuang subhimpunan neuron yang berbeda secara acak pada tiap "
                       "contoh akan mencegah persekongkolan, dan dengan begitu mengurangi "
                       "overfitting.",
                 "cite": "Geoff Hinton, dikutip Chollet & Watson, bab 5.4.4"},
                {"t": "band",
                 "md": "Gagasan intinya: menyuntikkan derau ke nilai keluaran sebuah lapis "
                       "==memutus pola kebetulan yang tidak bermakna== -- yang Hinton sebut "
                       "*persekongkolan* -- yang akan mulai dihafal model bila tidak ada "
                       "derau sama sekali."},
                {"t": "band", "style": "amber",
                 "md": "Asal-usulnya kebetulan menolong sebagai analogi: **rotasi pegawai "
                       "sebagai kendali kecurangan** adalah kendali internal yang sudah "
                       "dikenal luas. Dropout adalah kendali yang sama, diterapkan pada "
                       "neuron."},
                {"t": "p", "md": "Hasilnya pada model IMDB (gambar 5.22): peningkatan yang "
                                 "jelas atas model acuan, dan **tampak bekerja lebih baik "
                                 "daripada regularisasi L2**, sebab rugi validasi terendah "
                                 "yang dicapainya lebih rendah."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 5.4.4",
            "title": "Mana yang dipakai kapan",
            "blocks": [
                {"t": "table",
                 "head": ["Cara", "Kapan paling cocok", "Catatan"],
                 "widths": [24, 38, 38],
                 "rows": [
                     ["**Data lebih banyak / lebih baik**", "Selalu, kalau mungkin.",
                      "Imbal hasil terbesar. Menambah data yang terlalu berderau justru "
                      "merugikan."],
                     ["**Fitur yang lebih baik**", "Data sedikit; persoalan yang dipahami "
                      "mendalam.", "Bisa menghapus kebutuhan akan model besar sama sekali."],
                     ["**Kurangi kapasitas**", "Model kecil; data sedikit.",
                      "Cari kompromi -- jangan sampai malah underfit."],
                     ["**Regularisasi bobot (L1/L2)**", "**Model deep learning yang lebih kecil**.",
                      "Pada model besar yang sangat berparameter lebih, mengekang nilai bobot "
                      "==tidak banyak berpengaruh==."],
                     ["**Dropout**", "**Model besar** -- di situ regularisasi bobot kurang "
                      "mempan.", "Laju lazim 0,2-0,5. Pada IMDB hasilnya mengalahkan L2."],
                 ]},
                {"t": "band", "style": "rose",
                 "md": "Satu syarat menaungi semuanya: **regularisasi harus selalu dipandu "
                       "prosedur evaluasi yang tepat**. Anda hanya akan mencapai generalisasi "
                       "==kalau Anda bisa mengukurnya==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Ringkasan",
            "title": "Yang wajib terbawa dari bab 5",
            "blocks": [
                {"t": "steps", "items": [
                    "Tujuan model adalah **menggeneralisasi**: tepat pada masukan yang belum "
                    "pernah dilihat. Lebih sulit daripada kelihatannya.",
                    "Jaringan dalam menggeneralisasi dengan **menginterpolasi** pada manifold "
                    "laten data. Karena itu ia hanya memahami masukan yang ==dekat dengan "
                    "yang pernah dilihatnya==.",
                    "Persoalan pokoknya adalah **ketegangan optimalisasi vs generalisasi**. "
                    "Setiap praktik baik di buku ini menangani ketegangan itu.",
                    "**Ukur dulu, baru perbaiki.** Hold-out, K-lipat, K-lipat berulang -- "
                    "dan selalu sisakan himpunan uji yang benar-benar tak tersentuh.",
                    "**Tetapkan tolok banding akal sehat** sebelum melatih. Kalau tak "
                    "terkalahkan, mungkin persoalannya bukan persoalan machine learning.",
                    "Untuk fit: setel **learning rate dan ukuran batch**, perbaiki **prior "
                    "arsitektur**, tambah **kapasitas** sampai bisa overfit.",
                    "Untuk generalisasi: **data lebih baik → fitur lebih baik → early "
                    "stopping → kurangi kapasitas → L1/L2 → dropout**, dalam urutan itu.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "02_label_diacak_manifold.ipynb",
                     "href": "../../course-slides/notebooks/ch05/02_label_diacak_manifold.ipynb"},
                    {"k": "NOTEBOOK", "ic": "📓", "v": "05_regularisasi_l2_dropout.ipynb",
                     "href": "../../course-slides/notebooks/ch05/05_regularisasi_l2_dropout.ipynb"},
                    {"k": "BAB BERIKUT", "ic": "➡", "v": "Bab 6 — Alur kerja universal",
                     "href": "../ch06/index.html"},
                ]},
            ],
        },
    ],
}
