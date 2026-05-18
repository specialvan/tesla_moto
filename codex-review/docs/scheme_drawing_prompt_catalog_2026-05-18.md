# 12 方案图纸生图 / 改图提示词目录

评审日期：2026-05-18  
落地包：`codex-review/docs`  
事实源：`engineering/v2/scheme-XX/`、`reports/scheme_driver_power_protocol_diagrams.md`、`reports/scheme_bom_eda_integration_design.md`、`models/scheme_engineering_catalog.json`

## 0. 使用边界

1. 本目录的提示词面向 **文本生图** 工具（按用户截图：1024×1024、PNG、鲜明风格、GPT 系生图后端），用于产出 **概念示意图 / 信息图 / 工程示意草图**。
2. 生图结果 **不能** 替代 EDA 原理图、Layout、Gerber、ODB++、STEP、Parasolid、SolidWorks、Motor-CAD、Maxwell FEA、Fluent CFD 几何或 `.drawio` 的形式化拓扑。
3. 生图结果 **不证明** `engineering_validated=true`；它只用于：
   - 评审/汇报中的可视化锚点；
   - `.drawio`、Mermaid、PCB markdown 草案的视觉补充；
   - 与外部协作者沟通时的方案直观图。
4. 所有生成图必须保留与对应 `engineering/v2/scheme-XX/` 草案文件的文字 ID（如 `V2-S01-CTRL-field_weakening_state_machine-r00`），以便回溯。
5. 生图工具不能取代安全验证：退磁、热、过压、绝缘、故障安全相关图必须仍由真实 PCB/EDA/CAD/FEA 路径完成。

## 1. 共享风格基线

所有方案、所有图纸类型共享以下基线，避免风格漂移。

### 1.1 正向风格 token

```text
technical engineering schematic, flat infographic style, clean vector look,
dark navy or near-black background, soft grid lines, gold and white labels,
crisp sans-serif typography, balanced composition, isometric or top-down layout as appropriate,
high contrast, sharp edges, professional automotive powertrain documentation aesthetic
```

### 1.2 负向 prompt（统一基线）

```text
photorealistic faces, glamour photography, marketing render, watercolor,
cartoon mascots, anime style, low contrast, blurry, motion blur, lens flare,
busy decorative background, fake measurement units, hand-drawn sketch noise,
chinese calligraphy stroke, emoji, watermark, logo
```

### 1.3 标注语言

- 主标题、节点名、状态名、信号名：英文（与 `.drawio`、Mermaid 一致）。
- 可选副标题 / 备注：中文（如「弱磁状态机草图」）。
- 数值单位：SI 单位 + 工程别名（V、A、Nm、rpm、°C）。

### 1.4 张数与尺寸

- 默认 1 张、1024×1024、PNG、鲜明。
- 时序图 / 横向流程图建议改为 16:9 或 21:9 长图（如生图工具支持）。
- 改图模式优先复用现有 `.drawio` 截图或 Mermaid 渲染 PNG 作参考图。

## 2. 共享图纸模板

12 个方案的图纸大部分落在 8 类模板中。每类模板给出一段可直接复用的提示词，方案级章节只写差分。

### T01 驱动设计图（System Driver Block Diagram）

事实源参考：`reports/scheme_driver_power_protocol_diagrams.md`「驱动设计图」mermaid 块。

**生图提示词（中英混合，可直接粘贴）**：

```text
Generate a flat technical block diagram of an automotive traction inverter and motor control chain.
Layout left-to-right: Battery / DC link -> Precharge + main contactor -> 3-phase inverter ->
IPMSM motor. On top, MCU running FOC, connected to inverter gate drivers, to encoder / resolver,
to phase current sensors, to Vdc sensor, and to a specialized control block <SCHEME_BLOCK>.
Use rectangular nodes with rounded corners, gold strokes on dark navy background,
clean orthogonal connectors with arrowheads, short labels in English.
Aspect ratio 16:9, single image, no people, no marketing copy.
```

`<SCHEME_BLOCK>` 在方案级章节给出。

### T02 上电时序图（Power-on Sequence）

事实源参考：`reports/scheme_driver_power_protocol_diagrams.md`「上电时序图」mermaid `sequenceDiagram`。

**生图提示词**：

```text
Generate a clean UML-style sequence diagram for an EV traction inverter power-on procedure.
Show vertical lifelines for VCU, MCU, Inverter, Motor, and optional NVM. Arrows top-to-bottom
represent: wake with torque disabled, sensor self-test, precharge enable, Vdc stable check,
gate-driver enable, rotor alignment, load <SCHEME_TABLE>, torque enable.
Use thin gold horizontal arrows on dark background, monospace short labels, no decoration,
no human figures, no color gradients beyond two accent colors.
```

### T03 状态机（Controller State Machine）

事实源参考：`engineering/v2/scheme-XX/controller/*.drawio`。

**生图提示词**：

```text
Generate a finite-state-machine diagram for a motor controller subsystem.
States are rounded rectangles arranged in a 2x3 or 3x2 grid:
<SCHEME_STATES>. Directed edges with English transition labels show
<SCHEME_TRANSITIONS>. Use a flat infographic style, dark navy background,
pale blue node fills, gold stroke and labels, orthogonal connectors,
no shadows, no people, single-image composition.
```

### T04 PCB 页面草案图（PCB Sheet Outline Concept）

事实源参考：`engineering/v2/scheme-XX/pcb/*.md`。

**生图提示词**：

```text
Generate a conceptual PCB schematic sheet outline showing labeled blocks (not real symbols)
for: <SCHEME_PCB_BLOCKS>. Arrange blocks left-to-right in functional groups
(sensing, isolation, control, gate drive, safety latch). Annotate signal names in
English next to thin gold connectors. Dark navy background, light grid, no real
component footprints, no part numbers, no marketing copy. Make it clearly a
"page-level concept", not a manufacturable layout.
```

### T05 3D/CAD 封装边界草案图（Packaging / Busbar / Sensor Layout Concept）

事实源参考：`engineering/v2/scheme-XX/cad/*.md`。

**生图提示词**：

```text
Generate an isometric concept illustration of an EV inverter and motor mechanical
packaging boundary. Show: <SCHEME_CAD_ELEMENTS>. Use flat vector style, dark navy
background, soft cyan and gold accents, English labels with leader lines, no
photorealism, no human figures, no manufacturer branding. Mark LV / HV keep-out zones
and sensor mounting points clearly.
```

### T06 BOM / EDA 架构树（Component Family Risk Tree）

事实源参考：`engineering/v2/scheme-XX/bom_eda/*.md`、`reports/scheme_bom_eda_integration_design.md`。

**生图提示词**：

```text
Generate an infographic-style component family tree for an EV motor control subsystem.
Root node: <SCHEME_NAME>. Branches: <SCHEME_BOM_GROUPS>. Each leaf shows
a 2-3 word component family label and a risk badge (LOW / MED / HIGH) drawn as
small pills. Use dark navy background, gold trunk strokes, color-coded risk pills
(green / amber / red), English labels, no real manufacturer logos.
```

### T07 DVP&R / Test 计划树（Test Plan Tree）

事实源参考：`engineering/v2/scheme-XX/test_dvpr/*.md`。

**生图提示词**：

```text
Generate a left-to-right tree diagram of a verification plan. Root: <SCHEME_NAME>
verification. Level 1 branches: <SCHEME_TEST_AXES>. Level 2 leaves show short
acceptance hooks in English. Use clean vector style, dark navy background,
gold and pale blue accents, monospace labels for test IDs. No people, no labs,
no marketing photos.
```

### T08 协议链路图（Protocol / Diagnostics Link）

事实源参考：`reports/scheme_driver_power_protocol_diagrams.md`「协议链路图」。

**生图提示词**：

```text
Generate a network-style block diagram of communication links for an EV traction
controller. Nodes: VCU CAN/CAN-FD, MCU command parser, <SCHEME_PROTOCOL_BLOCK>,
FOC controller, SVPWM, UDS / XCP diagnostic interface, calibration tool. Show
arrows for direction, label each link with its bus type. Dark navy background,
gold accents, English labels, no people, no extra decoration.
```

## 3. 方案级差分提示词

每个方案给出 6 类核心图的差分 token：T01 `<SCHEME_BLOCK>`、T03 `<SCHEME_STATES>` 与 `<SCHEME_TRANSITIONS>`、T04 `<SCHEME_PCB_BLOCKS>`、T05 `<SCHEME_CAD_ELEMENTS>`、T06 `<SCHEME_BOM_GROUPS>`、T07 `<SCHEME_TEST_AXES>`、T08 `<SCHEME_PROTOCOL_BLOCK>`。

未落地草案的方案（S03/S05/S06/S07/S08/S09/S10/S12）给出基于 README 必需交付物的占位差分，标注「未落 markdown 草案，先生概念图」。

### 3.1 S01 `negative_d_axis_field_weakening`

事实源：`engineering/v2/scheme-01/`，已落 PCB / CAD / Controller / BOM / DVP 草案。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `negative_d_axis_field_weakening id_min(T,fault) limiter, with arrows from temperature sensor and Vdc sense feeding into it` |
| T03 `<SCHEME_STATES>` | `Power On + ADC self-test`, `Normal Torque Control (MTPA request)`, `Voltage Limited (enter field weakening)`, `Apply id_min(T,fault) clamp`, `Derate Torque`, `Fault Fallback (gate disable)` |
| T03 `<SCHEME_TRANSITIONS>` | `sensors valid`, `V margin < limit`, `speed high`, `demag / current risk`, `margin recovered`, `self-test fail`, `sensor / fault latch` |
| T04 `<SCHEME_PCB_BLOCKS>` | `Phase current sensing ia/ib/ic`, `Vdc sense divider`, `Motor & inverter temperature inputs`, `Gate-disable_n hardware path`, `Fault latch readback`, `MCU ADC front-end` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `three-phase busbar from inverter to motor`, `current sensor windows on busbar`, `motor-side and inverter-side temperature sensor mounts`, `LV / HV keep-out partition`, `service access for fault latch` |
| T06 `<SCHEME_BOM_GROUPS>` | `Current sensors`, `Vdc divider network`, `Temperature sensors`, `Gate-disable latch`, `Fault feedback chain` |
| T07 `<SCHEME_TEST_AXES>` | `Field weakening entry/exit`, `id_min(T,fault) clamp validation`, `Sensor fault injection`, `Gate-disable latch test` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `voltage / current / demag limiter` |

改图建议：使用 `engineering/v2/scheme-01/controller/V2-S01-CTRL-field_weakening_state_machine-r00.drawio` 导出 PNG，作为 T03 改图参考，写指令「保留状态名与转移条件英文标签，统一为深色信息图风格」。

### 3.2 S02 `mtpa_fw_mtpv_control`

事实源：`engineering/v2/scheme-02/`，已落 PCB / CAD / Controller / BOM / DVP 草案。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `MTPA / FW / MTPV LUT block taking torque request, feeding feasibility + derating, then current controller` |
| T03 `<SCHEME_STATES>` | `MTPA idle`, `MTPA active`, `Field Weakening`, `MTPV`, `Derate`, `LUT CRC fault fallback` |
| T03 `<SCHEME_TRANSITIONS>` | `LUT CRC ok`, `speed > base`, `V margin < limit`, `MTPV boundary reached`, `LUT CRC fail`, `mode reset` |
| T04 `<SCHEME_PCB_BLOCKS>` | `MCU + NVM (control LUT storage)`, `ADC front-end`, `Resolver / encoder interface`, `CAN / CAN-FD transceiver`, `LUT version diagnostic interface` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `controller enclosure outline`, `connector positions`, `harness exits`, `cooling path against power module`, `EMI partition between LV and HV` |
| T06 `<SCHEME_BOM_GROUPS>` | `MCU + NVM`, `ADC`, `Position interface`, `Communication transceivers`, `LUT release infrastructure` |
| T07 `<SCHEME_TEST_AXES>` | `MTPA / FW / MTPV HIL`, `LUT CRC and version control`, `Power-off recovery`, `Mode continuity` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `mode selector (MTPA / FW / MTPV) and id/iq reference LUT` |

改图建议：用 `engineering/v2/scheme-02/controller/V2-S02-CTRL-mode_transition_lut-r00.drawio` 导出图作为参考。

### 3.3 S03 `svpwm_overmodulation_voltage_utilization`

事实源：`engineering/v2/scheme-03/README.md`，所有正式图纸 `missing`，先用 README 必需交付物作占位。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `SVPWM / overmodulation / six-step selector block fed by FOC voltage command and Vdc sense, with THD / NVH monitor input` |
| T03 `<SCHEME_STATES>` | `Linear SVPWM`, `Overmodulation Region 1`, `Overmodulation Region 2`, `Six-Step`, `Derate on THD limit`, `Fallback to linear` |
| T03 `<SCHEME_TRANSITIONS>` | `voltage utilization rising`, `THD limit hit`, `NVH limit hit`, `Vdc recovered`, `safety derate request` |
| T04 `<SCHEME_PCB_BLOCKS>` | `Gate driver with dead-time control`, `EMC / EMI filter`, `Phase current sensing`, `DC-link capacitor bank`, `Bus bar interface` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `power module`, `DC-link capacitor`, `busbar layout`, `heatsink and cold plate interface`, `EMI shielding partitions` |
| T06 `<SCHEME_BOM_GROUPS>` | `Gate driver`, `Power modules`, `DC-link capacitors`, `Busbar`, `EMI components` |
| T07 `<SCHEME_TEST_AXES>` | `THD measurement`, `EMC compliance`, `NVH (torque ripple)`, `Inverter loss`, `Thermal stress` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `modulation mode telemetry + THD / NVH guard channel` |

注：本方案仅有概念占位，生图必须明确标注 "concept page, no real layout"。

### 3.4 S04 `nonlinear_flux_lut`

事实源：`engineering/v2/scheme-04/`，已落 PCB / CAD / Controller / BOM / DVP 草案；同时 EXP-006 phase-2 数值闭环已通过 targeted pytest。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `nonlinear flux LUT observer block taking id, iq, omega, and temperature, outputting lambda_d / lambda_q to FOC` |
| T03 `<SCHEME_STATES>` | `LUT load + CRC check`, `Bounds check passed`, `Bilinear interpolation active`, `Out-of-bounds clamp`, `Error monitor warning`, `Fallback to linear dq` |
| T03 `<SCHEME_TRANSITIONS>` | `LUT CRC ok`, `query inside LUT bounds`, `interpolation residual ok`, `out-of-bounds detected`, `monitor over threshold`, `recover to LUT` |
| T04 `<SCHEME_PCB_BLOCKS>` | `LUT observer inputs (id, iq, omega, T)`, `bounds checker`, `fallback diagnostic line`, `error budget telemetry`, `MCU NVM for LUT` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `FEA geometry source reference frame`, `dq coordinate origin`, `material stack callouts`, `mesh boundary illustration`, `sensor position bindings` |
| T06 `<SCHEME_BOM_GROUPS>` | `Current sensors`, `Position sensors`, `Temperature sensors`, `Vdc sensing`, `Diagnostic NVM` |
| T07 `<SCHEME_TEST_AXES>` | `LUT bounds enforcement`, `Interpolation consistency`, `FEA version binding`, `Bench correlation`, `Fallback behavior` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `LUT version + bounds telemetry` |

改图建议：以 `engineering/v2/scheme-04/controller/V2-S04-CTRL-flux_lut_interpolation-r00.drawio` 导出图作为参考。

### 3.5 S05 `magnetic_saturation_codesign`

事实源：`engineering/v2/scheme-05/README.md`，所有正式图纸 `missing`。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `candidate geometry generator -> FEA lambda LUT -> scorecard block feeding control LUT` |
| T03 `<SCHEME_STATES>` | `Candidate geometry intake`, `FEA LUT request`, `Scorecard evaluation`, `Down-select`, `Stop-criteria triggered` |
| T03 `<SCHEME_TRANSITIONS>` | `FEA result available`, `score above threshold`, `stress / demag risk too high`, `pareto loser`, `retain for trade study` |
| T04 `<SCHEME_PCB_BLOCKS>` | `saturation observer sample inputs`, `flux estimation diagnostics`, `MCU compute headroom block`, `optional bench data ingestion port` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `rotor barrier and bridge cross-section`, `stator slot outline`, `lamination stack`, `mechanical stress callouts`, `magnet pockets` |
| T06 `<SCHEME_BOM_GROUPS>` | `Electrical steel`, `Permanent magnets`, `Rotor process tooling`, `Saturation observer sensors` |
| T07 `<SCHEME_TEST_AXES>` | `FEA correlation`, `Mechanical stress`, `Iron loss`, `Demagnetization`, `NVH` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `candidate ID + score versioning channel` |

### 3.6 S06 `pmasynrm_high_saliency_low_pm`

事实源：`engineering/v2/scheme-06/README.md`，所有正式图纸 `missing`。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `high-saliency MTPA / MTPV control block with low-PM demag boundary monitor` |
| T03 `<SCHEME_STATES>` | `MTPA active`, `High-saliency FW`, `MTPV`, `Low-PM demag guard`, `Derate` |
| T03 `<SCHEME_TRANSITIONS>` | `MTPA boundary reached`, `FW margin shrinking`, `MTPV boundary`, `demag risk rising`, `recover` |
| T04 `<SCHEME_PCB_BLOCKS>` | `high-saliency control inputs`, `demag diagnostic input`, `current sensing for low-PM operating range`, `position sensor interface` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `PM fraction layout in rotor`, `flux barrier pattern`, `magnetic bridge`, `hairpin stator slot outline`, `cooling jacket interface` |
| T06 `<SCHEME_BOM_GROUPS>` | `Low-PM magnets`, `Laminations`, `Hairpin windings`, `Cooling / temperature sensing` |
| T07 `<SCHEME_TEST_AXES>` | `Torque ripple`, `Mechanical stress`, `Demagnetization`, `Thermal`, `NVH` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `saliency control telemetry + demag warning channel` |

### 3.7 S07 `variable_magnetization_memory_motor`

事实源：`engineering/v2/scheme-07/README.md`，所有正式图纸 `missing`，且外部 review-pr 提醒不能用 `psi_f` 缩放代理硬件。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `magnetization pulse driver block with energy storage bank, isolated gate path, current monitor, and interlock to FOC` |
| T03 `<SCHEME_STATES>` | `Magnetization idle`, `Pre-charge energy bank`, `Apply magnetization pulse`, `Apply de-magnetization pulse`, `Verify flux state`, `Unknown-state fallback`, `Lifetime cycle count update` |
| T03 `<SCHEME_TRANSITIONS>` | `bank ready`, `pulse trigger`, `state observed ok`, `state unknown`, `cycle limit reached`, `safe retreat` |
| T04 `<SCHEME_PCB_BLOCKS>` | `pulse capacitor bank`, `bi-directional pulse driver`, `pulse current sensing`, `isolation barrier`, `interlock with traction inverter` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `memory magnet placement`, `magnetization path cross-section`, `rotor magnetic circuit`, `thermal path callouts` |
| T06 `<SCHEME_BOM_GROUPS>` | `Pulse power stage`, `Energy storage`, `Magnet materials`, `Flux state observers`, `Safety isolation` |
| T07 `<SCHEME_TEST_AXES>` | `Magnetization / demagnetization pulses`, `State retention`, `Temperature drift`, `Unknown-state fallback`, `Lifetime cycling` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `flux state + lifetime cycle counter telemetry` |

注：生图标注 "research-pool concept, not engineering release"。

### 3.8 S08 `hybrid_excitation`

事实源：`engineering/v2/scheme-08/README.md`，所有正式图纸 `missing`；EXP-007 仅有 `psi_eff` 代理。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `field excitation DC/DC converter feeding field winding, with field current sense and loss-of-field detector wired into FOC` |
| T03 `<SCHEME_STATES>` | `Field excitation idle`, `Field excitation active`, `Three-variable control (id, iq, if)`, `Loss-of-field detected`, `Fallback to PM-only operation` |
| T03 `<SCHEME_TRANSITIONS>` | `field DC/DC enable`, `if reference set`, `optimization step`, `loss-of-field flag`, `recover` |
| T04 `<SCHEME_PCB_BLOCKS>` | `field DC/DC converter`, `field current sensing`, `loss-of-field detection`, `isolation between field and traction loops`, `over-excitation protection` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `field winding placement`, `slip-ring or brushless exciter`, `cooling interface for field winding`, `insulation barrier`, `excitation harness routing` |
| T06 `<SCHEME_BOM_GROUPS>` | `Field power devices`, `Field winding`, `Insulation system`, `Connectors`, `Excitation sensors` |
| T07 `<SCHEME_TEST_AXES>` | `Field thermal stress`, `Loss-of-field`, `Three-variable optimization`, `Bench validation` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `field current + loss-of-field telemetry` |

### 3.9 S09 `winding_reconfiguration`

事实源：`engineering/v2/scheme-09/README.md`，所有正式图纸 `missing`；EXP-008 只是静态 Ke/Kt 缩放代理。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `winding-switch matrix block between inverter outputs and motor terminals, with interlock, arc suppression, and state feedback` |
| T03 `<SCHEME_STATES>` | `Configuration A`, `Zero-torque window`, `Switch in progress`, `Configuration B`, `Illegal-state fallback`, `Circulating-current detected` |
| T03 `<SCHEME_TRANSITIONS>` | `switch request`, `zero-torque verified`, `switch complete`, `illegal state detected`, `current re-balanced`, `arc suppression triggered` |
| T04 `<SCHEME_PCB_BLOCKS>` | `high-voltage contactor or solid-state switch driver`, `interlock logic`, `arc suppression`, `state feedback to MCU`, `gate-disable backup path` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `motor winding end-turn arrangement`, `reconfiguration switch placement`, `insulation barriers`, `heat-path callouts`, `harness routing` |
| T06 `<SCHEME_BOM_GROUPS>` | `Switches and drivers`, `Interlock electronics`, `Harness and insulation`, `Sensing for circulating current` |
| T07 `<SCHEME_TEST_AXES>` | `Switching transient`, `Circulating current`, `Arc / insulation`, `Open / short / stuck fault behavior` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `winding configuration + switch state telemetry` |

### 3.10 S10 `multiphase_phase_group_control`

事实源：`engineering/v2/scheme-10/README.md`，所有正式图纸 `missing`；EXP-009 仅有可用电流降额代理。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `multiphase inverter with per-phase-group current sensing feeding a fault torque allocator and harmonic subspace controller` |
| T03 `<SCHEME_STATES>` | `Healthy multiphase`, `Single-phase fault`, `Phase-group fault`, `Derate via torque allocator`, `Shut down` |
| T03 `<SCHEME_TRANSITIONS>` | `phase fault detected`, `group fault detected`, `derate request`, `thermal limit`, `fault cleared` |
| T04 `<SCHEME_PCB_BLOCKS>` | `multiphase inverter stage`, `per-phase-group current sense`, `isolation barriers`, `phase-cutoff switches`, `connector interface` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `multiphase motor terminal layout`, `harness with per-phase routing`, `phase-group packaging boundary`, `thermal path per group` |
| T06 `<SCHEME_BOM_GROUPS>` | `Multiphase power modules`, `Sensing chain`, `Connectors`, `Harness`, `Isolation` |
| T07 `<SCHEME_TEST_AXES>` | `Single-phase fault`, `Phase-group fault`, `Harmonic subspace`, `Thermal`, `NVH` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `phase health + harmonic subspace telemetry` |

### 3.11 S11 `thermal_demag_safety_protection`

事实源：`engineering/v2/scheme-11/`，已落 PCB / CAD / Controller / BOM / DVP 草案。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `safety supervisor block taking magnet temperature, winding temperature, oil temperature, Vdc, current, and rotor speed, gating torque request and gate-disable` |
| T03 `<SCHEME_STATES>` | `Normal`, `Thermal / demag warning`, `Active derating`, `Unknown sensor fallback`, `Hardware gate-disable`, `Latched fault` |
| T03 `<SCHEME_TRANSITIONS>` | `temperature rising`, `derate trigger`, `sensor open / short`, `gate-disable assertion`, `latch set`, `latch reset only by service` |
| T04 `<SCHEME_PCB_BLOCKS>` | `temperature sensor front-ends`, `fault latch logic`, `gate-disable hardware path`, `fault classification readback`, `isolation` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `magnet temperature sensor mount`, `winding temperature sensor`, `oil / coolant temperature path`, `controller heatsink interface`, `service access` |
| T06 `<SCHEME_BOM_GROUPS>` | `Temperature sensors`, `Safety latch`, `Gate-disable hardware`, `Isolation parts`, `Fault feedback chain` |
| T07 `<SCHEME_TEST_AXES>` | `Thermal / demag derate`, `Sensor open-short`, `Unknown fallback`, `Gate-disable assertion`, `Latch recovery` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `safety fault classification + latch state telemetry` |

改图建议：以 `engineering/v2/scheme-11/controller/V2-S11-CTRL-safety_fault_state_machine-r00.drawio` 导出图作为参考。

### 3.12 S12 `weighted_efficiency_pareto_selection`

事实源：`engineering/v2/scheme-12/README.md`，所有正式图纸 `missing`；EXP-010 为说明性 drive cycle 代理。

| 模板 | 差分 token |
|---|---|
| T01 `<SCHEME_BLOCK>` | `pareto scorecard block consuming drive cycle weights, system losses, maturity scores, and risk factors, producing a candidate ranking` |
| T03 `<SCHEME_STATES>` | `Candidate intake`, `Drive cycle weighting`, `System loss aggregation`, `Maturity + risk scoring`, `Pareto ranking`, `Trade-study output` |
| T03 `<SCHEME_TRANSITIONS>` | `inputs versioned`, `weights applied`, `scores computed`, `pareto sweep`, `recommendation issued` |
| T04 `<SCHEME_PCB_BLOCKS>` | `candidate PCB / BOM / EDA index node (no real PCB)`, `audit trail interface`, `version registry` |
| T05 `<SCHEME_CAD_ELEMENTS>` | `candidate package index nodes for several topologies, with mass, packaging, and cooling boundaries as boxes` |
| T06 `<SCHEME_BOM_GROUPS>` | `Per-candidate BOM cost`, `Manufacturing risk`, `Supply risk`, `Controller delta cost` |
| T07 `<SCHEME_TEST_AXES>` | `Drive cycle audit`, `System loss audit`, `Sensitivity sweep`, `Evidence-path audit` |
| T08 `<SCHEME_PROTOCOL_BLOCK>` | `scorecard version + audit telemetry` |

## 4. 改图（图像到图像）工作流约定

1. 优先从 `.drawio` 导出 PNG（draw.io desktop / VS Code 插件均支持）或从 mermaid 渲染 PNG 作为输入参考图。
2. 改图提示词模板：

```text
Reference image: <V2-SXX-...> exported PNG.
Goal: re-render in the shared style baseline.
Preserve: every English node label, every transition label, the topology (nodes and edges).
Change: background to dark navy, node fill to pale blue, stroke to gold, sans-serif typography,
remove draw.io watermark, remove grid noise. Keep aspect ratio.
Do NOT add: people, marketing copy, manufacturer logos, decorative gradients.
```

3. 改图结果不得修改任何状态、信号、节点的语义；语义改动必须先回到 `.drawio` 源文件。

## 5. 落地行动

| 行动 | 目标 |
|---|---|
| DRAW-01 | 用 T03 + 3.1 / 3.2 / 3.4 / 3.11 的差分 token，先把 4 个已落 `.drawio` 的状态机生成统一风格的概念图 |
| DRAW-02 | 用 T01 + T08 的提示词为所有 12 个方案生成驱动设计图与协议链路图（mermaid 已存在） |
| DRAW-03 | 为 S03 / S05 / S06 / S07 / S08 / S09 / S10 / S12 生成 T03 概念图，并在 README 中明确标 "concept page" |
| DRAW-04 | 把生成图按 `engineering/v2/scheme-XX/<category>/illustrations/` 子目录归档，命名前缀 `V2-SXX-ILL-<topic>-r00.png` |
| DRAW-05 | 在每张生成图旁加 `*-prompt.txt`，保存最终使用的 prompt 与版本号，确保可重复 |

## 6. 禁止误读

- 文本生图产物不是 EDA / CAD / FEA 输出。
- 生图不能替代 `tests/`、`experiments/`、`models/scheme_simulation_coverage.json` 中的可复现证据。
- `engineering_validated` 状态不会因为生图美化而提升。
- 不要把生成图嵌入 `.drawio` 源文件正文，只可作为外部 illustration 引用。
