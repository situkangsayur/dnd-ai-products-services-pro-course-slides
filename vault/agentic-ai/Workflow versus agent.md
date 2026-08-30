---
tags: [agentic-ai, architecture, decision]
updated: 2026-08-30
---

# Workflow versus agent

**The test: who decides the next step?**

If a person wrote the sequence down and the code follows it, that is a
workflow, however many model calls are inside it. If the model chooses what
happens next, and the path cannot be known before the run, that is an agent.

Most things are workflows. Building them as agents buys nondeterminism,
unbounded cost and an untestable path, in exchange for flexibility the problem
did not need.

## Five workflow patterns to exhaust first

1. **Chaining** — fixed sequence, each step's output feeding the next
2. **Routing** — classify, then dispatch to a specialist path
3. **Parallelisation** — independent subtasks, gathered at the end
4. **Orchestrator–worker** — a planned decomposition, workers with fixed jobs
5. **Evaluator–optimiser** — generate, critique, revise, with a stopping rule

Reach for an agent when the path genuinely cannot be enumerated: open-ended
investigation, recovery from unpredictable failures, a task whose next step
depends on what the last one found.

## What autonomy costs

Nondeterministic cost, a path you cannot test exhaustively, failures that
compound silently, and a debugging story that requires [[The agent loop|traces]]
because nothing else reproduces.

Related: [[The agent loop]], [[When to split into multiple agents]]
