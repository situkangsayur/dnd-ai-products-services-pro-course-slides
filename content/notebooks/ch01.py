# -*- coding: utf-8 -*-
"""Chapter 1 notebooks — What Is Deep Learning?

The chapter has no code in the book. This notebook exists anyway, because the
one claim the chapter makes that people nod along to without believing is that
a program can be *produced from data rather than written*. Fifteen lines of
scikit-learn make that concrete in a way no slide does.
"""

DECK = "ch01"

NOTEBOOKS = [
    {
        "file": "01_the_ml_paradigm.ipynb",
        "title": "The machine learning paradigm, in fifteen lines",
        "lede": "Classical programming takes rules and data and produces answers. "
                "Machine learning takes data and answers and produces the rules. "
                "This notebook does both, on the same problem, so the difference "
                "is something you can run rather than something you are told.",
        "needs": "CPU — under a minute",
        "section": "01 — Artificial intelligence, machine learning, deep learning",
        "cells": [
            ("h2", "The problem"),
            ("md",
             "Classify a point in the plane as belonging to one of two classes. "
             "Trivially easy — which is exactly why it is a fair test of the "
             "*paradigm* rather than of anyone's cleverness with a model."),
            ("py", """import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)

# Two clouds, offset from one another and slightly overlapping.
a = rng.normal(loc=[0.0, 0.0], scale=0.8, size=(300, 2))
b = rng.normal(loc=[2.4, 2.0], scale=0.8, size=(300, 2))

X = np.vstack([a, b])
y = np.concatenate([np.zeros(len(a)), np.ones(len(b))])

plt.figure(figsize=(5, 5))
plt.scatter(X[y == 0, 0], X[y == 0, 1], s=12, alpha=.7, label="class 0")
plt.scatter(X[y == 1, 0], X[y == 1, 1], s=12, alpha=.7, label="class 1")
plt.legend(); plt.title("The data"); plt.gca().set_aspect("equal")
plt.show()"""),

            ("h2", "Classical programming: you write the rule"),
            ("md",
             "Look at the picture, pick a boundary, write it down. This is the "
             "loop the chapter calls *rules + data -> answers*, and note where "
             "the intelligence lives: **in your head, transcribed into a "
             "constant.**"),
            ("py", """def handwritten_rule(points):
    # A line I chose by looking at the scatter plot above.
    return (points[:, 0] + points[:, 1] > 2.2).astype(float)

acc = (handwritten_rule(X) == y).mean()
print(f"hand-written rule: {acc:.3f} accuracy")"""),
            ("out", "hand-written rule: 0.9xx accuracy"),
            ("note",
             "It works. It also took a human looking at a two-dimensional "
             "picture. Try the same approach on a 784-dimensional MNIST digit "
             "and the method collapses — not because it is wrong, but because "
             "there is no picture to look at."),

            ("h2", "Machine learning: the rule is produced from the data"),
            ("md",
             "Same problem, no boundary chosen by anyone. We hand over the data "
             "**and the answers**, and get a rule back."),
            ("py", """from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=0, stratify=y
)

model = LogisticRegression().fit(X_train, y_train)

print(f"learned rule:      {model.score(X_test, y_test):.3f} accuracy (held out)")
print(f"learned boundary:  {model.coef_[0][0]:+.2f}*x  {model.coef_[0][1]:+.2f}*y "
      f"{model.intercept_[0]:+.2f}  >  0")"""),
            ("out", """learned rule:      0.9xx accuracy (held out)
learned boundary:  +1.xx*x  +1.xx*y  -x.xx  >  0"""),
            ("md",
             "The second line is the point of the whole notebook. **That "
             "expression is a program**, and nobody wrote it — it was produced "
             "by looking at 420 examples and their answers."),

            ("h2", "Seeing the learned rule"),
            ("py", """xx, yy = np.meshgrid(np.linspace(-3, 5.5, 300),
                     np.linspace(-3, 5, 300))
grid = np.c_[xx.ravel(), yy.ravel()]
zz = model.predict_proba(grid)[:, 1].reshape(xx.shape)

plt.figure(figsize=(5.6, 5))
plt.contourf(xx, yy, zz, levels=20, cmap="RdBu_r", alpha=.55)
plt.contour(xx, yy, zz, levels=[0.5], colors="k", linewidths=1.6)
plt.scatter(X[y == 0, 0], X[y == 0, 1], s=10, c="#1f5fa8", edgecolors="w", linewidths=.3)
plt.scatter(X[y == 1, 0], X[y == 1, 1], s=10, c="#c0392b", edgecolors="w", linewidths=.3)
plt.title("Learned decision boundary (black) and confidence")
plt.gca().set_aspect("equal")
plt.show()"""),

            ("h2", "Why 'learning' is a representation problem"),
            ("md",
             "The chapter's claim is that learning means **searching for a more "
             "useful representation** of the data, inside a space of "
             "possibilities defined in advance. Here is that claim as an "
             "experiment: the same logistic regression, on data it cannot "
             "possibly separate — and then on a coordinate change that makes it "
             "trivial."),
            ("py", """from sklearn.datasets import make_circles

Xc, yc = make_circles(n_samples=600, factor=0.45, noise=0.08, random_state=0)

flat = LogisticRegression().fit(Xc, yc).score(Xc, yc)

# One new representation: distance from the origin. Nothing else changes.
Xr = np.c_[Xc, (Xc ** 2).sum(axis=1)]
lifted = LogisticRegression().fit(Xr, yc).score(Xr, yc)

print(f"raw coordinates:      {flat:.3f}")
print(f"+ one extra feature:  {lifted:.3f}")"""),
            ("out", """raw coordinates:      0.5xx
+ one extra feature:  1.000"""),
            ("md",
             "Same model, same optimizer, same data. **The only thing that "
             "changed was the representation**, and it took the problem from "
             "coin-flipping to solved.\n\n"
             "That is what the layers of a deep network are doing, chapter 2 "
             "onwards: not classifying, but repeatedly re-representing, until "
             "the last layer's job is as easy as the one above."),

            ("h2", "One thing to try"),
            ("md",
             "Replace `(Xc ** 2).sum(axis=1)` with a feature that does *not* "
             "help — the sum of the coordinates, say — and watch the accuracy "
             "stay at chance. Finding the representation is the whole problem, "
             "and it is why the rest of this course is about learning them "
             "rather than choosing them."),
        ],
        "takeaways": [
            "Classical programming produces answers from rules and data; "
            "machine learning produces **rules** from data and answers.",
            "A learned model is a program that nobody wrote — here, literally a "
            "printable expression.",
            "Learning is a **search for a useful representation** within a "
            "predefined space of possibilities.",
            "The right representation can turn an unsolvable problem into a "
            "trivial one, without changing the model at all.",
        ],
    },
]
