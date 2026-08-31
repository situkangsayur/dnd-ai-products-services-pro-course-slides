---
tags: [agentic-ai, architecture]
updated: 2026-08-31
---

# The agent loop

Plan → act → observe → check, until an exit condition fires. ReAct
(arXiv:2210.03629) is the canonical framing; the engineering is almost entirely
in the *check*.

## Six ways it must be able to stop

Not one. All six, independently:

1. **Goal reached** — the only happy one
2. **Step limit** — a count of tool calls
3. **Token limit**
4. **Cost limit** — in currency, because that is what gets approved
5. **Wall clock**
6. **Repetition** — the same tool with the same arguments twice running is
   almost always a loop rather than progress, and it is the exit people leave
   out

> A loop with no exit is a bug that bills by the token.

## The trace is not logging

It is the only debugging tool that works here, and it is also the audit
evidence. Every figure in an answer should trace to the call that produced it.
Alert on the **shape** of runs — mean steps per request, cost per request, tool
repetition rate, escalation rate — not only on errors. A rising step count is
usually the first visible sign that something upstream changed.

## Teaching it: run one, do not name four

The deck used to draw this as four boxes and an arrow back — which is a picture
of a `while` statement. It now turns a **real run** inside the ring: the SME
credit assessment, six turns, six tools, with the step budget filling one cell
per turn.

It stops at 6 of 8 **because it was finished, not because it ran out** — and the
seventh turn, the approval, is absent because no tool for it exists. What four
boxes cannot show is how many times it goes round, what a turn costs, and what
makes it stop, which is the entire subject.

Related: [[Tools are the permission boundary]], [[Workflow versus agent]],
[[The SME credit demo]]
