# S11 r01 提示词批包 · thermal_demag_safety_protection

修订日期：2026-05-18  
方案 ID：`thermal_demag_safety_protection`  
工程目录：`engineering/v2/scheme-11/`  
草案完整度：PCB / CAD / Controller / BOM / DVP&R 全  
依据：`V2-S11-PCB-safety_fault_latch-r00.md`、`V2-S11-CAD-thermal_sensor_cooling-r00.md`、`V2-S11-DVP-safety_fault_injection-r00.md`、`V2-S11-CTRL-safety_fault_state_machine-r00.drawio`

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S11 THERMAL / DEMAG / SAFETY SUPERVISOR — DRIVER BLOCK` |
| T02 | `S11 SAFETY SUPERVISOR — POWER-ON SEQUENCE` |
| T03 | `S11 SAFETY SUPERVISOR — STATE MACHINE` |
| T04 | `S11 SAFETY CHAIN — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S11 THERMAL / COOLING — CONCEPT BOUNDARY (CONCEPT ONLY)` |
| T06 | `S11 SAFETY CHAIN — BOM / EDA RISK TREE` |
| T07 | `S11 SAFETY SUPERVISOR — VERIFICATION PLAN` |
| T08 | `S11 SAFETY SUPERVISOR — PROTOCOL LINK` |

## 1. 生产参数

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| 磁钢温度 warning 阈值 | 100 | °C | r01 估值 |
| 磁钢温度 critical 阈值 | 120 | °C | r01 估值 |
| 绕组温度 warning | 140 | °C | r01 估值 |
| 绕组温度 critical | 160 | °C | r01 估值（class H） |
| 油温 warning | 80 | °C | r01 估值 |
| 油温 critical | 100 | °C | r01 估值 |
| Vdc 高 critical | 420 | V | r01 估值 |
| Vdc 低 critical | 240 | V | r01 估值 |
| id_min(T=25) | -240 | A | 同 S01 / r02 |
| temp_coefficient | -0.0035 | A/°C | 同 S01 / r02 |
| gate-disable 关断延迟目标 | < 100 | μs | r01 估值 |
| latch reset | 仅服务工具 | — | PCB 草案 |
| 传感器开短路检测 | < 1 | ms | PCB 草案 |
| DVP IDs | S11-DV-001..005 | — | DVP 草案 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S11-T01-r01
[priority] P1
[size] 1792x1024
[reference image] gpt-image-2/outputs/S11/V2-S11-ILL-T01-driver_block-r00.png
[positive prompt]
Flat technical block diagram for S11 thermal / demag / safety supervisor.
Title: "S11 THERMAL / DEMAG / SAFETY SUPERVISOR — DRIVER BLOCK".
Standard 5-block traction power-stage chain bottom.
Top right, highlighted sub-block: "Safety Supervisor (functional safety)" with
inputs from left (temperature sensors): "pm_temp (warning 100 °C, critical 120 °C)",
"winding_temp (warning 140 °C, critical 160 °C)",
"oil_temp (warning 80 °C, critical 100 °C)", "Vdc (240..420 V critical window)",
"current sensors", "rotor speed".
Supervisor outputs: "Gate Disable (to inverter, < 100 μs assertion)",
"Fault Status (to MCU / VCU)", "id_min(T) = -240 - 0.0035 × (T - 25) [A]" derate signal.
Show small latch icon "Latched fault — reset only by service".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all 3 temperature thresholds visible (pm/winding/oil with warning + critical)
- gate-disable < 100 μs and id_min formula visible
- latch icon present
```

### T02 sequence

```text
[image_id] IMG-S11-T02-r01
[priority] P1
[size] 1792x1024
[positive prompt]
UML sequence for S11 power-on and continuous safety monitoring. Title:
"S11 SAFETY SUPERVISOR — POWER-ON SEQUENCE".
Lifelines: VCU, MCU, Safety Supervisor, INV, M.
Steps:
(1) VCU->MCU "wake torque disabled"
(2) MCU->Safety Supervisor "self-test: all temperature sensors (pm/winding/oil), Vdc, current"
(3) Supervisor self "verify open / short detection within 1 ms"
(4) Supervisor->MCU "all sensors plausible"
(5) MCU->INV "enable gate drivers"
(6) Supervisor self continuous "monitor pm_temp < 120 °C, winding_temp < 160 °C, oil_temp < 100 °C, Vdc 240-420 V"
(7) On any critical: "Supervisor->INV gate-disable (< 100 μs)" -> "latch set" -> "MCU reads fault_reason"
(8) VCU->MCU "torque command allowed" (if all green)
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all threshold values present
- gate-disable < 100 μs latency visible
```

### T03 state machine

```text
[image_id] IMG-S11-T03-r01
[priority] P1
[size] 1024x1024
[reference image] gpt-image-2/outputs/S11/V2-S11-ILL-T03-state_machine-r00.png OR engineering/v2/scheme-11/controller/V2-S11-CTRL-safety_fault_state_machine-r00.drawio exported PNG
[positive prompt]
Finite-state-machine for S11 safety supervisor. Title:
"S11 SAFETY SUPERVISOR — STATE MACHINE".
<r01 ENUM RULE>
STATES (exactly 6):
  "Normal"
  "Thermal / demag warning (pm 100 °C / winding 140 °C / oil 80 °C)"
  "Active derating (id_min = -240 - 0.0035 × (T - 25) [A])"
  "Unknown sensor fallback (open / short < 1 ms)"
  "Hardware gate-disable (< 100 μs assertion)"
  "Latched fault (reset only by service)"
EDGES (exactly 7):
  "Normal" -> "Thermal / demag warning (pm 100 °C / winding 140 °C / oil 80 °C)" : "temperature rising"
  "Thermal / demag warning (pm 100 °C / winding 140 °C / oil 80 °C)" -> "Active derating (id_min = -240 - 0.0035 × (T - 25) [A])" : "derate trigger"
  "Active derating (id_min = -240 - 0.0035 × (T - 25) [A])" -> "Unknown sensor fallback (open / short < 1 ms)" : "sensor open / short"
  "Active derating (id_min = -240 - 0.0035 × (T - 25) [A])" -> "Hardware gate-disable (< 100 μs assertion)" : "critical threshold reached"
  "Unknown sensor fallback (open / short < 1 ms)" -> "Hardware gate-disable (< 100 μs assertion)" : "fallback elevated"
  "Hardware gate-disable (< 100 μs assertion)" -> "Latched fault (reset only by service)" : "latch set"
  "Latched fault (reset only by service)" -> "Normal" : "latch reset only by service"
Highlight "Active derating", "Unknown sensor fallback", "Hardware gate-disable",
"Latched fault" red.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
ensure node fill is pale blue hex #B6C7E0 (r00 was dark gray — off-baseline)
preserve every threshold inside state names verbatim
[acceptance]
- 6 states with embedded numeric thresholds
- 4 red-highlighted states
```

### T04 PCB concept

```text
[image_id] IMG-S11-T04-r01
[priority] P1
[size] 1024x1280
[reference image] gpt-image-2/outputs/S11/V2-S11-ILL-T04-pcb_sheet_concept-r00.png
[positive prompt]
Conceptual PCB sheet for S11 safety chain & fault latch. Title:
"S11 SAFETY CHAIN — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Set node fill to pale blue hex #B6C7E0 (r00 was dark gray).
Groups:
(SENSING) "pm_temp (NTC, redundant), warning 100 / critical 120 °C",
"winding_temp (PT1000), warning 140 / critical 160 °C",
"oil_temp (NTC), warning 80 / critical 100 °C", "Vdc sense (240-420 V window)"
(ISOLATION) "sensor isolation barrier", "LV / HV partition"
(CONTROL) "MCU safety task", "id_min(T) clamp logic", "fault classification readback"
(GATE DRIVE) "gate driver", "gate_disable_n hardware path (< 100 μs)"
(SAFETY LATCH) "fault latch logic (set, hold, service-only reset)",
"fault_reason map", "latch readback"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all 4 temperature / Vdc thresholds visible
- node fill pale blue (not gray)
- < 100 μs gate-disable label present
```

### T05 CAD packaging concept

```text
[image_id] IMG-S11-T05-r01
[priority] P1
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE illustration for S11 thermal sensor + cooling boundary.
Title: "S11 THERMAL / COOLING — CONCEPT BOUNDARY (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Flat line illustration only. Show:
- "Magnet temperature sensor mount (NTC, redundant, target near magnet hotspot)"
- "Winding temperature sensor (PT1000, in end-turn or slot)"
- "Oil / coolant temperature sensor (inlet + outlet)"
- "Controller heatsink interface (generic liquid cooling)"
- "Service access for sensor / harness replacement"
- "LV / HV keep-out partition (dashed gold plane)"
Use generic material categories only.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all 3 sensor mount families visible
- LV/HV partition
- concept watermark
```

### T06 BOM tree

```text
[image_id] IMG-S11-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
BOM risk tree for S11. Title: "S11 SAFETY CHAIN — BOM / EDA RISK TREE".
Root "S11 thermal_demag_safety_protection".
FIXED:
- "Temperature sensors (NTC / PT1000)" -> MED
- "Safety latch (SR latch + service-only reset)" -> HIGH
- "Gate-disable hardware" -> HIGH
- "Isolation parts (sensor / latch / driver)" -> MED
- "Fault feedback chain" -> MED
Leaves use generic family names only.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 branches with FIXED risk
```

### T07 verification tree

```text
[image_id] IMG-S11-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S11. Title: "S11 SAFETY SUPERVISOR — VERIFICATION PLAN".
Root: "S11 thermal_demag_safety_protection verification".
Level-1 branches with verbatim DVP IDs from V2-S11-DVP-safety_fault_injection-r00.md
(NOT TST-THM-001 etc. used in r00):
(S11-DV-001) "Thermal warning / critical thresholds (pm 100/120, winding 140/160, oil 80/100 °C)"
(S11-DV-002) "Sensor open / short (< 1 ms detection)"
(S11-DV-003) "Demag margin low (id_min = -240 - 0.0035 × (T - 25))"
(S11-DV-004) "Gate-disable assertion (< 100 μs)"
(S11-DV-005) "Fault reason traceability (DTC + log binding)"
Leaves keep numeric thresholds.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- DVP IDs verbatim from source markdown (NOT TST-xxx)
- numeric thresholds present
```

### T08 protocol link

```text
[image_id] IMG-S11-T08-r01
[priority] P1
[size] 1024x1280
[positive prompt]
Network block for S11. Title: "S11 SAFETY SUPERVISOR — PROTOCOL LINK".
Vertical chain: VCU CAN-FD -> MCU -> "Safety Fault Classification + Latch State Telemetry
(DTCs S11-DTC-THERMAL, S11-DTC-DEMAG, S11-DTC-SENSOR-FAULT, S11-DTC-LATCH)" ->
FOC -> SVPWM -> Inverter.
Right branches: Safety Supervisor (independent HW path) -> Gate Drivers
(< 100 μs gate-disable), UDS/XCP + Calibration.
Bus labels explicit (no Internal Bus placeholder).
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all DTC names verbatim
- < 100 μs gate-disable path visible
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S11-T01-r01 | P1 | [ ] | [ ] |
| IMG-S11-T02-r01 | P1 | [ ] | [ ] |
| IMG-S11-T03-r01 | P1 | [ ] | [ ] |
| IMG-S11-T04-r01 | P1 | [ ] | [ ] |
| IMG-S11-T05-r01 | P1 | [ ] | [ ] |
| IMG-S11-T06-r01 | P2 | [ ] | [ ] |
| IMG-S11-T07-r01 | P2 | [ ] | [ ] |
| IMG-S11-T08-r01 | P1 | [ ] | [ ] |
