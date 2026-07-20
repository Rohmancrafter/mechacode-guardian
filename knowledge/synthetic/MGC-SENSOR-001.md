# MGC-SENSOR-001 — MechaCo SNS-10 Industrial Sensor Training Module Troubleshooting Guide

**Document ID:** MGC-SENSOR-001
**Version:** 1.0.0
**Date:** 2026-07-20
**Author:** Muhammad Nur Rohman
**Project:** MechaCode Guardian
**License:** CC BY-NC 4.0
**Provenance:** Original synthetic content — not a real manufacturer document
**Safety Classification:** Low (elevated to Moderate for wiring fault scenarios)
**Equipment:** MechaCo SNS-10 (fictional inductive proximity sensor training module)
**Language:** English (with Indonesian aliases)
**Status:** ⚠ UNVERIFIED — Pending developer manual review

> **⚠ SYNTHETIC TRAINING DOCUMENT.** The MechaCo SNS-10 is a fictional device. All specifications, output codes, and measured values are invented for training purposes only. Do not apply these procedures to real sensors or wiring. Always refer to the official manufacturer documentation and consult a qualified technician.

---

## Table of Contents

1. [Equipment Overview](#1-equipment-overview)
2. [Fictional Specifications](#2-fictional-specifications)
3. [Fault Scenarios and Diagnosis](#3-fault-scenarios-and-diagnosis)
   - 3.1 [No Signal Output](#31-no-signal-output-tidak-ada-sinyal-keluaran)
   - 3.2 [Unstable or Flickering Signal](#32-unstable-or-flickering-signal-sinyal-tidak-stabil)
   - 3.3 [Incorrect Detection](#33-incorrect-detection-deteksi-tidak-tepat)
   - 3.4 [Alignment Problems](#34-alignment-problems-masalah-penyelarasan)
   - 3.5 [Contamination](#35-contamination-kontaminasi)
   - 3.6 [Wiring Faults](#36-wiring-faults-kesalahan-kabel)
   - 3.7 [Escalation Conditions](#37-escalation-conditions-kondisi-eskalasi)
4. [Safe Inspection Checklist](#4-safe-inspection-checklist)
5. [Prohibited Actions](#5-prohibited-actions)
6. [Indonesian Aliases and Bilingual Glossary](#6-indonesian-aliases-and-bilingual-glossary)

---

## 1. Equipment Overview [MGC-SENSOR-001 §1]

The MechaCo SNS-10 is a fictional three-wire NPN inductive proximity sensor used in educational mechatronics systems. It detects metallic target objects within its defined sensing range and provides a switched DC output signal to a PLC or controller input. It is typically mounted on an adjustable bracket and connected via a four-core shielded cable.

This guide covers seven fault scenarios. All diagnostic procedures assume the technician has reviewed MGC-SAFETY-001 and completed the pre-inspection prerequisites in MGC-SAFETY-001 §6.

---

## 2. Fictional Specifications [MGC-SENSOR-001 §2]

> ⚠ These values are fictional training values. They do not represent any real product.

| Parameter | Fictional Training Value |
|---|---|
| Supply voltage | 12–24 V DC (nominal 24 V DC) |
| Output type | NPN (normally open, switched to 0 V when target present) |
| Sensing range (nominal) | 8 mm |
| Sensing range (reliable zone) | 0–6 mm from face |
| Output current (max) | 200 mA |
| Indicator LED colour — active | Green (target present) |
| Indicator LED colour — power on | Amber |
| Output voltage (inactive) | Supply voltage − 1.5 V (typically 22.5 V) |
| Output voltage (active — target present) | < 1.5 V |
| Output code — no supply | SN-00 |
| Output code — output short detected | SN-01 |
| Supply current (operating) | 15 mA |

---

## 3. Fault Scenarios and Diagnosis [MGC-SENSOR-001 §3]

---

### 3.1 No Signal Output [MGC-SENSOR-001 §3.1]
*Tidak ada sinyal keluaran*

**Symptom:** PLC input does not change state when target is present. Sensor LED does not illuminate. Controller or PLC may show code SN-00.

**Indonesian aliases:** Tidak ada sinyal, sensor tidak aktif, LED mati, kode SN-00.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Supply voltage absent or wiring disconnected | High | Measure supply voltage at sensor connector (Brown wire to Blue wire): expect 22–26 V DC |
| C2 | Target not within sensing range | High | Verify target distance is within 0–6 mm of sensor face |
| C3 | Sensor body damaged or failed internally | Medium | Substitute with a known-good sensor of the same model |
| C4 | Blown output protection — internal short | Low | Code SN-01 would also appear; measure output pin voltage |

**Safe inspection steps** (with supply powered — low-voltage 24 V DC only, by qualified person):

1. Verify target material is metallic (ferrous preferred). Non-metallic targets are not detected by inductive sensors.
2. Check supply voltage at the sensor connector. Measure Brown (+V) to Blue (0 V): expect 22–26 V DC.
3. Manually present a steel target (e.g., a steel key) at 2–4 mm from the sensor face. Observe indicator LED.
4. If LED still does not illuminate and supply is correct, the sensor has failed internally — replace.

**Stop condition:** If supply voltage is absent, trace the wiring before reconnecting (see §3.6).

---

### 3.2 Unstable or Flickering Signal [MGC-SENSOR-001 §3.2]
*Sinyal tidak stabil / berkedip-kedip*

**Symptom:** PLC input changes state rapidly without a corresponding change in target position. Signal may flicker even with no target present.

**Indonesian aliases:** Sinyal tidak stabil, sinyal berkedip, input PLC berubah sendiri, sinyal naik-turun.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Target distance at the edge of sensing range | High | Measure the gap between sensor face and target; should be 2–4 mm for reliable operation |
| C2 | Electrical interference from nearby power cable | Medium | Route sensor cable away from power cables; use shielded cable |
| C3 | Supply voltage fluctuating | Medium | Monitor supply voltage with a multimeter while machine is running |
| C4 | Loose connector or cable at the sensor body | Medium | Inspect cable connector for mechanical tightness |

**Safe inspection steps:**

1. Measure the air gap between the sensor face and the target. Adjust mounting bracket to achieve 2–4 mm.
2. Visually inspect the sensor cable for physical contact with power cables. Separate by at least 50 mm and route at 90° if crossing.
3. Monitor supply voltage during operation. Any reading below 22 V or above 26 V is outside the normal operating range; readings below 18 V or above 28 V indicate a probable supply fault requiring investigation. Do not operate the sensor outside the rated 12–24 V DC supply range.
4. Inspect the connector at the sensor body. Tighten the locking ring if present.

---

### 3.3 Incorrect Detection [MGC-SENSOR-001 §3.3]
*Deteksi tidak tepat*

**Symptom:** Sensor detects target at the wrong position, too early, or too late compared to the intended detection point.

**Indonesian aliases:** Deteksi tidak tepat, sensor aktif di posisi salah, posisi deteksi bergeser.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Sensor mounting bracket shifted position | High | Compare current sensor position to the installation drawing or reference mark |
| C2 | Target geometry changed (bent, worn, or replaced) | Medium | Inspect target for deformation or dimensional change |
| C3 | Sensing range reduced by contamination on sensor face | Medium | Inspect sensor face for metallic debris, oil, or coating |

**Safe inspection steps** (with machine isolated):

1. Compare sensor position to the reference mark on the bracket. Reposition and re-tighten if shifted.
2. Inspect the target for bending, wear, or material change.
3. Clean the sensor face with a dry cloth. Do not use solvents unless specified for the sensor body material.

---

### 3.4 Alignment Problems [MGC-SENSOR-001 §3.4]
*Masalah penyelarasan*

**Symptom:** Sensor does not reliably detect the target on every machine cycle, even though it detects correctly in a static test.

**Indonesian aliases:** Masalah penyelarasan, sensor tidak konsisten, kadang aktif kadang tidak, penyelarasan sensor buruk.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Sensor face not perpendicular to target approach path | High | Visually check approach angle; the target should approach parallel to the sensor axis |
| C2 | Target too small for sensing face diameter | Medium | Target must cover at least 50% of the sensor face diameter (fictional guideline) |
| C3 | Bracket loosening during machine vibration | Medium | Check bracket tightness after one complete operating cycle |

**Safe inspection steps** (with machine isolated):

1. Loosen the mounting clamp and adjust the sensor so its face is perpendicular to the target travel path.
2. Run one manual cycle by hand and observe the detection point.
3. Verify bracket fastener torque is within hand-tight plus one-half turn range.

---

### 3.5 Contamination [MGC-SENSOR-001 §3.5]
*Kontaminasi*

**Symptom:** Sensing range has reduced compared to initial setup. Sensor may detect intermittently or require target to be closer than normal.

**Indonesian aliases:** Kontaminasi, kotoran pada sensor, sensor kotor, jangkauan deteksi berkurang.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Metal chips or swarf on the sensor face | High | Visually inspect sensor face under adequate lighting |
| C2 | Oil film on sensor face | High | Wipe sensor face with a clean dry cloth and retest |
| C3 | Paint or coating applied to sensor face during maintenance | Medium | Inspect sensor face for any coating or overspray |

**Safe inspection steps:**

1. Power down the machine and lock out (MGC-SAFETY-001 §5.1).
2. Inspect the sensor face. Metal chips can reduce the effective sensing range by 20–50%.
3. Clean the sensor face with a dry lint-free cloth. For oil films, use an isopropyl alcohol wipe only if the sensor body material is confirmed compatible. Do not use acetone or other solvents.
4. Restore sensing gap and test with a static target.

---

### 3.6 Wiring Faults [MGC-SENSOR-001 §3.6]
*Kesalahan kabel*

**Symptom:** Supply voltage absent at sensor, or output signal reads unexpectedly high or low voltage. Code SN-01 may appear.

**Indonesian aliases:** Kesalahan kabel, kabel putus, kabel korsleting, kode SN-01, kabel sensor rusak.

> **⚠ Caution:** Wiring fault investigation requires confirming that supply power is isolated before accessing cable connectors. A 24 V DC short circuit can damage the sensor, controller input, or supply.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Cable physically damaged (pinched, cut, or abraded) | High | Inspect full cable run visually; check for chafing at cable ties or guides |
| C2 | Connector not fully seated at sensor or controller end | Medium | Push connectors firmly together and check for audible click (if keyed) |
| C3 | Polarity reversal — Brown and Blue wires swapped | Medium | Measure voltage: Brown must be positive; if reversed, switch off supply immediately |
| C4 | Output wire (Black) shorted to supply or 0 V | Low | Code SN-01 active; measure resistance from Black wire to Blue wire (0 V) — expect > 10 kΩ when sensor is not active and target is absent |

**Safe inspection steps** (with supply isolated per MGC-SAFETY-001 §5.1):

1. **Isolate supply before touching any wiring.** A 24 V DC supply is not immediately life-threatening at normal currents, but a short circuit can damage equipment and cause burns.
2. Inspect the full cable run from sensor to controller. Look for pinch points at cable trays, bend radii, or tie points.
3. Using a multimeter in resistance mode, verify continuity of each wire end-to-end.
4. Verify wire polarity matches the connection diagram: Brown = +V, Blue = 0 V, Black = output.
5. If polarity is reversed and the sensor was powered in that state, the sensor may be damaged — replace.

**Stop condition:** If the cable has been physically cut or severely damaged — escalate. Do not attempt to splice sensor signal cables without guidance.

---

### 3.7 Escalation Conditions [MGC-SENSOR-001 §3.7]
*Kondisi eskalasi*

Stop all work immediately and contact a qualified technician if:

- Supply voltage at the sensor exceeds 28 V DC (overvoltage risk)
- The sensor body is physically cracked, melted, or discoloured
- Code SN-01 persists after replacing the sensor (indicates a controller input fault)
- Polarity reversal is found and the sensor may have been powered in reverse
- The wiring fault cannot be identified after completing Section 3.6

---

## 4. Safe Inspection Checklist [MGC-SENSOR-001 §4]

- [ ] Machine isolated and LOTO applied for any physical wiring access (MGC-SAFETY-001 §5.1)
- [ ] Supply voltage confirmed present and within range (22–26 V DC) before signal testing
- [ ] Target material confirmed as metallic
- [ ] Sensor face visually inspected for contamination
- [ ] Sensing gap measured and within reliable zone (0–6 mm)
- [ ] Cable run visually inspected for damage

---

## 5. Prohibited Actions [MGC-SENSOR-001 §5]

| # | Prohibited Action |
|---|---|
| P-01 | Accessing sensor wiring connectors without isolating supply power |
| P-02 | Using solvents incompatible with the sensor body material for cleaning |
| P-03 | Forcing a connector that does not seat naturally |
| P-04 | Splicing or extending sensor cable without engineering approval |
| P-05 | Applying supply voltage above 28 V DC to an SNS-10 rated 12–24 V DC |

---

## 6. Indonesian Aliases and Bilingual Glossary [MGC-SENSOR-001 §6]

| English | Bahasa Indonesia |
|---|---|
| No signal output | Tidak ada sinyal keluaran |
| Unstable signal | Sinyal tidak stabil |
| Incorrect detection | Deteksi tidak tepat |
| Alignment problem | Masalah penyelarasan |
| Contamination | Kontaminasi |
| Wiring fault | Kesalahan kabel |
| Sensing range | Jangkauan deteksi |
| Target | Benda target / objek deteksi |
| Proximity sensor | Sensor jarak / sensor proksimiti |
| NPN output | Keluaran NPN |
| Indicator LED | LED indikator |
| Supply voltage | Tegangan suplai |
| Cable continuity | Kontinuitas kabel |
| Polarity | Polaritas |
| Short circuit | Korsleting / hubung singkat |
| Connector | Konektor |
| Shielded cable | Kabel berpelindung |
