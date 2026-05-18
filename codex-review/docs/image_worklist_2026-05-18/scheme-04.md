# S04 nonlinear_flux_lut 图档分册

方案 ID：`nonlinear_flux_lut`  
工程目录：`engineering/v2/scheme-04/`  
当前草案：PCB / CAD / Controller / BOM / DVP 已落 markdown / drawio 草案。EXP-006 phase-2 数值闭环 targeted pytest 已通过。  
本分册产出落点：`engineering/v2/scheme-04/illustrations/`

> 通用风格 token 与负向 prompt 见 `image_worklist_2026-05-18/README.md` §1。`<STYLE>` = §1.1。

---

## IMG-S04-T01 驱动设计图

- 优先级：**P0**
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T01-driver_block-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §4 驱动设计图
- 工作流：mermaid → 改图，或纯生图
- 验收：能看到 LUT observer 接收 id/iq/omega/T，输出 lambda_d/lambda_q 到 FOC

### 提示词

```text
Flat technical block diagram of an EV traction control chain centered on a
nonlinear flux LUT observer. Layout left-to-right: "id, iq, omega, T inputs"
-> "Nonlinear flux LUT observer" -> "lambda_d / lambda_q outputs" -> "FOC
current controller" -> "PWM" -> "Inverter" -> "IPMSM motor". Sub-block inside
the LUT observer labeled "bounds checker + bilinear interpolation". A side
input from "NVM (LUT storage + CRC)" feeds into the LUT observer. Use
rectangular nodes with rounded corners, gold strokes on dark navy background,
clean orthogonal connectors, short English labels. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make the Nonlinear flux LUT observer visually larger to indicate central role
draw lambda_d / lambda_q outputs with two parallel labeled arrows
use dashed gold stroke for the NVM-to-observer LUT loading link
```

---

## IMG-S04-T02 上电时序图

- 优先级：P2
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T02-power_on_sequence-r00.png`
- 参考图：`mmd` —— 同上 §4 上电时序图
- 工作流：mermaid → 改图

### 提示词

```text
UML-style sequence diagram for a controller power-on procedure that loads and
validates a nonlinear flux LUT. Four vertical lifelines: MCU, NVM, FOC, VCU.
Top-to-bottom horizontal arrows: (1) MCU to NVM "load flux LUT and CRC",
(2) MCU self-loop "validate dq orientation and bounds",
(3) MCU self-loop "run unit-cell interpolation test",
(4) MCU to FOC "enable LUT-driven flux estimation",
(5) MCU self-loop "arm out-of-bounds monitor",
(6) VCU to MCU "torque command allowed",
(7) FOC self-loop "fallback to linear dq if LUT bounds violated".
Thin gold horizontal arrows on dark navy background, monospace short labels.
Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
add activation bars on MCU during LUT load and validation
make the fallback arrow stroke red-tinted to indicate safety path
keep NVM lifeline visually distinct as persistent storage
```

---

## IMG-S04-T03 控制器状态机

- 优先级：**P0**
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T03-state_machine-r00.png`
- 参考图：`drawio` —— `engineering/v2/scheme-04/controller/V2-S04-CTRL-flux_lut_interpolation-r00.drawio`
- 工作流：**强烈建议改图模式**
- 验收：6 状态 + 6 转移，保留 LUT load, bounds, interpolation, out-of-bounds clamp, monitor, fallback

### 提示词

```text
Finite-state-machine diagram for a nonlinear flux LUT observer subsystem.
States as rounded rectangles arranged in a 2x3 grid, exact labels:
- "LUT load + CRC check"
- "Bounds check passed"
- "Bilinear interpolation active"
- "Out-of-bounds clamp"
- "Error monitor warning"
- "Fallback to linear dq"
Directed edges with English transition labels showing exactly:
"LUT CRC ok", "query inside LUT bounds", "interpolation residual ok",
"out-of-bounds detected", "monitor over threshold", "recover to LUT".
Flat infographic style, dark navy background, pale blue node fills, gold
stroke and labels, orthogonal connectors, no shadows. <STYLE>
```

### 改图微调

```text
preserve every state label and every transition label exactly as written
make "Fallback to linear dq" use a red-tinted stroke to indicate degraded mode
arrange so the happy path forms a clear left-to-right progression
ensure "Out-of-bounds clamp" and "Error monitor warning" are visually adjacent
```

---

## IMG-S04-T04 PCB 页面草案

- 优先级：P1
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T04-pcb_sheet_concept-r00.png`
- 参考图：无 —— `engineering/v2/scheme-04/pcb/V2-S04-PCB-lut_observer_inputs-r00.md` 文字
- 工作流：纯生图 v0 → 改图

### 提示词

```text
Conceptual PCB schematic sheet outline for a nonlinear flux LUT observer
board. Show labeled functional blocks left-to-right in five groups:
(observer inputs) id, iq, omega, T inputs;
(bounds) bounds checker logic;
(fallback) fallback diagnostic line to linear dq path;
(telemetry) error budget telemetry;
(memory) MCU NVM block holding the LUT with CRC.
Annotate signal names in English next to thin gold connectors. Dark navy
background, light grid, no real component footprints, no part numbers.
Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
group blocks within each functional group inside a thin gold dashed bounding box
highlight the NVM block with thicker gold border to emphasize LUT storage
draw the fallback path with a dashed gold stroke to indicate degraded mode
```

---

## IMG-S04-T05 3D/CAD 封装边界

- 优先级：P1
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T05-cad_packaging_concept-r00.png`
- 参考图：无 —— `engineering/v2/scheme-04/cad/V2-S04-CAD-fea_geometry_source-r00.md` 文字
- 工作流：纯生图 v0 → 改图
- 备注：S04 的 CAD 草案重点是"FEA geometry source"约定，而非实物封装。建议生成"FEA 几何源信息图"风格

### 提示词

```text
Conceptual infographic illustrating the data binding between an EV motor FEA
geometry source and a nonlinear flux LUT. Show on the left: a stylized
cross-section of an IPMSM rotor and stator with dq coordinate origin marked.
Around it: callouts for "material stack", "mesh boundary illustration",
"sensor position bindings". On the right: an arrow flowing into a labeled box
"nonlinear flux LUT (lambda_d, lambda_q vs id, iq, T)". Flat vector style,
dark navy background, soft cyan and gold accents, English callouts with
leader lines. No photorealism, no manufacturer branding. Aspect ratio 4:3.
<STYLE>
```

### 改图微调

```text
make the dq coordinate axes clearly visible at the rotor center
label the d-axis and q-axis distinctly
keep all leader lines straight and non-overlapping
remove any pretend slot count detail
```

---

## IMG-S04-T06 BOM / EDA 风险树

- 优先级：P2
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T06-bom_eda_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Infographic-style component family risk tree for a nonlinear flux LUT observer
subsystem. Root node at top: "nonlinear flux LUT subsystem". Five first-level
branches: "Current sensors", "Position sensors", "Temperature sensors",
"Vdc sensing", "Diagnostic NVM". Each branch has 2-3 leaves. Each leaf carries
a LOW / MED / HIGH risk pill, color-coded green / amber / red. Dark navy
background, gold trunk strokes, English labels. Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
make Diagnostic NVM branch emphasized (this scheme depends on LUT integrity)
align all first-level branches at same vertical level
keep tree purely top-down
```

---

## IMG-S04-T07 测试树

- 优先级：P2
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T07-test_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Left-to-right tree diagram of a verification plan. Root on the left:
"nonlinear flux LUT verification". Level-1 branches:
"LUT bounds enforcement", "Interpolation consistency",
"FEA version binding", "Bench correlation", "Fallback behavior".
Level-2 leaves are short English acceptance hooks. Clean vector style,
dark navy background, gold and pale blue accents, monospace labels for
test IDs. No people, no labs. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
group "LUT bounds enforcement" and "Fallback behavior" near each other (both safety)
add a small FEA badge near "FEA version binding"
make Bench correlation use slightly different leaf color to indicate hardware-in-loop
```

---

## IMG-S04-T08 协议链路图

- 优先级：P1
- 目标：`engineering/v2/scheme-04/illustrations/V2-S04-ILL-T08-protocol_link-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §4 协议链路图
- 工作流：mermaid → 改图

### 提示词

```text
Network-style block diagram of communication links for a nonlinear flux LUT
controller. Nodes: "VCU CAN", "MCU command parser",
"LUT version + bounds telemetry", "FOC controller", "SVPWM",
"UDS / XCP diagnostics", "Calibration / FEA import tool". Arrows: VCU CAN
-> MCU; MCU -> LUT version + bounds telemetry; MCU -> FOC -> SVPWM;
FOC -> LUT version + bounds telemetry (feedback); MCU -> UDS / XCP;
Calibration / FEA import tool -> MCU. Each link labeled with its bus type
(CAN, XCP). Dark navy background, gold accents, English labels.
Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make LUT version + bounds telemetry visually highlighted as the routing hub
use dashed stroke for the FEA-import side channel
group request-side on left, feedback on right
```

---

## 本方案归档清单

| 图 ID | 优先级 | PNG | prompt.txt |
|---|---|---|---|
| IMG-S04-T01 driver | P0 | [ ] | [ ] |
| IMG-S04-T02 sequence | P2 | [ ] | [ ] |
| IMG-S04-T03 state machine | P0 | [ ] | [ ] |
| IMG-S04-T04 PCB | P1 | [ ] | [ ] |
| IMG-S04-T05 CAD | P1 | [ ] | [ ] |
| IMG-S04-T06 BOM tree | P2 | [ ] | [ ] |
| IMG-S04-T07 Test tree | P2 | [ ] | [ ] |
| IMG-S04-T08 protocol | P1 | [ ] | [ ] |
