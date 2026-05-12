# Claude 证据 Manifest

## 1. 固化快照

| 证据 | 快照路径 | 用途 |
|---|---|---|
| wiki 研究计划 | `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | 研发目标、物理模型、假设树、路线图和实验矩阵源证据 |
| HTML 知识库 | `claude-docs/snapshots/html/controllable_flux_motor_kb.html` | 可视化知识库和页面化证据 |

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

## 3. 仿真实验证据

| 实验 | Summary | CSV | README |
|---|---|---|---|
| EXP-001 | `experiments/exp_001_linear_dq/summary.json` | `experiments/exp_001_linear_dq/scan_results.csv` | `experiments/exp_001_linear_dq/README.md` |
| EXP-002 | `experiments/exp_002_variable_flux/summary.json` | `experiments/exp_002_variable_flux/variable_flux_scan.csv` | `experiments/exp_002_variable_flux/README.md` |
| EXP-003 | `experiments/exp_003_param_sweep/summary.json` | `experiments/exp_003_param_sweep/param_sweep_results.csv` | `experiments/exp_003_param_sweep/README.md` |
| EXP-004 | `experiments/exp_004_safety_boundaries/summary.json` | `experiments/exp_004_safety_boundaries/safety_boundary_results.csv` | `experiments/exp_004_safety_boundaries/README.md` |

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

## 5. 当前缺口证据

下列方向仍不是 Claude 主线的完整数值仿真闭环：

- `svpwm_overmodulation_voltage_utilization`
- `nonlinear_flux_lut`
- `hybrid_excitation`
- `winding_reconfiguration`
- `multiphase_phase_group_control`
- `weighted_efficiency_pareto_selection`

这些项已有工程文档或架构验证证据，但不能写成当前主线已通过完整数值仿真。

## 6. 更新规则

证据文件发生变化时：

1. 复制最新 wiki / HTML 到 `claude-docs/snapshots/`。
2. 更新本 manifest 的路径、用途和关键结论。
3. 如需要强审计，可补充 SHA256；在 Windows PowerShell 中可使用：

```powershell
Get-FileHash -Algorithm SHA256 <path>
```

未更新 manifest 的证据不得作为冻结快照引用。
