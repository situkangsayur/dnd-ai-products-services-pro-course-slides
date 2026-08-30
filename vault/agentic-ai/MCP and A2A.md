---
tags: [agentic-ai, protocols, interoperability]
updated: 2026-08-30
---

# MCP and A2A

They do different jobs and are not alternatives.

- **MCP** (Model Context Protocol) — how one agent reaches **inward** to tools,
  data and prompts. Anthropic, November 2024; now under the Linux Foundation.
  Revision 2025-06-18 added structured tool output, elicitation, classification
  of MCP servers as OAuth **Resource Servers**, and RFC 8707 resource
  indicators.
- **A2A** (Agent2Agent) — how agents coordinate **across** organisational
  boundaries. Google, donated to the Linux Foundation June 2025.

> Do not adopt A2A because it exists. It solves cross-organisational
> coordination. One organisation with one agent has added a protocol and bought
> nothing.

## The protocol is small

Line-delimited JSON-RPC 2.0: `initialize`, `tools/list`, `tools/call`. Small
enough to write out by hand, which is what `integrated/mcp/` does — a team that
has read the protocol makes better decisions about what to put behind it.

What the hand-written client deliberately omits is as instructive as what it
has: no retries, no reconnection, no concurrency, no sampling, no resources or
prompts. Each of those is a real feature and a decision to make deliberately
rather than inherit.

## Human-to-machine is an interface too

Approval, escalation and audit are interfaces with the same design obligations
as any API: what state travels, what the person sees, what comes back. The
approval gate is the one nobody designs, and it is the one an examiner reads.

Related: [[Tools are the permission boundary]], [[The SME credit demo]]
