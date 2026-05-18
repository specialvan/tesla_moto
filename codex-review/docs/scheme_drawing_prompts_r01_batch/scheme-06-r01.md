# S06 r01 提示词批包 · pmasynrm_high_saliency_low_pm

修订日期：2026-05-18  
方案 ID：`pmasynrm_high_saliency_low_pm`  
工程目录：`engineering/v2/scheme-06/`（仅 README）

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S06 PMaSynRM HIGH-SALIENCY LOW-PM — DRIVER BLOCK` |
| T02 | `S06 PMaSynRM — POWER-ON SEQUENCE` |
| T03 | `S06 HIGH-SALIENCY MTPA / MTPV — STATE MACHINE` |
| T04 | `S06 PMaSynRM — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S06 ROTOR / STATOR — CONCEPT CROSS-SECTION (CONCEPT ONLY)` |
| T06 | `S06 LOW-PM TOPOLOGY — BOM / EDA RISK TREE` |
| T07 | `S06 PMaSynRM — VERIFICATION PLAN` |
| T08 | `S06 PMaSynRM — PROTOCOL LINK` |

## 1. 生产参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| Vdc | 360 | V | motor_params.json |
| Imax | 260 | A | motor_params.json |
| 凸极比 L_q/L_d | >= 5 | — | r01 估值（PMaSynRM target） |
| PM fraction | 30-50 | % | r01 估值（低 PM 占比） |
| demag id_min | -200 | A | r01 估值（低 PM 更易退磁） |
| ripple <= | 3 | % | r01 估值 |
| 转子最大应力 | < 700 | MPa | r01 估值 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S06-T01-r01
[priority] P1
[size] 1792x1024
[positive prompt]
Flat technical block diagram for S06 PMaSynRM high-saliency low-PM control chain.
Title: "S06 PMaSynRM HIGH-SALIENCY LOW-PM — DRIVER BLOCK".
Power-stage: standard 5-block chain with motor labeled "PMaSynRM Motor
(PM fraction 30-50 %, saliency Lq/Ld >= 5, pole pairs 4)".
Control row standard. Top sub-block: "High-saliency MTPA/MTPV Control
(Vmax 207.85 V, Imax 260 A) with Low-PM demag boundary monitor
(id_min nominal -200 A)". Feed demag input from temperature sensors.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- saliency ratio and PM fraction labels visible
- demag id_min boundary in monitor block
```

### T02 sequence

```text
[image_id] IMG-S06-T02-r01
[priority] P2
[size] 1792x1024
[positive prompt]
UML sequence for S06 power-on, lifelines VCU/MCU/INV/M. Steps similar to S02 but
add specific "load demag boundary id_min = -200 A" and "load saliency LUT".
Title: "S06 PMaSynRM — POWER-ON SEQUENCE".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- demag id_min = -200 A step explicit
```

### T03 state machine（**P0 必修**）

```text
[image_id] IMG-S06-T03-r01
[priority] P0
[size] 1024x1024
[positive prompt]
Finite-state-machine for S06. Title: "S06 HIGH-SALIENCY MTPA / MTPV — STATE MACHINE".
<r01 ENUM RULE>
STATES (exactly 5, do NOT add a sixth Fault Fallback — that belongs to S11):
  "MTPA active"
  "High-saliency FW"
  "MTPV"
  "Low-PM demag guard (id_min nominal -200 A)"
  "Derate (thermal / demag)"
EDGES (exactly 5, unique labels):
  "MTPA active" -> "High-saliency FW" : "MTPA boundary reached"
  "High-saliency FW" -> "MTPV" : "FW margin shrinking"
  "MTPV" -> "Low-PM demag guard (id_min nominal -200 A)" : "MTPV boundary"
  "Low-PM demag guard (id_min nominal -200 A)" -> "Derate (thermal / demag)" : "demag risk rising"
  "Derate (thermal / demag)" -> "MTPA active" : "recover"
Highlight "Low-PM demag guard" and "Derate" red.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- EXACTLY 5 states (NO Fault Fallback; r00 added one wrongly)
- demag id_min -200 A visible
```

### T04 PCB concept

```text
[image_id] IMG-S06-T04-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S06 high-saliency controller. Title:
"S06 PMaSynRM — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Groups: (CONTROL) "MCU + FOC for high-saliency", "id_min(T) clamp logic";
(SENSING) "phase current (low PM operating range, 0-200 A)", "Vdc sense",
"motor / inverter / magnet temperature ADC";
(DEMAG DIAG) "demag diagnostic input", "id_min readback";
(POSITION) "resolver demod (high saliency needs higher resolution)";
(SAFETY) "gate-disable hardware path".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 groups; CONCEPT watermark
```

### T05 CAD packaging concept

```text
[image_id] IMG-S06-T05-r01
[priority] P1
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE cross-section for S06 PMaSynRM rotor / stator topology.
Title: "S06 ROTOR / STATOR — CONCEPT CROSS-SECTION (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Flat line illustration only. NO real material names.
Show:
- "Rotor with PM fraction 30-50 % (generic permanent magnets in flux barriers)"
- "Flux barrier pattern (multi-layer)"
- "Magnetic bridge (stress relief, target stress < 700 MPa)"
- "Hairpin stator slot outline"
- "Cooling jacket interface (generic liquid cooling)"
- "PM stay-in pocket"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- PM fraction and stress threshold visible
- flat line illustration only
```

### T06 BOM tree

```text
[image_id] IMG-S06-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
BOM risk tree for S06 low-PM topology. Title: "S06 LOW-PM TOPOLOGY — BOM / EDA RISK TREE".
Root "S06 pmasynrm_high_saliency_low_pm".
FIXED:
- "Low-PM permanent magnets (generic)" -> HIGH
- "Laminations (generic electrical steel)" -> MED
- "Hairpin windings (generic copper)" -> MED
- "Cooling / temperature sensing" -> LOW
- "Resolver high-resolution" -> MED
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 branches; only generic names
```

### T07 verification tree

```text
[image_id] IMG-S06-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S06. Title: "S06 PMaSynRM — VERIFICATION PLAN".
Branches (placeholder DVP IDs):
(S06-DV-001) "Torque ripple <= 3 %"
(S06-DV-002) "Mechanical stress (rotor < 700 MPa)"
(S06-DV-003) "Demagnetization (id_min nominal -200 A)"
(S06-DV-004) "Thermal / cooling"
(S06-DV-005) "NVH"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- numeric thresholds present
```

### T08 protocol link

```text
[image_id] IMG-S06-T08-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Network block for S06 protocol. Title: "S06 PMaSynRM — PROTOCOL LINK".
Vertical chain: VCU CAN-FD -> MCU -> "Saliency Control Telemetry + Demag Warning Channel" ->
FOC -> SVPWM -> Inverter. Right branches: UDS/XCP + Calibration.
Bus labels explicit (no Internal Bus placeholder).
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all bus labels with speeds
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S06-T01-r01 | P1 | [ ] | [ ] |
| IMG-S06-T02-r01 | P2 | [ ] | [ ] |
| IMG-S06-T03-r01 | **P0** | [ ] | [ ] |
| IMG-S06-T04-r01 | P2 | [ ] | [ ] |
| IMG-S06-T05-r01 | P1 | [ ] | [ ] |
| IMG-S06-T06-r01 | P2 | [ ] | [ ] |
| IMG-S06-T07-r01 | P2 | [ ] | [ ] |
| IMG-S06-T08-r01 | P2 | [ ] | [ ] |
