# IBM Bob Usage Log — MechaCode Guardian

**Version:** 0.2
**Date:** 2026-07-20 (updated same day with second session)
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
**Date:** 2026-07-20
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
**Date:** 2026-07-20
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

### Session C-001
**Date:** 2026-07-21
**Category:** C — Coding
**Task:** Scaffold the initial application foundation: backend (FastAPI modular monolith) and frontend (React + Vite + TypeScript).
**Prompt summary:** Developer requested a complete Day 1 scaffold covering: (1) FastAPI backend with all module packages (`core/`, `api/`, `ingestion/`, `retrieval/`, `generation/`, `safety/`, `reporting/`), config loading with environment variable validation, structured JSON logging, Pydantic v2 domain models, health/diagnose/report routers (stubs), LLMProvider Protocol, EmbeddingConfig singleton matching UD-03; (2) React + Vite + TypeScript frontend with react-i18next (id/en), typed API client, SymptomForm, DiagnosisResult, EscalationNotice, Checklist, ReportDownload components, DiagnosisPage, dev proxy to backend; (3) `.env.example` with all required variable names, no real values; (4) `.gitignore` updates for `.env`, `.venv/`, `node_modules/`, `dist/`; (5) `data/safety_triggers.json` with 21 patterns (≥ 20 required by FR-05.1); (6) `scripts/ingest.py` CLI stub; (7) `pyproject.toml` pytest config; (8) Unit tests for config, EmbeddingConfig, and FastAPI smoke tests; (9) README with all 5 competition topics; (10) IBM_BOB_USAGE.md session entry. Restrictions: no Astra DB writes, no LLM calls, no RAG pipeline, no real credentials.
**Output summary:** IBM Bob produced:
- `backend/main.py` — FastAPI app factory with CORS and router registration
- `backend/core/__init__.py`, `backend/core/config.py` — Settings with env var validation and singleton caching
- `backend/core/logging.py` — Structured JSON logger, Timer context manager, log_request()
- `backend/core/models.py` — Pydantic v2 domain models: Chunk, ProbableCause, ChecklistStep, EscalationTrigger, SessionData, ConfidenceBand, Language, HazardType
- `backend/core/embedding_config.py` — EmbeddingConfig singleton locked to UD-03 values
- `backend/api/schemas.py` — DiagnoseRequest, DiagnoseResponse, ReportResponse, HealthResponse, CitationBadge
- `backend/api/routers/health.py` — GET /health stub
- `backend/api/routers/diagnose.py` — POST /api/v1/diagnose stub (returns refusal_flag=true)
- `backend/api/routers/report.py` — POST /api/v1/report/{session_id} stub
- `backend/generation/providers/base.py` — LLMProvider Protocol, LLMResponse, ProviderError
- `backend/requirements.txt` — all Day 1 dependencies with docling commented for Day 2
- `pyproject.toml` — pytest configuration
- `frontend/` — Vite scaffold (react-ts template) with react-i18next added
- `frontend/vite.config.ts` — dev proxy for /api/* and /health to localhost:8000
- `frontend/src/api/client.ts` — typed TypeScript fetch wrappers
- `frontend/src/i18n/index.ts`, `locales/id.json`, `locales/en.json` — bilingual strings
- `frontend/src/components/SymptomForm.tsx` — FR-01 input form with language toggle
- `frontend/src/components/EscalationNotice.tsx` — non-dismissable safety alert (SR-02/03)
- `frontend/src/components/DiagnosisResult.tsx` — causes + citations + SR-04 disclaimer
- `frontend/src/components/Checklist.tsx` — ordered steps with safety notes (SR-05)
- `frontend/src/components/ReportDownload.tsx` — FR-07 Markdown download
- `frontend/src/pages/DiagnosisPage.tsx` — primary user journey page
- `frontend/src/main.tsx` — updated to mount DiagnosisPage
- `.env.example` — all variable names, no real values (NFR-04)
- `.gitignore` — added `.env`, `.venv/`, `node_modules/`, `dist/`, OS artefacts
- `data/safety_triggers.json` — 21 trigger patterns in bilingual regex (FR-05.1: minimum 20)
- `scripts/ingest.py` — CLI stub with argument parsing
- `README.md` — full rewrite covering all 5 competition topics (COMPETITION_REQUIREMENTS.md §5)
- `tests/unit/test_config.py` — 5 unit tests for Settings loading
- `tests/unit/test_embedding_config.py` — 5 unit tests for EmbeddingConfig UD-03 values
- `tests/unit/test_app_smoke.py` — 5 async smoke tests for all 3 routers
- `docs/IBM_BOB_USAGE.md` — this session entry (C-001)
**Acceptance:** MOD
**Verification:** UNVER — developer must: (1) read all generated files before committing; (2) run `pytest tests/unit/ -v` and confirm all tests pass; (3) run `npm run build` and confirm no TypeScript errors; (4) verify `.env` is not tracked by git.
**Developer notes:**
- All stub routers clearly state they are not operational. No placeholder pretends an external integration works.
- `EmbeddingConfig` is a frozen dataclass singleton to prevent accidental misconfiguration (UD-03 constraint).
- `safety_triggers.json` contains 21 patterns (exceeds minimum of 20), all in bilingual regex (Bahasa Indonesia + English).
- The `LLMProvider` Protocol uses `@runtime_checkable` so provider instances can be verified at runtime.
- `CORS_ORIGINS` defaults to `http://localhost:5173` (Vite dev server); must be updated before any public deployment.
- Frontend `App.tsx` from the Vite template is superseded by `DiagnosisPage.tsx` but left in place; it is not imported.
- `docling` is commented out in `requirements.txt` to avoid heavy transitive dependencies during scaffold; uncomment on Day 2.
- `pyproject.toml` sets `asyncio_mode = "auto"` for `pytest-asyncio` so async tests do not require per-test `@pytest.mark.asyncio` — verified compatible with the installed `pytest-asyncio>=0.23.0`.
**Commit reference:** *(to be filled)*
**Files affected:** See Output summary above (39 files created or modified)

---

### Session C-002
**Date:** 2026-07-22
**Category:** C — Coding
**Task:** Implement the deterministic dry-run ingestion pipeline.
**Prompt summary:** Developer requested implementation of the complete ingestion pipeline
under `backend/ingestion/` (manifest loading, secure path validation, Markdown loader,
heading-aware chunker, deterministic metadata/chunk-ID generation, dry-run report),
update of `scripts/ingest.py` (--file/--all/--dry-run with mutual-exclusion enforcement,
non-zero exit codes), comprehensive unit tests, and documentation updates.
Strict restrictions: no Astra DB, no Gemini embedding, no network calls, no credential access,
no heavy parser dependency (ARCHITECTURE.md §8 — Markdown corpus handled without docling),
HEAD must remain da4e749.
**Output summary:** IBM Bob produced:
- `backend/ingestion/manifest.py` — manifest loading and validation with typed dataclasses
- `backend/ingestion/path_security.py` — path validation; rejects traversal, symlinks, outside-corpus
- `backend/ingestion/loader.py` — UTF-8 Markdown reader (no network I/O)
- `backend/ingestion/chunker.py` — heading-aware, paragraph-aware, safety-atomic chunker
- `backend/ingestion/metadata.py` — deterministic chunk ID (SHA-256) + citation metadata
- `backend/ingestion/dry_run.py` — human-readable dry-run summary with explicit no-DB/no-embedding confirmation
- `backend/ingestion/pipeline.py` — orchestrator wiring all modules
- `backend/ingestion/__init__.py` — updated with module docstring
- `scripts/ingest.py` — full rewrite: --file/--all mutually exclusive, --dry-run required, exit codes 0/1/2/3
- `tests/unit/test_ingestion.py` — 61 unit tests covering all required scenarios
- `README.md` — added dry-run PowerShell commands; updated implementation status
- `docs/IBM_BOB_USAGE.md` — this session entry (C-002)
**Acceptance:** MOD
**Verification:** VER — developer ran all validations:
  `py -3.12 -m pytest tests/unit -v` → 76 passed
  `py -3.12 scripts/ingest.py --file knowledge/synthetic/MGC-MOTOR-001.md --dry-run` → 51 chunks, 14 sections, 0 failures
  `py -3.12 scripts/ingest.py --all --dry-run` → 5 files, 226 total chunks, 0 failures
  `npm --prefix frontend run build` → success
  HEAD confirmed da4e749, no commit or push performed.
**Developer notes:**
- ASSUMPTION [ingestion-chunker-A1]: chunk size uses character-based proxy (2048 chars ≈ 512 tokens,
  256 chars ≈ 64-token overlap) because ARCHITECTURE.md §8 explicitly avoids heavy tokeniser dependencies
  for the current Markdown corpus. Reported explicitly in dry-run output.
- `docling` is NOT used in this session — the pure-Python chunker handles the Markdown corpus correctly.
  docling will be integrated when PDF/DOCX sources are added.
- Safety-warning paragraphs (⚠, ESCALATION, WARNING) are marked as atomic blocks and never split.
- All chunk IDs are deterministic: `{doc_id}::{index:04d}::{sha256[:12]}`.
- `manifest.json` has `approved_for_rag: false` on all documents per the Day 3 audit (D-003);
  the pipeline accepts this — approval status is not enforced in dry-run mode.
- LF/CRLF line-ending warnings from `git diff --check` are normal on Windows with core.autocrlf=true;
  they are not whitespace errors and do not affect the diff content.
**Commit reference:** *(to be filled on commit)*
**Files affected:** `backend/ingestion/__init__.py`, `backend/ingestion/manifest.py`,
  `backend/ingestion/path_security.py`, `backend/ingestion/loader.py`,
  `backend/ingestion/chunker.py`, `backend/ingestion/metadata.py`,
  `backend/ingestion/dry_run.py`, `backend/ingestion/pipeline.py`,
  `scripts/ingest.py`, `tests/unit/test_ingestion.py`,
  `README.md`, `docs/IBM_BOB_USAGE.md`

---

### Template entries to be completed (remaining):

| Expected Session IDs | Day | Planned Task |
|---|---|---|
| C-003 | Day 3 | Astra DB retrieval client |
| C-004 | Day 4 | Safety gate implementation |
| C-005 | Day 5 | LLM provider abstraction + ProviderRouter |
| C-006 | Day 5 | Prompt templates (Indonesian + English) |
| C-007 | Day 6 | FastAPI route handlers |
| C-008 | Day 6 | Reporting module |
| C-009 | Day 7 | React frontend components |
| C-010 | Day 7 | API client (TypeScript fetch wrapper) |

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

---

### Session D-002
**Date:** 2026-07-20
**Category:** D — Documentation
**Task:** Create the synthetic knowledge corpus for the MechaCode Guardian RAG pipeline under `knowledge/synthetic/`.
**Prompt summary:** Developer requested eight files constituting a complete synthetic knowledge corpus: README.md (corpus purpose, scope, provenance, licensing, safety limitations, prohibited uses), LICENSE.md (CC BY-NC 4.0, Muhammad Nur Rohman, no-warranty/no-industrial-use notice), manifest.json (machine-readable document registry for RAG ingestion), and five technical documents: MGC-SAFETY-001 (general isolation/LOTO/hazard/escalation rules), MGC-MOTOR-001 (24 V DC training motor — 5 fault scenarios), MGC-SENSOR-001 (inductive proximity sensor — 7 fault scenarios), MGC-PLC-001 (training PLC/I/O — 5 fault scenarios), MGC-PNEUMATIC-001 (low-pressure pneumatic — 5 fault scenarios). Requirements included: stable citation IDs, Indonesian symptom aliases, bilingual glossaries, symptom tables, possible-cause tables, safe inspection checklists, fictional specifications, stop conditions, prohibited actions, escalation conditions, and 700–1000 words per technical document.
**Output summary:** IBM Bob produced all eight files:
- `knowledge/synthetic/README.md` — corpus overview, provenance, licensing, safety limitations, intended use, prohibited use, file index, evaluation coverage design
- `knowledge/synthetic/LICENSE.md` — CC BY-NC 4.0 full terms, no-warranty notice, no-industrial-use safety warning, author identification
- `knowledge/synthetic/manifest.json` — machine-readable registry of all five documents with document_id, title, version, language, license, provenance, equipment_type, fictional_equipment_name, approved_for_rag, safety_classification, and notes per document
- `knowledge/synthetic/MGC-SAFETY-001.md` — 9 sections covering definitions, 5 fundamental safety rules, 4 hazard categories (electrical, mechanical, pneumatic, chemical), LOTO sequence, pre-inspection prerequisites, 8 prohibited actions, 8 escalation triggers, bilingual glossary
- `knowledge/synthetic/MGC-MOTOR-001.md` — 5 fault scenarios (failure to start, overheating, abnormal vibration, intermittent operation, overload) with possible-cause tables, safe inspection steps, stop conditions; fictional MTR-24 specifications; bilingual glossary
- `knowledge/synthetic/MGC-SENSOR-001.md` — 7 fault scenarios (no signal, unstable signal, incorrect detection, alignment, contamination, wiring faults, escalation) for fictional SNS-10 inductive sensor; bilingual glossary
- `knowledge/synthetic/MGC-PLC-001.md` — 5 fault scenarios (missing input, inactive output, communication fault, unexpected machine state, safe diagnostic isolation) for fictional PLC-200; bilingual glossary
- `knowledge/synthetic/MGC-PNEUMATIC-001.md` — 5 fault scenarios (weak movement, failure to move, leakage, inconsistent motion, unsafe pressure) plus explicit depressurisation procedure for fictional PNU-05; bilingual glossary
**Acceptance:** PAR
**Verification:** UNVER — corpus content has not yet been manually reviewed by the developer. All specifications, fault codes, and procedures must be checked for internal consistency, safety accuracy, and evaluation usability before ingestion.
**Developer notes:**
- All content is original and synthetic. No manufacturer manual was reproduced or paraphrased.
- All fictional specifications are labelled with "⚠ fictional training value" notices.
- Every technical document carries a prominent synthetic-document disclaimer in its header.
- Safety-critical scenarios (MGC-SAFETY-001 §4.1, MGC-PNEUMATIC-001 §3.5, MGC-PLC-001 §3.4) are marked as escalation-required. The RAG system must not override these escalations.
- The pneumatic over-pressure scenario (MGC-PNEUMATIC-001 §3.5) is the highest-risk scenario in the corpus and must be verified as matching entries in `data/safety_triggers.json`.
- Indonesian aliases are present in symptom tables and bilingual glossaries but have not been tested against `gemini-embedding-001` retrieval. Bilingual retrieval quality must be validated on Day 3 per DELIVERY_PLAN.md.
- The corpus was designed to cover all five evaluation categories (A, B, C, D, E) defined in EVALUATION_PLAN.md §2.1. This must be confirmed when the evaluation dataset is constructed on Day 9.
- Acceptance is PAR because the developer must review and approve the corpus content before it is ingested. Any section that is factually incorrect or misleading from a safety perspective must be corrected before ingestion.
**Commit reference:** *(to be filled)*
**Files affected:** `knowledge/synthetic/README.md`, `knowledge/synthetic/LICENSE.md`, `knowledge/synthetic/manifest.json`, `knowledge/synthetic/MGC-SAFETY-001.md`, `knowledge/synthetic/MGC-MOTOR-001.md`, `knowledge/synthetic/MGC-SENSOR-001.md`, `knowledge/synthetic/MGC-PLC-001.md`, `knowledge/synthetic/MGC-PNEUMATIC-001.md`

---

### Session D-003
**Date:** 2026-07-20
**Category:** D — Documentation
**Task:** Pre-commit audit of the synthetic knowledge corpus under `knowledge/synthetic/`.
**Prompt summary:** Developer requested a strict audit of all corpus files covering: date accuracy (competition year 2026), citation consistency (document IDs vs equipment names), manifest validation (approved_for_rag, path existence, document count), SR-01 through SR-08 coverage mapping, safety content review, internal consistency check, Indonesian language quality, and provenance/licensing accuracy.
**Output summary:** IBM Bob performed a full inspection of all nine target files and produced the following corrections:
- Corrected all document `Date` headers from the incorrect prior-year date to `2026-07-20` in all eight corpus files and in `docs/PRD.md` and `docs/IBM_BOB_USAGE.md`.
- Set `approved_for_rag: false` on all five documents in `manifest.json` (was incorrectly `true`).
- Corrected `manifest.json` `created` field to `2026-07-20`.
- Updated `README.md` §3 (Provenance Statement) to honestly state that the corpus was created under Muhammad Nur Rohman's direction with IBM Bob assistance; removed the false claim that every sentence was personally authored by the developer without assistance.
- Updated `LICENSE.md` copyright year to 2026 and added provenance attribution footnote.
- Added SR-03 coverage paragraph to `MGC-SAFETY-001 §8` (escalation notice must be topmost priority element — previously unaddressed in corpus).
- Harmonised LOTO Indonesian term in `MGC-SAFETY-001 §2` to `Kunci/Tanda Pengaman (LOTO)` (consistent with §9 glossary).
- Corrected `MGC-SENSOR-001 §3.2 step 3` voltage threshold (was `< 20 V / > 28 V`; corrected to reflect the nominal expected range of 22–26 V DC with clear escalation language, consistent with §3.1 and §2 specifications).
- Corrected `docs/PRD.md §7` MVP date from the incorrect prior-year date to `2026-07-31`.
- Corrected all resolved decision dates in `docs/PRD.md §11.2` from the incorrect prior-year date to `2026-07-20`.
**Acceptance:** PAR
**Verification:** UNVER — corrections address structural and factual issues but developer must independently verify: (a) SR coverage mapping is complete; (b) all fictional values are self-consistent; (c) Indonesian aliases are idiomatic for the target technician audience.
**Developer notes:**
- Corpus status remains PAR / UNVER. No content has been marked approved or verified.
- No application code was modified. No commit or push was performed.
- All five documents remain at `approved_for_rag: false`. Developer must set this to `true` only after completing manual review of each document.
- Remaining open assumptions: fictional voltage/current/resistance thresholds are internally consistent but empirically unvalidated; Indonesian alias retrieval quality against `gemini-embedding-001` has not been tested; SR-04, SR-07, SR-08 enforcement depends on system implementation, not corpus content.
**Commit reference:** *(to be filled)*
**Files affected:** `knowledge/synthetic/README.md`, `knowledge/synthetic/LICENSE.md`, `knowledge/synthetic/manifest.json`, `knowledge/synthetic/MGC-SAFETY-001.md`, `knowledge/synthetic/MGC-MOTOR-001.md`, `knowledge/synthetic/MGC-SENSOR-001.md`, `knowledge/synthetic/MGC-PLC-001.md`, `knowledge/synthetic/MGC-PNEUMATIC-001.md`, `docs/PRD.md`, `docs/IBM_BOB_USAGE.md`

---

| Expected Session IDs | Day | Planned Task |
|---|---|---|
| D-004 | Day 10 | README.md — setup instructions, architecture summary, screenshots |
| D-005 | Day 10 | Inline docstrings for all public functions |

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
| C — Coding | 1 | 0 | 1 | 0 | 0 | 0 | 1 |
| T — Testing | 0 | — | — | — | — | — | — |
| R — Refactoring | 0 | — | — | — | — | — | — |
| S — Security | 0 | — | — | — | — | — | — |
| D — Documentation | 3 | 0 | 0 | 0 | 3 | 0 | 3 |
| P — Deployment | 0 | — | — | — | — | — | — |
| **Total** | **6** | **0** | **3** | **0** | **3** | **2** | **4** |

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
*Last updated: 2026-07-22 (Session C-002 — deterministic dry-run ingestion pipeline) by Muhammad Nur Rohman.*
