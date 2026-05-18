# S08 r01 提示词批包 · hybrid_excitation

修订日期：2026-05-18  
方案 ID：`hybrid_excitation`  
工程目录：`engineering/v2/scheme-08/`（仅 README）  
所有 8 张图挂 research pool watermark。EXP-007 仅 `psi_eff` 代理。

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S08 HYBRID EXCITATION — DRIVER BLOCK · RESEARCH POOL` |
| T02 | `S08 FIELD EXCITATION — POWER-ON SEQUENCE · RESEARCH POOL` |
| T03 | `S08 HYBRID EXCITATION — STATE MACHINE · RESEARCH POOL` |
| T04 | `S08 FIELD CONVERTER — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)` |
| T05 | `S08 FIELD WINDING PACKAGE — CONCEPT (CONCEPT ONLY · RESEARCH POOL)` |
| T06 | `S08 FIELD EXCITATION — BOM / EDA RISK TREE · RESEARCH POOL` |
| T07 | `S08 HYBRID EXCITATION — VERIFICATION PLAN · RESEARCH POOL` |
| T08 | `S08 HYBRID EXCITATION — PROTOCOL LINK · RESEARCH POOL` |

## 1. 生产参数（research pool placeholders）

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 励磁 DC/DC 输出 | 48 | V | r01 估值（low-side field winding） |
| 励磁电流 if 范围 | [-20, +30] | A | r01 估值 |
| psi_eff range | 0.02-0.10 | Wb | r01 估值（PM + field 合成） |
| Loss-of-field 检测窗 | < 5 | ms | r01 估值 |
| 励磁绕组绝缘等级 | H | — | r01 工程占位 |
| 励磁绕组冷却 | 油冷或液冷 | — | r01 估值 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S08-T01-r01
[priority] P1
[size] 1792x1024
[positive prompt]
Flat block diagram for S08 hybrid excitation. Title:
"S08 HYBRID EXCITATION — DRIVER BLOCK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Standard 5-block traction power-stage chain on bottom. ABOVE, add parallel field
excitation chain: "12 V battery (auxiliary)" -> "Field DC/DC Converter (48 V output)" ->
"Field current sense (if range -20..+30 A)" -> "Field winding (generic copper)" -> "Hybrid PMSM rotor".
Add "Loss-of-field detector (<5 ms detection window)" feeding back to MCU.
Top sub-block: "Three-variable Control (id, iq, if) with psi_eff 0.02-0.10 Wb".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- both traction and field chains visible
- numeric ranges present
```

### T02 sequence

```text
[image_id] IMG-S08-T02-r01
[priority] P1
[size] 1792x1024
[positive prompt]
UML sequence for S08 power-on with field excitation. Title:
"S08 FIELD EXCITATION — POWER-ON SEQUENCE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Lifelines: VCU, MCU, Traction INV, Field DC/DC, Field Winding, Motor.
Steps include:
(1) standard traction precharge
(2) MCU->Field DC/DC "enable field converter (48 V)"
(3) MCU->Field DC/DC "ramp if to reference (-20..+30 A)"
(4) MCU self "verify psi_eff via observer 0.02-0.10 Wb"
(5) "monitor loss-of-field (<5 ms)" continuous
(6) VCU->MCU "torque command allowed"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- field DC/DC ramp + loss-of-field monitor visible
```

### T03 state machine（**P0 必修**，修正 r00 箭头方向）

```text
[image_id] IMG-S08-T03-r01
[priority] P0
[size] 1024x1024
[positive prompt]
Finite-state-machine for S08. Title: "S08 HYBRID EXCITATION — STATE MACHINE · RESEARCH POOL".
<r01 ENUM RULE>
<r01 RESEARCH POOL WATERMARK>
STATES (exactly 5):
  "Field excitation idle"
  "Field excitation active (48 V)"
  "Three-variable control (id, iq, if)"
  "Loss-of-field detected (< 5 ms)"
  "Fallback to PM-only operation (psi_eff = psi_pm only)"
EDGES (exactly 6, unique; correct r00 directional errors):
  "Field excitation idle" -> "Field excitation active (48 V)" : "field DC/DC enable"
  "Field excitation active (48 V)" -> "Three-variable control (id, iq, if)" : "if reference set"
  "Three-variable control (id, iq, if)" -> "Three-variable control (id, iq, if)" : "optimization step (self-loop allowed)"
  "Three-variable control (id, iq, if)" -> "Loss-of-field detected (< 5 ms)" : "loss-of-field flag"
  "Loss-of-field detected (< 5 ms)" -> "Fallback to PM-only operation (psi_eff = psi_pm only)" : "field unavailable"
  "Fallback to PM-only operation (psi_eff = psi_pm only)" -> "Field excitation idle" : "recover"
Highlight "Loss-of-field detected" and "Fallback to PM-only operation" red.
IMPORTANT: "if reference set" MUST point Active -> Three-variable (NOT to Loss-of-field).
IMPORTANT: "recover" MUST point Fallback -> Idle (NOT to Three-variable).
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- arrow directions match r01 spec verbatim (r00 had errors)
- numeric parameters visible
```

### T04 PCB concept

```text
[image_id] IMG-S08-T04-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S08 field converter. Title:
"S08 FIELD CONVERTER — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
Groups:
(POWER) "Field DC/DC converter (48 V output, bi-directional)"
(SENSE) "Field current sense (-20..+30 A range)", "Field bank voltage monitor"
(DETECT) "Loss-of-field detector (< 5 ms)", "psi_eff observer interface"
(ISOLATION) "Isolation between field and traction (galvanic)"
(PROTECT) "Over-excitation protection", "Field thermal monitor"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- numeric ranges in sense and detect groups
```

### T05 CAD packaging concept（**P0 BLOCKER 重做**）

```text
[image_id] IMG-S08-T05-r01
[priority] P0 BLOCKER
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE illustration of S08 field winding package.
Title: "S08 FIELD WINDING PACKAGE — CONCEPT (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
FORBID: photorealistic 3D motor, brushless exciter render, real material grades.
Show as FLAT LINE only:
- Rotor cross-section labeled "Rotor with field winding on stator side (generic copper, insulation class H)"
- "Brushless exciter (generic, illustration only)" as labeled boxes
- "Slip-ring alternative (research-pool option, not chosen)" as ghosted dashed boxes
- "Cooling interface for field winding (generic liquid jacket)"
- "Insulation barrier (class H)" callout
- "Excitation harness routing" as gold polyline
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- flat line illustration only
- NO real material grade names
- both watermarks
```

### T06 BOM tree

```text
[image_id] IMG-S08-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
BOM risk tree for S08. Title: "S08 FIELD EXCITATION — BOM / EDA RISK TREE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Root "S08 hybrid_excitation".
FIXED:
- "Field power devices (DC/DC, switches)" -> HIGH
- "Field winding (generic copper, class H insulation)" -> MED
- "Insulation system (generic class H)" -> HIGH
- "Connectors / harness" -> MED
- "Excitation sensors (current, temp)" -> MED
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 branches with FIXED risk
```

### T07 verification tree

```text
[image_id] IMG-S08-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S08. Title: "S08 HYBRID EXCITATION — VERIFICATION PLAN · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Branches:
(S08-DV-001) "Field thermal stress (winding T < 180 °C, class H)"
(S08-DV-002) "Loss-of-field detection (< 5 ms)"
(S08-DV-003) "Three-variable optimization (id/iq/if pareto)"
(S08-DV-004) "Bench correlation (psi_eff measured vs predicted)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 4 placeholder DVP IDs with numeric thresholds
```

### T08 protocol link

```text
[image_id] IMG-S08-T08-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Network block for S08. Title: "S08 HYBRID EXCITATION — PROTOCOL LINK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Vertical chain: VCU -> MCU -> "Field Current + Loss-of-Field Telemetry
(if -20..+30 A, detection < 5 ms)" -> FOC -> SVPWM -> Inverter.
Parallel chain: MCU -> "Field DC/DC Controller" -> "Field winding".
Bus labels explicit.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- both chains visible; telemetry parameters present
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S08-T01-r01 | P1 | [ ] | [ ] |
| IMG-S08-T02-r01 | P1 | [ ] | [ ] |
| IMG-S08-T03-r01 | **P0** | [ ] | [ ] |
| IMG-S08-T04-r01 | P2 | [ ] | [ ] |
| IMG-S08-T05-r01 | **P0 BLOCKER** | [ ] | [ ] |
| IMG-S08-T06-r01 | P2 | [ ] | [ ] |
| IMG-S08-T07-r01 | P2 | [ ] | [ ] |
| IMG-S08-T08-r01 | P2 | [ ] | [ ] |
