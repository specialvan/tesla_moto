# S05 magnetic_saturation_codesign 图档分册

方案 ID：`magnetic_saturation_codesign`  
工程目录：`engineering/v2/scheme-05/`  
当前草案：仅 README，所有图纸 `missing`。生图标 "concept page"。  
本分册产出落点：`engineering/v2/scheme-05/illustrations/`

> 通用风格 token 与负向 prompt 见 `image_worklist_2026-05-18/README.md` §1。`<STYLE>` = §1.1。

---

## IMG-S05-T01 驱动设计图

- 优先级：**P0**
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T01-driver_block-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §5 驱动设计图
- 工作流：mermaid → 改图

### 提示词

```text
Flat technical block diagram of a magnetic saturation codesign pipeline.
Layout left-to-right: "Candidate geometry generator" -> "FEA solver" ->
"lambda_d / lambda_q LUT" -> "Scorecard evaluator (torque, voltage margin,
iron loss, demag, rotor stress, NVH)" -> "Down-select decision" -> "Control
LUT feed". Use rectangular nodes with rounded corners, gold strokes on dark
navy background, clean orthogonal connectors with arrowheads, short English
labels. Aspect ratio 16:9, single image. Caption: "concept page". <STYLE>
```

### 改图微调

```text
make the Scorecard evaluator visually larger to indicate decision center
use dashed gold strokes for the loop back from Down-select to Candidate generator
group inputs to the Scorecard as labeled small icons (torque, loss, demag, stress)
```

---

## IMG-S05-T02 上电时序图

- 优先级：P2
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T02-power_on_sequence-r00.png`
- 参考图：`mmd` —— 同上 §5 上电时序图
- 工作流：mermaid → 改图

### 提示词

```text
UML-style sequence diagram for a saturation codesign pipeline kickoff.
Four vertical lifelines: Designer, FEA, Scorecard, Reviewer. Top-to-bottom
horizontal arrows: (1) Designer to FEA "submit candidate geometry",
(2) FEA self-loop "solve lambda maps",
(3) FEA to Scorecard "deliver lambda_d / lambda_q LUT",
(4) Scorecard self-loop "evaluate torque, loss, demag, stress, NVH",
(5) Scorecard to Reviewer "send pareto ranking",
(6) Reviewer to Designer "approve, retain, or stop". Thin gold horizontal
arrows on dark navy background, monospace short labels. Aspect ratio 16:9.
<STYLE>
```

### 改图微调

```text
add an activation bar on FEA lifeline during solving
make Scorecard arrows visually distinct as decision step
```

---

## IMG-S05-T03 控制器状态机

- 优先级：**P0**
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T03-state_machine-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图
- 备注：S05 没有真正"控制器状态机"，本图描述"候选评审状态机"

### 提示词

```text
Finite-state-machine diagram for a saturation codesign candidate evaluation
loop. States as rounded rectangles arranged in a 2x3 grid, exact labels:
- "Candidate geometry intake"
- "FEA LUT request"
- "Scorecard evaluation"
- "Down-select"
- "Stop-criteria triggered"
- "Retain for trade study"
Directed edges with English transition labels showing exactly:
"FEA result available", "score above threshold", "stress / demag risk too high",
"pareto loser", "retain". Flat infographic style, dark navy background, pale
blue node fills, gold stroke and labels, orthogonal connectors. Caption:
"concept page, no real layout". <STYLE>
```

### 改图微调

```text
preserve every state label and every transition label exactly as written
make "Stop-criteria triggered" use a red-tinted stroke
align Candidate intake -> FEA -> Scorecard horizontally as the happy path
```

---

## IMG-S05-T04 PCB 页面草案

- 优先级：P1
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T04-pcb_sheet_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图
- 备注：S05 PCB 内容偏 saturation observer，重在采样输入

### 提示词

```text
Conceptual PCB schematic sheet outline for a saturation observer board. Show
labeled functional blocks left-to-right in four groups:
(observer inputs) saturation observer sample inputs;
(diagnostics) flux estimation diagnostics readback;
(compute) MCU compute headroom block;
(bench port) optional bench data ingestion port for calibration.
Annotate signal names in English next to thin gold connectors. Dark navy
background, light grid, no real component footprints. Caption: "concept page".
Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
keep diagnostics path drawn with a dashed gold stroke
highlight MCU compute headroom block with a small chip-shaped icon
remove any pretend chip pin numbers
```

---

## IMG-S05-T05 3D/CAD 封装边界

- 优先级：P1
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T05-cad_packaging_concept-r00.png`
- 参考图：无
- 工作流：纯生图 v0 → 改图
- 备注：S05 CAD 内容偏 rotor 截面（barrier / bridge），不是 inverter 封装

### 提示词

```text
Conceptual cross-section illustration of an IPMSM rotor lamination showing
saturation codesign features. Show: rotor outline with multiple flux barriers
(dark slots), magnetic bridges (thin bridges of steel between barriers),
embedded magnet pockets, stator slot outline around the rotor, lamination
stack hint at the edges, mechanical stress callouts on bridges. Flat vector
style, dark navy background, soft cyan and gold accents, English callouts
with leader lines. No photorealism, no manufacturer branding. Caption:
"concept page". Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
label flux barriers as "barrier 1", "barrier 2", "barrier 3" radially
label magnetic bridges with leader lines indicating stress concentration
mark stator slot outline as a thin gold ring around the rotor
remove any decorative magnet field arrows
```

---

## IMG-S05-T06 BOM / EDA 风险树

- 优先级：P2
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T06-bom_eda_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Infographic-style component family risk tree for a saturation codesign motor.
Root node at top: "magnetic saturation codesign motor". Four first-level
branches: "Electrical steel", "Permanent magnets", "Rotor process tooling",
"Saturation observer sensors". Each branch has 2-3 leaves. Each leaf carries
a LOW / MED / HIGH risk pill, color-coded green / amber / red. Dark navy
background, gold trunk strokes, English labels. Aspect ratio 4:3. <STYLE>
```

### 改图微调

```text
make Permanent magnets branch emphasized (supply risk usually HIGH)
keep tree top-down
make HIGH pills slightly larger
```

---

## IMG-S05-T07 测试树

- 优先级：P2
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T07-test_tree-r00.png`
- 参考图：无
- 工作流：纯生图

### 提示词

```text
Left-to-right tree diagram of a verification plan. Root on the left:
"saturation codesign verification". Level-1 branches:
"FEA correlation", "Mechanical stress", "Iron loss", "Demagnetization", "NVH".
Level-2 leaves are short English acceptance hooks. Clean vector style,
dark navy background, gold and pale blue accents, monospace labels for
test IDs. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
group Mechanical stress and Demagnetization branches near each other (both safety)
add a small FEA badge near FEA correlation branch
make leaves under Demagnetization use slightly red-tinted stroke
```

---

## IMG-S05-T08 协议链路图

- 优先级：P1
- 目标：`engineering/v2/scheme-05/illustrations/V2-S05-ILL-T08-protocol_link-r00.png`
- 参考图：`mmd` —— `reports/scheme_driver_power_protocol_diagrams.md` §5 协议链路图
- 工作流：mermaid → 改图

### 提示词

```text
Network-style block diagram of data and review links for the saturation
codesign workflow. Nodes: "Candidate geometry repository", "FEA toolchain",
"lambda LUT exchange channel", "Scorecard service",
"Candidate ID + score versioning channel", "Review board". Arrows:
Candidate geometry repository -> FEA toolchain; FEA toolchain ->
lambda LUT exchange channel -> Scorecard service; Scorecard service ->
Candidate ID + score versioning channel -> Review board; Review board ->
Candidate geometry repository (feedback). Each link labeled with its data
format (STEP, LUT JSON, score JSON, review PDF). Dark navy background, gold
accents, English labels. Aspect ratio 16:9. <STYLE>
```

### 改图微调

```text
make Candidate ID + score versioning channel visually highlighted as audit hub
use dashed gold stroke for the feedback loop from Review board
keep main pipeline horizontal across the top
```

---

## 本方案归档清单

| 图 ID | 优先级 | PNG | prompt.txt |
|---|---|---|---|
| IMG-S05-T01 driver | P0 | [ ] | [ ] |
| IMG-S05-T02 sequence | P2 | [ ] | [ ] |
| IMG-S05-T03 state machine | P0 | [ ] | [ ] |
| IMG-S05-T04 PCB | P1 | [ ] | [ ] |
| IMG-S05-T05 CAD | P1 | [ ] | [ ] |
| IMG-S05-T06 BOM tree | P2 | [ ] | [ ] |
| IMG-S05-T07 Test tree | P2 | [ ] | [ ] |
| IMG-S05-T08 protocol | P1 | [ ] | [ ] |
