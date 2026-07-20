# Product Requirements Document — MechaCode Guardian

**Version:** 0.2
**Date:** 2026-07-20 (updated same day with resolved decisions)
**Author:** Solo Developer
**Competition:** AI Builders Challenge with IBM Bob — Wildcard Challenge (Intelligent Systems for the Future of Work)
**Official deadline:** July 31, 2026 at 11:59 PM ET (= August 1, 2026 at 10:59 AM WIB)
**Internal deadline:** July 31, 2026 at 18:00 WIB (~17 hours before the official ET cutoff)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Target Users](#2-target-users)
3. [Jobs-to-be-Done](#3-jobs-to-be-done)
4. [User Journey](#4-user-journey)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [MVP Scope](#7-mvp-scope)
8. [Out-of-Scope Items](#8-out-of-scope-items)
9. [Safety Requirements](#9-safety-requirements)
10. [Measurable Acceptance Criteria](#10-measurable-acceptance-criteria)
11. [Open Assumptions and Unresolved Decisions](#11-open-assumptions-and-unresolved-decisions)

---

## 1. Problem Statement

Mechatronics technicians in Indonesian manufacturing, automotive, and industrial facilities spend a disproportionate amount of time searching fragmented technical manuals, relying on colleague memory, or making trial-and-error repairs that may cause secondary damage or safety incidents.

Key pain points:
- **Knowledge fragmentation.** Equipment manuals exist in multiple languages (Japanese, English, Bahasa Indonesia), formats (PDF, scanned paper), and storage locations. Retrieval is slow and inconsistent.
- **High-stakes errors.** Incorrect fault diagnosis on CNC machines, PLCs, or industrial robots can cause equipment damage (cost: millions of IDR) or personal injury.
- **Skilled technician shortage.** Senior technicians are scarce. Junior staff lack structured guidance for unfamiliar fault codes or symptom patterns.
- **No audit trail.** Verbal recommendations leave no traceable record; compliance audits and insurance claims suffer.
- **Language barrier.** Most technical content is in English or Japanese; Indonesian-speaking technicians lose nuance during improvised translation.

MechaCode Guardian addresses these pain points by acting as an AI-powered maintenance co-worker: it grounds every answer in ingested technical documents, shows explicit citations, flags hazardous scenarios for human escalation, and generates auditable diagnosis reports.

---

## 2. Target Users

| Persona | Role | Technical Level | Primary Need |
|---|---|---|---|
| **Teknisi Junior** | Field technician, ≤3 years experience | Low–Medium | Step-by-step guided diagnosis |
| **Teknisi Senior** | Senior technician / maintenance lead | High | Fast retrieval from dense manuals, cross-equipment reference |
| **Supervisor Maintenance** | Shift/maintenance supervisor | Medium | Audit trail, escalation status, KPI visibility |
| **Safety Officer** | HSE / EHS officer | Medium | Confirmation that safety procedures are enforced |
| **Trainer / Instructor** | In-house training facilitator | High | Generating case-based training material from real incidents |

> **Assumption A1:** The initial MVP targets Teknisi Junior and Teknisi Senior. Supervisor and Safety Officer views are post-MVP.

---

## 3. Jobs-to-be-Done

| JTBD | Trigger | Desired Outcome |
|---|---|---|
| **Diagnose a fault** | Machine shows alarm code or abnormal behaviour | Ranked list of probable causes with supporting evidence |
| **Follow a safe inspection sequence** | Need to investigate without causing secondary damage | Ordered, safety-gated checklist tailored to equipment state |
| **Translate and understand documentation** | Manual is in English or Japanese | Indonesian-language explanation grounded in that document |
| **Escalate a high-risk situation** | System detects hazardous scenario or low confidence | Clear escalation notice sent to senior technician |
| **Generate an audit report** | Repair completed, documentation required | PDF/Markdown report with timestamps, evidence, and actions taken |
| **Learn from a past case** | Recurring fault pattern | Summary of how similar cases were resolved previously |

---

## 4. User Journey

### Primary Journey: Fault Diagnosis

```
1. INPUT
   User opens web app → selects equipment type from a list
   → describes symptoms in Bahasa Indonesia or English (free text or structured form)

2. CONTEXT RETRIEVAL
   Backend embeds the query using gemini-embedding-001 (3072-dim)
   → searches Astra DB collection mechacode_guardian_kb
   → retrieves top-K chunks from synthetic technical documentation
   → each chunk carries: document ID, page number, section title, language

3. EVIDENCE RANKING
   RAG prompt sent to IBM Granite via watsonx.ai
   → LLM synthesises retrieved chunks into ranked probable causes
   → each cause tagged with: confidence band (High / Medium / Low), evidence source(s)

4. SAFETY GATE CHECK
   Backend evaluates safety flags:
   - High-voltage / stored energy present?
   - Is confidence band Low?
   - Is symptom pattern in the critical-escalation list?
   → If ANY flag triggers → escalation notice displayed prominently; checklist disabled

5. CHECKLIST GENERATION (if safe to proceed)
   LLM generates step-by-step inspection checklist
   → each step contains: action, safety note (if any), expected reading/result, evidence citation

6. REPORT GENERATION
   User marks steps complete / adds findings
   → System compiles diagnosis report: timestamp, equipment, symptoms, causes, steps, citations, outcome
   → Report exported as Markdown (PDF rendering: post-MVP)

7. FEEDBACK LOOP
   User rates the session (thumbs up/down + optional comment)
   → Rating stored for evaluation and model-improvement planning
```

---

## 5. Functional Requirements

### FR-01 Equipment and Symptom Input
- FR-01.1: System accepts free-text symptom description in Bahasa Indonesia and English.
- FR-01.2: System accepts structured input: equipment category, manufacturer, model, alarm code.
- FR-01.3: System detects language of input and responds in the same language (Indonesian default).

### FR-02 Document Ingestion (offline / admin workflow)
- FR-02.1: Admin can ingest synthetic documentation files (Markdown/plain text, stored under `knowledge/synthetic/`) via a CLI ingest script. Manufacturer PDFs are not ingested unless their redistribution rights are verified in writing.
- FR-02.2: IBM Docling parses and chunks documents; chunks are embedded using `gemini-embedding-001` (3072-dimensional, task type: `RETRIEVAL_DOCUMENT`) and stored in the Astra DB collection `mechacode_guardian_kb`.
- FR-02.3: Each chunk stores: source document name, page/section reference, section title, language, ingestion timestamp, provenance label (`synthetic`).
- FR-02.4: Duplicate documents (same hash) are detected and skipped.
- FR-02.5: All knowledge base documents are clearly labelled as synthetic training and demonstration material. No document may be ingested without an explicit provenance and licensing note.

### FR-03 Evidence Retrieval
- FR-03.1: System performs dense vector retrieval over the Astra DB collection `mechacode_guardian_kb`.
- FR-03.2: System returns a minimum of 3 and maximum of 10 evidence chunks per query.
- FR-03.3: Each retrieved chunk includes a cosine similarity score visible to the backend (not necessarily to the user).
- FR-03.4: Query embeddings are generated using `gemini-embedding-001` (3072-dimensional, task type: `RETRIEVAL_QUERY`) — the same model, dimensionality, and task configuration used at ingestion time.

### FR-04 Cause Ranking and Diagnosis
- FR-04.1: System presents ranked probable causes (1st, 2nd, 3rd most likely) with a plain-language explanation.
- FR-04.2: Each cause is attributed to one or more specific evidence chunks (document + page/section).
- FR-04.3: System assigns a confidence band based on retrieval similarity scores and LLM self-report:
  - **High:** composite score ≥ 0.68 — diagnosis proceeds.
  - **Medium:** composite score 0.55–0.67 — diagnosis proceeds with a clarification prompt or technician escalation recommendation.
  - **Low:** composite score < 0.55 — insufficient evidence; triggers SR-06 refusal or escalation.
  > **Note (A2 resolved):** Initial retrieval policy thresholds are: < 0.55 = refuse, 0.55–0.67 = escalate/clarify, ≥ 0.68 = proceed. These are provisional and **must be calibrated** against the 30-case evaluation dataset before the final submission. See EVALUATION_PLAN.md §12, ED-03.

### FR-05 Safety Gate
- FR-05.1: System maintains a configurable list of escalation-trigger keywords and symptom patterns (e.g., "tegangan tinggi", "arc flash", "stored energy", "gas leak").
- FR-05.2: If a safety trigger fires OR confidence band is Low, the system MUST display an escalation notice before any checklist.
- FR-05.3: Escalation notice is non-dismissable; it cannot be clicked through to proceed.
- FR-05.4: The checklist page is not rendered when escalation is active.

### FR-06 Inspection Checklist
- FR-06.1: System generates an ordered step-by-step checklist for each primary probable cause.
- FR-06.2: Each step includes: action description, tool/instrument required, safety precaution if applicable, expected outcome, evidence citation.
- FR-06.3: User can mark each step as Done / Not Applicable / Blocked.

### FR-07 Diagnosis Report
- FR-07.1: System assembles a diagnosis report at session close.
- FR-07.2: Report includes: session ID, timestamp, equipment details, symptoms, ranked causes, checklist state, all citations, user feedback.
- FR-07.3: Report is exportable as Markdown. *(PDF export: post-MVP — see Section 8.)*
- FR-07.4: Reports are persisted server-side for a minimum of 30 days.
  > **Assumption A3:** Storage for reports will use the filesystem or Astra DB; decision deferred to architecture phase.

### FR-08 Bilingual Support
- FR-08.1: UI labels and static text available in Bahasa Indonesia and English; default is Bahasa Indonesia.
- FR-08.2: LLM prompt templates are maintained in both languages; language selection is automatic based on input detection.
- FR-08.3: Quoted evidence from English-language manuals is presented in English with an Indonesian summary.

### FR-09 Provider Abstraction
- FR-09.1: LLM calls are routed through a provider abstraction layer with two registered providers:
  - **Primary:** IBM Granite via watsonx.ai.
  - **Fallback:** Gemini (developer's existing Google AI access).
- FR-09.2: If the primary provider returns an error or timeout, the system automatically retries on the Gemini fallback provider and logs a `FALLBACK_USED` event.
- FR-09.3: Both providers implement the same `LLMProvider` protocol; the router is provider-agnostic and can be extended to additional providers post-MVP.

---

## 6. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Latency | End-to-end diagnosis response (query → ranked causes displayed) ≤ 8 seconds at P95 under normal load. |
| NFR-02 | Latency | Checklist generation ≤ 5 seconds after causes are confirmed. |
| NFR-03 | Reliability | System handles LLM provider error with fallback; no blank screen for the user. |
| NFR-04 | Security | No secrets (API keys, tokens) committed to the git repository. All credentials loaded from environment variables or a secrets manager. |
| NFR-05 | Security | Uploaded documents are validated for type (PDF/DOCX only) and size (max 50 MB per file). |
| NFR-06 | Privacy | No personally identifiable information (PII) is stored in query logs. Session IDs are anonymous UUIDs. |
| NFR-07 | Cost | Total LLM API cost per diagnosis session ≤ USD 0.05 (target), ≤ USD 0.15 (ceiling). |
| NFR-08 | Deployability | System runs on developer's local machine (Intel i7 10th Gen, GTX 1650, 16 GB RAM) without GPU-dependent local models. |
| NFR-09 | Deployability | All required infrastructure is cloud-hosted (Astra DB, watsonx.ai, Google AI) except the backend process, which may run locally or on a low-cost VPS for demo purposes. |
| NFR-10 | Maintainability | Backend follows a modular monolith structure; each subsystem (ingestion, retrieval, generation, safety, reporting) is a separate Python module. |
| NFR-11 | Observability | Backend logs each request with: session ID, query hash (not raw query), provider used, latency, confidence band, escalation flag. |
| NFR-12 | Accessibility | Frontend passes WCAG 2.1 AA colour contrast for all text elements. |

---

## 7. MVP Scope

The MVP must be demonstrable by **2026-07-31**. It is defined as the minimum feature set that proves the core value proposition:

> *"MechaCode Guardian can take a symptom description, retrieve grounded evidence from synthetic technical documentation, produce a ranked diagnosis with citations, enforce a safety gate, and generate a checklist — all in Indonesian or English."*

**In-MVP features:**
- Web UI (React + Vite + TypeScript) with symptom input form and diagnosis output view
- FastAPI backend with all core endpoints
- Astra DB collection `mechacode_guardian_kb` populated with synthetic mechatronics documentation (`knowledge/synthetic/`)
- IBM Docling ingestion CLI script
- IBM Granite (watsonx.ai) as primary LLM; Gemini as registered fallback LLM
- `gemini-embedding-001` (3072-dim) for all embeddings — ingestion and query
- Evidence retrieval + ranked causes + citation display
- Safety gate with keyword-based escalation trigger list (minimum 20 patterns)
- Three-tier retrieval policy (refuse / escalate+clarify / proceed) calibrated against evaluation dataset
- Step-by-step checklist generation
- Markdown diagnosis report export
- Language detection and bilingual response
- Basic session logging

---

## 8. Out-of-Scope Items

The following are explicitly excluded from the MVP:

| Item | Reason |
|---|---|
| PDF report export | Requires rendering library; time risk |
| User authentication / login | Adds complexity; demo uses open access |
| Supervisor / Safety Officer dashboard | Post-MVP persona |
| Feedback loop integration back into the model | No fine-tuning in scope |
| Mobile-native app (iOS/Android) | Web-responsive is sufficient |
| Image/photo upload for fault diagnosis | Multimodal RAG is out of scope |
| Real-time IoT sensor data ingestion | Infrastructure out of scope |
| Offline / on-device LLM inference | Hardware limitation; no value for demo |
| Multi-tenant / enterprise deployment | Post-competition feature |
| Integration with CMMS or ERP systems | Out of scope |

---

## 9. Safety Requirements

Safety is a first-class requirement given the industrial context. The following rules are mandatory, not optional:

| ID | Rule |
|---|---|
| SR-01 | The system MUST NOT generate a diagnosis checklist for any session in which a safety-trigger pattern is detected in the input or in retrieved evidence. |
| SR-02 | The escalation notice MUST identify the nature of the hazard (e.g., "High-voltage detected — do not proceed without a licensed electrician"). |
| SR-03 | The escalation notice MUST be the topmost, highest-visual-priority element on the page when active. |
| SR-04 | The system MUST NOT present confidence scores as certainties. All outputs must carry a disclaimer: "This is an AI-assisted recommendation. Always verify with the applicable technical manual and qualified personnel." |
| SR-05 | Every checklist step that involves live electrical, hydraulic, or pneumatic systems MUST include a safety precaution note sourced from the technical manual. |
| SR-06 | If no relevant evidence is found in the knowledge base (retrieval score below minimum threshold), the system MUST refuse to generate a diagnosis and advise the user to consult the official manual directly. |
| SR-07 | The escalation trigger keyword list MUST be version-controlled, editable without code deployment, and auditable. |
| SR-08 | The system MUST NOT fabricate citations. If a statement cannot be attributed to a retrieved chunk, it must be labelled "general recommendation — no document source" and presented with reduced prominence. |

---

## 10. Measurable Acceptance Criteria

| ID | Criterion | Measurement Method | Target |
|---|---|---|---|
| AC-01 | Retrieval Recall | Evaluation dataset (see EVALUATION_PLAN.md) — does the correct evidence appear in top-K? | Recall@5 ≥ 0.80 |
| AC-02 | Cause Ranking Accuracy | Expert-labelled 30-case dataset — is the correct primary cause ranked #1 or #2? | Top-2 Accuracy ≥ 0.75 |
| AC-03 | Citation Faithfulness | Manual spot-check: does each cited chunk actually support the stated claim? | ≥ 90% of citations verified faithful |
| AC-04 | Safety Gate Recall | All 10 critical-risk test cases trigger escalation. | 10/10 (100%) |
| AC-05 | No Hallucinated Citation | LLM does not invent a document name or page number that does not exist. | 0 hallucinated citations in 30-case test |
| AC-06 | Latency | Median end-to-end response time (query → causes displayed). | ≤ 8 seconds |
| AC-07 | Bilingual Response | Input in Indonesian returns Indonesian response; input in English returns English response. | 100% language match across 10-case language test |
| AC-08 | Fallback Provider | Simulated primary-provider failure results in seamless fallback and correct response. | 100% success across 5 simulated failures |
| AC-09 | Report Completeness | Every generated report contains: session ID, timestamp, equipment, causes, citations, checklist state. | 100% of test reports pass schema validation |
| AC-10 | Cost per Session | LLM API cost for a single diagnosis session. | ≤ USD 0.05 average across 10 test sessions |

---

## 11. Assumptions and Decisions

### 11.1 Open Assumptions

| ID | Type | Description | Impact if Wrong |
|---|---|---|---|
| A1 | Assumption | MVP targets Teknisi Junior and Senior only. | Low — supervisor view can be added post-MVP |
| A2 | Assumption | Retrieval policy thresholds (< 0.55 refuse, 0.55–0.67 escalate, ≥ 0.68 proceed) are provisional starting points requiring calibration. | Medium — must be validated against 30-case evaluation dataset |
| A3 | Assumption | Diagnosis reports stored on filesystem initially; Astra DB `diagnosis_reports` collection used if filesystem is insufficient. | Low |
| A4 | Assumption | Synthetic documentation covers enough mechatronics fault patterns to produce meaningful Recall@5 ≥ 0.80 results. | High — if synthetic docs are too sparse, retrieval quality will be poor; document depth must be validated on Day 9 |

### 11.2 Resolved Decisions

| ID | Decision | Resolved Value | Date |
|---|---|---|---|
| UD-01 | Fallback LLM provider | **Gemini** (developer's existing Google AI access). Groq and Ollama rejected. | 2026-07-20 |
| UD-02 | Retrieval similarity thresholds | **< 0.55 = refuse (SR-06); 0.55–0.67 = escalate/clarify; ≥ 0.68 = proceed.** Provisional — must be calibrated against evaluation dataset. | 2026-07-20 |
| UD-03 | Embedding model | **`gemini-embedding-001`, 3072-dimensional output.** Same model, dimensionality, normalisation, and task type (`RETRIEVAL_DOCUMENT` for ingestion, `RETRIEVAL_QUERY` for queries) throughout. | 2026-07-20 |
| UD-04 | Frontend API routing | Direct REST calls from frontend to backend (no BFF proxy for MVP). | 2026-07-20 |
| UD-05 | Knowledge base content | **Original synthetic documentation** created specifically for MechaCode Guardian, stored under `knowledge/synthetic/`. Manufacturer manuals not ingested until redistribution rights verified in writing. | 2026-07-20 |

### 11.3 Remaining Open Decisions

| ID | Decision | Status |
|---|---|---|
| UD-06 | Demo backend hosting (local vs. VPS) | Open — decide by Day 8 |
