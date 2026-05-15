# 可控磁通研究方案工程落地深度梳理

日期：2026-05-15  
范围：当前 `claude-mainline` 已有实验、`models/scheme_*.json` 目录化方案、阶段门定义与覆盖登记  
目的：把“研究方案”收敛成“工程可落地路线”，明确每条路线的当前证据、缺口、集成点、验证路径和推进优先级。

---

## 1. 总体判断

当前仓库已经不是单点实验集合，而是具备了“方案目录 + 仿真覆盖 + 架构/BOM/EDA 规划 + 阶段门”的工程雏形。

但要真正工程落地，还需要把每条路线统一收敛到同一条主线：

1. **统一模型主线**：`sim/search.py`、`sim/run_*_experiment.py`、`models/*.json`。
2. **统一证据主线**：`experiments/*/summary.json`、CSV 结果、pytest、`scheme_simulation_coverage.json`。
3. **统一工程主线**：`scheme_engineering_catalog.json` 定义方案对象，`scheme_industry_stage_gate_process.json` 定义阶段门，`scheme_bom_eda_catalog.json` 定义硬件落点。
4. **统一决策主线**：不能只看单个实验数值，要回到加权效率、复杂度、风险、成熟度四维评价。

结论上，当前 12 条路线可以分成四类：

- **A 类：短期主线可工程化**  
  负 d 轴弱磁、MTPA/FW/MTPV 连续控制、非线性磁链 LUT、温度/退磁安全保护。
- **B 类：短期增强项，可作为主线附加能力**  
  SVPWM/过调制、电压利用率提升。
- **C 类：中期候选，需要 FEA/候选电机共设验证**  
  磁路饱和协同设计、PMaSynRM/高凸极低永磁占比。
- **D 类：长周期研究项，当前仅适合保持数值探索**  
  可变磁化状态、混合励磁、绕组重构、多相/相组控制。

---

## 2. 统一工程落地框架

每条路线都按以下五层落地：

1. **物理/控制机理层**：到底改变了什么量，改善了什么边界。
2. **数值模型层**：需要落在哪个 `sim/*.py` 或 `models/*.json`。
3. **控制集成层**：如何接入控制 LUT、限幅、模式切换、故障降级。
4. **硬件实现层**：是否只改标定/软件，还是需要新增 BOM/EDA。
5. **验证放行层**：对应哪个 stage gate，缺哪类证据才能往下走。

如果一条路线只在第 1 层或第 2 层成立，就还不是工程方案，只是研究假设。

---

## 3. 分方案工程落地矩阵

### 3.1 负 d 轴弱磁

- **方案 ID**：`negative_d_axis_field_weakening`
- **当前证据**：
  - `experiments/exp_001_linear_dq/summary.json`
  - `experiments/exp_004_safety_boundaries/summary.json`
  - `models/scheme_simulation_coverage.json`
- **当前结论**：
  - 在线性 dq 基线下，100 Nm 最小电流目标点可达 6750 rpm；
  - 加入简化温度/低母线/退磁边界后，最差样例掉到 5000 rpm；
  - 说明这条路线不是“有没有效果”的问题，而是“安全边界有多大”的问题。
- **工程落地点**：
  - 主搜索仍在 `sim/search.py`；
  - 安全过滤应并入候选过滤，而不是结果后处理；
  - 需要统一到控制 LUT 导出链路，而不是停留在单实验结论。
- **还缺什么**：
  - 实用化 `id_min(T)` 表，而不是当前简化折线；
  - `Vdc_min × 温度 × 转速` 联合边界扫描；
  - 与 `run_control_lut_generator.py` 的统一导出。
- **硬件影响**：
  - 不要求新增主功率拓扑；
  - 但要求更可靠的电流、Vdc、温度测量与 gate-disable 路径。
- **阶段门建议**：
  - 当前可推进到 `G3_model_simulation_and_controls`；
  - 进入 `G4/G5` 之前必须补齐 demag 边界和热边界。
- **落地判断**：**短期最现实，必须和安全保护路线绑定推进。**

### 3.2 MTPA / FW / MTPV 连续控制

- **方案 ID**：`mtpa_fw_mtpv_control`
- **当前证据**：
  - `models/control_lut_schema.json`
  - `models/control_lut.json`
  - `sim/run_control_lut_generator.py`
  - `experiments/exp_001_linear_dq/summary.json`
- **当前结论**：
  - 仓库已具备控制轨迹导出基础；
  - 但当前轨迹仍主要依赖线性基线，尚未和非线性 LUT、安全边界、Vdc 扰动闭环统一。
- **工程落地点**：
  - 这是整个项目的**控制主干路线**；
  - 未来其他多数方案都应回流成这条路线的输入：LUT、限幅、模式标签、不可行区标记。
- **还缺什么**：
  - 模式切换连续性验证报告；
  - 温度/低压联合 derating；
  - 非线性磁链 LUT 接入后重生成轨迹；
  - LUT CRC、版本号、不可行区标记策略。
- **硬件影响**：
  - 主要是 MCU/NVM/标定链路资源约束；
  - 相比磁路类方案，硬件变更最小。
- **阶段门建议**：
  - 应作为所有控制型路线的 `G3` 主线交付；
  - 通过后再进入 `G4` 的标定存储、诊断和量产接口设计。
- **落地判断**：**最核心主线，应优先成为所有实验的统一出口。**

### 3.3 SVPWM / 过调制 / 电压利用率提升

- **方案 ID**：`svpwm_overmodulation_voltage_utilization`
- **当前证据**：
  - `experiments/exp_005_modulation_factor/summary.json`
- **当前结论**：
  - 参数化模型下 `k_mod=1.04` 为当前最佳折中；
  - 目标点从 6750 rpm 提升到 7000 rpm，但收益不大，且代价来自谐波、电流纹波、损耗、NVH 风险。
- **工程落地点**：
  - 不应被视为独立主路线；
  - 更合理的定位是控制主线中的“高速区附加模式”。
- **还缺什么**：
  - PWM 重建或更真实的谐波/THD 评估；
  - 逆变器器件损耗图；
  - 允许启用区间和退出条件。
- **硬件影响**：
  - 对 gate driver、DC-link、电流采样带宽和 EMI 更敏感；
  - 需要 EDA 与功率回路布局同步评估。
- **阶段门建议**：
  - 在 `G3` 只能算参数化收益验证；
  - 进入 `G4` 之前必须给出 THD/NVH 测量计划。
- **落地判断**：**可做增强项，但不能替代主路线。**

### 3.4 非线性磁链 LUT

- **方案 ID**：`nonlinear_flux_lut`
- **当前证据**：
  - `models/flux_lut_schema.json`
  - `models/flux_lut_sample.json`
  - `experiments/exp_006_nonlinear_flux_lut/*`
  - `tests/test_nonlinear_flux_lut.py`
  - `tests/test_nonlinear_flux_lut_search.py`
- **当前结论**：
  - Schema、边界拒绝、双线性插值和搜索接入已打通；
  - 当前最大价值不是“算出更好结果”，而是把线性近似替换为可承接 FEA/实测数据的统一接口。
- **工程落地点**：
  - 这是从研究走向工程的**关键桥梁层**；
  - 未来 MTPA/FW/MTPV、铁耗、热、退磁都应建立在这个磁链数据层之上。
- **还缺什么**：
  - `run_control_lut_generator.py` 直接使用 LUT；
  - FEA 数据导入转换器；
  - 单位、坐标系、峰值/RMS 约定固化。
- **硬件影响**：
  - 主要落在标定存储、温度采样、诊断和调试接口；
  - 对功率硬件本身不强制新增器件，但对标定链路要求更高。
- **阶段门建议**：
  - 当前已具备 `G3` 的方法学基础；
  - 真正进入 `G4` 前要先完成 FEA/台架来源的 LUT 验证导入链。
- **落地判断**：**必须优先建设，是后续几乎所有高可信模型的共同底座。**

### 3.5 磁路饱和协同设计

- **方案 ID**：`magnetic_saturation_codesign`
- **当前证据**：
  - `experiments/exp_003_param_sweep/summary.json`
- **当前结论**：
  - 当前只是缩放 `Ld/Lq/psi_f` 的 clean-room 候选筛选；
  - 它能告诉我们“哪些参数区可能值得做 FEA”，但不能直接说明哪个转子方案可制造。
- **工程落地点**：
  - 不应直接往控制软件落；
  - 应走“候选电机几何 → FEA LUT → 非线性磁链接口 → 控制评分”这条链。
- **还缺什么**：
  - 候选几何参数化；
  - FEA 导出的 `lambda_d/lambda_q` 候选映射；
  - 强度、退磁、铁耗联合评分卡。
- **硬件影响**：
  - 主要是电机本体设计，不是控制板变更。
- **阶段门建议**：
  - 当前只到 `G2/G3` 前置研究；
  - 必须通过候选评分后才能进入硬件样机讨论。
- **落地判断**：**中期重点，但前提是建立 FEA→LUT→控制闭环。**

### 3.6 PMaSynRM / 高凸极低永磁占比

- **方案 ID**：`pmasynrm_high_saliency_low_pm`
- **当前证据**：
  - `experiments/exp_003_param_sweep/summary.json`
- **当前结论**：
  - 低 `psi_f` 只有和更高 saliency、甚至更高 Vdc/Imax 组合时才有竞争力；
  - 这意味着它不是单一“减磁钢”问题，而是整机系统协同问题。
- **工程落地点**：
  - 需要从 `exp_003` 的缩放参数，升级到“PM 占比、屏蔽桥、barrier 几何、转矩脉动”显式建模；
  - 最终仍要回流到 LUT 和控制轨迹生成。
- **还缺什么**：
  - PM fraction sweep；
  - torque ripple/NVH 筛选；
  - rotor stress screen；
  - 低速峰值转矩约束的几何级验证。
- **硬件影响**：
  - 核心在电机设计与 NVH/结构验证。
- **阶段门建议**：
  - 当前只适合作为 `G2` trade study 候选；
  - 在没有 FEA 和 ripple/stress 证据前，不应进入量产硬件讨论。
- **落地判断**：**有潜力，但当前仍然是“候选拓扑研究”，不是控制标定方案。**

### 3.7 可变磁化状态 / Memory Motor

- **方案 ID**：`variable_magnetization_memory_motor`
- **当前证据**：
  - `experiments/exp_002_variable_flux/summary.json`
- **当前结论**：
  - 纯数值上，降低 `psi_f` 并未天然带来主目标转矩优势；
  - 100 Nm 工况下，`psi_70pct` 和 `psi_55pct` 已不可达；
  - 它说明真实可变磁链路线必须解决低速能力缺口与状态切换收益阈值，不是只看高速降压。
- **工程落地点**：
  - 当前只能保留为“状态空间假设验证器”；
  - 还没有可直接落地到控制器的状态观测、脉冲策略和保护链。
- **还缺什么**：
  - 磁化/去磁脉冲能量模型；
  - 状态观测可信度；
  - 未知状态降额逻辑；
  - 状态切换时的转矩冲击和热影响。
- **硬件影响**：
  - 对逆变器脉冲能力、DC-link、温度和状态观测都提出新要求。
- **阶段门建议**：
  - 当前不应越过 `G3` 研究阶段；
  - 先证明“状态可控且可观测”，再谈工程路线。
- **落地判断**：**保持研究，不建议近期工程化。**

### 3.8 混合励磁

- **方案 ID**：`hybrid_excitation`
- **当前证据**：
  - `experiments/exp_007_hybrid_excitation/summary.json`
  - `experiments/exp_010_weighted_efficiency_pareto/summary.json`
- **当前结论**：
  - 在当前单实验 `exp_007` 中，最优点仍是 `if = 0 A`；
  - 但在工况加权 `exp_010` 中，`hybrid_excitation_if_plus_20` 成为 Pareto 前沿第一；
  - 这说明该路线对单点边界未必有优势，但对工况加权损耗可能有结构性收益。
- **工程落地点**：
  - 不能仅靠 `psi_eff = psi_pm + kf * if` 的等效模型推进；
  - 应升级为三变量 `id/iq/if` 联合优化，再叠加 field 热模型和 exciter 损耗。
- **还缺什么**：
  - field inductance、动态、热模型；
  - field converter 损耗；
  - loss-of-field 故障分析；
  - 主逆变器与励磁支路联合控制边界。
- **硬件影响**：
  - 明显新增 field converter、field sensing、热管理和接口隔离；
  - 是高硬件成本路线。
- **阶段门建议**：
  - 当前只适合 `G2/G3` 架构 + 数值联合论证；
  - 进入 `G4` 之前必须证明总损耗收益能覆盖新增系统复杂度。
- **落地判断**：**值得保留，但属于重硬件路线，必须靠加权收益而不是单点边界说服。**

### 3.9 绕组重构

- **方案 ID**：`winding_reconfiguration`
- **当前证据**：
  - `experiments/exp_008_winding_reconfiguration/summary.json`
- **当前结论**：
  - 当前参数化配置里，推荐仍是 `base`；
  - `series_torque -> base` 过渡可行，但 `base -> parallel_speed` 在配置转速处不可行；
  - 说明该路线的最大挑战不是静态双区间收益，而是切换点可行性。
- **工程落地点**：
  - 必须把“切换瞬态”和“非法配置保护”作为主问题；
  - 不能只用静态 Ke/Kt 缩放结果来判断工程价值。
- **还缺什么**：
  - switching transient；
  - current interruption / arc / circulating current；
  - interlock logic；
  - open/short/stuck fault 模型。
- **硬件影响**：
  - 需要高电流切换矩阵、隔离、反馈和硬件互锁；
  - 功率硬件代价很重。
- **阶段门建议**：
  - 只有在多配置收益明显超过单配置路线时才值得进入 `G4`；
  - 当前证据不支持加速推进。
- **落地判断**：**现阶段工程吸引力不足，除非后续模型证明收益显著。**

### 3.10 多相 / 相组控制

- **方案 ID**：`multiphase_phase_group_control`
- **当前证据**：
  - `experiments/exp_009_multiphase_phase_group/summary.json`
- **当前结论**：
  - 当前模型只把相组问题抽象成可用电流降额；
  - 在单组 limp-home 情形下，目标点不可达；
  - 说明多相路线如果没有更强 fault-tolerant torque 收益，就很难单靠“更多相数”证明价值。
- **工程落地点**：
  - 现阶段应定位为“架构和容错评估路线”，不是主控制增效路线；
  - 需要补 harmonic subspace、open-phase vectors、热失衡瞬态。
- **还缺什么**：
  - fault-tolerant torque allocator；
  - ADC/PWM 资源预算；
  - 中性点/相组故障控制策略；
  - 产品需求牵引下的容错价值证明。
- **硬件影响**：
  - 增加逆变器通道数、传感器、MCU/FPGA 资源、隔离域。
- **阶段门建议**：
  - 没有明确容错需求前，不建议进入高成本硬件阶段。
- **落地判断**：**适合在有强容错产品需求时再推进。**

### 3.11 温度 / 退磁 / 安全保护

- **方案 ID**：`thermal_demag_safety_protection`
- **当前证据**：
  - `experiments/exp_004_safety_boundaries/summary.json`
  - `models/scheme_industry_stage_gate_process.json`
  - `models/scheme_bom_eda_catalog.json`
- **当前结论**：
  - 这不是附属路线，而是所有路线的强制横切层；
  - 当前已实现简化版 `Rs(T)`、`psi_f(T)` 和 `id_min(T)`；
  - 但仍缺工程可信的 demag 数据和 fault case 闭环。
- **工程落地点**：
  - 应进入所有 search / LUT / controller export 的统一边界过滤；
  - 也应进入硬件安全链：温度、watchdog、gate-disable、fault latch。
- **还缺什么**：
  - FEA 或磁钢数据支持的 `id_min(T, fault)`；
  - 传感器可信度与故障注入；
  - DVP&R fault cases。
- **硬件影响**：
  - 对传感器、监控、电源监测、故障锁存要求直接影响原理图。
- **阶段门建议**：
  - 所有路线进入 `G4/G5` 前必须绑定这条路线；
  - 它不是可选项。
- **落地判断**：**横切必做项，与控制主线同等优先。**

### 3.12 工况加权效率 / Pareto 选择

- **方案 ID**：`weighted_efficiency_pareto_selection`
- **当前证据**：
  - `experiments/exp_010_weighted_efficiency_pareto/summary.json`
  - `experiments/exp_011_iron_loss/summary.json`
- **当前结论**：
  - 该路线不是物理实现路线，而是决策路由器；
  - 在仅铜耗加权时，`hybrid_excitation_if_plus_20` 最优；
  - 加入当前 Bertotti 铁耗后，系统效率判断会被高速铁耗强烈改变。
- **工程落地点**：
  - 它必须成为所有路线的统一决策出口；
  - 否则各实验只能得出局部边界，无法形成项目优先级。
- **还缺什么**：
  - 更真实 drive cycle；
  - iron + mechanical + inverter + thermal 统一损耗；
  - 风险、复杂度、成熟度字段并入 scorecard。
- **硬件影响**：
  - 主要是测试/日志/版本管理和候选追踪要求。
- **阶段门建议**：
  - 所有路线从“研究”升级到“工程候选”前，都必须经过该层评审。
- **落地判断**：**这是项目决策层，不是可选分析工具。**

---

## 4. 当前最值得推进的工程主线

### 主线一：控制量产主线

由以下四部分组成：

1. `negative_d_axis_field_weakening`
2. `mtpa_fw_mtpv_control`
3. `nonlinear_flux_lut`
4. `thermal_demag_safety_protection`

这是当前最接近可量产控制路线的组合，因为它：

- 不强依赖新增电机或主功率拓扑；
- 能逐步吸收更高可信度数据；
- 有明确的软件、标定、保护、诊断落点；
- 与现有仓库结构最一致。

建议把后续实现聚焦为：

- 统一 `search -> LUT -> control_lut -> safety filter -> coverage summary`；
- 不再让各实验孤立生长。

### 主线二：中期电机协同设计主线

由以下两部分组成：

1. `magnetic_saturation_codesign`
2. `pmasynrm_high_saliency_low_pm`

这条线应建立在“FEA 候选数据能够无缝回注到非线性磁链 LUT”的前提下。没有这条回注链，电机研究与控制工程会继续脱节。

### 主线三：长周期研究储备线

- `variable_magnetization_memory_motor`
- `hybrid_excitation`
- `winding_reconfiguration`
- `multiphase_phase_group_control`

这几条线当前都不适合直接进入工程实现排期，应继续保持“低成本建模、保留证据、持续比较”的策略，避免过早投入硬件化资源。

---

## 5. 建议的下一步工程动作

### P0：把主线真正收敛成统一工程出口

1. 让 `run_control_lut_generator.py` 支持非线性磁链 LUT。
2. 把 `exp_004` 的安全边界并入控制 LUT 生成过滤逻辑。
3. 给 control LUT 增加版本、CRC、不可行区标记、边界来源字段。
4. 更新 `scheme_simulation_coverage.json`，让覆盖关系体现“主干集成”而不是单实验存在。

### P1：建立 FEA / 实测数据接入桥梁

1. 增加 FEA 到 `flux_lut_schema.json` 的转换约定。
2. 固化 dq 约定、峰值/RMS、轴向符号和单位声明。
3. 为候选电机路线增加 scorecard 模板，把 FEA/LUT/控制结果绑在同一 candidate ID 下。

### P1：提升决策层可信度

1. 扩展 `exp_010/011` 到统一损耗模型。
2. 在 Pareto 输出中加入风险、复杂度、成熟度字段。
3. 区分“研究排序”和“工程推荐”，避免误读。

### P2：长周期方案继续保留，但不要抢主线资源

- Memory Motor、绕组重构、多相路线以边界扫描和业务 case 为主；
- 混合励磁继续用加权收益证明其存在意义；
- 不在缺少硬件收益证据时提前进入原理图阶段。

---

## 6. 最终结论

如果目标是“继续深度梳理每个研究方案的工程落地”，当前最重要的结论不是哪条路线单次数值最好，而是：

1. **真正可落地的近期主线已经很清楚**：弱磁 + 连续控制 + 非线性磁链 LUT + 安全保护。  
2. **中期突破的关键也很清楚**：把电机几何/FEA 候选无缝接到统一 LUT/控制/评分链。  
3. **长周期研究路线必须继续留在研究池**：除非它们能在加权收益上显著优于主线，并证明新增硬件复杂度值得付出。  
4. **项目下一阶段最应该做的不是再开新路线，而是收敛主干接口和证据链**。

也就是说，仓库接下来最有价值的工作，不是继续横向扩展更多实验名目，而是把现有 12 条路线压缩成一张真正能指导工程实施与资源投入的主干地图。