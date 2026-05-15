# V2 PRD：review-pr 外部资料逐条工程落地差距对齐

日期：2026-05-15  
输入资料：

- `review-pr/这是奇瑞公司的可变磁通电机，技术思路非常巧妙.html`
- `review-pr/新能源汽车驱动电机系列（）——驱动电机发展趋势（扁线、油冷、多合一）.html`

目标：把 `review-pr` 中的外部行业资料转成当前仓库可执行的 V2 工程需求，明确哪些内容能进入主线，哪些只能进入候选或研究池，以及与当前 `v0.3` 主干收敛任务的真实差距。

---

## 1. V2 总判断

两篇资料分别指向两类落地差距：

1. **可变磁通 / 电磁调磁差距**  
   当前仓库已有 `variable_magnetization_memory_motor` 和 `hybrid_excitation` 的参数化实验，但还没有把“真实可变磁通电机”的磁状态、磁化脉冲、状态观测、退磁安全和故障回退建成工程闭环。
2. **扁线 / 油冷 / 多合一系统工程差距**  
   当前仓库已有控制、磁链 LUT、安全边界、BOM/EDA 目录雏形，但对量产电驱系统的扁线制造、油冷热管理、多合一集成、台架验证和阶段门证据仍停留在目录级，尚未形成可执行 PRD。

因此 V2 的核心不是推翻 v0.3 主线，而是在 v0.3 之上补两层：

- 对控制主线补齐真实硬件约束：温度、油冷、母线、电流采样、故障关断、标定发布。
- 对研究池中的可变磁通路线补齐工程门槛：状态可控、状态可观测、切换可验证、故障可降级。

---

## 2. 外部资料逐条工程解读

### 2.1 奇瑞可变磁通电机资料

#### 2.1.1 资料主张

资料强调一种“电磁调磁”思路：通过电流脉冲改变记忆磁体或等效磁链状态，使电机在不同工况下拥有不同磁通水平。

工程上可以概括为：

- 低速 / 大转矩：保持较高磁链，提升转矩能力。
- 高速 / 弱磁区：降低等效磁链，降低反电势和电压压力。
- 相比机械调磁：减少机械移动机构、摩擦和高转速可靠性风险。
- 相比普通负 `id` 弱磁：它不是单纯用电流抵消磁链，而是改变磁体状态或等效磁链源。

#### 2.1.2 对当前仓库的真实差距

当前仓库已有：

- `experiments/exp_002_variable_flux/summary.json`
- `experiments/exp_007_hybrid_excitation/summary.json`
- `experiments/exp_010_weighted_efficiency_pareto/summary.json`
- `claude-review/docs/2026-05-15/research_scheme_engineering_landing_matrix.md`

但这些证据仍属于数值假设，不等同于真实可变磁通工程方案。

| 外部资料要点 | 当前仓库状态 | 差距判断 | V2 要求 |
|---|---|---|---|
| 通过脉冲改变磁链状态 | 仅有不同 `psi_f` 档位假设 | 缺磁化/去磁脉冲模型 | 新增磁化脉冲能量、电流、电压、持续时间、热影响需求 |
| 磁链状态可保持 | 无状态保持模型 | 缺保持时间、温漂、退磁漂移 | 定义状态保持验证指标和漂移边界 |
| 高速降反电势 | 已有弱磁和变量磁链数值实验 | 未区分负 `id` 弱磁与真实调磁 | 输出必须区分 `field_weakening_by_id` 与 `flux_state_change` |
| 无机械移动机构 | 无机械调磁对比 | 缺机械调磁 vs 电磁调磁 trade-off | 增加方案对比矩阵，避免误把调磁都归入同一类 |
| 控制复杂度更高 | 当前没有状态机 | 缺状态机、切换条件、禁止区 | 新增磁状态机 PRD 与故障回退需求 |
| 可靠性风险 | 当前仅有简化 demag limit | 缺脉冲越限、不可逆退磁、状态误判 | 安全边界扩展到磁状态失控与脉冲故障 |

#### 2.1.3 V2 对该路线的定位

`variable_magnetization_memory_motor` 不进入近期 v0.3 主线实现，但应从“纯参数化研究池”升级为“V2 研究池重点规范对象”。

原因：

- 它的工程价值可能真实存在，但不能用当前 `psi_f` 缩放实验证明。
- 它需要额外的材料、磁体、脉冲策略、热、退磁、状态观测证据。
- 如果过早进入主线，会稀释 v0.3 的弱磁 + 控制 LUT + 安全保护主干。

V2 判断：

- **近期主线**：普通负 `id` 弱磁、MTPA/FW/MTPV、非线性 LUT、安全保护。
- **重点研究池**：电磁调磁 / Memory Motor。
- **禁止误判**：不得把当前 `exp_002` 的不同 `psi_f` 档位结果表述为可变磁通电机工程可行性证明。

---

### 2.2 扁线、油冷、多合一趋势资料

#### 2.2.1 资料主张

资料强调新能源汽车驱动电机正在向三类工程方向收敛：

1. **扁线绕组**：提升槽满率、降低铜耗、提升功率密度。
2. **油冷**：直接冷却定子端部、绕组、转子或壳体，支撑高热流密度和高持续功率。
3. **多合一集成**：电机、控制器、减速器、冷却、壳体、线束和连接器集成，降低体积、重量和成本。

#### 2.2.2 对当前仓库的真实差距

当前仓库已有：

- `models/scheme_bom_eda_catalog.json`
- `models/scheme_industry_stage_gate_process.json`
- `experiments/exp_004_safety_boundaries/summary.json`
- `experiments/exp_011_iron_loss/summary.json`
- `models/control_lut_schema.json`

但仍明显偏控制和数值模型，硬件系统工程证据不足。

| 外部资料要点 | 当前仓库状态 | 差距判断 | V2 要求 |
|---|---|---|---|
| 扁线提升槽满率和效率 | 参数模型未包含绕组几何 | 缺绕组填充率、AC 铜耗、端部损耗 | 建立 winding geometry / copper loss / manufacturability 字段 |
| 油冷支撑高功率密度 | 仅有简化温度模型 | 缺油温、油量、喷油路径、转子甩油 | 建立 oil cooling thermal boundary 输入 |
| 转子磁钢温升影响退磁 | 有简化 demag limit | 缺磁钢温度估算和油冷耦合 | `id_min(T)` 必须升级为可溯源温度/材料边界 |
| 多合一共享壳体/冷却 | 只有 BOM/EDA 目录 | 缺页级架构与接口定义 | 输出 BOM/EDA 页级交付物和接口清单 |
| 高集成带来 EMC/NVH/热耦合 | 当前缺实证验证 | G4-G6 证据不足 | 阶段门加入 EMC/NVH/热台架/DVP&R 硬证据 |
| 高效率需要系统级损耗 | 有铜耗/铁耗雏形 | 缺逆变器、机械、油泵损耗 | Pareto 决策加入 system loss breakdown |

#### 2.2.3 V2 对该路线的定位

扁线、油冷、多合一不是单独的“控制算法路线”，而是所有候选电机从 G3 走向 G4/G5/G6 的硬件工程约束。

V2 判断：

- **扁线** 应进入候选电机 scorecard，而不是简单作为效率收益标签。
- **油冷** 应进入安全边界、热模型、台架计划和 BOM/EDA。
- **多合一** 应进入系统架构阶段门，约束连接器、壳体、冷却、EMC、NVH 和服务性。
- 当前仓库如果只继续扩展控制 LUT，而不补热管理和硬件集成证据，就无法对齐真实工程落地。

---

## 3. review-pr 条目化映射

### 3.1 资料 A：可变磁通 / 电磁调磁

| 条目 | 外部资料主张 | 当前工程状态 | V2 落地要求 | 阶段门定位 |
|---|---|---|---|---|
| A-1 | 通过电磁脉冲改变等效磁通，而不是机械移动机构 | 当前只有 `exp_002` 的静态 `psi_f` 档位 | 建立磁化/去磁脉冲模型，记录电流、电压、时间、能量 | G2 trade study |
| A-2 | 低速高磁链、高速低磁链，兼顾转矩与弱磁能力 | 当前弱磁主线与变量磁链实验彼此分离 | 明确区分负 `id` 弱磁与真实磁状态切换 | G3 模型验证 |
| A-3 | 记忆磁体状态需要保持与重复切换 | 当前无状态保持、漂移、寿命模型 | 增加状态保持时间、漂移、重复切换寿命指标 | G3-G6 |
| A-4 | 电磁调磁避免机械磨损，但提高控制和保护复杂度 | 当前无磁状态机和未知状态回退 | 定义状态机、禁止区、状态观测可信度、fallback state | G2-G4 |
| A-5 | 高速区收益依赖退磁边界和电压裕度 | 当前只有简化 demag limit 与线性电压约束 | 将磁状态、温度、Vdc、退磁风险统一进入 LUT 过滤 | G3 |
| A-6 | 工程价值取决于可控、可观测、可保护 | 当前只有数值假设，不足以证明工程可行 | 不允许将 `psi_f` 缩放实验作为量产可行性结论 | 全阶段约束 |

### 3.2 资料 B：扁线 / 油冷 / 多合一

| 条目 | 外部资料主张 | 当前工程状态 | V2 落地要求 | 阶段门定位 |
|---|---|---|---|---|
| B-1 | 扁线提升槽满率、效率和功率密度 | 当前电机参数未描述绕组几何 | 增加绕组类型、槽满率、导体截面、端部长度 | G2-G3 |
| B-2 | 扁线也带来 AC 铜耗、制造、绝缘和 NVH 风险 | 当前 Pareto 主要覆盖铜耗/铁耗雏形 | scorecard 加入 AC 铜耗、制造风险、NVH 风险 | G3-G4 |
| B-3 | 油冷支撑高热流密度和持续功率 | 当前只有简化温度模型 | 增加油温、流量、压力、喷油/甩油路径输入 | G3-G6 |
| B-4 | 磁钢温度和退磁风险必须受热管理约束 | 当前 `id_min(T)` 来源仍是简化假设 | demag curve 必须可追溯到材料、FEA 或台架数据 | G3-G4 |
| B-5 | 多合一集成降低体积重量，但耦合热、EMC、NVH、服务性 | 当前 BOM/EDA 只有目录级规划 | 输出页级 BOM/EDA、接口、接地、连接器和冷却约束 | G4 |
| B-6 | 量产放行依赖台架、DVP&R、DFMEA、PV 等硬证据 | 当前仓库主要是数值仿真 | 阶段门明确 numeric simulation 不能替代 G4-G7 证据 | G4-G7 |
| B-7 | 高效率应按系统级损耗评估 | 当前损耗模型尚未覆盖逆变器、机械、油泵、冷却惩罚 | Pareto 增加 system loss breakdown 和复杂度/成熟度评分 | G3-G6 |

---

## 4. V2 PRD 范围定义

### 4.1 V2 继续继承的 v0.3 主线

V2 不改变 v0.3 的近期工程主线：

1. `negative_d_axis_field_weakening`
2. `mtpa_fw_mtpv_control`
3. `nonlinear_flux_lut`
4. `thermal_demag_safety_protection`

这些仍是最现实的短期主线，因为它们能在不立即新增重硬件拓扑的情况下形成统一控制出口。

### 4.2 V2 新增的系统级需求层

V2 在上述主线之上新增 6 类需求：

1. **磁状态需求**：面向 Memory Motor / 电磁调磁。
2. **绕组与铜耗需求**：面向扁线、AC 铜耗、端部损耗。
3. **油冷热边界需求**：面向定子、转子、磁钢、油温、流量。
4. **多合一接口需求**：面向电机、逆变器、减速器、冷却、壳体集成。
5. **系统损耗需求**：面向铜耗、铁耗、逆变器、机械、油泵、热降额。
6. **阶段门证据需求**：面向 G3-G6 的仿真、FEA、台架、DVP&R、DFMEA。

---

## 5. 功能需求

### FR-1：磁状态机与电磁调磁研究接口

#### 需求描述

为可变磁通 / Memory Motor 路线定义统一磁状态机，使研究不再停留在静态 `psi_f` 档位，而能表达状态切换、保持、观测和故障。

#### 最小字段

- `flux_state_id`
- `effective_psi_f_wb`
- `magnetization_pulse_current_a`
- `magnetization_pulse_voltage_v`
- `pulse_duration_ms`
- `pulse_energy_j`
- `state_hold_time_s`
- `state_observer_confidence`
- `state_transition_allowed`
- `fallback_flux_state_id`
- `demag_irreversibility_risk`

#### 验收条件

- 能区分“负 `id` 弱磁”和“磁状态改变”。
- 每次状态切换都有能量、热、退磁风险记录。
- 未知状态时必须进入降额或禁止高速模式。

#### 阶段门

- G2：完成状态机和风险分析。
- G3：完成数值模型和故障场景仿真。
- G4 前：必须有磁体材料、脉冲硬件和保护链证据。

---

### FR-2：扁线绕组与铜耗工程输入

#### 需求描述

候选电机不再只用 `Ld/Lq/psi_f/Rs` 描述，还必须能表达绕组形态和制造约束。

#### 最小字段

- `winding_type`: `round_wire` / `hairpin_flat_wire` / `other`
- `slot_fill_factor`
- `conductor_cross_section_mm2`
- `end_winding_length_mm`
- `dc_resistance_ohm`
- `ac_resistance_model_ref`
- `skin_effect_assumption`
- `proximity_effect_assumption`
- `manufacturing_risk_level`

#### 验收条件

- 铜耗评估区分 DC 铜耗和 AC 铜耗。
- 扁线收益不能只用槽满率提升表述，必须同时记录端部、集肤、邻近效应风险。
- 候选 scorecard 能解释“效率收益”和“制造/NVH/成本风险”。

---

### FR-3：油冷与热-退磁边界输入

#### 需求描述

把当前简化 `Rs(T)`、`psi_f(T)`、`id_min(T)` 升级为可接收油冷边界的热保护需求。

#### 最小字段

- `cooling_type`: `water_jacket` / `stator_oil_spray` / `rotor_oil_cooling` / `integrated_oil_loop`
- `oil_inlet_temp_c`
- `oil_flow_lpm`
- `oil_pressure_kpa`
- `stator_winding_temp_c`
- `rotor_temp_c`
- `magnet_temp_c`
- `thermal_time_constant_s`
- `demag_curve_ref`
- `temperature_sensor_fault_policy`

#### 验收条件

- control LUT 生成时能引用热边界来源。
- 不可行原因能区分 `thermal_derating`、`demagnetization_risk`、`sensor_fault_derating`。
- 高速弱磁区必须同时检查电压裕度、磁钢温度和退磁边界。

---

### FR-4：多合一系统接口与 BOM/EDA 页级需求

#### 需求描述

把 `scheme_bom_eda_catalog.json` 从目录级提示升级到工程交付物约束。

#### 最小交付物

- inverter power stage page
- gate driver and protection page
- current / voltage / temperature sensing page
- resolver / position sensing page
- DC-link and discharge page
- oil pump / valve / pressure sensing page
- HV/LV connector page
- fault latch / gate-disable path
- enclosure grounding and EMC notes

#### 验收条件

- 每个主线方案都能映射到具体 BOM/EDA 页面。
- 安全保护方案必须拥有独立 fault path 描述。
- 多合一集成必须记录热、EMC、NVH、服务性和连接器约束。

---

### FR-5：系统损耗与 Pareto 决策升级

#### 需求描述

把当前 Pareto 决策从局部铜耗/铁耗扩展为系统损耗和工程风险联合评分。

#### 最小损耗项

- copper_loss_w
- iron_loss_w
- inverter_loss_w
- mechanical_loss_w
- oil_pump_loss_w
- cooling_penalty_w
- derating_penalty
- complexity_score
- maturity_score
- manufacturing_risk_score

#### 验收条件

- 排名能解释“为什么某路线进入主线、候选或研究池”。
- 重硬件路线必须证明加权收益覆盖新增复杂度。
- 高速效率收益不得脱离热、NVH、EMC、故障安全单独发布。

---

## 6. 非功能需求

### NFR-1：可追溯性

所有 V2 输出必须能追溯到：

- 输入模型版本；
- 参数来源；
- FEA / 台架 / 假设来源；
- 控制 LUT 生成器版本；
- 安全边界来源；
- 阶段门证据文件。

### NFR-2：工程成熟度标记

每个结果必须标记：

- `research_assumption`
- `numeric_simulation`
- `fea_supported`
- `bench_supported`
- `dv_supported`
- `production_released`

当前仓库结果默认不得越过 `numeric_simulation`，除非有明确外部证据文件。

### NFR-3：安全优先

任何控制收益必须被以下边界覆盖：

- 电流限制；
- 电压限制；
- 温度限制；
- 退磁限制；
- 传感器可信度；
- gate-disable / fault latch；
- 未知状态回退。

---

## 7. 与现有 v0.3 任务的对齐关系

| v0.3 任务 | V2 补充 | 原因 |
|---|---|---|
| T1 二维速度-转矩 LUT | 增加温度、Vdc、冷却状态、磁状态维度的扩展规划 | 真实量产 LUT 不只二维 |
| T2 不可行原因统一 | 增加 `thermal_derating`、`sensor_fault_derating`、`flux_state_unknown`、`magnetization_pulse_blocked` | 对齐可变磁通和油冷热管理 |
| T3 安全边界接入主干 | 安全边界来源从简化折线升级为材料/FEA/油冷/台架证据 | 避免把实验近似误认为工程边界 |
| T4 非线性磁链 LUT | 增加 FEA/实测/磁状态来源字段 | 支撑候选电机和可变磁通 |
| T5 模式切换连续性 | 增加磁状态切换冲击、热冲击、NVH 风险 | 对齐电磁调磁真实切换风险 |

---

## 8. 阶段门差距更新

### G0-G1：需求与安全概念

V2 必须补：

- 目标车型 / 工况 / 冷却架构；
- 是否采用扁线、油冷、多合一；
- 是否允许真实磁状态切换；
- 安全目标和故障回退策略。

### G2：系统架构与 trade study

V2 必须补：

- 机械调磁 vs 电磁调磁 vs 普通弱磁对比；
- 扁线 vs 圆线绕组工程对比；
- 水套冷却 vs 油冷 vs 集成油路对比；
- 多合一集成边界和接口矩阵。

### G3：模型、仿真与控制

V2 必须补：

- FEA / 实测到 `flux_lut_schema.json` 的转换；
- 油冷热边界输入；
- 系统损耗 breakdown；
- 磁状态机仿真；
- 控制 LUT 对温度、Vdc、磁状态、不可行原因的完整表达。

### G4：BOM / EDA / DFMEA

V2 必须补：

- 页级 BOM/EDA 交付物；
- oil pump / pressure / temp sensing；
- gate-disable / fault latch；
- DFMEA：退磁、油冷失效、传感器失效、磁状态误判、过调制风险。

### G5-G6：样机与台架验证

V2 必须补：

- 油冷覆盖率与温升台架；
- 扁线绕组热循环与绝缘验证；
- 高速弱磁与过调制 NVH/EMC；
- 可变磁通重复切换寿命；
- 未知磁状态和传感器故障注入。

---

## 9. V2 优先级

### P0：必须立即补入主线 PRD

1. 控制 LUT 输出中显式记录模型来源、安全边界来源和不可行原因。
2. 热/退磁边界从实验后处理进入主线控制生成。
3. 阶段门中明确“当前数值实验不能替代 G4-G6 硬件证据”。
4. 增加扁线、油冷、多合一作为 G2-G6 系统工程约束。

### P1：下一轮实现前置需求

1. FEA/实测到非线性磁链 LUT 的输入规范。
2. 候选电机 scorecard：绕组、冷却、损耗、热、制造、NVH、EMC。
3. 系统损耗 Pareto：铜耗、铁耗、逆变器、机械、油泵、冷却惩罚。
4. BOM/EDA 页级交付物清单。

### P2：研究池重点规范

1. Memory Motor / 电磁调磁状态机。
2. 磁化/去磁脉冲与热、退磁、安全保护。
3. 状态观测、状态保持、状态漂移、未知状态回退。
4. 机械调磁与电磁调磁 trade-off。

---

## 10. V2 不做什么

V2 不应立即做以下事情：

1. 不把 Memory Motor 直接纳入近期控制主线。
2. 不把扁线、油冷、多合一当成单独算法实验。
3. 不用当前参数化结果宣称可过 G4/G5。
4. 不绕过 FEA / 台架证据直接做量产判断。
5. 不继续增加孤立 runner 来证明单点收益。

---

## 11. 最终结论

`review-pr` 两篇资料对当前项目最大的价值，是提醒我们：真实工程落地不是“控制算法 + 参数扫描”就够了。

V2 PRD 的结论是：

1. **v0.3 主线仍然正确**：弱磁、连续控制、非线性 LUT、安全保护应该先收敛成统一控制出口。
2. **可变磁通必须重新定义为状态机工程问题**：当前 `psi_f` 缩放实验只能作为假设筛选，不能作为工程可行性证明。
3. **扁线、油冷、多合一必须进入阶段门**：它们决定真实电驱系统能否从 G3 数值仿真走向 G4-G6 硬件验证。
4. **下一阶段最关键差距是系统工程证据链**：FEA/实测 LUT、热边界、BOM/EDA、DFMEA、DVP&R、台架数据必须与控制 LUT 和 Pareto 决策打通。

因此，V2 的工程方向应是：

> 以 v0.3 控制主线为骨架，以扁线/油冷/多合一为硬件阶段门约束，以可变磁通状态机为研究池重点规范，把所有路线统一纳入可追溯、可验证、可放行的工程证据链。
