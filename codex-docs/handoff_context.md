# Codex 开发上下文 Handoff

## 1. 当前工作线

- 当前分支：`codex-review-line`
- 主要目标：把可控磁通量电机技术路线沉淀为可交接、可追踪、可继续开发的 Codex 知识库。
- 当前状态：EXP-001 到 EXP-010 全部具备**可重跑的 Python 入口 + 单元/烟雾测试 + 模型限制声明**；唯一仍标记 `needs_next_numeric_model` 的方案是 `nonlinear_flux_lut`（缺 lambda_d/lambda_q LUT schema 与插值测试）。
- 本目录目的：让下一位接手者能快速定位上下文、证据、仿真入口和仍需工程化的缺口。

## 2. 已完成的主线能力

| 能力 | 证据 |
|---|---|
| wiki 研发框架 | `wiki/controllable_flux_motor_research_plan.md` |
| HTML 知识库 | `controllable_flux_motor_kb.html` |
| 工程落地矩阵 | `reports/scheme_engineering_landing_matrix.md` |
| 驱动、上电时序、协议图 | `reports/scheme_driver_power_protocol_diagrams.md` |
| BOM / EDA 集成设计 | `reports/scheme_bom_eda_integration_design.md` |
| 成熟业界 stage-gate 流程 | `reports/scheme_industry_design_stage_gate_process.md` |
| 仿真覆盖目录 | `models/scheme_simulation_coverage.json` |

## 3. 当前已落地仿真

| 实验 | 入口 | 作用 |
|---|---|---|
| EXP-001 | `sim/run_linear_dq_experiment.py` | 线性 dq 基线、负 d 轴弱磁、MTPA/FW/MTPV 风格搜索 |
| EXP-002 | `sim/run_variable_flux_experiment.py` | 可变磁链 / memory motor 虚拟 `psi_f` 状态扫描 |
| EXP-003 | `sim/run_param_sweep_experiment.py` | 参数族扫描，覆盖磁饱和协同和 PMaSynRM 方向代理 |
| EXP-004 | `sim/run_safety_boundary_experiment.py` | 温度、Vdc 降额、简化退磁边界 |
| EXP-005 | `sim/run_modulation_factor_experiment.py` | SVPWM 过调制 `k_mod` 扫描 + 谐波 / 逆变器损耗 / 转矩纹波参数化惩罚 |
| EXP-007 | `sim/run_hybrid_excitation_experiment.py` | 混合励磁等效 `psi_eff = psi_pm + kf*if`，比对 `Pcu+Pf` |
| EXP-008 | `sim/run_winding_reconfiguration_experiment.py` | 绕组重构 `turns/R/Imax` 扫描 + 切换速度连续性增量 |
| EXP-009 | `sim/run_multiphase_phase_group_experiment.py` | 相组失效 / 均流不平衡降额下的可达速度 |
| EXP-010 | `sim/run_weighted_efficiency_pareto_experiment.py` | 城市 / 高速 / 起步三种工况下加权铜耗排名 |

## 4. 当前待建模方向

| 方向 | 当前覆盖状态 | 下一步 |
|---|---|---|
| 非线性磁链 LUT | `needs_next_numeric_model` | 增加 `lambda_d/lambda_q` LUT schema、插值和转矩测试（仍是唯一缺位） |
| EXP-005 谐波/损耗曲线 | `passed_numeric_simulation`（参数化代理） | 用实测逆变器损耗图和 PWM 波形重建替换线性代理 |
| EXP-007 励磁回路动态 | `passed_numeric_simulation`（稳态铜耗） | 增加场绕组电感、励磁机损耗、热耦合 |
| EXP-008 切换暂态 | `passed_numeric_simulation`（参数缩放） | 增加接触器电弧、循环电流、并联支路热分担 |
| EXP-009 故障暂态 | `passed_numeric_simulation`（聚合电流降额） | 增加谐波子空间、零序偏移、相级热 RC 故障暂态 |
| EXP-010 工况评分 | `passed_numeric_simulation`（铜耗+可达性） | 用实测 drive cycle、增加铁耗 / 机械损耗 / 逆变器损耗 |
| 高速反电动势待定方案 | `pending_deep_dive` | 参考 `claude-review/docs/2026-05-20/v2_high_speed_back_emf_pending_scheme_deep_dive.md`，用统一总损耗 scorecard 比较两挡、绕组重构、小范围混合励磁和可变磁化 |

## 5. 接手时优先检查

1. 先读 `codex-docs/README.md`。
2. 再读 `codex-docs/evidence_manifest.md`，确认证据哈希是否变化。
3. 打开 `models/scheme_simulation_coverage.json`，确认方案状态和下一步建模项。
4. 运行 `python -m pytest -q`。
5. 如测试生成 CSV 快照差异，确认是否是测试步长导致，不要误提交不需要的生成物。

## 6. 当前已知注意事项

- `.claude/settings.local.json` 是本地配置文件，不应提交到知识库。
- `codex-docs` 是新知识库入口；旧文档目录不存在时，不要在新文档中引用不存在路径。
- 部分源文件存在编码显示问题，作为历史证据保留，不在本轮重写原文。
- 当前分支的 `passed_numeric_simulation` 不等于工程验证，所有工程释放仍需 FEA、台架、热、EMC 和安规验证。
