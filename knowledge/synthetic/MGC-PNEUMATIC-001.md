# MGC-PNEUMATIC-001 — MechaCo PNU-05 Low-Pressure Pneumatic Training System Troubleshooting Guide

**Document ID:** MGC-PNEUMATIC-001
**Version:** 1.0.0
**Date:** 2026-07-20
**Author:** Muhammad Nur Rohman
**Project:** MechaCode Guardian
**License:** CC BY-NC 4.0
**Provenance:** Original synthetic content — not a real manufacturer document
**Safety Classification:** High (stored pressure energy requires mandatory depressurisation before component access)
**Equipment:** MechaCo PNU-05 (fictional low-pressure pneumatic training system)
**Language:** English (with Indonesian aliases)
**Status:** ⚠ UNVERIFIED — Pending developer manual review

> **⚠ SYNTHETIC TRAINING DOCUMENT.** The MechaCo PNU-05 is a fictional device. All pressure values, fault codes, and specifications are invented for training purposes only. Do not apply these procedures to real pneumatic systems. Compressed air at any pressure can cause serious injury if a component fails unexpectedly. Always refer to the official manufacturer documentation and consult a qualified technician.

---

## Table of Contents

1. [Equipment Overview](#1-equipment-overview)
2. [Fictional Specifications](#2-fictional-specifications)
3. [Fault Scenarios and Diagnosis](#3-fault-scenarios-and-diagnosis)
   - 3.1 [Weak or Slow Actuator Movement](#31-weak-or-slow-actuator-movement-gerakan-aktuator-lemah-atau-lambat)
   - 3.2 [Failure to Move](#32-failure-to-move-aktuator-tidak-bergerak)
   - 3.3 [Leakage Indication](#33-leakage-indication-indikasi-kebocoran)
   - 3.4 [Inconsistent or Erratic Motion](#34-inconsistent-or-erratic-motion-gerakan-tidak-konsisten)
   - 3.5 [Unsafe Pressure Conditions](#35-unsafe-pressure-conditions-kondisi-tekanan-tidak-aman)
4. [Safe Inspection Checklist](#4-safe-inspection-checklist)
5. [Depressurisation Procedure](#5-depressurisation-procedure)
6. [Prohibited Actions](#6-prohibited-actions)
7. [Escalation Conditions](#7-escalation-conditions)
8. [Indonesian Aliases and Bilingual Glossary](#8-indonesian-aliases-and-bilingual-glossary)

---

## 1. Equipment Overview [MGC-PNEUMATIC-001 §1]

The MechaCo PNU-05 is a fictional low-pressure pneumatic training system consisting of:

- A compressed air supply manifold with a manually operated main isolation valve
- A filter-regulator-lubricator (FRL) unit with a pressure gauge and manual bleed valve
- Two single-rod double-acting cylinders (Cylinder A and Cylinder B)
- Two 5/2-way solenoid-operated directional control valves (DCV-A and DCV-B)
- Flow control valves (one per cylinder end) for speed regulation
- Polyurethane tubing connecting all components
- A pressure switch providing a signal to the PLC when system pressure is within range

All diagnostic procedures in this document assume the technician has reviewed MGC-SAFETY-001, in particular Sections 4.3 (pneumatic hazards) and 5 (isolation/LOTO).

---

## 2. Fictional Specifications [MGC-PNEUMATIC-001 §2]

> ⚠ These values are fictional training values. They do not represent any real product.

| Parameter | Fictional Training Value |
|---|---|
| Maximum operating pressure | 6 bar |
| Minimum operating pressure | 4 bar |
| Nominal operating pressure | 5 bar |
| Regulator pressure range | 0–8 bar |
| Cylinder bore diameter (A and B) | 25 mm |
| Cylinder stroke (A and B) | 100 mm |
| Theoretical cylinder force at 5 bar (extend) | 245 N (fictional calculation only) |
| DCV coil supply voltage | 24 V DC |
| Pressure switch ON threshold | > 3.5 bar |
| Pressure switch OFF threshold | < 2.5 bar |
| Fault code — low system pressure | PN-01 |
| Fault code — DCV coil fault | PN-02 |
| Fault code — pressure switch fault | PN-03 |
| Tubing outer diameter | 6 mm (Push-in fitting) |

---

## 3. Fault Scenarios and Diagnosis [MGC-PNEUMATIC-001 §3]

---

### 3.1 Weak or Slow Actuator Movement [MGC-PNEUMATIC-001 §3.1]
*Gerakan aktuator lemah atau lambat*

**Symptom:** Cylinder extends or retracts more slowly than normal, or does not develop sufficient force to complete its task. System pressure gauge reads within normal range (4–6 bar). Fault code PN-01 may be absent.

**Indonesian aliases:** Gerakan aktuator lemah, silinder lambat, silinder tidak bertenaga, tekanan cukup tapi gerakan lambat.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Flow control valve set too restrictive | High | Inspect flow control valve setting on the exhaust side of the affected cylinder; open slightly and retest |
| C2 | Partial blockage in tubing — kinked or crushed tube | High | Visually trace the tubing run; look for kinks at fittings or guide channels |
| C3 | Cylinder seal worn — internal bypass reducing effective force | Medium | Observe if cylinder can be pushed in by hand during extension (indicates seal bypass) |
| C4 | DCV not fully shifting — partial actuation | Low | Listen for DCV click; partial coil energisation (< 20 V DC) may cause incomplete valve shift |

**Safe inspection steps** (with system pressure applied at nominal 5 bar — do not reach into cylinder path):

1. Stand clear of the cylinder stroke path before any test.
2. Observe the flow control valve on the exhaust port of the affected cylinder end. If the needle valve is fully closed, open it by one-quarter turn and retest cycle speed.
3. Trace the tubing from the DCV to the cylinder end fitting. Look for kinks at 90° bends or where tubing passes through guides.
4. If cylinder can be pushed in by hand during extension against 5 bar, an internal seal fault is confirmed — depressurise and replace cylinder (see §5 and §7).

**Stop condition:** If cylinder seal is confirmed bypassing — depressurise fully before further inspection.

---

### 3.2 Failure to Move [MGC-PNEUMATIC-001 §3.2]
*Aktuator tidak bergerak*

**Symptom:** Cylinder does not extend or retract at all when the DCV is commanded. Pressure gauge reads normal. PLC output LED for the relevant DCV is illuminated.

**Indonesian aliases:** Aktuator tidak bergerak, silinder tidak mau bergerak, silinder macet, tidak ada gerakan.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Flow control valve fully closed | High | Check both flow control valves on the affected cylinder — one may be accidentally fully closed |
| C2 | DCV not receiving 24 V DC signal — coil not energised | High | Measure DCV coil terminal voltage with multimeter: expect 22–26 V DC when PLC output is active |
| C3 | DCV coil burnt out — code PN-02 | Medium | Remove DCV coil connector and measure coil resistance: expect 25 Ω ± 5 Ω (fictional value); open circuit = failed coil |
| C4 | Cylinder mechanically seized — piston rod jammed | Medium | Attempt to move the piston rod by hand **only after full depressurisation** (§5) |
| C5 | Tubing completely disconnected at push-in fitting | Low | Audible air exhaust near the disconnection point |

**Safe inspection steps:**

1. Verify both flow control valves on the affected cylinder are open (needle valve not fully closed).
2. Measure coil voltage at the DCV connector during the command cycle. Expect 22–26 V DC.
3. If coil voltage is correct but DCV does not shift (audible click absent), replace the coil after **depressurising the system** (§5).
4. If PN-02 is active, measure coil resistance — open circuit confirms coil failure.

**Stop condition:** If attempting to check a seized cylinder — fully depressurise before any physical access to the cylinder.

---

### 3.3 Leakage Indication [MGC-PNEUMATIC-001 §3.3]
*Indikasi kebocoran*

**Symptom:** Audible hissing from the system when at rest or during operation. System pressure drops when the compressor is isolated. Cylinder does not hold position under load. Fault code PN-01 may appear.

**Indonesian aliases:** Kebocoran udara, suara mendesis, tekanan turun, silinder tidak bisa menahan posisi, bocor.

> **⚠ Caution:** Never attempt to locate or touch a leaking pneumatic connection while the system is pressurised. Pressurised air escaping from a small orifice can inject air into skin tissue, causing serious injury.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Push-in fitting not fully engaged — tube not fully inserted | High | Visually inspect fittings; gently pull tube to confirm it is retained by the collet |
| C2 | Tubing cut or cracked near a fitting | High | Apply soapy water to fittings and tubing runs — bubbles indicate leak location |
| C3 | DCV exhaust port seal degraded — air bleeding from exhaust | Medium | Locate exhaust port; air escaping at rest (DCV centred) indicates internal seal wear |
| C4 | Cylinder rod seal leak — air escaping around piston rod | Medium | Observe cylinder rod for air movement or soapy bubble growth |

**Safe inspection steps:**

1. **Do not touch or probe a leaking fitting while pressurised.** Reduce system pressure to below 1 bar before approaching (reduce regulator setting, not by touching the fitting).
2. To locate a small leak, apply a thin film of soapy water to fittings, tube runs, and the DCV body. Bubbles grow at the leak location.
3. After locating the leak, **fully depressurise** using the bleed valve on the FRL unit (§5), then repair.
4. For a push-in fitting leak: depressurise, press the collet release ring, remove and re-insert tube fully (tube should stop at the marking line on the tube end).

**Stop condition:** A leak at a pressure vessel thread, a crack in the regulator body, or a leak at any component that cannot be isolated with the manual main valve — **escalate immediately.**

---

### 3.4 Inconsistent or Erratic Motion [MGC-PNEUMATIC-001 §3.4]
*Gerakan tidak konsisten / tidak menentu*

**Symptom:** Cylinder stroke speed or force varies between cycles without any change in setpoint. May be faster on some cycles and slower on others.

**Indonesian aliases:** Gerakan tidak konsisten, kecepatan berubah-ubah, gerakan tidak menentu, silinder bergerak tidak teratur.

> **Note:** This is a multi-cause scenario. Two causes may be present simultaneously.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Unstable supply pressure — compressor cycling under heavy load | High | Observe system pressure gauge during multiple cycles; look for pressure drops below 4 bar |
| C2 | Moisture in the air line — intermittent water slug affecting flow | Medium | Drain the FRL water bowl and observe if consistency improves |
| C3 | Flow control valve partially blocked — intermittent bypass | Medium | Replace flow control valve on affected side |
| C4 | DCV partially sticking — slow shift on some cycles | Low | Listen for consistent DCV click on each cycle |

**Safe inspection steps:**

1. Observe the pressure gauge during five consecutive cycles. Supply pressure must remain between 4 and 6 bar throughout. If it drops below 4 bar, code PN-01 will activate.
2. Drain the FRL water bowl: turn the drain plug at the bottom of the bowl by one-quarter turn (with system pressure below 2 bar or using the manual bleed). Collect any drained water.
3. If moisture is found, inspect the air supply for a malfunctioning compressor air dryer.

---

### 3.5 Unsafe Pressure Conditions [MGC-PNEUMATIC-001 §3.5]
*Kondisi tekanan tidak aman*

**Symptom:** System pressure is outside the safe operating range. This includes:
- Over-pressure: gauge reads above 6 bar (*tekanan berlebih*)
- Pressure not reducing to zero after isolation and bleed (*tekanan tidak turun ke nol*)
- Component appears deformed, swollen, or cracked under pressure (*komponen rusak di bawah tekanan*)

**Indonesian aliases:** Tekanan berlebih, tekanan terlalu tinggi, tekanan tidak aman, komponen bengkak, tekanan tidak bisa diturunkan.

> **⚠ ESCALATION REQUIRED — DO NOT ATTEMPT FURTHER DIAGNOSIS.**

An unsafe pressure condition is a critical-risk scenario. Stored pneumatic energy at elevated pressure can cause sudden component failure, projectile hazards, and serious injury.

**Immediate actions:**

1. Stop the machine immediately using the emergency stop or normal stop control.
2. Do not approach the pressurised area.
3. If the regulator allows, reduce the regulator setpoint to minimum from a safe distance.
4. Do not attempt to access, touch, or remove any component that is visibly distorted, bulging, or cracked under pressure.
5. **Escalate to a qualified technician immediately.** Do not resume operation until a qualified technician has inspected and cleared the system.

**Safe return to service** (qualified technician only):

- Isolate air supply at the main valve.
- Use the FRL manual bleed valve to reduce system pressure to zero.
- Verify zero pressure with the gauge before touching any component.
- Identify the root cause of the over-pressure condition before reconnecting the supply.

---

## 4. Safe Inspection Checklist [MGC-PNEUMATIC-001 §4]

Before any physical inspection involving component access:

- [ ] Main air supply valve closed (manual quarter-turn valve)
- [ ] System depressurised using FRL bleed valve — gauge reads 0 bar (§5)
- [ ] Zero pressure confirmed on gauge and by pressing a tube collet release briefly
- [ ] LOTO applied to main air supply valve (MGC-SAFETY-001 §5.1)
- [ ] No visible deformation or damage on any component before proceeding
- [ ] Relevant fault scenario identified (Section 3.x)
- [ ] Soapy water test (if needed for leak location) only at reduced pressure (< 1 bar), not at system pressure

---

## 5. Depressurisation Procedure [MGC-PNEUMATIC-001 §5]

> **Mandatory before any physical component access.**

1. Issue a stop command to the PLC to de-energise all DCV solenoids.
2. Close the main air supply isolation valve (quarter-turn handle to the closed position, perpendicular to the pipe).
3. Allow any residual actuator movement to complete and machine to reach a stationary state.
4. Open the manual bleed valve on the FRL unit slowly (turn anti-clockwise). Listen for air exhaust. Allow to exhaust fully.
5. Observe the pressure gauge: it must read **0 bar** before proceeding.
6. As a secondary check, press and hold the collet release button on any push-in fitting for 2 seconds. No air should escape.
7. Apply LOTO to the main supply isolation valve.
8. Confirm zero pressure one final time before touching any fitting, tube, or component.

---

## 6. Prohibited Actions [MGC-PNEUMATIC-001 §6]

| # | Prohibited Action |
|---|---|
| P-01 | Touching, probing, or removing a pressurised push-in fitting or tube |
| P-02 | Increasing regulator pressure above the rated maximum (6 bar) |
| P-03 | Attempting to locate a leak by passing fingers over a pressurised fitting |
| P-04 | Accessing a cylinder for seal inspection without fully depressurising (§5) |
| P-05 | Resuming operation after an over-pressure event without a qualified technician inspection |
| P-06 | Bypassing the pressure switch or any pressure-relief device |

---

## 7. Escalation Conditions [MGC-PNEUMATIC-001 §7]

Stop all work immediately and contact a qualified technician if:

- System pressure exceeds 6 bar (*tekanan melebihi 6 bar*)
- Pressure does not drop to zero after full bleed procedure
- Any component shows visible deformation, bulging, or cracking
- A fitting or tube cannot be reseated and leakage continues
- The main air supply valve does not isolate completely
- An over-pressure condition has occurred for any reason
- Cylinder seal replacement is required (requires specific tooling and seal kits)

---

## 8. Indonesian Aliases and Bilingual Glossary [MGC-PNEUMATIC-001 §8]

| English | Bahasa Indonesia |
|---|---|
| Pneumatic system | Sistem pneumatik |
| Actuator / cylinder | Aktuator / silinder pneumatik |
| Extend | Maju / keluar (silinder) |
| Retract | Mundur / masuk (silinder) |
| System pressure | Tekanan sistem |
| Over-pressure | Tekanan berlebih / overpressure |
| Leakage | Kebocoran |
| Bleed / depressurise | Lepas tekanan / depressurisasi |
| Main isolation valve | Katup isolasi utama |
| FRL unit (filter-regulator-lubricator) | Unit FRL (filter-regulator-pelumas) |
| Directional control valve (DCV) | Katup kontrol arah (KKA) |
| Flow control valve | Katup kontrol aliran |
| Push-in fitting | Fitting tekan / quick-fit |
| Pressure gauge | Pengukur tekanan / pressure gauge |
| Pressure switch | Saklar tekanan |
| Solenoid coil | Kumparan solenoid |
| Seal | Sil / gasket |
| Piston rod | Batang piston |
| Stored energy | Energi tersimpan |
| Safe operating range | Rentang operasi aman |
