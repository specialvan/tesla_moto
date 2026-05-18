# S10 r01 提示词批包 · multiphase_phase_group_control

修订日期：2026-05-18  
方案 ID：`multiphase_phase_group_control`  
工程目录：`engineering/v2/scheme-10/`（仅 README）  
所有 8 张图挂 research pool watermark。EXP-009 仅可用电流降额代理。

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S10 MULTIPHASE / PHASE-GROUP CONTROL — DRIVER BLOCK · RESEARCH POOL` |
| T02 | `S10 MULTIPHASE — POWER-ON SEQUENCE · RESEARCH POOL` |
| T03 | `S10 PHASE-GROUP FAULT ALLOCATOR — STATE MACHINE · RESEARCH POOL` |
| T04 | `S10 MULTIPHASE INVERTER — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)` |
| T05 | `S10 PHASE-GROUP PACKAGING — CONCEPT (CONCEPT ONLY · RESEARCH POOL)` |
| T06 | `S10 MULTIPHASE — BOM / EDA RISK TREE · RESEARCH POOL` |
| T07 | `S10 MULTIPHASE FAULT TOLERANCE — VERIFICATION PLAN · RESEARCH POOL` |
| T08 | `S10 MULTIPHASE — PROTOCOL LINK · RESEARCH POOL` |

## 1. 生产参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 相数 | 6（双 3-phase 相组） | — | r01 估值 |
| Per-phase 峰值电流 | 130 | A | r01 估值（双组共 260 A） |
| 故障检测窗 | < 2 | ms | r01 估值 |
| 谐波子空间维度 | 2 | — | r01 估值（αβ + xy） |
| 单相故障 derate | 50 | % | r01 估值（双 3-phase） |
| 相组故障 derate | 100 | %（shut down） | r01 估值 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S10-T01-r01
[priority] P1
[size] 1792x1024
[positive prompt]
Flat block diagram for S10 multiphase / phase-group control. Title:
"S10 MULTIPHASE / PHASE-GROUP CONTROL — DRIVER BLOCK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Power-stage: "Battery / DC link (Vdc 360 V)" -> "Precharge + Main Contactor" ->
"Multiphase Inverter (6 phases, per-phase peak 130 A)" ->
"6-phase Motor (dual 3-phase groups)".
Per-phase-group current sensing: "Group A: ia1/ib1/ic1", "Group B: ia2/ib2/ic2".
Top sub-block: "Fault Torque Allocator + Harmonic Subspace Controller
(detection < 2 ms, αβ + xy subspaces)".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- both phase groups visible; harmonic subspace label present
```

### T02 sequence

```text
[image_id] IMG-S10-T02-r01
[priority] P1
[size] 1792x1024
[positive prompt]
UML sequence for S10 power-on with phase-group fault handling. Title:
"S10 MULTIPHASE — POWER-ON SEQUENCE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Lifelines: VCU, MCU, Group A Driver, Group B Driver, Motor, Allocator.
Steps include parallel enable of both groups, per-group current self-test
(130 A peak), harmonic subspace init (αβ + xy), allocator readiness,
"injected single-phase fault scenario" with "derate 50 %" response within
< 2 ms detection.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- parallel group enable steps visible
```

### T03 state machine

```text
[image_id] IMG-S10-T03-r01
[priority] P1
[size] 1024x1024
[positive prompt]
Finite-state-machine for S10. Title: "S10 PHASE-GROUP FAULT ALLOCATOR — STATE MACHINE · RESEARCH POOL".
<r01 ENUM RULE>
<r01 RESEARCH POOL WATERMARK>
STATES (exactly 5):
  "Healthy multiphase (both groups, peak 130 A each)"
  "Single-phase fault (detection < 2 ms)"
  "Phase-group fault (detection < 2 ms)"
  "Derate via torque allocator (50 % single, 100 % group)"
  "Shut down (manual recovery only)"
EDGES (exactly 6):
  "Healthy multiphase (both groups, peak 130 A each)" -> "Single-phase fault (detection < 2 ms)" : "phase fault detected"
  "Healthy multiphase (both groups, peak 130 A each)" -> "Phase-group fault (detection < 2 ms)" : "group fault detected"
  "Single-phase fault (detection < 2 ms)" -> "Derate via torque allocator (50 % single, 100 % group)" : "derate request"
  "Phase-group fault (detection < 2 ms)" -> "Derate via torque allocator (50 % single, 100 % group)" : "derate request"
  "Derate via torque allocator (50 % single, 100 % group)" -> "Shut down (manual recovery only)" : "thermal limit"
  "Single-phase fault (detection < 2 ms)" -> "Healthy multiphase (both groups, peak 130 A each)" : "fault cleared (no Shut down -> Healthy path)"
Highlight "Phase-group fault" and "Shut down" red.
IMPORTANT: there is NO arrow from "Shut down" back to "Healthy multiphase".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- "fault cleared" only originates from Single-phase fault, NOT Shut down
- numeric thresholds embedded
```

### T04 PCB concept

```text
[image_id] IMG-S10-T04-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S10 multiphase inverter. Title:
"S10 MULTIPHASE INVERTER — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
Groups:
(POWER STAGES) "Multiphase inverter stage Group A (3 phases, 130 A)",
"Multiphase inverter stage Group B (3 phases, 130 A)"
(SENSING) "Per-phase current sense Group A", "Per-phase current sense Group B"
(ISOLATION) "Isolation barriers between groups"
(SWITCHES) "Phase-cutoff contactors", "Per-group disable line"
(CONNECTORS) "6-phase output interface"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- per-group blocks with 130 A label
```

### T05 CAD packaging concept

```text
[image_id] IMG-S10-T05-r01
[priority] P1
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE illustration for S10 phase-group packaging.
Title: "S10 PHASE-GROUP PACKAGING — CONCEPT (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
Flat line illustration only. Show:
- "Multiphase motor terminal layout (6 terminals, group A vs B color tags)"
- "Harness with per-phase routing (generic copper)"
- "Phase-group packaging boundary (dashed)"
- "Thermal path per group (generic cooling)"
- "Service access for per-group disconnect"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 6 terminals visible; group labels A/B
```

### T06 BOM tree

```text
[image_id] IMG-S10-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
BOM risk tree for S10. Title: "S10 MULTIPHASE — BOM / EDA RISK TREE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Root "S10 multiphase_phase_group_control".
FIXED:
- "Multiphase power modules (2 × 3-phase, 130 A each)" -> HIGH
- "Sensing chain (per-phase, < 2 ms detection)" -> HIGH
- "Connectors (6-phase)" -> MED
- "Harness (per-phase routing)" -> MED
- "Isolation (inter-group)" -> HIGH
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 branches with FIXED risk
```

### T07 verification tree

```text
[image_id] IMG-S10-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S10. Title: "S10 MULTIPHASE FAULT TOLERANCE — VERIFICATION PLAN · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Branches:
(S10-DV-001) "Single-phase fault detection (< 2 ms, derate 50 %)"
(S10-DV-002) "Phase-group fault detection (< 2 ms, shut down)"
(S10-DV-003) "Harmonic subspace (αβ + xy decoupled)"
(S10-DV-004) "Thermal (per-group thermal balance)"
(S10-DV-005) "NVH under fault (torque ripple bounded)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 DVP IDs with numeric thresholds
```

### T08 protocol link

```text
[image_id] IMG-S10-T08-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Network block for S10. Title: "S10 MULTIPHASE — PROTOCOL LINK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Vertical chain: VCU -> MCU -> "Phase Health + Harmonic Subspace Telemetry
(6 channels health, αβ + xy)" -> FOC -> SVPWM (per-group) ->
"Multiphase Inverter Group A" + "Multiphase Inverter Group B".
Bus labels explicit.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- per-group inverters drawn separately
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S10-T01-r01 | P1 | [ ] | [ ] |
| IMG-S10-T02-r01 | P1 | [ ] | [ ] |
| IMG-S10-T03-r01 | P1 | [ ] | [ ] |
| IMG-S10-T04-r01 | P2 | [ ] | [ ] |
| IMG-S10-T05-r01 | P1 | [ ] | [ ] |
| IMG-S10-T06-r01 | P2 | [ ] | [ ] |
| IMG-S10-T07-r01 | P2 | [ ] | [ ] |
| IMG-S10-T08-r01 | P2 | [ ] | [ ] |
