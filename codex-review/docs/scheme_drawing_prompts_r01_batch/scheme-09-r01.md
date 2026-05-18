# S09 r01 提示词批包 · winding_reconfiguration

修订日期：2026-05-18  
方案 ID：`winding_reconfiguration`  
工程目录：`engineering/v2/scheme-09/`（仅 README）  
所有 8 张图挂 research pool watermark。EXP-008 仅 Ke/Kt 静态缩放代理。

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S09 WINDING RECONFIGURATION — DRIVER BLOCK · RESEARCH POOL` |
| T02 | `S09 WINDING SWITCH — POWER-ON SEQUENCE · RESEARCH POOL` |
| T03 | `S09 WINDING RECONFIGURATION — STATE MACHINE · RESEARCH POOL` |
| T04 | `S09 SWITCH MATRIX — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)` |
| T05 | `S09 RECONFIGURABLE WINDING — CONCEPT LAYOUT (CONCEPT ONLY · RESEARCH POOL)` |
| T06 | `S09 WINDING SWITCH — BOM / EDA RISK TREE · RESEARCH POOL` |
| T07 | `S09 WINDING RECONFIG — VERIFICATION PLAN · RESEARCH POOL` |
| T08 | `S09 WINDING RECONFIG — PROTOCOL LINK · RESEARCH POOL` |

## 1. 生产参数（research pool placeholders）

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 切换状态数 | 2（A=星形 / B=三角形等价） | — | r01 估值 |
| Ke/Kt 配置 A | nominal | — | EXP-008 估值 |
| Ke/Kt 配置 B | nominal × 1.73 | — | EXP-008 估值（三角形等效） |
| Zero-torque window | 50-200 | ms | r01 估值 |
| 高压接触器额定电压 | 800 | V | r01 估值 |
| 高压接触器额定电流 | 300 | A | r01 估值 |
| 互锁验证延迟 | < 1 | ms | r01 估值 |
| 环流检测阈值 | 5 | A | r01 估值 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S09-T01-r01
[priority] P1
[size] 1792x1024
[positive prompt]
Flat block diagram for S09 winding reconfiguration. Title:
"S09 WINDING RECONFIGURATION — DRIVER BLOCK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Standard 5-block traction chain bottom. Between Inverter and Motor, INSERT
a switch matrix block: "Winding-Switch Matrix (Configuration A <-> B,
2 states, HV contactors 800 V / 300 A class)".
Top sub-block: "Interlock + Arc Suppression Controller" with state feedback
"State A/B feedback" to MCU.
Add "Zero-torque verification (< 1 ms latency)" inline before switch.
Add "Circulating current monitor (threshold 5 A)".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- switch matrix and interlock visible; thresholds present
```

### T02 sequence

```text
[image_id] IMG-S09-T02-r01
[priority] P1
[size] 1792x1024
[positive prompt]
UML sequence for S09 winding switch event. Title:
"S09 WINDING SWITCH — POWER-ON SEQUENCE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Lifelines: VCU, MCU, Switch Driver, Switch Matrix, Motor, Interlock Monitor.
Steps:
(1) VCU->MCU "request reconfig A -> B"
(2) MCU->Switch Driver "ramp torque to zero"
(3) MCU self "verify zero-torque window (50-200 ms, < 1 ms interlock check)"
(4) MCU->Switch Driver "command switch matrix B"
(5) Switch Matrix->Motor "winding now Configuration B"
(6) MCU<-Interlock Monitor "circulating current = 0 A (< 5 A threshold)"
(7) MCU->VCU "reconfig complete; Ke/Kt updated"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all 7 steps with thresholds
```

### T03 state machine

```text
[image_id] IMG-S09-T03-r01
[priority] P1
[size] 1024x1024
[positive prompt]
Finite-state-machine for S09. Title: "S09 WINDING RECONFIGURATION — STATE MACHINE · RESEARCH POOL".
<r01 ENUM RULE>
<r01 RESEARCH POOL WATERMARK>
STATES (exactly 6):
  "Configuration A (nominal Ke/Kt)"
  "Zero-torque window (50-200 ms)"
  "Switch in progress (< 1 ms interlock check)"
  "Configuration B (Ke/Kt × 1.73)"
  "Illegal-state fallback (manual recovery only)"
  "Circulating-current detected (threshold 5 A)"
EDGES (exactly 7):
  "Configuration A (nominal Ke/Kt)" -> "Zero-torque window (50-200 ms)" : "switch request"
  "Zero-torque window (50-200 ms)" -> "Switch in progress (< 1 ms interlock check)" : "zero-torque verified"
  "Switch in progress (< 1 ms interlock check)" -> "Configuration B (Ke/Kt × 1.73)" : "switch complete"
  "Switch in progress (< 1 ms interlock check)" -> "Illegal-state fallback (manual recovery only)" : "illegal state detected"
  "Switch in progress (< 1 ms interlock check)" -> "Circulating-current detected (threshold 5 A)" : "arc suppression triggered"
  "Circulating-current detected (threshold 5 A)" -> "Configuration A (nominal Ke/Kt)" : "current re-balanced"
  "Illegal-state fallback (manual recovery only)" -> "Configuration A (nominal Ke/Kt)" : "manual recovery only (service)"
Highlight "Illegal-state fallback" and "Circulating-current detected" red.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 6 states with thresholds in parentheses
- 7 unique edges
```

### T04 PCB concept

```text
[image_id] IMG-S09-T04-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S09 switch matrix. Title:
"S09 SWITCH MATRIX — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
Groups:
(SWITCH DRIVER) "HV contactor driver (800 V / 300 A class)", "Solid-state switch driver alternative", "Pre-charge / arc suppression"
(INTERLOCK) "Interlock logic (< 1 ms)", "Mutex with traction PWM"
(STATE FEEDBACK) "Config A/B feedback line", "Stuck-state detection"
(MONITOR) "Circulating current sensor (5 A threshold)", "Arc / open detection"
(SAFETY BACKUP) "Gate-disable backup path"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 groups with thresholds
```

### T05 CAD packaging concept

```text
[image_id] IMG-S09-T05-r01
[priority] P1
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE illustration of S09 reconfigurable winding layout.
Title: "S09 RECONFIGURABLE WINDING — CONCEPT LAYOUT (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
Flat line illustration only. Show:
- "Motor end-turn arrangement (generic copper)"
- "Reconfiguration switch placement (generic HV contactors, 800 V / 300 A)" as labeled rectangles
- "Insulation barriers (class H generic)" as dashed planes
- "Heat-path callouts" with arrows
- "Excitation harness routing" as gold polyline
- "Service access for contactor replacement"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- flat line only; no real grade names
```

### T06 BOM tree

```text
[image_id] IMG-S09-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
BOM risk tree for S09. Title: "S09 WINDING SWITCH — BOM / EDA RISK TREE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Root "S09 winding_reconfiguration".
FIXED:
- "Switches and drivers (HV contactors / SSR)" -> HIGH
- "Interlock electronics" -> HIGH
- "Harness and insulation (class H generic)" -> MED
- "Sensing for circulating current" -> MED
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 4 branches with FIXED risk
```

### T07 verification tree

```text
[image_id] IMG-S09-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S09. Title: "S09 WINDING RECONFIG — VERIFICATION PLAN · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Branches:
(S09-DV-001) "Switching transient (zero-torque window 50-200 ms verified)"
(S09-DV-002) "Circulating current (< 5 A threshold)"
(S09-DV-003) "Arc / insulation (no flashover at 800 V)"
(S09-DV-004) "Open / short / stuck fault behavior (illegal-state fallback < 1 ms)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 4 DVP IDs with numeric thresholds
```

### T08 protocol link

```text
[image_id] IMG-S09-T08-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Network block for S09. Title: "S09 WINDING RECONFIG — PROTOCOL LINK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Vertical chain: VCU -> MCU -> "Winding Configuration + Switch State Telemetry
(A/B state, circulating I, arc flag)" -> FOC -> SVPWM -> Switch Matrix -> Inverter -> Motor.
Bus labels explicit.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- telemetry parameters visible
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S09-T01-r01 | P1 | [ ] | [ ] |
| IMG-S09-T02-r01 | P1 | [ ] | [ ] |
| IMG-S09-T03-r01 | P1 | [ ] | [ ] |
| IMG-S09-T04-r01 | P2 | [ ] | [ ] |
| IMG-S09-T05-r01 | P1 | [ ] | [ ] |
| IMG-S09-T06-r01 | P2 | [ ] | [ ] |
| IMG-S09-T07-r01 | P2 | [ ] | [ ] |
| IMG-S09-T08-r01 | P2 | [ ] | [ ] |
