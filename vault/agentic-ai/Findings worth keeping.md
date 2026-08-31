---
tags: [agentic-ai, findings, teaching]
updated: 2026-08-31
---

# Findings worth keeping

Things that building the demo changed my mind about, or that are worth saying
out loud in a session because they are counter to what the room expects.

## Gradient boosting lost

The demo fits gradient-boosted trees **and** logistic regression on the same
data, compares them on a held-out split, and ships the winner. The logistic
model wins: **0.762 against 0.733** on AUC.

The relationship in the data is close to linear and the population is small, so
the ensemble had nothing to find and found noise instead. Reaching for the most
powerful model is a habit, not a method — and here the simpler model wins twice:
on the metric, and on being explainable to somebody who can stop you deploying
it.

## The queue had to move to disk

It began as a dict, and worked perfectly until the MCP server became its own
process: the agent queued a recommendation into one process's memory and the
officer's app read an empty queue from another's.

That is not a Python problem. It is the ordinary consequence of splitting a
system into services, and it is exactly the kind of thing an architecture
diagram hides — the boxes were right, the arrows were right, and the state was
in the wrong place.

## Extrapolation should be reported, not hidden

Two of the six applicants sit outside the range the model was fitted on. A score
there is a guess wearing four decimal places. The model now returns
`reliability: low` and names the offending features, and the case is referred.

But the *ordering* matters: a failed policy clause is a decline whatever the
model says. An unreliable score must not be allowed to convert a decline into a
referral. The evaluation set caught that when I had it the wrong way round.

## A scripted answer must be derived from its own trace

The offline provider composes the final answer by reading the tool results out
of the conversation, rather than from a fixed string. An earlier case in the
repository had a scripted answer that contradicted its own trace — the most
embarrassing failure a demo can have, and the easiest one to have.

## "Reviewed source" is not compiled source

The Flutter client sat in the repository for weeks marked *not yet compiled* —
there was no SDK on the machine it was written on. It had been read several
times and looked right.

The first compile found a bug it could never have run past:
`ThemeData.cardTheme` takes a `CardTheme` up to Flutter 3.22 and a
`CardThemeData` after it. One word, and the app does not start.

Two more only appear from a **clean checkout**, which is the state anyone
following the how-to is in:

- `flutter create .` overwrites `AndroidManifest.xml`. In this repo that file
  is ours — it carries the network-security config and the deliberate decision
  *not* to request a `CAMERA` permission.
- `flutter create .` leaves a `test/widget_test.dart` written for the counter
  app it assumes you are building. It references a `MyApp` that does not exist
  here, so `flutter analyze` **fails** on a fresh clone.

The lesson generalises past Flutter, and it is the same one as
[[Tools are the permission boundary]]: a claim that has not been executed is a
claim about intentions. The APK's permission list can now be checked instead of
believed — `aapt2 dump badging` says `INTERNET`, and nothing else.

## The evaluation harness caught errors in my own evaluation sets

Twice. Both times an assertion was aimed at the wrong object. Writing the
known-good outcome *before* building is what made the mismatch visible.

Related: [[The SME credit demo]], [[Components at three levels]]
