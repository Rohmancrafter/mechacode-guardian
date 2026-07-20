# MechaCode Guardian — Synthetic Knowledge Corpus

**Version:** 1.0.0
**Date:** 2026-07-20
**Author:** Muhammad Nur Rohman
**Project:** MechaCode Guardian
**License:** Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
**Provenance:** Original synthetic content — created specifically for the MechaCode Guardian AI project

---

## 1. Purpose

This directory contains the synthetic knowledge corpus that powers the MechaCode Guardian RAG (Retrieval-Augmented Generation) pipeline. The documents were authored from scratch as original training and demonstration material. They are the only content ingested into the `mechacode_guardian_kb` vector database collection for the MVP.

The corpus serves three functions:

1. **RAG knowledge base.** The documents are chunked, embedded, and stored in Astra DB so the AI pipeline can retrieve relevant passages when responding to technician queries.
2. **Evaluation ground truth.** The 30-case evaluation dataset (see `tests/evaluation/`) is derived from specific, identifiable passages in these documents. This ensures that retrieval metrics measure the system's ability to find the right passage rather than general world knowledge.
3. **Demonstration material.** The corpus demonstrates the intended end-to-end workflow — symptom input, evidence retrieval, ranked diagnosis, safety gate, checklist — without requiring any real manufacturer documentation.

---

## 2. Fictional Equipment Scope

All equipment described in this corpus is **entirely fictional**. Equipment names, model numbers, alarm codes, and measured values are invented for training and demonstration purposes only.

| Document ID | Equipment Domain | Fictional Equipment Name |
|---|---|---|
| MGC-SAFETY-001 | General safety procedures | (cross-equipment) |
| MGC-MOTOR-001 | Training motor system | MechaCo MTR-24 (24 V DC training motor unit) |
| MGC-SENSOR-001 | Industrial sensor system | MechaCo SNS-10 (training sensor module) |
| MGC-PLC-001 | PLC and I/O system | MechaCo PLC-200 (training programmable controller) |
| MGC-PNEUMATIC-001 | Pneumatic system | MechaCo PNU-05 (low-pressure training pneumatic unit) |

These names do not refer to any real product by any manufacturer.

---

## 3. Provenance Statement

Every document in this corpus was created as **original synthetic material** under the direction of **Muhammad Nur Rohman** (project creator and maintainer) with writing assistance from **IBM Bob** (IBM's AI coding and writing assistant). Muhammad Nur Rohman is responsible for all design decisions, safety rules, fictional specifications, and editorial review.

Specifically:

- No manufacturer's technical manual, service bulletin, or proprietary documentation was intentionally reproduced, paraphrased, or adapted.
- No copyrighted third-party content was incorporated.
- The corpus uses conventional mechatronics terminology and general engineering principles that are common knowledge in the discipline.
- IBM Bob served as a structured writing and formatting tool; all content direction, safety requirements, and domain decisions were specified by Muhammad Nur Rohman.

Each individual document file contains its own provenance header. The `manifest.json` file in this directory records machine-readable provenance metadata for all documents.

---

## 4. Licensing

This corpus is released under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license. See `LICENSE.md` for the full terms.

Summary:
- **You may** share and adapt this material for non-commercial purposes, provided you give appropriate credit.
- **You may not** use this material for commercial purposes without separate written permission from the author.
- **No warranty** is provided. See Section 6 for the safety notice.

---

## 5. Safety Limitations

**Read this section carefully before using or distributing these documents.**

These documents are **synthetic training and demonstration material only**. They:

- Do **not** represent authoritative technical guidance for any real equipment.
- Do **not** constitute professional engineering, electrical, or safety advice.
- Contain **fictional** measurements, alarm codes, specifications, and procedures that may not reflect real-world equipment behaviour.
- Are **not** a substitute for manufacturer documentation, qualified engineering review, or site-specific safety procedures.

**Performing maintenance or repair work based solely on this corpus — on any real equipment — is dangerous and is explicitly prohibited.**

Any system that uses this corpus as its knowledge base **must** carry a prominent disclaimer to users that outputs are AI-assisted recommendations derived from synthetic training material, and that all actions must be verified by a qualified technician using official manufacturer documentation.

The MechaCode Guardian system enforces this through the safety gate (see `data/safety_triggers.json`) and the mandatory disclaimer appended to every diagnosis response.

---

## 6. Intended Use

| Use | Permitted |
|---|---|
| Training and evaluation of the MechaCode Guardian RAG pipeline | ✅ Yes |
| Competition demonstration (AI Builders Challenge) | ✅ Yes |
| Educational demonstration of AI-assisted fault diagnosis workflows | ✅ Yes (with attribution and the safety disclaimer from Section 5) |
| Non-commercial research and teaching | ✅ Yes (CC BY-NC 4.0) |
| Actual maintenance or repair of real industrial equipment | ❌ **No** |
| Commercial products or services | ❌ No (without written permission) |
| Representing this content as official manufacturer documentation | ❌ **No** |

---

## 7. Prohibition on Treating as Official Documentation

**These documents must never be presented to users, technicians, or any other audience as official manufacturer manuals, service documentation, or authoritative technical references.**

Any deployment of MechaCode Guardian or any derivative system must make clear — in the user interface, in any reports generated, and in any citation display — that the knowledge base contains synthetic training material, not manufacturer-approved documentation.

---

## 8. File Index

| File | Type | Description |
|---|---|---|
| `README.md` | This file | Corpus overview, provenance, licensing, safety limitations |
| `LICENSE.md` | License | CC BY-NC 4.0 full terms and safety notice |
| `manifest.json` | Metadata | Machine-readable document registry for RAG ingestion |
| `MGC-SAFETY-001.md` | Safety | General isolation, lockout/tagout, and escalation rules (cross-equipment) |
| `MGC-MOTOR-001.md` | Technical | Training motor system troubleshooting guide |
| `MGC-SENSOR-001.md` | Technical | Industrial sensor training troubleshooting guide |
| `MGC-PLC-001.md` | Technical | PLC and I/O training system guide |
| `MGC-PNEUMATIC-001.md` | Technical | Low-pressure pneumatic training system guide |

---

## 9. Corpus Design for Evaluation Coverage

This corpus is designed to support a minimum of 30 evaluation cases across the following categories defined in `docs/EVALUATION_PLAN.md`:

| Evaluation Category | Corpus Support |
|---|---|
| A — Standard fault diagnosis (12 cases) | Each technical document contains 4–5 clearly described fault scenarios with unambiguous causes |
| B — Multi-cause ambiguous (6 cases) | MGC-MOTOR-001 §3.3 and MGC-PNEUMATIC-001 §3.3 contain scenarios with two or three plausible causes |
| C — Critical-risk / safety escalation (10 cases) | MGC-SAFETY-001 and escalation sections in each document cover high-voltage, stored pressure, and chemical hazards |
| D — Out-of-scope / no evidence (4 cases) | No document covers hydraulic servo systems, CNC machining centres, or robotic welding — these are out-of-scope by design |
| E — Language switching (8 cases, overlapping) | All documents include Indonesian symptom aliases in symptom tables and a bilingual glossary |

---

*Last updated: 2026-07-20*
*Status: ⚠ UNVERIFIED — Pending developer manual review before ingestion into mechacode_guardian_kb.*
