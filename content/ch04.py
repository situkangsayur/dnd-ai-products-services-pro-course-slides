# -*- coding: utf-8 -*-
"""Bab 4 — Classification and regression.

Sumber: Chollet & Watson, *Deep Learning with Python*, 3rd ed., bab 4.
https://deeplearningwithpython.io/chapters/chapter04_classification-and-regression

Tiga contoh lengkap: IMDB (biner), Reuters (multikelas), California Housing
(regresi skalar). Angka hasil mengikuti naskah bab; yang berayun antar-jalan
ditandai apa adanya.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


SVG_OVERFIT = """
<svg viewBox="0 0 760 260" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Kurva rugi latih menurun terus, rugi validasi berbalik naik setelah epoch 4">
  <!-- sumbu -->
  <line x1="70" y1="212" x2="700" y2="212" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>
  <line x1="70" y1="26"  x2="70"  y2="212" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>
  <text class="d-sm" x="385" y="240" text-anchor="middle" fill="#7E93B4">epoch</text>
  <text class="d-sm" x="24"  y="120" fill="#7E93B4" transform="rotate(-90 24 120)">rugi</text>

  <!-- gridlines -->
  <g stroke="rgba(140,190,255,.10)" stroke-width="1">
    <line x1="70" y1="166" x2="700" y2="166"/>
    <line x1="70" y1="120" x2="700" y2="120"/>
    <line x1="70" y1="74"  x2="700" y2="74"/>
  </g>

  <!-- rugi latih: turun monoton -->
  <path d="M70,52 C160,104 250,146 340,170 C430,188 520,198 700,204"
        fill="none" stroke="#22D3EE" stroke-width="2.4"/>
  <!-- rugi validasi: turun lalu naik -->
  <path d="M70,66 C130,110 180,138 226,146 C300,158 420,182 700,206"
        fill="none" stroke="#FB7185" stroke-width="2.4"
        transform="translate(0,0)"/>
  <path d="M226,146 C320,136 460,104 700,54"
        fill="none" stroke="#FB7185" stroke-width="2.4"/>

  <!-- titik balik -->
  <line x1="226" y1="26" x2="226" y2="212"
        stroke="rgba(245,179,1,.7)" stroke-width="1.4" stroke-dasharray="5 4"/>
  <circle cx="226" cy="146" r="5" fill="#F5B301"/>
  <text class="d-sm" x="236" y="44" fill="#F5B301">epoch 4 &#8212; titik terbaik</text>

  <!-- legenda -->
  <rect x="470" y="220" width="16" height="3" fill="#22D3EE"/>
  <text class="d-sm" x="494" y="226">rugi latih</text>
  <rect x="580" y="220" width="16" height="3" fill="#FB7185"/>
  <text class="d-sm" x="604" y="226">rugi validasi</text>

  <text class="d-sm" x="360" y="96" fill="#FB7185">mulai overfitting</text>
</svg>
"""

TIKZ_OVERFIT = r"""
\begin{tikzpicture}[font=\sffamily\tiny]
  \draw[rule, line width=0.8pt] (0,0) -- (8.6,0);
  \draw[rule, line width=0.8pt] (0,0) -- (0,3.0);
  \node[text=ink3, anchor=north] at (4.3,-0.15) {epoch};
  \node[text=ink3, rotate=90, anchor=south] at (-0.35,1.5) {rugi};
  \draw[signal, line width=1.2pt]
    (0,2.6) .. controls (1.2,1.7) and (2.4,1.05) .. (4.0,0.62)
            .. controls (5.6,0.35) and (7.0,0.22) .. (8.6,0.15);
  \draw[rose, line width=1.2pt]
    (0,2.4) .. controls (0.8,1.6) and (1.5,1.15) .. (2.1,1.02);
  \draw[rose, line width=1.2pt]
    (2.1,1.02) .. controls (3.6,1.25) and (5.8,1.95) .. (8.6,2.75);
  \draw[amberbr, line width=0.9pt, dashed] (2.1,0) -- (2.1,3.0);
  \fill[amberbr] (2.1,1.02) circle (2.2pt);
  \node[text=amber, anchor=west] at (2.25,2.85) {epoch 4 --- titik terbaik};
  \node[text=rose, anchor=west] at (4.2,1.95) {mulai overfitting};
  \draw[signal, line width=1.2pt] (4.6,-0.55) -- (4.95,-0.55);
  \node[text=ink3, anchor=west] at (5.0,-0.55) {rugi latih};
  \draw[rose, line width=1.2pt] (6.5,-0.55) -- (6.85,-0.55);
  \node[text=ink3, anchor=west] at (6.9,-0.55) {rugi validasi};
\end{tikzpicture}
"""

SVG_BOTTLENECK = """
<svg viewBox="0 0 760 200" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Lapis 4 unit menjadi leher botol informasi di antara 64 dan 46">
  <defs>
    <marker id="bn" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.75)"/>
    </marker>
  </defs>

  <text class="d-sm" x="20" y="22" fill="#7BD949">yang benar</text>
  <rect class="d-box-a" x="20"  y="34" width="76" height="48" rx="8"/>
  <text class="d-mono" x="58" y="63" text-anchor="middle">64</text>
  <rect class="d-box-a" x="128" y="34" width="76" height="48" rx="8"/>
  <text class="d-mono" x="166" y="63" text-anchor="middle">64</text>
  <rect x="236" y="34" width="86" height="48" rx="8"
        fill="rgba(123,217,73,.14)" stroke="rgba(123,217,73,.6)" stroke-width="1.4"/>
  <text class="d-mono" x="279" y="63" text-anchor="middle">46</text>
  <path class="d-arrow" d="M96,58 L124,58"  marker-end="url(#bn)"/>
  <path class="d-arrow" d="M204,58 L232,58" marker-end="url(#bn)"/>
  <text class="d-sm" x="342" y="63" fill="#7BD949">akurasi ~80%</text>

  <line x1="20" y1="106" x2="740" y2="106" stroke="rgba(140,190,255,.2)" stroke-width="1"/>

  <text class="d-sm" x="20" y="132" fill="#FB7185">leher botol informasi</text>
  <rect class="d-box" x="20"  y="144" width="76" height="44" rx="8"/>
  <text class="d-mono" x="58" y="171" text-anchor="middle">64</text>
  <rect x="128" y="156" width="76" height="20" rx="6"
        fill="rgba(251,113,133,.18)" stroke="rgba(251,113,133,.75)" stroke-width="1.5"/>
  <text class="d-mono" x="166" y="171" text-anchor="middle" fill="#FB7185">4</text>
  <rect class="d-box" x="236" y="144" width="86" height="44" rx="8"/>
  <text class="d-mono" x="279" y="171" text-anchor="middle">46</text>
  <path class="d-arrow" d="M96,166 L124,166"  marker-end="url(#bn)"/>
  <path class="d-arrow" d="M204,166 L232,166" marker-end="url(#bn)"/>
  <text class="d-sm" x="342" y="171" fill="#FB7185">akurasi ~71% &#8212; turun 8 poin</text>
  <text class="d-sm" x="342" y="189" fill="#7E93B4">
    46 kelas tidak muat diperas ke 4 dimensi
  </text>
</svg>
"""

TIKZ_BOTTLENECK = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  u/.style={draw=signal!60, fill=signal!9, rounded corners=3pt, minimum width=1.1cm,
            minimum height=0.75cm, text=ink},
  ar/.style={-{Stealth[length=4pt]}, signal, line width=0.7pt}]
  \node[text=lime, anchor=west] at (0,1.15) {yang benar};
  \node[u] (a1) at (0.7,0.55) {\ttfamily 64};
  \node[u] (a2) at (2.3,0.55) {\ttfamily 64};
  \node[draw=lime!60, fill=limebr!14, rounded corners=3pt, minimum width=1.2cm,
        minimum height=0.75cm, text=ink] (a3) at (3.9,0.55) {\ttfamily 46};
  \draw[ar] (a1) -- (a2); \draw[ar] (a2) -- (a3);
  \node[text=lime, anchor=west] at (4.7,0.55) {akurasi ${\sim}80\%$};

  \draw[rule] (0,0.0) -- (9.0,0.0);

  \node[text=rose, anchor=west] at (0,-0.4) {leher botol informasi};
  \node[u] (b1) at (0.7,-1.05) {\ttfamily 64};
  \node[draw=rose!75, fill=rosebr!18, rounded corners=3pt, minimum width=1.1cm,
        minimum height=0.32cm, text=ink] (b2) at (2.3,-1.05) {\ttfamily 4};
  \node[u] (b3) at (3.9,-1.05) {\ttfamily 46};
  \draw[ar] (b1) -- (b2); \draw[ar] (b2) -- (b3);
  \node[text=rose, anchor=west] at (4.7,-1.05) {akurasi ${\sim}71\%$ --- turun 8 poin};
  \node[text=ink3, anchor=west] at (4.7,-1.4) {46 kelas tidak muat diperas ke 4 dimensi};
\end{tikzpicture}
"""

SVG_KFOLD = """
<svg viewBox="0 0 760 210" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Validasi silang K-lipat dengan K sama dengan 4">
  <text class="d-sm" x="20" y="20" fill="#7E93B4">
    data latih dibagi 4; tiap lipatan sekali jadi validasi
  </text>
  <g>
    <text class="d-mono" x="20" y="56" fill="#7E93B4">lipat 1</text>
    <rect x="90"  y="40" width="140" height="22" rx="5" fill="rgba(34,211,238,.20)" stroke="rgba(34,211,238,.7)"/>
    <rect x="234" y="40" width="140" height="22" rx="5" class="d-box"/>
    <rect x="378" y="40" width="140" height="22" rx="5" class="d-box"/>
    <rect x="522" y="40" width="140" height="22" rx="5" class="d-box"/>
    <text class="d-sm" x="678" y="56">skor 1</text>
  </g>
  <g>
    <text class="d-mono" x="20" y="92" fill="#7E93B4">lipat 2</text>
    <rect x="90"  y="76" width="140" height="22" rx="5" class="d-box"/>
    <rect x="234" y="76" width="140" height="22" rx="5" fill="rgba(34,211,238,.20)" stroke="rgba(34,211,238,.7)"/>
    <rect x="378" y="76" width="140" height="22" rx="5" class="d-box"/>
    <rect x="522" y="76" width="140" height="22" rx="5" class="d-box"/>
    <text class="d-sm" x="678" y="92">skor 2</text>
  </g>
  <g>
    <text class="d-mono" x="20" y="128" fill="#7E93B4">lipat 3</text>
    <rect x="90"  y="112" width="140" height="22" rx="5" class="d-box"/>
    <rect x="234" y="112" width="140" height="22" rx="5" class="d-box"/>
    <rect x="378" y="112" width="140" height="22" rx="5" fill="rgba(34,211,238,.20)" stroke="rgba(34,211,238,.7)"/>
    <rect x="522" y="112" width="140" height="22" rx="5" class="d-box"/>
    <text class="d-sm" x="678" y="128">skor 3</text>
  </g>
  <g>
    <text class="d-mono" x="20" y="164" fill="#7E93B4">lipat 4</text>
    <rect x="90"  y="148" width="140" height="22" rx="5" class="d-box"/>
    <rect x="234" y="148" width="140" height="22" rx="5" class="d-box"/>
    <rect x="378" y="148" width="140" height="22" rx="5" class="d-box"/>
    <rect x="522" y="148" width="140" height="22" rx="5" fill="rgba(34,211,238,.20)" stroke="rgba(34,211,238,.7)"/>
    <text class="d-sm" x="678" y="164">skor 4</text>
  </g>
  <rect x="90" y="180" width="572" height="22" rx="6"
        fill="rgba(123,217,73,.10)" stroke="rgba(123,217,73,.5)"/>
  <text class="d-sm" x="376" y="196" text-anchor="middle" fill="#7BD949">
    skor akhir = rerata keempatnya
  </text>
</svg>
"""

TIKZ_KFOLD = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  tr/.style={draw=rule, fill=papertint, rounded corners=2pt,
             minimum width=1.55cm, minimum height=0.34cm},
  va/.style={draw=signal!70, fill=signal!22, rounded corners=2pt,
             minimum width=1.55cm, minimum height=0.34cm}]
  \node[text=ink3, anchor=west] at (0,1.65) {data latih dibagi 4; tiap lipatan sekali jadi validasi};
  \foreach \r/\v in {0/1, 1/2, 2/3, 3/4} {
    \node[text=ink3, anchor=west, font=\ttfamily\tiny] at (0,{1.15-\r*0.46}) {lipat \v};
    \foreach \c in {1,2,3,4} {
      \pgfmathparse{int(\c==\v)}
      \ifnum\pgfmathresult=1
        \node[va] at ({0.9+\c*1.62},{1.15-\r*0.46}) {};
      \else
        \node[tr] at ({0.9+\c*1.62},{1.15-\r*0.46}) {};
      \fi
    }
    \node[text=ink3, anchor=west] at (8.0,{1.15-\r*0.46}) {skor \v};
  }
  \node[draw=lime!50, fill=limebr!8, rounded corners=3pt, minimum width=6.5cm,
        minimum height=0.36cm, text=lime] at (4.75,-0.85) {skor akhir = rerata keempatnya};
\end{tikzpicture}
"""


NB = ["01_imdb_klasifikasi_biner.ipynb", "02_reuters_multikelas.ipynb",
      "03_regresi_harga_rumah.ipynb"]

DECK = {
    "id": "ch04",
    "kind": "chapter",
    "number": 4,
    "title": "Klasifikasi dan Regresi",
    "subtitle": "Tiga alur kerja lengkap -- biner, multikelas, dan regresi skalar -- "
                "beserta aturan pilih loss dan aktivasi yang dipakai sisa buku ini.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- bab 4",
    "source_url": chapter_url(4),
    "duration": "3 jam (2 sesi)",
    "presenter": {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Asisten Pengajar"},
    "resources": chapter_resources(4, local_notebooks=NB),
    "objectives": [
        "Memilih **aktivasi keluaran dan fungsi rugi** yang benar untuk klasifikasi "
        "biner, multikelas, dan regresi -- tanpa menebak.",
        "Menyiapkan data teks dengan **multi-hot encoding**, dan label dengan "
        "**one-hot** atau **sparse**.",
        "Membaca **kurva rugi validasi** untuk menemukan titik berhenti terbaik, "
        "lalu melatih ulang sampai epoch itu saja.",
        "Mengenali **leher botol informasi** dan menaksir ukuran lapis antara "
        "dari banyaknya kelas.",
        "Menormalkan fitur dengan **statistik data latih**, dan menilai model "
        "berdata sedikit dengan **validasi silang K-lipat**.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Kosakata",
            "title": "Dua belas istilah yang dipakai sampai bab 20",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "table",
                         "head": ["Istilah", "Artinya"],
                         "widths": [30, 70],
                         "rows": [
                             ["**Sample / input**", "Satu titik data yang masuk ke model."],
                             ["**Prediction / output**", "Yang keluar dari model."],
                             ["**Target**", "Jawaban benar, dari sumber di luar model."],
                             ["**Loss value**", "Ukuran jarak prediksi ke target."],
                             ["**Classes**", "Himpunan label yang mungkin."],
                             ["**Mini-batch**", "Lazimnya 8-128 sampel sekaligus."],
                         ]},
                    ],
                    [
                        {"t": "table",
                         "head": ["Jenis tugas", "Cirinya"],
                         "widths": [38, 62],
                         "rows": [
                             ["**Binary classification**", "Dua kategori, saling meniadakan."],
                             ["**Multiclass**", "Lebih dari dua kategori, satu label per sampel."],
                             ["**Multilabel**", "Satu sampel boleh punya beberapa label."],
                             ["**Scalar regression**", "Satu nilai kontinu."],
                             ["**Vector regression**", "Beberapa nilai kontinu sekaligus."],
                         ]},
                    ],
                ]},
                {"t": "band",
                 "md": "Membedakan **multiclass** dari **multilabel** menentukan pilihan "
                       "aktivasi keluaran: ==softmax== untuk yang pertama (jumlahnya 1), "
                       "==sigmoid per kelas== untuk yang kedua."},
            ],
        },

        {"type": "section", "num": "01", "title": "Klasifikasi biner: ulasan IMDB",
         "lead": "50.000 ulasan film, positif atau negatif."},

        {
            "type": "slide",
            "kicker": "Bagian 4.1",
            "title": "Data, dan cara mengubah deret kata jadi tensor",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 4.1-4.3 — muat dan vektorkan",
                 "src": """import numpy as np
from keras.datasets import imdb

(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=10000)

def multi_hot_encode(sequences, num_classes):
    results = np.zeros((len(sequences), num_classes))
    for i, sequence in enumerate(sequences):
        results[i][sequence] = 1.0        # indeks kata yang muncul -> 1
    return results

x_train = multi_hot_encode(train_data, num_classes=10000)
x_test = multi_hot_encode(test_data, num_classes=10000)
y_train = train_labels.astype("float32")
y_test = test_labels.astype("float32")

print(x_train.shape, x_train[0][:12])"""},
                {"t": "out", "src": "(25000, 10000) [0. 1. 1. 0. 1. 1. 1. 1. 1. 1. 0. 0.]"},
                {"t": "bullets", "items": [
                    "25.000 latih + 25.000 uji, seimbang 50:50 positif-negatif.",
                    "`num_words=10000` hanya menyimpan **10.000 kata tersering**; sisanya dibuang.",
                    "Multi-hot ==membuang urutan kata==. Cukup untuk sentimen; bab 14-15 "
                    "menggantinya saat urutan mulai penting.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.1",
            "title": "Model, validasi, dan titik balik di epoch 4",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "listing 4.4-4.6",
                         "src": """model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dense(16, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="adam",
              loss="binary_crossentropy",
              metrics=["accuracy"])

x_val, partial_x = x_train[:10000], x_train[10000:]
y_val, partial_y = y_train[:10000], y_train[10000:]

history = model.fit(
    partial_x, partial_y,
    epochs=20, batch_size=512,
    validation_data=(x_val, y_val))"""},
                    ],
                    [
                        {"t": "fig", "svg": SVG_OVERFIT, "tikz": TIKZ_OVERFIT,
                         "cap": "Rugi latih turun terus; rugi validasi berbalik naik "
                                "setelah epoch 4."},
                    ],
                ]},
                {"t": "quote",
                 "md": "Setelah epoch keempat, Anda mengoptimalkan berlebihan pada data "
                       "latih, dan berakhir mempelajari representasi yang khas untuk data "
                       "latih itu saja -- yang tidak berlaku di luarnya.",
                 "cite": "Chollet & Watson, bab 4"},
            ],
            "notes": "Ini pola yang akan muncul di setiap bab sesudahnya. Latih 20 epoch "
                     "untuk MELIHAT titik baliknya, lalu latih ulang sampai titik itu.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.1",
            "title": "Hasilnya, dan tolok banding yang harus dikalahkan",
            "blocks": [
                {"t": "stats", "cols": 3, "items": [
                    {"v": "88%", "l": "akurasi uji setelah dilatih ulang 4 epoch"},
                    {"v": "50%", "l": "tolok banding acak (kelasnya seimbang)"},
                    {"v": "16", "l": "unit per lapis antara -- model sengaja kecil"},
                ]},
                {"t": "quote",
                 "md": "Tanpa fungsi aktivasi seperti `relu` (disebut juga nonlinearitas), "
                       "lapis `Dense` hanya terdiri dari dua operasi linear -- hasil kali "
                       "titik dan penjumlahan. Ruang hipotesis seperti itu terlalu sempit.",
                 "cite": "Chollet & Watson, bab 4"},
                {"t": "band",
                 "md": "**Crossentropy** datang dari teori informasi: ia mengukur ==jarak "
                       "antara dua sebaran peluang==. Itulah sebabnya ia pasangan alami "
                       "bagi keluaran sigmoid dan softmax, dan bukan MSE."},
            ],
        },

        {"type": "section", "num": "02", "title": "Multikelas: kawat berita Reuters",
         "lead": "46 topik, saling meniadakan."},

        {
            "type": "slide",
            "kicker": "Bagian 4.2",
            "title": "One-hot atau sparse -- antarmuka beda, hitungannya sama",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "label one-hot",
                         "src": """from keras.utils import to_categorical

y_train = to_categorical(train_labels)
y_test = to_categorical(test_labels)
# bentuknya (8982, 46)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"])"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "label sparse (bilangan bulat)",
                         "src": """y_train = train_labels     # biarkan bulat
y_test = test_labels
# bentuknya (8982,)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])"""},
                    ],
                ]},
                {"t": "code", "lang": "python", "file": "listing 4.11 — model dan metrik top-K",
                 "src": """model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(46, activation="softmax"),      # satu unit per kelas
])
top_3 = keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy")
model.compile(optimizer="adam", loss="categorical_crossentropy",
              metrics=["accuracy", top_3])"""},
                {"t": "band",
                 "md": "**Top-K accuracy** menanyakan hal yang berbeda: apakah kelas yang "
                       "benar ada di antara k tebakan teratas? Untuk 46 kelas, itu ukuran "
                       "yang ==jauh lebih berguna== bagi sistem yang hanya menyarankan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.2",
            "title": "Leher botol informasi: percobaan yang sengaja digagalkan",
            "blocks": [
                {"t": "fig", "svg": SVG_BOTTLENECK, "tikz": TIKZ_BOTTLENECK,
                 "cap": "Lapis 4 unit di tengah memaksa 46 kelas diperas ke 4 dimensi. "
                        "Turun 8 poin akurasi."},
                {"t": "quote",
                 "md": "Model itu sanggup menjejalkan sebagian besar informasi yang "
                       "diperlukan ke dalam representasi 4 dimensi -- tetapi tidak semuanya.",
                 "cite": "Chollet & Watson, bab 4"},
                {"t": "band", "style": "amber",
                 "md": "Aturan praktisnya: **lapis antara tidak boleh lebih sempit dari "
                       "jumlah kelas keluaran**. Itulah sebabnya contoh IMDB cukup 16 unit "
                       "(2 kelas), sementara Reuters butuh 64."},
            ],
            "notes": "Percobaan gagal ini justru bagian terbaik dari bab 4 — tunjukkan "
                     "utuh, jangan lewati. Peserta belajar lebih banyak dari yang gagal.",
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.2",
            "title": "Melatih ulang di epoch terbaik",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 4.14 — model produksi",
                 "src": """model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(46, activation="softmax"),
])
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.fit(x_train, y_train, epochs=9, batch_size=512)     # 9 = titik terbaik tadi

results = model.evaluate(x_test, y_test)
print(results)"""},
                {"t": "out", "src": """71/71 ---- 0s 3ms/step - accuracy: 0.7969 - loss: 0.9127
[0.9127, 0.7969]"""},
                {"t": "stats", "cols": 2, "items": [
                    {"v": "~80%", "l": "akurasi uji"},
                    {"v": "~19%", "l": "tolok banding acak -- 46 kelas, sebaran tak rata"},
                ]},
                {"t": "band",
                 "md": "Selalu hitung **tolok banding akal sehat** dulu. Angka 80% terdengar "
                       "biasa saja sampai Anda tahu bahwa menebak asal hanya memberi 19%."},
            ],
        },

        {"type": "section", "num": "03", "title": "Regresi skalar: harga rumah",
         "lead": "Data sedikit. Aturan mainnya berubah."},

        {
            "type": "slide",
            "kicker": "Bagian 4.3",
            "title": "Normalisasi fitur -- dan jebakan kebocoran data",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 4.16-4.17 — muat dan normalkan",
                 "src": """from keras.datasets import california_housing

(train_data, train_targets), (test_data, test_targets) = (
    california_housing.load_data(version="small"))
# 480 latih, 120 uji, 8 fitur numerik per distrik

mean = train_data.mean(axis=0)
std = train_data.std(axis=0)
x_train = (train_data - mean) / std
x_test = (test_data - mean) / std      # PAKAI statistik data LATIH, bukan uji

y_train = train_targets / 100000       # skalakan target ke rentang yang wajar
y_test = test_targets / 100000"""},
                {"t": "band", "style": "rose",
                 "md": "Baris `x_test = (test_data - mean) / std` memakai `mean` dan `std` "
                       "dari data **latih**. Menghitung ulang dari data uji adalah "
                       "==kebocoran informasi==: model jadi tahu sesuatu tentang data yang "
                       "seharusnya belum pernah dilihatnya. Bab 5 menamainya secara resmi."},
                {"t": "bullets", "items": [
                    "8 fitur: bujur, lintang, umur rumah, populasi, jumlah rumah tangga, "
                    "penghasilan median, total kamar, total kamar tidur.",
                    "Target: harga rumah median, kontinu, kira-kira $60 ribu sampai $500 ribu.",
                    "Rentang tiap fitur berbeda jauh; tanpa normalisasi ==optimalisasi jadi "
                    "kacau==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.3",
            "title": "Model regresi: keluaran tanpa aktivasi",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 4.18",
                 "src": """def get_model():
    model = keras.Sequential([
        layers.Dense(64, activation="relu"),
        layers.Dense(64, activation="relu"),
        layers.Dense(1),                 # TANPA aktivasi - bebas menebak nilai apa pun
    ])
    model.compile(optimizer="adam",
                  loss="mean_squared_error",
                  metrics=["mean_absolute_error"])
    return model"""},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔓", "h": "Tanpa aktivasi keluaran",
                     "p": "Sigmoid akan mengurung tebakan ke [0,1]. Regresi harus bebas.",
                     "style": "accent"},
                    {"ico": "🤏", "h": "Model sengaja kecil",
                     "p": "480 sampel saja. Model besar akan langsung menghafalnya.",
                     "style": "warn"},
                    {"ico": "📏", "h": "MSE untuk rugi, MAE untuk metrik",
                     "p": "MAE bisa dibaca manusia: MAE 0,5 ≈ meleset $50 ribu.",
                     "style": "accent"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.3",
            "title": "Validasi silang K-lipat, karena datanya sedikit",
            "blocks": [
                {"t": "fig", "svg": SVG_KFOLD, "tikz": TIKZ_KFOLD,
                 "cap": "Dengan 480 sampel, satu belahan validasi tunggal terlalu berisik "
                        "-- skornya bergantung pada belahan mana yang kebetulan terpilih."},
                {"t": "code", "lang": "python", "file": "listing 4.19 — inti gelung K-lipat",
                 "src": """k, num_epochs, all_scores = 4, 50, []
num_val_samples = len(x_train) // k

for i in range(k):
    fold_x_val = x_train[i * num_val_samples : (i + 1) * num_val_samples]
    fold_y_val = y_train[i * num_val_samples : (i + 1) * num_val_samples]
    fold_x_train = np.concatenate(
        [x_train[: i * num_val_samples], x_train[(i + 1) * num_val_samples :]], axis=0)
    fold_y_train = np.concatenate(
        [y_train[: i * num_val_samples], y_train[(i + 1) * num_val_samples :]], axis=0)

    model = get_model()
    model.fit(fold_x_train, fold_y_train, epochs=num_epochs, batch_size=16, verbose=0)
    val_loss, val_mae = model.evaluate(fold_x_val, fold_y_val, verbose=0)
    all_scores.append(val_mae)"""},
                {"t": "out", "src": """[0.265, 0.292, 0.232, 0.349]
rerata MAE: 0.296   ->  meleset sekitar $29.600"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 4.3",
            "title": "Berapa lama melatihnya? Tanya kurvanya",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 4.20 — rerata kurva MAE",
                 "src": """all_mae_histories = []
for i in range(k):
    # ... penyiapan lipatan sama seperti sebelumnya ...
    history = model.fit(fold_x_train, fold_y_train,
                        validation_data=(fold_x_val, fold_y_val),
                        epochs=200, batch_size=16, verbose=0)
    all_mae_histories.append(history.history["val_mean_absolute_error"])

average_mae_history = [
    np.mean([h[i] for h in all_mae_histories]) for i in range(200)
]"""},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "band",
                         "md": "MAE validasi ==mendatar di sekitar epoch 120-140==, lalu "
                               "mulai memburuk. Itulah titik berhentinya."},
                        {"t": "code", "lang": "python", "file": "model akhir",
                         "src": """model = get_model()
model.fit(x_train, y_train, epochs=130,
          batch_size=16, verbose=0)
mse, mae = model.evaluate(x_test, y_test)"""},
                    ],
                    [
                        {"t": "stats", "cols": 1, "items": [
                            {"v": "~0,31", "l": "MAE uji akhir -- meleset sekitar $31.000"},
                            {"v": "2,83", "l": "contoh tebakan pertama → sekitar $283.000"},
                        ]},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Ringkasan",
            "title": "Tabel yang akan Anda pakai terus",
            "blocks": [
                {"t": "table",
                 "head": ["Jenis tugas", "Aktivasi lapis akhir", "Fungsi rugi", "Metrik lazim"],
                 "widths": [28, 24, 30, 18],
                 "rows": [
                     ["Klasifikasi **biner**", "`sigmoid` (1 unit)",
                      "`binary_crossentropy`", "accuracy"],
                     ["**Multikelas**, label one-hot", "`softmax` (N unit)",
                      "`categorical_crossentropy`", "accuracy, top-K"],
                     ["**Multikelas**, label bulat", "`softmax` (N unit)",
                      "`sparse_categorical_crossentropy`", "accuracy"],
                     ["**Multilabel**", "`sigmoid` (N unit)",
                      "`binary_crossentropy`", "accuracy, AUC"],
                     ["**Regresi** skalar", "tanpa aktivasi (1 unit)",
                      "`mean_squared_error`", "MAE"],
                 ]},
                {"t": "steps", "items": [
                    "Vektorkan data diskret; **normalkan fitur dengan statistik data latih**.",
                    "Lapis antara ==tidak boleh lebih sempit dari jumlah kelas== -- leher botol.",
                    "Data sedikit → model kecil, satu atau dua lapis antara.",
                    "Latih sampai overfit untuk **melihat** titik baliknya, lalu latih ulang "
                    "sampai titik itu.",
                    "Data sedikit → **K-lipat**, bukan satu belahan validasi.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_imdb_klasifikasi_biner.ipynb",
                     "href": "../../course-slides/notebooks/ch04/01_imdb_klasifikasi_biner.ipynb"},
                    {"k": "BAB BERIKUT", "ic": "➡", "v": "Bab 5 — Dasar machine learning",
                     "href": "../ch05/index.html"},
                ]},
            ],
        },
    ],
}
