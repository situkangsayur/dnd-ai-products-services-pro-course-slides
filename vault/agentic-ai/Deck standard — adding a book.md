---
tags: [course/ai-professional, itb, standard, authoring]
source: "course-slides/AUTHORING.md"
updated: 2026-08-31
---

# Deck standard — adding a book

What has to be true before a deck is finished, and what a **second book** would
cost. The full version with the file template is `course-slides/AUTHORING.md`;
this note is the part worth having in the vault — the decisions, not the syntax.

State on 31 Aug 2026: 22 decks, 1 173 slides, 27 drawn figures, 181 mermaid,
16 listings that step through their own arithmetic.

## The thing to fix first

`tools/course.py` holds **one** `BOOK` dict and **one** `CH_SLUG` map from
chapter number to URL slug. Twenty files import it. That is correct and simple
while there is one book, and wrong the moment there are two: `chapter_url(7)`
stops having a single answer.

So `BOOK` → `BOOKS`, one slug map per book, and `chapter_url`, `book_source`
and `chapter_resources` all take the book. Deck ids have to be unique across
books too — `dlwp07`, not `ch07`.

Do it **before** writing the second book's first chapter. Deferring it means
writing twenty files that then have to be edited again.

## Six numbers that must be zero

Three lints run on every build — a listing with no prose either side, a figure
with no words near it, a slide too dense to read, a chapter deck too short, a
chapter deck with too few diagrams. Three sweeps measure the rendered page:
clipped mermaid labels, figures rendering below 55 % of their drawn size, and
slides that overflow **at their last step** (a stepped figure has more than one
layout).

Plus one equality: **PDF page count = web slide count, deck by deck.** A
uniform difference across many decks is always structural rather than content —
every PDF once had exactly one page more, because the LaTeX renderer emitted a
Session Objectives page and the web renderer did not.

## Four rules for drawing, and one for not

1. If it is arithmetic, **compute it**. `0.0089` beside `5.21` proves
   something; "the gradient gets bigger" does not.
2. If it is a process, **run one example**. See [[The agent loop]] — four boxes
   and an arrow back is a picture of a `while` statement.
3. If there is nothing to measure, compute the **consequence** and print the
   assumption on the drawing.
4. Never let the picture argue with the sentence. A slide titled *nested inside
   one another*, drawn as a top-to-bottom chain, teaches the wrong thing — and
   the picture usually wins.

**When not to draw:** if the cards can be reordered without the slide becoming
wrong, it is a *list*. Of 128 card slides with no figure, about seven actually
wanted one, and all seven were showcase slides. A figure per bullet is
decoration, and decoration costs height — **and height is display size**, since
the fit pass shrinks the whole slide to make room.

## What measurement taught, the hard way

- **An empty result is not a clean result.** A sweep once reported 1 113 slides
  and zero problems for a build of 1 169: one deck had failed to measure,
  silently. Read the failure list before the totals.
- **A declared number is not a measured one.** A figure-height threshold read
  off the stylesheet said 480px; the browser was handing out 270.
- **Look at the page occasionally.** The largest layout bug here — a transform
  origin pushing every shrunk slide 300px to the right — was invisible to every
  metric and obvious in one screenshot.

The same shape of lesson as [[Findings worth keeping]]: a claim that has not
been executed is a claim about intentions.

Related: [[Agentic AI — index]], [[Findings worth keeping]], [[The agent loop]]
