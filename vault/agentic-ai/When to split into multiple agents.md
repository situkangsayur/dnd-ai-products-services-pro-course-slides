---
tags: [agentic-ai, architecture, cost]
updated: 2026-08-30
---

# When to split into multiple agents

Three questions. If none is a yes, do not split.

1. **Do the parts need different permissions?** This is the strongest reason,
   because the split is then a security boundary and not an aesthetic one.
2. **Is there real parallelism?** Subtasks that genuinely do not interact, and
   are slow enough that fan-out beats the coordination overhead.
3. **Will the context not fit?** A genuine window problem, not a tidiness
   problem.

## The failure mode

Researcher / Writer / Critic feels organised and costs roughly three times one
agent with the same tools, because every agent re-reads the shared context and
the hand-offs are themselves model calls. Splitting on the org chart is not a
technical argument.

`agentdemo compare research_review` prints the token counts for exactly this,
against one agent doing the same job.

## Where splitting is right

- **Different permissions** — an investigator with no write tool anywhere in its
  registry, handing to an actor that has them
- **Genuine fan-out** — triage over independent items, where the crossover
  point is measurable
- **Escalation to a human** — see [[Regulation — OJK, PDP, ISO]]; the hand-off
  is a split whether you model it as one or not

Related: [[Workflow versus agent]], [[Tools are the permission boundary]]
