# S01 negative_d_axis_field_weakening 图档分册

方案 ID：`negative_d_axis_field_weakening`  
工程目录：`engineering/v2/scheme-01/`  
当前草案：PCB / CAD / Controller / BOM / DVP 已落 markdown / drawio 草案。  
本分册产出落点：`engineering/v2/scheme-01/illustrations/`

> 通用风格 token 与负向 prompt 见 `image_worklist_2026-05-18/README.md` §1。下方每条 prompt 末尾的 `<STYLE>` 占位符替换为 §1.1 整段；负向 prompt 直接用 §1.2 整段。

---

## IMG-S01-T01 驱动设计图

- 优先级：**P0**
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T01-driver_block-r00.png`
- 参考图：`mmd` —— 来源 `reports/scheme_driver_power_protocol_diagrams.md` §1 驱动设计图块
- 工作流：可选「mermaid 渲染 PNG → 改图」或纯「生图」
- 验收：图里能看到 Battery → Precharge → Inverter → IPMSM 的主功率链，以及 MCU 与 `id_min` limiter 子块的连线

### 提示词

```text
Flat technical block diagram of an automotive traction inverter and motor
control chain for an EV powertrain. Layout left-to-right with five primary
power-stage blocks: Battery / DC link, Precharge + main contactor,
3-phase inverter, IPMSM motor. Above the power chain, a control row contains:
MCU running FOC, gate driver interface, encoder / resolver input, phase current
sensors ia ib ic, Vdc sensor, and a highlighted sub-block labeled
"negative_d_axis_field_weakening id_min(T,fault) limiter". Connect Vdc sensor
and motor / inverter temperature inputs into the id_min limiter block. Use
rectangular nodes with rounded corners, gold strokes on dark navy background,
clean orthogonal connectors with arrowheads, short English labels. Aspect ratio
16:9, single image, no people, no marketing copy. <STYLE>
```

### 改图微调

```text
make id_min(T,fault) limiter visually highlighted with a slightly brighter gold border
keep the five-block power chain straight and horizontal across the bottom row
add small T and Vdc sensor icons feeding into the limiter block
remove any decorative motor render, keep motor as a simple labeled rounded rectangle
```

---

## IMG-S01-T02 上电时序图

- 优先级：P2
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T02-power_on_sequence-r00.png`
- 参考图：`mmd` —— 来源同上 §1 上电时序图块
- 工作流：mermaid 渲染 PNG → 改图，或纯生图
- 验收：4 条 lifeline（VCU / MCU / INV / M），自顶向下 6-8 条信令箭头，能看到 self-test、precharge、id_min load、torque enable

### 提示词

```text
UML-style sequence diagram for an EV traction inverter power-on procedure
specific to a field-weakening control firmware. Four vertical lifelines:
VCU, MCU, INV (inverter), M (motor). Top-to-bottom horizontal arrows in this
exact order: (1) VCU to MCU "Wake + torque disabled",
(2) MCU self-loop "self-test current / Vdc / position sensors",
(3) MCU to INV "enable precharge path",
(4) MCU self-loop "verify Vdc stable",
(5) MCU to INV "enable gate drivers",
(6) MCU to M "align or verify rotor position",
(7) MCU self-loop "load id_min(T) and FW limits",
(8) VCU to MCU "torque command allowed".
Thin gold horizontal arrows on dark navy background, monospace short labels,
no decoration, no human figures, no color gradients beyond two accent colors.
Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
align all arrow labels horizontally so they stay readable
make MCU self-loop arrows visually distinct from cross-lifeline arrows
add a thin vertical activation bar on MCU lifeline during self-test
```

---

## IMG-S01-T03 控制器状态机

- 优先级：**P0**
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T03-state_machine-r00.png`
- 参考图：`drawio` —— 来源 `engineering/v2/scheme-01/controller/V2-S01-CTRL-field_weakening_state_machine-r00.drawio`
- 工作流：**强烈建议改图模式**（draw.io 导出 PNG → 上传为参考图 → 用提示词刷风格）
- 验收：保留全部 6 状态、7 转移；节点位置可重排，但语义不可变

### 提示词

```text
Finite-state-machine diagram for a motor controller subsystem implementing
negative d-axis field weakening with safety fallback. States as rounded
rectangles arranged in a 2x3 grid, exact labels:
- "Power On + ADC self-test"
- "Normal Torque Control (MTPA request)"
- "Voltage Limited (enter field weakening)"
- "Apply id_min(T,fault) clamp"
- "Derate Torque"
- "Fault Fallback (gate disable)"
Directed edges with English transition labels showing exactly:
"sensors valid", "V margin < limit", "speed high", "demag / current risk",
"margin recovered", "self-test fail", "sensor / fault latch".
Flat infographic style, dark navy background, pale blue node fills, gold stroke
and labels, orthogonal connectors, no shadows, no people, single image. <STYLE>
```

### 改图微调

```text
preserve every state label and every transition label exactly as written
re-layout to a 2x3 grid with Power On at top-left and Fault Fallback at bottom-left
make Fault Fallback node use a slightly red-tinted stroke to indicate safety state
ensure no two arrows overlap; use orthogonal routing
remove the draw.io grid background, replace with solid dark navy
```

---

## IMG-S01-T04 PCB 页面草案

- 优先级：P1
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T04-pcb_sheet_concept-r00.png`
- 参考图：无 —— 仅有 `engineering/v2/scheme-01/pcb/V2-S01-PCB-sensing_fault_path-r00.md` 文字
- 工作流：纯生图 v0；不满意切到改图迭代
- 验收：左到右能看到 sensing、isolation、control、gate drive、safety latch 五个功能组；信号名清楚

### 提示词

```text
Conceptual PCB schematic sheet outline (not a real layout, not a manufacturable
artwork) for a field-weakening motor controller. Show labeled functional blocks
left-to-right in five groups: (sensing) phase current ia/ib/ic, Vdc sense divider,
motor temperature, inverter temperature; (isolation) sensor isolation barrier;
(control) MCU ADC front-end, FOC core, id_min(T,fault) limiter logic;
(gate drive) gate driver with dead-time, gate_disable_n hardware path;
(safety latch) fault latch readback, latch reset interface. Annotate signal names
in English next to thin gold connectors. Dark navy background, light grid,
no real component footprints, no part numbers, no marketing copy.
Make it clearly a "page-level concept", not a manufacturable layout.
Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
group blocks within each functional group inside a thin gold dashed bounding box
label each bounding box with the group name (sensing, isolation, control, gate drive, safety latch)
remove any pretend chip pin numbers; only show signal name labels
ensure gate_disable_n line is drawn with a thicker gold stroke to stand out
```

---

## IMG-S01-T05 3D/CAD 封装边界

- 优先级：P1
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T05-cad_packaging_concept-r00.png`
- 参考图：无 —— 仅有 `engineering/v2/scheme-01/cad/V2-S01-CAD-sensor_busbar_layout-r00.md` 文字
- 工作流：纯生图 v0 → 改图
- 验收：三相母排、电流传感器窗、温度传感器、LV/HV keep-out 分区都能看到

### 提示词

```text
Isometric concept illustration of an EV inverter and motor mechanical packaging
boundary for a field-weakening configuration. Show: a generic 3-phase inverter
housing on the left, three rectangular busbars going to the motor end-terminals
on the right, current sensor windows around the busbars, a motor-side
temperature sensor mounted on the motor housing, an inverter-side temperature
sensor inside the inverter housing, an LV / HV keep-out partition drawn as a
dashed plane, and a service access port for fault latch debugging. Flat vector
style, dark navy background, soft cyan and gold accents, English labels with
leader lines. No photorealism, no human figures, no manufacturer branding.
Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
make the LV/HV keep-out partition clearly visible as a dashed gold plane
label each busbar with phase letter A/B/C
keep all callouts in English, with thin leader lines, not overlapping each other
remove any pretend assembly screws or fasteners
```

---

## IMG-S01-T06 BOM / EDA 风险树

- 优先级：P2
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T06-bom_eda_tree-r00.png`
- 参考图：无
- 工作流：纯生图
- 验收：5 个一级分支 + 各自子节点 + LOW/MED/HIGH 风险胶囊

### 提示词

```text
Infographic-style component family risk tree for an EV motor control subsystem
implementing negative d-axis field weakening. Root node centered at top labeled
"negative d-axis field weakening". Five first-level branches:
"Current sensors", "Vdc divider network", "Temperature sensors",
"Gate-disable latch", "Fault feedback chain". Each branch has 2-3 leaves
representing component subfamilies. Each leaf carries a small pill-shaped risk
badge with text LOW / MED / HIGH; color-code green / amber / red respectively.
Dark navy background, gold trunk strokes, color-coded risk pills, English
labels, no real manufacturer logos, no part numbers. Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
keep the tree purely top-down, root at top, leaves at bottom
keep all five first-level branches at the same vertical level
make HIGH risk pills slightly larger to draw attention
ensure pill colors are accessible green-amber-red, not pastel
```

---

## IMG-S01-T07 测试树

- 优先级：P2
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T07-test_tree-r00.png`
- 参考图：无
- 工作流：纯生图
- 验收：4 条一级 axis + 每条 axis 2-3 个二级 acceptance hook

### 提示词

```text
Left-to-right tree diagram of a verification plan. Root on the left:
"negative d-axis field weakening verification". Level-1 branches:
"Field weakening entry / exit", "id_min(T,fault) clamp validation",
"Sensor fault injection", "Gate-disable latch test". Level-2 leaves show
short acceptance hooks in English, for example "entry hysteresis bounded",
"clamp respects T_max", "open / short detected within 1 ms",
"latch holds across power cycle". Clean vector style, dark navy background,
gold and pale blue accents, monospace labels for test IDs. No people,
no labs, no marketing photos. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
align all level-2 leaves vertically by branch
add a small DVPR badge near each level-1 branch label
keep monospace font only for test IDs (e.g., DVP-S01-01), not for prose labels
```

---

## IMG-S01-T08 协议链路图

- 优先级：P1
- 目标：`engineering/v2/scheme-01/illustrations/V2-S01-ILL-T08-protocol_link-r00.png`
- 参考图：`mmd` —— 来源 `reports/scheme_driver_power_protocol_diagrams.md` §1 协议链路图块
- 工作流：mermaid 渲染 PNG → 改图
- 验收：能看到 VCU CAN → MCU → 限幅 → FOC → SVPWM 主链，以及 UDS/XCP 诊断与标定支线

### 提示词

```text
Network-style block diagram of communication and control links for an EV
traction controller. Nodes: "VCU CAN / CAN-FD torque command",
"MCU command parser", "voltage / current / demag limiter",
"FOC id/iq controller", "SVPWM", "UDS / XCP diagnostics",
"Calibration tool". Arrows: VCU CAN -> MCU; MCU -> limiter; limiter -> FOC;
FOC -> SVPWM; MCU -> UDS/XCP; Calibration tool -> MCU. Each link labeled with
its bus type (CAN, CAN-FD, XCP, etc.). Dark navy background, gold accents,
English labels, no people, no extra decoration. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
group VCU CAN and Calibration tool on the left, MCU in the middle, FOC + SVPWM on the right
draw the diagnostic path (UDS/XCP) below the main control chain
use a slightly different stroke color for diagnostic links versus torque-command links
ensure every arrow has a bus label
```

---

## 本方案归档清单（生成完一张就勾）

| 图 ID | 优先级 | PNG | prompt.txt |
|---|---|---|---|
| IMG-S01-T01 driver | P0 | [ ] | [ ] |
| IMG-S01-T02 sequence | P2 | [ ] | [ ] |
| IMG-S01-T03 state machine | P0 | [ ] | [ ] |
| IMG-S01-T04 PCB | P1 | [ ] | [ ] |
| IMG-S01-T05 CAD | P1 | [ ] | [ ] |
| IMG-S01-T06 BOM tree | P2 | [ ] | [ ] |
| IMG-S01-T07 Test tree | P2 | [ ] | [ ] |
| IMG-S01-T08 protocol | P1 | [ ] | [ ] |
