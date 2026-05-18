# S03 svpwm_overmodulation_voltage_utilization 图档分册

方案 ID：`svpwm_overmodulation_voltage_utilization`  
工程目录：`engineering/v2/scheme-03/`  
当前草案：仅 README，所有图纸 `missing`。生图须明确标 "concept page"。  
本分册产出落点：`engineering/v2/scheme-03/illustrations/`

> 通用风格 token 与负向 prompt 见 `image_worklist_2026-05-18/README.md` §1。`<STYLE>` = §1.1。

---

## IMG-S03-T01 驱动设计图

- 优先级：**P0**
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T01-driver_block-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §3 驱动设计图
- 工作流：mermaid → 改图，或纯生图
- 验收：FOC voltage → SVPWM/Overmod/Six-step Selector → PWM → Gate driver → Inverter → Motor，且 Vdc Sense 与 THD/NVH Monitor 反馈进入 selector

### 提示词

```text
Flat technical block diagram of an EV traction inverter modulation chain.
Layout left-to-right: "FOC voltage command" -> "SVPWM / Overmod / Six-step
Selector" -> "PWM Compare" -> "Gate Driver" -> "Inverter Bridge" -> "Motor".
Below the chain, two feedback inputs labeled "Vdc Sense" and
"THD / NVH Monitor" feed into the Selector block. Use rectangular nodes with
rounded corners, gold strokes on dark navy background, clean orthogonal
connectors with arrowheads, short English labels. Aspect ratio 16:9, single
image, no people, no marketing copy. <STYLE>
```

### 改图微调

```text
make the SVPWM / Overmod / Six-step Selector visually larger to indicate routing hub
use a dashed gold stroke for the feedback inputs (Vdc, THD/NVH)
keep main chain straight and horizontal
```

---

## IMG-S03-T02 上电时序图

- 优先级：P2
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T02-power_on_sequence-r00.png`
- 参考图：`mmd` —— 同上 §3 上电时序图
- 工作流：mermaid → 改图

### 提示词

```text
UML-style sequence diagram for an EV inverter modulation subsystem power-on.
Three vertical lifelines: MCU, GD (gate driver), INV. Top-to-bottom horizontal
arrows: (1) MCU self-loop "load modulation limits",
(2) MCU to GD "gate-driver self-test", (3) GD to MCU "ack ok",
(4) MCU to INV "enable inverter outputs",
(5) MCU self-loop "set modulation mode = linear SVPWM",
(6) MCU self-loop "arm THD / NVH monitors".
Thin gold horizontal arrows on dark navy background, monospace short labels.
No decoration. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
add a thin vertical activation bar on MCU lifeline during modulation-limit loading
align all arrow labels horizontally
```

---

## IMG-S03-T03 控制器状态机

- 优先级：**P0**
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T03-state_machine-r00.png`
- 参考图：无 —— 仓库无 `.drawio`，纯生图 v0
- 工作流：纯生图 → 多轮改图
- 验收：5-6 状态 + 5 转移，能看到 SVPWM、Overmodulation Region 1/2、Six-Step、Derate、Fallback

### 提示词

```text
Finite-state-machine diagram for an inverter modulation controller. States as
rounded rectangles arranged in a 2x3 grid, exact labels:
- "Linear SVPWM"
- "Overmodulation Region 1"
- "Overmodulation Region 2"
- "Six-Step"
- "Derate on THD limit"
- "Fallback to linear"
Directed edges with English transition labels showing exactly:
"voltage utilization rising", "THD limit hit", "NVH limit hit",
"Vdc recovered", "safety derate request". Flat infographic style, dark navy
background, pale blue node fills, gold stroke and labels, orthogonal
connectors, no shadows, no people, single image. Mark with a small caption
"concept page, no real layout". <STYLE>
```

### 改图微调

```text
preserve every state label and every transition label exactly as written
arrange progression top-left "Linear SVPWM" -> right -> "Six-Step"
use a slightly red-tinted stroke for "Derate on THD limit" and "Fallback to linear"
ensure no two arrows overlap
```

---

## IMG-S03-T04 PCB 页面草案

- 优先级：P1
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T04-pcb_sheet_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图

### 提示词

```text
Conceptual PCB schematic sheet outline for a power inverter modulation board.
Show labeled functional blocks left-to-right in five groups:
(gate drive) gate driver with dead-time control, isolation;
(EMC) EMC / EMI filter network;
(sensing) phase current sensing, Vdc sensing;
(DC link) DC-link capacitor bank;
(power interface) bus bar interface to inverter modules.
Annotate signal names in English next to thin gold connectors. Dark navy
background, light grid, no real component footprints, no part numbers.
Caption: "concept page, no real layout". Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
group blocks within each functional group inside a thin gold dashed bounding box
highlight gate driver dead-time line with thicker gold stroke
remove any pretend chip pin numbers
```

---

## IMG-S03-T05 3D/CAD 封装边界

- 优先级：P1
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T05-cad_packaging_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图

### 提示词

```text
Isometric concept illustration of an EV inverter power stage mechanical
packaging. Show: a power module assembly at the center, DC-link capacitor bank
adjacent to the power module, three rectangular busbars connecting power
module to motor terminals, a heatsink / cold plate interface below the power
module, EMI shielding partitions around the modulation stage. Flat vector
style, dark navy background, soft cyan and gold accents, English labels with
leader lines. No photorealism, no manufacturer branding.
Caption: "concept page, no real layout". Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
label busbars with phase letters A/B/C
draw the EMI shielding partitions as dashed gold planes
keep heatsink as a simple plate, no fins detail
```

---

## IMG-S03-T06 BOM / EDA 风险树

- 优先级：P2
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T06-bom_eda_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Infographic-style component family risk tree for an inverter overmodulation
power stage. Root node at top: "SVPWM / overmodulation power stage". Five
first-level branches: "Gate driver", "Power modules", "DC-link capacitors",
"Busbar", "EMI components". Each branch has 2-3 leaves. Each leaf carries a
LOW / MED / HIGH risk pill, color-coded green / amber / red. Dark navy
background, gold trunk strokes, English labels, no logos. Aspect ratio 4:3.
<STYLE>
```

### 改图微调

```text
make Power modules branch slightly emphasized
align all first-level branches at same vertical level
keep tree purely top-down
```

---

## IMG-S03-T07 测试树

- 优先级：P2
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T07-test_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Left-to-right tree diagram of a verification plan. Root on the left:
"SVPWM / overmodulation verification". Level-1 branches:
"THD measurement", "EMC compliance", "NVH (torque ripple)",
"Inverter loss", "Thermal stress". Level-2 leaves are short English
acceptance hooks. Clean vector style, dark navy background, gold and pale
blue accents, monospace labels for test IDs. No people, no labs.
Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
group THD and NVH branches near each other (both signal-quality related)
add a small EMC chamber badge near the EMC branch
align level-2 leaves by branch
```

---

## IMG-S03-T08 协议链路图

- 优先级：P1
- 目标：`engineering/v2/scheme-03/illustrations/V2-S03-ILL-T08-protocol_link-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §3 协议链路图
- 工作流：mermaid → 改图

### 提示词

```text
Network-style block diagram of communication and telemetry links for an
inverter modulation subsystem. Nodes: "VCU CAN", "MCU command parser",
"Modulation mode telemetry + THD / NVH guard channel", "FOC controller",
"SVPWM core", "UDS / XCP diagnostics", "Calibration tool". Arrows: VCU CAN
-> MCU; MCU -> Modulation mode telemetry; MCU -> FOC -> SVPWM core;
SVPWM core -> Modulation mode telemetry (feedback); MCU -> UDS / XCP;
Calibration tool -> MCU. Each link labeled with its bus type. Dark navy
background, gold accents, English labels. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make Modulation mode telemetry block visually highlighted as the routing hub
use a different stroke color for diagnostic links versus normal control links
keep main control chain horizontal across the top
```

---

## 本方案归档清单

| 图 ID | 优先级 | PNG | prompt.txt |
|---|---|---|---|
| IMG-S03-T01 driver | P0 | [ ] | [ ] |
| IMG-S03-T02 sequence | P2 | [ ] | [ ] |
| IMG-S03-T03 state machine | P0 | [ ] | [ ] |
| IMG-S03-T04 PCB | P1 | [ ] | [ ] |
| IMG-S03-T05 CAD | P1 | [ ] | [ ] |
| IMG-S03-T06 BOM tree | P2 | [ ] | [ ] |
| IMG-S03-T07 Test tree | P2 | [ ] | [ ] |
| IMG-S03-T08 protocol | P1 | [ ] | [ ] |
