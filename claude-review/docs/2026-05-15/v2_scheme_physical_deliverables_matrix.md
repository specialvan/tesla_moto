# V2 分方案物理工程交付物矩阵

日期：2026-05-15  
目标：把 V2 每个方案从“工程推进描述”进一步落到可见的 PCB、3D/CAD、控制器设计、BOM/EDA、仿真和阶段门图纸包，防止只停留在文字 playbook、数值仿真或参数缩放。

关联文档：

- `claude-review/docs/2026-05-15/v2_scheme_engineering_playbook.md`
- `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.md`
- `reports/scheme_driver_power_protocol_diagrams.md`
- `reports/scheme_bom_eda_integration_design.md`
- `reports/scheme_industry_design_stage_gate_process.md`
- `engineering/v2/README.md`

---

## 1. 文档定位

本矩阵补齐用户指出的关键缺口：每个方案若要称为“深度工程落地”，不能只有控制策略、仿真结论或阶段门描述，必须能看到对应的物理设计交付物。

V2 判定规则：

1. **没有 PCB / EDA 页级对象**：不得进入电控硬件 G4。
2. **没有 3D / CAD / 封装边界**：不得宣称机械、冷却、装配或量产可行。
3. **没有控制器设计图**：不得宣称控制闭环、故障路径或标定发布可行。
4. **没有 BOM / 制造包 / 版本号**：不得进入样机或供应链评审。
5. **没有 DVP&R / DFMEA / gate evidence**：不得把 numeric simulation 写成 engineering validated。

---

## 2. 统一图纸与工程包分类

| 分类 | 必需内容 | 典型格式 | 阶段门 |
|---|---|---|---|
| PCB / Electrical | 原理图、Layout、stackup、隔离、采样、驱动、连接器、保护页 | PDF、Altium/KiCad、Gerber、ODB++ | G2-G4 |
| 3D / CAD | 电机截面、转子/定子、壳体、冷却油路、母排、连接器、装配干涉 | STEP、Parasolid、SolidWorks、Motor-CAD/Maxwell 几何 | G2-G5 |
| Controller Design | 控制框图、状态机、故障路径、标定 map、模式切换、降额策略 | drawio、SVG、PDF、Simulink/Python block | G3-G5 |
| BOM / EDA / MFG | BOM、网表、线束、Pick-place、IPC 图、制造说明、供应商字段 | XLSX、CSV、PDF、EDA export | G4-G6 |
| Simulation / Test | FEA、热、NVH、HIL、bench、DVP&R、DFMEA/FMDEA | report、CSV、summary JSON、test protocol | G3-G7 |

---

## 3. 文件命名与目录模板

### 3.1 目录模板

```text
engineering/v2/scheme-XX/
  README.md
  pcb/
  cad/
  controller/
  bom_eda/
  simulation/
  test_dvpr/
  gate_review/
```

当前仓库已先落地 `engineering/v2/README.md` 和 `engineering/v2/scheme-01/README.md` 至 `engineering/v2/scheme-12/README.md` 作为审计索引；尚未创建或伪造正式 PCB、CAD、EDA、drawio、BOM 或 DVP&R 文件。

### 3.2 文件命名模板

```text
V2-S<scheme_id>-<domain>-<artifact_name>-r<rev>.<extension>
```

领域枚举：`PCB`、`CAD`、`CTRL`、`BOM`、`EDA`、`FEA`、`THERMAL`、`NVH`、`TEST`、`DFMEA`、`DVP`、`GATE`。

示例：

- `V2-S01-PCB-current_voltage_sensing-r00.pdf`
- `V2-S03-CTRL-overmodulation_state_machine-r00.drawio`
- `V2-S07-CAD-memory_motor_rotor_stack-r00.step`
- `V2-S08-EDA-field_excitation_driver_bom-r00.xlsx`
- `V2-S11-DVP-demag_thermal_fault_injection-r00.md`

### 3.3 状态标签

| 标签 | 含义 | 可进入阶段 |
|---|---|---|
| `missing` | 尚无图纸本体或正式交付物文件；可已有 README 索引/目录锚点 | 不能过 G2 |
| `indexed` | 已有 README 审计索引和目录锚点，但无图纸本体 | 不能过 G2 |
| `stub` | 有占位图纸/接口草案文件 | G0-G1 |
| `draft` | 有可评审初稿文件 | G2-G3 |
| `reviewed` | 已完成设计评审 | G4-G5 |
| `released` | 已纳入版本和制造包 | G6-G7 |

---

## 4. 12 个方案物理交付矩阵

### 4.1 S01 负 d 轴弱磁（`negative_d_axis_field_weakening`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 电流采样、Vdc 采样、相电压重建、温度采样、gate-disable / fault latch 页 | `V2-S01-PCB-sensing_fault_path-r00.pdf` | G4 | ERC/DRC 通过，采样精度与 fault latch 路径可追溯 | `indexed` |
| 3D/CAD | 逆变器到电机三相连接、母排、电流传感器安装、温度传感器布置 | `V2-S01-CAD-sensor_busbar_layout-r00.step` | G3 | 间隙、爬电、装配空间和热路径明确 | `missing` |
| Controller | 弱磁状态机、`id_min(T,fault)` 限幅、低压/高温 derating、fallback | `V2-S01-CTRL-field_weakening_state_machine-r00.drawio` | G3 | control LUT 不可行原因和降额动作闭合 | `indexed` |
| BOM/EDA | 传感器、隔离采样、栅极关断、诊断输入 BOM | `V2-S01-BOM-sensing_fault_components-r00.xlsx` | G4 | 关键器件精度、温漂、诊断覆盖字段完整 | `missing` |
| Test | 高速低压、高温、传感器故障注入 DVP&R | `V2-S01-DVP-fw_fault_injection-r00.md` | G5 | 台架能复现电压/电流/退磁边界 | `missing` |

### 4.2 S02 MTPA / FW / MTPV 连续控制（`mtpa_fw_mtpv_control`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | MCU/NVM、resolver、ADC、电流采样、CAN/诊断接口页 | `V2-S02-PCB-control_io_map-r00.pdf` | G4 | 控制 LUT 存储、刷新、CRC、诊断链路明确 | `indexed` |
| 3D/CAD | 控制器壳体、接插件、散热路径、线束出口 | `V2-S02-CAD-controller_packaging-r00.step` | G3 | 接插件方向、线束半径和热界面可评审 | `missing` |
| Controller | MTPA/FW/MTPV 模式图、二维速度-转矩 LUT、切换连续性图 | `V2-S02-CTRL-mode_transition_lut-r00.drawio` | G3 | `id_jump/iq_jump/torque_jump` 有限且有回归测试 | `indexed` |
| BOM/EDA | MCU、NVM、resolver interface、通讯与标定接口 BOM | `V2-S02-EDA-controller_core_bom-r00.xlsx` | G4 | 容量、时序、ASIL/诊断字段可追踪 | `missing` |
| Test | HIL 模式切换、LUT CRC、断电恢复、标定一致性 | `V2-S02-TEST-lut_mode_hil-r00.md` | G5 | HIL 覆盖全部模式和不可行区 | `missing` |

### 4.3 S03 SVPWM / 过调制（`svpwm_overmodulation_voltage_utilization`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 栅极驱动、死区、母线电容、相电流采样、EMI/EMC 滤波页 | `V2-S03-PCB-gate_pwm_emc-r00.pdf` | G4 | 开关边沿、隔离、电流环采样窗口可评审 | `missing` |
| 3D/CAD | 逆变器功率模块、DC-link、母排、散热器与屏蔽结构 | `V2-S03-CAD-inverter_power_stage-r00.step` | G3 | 杂散电感、冷却接触和 EMC 屏蔽边界明确 | `missing` |
| Controller | SVPWM/六步/过调制状态机、进入/退出窗口、THD/NVH 限制 | `V2-S03-CTRL-overmodulation_state_machine-r00.drawio` | G3 | 退出条件、故障回退和调制因子限制可测试 | `indexed` |
| BOM/EDA | Gate driver、功率模块、电容、母排、EMI 元件 BOM | `V2-S03-BOM-inverter_overmodulation-r00.xlsx` | G4 | 器件电压/电流/热裕度满足高速区需求 | `missing` |
| Test | THD、EMC、NVH、逆变器损耗、热冲击测试计划 | `V2-S03-DVP-thd_emc_nvh-r00.md` | G5 | 过调制收益大于损耗/噪声/EMC 风险 | `missing` |

### 4.4 S04 非线性磁链 LUT（`nonlinear_flux_lut`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 无新增功率页；需要温度、位置、电流采样精度证明页 | `V2-S04-PCB-lut_observer_inputs-r00.pdf` | G4 | LUT 输入信号精度支持插值误差预算 | `indexed` |
| 3D/CAD | Maxwell/Motor-CAD 几何源、dq 坐标定义、FEA 网格截图 | `V2-S04-CAD-fea_geometry_source-r00.step` | G3 | 几何版本、坐标、单位、材料与 LUT 版本绑定 | `missing` |
| Controller | LUT 插值框图、边界 clamp/拒绝策略、误差监控 | `V2-S04-CTRL-flux_lut_interpolation-r00.drawio` | G3 | 越界原因、插值误差和 fallback 有测试 | `indexed` |
| BOM/EDA | 位置/温度/电流传感器精度与采样链 BOM | `V2-S04-BOM-lut_sensor_chain-r00.xlsx` | G4 | 传感器误差进入 LUT 误差预算 | `missing` |
| Test | FEA 回灌、台架反标定、LUT 误差报告 | `V2-S04-TEST-flux_lut_correlation-r00.md` | G5 | FEA/实测与控制 LUT 误差闭合 | `missing` |

### 4.5 S05 磁路饱和协同设计（`magnetic_saturation_codesign`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 不新增控制器主拓扑；需传感器与热保护接口页 | `V2-S05-PCB-saturation_sensor_inputs-r00.pdf` | G4 | 饱和相关观测输入可进入控制器 | `missing` |
| 3D/CAD | barrier、bridge、磁桥、转子应力、定转子叠片 CAD | `V2-S05-CAD-rotor_barrier_bridge-r00.step` | G3 | 结构应力、退磁、铁耗和制造约束同版评审 | `missing` |
| Controller | 饱和 LUT 回灌、候选几何 scorecard、控制轨迹对比图 | `V2-S05-CTRL-saturation_scorecard-r00.drawio` | G3 | FEA LUT 回灌后收益仍成立 | `indexed` |
| BOM/EDA | 硅钢、磁钢、转子工艺、传感器接口 BOM | `V2-S05-BOM-magnetic_stack-r00.xlsx` | G4 | 材料牌号、供应和制造风险字段完整 | `missing` |
| Test | FEA、转子应力、铁耗、退磁、NVH 组合 DVP&R | `V2-S05-DVP-saturation_codesign-r00.md` | G5 | 不能只用参数缩放晋级 | `missing` |

### 4.6 S06 PMaSynRM / 高凸极低永磁占比（`pmasynrm_high_saliency_low_pm`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 控制器采样、温度、位置、退磁保护接口页 | `V2-S06-PCB-pmasynrm_control_inputs-r00.pdf` | G4 | 支持高凸极控制和退磁诊断 | `missing` |
| 3D/CAD | PM fraction、rotor barrier、bridge、stress relief、扁线槽型 CAD | `V2-S06-CAD-pmasynrm_rotor_stator-r00.step` | G3 | 峰值转矩、ripple、stress、demag 同步评审 | `missing` |
| Controller | 高凸极 MTPA/MTPV 控制图、低 PM 退磁边界图 | `V2-S06-CTRL-saliency_control_map-r00.drawio` | G3 | 主工况效率和峰值转矩不被牺牲 | `indexed` |
| BOM/EDA | 低 PM 磁钢、叠片、扁线、冷却传感 BOM | `V2-S06-BOM-low_pm_topology-r00.xlsx` | G4 | 成本收益与供应风险可量化 | `missing` |
| Test | FEA torque ripple、应力、退磁、热、NVH DVP&R | `V2-S06-DVP-pmasynrm_validation-r00.md` | G5 | scorecard 超过基线且风险可控 | `missing` |

### 4.7 S07 可变磁化状态 / Memory Motor（`variable_magnetization_memory_motor`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 磁化脉冲驱动、储能、电流检测、隔离、互锁、失效关断页 | `V2-S07-PCB-magnetization_pulse_driver-r00.pdf` | G4 | 脉冲能量、电压、电流和互锁路径可审计 | `missing` |
| 3D/CAD | 记忆磁体、磁化线圈/路径、转子磁路、热路径 CAD | `V2-S07-CAD-memory_motor_magnetic_path-r00.step` | G3 | 磁状态保持、热、机械强度和装配空间成立 | `missing` |
| Controller | 磁状态机、状态观测、未知状态回退、重复切换寿命计数 | `V2-S07-CTRL-flux_state_machine-r00.drawio` | G3 | 不能用 `psi_f` 缩放代替真实磁状态 | `indexed` |
| BOM/EDA | 脉冲功率级、储能器件、磁体材料、观测传感 BOM | `V2-S07-BOM-memory_motor_pulse_chain-r00.xlsx` | G4 | 脉冲器件 SOA、寿命和安全失效字段完整 | `missing` |
| Test | 磁化/去磁脉冲、状态保持、温漂、未知状态回退 DVP&R | `V2-S07-DVP-magnetization_state-r00.md` | G5 | 证明状态可控、可观测、可回退 | `missing` |

### 4.8 S08 混合励磁（`hybrid_excitation`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 励磁 DC/DC、field current sensing、loss-of-field、隔离和保护页 | `V2-S08-PCB-field_excitation_converter-r00.pdf` | G4 | 励磁功率级和主逆变器故障隔离明确 | `missing` |
| 3D/CAD | 励磁绕组、滑环/无刷励磁、冷却、绝缘和封装 CAD | `V2-S08-CAD-field_winding_package-r00.step` | G3 | 励磁热、绝缘、装配和维修边界可评审 | `missing` |
| Controller | `id/iq/if` 三变量控制图、loss-of-field fallback | `V2-S08-CTRL-three_variable_control-r00.drawio` | G3 | 励磁损耗和故障进入可行性判断 | `indexed` |
| BOM/EDA | 励磁功率器件、绕组、绝缘、连接器、传感器 BOM | `V2-S08-BOM-field_excitation_hardware-r00.xlsx` | G4 | field converter 损耗和热边界可追溯 | `missing` |
| Test | 励磁热、loss-of-field、三变量优化、台架 DVP&R | `V2-S08-DVP-hybrid_excitation-r00.md` | G5 | 不能只看 `psi_eff = psi_pm + kf*if` | `missing` |

### 4.9 S09 绕组重构（`winding_reconfiguration`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 高压接触器/固态开关、互锁、arc suppression、状态反馈页 | `V2-S09-PCB-winding_switch_matrix-r00.pdf` | G4 | 非法状态、开短路、粘连和互锁路径明确 | `missing` |
| 3D/CAD | 绕组端部、重构开关布置、绝缘、热路径和线束 CAD | `V2-S09-CAD-reconfigurable_winding_layout-r00.step` | G3 | 端部空间、绝缘距离、热和维修可达性成立 | `missing` |
| Controller | 切换状态机、零转矩窗口、非法状态回退、环流检测 | `V2-S09-CTRL-winding_reconfig_state_machine-r00.drawio` | G3 | 不能只用静态 Ke/Kt 缩放 | `indexed` |
| BOM/EDA | 开关、驱动、互锁、线束、绝缘件 BOM | `V2-S09-BOM-switching_winding-r00.xlsx` | G4 | 额定电压/电流、寿命、故障模式字段完整 | `missing` |
| Test | 切换瞬态、环流、arc、open/short/stuck fault DVP&R | `V2-S09-DVP-switching_transient-r00.md` | G5 | 切换不引入不可控扭矩或电弧风险 | `missing` |

### 4.10 S10 多相 / 相组控制（`multiphase_phase_group_control`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 多相逆变器、相组电流采样、隔离、故障切除、连接器页 | `V2-S10-PCB-multiphase_inverter-r00.pdf` | G4 | 单相/相组故障隔离和诊断路径明确 | `missing` |
| 3D/CAD | 多相端子、线束、相组布置、热路径、封装 CAD | `V2-S10-CAD-phase_group_packaging-r00.step` | G3 | 线束、热、维修和相间绝缘可评审 | `missing` |
| Controller | fault torque allocator、谐波子空间、相组降额状态机 | `V2-S10-CTRL-fault_torque_allocator-r00.drawio` | G3 | 不能只用可用电流降额代理 | `indexed` |
| BOM/EDA | 多相功率模块、采样链、连接器、线束 BOM | `V2-S10-BOM-multiphase_powertrain-r00.xlsx` | G4 | 资源预算和容错需求有系统级依据 | `missing` |
| Test | 单相故障、相组故障、谐波、热、NVH DVP&R | `V2-S10-DVP-multiphase_fault_tolerance-r00.md` | G5 | 容错收益大于硬件复杂度和损耗 | `missing` |

### 4.11 S11 温度 / 退磁 / 安全保护（`thermal_demag_safety_protection`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 磁钢/油温/绕组温度采样、gate-disable、fault latch、ASIL 诊断页 | `V2-S11-PCB-safety_fault_latch-r00.pdf` | G4 | 故障检测、锁存、关断链路和诊断覆盖明确 | `indexed` |
| 3D/CAD | 温度传感器安装、油路、磁钢热路径、控制器散热 CAD | `V2-S11-CAD-thermal_sensor_cooling-r00.step` | G3 | 传感位置与热模型可对应 | `missing` |
| Controller | fault state machine、derating、unknown sensor fallback、gate-disable 映射 | `V2-S11-CTRL-safety_fault_state_machine-r00.drawio` | G3 | 所有方案进入硬件门前必须复用 | `indexed` |
| BOM/EDA | 传感器、隔离、诊断、关断、锁存器件 BOM | `V2-S11-BOM-safety_chain-r00.xlsx` | G4 | ASIL/诊断覆盖、温漂和失效模式字段完整 | `missing` |
| Test | 高温、退磁、传感器开短路、gate-disable fault injection DVP&R | `V2-S11-DVP-safety_fault_injection-r00.md` | G5 | 不能证明故障安全则禁止进硬件门 | `missing` |

### 4.12 S12 工况加权效率 / Pareto 选择（`weighted_efficiency_pareto_selection`）

| 类别 | 必需交付物 | 命名模板 | Gate | 验收条件 | 当前状态 |
|---|---|---|---|---|---|
| PCB | 不新增硬件；必须索引候选方案 PCB/BOM/EDA 版本 | `V2-S12-PCB-candidate_index-r00.md` | G4 | Pareto 输入引用真实硬件版本 | `indexed` |
| 3D/CAD | 候选拓扑 CAD 版本索引、质量、封装、冷却边界 | `V2-S12-CAD-candidate_package_index-r00.md` | G3 | 每个候选有可比较 CAD/质量/尺寸来源 | `indexed` |
| Controller | 决策 scorecard、drive cycle、系统损耗、成熟度权重图 | `V2-S12-CTRL-pareto_scorecard-r00.drawio` | G3 | 区分 research rank 与 engineering recommendation | `indexed` |
| BOM/EDA | 候选 BOM 成本、制造风险、供应风险、控制器差异索引 | `V2-S12-BOM-pareto_cost_risk-r00.xlsx` | G4 | 权重扰动下结论稳定 | `missing` |
| Test | drive cycle、系统损耗、敏感性分析、证据路径审计 | `V2-S12-DVP-pareto_traceability-r00.md` | G5 | 没有图纸/BOM/测试证据的候选不得推荐 | `missing` |

---

## 5. Gate 验收规则

| Gate | 图纸/交付物最低要求 | 禁止通过条件 |
|---|---|---|
| G0 | 方案 ID、目标、边界、禁止误判项 | 没有方案边界或把研究池写成量产候选 |
| G1 | 输入模型、接口、风险清单、占位图纸目录 | 没有图纸目录和文件命名规则 |
| G2 | PCB/CAD/CTRL 三类草图至少 `stub`，BOM 初表 | 只存在仿真图或文字描述 |
| G3 | FEA/CAD/控制器图进入 `draft`，关键接口闭合 | 参数缩放未回灌 FEA/CAD/控制器约束 |
| G4 | PCB 原理图、BOM/EDA、控制器状态机评审 | 没有 ERC/DRC、BOM、fault path 或诊断说明 |
| G5 | 样机制造包、HIL/bench DVP&R、DFMEA 初版 | 无台架/故障注入计划 |
| G6 | released 制造包、DVP&R 执行记录、变更控制 | 证据路径不完整或版本不可追溯 |
| G7 | PV/PPAP、量产变更控制、供应链冻结 | numeric simulation 替代 PV/PPAP |

---

## 6. 当前 V2 图纸缺口总览

| 方案组 | 当前主要缺口 | 下一步最小动作 |
|---|---|---|
| P0 主线控制与安全 | 控制器图已有草案思路，但 PCB/传感/故障锁存和 CAD 安装图未落地 | 先补 S01/S02/S04/S11 的 `CTRL` 图和 `PCB sensing/fault` 页级草案 |
| P1 候选拓扑 | FEA/CAD 几何、BOM、NVH/热/制造风险证据缺失 | 先补 S03/S05/S06/S12 的 CAD/FEA/BOM scorecard 模板 |
| P2 研究池 | 关键硬件拓扑和安全互锁图纸几乎全缺 | 先补 S07/S08/S09/S10 的禁止误判图、互锁/故障路径和停止条件 |

---

## 7. 维护规则

1. 新增任何 PCB、CAD、控制器图、BOM/EDA 或 DVP&R 文件，必须回填本矩阵的 `当前状态`。
2. 方案进入下一 gate 前，至少要有对应 gate 所需的图纸包路径和版本号。
3. HTML、Wiki 和 `claude-docs/snapshots/` 必须与本 Markdown 源同步。
4. 图纸文件本体若未进入仓库，也必须记录外部系统路径、版本号、责任人和审计状态。
5. 本矩阵只定义交付物和验收标准，不替代真实 EDA、CAD、FEA、台架或量产发布文件。

---

## 8. 最终判断

V2 后续深度推进的判断标准从“有没有方案说明”升级为“有没有可审计图纸包”：

> 每个方案必须能同时回答 PCB 在哪里、3D/CAD 在哪里、控制器状态机在哪里、BOM/EDA 在哪里、DVP&R/DFMEA 如何验证；否则只能保留为研究项，不能宣称工程落地。
