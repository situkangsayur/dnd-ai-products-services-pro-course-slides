---
tags: [agentic-ai, findings, teaching]
updated: 2026-08-30
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

## The evaluation harness caught errors in my own evaluation sets

Twice. Both times an assertion was aimed at the wrong object. Writing the
known-good outcome *before* building is what made the mismatch visible.

Related: [[The SME credit demo]], [[Components at three levels]]
