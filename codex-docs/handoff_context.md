# Codex 开发上下文 Handoff

## 1. 当前工作线

- 当前分支：`codex-review-line`
- 主要目标：把可控磁通量电机技术路线沉淀为可交接、可追踪、可继续开发的 Codex 知识库。
- 当前状态：EXP-001 到 EXP-004 已在当前分支落地；EXP-005 到 EXP-010 仍应视为下一阶段建模方向，除非后续分支把对应代码、测试和产物重新纳入。
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

| 实验 | 作用 |
|---|---|
| EXP-001 | 线性 dq 基线、负 d 轴弱磁、MTPA/FW/MTPV 风格搜索 |
| EXP-002 | 可变磁链 / memory motor 虚拟 `psi_f` 状态扫描 |
| EXP-003 | 参数族扫描，覆盖磁饱和协同和 PMaSynRM 方向代理 |
| EXP-004 | 温度、Vdc 降额、简化退磁边界 |

## 4. 当前待建模方向

| 方向 | 当前覆盖状态 | 下一步 |
|---|---|---|
| SVPWM 过调制 | `needs_next_numeric_model` | 增加显式 `k_mod`、谐波、损耗、纹波约束 |
| 非线性磁链 LUT | `needs_next_numeric_model` | 增加 `lambda_d/lambda_q` LUT schema、插值和转矩测试 |
| 混合励磁 | `needs_next_numeric_model` | 增加 `psi_eff = psi_pm + kf * if` 和励磁损耗 |
| 绕组重构 | `needs_next_numeric_model` | 增加多配置 Ke/Kt/R/L 扫描和切换连续性 |
| 多相相组控制 | `needs_next_numeric_model` | 增加相组失效、均流、降额模型 |
| 加权效率 Pareto | `passed_architecture_verification` | 增加工况权重和可追溯评分 |

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
