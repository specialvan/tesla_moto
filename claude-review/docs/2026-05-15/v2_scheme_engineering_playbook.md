# V2 分方案工程落地 Playbook

日期：2026-05-15  
目标：把 V2 PRD 中的系统工程要求落实到每一条研究/候选/主线方案，形成可执行的输入、输出、接口、BOM/EDA、验证证据和阶段门推进条件。

关联文档：

- `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.md`
- `claude-review/docs/2026-05-15/research_scheme_engineering_landing_matrix.md`
- `claude-review/docs/2026-05-15/stage_gate_execution_checklist.md`
- `claude-review/docs/2026-05-15/version_execution_roadmap.md`

---

## 1. V2 推进原则

V2 不再把每个方案当成孤立实验，而是按同一套工程化模板推进：

1. **输入模型**：线性 dq、非线性磁链 LUT、FEA/实测、热边界、冷却边界、磁状态边界。
2. **控制接口**：control LUT、feasibility map、mode transition、infeasibility reason、derating/fallback。
3. **硬件接口**：BOM/EDA 页级对象、传感器、驱动、冷却、保护、连接器、故障锁存。
4. **验证证据**：pytest/summary/CSV、FEA、HIL、bench DV、DVP&R、DFMEA、PV/PPAP。
5. **决策出口**：主线、候选、研究池、暂停，并说明进入/退出条件。

所有方案默认成熟度不超过 `numeric_simulation`，除非有明确 FEA、台架或量产证据。

---

## 2. V2 统一产物清单

| 产物 | 用途 | 适用方案 |
|---|---|---|
| `control_lut` | 控制发布候选，包含模型来源、边界来源、不可行原因 | 主线控制、弱磁、非线性 LUT、安全保护、过调制 |
| `candidate_scorecard` | 统一评价候选电机/硬件路线 | 磁路饱和、PMaSynRM、扁线/油冷、多合一、混合励磁 |
| `flux_lut_import_spec` | FEA/实测磁链面导入规范 | 非线性 LUT、磁路饱和、PMaSynRM、Memory Motor |
| `thermal_cooling_boundary` | 油冷、水冷、磁钢温度和退磁边界输入 | 所有进入 G4 的方案 |
| `bom_eda_page_map` | 页级硬件交付物映射 | 安全保护、过调制、混合励磁、绕组重构、多相 |
| `dfmea_dvpr_stub` | DFMEA/DVP&R 初稿 | 所有 G4+ 方案 |
| `system_loss_breakdown` | 铜耗、铁耗、逆变器、机械、油泵、冷却惩罚 | 所有路线决策 |
| `research_pool_guardrail` | 研究池保留说明和禁止误判项 | Memory Motor、绕组重构、多相、混合励磁 |

---

## 3. 分方案工程落地

### 3.1 负 d 轴弱磁

- **方案 ID**：`negative_d_axis_field_weakening`
- **V2 定位**：近期主线，必须和安全保护绑定推进。
- **工程目标**：在不改变硬件拓扑的前提下，通过负 `id` 降低合成 d 轴磁链和端电压压力，扩大高速可行区。

#### 输入要求

| 输入 | 当前状态 | V2 补齐 |
|---|---|---|
| 线性 dq 参数 | 已有 `models/motor_params.json` / EXP-001 | 补参数来源、温度版本、峰值/RMS 约定 |
| 电压/电流限制 | 已有基础约束 | 增加 Vdc_min、采样误差、逆变器限流策略 |
| 热/退磁边界 | EXP-004 简化 | 替换为 `id_min(T, fault)`、磁钢材料/FEA/台架来源 |
| 油冷边界 | 缺失 | 接入油温、流量、磁钢温度估计 |

#### 控制落地

1. 进入 `run_control_lut_generator.py` 主线。
2. control point 必须记录 `id_a`、`iq_a`、`voltage_margin_v`、`current_margin_a`、`demag_margin_a`。
3. 不可行原因至少区分：`voltage_exceeded`、`current_exceeded`、`demagnetization_risk`、`thermal_derating`。
4. 高速区必须有 derating 和 fallback 策略。

#### BOM/EDA 影响

- 不新增主功率拓扑；
- 必须映射到 current sensing、Vdc sensing、temperature sensing、gate-disable、fault latch 页面；
- 进入 G4 前需要明确传感器可信度和诊断覆盖。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G3 | 控制 LUT + feasibility map + 安全边界过滤测试 |
| G4 | sensing / gate-disable / fault latch 页级设计 |
| G5-G6 | 高温、低压、高速、传感器故障注入台架 |

#### 进入 / 停止条件

- **进入 G3 主线**：控制 LUT 已吸收热/退磁边界。
- **进入 G4 前**：demag curve 有可追溯来源。
- **停止或降级**：弱磁收益小于热/退磁风险，或传感器可信度不足。

---

### 3.2 MTPA / FW / MTPV 连续控制

- **方案 ID**：`mtpa_fw_mtpv_control`
- **V2 定位**：控制主干出口，所有控制型方案都应回流到此。
- **工程目标**：统一低速效率、中速转矩、高速电压极限下的控制轨迹，输出可发布控制 LUT。

#### 输入要求

- 线性 dq 或非线性磁链 LUT；
- speed axis + torque axis；
- Vdc/temperature/cooling state；
- current/voltage/demag/thermal limits；
- model source、generator version、boundary source。

#### 控制落地

1. 从单目标点升级为速度-转矩二维网格。
2. 对每个点记录 mode：`mtpa`、`field_weakening`、`mtpv`、`derated`、`infeasible`。
3. 模式切换必须记录 `id_jump_a`、`iq_jump_a`、`torque_jump_nm`。
4. 输出 CRC、schema version、generator metadata。

#### BOM/EDA 影响

- MCU/NVM 容量、标定页、诊断接口；
- resolver/position sensing 对高速控制边界影响；
- Vdc/current/temp sensing 对模式切换和保护直接约束。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G3 | 二维 control LUT、mode transition、validation report |
| G4 | 标定存储、诊断接口、版本管理设计 |
| G6 | 台架标定 release candidate、模式切换平顺性 |

#### 进入 / 停止条件

- **进入 G3 主线**：二维 LUT 和不可行原因闭合。
- **进入 G4**：LUT 可追溯、可版本化、可诊断。
- **停止或返工**：模式边界不连续，或 LUT 无法解释不可行区。

---

### 3.3 SVPWM / 过调制 / 电压利用率提升

- **方案 ID**：`svpwm_overmodulation_voltage_utilization`
- **V2 定位**：主线高速区增强项，不是独立路线。
- **工程目标**：在受控区间提升电压利用率，延伸高速可行区，同时控制谐波、损耗、NVH、EMC 风险。

#### 输入要求

- `k_mod` 或 modulation region；
- PWM 频率、死区、采样策略；
- DC-link、电流采样带宽；
- 逆变器损耗图和 THD/NVH 代理模型。

#### 控制落地

1. 仅允许在明确速度/转矩/Vdc/温度窗口启用。
2. control LUT 必须记录 `modulation_region` 和退出条件。
3. 不可行原因扩展：`overmodulation_forbidden`、`thd_limit_exceeded`。
4. 必须有回退到普通 SVPWM/FW 的策略。

#### BOM/EDA 影响

- gate driver、DC-link、current sensing bandwidth、EMI filter、layout loop inductance；
- 进入 G4 前必须同步功率回路和 EMC/NVH 风险。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G3 | 参数化收益 + THD/NVH 代理边界 |
| G4 | gate driver / DC-link / EMC 风险评审 |
| G6 | PWM 重建、THD、NVH、器件温升台架 |

#### 进入 / 停止条件

- **进入候选**：高速收益超过普通弱磁且风险可控。
- **进入 G4**：有可测的 THD/NVH/器件损耗计划。
- **停止**：收益小于系统损耗/EMC/NVH 代价。

---

### 3.4 非线性磁链 LUT

- **方案 ID**：`nonlinear_flux_lut`
- **V2 定位**：所有高可信电磁和控制方案的模型底座。
- **工程目标**：用 FEA/实测 `lambda_d/lambda_q` 面替代线性近似，并回灌控制 LUT、损耗评估和候选 scorecard。

#### 输入要求

| 输入 | V2 要求 |
|---|---|
| LUT grid | `id_axis_a`、`iq_axis_a`、可选 temperature axis |
| 单位约定 | dq 变换、峰值/RMS、相量、符号、插值策略 |
| 来源 | synthetic / FEA / bench / supplier / calibrated |
| 边界 | 禁止无保护外推，越界记为 `out_of_flux_lut_bounds` |
| candidate ID | 每个候选电机必须可追溯到同一 ID |

#### 控制落地

1. `run_control_lut_generator.py` 支持 LUT 模式。
2. 线性与 LUT 路径共享同一 feasibility map 和 reason set。
3. LUT 越界、温度缺失、来源不可信必须显式标记。
4. 与铁耗、热、退磁模型共享 candidate ID。

#### BOM/EDA 影响

- 标定存储容量；
- 诊断与调试接口；
- 温度采样维度；
- 生产/维修标定版本管理。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G3 | LUT schema、插值测试、控制搜索接入、越界测试 |
| G4 | 标定存储和版本管理设计 |
| G6 | FEA/台架 LUT 误差评估和回灌报告 |

#### 进入 / 停止条件

- **进入 G3 主线**：LUT 可稳定生成控制轨迹。
- **进入 G4**：LUT 来源可追溯，单位/坐标无歧义。
- **停止或隔离**：LUT 边界过窄、插值误差不可接受、来源不可信。

---

### 3.5 磁路饱和协同设计

- **方案 ID**：`magnetic_saturation_codesign`
- **V2 定位**：中期候选，需要 FEA→LUT→控制闭环。
- **工程目标**：通过磁桥、隔磁槽、barrier、凸极比设计提升弱磁/效率/转矩边界。

#### 输入要求

- 候选几何参数：barrier、bridge、magnet pocket、airgap、stack length；
- FEA 输出：`lambda_d/lambda_q`、torque ripple、iron loss、demag map；
- 结构输出：rotor stress、max speed margin；
- 制造输出：工艺风险、成本、良率。

#### 控制落地

1. 不直接改控制代码，先生成 candidate LUT。
2. 回灌 MTPA/FW/MTPV control LUT。
3. scorecard 同时比较效率、退磁、铁耗、结构、制造。
4. 只允许通过 scorecard 后进入硬件候选。

#### BOM/EDA 影响

- 主要影响电机本体，不直接新增控制板器件；
- 但可能改变温度传感器布局、冷却路径和标定容量。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G2 | 候选几何 trade study |
| G3 | FEA LUT + 控制回灌 + scorecard |
| G4 | 结构/热/制造风险进入 DFMEA |

#### 进入 / 停止条件

- **进入 G3 候选**：FEA LUT 可导入且控制收益明确。
- **进入 G4**：结构、退磁、铁耗、制造风险均可接受。
- **停止**：只在参数缩放中好看，几何/FEA 不成立。

---

### 3.6 PMaSynRM / 高凸极低永磁占比

- **方案 ID**：`pmasynrm_high_saliency_low_pm`
- **V2 定位**：中期候选拓扑，必须与扁线、油冷、系统损耗协同评估。
- **工程目标**：降低永磁占比，同时依靠高凸极比和控制策略维持转矩、效率和高速能力。

#### 输入要求

- PM fraction、barrier geometry、bridge thickness；
- `Ld/Lq/psi_f` 或 FEA LUT；
- torque ripple、NVH、rotor stress；
- 扁线绕组几何和油冷热边界。

#### 控制落地

1. 必须回到非线性 LUT 和控制 LUT。
2. 低速峰值转矩不能只用缩放参数判断。
3. 高速收益必须扣除铁耗、转矩脉动、热和 NVH 风险。
4. candidate scorecard 必须显式比较 PM cost saving 与系统复杂度。

#### BOM/EDA 影响

- 电机几何、磁钢供应链、NVH、结构强度；
- 温度传感器和油冷路径可能需要更精细布置。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G2 | PM fraction / saliency trade study |
| G3 | FEA LUT、ripple/stress/demag 初评 |
| G4 | 样机设计包、DFMEA、制造约束 |

#### 进入 / 停止条件

- **进入候选**：低 PM 成本收益不牺牲主工况效率和峰值转矩。
- **进入 G4**：ripple、stress、demag、thermal 均有证据。
- **停止**：只靠低 `psi_f` 牺牲低速转矩换高速裕度。

---

### 3.7 可变磁化状态 / Memory Motor

- **方案 ID**：`variable_magnetization_memory_motor`
- **V2 定位**：研究池重点规范，不进入近期主线。
- **工程目标**：验证真实磁状态是否可控、可观测、可保持、可安全回退。

#### 输入要求

| 输入 | V2 要求 |
|---|---|
| 磁状态 | `flux_state_id`、`effective_psi_f_wb`、状态保持时间 |
| 脉冲 | 电流、电压、时间、能量、温升 |
| 观测 | observer confidence、状态估计误差 |
| 安全 | 不可逆退磁风险、未知状态 fallback、禁止区 |
| 寿命 | 重复切换次数、漂移、温度影响 |

#### 控制落地

1. 建立磁状态机，而不是简单 `psi_f` scalar。
2. control LUT 必须区分 `field_weakening_by_id` 与 `flux_state_change`。
3. 未知状态必须降额或禁止高速模式。
4. 状态切换需要转矩冲击、热冲击、NVH 风险记录。

#### BOM/EDA 影响

- 可能要求更高脉冲电流能力；
- DC-link、gate driver、温度 sensing、状态观测链路更复杂；
- 必须有硬件禁止区和 fault latch。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G2 | 磁状态机、安全概念、trade-off |
| G3 | 状态切换数值模型、脉冲能量模型、故障场景 |
| G4 前 | 磁体材料、脉冲硬件、保护链可行性 |
| G6 | 重复切换、状态保持、故障注入台架 |

#### 进入 / 停止条件

- **保持研究**：状态不可观测或不可安全回退。
- **进入 G3 深化**：状态机和脉冲模型闭合。
- **进入 G4**：必须证明状态可控、可观测、可保护。
- **停止**：低速能力损失无法补偿，或脉冲风险不可控。

---

### 3.8 混合励磁

- **方案 ID**：`hybrid_excitation`
- **V2 定位**：重硬件研究候选，必须用系统损耗收益证明价值。
- **工程目标**：通过励磁支路连续调节等效磁链，改善加权效率或扩展工作区。

#### 输入要求

- `id/iq/if` 三变量优化；
- field inductance、field resistance、动态响应；
- field converter 损耗与热；
- loss-of-field、over-field、short/open fault；
- 与主逆变器、电池、冷却系统接口。

#### 控制落地

1. `psi_eff = psi_pm + kf * if` 只能作为早期代理。
2. 必须升级为三变量优化和励磁动态约束。
3. control LUT 需记录 `if_a`、field thermal limit、field converter state。
4. 故障时必须回退为永磁基线或降额模式。

#### BOM/EDA 影响

- 新增 field converter、field winding sensing、隔离、保护、热管理；
- EDA 页面新增励磁驱动、励磁电流采样、故障隔离；
- 系统复杂度显著上升。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G2 | 系统架构 trade study 和复杂度评估 |
| G3 | 三变量优化 + 系统损耗 Pareto |
| G4 | field converter 原理图、DFMEA、热设计 |
| G6 | loss-of-field / over-field 故障注入台架 |

#### 进入 / 停止条件

- **进入 G3 候选**：加权效率收益超过新增损耗。
- **进入 G4**：系统收益覆盖 BOM、热、隔离和故障复杂度。
- **停止**：最优点长期接近 `if=0`，或 field converter 损耗抵消收益。

---

### 3.9 绕组重构

- **方案 ID**：`winding_reconfiguration`
- **V2 定位**：研究池，只有在收益显著且切换可保护时才进入候选。
- **工程目标**：通过串并联或绕组连接状态改变等效 Ke/Kt，以兼顾低速转矩和高速电压裕度。

#### 输入要求

- winding state 定义；
- 切换转速/转矩/电流窗口；
- contactor / solid-state switch 模型；
- arc、circulating current、current interruption；
- open/short/stuck fault。

#### 控制落地

1. 静态 Ke/Kt 缩放不能作为工程判断。
2. 必须建模切换瞬态和非法状态保护。
3. control LUT 需记录 winding state 和 switch forbidden region。
4. 切换失败必须有 safe state。

#### BOM/EDA 影响

- 高电流切换矩阵、隔离、反馈、硬件互锁；
- 连接器、母排、热、EMI 风险显著上升；
- 原理图与 layout 风险重。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G2 | 静态收益 + 切换架构 trade study |
| G3 | transient、环流、非法状态仿真 |
| G4 | switch matrix、interlock、DFMEA |
| G6 | 切换瞬态、故障注入、热冲击台架 |

#### 进入 / 停止条件

- **保持研究**：切换点不可行或收益不明显。
- **进入候选**：双状态收益明显超过主线控制方案。
- **停止**：高电流切换风险无法用硬件互锁闭合。

---

### 3.10 多相 / 相组控制

- **方案 ID**：`multiphase_phase_group_control`
- **V2 定位**：容错产品需求牵引的研究池方案。
- **工程目标**：通过多相或相组控制提升 fault-tolerant torque、热分摊或 limp-home 能力。

#### 输入要求

- phase count / group topology；
- harmonic subspace model；
- open-phase vectors；
- per-phase thermal RC；
- ADC/PWM/MCU/FPGA 资源预算；
- neutral point / isolation strategy。

#### 控制落地

1. 不能只用可用电流降额代理判断。
2. 必须建立 fault-tolerant torque allocator。
3. control LUT 或 fault LUT 需表达开相、相组失效、热失衡。
4. 需要明确正常效率收益还是容错收益。

#### BOM/EDA 影响

- 增加逆变器通道、采样、隔离和控制资源；
- layout、EMC、诊断、连接器复杂度上升；
- 若无明确容错需求，不应进入硬件设计。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G1 | 产品容错需求和 limp-home 指标 |
| G2 | 相数/相组架构 trade study |
| G3 | fault torque allocator 和热失衡模型 |
| G4 | ADC/PWM/隔离/连接器设计 |
| G6 | open-phase / group fault 台架 |

#### 进入 / 停止条件

- **进入候选**：存在明确容错产品需求。
- **进入 G4**：资源预算和故障控制策略闭合。
- **停止**：单组 limp-home 不可达且无其他系统收益。

---

### 3.11 温度 / 退磁 / 安全保护

- **方案 ID**：`thermal_demag_safety_protection`
- **V2 定位**：横切强制层，所有方案进入 G4 前必须绑定。
- **工程目标**：把热、退磁、传感器可信度和故障关断变成控制主干与硬件设计的共同约束。

#### 输入要求

- `id_min(T, fault)`；
- magnet temp、stator temp、rotor temp、oil inlet temp、oil flow；
- sensor fault policy；
- Vdc fault、overcurrent、overtemp、resolver fault；
- gate-disable / fault latch path。

#### 控制落地

1. 安全边界进入 search / LUT 候选过滤。
2. 输出 `demagnetization_risk`、`thermal_derating`、`sensor_fault_derating`。
3. 所有高收益控制点必须附带安全裕度。
4. 未知温度或传感器异常必须降额。

#### BOM/EDA 影响

- 温度、Vdc、电流、resolver sensing；
- watchdog、gate-disable、fault latch；
- DC-link discharge 和安全状态；
- 油泵/压力/温度 sensing。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G1 | safety concept 和 fault mapping |
| G3 | 安全边界仿真、故障 derating |
| G4 | DFMEA/FM​EDA、保护链原理图 |
| G6 | fault injection、overtemp、low Vdc、sensor fault 台架 |

#### 进入 / 停止条件

- **进入主线**：所有控制输出可引用安全边界。
- **进入 G4**：保护链和 DFMEA 有实体文档。
- **停止其他方案**：若不能证明故障安全，不允许进入硬件门。

---

### 3.12 工况加权效率 / Pareto 选择

- **方案 ID**：`weighted_efficiency_pareto_selection`
- **V2 定位**：所有路线的统一决策出口。
- **工程目标**：把局部实验结果转为可解释的主线/候选/暂停决策。

#### 输入要求

- drive cycle / use case weights；
- copper、iron、inverter、mechanical、oil pump、cooling losses；
- derating penalty；
- complexity、maturity、manufacturing risk；
- candidate ID 和 evidence path。

#### 控制落地

1. Pareto 不直接发布控制，而发布决策解释。
2. 所有方案必须通过同一 scorecard 才能升级。
3. 区分 `research_rank` 与 `engineering_recommendation`。
4. 权重扰动下应保持结论稳定或明确敏感性。

#### BOM/EDA 影响

- 主要影响日志、测试、版本、候选追踪；
- 对硬件方案会反馈 BOM 成本、热、复杂度、成熟度。

#### 验证证据

| 阶段 | 必要证据 |
|---|---|
| G2 | trade study scorecard |
| G3 | 系统损耗和加权效率结果 |
| G4 | 风险/复杂度/成本并入决策 |
| G6 | 台架效率地图回灌 |

#### 进入 / 停止条件

- **进入主线决策**：所有候选有统一 evidence path。
- **进入工程推荐**：结论对权重扰动稳定，且风险可解释。
- **停止**：只在单点最好，但系统加权或复杂度不成立。

---

## 4. V2 分方案优先级总表

| 优先级 | 方案 | 下一步动作 | 放行目标 |
|---|---|---|---|
| P0 | 负 d 轴弱磁 | 安全边界进入 LUT、低压/高温联合扫描 | G3 主线 |
| P0 | MTPA/FW/MTPV | 二维 control LUT、模式连续性、不行原因闭合 | G3 主线 |
| P0 | 非线性磁链 LUT | FEA/实测导入规范、LUT 模式生成控制 LUT | G3 主线底座 |
| P0 | 温度/退磁安全保护 | `id_min(T,fault)`、sensor fault、gate-disable 映射 | G3/G4 前置 |
| P1 | SVPWM/过调制 | THD/NVH/损耗边界和启停窗口 | G3 候选 |
| P1 | 磁路饱和协同 | candidate geometry → FEA LUT → scorecard | G2-G3 候选 |
| P1 | PMaSynRM | PM fraction / ripple / stress / demag scorecard | G2-G3 候选 |
| P1 | Pareto 决策 | 系统损耗 + 成熟度 + 风险评分 | 统一决策出口 |
| P2 | Memory Motor | 磁状态机、脉冲、状态观测、未知状态回退 | 研究池规范 |
| P2 | 混合励磁 | 三变量优化、field converter 损耗和故障 | 研究候选 |
| P2 | 绕组重构 | 切换瞬态、互锁、环流、非法状态 | 研究池 |
| P2 | 多相相组 | fault torque allocator、资源预算、容错需求 | 研究池 |

---

## 5. 近期执行顺序

### 第 1 步：主线四件套闭环

1. 弱磁 + 安全边界进入 control LUT。
2. MTPA/FW/MTPV 二维化。
3. 非线性 LUT 作为一等输入源。
4. 温度/退磁/传感器 fault 进入统一 reason set。

### 第 2 步：候选电机 scorecard

1. 建立 candidate ID。
2. 增加 FEA LUT 导入规范。
3. 加入扁线、油冷、铁耗、退磁、NVH、制造风险字段。
4. 让磁路饱和、PMaSynRM、过调制通过同一评分出口。

### 第 3 步：研究池 guardrail

1. Memory Motor 不再用 `psi_f` 缩放直接代表工程可行性。
2. 混合励磁必须证明加权收益覆盖新增硬件。
3. 绕组重构必须先证明切换瞬态可保护。
4. 多相路线必须先有容错产品需求。

---

## 6. 最终判断

V2 每个方案的深度工程推进，不是把所有路线都推进到硬件，而是给每条路线明确：

- 当前能不能进入主线；
- 进入下一阶段需要什么输入；
- 输出要落在哪个统一接口；
- 缺哪些工程证据；
- 何时应该暂停或留在研究池。

按这个标准，当前最优路径仍然是：

> 先把弱磁 + 连续控制 + 非线性 LUT + 安全保护做成统一 G3 主线，再用 scorecard 接入磁路/PMaSynRM/过调制候选，最后用 guardrail 管住 Memory Motor、混合励磁、绕组重构和多相路线的工程化冲动。
