# -*- coding: utf-8 -*-
"""Bab 2 — The mathematical building blocks of neural networks.

Sumber: Chollet & Watson, *Deep Learning with Python*, 3rd ed., bab 2.
https://deeplearningwithpython.io/chapters/chapter02_mathematical-building-blocks

Semua listing di bawah ini mengikuti naskah bab 2 (Keras 3). Keluaran yang
ditampilkan adalah keluaran nyata dari notebook pendamping, bukan karangan;
angka akurasi memang berayun sedikit antar-jalan, dan itu disebut apa adanya.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


# =============================================================================
#  Peraga
# =============================================================================

SVG_RANKS = """
<svg viewBox="0 0 760 216" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Skalar, vektor, matriks, dan tensor peringkat 3">
  <g>
    <text class="d-sm" x="14" y="20" fill="#22D3EE">rank 0 &#183; skalar</text>
    <rect class="d-box-a" x="14" y="34" width="34" height="34" rx="6"/>
    <text class="d-mono" x="31" y="56" text-anchor="middle">12</text>
    <text class="d-sm" x="14" y="92">shape ()</text>
  </g>
  <g>
    <text class="d-sm" x="150" y="20" fill="#22D3EE">rank 1 &#183; vektor</text>
    <rect class="d-box-a" x="150" y="34" width="170" height="34" rx="6"/>
    <text class="d-mono" x="235" y="56" text-anchor="middle">12  3  6  14  7</text>
    <text class="d-sm" x="150" y="92">shape (5,)</text>
  </g>
  <g>
    <text class="d-sm" x="410" y="20" fill="#22D3EE">rank 2 &#183; matriks</text>
    <rect class="d-box-a" x="410" y="34" width="150" height="58" rx="6"/>
    <text class="d-mono" x="485" y="54" text-anchor="middle">5 78  2 34 0</text>
    <text class="d-mono" x="485" y="72" text-anchor="middle">6 79  3 35 1</text>
    <text class="d-sm" x="410" y="112">shape (3, 5)</text>
  </g>
  <g>
    <text class="d-sm" x="612" y="20" fill="#22D3EE">rank 3</text>
    <rect class="d-box" x="632" y="34" width="104" height="46" rx="6"/>
    <rect class="d-box" x="624" y="42" width="104" height="46" rx="6"/>
    <rect class="d-box-a" x="616" y="50" width="104" height="46" rx="6"/>
    <text class="d-mono" x="668" y="78" text-anchor="middle">matriks &#215; n</text>
    <text class="d-sm" x="612" y="116">shape (3, 3, 5)</text>
  </g>

  <line x1="14" y1="140" x2="744" y2="140" stroke="rgba(140,190,255,.2)" stroke-width="1"/>
  <text class="d-lbl" x="14" y="166" font-weight="700">MNIST sebagai tensor</text>
  <text class="d-sm" x="14" y="188">
    train_images.ndim = 3  &#183;  shape (60000, 28, 28)  &#183;  dtype uint8
  </text>
  <text class="d-sm" x="14" y="208" fill="#F5B301">
    sumbu ke-0 selalu sumbu sampel &#8212; dan sumbu itulah yang dipotong jadi batch
  </text>
</svg>
"""

TIKZ_RANKS = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  bx/.style={draw=signal!60, fill=signal!9, rounded corners=2.5pt, text=ink},
  gx/.style={draw=rule, fill=papertint, rounded corners=2.5pt, text=ink2}]
  \node[text=signal, anchor=west] at (0,1.0) {rank 0 $\cdot$ skalar};
  \node[bx, minimum width=0.7cm, minimum height=0.55cm] at (0.35,0.5) {\ttfamily 12};
  \node[text=ink3, anchor=west] at (0,-0.1) {shape ()};

  \node[text=signal, anchor=west] at (1.9,1.0) {rank 1 $\cdot$ vektor};
  \node[bx, minimum width=2.6cm, minimum height=0.55cm] at (3.2,0.5) {\ttfamily 12~~3~~6~~14~~7};
  \node[text=ink3, anchor=west] at (1.9,-0.1) {shape (5,)};

  \node[text=signal, anchor=west] at (5.5,1.0) {rank 2 $\cdot$ matriks};
  \node[bx, minimum width=2.5cm, minimum height=0.9cm, align=center] at (6.75,0.35)
    {\ttfamily 5~78~~2~34~0\\\ttfamily 6~79~~3~35~1};
  \node[text=ink3, anchor=west] at (5.5,-0.4) {shape (3, 5)};

  \node[text=signal, anchor=west] at (8.6,1.0) {rank 3};
  \node[gx, minimum width=1.7cm, minimum height=0.7cm] at (9.75,0.62) {};
  \node[gx, minimum width=1.7cm, minimum height=0.7cm] at (9.62,0.48) {};
  \node[bx, minimum width=1.7cm, minimum height=0.7cm] at (9.49,0.34) {\ttfamily matriks $\times$ n};
  \node[text=ink3, anchor=west] at (8.6,-0.4) {shape (3, 3, 5)};

  \draw[rule] (0,-0.8) -- (11.2,-0.8);
  \node[anchor=west, font=\bfseries\scriptsize, text=ink] at (0,-1.15) {MNIST sebagai tensor};
  \node[anchor=west, text=ink2] at (0,-1.5)
    {\ttfamily train\_images.ndim = 3 $\cdot$ shape (60000, 28, 28) $\cdot$ dtype uint8};
  \node[anchor=west, text=amber] at (0,-1.85)
    {sumbu ke-0 selalu sumbu sampel --- dan sumbu itulah yang dipotong jadi batch};
\end{tikzpicture}
"""

SVG_BROADCAST = """
<svg viewBox="0 0 760 200" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Broadcasting: vektor bentuk (10,) disiarkan ke matriks (32, 10)">
  <defs>
    <marker id="bc" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.75)"/>
    </marker>
  </defs>
  <rect class="d-box-a" x="20" y="40" width="120" height="110" rx="8"/>
  <text class="d-sm" x="80" y="88" text-anchor="middle">X</text>
  <text class="d-mono" x="80" y="110" text-anchor="middle">(32, 10)</text>

  <text class="d-lbl" x="164" y="102">+</text>

  <rect class="d-box" x="196" y="86" width="120" height="22" rx="6"/>
  <text class="d-mono" x="256" y="102" text-anchor="middle">y  (10,)</text>

  <path class="d-arrow" d="M330,97 L376,97" marker-end="url(#bc)"/>
  <text class="d-sm" x="336" y="86" fill="#7E93B4">langkah 1</text>

  <rect class="d-box" x="392" y="86" width="130" height="22" rx="6"/>
  <text class="d-mono" x="457" y="102" text-anchor="middle">(1, 10)</text>
  <text class="d-sm" x="392" y="128" fill="#7E93B4">tambah sumbu</text>

  <path class="d-arrow" d="M530,97 L572,97" marker-end="url(#bc)"/>
  <text class="d-sm" x="532" y="86" fill="#7E93B4">langkah 2</text>

  <rect x="588" y="40" width="120" height="110" rx="8"
        fill="rgba(123,217,73,.12)" stroke="rgba(123,217,73,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="648" y="88" text-anchor="middle">Y</text>
  <text class="d-mono" x="648" y="110" text-anchor="middle">(32, 10)</text>
  <text class="d-sm" x="588" y="168" fill="#7E93B4">diulang 32 kali</text>

  <text class="d-sm" x="20" y="188" fill="#F5B301">
    tidak ada penggandaan memori sungguhan &#8212; pengulangannya hanya algoritmis
  </text>
</svg>
"""

TIKZ_BROADCAST = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  ar/.style={-{Stealth[length=4pt]}, signal, line width=0.7pt}]
  \node[draw=signal!60, fill=signal!9, rounded corners=3pt, minimum width=1.7cm,
        minimum height=1.6cm, text=ink, align=center] (x) at (0,0) {X\\\ttfamily (32, 10)};
  \node[text=ink, font=\small] at (1.25,0) {$+$};
  \node[draw=rule, fill=papertint, rounded corners=3pt, minimum width=1.7cm,
        minimum height=0.42cm, text=ink2] (y) at (2.6,0) {\ttfamily y (10,)};
  \node[draw=rule, fill=papertint, rounded corners=3pt, minimum width=1.5cm,
        minimum height=0.42cm, text=ink2] (y2) at (5.0,0) {\ttfamily (1, 10)};
  \node[draw=lime!60, fill=limebr!12, rounded corners=3pt, minimum width=1.7cm,
        minimum height=1.6cm, text=ink, align=center] (Y) at (7.4,0) {Y\\\ttfamily (32, 10)};
  \draw[ar] (y) -- node[above, text=ink3, font=\tiny]{langkah 1} (y2);
  \draw[ar] (y2) -- node[above, text=ink3, font=\tiny]{langkah 2} (Y);
  \node[text=ink3, anchor=north] at (5.0,-0.35) {tambah sumbu};
  \node[text=ink3, anchor=north] at (7.4,-0.95) {diulang 32 kali};
  \node[text=amber, anchor=west] at (-1.0,-1.55)
    {tidak ada penggandaan memori sungguhan --- pengulangannya hanya algoritmis};
\end{tikzpicture}
"""

SVG_GRAPH = """
<svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Graf komputasi dengan lintasan maju dan lintasan mundur">
  <defs>
    <marker id="fw" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.8)"/>
    </marker>
    <marker id="bw" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(245,179,1,.9)"/>
    </marker>
  </defs>

  <text class="d-sm" x="14" y="20" fill="#22D3EE">lintasan maju &#8212; hitung nilai</text>
  <rect class="d-box" x="14"  y="34" width="86" height="30" rx="7"/>
  <text class="d-mono" x="57" y="54" text-anchor="middle">x</text>
  <rect class="d-box-a" x="140" y="34" width="96" height="30" rx="7"/>
  <text class="d-mono" x="188" y="54" text-anchor="middle">x1 = W&#183;x</text>
  <rect class="d-box-a" x="276" y="34" width="96" height="30" rx="7"/>
  <text class="d-mono" x="324" y="54" text-anchor="middle">x2 = x1+b</text>
  <rect class="d-box-a" x="412" y="34" width="106" height="30" rx="7"/>
  <text class="d-mono" x="465" y="54" text-anchor="middle">y = relu(x2)</text>
  <rect x="558" y="34" width="96" height="30" rx="7"
        fill="rgba(251,113,133,.14)" stroke="rgba(251,113,133,.6)" stroke-width="1.4"/>
  <text class="d-mono" x="606" y="54" text-anchor="middle">loss</text>
  <path class="d-arrow" d="M100,49 L136,49"  marker-end="url(#fw)"/>
  <path class="d-arrow" d="M236,49 L272,49"  marker-end="url(#fw)"/>
  <path class="d-arrow" d="M372,49 L408,49"  marker-end="url(#fw)"/>
  <path class="d-arrow" d="M518,49 L554,49"  marker-end="url(#fw)"/>

  <line x1="14" y1="96" x2="744" y2="96" stroke="rgba(140,190,255,.2)" stroke-width="1"/>

  <text class="d-sm" x="14" y="124" fill="#F5B301">
    lintasan mundur &#8212; balik arah sisi, kalikan turunan sepanjang lintasan
  </text>
  <g stroke="rgba(245,179,1,.9)" stroke-width="1.6" fill="none">
    <path d="M554,152 L518,152" marker-end="url(#bw)"/>
    <path d="M408,152 L372,152" marker-end="url(#bw)"/>
    <path d="M272,152 L236,152" marker-end="url(#bw)"/>
    <path d="M136,152 L100,152" marker-end="url(#bw)"/>
  </g>
  <text class="d-mono" x="536" y="144" text-anchor="middle" fill="#F5B301">&#8706;loss/&#8706;y</text>
  <text class="d-mono" x="390" y="144" text-anchor="middle" fill="#F5B301">&#8706;y/&#8706;x2</text>
  <text class="d-mono" x="254" y="144" text-anchor="middle" fill="#F5B301">&#8706;x2/&#8706;x1</text>
  <text class="d-mono" x="118" y="144" text-anchor="middle" fill="#F5B301">&#8706;x1/&#8706;W</text>

  <rect x="14" y="180" width="730" height="52" rx="10"
        fill="rgba(245,179,1,.07)" stroke="rgba(245,179,1,.35)" stroke-width="1.2"/>
  <text class="d-mono" x="34" y="206" fill="#F0DFB4">
    grad(loss, W) = &#8706;loss/&#8706;y &#215; &#8706;y/&#8706;x2 &#215; &#8706;x2/&#8706;x1 &#215; &#8706;x1/&#8706;W
  </text>
  <text class="d-sm" x="34" y="224">
    aturan rantai, dijalankan mundur di atas graf &#8212; itulah backpropagation
  </text>
</svg>
"""

TIKZ_GRAPH = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  bx/.style={draw=rule, fill=papertint, rounded corners=3pt, minimum width=1.5cm,
             minimum height=0.5cm, text=ink2},
  ax/.style={draw=signal!60, fill=signal!9, rounded corners=3pt, minimum width=1.7cm,
             minimum height=0.5cm, text=ink},
  fw/.style={-{Stealth[length=4pt]}, signal, line width=0.7pt},
  bw/.style={-{Stealth[length=4pt]}, amberbr, line width=0.8pt}]

  \node[text=signal, anchor=west] at (0,0.7) {lintasan maju --- hitung nilai};
  \node[bx] (x)  at (0.75,0)  {\ttfamily x};
  \node[ax] (x1) at (2.9,0)   {\ttfamily x1 = W$\cdot$x};
  \node[ax] (x2) at (5.1,0)   {\ttfamily x2 = x1+b};
  \node[ax] (y)  at (7.4,0)   {\ttfamily y = relu(x2)};
  \node[draw=rose!70, fill=rosebr!14, rounded corners=3pt, minimum width=1.4cm,
        minimum height=0.5cm, text=ink] (l) at (9.6,0) {\ttfamily loss};
  \draw[fw] (x) -- (x1); \draw[fw] (x1) -- (x2); \draw[fw] (x2) -- (y); \draw[fw] (y) -- (l);

  \draw[rule] (0,-0.55) -- (10.5,-0.55);
  \node[text=amber, anchor=west] at (0,-0.9)
    {lintasan mundur --- balik arah sisi, kalikan turunan sepanjang lintasan};
  \draw[bw] (9.0,-1.35) -- (8.1,-1.35);
  \draw[bw] (6.8,-1.35) -- (5.8,-1.35);
  \draw[bw] (4.5,-1.35) -- (3.6,-1.35);
  \draw[bw] (2.3,-1.35) -- (1.4,-1.35);
  \node[text=amber, font=\ttfamily\tiny] at (8.55,-1.1)  {$\partial$loss/$\partial$y};
  \node[text=amber, font=\ttfamily\tiny] at (6.3,-1.1)   {$\partial$y/$\partial$x2};
  \node[text=amber, font=\ttfamily\tiny] at (4.05,-1.1)  {$\partial$x2/$\partial$x1};
  \node[text=amber, font=\ttfamily\tiny] at (1.85,-1.1)  {$\partial$x1/$\partial$W};

  \node[draw=amber!45, fill=amberbr!8, rounded corners=4pt, minimum width=10.2cm,
        minimum height=0.95cm, anchor=north west, align=left] at (0,-1.75) {};
  \node[anchor=west, text=ink, font=\ttfamily\tiny] at (0.25,-2.05)
    {grad(loss, W) = $\partial$loss/$\partial$y $\times$ $\partial$y/$\partial$x2 $\times$ $\partial$x2/$\partial$x1 $\times$ $\partial$x1/$\partial$W};
  \node[anchor=west, text=ink3] at (0.25,-2.4)
    {aturan rantai, dijalankan mundur di atas graf --- itulah backpropagation};
\end{tikzpicture}
"""


# =============================================================================
#  Deck
# =============================================================================

NB = ["01_mnist_pertama.ipynb", "02_tensor_dan_operasi.ipynb",
      "03_gradien_dan_sgd.ipynb", "04_mnist_dari_nol.ipynb"]

DECK = {
    "id": "ch02",
    "kind": "chapter",
    "number": 2,
    "title": "Blok Bangunan Matematis Jaringan Saraf",
    "subtitle": "Tensor, operasi tensor, dan penurunan berbasis gradien -- "
                "dijelaskan lewat kode yang bisa dijalankan, bukan notasi.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- bab 2",
    "source_url": chapter_url(2),
    "duration": "3 jam (2 sesi)",
    "presenter": {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Asisten Pengajar"},
    "resources": chapter_resources(2, local_notebooks=NB),
    "objectives": [
        "Menjalankan contoh MNIST pertama dari ujung ke ujung dan menyebut peran "
        "**layer, loss, optimizer, dan metric** pada tiap barisnya.",
        "Membaca **rank, shape, dan dtype** sebuah tensor, dan memetakan data "
        "nyata (vektor, deret waktu, citra, video) ke bentuk tensornya.",
        "Menjelaskan **operasi elemen-demi-elemen, broadcasting, hasil kali "
        "tensor, dan reshape** beserta arti geometrisnya.",
        "Menerangkan **turunan, gradien, SGD mini-batch, dan aturan rantai**, "
        "lalu menunjuk letaknya di dalam graf komputasi.",
        "Menulis ulang MNIST **dari nol** -- Dense, Sequential, batch generator, "
        "dan lingkar pelatihan -- tanpa memakai `fit()`.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Peta bab",
            "title": "Satu contoh, dibongkar sampai ke bawah",
            "blocks": [
                {"t": "lead", "md": "Bab 2 bergerak dalam satu lingkaran penuh: jalankan "
                                    "MNIST dengan `fit()`, bongkar tiap potongnya, lalu "
                                    "==tulis ulang seluruhnya dari nol== dan buktikan "
                                    "hasilnya sama."},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "🔢", "h": "1 · Contoh pertama",
                     "p": "MNIST dalam 10 baris. Berjalan dulu, dimengerti belakangan.",
                     "tag": "bag. 2.1"},
                    {"ico": "📦", "h": "2 · Tensor",
                     "p": "Rank, shape, dtype, irisan, sumbu batch, dan data dunia nyata.",
                     "tag": "bag. 2.2"},
                    {"ico": "⚙", "h": "3 · Operasi tensor",
                     "p": "Elemen-demi-elemen, broadcasting, matmul, reshape, dan geometrinya.",
                     "tag": "bag. 2.3"},
                    {"ico": "📉", "h": "4 · Mesinnya",
                     "p": "Turunan, gradien, SGD, aturan rantai, autodiff.",
                     "tag": "bag. 2.4-2.6"},
                ]},
                {"t": "quote",
                 "md": "Kode yang bisa dijalankan adalah keterangan paling tepat dan paling "
                       "tidak ambigu untuk sebuah operasi matematis.",
                 "cite": "Semangat bab 2 -- notasi diganti implementasi"},
            ],
            "notes": "Sesi ini panjang. Pecah di antara bagian 2.3 dan 2.4; separuh pertama "
                     "soal data, separuh kedua soal belajar.",
        },

        {"type": "section", "num": "01", "title": "Sekali lihat jaringan saraf",
         "lead": "MNIST -- 'hello world'-nya deep learning."},

        {
            "type": "slide",
            "kicker": "Bagian 2.1",
            "title": "Muat data: 60.000 latih, 10.000 uji",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 2.1 — memuat MNIST",
                 "src": """from keras.datasets import mnist

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

print(train_images.shape, train_images.dtype)
print(len(train_labels), train_labels[:10])
print(test_images.shape)"""},
                {"t": "out", "src": """(60000, 28, 28) uint8
60000 [5 0 4 1 9 2 1 3 1 4]
(10000, 28, 28)"""},
                {"t": "table",
                 "head": ["Istilah", "Artinya di sini"],
                 "widths": [24, 76],
                 "rows": [
                     ["**Sample**", "Satu titik data -- satu citra 28×28."],
                     ["**Class**", "Satu kategori -- angka 0 sampai 9."],
                     ["**Label**", "Kelas yang melekat pada satu sample tertentu."],
                 ]},
            ],
            "notes": "Tunjukkan satu citra dengan matplotlib sebelum lanjut; peserta perlu "
                     "melihat bahwa 'data' di sini benar-benar gambar.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.1",
            "title": "Model, kompilasi, pelatihan -- sepuluh baris",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 2.2-2.5 — MNIST ujung ke ujung",
                 "src": """import keras
from keras import layers

model = keras.Sequential([
    layers.Dense(512, activation="relu"),
    layers.Dense(10, activation="softmax"),
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

train_images = train_images.reshape((60000, 28 * 28)).astype("float32") / 255
test_images = test_images.reshape((10000, 28 * 28)).astype("float32") / 255

model.fit(train_images, train_labels, epochs=5, batch_size=128)"""},
                {"t": "band",
                 "md": "Sebuah **layer** adalah *penyaring data*: ia menerima data dan "
                       "mengeluarkan representasi yang lebih berguna. `softmax` di lapis "
                       "akhir mengeluarkan ==10 skor peluang yang berjumlah 1==."},
            ],
            "notes": "Perhatikan: tidak ada input_shape. Keras menyimpulkan bentuk masukan "
                     "sendiri pada pemanggilan pertama — dibahas di bab 3.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.1",
            "title": "Hasilnya -- dan celah pertama yang harus dicurigai",
            "blocks": [
                {"t": "out", "src": """Epoch 1/5
469/469 ---- 3s 5ms/step - accuracy: 0.8747 - loss: 0.4358
Epoch 5/5
469/469 ---- 2s 5ms/step - accuracy: 0.9890 - loss: 0.0361

313/313 ---- 1s 2ms/step - accuracy: 0.9780 - loss: 0.0745
test accuracy: 0.978"""},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "stats", "cols": 2, "items": [
                            {"v": "98,9%", "l": "akurasi pada data latih"},
                            {"v": "97,8%", "l": "akurasi pada data uji"},
                        ]},
                    ],
                    [
                        {"t": "band", "style": "amber",
                         "md": "Selisih ~1,1 poin itu bukan derau. Itu **overfitting**: "
                               "model bekerja lebih baik pada yang pernah dilihatnya. "
                               "Bab 5 membahasnya sebagai persoalan pokok."},
                    ],
                ]},
                {"t": "code", "lang": "python", "file": "listing 2.6 — meramal",
                 "src": """test_digits = test_images[0:10]
predictions = model.predict(test_digits)
print(predictions[0].argmax(), predictions[0].max(), test_labels[0])"""},
                {"t": "out", "src": "7 0.99993 7"},
            ],
            "notes": "Angka pastinya berayun tiap kali dilatih ulang — katakan itu di depan, "
                     "supaya peserta tidak panik kalau notebooknya memberi 97,6%.",
        },

        {"type": "section", "num": "02", "title": "Representasi data: tensor",
         "lead": "Wadah untuk data. Tiga sifat, dan satu sumbu istimewa."},

        {
            "type": "slide",
            "kicker": "Bagian 2.2",
            "title": "Rank, shape, dtype",
            "blocks": [
                {"t": "fig", "svg": SVG_RANKS, "tikz": TIKZ_RANKS,
                 "cap": "Tensor menggeneralisasi matriks ke sebarang jumlah sumbu. "
                        "TensorFlow diberi nama menurut benda ini."},
                {"t": "band", "style": "amber",
                 "md": "Jebakan istilah: **vektor 5 dimensi ≠ tensor 5 dimensi**. Yang "
                       "pertama punya ==satu sumbu berisi lima angka==; yang kedua punya "
                       "==lima sumbu==. Salah baca di sini membuat pesan galat shape jadi "
                       "tidak terbaca."},
            ],
            "notes": "Tanya ke peserta: shape sebuah batch 128 citra RGB 224x224 itu apa? "
                     "Jawabannya (128, 224, 224, 3) — dan itu latihan yang bagus.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.2",
            "title": "Irisan tensor dan sumbu batch",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 2.7-2.9 — irisan",
                 "src": """my_slice = train_images[10:100]          # 90 citra
print(my_slice.shape)

print(train_images[:, 14:, 14:].shape)   # pojok kanan-bawah 14x14
print(train_images[:, 7:-7, 7:-7].shape) # 14x14 di tengah

batch = train_images[:128]               # batch ke-0
batch = train_images[128:256]            # batch ke-1
n = 3
batch = train_images[128 * n : 128 * (n + 1)]"""},
                {"t": "out", "src": """(90, 28, 28)
(60000, 14, 14)
(60000, 14, 14)"""},
                {"t": "band",
                 "md": "Sumbu ke-0 selalu **sumbu sampel**, dan karena model dilatih per "
                       "potongan kecil, sumbu itu juga disebut ==sumbu batch==. Setiap "
                       "pesan galat shape yang akan Anda temui dimulai dari membaca "
                       "sumbu ini."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.2.7-2.2.10",
            "title": "Data dunia nyata, dan bentuk tensornya",
            "blocks": [
                {"t": "table",
                 "head": ["Jenis data", "Rank", "Shape", "Contoh dari buku"],
                 "widths": [22, 8, 30, 40],
                 "rows": [
                     ["**Vektor**", "2", "`(samples, features)`",
                      "100.000 orang × (usia, jenis kelamin, penghasilan) → (100000, 3)"],
                     ["**Deret waktu**", "3", "`(samples, timesteps, features)`",
                      "250 hari × 390 menit × 3 nilai → (250, 390, 3)"],
                     ["**Citra**", "4", "`(samples, h, w, channels)`",
                      "128 citra RGB 256×256 → (128, 256, 256, 3)"],
                     ["**Video**", "5", "`(samples, frames, h, w, channels)`",
                      "4 klip × 240 bingkai × 144×256 × RGB → (4, 240, 144, 256, 3)"],
                 ]},
                {"t": "cols", "ratio": "3-2", "cols": [
                    [
                        {"t": "bullets", "items": [
                            "**Channels-last** `(…, h, w, c)` -- kebiasaan TensorFlow dan JAX.",
                            "**Channels-first** `(…, c, h, w)` -- kebiasaan PyTorch.",
                            "Keras 3 memakai `image_data_format` untuk memilih; salah "
                            "setelan di sini ==menghasilkan galat shape yang membingungkan==.",
                        ]},
                    ],
                    [
                        {"t": "stats", "cols": 1, "items": [
                            {"v": "106.168.320", "l": "nilai dalam contoh video 60 detik itu"},
                            {"v": "425 MB", "l": "ukurannya pada float32"},
                        ]},
                    ],
                ]},
            ],
            "notes": "Data tabular dan data transaksi umumnya masuk baris pertama (vektor) "
                     "atau kedua (deret waktu). Minta peserta menaksir shape datanya sendiri.",
        },

        {"type": "section", "num": "03", "title": "Gigi-giginya: operasi tensor",
         "lead": "Semuanya bermuara pada segenggam operasi -- dan semuanya punya arti geometris."},

        {
            "type": "slide",
            "kicker": "Bagian 2.3",
            "title": "Satu lapis Dense = tiga operasi",
            "blocks": [
                {"t": "code", "lang": "python", "file": "inti sebuah lapis Dense",
                 "src": """# output = relu(matmul(input, W) + b)
#            ^          ^            ^
#            |          |            +-- penjumlahan (dengan broadcasting)
#            |          +--------------- hasil kali tensor
#            +-------------------------- operasi elemen-demi-elemen

def naive_relu(x):
    assert len(x.shape) == 2
    x = x.copy()
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            x[i, j] = max(x[i, j], 0)
    return x"""},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "versi tervektorisasi",
                         "src": """z = x + y
z = np.maximum(z, 0.0)"""},
                    ],
                    [
                        {"t": "stats", "cols": 2, "items": [
                            {"v": "0,02 s", "l": "NumPy tervektorisasi, 1.000 iterasi"},
                            {"v": "2,45 s", "l": "gelung Python naif, 1.000 iterasi"},
                        ]},
                    ],
                ]},
                {"t": "band",
                 "md": "Selisih ==sekitar 100 kali== itu bukan soal bahasa. Versi NumPy "
                       "melimpahkan pekerjaannya ke BLAS yang ditulis dalam C dan Fortran; "
                       "di GPU, kode CUDA-nya tervektorisasi penuh."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.3.2",
            "title": "Broadcasting: bentuk kecil dipaskan ke bentuk besar",
            "blocks": [
                {"t": "fig", "svg": SVG_BROADCAST, "tikz": TIKZ_BROADCAST,
                 "cap": "Dua langkah: tambahkan sumbu sampai rank sama, lalu ulangi "
                        "sepanjang sumbu baru itu."},
                {"t": "code", "lang": "python", "file": "listing 2.11 — aturannya",
                 "src": """X = np.random.random((64, 3, 32, 10))
y = np.random.random((32, 10))
z = np.maximum(X, y)          # y disiarkan; hasilnya (64, 3, 32, 10)
print(z.shape)"""},
                {"t": "out", "src": "(64, 3, 32, 10)"},
            ],
            "notes": "Aturan umumnya: shape (a, b, ..., n, n+1, ..., m) berpasangan dengan "
                     "(n, n+1, ..., m). Broadcasting adalah sumber bug diam yang paling "
                     "sering — bentuknya cocok, artinya tidak.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.3.3-2.3.4",
            "title": "Hasil kali tensor dan reshape",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "matmul",
                         "src": """z = np.matmul(x, y)
z = x @ y            # bentuk singkat

# aturan kecocokan:
#   x.shape[1] == y.shape[0]
# hasilnya:
#   (x.shape[0], y.shape[1])

# (a, b, c, d) @ (d,)   -> (a, b, c)
# (a, b, c, d) @ (d, e) -> (a, b, c, e)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "reshape & transpose",
                         "src": """x = np.array([[0., 1.],
              [2., 3.],
              [4., 5.]])          # (3, 2)

np.reshape(x, (6,))               # (6,)
np.reshape(x, (2, 3))             # (2, 3)

x = np.zeros((300, 20))
np.transpose(x).shape             # (20, 300)"""},
                    ],
                ]},
                {"t": "band",
                 "md": "Reshape ==tidak mengubah satu pun koefisien==; ia hanya menata "
                       "ulang. Itulah yang terjadi pada `train_images.reshape((60000, 784))` "
                       "di contoh pertama tadi."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.3.5",
            "title": "Tafsir geometris -- dan mengapa aktivasi wajib ada",
            "blocks": [
                {"t": "table",
                 "head": ["Operasi", "Artinya secara geometris"],
                 "widths": [30, 70],
                 "rows": [
                     ["Penjumlahan vektor", "**Translasi** -- geser objek sejauh dan searah vektor itu."],
                     ["Kali matriks rotasi", "**Rotasi** sebesar sudut θ."],
                     ["Kali matriks diagonal", "**Penskalaan** mendatar dan menegak."],
                     ["Kali matriks sebarang", "**Transformasi linear**."],
                     ["Linear + translasi", "**Transformasi afin** -- persis `y = W @ x + b`."],
                 ]},
                {"t": "band", "style": "rose",
                 "md": "Merangkai dua transformasi afin menghasilkan **satu** transformasi "
                       "afin lagi: `affine2(affine1(x)) = (W2 @ W1) @ x + (W2 @ b1 + b2)`. "
                       "Jadi tumpukan Dense tanpa aktivasi ==diam-diam hanyalah satu model "
                       "linear==, sedalam apa pun. Fungsi aktivasi seperti ReLU-lah yang "
                       "membuat ruang hipotesisnya kaya."},
                {"t": "p", "md": "Gambaran yang dipakai Chollet: deep learning seperti "
                                 "**membuka remasan kertas**. Data yang terlipat rumit "
                                 "diluruskan sedikit demi sedikit oleh tiap lapis, sampai "
                                 "kelas-kelasnya bisa dipisah dengan bersih."},
            ],
            "notes": "Kalau ada satu hal dari bab 2 yang harus diingat manajer produk, ini: "
                     "tanpa nonlinearitas, kedalaman tidak membeli apa pun.",
        },

        {"type": "section", "num": "04", "title": "Mesinnya: penurunan berbasis gradien",
         "lead": "Turunan, gradien, SGD, dan aturan rantai."},

        {
            "type": "slide",
            "kicker": "Bagian 2.4",
            "title": "Lingkar pelatihan, dan langkah yang sulit",
            "blocks": [
                {"t": "steps", "items": [
                    "Ambil satu batch sampel `x` dan target `y_true`.",
                    "Jalankan model pada `x` (**lintasan maju**) → `y_pred`.",
                    "Hitung **rugi**: selisih antara `y_pred` dan `y_true`.",
                    "Perbarui bobot supaya ruginya turun sedikit.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "Langkah 4 itulah yang sulit. Menyetel tiap koefisien satu per satu "
                       "mustahil -- jaringan modern punya ==jutaan sampai miliaran parameter==. "
                       "Penurunan gradien menyelesaikannya sekaligus."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Turunan** adalah kemiringan hampiran linear "
                                         "setempat: untuk ε_x cukup kecil, "
                                         "`f(x + ε_x) ≈ y + a·ε_x`."},
                        {"t": "bullets", "items": [
                            "`a` negatif → menaikkan `x` **menurunkan** `f(x)`.",
                            "`a` positif → menaikkan `x` **menaikkan** `f(x)`.",
                            "Untuk mengecilkan `f`, geser `x` ==berlawanan arah turunannya==.",
                        ]},
                    ],
                    [
                        {"t": "p", "md": "**Gradien** adalah turunan untuk operasi tensor. "
                                         "Ia tensor sebentuk `W`, dan tiap koefisiennya "
                                         "menyatakan arah dan besar perubahan rugi bila "
                                         "koefisien `W` itu digeser."},
                        {"t": "band",
                         "md": "`W1 = W0 - step * grad(f(W0), W0)`"},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.4.3",
            "title": "SGD mini-batch, dan mengapa tidak diselesaikan secara analitis",
            "blocks": [
                {"t": "p", "md": "Minimum ada di tempat turunannya nol. Tetapi menyelesaikan "
                                 "`grad(f(W), W) = 0` secara analitis ==tidak terjangkau== "
                                 "untuk jaringan berparameter jutaan. Maka: iterasi."},
                {"t": "steps", "items": [
                    "Ambil batch acak `x`, `y_true`. (Kata *stochastic* datang dari **acak** ini.)",
                    "Lintasan maju → `y_pred`.",
                    "Hitung rugi.",
                    "**Lintasan mundur** → gradien rugi terhadap parameter.",
                    "`W -= learning_rate * gradient`.",
                ]},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🐢", "h": "Learning rate terlalu kecil",
                     "p": "Kekonvergenan lambat; banyak langkah untuk sedikit kemajuan.",
                     "style": "warn"},
                    {"ico": "🌀", "h": "Terlalu besar",
                     "p": "Pembaruan jadi ==acak==; rugi melompat-lompat dan tidak turun.",
                     "style": "bad"},
                    {"ico": "🎯", "h": "Momentum",
                     "p": "Perbarui berdasar gradien **sekarang dan pembaruan sebelumnya** -- "
                          "seperti bola menggelinding, cukup laju untuk melewati cekungan "
                          "dangkal.", "style": "good"},
                ]},
                {"t": "p", "md": "Varian yang memperbaiki kekonvergenan disebut **optimizer**: "
                                 "SGD dengan momentum, Adagrad, RMSprop, Adam."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.4.4-2.4.5",
            "title": "Aturan rantai di atas graf komputasi = backpropagation",
            "blocks": [
                {"t": "fig", "svg": SVG_GRAPH, "tikz": TIKZ_GRAPH,
                 "cap": "Graf komputasi adalah graf berarah tanpa siklus. Ia membuat "
                        "perhitungan bisa diperlakukan sebagai data -- struktur yang "
                        "terbaca mesin."},
                {"t": "bullets", "items": [
                    "Bila ada **beberapa lintasan** dari simpul `a` ke `b`, sumbangan tiap "
                    "lintasan ==dijumlahkan==.",
                    "Kerangka kerja modern menjalankan ini sendiri: itulah **automatic "
                    "differentiation**. Anda tidak pernah menulis backprop dengan tangan.",
                ]},
            ],
            "notes": "Kalau peserta pernah menurunkan backprop manual di kuliah S1, katakan "
                     "bahwa yang mereka kerjakan dulu itu persis ini — hanya saja kini "
                     "dikerjakan oleh graf.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.4.5",
            "title": "GradientTape: gradien dalam tiga baris",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 2.19-2.20 — autodiff",
                 "src": """import tensorflow as tf

x = tf.Variable(3.0)
with tf.GradientTape() as tape:
    y = 2 * x + 3
print(tape.gradient(y, x))          # dy/dx = 2

# turunan kedua: pita bersarang
time = tf.Variable(0.0)
with tf.GradientTape() as outer_tape:
    with tf.GradientTape() as inner_tape:
        position = 4.9 * time ** 2
    speed = inner_tape.gradient(position, time)
acceleration = outer_tape.gradient(speed, time)
print(acceleration)                 # 9.8"""},
                {"t": "out", "src": """tf.Tensor(2.0, shape=(), dtype=float32)
tf.Tensor(9.8, shape=(), dtype=float32)"""},
                {"t": "band",
                 "md": "Contoh kedua bukan sekadar pamer: `position = 4.9·t²` adalah "
                       "jatuh bebas, dan turunan keduanya memang ==percepatan gravitasi==. "
                       "Autodiff mengembalikan 9,8 tanpa pernah diberi tahu rumusnya."},
            ],
        },

        {"type": "section", "num": "05", "title": "Menulis ulang dari nol",
         "lead": "Tanpa fit(), tanpa Dense bawaan. Hasilnya harus sama."},

        {
            "type": "slide",
            "kicker": "Bagian 2.6.1",
            "title": "NaiveDense dan NaiveSequential",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 2.21-2.22 — lapis dan model",
                 "src": """import keras
from keras import ops

class NaiveDense:
    def __init__(self, input_size, output_size, activation=None):
        self.activation = activation
        self.W = keras.Variable(shape=(input_size, output_size), initializer="uniform")
        self.b = keras.Variable(shape=(output_size,), initializer="zeros")

    def __call__(self, inputs):
        x = ops.matmul(inputs, self.W) + self.b
        return self.activation(x) if self.activation is not None else x

    @property
    def weights(self):
        return [self.W, self.b]

class NaiveSequential:
    def __init__(self, layers):
        self.layers = layers

    def __call__(self, inputs):
        x = inputs
        for layer in self.layers:
            x = layer(x)
        return x

    @property
    def weights(self):
        return [w for layer in self.layers for w in layer.weights]"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.6.2-2.6.4",
            "title": "Satu langkah pelatihan, dan gelungnya",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 2.24-2.26 — lingkar pelatihan",
                 "src": """import tensorflow as tf
from keras import optimizers

optimizer = optimizers.SGD(learning_rate=1e-3)

def one_training_step(model, images_batch, labels_batch):
    with tf.GradientTape() as tape:
        predictions = model(images_batch)
        loss = ops.sparse_categorical_crossentropy(labels_batch, predictions)
        average_loss = ops.mean(loss)
    gradients = tape.gradient(average_loss, model.weights)
    optimizer.apply_gradients(zip(gradients, model.weights))
    return average_loss

def fit(model, images, labels, epochs, batch_size=128):
    for epoch in range(epochs):
        print(f"Epoch {epoch}")
        gen = BatchGenerator(images, labels, batch_size)
        for i in range(gen.num_batches):
            images_batch, labels_batch = gen.next()
            loss = one_training_step(model, images_batch, labels_batch)
            if i % 100 == 0:
                print(f"  loss at batch {i}: {loss:.2f}")"""},
                {"t": "band",
                 "md": "Empat langkah pada slide lingkar pelatihan tadi kini terlihat "
                       "sebagai empat baris: ==maju, rugi, gradien, perbarui==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 2.6.5",
            "title": "Buktinya: hasilnya memang sama",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 2.27 — menilai model",
                 "src": """model = NaiveSequential([
    NaiveDense(input_size=28 * 28, output_size=512, activation=ops.relu),
    NaiveDense(input_size=512, output_size=10, activation=ops.softmax),
])
fit(model, train_images, train_labels, epochs=10, batch_size=128)

predictions = model(test_images)
predicted_labels = ops.argmax(predictions, axis=1)
matches = predicted_labels == test_labels
print(f"accuracy: {ops.mean(matches):.2f}")"""},
                {"t": "out", "src": """Epoch 0
  loss at batch 0: 6.19
  loss at batch 400: 2.21
Epoch 9
  loss at batch 0: 0.36
  loss at batch 400: 0.34
accuracy: 0.90"""},
                {"t": "band", "style": "amber",
                 "md": "Sengaja ==lebih rendah dari 97,8%==. Bedanya bukan sihir Keras: "
                       "versi ini memakai SGD polos dengan learning rate 1e-3, sedangkan "
                       "yang pertama memakai **Adam**. Itu justru pelajarannya -- pilihan "
                       "optimizer berdampak sebesar itu."},
            ],
            "notes": "Ini slide yang paling sering salah dibaca. Tegaskan: turunnya akurasi "
                     "bukan bukti bahwa implementasi manualnya salah.",
        },

        {
            "type": "slide",
            "kicker": "Ringkasan",
            "title": "Yang wajib terbawa dari bab 2",
            "blocks": [
                {"t": "steps", "items": [
                    "**Tensor** = wadah angka dengan **rank, shape, dtype**. Sumbu ke-0 "
                    "adalah sumbu sampel alias sumbu batch.",
                    "**Operasi tensor** punya arti geometris. Dense tanpa aktivasi hanya "
                    "transformasi afin -- dan tumpukannya tetap afin.",
                    "**Belajar** = mencari nilai bobot yang mengecilkan rugi pada data latih.",
                    "**SGD mini-batch** memperbarui bobot dari gradien pada batch acak.",
                    "**Aturan rantai + autodiff** = backpropagation; graf komputasi yang "
                    "mengerjakannya.",
                    "**Loss** menakar keberhasilan tugas; **optimizer** menentukan varian "
                    "penurunan gradiennya.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_mnist_pertama.ipynb",
                     "href": "../../course-slides/notebooks/ch02/01_mnist_pertama.ipynb"},
                    {"k": "NOTEBOOK", "ic": "📓", "v": "04_mnist_dari_nol.ipynb",
                     "href": "../../course-slides/notebooks/ch02/04_mnist_dari_nol.ipynb"},
                    {"k": "BAB BERIKUT", "ic": "➡", "v": "Bab 3 — Kerangka kerja",
                     "href": "../ch03/index.html"},
                ]},
            ],
        },
    ],
}
