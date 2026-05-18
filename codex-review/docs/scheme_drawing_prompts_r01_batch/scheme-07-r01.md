# S07 r01 提示词批包 · variable_magnetization_memory_motor

修订日期：2026-05-18  
方案 ID：`variable_magnetization_memory_motor`  
工程目录：`engineering/v2/scheme-07/`（仅 README）  
**所有 8 张图必须挂 research pool watermark**（`_globals.md` §1.6）。  
外部 review-pr：`psi_f` 缩放不能代理硬件。

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S07 VARIABLE MAGNETIZATION (MEMORY MOTOR) — DRIVER BLOCK · RESEARCH POOL` |
| T02 | `S07 MAGNETIZATION PULSE — POWER-ON SEQUENCE · RESEARCH POOL` |
| T03 | `S07 MAGNETIZATION STATE MACHINE · RESEARCH POOL` |
| T04 | `S07 PULSE DRIVER — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)` |
| T05 | `S07 MEMORY MOTOR MAGNETIC PATH — CONCEPT (CONCEPT ONLY · RESEARCH POOL)` |
| T06 | `S07 MEMORY MOTOR — BOM / EDA RISK TREE · RESEARCH POOL` |
| T07 | `S07 MAGNETIZATION STATE — VERIFICATION PLAN · RESEARCH POOL` |
| T08 | `S07 MEMORY MOTOR — PROTOCOL LINK · RESEARCH POOL` |

## 1. 生产参数（research pool placeholders）

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 磁化脉冲电压 | 800 | V | r01 估值 |
| 磁化脉冲峰值电流 | 1000 | A | r01 估值 |
| 脉冲持续时间 | 50 | μs | r01 估值 |
| 储能电容能量 | 100 | J | r01 估值 |
| 磁状态分辨率 | 8 | 级 | r01 估值 |
| 寿命循环上限 | 10 000 | 次 | r01 估值 |
| 互锁验证延迟 | < 1 | ms | r01 估值 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S07-T01-r01
[priority] P1
[size] 1792x1024
[positive prompt]
Flat technical block diagram for S07 variable magnetization memory motor.
Title bar: "S07 VARIABLE MAGNETIZATION (MEMORY MOTOR) — DRIVER BLOCK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Standard 5-block power-stage chain. ABOVE the traction power chain, add a SECOND parallel sub-system:
"Magnetization Pulse Driver Bank (capacitor energy 100 J, pulse 800 V / 1000 A peak / 50 μs)" with
"Bi-directional pulse driver" feeding "Magnetization coil (research-pool topology)" inside motor.
Add "Interlock + traction inverter mutex (< 1 ms verification)" between the pulse path and the traction path.
Show "Flux state observer (8-level resolution)" feeding back to MCU.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- pulse parameters and interlock visible
- research pool watermark
```

### T02 sequence

```text
[image_id] IMG-S07-T02-r01
[priority] P1
[size] 1792x1024
[positive prompt]
UML sequence for S07 magnetization pulse cycle (NOT traction power-on).
Title: "S07 MAGNETIZATION PULSE — POWER-ON SEQUENCE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Lifelines: VCU, MCU, Pulse Driver, Energy Bank, Motor, Flux Observer.
Steps:
(1) VCU->MCU "request flux state change to target N"
(2) MCU->Energy Bank "pre-charge to 800 V (target energy 100 J)"
(3) Energy Bank->MCU "bank ready"
(4) MCU->Pulse Driver "trigger magnetization pulse 1000 A peak / 50 μs"
(5) Pulse Driver->Motor "pulse applied"
(6) Motor->Flux Observer "magnetic state settles"
(7) Flux Observer->MCU "state observed = N"
(8) MCU->VCU "state change confirmed; lifetime cycle ++"
Include "Safety interlock check" thick arrow gating step (4).
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- pulse / energy / state parameters present
- interlock visible
```

### T03 state machine（**P1 必修**，修正 r00 self-loop bug）

```text
[image_id] IMG-S07-T03-r01
[priority] P1
[size] 1024x1024
[positive prompt]
Finite-state-machine for S07 magnetization state. Title:
"S07 MAGNETIZATION STATE MACHINE · RESEARCH POOL".
<r01 ENUM RULE>
<r01 RESEARCH POOL WATERMARK>
STATES (exactly 7):
  "Magnetization idle"
  "Pre-charge energy bank (target 100 J at 800 V)"
  "Apply magnetization pulse (+pulse, 1000 A / 50 μs)"
  "Apply de-magnetization pulse (-pulse, 1000 A / 50 μs)"
  "Verify flux state (8-level resolution)"
  "Unknown-state fallback"
  "Lifetime cycle count update (limit 10000)"
EDGES (exactly 9, no duplicates, no extra self-loops):
  "Magnetization idle" -> "Pre-charge energy bank (target 100 J at 800 V)" : "bank ready request"
  "Pre-charge energy bank (target 100 J at 800 V)" -> "Apply magnetization pulse (+pulse, 1000 A / 50 μs)" : "pulse trigger up"
  "Pre-charge energy bank (target 100 J at 800 V)" -> "Apply de-magnetization pulse (-pulse, 1000 A / 50 μs)" : "pulse trigger down"
  "Apply magnetization pulse (+pulse, 1000 A / 50 μs)" -> "Verify flux state (8-level resolution)" : "pulse complete"
  "Apply de-magnetization pulse (-pulse, 1000 A / 50 μs)" -> "Verify flux state (8-level resolution)" : "pulse complete"
  "Verify flux state (8-level resolution)" -> "Lifetime cycle count update (limit 10000)" : "state observed ok"
  "Verify flux state (8-level resolution)" -> "Unknown-state fallback" : "state unknown"
  "Unknown-state fallback" -> "Magnetization idle" : "safe retreat"
  "Lifetime cycle count update (limit 10000)" -> "Magnetization idle" : "cycle limit reached"
Highlight "Unknown-state fallback" red.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 7 states; pulse energy and limit visible
- NO duplicate safe retreat self-loop (r00 had this)
```

### T04 PCB concept

```text
[image_id] IMG-S07-T04-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S07 pulse driver. Title:
"S07 PULSE DRIVER — CONCEPT PCB SHEET (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
Groups:
(ENERGY) "Pulse capacitor bank (100 J, 800 V class)", "Pre-charge resistor"
(DRIVER) "Bi-directional pulse driver (1000 A peak)", "Isolation gate path"
(SENSE) "Pulse current sensor (1000 A range)", "Bank voltage monitor"
(INTERLOCK) "Mutex with traction inverter (< 1 ms)", "Safe-state monitor"
(STATE) "Flux state observer interface (8-level)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 groups with pulse parameters
- both watermarks present
```

### T05 CAD packaging concept（**P0 BLOCKER 重做**）

```text
[image_id] IMG-S07-T05-r01
[priority] P0 BLOCKER
[size] 1280x1024
[positive prompt]
Conceptual isometric LINE illustration for S07 memory motor magnetic path.
Title: "S07 MEMORY MOTOR MAGNETIC PATH — CONCEPT (CONCEPT ONLY · RESEARCH POOL)".
<r01 CONCEPT WATERMARK>
<r01 RESEARCH POOL WATERMARK>
FORBID: M235-35A, 35PN440, SmCo, NdFeB, real dimensions in mm,
photorealistic 3D motor render, surface shading, metallic reflection.
Show as flat line illustration only:
- Rotor cross-section labeled "Rotor with memory magnet pockets (generic permanent magnets, mix of low-coercivity and high-coercivity types)"
- Magnetization path drawn as dashed arrows labeled "Magnetization flux path (pulse direction +/-)"
- Stator winding outline labeled "3-phase winding (generic copper)"
- A small thermal callout "Magnet T < 120 °C operational"
- A small interlock callout "Mutex with traction loop"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- NO real material names anywhere
- NO 3D shading
- both watermarks
- pulse direction arrows visible
```

### T06 BOM tree

```text
[image_id] IMG-S07-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
BOM risk tree for S07. Title: "S07 MEMORY MOTOR — BOM / EDA RISK TREE · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Root "S07 variable_magnetization_memory_motor".
FIXED:
- "Pulse power stage (driver, switches)" -> HIGH
- "Energy storage (cap bank, pre-charge)" -> HIGH
- "Magnet materials (generic)" -> MED
- "Flux state observers (sensors)" -> HIGH
- "Safety isolation (mutex hardware)" -> HIGH
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 branches, all HIGH or MED (research pool, treat conservatively)
```

### T07 verification tree

```text
[image_id] IMG-S07-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S07. Title: "S07 MAGNETIZATION STATE — VERIFICATION PLAN · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Branches (placeholder DVP IDs):
(S07-DV-001) "Magnetization / de-magnetization pulse (1000 A / 50 μs / 800 V)"
(S07-DV-002) "State retention (8-level resolution, retention > 72 h)"
(S07-DV-003) "Temperature drift (magnet T 25-120 °C)"
(S07-DV-004) "Unknown-state fallback (safe retreat < 1 ms)"
(S07-DV-005) "Lifetime cycling (10000 cycles)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- pulse parameters and cycle limit verbatim
```

### T08 protocol link

```text
[image_id] IMG-S07-T08-r01
[priority] P1
[size] 1024x1280
[positive prompt]
Network block for S07. Title: "S07 MEMORY MOTOR — PROTOCOL LINK · RESEARCH POOL".
<r01 RESEARCH POOL WATERMARK>
Vertical chain: VCU -> MCU -> "Flux State + Lifetime Cycle Counter Telemetry
(state 0-7, lifetime 0-10000)" -> FOC -> SVPWM -> Inverter.
Parallel chain: MCU -> "Pulse Driver Controller" -> "Energy Bank".
Right branches: UDS/XCP + Calibration.
Bus labels explicit.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- flux state telemetry values visible
- both pulse + traction paths drawn
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S07-T01-r01 | P1 | [ ] | [ ] |
| IMG-S07-T02-r01 | P1 | [ ] | [ ] |
| IMG-S07-T03-r01 | P1 | [ ] | [ ] |
| IMG-S07-T04-r01 | P2 | [ ] | [ ] |
| IMG-S07-T05-r01 | **P0 BLOCKER** | [ ] | [ ] |
| IMG-S07-T06-r01 | P2 | [ ] | [ ] |
| IMG-S07-T07-r01 | P2 | [ ] | [ ] |
| IMG-S07-T08-r01 | P1 | [ ] | [ ] |
