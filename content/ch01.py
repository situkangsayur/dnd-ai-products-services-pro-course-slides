# -*- coding: utf-8 -*-
"""Bab 1 — What is deep learning?

Sumber: Chollet & Watson, *Deep Learning with Python*, 3rd ed., bab 1.
https://deeplearningwithpython.io/chapters/chapter01_what-is-deep-learning

Bab ini tidak memuat kode. Yang dipakai di sini sebagai peraga adalah kode
sekecil mungkin untuk menunjukkan pembalikan paradigma pemrograman -> ML, dan
sisanya diagram. Semua kutipan dikembalikan ke bab aslinya.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


# =============================================================================
#  Peraga
# =============================================================================

SVG_HIERARCHY = """
<svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="AI memuat machine learning, yang memuat deep learning">
  <rect x="14" y="16" width="480" height="216" rx="16"
        fill="rgba(44,123,212,.10)" stroke="rgba(44,123,212,.55)" stroke-width="1.4"/>
  <text class="d-lbl" x="34" y="42" font-weight="700">Artificial Intelligence</text>
  <text class="d-sm" x="34" y="60">sejak 1950-an &#183; &#8220;mengotomasi tugas intelektual&#8221;</text>

  <rect x="42" y="76" width="424" height="140" rx="14"
        fill="rgba(34,211,238,.10)" stroke="rgba(34,211,238,.55)" stroke-width="1.4"/>
  <text class="d-lbl" x="62" y="102" font-weight="700">Machine Learning</text>
  <text class="d-sm" x="62" y="120">berkembang sejak 1990-an &#183; aturan dipelajari dari data</text>

  <rect x="70" y="136" width="368" height="66" rx="12"
        fill="rgba(167,139,250,.14)" stroke="rgba(167,139,250,.6)" stroke-width="1.4"/>
  <text class="d-lbl" x="90" y="162" font-weight="700">Deep Learning</text>
  <text class="d-sm" x="90" y="180">lapisan representasi bertingkat &#183; puluhan-ratusan lapis</text>

  <!-- kolom kanan: apa yang TIDAK masuk ML -->
  <rect x="520" y="60" width="226" height="128" rx="14"
        fill="rgba(255,255,255,.04)" stroke="rgba(140,190,255,.28)" stroke-width="1.2"/>
  <text class="d-lbl" x="540" y="86" font-weight="700">Symbolic AI</text>
  <text class="d-sm" x="540" y="106">1950-an &#8211; 1980-an</text>
  <text class="d-sm" x="540" y="126">aturan ditulis tangan</text>
  <text class="d-sm" x="540" y="146">unggul di catur,</text>
  <text class="d-sm" x="540" y="164">gagal di persoalan kabur</text>
  <line x1="494" y1="124" x2="518" y2="124" stroke="rgba(140,190,255,.4)"
        stroke-width="1.2" stroke-dasharray="4 3"/>
</svg>
"""

TIKZ_HIERARCHY = r"""
\begin{tikzpicture}[font=\sffamily]
  \node[draw=itbbluelt!70, fill=itbbluelt!8, rounded corners=5pt,
        minimum width=7.4cm, minimum height=3.4cm, anchor=north west] (ai) at (0,0) {};
  \node[anchor=north west, font=\bfseries\small, text=ink] at ($(ai.north west)+(0.28,-0.22)$)
    {Artificial Intelligence};
  \node[anchor=north west, font=\tiny, text=ink3] at ($(ai.north west)+(0.28,-0.62)$)
    {sejak 1950-an --- ``mengotomasi tugas intelektual''};

  \node[draw=signal!70, fill=signal!8, rounded corners=5pt,
        minimum width=6.5cm, minimum height=2.2cm, anchor=north west] (ml) at (0.45,-1.05) {};
  \node[anchor=north west, font=\bfseries\small, text=ink] at ($(ml.north west)+(0.26,-0.2)$)
    {Machine Learning};
  \node[anchor=north west, font=\tiny, text=ink3] at ($(ml.north west)+(0.26,-0.58)$)
    {sejak 1990-an --- aturan dipelajari dari data};

  \node[draw=violet!70, fill=violet!10, rounded corners=5pt,
        minimum width=5.6cm, minimum height=1.0cm, anchor=north west] (dl) at (0.9,-2.0) {};
  \node[anchor=north west, font=\bfseries\small, text=ink] at ($(dl.north west)+(0.24,-0.18)$)
    {Deep Learning};
  \node[anchor=north west, font=\tiny, text=ink3] at ($(dl.north west)+(0.24,-0.54)$)
    {lapisan representasi bertingkat};

  \node[draw=rule, fill=papertint, rounded corners=5pt,
        minimum width=3.4cm, minimum height=2.1cm, anchor=north west] (sym) at (8.0,-0.6) {};
  \node[anchor=north west, font=\bfseries\small, text=ink] at ($(sym.north west)+(0.24,-0.2)$)
    {Symbolic AI};
  \node[anchor=north west, font=\tiny, text=ink3, align=left] at ($(sym.north west)+(0.24,-0.62)$)
    {1950-an -- 1980-an\\aturan ditulis tangan\\unggul di catur,\\gagal di persoalan kabur};
  \draw[rule, dashed, line width=0.6pt] (7.45,-1.7) -- (7.95,-1.7);
\end{tikzpicture}
"""

SVG_PARADIGM = """
<svg viewBox="0 0 760 246" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Pemrograman klasik menghasilkan jawaban; machine learning menghasilkan aturan">
  <defs>
    <marker id="ar1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.75)"/>
    </marker>
  </defs>

  <text class="d-lbl" x="16" y="22" font-weight="700">Pemrograman klasik</text>
  <rect class="d-box" x="16"  y="38" width="112" height="34" rx="8"/>
  <text class="d-sm" x="72" y="59" text-anchor="middle">Aturan</text>
  <rect class="d-box" x="16"  y="82" width="112" height="34" rx="8"/>
  <text class="d-sm" x="72" y="103" text-anchor="middle">Data</text>
  <rect class="d-box-a" x="176" y="60" width="102" height="34" rx="8"/>
  <text class="d-sm" x="227" y="81" text-anchor="middle">Program</text>
  <rect class="d-box" x="322" y="60" width="102" height="34" rx="8"/>
  <text class="d-sm" x="373" y="81" text-anchor="middle">Jawaban</text>
  <path class="d-arrow" d="M128,55 L170,70" marker-end="url(#ar1)"/>
  <path class="d-arrow" d="M128,99 L170,84" marker-end="url(#ar1)"/>
  <path class="d-arrow" d="M278,77 L316,77" marker-end="url(#ar1)"/>

  <line x1="16" y1="140" x2="744" y2="140" stroke="rgba(140,190,255,.2)" stroke-width="1"/>

  <text class="d-lbl" x="16" y="168" font-weight="700">Machine learning</text>
  <rect class="d-box" x="16"  y="184" width="112" height="30" rx="8"/>
  <text class="d-sm" x="72" y="203" text-anchor="middle">Data</text>
  <rect class="d-box" x="16"  y="220" width="112" height="20" rx="6"/>
  <text class="d-sm" x="72" y="234" text-anchor="middle">Jawaban</text>
  <rect class="d-box-a" x="176" y="194" width="102" height="34" rx="8"/>
  <text class="d-sm" x="227" y="215" text-anchor="middle">Pelatihan</text>
  <rect x="322" y="194" width="102" height="34" rx="8"
        fill="rgba(167,139,250,.16)" stroke="rgba(167,139,250,.65)" stroke-width="1.4"/>
  <text class="d-sm" x="373" y="215" text-anchor="middle">Aturan</text>
  <path class="d-arrow" d="M128,199 L170,206" marker-end="url(#ar1)"/>
  <path class="d-arrow" d="M128,230 L170,218" marker-end="url(#ar1)"/>
  <path class="d-arrow" d="M278,211 L316,211" marker-end="url(#ar1)"/>

  <text class="d-mono" x="452" y="200">yang tadinya keluaran</text>
  <text class="d-mono" x="452" y="218">kini menjadi masukan</text>
</svg>
"""

TIKZ_PARADIGM = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  bx/.style={draw=rule, fill=papertint, rounded corners=3pt, minimum width=1.9cm,
             minimum height=0.6cm, text=ink2},
  ax/.style={draw=signal!60, fill=signal!10, rounded corners=3pt, minimum width=1.8cm,
             minimum height=0.6cm, text=ink},
  vx/.style={draw=violet!70, fill=violet!12, rounded corners=3pt, minimum width=1.8cm,
             minimum height=0.6cm, text=ink},
  ar/.style={-{Stealth[length=4pt]}, signal, line width=0.7pt}]

  \node[font=\bfseries\scriptsize, text=ink, anchor=west] at (0,1.55) {Pemrograman klasik};
  \node[bx] (r1) at (1,1.0) {Aturan};
  \node[bx] (d1) at (1,0.2) {Data};
  \node[ax] (p1) at (3.6,0.6) {Program};
  \node[bx] (a1) at (6.1,0.6) {Jawaban};
  \draw[ar] (r1) -- (p1); \draw[ar] (d1) -- (p1); \draw[ar] (p1) -- (a1);

  \draw[rule, line width=0.5pt] (0,-0.4) -- (8.6,-0.4);

  \node[font=\bfseries\scriptsize, text=ink, anchor=west] at (0,-0.95) {Machine learning};
  \node[bx] (d2) at (1,-1.4) {Data};
  \node[bx] (a2) at (1,-2.2) {Jawaban};
  \node[ax] (p2) at (3.6,-1.8) {Pelatihan};
  \node[vx] (r2) at (6.1,-1.8) {Aturan};
  \draw[ar] (d2) -- (p2); \draw[ar] (a2) -- (p2); \draw[ar] (p2) -- (r2);
  \node[text=ink3, anchor=west, align=left] at (7.2,-1.8)
    {yang tadinya keluaran\\kini menjadi masukan};
\end{tikzpicture}
"""

SVG_LAYERS = """
<svg viewBox="0 0 760 210" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Empat lapisan representasi mengubah piksel angka menjadi probabilitas kelas">
  <defs>
    <marker id="ar2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.7)"/>
    </marker>
  </defs>
  <rect class="d-box" x="10" y="62" width="76" height="76" rx="8"/>
  <text class="d-sm" x="48" y="96" text-anchor="middle">masukan</text>
  <text class="d-sm" x="48" y="114" text-anchor="middle">28&#215;28</text>

  <g>
    <rect class="d-box-a" x="132" y="52" width="80" height="96" rx="8"/>
    <text class="d-sm" x="172" y="94" text-anchor="middle">lapis 1</text>
    <text class="d-mono" x="172" y="112" text-anchor="middle">tepi</text>
  </g>
  <g>
    <rect class="d-box-a" x="248" y="52" width="80" height="96" rx="8"/>
    <text class="d-sm" x="288" y="94" text-anchor="middle">lapis 2</text>
    <text class="d-mono" x="288" y="112" text-anchor="middle">sudut</text>
  </g>
  <g>
    <rect class="d-box-a" x="364" y="52" width="80" height="96" rx="8"/>
    <text class="d-sm" x="404" y="94" text-anchor="middle">lapis 3</text>
    <text class="d-mono" x="404" y="112" text-anchor="middle">bagian</text>
  </g>
  <g>
    <rect class="d-box-a" x="480" y="52" width="80" height="96" rx="8"/>
    <text class="d-sm" x="520" y="94" text-anchor="middle">lapis 4</text>
    <text class="d-mono" x="520" y="112" text-anchor="middle">angka</text>
  </g>

  <rect x="600" y="62" width="150" height="76" rx="8"
        fill="rgba(123,217,73,.12)" stroke="rgba(123,217,73,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="675" y="90" text-anchor="middle">keluaran</text>
  <text class="d-mono" x="675" y="110" text-anchor="middle">P(0..9)</text>

  <path class="d-arrow" d="M88,100 L128,100"  marker-end="url(#ar2)"/>
  <path class="d-arrow" d="M214,100 L244,100" marker-end="url(#ar2)"/>
  <path class="d-arrow" d="M330,100 L360,100" marker-end="url(#ar2)"/>
  <path class="d-arrow" d="M446,100 L476,100" marker-end="url(#ar2)"/>
  <path class="d-arrow" d="M562,100 L596,100" marker-end="url(#ar2)"/>

  <text class="d-sm" x="10" y="182" fill="#7E93B4">
    setiap lapis mengubah representasi menjadi bentuk yang sedikit lebih berguna
  </text>
  <text class="d-sm" x="10" y="30" fill="#7E93B4">
    &#8220;kesulingan informasi&#8221; &#8212; informasi yang tidak relevan disaring, yang relevan diperkuat
  </text>
</svg>
"""

TIKZ_LAYERS = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  lay/.style={draw=signal!60, fill=signal!9, rounded corners=3pt,
              minimum width=1.25cm, minimum height=1.5cm, text=ink, align=center},
  io/.style={draw=rule, fill=papertint, rounded corners=3pt,
             minimum width=1.25cm, minimum height=1.2cm, text=ink2, align=center},
  ar/.style={-{Stealth[length=4pt]}, signal, line width=0.7pt}]
  \node[io]  (in) at (0,0)   {masukan\\$28\times28$};
  \node[lay] (l1) at (1.9,0) {lapis 1\\\ttfamily tepi};
  \node[lay] (l2) at (3.5,0) {lapis 2\\\ttfamily sudut};
  \node[lay] (l3) at (5.1,0) {lapis 3\\\ttfamily bagian};
  \node[lay] (l4) at (6.7,0) {lapis 4\\\ttfamily angka};
  \node[draw=lime!60, fill=limebr!12, rounded corners=3pt, minimum width=1.6cm,
        minimum height=1.2cm, text=ink, align=center] (out) at (8.7,0) {keluaran\\\ttfamily P(0..9)};
  \draw[ar] (in) -- (l1); \draw[ar] (l1) -- (l2); \draw[ar] (l2) -- (l3);
  \draw[ar] (l3) -- (l4); \draw[ar] (l4) -- (out);
  \node[text=ink3, anchor=west] at (-0.7,-1.25)
    {setiap lapis mengubah representasi menjadi bentuk yang sedikit lebih berguna};
\end{tikzpicture}
"""

SVG_LOOP = """
<svg viewBox="0 0 760 268" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Lingkar pelatihan: bobot, prediksi, fungsi rugi, optimalisasi">
  <defs>
    <marker id="ar3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.75)"/>
    </marker>
    <marker id="ar4" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(245,179,1,.85)"/>
    </marker>
  </defs>

  <rect class="d-box" x="16" y="96" width="104" height="40" rx="8"/>
  <text class="d-sm" x="68" y="121" text-anchor="middle">Masukan X</text>

  <rect x="164" y="60" width="132" height="112" rx="10"
        fill="rgba(44,123,212,.14)" stroke="rgba(44,123,212,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="230" y="88" text-anchor="middle">Lapis</text>
  <text class="d-sm" x="230" y="106" text-anchor="middle">(transformasi</text>
  <text class="d-sm" x="230" y="124" text-anchor="middle">data)</text>
  <rect x="180" y="136" width="100" height="24" rx="6"
        fill="rgba(245,179,1,.16)" stroke="rgba(245,179,1,.6)" stroke-width="1.2"/>
  <text class="d-mono" x="230" y="152" text-anchor="middle" fill="#F5B301">Bobot W</text>

  <rect class="d-box" x="340" y="96" width="112" height="40" rx="8"/>
  <text class="d-sm" x="396" y="121" text-anchor="middle">Prediksi Y&#39;</text>

  <rect class="d-box" x="340" y="192" width="112" height="34" rx="8"/>
  <text class="d-sm" x="396" y="214" text-anchor="middle">Target Y</text>

  <rect x="500" y="118" width="126" height="42" rx="10"
        fill="rgba(251,113,133,.14)" stroke="rgba(251,113,133,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="563" y="144" text-anchor="middle">Fungsi rugi</text>

  <rect x="500" y="24" width="126" height="42" rx="10"
        fill="rgba(123,217,73,.14)" stroke="rgba(123,217,73,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="563" y="50" text-anchor="middle">Optimalisasi</text>

  <path class="d-arrow" d="M120,116 L160,116" marker-end="url(#ar3)"/>
  <path class="d-arrow" d="M296,116 L336,116" marker-end="url(#ar3)"/>
  <path class="d-arrow" d="M452,120 L496,133" marker-end="url(#ar3)"/>
  <path class="d-arrow" d="M452,203 L496,158" marker-end="url(#ar3)"/>
  <path d="M563,118 L563,70" stroke="rgba(245,179,1,.85)" stroke-width="1.6"
        fill="none" marker-end="url(#ar4)"/>
  <path d="M500,45 C420,45 300,30 230,30 L230,54" stroke="rgba(245,179,1,.85)"
        stroke-width="1.6" fill="none" stroke-dasharray="5 4" marker-end="url(#ar4)"/>
  <text class="d-mono" x="300" y="22" fill="#F5B301">perbarui bobot</text>

  <text class="d-sm" x="640" y="144" fill="#FB7185">skor</text>
  <text class="d-sm" x="640" y="50"  fill="#7BD949">arah</text>
</svg>
"""

TIKZ_LOOP = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  bx/.style={draw=rule, fill=papertint, rounded corners=3pt, minimum width=1.7cm,
             minimum height=0.62cm, text=ink2, align=center},
  ar/.style={-{Stealth[length=4pt]}, signal, line width=0.7pt},
  fb/.style={-{Stealth[length=4pt]}, amberbr, line width=0.8pt}]
  \node[bx] (x) at (0,0) {Masukan $X$};
  \node[draw=itbbluelt!70, fill=itbbluelt!12, rounded corners=4pt, minimum width=2.1cm,
        minimum height=1.7cm, text=ink, align=center] (lay) at (2.5,0)
        {Lapis\\(transformasi data)};
  \node[draw=amber!70, fill=amberbr!16, rounded corners=3pt, minimum width=1.6cm,
        minimum height=0.42cm, text=ink, font=\ttfamily\tiny] (w) at (2.5,-0.62) {Bobot $W$};
  \node[bx] (yp) at (5.2,0) {Prediksi $\hat{Y}$};
  \node[bx] (y)  at (5.2,-1.5) {Target $Y$};
  \node[draw=rose!70, fill=rosebr!14, rounded corners=4pt, minimum width=1.9cm,
        minimum height=0.62cm, text=ink] (loss) at (7.9,-0.75) {Fungsi rugi};
  \node[draw=lime!70, fill=limebr!16, rounded corners=4pt, minimum width=1.9cm,
        minimum height=0.62cm, text=ink] (opt) at (7.9,1.15) {Optimalisasi};

  \draw[ar] (x) -- (lay); \draw[ar] (lay) -- (yp);
  \draw[ar] (yp) -- (loss); \draw[ar] (y) -- (loss);
  \draw[fb] (loss) -- (opt);
  \draw[fb, dashed] (opt) -| (2.5,0.9) -- (lay.north);
  \node[text=amber, anchor=south] at (4.6,1.3) {perbarui bobot};
\end{tikzpicture}
"""


# =============================================================================
#  Deck
# =============================================================================

DECK = {
    "id": "ch01",
    "kind": "chapter",
    "number": 1,
    "title": "Apa Itu Deep Learning?",
    "subtitle": "Meletakkan AI, machine learning, dan deep learning pada tempatnya "
                "masing-masing -- lalu memisahkan capaian nyata dari gembar-gembor.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- bab 1",
    "source_url": chapter_url(1),
    "duration": "90 menit",
    "presenter": {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Pengajar Utama"},
    "resources": chapter_resources(1, local_notebooks=["01_paradigma_ml.ipynb"]),
    "objectives": [
        "Menempatkan **AI, machine learning, dan deep learning** dalam hubungan "
        "yang benar -- yang mana memuat yang mana, dan sejak kapan.",
        "Menjelaskan **pembalikan paradigma**: pemrograman klasik menghasilkan "
        "jawaban, machine learning menghasilkan aturan.",
        "Menyebut **tiga bahan wajib** setiap sistem machine learning dan "
        "menunjukkan apa yang rusak bila salah satunya hilang.",
        "Menerangkan cara kerja deep learning lewat **bobot, fungsi rugi, dan "
        "backpropagation** tanpa menurunkan satu pun rumus.",
        "Membedakan **capaian yang sudah terbukti** dari **klaim yang belum**, "
        "dan menyebut apa yang memicu dua musim dingin AI sebelumnya.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------ peta ---
        {
            "type": "slide",
            "kicker": "Peta bab",
            "title": "Ke mana bab ini membawa kita",
            "blocks": [
                {"t": "lead", "md": "Bab pembuka tidak mengajarkan satu baris kode pun. "
                                    "Tugasnya lebih mendasar: memastikan kita memakai kata "
                                    "yang sama untuk hal yang sama."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🗺", "h": "Definisi dan sejarah",
                     "p": "Tiga lingkaran bersarang: AI, ML, DL. Ditambah satu cabang "
                          "yang **bukan** ML sama sekali -- symbolic AI.",
                     "tag": "bag. 1-3"},
                    {"ico": "⚙", "h": "Cara kerjanya",
                     "p": "Representasi, bobot, fungsi rugi, backpropagation. "
                          "Chollet menerangkannya dengan **tiga gambar**, bukan rumus.",
                     "tag": "bag. 4-6"},
                    {"ico": "⚖", "h": "Capaian vs gembar-gembor",
                     "p": "Apa yang **sudah** dikerjakan deep learning, dan mengapa "
                          "dua kali sebelumnya musim panas AI berubah jadi musim dingin.",
                     "tag": "bag. 7-12"},
                ]},
                {"t": "band", "md": "Untuk kelas ini bab 1 punya beban tambahan: ia yang "
                                    "menetapkan **kosakata bersama** yang dipakai sampai bab 20 "
                                    "dan sampai topik agentic AI di akhir kursus."},
            ],
            "notes": "Buka dengan pertanyaan ke peserta: siapa yang bisa menjelaskan beda "
                     "AI dan machine learning dalam satu kalimat? Jawaban yang beragam di "
                     "ruangan justru bahan yang bagus untuk masuk ke slide berikutnya.",
        },

        # --------------------------------------------------------- section ---
        {"type": "section", "num": "01", "title": "AI, machine learning, deep learning",
         "lead": "Tiga istilah yang di media dipakai bergantian, padahal bersarang."},

        {
            "type": "slide",
            "kicker": "Bagian 1.1",
            "title": "Tiga lingkaran yang bersarang, bukan tiga sinonim",
            "blocks": [
                {"t": "fig", "svg": SVG_HIERARCHY, "tikz": TIKZ_HIERARCHY,
                 "cap": "Gambar 1.1 -- deep learning adalah bagian dari machine learning, "
                        "yang adalah bagian dari AI. Symbolic AI ada di dalam AI tetapi "
                        "di luar machine learning."},
                {"t": "bullets", "items": [
                    "**AI** lahir 1950-an. Definisi kerjanya: *upaya mengotomasi tugas "
                    "intelektual yang biasanya dikerjakan manusia*. Cakupannya jauh lebih "
                    "luas dari ML.",
                    "**Symbolic AI** mendominasi 1950-an sampai 1980-an: aturan ditulis "
                    "tangan oleh pemrogram. Cukup untuk catur, ==runtuh== di persoalan "
                    "kabur seperti mengenali gambar atau bahasa.",
                    "**Machine learning** naik sejak 1990-an justru karena persoalan kabur "
                    "itulah yang tersisa.",
                ]},
            ],
            "notes": "Tekankan: kegagalan symbolic AI bukan kegagalan gagasan AI. Ia gagal "
                     "pada satu kelas persoalan tertentu -- yang aturannya tidak bisa "
                     "dituliskan manusia karena manusia sendiri tidak sadar memakainya.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.1",
            "title": "Kutipan yang membingkai seluruh bidang",
            "blocks": [
                {"t": "quote",
                 "md": "The Analytical Engine has no pretensions whatever to originate "
                       "anything. It can do whatever we know how to order it to perform.",
                 "cite": "Ada Lovelace, 1843 -- catatan atas mesin Charles Babbage"},
                {"t": "quote",
                 "md": "Every aspect of learning or any other feature of intelligence can "
                       "in principle be so precisely described that a machine can be made "
                       "to simulate it.",
                 "cite": "John McCarthy dkk., proposal lokakarya Dartmouth, 1956"},
                {"t": "band", "style": "amber",
                 "md": "Dua kutipan ini berselisih 113 tahun dan berselisih pendapat. "
                       "Pertanyaan Lovelace -- *bisakah mesin melampaui perintah kita?* -- "
                       "belum tuntas sampai hari ini; ==machine learning adalah jawaban "
                       "parsialnya==, sebab mesin memang menghasilkan sesuatu yang tidak "
                       "kita tuliskan: aturannya."},
            ],
            "notes": "Kutipan Lovelace dipakai Chollet sejak edisi pertama sebagai pembuka. "
                     "Sambungkan ke pertanyaan yang akan diajukan auditor mana pun: kalau "
                     "aturannya tidak kita tulis, siapa yang bertanggung jawab atas aturan itu?",
        },

        # --------------------------------------------------------- section ---
        {"type": "section", "num": "02", "title": "Pembalikan paradigma",
         "lead": "Yang tadinya keluaran, kini menjadi masukan."},

        {
            "type": "slide",
            "kicker": "Bagian 1.1.2",
            "title": "Machine learning membalik arah pemrograman",
            "blocks": [
                {"t": "fig", "svg": SVG_PARADIGM, "tikz": TIKZ_PARADIGM,
                 "cap": "Gambar 1.2 -- pemrograman klasik disuapi aturan dan data lalu "
                        "mengeluarkan jawaban; machine learning disuapi data dan jawaban "
                        "lalu mengeluarkan aturan."},
                {"t": "band",
                 "md": "Konsekuensinya langsung dan sering diremehkan: sistem ML "
                       "==dilatih, bukan diprogram==. Kalau tidak ada contoh yang sudah "
                       "berjawab, tidak ada yang bisa dilatih -- seberapa pun bagus "
                       "arsitekturnya."},
            ],
            "notes": "Di sini biasanya muncul pertanyaan 'kalau begitu datanya dari mana?'. "
                     "Jawab singkat saja, bab 6 membahasnya penuh sebagai universal workflow.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.1.2",
            "title": "Tiga bahan wajib -- hilang satu, bukan machine learning",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📥", "h": "1 · Titik data masukan",
                     "p": "Berkas suara, gambar, baris transaksi. Inilah yang akan "
                          "ditransformasi.", "style": "accent"},
                    {"ico": "🎯", "h": "2 · Contoh keluaran yang diharapkan",
                     "p": "Transkrip untuk suara, label untuk gambar, penanda "
                          "*fraud* untuk transaksi.", "style": "accent"},
                    {"ico": "📏", "h": "3 · Cara mengukur mutu",
                     "p": "Jarak antara tebakan dan jawaban benar. Inilah "
                          "**sinyal umpan balik** yang menyetel algoritmanya.",
                     "style": "accent"},
                ]},
                {"t": "p", "md": "Ketiganya adalah syarat minimum, bukan daftar keinginan. "
                                 "Chollet menyebut inti persoalannya sebagai "
                                 "*meaningfully transform data* -- mempelajari **representasi** "
                                 "yang membuat tugas jadi lebih mudah."},
                {"t": "table",
                 "head": ["Bahan yang hilang", "Yang sebenarnya Anda punya", "Akibatnya"],
                 "widths": [26, 34, 40],
                 "rows": [
                     ["Contoh keluaran", "Data mentah tanpa label",
                      "Bukan supervised learning. Pilihannya: pelabelan, atau pindah ke "
                      "unsupervised / self-supervised."],
                     ["Ukuran mutu", "Data dan label, tanpa metrik yang disepakati",
                      "Model bisa dilatih tetapi tidak bisa dinilai -- dan ini kegagalan "
                      "proyek yang paling sering di dunia nyata."],
                     ["Data masukan yang mewakili", "Contoh yang tidak menyerupai kondisi produksi",
                      "Model berhasil di laptop, gagal saat dipakai. Bab 5 dan 6 menamainya "
                      "secara teknis."],
                 ]},
            ],
            "notes": "Minta peserta memikirkan satu kasus pemakaian dari pekerjaannya sendiri, lalu "
                     "uji ketiga bahan itu. Yang paling sering hilang adalah bahan ketiga -- "
                     "kesepakatan tentang apa yang disebut 'benar'.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.1.3",
            "title": "Representasi: gagasan yang menyatukan seluruh buku",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Representasi** adalah cara lain menyandikan data "
                                         "yang sama. Foto yang sama bisa disandikan sebagai "
                                         "RGB atau HSV -- isinya identik, tetapi tugas yang "
                                         "mudah pada masing-masing berbeda."},
                        {"t": "bullets", "items": [
                            "*Pilih semua piksel merah* -- mudah di **RGB**.",
                            "*Buat gambar kurang jenuh* -- mudah di **HSV**.",
                            "Persoalan yang sama; yang berubah hanya sumbunya.",
                        ]},
                        {"t": "band",
                         "md": "Karena itu Chollet merumuskan machine learning sebagai "
                               "==pencarian representasi yang membuat tugas jadi mudah==."},
                    ],
                    [
                        {"t": "p", "md": "Contoh klasik bab ini: titik hitam dan putih yang "
                                         "bercampur pada sumbu asal (gambar 1.3). Tidak ada "
                                         "aturan sederhana yang memisahkannya."},
                        {"t": "p", "md": "Ubah sumbunya -- pindahkan titik asal, putar -- dan "
                                         "aturannya menjadi satu kalimat (gambar 1.4): "
                                         "*hitam bila x > 0*."},
                        {"t": "band", "style": "amber",
                         "md": "Tidak ada model yang jadi lebih pintar. Yang berubah hanya "
                               "representasinya. Inilah pekerjaan yang dulu disebut "
                               "**feature engineering** dan dikerjakan manusia."},
                    ],
                ]},
            ],
            "notes": "Kalau ada waktu, gambar manual di papan: sebar titik, lalu putar sumbu. "
                     "Peraga fisik ini jauh lebih nempel daripada slide.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.4",
            "title": "Ruang hipotesis -- dan mengapa aturan tulis-tangan runtuh",
            "blocks": [
                {"t": "p", "md": "Perubahan sumbu tadi kita rancang **dengan tangan**. Itu "
                                 "sanggup untuk persoalan sesederhana itu. Tetapi bisakah "
                                 "Anda menuliskan transformasi citra yang menjelaskan beda "
                                 "6 dan 8, atau 1 dan 7, ==untuk segala macam tulisan tangan==?"},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✍", "h": "Bisa -- sampai batas tertentu",
                     "p": "Aturan seperti *menghitung banyaknya gelung tertutup*, atau "
                          "histogram piksel tegak dan mendatar, lumayan membedakan angka "
                          "tulisan tangan.", "style": "warn"},
                    {"ico": "💥", "h": "Tetapi rapuh dan menyiksa",
                     "p": "Tiap kali muncul contoh tulisan baru yang mematahkan aturan yang "
                          "sudah disusun rapi, Anda harus menambah transformasi dan aturan "
                          "baru -- **sambil memperhitungkan interaksinya dengan semua aturan "
                          "sebelumnya**.", "style": "bad"},
                ]},
                {"t": "band",
                 "md": "Algoritma machine learning **tidak kreatif** dalam menemukan "
                       "transformasi ini. Ia sekadar menelusuri sehimpunan operasi yang "
                       "sudah ditetapkan lebih dulu -- himpunan itulah yang disebut "
                       "==ruang hipotesis (hypothesis space)==. Pada contoh 2D tadi, ruang "
                       "hipotesisnya adalah ruang semua perubahan sumbu yang mungkin."},
                {"t": "quote",
                 "md": "Itulah machine learning, secara ringkas: **mencari representasi dan "
                       "aturan yang berguna atas suatu data masukan, di dalam ruang "
                       "kemungkinan yang sudah ditetapkan, dengan tuntunan sebuah sinyal "
                       "umpan balik.**",
                 "cite": "Chollet & Watson, bab 1.4"},
                {"t": "p", "md": "Gagasan sesederhana itu menyelesaikan rentang tugas "
                                 "intelektual yang luar biasa lebar -- dari kemudi otonom "
                                 "sampai penjawaban pertanyaan dalam bahasa alami."},
            ],
            "notes": "Istilah 'ruang hipotesis' akan kembali di bab 3 saat topologi model "
                     "dibahas: memilih arsitektur = mempersempit ruang hipotesis.",
        },

        # --------------------------------------------------------- section ---
        {"type": "section", "num": "03", "title": "Yang 'dalam' pada deep learning",
         "lead": "Bukan pemahaman yang lebih dalam. Hanya lapisan yang lebih banyak."},

        {
            "type": "slide",
            "kicker": "Bagian 1.1.4",
            "title": "'Deep' menunjuk pada jumlah lapis, bukan kedalaman makna",
            "blocks": [
                {"t": "quote",
                 "md": "The \"deep\" in \"deep learning\" isn't a reference to any kind of "
                       "deeper understanding -- rather, it stands for this idea of "
                       "successive layers of representations.",
                 "cite": "Chollet & Watson, bab 1"},
                {"t": "fig", "svg": SVG_LAYERS, "tikz": TIKZ_LAYERS,
                 "cap": "Gambar 1.5-1.6 -- jaringan empat lapis untuk klasifikasi angka. "
                        "Representasi antara semakin jauh dari piksel dan semakin dekat "
                        "ke jawaban."},
                {"t": "bullets", "items": [
                    "Banyaknya lapis = **kedalaman** model. Jaringan modern punya puluhan "
                    "sampai ratusan lapis.",
                    "Lawannya, **shallow learning**, hanya satu atau dua lapis representasi.",
                    "Semua lapis dipelajari ==sekaligus, otomatis== dari data pelatihan -- "
                    "bukan dirancang satu per satu oleh manusia.",
                    "Chollet menyebut nama yang sebenarnya lebih tepat untuk bidang ini: "
                    "*layered representations learning* atau *hierarchical representations "
                    "learning*. Istilah **deep** menang karena sejarah, bukan karena akurasi.",
                ]},
            ],
            "notes": "Koreksi salah paham yang paling umum di ruangan: 'deep' sering "
                     "dikira berarti mesin memahami lebih dalam. Bukan. Ia sekadar "
                     "keterangan arsitektur.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.1.5 -- tiga gambar",
            "title": "Cara kerja deep learning, tanpa satu pun rumus",
            "blocks": [
                {"t": "fig", "svg": SVG_LOOP, "tikz": TIKZ_LOOP,
                 "cap": "Gambar 1.7-1.9 digabung: bobot memarametrikan lapis, fungsi rugi "
                        "mengukur jaraknya ke target, optimalisasi memakai skor itu untuk "
                        "menggeser bobot."},
                {"t": "steps", "items": [
                    "**Bobot memarametrikan transformasi** (gambar 1.7). Apa yang dikerjakan "
                    "sebuah lapis tersimpan di bobotnya. Belajar = menemukan nilai bobot yang "
                    "benar. Jaringan besar punya puluhan juta parameter.",
                    "**Fungsi rugi mengukur seberapa jauh melesetnya** (gambar 1.8). Ia "
                    "menghitung jarak antara prediksi dan target. Disebut juga *objective* "
                    "atau *cost function*.",
                    "**Backpropagation memakai skor itu sebagai umpan balik** (gambar 1.9): "
                    "geser bobot ke arah yang menurunkan rugi, ulangi ribuan kali. Inilah "
                    "**lingkar pelatihan**.",
                ]},
                {"t": "band",
                 "md": "Bobot mula-mula diisi ==acak==, jadi keluaran awal tentu ngawur dan "
                       "ruginya tinggi. Yang membuatnya bekerja adalah pengulangan lingkar "
                       "itu, bukan tebakan awal yang bagus."},
            ],
            "notes": "Ini slide paling penting di bab 1. Bab 2 akan membongkar setiap kotak "
                     "di diagram ini menjadi tensor dan turunan; cukup pastikan bentuk "
                     "lingkarnya tertanam dulu.",
        },

        {
            "type": "slide",
            "kicker": "Peraga 1 dari 2",
            "title": "Lingkar pelatihan itu, dalam sepuluh baris",
            "blocks": [
                {"t": "p", "md": "Bab 1 memang tidak memuat kode. Tetapi seluruh diagram di "
                                 "slide sebelumnya muat dalam potongan sekecil ini."},
                {"t": "code", "lang": "python", "file": "peraga kelas — bukan listing buku",
                 "src": """import numpy as np

# Data mainan: y = 2x + 1, ditambah sedikit derau.
rng = np.random.default_rng(0)
X = rng.uniform(-1, 1, size=(200, 1))
Y = 2 * X + 1 + rng.normal(0, 0.05, size=(200, 1))

# 1) Bobot -- mula-mula acak, persis seperti kata bab ini.
W, b = rng.normal(size=(1, 1)), np.zeros((1,))

for step in range(600):
    Y_pred = X @ W + b                  # lapis: transformasi data
    loss = np.mean((Y_pred - Y) ** 2)   # 2) fungsi rugi: seberapa jauh melesetnya

    # 3) gradien rugi terhadap bobot -- inti backpropagation
    grad = 2.0 * (Y_pred - Y) / len(X)
    W -= 0.5 * (X.T @ grad)             # geser ke arah yang menurunkan rugi
    b -= 0.5 * grad.sum()

    if step % 200 == 0:
        print(f"step {step:3d}  loss {loss:.5f}  W {W[0, 0]:+.3f}  b {b[0]:+.3f}")

print(f"selesai    loss {loss:.5f}  W {W[0, 0]:+.3f}  b {b[0]:+.3f}")"""},
            ],
            "notes": "Jalankan langsung di depan kelas kalau memungkinkan. Tiga komentar "
                     "bernomor di kode itu menunjuk persis ke tiga gambar pada slide "
                     "sebelumnya -- tunjuk bolak-balik antara keduanya.",
        },

        {
            "type": "slide",
            "kicker": "Peraga 2 dari 2",
            "title": "Yang keluar dari lingkar itu: aturannya sendiri",
            "blocks": [
                {"t": "out", "src": """step   0  loss 4.02891  W +0.126  b +0.000
step 200  loss 0.00932  W +1.842  b +0.968
step 400  loss 0.00268  W +1.972  b +0.997
selesai    loss 0.00251  W +1.994  b +1.000"""},
                {"t": "band",
                 "md": "Bobot bergerak dari acak ke ==W ≈ 2, b ≈ 1== -- hukum yang memang "
                       "membangkitkan datanya, dan yang tidak pernah kita tuliskan. "
                       "Itulah 'aturan sebagai keluaran' pada gambar 1.2."},
                {"t": "bullets", "items": [
                    "Tidak ada satu baris pun yang memberi tahu program bahwa jawabannya 2 dan 1.",
                    "Yang diberikan hanya **data, jawaban, dan ukuran rugi** -- tiga bahan wajib itu.",
                    "Bab 2 mengganti NumPy sebaris ini dengan tensor dan turunan otomatis; "
                    "bentuk lingkarnya ==tidak berubah==.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_paradigma_ml.ipynb",
                     "href": "../../notebooks/ch01/01_paradigma_ml.ipynb"},
                    {"k": "BAB PENUH", "ic": "📘", "v": "deeplearningwithpython.io",
                     "href": chapter_url(1)},
                ]},
            ],
            "notes": "Yang mau dilihat peserta bukan angkanya, melainkan bahwa loss turun "
                     "sendiri tanpa ada yang memberitahu jawabannya.",
        },

        # --------------------------------------------------------- section ---
        {"type": "section", "num": "04", "title": "Mengapa deep learning menang",
         "lead": "Tiga sifat, dan satu perubahan yang membuat pesaingnya tertinggal."},

        {
            "type": "slide",
            "kicker": "Bagian 1.1.6",
            "title": "Apa yang membuatnya berbeda dari shallow learning",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🧩", "h": "Kesederhanaan",
                     "p": "Feature engineering dikerjakan sendiri oleh model. Pipeline "
                          "bertingkat digantikan **satu model ujung-ke-ujung**.",
                     "tag": "simplicity", "style": "good"},
                    {"ico": "📈", "h": "Skalabilitas",
                     "p": "Cocok diparalelkan di GPU dan dilatih per *batch*, jadi ukuran "
                          "data ==tidak lagi jadi batas atas==.",
                     "tag": "scalability", "style": "good"},
                    {"ico": "♻", "h": "Keluwesan & pakai ulang",
                     "p": "Model bisa dilatih lanjut dengan data baru tanpa mulai dari nol; "
                          "*foundation model* dipindah ke tugas lain dengan sedikit "
                          "pelatihan tambahan.", "tag": "reusability", "style": "good"},
                ]},
                {"t": "p", "md": "Perbedaan pokoknya satu: pendekatan dangkal memaksa manusia "
                                 "merancang lapisan representasi dulu, lalu model bekerja di "
                                 "atasnya. Deep learning ==mempelajari semua lapisan itu "
                                 "sekaligus, dalam satu tarikan==."},
                {"t": "band", "style": "amber",
                 "md": "Ini juga sumber keluhan auditor: yang membuatnya kuat -- representasi "
                       "yang ditemukan sendiri -- persis yang membuatnya sulit diterangkan. "
                       "Bab 10 kembali ke soal ini untuk kasus citra."},
            ],
            "notes": "Sambungkan ke topik kepatuhan yang akan dibahas di sesi lain: "
                     "keterjelasan model bukan sekadar keinginan akademik di sektor "
                     "diatur ketat, ia persyaratan.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.2",
            "title": "Zaman AI generatif",
            "blocks": [
                {"t": "cols", "ratio": "3-2", "cols": [
                    [
                        {"t": "p", "md": "Mekanismenya: model menyusun ulang teks atau gambar "
                                         "dari masukannya sendiri. Targetnya diambil **dari "
                                         "masukan itu juga** -- inilah *self-supervised "
                                         "learning*, dan itulah sebabnya ia lepas dari batas "
                                         "ketersediaan label."},
                        {"t": "bullets", "items": [
                            "*Foundation model* dengan **ratusan miliar parameter**, dilatih "
                            "di atas data lebih dari **satu petabyte**.",
                            "Berperilaku seperti ==basis data kabur atas pengetahuan manusia==.",
                            "Persoalan baru diselesaikan lewat **prompting**, tanpa "
                            "pemrograman khusus per tugas.",
                            "Masuk kesadaran umum pada **2022**, tetapi percobaan "
                            "pembangkitan teks sudah ada sejak **1990-an**.",
                        ]},
                    ],
                    [
                        {"t": "stats", "cols": 1, "items": [
                            {"v": "10¹¹", "l": "orde parameter pada foundation model terkini"},
                            {"v": "> 1 PB", "l": "orde data pelatihan"},
                            {"v": "2022", "l": "tahun ia menjadi perbincangan umum"},
                        ]},
                    ],
                ]},
                {"t": "band",
                 "md": "Untuk kursus ini, bab 15-17 membongkar mesinnya (Transformer, "
                       "pembangkitan teks, pembangkitan gambar), dan topik LLM serta "
                       "agentic AI memakainya sebagai bahan bangunan."},
            ],
            "notes": "Tahan dulu pertanyaan tentang RAG dan fine-tuning; itu topik 4. "
                     "Di sini cukup tegaskan bahwa self-supervised-lah yang membuat "
                     "skala sebesar itu mungkin.",
        },

        # --------------------------------------------------------- section ---
        {"type": "section", "num": "05", "title": "Capaian, dan gembar-gembor",
         "lead": "Yang sudah terbukti, dan mengapa dua kali sebelumnya kita salah menaksir."},

        {
            "type": "slide",
            "kicker": "Bagian 1.3",
            "title": "Yang sudah benar-benar dikerjakan deep learning",
            "blocks": [
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "💬", "h": "Percakapan", "p": "ChatGPT, Gemini, Claude."},
                    {"ico": "⌨", "h": "Pembangkitan kode", "p": "GitHub Copilot dan sejenisnya."},
                    {"ico": "🖼", "h": "Gambar fotorealistik", "p": "Dari teks ke citra."},
                    {"ico": "👁", "h": "Setara manusia",
                     "p": "Klasifikasi citra, transkripsi suara, pengenalan tulisan tangan."},
                    {"ico": "🌐", "h": "Terjemahan & TTS", "p": "Naik tajam mutunya."},
                    {"ico": "🚗", "h": "Kemudi otonom",
                     "p": "Beroperasi di Phoenix, San Francisco, Los Angeles, Austin (2025)."},
                    {"ico": "♟", "h": "Melampaui manusia", "p": "Go, catur, poker."},
                    {"ico": "🧬", "h": "Struktur protein", "p": "AlphaFold."},
                ]},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📺", "h": "Sistem perekomendasi",
                     "p": "YouTube, Netflix, Spotify -- yang paling banyak dipakai orang "
                          "setiap hari tanpa menyadarinya."},
                    {"ico": "📜", "h": "Naskah kuno",
                     "p": "Puluhan ribu manuskrip di **Vatican Secret Archive** "
                          "ditranskripsi otomatis."},
                    {"ico": "🌱", "h": "Penyakit tanaman",
                     "p": "Dideteksi dan digolongkan langsung di lahan, cukup dengan "
                          "ponsel biasa."},
                    {"ico": "🩺", "h": "Citra medis",
                     "p": "Mendampingi onkolog dan radiolog menafsirkan hasil pencitraan."},
                    {"ico": "🌊", "h": "Bencana alam",
                     "p": "Meramalkan banjir, badai, bahkan gempa bumi."},
                    {"ico": "🧬", "h": "Struktur protein",
                     "p": "AlphaFold, dengan ketepatan yang belum pernah ada sebelumnya."},
                ]},
                {"t": "band",
                 "md": "Daftar ini ==bukan janji==; semuanya sudah berjalan. Itulah yang "
                       "membedakannya dari slide berikutnya."},
            ],
            "notes": "Sengaja ditaruh sebelum slide gembar-gembor. Urutannya penting: "
                     "akui dulu capaiannya, baru kritik taksirannya. Kalau dibalik, "
                     "terdengar seperti penyangkalan.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.9",
            "title": "Tiga gelombang dalam satu dasawarsa",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "👁", "h": "2013 – 2017 · persepsi",
                     "p": "Hasil yang mencengangkan pada tugas persepsi: klasifikasi citra, "
                          "transkripsi suara, pengenalan tulisan tangan.", "style": "accent"},
                    {"ico": "💬", "h": "2017 – 2022 · bahasa",
                     "p": "Kemajuan cepat pada pemrosesan bahasa alami. Transformer terbit "
                          "2017 -- bab 15 membongkarnya.", "style": "accent"},
                    {"ico": "🎨", "h": "2022 – kini · generatif",
                     "p": "Gelombang aplikasi AI generatif yang mengubah cara orang bekerja "
                          "sehari-hari.", "style": "accent"},
                ]},
                {"t": "p", "md": "Urutan ini penting untuk perencanaan: kemampuan yang "
                                 "matang lebih dulu -- persepsi -- adalah yang **paling "
                                 "murah dan paling andal** dipakai hari ini. Yang paling "
                                 "baru justru yang paling mahal dan paling belum stabil."},
                {"t": "band", "style": "amber",
                 "md": "Di lapangan, banyak kasus pemakaian yang benar-benar mendesak "
                       "sebetulnya jatuh di gelombang **pertama dan kedua** -- OCR dokumen, "
                       "klasifikasi keluhan, deteksi anomali. ==Tidak semuanya menuntut "
                       "model generatif.=="},
            ],
            "notes": "Slide ini sering mengubah arah diskusi anggaran. Tanyakan: kasus Anda "
                     "sebetulnya butuh gelombang yang mana?",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.4 -- 1.5",
            "title": "Waspadai gembar-gembor jangka pendek",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Ciri gembar-gembor sekarang**"},
                        {"t": "bullets", "items": [
                            "Ramalan pengangguran massal dan lonjakan produktivitas "
                            "**10x-100x** -- yang belum terjadi.",
                            "Narasi AGI dan superintelijensi yang menyeret jadwal jadi "
                            "tidak masuk akal.",
                            "Investasi AI -- terutama pusat data dan GPU -- melampaui "
                            "**$200 miliar per tahun**, sementara pendapatannya jauh "
                            "tertinggal di kisaran **$30 miliar**.",
                        ]},
                    ],
                    [
                        {"t": "p", "md": "**Dua musim dingin sebelumnya**"},
                        {"t": "bullets", "items": [
                            "**Pertama** -- Minsky, 1967: *\"Dalam satu generasi... persoalan "
                            "menciptakan kecerdasan buatan pada dasarnya akan terpecahkan.\"* "
                            "Pendanaan runtuh pada 1970-an.",
                            "**Kedua** -- *expert system* pada 1980-an; sekitar 1985 "
                            "perusahaan membelanjakan **lebih dari $1 miliar setahun**. "
                            "Pada awal 1990-an terbukti mahal dirawat, sulit diskalakan, "
                            "dan sempit cakupannya.",
                            "**Sekarang** -- masih di fase optimisme. Menurut Chollet, "
                            "kemunduran sebesar 1990-an ==tidak mungkin terulang== -- AI "
                            "sudah membuktikan nilainya. Kalau ada musim dingin, mestinya "
                            "sangat ringan.",
                        ]},
                    ],
                ]},
                {"t": "quote",
                 "md": "Today's \"artificial intelligence\" is more accurately described as "
                       "\"cognitive automation.\" AI excels at solving problems with narrowly "
                       "defined requirements.",
                 "cite": "Chollet & Watson, bab 1"},
            ],
            "notes": "Ini slide yang paling berguna saat peserta duduk di rapat anggaran. "
                     "Pesannya bukan 'jangan investasi', melainkan 'taksir sesuai apa yang "
                     "terbukti, bukan sesuai apa yang dijanjikan'.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.10",
            "title": "Urutannya terbalik dari yang dikira orang",
            "blocks": [
                {"t": "lead", "md": "Mudah mengira bahwa keberhasilan praktis AI generatif-lah "
                                    "yang melahirkan keyakinan akan AGI dalam waktu dekat. "
                                    "Menurut Chollet, ==yang terjadi justru sebaliknya=="},
                {"t": "steps", "items": [
                    "**2013** -- di kalangan elite teknologi sudah muncul kekhawatiran bahwa "
                    "AGI akan tiba dalam beberapa tahun. Saat itu yang dianggap di jalur "
                    "menuju ke sana adalah **DeepMind**, startup riset AI London yang "
                    "kemudian diakuisisi Google.",
                    "**2015** -- keyakinan itulah yang mendorong berdirinya **OpenAI**, yang "
                    "semula bermaksud menjadi penyeimbang sumber terbuka bagi DeepMind.",
                    "**2016** -- ajakan rekrutmen OpenAI menjanjikan **AGI tercapai pada 2020**. "
                    "Adil untuk dicatat: hanya sebagian kecil orang di industri yang percaya "
                    "jadwal seoptimistis itu waktu itu.",
                    "**Awal 2023** -- sebagian besar insinyur di San Francisco Bay Area tampak "
                    "yakin AGI akan tiba dalam satu-dua tahun berikutnya.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "OpenAI berperan penting menyalakan AI generatif. Jadi dalam pelintiran "
                       "yang ganjil, **keyakinan akan AGI-lah yang menaikkan AI generatif**, "
                       "bukan sebaliknya."},
            ],
            "notes": "Ini konteks yang jarang diketahui peserta dan sangat menolong saat "
                     "membaca berita AI: banyak klaim yang beredar adalah keturunan dari "
                     "keyakinan 2013, bukan simpulan dari bukti 2025.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.5",
            "title": "Otomasi kognitif bukan kecerdasan",
            "blocks": [
                {"t": "quote",
                 "md": "Intelligence is the ability to face the unknown, adapt to it, and "
                       "learn from it. Automation, even at its best, can only handle "
                       "situations it's been trained on.",
                 "cite": "Chollet & Watson, bab 1"},
                {"t": "table",
                 "head": ["", "Otomasi kognitif (yang kita punya)", "Kecerdasan (yang belum)"],
                 "widths": [18, 41, 41],
                 "rows": [
                     ["Cakupan", "Persoalan dengan syarat yang sempit dan jelas",
                      "Persoalan yang belum pernah dirumuskan siapa pun"],
                     ["Sumber kemampuan", "Contoh dalam data pelatihan",
                      "Penyesuaian saat berhadapan dengan yang tak dikenal"],
                     ["Saat menemui hal baru", "Menurun diam-diam, sering tanpa memberi tanda",
                      "Belajar dari situasi itu lalu memperbaiki diri"],
                 ]},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "Metafora Chollet: **AI itu seperti tokoh kartun, "
                                         "kecerdasan seperti makhluk hidup.** Kartun, "
                                         "sebagus apa pun gambarnya, hanya bisa memainkan "
                                         "adegan yang untuknya ia digambar. Makhluk hidup "
                                         "bisa menyesuaikan diri dengan yang tak terduga."},
                    ],
                    [
                        {"t": "p", "md": "*\"Kalau kartunnya digambar cukup realistis dan "
                                         "mencakup cukup banyak adegan, apa bedanya?\"* "
                                         "Bedanya adalah **keluwesan menyesuaikan diri** -- "
                                         "dan itulah sebabnya membangun otomasi yang kukuh "
                                         "begitu sulit: ia menuntut Anda memperhitungkan "
                                         "==setiap skenario yang mungkin=="},
                    ],
                ]},
                {"t": "band", "style": "rose",
                 "md": "Pembedaan ini punya akibat langsung di produksi: kalau sistem hanya "
                       "sanggup menangani apa yang pernah dilatihkan, maka ==pemantauan "
                       "pergeseran data bukan fitur tambahan==, melainkan syarat agar sistem "
                       "tetap layak dipakai. Bab 18 kembali ke sini."},
                {"t": "p", "md": "Karena itu Chollet menutup bagian ini dengan tenang: "
                                 "jangan cemas AI tiba-tiba sadar diri lalu mengambil alih "
                                 "kemanusiaan. Teknologi hari ini tidak menuju ke sana. "
                                 "*\"Seperti mengharapkan jam yang lebih baik akan melahirkan "
                                 "perjalanan waktu -- keduanya hal yang sama sekali berbeda.\"*"},
            ],
            "notes": "Ini jembatan ke seluruh sisa kursus. Kalimat kuncinya: model yang "
                     "bagus di laboratorium bisa jadi berbahaya di produksi, dan bedanya "
                     "ada pada apa yang tidak pernah ia lihat.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 1.6",
            "title": "Janji jangka panjang",
            "blocks": [
                {"t": "p", "md": "Chollet menutup bab ini dengan ramalannya sendiri dari 2017, "
                                 "yang sebagian besar sudah terpenuhi pada 2025 -- dipakai "
                                 "bukan untuk menyombong, melainkan untuk menunjukkan bentuk "
                                 "taksiran yang benar: **arahnya tepat, jadwalnya yang meleset**."},
                {"t": "table",
                 "head": ["Ramalan 2017", "Keadaannya pada 2025"],
                 "widths": [40, 60],
                 "rows": [
                     ["AI jadi asisten, bahkan teman",
                      "**Puluhan juta orang** memakai ChatGPT, Gemini, Claude sebagai asisten "
                      "harian. Ratusan ribu berinteraksi dengan \"teman\" AI di aplikasi "
                      "seperti Character.ai."],
                     ["Menjawab pertanyaan, membantu mendidik anak",
                      "Ternyata **penjawaban pertanyaan dan bantuan pekerjaan rumah** justru "
                      "menjadi pemakaian nomor satu chatbot ini."],
                     ["Mengantar Anda dari A ke B",
                      "Kemudi otonom penuh sudah terpasang dalam skala nyata di Phoenix, "
                      "San Francisco, Los Angeles, dan Austin."],
                     ["Membantu ilmuwan menemukan terobosan",
                      "**AlphaFold** membantu biolog meramal struktur protein. Matematikawan "
                      "**Terence Tao** memperkirakan AI bisa menjadi ko-penulis yang andal "
                      "dalam riset matematika sekitar 2026."],
                 ]},
                {"t": "band",
                 "md": "Kesimpulan bab: ==gembar-gembor jangka pendek akan kempis, "
                       "perubahan jangka panjang tetap datang==. Dua-duanya benar sekaligus, "
                       "dan itulah yang membuat perencanaan jadi sulit."},
            ],
            "notes": "Tutup dengan mengingatkan bahwa sisa buku ini praktis semua. Bab 1 "
                     "adalah satu-satunya bab yang boleh berdebat; setelah ini semuanya kode.",
        },

        # ------------------------------------------------------------- tutup -
        {
            "type": "slide",
            "kicker": "Ringkasan",
            "title": "Yang wajib terbawa dari bab 1",
            "blocks": [
                {"t": "steps", "items": [
                    "**AI ⊃ machine learning ⊃ deep learning.** Symbolic AI ada di dalam AI, "
                    "di luar ML.",
                    "**Machine learning membalik arah pemrograman**: data + jawaban masuk, "
                    "aturan keluar.",
                    "**Tiga bahan wajib**: masukan, contoh keluaran, dan ukuran mutu. "
                    "Yang paling sering hilang adalah yang ketiga.",
                    "**'Deep' = banyak lapis representasi**, bukan pemahaman yang lebih dalam.",
                    "**Bobot, fungsi rugi, backpropagation** -- lingkar pelatihan yang akan "
                    "dibongkar bab 2.",
                    "**Capaiannya nyata, taksirannya sering meleset.** Ini otomasi kognitif, "
                    "belum kecerdasan.",
                ]},
                {"t": "links", "items": [
                    {"k": "BAB BERIKUT", "ic": "➡", "v": "Bab 2 — Blok bangunan matematis",
                     "href": "../ch02/index.html"},
                    {"k": "TEKS PENUH", "ic": "📘", "v": "deeplearningwithpython.io",
                     "href": chapter_url(1)},
                    {"k": "KODE BUKU", "ic": "⌥", "v": "fchollet/deep-learning-with-python-notebooks",
                     "href": BOOK["code_repo"]},
                ]},
            ],
            "notes": "Kalau waktu habis, enam butir ini yang harus sempat dibacakan.",
        },
    ],
}
