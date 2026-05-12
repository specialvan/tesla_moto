# Codex 开发上下文 Handoff

## 1. 当前工作线

- 当前分支：`codex-review-line`
- 主要目标：把可控磁通量电机技术路线沉淀为可交接、可追踪、可继续开发的 Codex 知识库。
- 当前状态：EXP-001 到 EXP-010 已在当前 `codex-review-line` 分支落地，12 个方案在 `models/scheme_simulation_coverage.json` 中均为 `passed_numeric_simulation`。
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
| EXP-005 | SVPWM 过调制电压利用系数和谐波/损耗惩罚 |
| EXP-006 | 非线性 `lambda_d/lambda_q` LUT 插值与转矩 |
| EXP-007 | 混合励磁等效磁链和励磁损耗 |
| EXP-008 | 绕组重构配置参数集与切换连续性 |
| EXP-009 | 多相相组降额和失组工况 |
| EXP-010 | 加权效率 / Pareto 方案选择 |

## 4. 仍需工程化升级的方向

| 方向 | 当前覆盖状态 | 下一步 |
|---|---|---|
| SVPWM 过调制 | `passed_numeric_simulation` | 用 PWM 波形、器件损耗图和 EMI/纹波约束替换参数惩罚 |
| 非线性磁链 LUT | `passed_numeric_simulation` | 用 FEA / dyno `lambda_d/lambda_q` 图替换合成 LUT |
| 混合励磁 | `passed_numeric_simulation` | 增加励磁绕组 L/R、励磁电源损耗和热耦合 |
| 绕组重构 | `passed_numeric_simulation` | 增加切换瞬态、绝缘、循环电流和开关器件损耗 |
| 多相相组控制 | `passed_numeric_simulation` | 增加谐波子空间、开相电压矢量和逐相热模型 |
| 加权效率 Pareto | `passed_numeric_simulation` | 用工况能耗、成本、质量和安全风险替换 v0 权重 |

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
