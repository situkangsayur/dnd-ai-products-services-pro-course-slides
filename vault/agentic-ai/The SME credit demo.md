---
tags: [agentic-ai, demo, mcp, flutter, credit]
code: "ai-agentic-demo/integrated/"
updated: 2026-08-31
---

# The SME credit demo

The whole module, running: a **Flutter** app in a credit officer's hand —
Android and iOS from one codebase — a REST service, an agent, six tools reached
over [[MCP and A2A|MCP]], a classical ML model that produces the score, and a
human being who makes the decision.

The client **builds**: Flutter 3.47.2 / Dart 3.13.2, Android SDK 36, analyzer
clean, tests green, and a debug APK whose only permission is `INTERNET`. What
that first build cost is in [[Findings worth keeping]].

It exists to make one claim checkable rather than assertable:

> **An agent can orchestrate a regulated decision it is not permitted to make.**

Runs offline, no API key, no network: `python3 integrated/run_demo.py --check`.

## The shape

The officer opens an application on the phone, photographs the papers, and runs
an assessment. The agent reads the application, analyses twelve months of
account activity, checks credit policy, scores the applicant, cites the clauses
it relied on, and **queues** a recommendation. The officer agrees or disagrees,
gives a reason, and decides.

## Six tools, five of them reads

`get_customer`, `analyse_transactions`, `score_credit`, `retrieve_policy`,
`check_policy` — and exactly one write, `submit_recommendation`, which writes to
a queue.

There is no `approve_credit` anywhere in the registry, and
`test_the_agent_has_no_tool_that_approves_credit` fails if a second write tool
ever appears. The claim is checked on every commit, which is the difference
between a control and a slide.

## Six applicants, six different reasons

The one to spend time on is **APP-2202**. The model likes it more than any other
application in the set — band A, probability of default 0.003 — and the system
still refuses to sign it off, because the facility is above the delegated limit.
A limit is a delegation of authority, not a statement about risk.

## Where the personal data goes

The owner's name is on one endpoint, shown on one screen, and carried nowhere
else. The assessment request contains an application id. Document photographs go
to the bank's own store; there is no code path that could send an image to a
model provider. The redaction is a guardrail with a test behind it, not a line
in the prompt.

## Five screens, and the sixth

Applications → applicant → running → recommendation → recorded. The deck draws
them as phone frames rather than icons, and draws the sixth as a **hole**:
dashed, struck through, with no arrow leading into it. There is no screen and
no endpoint by which this app disburses anything.

Drawing the absence is the point. A capability boundary you can navigate around
is not a boundary.

Related: [[Tools are the permission boundary]], [[Findings worth keeping]]
