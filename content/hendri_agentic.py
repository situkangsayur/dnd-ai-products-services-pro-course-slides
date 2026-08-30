# -*- coding: utf-8 -*-
"""Module deck — Agentic AI.

Delivered after the LLM module. That module ends with a model that has been
fine-tuned, given retrieval, and wrapped in guardrails; this one asks what you
build around such a model so that it can *act*, and what it costs to let it.

The through-line is deliberately deflationary and it is load-bearing: most
problems brought to "agents" are workflows, most multi-agent designs do not
survive a cost table, and the engineering that matters is in tools, memory,
interfaces, evaluation and compliance rather than in prompts.

Every regulatory and architectural claim in here is traceable to a source in
``references/REFERENCES.md``, which was checked against the primary documents
rather than against summaries of them.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from course import COURSE  # noqa: E402
from diagrams import agent_loop  # noqa: E402


# ---------------------------------------------------------------- diagrams --

MMD_WHERE = """
flowchart LR
  A["<b>Topic 3</b><br/>Deep learning<br/><small>ch. 1-20</small>"]
  B["<b>Topic 4 - Viny</b><br/>LLM<br/><small>fine-tuning, RAG,<br/>re-rankers, guardrails</small>"]
  C["<b>Topic 6 - this module</b><br/>Agentic AI<br/><small>tools, autonomy,<br/>interfaces, compliance</small>"]
  A --> B --> C
  B -. "a model that answers" .-> C
  C -. "a system that acts" .-> D["Production"]
"""

MMD_RN_AGENT = """
flowchart LR
  E["<b>Environment</b>"]
  S["<b>Sensors</b><br/><small>percepts</small>"]
  F["<b>Agent function</b><br/><small>percept history -&gt; action</small>"]
  AC["<b>Actuators</b><br/><small>actions</small>"]
  E --> S --> F --> AC --> E
"""

MMD_RN_TYPES = """
flowchart TB
  A["<b>1. Simple reflex</b><br/><small>condition-action rules;<br/>no memory</small>"]
  B["<b>2. Model-based reflex</b><br/><small>keeps internal state<br/>of the world</small>"]
  C["<b>3. Goal-based</b><br/><small>searches and plans<br/>toward a goal</small>"]
  D["<b>4. Utility-based</b><br/><small>trades off between<br/>competing goals</small>"]
  L["<b>5. Learning</b><br/><small>improves its own<br/>components from experience</small>"]
  A --> B --> C --> D --> L
"""

MMD_LADDER = """
flowchart TB
  A["<b>AI</b><br/><small>a model that maps<br/>input to output</small>"]
  B["<b>AI workflow</b><br/><small>fixed steps you wrote,<br/>some of which call a model</small>"]
  C["<b>AI agent</b><br/><small>the model chooses which<br/>tool to call, in a loop</small>"]
  D["<b>Agentic system</b><br/><small>agent + memory + planning<br/>+ control over its own steps</small>"]
  E["<b>Multi-agent system</b><br/><small>several agents with distinct<br/>roles, coordinating</small>"]
  A --> B --> C --> D --> E
"""

MMD_WHO_DECIDES = """
flowchart TB
  Q["<b>Who decides the next step?</b>"]
  W["<b>You do, at design time</b><br/><small>control flow lives in your code</small>"]
  A["<b>The model does, at run time</b><br/><small>control flow lives in the prompt<br/>and the tool results</small>"]
  WR["That is a <b>workflow</b><br/><small>testable, cheap, predictable</small>"]
  AR["That is an <b>agent</b><br/><small>flexible, expensive, hard to test</small>"]
  Q --> W --> WR
  Q --> A --> AR
"""

MMD_WF_PATTERNS = """
flowchart TB
  P1["<b>1. Prompt chaining</b><br/><small>step feeds the next;<br/>gate between them</small>"]
  P2["<b>2. Routing</b><br/><small>classify, then send to a<br/>specialised path</small>"]
  P3["<b>3. Parallelisation</b><br/><small>sectioning, or voting<br/>for confidence</small>"]
  P4["<b>4. Orchestrator-workers</b><br/><small>central model splits and<br/>delegates dynamically</small>"]
  P5["<b>5. Evaluator-optimiser</b><br/><small>one generates, one critiques,<br/>loop until good</small>"]
  W["<b>Workflows</b><br/><small>predefined code paths</small>"]
  AG["<b>Agents</b><br/><small>the model directs itself</small>"]
  W --> P1
  W --> P2
  W --> P3
  W --> P4
  W --> P5
  P5 -. "add open-ended tool choice" .-> AG
"""

MMD_TOOL = """
flowchart LR
  S["<b>Tool schema</b><br/><small>name, description,<br/>typed parameters</small>"]
  M["<b>Model</b>"]
  CALL["<b>Tool call</b><br/><small>structured, validated</small>"]
  EX["<b>Your code</b><br/><small>the only thing that<br/>touches a real system</small>"]
  R["<b>Result</b><br/><small>appended to the context</small>"]
  S --> M --> CALL --> EX --> R --> M
"""

MMD_MEMORY = """
flowchart TB
  W["<b>Working</b><br/><small>the context window<br/>-- this turn only</small>"]
  E["<b>Episodic</b><br/><small>past runs<br/>-- a transcript store</small>"]
  S["<b>Semantic</b><br/><small>facts and documents<br/>-- vector or keyword index</small>"]
  P["<b>Procedural</b><br/><small>learned routines<br/>-- prompts, tools, playbooks</small>"]
  A["The agent's next step"]
  W --> A
  E --> A
  S --> A
  P --> A
"""

MMD_MATURITY = """
flowchart TB
  M1["<b>Minimum</b><br/><small>model + tools + a loop<br/>+ one exit condition</small>"]
  M2["<b>Best practice</b><br/><small>+ budgets, tracing, evals,<br/>guardrails, approval gate</small>"]
  M3["<b>Production ready</b><br/><small>+ identity, audit trail, DR,<br/>cost control, compliance,<br/>on-call, rollback</small>"]
  M1 --> M2 --> M3
  M1 -. "a demo" .-> D1["fine for a pilot"]
  M2 -. "an internal tool" .-> D2["fine for staff"]
  M3 -. "a regulated product" .-> D3["fine for customers"]
"""

MMD_STACK = """
flowchart TB
  MOD["<b>Model layer</b><br/><small>hosted API, or self-hosted<br/>open weights</small>"]
  ORCH["<b>Orchestration</b><br/><small>the loop, routing,<br/>retries, budgets</small>"]
  TOOLS["<b>Tools</b><br/><small>your APIs, databases,<br/>search, ML models, code</small>"]
  MEM["<b>Memory</b><br/><small>vector store, transcripts,<br/>document store</small>"]
  GUARD["<b>Guardrails</b><br/><small>input, tool-call, output;<br/>approval gates</small>"]
  OBS["<b>Observability</b><br/><small>traces, evals, cost,<br/>human review queue</small>"]
  GOV["<b>Governance</b><br/><small>identity, audit, retention,<br/>model registry</small>"]
  MOD --> ORCH
  TOOLS --> ORCH
  MEM --> ORCH
  ORCH --> GUARD --> OBS --> GOV
"""

MMD_INTERFACES = """
flowchart TB
  H["<b>Human to machine</b>"]
  H1["Chat / assistant"]
  H2["Approval gate<br/><small>the write-tool queue</small>"]
  H3["Escalation<br/><small>hand-off with state</small>"]
  H4["Audit review<br/><small>reading traces</small>"]
  M["<b>Machine to machine</b>"]
  M1["<b>MCP</b><br/><small>agent reaches INWARD<br/>to tools and data</small>"]
  M2["<b>A2A</b><br/><small>agents coordinate ACROSS<br/>organisational boundaries</small>"]
  M3["REST / gRPC<br/><small>your existing services</small>"]
  M4["Events / webhooks<br/><small>asynchronous triggers</small>"]
  H --> H1
  H --> H2
  H --> H3
  H --> H4
  M --> M1
  M --> M2
  M --> M3
  M --> M4
"""

MMD_MCP_A2A = """
flowchart TB
  U["User"]
  A1["<b>Agent A</b><br/><small>your bank</small>"]
  A2["<b>Agent B</b><br/><small>a partner</small>"]
  T1["Database"]
  T2["Credit scoring model"]
  T3["Document store"]
  U --> A1
  A1 -- "A2A: across organisations" --> A2
  A1 -- "MCP" --> T1
  A1 -- "MCP" --> T2
  A1 -- "MCP" --> T3
"""

MMD_REG_STACK = """
flowchart TB
  L1["<b>UU PDP</b><br/><small>UU 27/2022 -- personal data:<br/>lawful basis, rights, transfer</small>"]
  L2["<b>OJK</b><br/><small>AI governance 2025,<br/>POJK 11/2022, SEOJK 29/2022</small>"]
  L3["<b>ISO/IEC 27001:2022</b><br/><small>the ISMS everything sits in</small>"]
  L4["<b>ISO/IEC 27701:2025</b><br/><small>privacy management,<br/>now standalone</small>"]
  L5["<b>ISO/IEC 42001:2023</b><br/><small>AI management system</small>"]
  SYS["<b>Your agentic system</b>"]
  L1 --> SYS
  L2 --> SYS
  L3 --> SYS
  L4 --> SYS
  L5 --> SYS
"""

MMD_COMPLY = """
flowchart LR
  C1["<b>Decide</b><br/><small>lawful basis, data classes,<br/>residency, retention</small>"]
  C2["<b>Design in</b><br/><small>minimise at the tool,<br/>redact at the boundary,<br/>gate every write</small>"]
  C3["<b>Evidence</b><br/><small>traces = the audit trail;<br/>evals = the control test</small>"]
  C4["<b>Review</b><br/><small>DPIA, model registry,<br/>periodic re-approval</small>"]
  C1 --> C2 --> C3 --> C4
  C4 -. "findings" .-> C1
"""

MMD_SYSDESIGN = """
flowchart TB
  APP["<b>Mobile app</b><br/><small>Flutter · field officer</small>"]
  GW["<b>API gateway</b><br/><small>authn, rate limit, WAF</small>"]
  ORCH["<b>Agent service</b><br/><small>loop, budgets, guardrails</small>"]
  MCP["<b>MCP servers</b>"]
  T1["Customer REST API<br/><small>demo service</small>"]
  T2["Credit scoring<br/><small>classical ML, not an LLM</small>"]
  T3["Analytics<br/><small>SQL over transactions</small>"]
  T4["Policy retrieval<br/><small>regulation corpus</small>"]
  LLM["Model provider"]
  OBS["<b>Traces, evals, audit log</b>"]
  HUM["<b>Approval queue</b><br/><small>human decides the credit</small>"]
  APP --> GW --> ORCH
  ORCH --> LLM
  ORCH --> MCP
  MCP --> T1
  MCP --> T2
  MCP --> T3
  MCP --> T4
  ORCH --> OBS
  ORCH --> HUM

  %% The four tools fan out from one node, and an unconstrained fan makes the
  %% drawing exactly as tall as the fan is wide. Boxing them into one row keeps
  %% the figure inside the space a slide gives it -- and says something true
  %% besides: they are siblings behind one door, not a hierarchy.
  subgraph TOOLS["Behind the one door"]
    direction LR
    T1
    T2
    T3
    T4
  end
"""

MMD_DEPLOY = """
flowchart TB
  subgraph EDGE["Public edge"]
    direction LR
    CDN["CDN / WAF"]
    GW2["API gateway"]
  end
  subgraph PRIV["Private subnet -- data residency: Indonesia"]
    direction LR
    SVC["Agent service<br/><small>containers, autoscaled</small>"]
    MCPS["MCP servers"]
    ML["ML serving<br/><small>credit model</small>"]
    DB[("Postgres")]
    VEC[("Vector store")]
    OBJ[("Object store<br/>traces, documents")]
  end
  subgraph OUT["Egress, allow-listed"]
    PROV["Model provider"]
  end
  CDN --> GW2 --> SVC
  SVC --> MCPS --> ML
  MCPS --> DB
  MCPS --> VEC
  SVC --> OBJ
  SVC -. "TLS, no PII" .-> PROV
"""

MMD_CASE_FLOW = """
flowchart TB
  S1["<b>1.</b> Officer photographs the<br/>application in the field"]
  S2["<b>2.</b> Agent pulls customer and<br/>transaction data<br/><small>REST API, via MCP</small>"]
  S3["<b>3.</b> Agent runs the analysis<br/><small>SQL over 12 months</small>"]
  S4["<b>4.</b> Agent calls the credit model<br/><small>classical ML, returns a score<br/>and the reason codes</small>"]
  S5["<b>5.</b> Agent retrieves the policy<br/><small>which rules apply to this case</small>"]
  S6["<b>6.</b> Agent drafts a recommendation<br/><small>with every figure cited</small>"]
  S7["<b>7.</b> HUMAN decides<br/><small>the agent never approves credit</small>"]
  S8["<b>8.</b> Trace written to the audit log"]
  S1 --> S2 --> S3 --> S4
  S4 --> S5
  S5 --> S6 --> S7 --> S8

  %% Two rows of four. Eight steps in one line comes out 2441px wide and eight
  %% in one column 1110px tall; neither fits the space a slide gives a figure,
  %% and the renderer can only choose between the two -- it cannot invent a
  %% third shape. Subgraphs do that here.
  subgraph ROW1[" "]
    direction LR
    S1
    S2
    S3
    S4
  end
  subgraph ROW2[" "]
    direction LR
    S5
    S6
    S7
    S8
  end
"""

MMD_NOCODE = """
flowchart TB
  Q["How much will this change,<br/>and who maintains it?"]
  N["<b>No-code / low-code</b><br/><small>n8n, Dify, Flowise, Langflow,<br/>Make, Power Automate,<br/>Coze, Zapier Agents</small>"]
  C["<b>Code</b><br/><small>SDK + your own repo</small>"]
  NR["Fast to a demo.<br/>Hard to test, version,<br/>review, or audit."]
  CR["Slower to start.<br/>Diffable, testable,<br/>auditable, portable."]
  Q --> N --> NR
  Q --> C --> CR
"""

MMD_FAILURE = """
flowchart TB
  L["<b>Looping</b><br/><small>same tool, over and over</small>"]
  D["<b>Drift</b><br/><small>the goal quietly changes</small>"]
  H["<b>Confident wrong answers</b><br/><small>a hallucinated result<br/>treated as fact</small>"]
  C["<b>Cost blowout</b><br/><small>no budget, no cap</small>"]
  I["<b>Injection</b><br/><small>instructions inside<br/>retrieved content</small>"]
  F["<b>None of these throw.<br/>All of them show in a trace.</b>"]
  L --> F
  D --> F
  H --> F
  C --> F
  I --> F
"""

MMD_AUTONOMY = """
flowchart LR
  L0["<b>L0</b> Assisted<br/><small>human works,<br/>model drafts</small>"]
  L1["<b>L1</b> Workflow<br/><small>fixed steps,<br/>model in some</small>"]
  L2["<b>L2</b> Supervised agent<br/><small>agent acts, human<br/>approves each write</small>"]
  L3["<b>L3</b> Bounded autonomy<br/><small>agent acts alone inside<br/>a defined blast radius</small>"]
  L0 --> L1 --> L2 --> L3
"""


NB = []

REF = "references/REFERENCES.md"

RESOURCES = [
    {"kind": "site", "label": "Course home", "href": "../../index.html"},
    {"kind": "github", "label": "ai-agentic-demo — single-agent and multi-agent cases",
     "href": "https://github.com/situkangsayur/ai-agentic-demo"},
    {"kind": "book", "label": "Verified reference list (books, papers, standards, regulation)",
     "href": "https://github.com/situkangsayur/dnd-ai-products-services-pro-course-slides/blob/main/references/REFERENCES.md"},
    {"kind": "paper", "label": "OJK — Tata Kelola Kecerdasan Artifisial Perbankan Indonesia (2025)",
     "href": "https://ojk.go.id/id/Publikasi/Roadmap-dan-Pedoman/Perbankan/Pages/Tata-Kelola-Kecerdasan-Artifisial-Perbankan-Indonesia.aspx"},
]

DECK = {
    "id": "hendri-agentic",
    "kind": "module",
    "number": None,
    "title": "Agentic AI",
    "subtitle": "From the textbook definition of an agent to a system a regulator "
                "will accept — what to build, what to buy, and when not to build "
                "an agent at all.",
    "source": "Module material for " + COURSE["title"],
    "source_url": "https://hendrikarisma.my.id",
    "duration": "6 hours (4 sessions)",
    "presenter": {"name": "Hendri Karisma, M.T.", "role": "Teaching Assistant"},
    "resources": RESOURCES,
    "objectives": [
        "Trace the word *agent* from **Russell & Norvig** to its current use, and "
        "say precisely what has and has not changed.",
        "Apply one **operational test** to decide whether a given system is a "
        "workflow or an agent — and why most are workflows.",
        "Name the **five workflow patterns** and the point at which each stops "
        "being enough.",
        "Specify the components of an agentic system at three levels: "
        "**minimum, best practice, production ready**.",
        "Choose a **tech stack** across easy / medium / production tiers, "
        "commercial and open source, and justify it on properties you can verify.",
        "Judge **no-code platforms** against code on the four things that "
        "actually differ.",
        "Design both interfaces: **machine-to-machine** (MCP, A2A, REST, events) "
        "and **human-to-machine** (approval, escalation, audit).",
        "Map a deployment against **UU PDP, OJK, ISO/IEC 27001:2022 and "
        "27701:2025**, and produce the evidence an auditor asks for.",
        "Produce a **system design and a deployment design**, including where "
        "the data is allowed to be.",
        "Walk one end-to-end case: a Flutter app on Android and iOS, a REST service, a classical "
        "ML model behind MCP, and a human who makes the decision.",
    ],
    "slides": [
        {"type": "title"},

        # ==============================================================
        {"type": "section", "num": "01", "title": "Where this module sits",
         "lead": "The LLM module ended with a model that answers. This one is about "
                 "a system that acts."},

        {
            "type": "slide",
            "kicker": "Positioning",
            "title": "This continues directly from the LLM module",
            "blocks": [
                {"t": "p", "md": "Viny's module ends with a model that has been "
                                 "**fine-tuned**, given **retrieval**, re-ranked, and "
                                 "wrapped in **guardrails**. It answers well."},
                {"t": "mmd", "id": "hendri-where", "src": MMD_WHERE,
                 "cap": "Answering is not acting. Everything in this module is about "
                        "the gap between the two."},
                {"t": "p", "md": "Nothing here makes the model more capable. Everything "
                                 "here is about **what the model is connected to**, and "
                                 "about ==what happens when it is wrong==."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Positioning",
            "title": "What you already have, and what is still missing",
            "blocks": [
                {"t": "table",
                 "head": ["From the LLM module", "Still missing"],
                 "widths": [50, 50],
                 "rows": [
                     ["A model tuned to your domain",
                      "A way for it to **do** anything"],
                     ["Retrieval over your documents",
                      "Retrieval as a **choice the model makes**, not a fixed step"],
                     ["Guardrails on input and output",
                      "A guardrail on the **action** — the one that moves money"],
                     ["A good answer",
                      "A record of **how** it got there, that an auditor accepts"],
                 ]},
                {"t": "band", "md": "The last row is the one that decides whether any of "
                                    "this reaches production in a regulated institution."},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "02", "title": "What an agent is",
         "lead": "The word is older than the hype, and the old definition is the "
                 "useful one."},

        {
            "type": "slide",
            "kicker": "Russell & Norvig, ch. 2",
            "title": "The definition that predates all of this",
            "blocks": [
                {"t": "quote", "md": "An **agent** is anything that can be viewed as "
                                     "perceiving its environment through **sensors** and "
                                     "acting upon that environment through **actuators**.",
                 "cite": "Russell & Norvig, Artificial Intelligence: A Modern Approach, "
                         "4th ed., ch. 2"},
                {"t": "mmd", "id": "hendri-rn", "src": MMD_RN_AGENT,
                 "cap": "The agent function maps a percept history to an action. Nothing "
                        "in it requires a language model."},
                {"t": "p", "md": "A thermostat satisfies this. So does a list-sorting "
                                 "program. **The definition is broad on purpose** — which "
                                 "is why it needs the next slide."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Russell & Norvig, ch. 2",
            "title": "PEAS: how to specify one before building it",
            "blocks": [
                {"t": "p", "md": "Before any architecture, the textbook asks for four "
                                 "things. It is still the fastest way to find out whether "
                                 "a proposed agent is well posed."},
                {"t": "table",
                 "head": ["", "Meaning", "Our credit case"],
                 "widths": [16, 40, 44],
                 "rows": [
                     ["**P**erformance", "How is success measured?",
                      "Correct recommendation rate; time to decision; zero "
                      "unapproved writes"],
                     ["**E**nvironment", "What does it operate in?",
                      "Core banking APIs, transaction history, policy corpus, a "
                      "field officer"],
                     ["**A**ctuators", "What can it do?",
                      "Read data, run a model, retrieve policy, **draft** — never "
                      "approve"],
                     ["**S**ensors", "What can it perceive?",
                      "Application form, customer record, 12 months of transactions"],
                 ]},
                {"t": "p", "md": "If you cannot fill the P row with a number, you do not "
                                 "yet have a project — you have an intention."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Russell & Norvig, ch. 2",
            "title": "Five agent types, and where LLM agents actually sit",
            "blocks": [
                {"t": "mmd", "id": "hendri-rn-types", "src": MMD_RN_TYPES,
                 "cap": "The classical taxonomy, in increasing order of sophistication."},
                {"t": "p", "md": "A tool-calling LLM agent is **goal-based**: it searches "
                                 "over actions toward a stated goal. It is not "
                                 "**utility-based** — it has no explicit utility function "
                                 "to trade off competing goals — and it is not a "
                                 "**learning agent**: it does not improve its own "
                                 "components from experience within a run."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Definition",
            "title": "The modern definition, stated carefully",
            "blocks": [
                {"t": "lead", "md": "An **agentic system** is one in which a model "
                                    "decides, at run time, which actions to take and in "
                                    "what order, against tools it did not choose and "
                                    "within limits it cannot change."},
                {"t": "p", "md": "Three clauses, each doing work:\n\n"
                                 "**decides at run time** — separates it from a workflow.\n\n"
                                 "**tools it did not choose** — you supply the action "
                                 "space; that is your control surface.\n\n"
                                 "**limits it cannot change** — budgets, permissions and "
                                 "approval gates sit outside the model."},
                {"t": "band", "md": "Notice what is *not* in the definition: "
                                    "intelligence, understanding, reasoning, or "
                                    "autonomy as a virtue. ==Autonomy is a cost, "
                                    "purchased when flexibility is worth more than "
                                    "predictability.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Vocabulary",
            "title": "Five terms, in increasing order of autonomy",
            "blocks": [
                {"t": "mmd", "id": "hendri-ladder", "src": MMD_LADDER,
                 "cap": "Each step gives the model more say over what happens next — and "
                        "costs more to test."},
                {"t": "p", "md": "Vendor material uses these interchangeably. They are "
                                 "not interchangeable: the difference between them is a "
                                 "**cost** difference, a **testability** difference, and "
                                 "a **risk** difference."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Which is which",
            "title": "Agentic, or not? Six systems",
            "blocks": [
                {"t": "table",
                 "head": ["System", "Agentic?", "Why"],
                 "widths": [34, 14, 52],
                 "rows": [
                     ["A chatbot answering from a RAG index", "**No**",
                      "One fixed retrieve-then-answer path. No decision about what to do."],
                     ["A thermostat", "**No**",
                      "An agent by the textbook definition, but a simple-reflex one; "
                      "no goal, no choice."],
                     ["Document classifier routing to one of five queues", "**No**",
                      "That is routing — a workflow pattern. The path set is fixed."],
                     ["Model that decides whether to search, then which of nine tools", "**Yes**",
                      "The control flow is chosen at run time from a supplied action space."],
                     ["Coding assistant that runs tests, reads failures, retries", "**Yes**",
                      "Observes its own results and revises. This is the loop."],
                     ["n8n flow calling an LLM at step 3 of 7", "**No**",
                      "A workflow with a model in it. Nothing wrong with that — it is "
                      "usually the right answer."],
                 ]},
            ],
            "notes": "Ask the room for their own system before showing the verdicts. "
                     "Most people put their own work one rung higher than it belongs.",
        },

        # ==============================================================
        {"type": "section", "num": "03", "title": "Workflow versus agent",
         "lead": "One question separates them, and it decides your cost, your tests, "
                 "and your risk."},

        {
            "type": "slide",
            "kicker": "The operational test",
            "title": "Who decides the next step?",
            "blocks": [
                {"t": "mmd", "id": "hendri-who", "src": MMD_WHO_DECIDES,
                 "cap": "Everything else — the model, the tools, the prompt — can be "
                        "identical."},
                {"t": "band", "md": "**If you can draw the flowchart in advance and it "
                                    "does not change per request, you have a workflow.** "
                                    "Build it as one. It will be cheaper, faster, and "
                                    "you will be able to test it."},
            ],
            "notes": "Press on this. Most systems described as agents in industry talks "
                     "are workflows with a model in one or two boxes, and that is a "
                     "compliment rather than a criticism.",
        },

        {
            "type": "slide",
            "kicker": "Anthropic, Building Effective Agents (2024)",
            "title": "Five workflow patterns before you reach for an agent",
            "blocks": [
                {"t": "mmd", "id": "hendri-wf", "src": MMD_WF_PATTERNS,
                 "cap": "Workflows orchestrate models through predefined code paths; "
                        "agents let the model direct itself."},
                {"t": "p", "md": "The published guidance is explicit: **start simple, and "
                                 "add agency only when flexibility outweighs latency, "
                                 "cost, and compounding error.** It also warns against "
                                 "reaching for a framework first, because the abstraction "
                                 "hides the prompts and responses you need to debug."},
            ],
        },

        {
            "type": "slide",
            "kicker": "The five, in practice",
            "title": "When each pattern is the right answer",
            "blocks": [
                {"t": "table",
                 "head": ["Pattern", "Use it when", "Stops working when"],
                 "widths": [22, 39, 39],
                 "rows": [
                     ["**Prompt chaining**", "The task decomposes into fixed sequential "
                      "steps", "The steps depend on what earlier steps found"],
                     ["**Routing**", "Inputs fall into known categories needing different "
                      "handling", "A new category appears, or one input needs two paths"],
                     ["**Parallelisation**", "Subtasks are independent, or you want "
                      "several votes", "The subtasks need each other's results"],
                     ["**Orchestrator-workers**", "Subtasks cannot be known in advance",
                      "The orchestration itself becomes the hard part"],
                     ["**Evaluator-optimiser**", "You have a clear criterion and "
                      "iteration helps", "The evaluator is as unreliable as the generator"],
                 ]},
                {"t": "p", "md": "The last row is the one to be careful with: an "
                                 "LLM critiquing an LLM inherits the same blind spots. "
                                 "**Prefer a deterministic evaluator whenever the "
                                 "criterion can be expressed as code.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "The economics",
            "title": "What autonomy actually costs",
            "blocks": [
                {"t": "table",
                 "head": ["", "Workflow", "Agent"],
                 "widths": [26, 37, 37],
                 "rows": [
                     ["Model calls per request", "Known — 1 to 7", "**Unbounded until you bound it**"],
                     ["Latency", "Predictable", "Varies by an order of magnitude"],
                     ["Cost per request", "Computable in advance", "A distribution, with a long tail"],
                     ["Testing", "Ordinary integration tests", "Evaluation sets, and they are never complete"],
                     ["Failure mode", "An exception you can catch", "A plausible wrong answer"],
                     ["Audit story", "The code *is* the flowchart", "The trace is the only record"],
                 ]},
                {"t": "band", "md": "Every row favours the workflow. That is not an "
                                    "argument against agents — it is the **price list**, "
                                    "and you should know it before you pay.",
                 "style": "amber"},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "04", "title": "How an agent runs",
         "lead": "A loop, a tool schema, four kinds of memory, and something that "
                 "makes it stop."},

        {
            "type": "slide",
            "kicker": "The loop",
            "title": "Plan, act, observe, check",
            "blocks": [
                agent_loop("hendri-loop",
                           cap="The loop, and one real run turning inside it — the SME "
                               "credit assessment from the demo repository. Step through "
                               "it: six turns, six tools, and the step budget filling one "
                               "cell at a time.",
                           note="Four boxes and an arrow back is a picture of a while "
                                "statement. What it leaves out is how many times it goes "
                                "round, what each turn costs, and what makes it stop."),
                {"t": "p", "md": "This is the **ReAct** pattern — reason, then act, then "
                                 "read the result and reason again. Published as an ICLR "
                                 "2023 paper and now assumed by every framework in the "
                                 "field. Note where the run ends: **it stopped because it "
                                 "was finished, not because it ran out** — and turn 7, "
                                 "the approval, is not missing from the trace because the "
                                 "prompt was polite about it. There is no such tool."},
            ],
        },

        {
            "type": "slide",
            "kicker": "The loop · the part people forget",
            "title": "Six ways it must be able to stop",
            "blocks": [
                {"t": "p", "md": "A loop with no exit condition is a bug that bills by "
                                 "the token. An agent needs **all** of these, not one."},
                {"t": "bullets", "items": [
                    "**Goal satisfied** — the model says it is done, and something else "
                    "checks that claim.",
                    "**Step budget** — a hard maximum number of iterations.",
                    "**Token or currency budget** — a hard maximum spend per request.",
                    "**Wall-clock timeout** — a hung tool is not the model's problem to "
                    "solve.",
                    "**Repetition detector** — the same tool with the same arguments "
                    "twice running is a loop, not progress.",
                    "**Escalation path** — what happens when the budget is spent and the "
                    "goal is not met. *Silently returning a partial answer is the worst "
                    "option*, because it is indistinguishable from a complete one.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tools",
            "title": "The model never touches anything",
            "blocks": [
                {"t": "mmd", "id": "hendri-tool", "src": MMD_TOOL,
                 "cap": "The model emits a structured request. Your code decides whether "
                        "to honour it."},
                {"t": "band", "md": "This is the most important architectural fact in the "
                                    "module. **The model produces text describing an "
                                    "intention. Your code is the only thing that "
                                    "executes.** Every permission boundary you have lives "
                                    "in that gap."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tools · design",
            "title": "A tool is an API for a reader who forgets everything",
            "blocks": [
                {"t": "steps", "items": [
                    "**Name it for the task, not the system.** `find_customer_by_nik` "
                    "beats `crm_query_v2`.",
                    "**Write the description for the model.** It is the only "
                    "documentation the model gets, and it is re-read on every call.",
                    "**Type every parameter and validate on arrival.** Assume the "
                    "arguments are adversarial, because sometimes they are.",
                    "**Return errors as data, not exceptions.** "
                    "`{\"error\": \"no customer with that NIK\"}` lets the agent recover; "
                    "a thrown exception ends the run.",
                    "**Keep results small.** Every byte a tool returns occupies context "
                    "the model pays to re-read on every later step.",
                ]},
                {"t": "p", "md": "Most *prompt engineering* problems in agent systems are "
                                 "**tool description problems** wearing a disguise."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Tools · the dangerous ones",
            "title": "Read tools and write tools are not the same risk",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "👁", "h": "Read tools", "style": "good",
                     "p": "Search, retrieve, look up, score. A wrong call wastes tokens "
                          "and returns something unhelpful. **Recoverable inside the "
                          "loop.**"},
                    {"ico": "✍", "h": "Write tools", "style": "bad",
                     "p": "Send, delete, transfer, approve, disburse. A wrong call "
                          "**changes the world**, and no amount of later reasoning "
                          "undoes it."},
                ]},
                {"t": "band", "md": "Treat them differently from day one. **Read tools "
                                    "can be autonomous; write tools start behind an "
                                    "approval gate** and only leave it with evidence from "
                                    "your evaluation harness. OWASP names the failure: "
                                    "==excessive agency==.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memory",
            "title": "Four kinds, solving four different problems",
            "blocks": [
                {"t": "mmd", "id": "hendri-memory", "src": MMD_MEMORY,
                 "cap": "Four categories, four pieces of infrastructure."},
                {"t": "p", "md": "The mistake to avoid is treating *memory* as one thing "
                                 "and reaching for a vector database by reflex. **Most "
                                 "agents need working memory managed well and nothing "
                                 "else.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Memory · the operational view",
            "title": "What each one costs you to run",
            "blocks": [
                {"t": "table",
                 "head": ["Kind", "Implementation", "The failure it introduces"],
                 "widths": [18, 38, 44],
                 "rows": [
                     ["**Working**", "The context window itself",
                      "Overflow — old steps fall out and the agent forgets its goal"],
                     ["**Episodic**", "Transcript store, keyed by session",
                      "Replaying stale state as if it were current"],
                     ["**Semantic**", "Vector or keyword index — the LLM module's RAG",
                      "Retrieving confidently irrelevant context, which is worse than none"],
                     ["**Procedural**", "Versioned prompts, tool sets, playbooks",
                      "Drift between what is deployed and what was evaluated"],
                 ]},
                {"t": "p", "md": "Each row is a system to operate, back up, and retain "
                                 "lawfully. **Add them one at a time, and only when a "
                                 "specific observed failure demands it.**"},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "05", "title": "Single agent and multi-agent",
         "lead": "Three questions before you split, and an honest cost table."},

        {
            "type": "slide",
            "kicker": "Multi-agent",
            "title": "The supervisor pattern",
            "blocks": [
                {"t": "p", "md": "A supervisor decomposes the request, routes each part "
                                 "to a specialist with its **own tools and its own "
                                 "context**, and assembles the results."},
                {"t": "p", "md": "This is the pattern in almost every framework, under "
                                 "various names. The variations — peer-to-peer messaging, "
                                 "hierarchies, debate — are **elaborations of it, and each "
                                 "elaboration multiplies the cost**."},
                {"t": "band", "md": "Splitting for conceptual tidiness is the common "
                                    "mistake. Roles named *Researcher*, *Writer* and "
                                    "*Critic* feel organised and typically cost three "
                                    "times one agent doing the same work with the same "
                                    "tools."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Multi-agent · the test",
            "title": "Three questions before you split",
            "blocks": [
                {"t": "steps", "items": [
                    "Do the subtasks need **genuinely different tools or permissions**? "
                    "Then splitting is a *security boundary* — the strongest reason there "
                    "is.",
                    "Can they run **in parallel**? Then the latency win is real, provided "
                    "each subtask is slow enough to hide the coordination overhead.",
                    "Would one context window **overflow** otherwise? Then splitting is a "
                    "*memory strategy* and the summaries are the compression.",
                ]},
                {"t": "band", "md": "**If none of the three is a yes, you want one agent "
                                    "with more tools.** Cheaper, faster, and testable."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Multi-agent · the arithmetic",
            "title": "What each additional agent costs",
            "blocks": [
                {"t": "table",
                 "head": ["Cost", "Why it grows"],
                 "widths": [24, 76],
                 "rows": [
                     ["**Tokens**", "Every hand-off restates context. A supervisor "
                      "summarising for three specialists pays for that summary three "
                      "times, plus its own reasoning."],
                     ["**Latency**", "Sequential hand-offs add up. Parallel ones help "
                      "only if the subtasks are genuinely independent."],
                     ["**Failure surface**", "Each agent can loop, drift or hallucinate "
                      "independently — and **one specialist's wrong answer becomes "
                      "another's trusted input**."],
                     ["**Evaluation**", "Per-agent evals *and* end-to-end evals, because "
                      "a system can be right overall for the wrong reasons."],
                     ["**Audit**", "Every hand-off is a data flow. In a regulated "
                      "setting each one must be justified and logged."],
                 ]},
                {"t": "p", "md": "==Split on evidence, not on tidiness.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "Multi-agent · when it does pay",
            "title": "Three shapes where splitting is right",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🔐", "h": "Different permissions", "style": "good",
                     "p": "One agent may read customer records; another may write to the "
                          "ledger. Splitting is how those capabilities stay apart — a "
                          "**security boundary**, not a style choice."},
                    {"ico": "⚡", "h": "Genuine parallelism", "style": "good",
                     "p": "Twenty documents to analyse independently. Fan out, collect, "
                          "assemble. The contexts never interact."},
                    {"ico": "📚", "h": "Context that will not fit", "style": "good",
                     "p": "Inputs that genuinely exceed the window. Splitting is a "
                          "**memory strategy**, and the supervisor's summaries are the "
                          "compression."},
                ]},
                {"t": "p", "md": "In the credit case later in this module, exactly one of "
                                 "these applies — and it is the first."},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "06", "title": "Components, at three levels",
         "lead": "Minimum, best practice, production ready — and the honest label for "
                 "each."},

        {
            "type": "slide",
            "kicker": "Maturity",
            "title": "Three levels, and what each is actually fit for",
            "blocks": [
                {"t": "mmd", "id": "hendri-maturity", "src": MMD_MATURITY,
                 "cap": "The label on the right is the honest one. A demo is not an "
                        "internal tool, and an internal tool is not a product."},
                {"t": "p", "md": "The common failure is shipping a **minimum** system "
                                 "with **production** language attached to it. The "
                                 "components are the difference, and they are countable."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Level 1",
            "title": "Minimum — what makes it an agent at all",
            "blocks": [
                {"t": "bullets", "items": [
                    "**A model** with tool-calling.",
                    "**A tool set** with typed, validated parameters.",
                    "**A loop** that feeds results back in.",
                    "**One exit condition** — usually a step cap.",
                ]},
                {"t": "p", "md": "That is roughly two hundred lines. It will demo well, "
                                 "and it will surprise you the first time a tool returns "
                                 "something unexpected."},
                {"t": "band", "md": "Fit for: **a pilot you watch while it runs.** Not "
                                    "fit for anything unattended.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Level 2",
            "title": "Best practice — what makes it survivable",
            "blocks": [
                {"t": "table",
                 "head": ["Component", "What it prevents"],
                 "widths": [30, 70],
                 "rows": [
                     ["**Budgets** (all six)", "The loop that bills by the token"],
                     ["**Tracing**", "Being unable to answer *why did it do that*"],
                     ["**Evaluation sets**", "Shipping a prompt change that quietly "
                      "regresses"],
                     ["**Guardrails**", "Injection from retrieved content; secrets in "
                      "the output"],
                     ["**Approval gate on writes**", "The irreversible action nobody "
                      "authorised"],
                     ["**Structured errors**", "A run that ends instead of recovering"],
                 ]},
                {"t": "band", "md": "Fit for: **an internal tool used by trained staff** "
                                    "who can tell when it is wrong."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Level 3",
            "title": "Production ready — what a regulator and an on-call rota require",
            "blocks": [
                {"t": "table",
                 "head": ["Component", "Why it becomes mandatory"],
                 "widths": [32, 68],
                 "rows": [
                     ["**End-user identity propagation**", "Permissions checked against "
                      "the person, not the service account"],
                     ["**Immutable audit trail**", "The trace becomes evidence, so it "
                      "must be tamper-evident and retained"],
                     ["**Data classification and retention**", "UU PDP: you must know "
                      "what personal data went where, and delete it on schedule"],
                     ["**Model registry and versioning**", "Which model, which prompt, "
                      "which tool set produced this decision"],
                     ["**Cost control and quotas**", "Per-tenant, not just global"],
                     ["**Rollback**", "Prompts and tool sets are releases; they need to "
                      "go backwards"],
                     ["**Incident runbook and on-call**", "Someone has to own it at 2 a.m."],
                     ["**DR and residency**", "Where it runs, and where it fails over to"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Architecture",
            "title": "Seven layers, and the two that get skipped",
            "blocks": [
                {"t": "mmd", "id": "hendri-stack", "src": MMD_STACK,
                 "cap": "Guardrails and observability are the two most first attempts "
                        "leave out entirely; governance is the one regulated work adds."},
                {"t": "p", "md": "Read the middle of that diagram carefully. **The "
                                 "orchestration layer is ordinary distributed-systems "
                                 "work** — queueing, retries, budgets, telemetry — and "
                                 "your existing platform team already knows how to do it."},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "07", "title": "Tech stack",
         "lead": "Easy, medium, production — commercial and open source, and what each "
                 "tool is actually for."},

        {
            "type": "slide",
            "kicker": "Choosing",
            "title": "Three tiers, and the question each answers",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "🟢", "h": "Easy", "style": "good",
                     "p": "*Can this idea work at all?* Days to a demo. Hosted "
                          "everything. Accept the lock-in; you are buying information, "
                          "not building a system."},
                    {"ico": "🟡", "h": "Medium", "style": "accent",
                     "p": "*Will this survive real users?* Weeks. Your own repo, an SDK, "
                          "your own tools. Testable and diffable."},
                    {"ico": "🔴", "h": "Production", "style": "warn",
                     "p": "*Will this survive an auditor?* Months. Identity, residency, "
                          "audit trail, DR, cost control. The model is the small part."},
                ]},
                {"t": "band", "md": "**Do not start at the third tier.** Most ideas die "
                                    "at the first, and the cheapest place to learn that "
                                    "an idea is wrong is where it costs days."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Model layer",
            "title": "Hosted or self-hosted, and what actually decides it",
            "blocks": [
                {"t": "table",
                 "head": ["", "Hosted API", "Self-hosted open weights"],
                 "widths": [22, 39, 39],
                 "rows": [
                     ["Examples", "Anthropic Claude, OpenAI, Google Gemini, AWS Bedrock",
                      "Llama, Qwen, Mistral, Gemma — on vLLM, Ollama, TGI"],
                     ["Capability", "Highest available, immediately",
                      "Lower at the same price point, closing"],
                     ["Cost shape", "Per token — scales with usage",
                      "Fixed infrastructure — scales with capacity"],
                     ["Data", "**Leaves your perimeter**", "**Stays inside**"],
                     ["Effort", "An API key", "You now operate a GPU fleet"],
                 ]},
                {"t": "band", "md": "In practice the decision is rarely capability or "
                                    "cost. It is **where the data is allowed to be** — a "
                                    "regulatory question, answered before any code is "
                                    "written.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Orchestration",
            "title": "What each framework is actually for",
            "blocks": [
                {"t": "table",
                 "head": ["Tool", "What it does", "Trade-off"],
                 "widths": [22, 40, 38],
                 "rows": [
                     ["**No framework**", "You write the loop — about 200 lines",
                      "Most control, most legible. Anthropic's own guidance recommends "
                      "starting here."],
                     ["**LangGraph**", "Graph-structured state machine over agent steps",
                      "Explicit control flow, persistence, human-in-the-loop. Concepts "
                      "to learn."],
                     ["**OpenAI Agents SDK**", "Lightweight loop, handoffs, guardrails",
                      "Simple; closest to the provider's own model behaviour."],
                     ["**CrewAI**", "Role-based multi-agent teams",
                      "Fast to a multi-agent demo; encourages splitting before you have "
                      "a reason."],
                     ["**AutoGen**", "Conversational multi-agent, research lineage",
                      "Strong for experiments; a published architecture to argue with."],
                     ["**LlamaIndex**", "Retrieval-first, then agents over it",
                      "Best when the problem is mostly documents."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "The rest of the stack",
            "title": "One row per layer, with the open-source option named",
            "blocks": [
                {"t": "table",
                 "head": ["Layer", "Commercial", "Open source", "What it is for"],
                 "widths": [17, 26, 27, 30],
                 "rows": [
                     ["Vector store", "Pinecone, Weaviate Cloud",
                      "pgvector, Qdrant, Milvus", "Semantic memory and RAG"],
                     ["Tracing / evals", "LangSmith, Braintrust, Langfuse Cloud",
                      "**Langfuse**, Phoenix, OpenLLMetry",
                      "The trace, and regression gates"],
                     ["Gateway", "Portkey, Kong AI",
                      "LiteLLM, Envoy AI Gateway",
                      "One endpoint, key rotation, quotas, failover"],
                     ["Serving", "Bedrock, Vertex, Azure AI",
                      "vLLM, TGI, Ollama", "Running weights you host"],
                     ["Guardrails", "Azure AI Content Safety, Bedrock Guardrails",
                      "NeMo Guardrails, Guardrails AI", "Input, output, topic control"],
                     ["Workflow", "Temporal Cloud, Step Functions",
                      "**Temporal**, Airflow, Prefect",
                      "Durable execution, retries, long-running state"],
                 ]},
                {"t": "p", "md": "The bolded ones are the two worth knowing regardless of "
                                 "budget: **Langfuse** because traces are non-negotiable, "
                                 "and **Temporal** because a long-running agent is a "
                                 "durable-execution problem before it is an AI problem."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Trade-offs, stated plainly",
            "title": "Commercial against open source",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "💳", "h": "Commercial / managed", "style": "",
                     "p": "**For:** fastest to value, support contract, someone else is "
                          "on call, compliance certifications you can point at.\n\n"
                          "**Against:** per-seat or per-token cost that grows with "
                          "success, data leaves your perimeter, migration cost rises "
                          "with adoption."},
                    {"ico": "🔓", "h": "Open source / self-hosted", "style": "",
                     "p": "**For:** data stays inside, no per-token cost, auditable "
                          "end to end, no vendor can deprecate you.\n\n"
                          "**Against:** you are the support contract, you are on call, "
                          "and the certifications are now your evidence to produce."},
                ]},
                {"t": "band", "md": "For a regulated Indonesian institution the honest "
                                    "default is **hybrid**: managed model access through "
                                    "a gateway you control, everything stateful — traces, "
                                    "vectors, documents, the ML models — self-hosted "
                                    "inside the perimeter."},
            ],
        },

        {
            "type": "slide",
            "kicker": "No-code",
            "title": "No-code platforms, and the four things that actually differ",
            "blocks": [
                {"t": "mmd", "id": "hendri-nocode", "src": MMD_NOCODE,
                 "cap": "The question is not which is better. It is how much this will "
                        "change, and who maintains it."},
                {"t": "p", "md": "Worth naming so the room can evaluate them: **n8n, "
                                 "Dify, Flowise, Langflow, Coze, Make, Zapier Agents, "
                                 "Microsoft Power Automate / Copilot Studio, "
                                 "Google Vertex AI Agent Builder**, and the "
                                 "agent-builder features now inside most CRM suites."},
            ],
        },

        {
            "type": "slide",
            "kicker": "No-code · the honest comparison",
            "title": "Where each one wins",
            "blocks": [
                {"t": "table",
                 "head": ["", "No-code platform", "Code"],
                 "widths": [22, 39, 39],
                 "rows": [
                     ["Time to demo", "**Hours.** Genuinely.", "Days"],
                     ["Who can build it", "**A business analyst**", "An engineer"],
                     ["Version control", "A JSON export, if you are lucky",
                      "**Git, with reviewable diffs**"],
                     ["Testing", "Manual, mostly", "**Automated, in CI**"],
                     ["Audit evidence", "Screenshots of a canvas",
                      "**Traces, commits, eval runs**"],
                     ["Cost at scale", "Per-run pricing that surprises you",
                      "Your own infrastructure"],
                 ]},
                {"t": "band", "md": "For a **regulated** deployment the audit row usually "
                                    "settles it. You cannot show an examiner a canvas and "
                                    "call it a change-control record.", "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "No-code · the useful answer",
            "title": "Use both, for different phases",
            "blocks": [
                {"t": "steps", "items": [
                    "**Prototype in no-code.** Find out whether the workflow is even "
                    "right, with the business owner in the room changing it live.",
                    "**Write the evaluation set from the prototype.** The twenty real "
                    "cases it got wrong are worth more than the prototype itself.",
                    "**Rebuild the survivor in code**, against those evaluations, once "
                    "you know the shape is stable.",
                    "**Keep the no-code tool** for the genuinely low-risk automations "
                    "that will never face an auditor.",
                ]},
                {"t": "p", "md": "This is not a compromise. Prototyping is a **different "
                                 "activity** from building, and using one tool for both "
                                 "is what makes prototypes accidentally become "
                                 "production."},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "08", "title": "Interfaces",
         "lead": "Machine to machine, and human to machine. Both need designing."},

        {
            "type": "slide",
            "kicker": "Interfaces",
            "title": "Two directions, four kinds each",
            "blocks": [
                {"t": "mmd", "id": "hendri-interfaces", "src": MMD_INTERFACES,
                 "cap": "The human column is the one that gets designed last and matters "
                        "most in a regulated setting."},
                {"t": "p", "md": "**Machine-to-machine** is the half everyone builds: MCP "
                                 "inward to tools, A2A across organisations, REST and "
                                 "events to everything already running. **Human-to-machine** "
                                 "is the half that gets skipped — approval, escalation, "
                                 "audit — and it is the half a supervisor reads."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Machine to machine",
            "title": "MCP and A2A do different jobs",
            "blocks": [
                {"t": "mmd", "id": "hendri-mcp-a2a", "src": MMD_MCP_A2A,
                 "cap": "MCP reaches inward to tools and data; A2A reaches across to "
                        "other organisations' agents."},
                {"t": "p", "md": "**MCP** — introduced by Anthropic in November 2024, "
                                 "now under the Linux Foundation. JSON-RPC, modelled on "
                                 "the Language Server Protocol. The 2025-06-18 revision "
                                 "added structured tool output, elicitation, and "
                                 "classified MCP servers as OAuth **Resource Servers** "
                                 "with RFC 8707 resource indicators — which is what makes "
                                 "it usable under a real identity model."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Machine to machine",
            "title": "A2A, and why a standard mattered here",
            "blocks": [
                {"t": "p", "md": "**A2A** was created by Google and donated to the Linux "
                                 "Foundation in June 2025, with the project launched at "
                                 "Open Source Summit North America on 23 June 2025. It "
                                 "defines how agents from different vendors **discover "
                                 "each other, exchange messages, and coordinate tasks**."},
                {"t": "table",
                 "head": ["", "MCP", "A2A"],
                 "widths": [22, 39, 39],
                 "rows": [
                     ["Direction", "Agent → tools and data", "Agent ↔ agent"],
                     ["Boundary", "**Inside** your system", "**Across** organisations"],
                     ["Analogy", "A driver interface", "A negotiation protocol"],
                     ["In our case", "Customer API, credit model, analytics, policy",
                      "Not used — one institution, one agent"],
                 ]},
                {"t": "band", "md": "Do not adopt A2A because it exists. **It solves "
                                    "cross-organisational coordination**, and if you have "
                                    "one organisation you have added a protocol and "
                                    "bought nothing."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Human to machine",
            "title": "Four interfaces, and the one nobody designs",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "💬", "h": "Chat / assistant", "style": "",
                     "p": "The one everybody builds. Fine for exploration; a poor fit "
                          "wherever the task has a fixed shape and a form would be "
                          "faster."},
                    {"ico": "✅", "h": "Approval gate", "style": "accent",
                     "p": "Where a write tool waits. Must show **what** will happen, "
                          "**on what evidence**, and offer a real decline. This is a "
                          "product surface, not a dialog box."},
                    {"ico": "🆘", "h": "Escalation", "style": "accent",
                     "p": "The hand-off nobody designs. Must carry what was already "
                          "established so the human does not repeat the work — and must "
                          "come back."},
                    {"ico": "🔍", "h": "Audit review", "style": "accent",
                     "p": "Someone reads traces: sampled, plus every escalation. If the "
                          "trace is unreadable by a human, it is not an audit trail."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Human to machine",
            "title": "Designing the approval gate properly",
            "blocks": [
                {"t": "p", "md": "The gate is where an agentic system meets accountability, "
                                 "and a bad one is worse than none — it manufactures "
                                 "consent."},
                {"t": "bullets", "items": [
                    "**State the action in the approver's language**, not the tool's. "
                    "*Credit IDR 250,000 to account acc-771*, not `post_credit(...)`.",
                    "**Show the evidence** the agent used, with links to the source "
                    "records.",
                    "**Show what it did not check.** An approver needs to know the "
                    "boundary of the analysis.",
                    "**Make decline as easy as approve**, and record the reason — that is "
                    "your best training data.",
                    "**Never batch approvals by default.** Batching is how a gate becomes "
                    "a rubber stamp.",
                ]},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "09", "title": "Regulation and compliance",
         "lead": "UU PDP, OJK, ISO/IEC 27001 and 27701 — and a strategy for satisfying "
                 "all of them at once."},

        {
            "type": "slide",
            "kicker": "The landscape",
            "title": "Five instruments your system sits inside",
            "blocks": [
                {"t": "mmd", "id": "hendri-reg", "src": MMD_REG_STACK,
                 "cap": "They overlap heavily. That is good news: one control usually "
                        "satisfies several."},
                {"t": "p", "md": "Everything on this and the following slides was read "
                                 "from the primary documents. The full citation list, "
                                 "with the PDFs where they are downloadable, is in "
                                 "`references/REFERENCES.md` in the slides repository."},
            ],
        },

        {
            "type": "slide",
            "kicker": "OJK · April 2025",
            "title": "Tata Kelola Kecerdasan Artifisial Perbankan Indonesia",
            "blocks": [
                {"t": "p", "md": "Published by OJK on **29 April 2025**. Bilingual, and "
                                 "the single most directly relevant document for anyone "
                                 "deploying AI in an Indonesian bank."},
                {"t": "table",
                 "head": ["Chapter", "What it gives you"],
                 "widths": [8, 92],
                 "rows": [
                     ["1", "Background — where AI already sits in Indonesian banking"],
                     ["2", "**Risks and challenges** — the risk register to start from"],
                     ["3", "Regulation benchmark across countries — EU, Singapore, US"],
                     ["4", "**Guiding principles** — the values every control maps back to"],
                     ["5", "**Risk management and governance** — roles and three lines"],
                     ["6", "**Implementation guidance** — the lifecycle, stage by stage"],
                     ["7", "**Supervision and audit** — what an examiner will ask for"],
                 ]},
                {"t": "band", "md": "OJK positions it as a **minimum reference**, "
                                    "explicitly flexible as standards evolve. Read: it is "
                                    "a floor, not a ceiling."},
            ],
        },

        {
            "type": "slide",
            "kicker": "OJK · chapter 4",
            "title": "The principles, read out of the document",
            "blocks": [
                {"t": "p", "md": "Two layers, and they come from different lineages — "
                                 "worth knowing, because auditors from different "
                                 "backgrounds will use different vocabulary."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "⚖", "h": "Four ethics principles", "style": "accent",
                     "p": "Respect for human autonomy · Prevention of harm · Fairness · "
                          "Explicability.\n\n*(EU High-Level Expert Group lineage.)*"},
                    {"ico": "🏛", "h": "Nine governance principles", "style": "accent",
                     "p": "Proportionality and Do No Harm · Safety and Security · Right "
                          "to Privacy and Data Protection · Adaptive and Collaborative "
                          "Multi-Stakeholder Governance · Responsibility and "
                          "Accountability · Transparency and Clarity · Human Supervision "
                          "and Control · Sustainability · Awareness and Literacy.\n\n"
                          "*(UNESCO Recommendation lineage.)*"},
                ]},
                {"t": "p", "md": "The document also benchmarks **MAS FEAT** (Singapore) "
                                 "and uses the **ISACA AI Audit Toolkit** and the "
                                 "**VCIO model** for its audit chapter."},
            ],
        },

        {
            "type": "slide",
            "kicker": "OJK · the ones already binding",
            "title": "The AI guidance sits on top of existing obligations",
            "blocks": [
                {"t": "table",
                 "head": ["Instrument", "What it already requires of you"],
                 "widths": [32, 68],
                 "rows": [
                     ["**POJK 11/POJK.03/2022**",
                      "Penyelenggaraan Teknologi Informasi oleh Bank Umum — IT "
                      "governance, risk management, third-party and cloud arrangements"],
                     ["**SEOJK 29/SEOJK.03/2022**",
                      "Ketahanan dan Keamanan Siber — cyber resilience and security"],
                     ["**SEOJK 24/SEOJK.03/2023**",
                      "Digital maturity assessment for commercial banks"],
                     ["**POJK 1/POJK.03/2019**",
                      "Internal audit function — who has to be able to review this"],
                     ["**POJK 3/2024**",
                      "Financial-sector technology innovation, including the sandbox"],
                 ]},
                {"t": "band", "md": "**Nothing in the AI guidance replaces these.** An "
                                    "agentic system is an IT system first: it inherits "
                                    "every obligation your core banking platform already "
                                    "carries."},
            ],
        },

        {
            "type": "slide",
            "kicker": "UU PDP · UU 27/2022",
            "title": "What personal data protection means for an agent",
            "blocks": [
                {"t": "p", "md": "The law is general; the agentic specifics are where it "
                                 "bites. Five questions, each with an architectural answer."},
                {"t": "table",
                 "head": ["The question", "Where it lands in your design"],
                 "widths": [36, 64],
                 "rows": [
                     ["What is your **lawful basis**?",
                      "Decided per data class, before the tool is written"],
                     ["Does personal data reach the **model provider**?",
                      "Redact at the tool boundary, or self-host. This is the decision "
                      "that shapes the whole stack."],
                     ["Can you honour **erasure**?",
                      "Traces contain personal data. They need retention rules and a "
                      "deletion path, like any other store."],
                     ["Can you explain an **automated decision**?",
                      "Reason codes from the model, plus the trace. This is why the "
                      "credit model is classical ML, not an LLM."],
                     ["Where does it **cross a border**?",
                      "Every egress, including the model API call, is a transfer"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "ISO/IEC 27001:2022 and 27701:2025",
            "title": "One correction worth making now",
            "blocks": [
                {"t": "p", "md": "**ISO/IEC 27001:2022** is the information security "
                                 "management system your agentic deployment lives inside. "
                                 "Its Annex A controls are what an auditor will walk "
                                 "through."},
                {"t": "band", "md": "**ISO/IEC 27701 changed.** The second edition was "
                                    "published on **14 October 2025** and is now a "
                                    "==standalone management system standard==. The 2019 "
                                    "first edition was an *extension* to 27001 and 27002 "
                                    "— and a great deal of material still in circulation "
                                    "describes it that way.", "style": "amber"},
                {"t": "p", "md": "Also worth knowing: **ISO/IEC 42001:2023** (AI "
                                 "management systems) and **ISO/IEC 23894:2023** (AI risk "
                                 "management guidance) are the AI-specific companions, "
                                 "and their vocabulary maps closely onto the **NIST AI "
                                 "RMF** Govern / Map / Measure / Manage structure."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Strategy",
            "title": "Satisfying all of them without doing the work five times",
            "blocks": [
                {"t": "mmd", "id": "hendri-comply", "src": MMD_COMPLY,
                 "cap": "One loop, four stages. The instruments differ; the evidence "
                        "they want is largely the same."},
                {"t": "p", "md": "The insight that saves the most effort: **your traces "
                                 "are already the audit trail, and your evaluation sets "
                                 "are already the control tests.** Build them for "
                                 "engineering reasons, and the compliance artefacts are a "
                                 "by-product rather than a second project."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Strategy · the mapping",
            "title": "One control, several obligations",
            "blocks": [
                {"t": "table",
                 "head": ["Control you build", "Satisfies"],
                 "widths": [34, 66],
                 "rows": [
                     ["**Immutable trace of every run**",
                      "OJK ch. 7 (audit) · ISO 27001 A.8.15 logging · UU PDP "
                      "accountability · NIST *Measure*"],
                     ["**Approval gate on write tools**",
                      "OJK human supervision and control · ISO 27001 A.5.15 access "
                      "control · UU PDP automated-decision safeguards"],
                     ["**End-user identity propagation**",
                      "ISO 27001 A.5.15 / A.8.2 · POJK 11/2022 IT governance"],
                     ["**Redaction at the tool boundary**",
                      "UU PDP minimisation and transfer · ISO 27701 PII controls"],
                     ["**Evaluation set as a release gate**",
                      "OJK ch. 6 lifecycle · ISO 42001 · NIST *Manage*"],
                     ["**Model and prompt registry**",
                      "OJK explainability and accountability · ISO 42001 · change control"],
                 ]},
                {"t": "band", "md": "Six controls, roughly twenty obligations. **Design "
                                    "the control once, map it many times** — and keep the "
                                    "map, because that table is what you hand an "
                                    "examiner."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Strategy · the hardest one",
            "title": "The question to settle before writing any code",
            "blocks": [
                {"t": "lead", "md": "**May customer personal data leave the perimeter to "
                                    "reach a model provider?**"},
                {"t": "p", "md": "Every architectural decision in this module follows from "
                                 "that answer, and it is not an engineering decision."},
                {"t": "table",
                 "head": ["If the answer is…", "Then your architecture is…"],
                 "widths": [24, 76],
                 "rows": [
                     ["**No, never**",
                      "Self-hosted open weights inside the perimeter. Lower capability, "
                      "fixed cost, full control. Plan the GPU capacity."],
                     ["**Only if de-identified**",
                      "Hosted model, with redaction and tokenisation **at the tool "
                      "boundary** — and a test proving nothing personal crosses it."],
                     ["**Yes, under contract**",
                      "Hosted model with a data processing agreement, in-region "
                      "processing, zero-retention terms, and the transfer documented "
                      "under UU PDP."],
                 ]},
                {"t": "band", "md": "Ask it in the first meeting. Teams that defer it "
                                    "rebuild.", "style": "rose"},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "10", "title": "System design",
         "lead": "One case, designed properly: where each component sits and why."},

        {
            "type": "slide",
            "kicker": "The case",
            "title": "SME credit assessment, in the field",
            "blocks": [
                {"t": "p", "md": "One case, chosen because it needs everything this "
                                 "module covers at once — and nothing it does not."},
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "📊", "h": "Real data analysis", "style": "accent",
                     "p": "Twelve months of transaction history, aggregated and "
                          "compared against the applicant's stated turnover."},
                    {"ico": "🤖", "h": "A classical ML model", "style": "accent",
                     "p": "Credit scoring — gradient-boosted trees, **not an LLM** — "
                          "exposed as a tool. It returns a score *and reason codes*."},
                    {"ico": "⚖", "h": "Regulation in the loop", "style": "accent",
                     "p": "UU PDP on the customer data, OJK on the decision, and a "
                          "policy corpus the agent must cite from."},
                    {"ico": "📱", "h": "A mobile front end", "style": "accent",
                     "p": "A Flutter app — Android and iOS — the field officer uses at the applicant's "
                          "premises, often on a poor connection."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "The case · the boundary that matters",
            "title": "The agent recommends. A human decides.",
            "blocks": [
                {"t": "lead", "md": "**The agent has no tool that approves credit.** Not "
                                    "a disabled one, not a gated one — the capability is "
                                    "absent from its registry."},
                {"t": "p", "md": "That is a deliberate architectural choice with three "
                                 "justifications, and it is worth being able to state all "
                                 "three:"},
                {"t": "steps", "items": [
                    "**Regulatory** — OJK's human supervision and control principle, and "
                    "UU PDP's safeguards around automated decisions with legal effect.",
                    "**Technical** — an LLM cannot compose functions reliably, and a "
                    "credit decision is a composition. *Faith and Fate* (NeurIPS 2023) "
                    "is the published evidence.",
                    "**Practical** — an instruction can be argued with; an absent tool "
                    "cannot. Removing the capability is stronger than forbidding its use.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "System design",
            "title": "The components, and what talks to what",
            "blocks": [
                {"t": "mmd", "id": "hendri-sysdesign", "src": MMD_SYSDESIGN,
                 # Eleven components. Simplifying it to fit would be simplifying
                 # it into a lie, so it gets the slide instead.
                 "full": True,
                 "cap": "Four MCP servers, one of which is a classical ML model. The "
                        "approval queue is a first-class component, not an afterthought."},
                {"t": "p", "md": "Note what the agent service does **not** hold: no "
                                 "customer data at rest, no credentials for the core "
                                 "systems. It holds a loop, a budget, and a set of "
                                 "capabilities it was granted."},
            ],
        },

        {
            "type": "slide",
            "kicker": "System design · the tools",
            "title": "Five read tools, one write, and why they are separate",
            "blocks": [
                {"t": "table",
                 "head": ["Tool", "Kind", "Why separate"],
                 "widths": [24, 12, 64],
                 "rows": [
                     ["`get_customer`", "read",
                      "Wraps the existing REST service. Different owner, different "
                      "release cycle, different rate limits."],
                     ["`analyse_transactions`", "read",
                      "SQL over the warehouse. Heavy, cacheable, and needs its own "
                      "timeout."],
                     ["`score_credit`", "read",
                      "**Classical ML behind an API.** Versioned separately, monitored "
                      "for drift, and auditable on its own terms."],
                     ["`retrieve_policy`", "read",
                      "The regulation and internal-policy corpus. Its own index, its own "
                      "update cadence."],
                     ["`check_policy`", "read",
                      "Runs every machine-checkable clause, returns pass/fail. "
                      "**Policy is deterministic and belongs in code.**"],
                 ]},
                {"t": "band", "md": "**All five are read tools.** There is exactly one "
                                    "write in the whole system, and it is on the next "
                                    "slide."},
            ],
        },

        {
            "type": "slide",
            "kicker": "System design · the only write",
            "title": "One write tool, and it writes to a queue",
            "blocks": [
                {"t": "lead", "md": "`submit_recommendation` — queues a recommendation "
                                    "for a named officer to decide. **Nothing here "
                                    "approves credit.**"},
                {"t": "steps", "items": [
                    "**The capability does not exist.** There is no `approve_credit` "
                    "anywhere in the registry, so no prompt can reach one and no "
                    "injected instruction can talk the model into one.",
                    "**A test asserts it.** `test_the_agent_has_no_tool_that_approves_"
                    "credit` fails if a write tool other than this one ever appears. "
                    "The claim on this slide is checked on every commit.",
                    "**The server fills in the provenance itself.** The model supplies a "
                    "recommendation and a rationale; the *score*, the *model version* "
                    "and the *policy result* are re-derived server-side. A field the "
                    "model could have misremembered is a field an auditor cannot rely "
                    "on.",
                    "**A decision needs a person and a reason.** The queue refuses a "
                    "decision with no officer id, refuses an empty reason, and refuses "
                    "to let the same item be decided twice.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "System design · the ML model",
            "title": "Why the score comes from a classical model, not the LLM",
            "blocks": [
                {"t": "table",
                 "head": ["", "Classical ML", "LLM"],
                 "widths": [26, 37, 37],
                 "rows": [
                     ["Determinism", "**Same input, same score**", "Varies by sampling"],
                     ["Explainability", "**Reason codes, SHAP values**",
                      "A plausible narrative, unverifiable"],
                     ["Validation", "Standard model risk practice, backtesting",
                      "No accepted method for a credit decision"],
                     ["Drift monitoring", "**Well understood**", "An open problem"],
                     ["Regulatory acceptance", "**Established**", "Not established"],
                     ["Cost per call", "Fractions of a cent", "Orders of magnitude more"],
                 ]},
                {"t": "p", "md": "The LLM's job here is **orchestration and explanation** "
                                 "— deciding what to look up, and writing the "
                                 "recommendation in the officer's language. The numbers "
                                 "come from something that can be validated. "
                                 "==Use each for what it is good at.=="},
            ],
        },

        {
            "type": "slide",
            "kicker": "System design · the ML model",
            "title": "Which classical model? We measured, and it was not the fancy one",
            "blocks": [
                {"t": "p", "md": "The demo fits **two** candidates on the same data, "
                                 "compares them on a held-out split, and ships the "
                                 "winner. The result is not the one the room expects."},
                {"t": "table",
                 "head": ["Candidate", "Held-out AUC", "Verdict"],
                 "widths": [38, 22, 40],
                 "rows": [
                     ["Gradient-boosted trees", "0.733",
                      "Rejected. Spent its capacity on noise."],
                     ["**Logistic regression**", "**0.762**",
                      "**Shipped.** Also the one you can put in front of an examiner."],
                 ]},
                {"t": "p", "md": "The relationship in this data is close to linear and the "
                                 "population is small, so the ensemble had nothing to "
                                 "find and found noise instead. **Reaching for the most "
                                 "powerful model is a habit, not a method.** Here the "
                                 "simpler model wins twice: on the metric, and on "
                                 "==being explainable to somebody who can stop you from "
                                 "deploying it.=="},
                {"t": "band", "md": "Run `python3 integrated/run_demo.py --check` and the "
                                    "comparison is printed. If your data is different, "
                                    "you will get a different answer — which is the "
                                    "point of running it rather than assuming it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "System design · the flow",
            "title": "Eight steps, from photograph to audit log",
            "blocks": [
                {"t": "mmd", "id": "hendri-case-flow", "src": MMD_CASE_FLOW,
                 "cap": "Step 7 is a person. Step 8 is what makes step 7 defensible six "
                        "months later."},
                {"t": "p", "md": "Steps 1–6 are the agent working: read the application, "
                                 "analyse the account, check policy, score, cite the "
                                 "clause, queue the recommendation. **Step 7 is a person**, "
                                 "and nothing in steps 1–6 can reach past it. Step 8 writes "
                                 "the whole run down — ==the officer's reason included==, "
                                 "which is the only place this system learns something it "
                                 "did not already know."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Deployment",
            "title": "Where each piece runs, and where the data is allowed to be",
            "blocks": [
                {"t": "mmd", "id": "hendri-deploy", "src": MMD_DEPLOY,
                 "cap": "One egress, allow-listed, carrying no personal data. Everything "
                        "stateful stays in-region."},
                {"t": "p", "md": "The single dotted line is the whole compliance argument. "
                                 "**If that line carries personal data, the design is "
                                 "different** — and you need the contract, the transfer "
                                 "record, and the DPIA to match."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Deployment · the checklist",
            "title": "What has to be true before this serves a customer",
            "blocks": [
                {"t": "steps", "items": [
                    "**Egress is allow-listed** and every destination is documented as a "
                    "transfer.",
                    "**Redaction is tested**, with a case in the evaluation set that "
                    "fails if personal data reaches the provider.",
                    "**Traces are immutable and retained** on a schedule that satisfies "
                    "both audit and erasure.",
                    "**Identity propagates** — permissions are evaluated against the "
                    "officer, never the service account.",
                    "**Budgets are per tenant**, not only global, so one runaway session "
                    "cannot exhaust the quota for everyone.",
                    "**Rollback is rehearsed** for prompts and tool sets, not only for "
                    "code.",
                    "**Someone is on call**, and the runbook says what to do when the "
                    "model provider is degraded.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Cloud",
            "title": "Providers that can host this, and what to check",
            "blocks": [
                {"t": "table",
                 "head": ["Provider", "Agent-relevant services", "Indonesia region"],
                 "widths": [20, 50, 30],
                 "rows": [
                     ["**AWS**", "Bedrock (+ Agents, Guardrails), SageMaker, EKS, "
                      "Step Functions", "Jakarta — ap-southeast-3"],
                     ["**Google Cloud**", "Vertex AI (Agent Builder, Agent Engine), GKE, "
                      "Workflows", "Jakarta — asia-southeast2"],
                     ["**Microsoft Azure**", "Azure AI Foundry, AI Content Safety, AKS, "
                      "Durable Functions", "Indonesia Central"],
                     ["**Alibaba Cloud**", "Model Studio, ACK", "Jakarta"],
                     ["**Domestic / on-prem**", "Biznet, Lintasarta, Telkom; or your own "
                      "data centre with vLLM", "By definition"],
                 ]},
                {"t": "band", "md": "Region availability is **not** the same as the model "
                                    "being served from that region. Ask specifically where "
                                    "*inference* runs, and get it in the contract.",
                 "style": "amber"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Cloud · what to ask before signing",
            "title": "Six questions a procurement team should carry",
            "blocks": [
                {"t": "bullets", "items": [
                    "**Where does inference physically run**, and can that be pinned?",
                    "**What is the retention** on prompts and completions — and is "
                    "zero-retention contractual or a setting someone can flip?",
                    "**Is our data used for training?** Get the default and the opt-out "
                    "in writing.",
                    "**Which certifications apply** to the specific service, not the "
                    "provider generally — ISO 27001, 27701, SOC 2, and their scope "
                    "statements.",
                    "**What is the deprecation policy** for a model version we have "
                    "validated? A silent model update invalidates your evaluation.",
                    "**What are the exit terms** — can we extract traces, embeddings and "
                    "fine-tunes, in what format, over what period?",
                ]},
                {"t": "p", "md": "The fifth is the one people miss. **A model updated "
                                 "underneath you is a change you did not test**, and in a "
                                 "regulated setting that is a finding."},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "11", "title": "The demo",
         "lead": "A Flutter app on either phone, a REST service, a model behind MCP, and a human who "
                 "decides."},

        {
            "type": "slide",
            "kicker": "Demo · the mobile app",
            "title": "Why the front end is a phone",
            "blocks": [
                {"t": "p", "md": "The officer is at the applicant's premises, not at a "
                                 "desk. That single fact changes four design decisions."},
                {"t": "table",
                 "head": ["Constraint", "What it forces"],
                 "widths": [28, 72],
                 "rows": [
                     ["**Poor connectivity**",
                      "The request is queued and resumable. An agent run is minutes, not "
                      "milliseconds — treat it as a job, not a call."],
                     ["**Small screen**",
                      "The recommendation must fit and be scannable. The evidence sits "
                      "behind a tap, not on the first screen."],
                     ["**Camera as a sensor**",
                      "Documents arrive as photographs. Extraction happens server-side, "
                      "with a confirmation step."],
                     ["**Device is not trusted**",
                      "No credentials for core systems on the phone. It holds a session "
                      "token and nothing else."],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Demo · what the officer sees",
            "title": "Five screens, and one of them is the point",
            "blocks": [
                {"t": "cards", "cols": 3, "items": [
                    {"ico": "📥", "h": "1 — Applications", "style": "",
                     "p": "What is waiting. The officer picks one and the rest of the "
                          "app is about that file."},
                    {"ico": "📸", "h": "2 — Applicant", "style": "",
                     "p": "The figures, the owner's name — **shown here and carried "
                          "nowhere else** — and the document camera."},
                    {"ico": "⏳", "h": "3 — Running", "style": "",
                     "p": "The run is a job. Progress names *which tool is running*, so a "
                          "slow lookup is distinguishable from a hung one."},
                    {"ico": "📋", "h": "4 — Recommendation", "style": "accent",
                     "p": "**Every figure carries its source.** Score and reason codes "
                          "from the credit model, policy clauses printed in full, and "
                          "the trace one tap away."},
                    {"ico": "✅", "h": "5 — Recorded", "style": "accent",
                     "p": "**The officer decides**, with a reason that is required even "
                          "when they agree. The reason is stored against their id."},
                    {"ico": "🚫", "h": "The screen that is absent", "style": "bad",
                     "p": "There is no screen, and no endpoint, by which this app "
                          "disburses anything. The boundary is in the code, not in the "
                          "navigation."},
                ]},
                {"t": "band", "md": "Screen 3 is where the module's argument becomes a "
                                    "product: **a recommendation you cannot check is a "
                                    "recommendation you should not act on.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Demo · the pieces to build",
            "title": "What ships with this module",
            "blocks": [
                {"t": "table",
                 "head": ["Component", "Stack", "Purpose"],
                 "widths": [26, 26, 48],
                 "rows": [
                     ["**Mobile app**", "Flutter — Android + iOS",
                      "Five screens from one codebase; the assessment is a job"],
                     ["**Agent case**", "Python, `agentcore`",
                      "The loop, budgets, guardrails, traces — from the demo repository"],
                     ["**REST service**", "Python standard library",
                      "Stands in for core banking, analytics, policy and the queue. No "
                      "framework: the point is the shape of the API."],
                     ["**Credit model**", "scikit-learn",
                      "Two candidates fitted, the better one shipped; returns the score "
                      "**and the reason codes**"],
                     ["**MCP server and client**", "Written out by hand",
                      "Line-delimited JSON-RPC. Small enough to read in one sitting, "
                      "which is why it is not the SDK here."],
                     ["**Approval queue**", "A locked JSON file",
                      "Where a write waits for a person — shared across processes"],
                 ]},
                {"t": "p", "md": "All of it runs locally with no API key, against the "
                                 "offline provider in `agentcore` — so the whole system "
                                 "can be demonstrated in a classroom with no credentials "
                                 "and no network. **One command runs the lot:** "
                                 "`python3 integrated/run_demo.py --check`."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Demo · what it is designed to show",
            "title": "Five things you can only see end to end",
            "blocks": [
                {"t": "steps", "items": [
                    "**An LLM orchestrating, not deciding.** The score comes from a model "
                    "that can be validated; the LLM chooses what to look up and how to "
                    "explain it.",
                    "**A capability boundary that is structural.** No approval tool exists "
                    "anywhere in the agent's registry.",
                    "**A trace that is an audit trail.** Every figure in the "
                    "recommendation traces to the call that produced it.",
                    "**Redaction that is tested**, with an evaluation case that fails if "
                    "personal data would reach the provider.",
                    "**A hand-off that comes back.** The officer's decision and reason "
                    "return to the system and close the loop.",
                ]},
            ],
        },

        # ==============================================================
        {"type": "section", "num": "12", "title": "Operating it",
         "lead": "How you know it works, and what you do when it stops."},

        {
            "type": "slide",
            "kicker": "Evaluation",
            "title": "Three levels, because they catch different things",
            "blocks": [
                {"t": "table",
                 "head": ["Level", "What it asserts", "What it misses"],
                 "widths": [24, 40, 36],
                 "rows": [
                     ["**Unit**", "The right tool is called with the right arguments",
                      "Whether the sequence produces a useful outcome"],
                     ["**End to end**", "The outcome matches a known good one",
                      "*Why* — a right answer for the wrong reason still passes"],
                     ["**Human review**", "Whether it is actually good, by a standard you "
                      "cannot encode", "Coverage — it is sampled"],
                 ]},
                {"t": "band", "md": "Run all three **before every prompt change, model "
                                    "upgrade, and tool change.** In this domain a prompt "
                                    "edit is a code change with no type checker behind it."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Evaluation · building the set",
            "title": "Where the twenty cases come from",
            "blocks": [
                {"t": "steps", "items": [
                    "**Twenty real applications**, taken from what the process handles "
                    "today. Not twenty imagined ones.",
                    "**Write the good outcome for each** before building anything, while "
                    "you are still honest about what good means.",
                    "**Add every failure you observe**, permanently. This is how the set "
                    "grows, and why it is versioned.",
                    "**Include the boring cases.** A set of only hard cases lets you ship "
                    "something that fails the easy ones.",
                    "**Keep a held-out slice** you do not look at while iterating — the "
                    "validation-set overfitting problem, in a new setting.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operating",
            "title": "Five failure modes, and how each announces itself",
            "blocks": [
                {"t": "mmd", "id": "hendri-failure", "src": MMD_FAILURE,
                 "cap": "None of these raise an exception. All of them are visible in a "
                        "trace."},
                {"t": "p", "md": "Alert on the **shape** of runs, not only on errors: "
                                 "mean steps per request, cost per request, tool-call "
                                 "repetition rate, escalation rate. **A rising step count "
                                 "is usually the first visible sign that something "
                                 "upstream changed.**"},
            ],
        },

        {
            "type": "slide",
            "kicker": "Operating · deployment",
            "title": "The autonomy ladder, and where to stop",
            "blocks": [
                {"t": "mmd", "id": "hendri-autonomy", "src": MMD_AUTONOMY,
                 "cap": "Move up a rung only with evidence from the evaluation harness."},
                {"t": "band", "md": "For a credit decision under OJK supervision, **L2 is "
                                    "the destination**, not a waypoint. The question at "
                                    "L3 is not *how good is it* but ==what is the blast "
                                    "radius when it is wrong== — and that boundary belongs "
                                    "in code, not in a prompt."},
            ],
        },

        {
            "type": "slide",
            "kicker": "Common failure modes",
            "title": "Four ways this work goes wrong in practice",
            "blocks": [
                {"t": "cards", "cols": 2, "items": [
                    {"ico": "🏗", "h": "Building an agent for a workflow", "style": "bad",
                     "p": "The most common and most expensive mistake. Apply the "
                          "operational test first: **who decides the next step?**"},
                    {"ico": "👯", "h": "Splitting for tidiness", "style": "bad",
                     "p": "Researcher / Writer / Critic feels organised and costs three "
                          "times one agent with the same tools. Split on the three "
                          "questions, not on the org chart."},
                    {"ico": "🕳", "h": "No trace until the first incident", "style": "warn",
                     "p": "Nothing here reproduces. Without traces you cannot debug it, "
                          "and you cannot evidence it to an auditor either."},
                    {"ico": "⚖", "h": "Compliance as a final gate", "style": "warn",
                     "p": "The residency question decides the architecture. Asking it "
                          "after the build means rebuilding."},
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this module (1 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**The definition is old.** Russell & Norvig: percepts in through "
                    "sensors, actions out through actuators. What is new is the action "
                    "space, not the idea.",
                    "**Who decides the next step** separates a workflow from an agent. "
                    "Most things are workflows — build them as workflows.",
                    "**Five workflow patterns come first.** Reach for an agent when the "
                    "path genuinely cannot be known in advance.",
                    "**The model never touches anything.** It emits an intention; your "
                    "code decides. Every permission boundary lives in that gap.",
                    "**Six exit conditions**, not one. And read tools differ from write "
                    "tools from day one.",
                    "**Three questions before splitting** — different permissions, real "
                    "parallelism, or context that will not fit.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "Summary",
            "title": "What has to survive this module (2 of 2)",
            "blocks": [
                {"t": "steps", "items": [
                    "**Components come in three levels**, and calling a minimum system "
                    "production-ready is how incidents happen.",
                    "**Prototype in no-code, build in code.** They are different "
                    "activities; using one tool for both is how prototypes become "
                    "production by accident.",
                    "**MCP reaches inward, A2A reaches across.** Adopt the one you need.",
                    "**Settle the data-residency question first.** It decides the "
                    "architecture, and it is not an engineering decision.",
                    "**One control, several obligations.** Traces are the audit trail; "
                    "evaluation sets are the control tests. Keep the mapping table.",
                    "**Let the classical model produce the number** and the LLM produce "
                    "the explanation. Use each for what it can be validated on.",
                ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "References",
            "title": "Where every claim in this module comes from",
            "blocks": [
                {"t": "p", "md": "Each of these was checked against the **primary "
                                 "document**, not a summary of it. Where the two "
                                 "disagreed, the primary document won — twice, and both "
                                 "corrections are noted in the list."},
                {"t": "table",
                 "head": ["Area", "Principal sources"],
                 "widths": [22, 78],
                 "rows": [
                     ["**Foundations**", "Russell & Norvig, *AI: A Modern Approach*, 4th "
                      "ed., ch. 2 · Wooldridge, *An Introduction to MultiAgent Systems* · "
                      "Chollet, *On the Measure of Intelligence* (arXiv:1911.01547)"],
                     ["**The loop**", "ReAct (arXiv:2210.03629) · Chain-of-Thought "
                      "(arXiv:2201.11903) · Toolformer (arXiv:2302.04761) · Reflexion "
                      "(arXiv:2303.11366) · CodeAct (arXiv:2402.01030)"],
                     ["**Limits**", "Dziri et al., *Faith and Fate* (arXiv:2305.18654)"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "References",
            "title": "Practice, security, and the rules you are held to",
            "blocks": [
                {"t": "table",
                 "head": ["Area", "Principal sources"],
                 "widths": [22, 78],
                 "rows": [
                     ["**Practice**", "Anthropic, *Building Effective Agents* (2024) · "
                      "Model Context Protocol specification · Agent2Agent, Linux "
                      "Foundation (2025)"],
                     ["**Security**", "OWASP Top 10 for LLM Applications · NIST AI RMF "
                      "1.0 (NIST AI 100-1)"],
                     ["**Regulation**", "OJK, *Tata Kelola Kecerdasan Artifisial "
                      "Perbankan Indonesia* (29 April 2025) · UU 27/2022 (PDP) · POJK "
                      "11/POJK.03/2022 · SEOJK 29/SEOJK.03/2022"],
                     ["**Standards**", "ISO/IEC 27001:2022 · ISO/IEC 27701:2025 · "
                      "ISO/IEC 42001:2023 · ISO/IEC 23894:2023"],
                 ]},
            ],
        },

        {
            "type": "slide",
            "kicker": "References",
            "title": "The list is a file, and it is checkable",
            "blocks": [
                {"t": "p", "md": "The full list lives in the slides repository with the "
                                 "downloadable PDFs beside it, and a script that re-fetches "
                                 "every link and reports what has moved."},
                {"t": "code", "lang": "bash", "file": "keeping it honest", "src": """cd course-slides/references
python3 check.py --pdf      # re-fetch every link, verify every local PDF"""},
                {"t": "p", "md": "**Two corrections that pass to you.** ISO/IEC 27701 is "
                                 "no longer an extension to 27001 — the second edition of "
                                 "14 October 2025 is standalone. And the OJK AI guidance "
                                 "is dated **2025**, not 2024 as several secondary sources "
                                 "state."},
                {"t": "links", "items": [
                    {"k": "LIST", "ic": "📚", "v": "references/REFERENCES.md",
                     "href": "https://github.com/situkangsayur/dnd-ai-products-services-pro-course-slides/blob/main/references/REFERENCES.md"},
                    {"k": "OJK", "ic": "🏛", "v": "Tata Kelola Kecerdasan Artifisial Perbankan Indonesia",
                     "href": "https://ojk.go.id/id/Publikasi/Roadmap-dan-Pedoman/Perbankan/Pages/Tata-Kelola-Kecerdasan-Artifisial-Perbankan-Indonesia.aspx"},
                    {"k": "REPO", "ic": "🐙", "v": "ai-agentic-demo",
                     "href": "https://github.com/situkangsayur/ai-agentic-demo"},
                    {"k": "BACK", "ic": "⬅", "v": "Large Language Models — Viny's module",
                     "href": "../viny-llm/index.html"},
                ]},
            ],
        },
    ],
}
