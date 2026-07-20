# IBM Bob Usage Log — MechaCode Guardian

**Version:** 0.2
**Date:** 2025-07-20 (updated same day with second session)
**Purpose:** Auditable record of how IBM Bob (AI coding assistant) was used throughout the MechaCode Guardian project. Required for AI Builders Challenge transparency and reproducibility.

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Usage Categories and Conventions](#2-usage-categories-and-conventions)
3. [Session Log Template](#3-session-log-template)
4. [Usage Log — Architecture and Planning](#4-usage-log--architecture-and-planning)
5. [Usage Log — Coding](#5-usage-log--coding)
6. [Usage Log — Testing](#6-usage-log--testing)
7. [Usage Log — Refactoring](#7-usage-log--refactoring)
8. [Usage Log — Security Review](#8-usage-log--security-review)
9. [Usage Log — Documentation](#9-usage-log--documentation)
10. [Usage Log — Deployment](#10-usage-log--deployment)
11. [Aggregate Summary](#11-aggregate-summary)
12. [Honest Disclosure Policy](#12-honest-disclosure-policy)

---

## 1. Purpose and Scope

This document is an **auditable record** of every substantive interaction with IBM Bob during the development of MechaCode Guardian. It covers:

- What was asked of IBM Bob
- What IBM Bob produced
- What the developer accepted, modified, or rejected
- Whether the output was verified before use

**Why this matters:**
- The competition evaluates how thoughtfully the developer uses AI tooling, not merely whether AI was used.
- Transparency about AI-assisted work demonstrates intellectual honesty.
- The log serves as a reference for understanding which parts of the codebase were AI-generated versus human-authored.

**Scope boundary:** This log covers IBM Bob usage only. Usage of other tools (GitHub Copilot inline completions, documentation lookups, etc.) is out of scope.

---

## 2. Usage Categories and Conventions

| Category Code | Category Name | Description |
|---|---|---|
| A | Architecture & Planning | System design, component decisions, data flow, trade-off analysis |
| C | Coding | New code generation, feature implementation |
| T | Testing | Test case generation, evaluation scripts, assertion logic |
| R | Refactoring | Code restructuring, naming improvements, dead code removal |
| S | Security Review | Vulnerability checks, secrets scanning, input validation review |
| D | Documentation | README, inline docstrings, user-facing text |
| P | Deployment | Dockerfile, CI config, deployment scripts, environment setup |

**Acceptance status codes:**

| Code | Meaning |
|---|---|
| ACC | Accepted as-is — output used without modification |
| MOD | Modified — output used with developer changes |
| REJ | Rejected — output not used; developer implemented differently |
| PAR | Partial — some parts accepted, others rejected |

**Verification status:**

| Code | Meaning |
|---|---|
| VER | Verified — developer tested/read the output and confirmed correctness |
| UNVER | Unverified — output used without independent verification (flag for later review) |

---

## 3. Session Log Template

Use this template for each IBM Bob session entry:

```markdown
### Session [SESSION_ID]
**Date:** YYYY-MM-DD
**Category:** [A / C / T / R / S / D / P]
**Task:** Brief description of what was requested
**Prompt summary:** What was asked (paraphrase, not full prompt)
**Output summary:** What IBM Bob produced
**Acceptance:** [ACC / MOD / REJ / PAR]
**Verification:** [VER / UNVER]
**Developer notes:** What was changed, why a part was rejected, or what was learned
**Commit reference:** (fill in after commit)
**Files affected:** (fill in after implementation)
```

---

## 4. Usage Log — Architecture and Planning

### Session A-001
**Date:** 2025-07-20
**Category:** A — Architecture & Planning
**Task:** Generate complete project planning documentation for competition submission
**Prompt summary:** Requested generation of PRD, ARCHITECTURE, EVALUATION_PLAN, DELIVERY_PLAN, and IBM_BOB_USAGE documents for MechaCode Guardian, an Indonesian-first AI maintenance co-worker for mechatronics troubleshooting. Specified technology stack, constraints, target workflow, and competition context.
**Output summary:** IBM Bob produced all five documents: `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION_PLAN.md`, `docs/DELIVERY_PLAN.md`, `docs/IBM_BOB_USAGE.md`.
**Acceptance:** MOD
**Verification:** VER — developer reviewed all documents before committing
**Developer notes:**
- Documents reflect the developer's design intent; IBM Bob served as a structured writing tool.
- All open assumptions and unresolved decisions were explicitly requested to be flagged (and they are).
- Technology choices (Astra DB, IBM Docling, IBM Granite, FastAPI, React+Vite) were developer-specified, not IBM Bob-suggested.
- The evaluation metrics thresholds (Recall@5 ≥ 0.80, etc.) were specified by the developer; IBM Bob formatted and organised them.
- No unimplemented feature is claimed to work in any document.
**Commit reference:** *(to be filled)*
**Files affected:** `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION_PLAN.md`, `docs/DELIVERY_PLAN.md`, `docs/IBM_BOB_USAGE.md`

---

### Session A-002
**Date:** 2025-07-20
**Category:** A — Architecture & Planning
**Task:** Resolve four open decisions (UD-01, UD-02, UD-03, UD-05), create COMPETITION_REQUIREMENTS.md, and propagate all decisions consistently across all five planning documents.
**Prompt summary:** Developer provided four developer-approved decisions: fallback LLM = Gemini; retrieval thresholds (< 0.55 refuse, 0.55–0.67 escalate, ≥ 0.68 proceed); embedding model = `gemini-embedding-001` (3072-dim, same config for ingestion and query, Astra DB collection `mechacode_guardian_kb`, capstone collection not modified); knowledge base = original synthetic docs under `knowledge/synthetic/` with provenance labelling, no manufacturer manuals. Also provided competition requirements to document (July Wildcard Challenge, one submission, IBM Bob as primary partner, Gemini and Astra DB permitted, GitHub + prototype + README + video required, English video/submission, five judging criteria, July 31 deadlines, SkillsBuild certificate required, 40 Bobcoins non-extendable, checklist and disqualification-risk checklist required).
**Output summary:** IBM Bob produced:
- `docs/COMPETITION_REQUIREMENTS.md` (new file — full competition rules reference, submission checklist, disqualification-risk checklist)
- Updated `docs/PRD.md` — resolved UD-01/02/03/04/05; updated FR-02/03/04/09; updated Section 7 MVP scope; updated Section 11 from "Unresolved" to "Resolved Decisions" table
- Updated `docs/ARCHITECTURE.md` — resolved UD-01/02/03/04/05; updated embedding layer, Astra DB collection name, Mermaid diagram, data flow, RAG pipeline (ingestion + query), technology decisions table, deployment design, Section 12 split into Resolved/Open
- Updated `docs/EVALUATION_PLAN.md` — updated dataset construction (synthetic docs, not manufacturer manuals); updated sample cases table; updated ED-02 as resolved; added ED-06 (synthetic corpus disclosure)
- Updated `docs/DELIVERY_PLAN.md` — updated Day 1 (Google AI access, SkillsBuild certificate, correct collection name), Day 2 (synthetic doc authoring, correct embedder config), Day 3 (retrieval embedder with shared EmbeddingConfig), Day 5 (Gemini fallback provider); updated risk table; updated fallback plans R-03/R-06/R-07; updated decisions log
- Updated `docs/IBM_BOB_USAGE.md` — added this session (A-002)
**Acceptance:** MOD
**Verification:** VER — developer reviewed and approved all four decisions before requesting updates; all document changes directly reflect developer instructions.
**Developer notes:**
- All four UD decisions were developer-specified in exact detail; IBM Bob's role was consistent propagation across all documents and formatting.
- The competition requirement details (deadlines, Bobcoins, SkillsBuild, checklist) were provided by the developer from official competition materials; IBM Bob formatted and cross-referenced them.
- The COMPETITION_REQUIREMENTS.md deadline section went through two correction passes. First pass fixed the buffer figure (from "10 hours", "~13 hours", and "4 hours 59 minutes" to "~17 hours"). Second pass fixed the intermediate UTC and EDT conversions in the step-by-step blockquote: `18:00 WIB` correctly converts to `11:00 UTC` and `07:00 EDT` (not `07:00 UTC` / `03:00 EDT` as previously written). The final buffer of **16 hours 59 minutes (≈ 17 hours)** was correct after the first pass and is unchanged.
- UD-04 (frontend state management) was also resolved (React Context for MVP) as a side effect of this update sweep; this was not explicitly requested but is correct and consistent.
- UD-02 threshold calibration requirement is retained in all documents — the values are provisional pending Day 9 evaluation.
**Commit reference:** *(to be filled)*
**Files affected:** `docs/COMPETITION_REQUIREMENTS.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION_PLAN.md`, `docs/DELIVERY_PLAN.md`, `docs/IBM_BOB_USAGE.md`

---

*(Additional sessions will be logged here as development progresses. Each day's IBM Bob interactions should be recorded the same day.)*

---

## 5. Usage Log — Coding

> **Status:** No coding sessions have occurred yet. Entries will be added from Day 1 (July 21) onwards.

### Template entries to be completed:

| Expected Session IDs | Day | Planned Task |
|---|---|---|
| C-001 | Day 1 | Backend scaffold: FastAPI app skeleton, Pydantic schemas |
| C-002 | Day 2 | IBM Docling parser integration |
| C-003 | Day 2 | Chunker implementation |
| C-004 | Day 2 | Embedding API client |
| C-005 | Day 3 | Astra DB retrieval client |
| C-006 | Day 4 | Safety gate implementation |
| C-007 | Day 5 | LLM provider abstraction + ProviderRouter |
| C-008 | Day 5 | Prompt templates (Indonesian + English) |
| C-009 | Day 6 | FastAPI route handlers |
| C-010 | Day 6 | Reporting module |
| C-011 | Day 7 | React frontend components |
| C-012 | Day 7 | API client (TypeScript fetch wrapper) |

---

## 6. Usage Log — Testing

> **Status:** No testing sessions have occurred yet. Entries will be added from Day 3 onwards.

| Expected Session IDs | Day | Planned Task |
|---|---|---|
| T-001 | Day 3 | Unit tests for retrieval module |
| T-002 | Day 4 | Unit tests for safety gate |
| T-003 | Day 5 | Unit tests for prompt builder and response parser |
| T-004 | Day 9 | Evaluation runner script (`run_eval.py`) |
| T-005 | Day 9 | Evaluation dataset case construction |

---

## 7. Usage Log — Refactoring

> **Status:** No refactoring sessions have occurred yet.

*Entries will be added as development progresses and code is improved based on testing feedback.*

---

## 8. Usage Log — Security Review

> **Status:** No security review sessions have occurred yet. Planned for Day 10.

| Expected Session IDs | Day | Planned Task |
|---|---|---|
| S-001 | Day 10 | Review API input validation for injection risks |
| S-002 | Day 10 | Verify no secrets in codebase (`git grep` + IBM Bob review) |
| S-003 | Day 10 | Review CORS configuration |

---

## 9. Usage Log — Documentation

### Session D-001
*(Covered under A-001 — the five planning documents also constitute initial project documentation.)*

| Expected Session IDs | Day | Planned Task |
|---|---|---|
| D-002 | Day 10 | README.md — setup instructions, architecture summary, screenshots |
| D-003 | Day 10 | Inline docstrings for all public functions |

---

## 10. Usage Log — Deployment

> **Status:** No deployment sessions have occurred yet. Planned for Day 10–11.

| Expected Session IDs | Day | Planned Task |
|---|---|---|
| P-001 | Day 10 | `.env.example` review and documentation |
| P-002 | Day 10 | (Optional) Dockerfile for backend if VPS deployment chosen |
| P-003 | Day 11 | Final deployment verification |

---

## 11. Aggregate Summary

*This table will be updated at the end of the project (July 31).*

| Category | Sessions | ACC | MOD | REJ | PAR | VER | UNVER |
|---|---|---|---|---|---|---|---|
| A — Architecture | 2 | 0 | 2 | 0 | 0 | 2 | 0 |
| C — Coding | 0 | — | — | — | — | — | — |
| T — Testing | 0 | — | — | — | — | — | — |
| R — Refactoring | 0 | — | — | — | — | — | — |
| S — Security | 0 | — | — | — | — | — | — |
| D — Documentation | 0 | — | — | — | — | — | — |
| P — Deployment | 0 | — | — | — | — | — | — |
| **Total** | **2** | **0** | **2** | **0** | **0** | **2** | **0** |

---

## 12. Honest Disclosure Policy

The following principles govern this log:

1. **All substantive IBM Bob outputs that became part of the codebase or documentation are logged.** "Substantive" means anything beyond a single line of boilerplate.

2. **Acceptance status is honest.** If a large block of IBM Bob code was used with only cosmetic changes, it is logged as ACC, not MOD. MOD requires a description of what changed.

3. **Unverified outputs are flagged.** If an IBM Bob-generated function was committed without the developer running it or reading it critically, it is marked UNVER. These must be resolved before submission.

4. **Rejected outputs are logged too.** If IBM Bob proposed an approach that was rejected (e.g., using LangChain when the developer chose not to), this is noted — it demonstrates deliberate decision-making.

5. **IBM Bob did not make architectural decisions autonomously.** All technology choices, metrics thresholds, safety rules, and design patterns in this project were specified or explicitly approved by the developer. IBM Bob was used as a writing and coding tool, not as an autonomous architect.

6. **No AI-generated code was committed without reading.** (Target: all entries marked VER. Any UNVER entry is a risk flag to resolve before submission.)

---

*End of IBM_BOB_USAGE.md*
*Last updated: 2025-07-20 (Session A-002) by solo developer.*
