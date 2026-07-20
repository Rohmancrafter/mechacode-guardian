# Delivery Plan — MechaCode Guardian

**Version:** 0.2
**Date:** 2025-07-20 (updated same day with resolved decisions)
**Official Deadline:** July 31, 2026 at 11:59 PM ET (= August 1, 2026 at 10:59 AM WIB)
**Internal Deadline:** July 31, 2026 at 18:00 WIB (~17 hours before the official ET cutoff)
**Developer:** Solo developer, Windows 11, Intel i7 10th Gen, GTX 1650, 16 GB RAM
**Total window:** 12 days (July 20–31)

---

## Table of Contents

1. [Milestones Overview](#1-milestones-overview)
2. [Daily Execution Schedule](#2-daily-execution-schedule)
3. [Definition of Done](#3-definition-of-done)
4. [Main Risks](#4-main-risks)
5. [Fallback Plans](#5-fallback-plans)
6. [Decisions Log](#6-decisions-log)

---

## 1. Milestones Overview

| Milestone | ID | Target Date | Status |
|---|---|---|---|
| Documentation complete | M0 | July 20 | ✅ Done (today) |
| Development environment ready | M1 | July 21 | ⬜ |
| Document ingestion pipeline working | M2 | July 23 | ⬜ |
| Core backend: retrieval + safety gate | M3 | July 25 | ⬜ |
| Core backend: generation + reports | M4 | July 26 | ⬜ |
| Frontend MVP functional | M5 | July 28 | ⬜ |
| Evaluation dataset built and first eval run | M6 | July 29 | ⬜ |
| Bug fixes, polish, README update | M7 | July 30 | ⬜ |
| Final submission package ready | M8 | July 31 | ⬜ |

---

## 2. Daily Execution Schedule

### Day 0 — Sunday, July 20
**Theme: Planning and Documentation**

- [x] Read and understand competition brief
- [x] Inspect existing repository
- [x] Write PRD.md
- [x] Write ARCHITECTURE.md
- [x] Write EVALUATION_PLAN.md
- [x] Write DELIVERY_PLAN.md
- [x] Write IBM_BOB_USAGE.md

**Milestone:** M0 — Documentation complete

---

### Day 1 — Monday, July 21
**Theme: Environment Setup and Scaffolding**

- [ ] Verify access: watsonx.ai account, Astra DB account, Google AI account (for `gemini-embedding-001` and Gemini fallback), IBM Builder pass
- [ ] Verify IBM SkillsBuild completion certificate is obtained or initiate course immediately (**non-technical blocker**)
- [ ] Create watsonx.ai project, generate API key, note IBM Granite model ID
- [ ] Generate Google AI API key; confirm `gemini-embedding-001` access (output_dimensionality=3072)
- [ ] Create Astra DB database and collections: `mechacode_guardian_kb` (vector, 3072-dim, cosine) and `diagnosis_reports`; confirm capstone collection is **not** modified
- [ ] Scaffold backend: `backend/` directory, virtual environment (Python 3.11), install core dependencies: `fastapi`, `uvicorn`, `pydantic`, `astrapy`, `ibm-watsonx-ai`, `google-generativeai`, `langdetect`, `python-dotenv`
- [ ] Create `.env.example` with all required variable names: `ASTRA_DB_TOKEN`, `WX_API_KEY`, `WX_PROJECT_ID`, `GOOGLE_AI_API_KEY` (no real values)
- [ ] Scaffold frontend: `npm create vite@latest frontend -- --template react-ts`, install `react-i18next`
- [ ] Verify both servers start: `uvicorn backend.main:app --reload` and `npm run dev`
- [ ] Update `.gitignore` for frontend (`node_modules/`, `dist/`) and backend (`*.env`, `.venv/`)
- [ ] Commit: "chore: project scaffold"

**Milestone check:** Both dev servers run with no errors.

**Time estimate:** 4–6 hours

---

### Day 2 — Tuesday, July 22
**Theme: Synthetic Knowledge Base Creation + Ingestion Pipeline**

- [ ] Author synthetic documentation set (`knowledge/synthetic/`) — minimum 2 synthetic technical documents (e.g., `MechaCo_MC100_CNC_Manual.md`, `MechaCo_PL200_PLC_Manual.md`) with: realistic alarm codes, fault descriptions, troubleshooting steps, safety notes. Clearly label each file as "Synthetic training and demonstration material — not a real manufacturer document."
- [ ] Add provenance and licensing header to each synthetic document: author, date, license (e.g., CC BY 4.0 or proprietary), and explicit "synthetic" declaration.
- [ ] Install IBM Docling: `pip install docling`
- [ ] Implement `backend/ingestion/docling_parser.py`: parse Markdown/text → structured chunks
- [ ] Implement `backend/ingestion/chunker.py`: sliding window chunker (512 tokens, 64-token overlap); tag each chunk with `provenance: "synthetic"`
- [ ] Test chunker on first synthetic doc: verify chunk count, metadata preservation
- [ ] Implement `backend/ingestion/embedder.py`: call `gemini-embedding-001` (`task_type=RETRIEVAL_DOCUMENT`, `output_dimensionality=3072`), return normalised 3072-dim float vector
- [ ] Test embedding call: verify vector dimension is exactly 3072, confirm Indonesian text embeds without error
- [ ] Implement `scripts/ingest.py`: end-to-end CLI (`python scripts/ingest.py --file knowledge/synthetic/doc.md --collection mechacode_guardian_kb`)
- [ ] Run ingestion on first synthetic doc: verify chunks appear in Astra DB `mechacode_guardian_kb` console

**Milestone check:** At least one manual successfully ingested; chunks visible in Astra DB.

**Time estimate:** 6–8 hours

---

### Day 3 — Wednesday, July 23
**Theme: Ingestion Hardening + Retrieval Module**

- [ ] Author and ingest second synthetic document
- [ ] Add duplicate detection (hash check) to `ingest.py`
- [ ] Implement `backend/retrieval/astra_client.py`: ANN cosine search against `mechacode_guardian_kb`, return `List[Chunk]`
- [ ] Implement `backend/retrieval/embedder.py`: call `gemini-embedding-001` with `task_type=RETRIEVAL_QUERY`, `output_dimensionality=3072` — use shared `EmbeddingConfig` constant to enforce consistency with ingestion embedder
- [ ] Write unit test for retrieval: mock Astra DB response, verify chunk schema includes `provenance` field
- [ ] Manual retrieval test: submit a known query from synthetic doc, inspect top-K results in terminal, confirm similarity scores are in expected range
- [ ] Implement language detection in `backend/core/language.py` (`langdetect`)
- [ ] Commit: "feat: ingestion pipeline + retrieval module"

**Milestone:** M2 — Document ingestion pipeline working

**Time estimate:** 5–7 hours

---

### Day 4 — Thursday, July 24
**Theme: Safety Gate + Core Config**

- [ ] Create `data/safety_triggers.json` with minimum 20 trigger patterns (Bahasa Indonesia + English)
- [ ] Implement `backend/safety/gate.py`: regex scan of input and retrieved chunks against trigger list
- [ ] Implement escalation response schema in `backend/api/schemas.py`
- [ ] Write unit tests for safety gate: test each trigger category fires correctly
- [ ] Write unit test for SR-06: simulate empty retrieval, verify refusal response
- [ ] Implement `backend/core/config.py`: load all env vars, validate at startup
- [ ] Implement structured logging in `backend/core/logging.py`: session_id, provider, latency, escalation_flag, confidence_band
- [ ] Commit: "feat: safety gate + core config + logging"

**Milestone check:** Safety gate unit tests pass 100%.

**Time estimate:** 5–6 hours

---

### Day 5 — Friday, July 25
**Theme: Generation Module — LLM Provider Abstraction**

- [ ] Implement `backend/generation/providers/base.py`: `LLMProvider` Protocol
- [ ] Implement `backend/generation/providers/granite.py`: watsonx.ai IBM Granite provider
- [ ] Implement `backend/generation/providers/gemini.py`: Gemini fallback provider via `google-generativeai` SDK
- [ ] Implement `backend/generation/router.py`: `ProviderRouter` — try primary (Granite), on error retry Gemini fallback, emit `FALLBACK_USED` log
- [ ] Implement `backend/generation/prompts/diagnosis_id.txt` (Indonesian)
- [ ] Implement `backend/generation/prompts/diagnosis_en.txt` (English)
- [ ] Implement `backend/generation/prompt_builder.py`: inject chunks into prompt template
- [ ] Implement `backend/generation/parser.py`: parse JSON response from LLM → `DiagnosisOutput` schema
- [ ] Add citation validation: if LLM references chunk index outside retrieved set, strip and log `CITATION_ANOMALY`
- [ ] Write unit tests for prompt builder and response parser
- [ ] Commit: "feat: generation module + LLM provider abstraction"

**Milestone:** M3 — Core backend: retrieval + safety gate

**Time estimate:** 6–8 hours

---

### Day 6 — Saturday, July 26
**Theme: API Endpoints + Reporting Module**

- [ ] Implement `backend/api/routers/diagnose.py`: `POST /api/v1/diagnose` — full pipeline (retrieve → safety check → generate)
- [ ] Implement `backend/api/routers/report.py`: `POST /api/v1/report/{session_id}` — assemble and return Markdown report
- [ ] Implement `backend/reporting/assembler.py`: compile session data into `MarkdownReport`
- [ ] Implement Astra DB write for `diagnosis_reports` collection
- [ ] Add CORS middleware to FastAPI app
- [ ] Integration test: submit a full diagnosis request via `curl` or `httpx`, inspect full response JSON
- [ ] Integration test: generate a report for a completed session
- [ ] Commit: "feat: API endpoints + reporting module"

**Milestone:** M4 — Core backend: generation + reports

**Time estimate:** 5–7 hours

---

### Day 7 — Sunday, July 27
**Theme: Frontend — Diagnosis Flow**

- [ ] Design component tree: `SymptomForm`, `DiagnosisResult`, `EscalationNotice`, `Checklist`, `ReportDownload`
- [ ] Implement `SymptomForm`: equipment type, manufacturer, model, alarm code, symptom text, language toggle
- [ ] Implement API client: `src/api/diagnose.ts` — typed `fetch` wrapper
- [ ] Implement `DiagnosisResult`: render ranked causes, confidence band, citation badges
- [ ] Implement `EscalationNotice`: non-dismissable warning card, displayed before any other content when escalation_flag=true
- [ ] Implement `Checklist`: render ordered steps with Done/N/A/Blocked toggle
- [ ] Implement `ReportDownload`: trigger `POST /api/v1/report/{session_id}`, offer Markdown blob download
- [ ] Add i18n strings: Bahasa Indonesia (default) and English
- [ ] Commit: "feat: frontend diagnosis flow"

**Time estimate:** 7–9 hours

---

### Day 8 — Monday, July 28
**Theme: Frontend Polish + End-to-End Testing**

- [ ] Verify WCAG AA colour contrast for all text elements
- [ ] Add loading states and error states to all API calls (no blank screens)
- [ ] Add disclaimer text to diagnosis result: "AI-assisted recommendation — verify with qualified personnel"
- [ ] End-to-end manual test: full workflow from symptom input to report download
- [ ] End-to-end test: hazardous scenario → confirm escalation notice appears and checklist is absent
- [ ] End-to-end test: out-of-scope query → confirm SR-06 refusal message
- [ ] Test fallback provider: temporarily set primary API key to invalid → confirm fallback fires and logs
- [ ] Fix all blocking bugs found during E2E testing
- [ ] Commit: "fix: frontend polish + E2E fixes"

**Milestone:** M5 — Frontend MVP functional

**Time estimate:** 5–7 hours

---

### Day 9 — Tuesday, July 29
**Theme: Evaluation Dataset + First Eval Run**

- [ ] Build evaluation dataset: create 30 JSON case files in `tests/evaluation/dataset/`
- [ ] Label ground truth for each case (document + page + primary cause + escalation flag)
- [ ] Implement `tests/evaluation/run_eval.py`: loop over dataset, call API, collect metrics
- [ ] Run first evaluation pass
- [ ] Compute: Recall@5, MRR, Top-2 Accuracy, Citation Faithfulness, Escalation Recall (EM-01 to EM-08)
- [ ] Check CST-01 (escalation recall) and CST-02 (SR-06 refusal) — **both must be 100%**
- [ ] If either CST-01/CST-02 fails → immediate fix before proceeding
- [ ] Run baseline comparison: same 30 cases, Granite with no RAG
- [ ] Record all results in `tests/evaluation/results/eval_run_001.json`
- [ ] Commit: "eval: first evaluation run results"

**Milestone:** M6 — Evaluation dataset built and first eval run complete

**Time estimate:** 6–8 hours

---

### Day 10 — Wednesday, July 30
**Theme: Fixes, README, and Submission Prep**

- [ ] Address any evaluation failures from Day 9
- [ ] Run `pip-audit` to check for known vulnerabilities in Python dependencies
- [ ] Run `npm audit` for frontend dependencies
- [ ] Update `README.md`: project description, architecture summary, setup instructions, screenshots/demo GIF
- [ ] Verify `.env.example` is complete and `.env` is NOT committed
- [ ] Run final evaluation pass after fixes
- [ ] Prepare competition submission text (project description, innovation statement, challenge fit)
- [ ] Commit: "docs: README + submission prep"

**Milestone:** M7 — Bug fixes, polish, README update

**Time estimate:** 5–6 hours

---

### Day 11 — Thursday, July 31
**Theme: Final Submission**

- [ ] Final review of all 5 docs/ files for accuracy
- [ ] Final review of evaluation results — confirm all blocking criteria pass
- [ ] Final `git push` to main branch
- [ ] Submit to AI Builders Challenge platform before **18:00 WIB** internal deadline (~17 hours before official ET cutoff)
- [ ] Create GitHub release tag: `v0.1.0-competition`

**Milestone:** M8 — Final submission package ready

**Time estimate:** 2–3 hours + buffer

---

## 3. Definition of Done

A feature is **done** when ALL of the following apply:

- [ ] Code is committed to `main` with a descriptive commit message
- [ ] No secrets are present in any committed file (verified by `git grep -r "sk-" .` and similar)
- [ ] Relevant unit tests exist and pass
- [ ] The feature works end-to-end in a manual test on the developer's machine
- [ ] Any new environment variables are documented in `.env.example`
- [ ] No new `TODO` comments have been added without a corresponding task in this plan

The **MVP as a whole** is done when:

- [ ] All M1–M8 milestones are marked complete
- [ ] CST-01 (Safety Escalation Recall = 100%) passes
- [ ] CST-02 (SR-06 Refusal = 100%) passes
- [ ] Recall@5 ≥ 0.80
- [ ] P95 Latency ≤ 8 seconds
- [ ] Zero hallucinated citations
- [ ] README is up to date and setup instructions are verified

---

## 4. Main Risks

| Risk ID | Risk | Probability | Impact | Day First Relevant |
|---|---|---|---|---|
| R-01 | watsonx.ai free tier rate limits delay testing | High | Medium | Day 1 |
| R-02 | IBM Docling has parsing issues with synthetic Markdown documents | Low | Low | Day 2 |
| R-03 | `gemini-embedding-001` retrieval quality poor on Indonesian technical terms in synthetic docs | Low | High | Day 3 |
| R-04 | Astra DB ANN search returns low-quality results on synthetic content | Low | Medium | Day 3 |
| R-05 | IBM Granite output is not consistently structured JSON | Medium | High | Day 5 |
| R-06 | Gemini fallback provider configuration issue | Low | Medium | Day 5 |
| R-07 | Synthetic documentation too sparse — not enough content to reach Recall@5 ≥ 0.80 | Medium | High | Day 9 |
| R-08 | Evaluation recall <0.80 even with adequate synthetic docs | Medium | Medium | Day 9 |
| R-09 | Safety escalation recall <100% on first eval run | Low | Critical | Day 9 |
| R-10 | Developer unavailable due to personal circumstances | Unknown | High | Any |
| R-11 | IBM SkillsBuild certificate not obtained before deadline | Low | Critical | Day 1 |

---

## 5. Fallback Plans

### R-01 — watsonx.ai rate limits
- **Mitigation:** Request increased quota via IBM Builder program. Use mock LLM responses for frontend/unit development to avoid burning tokens.
- **Fallback:** Cache LLM responses for identical test inputs during development. Use fallback provider for non-critical development testing.

### R-02 — Docling parsing issues with synthetic Markdown documents
- **Mitigation:** Synthetic documents are Markdown/plain text — the easiest possible format for Docling or any text parser. This risk is low.
- **Fallback:** If Docling fails on Markdown for any reason, use Python's built-in file reader directly; chunker does not require Docling for plain-text sources.

### R-03 — Poor Indonesian embedding quality (`gemini-embedding-001`)
- **Mitigation:** `gemini-embedding-001` is a multilingual model with strong Indonesian support. Test with Indonesian synthetic text on Day 3 before proceeding.
- **Fallback:** If retrieval quality is unacceptable, add query augmentation: append the English translation of the Indonesian symptom description to the embedding input. This is a last resort — it should not be needed.

### R-04 — Low ANN quality on technical jargon
- **Mitigation:** Hybrid search: combine ANN (semantic) with keyword search (BM25-like) if Astra DB supports it.
- **Fallback:** Add a keyword pre-filter on alarm code field before ANN search to narrow the candidate set.

### R-05 — Inconsistent LLM JSON output
- **Mitigation:** Use structured output / function-calling mode if Granite supports it. Use retry-with-repair: send malformed JSON back to LLM with correction instruction.
- **Fallback:** If structured output is unreliable, use regex + heuristic extraction from free-text output.

### R-06 — Gemini fallback provider configuration issue
- **Mitigation:** Implement and smoke-test the Gemini provider on Day 5. The `google-generativeai` SDK is well-documented; configuration issues are expected to be minor.
- **Fallback:** If Gemini is genuinely unavailable on Day 5, add a mock fallback provider that returns a fixed "service degraded" response; remove fallback from competition demo scope and note it as a planned feature.

### R-07 — Synthetic documentation too sparse
- **Mitigation:** On Day 2, author documents with sufficient fault-case depth: minimum 15 distinct fault entries per document, each with: fault code, symptoms, probable causes (2–3), diagnostic steps, safety notes. Target 3,000–5,000 words per document.
- **Fallback:** Add a third synthetic document on Day 3 if Recall@5 is low during Day 3 manual retrieval tests. The knowledge/synthetic/ directory can hold any number of documents.

### R-08 — Evaluation recall <0.80
- **Mitigation:** Tune chunk size, overlap, and top-K. Try metadata filtering by equipment category to narrow search space.
- **Fallback:** Accept Recall@5 ≥ 0.70 for MVP if time does not allow further tuning; document this as a known limitation.

### R-09 — Safety escalation recall <100%
- **Immediate action (Day 9 evening):** Manually inspect the missed case. Add or fix the missing trigger pattern in `safety_triggers.json`. Re-run eval. This is a blocker — do not submit until resolved.

### R-10 — Developer unavailable
- **Fallback:** Defer non-blocking items (baseline comparison, bilingual UI polish) to reduce the critical path to: ingestion + retrieval + safety gate + basic frontend + one eval run.

---

## 6. Decisions Log

This log records decisions made during delivery, with dates and rationale.

| Date | Decision | Rationale | Alternatives Rejected |
|---|---|---|---|
| 2025-07-20 | Use Markdown for reports (not PDF) | Time risk; PDF rendering library adds a day of work | pdfkit, WeasyPrint |
| 2025-07-20 | No LangChain or LlamaIndex | Reduces dependency surface, improves debugability, keeps token usage explicit | LangChain RAG chain |
| 2025-07-20 | Astra DB as vector store, collection `mechacode_guardian_kb` | No self-hosted infra, free tier, native vector search; competition-permitted | Qdrant (self-hosted), pgvector |
| 2025-07-20 | Modular monolith (not microservices) | Solo developer, 12-day window; microservices add deployment overhead | Separate FastAPI services |
| 2025-07-20 | **UD-01 resolved:** Fallback LLM = Gemini | Developer has existing Google AI access; competition-permitted; same API covers embeddings | Groq (new account required), Ollama (GPU dependency) |
| 2025-07-20 | **UD-02 resolved:** Retrieval thresholds: <0.55 refuse, 0.55–0.67 escalate, ≥0.68 proceed (provisional) | Reasonable starting point; calibration required on Day 9 | Any single-threshold approach (less nuanced) |
| 2025-07-20 | **UD-03 resolved:** Embedding model = `gemini-embedding-001`, 3072-dim | Multilingual; competition-permitted; consistent with Gemini fallback LLM API | ibm/slate (English-only), paraphrase-multilingual-MiniLM (lower dim, local) |
| 2025-07-20 | **UD-05 resolved:** Knowledge base = original synthetic documentation under `knowledge/synthetic/` | Eliminates copyright risk; full content control; evaluation integrity | Manufacturer PDFs (redistribution rights unverified) |
