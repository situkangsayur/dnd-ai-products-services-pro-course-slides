---
tags: [agentic-ai, tooling, procurement]
updated: 2026-08-30
---

# Tech stack and no-code

Three tiers, and each answers a different question.

- **Easy** — no-code and hosted builders. Question: *is this worth building?*
- **Medium** — a framework (LangGraph, CrewAI, an SDK). Question: *what shape
  is it?*
- **Production ready** — your own code over your own services. Question: *can
  we run this for three years and evidence it?*

## The rule

> **Prototype in no-code, build in code.** They are different activities.

Using one tool for both is how a prototype becomes production by accident — and
the moment it does, you own an artefact nobody can review, version, test or
roll back.

## What actually differs between no-code and code

1. **Version control and review** — a diff, or a canvas somebody edited
2. **Testing** — an evaluation set in CI, or clicking through it
3. **Data residency** — where the vendor runs, which you do not choose
4. **Exit cost** — a rewrite, or a git history

Compare stacks on properties you can verify — licence, hosting model, protocol
support, whether you can self-host — not on published benchmark scores. None of
the vendor agent-framework comparisons are reproducible.

Related: [[MCP and A2A]], [[Components at three levels]]
