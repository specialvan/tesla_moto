# S02 mtpa_fw_mtpv_control 图档分册

方案 ID：`mtpa_fw_mtpv_control`  
工程目录：`engineering/v2/scheme-02/`  
当前草案：PCB / CAD / Controller / BOM / DVP 已落 markdown / drawio 草案。  
本分册产出落点：`engineering/v2/scheme-02/illustrations/`

> 通用风格 token 与负向 prompt 见 `image_worklist_2026-05-18/README.md` §1。`<STYLE>` = §1.1。

---

## IMG-S02-T01 驱动设计图

- 优先级：**P0**
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T01-driver_block-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §2 驱动设计图
- 工作流：mermaid 渲染 PNG → 改图，或纯生图
- 验收：能看到 LUT 块吃 torque 请求 → feasibility / derating → current controller → PWM → inverter → motor 的反馈回路

### 提示词

```text
Flat technical block diagram of an EV traction control chain centered on an
MTPA / FW / MTPV LUT. Layout left-to-right: "Vehicle torque request" ->
"MTPA / FW / MTPV LUT" -> "Feasibility + Derating" -> "Current Controller" ->
"PWM Modulator" -> "Inverter" -> "Motor". A bottom feedback loop labeled
"Position + Current + Vdc Feedback" returns from the Motor back into the LUT.
Use rectangular nodes with rounded corners, gold strokes on dark navy
background, clean orthogonal connectors with arrowheads, short English labels.
Aspect ratio 16:9, single image, no people, no marketing copy. <STYLE>
```

### 改图微调

```text
make the MTPA / FW / MTPV LUT block visually larger and brighter than the others
draw the feedback loop with a clearly different stroke style (dashed gold)
keep the seven main blocks in a single straight horizontal row
```

---

## IMG-S02-T02 上电时序图

- 优先级：P2
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T02-power_on_sequence-r00.png`
- 参考图：`mmd` —— 同上 §2 上电时序图
- 工作流：mermaid → 改图
- 验收：4 条 lifeline（MCU / NVM / INV / VCU），能看到 LUT 加载 + CRC、precharge、模式选择

### 提示词

```text
UML-style sequence diagram for an EV traction controller power-on procedure
specific to MTPA / FW / MTPV LUT-based control. Four vertical lifelines:
MCU, NVM, INV, VCU. Top-to-bottom horizontal arrows in this order:
(1) MCU to NVM "load control LUT and CRC",
(2) MCU self-loop "validate unit convention and bounds",
(3) MCU to INV "precharge and gate-driver check",
(4) MCU self-loop "resolver / encoder check",
(5) MCU self-loop "set mode = MTPA idle",
(6) VCU to MCU "enable torque",
(7) MCU self-loop "choose MTPA / FW / MTPV by speed, Vdc, T".
Thin gold horizontal arrows on dark navy background, monospace short labels,
no decoration, no human figures. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
add a thin vertical activation bar on MCU lifeline during LUT load and validate
make NVM lifeline a slightly different color to indicate persistent storage role
align all arrow labels horizontally
```

---

## IMG-S02-T03 控制器状态机

- 优先级：**P0**
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T03-state_machine-r00.png`
- 参考图：`drawio` —— `engineering/v2/scheme-02/controller/V2-S02-CTRL-mode_transition_lut-r00.drawio`
- 工作流：**强烈建议改图模式**
- 验收：6 状态、6 转移条件全部保留

### 提示词

```text
Finite-state-machine diagram for a motor controller running MTPA / FW / MTPV
mode switching with LUT CRC protection. States as rounded rectangles arranged
in a 2x3 grid, exact labels:
- "MTPA idle"
- "MTPA active"
- "Field Weakening"
- "MTPV"
- "Derate"
- "LUT CRC fault fallback"
Directed edges with English transition labels showing exactly:
"LUT CRC ok", "speed > base", "V margin < limit", "MTPV boundary reached",
"LUT CRC fail", "mode reset". Flat infographic style, dark navy background,
pale blue node fills, gold stroke and labels, orthogonal connectors,
no shadows, no people, single image. <STYLE>
```

### 改图微调

```text
preserve every state label and every transition label exactly as written
make "LUT CRC fault fallback" use a red-tinted stroke to indicate fault state
keep MTPA idle and MTPA active visually adjacent
ensure mode transitions form a clear progression: idle -> active -> FW -> MTPV
```

---

## IMG-S02-T04 PCB 页面草案

- 优先级：P1
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T04-pcb_sheet_concept-r00.png`
- 参考图：无 —— `engineering/v2/scheme-02/pcb/V2-S02-PCB-control_io_map-r00.md` 文字
- 工作流：纯生图 v0 → 改图
- 验收：MCU + NVM、ADC、位置、通信、LUT 诊断 5 个功能组清晰

### 提示词

```text
Conceptual PCB schematic sheet outline for an MTPA / FW / MTPV controller
board. Show labeled functional blocks left-to-right in five groups:
(MCU core) MCU and NVM for control LUT storage, watchdog;
(analog front-end) ADC front-end for phase current and Vdc;
(position) resolver / encoder interface;
(communication) CAN / CAN-FD transceiver, optional FlexRay;
(LUT release) LUT version diagnostic interface, calibration port.
Annotate signal names in English next to thin gold connectors. Dark navy
background, light grid, no real component footprints, no part numbers. Make it
clearly a "page-level concept", not a manufacturable layout. Aspect ratio 4:3.
<STYLE>
```

### 改图微调

```text
group blocks within each functional group inside a thin gold dashed bounding box
label each bounding box with the group name (MCU core, analog front-end, position, communication, LUT release)
highlight the LUT release block with slightly brighter gold border
remove any pretend chip pin numbers; only show signal name labels
```

---

## IMG-S02-T05 3D/CAD 封装边界

- 优先级:P1
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T05-cad_packaging_concept-r00.png`
- 参考图：无 —— `engineering/v2/scheme-02/cad/V2-S02-CAD-controller_packaging-r00.md` 文字
- 工作流：纯生图 v0 → 改图
- 验收：壳体、连接器、线束出口、冷却面、EMI 分区可见

### 提示词

```text
Isometric concept illustration of an EV motor controller enclosure showing
mechanical packaging boundary. Show: a rectangular controller housing, multiple
connector positions on one face for power, signal, communication, and service;
harness exits with strain relief; a cooling interface plate against the power
module on one side; an internal EMI partition wall separating LV control
section from HV power section. Flat vector style, dark navy background,
soft cyan and gold accents, English labels with leader lines. No photorealism,
no human figures, no manufacturer branding. Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
label every connector with its function (power, signal, comms, service)
draw the EMI partition wall as a dashed gold plane
keep all leader lines straight and non-overlapping
remove any pretend assembly screws or fasteners
```

---

## IMG-S02-T06 BOM / EDA 风险树

- 优先级：P2
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T06-bom_eda_tree-r00.png`
- 参考图：无
- 工作流：纯生图
- 验收：5 个一级分支 + 子节点 + LOW/MED/HIGH 胶囊

### 提示词

```text
Infographic-style component family risk tree for an MTPA / FW / MTPV motor
controller. Root node centered at top labeled "MTPA / FW / MTPV controller".
Five first-level branches: "MCU + NVM", "ADC", "Position interface",
"Communication transceivers", "LUT release infrastructure". Each branch has 2-3
leaves representing component subfamilies. Each leaf carries a small
pill-shaped risk badge LOW / MED / HIGH, color-coded green / amber / red.
Dark navy background, gold trunk strokes, color-coded risk pills, English
labels, no real manufacturer logos. Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
make MCU + NVM branch slightly emphasized with thicker gold stroke
keep tree purely top-down
make HIGH risk pills slightly larger
```

---

## IMG-S02-T07 测试树

- 优先级：P2
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T07-test_tree-r00.png`
- 参考图：无
- 工作流：纯生图
- 验收：4 条 axis，每条 2-3 个 hook

### 提示词

```text
Left-to-right tree diagram of a verification plan. Root on the left:
"MTPA / FW / MTPV control verification". Level-1 branches:
"MTPA / FW / MTPV HIL", "LUT CRC and version control",
"Power-off recovery", "Mode continuity". Level-2 leaves are short English
acceptance hooks, for example "mode latency < 1 ms",
"CRC fail triggers fallback", "LUT version visible in diagnostics",
"transition torque step bounded". Clean vector style, dark navy background,
gold and pale blue accents, monospace labels for test IDs.
No people, no labs. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
align level-2 leaves vertically by branch
add a small HIL badge near "MTPA / FW / MTPV HIL" branch
make CRC-related leaves visually grouped
```

---

## IMG-S02-T08 协议链路图

- 优先级：P1
- 目标：`engineering/v2/scheme-02/illustrations/V2-S02-ILL-T08-protocol_link-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §2 协议链路图
- 工作流：mermaid → 改图
- 验收：mode selector、id/iq reference LUT、status return path、XCP calibration 都能看到

### 提示词

```text
Network-style block diagram of communication and control links for an MTPA /
FW / MTPV controller. Nodes: "CAN torque / speed request",
"Command arbitration", "Mode selector (MTPA / FW / MTPV)",
"id/iq reference LUT", "FOC", "Status (mode, margins, derate)",
"XCP calibration". Arrows: CAN -> Command arbitration -> Mode selector ->
id/iq reference LUT -> FOC; FOC -> Status -> CAN (return); XCP calibration
-> id/iq reference LUT. Each link labeled with its bus type. Dark navy
background, gold accents, English labels, no people. Aspect ratio 16:9.
<STYLE>
```

### 改图微调

```text
group request side on the left and feedback / status on the right
use a slightly different stroke color for calibration link versus normal control link
make Mode selector visually highlighted as the routing hub
ensure every arrow has a bus label
```

---

## 本方案归档清单

| 图 ID | 优先级 | PNG | prompt.txt |
|---|---|---|---|
| IMG-S02-T01 driver | P0 | [ ] | [ ] |
| IMG-S02-T02 sequence | P2 | [ ] | [ ] |
| IMG-S02-T03 state machine | P0 | [ ] | [ ] |
| IMG-S02-T04 PCB | P1 | [ ] | [ ] |
| IMG-S02-T05 CAD | P1 | [ ] | [ ] |
| IMG-S02-T06 BOM tree | P2 | [ ] | [ ] |
| IMG-S02-T07 Test tree | P2 | [ ] | [ ] |
| IMG-S02-T08 protocol | P1 | [ ] | [ ] |
