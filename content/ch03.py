# -*- coding: utf-8 -*-
"""Chapter 3 — Introduction to TensorFlow, PyTorch, JAX, and Keras.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 3
(pp. 57-104), read from the book PDF.

The speed rankings in this chapter are the authors' assessment. They are
labelled as such on the slide rather than presented as a benchmark this course
ran.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_STACK = """
flowchart TB
  K["<b>Keras 3</b><br/>layers, models, losses,<br/>optimizers, metrics, training loops"]
  TF["<b>TensorFlow</b><br/>GradientTape<br/>@tf.function"]
  PT["<b>PyTorch</b><br/>.backward()<br/>torch.compile()"]
  JX["<b>JAX</b><br/>jax.grad()<br/>@jax.jit"]
  BASE["autodiff  ·  tensor compute on CPU / GPU / TPU  ·  distributed execution"]
  K --> TF
  K --> PT
  K --> JX
  TF --> BASE
  PT --> BASE
  JX --> BASE
"""

MMD_TIMELINE = """
flowchart LR
  A["1964<br/>first autodiff<br/>paper"]
  B["2006<br/>NVIDIA<br/>releases CUDA"]
  C["2009<br/>Theano<br/>autodiff + GPU"]
  D["2015<br/>Keras, then<br/>TensorFlow"]
  E["2016<br/>PyTorch"]
  F["2018<br/>JAX"]
  G["2023<br/>PyTorch 2.0<br/>Keras 3.0"]
  A --> B --> C --> D --> E --> F --> G
"""

MMD_GRADSTYLE = """
flowchart TB
  subgraph TF["TensorFlow — record then replay"]
    T1["open a GradientTape"] --> T2["run the forward pass"] --> T3["tape.gradient(loss, w)"]
  end
  subgraph PT["PyTorch — build then walk back"]
    P1["run the forward pass"] --> P2["loss.backward()"] --> P3["read w.grad"] --> P4["zero_grad()"]
  end
  subgraph JX["JAX — transform the function"]
    J1["write a pure loss function"] --> J2["jax.value_and_grad(fn)"] --> J3["call the new function"]
  end
"""

MMD_LAYERLIFE = """
flowchart LR
  A["Layer created<br/><code>SimpleDense(32)</code>"]
  B["First call with data<br/><code>layer(x)</code>"]
  C["build(input_shape)<br/><small>weights created now</small>"]
  D["call(inputs)<br/><small>the forward pass</small>"]
  E["Later calls<br/><small>build is skipped</small>"]
  A --> B --> C --> D
  D --> E --> D
"""


MMD_CHOOSE = """
flowchart TB
  Q1{"Must it run<br/>on-premise or on<br/>mobile / browser?"}
  Q2{"Does your team live<br/>on Hugging Face?"}
  Q3{"TPUs, or very<br/>large-scale training?"}
  TF["TensorFlow backend"]
  PT["PyTorch backend"]
  JX["JAX backend"]
  ANY["Any of them —<br/>write Keras and decide later"]
  Q1 -- yes --> TF
  Q1 -- no --> Q2
  Q2 -- yes --> PT
  Q2 -- no --> Q3
  Q3 -- yes --> JX
  Q3 -- no --> ANY
"""

MMD_VALSPLIT = """
flowchart LR
  ALL["All labelled data"] --> SH["Shuffle"]
  SH --> V["Validation<br/>30%"]
  SH --> T["Training<br/>70%"]
  T --> FIT["fit(...)"]
  V --> FIT
  FIT --> H["History<br/>per-epoch metrics"]
"""

NB = ["01_three_frameworks_side_by_side.ipynb", "02_keras3_switch_backend.ipynb",
      "03_custom_layer_and_fit.ipynb"]

DECK = {
    "id": "ch03",
    "kind": "chapter",
    "number": 3,
    "title": "Introduction to TensorFlow, PyTorch, JAX, and Keras",
    "subtitle": "The same Dense layer written four times — so the design differences "
                "between the frameworks are something you can see rather than "
                "something you are told.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 3",
    "source_url": chapter_url(3),
    "duration": "2.5 hours",
    "presenter": {"name": "Rahman Indra Kesuma, S.Kom., M.Cs.", "role": "Teaching Assistant"},
    "resources": chapter_resources(3, local_notebooks=NB),
    "objectives": [
        "Name the **three capabilities** every modern framework provides, and what "
        "distinguishes them beyond that.",
        "Compute gradients with **GradientTape, `.backward()`, and `jax.grad()`**, "
        "and explain why the three look so different.",
        "Distinguish **stateful imperative** (TF, PyTorch) from **stateless "
        "functional** (JAX), and say what that costs when writing a training loop.",
        "Switch the Keras 3 backend without changing a line of model code.",
        "Write a custom `Layer` with `build()` and `call()`, then drive it through "
        "`compile()` and `fit()`.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Section 3.1",
            "title": "How the field arrived here",
            "blocks": [
                {"t": "mmd", "id": "ch03-timeline", "src": MMD_TIMELINE,
                 "cap": "Automatic differentiation is from 1964. What was new in 2009 was "
                        "combining it with GPU computation."},
                {"t": "band",
                 "md": "One number worth keeping: by **mid-2016, more than half** of "
                       "TensorFlow's users reached it ==through Keras=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.1",
            "title": "Three capabilities every one of them has",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "∂", "h": "Automatic differentiation",
                     "p": "For any differentiable function you write, not just for a fixed "
                          "catalogue of layers.", "style": "accent"},
                    {"ico": "▦", "h": "Tensor computation",
                     "p": "On CPUs, GPUs, and specialised hardware such as TPUs.",
                     "style": "accent"},
                    {"ico": "⇄", "h": "Distributed execution",
                     "p": "Across devices and across machines.", "style": "accent"},
                ]},
                {"t": "band",
                 "md": "Because all of them provide all three, choosing a framework is "
                       "==not a question of capability==. It is a question of writing style, "
                       "ecosystem, and speed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.2",
            "title": "Keras on top, three engines underneath",
            "blocks": [
                {"t": "mmd", "id": "ch03-stack", "src": MMD_STACK,
                 "cap": "Keras needs a backend. NumPy can be plugged in but cannot train — "
                        "it has no gradient API."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.2",
            "title": "Where the line between them falls",
            "blocks": [
                {"t": "quote",
                 "md": "Keras is like a prefabricated building kit, while TensorFlow, "
                       "PyTorch, and JAX are like raw materials used in construction.",
                 "cite": "Chollet & Watson, section 3.2"},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**Low level** — tensors, tensor operations, and "
                                         "backpropagation."},
                    ],
                    [
                        {"t": "p", "md": "**High level** — layers combined into models, "
                                         "losses, optimizers, metrics, and training loops."},
                    ],
                ]},
            ],
        },

        {"type": "section", "num": "01", "title": "TensorFlow",
         "lead": "Immutable tensors, Variables for state, a tape for gradients."},

        {
            "type": "slide",
            "kicker": "Section 3.3",
            "title": "Constants are immutable; state needs a Variable",
            "blocks": [
                {"t": "p", "md": "This is the first thing that surprises people coming from "
                                 "NumPy: a TensorFlow tensor cannot be assigned into. "
                                 "Anything that has to change during training must be a "
                                 "`tf.Variable`."},
                {"t": "code", "lang": "python", "file": "tensors and variables",
                 "src": """import tensorflow as tf

tf.ones(shape=(2, 1))
tf.constant([1.0, 2.0])            # IMMUTABLE — cannot be assigned into

v = tf.Variable(initial_value=tf.random.normal(shape=(3, 1)))
v.assign(tf.ones((3, 1)))          # replace the whole value
v[0, 0].assign(3.0)                # replace part of it
v.assign_add(tf.ones((3, 1)))      # an efficient +="""},
                {"t": "band", "style": "amber",
                 "md": "Forgetting this produces a confusing error at the worst moment: "
                       "==your weights simply refuse to update=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.3",
            "title": "Operations, and one naming detail to notice",
            "blocks": [
                {"t": "p", "md": "The operation names mostly follow NumPy, with occasional "
                                 "divergences. Watch the keyword in the last line."},
                {"t": "code", "lang": "python", "file": "tensor operations",
                 "src": """a = tf.ones((2, 2))
b = tf.square(a)                   # element-wise
c = tf.sqrt(a)                     # element-wise
d = b + c                          # element-wise
e = tf.matmul(a, b)                # matrix product
f = tf.concat((a, b), axis=0)      # note: 'axis'

def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)"""},
                {"t": "p", "md": "That `axis` keyword becomes `dim` in PyTorch — a small "
                                 "difference that costs real time when porting code."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.3",
            "title": "GradientTape: record, then ask",
            "blocks": [
                {"t": "p", "md": "TensorFlow records the operations performed inside a tape's "
                                 "scope, then replays them backwards when you ask for a "
                                 "gradient."},
                {"t": "code", "lang": "python", "file": "gradients",
                 "src": """input_var = tf.Variable(3.0)
with tf.GradientTape() as tape:
    result = tf.square(input_var)
gradient = tape.gradient(result, input_var)

# A constant is not watched by default — say so explicitly:
c = tf.constant(3.0)
with tf.GradientTape() as tape:
    tape.watch(c)
    result = tf.square(c)
gradient = tape.gradient(result, c)"""},
                {"t": "band",
                 "md": "Variables are watched automatically because they are what you "
                       "normally differentiate. ==Constants must be opted in=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.3",
            "title": "Compilation: graph mode and XLA",
            "blocks": [
                {"t": "p", "md": "Decorating a function replaces it with a compiled program. "
                                 "The first call is slower; every call after that is faster."},
                {"t": "code", "lang": "python", "file": "two levels of compilation",
                 "src": """@tf.function
def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)

@tf.function(jit_compile=True)     # XLA: more aggressive, slower first compile
def dense(inputs, W, b):
    return tf.nn.relu(tf.matmul(inputs, W) + b)"""},
                {"t": "p", "md": "This is the same mechanism that later lets a model be "
                                 "**exported without Python** — chapter 6 uses it for "
                                 "deployment."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.3",
            "title": "TensorFlow: where it wins and where it hurts",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✔", "h": "Strengths",
                     "p": "Fast via graph mode and XLA · very feature-complete (string "
                          "tensors, ragged tensors) · outstanding `tf.data` for preprocessing "
                          "· **the most mature ecosystem for production, mobile, and "
                          "browser deployment**.", "style": "good"},
                    {"ico": "✖", "h": "Weaknesses",
                     "p": "A sprawling API with thousands of operations · inconsistent with "
                          "NumPy in places · less support on Hugging Face than PyTorch.",
                     "style": "bad"},
                ]},
                {"t": "p", "md": "For teams that must deploy on-premise, that production "
                                 "ecosystem is usually the argument that decides it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.3",
            "title": "A whole training step in TensorFlow",
            "blocks": [
                {"t": "p", "md": "Putting the pieces together: a compiled step function that "
                                 "runs the forward pass under a tape, reads the gradients, "
                                 "and updates two variables in place."},
                {"t": "code", "lang": "python", "file": "an end-to-end training step",
                 "src": """learning_rate = 0.1

@tf.function(jit_compile=True)
def training_step(inputs, targets, W, b):
    with tf.GradientTape() as tape:
        predictions = model(inputs, W, b)
        loss = mean_squared_error(predictions, targets)
    grad_wrt_W, grad_wrt_b = tape.gradient(loss, [W, b])
    W.assign_sub(grad_wrt_W * learning_rate)      # in-place: W is a Variable
    b.assign_sub(grad_wrt_b * learning_rate)
    return loss

for step in range(40):
    loss = training_step(inputs, targets, W, b)"""},
                {"t": "band",
                 "md": "`assign_sub` mutates the variable. Hold that image — ==the JAX "
                       "version of this same loop cannot mutate anything==, and the "
                       "difference is instructive."},
            ],
        },

        {"type": "section", "num": "02", "title": "PyTorch",
         "lead": "Mutable tensors, .backward() fills .grad, eager by default."},

        {
            "type": "slide",
            "kicker": "Section 3.4",
            "title": "Tensors you can assign into",
            "blocks": [
                {"t": "p", "md": "PyTorch takes the opposite decision from TensorFlow: its "
                                 "tensors behave like NumPy arrays and can be written to "
                                 "directly."},
                {"t": "code", "lang": "python", "file": "tensors and parameters",
                 "src": """import torch                      # the package is 'torch', not 'pytorch'

x = torch.zeros(size=(2, 1))
x[0, 0] = 1.0                       # ASSIGNABLE — unlike TensorFlow

p = torch.nn.parameter.Parameter(data=x)     # marks this as trained state

f = torch.cat((torch.ones((2, 2)), x), dim=0)   # note: 'dim', not 'axis'"""},
                {"t": "p", "md": "`Parameter` does not change the maths; it marks a tensor as "
                                 "something an optimizer should own."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.4",
            "title": "No tape — the graph is built as you go",
            "blocks": [
                {"t": "p", "md": "Each forward pass builds a one-time computation graph. "
                                 "Calling `.backward()` on a scalar walks it in reverse and "
                                 "fills in a `.grad` on every tensor involved."},
                {"t": "code", "lang": "python", "file": "gradients, and the trap",
                 "src": """input_var = torch.tensor(3.0, requires_grad=True)
result = torch.square(input_var)
result.backward()                   # populates input_var.grad
print(input_var.grad)

input_var.grad = None               # REQUIRED — gradients accumulate otherwise"""},
                {"t": "band", "style": "rose",
                 "md": "That last line is the classic PyTorch bug. The next `.backward()` "
                       "**adds** to the existing gradient rather than replacing it, so "
                       "==training silently stops working=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.4",
            "title": "The three-line incantation",
            "blocks": [
                {"t": "p", "md": "Model, loss, and optimizer are aware of each other, and a "
                                 "training step is always the same three calls in the same "
                                 "order."},
                {"t": "code", "lang": "python", "file": "the PyTorch training pattern",
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
    loss = mean_squared_error(targets, model(inputs))
    loss.backward()        # 1. compute gradients
    optimizer.step()       # 2. update the weights
    model.zero_grad()      # 3. clear, ready for the next batch
    return loss"""},
                {"t": "p", "md": "Learn those three lines in that order and most PyTorch code "
                                 "becomes readable."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.4",
            "title": "PyTorch: where it wins and where it hurts",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✔", "h": "Strengths",
                     "p": "Eager by default, which makes debugging the easiest of the three · "
                          "**first-class support on Hugging Face**, and that is the single "
                          "biggest driver of its adoption.", "style": "good"},
                    {"ico": "✖", "h": "Weaknesses",
                     "p": "Internally inconsistent API (`axis` sometimes becomes `dim`) · "
                          "in the authors' assessment **the slowest of the major "
                          "frameworks** · `torch.compile()` is still full of edge cases and "
                          "little used.", "style": "bad"},
                ]},
                {"t": "p", "md": "If your team already lives on Hugging Face, PyTorch will "
                                 "feel like home. That is a legitimate reason to choose it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.4",
            "title": "Compilation in PyTorch, and why it is rarely used",
            "blocks": [
                {"t": "p", "md": "PyTorch gained a compiler comparatively late. It can be "
                                 "applied to a model or used as a decorator."},
                {"t": "code", "lang": "python", "file": "torch.compile",
                 "src": """compiled_model = torch.compile(model)

@torch.compile
def dense(inputs, W, b):
    return torch.nn.relu(torch.matmul(inputs, W) + b)"""},
                {"t": "band", "style": "amber",
                 "md": "Unlike TensorFlow and JAX, **most PyTorch code runs eagerly, "
                       "uncompiled**. The book is blunt that the Dynamo compiler is still "
                       "full of edge cases and that ==only a small percentage of users "
                       "employ it=="},
            ],
        },

        {"type": "section", "num": "03", "title": "JAX",
         "lead": "Stateless functions. Gradients as a transformation of a function."},

        {
            "type": "slide",
            "kicker": "Section 3.5",
            "title": "Stateless — including the random numbers",
            "blocks": [
                {"t": "p", "md": "JAX functions keep no state between calls. State is passed "
                                 "in as arguments and returned as results — and that applies "
                                 "to the random number generator too."},
                {"t": "code", "lang": "python", "file": "arrays, keys, updates",
                 "src": """import jax
from jax import numpy as jnp

jnp.ones(shape=(2, 1))              # the NumPy API, with no divergence

seed_key = jax.random.key(123)
jax.random.normal(seed_key, shape=(3,))     # same key -> same value, always
key1, key2 = jax.random.split(seed_key)     # how you get a fresh key

x = jnp.array([1, 2, 3], dtype="float32")
new_x = x.at[0].set(10)             # arrays are immutable: you get a new one"""},
                {"t": "band",
                 "md": "It reads as extra work, and it is. What you buy is computation that "
                       "==parallelises automatically without synchronisation==, and results "
                       "that are exactly reproducible."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.5",
            "title": "jax.grad(): a function in, a function out",
            "blocks": [
                {"t": "p", "md": "JAX does not record operations. It **transforms your "
                                 "function** into a different function that computes "
                                 "gradients."},
                {"t": "code", "lang": "python", "file": "the transformation",
                 "src": """def compute_loss(state, inputs, targets):
    W, b = state
    predictions = jnp.matmul(inputs, W) + b
    return jnp.mean(jnp.square(targets - predictions))

grad_fn = jax.value_and_grad(compute_loss)      # function -> gradient function
loss, grads = grad_fn((W, b), inputs, targets)  # grads mirrors the shape of state"""},
                {"t": "table",
                 "head": ["What you need", "What you call"],
                 "widths": [42, 58],
                 "rows": [
                     ["Gradients only", "`jax.grad(f)`"],
                     ["Loss **and** gradients together", "`jax.value_and_grad(f)` — cheaper"],
                     ["Plus auxiliary outputs", "`jax.value_and_grad(f, has_aux=True)`"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.5",
            "title": "What a full training step looks like",
            "blocks": [
                {"t": "p", "md": "Because nothing mutates, the step function has to **return** "
                                 "the new weights. That single constraint shapes all JAX code."},
                {"t": "code", "lang": "python", "file": "a JAX training step",
                 "src": """@jax.jit
def training_step(inputs, targets, W, b):
    loss, grads = grad_fn((W, b), inputs, targets)
    grad_W, grad_b = grads
    W = W - grad_W * 0.1
    b = b - grad_b * 0.1
    return loss, W, b                # state comes back out

for step in range(40):
    loss, W, b = training_step(inputs, targets, W, b)"""},
                {"t": "band", "style": "amber",
                 "md": "Notice the loop: `W` and `b` are ==threaded through by hand==. Nothing "
                       "is updated in place, anywhere."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.5",
            "title": "JAX: where it wins and where it hurts",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "✔", "h": "Strengths",
                     "p": "In the authors' assessment **the fastest of the three** · perfect "
                          "NumPy API consistency, so no surprises · built for XLA and TPUs "
                          "from the beginning.", "style": "good"},
                    {"ico": "✖", "h": "Weaknesses",
                     "p": "Metaprogramming plus compilation makes debugging **markedly "
                          "harder** than eager execution · low-level training loops are more "
                          "verbose than TF or PyTorch.", "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Sections 3.3 – 3.5",
            "title": "The same job, three ways of asking for it",
            "blocks": [
                {"t": "mmd", "id": "ch03-gradstyle", "src": MMD_GRADSTYLE,
                 "cap": "The gradient is the same quantity in all three; what differs is who "
                        "holds the state while it is computed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Sections 3.3 – 3.5",
            "title": "Side by side",
            "blocks": [
                {"t": "table",
                 "head": ["", "TensorFlow", "PyTorch", "JAX"],
                 "widths": [17, 28, 28, 27],
                 "rows": [
                     ["**Paradigm**", "Stateful imperative", "Stateful imperative",
                      "Stateless functional"],
                     ["**Tensors**", "Immutable (`Variable` for state)", "Mutable",
                      "Immutable (`.at[].set()`)"],
                     ["**Gradients**", "`GradientTape`", "`.backward()` → `.grad`",
                      "`jax.grad()` transformation"],
                     ["**Compilation**", "`@tf.function`, XLA", "`@torch.compile` (Dynamo)",
                      "`@jax.jit` (XLA)"],
                     ["**Debugging**", "Harder in graph mode", "Easiest",
                      "Hardest (functional + JIT)"],
                     ["**Ecosystem**", "Production tooling", "Hugging Face, research",
                      "Research, Google scale"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Sections 3.3 – 3.5",
            "title": "About those speed claims",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "The book's ranking — JAX fastest, PyTorch slowest, a 20–30% spread "
                       "and up to 3–5× on large models — is the **authors' assessment**, "
                       "==not a benchmark this course ran=="},
                {"t": "p", "md": "Treat it as a direction to investigate, and measure it "
                                 "yourself on your own workload before it becomes a "
                                 "procurement argument."},
            ],
            "notes": "Do not let the room turn this into a framework war. The point is that "
                     "real design differences exist and Keras papers over them.",
        },

        {"type": "section", "num": "04", "title": "Keras",
         "lead": "One model definition, three engines behind it."},

        {
            "type": "slide",
            "kicker": "Section 3.6",
            "title": "Switching backend without touching the model",
            "blocks": [
                {"t": "p", "md": "The backend is a configuration choice, not a code change. "
                                 "There are two ways to make it."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "way 1 — environment variable",
                         "src": """import os
os.environ["KERAS_BACKEND"] = "jax"

import keras            # MUST come after
print(keras.backend.backend())"""},
                        {"t": "out", "src": "jax"},
                    ],
                    [
                        {"t": "code", "lang": "json", "file": "way 2 — ~/.keras/keras.json",
                         "src": """{
    "floatx": "float32",
    "epsilon": 1e-07,
    "backend": "tensorflow",
    "image_data_format": "channels_last"
}"""},
                    ],
                ]},
                {"t": "band", "style": "rose",
                 "md": "The ordering is not negotiable: `os.environ[...]` must run "
                       "==before the first `import keras`==. After Keras is imported, "
                       "changing it has no effect — and this is the number one confusion "
                       "in the lab sessions."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.1",
            "title": "Layer: the unit everything is built from",
            "blocks": [
                {"t": "p", "md": "Every Keras component either is a `Layer` or works closely "
                                 "with one. A custom layer needs two methods: `build()` "
                                 "creates the weights, `call()` does the work."},
                {"t": "code", "lang": "python", "file": "listing 3.22 — a custom Layer",
                 "src": """import keras

class SimpleDense(keras.Layer):
    def __init__(self, units, activation=None):
        super().__init__()
        self.units = units
        self.activation = activation

    def build(self, input_shape):          # called once, when the first input arrives
        batch_dim, input_dim = input_shape
        self.W = self.add_weight(shape=(input_dim, self.units),
                                 initializer="random_normal")
        self.b = self.add_weight(shape=(self.units,), initializer="zeros")

    def call(self, inputs):
        y = keras.ops.matmul(inputs, self.W) + self.b
        return self.activation(y) if self.activation is not None else y"""},
                {"t": "p", "md": "Note that `build()` receives the input shape. The layer does "
                                 "not need to be told it in advance."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.2",
            "title": "Automatic shape inference, and what it buys",
            "blocks": [
                {"t": "mmd", "id": "ch03-layerlife", "src": MMD_LAYERLIFE,
                 "cap": "Weights are created on the first call, not at construction time."},
                {"t": "p", "md": "This is why `Sequential` in chapter 2 only had to name the "
                                 "number of units. There was ==no `input_shape` anywhere==, "
                                 "and now you know why."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.2",
            "title": "Seeing it happen",
            "blocks": [
                {"t": "p", "md": "Instantiate the layer, call it on data, and read back the "
                                 "output shape it inferred."},
                {"t": "code", "lang": "python", "file": "using the custom layer",
                 "src": """my_dense = SimpleDense(units=32, activation=keras.ops.relu)

input_tensor = keras.ops.ones(shape=(2, 784))
output_tensor = my_dense(input_tensor)
print(output_tensor.shape)"""},
                {"t": "out", "src": "(2, 32)"},
                {"t": "p", "md": "The 784 was never written down. It was read off the data at "
                                 "the moment the layer was first used."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6",
            "title": "Which backend, in practice",
            "blocks": [
                {"t": "mmd", "id": "ch03-choose", "src": MMD_CHOOSE,
                 "cap": "A decision aid, not a law. The point of Keras is that this choice "
                        "stays reversible."},
                {"t": "p", "md": "The authors suggest **JAX** for best performance — but the "
                                 "same Keras code runs on all three, so the decision can be "
                                 "deferred and revisited."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.3",
            "title": "Models are graphs of layers — and a choice of hypothesis space",
            "blocks": [
                {"t": "quote",
                 "md": "The topology of a model defines a hypothesis space. By choosing a "
                       "network topology, you constrain your space of possibilities to a "
                       "specific series of tensor operations.",
                 "cite": "Chollet & Watson, section 3.6.3"},
                {"t": "p", "md": "That phrase — **hypothesis space** — is the one from chapter "
                                 "1. Choosing an architecture is choosing what the model is "
                                 "allowed to learn. Chapter 7 covers the three ways of "
                                 "expressing that choice."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.4",
            "title": "compile(): three decisions, spelled out",
            "blocks": [
                {"t": "p", "md": "The string shorthand is convenient, but the object form is "
                                 "what you need as soon as a learning rate has to be tuned."},
                {"t": "code", "lang": "python", "file": "listing 3.26 — two equivalent forms",
                 "src": """model.compile(
    optimizer="rmsprop",
    loss="mean_squared_error",
    metrics=["accuracy"],
)

model.compile(
    optimizer=keras.optimizers.RMSprop(learning_rate=1e-4),
    loss=keras.losses.MeanSquaredError(),
    metrics=[keras.metrics.BinaryAccuracy()],
)"""},
                {"t": "p", "md": "Built in and ready to use: **SGD, RMSprop, Adam**; losses "
                                 "including the crossentropies and MSE; metrics including "
                                 "accuracy, AUC, precision, and recall."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.5",
            "title": "fit(), and why validation data is not optional",
            "blocks": [
                {"t": "p", "md": "`fit()` runs the loop and returns a `History` object whose "
                                 "`.history` dictionary holds the per-epoch values of every "
                                 "metric — which is what you plot."},
                {"t": "code", "lang": "python", "file": "listing 3.29 — training with validation",
                 "src": """history = model.fit(
    training_inputs, training_targets,
    epochs=5, batch_size=16,
    validation_data=(val_inputs, val_targets),
)
print(history.history.keys())

loss_and_metrics = model.evaluate(val_inputs, val_targets, batch_size=128)
predictions = model.predict(new_inputs, batch_size=128)"""},
                {"t": "quote",
                 "md": "The goal of machine learning is not to obtain models that perform "
                       "well on the training data … it is to obtain models that perform well "
                       "in general, particularly on data points that the model has never "
                       "encountered before.",
                 "cite": "Chollet & Watson, section 3.6.5"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.5",
            "title": "Holding data back, by hand",
            "blocks": [
                {"t": "mmd", "id": "ch03-valsplit", "src": MMD_VALSPLIT,
                 "cap": "Shuffle first, then split. Splitting an ordered array is one of the "
                        "classic ways to get a meaningless validation score."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.5",
            "title": "…and what that looks like in code",
            "blocks": [
                {"t": "p", "md": "`fit()` can do this for you with `validation_split`, but "
                                 "doing it by hand once makes the shuffle step impossible "
                                 "to forget later."},
                {"t": "code", "lang": "python", "file": "listing 3.28 — a manual split",
                 "src": """indices_permutation = np.random.permutation(len(inputs))
shuffled_inputs = inputs[indices_permutation]
shuffled_targets = targets[indices_permutation]

num_validation_samples = int(0.3 * len(inputs))
val_inputs = shuffled_inputs[:num_validation_samples]
val_targets = shuffled_targets[:num_validation_samples]
training_inputs = shuffled_inputs[num_validation_samples:]
training_targets = shuffled_targets[num_validation_samples:]"""},
                {"t": "band",
                 "md": "Chapter 5 shows what goes wrong when the shuffle is skipped: you can "
                       "end up training on classes 0–7 and testing on 8–9, and ==the code "
                       "will not complain=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.6",
            "title": "Two ways to run inference, and when each is right",
            "blocks": [
                {"t": "p", "md": "Calling the model directly is fine for a small batch you "
                                 "already hold in memory. `predict()` is what you want for "
                                 "anything larger."},
                {"t": "code", "lang": "python", "file": "inference",
                 "src": """predictions = model(new_inputs)                          # all at once
predictions = model.predict(new_inputs, batch_size=128)  # batched, returns NumPy"""},
                {"t": "band",
                 "md": "`predict()` iterates in batches, so it ==will not exhaust memory== on "
                       "a large array, and it hands back NumPy rather than backend tensors."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.7",
            "title": "Why this stack is a safe thing to learn",
            "blocks": [
                {"t": "bullets", "items": [
                    "**Python has won** the ML and data science ecosystem; the authors see no "
                    "replacement within fifteen years.",
                    "All four frameworks are **stable**. New ones may appear, but are unlikely "
                    "to displace existing workflows.",
                    "New hardware — AMD GPUs and others — must integrate with the existing "
                    "frameworks, so it ==does not disrupt your code==.",
                ]},
                {"t": "band",
                 "md": "Which is the actual argument for Keras: it has provided **future-proof "
                       "stability since 2015**, and a pluggable backend is what lets it keep "
                       "doing so."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 3.6.4",
            "title": "Metrics are watched; loss is optimised",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "A **metric** is monitored but ==never optimised for==. Only the "
                       "**loss** is minimised. Confusing the two is an expensive mistake, "
                       "and chapters 5 and 6 return to exactly why."},
                {"t": "p", "md": "The short version: many of the things you actually care "
                                 "about — ROC AUC, for instance — cannot be used as a loss "
                                 "because they are not differentiable."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "Every major framework gives you **autodiff, GPU/TPU tensor computation, "
                    "and distributed execution**. The rest is style.",
                    "**TensorFlow** — immutable tensors plus `Variable`, `GradientTape`, and "
                    "the strongest production ecosystem.",
                    "**PyTorch** — mutable tensors, `.backward()`, eager, king of Hugging "
                    "Face. Never forget `zero_grad()`.",
                    "**JAX** — stateless functional, `jax.grad()` as a transformation, "
                    "explicit random keys, fastest by the authors' account.",
                    "**Keras 3** sits on all three. Set `KERAS_BACKEND` ==before== "
                    "`import keras`.",
                    "A `Layer` with `build()` + `call()` is the unit everything is made of, "
                    "and input shapes are inferred on first use.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "01_three_frameworks_side_by_side.ipynb",
                     "href": "../../course-slides/notebooks/ch03/01_three_frameworks_side_by_side.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 4 — Classification and regression",
                     "href": "../ch04/index.html"},
                ]},
            ],
        },
    ],
}
