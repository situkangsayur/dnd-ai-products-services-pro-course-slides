---
tags: [agentic-ai, architecture, production]
updated: 2026-08-30
---

# Components at three levels

Calling a minimum system production-ready is how incidents happen. Name the
level out loud.

## Minimum — what makes it an agent at all

A model, a tool registry, a loop, and an exit condition. That is it. It will run
and it will demo well.

## Best practice — what makes it survivable

Traces on every run. Budgets on all six dimensions. Guardrails on input, tool
call and output. An evaluation set with known-good outcomes. Structured errors
that the loop can recover from. Approval gates on writes.

## Production ready — what a regulator and an on-call rota require

Everything above, plus: identity propagated from the end user; model and prompt
versioning with rollback; drift and shape monitoring with alerts; an audit trail
an examiner can read; a documented human oversight path; incident response that
someone has actually rehearsed; and data residency that is *designed*, not
discovered.

The two that get skipped are **evaluation** and **the audit trail**, and they
are the two that make everything else defensible.

Related: [[The agent loop]], [[Regulation — OJK, PDP, ISO]]
