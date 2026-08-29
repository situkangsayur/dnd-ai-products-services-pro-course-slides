# -*- coding: utf-8 -*-
"""Bab 7 — A deep dive on Keras.

Sumber: Chollet & Watson, *Deep Learning with Python*, 3rd ed., bab 7
(hlm. 190-230). Ditulis dari naskah PDF edisi ketiga.

Bab terpanjang di paruh pertama buku. Kuncinya satu asas: *progressive
disclosure of complexity* -- mudah dimulai, tetapi tidak ada langit-langit.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


SVG_SPECTRUM = """
<svg viewBox="0 0 760 240" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Spektrum alur kerja Keras dari Sequential sampai subclassing">
  <defs>
    <linearGradient id="sg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"   stop-color="#2C7BD4" stop-opacity=".45"/>
      <stop offset="0.5" stop-color="#22D3EE" stop-opacity=".40"/>
      <stop offset="1"   stop-color="#A78BFA" stop-opacity=".45"/>
    </linearGradient>
  </defs>
  <rect x="20" y="26" width="720" height="6" rx="3" fill="url(#sg)"/>

  <rect class="d-box" x="20"  y="48" width="166" height="86" rx="10"/>
  <text class="d-lbl" x="36" y="74">Sequential API</text>
  <text class="d-sm"  x="36" y="96">+ lapis bawaan</text>
  <text class="d-sm"  x="36" y="122" fill="#7E93B4">pemula, model sederhana</text>

  <rect class="d-box-a" x="200" y="48" width="166" height="86" rx="10"/>
  <text class="d-lbl" x="216" y="74">Functional API</text>
  <text class="d-sm"  x="216" y="96">+ lapis bawaan</text>
  <text class="d-sm"  x="216" y="122" fill="#7E93B4">kasus pemakaian baku</text>

  <rect class="d-box-a" x="380" y="48" width="176" height="86" rx="10"/>
  <text class="d-lbl" x="396" y="74">Functional API</text>
  <text class="d-sm"  x="396" y="94">+ lapis, metrik, rugi kustom</text>
  <text class="d-sm"  x="396" y="122" fill="#7E93B4">kasus khusus, solusi jahit</text>

  <rect x="570" y="48" width="170" height="86" rx="10"
        fill="rgba(167,139,250,.14)" stroke="rgba(167,139,250,.6)" stroke-width="1.4"/>
  <text class="d-lbl" x="586" y="74">Subclassing</text>
  <text class="d-sm"  x="586" y="96">tulis semuanya sendiri</text>
  <text class="d-sm"  x="586" y="122" fill="#7E93B4">peneliti</text>

  <text class="d-sm" x="20"  y="168" fill="#22D3EE">mudah dipakai</text>
  <text class="d-sm" x="740" y="168" text-anchor="end" fill="#A78BFA">luwes sepenuhnya</text>

  <rect x="20" y="186" width="720" height="42" rx="10"
        fill="rgba(34,211,238,.07)" stroke="rgba(34,211,238,.3)" stroke-width="1.2"/>
  <text class="d-sm" x="40" y="204">
    Semuanya berdiri di atas API bersama: Layer dan Model. Komponen dari satu alur kerja
  </text>
  <text class="d-sm" x="40" y="222">
    bisa dipakai di alur kerja mana pun &#8212; Anda tidak perlu ganti kerangka saat naik tingkat.
  </text>
</svg>
"""

TIKZ_SPECTRUM = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  bx/.style={draw=rule, fill=papertint, rounded corners=4pt, minimum width=2.5cm,
             minimum height=1.25cm, align=left, text=ink2},
  ax/.style={draw=signal!60, fill=signal!9, rounded corners=4pt, minimum width=2.5cm,
             minimum height=1.25cm, align=left, text=ink2}]
  \shade[left color=itbbluelt!45, right color=violet!45]
    (0,1.15) rectangle (10.4,1.28);
  \node[bx] (a) at (1.25,0.4)
    {\textbf{Sequential API}\\+ lapis bawaan\\[2pt]\textcolor{ink3}{pemula, model sederhana}};
  \node[ax] (b) at (3.9,0.4)
    {\textbf{Functional API}\\+ lapis bawaan\\[2pt]\textcolor{ink3}{kasus pemakaian baku}};
  \node[ax] (c) at (6.55,0.4)
    {\textbf{Functional API}\\+ lapis, metrik, rugi kustom\\[2pt]\textcolor{ink3}{kasus khusus}};
  \node[draw=violet!70, fill=violet!12, rounded corners=4pt, minimum width=2.5cm,
        minimum height=1.25cm, align=left, text=ink2] (d) at (9.2,0.4)
    {\textbf{Subclassing}\\tulis semuanya sendiri\\[2pt]\textcolor{ink3}{peneliti}};
  \node[text=signal, anchor=west] at (0,-0.5) {mudah dipakai};
  \node[text=violet, anchor=east] at (10.4,-0.5) {luwes sepenuhnya};
  \node[draw=signal!35, fill=signal!6, rounded corners=4pt, minimum width=10.2cm,
        minimum height=0.7cm, align=left, text=ink2] at (5.2,-1.15)
    {~Semuanya berdiri di atas API bersama: \texttt{Layer} dan \texttt{Model}. Komponen dari satu\\
     ~alur kerja bisa dipakai di alur kerja mana pun --- tak perlu ganti kerangka saat naik tingkat.};
\end{tikzpicture}
"""

SVG_TICKET = """
<svg viewBox="0 0 760 280" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Model tiket dukungan: tiga masukan, satu concatenate, dua keluaran">
  <defs>
    <marker id="tk" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="rgba(34,211,238,.75)"/>
    </marker>
  </defs>

  <rect class="d-box" x="20" y="30"  width="140" height="34" rx="8"/>
  <text class="d-mono" x="90" y="52" text-anchor="middle">title</text>
  <text class="d-sm" x="168" y="52" fill="#7E93B4">(10000,)</text>

  <rect class="d-box" x="20" y="106" width="140" height="34" rx="8"/>
  <text class="d-mono" x="90" y="128" text-anchor="middle">text_body</text>
  <text class="d-sm" x="168" y="128" fill="#7E93B4">(10000,)</text>

  <rect class="d-box" x="20" y="182" width="140" height="34" rx="8"/>
  <text class="d-mono" x="90" y="204" text-anchor="middle">tags</text>
  <text class="d-sm" x="168" y="204" fill="#7E93B4">(100,)</text>

  <rect class="d-box-a" x="252" y="98" width="140" height="50" rx="10"/>
  <text class="d-sm" x="322" y="120" text-anchor="middle">Concatenate</text>
  <text class="d-mono" x="322" y="138" text-anchor="middle">(20100,)</text>

  <rect x="432" y="98" width="150" height="50" rx="10"
        fill="rgba(167,139,250,.14)" stroke="rgba(167,139,250,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="507" y="120" text-anchor="middle">Dense 64 relu</text>
  <text class="d-mono" x="507" y="138" text-anchor="middle">dense_features</text>

  <rect x="626" y="56" width="116" height="42" rx="9"
        fill="rgba(123,217,73,.14)" stroke="rgba(123,217,73,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="684" y="74" text-anchor="middle">priority</text>
  <text class="d-mono" x="684" y="90" text-anchor="middle">1 &#183; sigmoid</text>

  <rect x="626" y="148" width="116" height="42" rx="9"
        fill="rgba(123,217,73,.14)" stroke="rgba(123,217,73,.6)" stroke-width="1.4"/>
  <text class="d-sm" x="684" y="166" text-anchor="middle">department</text>
  <text class="d-mono" x="684" y="182" text-anchor="middle">4 &#183; softmax</text>

  <path class="d-arrow" d="M212,50 C236,50 236,110 248,116" marker-end="url(#tk)"/>
  <path class="d-arrow" d="M212,123 L248,123" marker-end="url(#tk)"/>
  <path class="d-arrow" d="M212,199 C236,199 236,138 248,132" marker-end="url(#tk)"/>
  <path class="d-arrow" d="M392,123 L428,123" marker-end="url(#tk)"/>
  <path class="d-arrow" d="M582,116 C606,116 606,84 622,80"  marker-end="url(#tk)"/>
  <path class="d-arrow" d="M582,131 C606,131 606,164 622,168" marker-end="url(#tk)"/>

  <rect x="20" y="238" width="722" height="34" rx="9"
        fill="rgba(245,179,1,.07)" stroke="rgba(245,179,1,.32)" stroke-width="1.2"/>
  <text class="d-sm" x="40" y="260" fill="#F0DFB4">
    Tiga masukan, dua keluaran, satu simpul antara yang dipakai bersama &#8212; tidak mungkin ditulis sebagai Sequential.
  </text>
</svg>
"""

TIKZ_TICKET = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  ix/.style={draw=rule, fill=papertint, rounded corners=3pt, minimum width=1.9cm,
             minimum height=0.5cm, text=ink2, font=\ttfamily\tiny},
  ax/.style={draw=signal!60, fill=signal!10, rounded corners=3pt, minimum width=1.9cm,
             minimum height=0.68cm, text=ink, align=center},
  ox/.style={draw=lime!65, fill=limebr!14, rounded corners=3pt, minimum width=1.7cm,
             minimum height=0.6cm, text=ink, align=center},
  ar/.style={-{Stealth[length=4pt]}, signal, line width=0.7pt}]
  \node[ix] (t)  at (0,1.1)  {title};
  \node[ix] (b)  at (0,0.35) {text\_body};
  \node[ix] (g)  at (0,-0.4) {tags};
  \node[ax] (cc) at (2.7,0.35) {Concatenate\\\ttfamily (20100,)};
  \node[draw=violet!70, fill=violet!12, rounded corners=3pt, minimum width=2.1cm,
        minimum height=0.68cm, text=ink, align=center] (d) at (5.5,0.35)
        {Dense 64 relu\\\ttfamily dense\_features};
  \node[ox] (p)  at (8.2,0.95) {priority\\\ttfamily 1 $\cdot$ sigmoid};
  \node[ox] (dp) at (8.2,-0.3) {department\\\ttfamily 4 $\cdot$ softmax};
  \draw[ar] (t) -- (cc); \draw[ar] (b) -- (cc); \draw[ar] (g) -- (cc);
  \draw[ar] (cc) -- (d); \draw[ar] (d) -- (p); \draw[ar] (d) -- (dp);
  \node[draw=amber!35, fill=amberbr!7, rounded corners=4pt, minimum width=10.2cm,
        minimum height=0.55cm, text=ink2] at (4.6,-1.4)
    {~Tiga masukan, dua keluaran, satu simpul antara yang dipakai bersama --- tak mungkin ditulis sebagai Sequential.};
\end{tikzpicture}
"""


NB = ["01_tiga_cara_membangun_model.ipynb", "02_metrik_dan_callback_kustom.ipynb",
      "03_train_step_kustom_per_backend.ipynb"]

DECK = {
    "id": "ch07",
    "kind": "chapter",
    "number": 7,
    "title": "Menyelam ke Keras",
    "subtitle": "Tiga cara membangun model, tiga tingkat kendali atas pelatihannya -- "
                "dan satu asas yang menyatukan semuanya: mudah dimulai, tanpa langit-langit.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- bab 7 (hlm. 190-230)",
    "source_url": chapter_url(7),
    "duration": "3 jam (2 sesi)",
    "presenter": {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Asisten Pengajar"},
    "resources": chapter_resources(7, local_notebooks=NB),
    "objectives": [
        "Menjelaskan asas **progressive disclosure of complexity** dan menempatkan "
        "diri sendiri pada spektrum alur kerja Keras.",
        "Membangun model bermasukan-jamak dan berkeluaran-jamak dengan "
        "**Functional API**, lalu melatihnya dengan senarai maupun kamus.",
        "Memanfaatkan **akses ke keterhubungan lapis**: menggambar topologi dengan "
        "`plot_model()` dan **mengekstraksi fitur** dari simpul antara.",
        "Menulis **Model subclass** -- dan menyebut apa yang hilang saat memilihnya.",
        "Menulis **metrik kustom** (`update_state`, `result`, `reset_state`) dan "
        "**callback kustom**, serta memakai `EarlyStopping` + `ModelCheckpoint`.",
        "Menulis **`train_step()` sendiri** di TensorFlow, PyTorch, dan JAX -- dan "
        "menyisipkannya ke `fit()` supaya callback dan optimasi bawaan tetap terpakai.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Bagian 7.1",
            "title": "Progressive disclosure of complexity",
            "blocks": [
                {"t": "fig", "svg": SVG_SPECTRUM, "tikz": TIKZ_SPECTRUM,
                 "cap": "Gambar 7.1 -- bukan empat kerangka berbeda, melainkan satu "
                        "spektrum di atas API yang sama."},
                {"t": "quote",
                 "md": "Anda bisa memakai Keras seperti memakai scikit-learn -- tinggal "
                       "memanggil `fit()` dan membiarkan kerangkanya bekerja -- atau "
                       "memakainya seperti NumPy, dengan kendali penuh atas setiap detail "
                       "kecil.",
                 "cite": "Chollet & Watson, bab 7.1"},
                {"t": "band",
                 "md": "Analogi yang dipakai buku: **Keras adalah Python-nya deep learning**. "
                       "Python multiparadigma -- berorientasi objek, fungsional, prosedural, "
                       "semuanya rukun. Karena itu ==Anda tidak perlu pindah kerangka== saat "
                       "berpindah dari mahasiswa ke peneliti, atau dari data scientist ke "
                       "deep learning engineer."},
            ],
            "notes": "Kalimat yang perlu diulang: apa yang dipelajari peserta hari ini tetap "
                     "berlaku setelah mereka jadi ahli. Ini menghilangkan kecemasan 'nanti "
                     "harus belajar ulang'.",
        },

        {"type": "section", "num": "01", "title": "Tiga cara membangun model",
         "lead": "Sequential, Functional, subclassing -- dan kapan masing-masing."},

        {
            "type": "slide",
            "kicker": "Bagian 7.2.1-7.2.2",
            "title": "Sequential itu pada dasarnya senarai Python",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Sequential** -- API yang paling mudah didekati. "
                                         "Batasnya juga jelas: ia hanya bisa menyatakan model "
                                         "dengan **satu masukan dan satu keluaran**, satu "
                                         "lapis sesudah lapis lain."},
                        {"t": "band", "style": "amber",
                         "md": "Padahal di praktik, model dengan **masukan jamak** (citra "
                               "dan metadatanya), **keluaran jamak** (beberapa hal yang mau "
                               "diramalkan), atau **topologi tak-linear** itu ==biasa sekali=="},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.8 — versi Functional",
                         "src": """inputs = keras.Input(shape=(3,),
                     name="my_input")
features = layers.Dense(
    64, activation="relu")(inputs)
outputs = layers.Dense(
    10, activation="softmax")(features)

model = keras.Model(
    inputs=inputs, outputs=outputs,
    name="my_functional_model")"""},
                    ],
                ]},
                {"t": "code", "lang": "python", "file": "tensor simbolik",
                 "src": """inputs.shape        # (None, 3)  <- None = ukuran batch, bebas
inputs.dtype        # "float32"

features = layers.Dense(64, activation="relu")(inputs)
features.shape      # (None, 64)"""},
                {"t": "band",
                 "md": "`inputs` itu **tensor simbolik**: ia ==tidak memuat data apa pun==, "
                       "tetapi menyandikan spesifikasi tensor yang kelak akan dilihat model. "
                       "Semua lapis Keras bisa dipanggil baik pada tensor data sungguhan "
                       "maupun pada tensor simbolik -- yang kedua mengembalikan tensor "
                       "simbolik baru dengan shape dan dtype yang sudah diperbarui."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.2.2 · listing 7.9",
            "title": "Di sinilah Functional API bersinar",
            "blocks": [
                {"t": "p", "md": "Kasus dari buku: sistem yang **memeringkat tiket dukungan "
                                 "pelanggan menurut prioritas** dan mengarahkannya ke "
                                 "departemen yang tepat."},
                {"t": "fig", "svg": SVG_TICKET, "tikz": TIKZ_TICKET,
                 "cap": "Tiga masukan (judul, badan teks, tag), dua keluaran (skor prioritas "
                        "dan departemen)."},
                {"t": "code", "lang": "python", "file": "listing 7.9",
                 "src": """vocabulary_size, num_tags, num_departments = 10000, 100, 4

title     = keras.Input(shape=(vocabulary_size,), name="title")
text_body = keras.Input(shape=(vocabulary_size,), name="text_body")
tags      = keras.Input(shape=(num_tags,), name="tags")

features = layers.Concatenate()([title, text_body, tags])
features = layers.Dense(64, activation="relu", name="dense_features")(features)

priority   = layers.Dense(1, activation="sigmoid", name="priority")(features)
department = layers.Dense(num_departments, activation="softmax",
                          name="department")(features)

model = keras.Model(inputs=[title, text_body, tags],
                    outputs=[priority, department])"""},
                {"t": "band",
                 "md": "Buku menyebutnya ==seperti bermain LEGO==: cara yang sederhana "
                       "tetapi sangat luwes untuk mendefinisikan graf lapis yang sebarang."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.2.2 · listing 7.10-7.11",
            "title": "Melatihnya: senarai berurutan, atau kamus bernama",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.10 — senarai",
                         "src": """model.compile(
    optimizer="adam",
    loss=["mean_squared_error",
          "sparse_categorical_crossentropy"],
    metrics=[["mean_absolute_error"],
             ["accuracy"]])

model.fit(
    [title_data, text_body_data, tags_data],
    [priority_data, department_data],
    epochs=1)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.11 — kamus",
                         "src": """model.compile(
    optimizer="adam",
    loss={"priority": "mean_squared_error",
          "department":
              "sparse_categorical_crossentropy"},
    metrics={"priority": ["mean_absolute_error"],
             "department": ["accuracy"]})

model.fit(
    {"title": title_data,
     "text_body": text_body_data,
     "tags": tags_data},
    {"priority": priority_data,
     "department": department_data},
    epochs=1)"""},
                    ],
                ]},
                {"t": "band",
                 "md": "Versi senarai **harus mengikuti urutan** yang Anda berikan ke "
                       "konstruktor `Model()`. Kalau masukan atau keluarannya banyak, "
                       "==pakai kamus bernama== -- urutannya jadi tidak penting lagi, dan "
                       "kodenya jauh lebih tahan salah."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.2.2 · listing 7.12-7.13",
            "title": "Kekuatan sesungguhnya: akses ke keterhubungan lapis",
            "blocks": [
                {"t": "p", "md": "Model Functional adalah **struktur data graf yang eksplisit**. "
                                 "Itu memungkinkan dua hal yang tidak bisa dilakukan model "
                                 "subclass: **penggambaran topologi** dan **ekstraksi fitur**."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "menggambar topologi",
                         "src": """keras.utils.plot_model(
    model, "ticket_classifier.png")

# versi yang jauh lebih menolong
# saat mengawakutu:
keras.utils.plot_model(
    model,
    "ticket_classifier_with_shape_info.png",
    show_shapes=True,
    show_layer_names=True)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.12 — memeriksa simpul",
                         "src": """model.layers
model.layers[3].input
model.layers[3].output
# <KerasTensor shape=(None, 20100),
#  dtype=float32>"""},
                    ],
                ]},
                {"t": "code", "lang": "python", "file": "listing 7.13 — ekstraksi fitur",
                 "src": """# Mau menambah keluaran ketiga: taksiran kesulitan tiket.
# TIDAK perlu membangun dan melatih ulang dari nol.
features = model.layers[4].output          # lapis Dense antara tadi
difficulty = layers.Dense(3, activation="softmax", name="difficulty")(features)

new_model = keras.Model(
    inputs=[title, text_body, tags],
    outputs=[priority, department, difficulty])"""},
                {"t": "band",
                 "md": "`None` pada shape tensor menyatakan **ukuran batch** -- model ini "
                       "menerima batch berukuran berapa pun."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.2.3 · listing 7.14",
            "title": "Model subclassing: kendali penuh",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 7.14",
                 "src": """class CustomerTicketModel(keras.Model):
    def __init__(self, num_departments):
        super().__init__()                       # jangan lupa konstruktor induknya
        self.concat_layer = layers.Concatenate()
        self.mixing_layer = layers.Dense(64, activation="relu")
        self.priority_scorer = layers.Dense(1, activation="sigmoid")
        self.department_classifier = layers.Dense(num_departments,
                                                  activation="softmax")

    def call(self, inputs):                      # lintasan maju ditulis di sini
        features = self.concat_layer(
            [inputs["title"], inputs["text_body"], inputs["tags"]])
        features = self.mixing_layer(features)
        return self.priority_scorer(features), self.department_classifier(features)"""},
                {"t": "table",
                 "head": ["", "`Layer`", "`Model`"],
                 "widths": [34, 33, 33],
                 "rows": [
                     ["Perannya", "Bata bangunan untuk membuat model.",
                      "Objek tingkat atas yang benar-benar dilatih dan diekspor."],
                     ["`fit()`, `evaluate()`, `predict()`", "Tidak punya.", "Punya."],
                     ["Disimpan ke berkas", "Tidak.", "Bisa."],
                 ]},
                {"t": "band",
                 "md": "Selebihnya kedua kelas itu **praktis identik**. Subclassing membuka "
                       "model yang ==tidak bisa dinyatakan sebagai graf berarah tanpa siklus== "
                       "-- misalnya `call()` yang memakai lapis di dalam gelung `for`, atau "
                       "bahkan memanggilnya secara rekursif."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.2.3",
            "title": "Harga kebebasan itu",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Model Functional** = struktur data eksplisit -- "
                                         "graf lapis yang bisa Anda lihat, periksa, dan ubah."},
                        {"t": "p", "md": "**Model subclass** = ==sepotong bytecode== -- kelas "
                                         "Python dengan metode `call()` berisi kode mentah. "
                                         "Itulah sumber keluwesannya, dan sekaligus sumber "
                                         "batasannya."},
                    ],
                    [
                        {"t": "cards", "cols": 1, "items": [
                            {"ico": "🚫", "h": "Yang hilang saat subclassing",
                             "p": "`summary()` **tidak menampilkan keterhubungan lapis** · "
                                  "`plot_model()` **tidak bisa dipakai** · **ekstraksi fitur "
                                  "tidak mungkin** -- sebab memang tidak ada grafnya.",
                             "style": "bad"},
                        ]},
                    ],
                ]},
                {"t": "band", "style": "rose",
                 "md": "Begitu model subclass diinstansiasi, **lintasan majunya menjadi kotak "
                       "hitam sepenuhnya**. Anda mengembangkan objek Python baru, bukan "
                       "sekadar menjepretkan bata LEGO -- ==permukaan galatnya jauh lebih "
                       "luas, dan pekerjaan awakutunya lebih banyak==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.2.4-7.2.5 · listing 7.15-7.16",
            "title": "Ketiganya bisa dicampur -- dan mana yang dipilih",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.15 — subclass di dalam Functional",
                         "src": """class Classifier(keras.Model):
    def __init__(self, num_classes=2):
        super().__init__()
        units, act = ((1, "sigmoid") if num_classes == 2
                      else (num_classes, "softmax"))
        self.dense = layers.Dense(units, activation=act)

    def call(self, inputs):
        return self.dense(inputs)

inputs = keras.Input(shape=(3,))
features = layers.Dense(64, activation="relu")(inputs)
outputs = Classifier(num_classes=10)(features)
model = keras.Model(inputs=inputs, outputs=outputs)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.16 — Functional di dalam subclass",
                         "src": """inputs = keras.Input(shape=(64,))
outputs = layers.Dense(1, activation="sigmoid")(inputs)
binary_classifier = keras.Model(inputs, outputs)

class MyModel(keras.Model):
    def __init__(self):
        super().__init__()
        self.dense = layers.Dense(64, activation="relu")
        self.classifier = binary_classifier

    def call(self, inputs):
        return self.classifier(self.dense(inputs))"""},
                    ],
                ]},
                {"t": "band",
                 "md": "**Saran buku:** kalau model Anda bisa dinyatakan sebagai graf berarah "
                       "tanpa siklus, ==pakai Functional API, bukan subclassing==. Seluruh "
                       "contoh di sisa buku memakai Functional API -- tetapi dengan "
                       "**lapis-lapis subclass** di dalamnya. Kombinasi itu memberi keluwesan "
                       "pengembangan sekaligus keuntungan Functional API."},
            ],
        },

        {"type": "section", "num": "02", "title": "Lingkar pelatihan bawaan",
         "lead": "Metrik kustom, callback, dan TensorBoard."},

        {
            "type": "slide",
            "kicker": "Bagian 7.3.1 · listing 7.18",
            "title": "Menulis metrik sendiri",
            "blocks": [
                {"t": "p", "md": "Metrik Keras adalah subkelas `keras.metrics.Metric`. "
                                 "Seperti lapis, ia punya **keadaan internal** yang disimpan "
                                 "di variabel Keras. Bedanya, variabel itu ==tidak diperbarui "
                                 "lewat backpropagation==, jadi Anda menulis sendiri logika "
                                 "pembaruannya."},
                {"t": "code", "lang": "python", "file": "listing 7.18 — RMSE sebagai metrik kustom",
                 "src": """from keras import ops

class RootMeanSquaredError(keras.metrics.Metric):
    def __init__(self, name="rmse", **kwargs):
        super().__init__(name=name, **kwargs)
        self.mse_sum = self.add_weight(name="mse_sum", initializer="zeros")
        self.total_samples = self.add_weight(name="total_samples", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true = ops.one_hot(y_true, num_classes=ops.shape(y_pred)[1])
        self.mse_sum.assign_add(ops.sum(ops.square(y_true - y_pred)))
        self.total_samples.assign_add(ops.shape(y_pred)[0])

    def result(self):
        return ops.sqrt(self.mse_sum / self.total_samples)

    def reset_state(self):                 # supaya objek metrik yang sama bisa dipakai
        self.mse_sum.assign(0.)            # lintas-epoch dan lintas latih/evaluasi
        self.total_samples.assign(0.)"""},
                {"t": "band",
                 "md": "Tiga metode itulah kontraknya: **`update_state()`** memperbarui, "
                       "**`result()`** melaporkan nilai sekarang, **`reset_state()`** "
                       "mengosongkan tanpa perlu membuat objek baru."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.3.2",
            "title": "Callback: dari pesawat kertas jadi dron",
            "blocks": [
                {"t": "quote",
                 "md": "Meluncurkan pelatihan pada data besar selama puluhan epoch dengan "
                       "`model.fit()` itu sedikit seperti melempar pesawat kertas: setelah "
                       "dorongan awal, Anda tidak punya kendali atas lintasannya maupun "
                       "tempat mendaratnya. API callback Keras mengubah panggilan "
                       "`model.fit()` Anda dari pesawat kertas menjadi **dron cerdas dan "
                       "otonom** yang bisa memeriksa dirinya sendiri dan bertindak.",
                 "cite": "Chollet & Watson, bab 7.3.2"},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "💾", "h": "Model checkpointing",
                     "p": "Menyimpan keadaan model di berbagai titik selama pelatihan."},
                    {"ico": "⏹", "h": "Early stopping",
                     "p": "Menghentikan pelatihan saat rugi validasi berhenti membaik -- "
                          "dan menyimpan model terbaik yang sudah diperoleh."},
                    {"ico": "🎚", "h": "Menyetel parameter dinamis",
                     "p": "Misalnya learning rate optimizer, di tengah pelatihan."},
                    {"ico": "📝", "h": "Mencatat & menggambar",
                     "p": "Bilah kemajuan `fit()` yang sudah Anda kenal itu ==sebenarnya "
                          "sebuah callback=="},
                ]},
                {"t": "code", "lang": "python", "file": "callback bawaan (tidak lengkap)",
                 "src": """keras.callbacks.ModelCheckpoint
keras.callbacks.EarlyStopping
keras.callbacks.LearningRateScheduler
keras.callbacks.ReduceLROnPlateau
keras.callbacks.CSVLogger"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.3.2 · listing 7.19",
            "title": "EarlyStopping + ModelCheckpoint: pasangan baku",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 7.19",
                 "src": """callbacks_list = [
    keras.callbacks.EarlyStopping(
        monitor="accuracy",     # dipantau, jadi harus ada di metrics model
        patience=1,             # berhenti bila tak membaik lebih dari satu epoch
    ),
    keras.callbacks.ModelCheckpoint(
        filepath="checkpoint_path.keras",
        monitor="val_loss",
        save_best_only=True,    # berkas tidak ditimpa kecuali val_loss membaik
    ),
]

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_images, train_labels, epochs=10,
          callbacks=callbacks_list,
          validation_data=(val_images, val_labels))   # WAJIB, karena val_* dipantau"""},
                {"t": "band",
                 "md": "Ini menggantikan pola boros di bab 4-5: latih sampai overfit untuk "
                       "**mencari** epoch terbaik, lalu latih ulang dari nol sebanyak itu. "
                       "Dengan pasangan callback ini, ==sekali jalan sudah cukup=="},
                {"t": "code", "lang": "python", "file": "menyimpan dan memuat manual",
                 "src": """model.save("my_checkpoint_path.keras")
model = keras.models.load_model("checkpoint_path.keras")"""},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.3.3 · listing 7.20",
            "title": "Callback kustom -- enam kait yang tersedia",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "kait yang bisa Anda isi",
                         "src": """on_epoch_begin(epoch, logs)
on_epoch_end(epoch, logs)
on_batch_begin(batch, logs)
on_batch_end(batch, logs)
on_train_begin(logs)
on_train_end(logs)"""},
                        {"t": "p", "md": "Semuanya dipanggil dengan argumen `logs`, sebuah "
                                         "kamus berisi informasi tentang batch, epoch, atau "
                                         "jalannya pelatihan -- metrik latih dan validasi."},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 7.20 — riwayat rugi per batch",
                         "src": """class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs):
        self.per_batch_losses = []

    def on_batch_end(self, batch, logs):
        self.per_batch_losses.append(
            logs.get("loss"))

    def on_epoch_end(self, epoch, logs):
        plt.clf()
        plt.plot(range(len(self.per_batch_losses)),
                 self.per_batch_losses)
        plt.savefig(f"plot_at_epoch_{epoch}", dpi=300)
        self.per_batch_losses = []"""},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.3.4",
            "title": "TensorBoard: memutar lingkar kemajuan lebih cepat",
            "blocks": [
                {"t": "p", "md": "Kemajuan adalah proses berulang: **gagasan → percobaan → "
                                 "hasil → gagasan berikutnya** (gambar 7.6). Makin banyak "
                                 "putaran yang bisa Anda jalankan, makin tajam gagasannya. "
                                 "Keras memperpendek jarak gagasan-ke-percobaan; GPU cepat "
                                 "memperpendek percobaan-ke-hasil; ==TensorBoard menangani "
                                 "hasil-ke-gagasan berikutnya=="},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "📈", "h": "Pantau metrik", "p": "Secara visual, selama pelatihan berjalan."},
                    {"ico": "🏗", "h": "Gambar arsitektur", "p": "Visualisasi model."},
                    {"ico": "📊", "h": "Histogram", "p": "Aktivasi dan gradien."},
                    {"ico": "🧭", "h": "Embedding 3D", "p": "Jelajahi ruang embedding."},
                ]},
                {"t": "code", "lang": "python", "file": "memakainya",
                 "src": """tensorboard = keras.callbacks.TensorBoard(log_dir="/full_path_to_your_log_dir")
model.fit(train_images, train_labels, epochs=10,
          validation_data=(val_images, val_labels),
          callbacks=[tensorboard])"""},
                {"t": "code", "lang": "bash", "file": "menjalankan servernya",
                 "src": """# di mesin lokal
tensorboard --logdir /full_path_to_your_log_dir

# di dalam notebook Colab
%load_ext tensorboard
%tensorboard --logdir /full_path_to_your_log_dir"""},
            ],
        },

        {"type": "section", "num": "03", "title": "Menulis lingkar pelatihan sendiri",
         "lead": "Saat fit() tidak cukup -- dan cara tetap memakainya."},

        {
            "type": "slide",
            "kicker": "Bagian 7.4",
            "title": "Kapan fit() memang tidak cukup",
            "blocks": [
                {"t": "p", "md": "`fit()` bawaan **hanya berfokus pada supervised learning**: "
                                 "ada target yang diketahui, dan rugi dihitung sebagai fungsi "
                                 "target itu dan prediksi model. Tidak semua bentuk machine "
                                 "learning masuk kategori itu."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🎨", "h": "Generative learning",
                     "p": "Tidak ada target eksplisit. Diperkenalkan di **bab 16**."},
                    {"ico": "🔁", "h": "Self-supervised",
                     "p": "Targetnya diambil **dari masukannya sendiri**."},
                    {"ico": "🐕", "h": "Reinforcement learning",
                     "p": "Pembelajaran didorong **imbalan sesekali** -- seperti melatih anjing."},
                ]},
                {"t": "band", "style": "amber",
                 "md": "Dua kehalusan yang harus diperhatikan saat menulis lingkar sendiri:"},
                {"t": "steps", "items": [
                    "**`training=True` wajib diteruskan.** Lapis seperti `Dropout` berperilaku "
                    "berbeda saat latih dan saat inferensi. `dropout(inputs, training=True)` "
                    "menjatuhkan sebagian aktivasi; `training=False` tidak melakukan apa pun. "
                    "Jadi: `predictions = model(inputs, training=True)`.",
                    "**Pakai `model.trainable_weights`, bukan `model.weights`.** Model punya "
                    "dua jenis bobot: **terlatih** (diperbarui backpropagation) dan **tak "
                    "terlatih** (diperbarui lapis pemiliknya saat lintasan maju). Di antara "
                    "lapis bawaan Keras, satu-satunya yang punya bobot tak terlatih adalah "
                    "**`BatchNormalization`** -- ia melacak rerata dan simpangan baku data "
                    "yang lewat (bab 9).",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.4.2",
            "title": "Satu langkah pelatihan, tiga backend",
            "blocks": [
                {"t": "code", "lang": "python", "file": "TensorFlow",
                 "src": """def train_step(inputs, targets):
    with tf.GradientTape() as tape:
        predictions = model(inputs, training=True)
        loss = loss_fn(targets, predictions)
    gradients = tape.gradient(loss, model.trainable_weights)
    optimizer.apply(gradients, model.trainable_weights)
    return loss"""},
                {"t": "code", "lang": "python", "file": "PyTorch",
                 "src": """def train_step(inputs, targets):
    predictions = model(inputs, training=True)
    loss = loss_fn(targets, predictions)
    loss.backward()                                     # isi nilai gradien
    gradients = [w.value.grad for w in model.trainable_weights]
    with torch.no_grad():                               # WAJIB di dalam no_grad()
        optimizer.apply(gradients, model.trainable_weights)
    model.zero_grad()                                   # WAJIB - backward() itu menumpuk
    return loss"""},
                {"t": "band", "style": "rose",
                 "md": "Pada PyTorch, `model.zero_grad()` **kritis**: panggilan `backward()` "
                       "bersifat menambahkan. Kalau gradien tidak dikosongkan tiap langkah, "
                       "nilainya menumpuk dan ==pelatihan tidak akan berjalan=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.4.2 · JAX",
            "title": "JAX: paling rumit, karena tanpa keadaan sama sekali",
            "blocks": [
                {"t": "p", "md": "Karena fungsi gradiennya diperoleh lewat metapemrograman, "
                                 "Anda harus lebih dulu menuliskan fungsi yang **mengembalikan** "
                                 "rugi. Fungsi itu harus tanpa keadaan: ia menerima semua "
                                 "variabel yang dipakainya sebagai argumen, dan "
                                 "**mengembalikan nilai setiap variabel yang diperbaruinya** "
                                 "-- termasuk bobot tak terlatih tadi."},
                {"t": "code", "lang": "python", "file": "stateless_call() dan value_and_grad",
                 "src": """# lintasan maju tanpa keadaan
outputs, non_trainable_weights = model.stateless_call(
    trainable_weights, non_trainable_weights, inputs)

def compute_loss_and_updates(trainable_variables, non_trainable_variables,
                             inputs, targets):
    outputs, non_trainable_variables = model.stateless_call(
        trainable_variables, non_trainable_variables, inputs, training=True)
    loss = loss_fn(targets, outputs)
    return loss, non_trainable_variables      # skalar DULU, sisanya jadi 'aux'

# jax.grad hanya menerima fungsi yang mengembalikan skalar -> pakai has_aux
grad_fn = jax.value_and_grad(compute_loss_and_updates, has_aux=True)
(loss, non_trainable_weights), gradients = grad_fn(
    trainable_variables, non_trainable_variables, inputs, targets)

# optimizer pun punya keadaan (momentum dll), jadi ada padanan tanpa-keadaannya
trainable_variables, optimizer_variables = optimizer.stateless_apply(
    optimizer_variables, gradients, trainable_variables)"""},
                {"t": "band",
                 "md": "Pola yang sama berlaku untuk metrik: di JAX, metode yang mengubah "
                       "keadaan seperti `update_state()` tidak bisa dipanggil di dalam fungsi "
                       "tanpa keadaan. Padanannya: ==`stateless_update_state()`, "
                       "`stateless_result()`, `stateless_reset_state()`=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.4.3",
            "title": "Memakai metrik di tingkat rendah",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "metrik biasa",
                         "src": """metric = keras.metrics.SparseCategoricalAccuracy()
targets = ops.array([0, 1, 2])
predictions = ops.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])
metric.update_state(targets, predictions)
print(f"result: {metric.result():.2f}")"""},
                        {"t": "out", "src": "result: 1.00"},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "melacak rerata skalar",
                         "src": """values = ops.array([0, 1, 2, 3, 4])
mean_tracker = keras.metrics.Mean()
for value in values:
    mean_tracker.update_state(value)
print(f"Mean: {mean_tracker.result():.2f}")"""},
                        {"t": "out", "src": "Mean: 2.00"},
                    ],
                ]},
                {"t": "band", "style": "amber",
                 "md": "Jangan lupa `metric.reset_state()` saat mau mengosongkan hasilnya -- "
                       "**di awal tiap epoch pelatihan, dan di awal evaluasi**. Lupa "
                       "melakukannya membuat angka metrik ==tercampur antar-epoch=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 7.4.4 · listing 7.21",
            "title": "Jalan tengah: train_step() sendiri, fit() tetap dipakai",
            "blocks": [
                {"t": "p", "md": "Menulis seluruh lingkar dari nol memberi keluwesan paling "
                                 "besar, tetapi Anda kehilangan **callback, pengoptimalan "
                                 "unjuk kerja, dan dukungan pelatihan tersebar**. Jalan "
                                 "tengahnya: ganti `train_step()` saja, biarkan kerangka "
                                 "mengerjakan sisanya."},
                {"t": "code", "lang": "python", "file": "listing 7.21 — versi TensorFlow",
                 "src": """loss_fn = keras.losses.SparseCategoricalCrossentropy()
loss_tracker = keras.metrics.Mean(name="loss")

class CustomModel(keras.Model):
    def train_step(self, data):
        inputs, targets = data
        with tf.GradientTape() as tape:
            predictions = self(inputs, training=True)   # self, bukan model
            loss = loss_fn(targets, predictions)
        gradients = tape.gradient(loss, self.trainable_weights)
        self.optimizer.apply(gradients, self.trainable_weights)
        loss_tracker.update_state(loss)
        return {"loss": loss_tracker.result()}          # nama metrik -> nilainya

    @property
    def metrics(self):
        return [loss_tracker]      # didaftarkan agar reset_state() dipanggil otomatis
                                   # di awal tiap epoch dan di awal evaluate()"""},
                {"t": "bullets", "items": [
                    "Pola ini **tidak menghalangi** Anda memakai Functional API -- berlaku "
                    "untuk Sequential, Functional, maupun subclass.",
                    "Anda **tidak perlu** dekorator `@tf.function` atau `@jax.jit`; "
                    "==kerangkanya yang mengerjakan itu untuk Anda==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Ringkasan",
            "title": "Yang wajib terbawa dari bab 7",
            "blocks": [
                {"t": "steps", "items": [
                    "**Progressive disclosure of complexity** -- satu spektrum alur kerja di "
                    "atas API bersama `Layer` dan `Model`, bukan beberapa kerangka terpisah.",
                    "**Sequential** untuk tumpukan sederhana; **Functional API** untuk graf "
                    "lapis -- dan itu yang dipakai sisa buku ini; **subclassing** untuk yang "
                    "tidak bisa dinyatakan sebagai graf.",
                    "Functional memberi **akses ke keterhubungan lapis**: `plot_model()` dan "
                    "ekstraksi fitur. Subclassing ==membuang keduanya==.",
                    "Campuran terbaik: **model Functional yang berisi lapis-lapis subclass**.",
                    "**Metrik kustom** = `update_state` / `result` / `reset_state`. "
                    "**Callback** = enam kait `on_*`.",
                    "**`EarlyStopping` + `ModelCheckpoint`** menggantikan pola latih-ulang "
                    "yang boros itu.",
                    "Menulis `train_step()` sendiri: ingat **`training=True`** dan "
                    "**`trainable_weights`**; di PyTorch jangan lupa **`zero_grad()`**; "
                    "di JAX semuanya lewat padanan **`stateless_*`**.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "03_train_step_kustom_per_backend.ipynb",
                     "href": "../../course-slides/notebooks/ch07/03_train_step_kustom_per_backend.ipynb"},
                    {"k": "BAB BERIKUT", "ic": "➡", "v": "Bab 8 — Klasifikasi citra",
                     "href": "../ch08/index.html"},
                ]},
            ],
        },
    ],
}
