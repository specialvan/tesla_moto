# Codex 证据 Manifest

## 1. 固化快照

| 证据 | 快照路径 | SHA256 | 用途 |
|---|---|---|---|
| wiki 研究计划 | `codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | `2C16230F519501E80B18BCF44D7DAA0100224E96B436B25D9A50730F5E2661FB` | 研发目标、物理模型、假设树和路线图源证据 |
| HTML 知识库 | `codex-docs/snapshots/html/controllable_flux_motor_kb.html` | `7759CFC7153CD26668DA10E6FF82E694B8434DF06423B496D2D4C4AD2E8F1A16` | 可视化知识库和页面化证据 |

## 2. 活动证据源

| 证据 | 路径 | SHA256 | 用途 |
|---|---|---|---|
| 仿真覆盖目录 | `models/scheme_simulation_coverage.json` | `791C76F13D7255B26D716E1DD3159952B2F1F8C798B6B7A1854F72E608C46792` | 12 个方案的状态、测试和产物映射 |
| V2 数值闭环记录 | `codex-reviwe/v2_numeric_simulation_closure.md` | `797129D3129D2437308D757D76E3CE336FA538A387F17911D6AC526D7421D0C2` | EXP-005 到 EXP-010 的工程解释 |
| Claude 对 Codex 线评审 | `claude-review/codex_development_review.md` | `C67E9503A9AABC19ABB7AB4362C85307BCEA9E85A57D5B41BF2BA901325132D5` | Codex 开发线优缺点、合并建议和风险评审 |
| 工程落地矩阵 | `reports/scheme_engineering_landing_matrix.md` | `DAD3B892A4B034A0111A21D98CA08E576FE9CB6EEC9B0B06D868F8E5B9B70526` | 每种方案的工程目标、输入、实验、验收 |
| 驱动/上电/协议图 | `reports/scheme_driver_power_protocol_diagrams.md` | `59A41D2AE4ACB08C4B5D1368F458961A824BEE1E2285512891BDE63217BF0DBB` | 每种方案对应驱动设计图、上电时序图、协议链路图 |
| BOM/EDA 集成 | `reports/scheme_bom_eda_integration_design.md` | `3BC3F288F0D106836CA9199E057BF4833585CF2476055F5A0572038E3E1F5128` | BOM 配件分组、EDA 电路模块、接口和保护 |
| Stage-gate 流程 | `reports/scheme_industry_design_stage_gate_process.md` | `85BC81B775B30E6906F4D32200DABFEA12DE054C0F1BECF587570407A3A537A5` | 成熟业界设计推进流程和评审门槛 |

## 3. 仿真实验证据

| 实验 | Summary | CSV |
|---|---|---|
| EXP-001 | `experiments/exp_001_linear_dq/summary.json` | `experiments/exp_001_linear_dq/scan_results.csv` |
| EXP-002 | `experiments/exp_002_variable_flux/summary.json` | `experiments/exp_002_variable_flux/variable_flux_scan.csv` |
| EXP-003 | `experiments/exp_003_param_sweep/summary.json` | `experiments/exp_003_param_sweep/param_sweep_results.csv` |
| EXP-004 | `experiments/exp_004_safety_boundaries/summary.json` | `experiments/exp_004_safety_boundaries/safety_boundary_results.csv` |
| EXP-005 | `experiments/exp_005_modulation_factor/summary.json` | `experiments/exp_005_modulation_factor/modulation_sweep_results.csv` |
| EXP-006 | `experiments/exp_006_nonlinear_flux_lut/summary.json` | `experiments/exp_006_nonlinear_flux_lut/nonlinear_flux_lut_results.csv` |
| EXP-007 | `experiments/exp_007_hybrid_excitation/summary.json` | `experiments/exp_007_hybrid_excitation/hybrid_excitation_results.csv` |
| EXP-008 | `experiments/exp_008_winding_reconfiguration/summary.json` | `experiments/exp_008_winding_reconfiguration/winding_reconfiguration_results.csv` |
| EXP-009 | `experiments/exp_009_multiphase_phase_group/summary.json` | `experiments/exp_009_multiphase_phase_group/multiphase_phase_group_results.csv` |
| EXP-010 | `experiments/exp_010_weighted_efficiency_pareto/summary.json` | `experiments/exp_010_weighted_efficiency_pareto/weighted_efficiency_pareto_results.csv` |

## 4. 当前缺口证据

当前 `models/scheme_simulation_coverage.json` 中 12 个方向均已有数值仿真证据。剩余缺口不是“无仿真”，而是模型成熟度缺口：

- 参数化惩罚需要替换为 PWM、器件、EMI 和纹波模型；
- 合成 LUT 需要替换为 FEA 或台架磁链图；
- 聚合降额需要替换为逐相/逐组动态模型；
- v0 Pareto 权重需要替换为工况、成本、质量和安全风险模型。

## 5. 更新规则

证据文件发生变化时，重新运行：

```powershell
Get-FileHash -Algorithm SHA256 <path>
```

然后同步更新本 manifest。未更新哈希的证据不得作为冻结快照引用。
