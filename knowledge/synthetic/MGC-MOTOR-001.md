# MGC-MOTOR-001 — MechaCo MTR-24 Training Motor System Troubleshooting Guide

**Document ID:** MGC-MOTOR-001
**Version:** 1.0.0
**Date:** 2026-07-20
**Author:** Muhammad Nur Rohman
**Project:** MechaCode Guardian
**License:** CC BY-NC 4.0
**Provenance:** Original synthetic content — not a real manufacturer document
**Safety Classification:** Moderate
**Equipment:** MechaCo MTR-24 (fictional 24 V DC training motor unit)
**Language:** English (with Indonesian aliases)
**Status:** ⚠ UNVERIFIED — Pending developer manual review

> **⚠ SYNTHETIC TRAINING DOCUMENT.** The MechaCo MTR-24 is a fictional device. All specifications, alarm codes, and measured values are invented for training purposes only. Do not apply these procedures to real equipment. Always refer to the official manufacturer documentation and consult a qualified technician.

---

## Table of Contents

1. [Equipment Overview](#1-equipment-overview)
2. [Fictional Specifications](#2-fictional-specifications)
3. [Fault Scenarios and Diagnosis](#3-fault-scenarios-and-diagnosis)
   - 3.1 [Failure to Start](#31-failure-to-start-motor-tidak-mau-berputar)
   - 3.2 [Overheating Indication](#32-overheating-indication-indikasi-panas-berlebih)
   - 3.3 [Abnormal Vibration Indication](#33-abnormal-vibration-indication-indikasi-getaran-abnormal)
   - 3.4 [Intermittent Operation](#34-intermittent-operation-operasi-terputus-putus)
   - 3.5 [Overload Indication](#35-overload-indication-indikasi-beban-lebih)
4. [Safe Inspection Checklist](#4-safe-inspection-checklist)
5. [Prohibited Actions](#5-prohibited-actions)
6. [Escalation Conditions](#6-escalation-conditions)
7. [Indonesian Aliases and Bilingual Glossary](#7-indonesian-aliases-and-bilingual-glossary)

---

## 1. Equipment Overview [MGC-MOTOR-001 §1]

The MechaCo MTR-24 is a fictional 24 V DC brushed training motor unit used in educational mechatronics laboratory settings. It consists of a motor body, an integrated thermal protection switch, a brushed commutator, a drive shaft with coupling flange, and a terminal block for power connection. It is controlled by a speed controller module (sold separately).

This troubleshooting guide covers five common fault scenarios encountered in training lab environments. All diagnostic procedures in this document assume the technician has completed the pre-inspection prerequisites in MGC-SAFETY-001 §6.

---

## 2. Fictional Specifications [MGC-MOTOR-001 §2]

> ⚠ These values are fictional training values. They do not represent any real product.

| Parameter | Fictional Training Value |
|---|---|
| Rated voltage | 24 V DC |
| Rated current (full load) | 2.5 A |
| No-load current | 0.4 A |
| Rated speed | 1,800 RPM |
| Thermal protection trip temperature | 85 °C (internal switch, auto-reset) |
| Winding resistance (terminal A to B) | 4.2 Ω ± 0.5 Ω |
| Brush contact resistance | < 0.3 Ω |
| Supply fuse rating | 5 A slow-blow |
| Alarm code — thermal trip | MT-01 |
| Alarm code — overload | MT-02 |
| Alarm code — no supply detected | MT-03 |

---

## 3. Fault Scenarios and Diagnosis [MGC-MOTOR-001 §3]

---

### 3.1 Failure to Start [MGC-MOTOR-001 §3.1]
*Motor tidak mau berputar*

**Symptom:** Motor does not rotate when start command is issued. No audible attempt to start. Controller shows alarm MT-03 (no supply detected) or no alarm at all.

**Indonesian aliases:** Motor tidak berputar, motor diam, tidak ada respon saat start, alarm MT-03.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Supply voltage absent or too low | High | Measure supply voltage at terminal block with motor isolated: expect 22–26 V DC |
| C2 | Blown supply fuse | High | Visually inspect and test 5 A slow-blow fuse |
| C3 | Loose or broken supply wiring | Medium | Inspect terminal block connections for tightness and wire integrity |
| C4 | Faulty speed controller — no output | Medium | Measure controller output terminals with a multimeter |
| C5 | Thermal protection switch open (latched) | Low | Allow motor to cool for 15 minutes, then retry |

**Safe inspection steps for C1–C3** (after isolation per MGC-SAFETY-001 §5.1):

1. Isolate the motor and controller using the main supply isolator. Apply LOTO.
2. After verifying zero energy, measure winding resistance at the terminal block. Expected: 4.2 Ω ± 0.5 Ω. If open circuit (> 1 MΩ), winding is broken — escalate.
3. Re-energise only the supply measurement point (do not reconnect motor). Measure supply voltage. Expected: 22–26 V DC.
4. If supply is absent, check and replace the 5 A fuse. Record fuse rating before replacement.
5. Inspect terminal screws for tightness. Tighten to hand-tight plus one quarter turn only.

**Stop condition:** If measured winding resistance is open circuit or the fuse fails again immediately after replacement — stop and escalate.

---

### 3.2 Overheating Indication [MGC-MOTOR-001 §3.2]
*Indikasi panas berlebih*

**Symptom:** Motor body feels hot to the touch. Controller shows alarm MT-01 (thermal trip). Motor may have stopped automatically.

**Indonesian aliases:** Motor panas berlebih, suhu tinggi, alarm MT-01, motor berhenti karena panas.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Ambient temperature too high or blocked ventilation | High | Check ventilation slots for blockage; measure room temperature |
| C2 | Continuous operation at or above rated current (2.5 A) | High | Review recent duty cycle; check load torque |
| C3 | Excessive brush friction due to worn brushes | Medium | Inspect brush length and contact surface after isolation |
| C4 | Partial winding short increasing current draw | Low | Measure supply current at rated load; expect ≤ 2.5 A |

**Safe inspection steps** (after isolation per MGC-SAFETY-001 §5.1):

1. Allow motor to cool until the body is safe to touch (typically 15 minutes).
2. Verify ventilation slots are clear of dust, debris, or obstructions.
3. Inspect brushes: remove brush caps after isolation. Brush length below 4 mm (fictional threshold) indicates replacement needed.
4. Reconnect and run the motor at no-load. Measure current: expect 0.4 A. If current exceeds 0.8 A at no load, a winding issue is suspected — escalate.

**Stop condition:** If the alarm MT-01 recurs within 5 minutes of restart at no load — stop and escalate.

---

### 3.3 Abnormal Vibration Indication [MGC-MOTOR-001 §3.3]
*Indikasi getaran abnormal*

**Symptom:** Visible or audible vibration that is louder or more pronounced than normal operation. Vibration may be intermittent or continuous.

**Indonesian aliases:** Getaran tidak normal, bunyi kasar, motor bergetar, vibrasi berlebih.

> **Note:** This is a multi-cause scenario. Two or more causes may be present simultaneously.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Loose mounting bolts | High | Visually inspect and attempt to move motor body by hand with machine stopped and isolated |
| C2 | Coupling misalignment | High | Inspect shaft coupling alignment with a straight-edge after isolation |
| C3 | Worn or damaged bearing | Medium | Listen for grinding or knocking sound; bearing noise is typically speed-dependent |
| C4 | Debris on the commutator or unbalanced load | Medium | Inspect commutator for debris after isolation |
| C5 | Shaft bent or eccentric | Low | Mark shaft with a felt-tip pen and rotate by hand after isolation — observe wobble |

**Safe inspection steps** (after isolation per MGC-SAFETY-001 §5.1):

1. Isolate the motor and apply LOTO.
2. Attempt to rock the motor body by hand. Any movement indicates loose mounting — tighten mounting bolts.
3. Inspect the coupling between motor shaft and driven load. A straight-edge held along both shafts should show no visible angular deviation.
4. Rotate the shaft slowly by hand. A grinding or clicking sensation indicates a bearing fault — escalate.
5. Inspect the commutator surface for carbon deposits or debris. Clean with a dry, lint-free cloth only.

**Stop condition:** If grinding is felt in the shaft rotation, or if the shaft wobbles visibly — stop and escalate. Do not run the motor.

---

### 3.4 Intermittent Operation [MGC-MOTOR-001 §3.4]
*Operasi terputus-putus*

**Symptom:** Motor starts and runs normally, then stops unexpectedly before the stop command is issued. May restart on its own or require manual reset.

**Indonesian aliases:** Motor berhenti sendiri, operasi tidak stabil, motor mati mendadak, berhenti tanpa perintah.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Intermittent supply connection (loose terminal or worn cable) | High | Inspect terminal block screws and cable at bend points |
| C2 | Thermal protection cycling (borderline overtemperature) | High | Check if MT-01 alarm is also logged intermittently |
| C3 | Brush arcing due to worn brushes or contaminated commutator | Medium | Inspect brushes and commutator after isolation |
| C4 | Controller output instability | Low | Monitor controller output voltage during operation |

**Safe inspection steps** (after isolation per MGC-SAFETY-001 §5.1):

1. Inspect all terminal screws for tightness. Gently pull each wire by hand to confirm secure seating.
2. Inspect the supply cable for cracks, kinks, or damage near entry points.
3. Inspect brushes for wear (minimum length 4 mm). Inspect commutator for carbon tracking.
4. If the controller is suspected, substitute with a known-good unit and retest.

**Stop condition:** If inspection does not identify a clear cause after steps 1–4 — stop and escalate.

---

### 3.5 Overload Indication [MGC-MOTOR-001 §3.5]
*Indikasi beban lebih*

**Symptom:** Controller shows alarm MT-02 (overload). Motor draws more than 2.5 A at full load speed. Motor body may be warm.

**Indonesian aliases:** Beban lebih, overcurrent, alarm MT-02, arus berlebih.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Mechanical overload — driven load resistance too high | High | Disconnect driven load and run motor at no-load; if current returns to 0.4 A, the load is the cause |
| C2 | Seized bearing — mechanical drag | Medium | Rotate shaft by hand after isolation; should turn freely |
| C3 | Partial winding short — increased current | Low | Measure winding resistance; expect 4.2 Ω ± 0.5 Ω |

**⚠ Escalation required if:**
- Measured current exceeds 4.0 A (160% of rated — fictional threshold) even with no load attached.
- Winding resistance is below 3.0 Ω (indicates a short).
- The shaft cannot be rotated freely by hand.

**Safe inspection steps** (after isolation per MGC-SAFETY-001 §5.1):

1. Disconnect the driven load (coupling or belt) after isolation.
2. Re-energise and run motor at no-load. Measure current. Expect 0.4 A ± 0.1 A.
3. If overload alarm clears and current is normal, the fault is in the driven load — investigate the load mechanism.
4. If overload persists at no-load, measure winding resistance. If out of range — escalate.

---

## 4. Safe Inspection Checklist [MGC-MOTOR-001 §4]

Perform this checklist before any physical inspection of the MTR-24:

- [ ] Equipment isolated using main supply isolator (MGC-SAFETY-001 §5.1)
- [ ] LOTO applied — personal lock and tag in place
- [ ] Zero energy verified with a calibrated multimeter (expect 0 V at motor terminals)
- [ ] Motor body temperature safe to touch (below 40 °C)
- [ ] Relevant fault scenario identified (Section 3.x)
- [ ] No burning smell present (if yes — stop and escalate, see §6)
- [ ] No visible burn marks on terminal block or wiring (if yes — stop and escalate)

---

## 5. Prohibited Actions [MGC-MOTOR-001 §5]

| # | Prohibited Action |
|---|---|
| P-01 | Opening the motor terminal box while the supply is connected |
| P-02 | Running the motor with mounting bolts removed |
| P-03 | Replacing a blown fuse with a higher-rated fuse |
| P-04 | Attempting to re-start if the shaft cannot be rotated freely by hand |
| P-05 | Operating the motor continuously above rated current (2.5 A) |

---

## 6. Escalation Conditions [MGC-MOTOR-001 §6]

Stop all work immediately and contact a qualified technician if:

- Burning smell is present (*bau terbakar*) at any point
- Burn marks are visible on any component
- Winding resistance is open circuit (> 1 MΩ) or below 3.0 Ω
- No-load current exceeds 0.8 A
- The shaft cannot be rotated freely by hand
- Overload alarm (MT-02) recurs immediately at no-load
- Thermal alarm (MT-01) recurs within 5 minutes at no-load
- Any cause cannot be identified after completing the relevant inspection steps

---

## 7. Indonesian Aliases and Bilingual Glossary [MGC-MOTOR-001 §7]

| English | Bahasa Indonesia |
|---|---|
| Motor failure to start | Motor tidak mau berputar / motor diam |
| Overheating | Panas berlebih / suhu tinggi |
| Abnormal vibration | Getaran abnormal / getaran tidak normal |
| Intermittent operation | Operasi terputus-putus / motor berhenti sendiri |
| Overload | Beban lebih / overcurrent |
| Winding resistance | Resistansi lilitan |
| Thermal protection trip | Proteksi termal aktif |
| Brush | Sikat arang |
| Commutator | Komutator |
| Terminal block | Blok terminal |
| Supply fuse | Sekring suplai |
| Rated current | Arus nominal |
| No-load current | Arus tanpa beban |
| Shaft | Poros |
| Mounting bolts | Baut pemasangan |
| Coupling | Kopling |
| Bearing | Bantalan |
