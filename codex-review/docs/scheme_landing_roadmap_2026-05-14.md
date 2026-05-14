# 12 个可控磁通量方案深度落地路线图

评审日期：2026-05-14  
落地包：`codex-review/docs`  
对照事实源：`models/scheme_simulation_coverage.json`、`models/scheme_engineering_catalog.json`、`models/scheme_bom_eda_catalog.json`、`models/scheme_industry_stage_gate_process.json`、`experiments/exp_*/summary.json`、`tests/`

## 1. 总体判断

当前项目已经从“概念路线枚举”推进到“12 个方案均有可追踪数值代理或工程目录”的状态。下一步不能简单继续扩展新实验编号，而应把各方案按工程成熟度拆成可落地工作包：

```text
L0 事实源修复与证据一致性
  ↓
L1 控制主线闭环：弱磁 + MTPA/FW/MTPV + 安全保护
  ↓
L2 非线性磁链与 FEA 数据回灌
  ↓
L3 增强路线：过调制、PMaSynRM/磁饱和、加权 Pareto
  ↓
L4 高风险真实可变磁链路线：memory motor / hybrid excitation / winding reconfiguration / multiphase
  ↓
L5 低压台架、HIL、热/EMC/绝缘/功能安全验证
```

当前所有 `passed_numeric_simulation` 仍只代表可复现代理数值实验，不代表电磁、热、机械、EMC、安规或车规释放。

## 2. 横向落地原则

### 2.1 不允许跳过的共同门槛

| 门槛 | 要求 | 适用范围 |
|---|---|---|
| 证据闭环 | coverage、summary、CSV、测试、manifest、wiki/HTML 状态一致 | 所有方案 |
| 限制声明 | `engineering_validated=false` 或同等限制口径必须保留 | 所有代理模型 |
| 安全优先 | `id_min(T)`、`Imax(T)`、Vdc 上下限、温度降额优先于效率优化 | 所有控制与硬件路线 |
| 坐标约定 | dq 方向、峰值/RMS、电压限幅、温度维度、LUT 边界必须显式版本化 | 控制、FEA、台架数据 |
| 不可行区标记 | LUT 和控制表必须标记不可行区，不能 silent extrapolation | MTPA/FW/MTPV、LUT、Pareto |
| 阶段门 | 必须经过 G0 到 G3 才能进入硬件设计，经过 G4/G5 才能低压样机 | 所有硬件相关路线 |

### 2.2 当前首要工程断点

| 断点 | 影响 | 处置 |
|---|---|---|
| coverage 引用不存在的 `tests/test_control_search.py` | 测试证据链不完整 | 替换为真实测试或新增测试，并增强路径存在性校验 |
| `claude-docs` / wiki / HTML 滞后 | 接手者误判当前状态 | 按 `documentation_sync_matrix_2026-05-14.md` 同步 |
| EXP-006 未接入已提交共享搜索 | 非线性 LUT 还不能生成电压约束控制轨迹 | 先完成 search API 的 `flux_lut` 支持与 runner |
| 工程目录 deliverables 混合现有/未来路径 | 自动审计困难 | 拆分 `existing_artifacts` 和 `planned_deliverables` |
| `.claude/` 未跟踪 | 工作树污染风险 | 忽略或抽取必要长期文件 |

## 3. 推荐推进顺序

| 顺序 | 工作线 | 包含方案 | 目标 |
|---|---|---|---|
| P0 | 证据与门禁修复 | 全部 | 修复覆盖路径、manifest、docs/wiki/HTML 漂移，建立自动一致性检查 |
| P1 | 控制 + 安全主线 | `negative_d_axis_field_weakening`, `mtpa_fw_mtpv_control`, `thermal_demag_safety_protection` | 形成可生成控制 LUT 的安全闭环 |
| P2 | 非线性磁链数据层 | `nonlinear_flux_lut`, `magnetic_saturation_codesign`, `pmasynrm_high_saliency_low_pm` | 从缩放代理升级到 FEA/测量 LUT 回灌 |
| P3 | 系统收益量化 | `svpwm_overmodulation_voltage_utilization`, `weighted_efficiency_pareto_selection` | 用真实损耗和工况权重决定哪些路线值得硬件化 |
| P4 | 高风险硬件预研 | `variable_magnetization_memory_motor`, `hybrid_excitation`, `winding_reconfiguration`, `multiphase_phase_group_control` | 只在 scorecard 明确胜出时进入硬件 trade study |

## 4. 方案级落地路线

### 4.1 `negative_d_axis_field_weakening`：负 d 轴弱磁

**当前证据**

- `experiments/exp_001_linear_dq/summary.json`
- `experiments/exp_001_linear_dq/scan_results.csv`
- `tests/test_dq_model.py`
- `tests/test_param_sweep.py`
- `models/scheme_simulation_coverage.json`

**当前定位**

这是短期主线的基础能力：通过负 `id` 降低合成 d 轴磁链和端电压需求，但不改变永磁体本身 `psi_f/Ke`。

**主要缺口**

- 退磁约束仍没有作为 `sim/search.py` 候选过滤器的一等约束；
- `id_min(T)` 仍是简化逻辑，尚未来自磁钢数据或 FEA；
- 低 Vdc、高温和目标转矩组合还未形成统一安全 LUT。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| FW-01 退磁约束注入 | `id_min(T)` schema 和 search candidate filter | 任何搜索结果都满足 `id >= id_min(T)` |
| FW-02 低压高温扫描 | Vdc/T/target torque 三维边界表 | 高温低压不可行区显式标记 |
| FW-03 弱磁启用门槛 | 弱磁 enable/disable 策略 | 不满足温度/电压/电流安全时禁止进入弱磁 |

**阶段门**

进入低压台架前，必须证明热态 `id_min(T)`、Vdc_min 和目标转矩边界全部正裕度；否则只能保留为仿真路线。

### 4.2 `mtpa_fw_mtpv_control`：MTPA/FW/MTPV 连续控制

**当前证据**

- `experiments/exp_001_linear_dq/summary.json`
- `experiments/exp_001_linear_dq/scan_results.csv`
- `sim/search.py`
- coverage 当前引用的 `tests/test_control_search.py` 不存在，需要修复

**当前定位**

这是控制轨迹主线，目标是把低速 MTPA、过渡弱磁和高速 MTPV 串成连续、可标定、可降额的 LUT。

**主要缺口**

- 当前 EXP-001 输出是扫描结果，不是正式控制 LUT；
- mode transition 连续性、不可行区标记和 LUT CRC/版本尚未落地；
- coverage 测试路径存在断点。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| CTRL-01 coverage 修复 | 替换/新增真实测试路径 | `pytest_tests` 全部存在且 CI 可发现 |
| CTRL-02 控制 LUT schema | `models/control_lut_schema.json` | 速度/转矩/Vdc/T 坐标、不可行区、模式标记完整 |
| CTRL-03 LUT 生成 runner | `sim/run_control_lut_experiment.py` | 可从参数文件重跑生成 LUT 和 summary |
| CTRL-04 连续性检查 | `reports/control_trajectory_continuity.md` | `id/iq/torque` 跳变低于标定阈值 |

**阶段门**

只有当 LUT 生成、不可行区标记、mode transition 连续性和安全限制都通过测试后，才可进入 HIL 或低压台架标定。

### 4.3 `svpwm_overmodulation_voltage_utilization`：SVPWM / 过调制电压利用

**当前证据**

- `experiments/exp_005_modulation_factor/summary.json`
- `experiments/exp_005_modulation_factor/modulation_sweep_results.csv`
- `tests/test_modulation.py`
- `tests/test_modulation_factor_experiment.py`

**当前定位**

该方案是逆变器电压利用增强线，目标是在同等 DC bus 下提高可用基波电压，降低弱磁压力。

**主要缺口**

- 当前谐波、电流纹波、逆变器损耗和转矩脉动是参数化代理；
- 尚无 PWM 波形重建、器件 loss map、死区、EMI/NVH 约束；
- 未形成过调制 enable gate。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| MOD-01 过调制限制表 | `models/modulation_strategy_limits.json` | 每个 `k_mod` 有速度/转矩/Vdc 启用边界 |
| MOD-02 PWM 重建代理 | PWM 电压矢量/THD 估计脚本 | THD、谐波电流和转矩纹波可追溯 |
| MOD-03 逆变器损耗接口 | loss map schema | 器件损耗可替代当前参数惩罚 |
| MOD-04 enable gate | 过调制启用策略 | 超过 THD/NVH/损耗阈值自动降回线性区 |

**阶段门**

只有证明加权效率净收益大于 THD/NVH/损耗惩罚，才可进入控制实现；否则只能作为高转速极限策略保留。

### 4.4 `nonlinear_flux_lut`：非线性磁链表

**当前证据**

- `models/flux_lut_schema.json`
- `models/flux_lut_sample.json`
- `sim/nonlinear_flux_lut.py`
- `sim/run_nonlinear_flux_lut_search_experiment.py`
- `experiments/exp_006_nonlinear_flux_lut/summary.json`
- `experiments/exp_006_nonlinear_flux_lut/nonlinear_flux_lut_results.csv`
- `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json`
- `experiments/exp_006_nonlinear_flux_lut/lut_search_scan_results.csv`
- `tests/test_nonlinear_flux_lut.py`
- `tests/test_nonlinear_flux_lut_search.py`

**当前定位**

这是从线性 dq 代理迈向 FEA/测量数据闭环的核心数据层。当前已证明 synthetic LUT schema、边界检查、插值、非线性转矩计算，并在工作树中通过 phase-2 runner 接入电压/电流约束搜索。

**主要缺口**

- LUT 不是 FEA 或测量来源；
- phase-2 仍是 synthetic LUT 搜索证明，不是共享控制 LUT 交付；
- 未引入温度维度、损耗和退磁边界；
- targeted pytest 已通过，但仍需与 manifest、wiki/HTML、snapshots 和提交拆分同步。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| LUT-01 search API 扩展 | `sim/search.py` 支持可选 `flux_lut` | 已在工作树形成，targeted pytest 通过；提交前需复核全量测试 |
| LUT-02 LUT search runner | `sim/run_nonlinear_flux_lut_search_experiment.py` | 已输出 `lut_search_summary.json` 和 CSV，header 与 EXP-001 对齐 |
| LUT-03 FEA import contract | FEA/测量 LUT 导入约定 | dq 方向、单位、峰值/RMS、温度、边界全部声明 |
| LUT-04 控制 LUT 回灌 | 基于 LUT 的 MTPA/FW/MTPV 候选表 | 不可行区和 out-of-bound 行为可测试 |

**阶段门**

只有当 FEA/测量 LUT 能稳定回灌控制搜索，并导出共享 MTPA/FW/MTPV 控制 LUT，且线性基线回归不被破坏，才可把该路线升级为控制主线输入。

### 4.5 `magnetic_saturation_codesign`：磁路饱和协同设计

**当前证据**

- `experiments/exp_003_param_sweep/summary.json`
- `experiments/exp_003_param_sweep/param_sweep_results.csv`
- `tests/test_param_sweep.py`
- `models/scheme_engineering_catalog.json`

**当前定位**

当前只是通过缩放 `Ld/Lq/psi_f` 代理高凸极和磁饱和协同，不是真实几何推荐。

**主要缺口**

- 缺候选转子几何变量；
- 缺 FEA `lambda_d/lambda_q` 候选图；
- 缺转矩脉动、铁耗、转子强度和退磁评分；
- 缺 candidate scorecard。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| EM-01 候选几何矩阵 | `em_design/candidates/candidate_matrix.md` | 每个变量有范围、单位、约束 |
| EM-02 FEA LUT 协议 | `models/flux_lut_candidate_*.json` schema | 可导入 `nonlinear_flux_lut` 路径 |
| EM-03 候选 scorecard | `reports/em_codesign_review.md` | 同时评分转矩、速度、铁耗、退磁、强度、NVH 风险 |
| EM-04 反向淘汰表 | stop criteria | 单点高速收益不能覆盖铁耗/强度/退磁风险时停止 |

**阶段门**

只有 FEA-derived LUT 回灌后仍优于线性基线和 EXP-003 代理候选，才进入详细电磁设计。

### 4.6 `pmasynrm_high_saliency_low_pm`：PMaSynRM / 高凸极低永磁

**当前证据**

- `experiments/exp_003_param_sweep/summary.json`
- `tests/test_param_sweep.py`
- `models/scheme_engineering_catalog.json`

**当前定位**

该路线尝试降低 PM 磁链和高速 Ke，同时依靠磁阻转矩和高凸极比补偿低速转矩。

**主要缺口**

- 当前只有 `psi_f/Ld/Lq` 缩放代理；
- 缺 PM fraction、barrier topology、转矩脉动、NVH 和转子强度约束；
- 缺低永磁候选与基线的真实 FEA 对比。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| PMAS-01 PM fraction 扫描 | PM 占比候选表 | 每个候选保留低速转矩能力 |
| PMAS-02 凸极/磁阻转矩拆分 | saliency scorecard | 磁阻转矩贡献可解释 |
| PMAS-03 转矩脉动筛选 | torque ripple / NVH 风险表 | 低 Ke 候选不能以过高 ripple 换取速度 |
| PMAS-04 FEA 回灌 | candidate LUT | 高速电压裕度和低速转矩同时优于门槛 |

**阶段门**

低速峰值转矩、高速电压裕度、转矩脉动、转子强度任一不达标，均不得升级为工程候选。

### 4.7 `variable_magnetization_memory_motor`：可变磁化状态 / Memory Motor

**当前证据**

- `experiments/exp_002_variable_flux/summary.json`
- `experiments/exp_002_variable_flux/variable_flux_scan.csv`
- `tests/test_variable_flux.py`

**当前定位**

当前只做虚拟 `psi_f` 档位扫描，结论是单纯降低 `psi_f` 会显著损失目标转矩能力，不能独立视为收益。

**主要缺口**

- 缺磁化/去磁脉冲能量模型；
- 缺状态观测、状态置信度和未知状态降额；
- 缺不可逆退磁、温漂和寿命路径；
- 缺脉冲对 DC-link、逆变器和磁钢的应力分析。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| MEM-01 状态置信度模型 | `models/psi_f_state_schema.json` | high/mid/low/unknown 状态和置信度定义完整 |
| MEM-02 状态转换能量 | pulse energy model | 脉冲电流、能量、温度限制可追踪 |
| MEM-03 unknown-state derating | 状态未知降额策略 | 任何未知状态不允许全扭矩输出 |
| MEM-04 stop/go business case | `reports/variable_magnetization_business_case.md` | 收益必须超过脉冲硬件、观测和退磁风险 |

**阶段门**

状态观测和脉冲安全路径不明确前，不进入硬件；即使进入硬件，也必须先低压和限能验证。

### 4.8 `hybrid_excitation`：混合励磁

**当前证据**

- `experiments/exp_007_hybrid_excitation/summary.json`
- `experiments/exp_007_hybrid_excitation/hybrid_excitation_results.csv`
- `tests/test_hybrid_excitation.py`
- `tests/test_hybrid_excitation_experiment.py`

**当前定位**

当前用等效 `psi_eff = psi_pm + kf * if` 和励磁铜耗比较边界收益，是稳态代理模型。

**主要缺口**

- 缺场绕组电感、电流环动态、励磁机/整流器损耗；
- 缺场绕组热路径和与主电机热耦合；
- 缺失励、过励、短路等故障模式；
- 缺 field converter BOM/EDA 细化。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| HYB-01 场电路动态 | `models/hybrid_excitation_params.json` | `Rf/Lf/If_limit/kf` 全部版本化 |
| HYB-02 三变量优化 | id/iq/if 搜索 runner | 总损耗 `Pcu + Pfield + Pinverter` 可比较 |
| HYB-03 场绕组热模型 | field thermal limit | if 命令受热限制约束 |
| HYB-04 失励故障 | loss-of-field derate | 失励时转矩和电压安全降额 |

**阶段门**

只有加权总损耗在多个工况下优于控制弱磁主线，并且场绕组热与故障安全可控，才继续进入硬件 trade study。

### 4.9 `winding_reconfiguration`：绕组重构

**当前证据**

- `experiments/exp_008_winding_reconfiguration/summary.json`
- `experiments/exp_008_winding_reconfiguration/winding_reconfiguration_results.csv`
- `tests/test_winding_reconfiguration.py`
- `tests/test_winding_reconfiguration_experiment.py`

**当前定位**

当前只用参数化 turns/resistance/current scale 比较串/并/基准配置，并做切换速度处的连续性代理。

**主要缺口**

- 缺高电流开关、接触器或半导体矩阵的暂态模型；
- 缺非法配置硬件互锁；
- 缺环流、绝缘、EMI、热分配和 stuck-switch 故障；
- 缺真实绕组布局与端部连接设计。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| WR-01 合法状态表 | `models/winding_configurations.json` | 所有合法/非法连接和默认安全态定义 |
| WR-02 切换暂态代理 | switching transient model | 切换电流、扭矩冲击和电压尖峰可估算 |
| WR-03 硬件互锁逻辑 | switch matrix interlock spec | 软件错误不能进入非法配置 |
| WR-04 收益/复杂度门槛 | switching business case | 加权收益覆盖开关损耗、成本、可靠性和 EMI 风险 |

**阶段门**

若收益只在窄工况出现，或硬件复杂度/EMI/绝缘风险过高，应停止在仿真阶段。

### 4.10 `multiphase_phase_group_control`：多相相组控制

**当前证据**

- `experiments/exp_009_multiphase_phase_group/summary.json`
- `experiments/exp_009_multiphase_phase_group/multiphase_phase_group_results.csv`
- `tests/test_multiphase_phase_group.py`
- `tests/test_multiphase_phase_group_experiment.py`

**当前定位**

当前用相组健康数和不均流参数做聚合电流降额，评估失组/limp-home 可达性。

**主要缺口**

- 缺谐波子空间解耦；
- 缺中性点偏移电压矢量；
- 缺每相/每组热 RC；
- 缺 MCU/FPGA PWM、ADC、gate-driver 资源预算；
- 缺产品层面对容错价值的明确需求。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| MPH-01 产品用例约束 | multiphase use-case brief | 必须说明为何需要多相而非三相冗余策略 |
| MPH-02 相组模型升级 | harmonic subspace model | 相组故障不只表现为电流降额 |
| MPH-03 资源预算 | MCU/FPGA + gate-driver budget | ADC/PWM/计算资源满足控制周期 |
| MPH-04 故障 DVP&R | phase-loss test plan | 单组失效、过热、不均流都有安全降额 |

**阶段门**

如果产品没有明确容错、热分配或谐波控制需求，该方案不应进入硬件设计。

### 4.11 `thermal_demag_safety_protection`：热、退磁和安全保护

**当前证据**

- `experiments/exp_004_safety_boundaries/summary.json`
- `experiments/exp_004_safety_boundaries/safety_boundary_results.csv`
- `tests/test_safety_limits.py`
- `tests/test_safety_boundary_experiment.py`
- `models/scheme_industry_stage_gate_process.json`

**当前定位**

这是所有路线的横向安全层，不是可选增强功能。任何效率或高速收益都不能覆盖安全边界。

**主要缺口**

- `id_min(T)` 仍是简化退磁线；
- 缺 `id_min(T, fault)`、`Imax(T)`、磁钢温度估计和短路边界；
- 缺硬件 gate-disable、watchdog、fault latch 设计验证；
- 缺 fault injection 测试计划。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| SAFE-01 限制层级 | safety limit hierarchy | 安全限制优先级高于 torque/efficiency optimizer |
| SAFE-02 退磁数据替换 | `models/thermal_demag_limits.json` | 磁钢/FEA/台架来源可追溯 |
| SAFE-03 fault injection | DVP&R fault cases | 温度传感器故障、Vdc 异常、过流、弱磁过深均可降额 |
| SAFE-04 硬件关断链 | gate-disable verification | 软件失效时硬件仍能切断危险命令 |

**阶段门**

没有 SAFE 层，任何方案都不得进入高压高速台架；低压台架也必须限制能量、速度和电流。

### 4.12 `weighted_efficiency_pareto_selection`：工况加权效率和 Pareto 选择

**当前证据**

- `experiments/exp_010_weighted_efficiency_pareto/summary.json`
- `experiments/exp_010_weighted_efficiency_pareto/weighted_efficiency_pareto_results.csv`
- `tests/test_drive_cycle.py`
- `tests/test_weighted_efficiency_pareto_experiment.py`

**当前定位**

这是路线升级的决策层，用于防止单点高速指标绑架整体工程选择。

**主要缺口**

- 当前 drive cycle 是说明性，不是实测；
- 当前只计铜耗，缺铁耗、机械损耗、逆变器损耗；
- 缺风险、复杂度、BOM、成熟度和安全成本的统一评分；
- 缺 sensitivity scan。

**下一步落地包**

| 工作包 | 输出 | 验收 |
|---|---|---|
| PAR-01 scorecard schema | `models/route_scorecard_schema.json` | 效率、风险、成本、成熟度、证据等级字段完整 |
| PAR-02 损耗扩展 | copper + iron + inverter + mechanical loss model | 不再只按铜耗排序 |
| PAR-03 工况替换 | measured/representative drive cycle | 权重来源可追溯 |
| PAR-04 升级评审会 | promotion review checklist | 每条路线升级必须通过 scorecard |

**阶段门**

没有 Pareto scorecard，不允许把任何高风险路线推进到硬件；有 scorecard 但敏感性不稳定，也只能继续仿真。

## 5. 三个月内建议里程碑

| 周期 | 目标 | 产物 |
|---|---|---|
| Week 1 | 修复证据链和文档漂移 | coverage 测试路径修复、manifest/wiki/HTML 同步、`.claude/` 处置 |
| Week 2 | 控制 LUT 与安全候选过滤 | `control_lut_schema.json`、`id_min(T)` filter、LUT 连续性测试 |
| Week 3 | EXP-006 LUT 接入共享搜索 | `flux_lut` search API、LUT search runner、线性基线回归 |
| Week 4 | 过调制与 Pareto 升级 | modulation limits、loss map schema、scorecard schema |
| Month 2 | FEA 数据契约与候选几何 | FEA import contract、candidate matrix、PM fraction/saliency sweep plan |
| Month 3 | 硬件预研路线 go/no-go | memory/hybrid/winding/multiphase business case 和 stop criteria |

## 6. 当前不建议立即做的事

- 不建议直接进入高压高速台架；
- 不建议把 EXP-010 当前 Pareto 排名写成设计定案；
- 不建议把 EXP-006 phase-2 synthetic LUT 搜索证明直接宣称为 FEA/实测驱动的非线性控制 LUT 工程闭环；
- 不建议把 memory motor、混合励磁、绕组重构、多相控制直接投硬件；
- 不建议继续新增大量实验编号而不修复 manifest、wiki、HTML 和 coverage 测试断点。

## 7. 下一步最小可执行清单

1. 已修复 `models/scheme_simulation_coverage.json` 中不存在的 `tests/test_control_search.py` 引用。
2. 已给 `tests/test_scheme_simulation_coverage.py` 增加 `pytest_tests` 路径存在性检查。
3. 更新 `claude-docs/evidence_manifest.md`，纳入 EXP-005 到 EXP-010 和 EXP-006 LUT 证据。
4. 将 EXP-006 LUT search 的 runner/API/测试/产物作为独立提交，并同步文档入口。
5. 建立 `models/control_lut_schema.json` 与 `models/route_scorecard_schema.json`。
6. 把 wiki/HTML 实验矩阵同步到 EXP-001 到 EXP-010。
