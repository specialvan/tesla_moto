# S03 r01 提示词批包 · svpwm_overmodulation_voltage_utilization

修订日期：2026-05-18  
方案 ID：`svpwm_overmodulation_voltage_utilization`  
工程目录：`engineering/v2/scheme-03/`（仅 README，r01 中 PCB / CAD / BOM 用工程占位参数）  
依据：`reports/scheme_driver_power_protocol_diagrams.md`、`reports/scheme_bom_eda_integration_design.md`、`models/motor_params.json`

## 0. SCHEME_TITLE 锁定

| 模板 | 文本 |
|---|---|
| T01 | `S03 SVPWM / OVERMODULATION / SIX-STEP — DRIVER BLOCK` |
| T02 | `S03 OVERMODULATION — POWER-ON SEQUENCE` |
| T03 | `S03 OVERMODULATION CONTROL — STATE MACHINE` |
| T04 | `S03 OVERMODULATION — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S03 INVERTER POWER STAGE — CONCEPT PACKAGING (CONCEPT ONLY)` |
| T06 | `S03 OVERMODULATION — BOM / EDA RISK TREE` |
| T07 | `S03 OVERMODULATION — VERIFICATION PLAN` |
| T08 | `S03 OVERMODULATION — PROTOCOL LINK` |

## 1. 生产参数清单

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| Vdc 标称 | 360 | V | motor_params.json |
| Vmax SVPWM linear | 207.85 | V | 1/√3 · Vdc |
| Vmax six-step | 229.18 | V | 1.103 · Vmax(SVPWM linear) 估值 |
| Modulation index linear | ≤ 0.907 | — | r01 估值 |
| Modulation index overmodulation R1 | 0.907 - 0.952 | — | r01 估值（待 r03 FEA 标定） |
| Modulation index overmodulation R2 | 0.952 - 1.000 | — | 同上 |
| THD limit | ≤ 8 % | — | r01 估值（NVH 联动） |
| EMC limit | EN 55025 Class 5 | — | r01 工程占位 |
| 开关频率 | 10 | kHz | r01 估值 |
| Dead-time | 1.5 | μs | r01 估值 |

> 所有数值标 `r01 estimate`，r02 / r03 必须按 FEA + 台架替换。

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S03-T01-r01
[priority] P1
[size] 1792x1024
[reference image] gpt-image-2/outputs/S03/V2-S03-ILL-T01-driver_block-r00.png
[positive prompt]
Flat technical block diagram for S03 SVPWM / overmodulation / six-step control.
Title bar text MUST be: "S03 SVPWM / OVERMODULATION / SIX-STEP — DRIVER BLOCK".
Bottom power-stage row (5 blocks): "Battery / DC link (Vdc 360 V)",
"Precharge + Main Contactor", "3-Phase Inverter (10 kHz switching)",
"IPMSM Motor". Control row: "MCU + FOC", "Gate Drivers (dead-time 1.5 μs)",
"Encoder / Resolver", "Phase Current Sensors (ia/ib/ic)", "Vdc Sensor".
On top, highlighted sub-block: "SVPWM / Overmodulation / Six-Step Selector
(Vmax linear 207.85 V, Vmax six-step ~229 V, modulation index thresholds
0.907 / 0.952 / 1.000)" with input from MCU FOC voltage command and Vdc;
output PWM duties to Gate Drivers. Add a side block "THD / NVH Monitor
(THD <= 8 %)" feeding back into Selector with a derate signal.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
Selector block must show modulation index thresholds verbatim
add "10 kHz" label on inverter; "1.5 μs" inside Gate Drivers
[acceptance]
- Selector + THD/NVH Monitor visible; numerical thresholds present
```

### T02 power-on sequence

```text
[image_id] IMG-S03-T02-r01
[priority] P1
[size] 1792x1024
[positive prompt]
UML sequence for S03 power-on, four lifelines VCU/MCU/INV/M, arrows top-down:
(1) t=0: VCU -> MCU "wake torque disabled"
(2) t<50: MCU self "self-test ia/ib/ic Vdc"
(3) t=100: MCU -> INV "enable gate drivers, dead-time 1.5 μs"
(4) t=150: MCU self "verify Vdc 360 V nominal"
(5) t=200: MCU self "load modulation thresholds (0.907 / 0.952 / 1.000)"
(6) t=220: MCU self "load THD limit 8 %"
(7) t=250: VCU -> MCU "torque command allowed"
Title: "S03 OVERMODULATION — POWER-ON SEQUENCE". Thick MCU activation bar t=0..250 ms.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 7 arrows with time tags and threshold values
```

### T03 state machine（**P0 必修**）

```text
[image_id] IMG-S03-T03-r01
[priority] P0
[size] 1024x1024
[positive prompt]
Finite-state-machine diagram for S03 overmodulation control. Title bar text MUST be:
"S03 OVERMODULATION CONTROL — STATE MACHINE".
<r01 ENUM RULE>
STATES (exactly 6, 2x3 grid):
  top-left: "Linear SVPWM (m <= 0.907)"
  top-mid:  "Overmodulation Region 1 (0.907 < m <= 0.952)"
  top-right:"Overmodulation Region 2 (0.952 < m < 1.000)"
  bot-left: "Six-Step (m = 1.000)"
  bot-mid:  "Derate on THD limit (THD > 8 %)"
  bot-right:"Fallback to Linear"
EDGES (exactly 7, each label unique):
  "Linear SVPWM (m <= 0.907)" -> "Overmodulation Region 1 (0.907 < m <= 0.952)" : "voltage utilization rising"
  "Overmodulation Region 1 (0.907 < m <= 0.952)" -> "Overmodulation Region 2 (0.952 < m < 1.000)" : "deeper modulation index"
  "Overmodulation Region 2 (0.952 < m < 1.000)" -> "Six-Step (m = 1.000)" : "max voltage utilization"
  "Overmodulation Region 2 (0.952 < m < 1.000)" -> "Derate on THD limit (THD > 8 %)" : "THD limit hit"
  "Derate on THD limit (THD > 8 %)" -> "Fallback to Linear" : "NVH limit hit"
  "Fallback to Linear" -> "Linear SVPWM (m <= 0.907)" : "Vdc recovered"
  "Six-Step (m = 1.000)" -> "Derate on THD limit (THD > 8 %)" : "safety derate request"
Highlight "Derate on THD limit" and "Fallback to Linear" red.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
verify NO duplicate "voltage utilization rising" labels (r00 had this bug)
each state name includes its m-range in parentheses
[acceptance]
- 6 verbatim states with m-range
- 7 unique edge labels; no duplicates
```

### T04 PCB concept

```text
[image_id] IMG-S03-T04-r01
[priority] P1
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S03 inverter gate / PWM / EMC. Title bar:
"S03 OVERMODULATION — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Five groups:
(GATE DRIVE) "6-channel gate driver (1.5 μs dead-time)", "Desat protection",
"Negative bias rail"
(POWER) "DC-link capacitor bank (Vdc 360 V)", "Bus-bar interface"
(CURRENT SENSE) "ia/ib/ic shunt or hall (100 kSPS)", "Sample window aligned to PWM 10 kHz"
(EMC) "Common-mode choke", "Differential filter", "Snubber"
(SAFETY) "THD / NVH Monitor (THD <= 8 %)", "Modulation index telemetry"
<= 18 short signal tokens. Concept watermark top-right.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 groups verbatim; dead-time and switching frequency labels present
```

### T05 CAD packaging concept

```text
[image_id] IMG-S03-T05-r01
[priority] P1
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE illustration for S03 inverter power stage packaging.
Title: "S03 INVERTER POWER STAGE — CONCEPT PACKAGING (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Flat line illustration only: "Power Module (6 switches, peak 260 A)",
"DC-link Capacitor Bank (Vdc 360 V class)", "Bus-bars (Phase A/B/C)",
"Heatsink + Cold Plate (generic liquid cooling)", "EMC Shield Partition (dashed)",
"Snubber location". Generic material names only.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- flat line illustration; no metallic shading
- voltage / current annotations on capacitors and bus-bars
```

### T06 BOM tree

```text
[image_id] IMG-S03-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
Component family risk tree for S03. Title: "S03 OVERMODULATION — BOM / EDA RISK TREE".
Root "S03 svpwm_overmodulation_voltage_utilization".
FIXED risk pills:
- "Gate driver" -> HIGH (red, dead-time critical)
- "Power modules" -> HIGH (red, six-step thermal)
- "DC-link capacitors" -> MED (amber)
- "Bus-bar" -> LOW (green)
- "EMI components" -> MED (amber)
Leaves:
- Gate driver: "Half-bridge driver", "Desat protection IC", "Isolation"
- Power modules: "SiC MOSFET", "IGBT", "Diode"
- DC-link capacitors: "Film capacitor", "Electrolytic backup"
- Bus-bar: "Copper laminate", "Insulation sleeve"
- EMI components: "CMC", "DM filter", "Y-cap"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 branches with FIXED risk colors
```

### T07 verification tree

```text
[image_id] IMG-S03-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan tree for S03. Title: "S03 OVERMODULATION — VERIFICATION PLAN".
Root: "S03 svpwm_overmodulation verification".
Level-1 branches with placeholder DVP IDs (待 r03 锁定):
(S03-DV-001) "THD measurement (target <= 8 %)"
(S03-DV-002) "EMC compliance EN 55025 Class 5"
(S03-DV-003) "NVH torque ripple (target <= 3 %)"
(S03-DV-004) "Inverter loss vs modulation index sweep"
(S03-DV-005) "Thermal stress at six-step (junction T <= 150 C)"
Acceptance hook leaves keep numeric thresholds.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 verbatim DVP IDs with placeholder marker
- numeric thresholds present
```

### T08 protocol link

```text
[image_id] IMG-S03-T08-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Network block diagram for S03 protocol. Title: "S03 OVERMODULATION — PROTOCOL LINK".
Vertical chain: "VCU (CAN-FD 5 Mbit/s)" -> "MCU command parser" ->
"Modulation Mode Telemetry + THD / NVH Guard Channel" ->
"FOC id/iq controller" -> "SVPWM (10 kHz)" -> "3-phase Inverter".
Right branches: "UDS / XCP", "Calibration Tool".
Bus labels: VCU->MCU "CAN-FD 5 Mbit/s"; MCU->Guard "internal AXI 32-bit";
Guard->FOC "internal AXI 32-bit (m, THD)"; FOC->SVPWM "internal AXI 32-bit";
SVPWM->Inverter "PWM U/V/W (10 kHz)"; MCU<->UDS/XCP "CAN-FD + Ethernet";
Calibration->XCP "XCP-over-Ethernet TCP/IP".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all bus labels with explicit speeds
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S03-T01-r01 | P1 | [ ] | [ ] |
| IMG-S03-T02-r01 | P1 | [ ] | [ ] |
| IMG-S03-T03-r01 | **P0** | [ ] | [ ] |
| IMG-S03-T04-r01 | P1 | [ ] | [ ] |
| IMG-S03-T05-r01 | P1 | [ ] | [ ] |
| IMG-S03-T06-r01 | P2 | [ ] | [ ] |
| IMG-S03-T07-r01 | P2 | [ ] | [ ] |
| IMG-S03-T08-r01 | P2 | [ ] | [ ] |
