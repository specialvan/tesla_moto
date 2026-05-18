# S07 variable_magnetization_memory_motor 图档分册

方案 ID：`variable_magnetization_memory_motor`  
工程目录：`engineering/v2/scheme-07/`  
当前草案：仅 README，所有图纸 `missing`。本方案属于 **research-pool**，所有生图必须加 "research-pool concept, not engineering release" caption。  
本分册产出落点：`engineering/v2/scheme-07/illustrations/`

> 通用风格 token 与负向 prompt 见 `image_worklist_2026-05-18/README.md` §1。`<STYLE>` = §1.1。

---

## IMG-S07-T01 驱动设计图

- 优先级：**P0**
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T01-driver_block-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §7 驱动设计图
- 工作流：mermaid → 改图

### 提示词

```text
Flat technical block diagram of a memory-motor variable magnetization control
chain. Layout left-to-right: "DC link" -> "Pulse capacitor bank" ->
"Bi-directional pulse driver" -> "Memory motor" (with embedded variable-state
magnets), and in parallel "3-phase traction inverter" -> "Memory motor".
A top control row contains: "MCU", "Pulse current monitor",
"Flux state observer", "Interlock with traction inverter". MCU drives both
the pulse driver and the traction inverter; pulse current monitor feeds back
to MCU; flux state observer reads back to MCU. Use rectangular nodes with
rounded corners, gold strokes on dark navy background, clean orthogonal
connectors, short English labels. Caption: "research-pool concept,
not engineering release". Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make the Pulse capacitor bank visually larger to indicate energy storage
draw the interlock link with red-tinted stroke to indicate safety-critical
keep traction inverter path visually parallel and below the pulse path
```

---

## IMG-S07-T02 上电时序图

- 优先级：P2
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T02-power_on_sequence-r00.png`
- 参考图：`mmd` —— 同上 §7 上电时序图
- 工作流：mermaid → 改图

### 提示词

```text
UML-style sequence diagram for a memory-motor power-on and magnetization
session. Five vertical lifelines: VCU, MCU, PulseStage, INV, Motor.
Top-to-bottom arrows: (1) MCU self-loop "self-test sensors and interlock",
(2) MCU to PulseStage "pre-charge energy bank",
(3) PulseStage to MCU "bank ready",
(4) MCU to PulseStage "apply magnetization pulse",
(5) Motor to MCU "flux state observed",
(6) MCU self-loop "update lifetime cycle count",
(7) MCU to INV "enable traction torque". Thin gold horizontal arrows on
dark navy background, monospace short labels. Caption:
"research-pool concept". Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
add activation bars on PulseStage during pre-charge and pulse apply
make the pulse-apply arrow visually thicker
draw interlock-related lines red-tinted
```

---

## IMG-S07-T03 控制器状态机

- 优先级：**P0**
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T03-state_machine-r00.png`
- 参考图：无
- 工作流：纯生图 → 改图

### 提示词

```text
Finite-state-machine diagram for a memory-motor magnetization state controller.
States as rounded rectangles arranged in a 3x3 grid (with one cell empty),
exact labels:
- "Magnetization idle"
- "Pre-charge energy bank"
- "Apply magnetization pulse"
- "Apply de-magnetization pulse"
- "Verify flux state"
- "Unknown-state fallback"
- "Lifetime cycle count update"
- "Safe retreat"
Directed edges with English transition labels showing exactly:
"bank ready", "pulse trigger", "state observed ok", "state unknown",
"cycle limit reached", "safe retreat". Flat infographic style, dark navy
background, pale blue node fills, gold stroke and labels, orthogonal
connectors. Caption: "research-pool concept, not engineering release".
<STYLE>
```

### 改图微调

```text
preserve every state label and every transition label exactly as written
make "Unknown-state fallback" and "Safe retreat" red-tinted strokes
arrange so Magnetization idle -> Pre-charge -> Apply pulse -> Verify -> Lifetime
forms a clear progression
```

---

## IMG-S07-T04 PCB 页面草案

- 优先级：P1
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T04-pcb_sheet_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图
- 备注：S07 PCB 涉及高能脉冲电路，画感强、危险性高

### 提示词

```text
Conceptual PCB schematic sheet outline for a memory-motor magnetization pulse
driver board. Show labeled functional blocks left-to-right in five groups:
(energy storage) pulse capacitor bank, charging path;
(power switch) bi-directional pulse driver bridge;
(sensing) pulse current sensing with high bandwidth;
(isolation) isolation barrier between pulse stage and traction logic;
(interlock) hardware interlock with traction inverter enable.
Annotate signal names in English next to thin gold connectors. Dark navy
background, light grid, no real component footprints. Caption:
"research-pool concept, no real layout". Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
highlight the interlock block with red-tinted border
draw isolation barrier as a clearly visible vertical dashed line dividing the sheet
emphasize pulse capacitor bank visually as a large rectangular group
```

---

## IMG-S07-T05 3D/CAD 封装边界

- 优先级：P1
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T05-cad_packaging_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图

### 提示词

```text
Conceptual cross-section illustration of a memory motor showing variable-state
magnets and magnetization path. Show: rotor outline with embedded
"memory magnets" labeled distinctly, magnetization path arrows through the
rotor magnetic circuit (concept only), stator with windings hint, thermal
path callouts indicating temperature drift sensitivity. Flat vector style,
dark navy background, soft cyan and gold accents, English callouts with
leader lines. No photorealism. Caption: "research-pool concept,
not engineering release". Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
make memory magnets visually distinct from any "regular" PM (use a different fill texture)
draw magnetization path arrows in a dashed gold stroke
label "temperature drift sensitivity" prominently
```

---

## IMG-S07-T06 BOM / EDA 风险树

- 优先级：P2
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T06-bom_eda_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Infographic-style component family risk tree for a memory-motor variable
magnetization subsystem. Root node at top:
"variable magnetization memory motor". Five first-level branches:
"Pulse power stage", "Energy storage", "Magnet materials",
"Flux state observers", "Safety isolation". Each branch has 2-3 leaves. Each
leaf carries a LOW / MED / HIGH risk pill, color-coded green / amber / red.
Dark navy background, gold trunk strokes, English labels. Caption:
"research-pool concept". Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
make Magnet materials and Safety isolation branches emphasized
keep most leaves at MED or HIGH (this is research-pool)
make HIGH risk pills slightly larger
```

---

## IMG-S07-T07 测试树

- 优先级：P2
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T07-test_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Left-to-right tree diagram of a verification plan. Root on the left:
"memory motor magnetization verification". Level-1 branches:
"Magnetization / demagnetization pulses", "State retention",
"Temperature drift", "Unknown-state fallback", "Lifetime cycling".
Level-2 leaves are short English acceptance hooks. Clean vector style,
dark navy background, gold and pale blue accents, monospace labels for
test IDs. Caption: "research-pool concept". Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make Unknown-state fallback leaves red-tinted
group Magnetization pulses and State retention near each other
add a small cycle-count badge near Lifetime cycling branch
```

---

## IMG-S07-T08 协议链路图

- 优先级：P1
- 目标：`engineering/v2/scheme-07/illustrations/V2-S07-ILL-T08-protocol_link-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §7 协议链路图
- 工作流：mermaid → 改图

### 提示词

```text
Network-style block diagram of communication links for a memory-motor
controller. Nodes: "VCU CAN", "MCU command parser",
"Flux state + lifetime cycle counter telemetry", "Pulse stage controller",
"FOC controller", "SVPWM", "UDS / XCP diagnostics",
"Service-only magnetization session interface". Arrows: VCU CAN -> MCU;
MCU -> Flux state telemetry; MCU -> Pulse stage controller;
MCU -> FOC -> SVPWM; FOC -> Flux state telemetry (feedback);
MCU -> UDS / XCP; Service-only interface -> MCU (gated). Each link labeled
with its bus type. Dark navy background, gold accents, English labels.
Caption: "research-pool concept". Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make Service-only interface link clearly gated (dashed + red badge "service only")
highlight Flux state telemetry as routing hub
draw Pulse stage controller arrow visually thicker
```

---

## 本方案归档清单

| 图 ID | 优先级 | PNG | prompt.txt |
|---|---|---|---|
| IMG-S07-T01 driver | P0 | [ ] | [ ] |
| IMG-S07-T02 sequence | P2 | [ ] | [ ] |
| IMG-S07-T03 state machine | P0 | [ ] | [ ] |
| IMG-S07-T04 PCB | P1 | [ ] | [ ] |
| IMG-S07-T05 CAD | P1 | [ ] | [ ] |
| IMG-S07-T06 BOM tree | P2 | [ ] | [ ] |
| IMG-S07-T07 Test tree | P2 | [ ] | [ ] |
| IMG-S07-T08 protocol | P1 | [ ] | [ ] |
