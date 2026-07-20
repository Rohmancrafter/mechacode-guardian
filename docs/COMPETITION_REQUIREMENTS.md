# Competition Requirements — AI Builders Challenge with IBM Bob

**Version:** 0.1
**Date:** 2026-07-20
**Source:** Official AI Builders Challenge rules — July Wildcard Challenge
**Purpose:** Single authoritative reference for all competition constraints, requirements, and submission rules. Cross-referenced by all other planning documents.

---

## Table of Contents

1. [Challenge Identity](#1-challenge-identity)
2. [Eligibility and Submission Rules](#2-eligibility-and-submission-rules)
3. [Required Technologies](#3-required-technologies)
4. [Required Deliverables](#4-required-deliverables)
5. [README Requirements](#5-readme-requirements)
6. [Content and Language Rules](#6-content-and-language-rules)
7. [Judging Criteria](#7-judging-criteria)
8. [Deadlines](#8-deadlines)
9. [Prerequisites — IBM SkillsBuild](#9-prerequisites--ibm-skillsbuild)
10. [Bobcoins Policy](#10-bobcoins-policy)
11. [Submission Checklist](#11-submission-checklist)
12. [Disqualification-Risk Checklist](#12-disqualification-risk-checklist)

---

## 1. Challenge Identity

| Field | Value |
|---|---|
| Challenge name | July Wildcard Challenge |
| Theme | Intelligent Systems for the Future of Work |
| Challenge type | Monthly Wildcard |
| Submission window | July 2026 |
| Organiser | IBM (AI Builders Challenge with IBM Bob) |

---

## 2. Eligibility and Submission Rules

| Rule | Detail |
|---|---|
| Submissions per challenge | **One submission per monthly challenge** — only one project may be submitted for the July Wildcard Challenge. |
| Existing development | **Existing capstone development is permitted** — a project already under active development may be submitted, provided it meets all other requirements. |
| Primary AI development partner | **IBM Bob must be the primary AI development partner** throughout the project. IBM Bob usage must be documented and demonstrable. |
| Supporting technologies | **Gemini and Astra DB are explicitly permitted** as supporting technologies alongside IBM Bob. |
| Team size | Solo developer (this submission). |

---

## 3. Required Technologies

| Technology | Role | Status in MechaCode Guardian |
|---|---|---|
| IBM Bob | Primary AI development partner — architecture, coding, testing, documentation | Primary tool — all usage logged in `docs/IBM_BOB_USAGE.md` |
| Gemini (Google) | Permitted supporting technology | Used as fallback LLM (UD-01 resolved) and as embedding model (`gemini-embedding-001`, UD-03 resolved) |
| Astra DB (DataStax) | Permitted supporting technology | Vector store for knowledge base chunks and diagnosis reports |

> **Note:** IBM Granite via watsonx.ai is the **primary LLM** for all diagnosis and generation tasks. Gemini is used as the fallback LLM and for embeddings only.

---

## 4. Required Deliverables

| Deliverable | Requirement | Status |
|---|---|---|
| GitHub repository | Public repository containing all project code | ⬜ Pending — to be made public before submission |
| Prototype | Working prototype demonstrating the core AI capability | ⬜ Pending — scheduled per DELIVERY_PLAN.md |
| README.md | Must explain problem, AI approach, architecture, theme, IBM Bob usage | ⬜ Pending — scheduled for Day 10 |
| Video | Demo/explanation video; must be in English | ⬜ Pending — scheduled for Day 11 |
| Submission form | Completed submission on the challenge platform | ⬜ Pending — due July 31 |

---

## 5. README Requirements

The `README.md` in the root of the repository **must** cover all five of the following topics:

| # | Required Topic | Notes |
|---|---|---|
| 1 | **Problem statement** | What problem MechaCode Guardian solves; why it matters for Indonesian mechatronics technicians |
| 2 | **AI approach** | How IBM Bob, IBM Granite (watsonx.ai), Gemini embedding, and RAG are used together |
| 3 | **Architecture** | High-level system design; reference to `docs/ARCHITECTURE.md` for detail |
| 4 | **Selected theme** | Explicitly state: "Intelligent Systems for the Future of Work" |
| 5 | **IBM Bob usage** | Summary of how IBM Bob was used; reference to `docs/IBM_BOB_USAGE.md` for full log |

> **Implementation note:** The README must be written in English (see Section 6). A brief Bahasa Indonesia section is acceptable as a secondary addition but must not replace the English content.

---

## 6. Content and Language Rules

| Rule | Detail |
|---|---|
| Video language | **Must be in English** |
| Submission content | **Must be in English** (README, submission form text, video narration) |
| Application language | The *application itself* is bilingual (Indonesian default + English); this does not violate the English submission rule |

---

## 7. Judging Criteria

Projects are evaluated on five dimensions. Relative weighting is not publicly specified; all five must be addressed in the submission.

| Criterion | What Evaluators Look For | How MechaCode Guardian Addresses It |
|---|---|---|
| **Technical Execution** | Quality of implementation; correct use of IBM Bob and permitted technologies; code structure | IBM Granite RAG pipeline; Gemini embedding; Astra DB vector store; FastAPI modular backend; documented in ARCHITECTURE.md |
| **Innovation** | Novel application of AI; creative use of the technology stack | Indonesian-first industrial AI maintenance co-worker; evidence-grounded RAG with safety gate; auditable citation chain |
| **Feasibility** | Is the solution realistic and deployable? Does it run within real constraints? | Runs on i7/16 GB hardware; no local GPU; cloud-hosted AI services; 12-day solo execution plan |
| **Challenge Fit** | Does the project address the theme: "Intelligent Systems for the Future of Work"? | Directly replaces fragmented, error-prone manual maintenance workflows with an AI co-worker for front-line technicians |
| **Real-World Impact** | Does the solution solve a genuine problem for real users? | Addresses technician shortage, safety risk, and knowledge fragmentation in Indonesian manufacturing |

---

## 8. Deadlines

| Deadline | Date and Time | Notes |
|---|---|---|
| **Official competition deadline** | **July 31, 2026 at 11:59 PM ET** | Eastern Daylight Time (UTC-4). This is the hard cutoff on the competition platform. Equivalent to August 1, 2026 at 10:59 AM WIB. |
| **Internal developer deadline** | **July 31, 2026 at 18:00 WIB** | Western Indonesian Time (UTC+7). Provides approximately **17 hours** of buffer before the official ET cutoff. **All work must be complete and submitted by this time.** |
| Bobcoins deadline | Same as competition deadline | 40 Bobcoins available; cannot be extended (see Section 10) |

> **Time conversion:** WIB is UTC+7. ET (Eastern Daylight Time in July) is UTC-4. The offset between WIB and EDT is 11 hours (WIB leads EDT).
> - July 31, 2026 at **18:00 WIB** = July 31, 2026 at **11:00 UTC** = July 31, 2026 at **07:00 EDT**
> - July 31, 2026 at **11:59 PM EDT** = August 1, 2026 at **03:59 UTC** = August 1, 2026 at **10:59 WIB**
>
> The internal deadline of July 31 at 18:00 WIB is therefore **16 hours 59 minutes (≈ 17 hours)** before the official cutoff of August 1 at 10:59 WIB. This buffer is intentional and must be preserved.

---

## 9. Prerequisites — IBM SkillsBuild

| Requirement | Detail |
|---|---|
| IBM SkillsBuild completion certificate | **Required** for submission. The developer must complete the required IBM SkillsBuild course(s) and obtain the completion certificate before submitting. |
| Action required | Verify certificate is obtained and on file before July 31 internal deadline. |

> **Risk:** If the SkillsBuild certificate is not obtained before the submission deadline, the submission will be incomplete. This is a non-technical blocker. Add to Day 1 checklist: verify SkillsBuild status.

---

## 10. Bobcoins Policy

| Rule | Detail |
|---|---|
| Bobcoins available | 40 Bobcoins for this challenge |
| Extension policy | **40 Bobcoins cannot be extended.** No additional Bobcoins will be granted for this challenge period. |
| Implication | Token budget is fixed. All IBM Bob interactions must be efficient. Avoid redundant or exploratory prompts that consume Bobcoins without producing usable output. |

> **Practical guidance:** Use IBM Bob for high-leverage tasks: architecture decisions, code generation, test writing, security review, documentation. Avoid using IBM Bob for tasks that can be done directly (e.g., simple file reads, syntax lookups).

---

## 11. Submission Checklist

Use this checklist immediately before submitting on July 31.

### 11.1 Repository and Code

- [ ] GitHub repository is **public**
- [ ] `README.md` covers all 5 required topics (problem, AI approach, architecture, theme, IBM Bob usage)
- [ ] `README.md` is written in **English**
- [ ] No secrets, API keys, or tokens present in any committed file
- [ ] `.env.example` is present with all required variable names (no real values)
- [ ] `.gitignore` correctly excludes `.env`, `.venv/`, `node_modules/`, `dist/`
- [ ] `docs/IBM_BOB_USAGE.md` is up to date with all substantive IBM Bob sessions
- [ ] `docs/COMPETITION_REQUIREMENTS.md` is accurate and up to date

### 11.2 Prototype

- [ ] Backend starts successfully: `uvicorn backend.main:app`
- [ ] Frontend starts successfully: `npm run dev`
- [ ] Full diagnosis workflow completes end-to-end (symptom → causes → checklist → report)
- [ ] Escalation notice appears for hazardous scenarios
- [ ] SR-06 refusal appears for out-of-scope queries
- [ ] Fallback LLM activates when primary provider is disabled
- [ ] Diagnosis report downloads as Markdown with all required fields

### 11.3 Evaluation Results

- [ ] CST-01: Safety Escalation Recall = 10/10 (100%) — **BLOCKER if not met**
- [ ] CST-02: SR-06 Refusal Accuracy = 4/4 (100%) — **BLOCKER if not met**
- [ ] Recall@5 ≥ 0.80
- [ ] Zero hallucinated citations
- [ ] P95 latency ≤ 8 seconds
- [ ] Evaluation results file committed at `tests/evaluation/results/eval_run_final.json`

### 11.4 Prerequisites

- [ ] IBM SkillsBuild completion certificate obtained and on file
- [ ] Submission form on competition platform fully completed
- [ ] Submission submitted **before 18:00 WIB** (internal deadline)

### 11.5 Video

- [ ] Demo video recorded
- [ ] Video narration and any on-screen text are in **English**
- [ ] Video demonstrates: symptom input → diagnosis → escalation → checklist → report download
- [ ] Video is uploaded and link included in submission form

---

## 12. Disqualification-Risk Checklist

The following conditions represent known disqualification or rejection risks. Each must be verified before submission.

| Risk | Check | Mitigation |
|---|---|---|
| **Secrets in repository** | Run `git log --all --full-history -- "*.env"` and `git grep -r "API_KEY\|sk-\|Bearer" .` | Ensure `.env` was never committed; rotate any keys that were |
| **IBM Bob not used as primary AI partner** | Verify `docs/IBM_BOB_USAGE.md` has substantive entries for coding, not just planning | Use IBM Bob for at minimum 3 coding sessions |
| **More than one submission** | Confirm this is the only submission to the July challenge | Only submit once |
| **README missing required topics** | Cross-check README against Section 5 of this document | All 5 topics must be explicitly present |
| **Video not in English** | Watch final video before uploading | Re-record if narration is in Indonesian |
| **SkillsBuild certificate missing** | Locate certificate in IBM SkillsBuild account | Complete course immediately if not done |
| **Submission after ET deadline** | Submit by 18:00 WIB (internal deadline) | Do not rely on the ET cutoff as a safety margin |
| **Prototype does not run from README instructions** | Follow README setup steps on a clean environment | Test setup instructions before final submission |
| **Manufacturer manuals ingested without rights** | Verify knowledge base contains only `knowledge/synthetic/` content for MVP | Do not ingest any manufacturer PDF unless redistribution rights confirmed in writing |
