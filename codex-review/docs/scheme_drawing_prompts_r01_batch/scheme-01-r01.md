# S01 r01 提示词批包 · negative_d_axis_field_weakening

修订日期：2026-05-18
方案 ID：`negative_d_axis_field_weakening`
工程目录：`engineering/v2/scheme-01/`
草案完整度：PCB / CAD / Controller / BOM / DVP&R 全
生产参数来源：`models/motor_params.json`、本方案 PCB / BOM / DVP 草案
输出落点：`gpt-image-2/outputs/S01/V2-S01-ILL-TYY-...-r01.png` 与同名 `-r01-prompt.txt`

---

## 0. SCHEME_TITLE 锁定

| 模板 | SCHEME_TITLE 文本 |
|---|---|
| T01 | `S01 NEGATIVE d-AXIS FIELD WEAKENING — DRIVER BLOCK` |
| T02 | `S01 FIELD WEAKENING — POWER-ON SEQUENCE` |
| T03 | `S01 FIELD WEAKENING — CONTROLLER STATE MACHINE` |
| T04 | `S01 FIELD WEAKENING — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S01 FIELD WEAKENING — CONCEPT PACKAGING (CONCEPT ONLY)` |
| T06 | `S01 FIELD WEAKENING — BOM / EDA RISK TREE` |
| T07 | `S01 FIELD WEAKENING — VERIFICATION PLAN` |
| T08 | `S01 FIELD WEAKENING — PROTOCOL LINK` |

---

## 1. 方案生产参数清单（嵌入 prompt 的数值与组件）

### 1.1 电气 / 控制

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| pole_pairs | 4 | — | motor_params.json |
| Vdc 标称 | 360 | V | motor_params.json |
| Vmax (SVPWM linear) | 207.85 | V | motor_params.json |
| Imax_phase_peak | 260 | A | motor_params.json |
| speed_max | 18 000 | rpm | motor_params.json |
| FW 进入 V margin 阈值 | 5 | V | r02 工程窗 |
| id_min 标称下界 | -240 | A | r02 demag estimate |
| temp_coefficient | -0.0035 | A/°C | r02 demag estimate |

### 1.2 PCB / 采样链（5 信号组）

`ia / ib / ic`（相电流 ADC）、`vdc_sense`（Vdc 分压）、`motor_temp / inverter_temp`（温度 ADC）、`gate_disable_n`（硬件关断）、`fault_latched`（锁存反馈）。

### 1.3 BOM 器件族（5 分支，r01 固化 risk）

| 分支 | risk（r01 固定） |
|---|---|
| Phase current sensors | MED |
| DC bus divider / isolator | MED |
| Temperature sensors | LOW |
| Gate-disable latch | HIGH |
| Fault feedback chain | MED |

### 1.4 DVP&R ID（来自 `V2-S01-DVP-fw_fault_injection-r00.md`）

`S01-DV-001` 弱磁进入/退出 · `S01-DV-002` id_min(T,fault) 限幅 · `S01-DV-003` Vdc 采样故障 · `S01-DV-004` 电流采样异常 · `S01-DV-005` gate-disable latch。

---

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S01-T01-r01
[priority] P1
[size]    1792x1024
[mode]    生图（可选改图，参考 r00 PNG）
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T01-driver_block-r00.png (改图模式)
[positive prompt]
Flat technical block diagram of an EV traction inverter and motor control chain
specific to S01 negative d-axis field weakening. Title bar text MUST be:
"S01 NEGATIVE d-AXIS FIELD WEAKENING — DRIVER BLOCK".
Layout left-to-right with five primary power-stage blocks across the bottom row:
"Battery / DC link (Vdc 360 V nominal)", "Precharge + Main Contactor",
"3-Phase Inverter (6 switches, peak phase current 260 A)",
"IPMSM Motor (pole pairs = 4, speed up to 18000 rpm)".
Above the power chain, a control row with five blocks left-to-right:
"MCU running FOC", "Gate Drivers (6 channels)", "Encoder / Resolver",
"Phase Current Sensors (ia, ib, ic)", "Vdc Sensor".
On the top-right, a highlighted scheme-specific sub-block labeled
"id_min(T, fault) Limiter — Vmax 207.85 V, V_margin threshold 5 V".
Draw arrows from "Motor Temperature" and "Inverter Temperature" sensor icons
on the far right INTO the id_min Limiter; draw an arrow from "Vdc Sensor"
INTO the id_min Limiter; draw the Limiter output as a short labeled arrow
"id_min(T, fault)" feeding into the FOC inside the MCU.
Use rectangular nodes with rounded corners (radius 12 px), pale blue node fills,
gold strokes, short English labels in white sans-serif. Connectors are orthogonal
gold lines with arrowheads. NO photorealistic motor or inverter render.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
make the id_min Limiter block have a slightly brighter gold border than other nodes
keep the five-block power chain horizontal across the bottom; align baselines
add small icons (thermometer / capacitor) inside Motor/Inverter Temp and Vdc Sensor blocks
remove any decorative motor render; IPMSM Motor stays as a labeled rounded rectangle
ensure no node overlaps and every arrow has a short label
[acceptance]
- Title bar verbatim
- Five power-stage blocks visible bottom row with their parenthetical parameters
- id_min Limiter sub-block highlighted and connected from 3 inputs (Vdc, motor T, inverter T)
- "Vmax 207.85 V" and "V_margin threshold 5 V" labels readable inside Limiter block
```

### T02 power-on sequence

```text
[image_id] IMG-S01-T02-r01
[priority] P1
[size]    1792x1024
[mode]    生图（可选改图，参考 r00 PNG）
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T02-power_on_sequence-r00.png (改图模式)
[positive prompt]
UML-style sequence diagram for the S01 field-weakening firmware power-on
procedure. Title bar text MUST be: "S01 FIELD WEAKENING — POWER-ON SEQUENCE".
Four vertical lifelines from left to right: VCU, MCU, INV (3-phase inverter),
M (IPMSM motor). Top-to-bottom horizontal arrows in this exact order with
labeled time annotations:
(1) "VCU -> MCU: Wake + torque disabled" at t = 0 ms
(2) "MCU self-loop: ADC self-test (ia/ib/ic, Vdc, motor T, inverter T)" at t < 50 ms
(3) "MCU -> INV: enable precharge path" at t = 50 ms
(4) "MCU self-loop: verify Vdc stable >= 240 V at t = 200 ms"
(5) "MCU -> INV: enable gate drivers" at t = 200 ms
(6) "MCU -> M: verify rotor position via resolver" at t = 220 ms
(7) "MCU self-loop: load id_min(T) and FW limits from NVM" at t = 240 ms
(8) "VCU -> MCU: torque command allowed" at t = 250 ms
Use a thick orange MCU activation bar from t = 0 to t = 250 ms during self-test
and LUT load. Use thin gold horizontal arrows on dark navy background,
monospace short labels for both messages and time annotations.
NO human figures, no color gradients beyond the gold + pale-blue + white palette.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
align all arrow labels horizontally so they remain readable
keep self-loop labels left of the MCU lifeline so they do not collide with INV/M arrows
make the MCU activation bar visibly thicker (4 px stroke) than other lifelines
ensure each step shows the time tag (t = ...) in monospace
[acceptance]
- 8 arrows in stated order with Vdc thresholds and timing labels embedded
- MCU activation bar visible across self-test region
- Title bar verbatim
```

### T03 state machine（**P0 必修**）

```text
[image_id] IMG-S01-T03-r01
[priority] P0
[size]    1024x1024
[mode]    强烈建议改图（先 draw.io 导出 r00 PNG，再上传）
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T03-state_machine-r00.png OR engineering/v2/scheme-01/controller/V2-S01-CTRL-field_weakening_state_machine-r00.drawio exported PNG
[positive prompt]
Finite-state-machine diagram for the S01 negative-d-axis field-weakening
controller. Title bar text MUST be:
"S01 FIELD WEAKENING — CONTROLLER STATE MACHINE".
<r01 ENUM RULE>
STATES (exactly 6, in this layout order left-to-right, top-to-bottom in a 2x3 grid):
  top-left: "Power On + ADC self-test"
  top-mid:  "Normal Torque Control (MTPA request)"
  top-right:"Voltage Limited (enter field weakening, V_margin < 5 V)"
  bot-left: "Apply id_min(T, fault) clamp (id_min nominal -240 A, dI/dT -0.0035 A/°C)"
  bot-mid:  "Derate Torque"
  bot-right:"Fault Fallback (gate disable)"
EDGES (exactly 7, each label appears once and only once):
  "Power On + ADC self-test" -> "Normal Torque Control (MTPA request)" : "sensors valid"
  "Power On + ADC self-test" -> "Fault Fallback (gate disable)"        : "self-test fail"
  "Normal Torque Control (MTPA request)" -> "Voltage Limited (enter field weakening, V_margin < 5 V)" : "V margin < limit"
  "Voltage Limited (enter field weakening, V_margin < 5 V)" -> "Apply id_min(T, fault) clamp (id_min nominal -240 A, dI/dT -0.0035 A/°C)" : "speed high"
  "Apply id_min(T, fault) clamp (id_min nominal -240 A, dI/dT -0.0035 A/°C)" -> "Derate Torque" : "demag / current risk"
  "Derate Torque" -> "Normal Torque Control (MTPA request)" : "margin recovered"
  "Derate Torque" -> "Fault Fallback (gate disable)" : "sensor / fault latch"
Highlight "Fault Fallback (gate disable)" node with red-tinted stroke
hex #C0392B; all other nodes use gold stroke hex #D8A638.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
preserve every state label and every transition label exactly as written above
re-layout to a 2x3 grid: Power On top-left, Fault Fallback bottom-right
remove the draw.io grid background, replace with single solid dark navy
ensure no two arrows overlap; route orthogonally only
the bottom-left "Apply id_min(T, fault) clamp" cell must show the numeric
clamp values "id_min -240 A" and "dI/dT -0.0035 A/°C" in a sub-line
[acceptance]
- 6 states with verbatim labels (including parenthetical numerical params)
- 7 edges with unique labels; "V margin < limit" present
- Fault Fallback red-tinted; title bar verbatim
- id_min clamp values visible
```

### T04 PCB concept

```text
[image_id] IMG-S01-T04-r01
[priority] P1
[size]    1024x1280
[mode]    生图（可选改图）
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T04-pcb_sheet_concept-r00.png (改图模式)
[positive prompt]
Conceptual PCB schematic sheet outline (NOT a real layout, NOT a manufacturable
artwork) for the S01 field-weakening controller sensing & fault path.
Title bar text MUST be:
"S01 FIELD WEAKENING — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Show five labeled functional groups left-to-right, each in a dashed gold
bounding box with the group name printed above:
(SENSING) blocks: "ia / ib / ic ADC front-end", "Vdc divider + isolator",
"motor_temp ADC", "inverter_temp ADC"
(ISOLATION) blocks: "sensor isolation barrier", "LV / HV partition line"
(CONTROL) blocks: "MCU ADC inputs", "FOC core", "id_min(T, fault) Limiter logic",
"NVM holding id_min(T) LUT"
(GATE DRIVE) blocks: "6-channel gate driver", "dead-time control",
"gate_disable_n hardware path (thick gold stroke, 4 px)"
(SAFETY LATCH) blocks: "fault latch logic", "fault_latched readback", "latch reset"
Reduce signal labels to no more than 18 short tokens total across the sheet.
Annotate signal names in English next to thin gold connectors.
NO pretend chip pin numbers, NO real part outlines, NO manufacturer logos.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
group blocks within each functional group inside a thin dashed gold bounding box
label each bounding box with the uppercase group name (SENSING / ISOLATION / CONTROL / GATE DRIVE / SAFETY LATCH)
remove any pretend chip pin numbers; show signal name labels only
ensure gate_disable_n stroke is the thickest (4 px) gold line
verify the CONCEPT ONLY watermark is in the top-right corner
[acceptance]
- 5 functional groups visible with verbatim names
- CONCEPT ONLY watermark visible
- gate_disable_n is visually thickest
- <=18 short signal tokens total
```

### T05 CAD packaging concept

```text
[image_id] IMG-S01-T05-r01
[priority] P1
[size]    1280x1024
[mode]    生图（可选改图）
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T05-cad_packaging_concept-r00.png (改图模式)
[positive prompt]
Conceptual isometric LINE illustration of the S01 inverter-to-motor
packaging boundary for field-weakening configuration. Title bar text MUST be:
"S01 FIELD WEAKENING — CONCEPT PACKAGING (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Show as flat isometric line drawing only (NO shading, NO surface texture,
NO metallic reflection, NO photorealistic 3D motor):
- a generic inverter housing on the left labeled "3-Phase Inverter Housing"
- three rectangular busbars going to motor terminals on the right, labeled
  "Phase A busbar", "Phase B busbar", "Phase C busbar" with thin gold leader lines
- a current sensor window around each busbar labeled "Hall / flux-gate window"
- a motor-side temperature sensor mount on the motor housing labeled
  "motor_temp NTC mount"
- an inverter-side temperature sensor inside the inverter housing labeled
  "inverter_temp NTC mount"
- an LV / HV keep-out partition drawn as a dashed gold plane labeled
  "LV / HV keep-out partition"
- a service access port labeled "fault latch service access"
Use generic material category labels only: "aluminium housing", "copper busbar",
"NTC sensor". NO M270-35A / NdFeB / SmCo / FR-4 / ADC12.
Aspect ratio 5:4 (1280x1024); orientation: motor on the right, inverter on the left.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
make LV/HV keep-out partition clearly visible as a dashed gold plane
label each busbar with phase letter A/B/C in uppercase
keep all callouts in English with thin gold leader lines, no overlap
remove any assembly screws, fasteners, or surface shading
verify NO real material grade names appear
[acceptance]
- flat isometric line illustration only (no shading)
- 3 busbars labeled A/B/C with sensor windows
- LV/HV partition visible
- CONCEPT ONLY watermark + verbatim title
```

### T06 BOM tree

```text
[image_id] IMG-S01-T06-r01
[priority] P2
[size]    1024x1024
[mode]    生图
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T06-bom_eda_tree-r00.png (改图模式)
[positive prompt]
Infographic-style component family risk tree for the S01 sensing & fault chain.
Title bar text MUST be: "S01 FIELD WEAKENING — BOM / EDA RISK TREE".
Root node centered at top labeled "S01 negative_d_axis_field_weakening".
Five first-level branches at the same vertical level:
"Current sensors", "Vdc divider / isolator", "Temperature sensors",
"Gate-disable latch", "Fault feedback chain".
Each first-level branch carries a risk badge displayed as a small pill on its
right side, with FIXED risk colors (do NOT randomize):
- "Current sensors" -> MED (amber)
- "Vdc divider / isolator" -> MED (amber)
- "Temperature sensors" -> LOW (green)
- "Gate-disable latch" -> HIGH (red)
- "Fault feedback chain" -> MED (amber)
Each branch has 2-3 leaves with 2-3 word component family names.
Suggested leaves (use exactly these):
- Current sensors: "Shunt resistors", "Hall-effect sensors", "Isolated amplifiers"
- Vdc divider / isolator: "Precision divider", "Isolation amplifier"
- Temperature sensors: "Motor NTC", "Inverter NTC", "PT1000"
- Gate-disable latch: "SR latch", "Digital isolator", "Reset interface"
- Fault feedback chain: "Opto isolator", "Logic buffer", "MCU input"
Use dark navy background, gold trunk strokes, fixed risk pill colors
(LOW green, MED amber, HIGH red).
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
keep the tree purely top-down, root at top, leaves at bottom
keep all five first-level branches at the same vertical level
make HIGH risk pills slightly larger to draw attention
use accessible green / amber / red, not pastel
do NOT introduce manufacturer part numbers
[acceptance]
- 5 first-level branches with verbatim names
- per-branch risk badge matches fixed mapping above
- leaves use exactly the suggested family names
```

### T07 verification tree

```text
[image_id] IMG-S01-T07-r01
[priority] P2
[size]    1792x1024
[mode]    生图
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T07-test_tree-r00.png (改图模式)
[positive prompt]
Left-to-right verification plan tree for S01 field weakening.
Title bar text MUST be: "S01 FIELD WEAKENING — VERIFICATION PLAN".
Root on the left labeled "S01 negative_d_axis_field_weakening verification".
Five level-1 branches, each carrying a DVP&R ID from
engineering/v2/scheme-01/test_dvpr/V2-S01-DVP-fw_fault_injection-r00.md in
monospace font:
(S01-DV-001) "Field weakening entry / exit (HIL planned)"
(S01-DV-002) "id_min(T, fault) clamp validation (SIL/HIL planned)"
(S01-DV-003) "Vdc sampling fault injection (planned)"
(S01-DV-004) "Phase current sampling fault injection (planned)"
(S01-DV-005) "Gate-disable latch test (bench planned)"
Each level-1 branch has 2-3 level-2 leaves with short acceptance hooks:
- S01-DV-001: "entry hysteresis bounded", "V margin >= 5 V at exit"
- S01-DV-002: "clamp respects T_max 120 C", "id_min within nominal -240 A"
- S01-DV-003: "Vdc fault detected < 1 ms", "fallback enters"
- S01-DV-004: "open / short detected < 1 ms", "derate triggered"
- S01-DV-005: "latch set verified", "latch holds across power cycle"
Monospace font used ONLY for DVP IDs (S01-DV-xxx); prose labels stay in
sans-serif. Use clean vector style, dark navy background, gold and pale blue
accents. NO labs / NO marketing photos.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
align all level-2 leaves vertically by branch
add a small DVPR badge near each level-1 branch label
keep monospace font only for test IDs (S01-DV-001 ...)
do not invent DVP IDs not present in the source markdown
[acceptance]
- 5 level-1 branches with verbatim DVP IDs
- 2-3 leaves per branch with verbatim acceptance hook text
```

### T08 protocol link

```text
[image_id] IMG-S01-T08-r01
[priority] P1
[size]    1024x1280
[mode]    生图（可选改图）
[reference image] gpt-image-2/outputs/S01/V2-S01-ILL-T08-protocol_link-r00.png (改图模式)
[positive prompt]
Network-style block diagram of communication and control links for S01.
Title bar text MUST be: "S01 FIELD WEAKENING — PROTOCOL LINK".
Nodes (vertical primary chain top-to-bottom):
"VCU (CAN-FD)" -> "MCU command parser" -> "Voltage / Current / Demag Limiter
(id_min limiter, Vmax 207.85 V threshold, demag dI/dT -0.0035 A/°C)" ->
"FOC id/iq controller" -> "SVPWM" -> "3-phase Inverter".
Right-side branch from MCU: "UDS / XCP Diagnostic Interface" and "Calibration Tool".
Every edge MUST carry an explicit bus label as follows:
- VCU -> MCU : "CAN-FD 5 Mbit/s"
- MCU -> Limiter : "internal AXI 32-bit (signals: V_bus, I_phase, T_magnet)"
- Limiter -> FOC : "internal AXI 32-bit"
- FOC -> SVPWM : "internal AXI 32-bit"
- SVPWM -> Inverter : "PWM U / V / W gate signals"
- MCU -> UDS / XCP : "CAN-FD 5 Mbit/s (UDS) + Ethernet 100 Mbit/s (XCP)"
- Calibration Tool -> UDS / XCP : "XCP-over-Ethernet TCP/IP"
Do NOT use generic "Internal Bus" placeholders. Use solid lines for all primary
control-chain arrows; reserve dashed lines for diagnostic-only branches and
label them as such.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
group VCU CAN at the top, MCU in the middle, FOC / SVPWM / Inverter at the bottom
draw the diagnostic path (UDS / XCP / Calibration) on the right side
use a slightly different stroke color (pale cyan) for diagnostic links versus
torque-command links
ensure every arrow has an explicit bus label
[acceptance]
- 7 bus labels verbatim; no "Internal Bus" placeholder
- limiter block shows numeric thresholds (Vmax 207.85, dI/dT -0.0035)
- title bar verbatim
```

---

## 3. 本方案归档清单（生成完一张就勾）

| 图 ID | 优先级 | r01 PNG | r01 prompt.txt |
|---|---|---|---|
| IMG-S01-T01-r01 | P1 | [ ] | [ ] |
| IMG-S01-T02-r01 | P1 | [ ] | [ ] |
| IMG-S01-T03-r01 | **P0** | [ ] | [ ] |
| IMG-S01-T04-r01 | P1 | [ ] | [ ] |
| IMG-S01-T05-r01 | P1 | [ ] | [ ] |
| IMG-S01-T06-r01 | P2 | [ ] | [ ] |
| IMG-S01-T07-r01 | P2 | [ ] | [ ] |
| IMG-S01-T08-r01 | P1 | [ ] | [ ] |
