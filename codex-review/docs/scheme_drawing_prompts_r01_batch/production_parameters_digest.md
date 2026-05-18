# 12 方案生产参数总览（嵌入 r01 提示词的参数清单）

修订日期：2026-05-18
作用：把每方案 r01 提示词嵌入的生产参数集中登记，便于审计与后续 r02/r03 替换。
出处：`engineering/v2/scheme-XX/{controller,pcb,cad,bom_eda,test_dvpr}/`、`models/motor_params.json`、`models/control_lut.json`、`models/control_lut_schema.json`、r01 工程窗估值。
关联：`scheme-01-r01.md`..`scheme-12-r01.md`。

> 凡标 `estimate` 或 `r01 工程窗` 的参数都尚未台架验证，r02 仿真闭环或 r03 实测必须替换。

---

## 1. 共享电气底座（多方案复用）

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| pole_pairs | 4 | — | motor_params.json |
| Vdc 标称 | 360 | V | motor_params.json |
| Vmax SVPWM linear | 207.85 | V | 1/√3 · Vdc |
| Imax_phase_peak | 260 | A | motor_params.json |
| speed_max | 18 000 | rpm | motor_params.json |
| speed_step | 250 | rpm | motor_params.json |
| FW V_margin 进入阈值 | 5 | V | r01 工程窗 |
| id_min(T=25 °C) | -240 | A | r02 demag estimate |
| temp_coefficient | -0.0035 | A/°C | r02 demag estimate |

---

## 2. 方案专属生产参数

### 2.1 S01 negative_d_axis_field_weakening

- PCB 信号：`ia/ib/ic`、`vdc_sense`、`motor_temp`、`inverter_temp`、`gate_disable_n`、`fault_latched`
- BOM 5 分支风险：current sensors=MED、Vdc divider=MED、temperature=LOW、gate-disable latch=HIGH、fault feedback=MED
- DVP IDs：S01-DV-001..005

### 2.2 S02 mtpa_fw_mtpv_control

- torque_axis r03 标称：[50, 100, 150, 200] N·m
- LUT CRC：CRC-32 IEEE 802.3
- NVM 双 banks A/B + version semver
- 模式跳变 id_jump <= 30 A、iq_jump <= 30 A、torque_jump <= 5.0 N·m
- ADC：12-bit 100 kSPS
- CAN-FD：5 Mbit/s；SPI MCU↔NVM：50 MHz；Ethernet XCP：100 Mbit/s
- BOM：MCU+NVM=HIGH、ADC=MED、resolver=MED、CAN-FD=LOW、LUT release infra=HIGH
- DVP IDs：S02-DV-001..005
- 完整 r02 sheet：`engineering/v2/scheme-02/parameters/V2-S02-PARAM-*-r02.{md,json}`

### 2.3 S03 svpwm_overmodulation_voltage_utilization

- Vmax linear：207.85 V；Vmax six-step：~229.18 V
- Modulation index 阈值：0.907 / 0.952 / 1.000
- THD limit：8 %；EMC：EN 55025 Class 5
- 开关频率：10 kHz；Dead-time：1.5 μs
- BOM：gate driver=HIGH、power modules=HIGH、DC-link cap=MED、busbar=LOW、EMI=MED
- DVP IDs：S03-DV-001..005（待 r03 锁定）

### 2.4 S04 nonlinear_flux_lut

- LUT 输入：id [-260..+40 A]、iq [0..260 A]、omega_e [0..7540 rad/s]、T [25..120 °C]
- LUT 输出：lambda_d / lambda_q (Wb)；CRC-32
- 插值：双线性；越界 fallback：linear dq
- residual_high 阈值：12 %
- ADC：12-bit ±0.5 % FS；位置延迟预算 <= 60 μs
- BOM：current=MED、position=HIGH、temperature=MED、Vdc=LOW、NVM=HIGH
- DVP IDs：S04-DV-001..005

### 2.5 S05 magnetic_saturation_codesign

- 候选 geometry：3-6；FEA LUT 节点：id×iq×T = 30×30×5
- 候选 score 阈值：torque +5 %、iron loss +3 %、stress < 600 MPa、demag id_min >= -240 A、ripple <= 3 %
- BOM：electrical steel=MED、PM=HIGH、rotor tooling=HIGH、saturation sensors=MED、stator lamination=LOW
- DVP IDs：S05-DV-001..005（待 r03 锁定）

### 2.6 S06 pmasynrm_high_saliency_low_pm

- 凸极比 Lq/Ld：>= 5；PM fraction：30-50 %
- demag id_min（low PM）：-200 A
- 转子最大应力：< 700 MPa；ripple <= 3 %
- BOM：low-PM=HIGH、laminations=MED、hairpin=MED、cooling=LOW、resolver=MED
- DVP IDs：S06-DV-001..005（待 r03 锁定）

### 2.7 S07 variable_magnetization_memory_motor（research pool）

- 磁化脉冲：800 V / 1000 A 峰值 / 50 μs / 能量 100 J
- 磁状态分辨率：8 级；寿命循环上限：10 000 次
- 互锁验证延迟：< 1 ms
- BOM：pulse stage=HIGH、energy storage=HIGH、magnet=MED、observer=HIGH、isolation=HIGH
- DVP IDs：S07-DV-001..005（待 r03 锁定）

### 2.8 S08 hybrid_excitation（research pool）

- 励磁 DC/DC：48 V output；if range：[-20, +30] A
- psi_eff range：0.02-0.10 Wb
- Loss-of-field 检测窗：< 5 ms
- 绝缘等级：H；冷却：油/液冷
- BOM：field power=HIGH、winding=MED、insulation=HIGH、connectors=MED、excitation sensors=MED
- DVP IDs：S08-DV-001..004（待 r03 锁定）

### 2.9 S09 winding_reconfiguration（research pool）

- 切换状态：A（星形）/B（三角形等价），Ke/Kt 配置 B = A × 1.73
- HV 接触器：800 V / 300 A class
- Zero-torque window：50-200 ms
- 互锁验证延迟：< 1 ms；环流检测阈值：5 A
- BOM：switches/drivers=HIGH、interlock=HIGH、harness=MED、sensing=MED
- DVP IDs：S09-DV-001..004（待 r03 锁定）

### 2.10 S10 multiphase_phase_group_control（research pool）

- 相数：6（双 3-phase 相组）；Per-phase 峰值：130 A
- 故障检测窗：< 2 ms；谐波子空间：αβ + xy
- 单相故障 derate：50 %；相组故障 derate：100 %（shut down）
- BOM：multiphase power=HIGH、sensing=HIGH、connectors=MED、harness=MED、isolation=HIGH
- DVP IDs：S10-DV-001..005（待 r03 锁定）

### 2.11 S11 thermal_demag_safety_protection

- pm_temp：warning 100 °C / critical 120 °C
- winding_temp：warning 140 °C / critical 160 °C
- oil_temp：warning 80 °C / critical 100 °C
- Vdc 安全窗：240-420 V critical
- id_min(T)：-240 - 0.0035 × (T - 25) [A]
- gate-disable 关断延迟目标：< 100 μs
- 传感器开短路检测：< 1 ms；latch reset：仅服务工具
- BOM：temperature=MED、safety latch=HIGH、gate-disable=HIGH、isolation=MED、fault feedback=MED
- DVP IDs（来自 r00 DVP 草案）：S11-DV-001..005（不再使用 TST-THM-001 等占位）

### 2.12 S12 weighted_efficiency_pareto_selection

- 候选方案数：11（S01-S11）
- Drive cycle 权重：WLTP 0.4 / CLTC 0.3 / Urban 0.2 / Highway 0.1
- Score 维度：5（效率 / 性能 / 成本 / 体积 / 风险）；TRL 等价 1-5
- Sensitivity sweep：±20 % 权重扰动
- BOM：per-candidate cost=MED、manufacturing risk=MED、supply risk=HIGH、controller delta=MED
- DVP IDs：S12-DV-001..004（待 r03 锁定）

---

## 3. 参数收口与升级路径

| 档位 | 参数状态 | 责任 | 触发条件 |
|---|---|---|---|
| r01（本批） | 工程窗 estimate + 已有草案数值 | Claude / Codex | 落地 r01 提示词 |
| r02 | FEA / 仿真闭环参数 | Claude / Codex | 每方案 `engineering/v2/scheme-XX/parameters/` 沉淀 sheet（S02 已示范） |
| r03 | 仿真闭环 pass/fail + pytest 校验 | 工程组 | 每方案 `sim/run_scheme_XX_*.py` + `tests/test_scheme_XX_*.py` |
| 工程发布 | 台架 / FEA / HIL 三件实测 | 工程组 | `engineering_validated = true` 翻转 |

> 当前所有 r01 数值都不允许翻 `engineering_validated`；r02 仿真通过也不翻；只有台架 + FEA + HIL 三件齐才能翻。

## 4. 待对齐项

| 项 | 状态 | 处理 |
|---|---|---|
| `models/motor_params.json` Rs / Ld / Lq / psi_f 仍为 `estimate` | open | r02 nonlinear flux LUT 替换 |
| S07 / S08 / S09 / S10 仍是 research pool 占位参数 | open | r02 仅在确定上线时推进 |
| `gpt-image-2/prompts/schemes.json` 尺寸覆盖未落 | open | 下一轮代码变更 |
| `engineering/v2/scheme-XX/illustrations/` 目录仍空 | open | r01 出图后归档 |
| DVP IDs（S03/S05/S06/S07/S08/S09/S10/S12）为占位 | open | r02 时按草案锁定 |
