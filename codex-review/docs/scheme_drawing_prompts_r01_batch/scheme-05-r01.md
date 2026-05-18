# S05 r01 提示词批包 · magnetic_saturation_codesign

修订日期：2026-05-18  
方案 ID：`magnetic_saturation_codesign`  
工程目录：`engineering/v2/scheme-05/`（仅 README，r01 工程占位）  
依据：reports / motor_params.json

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S05 MAGNETIC SATURATION CO-DESIGN — PIPELINE BLOCK` |
| T02 | `S05 CO-DESIGN PIPELINE — POWER-ON SEQUENCE` |
| T03 | `S05 GEOMETRY CO-DESIGN — PIPELINE STATE MACHINE` |
| T04 | `S05 SATURATION OBSERVER — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S05 ROTOR / STATOR — CONCEPT CROSS-SECTION (CONCEPT ONLY)` |
| T06 | `S05 MAGNETIC STACK — BOM / EDA RISK TREE` |
| T07 | `S05 SATURATION CO-DESIGN — VERIFICATION PLAN` |
| T08 | `S05 CO-DESIGN — DATA / VERSION LINK` |

## 1. 生产参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 候选 geometry 数 | 3-6 | — | r01 估值 |
| FEA LUT 节点 | id×iq×T = 30×30×5 | — | r01 估值 |
| 候选 score threshold | torque 提升 >= 5 % AND iron loss <= +3 % | — | r01 估值 |
| stress 限值 | 转子最大应力 < 600 MPa | — | r01 估值 |
| demag 限值 | id_min nominal >= -240 A | — | r02 同 S01 |
| iron loss budget | <= baseline + 3 % | — | r01 估值 |
| NVH torque ripple | <= 3 % | — | r01 估值 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S05-T01-r01
[priority] P1
[size] 1792x1024
[positive prompt]
Flat technical block diagram for S05 magnetic saturation co-design pipeline.
Title bar: "S05 MAGNETIC SATURATION CO-DESIGN — PIPELINE BLOCK".
This is NOT a motor controller chain. It is a design pipeline with these blocks
left-to-right: "Candidate Geometry Generator (3-6 candidates)" ->
"FEA Lambda LUT (id×iq×T = 30×30×5)" -> "Scorecard
(torque >= +5 %, iron loss <= +3 %, stress < 600 MPa, demag id_min >= -240 A,
ripple <= 3 %)" -> "Down-Select" -> "Retained Control LUT inputs (feed into
sim/run_control_lut_generator.py)". Show a feedback arrow from FEA LUT into the
scorecard.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- All scorecard thresholds visible
- Title verbatim; NO motor controller imagery
```

### T02 sequence

```text
[image_id] IMG-S05-T02-r01
[priority] P2
[size] 1792x1024
[positive prompt]
UML sequence for S05 co-design pipeline. Title: "S05 CO-DESIGN PIPELINE — POWER-ON SEQUENCE".
Lifelines: Engineer, CAD, FEA, Scorecard, Control LUT.
Arrows top-down:
(1) Engineer->CAD "submit candidate geometry rev X"
(2) CAD->FEA "geometry STEP (generic, no part numbers)"
(3) FEA self "mesh tetra, solve lambda(id,iq,T) 30×30×5"
(4) FEA->Scorecard "lambda LUT body + CRC"
(5) Scorecard self "compute torque, iron loss, stress, demag, ripple"
(6) Scorecard->Engineer "score vs threshold (torque +5 %, loss +3 %, stress 600 MPa, ripple 3 %)"
(7) Engineer->Control LUT "retain candidate or reject"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 7 arrows, threshold values present
```

### T03 state machine（**P0 必修**）

```text
[image_id] IMG-S05-T03-r01
[priority] P0
[size] 1024x1024
[positive prompt]
Finite-state-machine for S05 geometry co-design pipeline. Title bar:
"S05 GEOMETRY CO-DESIGN — PIPELINE STATE MACHINE".
DO NOT use "MOTOR CONTROLLER SUBSYSTEM" title (it is not a motor controller).
<r01 ENUM RULE>
STATES (exactly 6):
  "Candidate geometry intake"
  "FEA LUT request (id×iq×T = 30×30×5)"
  "Scorecard evaluation (torque +5 %, loss +3 %, ripple 3 %)"
  "Down-select"
  "Stop-criteria triggered (stress >= 600 MPa or demag risk)"
  "Retain for trade study"
EDGES (exactly 7):
  "Candidate geometry intake" -> "FEA LUT request (id×iq×T = 30×30×5)" : "geometry signed off"
  "FEA LUT request (id×iq×T = 30×30×5)" -> "Scorecard evaluation (torque +5 %, loss +3 %, ripple 3 %)" : "FEA result available"
  "Scorecard evaluation (torque +5 %, loss +3 %, ripple 3 %)" -> "Down-select" : "score above threshold"
  "Down-select" -> "Stop-criteria triggered (stress >= 600 MPa or demag risk)" : "stress / demag risk too high"
  "Down-select" -> "Retain for trade study" : "pareto retain"
  "Retain for trade study" -> "Candidate geometry intake" : "next candidate"
  "Scorecard evaluation (torque +5 %, loss +3 %, ripple 3 %)" -> "Stop-criteria triggered (stress >= 600 MPa or demag risk)" : "pareto loser"
Highlight "Stop-criteria triggered" red.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- title not "MOTOR CONTROLLER"
- 6 states with parenthetical numeric thresholds
```

### T04 PCB concept

```text
[image_id] IMG-S05-T04-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S05 saturation observer (optional bench data ingestion).
Title: "S05 SATURATION OBSERVER — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Groups: (SAMPLE) "current ia/ib/ic ADC", "lambda observer inputs";
(COMPUTE) "MCU compute headroom (FOC core)", "flux estimation block";
(DIAGNOSTIC) "saturation observer telemetry"; (BENCH PORT) "optional bench data port";
(TIMING) "sample window aligned to PWM".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 groups, CONCEPT watermark present
```

### T05 CAD packaging concept

```text
[image_id] IMG-S05-T05-r01
[priority] P1
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE cross-section for S05 rotor / stator topology.
Title: "S05 ROTOR / STATOR — CONCEPT CROSS-SECTION (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Flat line illustration, NO shading, NO real material names.
Show: "Rotor flux barriers (3 layers)", "Magnetic bridge (generic)",
"Magnet pockets (generic permanent magnets)", "Stator slot outline",
"Lamination stack (generic electrical steel)", "Mechanical stress callout
(stress < 600 MPa target)". Add coordinate frame on the side.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- flat line only; no real grade names
- stress threshold callout visible
```

### T06 BOM tree

```text
[image_id] IMG-S05-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
Component family risk tree for S05 magnetic stack. Title:
"S05 MAGNETIC STACK — BOM / EDA RISK TREE".
Root "S05 magnetic_saturation_codesign".
FIXED:
- "Electrical steel (generic)" -> MED
- "Permanent magnets (generic)" -> HIGH
- "Rotor process tooling" -> HIGH
- "Saturation observer sensors" -> MED
- "Stator slot lamination" -> LOW
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- generic family names only (NO grade designations)
```

### T07 verification tree

```text
[image_id] IMG-S05-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S05. Title: "S05 SATURATION CO-DESIGN — VERIFICATION PLAN".
Branches (placeholder DVP IDs, 待 r03 锁定):
(S05-DV-001) "FEA correlation (lambda LUT vs measured)"
(S05-DV-002) "Mechanical stress (rotor < 600 MPa @ 18000 rpm)"
(S05-DV-003) "Iron loss (<= baseline + 3 %)"
(S05-DV-004) "Demagnetization (id_min >= -240 A)"
(S05-DV-005) "NVH (torque ripple <= 3 %)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 placeholder DVP IDs with numeric thresholds
```

### T08 protocol link

```text
[image_id] IMG-S05-T08-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Data / version flow for S05. Title: "S05 CO-DESIGN — DATA / VERSION LINK".
Vertical chain: "CAD repo (geometry rev)" -> "FEA solver" -> "Lambda LUT artifact (CRC-32)" ->
"Scorecard" -> "Trade-study output" -> "Control LUT input (models/control_lut.json input)".
Right branch: "Audit log" + "Version registry".
Links use generic "data pipe" labels with CRC / version annotations.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- version+CRC labels present
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S05-T01-r01 | P1 | [ ] | [ ] |
| IMG-S05-T02-r01 | P2 | [ ] | [ ] |
| IMG-S05-T03-r01 | **P0** | [ ] | [ ] |
| IMG-S05-T04-r01 | P2 | [ ] | [ ] |
| IMG-S05-T05-r01 | P1 | [ ] | [ ] |
| IMG-S05-T06-r01 | P2 | [ ] | [ ] |
| IMG-S05-T07-r01 | P2 | [ ] | [ ] |
| IMG-S05-T08-r01 | P2 | [ ] | [ ] |
