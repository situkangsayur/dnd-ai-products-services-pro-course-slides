---
tags: [agentic-ai, course/ai-professional, itb, index]
source: "course-slides/content/hendri_agentic.py — 91 slides"
updated: 2026-08-31
---

# Agentic AI — index

The module I teach in *Designing and Building AI Products and Services* (ITB,
Directorate of Sustainable Professional Education). It follows Viny's LLM module:
hers ends with a model that **answers**, mine is about a system that **acts**.

The module is deliberately deflationary. Most problems brought to "agents" are
workflows; most multi-agent designs do not survive a cost table; and the
engineering that matters is in tools, memory, guardrails and evaluation rather
than in prompts.

## The spine

1. [[Workflow versus agent]] — the operational test, applied first
2. [[The agent loop]] — plan, act, observe, check, and six exits
3. [[Tools are the permission boundary]] — where every control actually lives
4. [[When to split into multiple agents]] — three questions, not an org chart
5. [[Components at three levels]] — minimum, best practice, production ready
6. [[Tech stack and no-code]] — different tools for different phases
7. [[MCP and A2A]] — inward against across
8. [[Regulation — OJK, PDP, ISO]] — the question that decides the architecture
9. [[The SME credit demo]] — all of it, running, on a phone
10. [[Findings worth keeping]] — what building it changed my mind about

## The one-line version

> The definition of an agent is old — Russell & Norvig, percepts in through
> sensors, actions out through actuators. What is new is the **action space**,
> and everything difficult follows from that rather than from the model.

## Artefacts

- Deck: `course-slides/content/hendri_agentic.py` → LaTeX + web, 91 slides
  (22 drawn figures, PDF page-for-page identical to the web deck)
- Code: `ai-agentic-demo/` — nine cases and the integrated system
- References: `course-slides/references/REFERENCES.md`, every link checkable
  with `python3 check.py`
