---
tags: [agentic-ai, security, architecture]
updated: 2026-08-30
---

# Tools are the permission boundary

**The model never touches anything.** It emits a structured description of an
intention; your code decides whether to honour it. Every permission boundary in
an agentic system lives in that gap.

This is why a capability boundary is an **absent tool**, not an instruction. A
prompt that says "never approve credit" is a request. A registry with no
approval tool in it is a control — and it survives prompt injection, model
upgrades, and a clever user, because there is nothing there to reach.

## Rules that earn their place

- A tool description is written **for the model**, re-read on every call. Say
  what it returns and when *not* to call it.
- **Errors are data, not exceptions.** A tool that returns `{"error": ...}` lets
  the agent recover; one that throws ends the run.
- **Results stay small.** Every byte occupies context the model pays to re-read
  on every subsequent step. Truncate loudly — a silent truncation means the
  model reasons confidently about half a document without knowing it.
- **Read tools and write tools are different risks** from day one. Reads can be
  autonomous; writes start behind a gate and leave it only with evidence.
- **Identity travels from the end user**, not from the service. An agent running
  as a service account holds the union of everyone's permissions.

## Guardrails go in three places

On the input, on the tool call, and on the output. Prefer deterministic checks:
a guardrail that is itself a model call is a guardrail that can be wrong, and it
doubles the cost of being so. Retrieved content is untrusted input — run the
injection check over tool results too.

Related: [[The agent loop]], [[The SME credit demo]]
