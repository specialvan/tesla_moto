# S06 pmasynrm_high_saliency_low_pm 图档分册

方案 ID：`pmasynrm_high_saliency_low_pm`  
工程目录：`engineering/v2/scheme-06/`  
当前草案：仅 README，所有图纸 `missing`。生图标 "concept page"。  
本分册产出落点：`engineering/v2/scheme-06/illustrations/`

> 通用风格 token 与负向 prompt 见 `image_worklist_2026-05-18/README.md` §1。`<STYLE>` = §1.1。

---

## IMG-S06-T01 驱动设计图

- 优先级：**P0**
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T01-driver_block-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §6 驱动设计图
- 工作流：mermaid → 改图

### 提示词

```text
Flat technical block diagram of a PMaSynRM high-saliency low-PM traction
control chain. Layout left-to-right: "Torque request" -> "High-saliency MTPA
table" -> "Field weakening / MTPV switch" -> "Low-PM demag boundary monitor"
-> "FOC current controller" -> "PWM" -> "Inverter" -> "PMaSynRM motor".
A feedback path returns current, position, Vdc, and temperature to the
high-saliency MTPA table. Use rectangular nodes with rounded corners, gold
strokes on dark navy background, clean orthogonal connectors, short English
labels. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make the high-saliency MTPA table visually larger
draw the low-PM demag boundary monitor with a red-tinted stroke
use dashed gold stroke for the feedback path
```

---

## IMG-S06-T02 上电时序图

- 优先级：P2
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T02-power_on_sequence-r00.png`
- 参考图：`mmd` —— 同上 §6 上电时序图
- 工作流：mermaid → 改图

### 提示词

```text
UML-style sequence diagram for a PMaSynRM controller power-on sequence with
demag guard. Four vertical lifelines: VCU, MCU, INV, M. Top-to-bottom arrows:
(1) MCU self-loop "load high-saliency MTPA table",
(2) MCU self-loop "load low-PM demag boundary",
(3) MCU to INV "precharge and gate-driver check",
(4) MCU to M "verify rotor alignment",
(5) MCU self-loop "arm demag monitor",
(6) VCU to MCU "enable torque",
(7) MCU self-loop "select MTPA / FW / MTPV by speed, Vdc, T".
Thin gold horizontal arrows on dark navy background, monospace short labels.
Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
add activation bars on MCU during table loading
make the demag monitor arm step red-tinted
keep lifelines visually clean and equidistant
```

---

## IMG-S06-T03 控制器状态机

- 优先级：**P0**
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T03-state_machine-r00.png`
- 参考图：无
- 工作流：纯生图 → 改图

### 提示词

```text
Finite-state-machine diagram for a PMaSynRM high-saliency low-PM controller
with demag guard. States as rounded rectangles arranged in a 2x3 grid,
exact labels:
- "MTPA active"
- "High-saliency FW"
- "MTPV"
- "Low-PM demag guard"
- "Derate"
- "Fault Fallback"
Directed edges with English transition labels showing exactly:
"MTPA boundary reached", "FW margin shrinking", "MTPV boundary",
"demag risk rising", "recover", "fault latch". Flat infographic style, dark
navy background, pale blue node fills, gold stroke and labels, orthogonal
connectors. Caption: "concept page". <STYLE>
```

### 改图微调

```text
preserve every state label and every transition label exactly as written
make "Low-PM demag guard" and "Fault Fallback" red-tinted strokes
ensure MTPA -> High-saliency FW -> MTPV forms a clear horizontal happy path
```

---

## IMG-S06-T04 PCB 页面草案

- 优先级：P1
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T04-pcb_sheet_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图

### 提示词

```text
Conceptual PCB schematic sheet outline for a PMaSynRM controller with low-PM
demag diagnostics. Show labeled functional blocks left-to-right in four
groups: (high-saliency control inputs) id / iq / omega / T sensing;
(demag diagnostic) demag observer input and threshold logic;
(low-PM sensing) extended current sensing for low-PM operating range;
(position) high-resolution position sensor interface.
Annotate signal names in English next to thin gold connectors. Dark navy
background, light grid, no real component footprints. Caption: "concept page".
Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
highlight demag diagnostic block with red-tinted border
draw extended current sensing with thicker traces to indicate higher dynamic range
keep position sensor block visually distinct as precision input
```

---

## IMG-S06-T05 3D/CAD 封装边界

- 优先级：P1
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T05-cad_packaging_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图
- 备注：S06 CAD 重点是 rotor/stator 截面，PM 占比和 barrier / bridge

### 提示词

```text
Conceptual cross-section illustration of a PMaSynRM rotor and stator with
low PM fraction and high saliency. Show: rotor outline with multiple flux
barriers shaped to maximize d-axis reluctance, small magnet pockets between
barriers (clearly less PM area than a conventional IPMSM), magnetic bridges
between barriers, stator with hairpin slot outline, cooling jacket interface
hint around the stator. Flat vector style, dark navy background, soft cyan
and gold accents, English callouts with leader lines indicating "low PM
fraction", "barrier pattern", "magnetic bridge", "hairpin slot",
"cooling jacket". No photorealism. Caption: "concept page". Aspect ratio 4:3.
<STYLE>
```

### 改图微调

```text
make PM pockets visibly smaller than barrier slots to emphasize low-PM design
label d-axis and q-axis distinctly
mark hairpin slot outline as a distinct shape (not generic round slots)
remove any decorative magnet field arrows
```

---

## IMG-S06-T06 BOM / EDA 风险树

- 优先级：P2
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T06-bom_eda_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Infographic-style component family risk tree for a PMaSynRM high-saliency
low-PM motor. Root node at top: "PMaSynRM low-PM motor". Four first-level
branches: "Low-PM magnets", "Laminations", "Hairpin windings",
"Cooling / temperature sensing". Each branch has 2-3 leaves. Each leaf
carries a LOW / MED / HIGH risk pill, color-coded green / amber / red.
Dark navy background, gold trunk strokes, English labels. Aspect ratio 4:3.
<STYLE>
```

### 改图微调

```text
make Low-PM magnets branch use a slightly different color to indicate cost-driven choice
emphasize Hairpin windings branch (manufacturing risk)
keep tree top-down
```

---

## IMG-S06-T07 测试树

- 优先级：P2
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T07-test_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Left-to-right tree diagram of a verification plan. Root on the left:
"PMaSynRM low-PM verification". Level-1 branches:
"Torque ripple", "Mechanical stress", "Demagnetization", "Thermal", "NVH".
Level-2 leaves are short English acceptance hooks. Clean vector style,
dark navy background, gold and pale blue accents, monospace labels for
test IDs. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
group Demagnetization and Thermal near each other
make Demagnetization leaves red-tinted strokes
add small NVH waveform icon near NVH branch
```

---

## IMG-S06-T08 协议链路图

- 优先级：P1
- 目标：`engineering/v2/scheme-06/illustrations/V2-S06-ILL-T08-protocol_link-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §6 协议链路图
- 工作流：mermaid → 改图

### 提示词

```text
Network-style block diagram of communication links for a PMaSynRM controller.
Nodes: "VCU CAN", "MCU command parser",
"Saliency control telemetry + demag warning channel", "FOC controller",
"SVPWM", "UDS / XCP diagnostics", "Calibration tool". Arrows: VCU CAN -> MCU;
MCU -> Saliency control telemetry; MCU -> FOC -> SVPWM; FOC -> Saliency
control telemetry (feedback); MCU -> UDS / XCP; Calibration tool -> MCU.
Each link labeled with its bus type. Dark navy background, gold accents,
English labels. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
highlight Saliency control telemetry + demag warning channel as routing hub
make demag-warning related links red-tinted
group request side on left, feedback on right
```

---

## 本方案归档清单

| 图 ID | 优先级 | PNG | prompt.txt |
|---|---|---|---|
| IMG-S06-T01 driver | P0 | [ ] | [ ] |
| IMG-S06-T02 sequence | P2 | [ ] | [ ] |
| IMG-S06-T03 state machine | P0 | [ ] | [ ] |
| IMG-S06-T04 PCB | P1 | [ ] | [ ] |
| IMG-S06-T05 CAD | P1 | [ ] | [ ] |
| IMG-S06-T06 BOM tree | P2 | [ ] | [ ] |
| IMG-S06-T07 Test tree | P2 | [ ] | [ ] |
| IMG-S06-T08 protocol | P1 | [ ] | [ ] |
