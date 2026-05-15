# 可控磁通项目版本推进路线图

日期：2026-05-15  
目标：把当前研究型仓库收敛成可持续推进的工程主线，避免实验脚本继续横向发散。

---

## 1. 路线图总原则

后续版本推进不再以“新增多少实验”为核心，而以“主干接口是否统一、证据是否可追溯、阶段门是否可放行”为核心。

主干必须围绕三层统一：

1. **统一输入模型层**  
   - 线性 dq 参数源；
   - 非线性磁链 LUT 参数源；
   - 后续候选电机 / FEA 数据也必须回到这两类统一入口。
2. **统一求解层**  
   - 以 `sim/search.py:21` 的 `GridSpec`、`sim/search.py:66` 的 `Candidate`、`sim/search.py:127` / `151` / `171` 的搜索策略为核心；
   - 扩展必须以共享求解骨架为前提，而不是复制 runner。
3. **统一输出层**  
   - 以 `models/control_lut_schema.json:1` 为主输出契约；
   - `summary.json` 和 CSV 只作为派生视图；
   - 阶段门、覆盖登记、方案评分都应回引用同一批结果。

---

## 2. v0.3：主干收敛版

### 2.1 版本目标

建立唯一可持续主线：

- 负 d 轴弱磁；
- MTPA / FW / MTPV 连续控制；
- 非线性磁链 LUT；
- 温度 / 退磁 / 安全边界。

这四项组成近期最现实的工程主干。

### 2.2 本阶段必须完成的能力

1. `run_control_lut_generator.py` 能明确表达主线控制轨迹生成逻辑。  
2. 非线性磁链 LUT 与线性 dq 模型都能进入统一搜索链。  
3. 安全边界不再只是实验后分析，而能作为控制 LUT 生成过滤条件。  
4. 输出结果统一回到 control LUT、feasibility map、mode transition、validation 四类证据。

### 2.3 关键文件

- `sim/search.py:21`
- `sim/search.py:127`
- `sim/search.py:151`
- `sim/search.py:171`
- `sim/search.py:197`
- `sim/run_control_lut_generator.py:44`
- `sim/run_control_lut_generator.py:196`
- `sim/run_control_lut_generator.py:261`
- `models/control_lut_schema.json:1`
- `models/flux_lut_schema.json:1`
- `experiments/exp_001_linear_dq/summary.json:1`
- `experiments/exp_004_safety_boundaries/summary.json:1`
- `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json`

### 2.4 验收证据

- control LUT 能追溯模型来源；
- 不可行点有明确 `infeasibility_reason`；
- 模式切换连续性可报告；
- 安全边界已进入 LUT 过滤逻辑；
- `scheme_simulation_coverage.json` 体现主干集成关系，而不是分散实验存在。

### 2.5 本阶段不进入主线的方案

继续留在研究池：

- Memory Motor；
- 混合励磁；
- 绕组重构；
- 多相 / 相组控制。

---

## 3. v0.4：工程证据化版

### 3.1 版本目标

把主干从“能跑”提升到“可审、可追溯、可准备下阶段工程接口”。

### 3.2 本阶段必须完成的能力

1. 控制 LUT 增加版本、生成器信息、模型来源、边界来源。  
2. 统一 coverage 目录，把方案、实验、测试、工艺阶段门拉通。  
3. 把方案目录、stage gate、BOM/EDA 规划映射到统一证据矩阵。  
4. 固化 dq 约定、峰值/RMS、单位、插值/外推策略。

### 3.3 关键文件

- `models/scheme_engineering_catalog.json:1`
- `models/scheme_industry_stage_gate_process.json:1`
- `models/scheme_simulation_coverage.json:1`
- `models/scheme_bom_eda_catalog.json:1`
- `models/control_lut_schema.json:59`
- `models/control_lut_schema.json:150`
- `models/control_lut_schema.json:220`
- `models/control_lut_schema.json:260`

### 3.4 验收证据

- G3 所需控制/仿真证据可一键指向具体文件；
- 每个主线方案有明确 required_inputs / acceptance / failure_modes；
- 所有 summary 都有 `parameter_source`、`model_scope`、`model_limitations`；
- 可生成“控制发布草案”和“研究池保留说明”。

### 3.5 本阶段仍不进入工程实现排期的方案

- Memory Motor；
- 绕组重构；
- 多相 / 相组控制。  
混合励磁可保留，但只作为对比候选，不抢占主线实现资源。

---

## 4. v0.5：FEA / 候选电机接入版

### 4.1 版本目标

把中期突破路线真正接入主干：

- 磁路饱和协同设计；
- PMaSynRM / 高凸极低永磁占比。

### 4.2 本阶段必须完成的能力

1. FEA 或候选几何数据能转换为 `flux_lut_schema.json` 兼容输入。  
2. 候选电机拥有统一 candidate ID。  
3. 候选磁链面可回灌控制 LUT 生成。  
4. 候选比较不只看转速边界，还要看加权效率、退磁、铁耗、结构风险。

### 4.3 关键文件 / 证据对象

- `models/flux_lut_schema.json:1`
- `experiments/exp_003_param_sweep/summary.json:1`
- `experiments/exp_006_nonlinear_flux_lut/summary.json:1`
- `claude-review/docs/2026-05-15/research_scheme_engineering_landing_matrix.md`
- 后续新增候选 scorecard / FEA-LUT 转换规范文档

### 4.4 验收证据

- 候选 FEA 数据可以无歧义导入；
- LUT 回灌后控制轨迹、可行区、损耗评估能自动再生成；
- 至少能区分“值得继续候选”和“应停止”的电机方向。

### 4.5 研究池变化

- `magnetic_saturation_codesign`、`pmasynrm_high_saliency_low_pm` 从纯研究进入工程候选评审；
- 其余重硬件路线仍维持研究池状态。

---

## 5. V2：外部工程资料对齐版

### 5.1 版本目标

基于 `review-pr` 中可变磁通、扁线、油冷、多合一资料，把当前研究主线与真实量产电驱工程差距对齐。

### 5.2 本阶段必须补齐的能力

1. 把 Memory Motor / 电磁调磁从静态 `psi_f` 档位假设升级为磁状态机、脉冲能量、状态观测、故障回退问题。  
2. 把扁线绕组、油冷热管理、多合一集成纳入 G2-G6 阶段门，而不是停留在控制算法外部背景。  
3. 把候选电机 scorecard 扩展到绕组、冷却、系统损耗、制造、NVH、EMC 和安全保护。  
4. 明确当前数值实验不能替代 FEA、台架、DFMEA、DVP&R 与量产发布证据。

### 5.3 关键文件 / 证据对象

- `review-pr/这是奇瑞公司的可变磁通电机，技术思路非常巧妙.html`
- `review-pr/新能源汽车驱动电机系列（）——驱动电机发展趋势（扁线、油冷、多合一）.html`
- `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.md`
- `models/scheme_bom_eda_catalog.json:1`
- `models/scheme_industry_stage_gate_process.json:1`
- `models/control_lut_schema.json:1`
- `models/flux_lut_schema.json:1`

### 5.4 验收证据

- V2 PRD 能逐条说明外部资料主张、当前仓库状态、真实工程差距和后续动作；
- Memory Motor 不再被误读为简单 `psi_f` 缩放实验；
- 扁线、油冷、多合一被纳入硬件阶段门和候选 scorecard；
- v0.3 主线与 V2 系统工程约束关系清晰。

---

## 6. v0.6：路线决策收口版

### 6.1 版本目标

形成真正的工程路线选择机制，而不是实验结果堆叠。

### 6.2 本阶段必须完成的能力

1. 工况加权效率和 Pareto 输出扩展为统一决策面；
2. 铁耗、铜耗、机械损耗、逆变器损耗、温度影响逐步并入；
3. 评分中加入复杂度、成熟度、风险、硬件新增量；
4. 能明确给出：主线方案、候选方案、暂停方案。

### 6.3 关键文件

- `experiments/exp_010_weighted_efficiency_pareto/summary.json:1`
- `experiments/exp_011_iron_loss/summary.json:1`
- `sim/iron_loss.py`
- `models/scheme_simulation_coverage.json:1`
- `claude-review/docs/2026-05-15/research_scheme_engineering_landing_matrix.md`

### 6.4 验收证据

- Pareto 推荐在小范围权重扰动下稳定；
- 每条路线能解释为何进入主线或继续留在研究池；
- 决策结果可追溯回具体实验、schema 和 stage gate。

---

## 7. 主线 / 候选 / 研究池的版本性划分

### 主线

- `negative_d_axis_field_weakening`
- `mtpa_fw_mtpv_control`
- `nonlinear_flux_lut`
- `thermal_demag_safety_protection`

### 中期候选

- `magnetic_saturation_codesign`
- `pmasynrm_high_saliency_low_pm`
- `svpwm_overmodulation_voltage_utilization`

### 研究池

- `variable_magnetization_memory_motor`
- `hybrid_excitation`
- `winding_reconfiguration`
- `multiphase_phase_group_control`

---

## 8. 版本推进的最终判断

下一阶段最重要的不是再加更多实验名目，而是完成三件事：

1. 把主干求解与控制输出统一起来；
2. 把安全边界和非线性磁链接入主线；
3. 把候选电机 / FEA / Pareto 决策纳入同一证据链。

如果这三件事完成，这个项目才会从“研究集合”真正进入“可工程推进的平台”。