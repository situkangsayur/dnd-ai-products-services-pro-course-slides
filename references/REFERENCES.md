# References — Agentic AI module

Every source here has been **checked against the primary document**, not quoted
from a summary. Where a PDF is openly downloadable it sits in `pdf/`; where it
is not, the link is given and the reason noted.

Two conventions:

- **Verified** means the page or PDF was fetched and the title, issuing body,
  and date read off it during this build.
- **Link only** means the source is real and citable but paywalled, login-gated,
  or served in a form that cannot be archived here.

Last checked: **30 August 2026**.

---

## 1. Foundations — what an agent is

| Source | Why it is here | Status |
|---|---|---|
| Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson, 2021. ISBN 978-0134610993. Ch. 2, "Intelligent Agents". | The definition the module starts from: an agent perceives through sensors and acts through actuators; the PEAS framing; the five agent types from simple-reflex to learning. Predates LLMs by decades, which is the point. | Link only (textbook) · [aimacode on GitHub](https://github.com/aimacode) — the book's companion code |
| Wooldridge, M. *An Introduction to MultiAgent Systems*, 2nd ed. Wiley, 2009. | The multi-agent vocabulary — autonomy, reactivity, pro-activeness, social ability — that current writing rediscovers without citing. | Link only (textbook) |
| Chollet, F. "On the Measure of Intelligence." arXiv:1911.01547, 2019. | Where the skill-versus-generality distinction is argued precisely. Underpins the module's claim that a system solving one fixed task well is not thereby agentic. | `pdf/measure-of-intelligence-chollet-2019.pdf` |

## 2. The modern agent loop

| Source | Why it is here | Status |
|---|---|---|
| Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023. arXiv:2210.03629. | The reason-then-act loop the whole field now assumes. | `pdf/react-yao-2022.pdf` |
| Wei, J. et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS 2022. arXiv:2201.11903. | Where showing the working came from. | `pdf/chain-of-thought-wei-2022.pdf` |
| Schick, T. et al. "Toolformer: Language Models Can Teach Themselves to Use Tools." NeurIPS 2023. arXiv:2302.04761. | Tool use as a learned capability rather than a prompt trick. | `pdf/toolformer-schick-2023.pdf` |
| Shinn, N. et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023. arXiv:2303.11366. | Self-critique loops, and their limits. | `pdf/reflexion-shinn-2023.pdf` |
| Wang, X. et al. "Executable Code Actions Elicit Better LLM Agents." ICML 2024. arXiv:2402.01030. | Code as the action space — the argument behind the code-execution tool in the demo. | `pdf/executable-code-actions-wang-2024.pdf` |
| Lewis, P. et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020. arXiv:2005.11401. | The RAG paper proper. Carries over from the LLM module. | `pdf/rag-lewis-2020.pdf` |
| Wu, Q. et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155, 2023. | A named multi-agent architecture to argue with. | `pdf/autogen-wu-2023.pdf` |
| Dziri, N. et al. "Faith and Fate: Limits of Transformers on Compositionality." NeurIPS 2023. arXiv:2305.18654. | The evidence that LLMs cannot compose functions reliably — the sharpest published limit on what an agent built from one can be trusted to do. | `pdf/faith-and-fate-dziri-2023.pdf` |

## 3. Engineering practice — vendor documentation

| Source | Why it is here | Status |
|---|---|---|
| Anthropic. "Building Effective Agents." Engineering blog, December 2024. | The workflow-versus-agent distinction the module's operational test is built on, and the five workflow patterns: prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimiser. Also the recommendation to start without a framework. | Verified · [anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) |
| Model Context Protocol — specification and documentation. Introduced by Anthropic, November 2024; revision 2025-06-18 added structured tool output, elicitation, OAuth Resource Server classification and RFC 8707 resource indicators. Now under the Linux Foundation. | The machine-to-machine standard for connecting an agent to tools and data. | Verified · [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| Agent2Agent (A2A) Protocol. Created by Google, donated to the Linux Foundation June 2025; project launched at Open Source Summit North America, 23 June 2025. | The agent-to-agent standard, complementary to MCP: A2A is how agents coordinate **across** organisational boundaries, MCP is how one agent reaches **inward** to tools. | Verified · [a2a-protocol.org](https://a2a-protocol.org/latest/) · [Linux Foundation announcement](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) |
| OpenAI. Agents SDK / Assistants documentation. | One of the three stacks compared. | Link only · [platform.openai.com/docs](https://platform.openai.com/docs) |
| LangChain / LangGraph documentation. | Graph-structured orchestration; the most common "medium" stack. | Link only · [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/) |
| AWS Bedrock Agents · Azure AI Foundry · Google Vertex AI Agent Builder | The three managed deployment paths compared in the cloud section. | Link only — vendor docs |

## 4. Security

| Source | Why it is here | Status |
|---|---|---|
| OWASP. *Top 10 for Large Language Model Applications*. | Prompt injection, insecure output handling, excessive agency. "Excessive agency" is the entry that names precisely what this module's write-tool gate exists to prevent. | Link only · [owasp.org/www-project-top-10-for-large-language-model-applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |
| NIST. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1, January 2023. | The Govern / Map / Measure / Manage structure. The vocabulary regulators increasingly borrow. | `pdf/nist-ai-rmf-100-1.pdf` |

## 5. Regulation — Indonesia

| Source | Why it is here | Status |
|---|---|---|
| **OJK. *Tata Kelola Kecerdasan Artifisial Perbankan Indonesia* (Indonesian Banking Artificial Intelligence Governance). Published 29 April 2025.** | **The single most directly relevant document for this audience.** Bilingual, seven chapters: background; risks and challenges; regulation benchmark across countries; guiding principles; risk management and governance; implementation guidance; supervision and audit. | **Verified · `pdf/ojk-tata-kelola-ai-perbankan-2025.pdf`** (11 MB) · [OJK page](https://ojk.go.id/id/Publikasi/Roadmap-dan-Pedoman/Perbankan/Pages/Tata-Kelola-Kecerdasan-Artifisial-Perbankan-Indonesia.aspx) |
| UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP). | Indonesia's personal data protection law. Consent, data subject rights, controller/processor duties, cross-border transfer, sanctions. | Link only — the BPK portal serves an HTML wrapper rather than a direct PDF · [peraturan.bpk.go.id](https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022) |
| POJK No. 11/POJK.03/2022 — Penyelenggaraan Teknologi Informasi oleh Bank Umum. | Cited by the OJK AI guidance as the standing IT governance obligation an AI system must sit inside. | Link only · [ojk.go.id](https://ojk.go.id/id/regulasi/Pages/POJK-tentang-Penerapan-Manajemen-Risiko-dalam-Penggunaan-Teknologi-Informasi-Oleh-Bank-Umum.aspx) |
| POJK No. 3 Tahun 2024 — Penyelenggaraan Inovasi Teknologi Sektor Keuangan. | The regulatory sandbox and financial-sector technology innovation regime. | Link only |
| SEOJK No. 29/SEOJK.03/2022 — Ketahanan dan Keamanan Siber bagi Bank Umum. | Cyber resilience obligations, cited by the AI guidance. | Link only |
| SEOJK No. 24/SEOJK.03/2023 · SEOJK No. 21/SEOJK.03/2017 · POJK No. 1/POJK.03/2019 | Further instruments the OJK AI guidance cross-references (digital maturity assessment; IT risk management; internal audit function). | Link only |

### Principles the OJK guidance adopts

Read directly out of the PDF, chapter 4. Two layers.

**The four ethics principles** (EU High-Level Expert Group lineage): respect for
human autonomy · prevention of harm · fairness · explicability.

**The nine governance principles** (UNESCO Recommendation lineage):
a. Proportionality and Do No Harm · b. Safety and Security · c. Right to Privacy
and Data Protection · d. Adaptive and Collaborative Multi-Stakeholder Governance ·
e. Responsibility and Accountability · f. Transparency and Clarity ·
g. Human Supervision and Control · h. Sustainability · i. Awareness and Literacy.

The guidance also benchmarks against MAS (Singapore) **FEAT** — Fairness, Ethics,
Accountability and Transparency — and uses the **ISACA AI Audit Toolkit** and the
**VCIO model** (Values, Criteria, Indicators, Observables) for the audit chapter.

## 6. Standards

| Source | Why it is here | Status |
|---|---|---|
| ISO/IEC 27001:2022 — Information security management systems — Requirements. | The ISMS the whole system has to live inside. Annex A controls are what an auditor will ask about. | Link only (paywalled) · [iso.org/standard/27001](https://www.iso.org/standard/27001) |
| **ISO/IEC 27701:2025** — Privacy information management systems — Requirements and guidance. Second edition, published **14 October 2025**. | **Now a standalone management system standard.** The 2019 first edition was an *extension* to ISO/IEC 27001 and 27002; much existing material still describes it that way and is out of date. | Verified (metadata) · Link only (paywalled) · [iso.org/standard/27701](https://www.iso.org/standard/27701) |
| ISO/IEC 42001:2023 — AI management systems. | The AI-specific management system standard; the natural companion to 27001 for an agentic deployment. | Link only (paywalled) |
| ISO/IEC 23894:2023 — AI — Guidance on risk management. | Risk vocabulary that maps onto the NIST AI RMF. | Link only (paywalled) |

## 7. Building the demo — what the implementation follows

The integrated case in `ai-agentic-demo/integrated/` is not free-hand. These are
the documents it was written against, and each one is load-bearing somewhere in
the code.

| Source | Where it shows up | Status |
|---|---|---|
| **JSON-RPC 2.0 Specification** (2013-01-04). | The MCP server and client in `integrated/mcp/` are written out by hand against this and the MCP revision above. Line-delimited JSON-RPC over stdio, three methods. | Verified · [jsonrpc.org/specification](https://www.jsonrpc.org/specification) |
| Mitchell, M. et al. (2019). **Model Cards for Model Reporting.** *FAT\* '19.* arXiv:1810.03993. | `scoring.model_card()` returns one, and the agent fetches it rather than remembering the model version. Sections used: intended use, factors, metrics, training data, ethical considerations, caveats. | Verified · PDF in `pdf/model-cards-mitchell-2019.pdf` · [arXiv](https://arxiv.org/abs/1810.03993) |
| Gebru, T. et al. (2018/2021). **Datasheets for Datasets.** arXiv:1803.09010. | Why `data/make_transactions.py` states its generating process and its seed, and why the model card says out loud that the population is synthetic. | Verified · PDF in `pdf/datasheets-gebru-2018.pdf` · [arXiv](https://arxiv.org/abs/1803.09010) |
| **scikit-learn** — Ensemble methods and Linear models, user guide. | Both candidate models. The demo fits gradient-boosted trees *and* logistic regression, compares held-out AUC, and ships the winner — which is the logistic model. | Verified · [scikit-learn.org](https://scikit-learn.org/stable/modules/ensemble.html) |
| **Android — Getting a result from an activity** (`ActivityResultContracts.TakePicture`). | Why the app asks for no `CAMERA` permission: it hands a file it owns to a camera app that already has the right. | Verified · [developer.android.com](https://developer.android.com/training/basics/intents/result) |
| **Android — Network security configuration.** | Cleartext is permitted to two named hosts for the classroom demo, not app-wide. The exception is visible and bounded. | Verified · [developer.android.com](https://developer.android.com/privacy-and-security/security-config) |
| **Jetpack Compose** documentation. | The five screens, and the state-holder pattern in `FieldViewModel`. | Verified · [developer.android.com](https://developer.android.com/develop/ui/compose/documentation) |

**A note on the credit content.** The ten policy clauses, the 1.25 debt-service
coverage floor and the loan-to-value cap are written for teaching. They are
plausible and internally consistent; they are not any institution's policy, and
they carry no citation because there is none to give. Where the module makes a
claim that a *regulator* requires something — human decision rights, adverse
action reasons, data residency — that claim is cited in section 5 and not here.

## 8. Not used, and why

- **Blog posts summarising the above.** Where a summary and the primary document
  disagreed during this build, the primary document won. Two examples worth
  keeping: ISO/IEC 27701 is no longer an extension to 27001, and the OJK AI
  guidance is dated 2025 rather than 2024 as several secondary sources state.
- **Vendor benchmark claims** about agent frameworks. None of the published
  comparisons are reproducible, so the module compares stacks on properties you
  can verify yourself — licence, hosting model, protocol support — rather than
  on scores.

---

## How to refresh this

```bash
cd course-slides/references
python3 check.py          # re-fetch every link and report what moved
```

Anything that returns a non-200, or whose title no longer matches, is reported
rather than silently left to rot.
