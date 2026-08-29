# -*- coding: utf-8 -*-
"""Chapter 5 — Fundamentals of machine learning.

Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed., chapter 5
(pp. 136-170), read from the book PDF.

This is the chapter that turns "the model runs" into "the model may be given to
other people". Section 5.2.3 -- temporal leaks and duplicate samples -- is the
one that most often saves a project from failing quietly.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import BOOK, chapter_resources, chapter_url  # noqa: E402


MMD_TENSION = """
flowchart LR
  O["<b>Optimisation</b><br/>fit the training data<br/>as well as possible"]
  G["<b>Generalisation</b><br/>perform on data<br/>never seen before"]
  M["The model"]
  O -- "you control this" --> M
  G -. "you do NOT control this" .-> M
"""

MMD_SPLITS = """
flowchart LR
  ALL["All labelled data"]
  TR["Training set<br/><small>the model is fitted here</small>"]
  VA["Validation set<br/><small>hyperparameters tuned here</small>"]
  TE["Test set<br/><small>touched once, at the end</small>"]
  ALL --> TR
  ALL --> VA
  ALL --> TE
  VA -. "information leaks<br/>a little each time" .-> TR
"""

MMD_PROTOCOLS = """
flowchart TB
  Q{"How much data<br/>do you have?"}
  H["Hold-out validation<br/><small>1 model</small>"]
  K["K-fold validation<br/><small>K models</small>"]
  I["Iterated K-fold<br/>with shuffling<br/><small>P x K models</small>"]
  Q -- "plenty" --> H
  Q -- "not much" --> K
  Q -- "very little, and<br/>precision matters" --> I
"""

MMD_DIAGNOSE = """
flowchart TB
  S1{"Does the training<br/>loss go down?"}
  F1["Tune the learning rate<br/>and the batch size"]
  S2{"Can you beat the<br/>common-sense baseline?"}
  F2["Wrong architecture priors,<br/>or the data does not<br/>contain the answer"]
  S3{"Can you make<br/>it overfit?"}
  F3["Not enough capacity:<br/>more layers, wider layers"]
  F4["Now switch to<br/>maximising generalisation"]
  S1 -- no --> F1
  S1 -- yes --> S2
  S2 -- no --> F2
  S2 -- yes --> S3
  S3 -- no --> F3
  S3 -- yes --> F4
"""

MMD_REGULARISE = """
flowchart LR
  A["More or<br/>better data"] --> B["Better<br/>features"]
  B --> C["Early<br/>stopping"]
  C --> D["Reduce<br/>capacity"]
  D --> E["L1 / L2 weight<br/>regularisation"]
  E --> F["Dropout"]
"""

MMD_DROPOUT = """
flowchart LR
  A["Layer output<br/><code>[0.2, 0.5, 1.3, 0.8, 1.1]</code>"]
  B["Drop 50% at random<br/><code>[0, 0.5, 1.3, 0, 1.1]</code>"]
  C["Scale up by 1/(1-rate)<br/>during training"]
  D["At test time:<br/>nothing dropped,<br/>nothing rescaled"]
  A --> B --> C --> D
"""

FIG_CANON = "figs/book/figure-5-1.png"


NB = ["01_spurious_correlations.ipynb", "02_shuffled_labels_and_manifolds.ipynb",
      "03_evaluation_protocols.ipynb", "04_model_capacity.ipynb",
      "05_regularisation_l2_dropout.ipynb"]

DECK = {
    "id": "ch05",
    "kind": "chapter",
    "number": 5,
    "title": "Fundamentals of Machine Learning",
    "subtitle": "The tension between optimisation and generalisation — why it is "
                "unavoidable, how to measure it, and which remedies actually help.",
    "source": "Chollet & Watson, Deep Learning with Python 3e — chapter 5",
    "source_url": chapter_url(5),
    "duration": "3 hours (2 sessions)",
    "presenter": {"name": "Prof. Bambang Riyanto Trilaksono", "role": "Lead Instructor"},
    "resources": chapter_resources(5, local_notebooks=NB),
    "objectives": [
        "State the **optimisation vs generalisation** tension, and name the three "
        "causes of overfitting: noisy data, ambiguous features, and rare features.",
        "Explain the **manifold hypothesis**, and why generalisation in deep "
        "learning is *interpolation* rather than reasoning.",
        "Choose an evaluation protocol — **hold-out, K-fold, iterated K-fold** — "
        "and avoid the three pitfalls that invalidate it.",
        "Set a **common-sense baseline** before training anything.",
        "Diagnose the three training failures: **won't start, won't generalise, "
        "won't overfit** — and apply the right remedy to each.",
        "Apply **dataset curation, feature engineering, early stopping, capacity "
        "reduction, weight regularisation, and dropout**, and know when each fits.",
    ],
    "slides": [
        {"type": "title"},

        {
            "type": "slide",
            "kicker": "Roadmap",
            "title": "From \"it runs\" to \"it may be released\"",
            "blocks": [
                {"t": "lead", "md": "Chapter 4 introduced overfitting as an event. Chapter 5 "
                                    "turns it into ==a way of thinking==, and nearly every "
                                    "best practice in the rest of the book manages the same "
                                    "single tension."},
                {"t": "cards", "cols": 4, "items": [
                    {"ico": "🎯", "h": "5.1 · Generalisation",
                     "p": "What causes overfitting, and why deep learning generalises at all.",
                     "style": "accent"},
                    {"ico": "📐", "h": "5.2 · Evaluation",
                     "p": "Three protocols, a common-sense baseline, and three pitfalls.",
                     "style": "accent"},
                    {"ico": "🔧", "h": "5.3 · Improving fit",
                     "p": "Three training failures and their remedies. The goal: be **able** "
                          "to overfit.", "style": "accent"},
                    {"ico": "🛡", "h": "5.4 · Improving generalisation",
                     "p": "Curation, features, early stopping, and three kinds of "
                          "regularisation.", "style": "accent"},
                ]},
            ],
        },

        {"type": "section", "num": "01", "title": "Generalisation: the goal",
         "lead": "Why overfitting happens in every problem, without exception."},

        {
            "type": "slide",
            "kicker": "Section 5.1",
            "title": "The one tension everything else serves",
            "blocks": [
                {"t": "mmd", "id": "ch05-tension", "src": MMD_TENSION,
                 "cap": "You can only act on one side of this picture."},
                {"t": "quote",
                 "md": "The goal of the game is to get good generalisation, of course, but "
                       "you don't control generalisation; you can only fit the model to its "
                       "training data. If you do that too well, overfitting kicks in and "
                       "generalisation suffers.",
                 "cite": "Chollet & Watson, section 5.1"},
            ],
            "notes": "The key phrase is 'you don't control generalisation'. Every technique "
                     "in this chapter is indirect — none of them adjusts it straight.",
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.1",
            "title": "The canonical curve — and it is universal",
            "blocks": [
                {"t": "img", "src": FIG_CANON, "credit": True, "max_h": "38vh",
                 "cap": "Figure 5.1 — the same shape appears with every model type and every "
                        "dataset."},
                {"t": "bullets", "items": [
                    "**Underfit** — progress still available; the network has not yet modelled "
                    "the relevant patterns.",
                    "**Robust fit** — the best point. Narrow, and visible only through "
                    "validation metrics.",
                    "**Overfit** — the model starts learning patterns ==specific to the "
                    "training data== that mislead on new data.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.1",
            "title": "Cause 1 — noisy training data",
            "blocks": [
                {"t": "p", "md": "Real datasets contain invalid inputs — an all-black MNIST "
                                 "image, for instance. Worse, they contain perfectly valid "
                                 "inputs that are **mislabelled**."},
                {"t": "band", "style": "warn",
                 "md": "A model that goes out of its way to accommodate those outliers gets "
                       "worse on everything near them: a 4 resembling a mislabelled 4 "
                       "==ends up classified as a 9=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.1",
            "title": "Cause 2 — ambiguous features",
            "blocks": [
                {"t": "p", "md": "Not all noise comes from mistakes. Perfectly clean, "
                                 "correctly labelled data can still be noisy when the problem "
                                 "itself involves uncertainty."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**No objective boundary.** Is this banana unripe, "
                                         "ripe, or rotten? Different human labellers "
                                         "disagree on the same photograph."},
                    ],
                    [
                        {"t": "p", "md": "**Genuine randomness.** The same atmospheric "
                                         "pressure reading is sometimes followed by rain and "
                                         "sometimes by clear sky."},
                    ],
                ]},
                {"t": "band",
                 "md": "A model overfits such data by being **too confident** in the "
                       "ambiguous region. A robust fit ==ignores individual points and looks "
                       "at the bigger picture=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.1",
            "title": "Cause 3 — rare features and spurious correlations",
            "blocks": [
                {"t": "p", "md": "If you had only ever met two orange tabby cats and both were "
                                 "antisocial, you might conclude orange tabbies are "
                                 "antisocial. That is overfitting, in one sentence."},
                {"t": "p", "md": "The machine version: the word *cherimoya* appears in exactly "
                                 "one training review, which happens to be negative. A poorly "
                                 "regularised model gives it enormous weight and thereafter "
                                 "==condemns every text that mentions the fruit=="},
                {"t": "band", "style": "rose",
                 "md": "And it need not be that rare. A word appearing in **100** samples, "
                       "positive **54%** of the time, may be pure statistical fluke — and the "
                       "model will use it anyway. Chollet calls this **one of the most common "
                       "sources of overfitting**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.1 · listing 5.1",
            "title": "Proving it: add pure noise, lose accuracy",
            "blocks": [
                {"t": "p", "md": "Take MNIST and glue on 784 channels of white noise. Then "
                                 "build a second copy with 784 channels of zeros. **The "
                                 "information content is identical in both.**"},
                {"t": "code", "lang": "python", "file": "listing 5.1 — two comparison sets",
                 "src": """(train_images, train_labels), _ = mnist.load_data()
train_images = train_images.reshape((60000, 28 * 28)).astype("float32") / 255

train_images_with_noise_channels = np.concatenate(
    [train_images, np.random.random((len(train_images), 784))], axis=1)

train_images_with_zeros_channels = np.concatenate(
    [train_images, np.zeros((len(train_images), 784))], axis=1)"""},
                {"t": "p", "md": "A human classifier would be entirely unaffected by either "
                                 "transformation."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.1 · listing 5.2",
            "title": "…and the model is not unaffected",
            "blocks": [
                {"t": "p", "md": "Train the same architecture on both and compare validation "
                                 "accuracy epoch by epoch."},
                {"t": "code", "lang": "python", "file": "listing 5.2 — same model, two datasets",
                 "src": """model = get_model()
history_noise = model.fit(train_images_with_noise_channels, train_labels,
                          epochs=10, batch_size=128, validation_split=0.2)

model = get_model()
history_zeros = model.fit(train_images_with_zeros_channels, train_labels,
                          epochs=10, batch_size=128, validation_split=0.2)"""},
                {"t": "stats", "cols": 1, "items": [
                    {"v": "−1 point", "l": "validation accuracy, purely from spurious correlations"},
                ]},
                {"t": "band",
                 "md": "One percentage point, from information carrying **no signal at all**. "
                       "Add more noise channels and it degrades further. Hence **feature "
                       "selection**: score each feature's usefulness — mutual information "
                       "with the labels, say — and ==keep only what clears a threshold=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.2 · listing 5.4",
            "title": "A model will fit absolutely anything",
            "blocks": [
                {"t": "p", "md": "Shuffle the MNIST labels so that no relationship remains "
                                 "between images and targets, then train for 100 epochs."},
                {"t": "code", "lang": "python", "file": "listing 5.4 — randomly shuffled labels",
                 "src": """random_train_labels = train_labels[:]        # copy
np.random.shuffle(random_train_labels)       # destroy every input-target relation

model.fit(train_images, random_train_labels,
          epochs=100, batch_size=128, validation_split=0.2)"""},
                {"t": "out", "src": """training loss      : falls steadily, smoothly
validation accuracy: stuck at ~10%  (= the random baseline for 10 classes)"""},
                {"t": "band", "style": "amber",
                 "md": "The training loss falls even though **nothing is learnable**. The "
                       "model is ==memorising, like a Python dictionary==. So the ability to "
                       "fit is no evidence that the problem is solvable."},
            ],
            "notes": "The most useful diagnostic in the chapter: training loss falling while "
                     "validation sits at the baseline means the data does not contain the "
                     "answer — it is not a modelling problem.",
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.2",
            "title": "So why does it generalise at all?",
            "blocks": [
                {"t": "p", "md": "If a network can memorise noise, why does it ever work on "
                                 "new inputs? Chollet's answer is that the reason has "
                                 "**little to do with the model** and much to do with the "
                                 "structure of information in the real world."},
                {"t": "band",
                 "md": "MNIST inputs are 28×28 arrays of bytes, so there are **256⁷⁸⁴** "
                       "possible inputs — ==more than there are atoms in the universe==. "
                       "Almost none of them look like handwriting."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.2",
            "title": "The manifold hypothesis",
            "blocks": [
                {"t": "quote",
                 "md": "The manifold hypothesis posits that all natural data lies on a "
                       "low-dimensional manifold within the high-dimensional space where it "
                       "is encoded.",
                 "cite": "Chollet & Watson, section 5.1.2"},
                {"t": "bullets", "items": [
                    "A **manifold** is a lower-dimensional subspace that is locally similar "
                    "to a linear space — a smooth curve is a 1D manifold inside a 2D plane.",
                    "The subspace of valid digits is **continuous**: perturb a sample slightly "
                    "and it is still the same digit.",
                    "Any two digits are joined by a **smooth path** of intermediate images "
                    "that all still look like digits.",
                    "It holds for handwriting, human faces, tree morphology, the human voice, "
                    "and ==even natural language==.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.2",
            "title": "Interpolation, and what it is not",
            "blocks": [
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**What the model can do**"},
                        {"t": "bullets", "items": [
                            "Make sense of an unseen point by relating it to nearby points on "
                            "the manifold.",
                            "Understand the whole space from a sample of it — *filling in "
                            "the blanks*.",
                            "Chollet calls this **local generalisation**.",
                        ]},
                    ],
                    [
                        {"t": "p", "md": "**What it cannot**"},
                        {"t": "bullets", "items": [
                            "**Extreme generalisation**, which humans do constantly.",
                            "You can spend a week in New York, a week in Shanghai, and a week "
                            "in Bangalore ==without thousands of lifetimes of rehearsal==.",
                            "That rests on abstraction, symbolic models, reasoning, and innate "
                            "priors — what we call **reason**, not intuition.",
                        ]},
                    ],
                ]},
                {"t": "band",
                 "md": "Interpolation is only ==the tip of the iceberg==. Treating it as the "
                       "whole of generalisation is a mistake; chapter 19 returns to this."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.2",
            "title": "And it is not linear interpolation either",
            "blocks": [
                {"t": "p", "md": "Interpolating **on the latent manifold** is a different "
                                 "operation from averaging in the encoding space."},
                {"t": "band", "style": "amber",
                 "md": "The pixel-wise average of two MNIST digits ==is usually not a valid "
                       "digit at all==. Every point on the latent manifold is; the straight "
                       "line between two points in pixel space is not."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.2",
            "title": "Why deep learning is suited to this",
            "blocks": [
                {"t": "p", "md": "A deep model is a very high-dimensional curve, fitted to "
                                 "data points by gradient descent — smoothly and incrementally."},
                {"t": "steps", "items": [
                    "The curve has enough parameters to fit **anything**; trained long enough "
                    "it simply memorises.",
                    "But the data is **not** scattered points — it forms a structured, "
                    "low-dimensional manifold.",
                    "Because the fitting happens ==gradually and smoothly==, there is an "
                    "intermediate moment when the model curve approximates the data's own "
                    "manifold. That is the robust fit.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.2",
            "title": "Two properties that make it work",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "〰", "h": "A smooth, continuous mapping",
                     "p": "Required, because the model must be differentiable — and that "
                          "smoothness is exactly what helps it approximate a manifold, which "
                          "has the same property.", "style": "good"},
                    {"ico": "🏗", "h": "Architecture priors",
                     "p": "Models are structured to mirror the *shape* of the information in "
                          "their data — especially image models (ch. 8–12) and sequence "
                          "models (ch. 13).", "style": "good"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.3",
            "title": "Training data is paramount",
            "blocks": [
                {"t": "quote",
                 "md": "The only thing you will find in a deep learning model is what you put "
                       "into it: the priors encoded in its architecture and the data it was "
                       "trained on.",
                 "cite": "Chollet & Watson, section 5.1.3"},
                {"t": "bullets", "items": [
                    "The power to generalise is more a consequence of **your data's natural "
                    "structure** than of any property of your model.",
                    "Curve fitting needs a **dense sampling** of the input space — especially "
                    "near decision boundaries.",
                    "Sparse sampling → the learned curve does not match the latent space, and "
                    "==interpolation goes wrong==.",
                ]},
                {"t": "band",
                 "md": "Hence the single most effective move available to you: "
                       "**train on more data, or on better data.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.1.3",
            "title": "When more data is not an option",
            "blocks": [
                {"t": "p", "md": "The next best thing is to **limit how much information the "
                                 "model is allowed to store**, or to constrain the smoothness "
                                 "of its curve."},
                {"t": "band",
                 "md": "If a network can only afford to memorise a few patterns, or only very "
                       "regular ones, optimisation ==forces it towards the most prominent "
                       "patterns== — the ones with a better chance of generalising."},
                {"t": "p", "md": "Fighting overfitting this way is called **regularisation**, "
                                 "and section 5.4.4 covers it in full."},
            ],
        },

        {"type": "section", "num": "02", "title": "Evaluating machine learning models",
         "lead": "You can only control what you can observe."},

        {
            "type": "slide",
            "kicker": "Section 5.2.1",
            "title": "Why two sets are not enough",
            "blocks": [
                {"t": "mmd", "id": "ch05-splits", "src": MMD_SPLITS,
                 "cap": "Tuning on the validation set is itself a form of learning — and it "
                        "leaks."},
                {"t": "p", "md": "**Hyperparameters** (layer count, layer size) are what you "
                                 "tune; **parameters** (the weights) are what the model "
                                 "learns. Tuning is a search, and searches can overfit."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.1",
            "title": "Information leaks, one bit at a time",
            "blocks": [
                {"t": "p", "md": "Every time you adjust a hyperparameter based on validation "
                                 "performance, some information about the validation data "
                                 "passes into the model."},
                {"t": "bullets", "items": [
                    "Do it **once**, for one parameter: a few bits leak, and the set stays "
                    "trustworthy.",
                    "Do it **many times** — run, evaluate, adjust, repeat — and an "
                    "increasingly significant amount leaks.",
                    "You end up with a model that does artificially well on validation, "
                    "==because that is what you optimised it for==.",
                ]},
                {"t": "band", "style": "rose",
                 "md": "Hence the third set. The model must have had **no access to any "
                       "information about the test set, even indirectly**. If anything at all "
                       "was tuned on test performance, your measure of generalisation is "
                       "already flawed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.1",
            "title": "Three evaluation protocols",
            "blocks": [
                {"t": "mmd", "id": "ch05-protocols", "src": MMD_PROTOCOLS,
                 "cap": "Pick one. In most cases the first is good enough."},
                {"t": "p", "md": "The tell that hold-out has failed you: **different random "
                                 "shuffles before splitting give very different scores**. "
                                 "That is the signal to move to K-fold."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.1 · listing 5.6",
            "title": "K-fold, and the line people get wrong",
            "blocks": [
                {"t": "p", "md": "The mechanics are simple; the one thing that must not slip "
                                 "is the model construction inside the loop."},
                {"t": "code", "lang": "python", "file": "listing 5.6 — K-fold cross-validation",
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

    model = get_model()            # a BRAND-NEW, untrained model every fold
    model.fit(training_data, ...)
    validation_scores.append(model.evaluate(validation_data, ...))

validation_score = np.average(validation_scores)"""},
                {"t": "band",
                 "md": "Reusing an already-trained model across folds carries knowledge "
                       "between them and ==invalidates the entire estimate=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.1",
            "title": "And then the final model",
            "blocks": [
                {"t": "p", "md": "K-fold gives you an *estimate*, not a model to ship. Once "
                                 "you trust the estimate, train once more on everything that "
                                 "is not test data."},
                {"t": "code", "lang": "python", "file": "after the folds",
                 "src": """model = get_model()
model.fit(data, ...)                          # all non-test data
test_score = model.evaluate(test_data, ...)   # touched once, here"""},
                {"t": "p", "md": "**Iterated K-fold with shuffling** repeats the whole "
                                 "procedure P times with a fresh shuffle each time. It trains "
                                 "P × K models — expensive, and the book notes it is "
                                 "especially useful in Kaggle competitions."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.2",
            "title": "The altimeter on an invisible rocket",
            "blocks": [
                {"t": "quote",
                 "md": "Training a deep learning model is a bit like pressing a button that "
                       "launches a rocket in a parallel world. You can't hear it or see it … "
                       "The only feedback you have is your validation metrics — like an "
                       "altitude meter on your invisible rocket.",
                 "cite": "Chollet & Watson, section 5.2.2"},
                {"t": "p", "md": "Which raises the question the next slide answers: "
                                 "**what altitude did you start at?**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.2",
            "title": "Set the baseline before you train anything",
            "blocks": [
                {"t": "table",
                 "head": ["Problem", "Common-sense baseline", "Why"],
                 "widths": [24, 22, 54],
                 "rows": [
                     ["MNIST", "**> 0.10**", "A random classifier over 10 balanced classes."],
                     ["IMDB", "**> 0.50**", "Two classes, balanced 50:50."],
                     ["Reuters", "**≈ 0.18–0.19**", "46 classes, but very unevenly distributed."],
                     ["Binary, 90:10 split", "**> 0.90**",
                      "A classifier that always answers A already scores 0.90. You must beat "
                      "that."],
                 ]},
                {"t": "band", "style": "rose",
                 "md": "If you **cannot beat a trivial solution, your model is worthless**. "
                       "Either the model is wrong, or — and this happens — ==the problem "
                       "cannot be approached with machine learning at all=="},
            ],
            "notes": "This slide saves more budget than any other. Have people write down the "
                     "baseline for their own case before training anything.",
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.3",
            "title": "Three pitfalls that invalidate an evaluation",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🎲", "h": "1 · Data representativeness",
                     "p": "Samples ordered by class, then the first 80% taken as training: you "
                          "train on classes 0–7 and test on 8–9. *A ridiculous mistake, and "
                          "surprisingly common.* **Shuffle before splitting.**",
                     "style": "warn"},
                    {"ico": "⏳", "h": "2 · The arrow of time",
                     "p": "Predicting the future from the past? **Do not shuffle.** It creates "
                          "a ==temporal leak==: the model trains on data from the future. All "
                          "test data must be later than all training data.", "style": "bad"},
                    {"ico": "👯", "h": "3 · Redundancy",
                     "p": "Duplicate points are common in real data. Shuffle and split, and "
                          "copies land in both training and validation — you are testing on "
                          "your training data. **The worst thing you can do.**", "style": "bad"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.2.3",
            "title": "Why transactional data hits two of them at once",
            "blocks": [
                {"t": "band", "style": "amber",
                 "md": "Sequences of events are **temporal**, and the same subject recurs "
                       "across many rows. Splitting randomly by row ==violates pitfalls 2 and "
                       "3 in a single step=="},
                {"t": "p", "md": "The fix is to split by **time** and by **subject**, not by "
                                 "row — and to state which you did when you report a score."},
            ],
        },

        {"type": "section", "num": "03", "title": "Improving model fit",
         "lead": "To reach the perfect fit, you must first overfit."},

        {
            "type": "slide",
            "kicker": "Section 5.3",
            "title": "Diagnose before you treat",
            "blocks": [
                {"t": "mmd", "id": "ch05-diagnose", "src": MMD_DIAGNOSE,
                 "cap": "Three questions, asked in order. Each failure has a different remedy."},
                {"t": "quote",
                 "md": "To achieve the perfect fit, you must first overfit. Since you don't "
                       "know in advance where the boundary lies, you must cross it to find it.",
                 "cite": "Chollet & Watson, section 5.3"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.3.1 · listing 5.7–5.8",
            "title": "Failure 1 — training never starts",
            "blocks": [
                {"t": "p", "md": "When the loss is stuck, it is always a gradient-descent "
                                 "configuration problem. Here is the same MNIST model at an "
                                 "absurd learning rate, and at a sane one."},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "code", "lang": "python", "file": "listing 5.7 — too high",
                         "src": """model.compile(
    optimizer=keras.optimizers.RMSprop(
        learning_rate=1.0),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])"""},
                        {"t": "out", "src": "accuracy stalls at 20%-40%"},
                    ],
                    [
                        {"t": "code", "lang": "python", "file": "listing 5.8 — reasonable",
                         "src": """model.compile(
    optimizer=keras.optimizers.RMSprop(
        learning_rate=1e-2),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])"""},
                        {"t": "out", "src": "the model now trains"},
                    ],
                ]},
                {"t": "band",
                 "md": "All these parameters interact, so the advice is narrow: **tune the "
                       "learning rate and the batch size, and hold the rest constant.** A "
                       "bigger batch gives ==less noisy, more informative gradients=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.3.2",
            "title": "Failure 2 — it trains but does not generalise",
            "blocks": [
                {"t": "band", "style": "rose",
                 "md": "The book calls this **the worst situation you can find yourself in**: "
                       "it signals something fundamentally wrong, and ==it is often not easy "
                       "to tell what=="},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🕳", "h": "The data may not contain the answer",
                     "p": "Exactly what happened with the shuffled MNIST labels: it trains "
                          "fine, and validation sits at 10% forever.", "style": "bad"},
                    {"ico": "🏛", "h": "The architecture priors may be wrong",
                     "p": "Chapter 13 shows a timeseries problem where a densely connected "
                          "model cannot beat a trivial baseline and a recurrent one "
                          "generalises well.", "style": "warn"},
                ]},
                {"t": "p", "md": "Practical advice: **read up on architecture best practices "
                                 "for your kind of task** — you are almost certainly not the "
                                 "first to attempt it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.3.3 · listing 5.9",
            "title": "Failure 3 — it cannot be made to overfit",
            "blocks": [
                {"t": "p", "md": "If validation loss flattens and never reverses, the model "
                                 "lacks the representational power to model the problem. "
                                 "Here is that failure, deliberately built."},
                {"t": "code", "lang": "python", "file": "listing 5.9 — insufficient capacity",
                 "src": """model = keras.Sequential([layers.Dense(10, activation="softmax")])
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
history_small = model.fit(train_images, train_labels,
                          epochs=20, batch_size=128, validation_split=0.2)"""},
                {"t": "out", "src": "validation loss falls to 0.26 and simply stays there"},
                {"t": "band",
                 "md": "You can fit, but you cannot clearly overfit — even after many passes. "
                       "==It should always be possible to overfit==, so this points at "
                       "capacity."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.3.3",
            "title": "Too little, right, and too much",
            "blocks": [
                {"t": "table",
                 "head": ["Model", "Architecture", "What happens", "Figure"],
                 "widths": [20, 26, 42, 12],
                 "rows": [
                     ["**Under-capacity**", "`Dense(10, softmax)` alone",
                      "Validation loss reaches 0.26 and stops. Fits, but ==cannot clearly "
                      "overfit==.", "5.14"],
                     ["**Right capacity**", "2 × `Dense(128, relu)`",
                      "Fits fast, starts overfitting **after eight epochs**. Exactly the "
                      "shape you want.", "5.15"],
                     ["**Over-capacity**", "3 × `Dense(2048, relu)`",
                      "Overfits **immediately**; training loss near zero very quickly, "
                      "validation loss noisy.", "5.16"],
                 ]},
                {"t": "band",
                 "md": "The workflow: **start with few layers and parameters, and grow until "
                       "validation loss stops improving.** There is no formula for the right "
                       "size — it is found on the validation set, ==never on the test set=="},
            ],
        },

        {"type": "section", "num": "04", "title": "Improving generalisation",
         "lead": "Five moves, in order of how much they are worth."},

        {
            "type": "slide",
            "kicker": "Section 5.4",
            "title": "The order to try things in",
            "blocks": [
                {"t": "mmd", "id": "ch05-regularise", "src": MMD_REGULARISE,
                 "cap": "Left to right, cheapest and most effective first."},
                {"t": "p", "md": "Every one of these is downstream of the same idea: make the "
                                 "model's curve smoother, or make interpolation easier."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.1",
            "title": "Dataset curation pays the most, and gets skipped the most",
            "blocks": [
                {"t": "quote",
                 "md": "Deep learning is curve fitting, not magic.",
                 "cite": "Chollet & Watson, section 5.4.1"},
                {"t": "steps", "items": [
                    "**Make sure you have enough data.** You need a dense sampling of the "
                    "input-cross-output space. Problems that look impossible sometimes become "
                    "solvable with a larger dataset.",
                    "**Minimise labelling errors.** Look at your inputs for anomalies; "
                    "proofread the labels.",
                    "**Clean the data and handle missing values.** Chapter 6 covers how.",
                    "**Do feature selection** if you have many features and are unsure which "
                    "are useful.",
                ]},
                {"t": "band", "style": "amber",
                 "md": "And know the limit: if the problem is **overly noisy or fundamentally "
                       "discrete** — sorting a list, say — deep learning ==will not help you==, "
                       "at any data volume."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.2",
            "title": "Feature engineering: the clock face",
            "blocks": [
                {"t": "table",
                 "head": ["Level", "What goes in", "What it takes to solve"],
                 "widths": [24, 36, 40],
                 "rows": [
                     ["**Raw data**", "The pixel grid of a clock",
                      "A convolutional network, and considerable compute."],
                     ["**Better features**", "(x, y) coordinates of each hand's tip",
                      "A simple machine learning algorithm suffices."],
                     ["**Better still**", "The angle θ of each hand (polar coordinates)",
                      "==No machine learning at all== — rounding and a dictionary lookup."],
                 ]},
                {"t": "band",
                 "md": "That is the essence of it: **making a problem easier by expressing it "
                       "more simply**. Make the latent manifold smoother and better organised. "
                       "It requires understanding the problem deeply."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.2",
            "title": "Deep learning removed the need — but not entirely",
            "blocks": [
                {"t": "p", "md": "Before deep learning this was **the** most important part of "
                                 "the workflow. MNIST solutions were built from hand-coded "
                                 "features: the number of closed loops in a digit, its height, "
                                 "histograms of pixel values."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🪶", "h": "Still worth it — reason 1",
                     "p": "Good features solve problems **with fewer resources**. Using a "
                          "ConvNet to read a clock face would be absurd.", "style": "good"},
                    {"ico": "📉", "h": "Still worth it — reason 2",
                     "p": "Good features solve problems **with far less data**. A model's "
                          "ability to find its own features depends on having a lot of it.",
                     "style": "good"},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.3",
            "title": "Early stopping",
            "blocks": [
                {"t": "p", "md": "Deep models are always **vastly overparameterised** — far "
                                 "more degrees of freedom than the minimum needed. That is not "
                                 "a problem, because ==you never fit one all the way=="},
                {"t": "cols", "ratio": "1-1", "cols": [
                    [
                        {"t": "p", "md": "**The chapter-4 way** — train longer than needed to "
                                         "find the best epoch, then train a fresh model for "
                                         "exactly that many."},
                        {"t": "band", "style": "amber",
                         "md": "Standard, but it means ==doing the work twice=="},
                    ],
                    [
                        {"t": "p", "md": "**The better way** — save the model at the end of "
                                         "each epoch and keep the best. In Keras this is the "
                                         "`EarlyStopping` callback, which halts as soon as "
                                         "validation stops improving **while remembering the "
                                         "best state**."},
                        {"t": "band", "md": "Callbacks are covered in **chapter 7**."},
                    ],
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.4 · listing 5.10–5.12",
            "title": "Regularisation 1 — make the model smaller",
            "blocks": [
                {"t": "p", "md": "With limited memorisation capacity the model is ==forced to "
                                 "learn compressed representations that have predictive "
                                 "power== — precisely the kind we want."},
                {"t": "table",
                 "head": ["Version", "Hidden layers", "Starts overfitting", "Behaviour"],
                 "widths": [18, 20, 18, 44],
                 "rows": [
                     ["**Reference**", "2 × `Dense(16)`", "epoch 4", "The comparison point."],
                     ["**Smaller**", "2 × `Dense(4)`", "epoch 6",
                      "Overfits later, and **degrades more slowly** once it does."],
                     ["**Much larger**", "2 × `Dense(512)`", "epoch 1",
                      "Overfits almost immediately and far more severely; validation loss "
                      "noisier, training loss near zero fast."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.4 · listing 5.13",
            "title": "Regularisation 2 — constrain the weights",
            "blocks": [
                {"t": "p", "md": "Occam's razor applied to weights: given the same data and "
                                 "architecture many weight settings explain it, and "
                                 "**simpler ones are less likely to overfit**."},
                {"t": "code", "lang": "python", "file": "listing 5.13–5.14 — weight regularisers",
                 "src": """from keras.regularizers import l2
from keras import regularizers

model = keras.Sequential([
    layers.Dense(16, kernel_regularizer=l2(0.002), activation="relu"),
    layers.Dense(16, kernel_regularizer=l2(0.002), activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])

regularizers.l1(0.001)                     # L1
regularizers.l1_l2(l1=0.001, l2=0.001)     # both at once"""},
                {"t": "band",
                 "md": "`l2(0.002)` adds `0.002 * weight ** 2` per coefficient to the loss. "
                       "The penalty applies **only during training**, so ==training loss will "
                       "read much higher than test loss== — expected, not a bug."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.4",
            "title": "L1 or L2, and when weight regularisation stops helping",
            "blocks": [
                {"t": "table",
                 "head": ["Kind", "Penalty added to the loss", "Effect"],
                 "widths": [14, 44, 42],
                 "rows": [
                     ["**L1**", "Proportional to the **absolute value** of the weights.",
                      "Pushes weights towards **sparsity** — many exactly zero."],
                     ["**L2**", "Proportional to the **square** of the weights.",
                      "Pushes all weights small. Also called **weight decay** — different "
                      "name, identical mathematics."],
                 ]},
                {"t": "band", "style": "amber",
                 "md": "Weight regularisation is **typically used on smaller models**. Large "
                       "models are so overparameterised that constraining weight values "
                       "==has little effect on capacity==. For those, dropout is preferred."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.4 · listing 5.15",
            "title": "Regularisation 3 — dropout",
            "blocks": [
                {"t": "mmd", "id": "ch05-dropout", "src": MMD_DROPOUT,
                 "cap": "Figure 5.21 — the rescaling is done during training so that test "
                        "time needs no adjustment at all."},
                {"t": "p", "md": "The **dropout rate** is the fraction zeroed out, usually "
                                 "between **0.2 and 0.5**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.4",
            "title": "…and how it looks in a model",
            "blocks": [
                {"t": "p", "md": "A `Dropout` layer is inserted after the layer whose output "
                                 "it should perturb."},
                {"t": "code", "lang": "python", "file": "listing 5.15 — dropout on the IMDB model",
                 "src": """model = keras.Sequential([
    layers.Dense(16, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(16, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(1, activation="sigmoid"),
])"""},
                {"t": "band",
                 "md": "On the IMDB model this is a clear improvement over the reference — "
                       "and it reaches a **lower minimum validation loss than L2 did**."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.4",
            "title": "Where dropout came from",
            "blocks": [
                {"t": "quote",
                 "md": "I went to my bank. The tellers kept changing and I asked one of them "
                       "why. He said he didn't know but they got moved around a lot. I figured "
                       "it must be because it would require cooperation between employees to "
                       "successfully defraud the bank. This made me realize that randomly "
                       "removing a different subset of neurons on each example would prevent "
                       "conspiracies and thus reduce overfitting.",
                 "cite": "Geoff Hinton, quoted in Chollet & Watson, section 5.4.4"},
                {"t": "band",
                 "md": "The mechanism in one line: injecting noise into a layer's outputs "
                       "==breaks up accidental patterns== — Hinton's *conspiracies* — that the "
                       "model would otherwise start memorising."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Section 5.4.4",
            "title": "Which technique, when",
            "blocks": [
                {"t": "table",
                 "head": ["Technique", "Best suited to", "Notes"],
                 "widths": [24, 34, 42],
                 "rows": [
                     ["**More / better data**", "Always, where possible.",
                      "The largest return. Adding overly noisy data harms instead."],
                     ["**Better features**", "Small data; well-understood problems.",
                      "Can remove the need for a large model entirely."],
                     ["**Reduce capacity**", "Small models; small datasets.",
                      "Find the compromise — do not tip into underfitting."],
                     ["**L1 / L2**", "**Smaller** deep learning models.",
                      "On very large models, constraining weights ==does little=="],
                     ["**Dropout**", "**Large** models, where weight decay is weak.",
                      "Rates of 0.2–0.5. Beat L2 on the IMDB benchmark."],
                 ]},
                {"t": "band", "style": "rose",
                 "md": "One condition governs all of them: **regularisation must be guided by "
                       "an accurate evaluation procedure**. You will only achieve "
                       "generalisation ==if you can measure it=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this chapter",
            "blocks": [
                {"t": "steps", "items": [
                    "The purpose of a model is to **generalise** — to be accurate on inputs it "
                    "has never seen. Harder than it sounds.",
                    "Deep networks generalise by **interpolating** on the data's latent "
                    "manifold, which is why they only make sense of inputs ==close to what "
                    "they have seen==.",
                    "The fundamental problem is the **optimisation vs generalisation tension**. "
                    "Every best practice in the book manages it.",
                    "**Measure before you improve.** Hold-out, K-fold, iterated K-fold — and "
                    "always keep a completely untouched test set.",
                    "**Set a common-sense baseline first.** If you cannot beat it, the problem "
                    "may not be a machine learning problem.",
                    "To fit: **learning rate and batch size → architecture priors → capacity**, "
                    "until it can overfit.",
                    "To generalise: **better data → better features → early stopping → less "
                    "capacity → L1/L2 → dropout**, in that order.",
                ]},
                {"t": "links", "items": [
                    {"k": "NOTEBOOK", "ic": "📓", "v": "02_shuffled_labels_and_manifolds.ipynb",
                     "href": "../../course-slides/notebooks/ch05/02_shuffled_labels_and_manifolds.ipynb"},
                    {"k": "NEXT", "ic": "➡", "v": "Chapter 6 — The universal workflow",
                     "href": "../ch06/index.html"},
                ]},
            ],
        },
    ],
}
