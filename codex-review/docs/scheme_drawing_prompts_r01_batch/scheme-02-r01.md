# S02 r01 提示词批包 · mtpa_fw_mtpv_control

修订日期：2026-05-18
方案 ID：`mtpa_fw_mtpv_control`
工程目录：`engineering/v2/scheme-02/`
草案完整度：PCB / CAD / Controller / BOM / DVP&R 全
生产参数来源：`models/motor_params.json`、`models/control_lut.json`、
`engineering/v2/scheme-02/parameters/V2-S02-PARAM-control-r02.md`
输出落点：`gpt-image-2/outputs/S02/V2-S02-ILL-TYY-...-r01.png`

---

## 0. SCHEME_TITLE 锁定

| 模板 | SCHEME_TITLE 文本 |
|---|---|
| T01 | `S02 MTPA / FW / MTPV CONTINUOUS CONTROL — DRIVER BLOCK` |
| T02 | `S02 MTPA / FW / MTPV — POWER-ON SEQUENCE` |
| T03 | `S02 MODE TRANSITION LUT — STATE MACHINE` |
| T04 | `S02 MODE TRANSITION LUT — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S02 CONTROLLER PACKAGING — CONCEPT BOUNDARY (CONCEPT ONLY)` |
| T06 | `S02 MTPA / FW / MTPV — BOM / EDA RISK TREE` |
| T07 | `S02 MTPA / FW / MTPV — VERIFICATION PLAN` |
| T08 | `S02 MTPA / FW / MTPV — PROTOCOL LINK` |

---

## 1. 方案生产参数清单

### 1.1 控制 / LUT

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| pole_pairs | 4 | — | motor_params.json |
| Vdc 标称 | 360 | V | motor_params.json |
| Vmax (SVPWM linear) | 207.85 | V | motor_params.json |
| I_max_phase_peak | 260 | A | motor_params.json |
| speed_max | 18 000 | rpm | motor_params.json |
| speed_step | 250 | rpm | motor_params.json |
| torque_axis r03 标称 | [50, 100, 150, 200] | N·m | r02 sheet |
| LUT CRC | CRC-32 IEEE 802.3 | — | r02 sheet |
| LUT version | semver `MAJOR.MINOR.PATCH` | — | r02 sheet |
| NVM 写入策略 | A/B 双 banks | — | r02 sheet |
| V_margin FW 阈值 | 5 | V | r02 sheet |
| id_jump 最大 | 30 | A | r02 sheet S02-SIM-010 |
| iq_jump 最大 | 30 | A | r02 sheet S02-SIM-011 |
| torque_jump 最大 | 5.0 | N·m | r02 sheet S02-SIM-009 |

### 1.2 PCB 信号

`ia/ib/ic` ADC、`vdc_sense`、resolver/encoder、CAN-FD 收发、SPI MCU↔NVM、LUT version diagnostic、`mode_state` 输出。

### 1.3 BOM 器件族（5 分支，r01 固化 risk）

| 分支 | risk |
|---|---|
| MCU + NVM | HIGH |
| ADC front-end | MED |
| Position interface (resolver / encoder) | MED |
| Communication transceivers (CAN-FD) | LOW |
| LUT release infrastructure | HIGH |

### 1.4 DVP&R ID（来自 `V2-S02-TEST-lut_mode_hil-r00.md`）

`S02-DV-001` MTPA/FW/MTPV 模式切换连续性 · `S02-DV-002` LUT CRC 失败 · `S02-DV-003` LUT 版本不匹配 · `S02-DV-004` 断电恢复 · `S02-DV-005` 不可行区请求。

---

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S02-T01-r01
[priority] P1
[size]    1792x1024
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T01-driver_block-r00.png
[positive prompt]
Flat technical block diagram of an EV traction inverter and motor control chain
specific to S02 MTPA / FW / MTPV continuous control. Title bar text MUST be:
"S02 MTPA / FW / MTPV CONTINUOUS CONTROL — DRIVER BLOCK".
Bottom power-stage row left-to-right (5 blocks):
"Battery / DC link (Vdc 360 V)", "Precharge + Main Contactor",
"3-Phase Inverter (peak current 260 A)",
"IPMSM Motor (pole pairs = 4, speed up to 18000 rpm)".
Control row above (left-to-right): "MCU + NVM", "Gate Drivers (6 channels)",
"Encoder / Resolver", "Phase Current Sensors (ia, ib, ic)", "Vdc Sensor".
On top-right, highlighted sub-block: "MTPA / FW / MTPV Mode Selector LUT
(2D speed-torque, speed 0-18000 rpm step 250, torque [50, 100, 150, 200] N·m,
V_margin 5 V threshold)" connected by "torque request" arrow from VCU and by
output "id / iq reference" arrow into FOC inside MCU.
Show small NVM icon next to MCU labeled "control LUT, CRC-32, A/B banks,
version semver".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
make the Mode Selector LUT block slightly larger and gold-highlighted
keep power-stage chain straight and horizontal
add a small NVM icon (rectangle with "A/B") above the MCU
ensure the LUT block shows the torque-axis list "[50, 100, 150, 200] N·m"
[acceptance]
- Title bar verbatim
- Mode Selector LUT block has explicit "[50, 100, 150, 200] N·m" and "V_margin 5 V" text
- NVM A/B banks visible
```

### T02 power-on sequence

```text
[image_id] IMG-S02-T02-r01
[priority] P1
[size]    1792x1024
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T02-power_on_sequence-r00.png
[positive prompt]
UML-style sequence diagram for S02 MTPA / FW / MTPV power-on procedure.
Title bar text MUST be: "S02 MTPA / FW / MTPV — POWER-ON SEQUENCE".
Five lifelines left-to-right: VCU, MCU, NVM, INV, M.
Arrows top-to-bottom in this exact order with time tags:
(1) "VCU -> MCU: Wake + torque disabled" at t = 0 ms
(2) "MCU -> NVM: read LUT bank A header (version, CRC-32)" at t < 30 ms
(3) "NVM -> MCU: header bytes returned"
(4) "MCU self-loop: verify LUT CRC vs stored expected" at t < 80 ms
(5) "MCU self-loop: ADC self-test (ia/ib/ic, Vdc)" at t < 100 ms
(6) "MCU -> INV: enable precharge path" at t = 100 ms
(7) "MCU self-loop: Vdc stable >= 240 V" at t = 200 ms
(8) "MCU -> INV: enable gate drivers" at t = 200 ms
(9) "MCU -> M: resolver self-test" at t = 220 ms
(10) "MCU self-loop: load LUT body into RAM (mode_state -> MTPA idle)" at t = 250 ms
(11) "VCU -> MCU: torque command allowed" at t = 280 ms
Thick MCU activation bar across t = 0..280 ms. Show LUT CRC failure red arrow
branching to a fault lane labeled "S02-DTC-LUT-CRC-FAIL".
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
include the CRC-fail branch as a small red dashed arrow off step (4)
align all time tags in monospace on the right side of each arrow
[acceptance]
- 11 arrows with explicit time tags and bank/CRC references
- CRC-fail branch visible
- Title verbatim
```

### T03 state machine（**P0 必修**）

```text
[image_id] IMG-S02-T03-r01
[priority] P0
[size]    1024x1024
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T03-state_machine-r00.png OR engineering/v2/scheme-02/controller/V2-S02-CTRL-mode_transition_lut-r00.drawio exported PNG
[positive prompt]
Finite-state-machine diagram for the S02 MTPA / FW / MTPV mode transition LUT.
Title bar text MUST be: "S02 MODE TRANSITION LUT — STATE MACHINE".
<r01 ENUM RULE>
STATES (exactly 6, layout in a 2x3 grid):
  top-left: "MTPA idle"
  top-mid:  "MTPA active"
  top-right:"Field Weakening (V_margin < 5 V)"
  bot-left: "LUT CRC fault fallback"
  bot-mid:  "MTPV (boundary reached)"
  bot-right:"Derate (thermal / demag)"
EDGES (exactly 7, each label appears once and only once):
  "MTPA idle" -> "MTPA active" : "LUT CRC ok"
  "MTPA active" -> "Field Weakening (V_margin < 5 V)" : "speed > base"
  "Field Weakening (V_margin < 5 V)" -> "MTPV (boundary reached)" : "MTPV boundary reached"
  "MTPV (boundary reached)" -> "Field Weakening (V_margin < 5 V)" : "V margin recovered"
  "MTPA active" -> "Derate (thermal / demag)" : "thermal / demag risk"
  "Derate (thermal / demag)" -> "MTPA idle" : "mode reset"
  "MTPA idle" -> "LUT CRC fault fallback" : "LUT CRC fail"
Highlight "LUT CRC fault fallback" and "Derate (thermal / demag)" with
red-tinted stroke hex #C0392B; all other nodes use gold stroke.
"mode reset" MUST point to "MTPA idle" (not to "Derate").
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
verify "mode reset" arrow lands on MTPA idle, not on Derate (r00 was wrong)
preserve numeric label "V_margin < 5 V" in the Field Weakening state name
[acceptance]
- 6 states with parenthetical numeric thresholds where listed
- 7 edges with unique verbatim labels
- "mode reset" terminus = MTPA idle
- Fault states red-tinted
```

### T04 PCB concept

```text
[image_id] IMG-S02-T04-r01
[priority] P1
[size]    1024x1280
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T04-pcb_sheet_concept-r00.png
[positive prompt]
Conceptual PCB schematic sheet outline for the S02 MTPA / FW / MTPV controller
I/O map. Title bar text MUST be:
"S02 MODE TRANSITION LUT — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Five functional groups in dashed gold bounding boxes:
(MCU CORE) "MCU 32-bit", "Internal SRAM 512 KB", "FOC core"
(NVM) "External NVM (256 KB)", "A/B bank selector", "CRC-32 hash engine",
"LUT version registry"
(ADC FRONT-END) "ia/ib/ic ADC (3 channels, 12-bit, 100 kSPS)", "Vdc ADC",
"motor_temp ADC", "inverter_temp ADC"
(POSITION) "Resolver excitation", "Resolver demod", "Encoder quad input"
(COMM) "CAN-FD transceiver (5 Mbit/s)", "LIN backup", "Ethernet TJA1100 phy"
Add a small "LUT version diagnostic" callout bridging NVM and COMM groups,
labeled "S02-DTC-LUT-VER-MISMATCH path".
Keep <= 18 short signal tokens.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
add explicit "12-bit / 100 kSPS" and "5 Mbit/s" sub-text under matching blocks
the LUT version diagnostic callout should be a small dashed amber loop
verify CONCEPT ONLY watermark top-right
[acceptance]
- 5 group bounding boxes with verbatim group names
- LUT version diagnostic callout present
- numerical specs visible (12-bit, 100 kSPS, 5 Mbit/s, 256 KB)
```

### T05 CAD packaging concept

```text
[image_id] IMG-S02-T05-r01
[priority] P1
[size]    1280x1024
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T05-cad_packaging_concept-r00.png
[positive prompt]
Conceptual isometric LINE illustration of the S02 controller mechanical
packaging boundary. Title bar text MUST be:
"S02 CONTROLLER PACKAGING — CONCEPT BOUNDARY (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Flat isometric line illustration only. Show: a generic controller enclosure
labeled "Controller Housing (aluminium)", with connector positions:
"CAN-FD connector", "Resolver connector", "12 V battery connector",
"3-phase output bus interface". Below the housing show "Cooling plate"
labeled "liquid-cooled cold plate, generic". Inside, sketch a partition labeled
"LV (12 V) / HV (Vdc 360 V) partition". Use generic categories only
(aluminium, copper, insulator); do NOT name material grades. No screws shown.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
ensure flat line illustration only; no metallic shading
label LV / HV partition explicitly with voltage levels in parentheses
add small leader lines for each connector
[acceptance]
- flat line illustration; CONCEPT ONLY watermark present
- LV / HV partition with voltage levels
- generic material categories only
```

### T06 BOM tree

```text
[image_id] IMG-S02-T06-r01
[priority] P2
[size]    1024x1024
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T06-bom_eda_tree-r00.png
[positive prompt]
Component family risk tree for S02. Title bar:
"S02 MTPA / FW / MTPV — BOM / EDA RISK TREE".
Root "S02 mtpa_fw_mtpv_control".
Five first-level branches with FIXED risk pills:
- "MCU + NVM" -> HIGH (red)
- "ADC front-end" -> MED (amber)
- "Position interface (resolver / encoder)" -> MED (amber)
- "Communication transceivers (CAN-FD)" -> LOW (green)
- "LUT release infrastructure" -> HIGH (red)
Leaves:
- MCU + NVM: "32-bit safety MCU", "External NVM 256 KB", "Watchdog"
- ADC front-end: "12-bit SAR ADC", "Anti-aliasing filter", "Reference voltage"
- Position interface: "Resolver-to-digital", "Encoder quadrature decoder"
- Communication transceivers: "CAN-FD PHY", "LIN PHY"
- LUT release infrastructure: "CRC-32 engine", "Bank A/B switch", "Version registry"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
keep all five first-level branches at same vertical level
risk pills must be accessible green / amber / red
do NOT introduce manufacturer part numbers
[acceptance]
- 5 branches with verbatim names and FIXED risk colors
- Leaves match the list above
```

### T07 verification tree

```text
[image_id] IMG-S02-T07-r01
[priority] P2
[size]    1792x1024
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T07-test_tree-r00.png
[positive prompt]
Left-to-right verification plan tree for S02. Title bar:
"S02 MTPA / FW / MTPV — VERIFICATION PLAN".
Root: "S02 mtpa_fw_mtpv_control verification".
Five level-1 branches with DVP IDs in monospace:
(S02-DV-001) "MTPA/FW/MTPV mode continuity (HIL planned)"
(S02-DV-002) "LUT CRC fault injection (planned)"
(S02-DV-003) "LUT version mismatch (HIL planned)"
(S02-DV-004) "Power-off recovery (HIL planned)"
(S02-DV-005) "Infeasible region request (SIL/HIL)"
Level-2 leaves with acceptance hooks:
- S02-DV-001: "id_jump <= 30 A", "iq_jump <= 30 A", "torque_jump <= 5 N·m"
- S02-DV-002: "fallback enters within 200 ms", "DTC S02-DTC-LUT-CRC-FAIL set"
- S02-DV-003: "rejects load within 200 ms", "DTC S02-DTC-LUT-VER-MISMATCH set"
- S02-DV-004: "NVM read + CRC ok < 500 ms", "mode resets to MTPA idle"
- S02-DV-005: "INFEASIBLE returned", "derate triggered"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
monospace for DVP IDs only; prose stays sans-serif
include the numeric thresholds (30 A, 5 N·m, 200 ms, 500 ms) verbatim
[acceptance]
- 5 verbatim DVP IDs
- numeric thresholds present
```

### T08 protocol link

```text
[image_id] IMG-S02-T08-r01
[priority] P1
[size]    1024x1280
[reference image] gpt-image-2/outputs/S02/V2-S02-ILL-T08-protocol_link-r00.png
[positive prompt]
Network-style block diagram for S02. Title bar:
"S02 MTPA / FW / MTPV — PROTOCOL LINK".
Vertical chain top-to-bottom:
"VCU (CAN-FD 5 Mbit/s)" -> "MCU command parser" ->
"Mode Selector (MTPA / FW / MTPV)" -> "FOC id/iq controller" -> "SVPWM" ->
"3-phase Inverter".
Right-side branches from MCU: "External NVM (LUT, A/B banks, CRC-32)" and
"UDS / XCP Diagnostic" with "Calibration Tool".
Bus labels (no "Internal Bus" placeholder):
- VCU -> MCU : "CAN-FD 5 Mbit/s"
- MCU -> Mode Selector : "internal AXI 32-bit"
- Mode Selector -> FOC : "internal AXI 32-bit (id_ref, iq_ref)"
- FOC -> SVPWM : "internal AXI 32-bit (vd, vq)"
- SVPWM -> Inverter : "PWM U/V/W"
- MCU <-> NVM : "SPI 50 MHz"
- MCU <-> UDS / XCP : "CAN-FD 5 Mbit/s (UDS) + Ethernet 100 Mbit/s (XCP)"
- Calibration Tool -> UDS / XCP : "XCP-over-Ethernet TCP/IP"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
NVM block must show "A/B banks, CRC-32" sub-label
SPI link must show 50 MHz; all bus speeds must be explicit
[acceptance]
- 8 bus labels verbatim with explicit speeds
- NVM bank/CRC labels present
- title bar verbatim
```

---

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S02-T01-r01 | P1 | [ ] | [ ] |
| IMG-S02-T02-r01 | P1 | [ ] | [ ] |
| IMG-S02-T03-r01 | **P0** | [ ] | [ ] |
| IMG-S02-T04-r01 | P1 | [ ] | [ ] |
| IMG-S02-T05-r01 | P1 | [ ] | [ ] |
| IMG-S02-T06-r01 | P2 | [ ] | [ ] |
| IMG-S02-T07-r01 | P2 | [ ] | [ ] |
| IMG-S02-T08-r01 | P1 | [ ] | [ ] |
