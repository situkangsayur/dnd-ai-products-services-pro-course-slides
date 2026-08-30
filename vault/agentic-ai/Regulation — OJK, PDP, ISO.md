---
tags: [agentic-ai, regulation, indonesia, compliance]
updated: 2026-08-30
---

# Regulation — OJK, PDP, ISO

## Five instruments the system sits inside

| Instrument | What it obliges |
|---|---|
| **OJK, *Tata Kelola Kecerdasan Artifisial Perbankan Indonesia*** (29 April 2025) | Governance of AI in banking: four ethics principles, nine governance principles, and an audit chapter |
| **UU 27/2022 (PDP)** | Personal data: lawful basis, purpose limitation, subject rights, transfer conditions |
| **POJK 11/POJK.03/2022** and **SEOJK 29/SEOJK.03/2022** | IT risk management for commercial banks; the instruments the AI guidance sits on top of |
| **ISO/IEC 27001:2022** | The ISMS everything lives inside |
| **ISO/IEC 27701:2025** | Privacy information management |

The OJK guidance is dated **2025**, not 2024 as several secondary sources
state. Its four ethics principles descend from the EU HLEG list; the nine
governance principles from UNESCO. It benchmarks against MAS **FEAT** and uses
the **ISACA AI Audit Toolkit** and the **VCIO model** for auditing.

## The correction people still get wrong

**ISO/IEC 27701 is no longer an extension to 27001.** The second edition,
14 October 2025, is a standalone management system standard. The 2019 first
edition was an extension, and a lot of material still describes it that way.

## The question to settle before writing any code

**Where is the data allowed to be?** It decides the architecture, it is not an
engineering decision, and asking it after the build means rebuilding. In the
demo it reduces to a single dotted line on the deployment diagram: one
allow-listed egress, carrying no personal data. If that line carries personal
data, you need the contract, the transfer record and the DPIA to match.

## One control, several obligations

Do not implement five compliance programmes. Six controls cover roughly twenty
obligations:

- **Traces** → the audit trail for OJK, and evidence for 27001 Annex A logging
- **Evaluation sets** → the control tests, for AI governance and model risk
- **Model cards** → intended use, factors, limitations; asked for by all of them
- **Approval gates** → human decision rights (OJK), and separation of duties
- **Redaction at the boundary** → PDP data minimisation, evidenced in a test
- **Residency by design** → PDP transfer conditions, and the ISMS scope

Keep the mapping table. It is the artefact that stops the same work being done
five times under five names.

Related: [[Components at three levels]], [[The SME credit demo]]
