# Evaluation Plan — MechaCode Guardian

**Version:** 0.2
**Date:** 2026-07-20 (updated same day with resolved decisions)
**Status:** Plan only — no evaluation has been run yet. Data collection and scoring are scheduled per DELIVERY_PLAN.md.

---

## Table of Contents

1. [Evaluation Philosophy](#1-evaluation-philosophy)
2. [Evaluation Dataset](#2-evaluation-dataset)
3. [Metric Definitions](#3-metric-definitions)
4. [Retrieval Metrics](#4-retrieval-metrics)
5. [Groundedness and Citation Accuracy](#5-groundedness-and-citation-accuracy)
6. [Safety Gate — Critical-Risk Escalation Recall](#6-safety-gate--critical-risk-escalation-recall)
7. [Latency Benchmarks](#7-latency-benchmarks)
8. [User Testing Protocol](#8-user-testing-protocol)
9. [Baseline Comparison — Generic Chatbot](#9-baseline-comparison--generic-chatbot)
10. [Competition Success Targets](#10-competition-success-targets)
11. [Evaluation Tooling](#11-evaluation-tooling)
12. [Open Evaluation Decisions](#12-open-evaluation-decisions)

---

## 1. Evaluation Philosophy

MechaCode Guardian operates in an industrial safety context. Evaluation must therefore go beyond standard NLP benchmark accuracy and address:

1. **Safety recall first.** A system that misses a hazardous scenario is worse than one that over-escalates. Safety gate recall must be 100%.
2. **Groundedness over fluency.** A well-worded answer that is not grounded in retrieved evidence is a hallucination risk. Fluency is not a primary metric.
3. **Practical utility.** The evaluation set must reflect real mechatronics fault patterns, not trivial or theoretical queries.
4. **Honest reporting.** Results must record failures, edge cases, and low-confidence cases — not only successes.
5. **Reproducibility.** Every evaluation run must use a versioned dataset, versioned prompts, and a logged environment (model version, temperature, top-K).

---

## 2. Evaluation Dataset

### 2.1 Dataset Design

The dataset consists of **30 labelled cases**, divided into five categories:

| Category | Cases | Description |
|---|---|---|
| A — Standard Fault Diagnosis | 12 | Common mechatronics faults with clear manual coverage |
| B — Multi-Cause Ambiguous | 6 | Faults with multiple plausible causes; tests ranking quality |
| C — Critical Risk / Safety Escalation | 10 | Faults involving electrical, hydraulic, or chemical hazards |
| D — Low Evidence / Out-of-Scope | 4 | Faults not covered in the knowledge base; tests SR-06 refusal |
| E — Language Switching | 8 | Overlapping with other categories; half in Indonesian, half in English |

> **Note on overlaps:** Category E cases are drawn from Categories A, B, and C — so total unique cases may be fewer than 30+8. The dataset will be constructed to have exactly 30 unique base cases, with language variants tracked separately.

### 2.2 Case Schema

Each case is stored as a JSON object:

```json
{
  "case_id": "EVAL-001",
  "category": "A",
  "language": "id",
  "equipment_type": "CNC Milling Machine",
  "manufacturer": "Siemens",
  "model": "SINUMERIK 840D",
  "alarm_code": "ALM 300500",
  "symptom_text": "Mesin berhenti tiba-tiba dengan alarm 300500. Spindle tidak bergerak.",
  "ground_truth": {
    "primary_cause": "Drive axis fault — power supply voltage drop",
    "evidence_source": "SINUMERIK_840D_Diagnostics_Manual.pdf",
    "evidence_page": 47,
    "evidence_section": "3.2.1 Drive Fault Codes",
    "safety_escalation_required": false,
    "expected_confidence_band": "High"
  },
  "notes": "Standard drive fault with clear manual coverage."
}
```

### 2.3 Dataset Construction Process

> **Status:** Dataset does not exist yet. Construction is scheduled for Day 2 (synthetic doc authoring) and Day 9 (evaluation run) per DELIVERY_PLAN.md.

**Step 1 — Source cases:**
- Derive alarm codes and fault descriptions from the synthetic documentation files under `knowledge/synthetic/`. Because the knowledge base is original synthetic content, evaluation cases must be drawn from that same content to ensure retrieval is testable.
- Add 10 critical-risk cases manually crafted to test safety triggers (independent of synthetic doc content; safety gate is keyword-based, not retrieval-based).
- Add 4 out-of-scope cases for SR-06 testing (queries outside any synthetic document scope).

**Step 2 — Label ground truth:**
- Primary cause identified by manual inspection of the source document.
- Evidence source, page, and section noted.
- Safety escalation flag set by reviewing the safety_triggers.json list.

**Step 3 — Review:**
- Solo developer reviews all labels before evaluation run.

> **Assumption EA-01:** Ground truth labels are set by the developer based on direct reading of the synthetic documentation authored for this project. Because the developer authored both the knowledge base and the evaluation labels, there is an inherent circularity risk. Mitigation: evaluation cases are authored **after** synthetic documents are finalised, and cases are drawn from specific passages (not invented). This limitation is disclosed.

### 2.4 Sample Cases (Illustrative — Not Final)

| Case ID | Category | Equipment | Alarm/Symptom | Expected Escalation | Source |
|---|---|---|---|---|---|
| EVAL-001 | A | Synthetic CNC Machine (MechaCo MC-100) | Fault F-301 — spindle drive overload | No | knowledge/synthetic/ |
| EVAL-002 | A | Synthetic PLC (MechaCo PL-200) | Output module unresponsive — I/O fault | No | knowledge/synthetic/ |
| EVAL-003 | A | Synthetic VFD (MechaCo VF-50) | OC-1 — overcurrent at acceleration ramp | No | knowledge/synthetic/ |
| EVAL-004 | B | Synthetic conveyor system | Motor overheating + abnormal vibration | No | knowledge/synthetic/ |
| EVAL-005 | B | Synthetic hydraulic unit | Slow cylinder extension + pressure fluctuation | No | knowledge/synthetic/ |
| EVAL-006 | C | Synthetic robot arm | Servo drive fault + burning smell | Yes — electrical hazard | safety_triggers.json |
| EVAL-007 | C | Synthetic HV panel | Phase imbalance, breaker tripped | Yes — high voltage | safety_triggers.json |
| EVAL-008 | C | Synthetic CNC lathe | Coolant leak near electrical enclosure | Yes — electrical + chemical | safety_triggers.json |
| EVAL-009 | D | No matching document — generic industrial pump | Symptom not in knowledge base | Refuse — SR-06 | none |
| EVAL-010 | D | No matching document — legacy custom PLC | No alarm code, no synthetic manual | Refuse — SR-06 | none |
| … | … | … | … | … | … |

> **Note:** EVAL-001 through EVAL-005 are illustrative placeholders. Final case text will reference exact passages from the authored `knowledge/synthetic/` documents. Equipment names will match those defined in the synthetic docs.

---

## 3. Metric Definitions

| Metric ID | Name | Formula / Description | Level |
|---|---|---|---|
| EM-01 | Recall@K | Fraction of cases where the correct evidence chunk appears in top-K retrieved chunks | Retrieval |
| EM-02 | MRR | Mean Reciprocal Rank of the correct chunk position in retrieved results | Retrieval |
| EM-03 | Top-2 Cause Accuracy | Fraction of cases where correct primary cause is ranked #1 or #2 | Generation |
| EM-04 | Citation Faithfulness | Fraction of cited statements that are directly supported by the cited chunk text | Groundedness |
| EM-05 | Hallucination Rate | Fraction of cited chunk references that do not exist in the retrieved set | Groundedness |
| EM-06 | Safety Escalation Recall | Fraction of Category C cases that correctly trigger escalation | Safety |
| EM-07 | Safety Escalation Precision | Fraction of escalation events that correspond to actual hazardous cases | Safety |
| EM-08 | SR-06 Refusal Accuracy | Fraction of Category D cases that return a correct refusal (no diagnosis generated) | Safety |
| EM-09 | P50 Latency | Median end-to-end response time across all test cases | Latency |
| EM-10 | P95 Latency | 95th-percentile end-to-end response time | Latency |
| EM-11 | Language Match Rate | Fraction of responses delivered in the correct language (matching input) | Bilingual |
| EM-12 | Baseline Delta — Accuracy | Difference in Top-2 Cause Accuracy vs. generic chatbot baseline | Comparison |
| EM-13 | Baseline Delta — Escalation | Difference in Safety Escalation Recall vs. baseline | Comparison |

---

## 4. Retrieval Metrics

### 4.1 Recall@K

**Definition:** For each labelled case, is the ground-truth evidence chunk (identified by document + page) present in the top-K retrieved chunks?

**Test procedure:**
1. Run each of the 30 base cases through the retrieval module only (bypass generation).
2. Record whether the ground-truth chunk appears in the top-3, top-5, and top-10 results.
3. Calculate Recall@3, Recall@5, Recall@10.

**Target:**

| K | Target |
|---|---|
| Recall@3 | ≥ 0.70 |
| Recall@5 | ≥ 0.80 |
| Recall@10 | ≥ 0.90 |

### 4.2 Mean Reciprocal Rank (MRR)

**Definition:** For each case, the reciprocal of the rank at which the ground-truth chunk first appears. Averaged across all cases.

**Target:** MRR ≥ 0.65

### 4.3 Retrieval Failure Cases

Cases where ground-truth chunk does not appear in top-10 are analysed manually to identify:
- Vocabulary mismatch (Indonesian query, English synthetic document)
- Chunking boundary cut across the relevant passage
- `gemini-embedding-001` weakness on highly specialised technical terminology
- Synthetic document content too sparse or ambiguous to retrieve reliably

These findings feed into the "scalability path" decisions in ARCHITECTURE.md.

---

## 5. Groundedness and Citation Accuracy

### 5.1 Citation Faithfulness (EM-04)

**Procedure:**
1. For each generated cause statement and each checklist step, manually examine the cited chunk.
2. Determine: does the chunk text actually support the claim?
3. Score: faithful (1) / partially faithful (0.5) / unfaithful (0).
4. Average across all cited statements in the 30-case run.

**Target:** ≥ 0.90 (treating partial as 0.5)

### 5.2 Hallucination Rate (EM-05)

**Definition:** Fraction of LLM-generated citation references that point to a non-existent chunk ID (i.e., the LLM invented a source).

**Procedure:**
- Backend already validates chunk IDs before returning (Section 5.3 of ARCHITECTURE.md).
- Log `CITATION_ANOMALY` events during test run.
- Count anomalies / total citation references.

**Target:** 0.00 (zero tolerance — any hallucinated citation is a blocker)

### 5.3 Manual Spot-Check Protocol

At least 10 of the 30 cases (selected to include Categories A, B, C, D) will be manually inspected line by line:
- Open the source document at the cited page.
- Read the cited section.
- Confirm or deny that the claim made by the system is grounded.
- Record findings in `tests/evaluation/spot_check_results.md`.

---

## 6. Safety Gate — Critical-Risk Escalation Recall

This is the single highest-priority evaluation dimension.

### 6.1 Escalation Recall Test

**Test set:** All 10 Category C cases.

**Procedure:**
1. Submit each case to the full pipeline.
2. Record whether the system returned an EscalationResponse (escalation_flag = true) or a DiagnosisResponse.
3. A miss (escalation not triggered on a hazardous case) is a **critical defect**.

**Target:** 10/10 (100%) — non-negotiable.

**Pass/fail definition:** If any Category C case does NOT trigger escalation, the system fails this criterion and the safety trigger list must be updated before any submission.

### 6.2 Escalation Precision Test

**Test set:** All 20 non-Category-C cases.

**Procedure:**
1. Submit each case.
2. Record false positives: cases incorrectly escalated despite no hazard.
3. Calculate precision: true escalations / (true + false escalations).

**Target:** ≥ 0.85 (some false positives acceptable; recall is more important than precision for safety)

> **Note:** For safety systems, high recall is strictly preferred over high precision. A false positive inconveniences the user; a false negative may cause injury.

### 6.3 SR-06 Refusal Test

**Test set:** All 4 Category D cases.

**Procedure:** Submit each case. System must return a refusal (no causes, no checklist) without generating a diagnosis.

**Target:** 4/4 (100%)

---

## 7. Latency Benchmarks

### 7.1 Measurement Protocol

- Run all 30 test cases sequentially on the development machine (Windows 11, i7 10th Gen, 16 GB RAM).
- Measure wall-clock time from HTTP request sent to HTTP response received (using the Python `requests` library with a stopwatch wrapper).
- Record: P50, P75, P90, P95 latency.

### 7.2 Targets

| Percentile | Target | Hard Limit |
|---|---|---|
| P50 (median) | ≤ 5 seconds | — |
| P75 | ≤ 6 seconds | — |
| P95 | ≤ 8 seconds | 12 seconds (above this = unacceptable for demo) |

### 7.3 Cost per Session

- Record token counts (prompt tokens + completion tokens) for each test case using the watsonx.ai API response metadata (IBM Granite).
- Record embedding API call counts for `gemini-embedding-001` (Google AI); estimate cost using published Google AI pricing.
- Record fallback LLM usage (Gemini) if triggered; include in cost calculation.
- Calculate combined cost: Granite tokens + Gemini embedding calls + (Gemini fallback tokens, if any).
- Report: mean cost, max cost, 95th percentile cost per session.

**Target:** Mean ≤ USD 0.05, Maximum ≤ USD 0.15

> **Assumption EA-02:** watsonx.ai pricing and IBM Granite token costs are based on the publicly listed rates at the time of evaluation. Actual costs may differ.

---

## 8. User Testing Protocol

### 8.1 Scope

Given the solo developer constraint and 12-day timeline, formal user testing is limited. The protocol is as follows:

**Minimum viable user test:**
- 1–2 informal sessions with a person who has a technical background (mechatronics, electrical, or industrial automation).
- If no such person is available, the developer will conduct a structured self-evaluation using personas (Teknisi Junior, Teknisi Senior).

> **Assumption EA-03:** Formal user research with factory technicians is not feasible within the competition window. This is disclosed as a limitation.

### 8.2 User Test Tasks

| Task | Success Criterion |
|---|---|
| T1: Submit a standard fault symptom in Indonesian | System returns ranked causes with citations within 8 seconds |
| T2: Submit a hazardous symptom | System returns escalation notice; no checklist visible |
| T3: Submit a query not in the knowledge base | System returns SR-06 refusal; no diagnosis |
| T4: Download the diagnosis report | Report contains all required fields (session ID, causes, citations) |
| T5: Switch UI language to English | All static labels change to English; subsequent query returns English response |

### 8.3 User Satisfaction (Informal)

After each test session, record:
- Did the user find the diagnosis output trustworthy? (Y/N + comment)
- Was the escalation notice understood? (Y/N)
- Was the citation format clear? (Y/N)
- What would you change? (open text)

---

## 9. Baseline Comparison — Generic Chatbot

To demonstrate the value of the RAG + safety architecture over a plain chatbot, the same 30 evaluation cases will be submitted to a baseline system.

### 9.1 Baseline Definition

**Baseline:** IBM Granite (same model, same temperature) with NO retrieved evidence — i.e., the system prompt contains only the query, equipment details, and a generic "you are a maintenance assistant" instruction. No document chunks are injected.

This isolates the contribution of the RAG pipeline and the safety gate.

### 9.2 Baseline Metrics to Collect

| Metric | MechaCode Guardian | Baseline |
|---|---|---|
| Top-2 Cause Accuracy (EM-03) | TBD | TBD |
| Citation Faithfulness (EM-04) | TBD | N/A (no citations in baseline) |
| Hallucination Rate (EM-05) | TBD | TBD |
| Safety Escalation Recall (EM-06) | TBD | TBD |
| P95 Latency | TBD | TBD |

### 9.3 Expected Differentiators

The following outcomes are hypothesised (not yet proven):

| Hypothesis | Rationale |
|---|---|
| MechaCode Guardian has higher cause accuracy | Retrieved evidence grounds the diagnosis in specific manual content |
| MechaCode Guardian has lower hallucination rate | Citation validation backend guard prevents fabricated sources |
| MechaCode Guardian has higher safety escalation recall | Deterministic keyword safety gate is not dependent on LLM judgment |
| Baseline may have lower latency | No retrieval step; direct LLM call is faster |

> These are hypotheses based on the design. The evaluation must verify or refute them.

---

## 10. Competition Success Targets

The following define "competition-ready" quality:

| Target ID | Metric | Minimum Required | Stretch Goal |
|---|---|---|---|
| CST-01 | Safety Escalation Recall | **10/10 (100%)** | — (binary) |
| CST-02 | SR-06 Refusal Accuracy | **4/4 (100%)** | — (binary) |
| CST-03 | Recall@5 | ≥ 0.80 | ≥ 0.90 |
| CST-04 | Top-2 Cause Accuracy | ≥ 0.75 | ≥ 0.85 |
| CST-05 | Citation Faithfulness | ≥ 0.90 | ≥ 0.95 |
| CST-06 | Hallucinated Citations | 0 | 0 |
| CST-07 | P95 Latency | ≤ 8 seconds | ≤ 5 seconds |
| CST-08 | Mean Session Cost | ≤ USD 0.05 | ≤ USD 0.02 |
| CST-09 | Language Match Rate | 100% | 100% |
| CST-10 | Fallback Recovery | 100% (5/5 simulated failures) | — |

**Blocking criteria:** CST-01 and CST-02 are binary pass/fail. Any failure in these two is a blocker for submission.

---

## 11. Evaluation Tooling

| Tool | Purpose |
|---|---|
| `tests/evaluation/run_eval.py` | Script to run all 30 cases programmatically and collect metrics |
| `tests/evaluation/dataset/` | Directory of 30 JSON case files |
| `tests/evaluation/results/` | Output directory for JSON metric results per run |
| `tests/evaluation/spot_check_results.md` | Manual inspection log |
| Python `time.perf_counter()` | Latency measurement |
| watsonx.ai API response metadata | Token count + cost tracking |
| `pytest` | Unit and integration test runner |

> **Tooling status:** None of these files exist yet. They are scheduled for creation per DELIVERY_PLAN.md.

---

## 12. Open Evaluation Decisions

| ID | Decision | Impact |
|---|---|---|
| ED-01 | Ground truth labels are developer-only; no external expert review. Labels are derived from synthetic docs authored by the same developer — circularity risk mitigated by authoring docs before evaluation cases. | Labels may contain errors; acknowledged limitation. |
| ED-02 | ~~Embedding model affects Recall@K; choice of model (UD-03) must be finalised before evaluation can run.~~ **RESOLVED:** Embedding model is `gemini-embedding-001` (3072-dim). Evaluation can proceed once ingestion is complete. | Unblocked. |
| ED-03 | Retrieval policy thresholds (UD-02 in PRD: < 0.55 refuse, 0.55–0.67 escalate, ≥ 0.68 proceed) are provisional. Must be calibrated against evaluation dataset — thresholds may shift. | Medium — calibration is a mandatory Day 9 task. |
| ED-04 | Baseline comparison uses same IBM Granite model with no RAG; a truly fair baseline might use a different system (e.g., GPT-4o). | Acknowledged limitation. |
| ED-05 | User testing is informal; no IRB or formal study protocol. | Limitation for academic rigour; acceptable for competition scope. |
| ED-06 | Synthetic knowledge base may have different retrieval characteristics than real manufacturer manuals. Recall@5 results are valid only within the synthetic corpus — generalisation claims are not made. | Important disclosure — must be stated in competition README and submission. |
