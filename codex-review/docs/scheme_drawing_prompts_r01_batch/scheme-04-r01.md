# S04 r01 提示词批包 · nonlinear_flux_lut

修订日期：2026-05-18  
方案 ID：`nonlinear_flux_lut`  
工程目录：`engineering/v2/scheme-04/`  
草案完整度：PCB / CAD / Controller / BOM / DVP&R 全 + EXP-006 phase-2 通过  
依据：`engineering/v2/scheme-04/{pcb,cad,bom_eda,controller,test_dvpr}/`、`models/flux_lut_sample.json`、`models/motor_params.json`

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S04 NONLINEAR FLUX LUT — DRIVER BLOCK` |
| T02 | `S04 NONLINEAR FLUX LUT — POWER-ON SEQUENCE` |
| T03 | `S04 NONLINEAR FLUX LUT — STATE MACHINE` |
| T04 | `S04 NONLINEAR FLUX LUT — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S04 FEA GEOMETRY SOURCE — CONCEPT FRAME (CONCEPT ONLY)` |
| T06 | `S04 NONLINEAR FLUX LUT — BOM / EDA RISK TREE` |
| T07 | `S04 NONLINEAR FLUX LUT — VERIFICATION PLAN` |
| T08 | `S04 NONLINEAR FLUX LUT — PROTOCOL LINK` |

## 1. 生产参数

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| pole_pairs | 4 | — | motor_params.json |
| LUT 输入 | id, iq, omega_e, T | — | PCB 草案 |
| LUT 输出 | lambda_d, lambda_q | Wb | exp-006 phase-2 |
| id 网格 | [-260, +40], step 2.0 | A | grid |
| iq 网格 | [0, 260], step 2.0 | A | grid |
| omega_e 网格 | 0..7540 (= 18000 rpm × 2π × pole_pairs / 60) | rad/s | 折算 |
| T 切片 | [25, 60, 80, 100, 120] | °C | r01 工程窗 |
| LUT CRC | CRC-32 IEEE 802.3 | — | r02 估值 |
| 插值方式 | 双线性 | — | exp-006 |
| 越界 fallback | linear dq | — | controller drawio |
| residual_high 阈值 | 12 % | — | r01 估值（待 r03 替换） |
| 采样精度（id/iq） | 12-bit ADC, ±0.5 % FS | — | PCB 草案 |
| 位置延迟预算 | <= 60 μs | — | r01 估值 |

## 2. T01-T08 完整提示词

### T01 driver block

```text
[image_id] IMG-S04-T01-r01
[priority] P1
[size] 1792x1024
[reference image] gpt-image-2/outputs/S04/V2-S04-ILL-T01-driver_block-r00.png
[positive prompt]
Flat technical block diagram for S04 nonlinear flux LUT control chain.
Title bar text MUST be: "S04 NONLINEAR FLUX LUT — DRIVER BLOCK".
Bottom power-stage row: "Battery / DC link (Vdc 360 V)",
"Precharge + Main Contactor", "3-Phase Inverter", "IPMSM Motor (pole pairs = 4)".
Control row: "MCU + FOC", "Gate Drivers (6 channels)", "Encoder / Resolver",
"Phase Current Sensors (ia/ib/ic, 12-bit ADC ±0.5 % FS)", "Vdc Sensor",
"Temperature Sensors (motor / inverter, T axis [25, 60, 80, 100, 120] C)".
On top, highlighted block: "Nonlinear Flux LUT Observer
(inputs id [-260..+40 A], iq [0..260 A], omega_e [0..7540 rad/s], T;
outputs lambda_d / lambda_q in Wb; CRC-32 protected; fallback to linear dq)".
Show small surface-plot icon inside the observer block.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- Observer block shows all 4 input axes with ranges and units
- "fallback to linear dq" text visible
```

### T02 power-on sequence

```text
[image_id] IMG-S04-T02-r01
[priority] P1
[size] 1792x1024
[positive prompt]
UML sequence for S04 power-on, lifelines VCU/MCU/NVM/INV/M. Arrows top-down:
(1) t=0: VCU->MCU "wake torque disabled"
(2) t<30: MCU->NVM "read flux LUT header (version, CRC-32)"
(3) t<80: MCU self "verify LUT CRC vs expected"
(4) t<100: MCU self "verify bounds metadata id [-260..+40], iq [0..260], T [25..120]"
(5) t<120: MCU self "ADC self-test"
(6) t=200: MCU->INV "enable gate drivers, Vdc stable >= 240 V"
(7) t=250: MCU self "load LUT body, residual monitor threshold 12 %"
(8) t=280: VCU->MCU "torque command allowed"
Title: "S04 NONLINEAR FLUX LUT — POWER-ON SEQUENCE". Thick MCU activation bar.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 8 arrows with LUT bounds and residual threshold present
```

### T03 state machine

```text
[image_id] IMG-S04-T03-r01
[priority] P1
[size] 1024x1024
[reference image] engineering/v2/scheme-04/controller/V2-S04-CTRL-flux_lut_interpolation-r00.drawio exported PNG
[positive prompt]
Finite-state-machine diagram for S04 nonlinear flux LUT. Title bar:
"S04 NONLINEAR FLUX LUT — STATE MACHINE".
<r01 ENUM RULE>
STATES (exactly 6, 2x3):
  top-left: "LUT load + CRC check"
  top-mid:  "Bounds check passed"
  top-right:"Bilinear interpolation active"
  bot-left: "Out-of-bounds clamp"
  bot-mid:  "Error monitor warning (residual > 12 %)"
  bot-right:"Fallback to linear dq"
EDGES (exactly 7, unique labels):
  "LUT load + CRC check" -> "Bounds check passed" : "LUT CRC ok"
  "Bounds check passed" -> "Bilinear interpolation active" : "query inside LUT bounds"
  "Bilinear interpolation active" -> "Out-of-bounds clamp" : "out-of-bounds detected"
  "Out-of-bounds clamp" -> "Bilinear interpolation active" : "recover to LUT"
  "Bilinear interpolation active" -> "Error monitor warning (residual > 12 %)" : "residual rising"
  "Error monitor warning (residual > 12 %)" -> "Fallback to linear dq" : "monitor over threshold"
  "Fallback to linear dq" -> "LUT load + CRC check" : "session reset"
Highlight Out-of-bounds clamp / Error monitor warning / Fallback red.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- residual threshold "12 %" visible inside the warning state name
- 7 unique edges
```

### T04 PCB concept（**P0 必修**）

```text
[image_id] IMG-S04-T04-r01
[priority] P0
[size] 1024x1280
[reference image] gpt-image-2/outputs/S04/V2-S04-ILL-T04-pcb_sheet_concept-r00.png
[positive prompt]
Conceptual PCB sheet for S04 LUT observer & safety architecture. Title bar:
"S04 NONLINEAR FLUX LUT — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Reduce density: <= 18 short signal tokens total.
Five functional groups in dashed gold bounding boxes:
(LUT OBSERVER INPUTS) "ia / ib / ic (12-bit, ±0.5 % FS)", "Vdc sense",
"resolver / encoder (delay <= 60 μs)", "motor / inverter temperature T [25..120 C]"
(BOUNDS CHECK) "id range [-260..+40] A", "iq range [0..260] A",
"omega_e range [0..7540 rad/s]", "T slice picker"
(FALLBACK DIAGNOSTIC) "out-of-bounds line", "residual monitor (>12 % warn)",
"fallback_active flag"
(ERROR BUDGET TELEMETRY) "id/iq error budget", "position delay budget",
"T error budget", "Vdc error budget"
(MCU NVM) "external NVM (LUT body)", "CRC-32 engine", "version registry"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
verify CONCEPT ONLY watermark
verify exactly five group bounding boxes
<= 18 signal tokens (count carefully)
[acceptance]
- 5 group bounding boxes verbatim
- Concept watermark present
- numeric ranges visible
```

### T05 CAD packaging concept（**P0 BLOCKER 重做**）

```text
[image_id] IMG-S04-T05-r01
[priority] P0 BLOCKER
[size] 1280x1024
[reference image] gpt-image-2/outputs/S04/V2-S04-ILL-T05-cad_packaging_concept-r00.png (only as composition reference; r00 violates rules)
[positive prompt]
Conceptual isometric LINE illustration of the S04 FEA geometry source reference
frame. Title bar text MUST be:
"S04 FEA GEOMETRY SOURCE — CONCEPT FRAME (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Flat isometric line illustration ONLY. NO photorealistic motor cross-section.
NO real material grade names (forbid M270-35A, NdFeB, SmCo, ADC12, C11000, FR-4).
Show:
- A coordinate frame on the left labeled "FEA reference frame (X forward, Y left, Z up)"
- A dq-axis origin labeled "dq coordinate origin at rotor center"
- A material stack as 4 labeled empty boxes only: "electrical steel (generic)",
  "magnet (generic permanent magnet)", "copper (generic winding)", "insulator (generic)"
- A wireframe cube on the right labeled "FEA mesh boundary (tetra)"
  with vertices showing keep-out clearance text "HV >= 20 mm, LV >= 10 mm"
- Sensor position bindings as 3 numbered callouts: "(1) resolver / encoder position",
  "(2) motor temperature mount", "(3) winding temperature mount"
- Units callout "Units: mm, kg, s"
Forbid any shading, surface texture, or metallic reflection.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[改图微调]
verify flat line illustration only; no 3D shading at all
verify NO real material grade names appear
each box is hollow with thin gold border, NO fill texture
[acceptance]
- flat line only; concept watermark
- 4 generic material category boxes
- 3 sensor callouts numbered
- coordinate frame + units callout
- NO real material names whatsoever
```

### T06 BOM tree

```text
[image_id] IMG-S04-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
Component family risk tree for S04 LUT sensor chain. Title:
"S04 NONLINEAR FLUX LUT — BOM / EDA RISK TREE".
Root "S04 nonlinear_flux_lut".
FIXED risk pills:
- "Current sensors (ia/ib/ic)" -> MED
- "Position sensors (resolver / encoder)" -> HIGH (delay-critical)
- "Temperature sensors" -> MED
- "Vdc sensing" -> LOW
- "Diagnostic NVM (LUT body + CRC-32)" -> HIGH
Leaves: brief 2-3 token component family names per branch.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 branches with FIXED risk
```

### T07 verification tree

```text
[image_id] IMG-S04-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S04. Title: "S04 NONLINEAR FLUX LUT — VERIFICATION PLAN".
Root: "S04 nonlinear_flux_lut verification".
Level-1 branches with DVP IDs from V2-S04-TEST-flux_lut_correlation-r00.md:
(S04-DV-001) "LUT bounds enforcement (out-of-bounds reject / clamp)"
(S04-DV-002) "Bilinear interpolation consistency (residual < 12 %)"
(S04-DV-003) "FEA geometry version binding (CAD / FEA / LUT versions match)"
(S04-DV-004) "Bench correlation (measured vs predicted residual)"
(S04-DV-005) "Fallback behavior (residual high -> linear dq)"
Acceptance hooks: numeric thresholds verbatim.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 5 DVP IDs verbatim, residual threshold present
```

### T08 protocol link

```text
[image_id] IMG-S04-T08-r01
[priority] P1
[size] 1024x1280
[positive prompt]
Network block diagram for S04. Title: "S04 NONLINEAR FLUX LUT — PROTOCOL LINK".
Vertical chain: "VCU (CAN-FD 5 Mbit/s)" -> "MCU command parser" ->
"LUT Version + Bounds Telemetry (CRC-32, bounds id/iq/omega/T)" ->
"FOC id/iq controller" -> "SVPWM" -> "3-phase Inverter".
Right branches: "External NVM (LUT body)" via SPI, "UDS / XCP" + "Calibration Tool".
Bus labels (explicit, no placeholders):
- VCU->MCU "CAN-FD 5 Mbit/s"
- MCU<->NVM "SPI 50 MHz"
- MCU->Telemetry "internal AXI 32-bit"
- Telemetry->FOC "internal AXI 32-bit (lambda_d, lambda_q)"
- FOC->SVPWM "internal AXI 32-bit"
- SVPWM->Inverter "PWM U/V/W (10 kHz)"
- MCU<->UDS/XCP "CAN-FD (UDS) + Ethernet 100 Mbit/s (XCP)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 7 verbatim bus labels with speeds
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S04-T01-r01 | P1 | [ ] | [ ] |
| IMG-S04-T02-r01 | P1 | [ ] | [ ] |
| IMG-S04-T03-r01 | P1 | [ ] | [ ] |
| IMG-S04-T04-r01 | **P0** | [ ] | [ ] |
| IMG-S04-T05-r01 | **P0 BLOCKER** | [ ] | [ ] |
| IMG-S04-T06-r01 | P2 | [ ] | [ ] |
| IMG-S04-T07-r01 | P2 | [ ] | [ ] |
| IMG-S04-T08-r01 | P1 | [ ] | [ ] |
