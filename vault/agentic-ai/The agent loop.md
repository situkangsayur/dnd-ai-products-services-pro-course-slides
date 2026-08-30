---
tags: [agentic-ai, architecture]
updated: 2026-08-30
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

Related: [[Tools are the permission boundary]], [[Workflow versus agent]]
