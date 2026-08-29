# -*- coding: utf-8 -*-
"""Module deck — Agentic AI.

A standalone module of the course, delivered after the book chapters. It is not
derived from Deep Learning with Python; it sits on top of it, taking chapter 16's
LLM as a given and asking what you build around one.

The through-line is deliberately deflationary: most problems people bring to
"agents" are workflows, most multi-agent designs do not survive contact with a
cost model, and the interesting engineering is in tools, memory, and evaluation
rather than in prompts.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import COURSE  # noqa: E402


MMD_LADDER = """
flowchart TB
  A["<b>AI</b><br/><small>a model that maps<br/>input to output</small>"]
  B["<b>AI workflow</b><br/><small>a fixed sequence of steps,<br/>some of which call a model</small>"]
  C["<b>AI agent</b><br/><small>a model that chooses<br/>which tool to call, in a loop,<br/>until a goal is met</small>"]
  D["<b>Agentic system</b><br/><small>an agent with memory, planning,<br/>and control over its own steps</small>"]
  E["<b>Multi-agent system</b><br/><small>several agents with distinct roles,<br/>coordinating through messages</small>"]
  A --> B --> C --> D --> E
"""

MMD_WHO_DECIDES = """
flowchart TB
  Q["<b>Who decides the next step?</b>"]
  W["<b>You do, at design time</b><br/><small>the control flow is in your code</small>"]
  A["<b>The model does, at run time</b><br/><small>the control flow is in the prompt<br/>and the tool results</small>"]
  WR["That is a <b>workflow</b><br/><small>testable, cheap, predictable</small>"]
  AR["That is an <b>agent</b><br/><small>flexible, expensive, hard to test</small>"]
  Q --> W --> WR
  Q --> A --> AR
"""

MMD_LOOP = """
flowchart TB
  G["Goal or user request"]
  P["<b>Plan</b><br/><small>what should happen next?</small>"]
  T["<b>Act</b><br/><small>call a tool</small>"]
  O["<b>Observe</b><br/><small>the tool result enters<br/>the context</small>"]
  C["<b>Check</b><br/><small>is the goal met?<br/>is the budget spent?</small>"]
  D["Answer, or hand off<br/>to a human"]
  G --> P --> T --> O --> C
  C -- "not yet" --> P
  C -- "done, or out of budget" --> D
"""

MMD_TOOL = """
flowchart LR
  M["<b>Model</b>"]
  S["<b>Tool schema</b><br/><small>name, description,<br/>typed parameters</small>"]
  CALL["<b>Tool call</b><br/><small>structured, validated</small>"]
  EX["<b>Your code</b><br/><small>the only thing that<br/>actually touches a system</small>"]
  R["<b>Result</b><br/><small>appended to the context</small>"]
  S --> M --> CALL --> EX --> R --> M
"""

MMD_MEMORY = """
flowchart TB
  W["<b>Working memory</b><br/><small>the context window<br/>-- this turn only</small>"]
  E["<b>Episodic memory</b><br/><small>what happened in past runs<br/>-- a transcript store</small>"]
  S["<b>Semantic memory</b><br/><small>facts and documents<br/>-- a vector or keyword index</small>"]
  P["<b>Procedural memory</b><br/><small>learned routines<br/>-- prompts, tools, playbooks</small>"]
  A["The agent's next step"]
  W --> A
  E --> A
  S --> A
  P --> A
"""

MMD_STACK = """
flowchart TB
  MOD["<b>Model layer</b><br/><small>hosted API, or a self-hosted<br/>open-weights model</small>"]
  ORCH["<b>Orchestration layer</b><br/><small>the loop, tool routing,<br/>retries, budgets</small>"]
  TOOLS["<b>Tool layer</b><br/><small>your APIs, databases,<br/>search, code execution</small>"]
  MEM["<b>Memory layer</b><br/><small>vector store, transcript store,<br/>document store</small>"]
  OBS["<b>Observability layer</b><br/><small>traces, evals, cost accounting,<br/>human review queue</small>"]
  GUARD["<b>Guardrail layer</b><br/><small>input filters, output checks,<br/>approval gates</small>"]
  MOD --> ORCH
  TOOLS --> ORCH
  MEM --> ORCH
  ORCH --> GUARD --> OBS
"""

MMD_MULTIAGENT = """
flowchart TB
  U["Request"]
  S["<b>Supervisor</b><br/><small>decomposes, routes,<br/>and assembles</small>"]
  A1["<b>Specialist A</b><br/><small>own tools,<br/>own context</small>"]
  A2["<b>Specialist B</b>"]
  A3["<b>Specialist C</b>"]
  R["Assembled answer"]
  U --> S
  S --> A1 --> S
  S --> A2 --> S
  S --> A3 --> S
  S --> R
"""

MMD_WHEN_MULTI = """
flowchart TB
  Q["Should this be<br/>more than one agent?"]
  C1["Do the subtasks need<br/><b>genuinely different tools<br/>or permissions</b>?"]
  C2["Can they run<br/><b>in parallel</b>?"]
  C3["Would one context window<br/><b>overflow</b> otherwise?"]
  Y["<b>Yes -- split</b>"]
  N["<b>No -- one agent,<br/>more tools</b>"]
  Q --> C1
  Q --> C2
  Q --> C3
  C1 --> Y
  C2 --> Y
  C3 --> Y
  Q -- "none of the above" --> N
"""

MMD_EVAL = """
flowchart TB
  T["<b>Trace</b><br/><small>every step, tool call,<br/>and token, recorded</small>"]
  U["<b>Unit evals</b><br/><small>does this tool get called<br/>with the right arguments?</small>"]
  E["<b>End-to-end evals</b><br/><small>a fixed set of tasks with<br/>known good outcomes</small>"]
  H["<b>Human review</b><br/><small>sampled, and every<br/>escalation</small>"]
  R["<b>Regression gate</b><br/><small>run before every<br/>prompt or model change</small>"]
  T --> U --> R
  T --> E --> R
  T --> H --> R
"""

MMD_FAILURE = """
flowchart TB
  L["<b>Looping</b><br/><small>the same tool, over and over</small>"]
  D["<b>Drift</b><br/><small>the goal quietly changes<br/>mid-run</small>"]
  H["<b>Confident wrong answers</b><br/><small>a hallucinated tool result<br/>treated as fact</small>"]
  C["<b>Cost blowout</b><br/><small>no budget, no cap,<br/>no early stop</small>"]
  F["<b>Every one of these is<br/>invisible without traces</b>"]
  L --> F
  D --> F
  H --> F
  C --> F
"""

MMD_MATURITY = """
flowchart LR
  L0["<b>L0</b><br/>Assisted<br/><small>a human does the work,<br/>the model drafts</small>"]
  L1["<b>L1</b><br/>Workflow<br/><small>fixed steps, model in<br/>some of them</small>"]
  L2["<b>L2</b><br/>Supervised agent<br/><small>agent acts, human<br/>approves each write</small>"]
  L3["<b>L3</b><br/>Bounded autonomy<br/><small>agent acts alone within<br/>a defined blast radius</small>"]
  L0 --> L1 --> L2 --> L3
"""


NB = []

RESOURCES = [
    {"kind": "site", "label": "Course home", "href": "../../index.html"},
    {"kind": "github", "label": "ai-agentic-demo — single-agent and multi-agent cases",
     "href": "https://github.com/situkangsayur/ai-agentic-demo"},
]

DECK = {
    "id": "hendri-agentic",
    "kind": "module",
    "number": None,
    "title": "Agentic AI",
    "subtitle": "What you build around a language model — and the more useful question "
                "of when you should not.",
    "source": "Module material for " + COURSE["title"],
    "source_url": "https://hendrikarisma.my.id",
    "duration": "3 hours (2 sessions)",
    "presenter": {"name": "Hendri Karisma, M.T.", "role": "Teaching Assistant"},
    "resources": RESOURCES,
    "objectives": [
        "Distinguish **AI, AI workflow, AI agent, agentic system, and multi-agent "
        "system** using one operational test.",
        "Describe the **agent loop** — plan, act, observe, check — and name what "
        "terminates it.",
        "Design a **tool** properly: schema, description, validation, and the fact "
        "that only your code touches a real system.",
        "Choose between the **four kinds of memory**, and say which problem each one "
        "solves.",
        "Lay out a **tech stack** across model, orchestration, tools, memory, "
        "guardrails, and observability.",
        "Apply a **three-question test** before splitting a system into multiple "
        "agents.",
        "Build an **evaluation harness** for a non-deterministic system, and explain "
        "why traces come first.",
        "Place a proposed deployment on the **autonomy ladder** and justify the "
        "level chosen.",
    ],
    "slides": [
        {"type": "title"},

        # ------------------------------------------------------------------
        {"type": "section", "num": "01", "title": "What the words mean",
         "lead": "Five terms that are used interchangeably and should not be."},

        {
            "type": "slide",
            "kicker": "Setting up",
            "title": "This module sits on top of chapter 16",
            "blocks": [
                {"t": "p", "md": "Chapter 16 gave us a language model: a system that, given a "
                                 "sequence, produces a plausible continuation. It also gave us "
                                 "the honest limits — hallucination, prompt sensitivity, no "
                                 "adaptation to genuine novelty."},
                {"t": "lead", "md": "This module asks a different question: **given such a model, "
                                    "what do you build around it** so that it can affect the "
                                    "world rather than only describe it?"},
                {"t": "band", "md": "Nothing in this module makes the model more capable. "
                                    "Everything in it is about **what the model is connected "
                                    "to**, and about ==what happens when it is wrong=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Vocabulary",
            "title": "Five terms, in increasing order of autonomy",
            "blocks": [
                {"t": "mmd", "id": "hendri-ladder", "src": MMD_LADDER,
                 "cap": "Each step gives the model more say over what happens next."},
                {"t": "p", "md": "These are used interchangeably in vendor material and they are "
                                 "not interchangeable. **The difference between them is a cost "
                                 "difference, a testability difference, and a risk difference** "
                                 "— which makes it worth being precise."},
            ],
        },

        {
            "type": "slide",
            "kicker": "The operational test",
            "title": "One question separates a workflow from an agent",
            "blocks": [
                {"t": "mmd", "id": "hendri-who-decides", "src": MMD_WHO_DECIDES,
                 "cap": "Everything else — the model, the tools, the prompt — can be identical."},
                {"t": "band", "md": "**If you can draw the flowchart in advance and it does not "
                                    "change per request, you have a workflow.** Build it as a "
                                    "workflow. It will be cheaper, faster, and you will be able "
                                    "to test it."},
            ],
            "notes": "Press on this. Most systems described as agents in industry talks are "
                     "workflows with a model in one or two of the boxes, and that is a "
                     "compliment, not a criticism.",
        },

        {
            "type": "slide",
            "kicker": "Vocabulary",
            "title": "The five, stated precisely",
            "blocks": [
                {"t": "table",
                 "head": ["Term", "Control flow", "What it is good for"],
                 "widths": [22, 38, 40],
                 "rows": [
                     ["**AI**", "None — one call in, one answer out",
                      "Classification, extraction, summarization, generation."],
                     ["**AI workflow**", "**Yours**, fixed at design time",
                      "Most business processes. Predictable cost and latency."],
                     ["**AI agent**", "**The model's**, chosen per step from a tool set",
                      "Tasks whose shape is not known until you see the request."],
                     ["**Agentic system**", "The model's, plus memory and planning across turns",
                      "Long-running work; tasks that resume."],
                     ["**Multi-agent**", "A supervisor routing between specialists",
                      "Genuinely separable subtasks with different tools or permissions."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "A note on the hype",
            "title": "Deflating this on purpose",
            "blocks": [
                {"t": "lead", "md": "**Most problems brought to \"agents\" are workflows.** Most "
                                    "multi-agent designs do not survive contact with a cost model."},
                {"t": "p", "md": "That is not a reason to avoid the topic. It is the reason to "
                                 "learn it properly — because the value in this area is almost "
                                 "entirely in **tools, memory, and evaluation**, and almost none "
                                 "of it is in prompts."},
                {"t": "p", "md": "A useful habit for the rest of this module: every time you see a "
                                 "technique, ask **what it would cost to run 10,000 times a day, "
                                 "and how you would know it was working**."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "02", "title": "How an agent actually runs",
         "lead": "A loop, a tool schema, and something that makes it stop."},

        {
            "type": "slide",
            "kicker": "The loop",
            "title": "Plan, act, observe, check",
            "blocks": [
                {"t": "mmd", "id": "hendri-loop", "src": MMD_LOOP,
                 "cap": "The whole of agent engineering is in what fills each of these boxes."},
                {"t": "p", "md": "Note the shape. This is **the generation loop from chapter 16 "
                                 "with a tool call in the middle** — the model's output at one "
                                 "step becomes part of its input at the next. Everything chapter "
                                 "15 said about that pattern still applies."},
            ],
        },

        {
            "type": "slide",
            "kicker": "The loop · the part people forget",
            "title": "What terminates it",
            "blocks": [
                {"t": "p", "md": "A loop with no exit condition is a bug that bills by the token. "
                                 "Every agent needs **all** of the following, not one of them."},
                {"t": "bullets", "items": [
                    "**Goal satisfied** — the model says it is done, and something else checks "
                    "that claim.",
                    "**Step budget** — a hard maximum number of iterations.",
                    "**Token or currency budget** — a hard maximum spend per request.",
                    "**Wall-clock timeout** — because a hung tool is not the model's problem to "
                    "solve.",
                    "**Repetition detector** — the same tool with the same arguments twice in a "
                    "row is almost always a loop, not progress.",
                    "**Escalation path** — what happens when the budget is spent and the goal is "
                    "not met. *Silently returning a partial answer is the worst option.*",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tools",
            "title": "The model never touches anything",
            "blocks": [
                {"t": "mmd", "id": "hendri-tool", "src": MMD_TOOL,
                 "cap": "The model emits a structured request. Your code decides whether to "
                        "honour it."},
                {"t": "band", "md": "This is the single most important architectural fact in the "
                                    "module. **The model produces text describing an intention. "
                                    "Your code is the only thing that executes.** Every "
                                    "permission boundary you have lives in that gap."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tools · design",
            "title": "A tool is an API designed for a reader who forgets",
            "blocks": [
                {"t": "steps", "items": [
                    "**Name it for the task, not the system.** `find_customer_by_email` beats "
                    "`crm_query_v2`.",
                    "**Write the description for the model, not for your team.** It is the only "
                    "documentation the model gets, and it is read fresh every single call.",
                    "**Type every parameter, and validate on arrival.** Assume the arguments are "
                    "adversarial, because sometimes they will be.",
                    "**Return errors as data, not exceptions.** A tool that returns "
                    "`{\"error\": \"no customer with that email\"}` lets the agent recover; one "
                    "that throws ends the run.",
                    "**Keep results small.** Every byte a tool returns occupies context that the "
                    "model then pays to read on every subsequent step.",
                ]},
                {"t": "p", "md": "Most *prompt engineering* problems in agent systems are "
                                 "actually **tool description problems** wearing a disguise."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tools · the dangerous ones",
            "title": "Read tools and write tools are not the same risk",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "👁", "h": "Read tools", "style": "good",
                     "p": "Search, retrieve, look up, calculate. A wrong call wastes tokens and "
                          "returns something unhelpful. **Recoverable within the loop.**"},
                    {"ico": "✍", "h": "Write tools", "style": "bad",
                     "p": "Send, delete, transfer, approve, publish. A wrong call **changes the "
                          "world**, and no amount of subsequent reasoning undoes it."},
                ]},
                {"t": "band", "md": "Treat these differently from day one. **Read tools can be "
                                    "autonomous; write tools should start behind an approval "
                                    "gate** and only move out of it with evidence from your "
                                    "evaluation harness.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memory",
            "title": "Four kinds, solving four different problems",
            "blocks": [
                {"t": "mmd", "id": "hendri-memory", "src": MMD_MEMORY,
                 "cap": "Borrowed vocabulary from cognitive psychology, used loosely — but the "
                        "four categories map onto four different pieces of infrastructure."},
                {"t": "p", "md": "The mistake to avoid is treating *memory* as one thing and "
                                 "reaching for a vector database by reflex. **Most agents need "
                                 "working memory managed well and nothing else.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memory · the practical version",
            "title": "What each one costs you",
            "blocks": [
                {"t": "table",
                 "head": ["Kind", "Implementation", "The failure mode it introduces"],
                 "widths": [20, 38, 42],
                 "rows": [
                     ["**Working**", "The context window itself",
                      "Overflow. Old steps silently fall out and the agent forgets its goal."],
                     ["**Episodic**", "A transcript store, keyed by session",
                      "Replaying stale state as if it were current."],
                     ["**Semantic**", "Vector or keyword index over documents — chapter 16's RAG",
                      "Retrieving confidently irrelevant context, which is worse than none."],
                     ["**Procedural**", "Versioned prompts, tool sets, playbooks",
                      "Drift between what is deployed and what was evaluated."],
                 ]},
                {"t": "p", "md": "Each row is a system to operate. **Add them one at a time, and "
                                 "only when a specific observed failure demands it.**"},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "03", "title": "The tech stack",
         "lead": "Six layers, and the two that teams skip."},

        {
            "type": "slide",
            "kicker": "Architecture",
            "title": "Six layers",
            "blocks": [
                {"t": "mmd", "id": "hendri-stack", "src": MMD_STACK,
                 "cap": "Guardrails and observability are the two layers most first attempts "
                        "leave out entirely."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Architecture · model layer",
            "title": "Hosted or self-hosted, and what actually decides it",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "☁", "h": "Hosted API", "style": "",
                     "p": "Best capability per unit of effort, no infrastructure, immediate "
                          "access to new models. **Cost scales linearly with usage**, and your "
                          "data leaves your perimeter."},
                    {"ico": "🏠", "h": "Self-hosted open weights", "style": "",
                     "p": "Data stays inside. Fixed infrastructure cost rather than per-token. "
                          "**Lower capability at the same price point**, and you now operate a "
                          "GPU fleet."},
                ]},
                {"t": "band", "md": "In practice the decision is rarely about capability or cost. "
                                    "It is about **where the data is allowed to be** — which is a "
                                    "regulatory question, not an engineering one, and it should "
                                    "be answered before any code is written.", "style": "amber"},
            ],
            "notes": "For participants from regulated industries this is the slide that matters "
                     "most. The constraint is usually a specific clause in a specific rule, and "
                     "the right move is to go and read it rather than assume.",
        },

        {
            "type": "slide",
            "kicker": "Architecture · orchestration layer",
            "title": "What the orchestrator is responsible for",
            "blocks": [
                {"t": "bullets", "items": [
                    "**Running the loop** — and enforcing every one of the termination "
                    "conditions from earlier.",
                    "**Routing tool calls** to implementations, and validating arguments before "
                    "they arrive.",
                    "**Retrying** transient failures, with backoff, without re-charging the "
                    "model for the same reasoning.",
                    "**Accounting** — tokens, currency, and latency, per request and per tool.",
                    "**Emitting traces** for everything above.",
                ]},
                {"t": "p", "md": "Frameworks exist for all of this and are worth using. But note "
                                 "what the list contains: **queueing, retries, budgets, and "
                                 "telemetry.** This is ordinary distributed-systems work, and "
                                 "your existing platform team already knows how to do it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Architecture · guardrails",
            "title": "Three places to put a check",
            "blocks": [
                {"t": "steps", "items": [
                    "**On the input.** Reject or sanitise before the model sees it — prompt "
                    "injection carried in a retrieved document is the case people miss.",
                    "**On the tool call.** Validate arguments, check permissions against the "
                    "*end user's* identity rather than the service's, and gate write tools "
                    "behind approval.",
                    "**On the output.** Schema-check structured output; scan free text for the "
                    "categories your policy prohibits; verify claims against retrieved sources "
                    "where you can.",
                ]},
                {"t": "band", "md": "A guardrail that is itself a model call is a guardrail that "
                                    "can be wrong. **Prefer deterministic checks wherever the "
                                    "check can be expressed deterministically** — schema "
                                    "validation, allow-lists, permission lookups."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Architecture · the one people skip",
            "title": "Observability is not optional here",
            "blocks": [
                {"t": "p", "md": "In a deterministic system, a bug reproduces. In this one it "
                                 "does not — the same request can take a different path on "
                                 "Tuesday than it did on Monday, with the same code and the same "
                                 "weights."},
                {"t": "lead", "md": "**A trace of every step, every tool call, and every token is "
                                    "the only debugging tool you have.** Build it first, not "
                                    "after the first incident."},
                {"t": "p", "md": "The minimum useful trace records: the full prompt sent, the "
                                 "model and version, every tool call with arguments and results, "
                                 "token counts and cost per step, latency per step, and the "
                                 "termination reason. ==If you cannot answer *why did it do that* "
                                 "from your logs, you do not have logs.=="},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "04", "title": "Multi-agent, and when not to",
         "lead": "A supervisor, some specialists, and a three-question test."},

        {
            "type": "slide",
            "kicker": "Multi-agent",
            "title": "The supervisor pattern",
            "blocks": [
                {"t": "mmd", "id": "hendri-multiagent", "src": MMD_MULTIAGENT,
                 "cap": "Each specialist has its own tools, its own context, and its own "
                        "instructions."},
                {"t": "p", "md": "This is the pattern that appears in almost every multi-agent "
                                 "framework, under various names. The variations — peer-to-peer "
                                 "messaging, hierarchies, debate — are **elaborations of it, and "
                                 "each elaboration multiplies the cost.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Multi-agent · the test",
            "title": "Three questions before you split",
            "blocks": [
                {"t": "mmd", "id": "hendri-when-multi", "src": MMD_WHEN_MULTI,
                 "cap": "If none of the three is a yes, you want one agent with more tools."},
                {"t": "band", "md": "**Splitting for conceptual tidiness is the common mistake.** "
                                    "Roles named *Researcher*, *Writer*, and *Critic* feel "
                                    "organised and typically cost three times as much as one "
                                    "agent doing the same work with the same tools."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Multi-agent · the honest arithmetic",
            "title": "What each additional agent costs",
            "blocks": [
                {"t": "table",
                 "head": ["Cost", "Why it grows"],
                 "widths": [26, 74],
                 "rows": [
                     ["**Tokens**",
                      "Every hand-off re-states context. A supervisor that summarises for three "
                      "specialists pays for that summary three times, plus its own reasoning."],
                     ["**Latency**",
                      "Sequential hand-offs add up. Parallel ones only help if the subtasks are "
                      "genuinely independent."],
                     ["**Failure surface**",
                      "Each agent can loop, drift, or hallucinate independently — **and one "
                      "specialist's wrong answer becomes another's trusted input.**"],
                     ["**Evaluation**",
                      "You now need per-agent evals *and* end-to-end evals, because a system "
                      "that is right overall can be right for the wrong reasons."],
                 ]},
                {"t": "p", "md": "A finding worth carrying: decompose a task into five or six "
                                 "specialists and it is common for **only one or two to justify "
                                 "their existence** once the traces are read."},
            ],
            "notes": "This is the slide to be blunt on. The room will have seen impressive "
                     "multi-agent diagrams; almost none of them come with a cost table.",
        },

        {
            "type": "slide",
            "kicker": "Multi-agent · when it does pay",
            "title": "Three shapes where splitting is right",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔐", "h": "Different permissions", "style": "good",
                     "p": "One agent may read customer records; another may write to the "
                          "ledger. **Splitting is how you keep those capabilities apart** — a "
                          "security boundary, not a stylistic one."},
                    {"ico": "⚡", "h": "Genuine parallelism", "style": "good",
                     "p": "Twenty documents to analyse independently. Fan out, collect, "
                          "assemble. The latency win is real and the contexts do not interact."},
                    {"ico": "📚", "h": "Context that will not fit", "style": "good",
                     "p": "A task whose inputs genuinely exceed the window. Splitting is a "
                          "**memory strategy** here, and the supervisor's summaries are the "
                          "compression."},
                ]},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "05", "title": "Evaluation and operation",
         "lead": "How you know it works, and what you do when it stops."},

        {
            "type": "slide",
            "kicker": "Evaluation",
            "title": "You cannot test this the way you test code",
            "blocks": [
                {"t": "p", "md": "The system is non-deterministic, the output space is open, and "
                                 "the correct answer is often a judgement call. Standard unit "
                                 "testing does not reach any of that."},
                {"t": "mmd", "id": "hendri-eval", "src": MMD_EVAL,
                 "cap": "Traces first. Everything downstream is built on them."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Evaluation · the three levels",
            "title": "What each level catches",
            "blocks": [
                {"t": "table",
                 "head": ["Level", "What it asserts", "What it misses"],
                 "widths": [24, 40, 36],
                 "rows": [
                     ["**Unit evals**",
                      "Given this input, the right tool is called with the right arguments.",
                      "Whether the sequence of correct calls produces a useful outcome."],
                     ["**End-to-end evals**",
                      "Given this task, the final outcome matches a known good one.",
                      "*Why* it succeeded — a right answer for the wrong reason still passes."],
                     ["**Human review**",
                      "Whether the output is actually good, by a standard you cannot encode.",
                      "Coverage. It is sampled, so it finds classes of failure, not instances."],
                 ]},
                {"t": "band", "md": "Run all three **before every prompt change, every model "
                                    "upgrade, and every tool change**. In this domain a prompt "
                                    "edit is a code change with no type checker behind it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Evaluation · building the set",
            "title": "Where the evaluation tasks come from",
            "blocks": [
                {"t": "steps", "items": [
                    "**Start with twenty real requests**, taken from whatever the process looks "
                    "like today. Not twenty imagined ones.",
                    "**Write down the good outcome for each** — before you build anything, while "
                    "you are still honest about what good means.",
                    "**Add every failure you observe** in development, permanently. This is how "
                    "the set grows, and it is why it is worth versioning.",
                    "**Include the boring cases.** A set made only of hard cases will let you "
                    "ship something that fails the easy ones.",
                    "**Keep a held-out slice** you do not look at while iterating. Chapter 18's "
                    "warning about validation-set overfitting applies here exactly.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operation",
            "title": "Four failure modes, and how each announces itself",
            "blocks": [
                {"t": "mmd", "id": "hendri-failure", "src": MMD_FAILURE,
                 "cap": "None of these throw an exception. All of them show in a trace."},
                {"t": "p", "md": "Set alerts on the **shape** of runs, not only on errors: mean "
                                 "steps per request, cost per request, tool-call repetition rate, "
                                 "and escalation rate. **A rising step count is usually the first "
                                 "visible sign that something upstream changed.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operation · deployment",
            "title": "The autonomy ladder",
            "blocks": [
                {"t": "mmd", "id": "hendri-maturity", "src": MMD_MATURITY,
                 "cap": "Move up a rung only with evidence from the evaluation harness."},
                {"t": "band", "md": "At **L3**, the question that matters is not *how good is it?* "
                                    "but ==what is the blast radius when it is wrong?== Define "
                                    "that boundary in code — spend limits, record scopes, "
                                    "reversibility — not in the prompt."},
            ],
        },

        # ------------------------------------------------------------------
        {"type": "section", "num": "06", "title": "Cases",
         "lead": "What we will build, and what each one is chosen to teach."},

        {
            "type": "slide",
            "kicker": "Cases",
            "title": "Single-agent cases",
            "blocks": [
                {"t": "table",
                 "head": ["Case", "What it teaches"],
                 "widths": [32, 68],
                 "rows": [
                     ["**Document Q&A with citations**",
                      "Retrieval as a tool, not as a preprocessing step. Grounding, and how to "
                      "make a citation verifiable rather than decorative."],
                     ["**Structured extraction from messy input**",
                      "Schema-constrained output, validation on arrival, and what to do with the "
                      "20% that fails validation."],
                     ["**Internal API assistant**",
                      "Tool design under real permissions. Read tools autonomous, write tools "
                      "gated. Identity propagation."],
                     ["**Data analysis with code execution**",
                      "The most powerful and most dangerous tool there is. Sandboxing, resource "
                      "limits, and why the output must still be checked."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Cases",
            "title": "Multi-agent cases",
            "blocks": [
                {"t": "table",
                 "head": ["Case", "What it teaches"],
                 "widths": [32, 68],
                 "rows": [
                     ["**Parallel document triage**",
                      "The clean case for fan-out: independent subtasks, real latency win, no "
                      "shared context. The one that unambiguously justifies splitting."],
                     ["**Research and draft with a separate reviewer**",
                      "The *tidy* decomposition — and a cost comparison against one agent doing "
                      "both, run honestly."],
                     ["**Cross-permission workflow**",
                      "Two agents that must not share capabilities. Splitting as a security "
                      "boundary."],
                     ["**Escalation to a human**",
                      "The hand-off nobody designs and everybody needs. What state goes with it, "
                      "and how the human hands it back."],
                 ]},
                {"t": "p", "md": "All four ship in the **ai-agentic-demo** monorepo, each with a "
                                 "trace viewer and an evaluation set, so the cost and quality "
                                 "claims on these slides can be checked rather than believed."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Cases · the exercise",
            "title": "What you will do with them",
            "blocks": [
                {"t": "steps", "items": [
                    "**Bring a process from your own work** — one that exists, with real inputs "
                    "you can describe.",
                    "**Classify it** using the operational test from section 01. Most will be "
                    "workflows, and that is the correct answer.",
                    "**Write the twenty evaluation cases** before writing any prompt.",
                    "**Build the smallest version** that could work: one agent, the fewest tools "
                    "that cover the task.",
                    "**Run it, read the traces, and report what surprised you.** That last step "
                    "is the assessment.",
                ]},
                {"t": "band", "md": "The deliverable is not a working agent. It is **a defensible "
                                    "answer to whether you should have built one** — supported by "
                                    "traces, costs, and an evaluation set."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this module",
            "blocks": [
                {"t": "steps", "items": [
                    "**Who decides the next step** is the question that separates a workflow "
                    "from an agent. Most things are workflows; build them as workflows.",
                    "**The loop needs more than one exit.** Goal, steps, tokens, time, "
                    "repetition, and an escalation path.",
                    "**The model never touches anything.** It emits a structured intention; your "
                    "code decides whether to honour it. Every permission boundary lives there.",
                    "**Read tools and write tools are different risks**, and should have "
                    "different defaults from day one.",
                    "**Memory is four things, not one.** Add each only when an observed failure "
                    "demands it.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this module (2 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**Guardrails and observability are layers**, not features. Traces come "
                    "before everything else, because nothing here reproduces.",
                    "**Three questions before splitting into multiple agents** — different "
                    "permissions, real parallelism, or context that will not fit. Tidiness is "
                    "not one of them.",
                    "**Evaluate at three levels** — unit, end-to-end, and sampled human review — "
                    "and run all three before any prompt or model change.",
                    "**Move up the autonomy ladder on evidence**, and define the blast radius in "
                    "code rather than in the prompt.",
                ]},
                {"t": "links", "items": [
                    {"k": "REPO", "ic": "🐙", "v": "ai-agentic-demo",
                     "href": "https://github.com/situkangsayur/ai-agentic-demo"},
                    {"k": "BACK", "ic": "⬅", "v": "Chapter 16 — Text generation",
                     "href": "../ch16/index.html"},
                ]},
            ],
        },
    ],
}
