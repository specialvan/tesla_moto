# 12 方案图纸 r01 提示词目录

修订日期：2026-05-18
基线版本：r00（`codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18.md`）
评审依据：`claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md`
生成工具：`gpt-image-2`（fallback：`gpt-image-1` / `dall-e-3`）

---

## 0. 与 r00 的关系

1. r01 提示词只迭代 r00 评审中 P0/P1 级问题；P2 级（密度、装饰）允许保留 r00 出图。
2. r01 prompt 落地后产出图按 `V2-SXX-ILL-TYY-...-r01.png` 命名，与 r00 共存于 `gpt-image-2/outputs/SXX/`，不覆盖 r00。
3. r01 不修改任何 `.drawio` / mermaid / markdown 草案；语义改动必须先回到草案源。
4. r01 同样适用"概念示意 / 评审可视化"边界；不会把 `engineering_validated` 改成 `true`。

---

## 1. 全局基线升级（r01-GLOBAL）

### 1.1 r01 正向风格 token（追加到每条 prompt 末尾，替代 r00 §1.1）

```text
technical engineering schematic, flat infographic style, clean vector look,
single solid dark navy background hex #0B1A33, no gradient, no texture,
node fills pale blue hex #B6C7E0 with gold strokes hex #D8A638,
labels in crisp sans-serif white hex #F2F2F2 and gold hex #D8A638,
fault and safety states use red-tinted stroke hex #C0392B,
high contrast, orthogonal connectors only, no diagonal lines,
professional automotive powertrain documentation aesthetic, single image,
title bar text MUST be: "<SCHEME_TITLE>", do NOT add any other title
```

### 1.2 r01 负向 prompt（扩展 r00 §1.2）

```text
photorealistic faces, glamour photography, marketing render, watercolor,
cartoon mascots, anime style, low contrast, blurry, motion blur, lens flare,
busy decorative background, fake measurement units, hand-drawn sketch noise,
chinese calligraphy stroke, emoji, watermark icon, manufacturer logo,
real manufacturer parts, real component photos,
specific steel grades, specific magnet grades, specific copper grades,
M270-35A, 35PN440, ADC12, C11000, SmCo, NdFeB, FR-4, real material designations,
real engineering dimensions in mm, real torque or current numeric callouts,
photorealistic 3D motor cross-section, metallic shading, surface reflection,
shadow casting, depth-of-field blur, decorative trophy or icon flourishes,
generic title "MOTOR CONTROLLER SUBSYSTEM" when scheme is not a motor controller,
duplicated arrow labels on different edges,
self-loop arrows that do not return to a different state,
missing transition labels
```

### 1.3 r01 模板尺寸覆盖（建议落入 `gpt-image-2/prompts/schemes.json`）

| 模板 | r00 默认 | r01 建议 | 理由 |
|---|---|---|---|
| T01 driver block | 1024×1024 | 1792×1024 | 左右链路长，prompt 已要求 16:9 |
| T02 power-on sequence | 1024×1024 | 1792×1024 | 多 lifeline + 8 信令，需要横向呼吸 |
| T03 state machine | 1024×1024 | 1024×1024 | 6 状态 2×3 网格保持 1:1 |
| T04 PCB sheet | 1024×1024 | 1024×1280 | 多功能组左右 + 信号名垂直补齐 |
| T05 CAD packaging | 1024×1024 | 1280×1024 | 等轴侧视图需要横向 |
| T06 BOM tree | 1024×1024 | 1024×1024 | 树状自上而下 |
| T07 verification tree | 1024×1024 | 1792×1024 | 左到右树 |
| T08 protocol link | 1024×1024 | 1024×1280 | 主链垂直 + 旁路诊断 |

### 1.4 r01 显式枚举规则（应用到 T03/T07 等图）

```text
You MUST render EXACTLY N states (or nodes) listed below, no more, no less.
You MUST render EXACTLY M directed edges listed below, no more, no less.
Each edge MUST carry its label text verbatim, in English.
Do NOT add a self-loop unless explicitly listed.
Do NOT duplicate a label on multiple edges.
Highlight nodes whose label contains "Fault", "Fallback", "Shut down",
"Latched", or "Unknown" with a red-tinted stroke hex #C0392B.
```

### 1.5 r01 概念水印（应用到 T04/T05）

```text
Top-right corner: small monospace text "CONCEPT ONLY · NOT FOR LAYOUT · r01",
gold hex #D8A638, semi-transparent. The image MUST clearly read as a concept,
not as a manufacturable layout or as a CAD/FEA render.
For T05, additionally use a flat isometric line illustration style,
NO shading, NO surface texture, NO metallic reflection, NO real materials.
For T04, additionally avoid pretend pin numbers; only show signal name labels.
```

---

## 2. 12 方案 r01 差分提示词

每方案给出 8 模板的 r01 增补字段。仅列与 r00 不同的 token，未列项继续沿用 r00（`codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18.md` §3）。

### 2.1 S01 `negative_d_axis_field_weakening`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S01 NEGATIVE d-AXIS FIELD WEAKENING – DRIVER BLOCK` |
| T03 SCHEME_TITLE | `S01 FIELD WEAKENING – CONTROLLER STATE MACHINE` |
| T03 显式枚举 | `STATES = ["Power On + ADC self-test", "Normal Torque Control (MTPA request)", "Voltage Limited (enter field weakening)", "Apply id_min(T,fault) clamp", "Derate Torque", "Fault Fallback (gate disable)"]; EDGES = [("Power On + ADC self-test" -> "Normal Torque Control (MTPA request)", "sensors valid"), ("Power On + ADC self-test" -> "Fault Fallback (gate disable)", "self-test fail"), ("Normal Torque Control (MTPA request)" -> "Voltage Limited (enter field weakening)", "V margin < limit"), ("Voltage Limited (enter field weakening)" -> "Apply id_min(T,fault) clamp", "speed high"), ("Apply id_min(T,fault) clamp" -> "Derate Torque", "demag / current risk"), ("Derate Torque" -> "Normal Torque Control (MTPA request)", "margin recovered"), ("Derate Torque" -> "Fault Fallback (gate disable)", "sensor / fault latch")]` |
| T03 视觉 | `Highlight "Fault Fallback (gate disable)" node with red-tinted stroke; place "Power On + ADC self-test" at top-left and "Fault Fallback (gate disable)" at bottom-right` |
| T04 增补 | `Top-right CONCEPT ONLY watermark; reduce signal labels to <= 18 short tokens; group blocks within dashed gold bounding boxes labeled SENSING / ISOLATION / CONTROL / GATE DRIVE / SAFETY LATCH; ensure gate_disable_n line is the thickest stroke` |
| T05 增补 | `Flat isometric line illustration, NO shading, NO surface texture, NO metallic reflection; label phase A/B/C on the three busbars; explicit LV/HV keep-out dashed plane; no real material names` |
| T08 增补 | `Replace dashed line MCU->limiter with solid line; add signal labels "V_bus, I_phase, T_magnet" on that edge; every arrow MUST carry a bus label such as CAN-FD / SPI / FlexRay / XCP-Ethernet; no "Internal Bus" placeholder` |

改图建议：以 r00 PNG 作为参考图，要求模型"preserve every node and edge, restyle only"，再叠加上述增补。

### 2.2 S02 `mtpa_fw_mtpv_control`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S02 MTPA / FW / MTPV CONTINUOUS CONTROL – DRIVER BLOCK` |
| T03 SCHEME_TITLE | `S02 MODE TRANSITION LUT – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["MTPA idle", "MTPA active", "Field Weakening", "MTPV", "Derate", "LUT CRC fault fallback"]; EDGES = [("MTPA idle" -> "MTPA active", "LUT CRC ok"), ("MTPA active" -> "Field Weakening", "speed > base"), ("Field Weakening" -> "MTPV", "V margin < limit"), ("MTPV" -> "Field Weakening", "MTPV boundary reached"), ("MTPA active" -> "Derate", "thermal / demag risk"), ("Derate" -> "MTPA idle", "mode reset"), ("MTPA idle" -> "LUT CRC fault fallback", "LUT CRC fail")]` |
| T03 视觉 | `Highlight "LUT CRC fault fallback" node with red-tinted stroke; "mode reset" must point back to "MTPA idle", not to "Derate"` |
| T04 增补 | `Add explicit "LUT version diagnostic" node bridging MCU+NVM and CAN/CAN-FD; CONCEPT ONLY watermark` |
| T08 增补 | `Replace "Internal Bus" placeholder with explicit bus names: SPI for MCU<->NVM, internal AXI for MCU<->MODE SELECTOR, internal data path for SELECTOR<->FOC; UDS over CAN-FD; XCP over Ethernet TCP/IP` |

### 2.3 S03 `svpwm_overmodulation_voltage_utilization`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S03 SVPWM / OVERMODULATION / SIX-STEP – DRIVER BLOCK` |
| T03 SCHEME_TITLE | `S03 OVERMODULATION CONTROL – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["Linear SVPWM", "Overmodulation Region 1", "Overmodulation Region 2", "Six-Step", "Derate on THD limit", "Fallback to linear"]; EDGES = [("Linear SVPWM" -> "Overmodulation Region 1", "voltage utilization rising"), ("Overmodulation Region 1" -> "Overmodulation Region 2", "deeper modulation index"), ("Overmodulation Region 2" -> "Six-Step", "max voltage utilization"), ("Overmodulation Region 2" -> "Derate on THD limit", "THD limit hit"), ("Derate on THD limit" -> "Fallback to linear", "NVH limit hit"), ("Fallback to linear" -> "Linear SVPWM", "Vdc recovered"), ("Six-Step" -> "Derate on THD limit", "safety derate request")]; do NOT duplicate "voltage utilization rising" or "Vdc recovered" on multiple edges` |
| T03 视觉 | `Highlight "Derate on THD limit" and "Fallback to linear" with red-tinted stroke` |
| T04 增补 | `Highlight dead-time control sub-block as a dedicated card inside GATE DRIVE group` |

### 2.4 S04 `nonlinear_flux_lut`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S04 NONLINEAR FLUX LUT – DRIVER BLOCK` |
| T03 SCHEME_TITLE | `S04 NONLINEAR FLUX LUT – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["LUT load + CRC check", "Bounds check passed", "Bilinear interpolation active", "Out-of-bounds clamp", "Error monitor warning", "Fallback to linear dq"]; EDGES = [("LUT load + CRC check" -> "Bounds check passed", "LUT CRC ok"), ("Bounds check passed" -> "Bilinear interpolation active", "query inside LUT bounds"), ("Bilinear interpolation active" -> "Out-of-bounds clamp", "out-of-bounds detected"), ("Out-of-bounds clamp" -> "Bilinear interpolation active", "recover to LUT"), ("Bilinear interpolation active" -> "Error monitor warning", "interpolation residual ok"), ("Error monitor warning" -> "Fallback to linear dq", "monitor over threshold"), ("Fallback to linear dq" -> "LUT load + CRC check", "session reset")]` |
| T03 视觉 | `Highlight "Out-of-bounds clamp", "Error monitor warning" and "Fallback to linear dq" with red-tinted stroke` |
| T04 增补 | `**P0 redo**: reduce label density to <= 16 short signal tokens; remove pretend pin numbers; large CONCEPT ONLY watermark top-right; group: LUT OBSERVER INPUTS / BOUNDS CHECK / FALLBACK DIAGNOSTIC / ERROR BUDGET TELEMETRY / MCU NVM` |
| T05 增补 | `**P0 BLOCKER redo**: flat isometric line illustration of FEA reference frame, dq coordinate origin, material stack as labeled boxes (NO real grade names), mesh boundary as a wireframe cube, sensor position bindings as numbered callouts. Forbid M270-35A, NdFeB, SmCo, ADC12, C11000, mm dimensions, photorealistic motor render` |

### 2.5 S05 `magnetic_saturation_codesign`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S05 MAGNETIC SATURATION CO-DESIGN – PIPELINE BLOCK` |
| T03 SCHEME_TITLE | `S05 GEOMETRY CO-DESIGN – PIPELINE STATE MACHINE`（**禁止使用 MOTOR CONTROLLER SUBSYSTEM 字样**） |
| T03 显式枚举 | `STATES = ["Candidate geometry intake", "FEA LUT request", "Scorecard evaluation", "Down-select", "Stop-criteria triggered", "Retain for trade study"]; EDGES = [("Candidate geometry intake" -> "FEA LUT request", "geometry signed off"), ("FEA LUT request" -> "Scorecard evaluation", "FEA result available"), ("Scorecard evaluation" -> "Down-select", "score above threshold"), ("Down-select" -> "Stop-criteria triggered", "stress / demag risk too high"), ("Down-select" -> "Retain for trade study", "pareto retain"), ("Retain for trade study" -> "Candidate geometry intake", "next candidate"), ("Scorecard evaluation" -> "Stop-criteria triggered", "pareto loser")]` |
| T03 视觉 | `Highlight "Stop-criteria triggered" with red-tinted stroke; do NOT show motor controller imagery` |

### 2.6 S06 `pmasynrm_high_saliency_low_pm`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S06 PMaSynRM HIGH-SALIENCY LOW-PM – DRIVER BLOCK` |
| T03 SCHEME_TITLE | `S06 HIGH-SALIENCY MTPA / MTPV – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["MTPA active", "High-saliency FW", "MTPV", "Low-PM demag guard", "Derate"]; EDGES = [("MTPA active" -> "High-saliency FW", "MTPA boundary reached"), ("High-saliency FW" -> "MTPV", "FW margin shrinking"), ("MTPV" -> "Low-PM demag guard", "MTPV boundary"), ("Low-PM demag guard" -> "Derate", "demag risk rising"), ("Derate" -> "MTPA active", "recover")]; do NOT add a sixth "Fault Fallback" state — that belongs to S11 not S06` |
| T03 视觉 | `Highlight "Low-PM demag guard" and "Derate" with red-tinted stroke` |

### 2.7 S07 `variable_magnetization_memory_motor`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S07 VARIABLE MAGNETIZATION (MEMORY MOTOR) – RESEARCH POOL CONCEPT` |
| T01 视觉 | `Top-right monospace watermark: "RESEARCH POOL CONCEPT · NOT ENGINEERING RELEASE"` |
| T03 SCHEME_TITLE | `S07 MAGNETIZATION STATE MACHINE – RESEARCH POOL CONCEPT` |
| T03 显式枚举 | `STATES = ["Magnetization idle", "Pre-charge energy bank", "Apply magnetization pulse", "Apply de-magnetization pulse", "Verify flux state", "Unknown-state fallback", "Lifetime cycle count update"]; EDGES = [("Magnetization idle" -> "Pre-charge energy bank", "bank ready"), ("Pre-charge energy bank" -> "Apply magnetization pulse", "pulse trigger up"), ("Pre-charge energy bank" -> "Apply de-magnetization pulse", "pulse trigger down"), ("Apply magnetization pulse" -> "Verify flux state", "pulse complete"), ("Apply de-magnetization pulse" -> "Verify flux state", "pulse complete"), ("Verify flux state" -> "Lifetime cycle count update", "state observed ok"), ("Verify flux state" -> "Unknown-state fallback", "state unknown"), ("Unknown-state fallback" -> "Magnetization idle", "safe retreat"), ("Lifetime cycle count update" -> "Magnetization idle", "cycle limit reached")]; remove the duplicate "Safe retreat" self-loop seen in r00` |
| T03 视觉 | `Highlight "Unknown-state fallback" with red-tinted stroke` |
| T05 增补 | `**P0 BLOCKER redo**: flat isometric line illustration only; forbid SmCo, NdFeB, M235-35A, 35PN440, real dimensions in mm; show memory magnet placement as labeled rectangles inside rotor cross-section, magnetization path as dashed arrows; large RESEARCH POOL CONCEPT watermark` |

### 2.8 S08 `hybrid_excitation`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S08 HYBRID EXCITATION – RESEARCH POOL CONCEPT` |
| T01 视觉 | `Top-right RESEARCH POOL CONCEPT watermark` |
| T03 SCHEME_TITLE | `S08 HYBRID EXCITATION – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["Field excitation idle", "Field excitation active", "Three-variable control (id, iq, if)", "Loss-of-field detected", "Fallback to PM-only operation"]; EDGES = [("Field excitation idle" -> "Field excitation active", "field DC/DC enable"), ("Field excitation active" -> "Three-variable control (id, iq, if)", "if reference set"), ("Three-variable control (id, iq, if)" -> "Three-variable control (id, iq, if)", "optimization step"), ("Three-variable control (id, iq, if)" -> "Loss-of-field detected", "loss-of-field flag"), ("Loss-of-field detected" -> "Fallback to PM-only operation", "field unavailable"), ("Fallback to PM-only operation" -> "Field excitation idle", "recover")]; correct r00 directional errors — "if reference set" must point Active->Three-variable (NOT Active->Loss-of-field); "recover" must point Fallback->Idle (NOT Fallback->Three-variable)` |
| T03 视觉 | `Highlight "Loss-of-field detected" and "Fallback to PM-only operation" with red-tinted stroke` |
| T05 增补 | `**P0 BLOCKER redo**: flat isometric line illustration only; forbid brushless-exciter photoreal cross-section; show field winding as labeled rectangles, exciter as a stack of boxes, harness as gold polyline; large RESEARCH POOL CONCEPT watermark` |

### 2.9 S09 `winding_reconfiguration`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S09 WINDING RECONFIGURATION – RESEARCH POOL CONCEPT` |
| T03 SCHEME_TITLE | `S09 WINDING RECONFIGURATION – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["Configuration A", "Zero-torque window", "Switch in progress", "Configuration B", "Illegal-state fallback", "Circulating-current detected"]; EDGES = [("Configuration A" -> "Zero-torque window", "switch request"), ("Zero-torque window" -> "Switch in progress", "zero-torque verified"), ("Switch in progress" -> "Configuration B", "switch complete"), ("Switch in progress" -> "Illegal-state fallback", "illegal state detected"), ("Switch in progress" -> "Circulating-current detected", "arc suppression triggered"), ("Circulating-current detected" -> "Configuration A", "current re-balanced"), ("Illegal-state fallback" -> "Configuration A", "manual recovery only")]; "manual recovery only" implies service intervention, not auto` |
| T03 视觉 | `Highlight "Illegal-state fallback" and "Circulating-current detected" with red-tinted stroke` |

### 2.10 S10 `multiphase_phase_group_control`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S10 MULTIPHASE / PHASE-GROUP CONTROL – RESEARCH POOL CONCEPT` |
| T03 SCHEME_TITLE | `S10 PHASE-GROUP FAULT ALLOCATOR – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["Healthy multiphase", "Single-phase fault", "Phase-group fault", "Derate via torque allocator", "Shut down"]; EDGES = [("Healthy multiphase" -> "Single-phase fault", "phase fault detected"), ("Single-phase fault" -> "Derate via torque allocator", "derate request"), ("Healthy multiphase" -> "Phase-group fault", "group fault detected"), ("Phase-group fault" -> "Derate via torque allocator", "derate request"), ("Derate via torque allocator" -> "Shut down", "thermal limit"), ("Single-phase fault" -> "Healthy multiphase", "fault cleared")]; do NOT route "fault cleared" from "Shut down" back to "Healthy multiphase" (shut down requires service intervention)` |
| T03 视觉 | `Highlight "Phase-group fault" and "Shut down" with red-tinted stroke` |

### 2.11 S11 `thermal_demag_safety_protection`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S11 THERMAL / DEMAG / SAFETY SUPERVISOR – DRIVER BLOCK` |
| T03 SCHEME_TITLE | `S11 SAFETY SUPERVISOR – STATE MACHINE` |
| T03 显式枚举 | `STATES = ["Normal", "Thermal / demag warning", "Active derating", "Unknown sensor fallback", "Hardware gate-disable", "Latched fault"]; EDGES = [("Normal" -> "Thermal / demag warning", "temperature rising"), ("Thermal / demag warning" -> "Active derating", "derate trigger"), ("Active derating" -> "Unknown sensor fallback", "sensor open / short"), ("Active derating" -> "Hardware gate-disable", "gate-disable assertion"), ("Hardware gate-disable" -> "Latched fault", "latch set"), ("Latched fault" -> "Normal", "latch reset only by service"), ("Unknown sensor fallback" -> "Hardware gate-disable", "fallback elevated")]` |
| T03 视觉 | `Highlight "Active derating", "Unknown sensor fallback", "Hardware gate-disable", "Latched fault" with red-tinted stroke` |
| T04 增补 | `Set node fill to pale blue hex #B6C7E0 (current r00 is dark gray, off-baseline); CONCEPT ONLY watermark` |
| T07 增补 | `Replace TST-THM-001..TST-LAT-005 with the DVP IDs from V2-S11-DVP-safety_fault_injection-r00.md: S11-DV-001 thermal warning/critical, S11-DV-002 sensor open/short, S11-DV-003 demag margin, S11-DV-004 gate-disable assertion, S11-DV-005 fault reason traceability` |

### 2.12 S12 `weighted_efficiency_pareto_selection`

| 模板 | r01 增补 |
|---|---|
| T01 SCHEME_TITLE | `S12 WEIGHTED EFFICIENCY PARETO SELECTION – SCORECARD BLOCK` |
| T01 视觉 | `Remove trophy icon (decorative); replace with a plain "Candidate Ranking" labeled rectangle` |
| T03 SCHEME_TITLE | `S12 PARETO SCORECARD PIPELINE – STATE MACHINE`（**禁止使用 MOTOR CONTROLLER SUBSYSTEM 字样**） |
| T03 显式枚举 | `STATES = ["Candidate intake", "Drive cycle weighting", "System loss aggregation", "Maturity + risk scoring", "Pareto ranking", "Trade-study output"]; EDGES = [("Candidate intake" -> "Drive cycle weighting", "inputs versioned"), ("Drive cycle weighting" -> "System loss aggregation", "weights applied"), ("System loss aggregation" -> "Maturity + risk scoring", "losses computed"), ("Maturity + risk scoring" -> "Pareto ranking", "scores ready"), ("Pareto ranking" -> "Trade-study output", "pareto sweep done"), ("Trade-study output" -> "Candidate intake", "recommendation issued")]` |
| T03 视觉 | `Do NOT show traction motor or inverter imagery; pipeline boxes only` |

---

## 3. 模板级 r01 提示词重写（直接复用片段）

下方提示词可直接粘贴生图工具（替换 `<...>` 占位符），不再依赖 r00 模板：

### T01 driver block（r01）

```text
Flat technical block diagram for an EV traction inverter and motor control chain
specific to <SCHEME_NAME>. Layout left-to-right with five primary power-stage
blocks: Battery / DC link, Precharge + main contactor, 3-phase inverter, IPMSM motor.
Above the power chain, a control row with: MCU running FOC, gate driver interface,
encoder / resolver, phase current sensors ia ib ic, Vdc sensor, and the scheme-
specific sub-block <SCHEME_BLOCK>. Connect <SCHEME_INPUTS> into <SCHEME_BLOCK>.
Title bar text MUST be: "<SCHEME_TITLE>".
Aspect ratio 16:9, single image, no people, no marketing copy.
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

### T02 sequence（r01）

```text
UML-style sequence diagram for an EV traction inverter power-on procedure
specific to <SCHEME_NAME>. Four vertical lifelines: VCU, MCU, INV, M (plus optional
NVM lifeline). Top-to-bottom horizontal arrows in this exact order:
<SCHEME_SEQUENCE>. Use thin gold horizontal arrows on dark navy background,
monospace short labels, thicker activation bar on MCU lifeline during self-test
and LUT load. Allow up to 16:9 aspect ratio with comfortable horizontal spacing.
Title bar text MUST be: "<SCHEME_TITLE>".
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

### T03 state machine（r01）

```text
Finite-state-machine diagram for <SCHEME_NAME> subsystem.
<r01 GLOBAL ENUMERATION RULE §1.4>
STATES = <SCHEME_STATES>. EDGES = <SCHEME_EDGES_WITH_LABELS>.
Render the states as rounded rectangles in a 2x3 or 3x2 grid;
arrange so that the first state is top-left and the most "fault / fallback"
state is bottom-right.
Title bar text MUST be: "<SCHEME_TITLE>".
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

### T04 PCB sheet（r01）

```text
Conceptual PCB schematic sheet outline (NOT a real layout, NOT a manufacturable
artwork) for <SCHEME_NAME>. Show labeled functional blocks left-to-right in
five groups: SENSING, ISOLATION, CONTROL, GATE DRIVE, SAFETY LATCH.
Block details: <SCHEME_PCB_BLOCKS>. Group blocks within dashed gold bounding
boxes labeled with the group name. Annotate signal names in English next to
thin gold connectors. Reduce signal labels to no more than 18 short tokens.
<r01 CONCEPT WATERMARK §1.5>
Title bar text MUST be: "<SCHEME_TITLE> – CONCEPT PCB SHEET".
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

### T05 CAD packaging（r01）

```text
Conceptual isometric line illustration of <SCHEME_NAME> mechanical packaging
boundary. Flat vector style only. NO shading, NO surface texture, NO metallic
reflection, NO photorealistic motor cross-section. Show: <SCHEME_CAD_ELEMENTS>
as labeled outlined rectangles or wireframes. Mark LV / HV keep-out zones as
dashed planes. Use generic material categories (electrical steel, magnet,
copper, insulator, coolant) WITHOUT specific grades or real designations.
<r01 CONCEPT WATERMARK §1.5>
Title bar text MUST be: "<SCHEME_TITLE> – CONCEPT PACKAGING".
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

### T06 BOM tree（r01）

```text
Infographic-style component family risk tree for <SCHEME_NAME>. Root node centered
at top labeled "<SCHEME_NAME>". First-level branches: <SCHEME_BOM_GROUPS>.
Each leaf shows a 2-3 word component family label and a risk badge (LOW / MED /
HIGH) drawn as small pills. <SCHEME_PER_LEAF_RISK_OVERRIDES>.
Title bar text MUST be: "<SCHEME_TITLE> – BOM / EDA RISK TREE".
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

### T07 verification tree（r01）

```text
Left-to-right verification plan tree for <SCHEME_NAME>. Root on the left.
Level-1 branches: <SCHEME_TEST_AXES>. Level-2 leaves show short acceptance
hooks in English. Each level-1 branch must carry a DVP&R ID derived from
<SCHEME_DVP_IDS> (do NOT invent new IDs). Use monospace font ONLY for the
test IDs; keep prose labels in sans-serif.
Title bar text MUST be: "<SCHEME_TITLE> – VERIFICATION PLAN".
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

### T08 protocol link（r01）

```text
Network-style block diagram of communication and control links for
<SCHEME_NAME>. Nodes: VCU CAN/CAN-FD, MCU command parser,
<SCHEME_PROTOCOL_BLOCK>, FOC id/iq controller, SVPWM, UDS / XCP diagnostics,
calibration tool. Every arrow MUST carry an explicit bus label such as
CAN, CAN-FD, SPI, FlexRay, internal AXI bus, XCP-over-Ethernet (TCP/IP).
Do NOT use generic "Internal Bus" placeholders. Replace any dashed line with
a solid line unless the dashed line carries a label like "fault path".
Title bar text MUST be: "<SCHEME_TITLE> – PROTOCOL LINK".
<r01 GLOBAL POSITIVE STYLE TOKEN §1.1>
```

---

## 4. 改图（图像到图像）工作流（r01）

1. 拿 r00 的 PNG 作为输入参考图。
2. 改图指令模板：

```text
Reference image: V2-SXX-ILL-TYY-...-r00.png
Goal: re-render in the r01 style baseline.
Preserve: every English node label and every transition label EXACTLY as in
the r00 image, including their on-image positions; preserve the topology
(nodes and edges) so that no semantic information changes.
Change: background to single solid dark navy hex #0B1A33,
node fill to pale blue hex #B6C7E0, stroke to gold hex #D8A638,
fault / fallback nodes to red-tinted stroke hex #C0392B,
title bar to: "<SCHEME_TITLE>" exactly.
Remove: any "MOTOR CONTROLLER SUBSYSTEM" generic title where the scheme is
not a motor controller, any real material designations, any decorative
trophy/icon flourishes, any photorealistic motor / PCB rendering.
Do NOT add: people, marketing copy, manufacturer logos, decorative gradients.
```

3. 若 r00 图存在工程语义错误（如 S08 T03 箭头方向反），改图模式不能修复；必须切回纯生图模式，使用 §2 的显式枚举 prompt。

---

## 5. r01 落地行动

| ID | 行动 | 落点 | 责任 | 状态 |
|---|---|---|---|---|
| R01-DRAW-01 | 重生 P0 8 张：S01/S02/S03/S04 T03、S04 T04、S04/S07/S08 T05、S05/S06/S12 T03 | `gpt-image-2/outputs/SXX/V2-SXX-ILL-TYY-...-r01.png` | 用户手动（按 §2 / §3 prompt） | 待执行 |
| R01-DRAW-02 | 推荐重生 P1 40 张：T02 sequence × 12、T05 CAD × 多张、T08 protocol bus label × 多张 | 同上 | 用户手动 | 待执行 |
| R01-CONF-01 | 在 `gpt-image-2/prompts/schemes.json` 中加 size 覆盖（参见 §1.3） | `gpt-image-2/prompts/schemes.json` | Claude 或 Codex | 待执行 |
| R01-DOC-01 | 把本目录引用入 `image_worklist_2026-05-18/README.md` 与 `scheme-XX.md` 分册 | `codex-review/docs/image_worklist_2026-05-18/` | Claude（本轮） | 已规划 |
| R01-REVIEW-01 | r01 出图后再做一轮 Claude 评审，比较 r00 vs r01 | `claude-review/docs/2026-05-19/...` | 下一轮 | 待执行 |

---

## 6. 禁止误读

1. r01 提示词改善的是 **图与提示词的对齐度**，不改善 **图与真实工程交付物的等价性**。
2. r01 重生图 **不**等于工程交付物，**不**升级 `engineering_validated`。
3. 出现真实材料牌号或写实 render 必须立即拒收。
4. 任何方案语义改动必须先回到 `engineering/v2/scheme-XX/` 的 `.drawio` / mermaid / markdown 源；r01 prompt 不是设计源。
5. r01 不替代 EDA / CAD / FEA / HIL 任何文件。
