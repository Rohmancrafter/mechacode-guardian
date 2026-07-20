# MGC-PLC-001 — MechaCo PLC-200 Training Programmable Controller Diagnostic Guide

**Document ID:** MGC-PLC-001
**Version:** 1.0.0
**Date:** 2026-07-20
**Author:** Muhammad Nur Rohman
**Project:** MechaCode Guardian
**License:** CC BY-NC 4.0
**Provenance:** Original synthetic content — not a real manufacturer document
**Safety Classification:** Moderate
**Equipment:** MechaCo PLC-200 (fictional 24 V DC training programmable logic controller)
**Language:** English (with Indonesian aliases)
**Status:** ⚠ UNVERIFIED — Pending developer manual review

> **⚠ SYNTHETIC TRAINING DOCUMENT.** The MechaCo PLC-200 is a fictional device. All fault codes, register values, and specifications are invented for training purposes only. Do not apply these procedures to real PLC systems. Always refer to the official manufacturer documentation and consult a qualified technician for real equipment.

---

## Table of Contents

1. [Equipment Overview](#1-equipment-overview)
2. [Fictional Specifications](#2-fictional-specifications)
3. [Fault Scenarios and Diagnosis](#3-fault-scenarios-and-diagnosis)
   - 3.1 [Missing Input Signal](#31-missing-input-signal-sinyal-input-tidak-ada)
   - 3.2 [Inactive Output](#32-inactive-output-output-tidak-aktif)
   - 3.3 [Communication Fault Indication](#33-communication-fault-indication-indikasi-kesalahan-komunikasi)
   - 3.4 [Unexpected Machine State](#34-unexpected-machine-state-kondisi-mesin-tidak-terduga)
   - 3.5 [Safe Diagnostic Isolation](#35-safe-diagnostic-isolation-isolasi-diagnostik-yang-aman)
4. [Safe Inspection Checklist](#4-safe-inspection-checklist)
5. [Prohibited Actions](#5-prohibited-actions)
6. [Escalation Conditions](#6-escalation-conditions)
7. [Indonesian Aliases and Bilingual Glossary](#7-indonesian-aliases-and-bilingual-glossary)

---

## 1. Equipment Overview [MGC-PLC-001 §1]

The MechaCo PLC-200 is a fictional compact modular PLC used in educational mechatronics training systems. It consists of a CPU module, a digital input module (8 inputs, 24 V DC sourcing), a digital output module (8 outputs, 24 V DC transistor NPN), and a power supply module. All modules are mounted on a DIN rail inside a training panel.

The CPU module has a built-in status display showing: RUN (green), STOP (amber), ERROR (red), and COMM (blue) indicator LEDs. Fault codes are accessible via the status display scroll function or a connected programming terminal.

All diagnostic procedures in this document assume the technician has reviewed MGC-SAFETY-001 and completed the pre-inspection prerequisites in MGC-SAFETY-001 §6.

---

## 2. Fictional Specifications [MGC-PLC-001 §2]

> ⚠ These values are fictional training values. They do not represent any real product.

| Parameter | Fictional Training Value |
|---|---|
| CPU supply voltage | 24 V DC ± 10% |
| I/O bus voltage | 24 V DC |
| Digital inputs | 8 × 24 V DC sourcing (current sink input) |
| Input ON threshold | > 15 V DC |
| Input OFF threshold | < 5 V DC |
| Digital outputs | 8 × NPN transistor, 0.5 A per output max |
| Program scan cycle time | 5 ms (training load) |
| Fault code — input module fault | PL-I01 |
| Fault code — output module fault | PL-O01 |
| Fault code — CPU communication error | PL-C01 |
| Fault code — watchdog timeout | PL-W01 |
| Fault code — power supply out of range | PL-P01 |
| Non-volatile memory | 128 KB flash (program) |

---

## 3. Fault Scenarios and Diagnosis [MGC-PLC-001 §3]

---

### 3.1 Missing Input Signal [MGC-PLC-001 §3.1]
*Sinyal input tidak ada*

**Symptom:** A machine function that depends on a specific PLC input does not respond. The input indicator LED on the input module does not illuminate when the field device is activated. Fault code PL-I01 may appear.

**Indonesian aliases:** Sinyal input tidak ada, input tidak terdeteksi, LED input mati, kode PL-I01.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Field device (sensor or switch) not providing signal | High | Verify sensor operation independently (see MGC-SENSOR-001) |
| C2 | Field wiring between device and PLC input terminal disconnected or open | High | Measure voltage at PLC input terminal: expect > 15 V DC when device is active |
| C3 | PLC input channel failed internally | Medium | Code PL-I01 active; substitute a working input channel and retest program |
| C4 | I/O bus supply voltage out of range | Low | Measure I/O bus voltage: expect 22–26 V DC |

**Safe inspection steps** (with machine in STOP mode):

1. Place the PLC in STOP mode using the mode switch on the CPU. Confirm STOP indicator is amber.
2. Activate the field device manually and observe the corresponding input LED on the input module.
3. If LED is off, measure voltage at the input terminal with a multimeter: expect > 15 V DC when device is active.
4. If voltage is present but LED is off, the input channel is suspect — test on an adjacent channel.
5. If voltage is absent, trace the field wiring from the device to the PLC terminal. Check for open connections, loose terminal screws, or damaged cable.

**Stop condition:** If the PLC displays fault code PL-P01 (power supply out of range) at any point — stop and escalate.

---

### 3.2 Inactive Output [MGC-PLC-001 §3.2]
*Output tidak aktif*

**Symptom:** A machine actuator (motor, valve, or indicator) that is controlled by a PLC output does not operate, even though the PLC program logic should have activated the output. The output indicator LED may or may not be illuminated.

**Indonesian aliases:** Output tidak aktif, aktuator tidak bergerak, LED output tidak menyala, kode PL-O01.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Output LED off — PLC logic has not activated the output | High | Review the PLC program logic for the relevant output; check input conditions that enable it |
| C2 | Output LED on, but actuator not responding — wiring or load fault | High | Measure voltage at the output terminal: expect 0 V when active (NPN transistor pulls to 0 V) |
| C3 | Output LED on, wiring correct — actuator internal fault | Medium | Substitute with a known-good actuator or verify actuator independently |
| C4 | Output module failed — code PL-O01 | Low | PL-O01 active; output channel does not switch even though logic requests it |

**Safe inspection steps** (with machine isolated for actuator wiring checks):

1. In STOP mode, use the programming terminal's forced output function (if available and permitted) to activate the suspect output channel. Observe the output LED.
2. If LED activates but actuator does not respond, measure voltage at the actuator wiring terminals (with actuator circuit isolated). NPN output: expect 0 V (connected to 0 V bus) when active.
3. If voltage is correct at the terminal but actuator does not operate, the fault is within the actuator — investigate separately.
4. If LED does not activate via force command and PL-O01 is present, the output module may be damaged — escalate.

**Stop condition:** If forced output activation is not authorised by a qualified technician — do not force outputs. Proceed only with observation and measurement.

---

### 3.3 Communication Fault Indication [MGC-PLC-001 §3.3]
*Indikasi kesalahan komunikasi*

**Symptom:** COMM indicator LED on CPU is red or flashing. PLC may show fault code PL-C01. Programming terminal cannot connect. A connected remote I/O module may not respond.

**Indonesian aliases:** Kesalahan komunikasi, COMM error, PLC tidak bisa dihubungi, kode PL-C01.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Communication cable physically disconnected or damaged | High | Inspect the communication cable between CPU and terminal or between modules |
| C2 | Incorrect communication settings (baud rate, address) | Medium | Verify settings match between programming terminal and PLC (see fictional default: 9600 baud, address 1) |
| C3 | CPU module overloaded — watchdog timeout (PL-W01) | Medium | PL-W01 may appear alongside PL-C01; power-cycle the PLC and observe if fault clears |
| C4 | EMI interference affecting communication line | Low | Inspect cable routing for proximity to power cables; reroute if necessary |

**Safe inspection steps:**

1. Inspect the communication cable at both ends. Press connectors firmly; check for damaged pins.
2. Power-cycle the PLC (turn off 24 V DC supply, wait 10 seconds, restore). Observe startup LED sequence: RUN (green) should be steady within 3 seconds.
3. If fault clears after power-cycle but recurs, suspect intermittent cable or EMI — document frequency and circumstances.
4. Verify programming terminal settings: baud rate 9,600, address 1 (fictional defaults for PLC-200).

**Stop condition:** If the PLC does not reach RUN state after power-cycle and PL-W01 remains — stop and escalate.

---

### 3.4 Unexpected Machine State [MGC-PLC-001 §3.4]
*Kondisi mesin tidak terduga*

**Symptom:** A machine axis, valve, or actuator is in a state (active or inactive) that does not correspond to the expected program state. The machine may have moved unexpectedly, or a process may have skipped a step.

**Indonesian aliases:** Kondisi mesin tidak terduga, mesin bergerak sendiri, kondisi output salah, aktuator aktif tanpa perintah.

> **⚠ Safety Priority:** Unexpected machine movement is a high-risk condition. Do not approach the machine or attempt manual inspection while the machine is in an unknown state with power applied. Escalation may be required.

| # | Possible Cause | Likelihood | Distinguishing Check |
|---|---|---|---|
| C1 | Program logic error — incorrect condition or wrong output mapped | High | Review program rung logic for the affected output in programming terminal |
| C2 | Spurious input signal causing incorrect step transition | Medium | Monitor input values in real time on programming terminal during fault condition |
| C3 | Stuck or welded output relay/transistor in output module | Medium | Check output physically while in STOP mode; output should not have voltage |
| C4 | Memory corruption — PL-W01 previously occurred | Low | Check event log in programming terminal; if PL-W01 recently occurred, verify program checksum |

**Safe inspection steps:**

1. **Before approaching the machine,** place the PLC in STOP mode. Confirm that all outputs have de-activated and the machine is stationary.
2. If the machine does not de-activate on STOP mode — **stop, do not approach, and escalate immediately.**
3. If machine de-activates in STOP mode, use the programming terminal to read the current state of all inputs and outputs.
4. Enable real-time monitoring and restore to RUN mode only while observing from a safe position outside any hazard zone.
5. Identify which input or output transitions at the incorrect moment.

**Stop condition:** If any output remains active in PLC STOP mode — this is an escalation condition. See §6.

---

### 3.5 Safe Diagnostic Isolation [MGC-PLC-001 §3.5]
*Isolasi diagnostik yang aman*

This section defines the safe isolation procedure for the MechaCo PLC-200 before any physical inspection of modules, terminals, or wiring.

**Procedure:**

1. Place PLC in STOP mode using the CPU mode switch. Confirm STOP LED is amber.
2. Confirm all machine axes and actuators are de-activated and in a safe rest position.
3. If any actuator is suspended or elevated, lower it to the ground state before proceeding.
4. Isolate the 24 V DC supply to the I/O bus using the dedicated isolator switch on the training panel.
5. Apply LOTO to the isolator (MGC-SAFETY-001 §5.1).
6. Verify zero voltage at the I/O bus terminal strip using a calibrated multimeter. Expect < 1 V DC.
7. Verify zero voltage at the CPU supply terminals. Expect < 1 V DC.
8. Proceed with physical inspection.

> **Note:** The CPU itself may retain its program in non-volatile flash memory after power-off. No data is lost by following this isolation procedure under normal operating conditions.

---

## 4. Safe Inspection Checklist [MGC-PLC-001 §4]

- [ ] PLC placed in STOP mode; STOP LED (amber) confirmed
- [ ] All machine actuators de-activated and in safe rest position
- [ ] I/O bus supply isolated and LOTO applied (§3.5)
- [ ] Zero voltage verified at I/O bus terminals and CPU supply
- [ ] Programming terminal connected and fault codes read
- [ ] Event log checked for recent PL-W01 (watchdog) events

---

## 5. Prohibited Actions [MGC-PLC-001 §5]

| # | Prohibited Action |
|---|---|
| P-01 | Modifying the PLC program on a running machine without change authorisation |
| P-02 | Forcing outputs while personnel are in the machine work envelope |
| P-03 | Replacing a CPU or output module without first isolating the I/O bus supply |
| P-04 | Clearing fault codes without identifying and resolving the root cause |
| P-05 | Operating a machine that moved unexpectedly without first understanding the cause |

---

## 6. Escalation Conditions [MGC-PLC-001 §6]

Stop all work immediately and contact a qualified technician if:

- A machine actuator remains active in PLC STOP mode (*output aktif saat PLC dalam mode STOP*)
- Fault code PL-P01 (power supply out of range) is active
- PLC does not reach RUN state after a power-cycle and PL-W01 remains active
- Program checksum error is indicated after a previous PL-W01 event
- Unexpected machine movement occurs and cannot be stopped by PLC STOP command
- Any wiring fault is found at voltages that cannot be confirmed as 24 V DC only

---

## 7. Indonesian Aliases and Bilingual Glossary [MGC-PLC-001 §7]

| English | Bahasa Indonesia |
|---|---|
| PLC input | Input PLC |
| PLC output | Output PLC |
| Input signal missing | Sinyal input tidak ada |
| Output inactive | Output tidak aktif |
| Communication fault | Kesalahan komunikasi |
| Unexpected machine state | Kondisi mesin tidak terduga |
| STOP mode | Mode STOP |
| RUN mode | Mode RUN |
| Fault code | Kode kesalahan |
| Output module | Modul output |
| Input module | Modul input |
| CPU module | Modul CPU |
| Programming terminal | Terminal pemrograman |
| Watchdog timeout | Timeout watchdog |
| Forced output | Output yang dipaksa aktif |
| Event log | Log kejadian |
| DIN rail | Rel DIN |
| I/O bus | Bus I/O |
| Scan cycle | Siklus scan |
