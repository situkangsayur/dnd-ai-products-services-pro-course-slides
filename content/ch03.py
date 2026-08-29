# -*- coding: utf-8 -*-
"""Bab 3 — Introduction to TensorFlow, PyTorch, JAX, and Keras.

Sumber: Chollet & Watson, *Deep Learning with Python*, 3rd ed., bab 3.
https://deeplearningwithpython.io/chapters/chapter03_introduction-to-ml-frameworks

Penilaian kecepatan antar-kerangka di bab ini adalah penilaian penulisnya, dan
di sini ditandai sebagai penilaian penulis -- bukan hasil tolok ukur kelas ini.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


SVG_STACK = """
<svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Keras sebagai lapisan tingkat tinggi di atas TensorFlow, PyTorch, dan JAX">
  <rect x="60" y="18" width="640" height="52" rx="12"
        fill="rgba(167,139,250,.16)" stroke="rgba(167,139,250,.65)" stroke-width="1.5"/>
  <text class="d-lbl" x="380" y="42" text-anchor="middle" font-weight="700">Keras 3</text>
  <text class="d-sm" x="380" y="60" text-anchor="middle">
    layer &#183; model &#183; loss &#183; optimizer &#183; metric &#183; lingkar pelatihan
  </text>

  <line x1="200" y1="70" x2="200" y2="100" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>
  <line x1="380" y1="70" x2="380" y2="100" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>
  <line x1="560" y1="70" x2="560" y2="100" stroke="rgba(140,190,255,.35)" stroke-width="1.2"/>

  <rect class="d-box-a" x="112" y="100" width="176" height="76" rx="10"/>
  <text class="d-lbl" x="200" y="126" text-anchor="middle">TensorFlow</text>
  <text class="d-sm" x="200" y="146" text-anchor="middle">GradientTape</text>
  <text class="d-sm" x="200" y="164" text-anchor="middle">@tf.function</text>

  <rect class="d-box-a" x="292" y="100" width="176" height="76" rx="10"/>
  <text class="d-lbl" x="380" y="126" text-anchor="middle">PyTorch</text>
  <text class="d-sm" x="380" y="146" text-anchor="middle">.backward()</text>
  <text class="d-sm" x="380" y="164" text-anchor="middle">torch.compile()</text>

  <rect class="d-box-a" x="472" y="100" width="176" height="76" rx="10"/>
  <text class="d-lbl" x="560" y="126" text-anchor="middle">JAX</text>
  <text class="d-sm" x="560" y="146" text-anchor="middle">jax.grad()</text>
  <text class="d-sm" x="560" y="164" text-anchor="middle">@jax.jit</text>

  <rect class="d-box" x="112" y="196" width="536" height="40" rx="10"/>
  <text class="d-sm" x="380" y="221" text-anchor="middle">
    autodiff &#183; komputasi tensor di CPU / GPU / TPU &#183; komputasi tersebar
  </text>
</svg>
"""

TIKZ_STACK = r"""
\begin{tikzpicture}[font=\sffamily\tiny,
  fw/.style={draw=signal!60, fill=signal!9, rounded corners=4pt,
             minimum width=2.7cm, minimum height=1.25cm, text=ink, align=center}]
  \node[draw=violet!70, fill=violet!14, rounded corners=5pt, minimum width=9.6cm,
        minimum height=0.95cm, text=ink, align=center] (k) at (0,2.0)
    {{\bfseries\small Keras 3}\\layer $\cdot$ model $\cdot$ loss $\cdot$ optimizer $\cdot$ metric $\cdot$ lingkar pelatihan};
  \node[fw] (tf) at (-3.2,0.55) {{\bfseries TensorFlow}\\GradientTape\\\ttfamily @tf.function};
  \node[fw] (pt) at (0,0.55)    {{\bfseries PyTorch}\\\ttfamily .backward()\\\ttfamily torch.compile()};
  \node[fw] (jx) at (3.2,0.55)  {{\bfseries JAX}\\\ttfamily jax.grad()\\\ttfamily @jax.jit};
  \draw[rule] (tf.north) -- ($(tf.north)+(0,0.35)$);
  \draw[rule] (pt.north) -- ($(pt.north)+(0,0.35)$);
  \draw[rule] (jx.north) -- ($(jx.north)+(0,0.35)$);
  \node[draw=rule, fill=papertint, rounded corners=4pt, minimum width=9.0cm,
        minimum height=0.6cm, text=ink2] at (0,-0.55)
    {autodiff $\cdot$ komputasi tensor di CPU / GPU / TPU $\cdot$ komputasi tersebar};
\end{tikzpicture}
"""

SVG_TIMELINE = """
<svg viewBox="0 0 760 170" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Garis waktu kerangka kerja deep learning 1964 sampai 2023">
  <line x1="30" y1="96" x2="736" y2="96" stroke="rgba(140,190,255,.32)" stroke-width="1.6"/>
  <g>
    <circle cx="46"  cy="96" r="5" fill="#2C7BD4"/>
    <text class="d-mono" x="46"  y="126" text-anchor="middle" fill="#7E93B4">1964</text>
    <text class="d-sm"   x="46"  y="74"  text-anchor="middle">autodiff</text>
  </g>
  <g>
    <circle cx="146" cy="96" r="5" fill="#2C7BD4"/>
    <text class="d-mono" x="146" y="126" text-anchor="middle" fill="#7E93B4">2006</text>
    <text class="d-sm"   x="146" y="74"  text-anchor="middle">CUDA</text>
  </g>
  <g>
    <circle cx="246" cy="96" r="5" fill="#2C7BD4"/>
    <text class="d-mono" x="246" y="126" text-anchor="middle" fill="#7E93B4">2009</text>
    <text class="d-sm"   x="246" y="74"  text-anchor="middle">Theano</text>
  </g>
  <g>
    <circle cx="346" cy="96" r="6" fill="#22D3EE"/>
    <text class="d-mono" x="346" y="126" text-anchor="middle" fill="#7E93B4">2015</text>
    <text class="d-sm"   x="346" y="74"  text-anchor="middle" fill="#22D3EE">Keras</text>
    <text class="d-sm"   x="346" y="56"  text-anchor="middle" fill="#22D3EE">TensorFlow</text>
  </g>
  <g>
    <circle cx="452" cy="96" r="5" fill="#2C7BD4"/>
    <text class="d-mono" x="452" y="126" text-anchor="middle" fill="#7E93B4">2016</text>
    <text class="d-sm"   x="452" y="74"  text-anchor="middle">PyTorch</text>
  </g>
  <g>
    <circle cx="558" cy="96" r="5" fill="#2C7BD4"/>
    <text class="d-mono" x="558" y="126" text-anchor="middle" fill="#7E93B4">2018</text>
    <text class="d-sm"   x="558" y="74"  text-anchor="middle">JAX</text>
  </g>
  <g>
    <circle cx="690" cy="96" r="6" fill="#A78BFA"/>
    <text class="d-mono" x="690" y="126" text-anchor="middle" fill="#7E93B4">2023</text>
    <text class="d-sm"   x="690" y="74"  text-anchor="middle" fill="#A78BFA">PyTorch 2.0</text>
    <text class="d-sm"   x="690" y="56"  text-anchor="middle" fill="#A78BFA">Keras 3.0</text>
  </g>
  <text class="d-sm" x="30" y="158" fill="#F5B301">
    Pertengahan 2016: lebih dari separuh pengguna TensorFlow mengaksesnya lewat Keras
  </text>
</svg>
"""

TIKZ_TIMELINE = r"""
\begin{tikzpicture}[font=\sffamily\tiny]
  \draw[rule, line width=1pt] (0,0) -- (11,0);
  \foreach \x/\y/\l in {0.3/1964/autodiff, 1.9/2006/CUDA, 3.4/2009/Theano,
                        5.0/2015/{Keras + TensorFlow}, 6.7/2016/PyTorch,
                        8.3/2018/JAX, 10.4/2023/{PyTorch 2.0 + Keras 3.0}} {
    \fill[itbbluelt] (\x,0) circle (2.2pt);
    \node[text=ink3, font=\ttfamily\tiny, anchor=north] at (\x,-0.12) {\y};
    \node[text=ink, anchor=south, align=center, text width=1.9cm] at (\x,0.12) {\l};
  }
  \node[text=amber, anchor=west] at (0,-0.85)
    {Pertengahan 2016: lebih dari separuh pengguna TensorFlow mengaksesnya lewat Keras};
\end{tikzpicture}
"""


NB = ["01_tiga_kerangka_berdampingan.ipynb", "02_keras3_ganti_backend.ipynb",
      "03_layer_kustom_dan_fit.ipynb"]

DECK = {
    "id": "ch03",
    "kind": "chapter",
    "number": 3,
    "title": "Pengenalan TensorFlow, PyTorch, JAX, dan Keras",
    "subtitle": "Satu lapis Dense yang sama, ditulis empat kali -- supaya perbedaan "
                "rancangan keempat kerangka kerja itu terlihat, bukan sekadar didengar.",
    "source": "Chollet & Watson, Deep Learning with Python 3e -- bab 3",
    "source_url": chapter_url(3),
    "duration": "2,5 jam",
    "presenter": {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Asisten Pengajar"},
    "resources": chapter_resources(3, local_notebooks=NB),
    "objectives": [
        "Menyebut **tiga kemampuan** yang dimiliki semua kerangka kerja modern, dan "
        "apa yang membedakan ketiganya di luar itu.",
        "Menghitung gradien dengan **GradientTape, `.backward()`, dan `jax.grad()`**, "
        "dan menjelaskan mengapa ketiganya berbeda bentuk.",
        "Membedakan **stateful imperatif** (TF, PyTorch) dari **stateless fungsional** "
        "(JAX), dan menyebut akibatnya pada penulisan lingkar pelatihan.",
        "Mengganti backend Keras 3 tanpa mengubah satu baris pun kode model.",
        "Menulis **Layer kustom** dengan `build()` dan `call()`, lalu memakainya "
        "lewat `compile()` dan `fit()`.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Bagian 3.1",
            "title": "Bagaimana kita sampai di sini",
            "blocks": [
                {"t": "fig", "svg": SVG_TIMELINE, "tikz": TIKZ_TIMELINE,
                 "cap": "Autodiff sudah ada sejak 1964; yang baru pada 2009 adalah "
                        "menggabungkannya dengan komputasi GPU."},
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "∂", "h": "Automatic differentiation",
                     "p": "Untuk sebarang fungsi terdiferensialkan yang Anda tulis.",
                     "style": "accent"},
                    {"ico": "▦", "h": "Komputasi tensor",
                     "p": "Di CPU, GPU, dan perangkat keras khusus seperti TPU.",
                     "style": "accent"},
                    {"ico": "⇄", "h": "Komputasi tersebar",
                     "p": "Antar-perangkat dan antar-mesin.", "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Ketiganya dimiliki **semua** kerangka kerja besar. Jadi memilih "
                       "kerangka kerja ==bukan soal kemampuan==, melainkan soal gaya "
                       "penulisan, ekosistem, dan kecepatan."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.2",
            "title": "Keras di atas, tiga mesin di bawah",
            "blocks": [
                {"t": "fig", "svg": SVG_STACK, "tikz": TIKZ_STACK,
                 "cap": "Keras memerlukan sebuah backend; NumPy bisa dipasang tetapi "
                        "tidak bisa melatih, sebab tidak punya API gradien."},
                {"t": "quote",
                 "md": "Keras itu seperti perangkat bangunan pracetak, sedangkan "
                       "TensorFlow, PyTorch, dan JAX adalah bahan mentahnya.",
                 "cite": "Chollet & Watson, bab 3"},
            ],
            "notes": "Pembagian kerjanya: yang di bawah mengurus tensor, operasi, dan "
                     "backprop; yang di atas mengurus layer, model, loss, optimizer, "
                     "metric, dan lingkar pelatihan.",
        },

        {"type": "section", "num": "01", "title": "TensorFlow",
         "lead": "Tensor kekal, Variable untuk keadaan, GradientTape untuk gradien."},

        {
            "type": "slide",
            "kicker": "Bagian 3.3",
            "title": "Tensor kekal, Variable yang bisa diubah",
            "blocks": [
                {"t": "code", "lang": "python", "file": "tensor dan variable di TensorFlow",
                 "src": """import tensorflow as tf

tf.ones(shape=(2, 1))
tf.zeros(shape=(2, 1))
tf.constant([1.0, 2.0])            # KEKAL - tidak bisa ditugasi ulang

v = tf.Variable(initial_value=tf.random.normal(shape=(3, 1)))
v.assign(tf.ones((3, 1)))          # ganti seluruh nilainya
v[0, 0].assign(3.0)                # ganti sebagiannya
v.assign_add(tf.ones((3, 1)))      # += yang efisien

a = tf.ones((2, 2))
e = tf.matmul(a, tf.square(a))
f = tf.concat((a, e), axis=0)      # perhatikan: 'axis'"""},
                {"t": "band", "style": "amber",
                 "md": "Bedanya penting: tensor TensorFlow itu **konstanta yang kekal**. "
                       "Untuk parameter yang harus berubah saat dilatih, Anda ==wajib== "
                       "memakai `tf.Variable`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.3",
            "title": "GradientTape dan kompilasi graf",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "gradien",
                         "src": """input_var = tf.Variable(3.0)
with tf.GradientTape() as tape:
    result = tf.square(input_var)
gradient = tape.gradient(result, input_var)

# konstanta harus 'ditonton' dulu
c = tf.constant(3.0)
with tf.GradientTape() as tape:
    tape.watch(c)
    result = tf.square(c)
gradient = tape.gradient(result, c)"""},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "kompilasi",
                         "src": """@tf.function
def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)

# XLA: lebih agresif, kompilasi
# pertama lebih lama
@tf.function(jit_compile=True)
def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)"""},
                    ],
                ]},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✔", "h": "Kekuatan",
                     "p": "Cepat lewat mode graf dan XLA · lengkap sekali (tensor string, "
                          "ragged tensor) · `tf.data` unggul untuk pra-pemrosesan · "
                          "ekosistem produksi paling matang (TFX, TF-Serving, TFLite).",
                     "style": "good"},
                    {"ico": "✖", "h": "Kelemahan",
                     "p": "API sangat luas dengan ribuan operasi · di beberapa tempat "
                          "menyimpang dari NumPy · dukungan di Hugging Face kalah dari "
                          "PyTorch.", "style": "bad"},
                ]},
            ],
            "notes": "Untuk BRI yang perlu deployment on-premise, ekosistem produksi TF "
                     "ini justru argumen yang paling relevan.",
        },

        {"type": "section", "num": "02", "title": "PyTorch",
         "lead": "Tensor bisa diubah, .backward() mengisi .grad, eager sebagai bawaan."},

        {
            "type": "slide",
            "kicker": "Bagian 3.4",
            "title": "Gaya PyTorch: tanpa pita, ada .grad",
            "blocks": [
                {"t": "code", "lang": "python", "file": "tensor, parameter, gradien",
                 "src": """import torch                      # paketnya 'torch', bukan 'pytorch'

x = torch.zeros(size=(2, 1))
x[0, 0] = 1.0                       # BISA ditugasi - beda dari TensorFlow

p = torch.nn.parameter.Parameter(data=x)      # penanda: ini keadaan terlatih

f = torch.cat((torch.ones((2, 2)), x), dim=0) # perhatikan: 'dim', bukan 'axis'

input_var = torch.tensor(3.0, requires_grad=True)
result = torch.square(input_var)
result.backward()                   # mengisi input_var.grad
print(input_var.grad)

input_var.grad = None               # WAJIB: gradien menumpuk kalau tidak dinolkan"""},
                {"t": "band", "style": "rose",
                 "md": "Baris terakhir itu sumber bug klasik. Panggilan `.backward()` "
                       "berikutnya ==menjumlahkan== gradien baru ke yang lama, bukan "
                       "menggantinya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.4",
            "title": "Module, optimizer, dan mantra tiga baris",
            "blocks": [
                {"t": "code", "lang": "python", "file": "pola pelatihan PyTorch",
                 "src": """class LinearModel(torch.nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.W = torch.nn.Parameter(torch.rand(input_dim, output_dim))
        self.b = torch.nn.Parameter(torch.zeros(output_dim))

    def forward(self, inputs):
        return torch.matmul(inputs, self.W) + self.b

model = LinearModel(2, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

def training_step(inputs, targets):
    predictions = model(inputs)
    loss = mean_squared_error(targets, predictions)
    loss.backward()        # 1. hitung gradien
    optimizer.step()       # 2. perbarui bobot
    model.zero_grad()      # 3. nolkan, siap batch berikutnya
    return loss"""},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✔", "h": "Kekuatan",
                     "p": "Eager sebagai bawaan -- pengawakutuan paling mudah · "
                          "dukungan kelas satu di Hugging Face, dan itulah pendorong "
                          "adopsi terbesarnya.", "style": "good"},
                    {"ico": "✖", "h": "Kelemahan",
                     "p": "API tidak konsisten (`axis` kadang jadi `dim`) · menurut "
                          "penulis, **paling lambat** di antara yang besar · "
                          "`torch.compile()` masih penuh kasus tepi dan jarang dipakai.",
                     "style": "bad"},
                ]},
            ],
            "notes": "Kalau peserta datang dari Hugging Face, PyTorch akan terasa paling "
                     "akrab. Katakan itu; jangan paksakan satu kerangka.",
        },

        {"type": "section", "num": "03", "title": "JAX",
         "lead": "Fungsi tanpa keadaan. Gradien sebagai transformasi fungsi."},

        {
            "type": "slide",
            "kicker": "Bagian 3.5",
            "title": "Tanpa keadaan -- termasuk bilangan acaknya",
            "blocks": [
                {"t": "code", "lang": "python", "file": "array, kunci acak, pembaruan",
                 "src": """import jax
from jax import numpy as jnp

jnp.ones(shape=(2, 1))              # API NumPy, tanpa penyimpangan

# Tidak ada keadaan acak global: kunci diberikan secara eksplisit
seed_key = jax.random.key(123)
jax.random.normal(seed_key, shape=(3,))     # kunci sama -> nilai sama, selalu
key1, key2 = jax.random.split(seed_key)     # cara membuat kunci baru

# Array kekal: perbarui dengan menghasilkan array baru
x = jnp.array([1, 2, 3], dtype="float32")
new_x = x.at[0].set(10)"""},
                {"t": "band",
                 "md": "Kelihatannya merepotkan, dan memang. Imbalannya: perhitungan jadi "
                       "==bisa diparalelkan otomatis tanpa sinkronisasi==, dan hasilnya "
                       "deterministik -- dua hal yang menentukan pada skala besar."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.5",
            "title": "jax.grad(): gradien sebagai transformasi fungsi",
            "blocks": [
                {"t": "code", "lang": "python", "file": "lingkar pelatihan JAX yang utuh",
                 "src": """def model(inputs, W, b):
    return jnp.matmul(inputs, W) + b

def compute_loss(state, inputs, targets):
    W, b = state
    predictions = model(inputs, W, b)
    return jnp.mean(jnp.square(targets - predictions))

grad_fn = jax.value_and_grad(compute_loss)   # fungsi -> fungsi gradien

@jax.jit
def training_step(inputs, targets, W, b):
    loss, grads = grad_fn((W, b), inputs, targets)
    grad_W, grad_b = grads
    W = W - grad_W * 0.1
    b = b - grad_b * 0.1
    return loss, W, b                        # keadaan WAJIB dikembalikan"""},
                {"t": "table",
                 "head": ["Kebutuhan", "Pemanggilannya"],
                 "widths": [40, 60],
                 "rows": [
                     ["Gradien saja", "`jax.grad(f)`"],
                     ["Rugi **dan** gradien sekaligus", "`jax.value_and_grad(f)` -- lebih hemat"],
                     ["Ada keluaran sampingan", "`jax.value_and_grad(f, has_aux=True)`"],
                 ]},
                {"t": "band", "style": "amber",
                 "md": "Perhatikan baris terakhir: `training_step` **mengembalikan** W dan b. "
                       "Tidak ada yang berubah di tempat. Inilah harga dan sekaligus "
                       "keuntungan gaya fungsional."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.3-3.5",
            "title": "Ketiganya berdampingan",
            "blocks": [
                {"t": "table",
                 "head": ["", "TensorFlow", "PyTorch", "JAX"],
                 "widths": [17, 28, 28, 27],
                 "rows": [
                     ["**Paradigma**", "Imperatif berkeadaan", "Imperatif berkeadaan",
                      "Fungsional tanpa keadaan"],
                     ["**Tensor**", "Kekal (`Variable` untuk keadaan)", "Bisa diubah",
                      "Kekal (`.at[].set()`)"],
                     ["**Gradien**", "`GradientTape`", "`.backward()` → `.grad`",
                      "`jax.grad()` (transformasi)"],
                     ["**Kompilasi**", "`@tf.function`, XLA", "`@torch.compile` (Dynamo)",
                      "`@jax.jit` (XLA)"],
                     ["**Eksekusi**", "Eager + graf", "Eager (bawaan)", "Eager + JIT"],
                     ["**Awak-kutu**", "Lebih sulit di mode graf", "Paling mudah",
                      "Sulit (fungsional + JIT)"],
                     ["**Ekosistem**", "Perkakas produksi", "Hugging Face, riset",
                      "Riset, skala Google"],
                 ]},
                {"t": "band", "style": "amber",
                 "md": "Peringkat kecepatan di bab ini -- JAX tercepat, PyTorch terlambat, "
                       "selisih 20-30% dan sampai 3-5x pada model besar -- adalah "
                       "==penilaian penulis buku==, bukan tolok ukur yang dijalankan kelas "
                       "ini. Perlakukan sebagai petunjuk arah, dan ukur sendiri untuk "
                       "beban kerja Anda."},
            ],
            "notes": "Jangan berdebat soal kerangka mana yang menang. Yang penting peserta "
                     "tahu ada perbedaan rancangan yang nyata, dan Keras menutupinya.",
        },

        {"type": "section", "num": "04", "title": "Keras",
         "lead": "Satu kode model, tiga mesin di belakangnya."},

        {
            "type": "slide",
            "kicker": "Bagian 3.6",
            "title": "Mengganti backend tanpa menyentuh model",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "cara 1 — variabel lingkungan",
                         "src": """import os
os.environ["KERAS_BACKEND"] = "jax"

import keras          # HARUS setelah baris di atas
print(keras.backend.backend())"""},
                        {"t": "out", "src": "jax"},
                    ],
                    [
                        {"t": "code", "lang": "json", "file": "cara 2 — ~/.keras/keras.json",
                         "src": """{
    "floatx": "float32",
    "epsilon": 1e-07,
    "backend": "tensorflow",
    "image_data_format": "channels_last"
}"""},
                    ],
                ]},
                {"t": "band", "style": "rose",
                 "md": "Urutannya tidak bisa ditawar: `os.environ[...]` harus dijalankan "
                       "==sebelum `import keras` yang pertama==. Setelah Keras terimpor, "
                       "menggantinya tidak berpengaruh, dan ini kebingungan nomor satu "
                       "di praktikum."},
                {"t": "p", "md": "Penulis menyarankan **JAX** untuk unjuk kerja terbaik, "
                                 "tetapi kode Keras yang sama berjalan di ketiganya."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.6.1-3.6.2",
            "title": "Layer: satuan bangunan, dan penyimpulan bentuk otomatis",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 3.22 — Layer kustom",
                 "src": """import keras

class SimpleDense(keras.Layer):
    def __init__(self, units, activation=None):
        super().__init__()
        self.units = units
        self.activation = activation

    def build(self, input_shape):          # dipanggil sekali, saat masukan pertama tiba
        batch_dim, input_dim = input_shape
        self.W = self.add_weight(shape=(input_dim, self.units),
                                 initializer="random_normal")
        self.b = self.add_weight(shape=(self.units,), initializer="zeros")

    def call(self, inputs):
        y = keras.ops.matmul(inputs, self.W) + self.b
        return self.activation(y) if self.activation is not None else y

my_dense = SimpleDense(units=32, activation=keras.ops.relu)
output = my_dense(keras.ops.ones(shape=(2, 784)))
print(output.shape)"""},
                {"t": "out", "src": "(2, 32)"},
                {"t": "band",
                 "md": "Karena `build()` menerima `input_shape`, Anda ==tidak perlu "
                       "menyebutkan ukuran masukan== saat menyusun model. Itulah sebabnya "
                       "`Sequential` di bab 2 hanya menyebut jumlah unit."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Bagian 3.6.4-3.6.6",
            "title": "compile(), fit(), dan data validasi",
            "blocks": [
                {"t": "code", "lang": "python", "file": "listing 3.26-3.29 — alur lengkap",
                 "src": """model = keras.Sequential([keras.layers.Dense(1)])

model.compile(
    optimizer=keras.optimizers.RMSprop(learning_rate=1e-4),
    loss=keras.losses.MeanSquaredError(),
    metrics=[keras.metrics.BinaryAccuracy()],
)

history = model.fit(
    training_inputs, training_targets,
    epochs=5, batch_size=16,
    validation_data=(val_inputs, val_targets),
)
print(history.history.keys())

loss_and_metrics = model.evaluate(val_inputs, val_targets, batch_size=128)
predictions = model.predict(new_inputs, batch_size=128)"""},
                {"t": "quote",
                 "md": "Tujuan machine learning bukan memperoleh model yang bekerja baik "
                       "pada data latih -- melainkan model yang bekerja baik secara umum, "
                       "terutama pada data yang belum pernah ditemuinya.",
                 "cite": "Chollet & Watson, bab 3"},
                {"t": "band", "style": "amber",
                 "md": "Karena itu **metric** dipantau tetapi ==tidak dioptimalkan==; yang "
                       "dioptimalkan hanya loss. Membingungkan keduanya adalah kesalahan "
                       "yang mahal, dan bab 5-6 kembali ke sini."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Ringkasan",
            "title": "Yang wajib terbawa dari bab 3",
            "blocks": [
                {"t": "steps", "items": [
                    "Semua kerangka kerja besar memberi **autodiff, komputasi tensor "
                    "di GPU/TPU, dan komputasi tersebar**. Sisanya soal gaya.",
                    "**TensorFlow** -- tensor kekal + `Variable`, `GradientTape`, ekosistem "
                    "produksi terkuat.",
                    "**PyTorch** -- tensor bisa diubah, `.backward()`, eager, raja Hugging Face. "
                    "Jangan lupa `zero_grad()`.",
                    "**JAX** -- fungsional tanpa keadaan, `jax.grad()` sebagai transformasi, "
                    "kunci acak eksplisit, tercepat menurut penulis.",
                    "**Keras 3** duduk di atas ketiganya. Ganti backend lewat "
                    "`KERAS_BACKEND` ==sebelum== `import keras`.",
                    "`Layer` dengan `build()` + `call()` adalah satuan bangunan segalanya; "
                    "bentuk masukan disimpulkan sendiri.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_tiga_kerangka_berdampingan.ipynb",
                     "href": "../../course-slides/notebooks/ch03/01_tiga_kerangka_berdampingan.ipynb"},
                    {"k": "BAB BERIKUT", "ic": "➡", "v": "Bab 4 — Klasifikasi dan regresi",
                     "href": "../ch04/index.html"},
                    {"k": "KODE BUKU", "ic": "⌥", "v": "notebook resmi bab 3",
                     "href": BOOK["code_repo"] + "/blob/master/chapter03_introduction-to-ml-frameworks.ipynb"},
                ]},
            ],
        },
    ],
}
