# MGC-SAFETY-001 — General Safety and Isolation Procedures

**Document ID:** MGC-SAFETY-001
**Version:** 1.0.0
**Date:** 2026-07-20
**Author:** Muhammad Nur Rohman
**Project:** MechaCode Guardian
**License:** CC BY-NC 4.0
**Provenance:** Original synthetic content — not a real manufacturer document
**Safety Classification:** Critical
**Language:** English (with Indonesian aliases)
**Status:** ⚠ UNVERIFIED — Pending developer manual review

> **⚠ SYNTHETIC TRAINING DOCUMENT.** This document was created for the MechaCode Guardian AI training corpus. It does not represent official safety guidance for any real equipment or installation. All procedures must be verified by a qualified technician using the official documentation for the specific equipment in use.

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Definitions](#2-definitions)
3. [Fundamental Safety Rules](#3-fundamental-safety-rules)
4. [Hazard Recognition](#4-hazard-recognition)
5. [Isolation and Lockout/Tagout (LOTO)](#5-isolation-and-lockouttagout-loto)
6. [Pre-Inspection Prerequisites](#6-pre-inspection-prerequisites)
7. [Prohibited Actions](#7-prohibited-actions)
8. [Technician Escalation Rules](#8-technician-escalation-rules)
9. [Indonesian Aliases and Bilingual Glossary](#9-indonesian-aliases-and-bilingual-glossary)

---

## 1. Purpose and Scope [MGC-SAFETY-001 §1]

This document defines the general safety procedures that apply to all equipment covered by the MechaCode Guardian training corpus. It is the highest-priority document in the knowledge base. Any diagnosis session that matches a hazard condition described in this document must be escalated to a qualified technician immediately, regardless of confidence level.

**Scope:** All equipment within the MechaCode Guardian training corpus: motor systems (MGC-MOTOR-001), sensor systems (MGC-SENSOR-001), PLC systems (MGC-PLC-001), and pneumatic systems (MGC-PNEUMATIC-001).

---

## 2. Definitions [MGC-SAFETY-001 §2]

| Term | Indonesian | Definition |
|---|---|---|
| Isolation | Isolasi | Disconnecting all energy sources from equipment before accessing internal components |
| Lockout/Tagout (LOTO) | Kunci/Tanda Pengaman (LOTO) | A procedure for securing energy isolation devices with a physical lock and warning tag |
| Stored energy | Energi tersimpan | Residual energy remaining in a system after isolation (e.g., capacitors, compressed air, springs) |
| Qualified technician | Teknisi berkualifikasi | A person trained, tested, and authorised to perform specific maintenance tasks on specific equipment |
| Safe state | Kondisi aman | Equipment is de-energised, isolated, and verified as safe to approach |
| Hazardous condition | Kondisi berbahaya | Any situation with potential for electrical, mechanical, chemical, or thermal injury |

---

## 3. Fundamental Safety Rules [MGC-SAFETY-001 §3]

The following rules are absolute. No diagnosis recommendation overrides them.

**Rule 1 — Never work on energised equipment** unless you hold a written work permit for live work and a qualified technician is present.

*Indonesian alias: Jangan bekerja pada peralatan yang masih aktif/bertenaga.*

**Rule 2 — Always isolate and verify before touching** internal components. Use a calibrated voltage tester or a current clamp to confirm zero energy after isolation.

*Indonesian alias: Selalu isolasi dan verifikasi sebelum menyentuh komponen internal.*

**Rule 3 — Treat stored energy as live energy.** Capacitors, compressed air, charged springs, and elevated loads remain dangerous after power is disconnected.

*Indonesian alias: Perlakukan energi tersimpan seperti energi aktif.*

**Rule 4 — One person, one lock.** In a multi-person LOTO, each person applies their own lock. A supervisor cannot remove another person's lock.

**Rule 5 — When in doubt, stop and escalate.** If any symptom, measurement, or observation is unexpected, stop work and contact a qualified technician before proceeding.

*Indonesian alias: Jika ragu, hentikan pekerjaan dan hubungi teknisi berkualifikasi.*

---

## 4. Hazard Recognition [MGC-SAFETY-001 §4]

### 4.1 Electrical Hazards [MGC-SAFETY-001 §4.1]

**Stop immediately and escalate** if any of the following are observed:

- Visible burn marks, discolouration, or melted insulation on wiring or components
- Burning smell (*bau terbakar*) from any electrical component
- Sparks or arcing during or after power-on
- Tripped circuit breaker that resets and immediately trips again
- Any symptom involving voltages above 50 V AC or 75 V DC
- Phase imbalance or missing phase on three-phase systems
- Any suspected arc flash condition (*loncatan busur api*)

**Do not open** electrical enclosures, touch terminals, or perform any wiring checks until the system is fully isolated and verified as de-energised.

### 4.2 Mechanical Hazards [MGC-SAFETY-001 §4.2]

**Stop immediately and escalate** if:

- A moving part cannot be stopped by normal control means
- Abnormal vibration (*getaran abnormal*) is severe enough to cause loose fasteners or structural movement
- Rotating components show visible wobble or eccentricity
- Any guard, cover, or interlock has been defeated or is missing

### 4.3 Pneumatic Hazards [MGC-SAFETY-001 §4.3]

**Stop immediately and escalate** if:

- A pressure vessel or line is leaking (*kebocoran tekanan*)
- System pressure exceeds the rated maximum (see equipment-specific document)
- A pressurised component must be physically accessed (requires full depressurisation first)
- An actuator moves unexpectedly when the control system is in a stopped state

### 4.4 Chemical and Environmental Hazards [MGC-SAFETY-001 §4.4]

**Stop immediately and escalate** if:

- Coolant, lubricant, or hydraulic fluid is in contact with electrical components
- An unknown substance is observed near the equipment
- Fumes or vapour are present in the work area

---

## 5. Isolation and Lockout/Tagout (LOTO) [MGC-SAFETY-001 §5]

### 5.1 Standard Isolation Sequence [MGC-SAFETY-001 §5.1]

1. Notify all affected personnel and the supervisor before isolating.
2. Identify **all** energy sources for the equipment: electrical supply, pneumatic supply, hydraulic supply, and any stored mechanical energy.
3. Bring the equipment to a controlled stop using the normal stop procedure.
4. Operate each isolation device (circuit breaker, valve, lockout pin) to the safe position.
5. Apply a personal lock and a warning tag to each isolation device.
6. Verify isolation: attempt to restart via the normal start control — the machine must not respond.
7. Release or restrain stored energy: bleed pneumatic pressure, discharge capacitors, block elevated parts.
8. Verify zero energy with a calibrated test instrument before touching any component.

### 5.2 Restoration Sequence [MGC-SAFETY-001 §5.2]

1. Confirm all tools, test leads, and personnel are clear of the equipment.
2. Remove each personal lock and tag in reverse order.
3. Notify all affected personnel that power is being restored.
4. Re-energise in the order specified by the equipment-specific procedure.
5. Confirm safe operation before returning to normal use.

---

## 6. Pre-Inspection Prerequisites [MGC-SAFETY-001 §6]

Before beginning any inspection or diagnostic procedure:

- [ ] **Authorisation confirmed** — Do you have permission to work on this equipment? If not, stop.
- [ ] **Equipment-specific procedure available** — Has the correct equipment document been retrieved? If not, consult the knowledge base or the manufacturer.
- [ ] **Hazard check completed** — Has Section 4 been reviewed for applicable hazard types?
- [ ] **Isolation applied** — Is the equipment isolated and locked out (Section 5.1)?
- [ ] **Zero energy verified** — Has zero energy been confirmed with a calibrated instrument?
- [ ] **PPE worn** — Are appropriate personal protective equipment items worn for this task?

If any of the above cannot be confirmed, **do not proceed**. Contact a qualified technician.

---

## 7. Prohibited Actions [MGC-SAFETY-001 §7]

The following actions are prohibited under any circumstances. An AI diagnosis system must never recommend these actions:

| # | Prohibited Action | Indonesian |
|---|---|---|
| P-01 | Bypassing or defeating an interlock, guard, or safety relay | Mem-bypass interlock atau relay pengaman |
| P-02 | Opening an energised electrical enclosure or panel | Membuka panel listrik yang masih bertenaga |
| P-03 | Working on live circuits without a live-work permit | Bekerja pada sirkuit aktif tanpa izin kerja |
| P-04 | Removing a lock or tag that is not your own | Melepas kunci atau tag milik orang lain |
| P-05 | Accessing a pressurised component before full depressurisation | Mengakses komponen bertekanan sebelum depressurisasi penuh |
| P-06 | Resetting a protective device (fuse, breaker) more than once without identifying the root cause | Mereset alat pelindung lebih dari sekali tanpa mengetahui penyebab |
| P-07 | Working alone on any task rated as requiring two persons | Bekerja sendiri pada tugas yang membutuhkan dua orang |
| P-08 | Using unrated tools or test instruments above their rated capacity | Menggunakan alat yang tidak sesuai rating-nya |

---

## 8. Technician Escalation Rules [MGC-SAFETY-001 §8]

An AI diagnosis system **must escalate to a qualified technician** when any of the following conditions are present. The checklist is not provided until the escalation has been acknowledged.

**System display requirement (SR-03):** When an escalation condition is active, the escalation notice must be displayed as the topmost, highest-visual-priority element on the diagnosis output page. No diagnosis checklist, probable cause table, or further instruction may appear below an active escalation notice until the notice is explicitly acknowledged by a qualified technician. This rule is absolute and not overridable by confidence score or retrieval result.

| Escalation Trigger | Indonesian Alias | Reason |
|---|---|---|
| Any symptom in Section 4.1 (electrical hazard) | Bahaya listrik / tegangan tinggi | Electrical injury risk |
| Any symptom in Section 4.3 (pneumatic hazard) | Bahaya tekanan / kebocoran tekanan | Stored energy injury risk |
| Burning smell from any component | Bau terbakar | Fire and electrical failure risk |
| Breaker tripping repeatedly | Pemutus sirkuit terus trip | Indicates overload or short circuit |
| Phase imbalance or missing phase | Ketidakseimbangan fasa / fasa hilang | Motor and equipment damage risk |
| Liquid near electrical components | Cairan dekat komponen listrik | Electrocution and short-circuit risk |
| Diagnosis confidence is Low (retrieval score < 0.55) | Keyakinan diagnosis rendah | Insufficient evidence — human judgment required |
| Symptom not found in knowledge base | Gejala tidak ditemukan dalam basis data | No grounded diagnosis possible |

---

## 9. Indonesian Aliases and Bilingual Glossary [MGC-SAFETY-001 §9]

| English Term | Bahasa Indonesia |
|---|---|
| Electrical hazard | Bahaya listrik |
| High voltage | Tegangan tinggi |
| Arc flash | Loncatan busur api |
| Lockout/Tagout | Kunci/Tanda pengaman (LOTO) |
| Stored energy | Energi tersimpan |
| Isolation | Isolasi |
| Qualified technician | Teknisi berkualifikasi |
| Safety gate / escalation | Eskalasi keselamatan |
| Pressurised line | Saluran bertekanan |
| Depress / bleed pressure | Depressurisasi / lepas tekanan |
| Burning smell | Bau terbakar |
| Phase imbalance | Ketidakseimbangan fasa |
| Breaker tripped | Pemutus sirkuit trip |
| Live circuit | Sirkuit aktif / bertenaga |
| Interlock | Interlock / kunci pengaman |
| Safe state | Kondisi aman |
| Hazardous condition | Kondisi berbahaya |
