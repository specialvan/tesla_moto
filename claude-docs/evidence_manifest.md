# Claude 证据 Manifest

## 1. 固化快照

| 证据 | 快照路径 | 用途 |
|---|---|---|
| wiki 研究计划 | `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | 研发目标、物理模型、假设树、路线图和实验矩阵源证据 |
| V2 review-pr 工程差距 Wiki | `claude-docs/snapshots/wiki/v2_review_pr_engineering_prd_wiki.md` | 外部资料到真实工程落地差距的知识库证据 |
| V2 分方案工程落地 Wiki | `claude-docs/snapshots/wiki/v2_scheme_engineering_playbook_wiki.md` | 12 条主线、候选、研究池路线逐条推进的知识库证据 |
| HTML 知识库 | `claude-docs/snapshots/html/controllable_flux_motor_kb.html` | 可视化知识库和页面化证据 |
| V2 review-pr 工程差距 HTML | `claude-docs/snapshots/html/v2_review_pr_engineering_prd.html` | V2 PRD 的页面化评审证据 |
| V2 分方案工程落地 HTML | `claude-docs/snapshots/html/v2_scheme_engineering_playbook.html` | V2 分方案 playbook 的页面化评审证据 |

## 2. 活动证据源

| 证据 | 路径 | 用途 |
|---|---|---|
| 仿真覆盖目录 | `models/scheme_simulation_coverage.json` | 12 个方案的状态、测试和产物映射 |
| 工程落地矩阵 | `reports/scheme_engineering_landing_matrix.md` | 每种方案的工程目标、输入、实验、验收 |
| 驱动/上电/协议图 | `reports/scheme_driver_power_protocol_diagrams.md` | 每种方案对应驱动设计图、上电时序图、协议链路图 |
| BOM/EDA 集成 | `reports/scheme_bom_eda_integration_design.md` | BOM 配件分组、EDA 电路模块、接口和保护 |
| Stage-gate 流程 | `reports/scheme_industry_design_stage_gate_process.md` | 成熟业界设计推进流程和评审门槛 |
| 工程目录 JSON | `models/scheme_engineering_catalog.json` | 方案目录、证据路径和工程元数据 |
| 行业阶段门 JSON | `models/scheme_industry_stage_gate_process.json` | 阶段门结构化数据 |
| 高保真工具链选型 | `claude-docs/toolchain_selection_and_github_references.md` | Maxwell / Motor-CAD / Simulink / GitHub 参考项目和质量门槛 |
| Maxwell / Motor-CAD 仿真方案 | `claude-docs/maxwell_motorcad_simulation_plan.md` | 确定工程主线仿真平台、FEA/热/NVH/控制闭环和中文报告结构 |
| V2 review-pr PRD | `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.md` | 可变磁通、扁线、油冷、多合一外部资料到工程落地差距的完整需求源 |
| V2 review-pr Wiki | `wiki/v2_review_pr_engineering_prd_wiki.md` | V2 PRD 的知识库索引活动源 |
| V2 review-pr HTML | `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.html` | V2 PRD 的页面化活动源 |
| V2 分方案工程落地 Playbook | `claude-review/docs/2026-05-15/v2_scheme_engineering_playbook.md` | 12 条路线逐条明确输入输出、BOM/EDA 影响、缺失证据和阶段门条件的完整执行源 |
| V2 分方案工程落地 Wiki | `wiki/v2_scheme_engineering_playbook_wiki.md` | V2 分方案 playbook 的知识库索引活动源 |
| V2 分方案工程落地 HTML | `claude-review/docs/2026-05-15/v2_scheme_engineering_playbook.html` | V2 分方案 playbook 的页面化活动源 |
| Claude 文档迁移索引 | `claude-docs/migration_alignment_index.md` | 确认 Claude 知识库、wiki、HTML、handoff、证据和工具链文档已按 Codex 文档包对齐 |

## 3. 仿真实验证据

| 实验 | Summary | CSV | README |
|---|---|---|---|
| EXP-001 | `experiments/exp_001_linear_dq/summary.json` | `experiments/exp_001_linear_dq/scan_results.csv` | `experiments/exp_001_linear_dq/README.md` |
| EXP-002 | `experiments/exp_002_variable_flux/summary.json` | `experiments/exp_002_variable_flux/variable_flux_scan.csv` | `experiments/exp_002_variable_flux/README.md` |
| EXP-003 | `experiments/exp_003_param_sweep/summary.json` | `experiments/exp_003_param_sweep/param_sweep_results.csv` | `experiments/exp_003_param_sweep/README.md` |
| EXP-004 | `experiments/exp_004_safety_boundaries/summary.json` | `experiments/exp_004_safety_boundaries/safety_boundary_results.csv` | `experiments/exp_004_safety_boundaries/README.md` |
| EXP-005 | `experiments/exp_005_modulation_factor/summary.json` | `experiments/exp_005_modulation_factor/modulation_sweep_results.csv` | `-` |
| EXP-006 phase-1 | `experiments/exp_006_nonlinear_flux_lut/summary.json` | `experiments/exp_006_nonlinear_flux_lut/nonlinear_flux_lut_results.csv` | `experiments/exp_006_nonlinear_flux_lut/README.md` |
| EXP-006 phase-2 | `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json` | `experiments/exp_006_nonlinear_flux_lut/lut_search_scan_results.csv` | `experiments/exp_006_nonlinear_flux_lut/README.md` |
| EXP-007 | `experiments/exp_007_hybrid_excitation/summary.json` | `experiments/exp_007_hybrid_excitation/hybrid_excitation_results.csv` | `-` |
| EXP-008 | `experiments/exp_008_winding_reconfiguration/summary.json` | `experiments/exp_008_winding_reconfiguration/winding_reconfiguration_results.csv` | `-` |
| EXP-009 | `experiments/exp_009_multiphase_phase_group/summary.json` | `experiments/exp_009_multiphase_phase_group/multiphase_phase_group_results.csv` | `-` |
| EXP-010 | `experiments/exp_010_weighted_efficiency_pareto/summary.json` | `experiments/exp_010_weighted_efficiency_pareto/weighted_efficiency_pareto_results.csv` | `-` |

## 4. 当前关键证据结论

### EXP-001

- 模型范围：准稳态线性 dq IPMSM 网格搜索。
- 当前基线：100 Nm、360 V DC bus、260 A phase peak。
- 结果：最小电流目标转矩点可达 6750 rpm；最大可行正转矩点可扫到 18000 rpm。

### EXP-002

- 模型范围：虚拟 `psi_f` 缩放状态扫描。
- 结果：直接降低 `psi_f` 会显著损失目标转矩能力。
- 含义：真实低 `Ke` 路线必须配合状态切换、拓扑、凸极比和控制轨迹协同。

### EXP-003

- 模型范围：`psi_f/Ld/Lq/Vdc/Imax` 参数族启发式扫描。
- 结果：最高分组合为 `psi1.00_ld0.80_lq1.60_vdc1.15_imax1.15`。
- 低磁链候选：`psi0.70_ld0.80_lq1.60_vdc1.15_imax1.15` 排名第二。
- 含义：低 `psi_f` 不是独立收益源，必须和高凸极比、较高母线电压或电流能力协同。

### EXP-004

- 模型范围：温度修正线性 dq + 简化退磁边界。
- 含义：退磁和热边界必须成为所有控制/拓扑路线的横向安全层。
- 限制：简化退磁线必须被真实磁钢数据、FEA 或台架数据替换。

### EXP-005

- 模型范围：在线性 dq speed sweep 上显式引入 `k_mod` 调制因子与参数化谐波/损耗惩罚。
- 含义：已可重跑评估过调制电压利用率收益，但仍需实测逆变器损耗图与 PWM 重建 THD 替换参数化代理。

### EXP-006

- phase-1 模型范围：synthetic `lambda_d/lambda_q` LUT schema、边界检查、双线性插值、非线性转矩。
- phase-2 模型范围：在现有 `search.py` 上接入 LUT，完成电压/电流约束下的 target torque 与 max feasible torque speed sweep。
- 含义：主线已证明非线性磁链表不仅能独立成立，还能进入受约束搜索链路；但仍未形成 FEA/实测驱动的工程释放证据。

### EXP-007 ~ EXP-010

- EXP-007：已可重跑混合励磁等效 `psi_eff` 代理实验，下一步是补励磁电感、漏磁和热耦合。
- EXP-008：已可重跑绕组重构代理实验，下一步是补切换瞬态、环流和支路热分配。
- EXP-009：已可重跑多相相组降额实验，下一步是补谐波子空间解耦和每相热 RC。
- EXP-010：已可重跑加权效率路由筛选，下一步是用实测工况与更多损耗项替换示意代理。

## 5. 当前缺口证据

下列方向仍不是 Claude 主线的完整数值仿真闭环：

- `svpwm_overmodulation_voltage_utilization`
- `nonlinear_flux_lut`
- `hybrid_excitation`
- `winding_reconfiguration`
- `multiphase_phase_group_control`
- `weighted_efficiency_pareto_selection`

这些项已有工程文档、可复现实验或架构验证证据，但不能写成当前主线已通过完整数值仿真。

## 6. 更新规则

证据文件发生变化时：

1. 复制最新 wiki / HTML 到 `claude-docs/snapshots/`。
2. 更新本 manifest 的路径、用途和关键结论。
3. 如需要强审计，可补充 SHA256；在 Windows PowerShell 中可使用：

```powershell
Get-FileHash -Algorithm SHA256 <path>
```

未更新 manifest 的证据不得作为冻结快照引用。
