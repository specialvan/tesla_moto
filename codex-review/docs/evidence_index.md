# Codex 对 Claude 开发内容评审证据索引

评审日期：2026-05-14

## 1. Git 与工作树证据

| 证据 | 当前观察 | 评审用途 |
|---|---|---|
| `git status --short --branch` | `claude-mainline...origin/claude-mainline [ahead 4]` | 判断当前本地分支领先远端，评审结论对应未必已推送的本地状态 |
| `git status --short --branch` | `M claude-docs/maxwell_motorcad_simulation_plan.md` | 标记工具链方案文档存在未提交修改 |
| `git status --short --branch` | `M claude-docs/toolchain_selection_and_github_references.md` | 标记工具链引用文档存在未提交修改 |
| `git status --short --branch` | `?? .claude/` | 标记本地 agent 工作目录未跟踪，需防止误纳入长期知识库 |
| `git log --oneline -n 12 --decorate` | HEAD 为 `7b9887e feat(sim): 补齐EXP-006非线性磁链LUT实验` | 确认当前评审覆盖到 EXP-006 最近补齐后的主线 |
| `git log --oneline -n 12 --decorate` | 近四个本地提交补齐 EXP-005/007/008/009/010、测试、coverage 和 EXP-006 | 确认文档滞后不是单纯误读，而是代码/coverage 已推进后文档未完全同步 |

## 2. Claude 过程文档证据

| 路径 | 当前用途 | 关键观察 |
|---|---|---|
| `claude-docs/README.md` | Claude 知识库入口 | 仍写 EXP-005、EXP-007 到 EXP-010 不属于 Claude 主线已完成工程闭环，与当前 coverage/experiments 不一致 |
| `claude-docs/handoff_context.md` | 接手上下文 | 仍写当前状态为 EXP-001 到 EXP-004 与 EXP-006，漏掉 EXP-005/007/008/009/010 |
| `claude-docs/evidence_manifest.md` | 证据 manifest | 仿真实验证据表只列 EXP-001 到 EXP-004，未纳入 EXP-005 到 EXP-010 与 EXP-006 最新产物 |
| `claude-docs/simulation_traceability.md` | 仿真追踪矩阵 | 方案映射已显示 EXP-005 到 EXP-010 为 `passed_numeric_simulation`，但“下一批最小实验包”仍像待落地清单 |
| `claude-docs/wiki_html_evidence.md` | wiki/html 快照说明 | 仍描述 HTML 已同步 EXP-003 结论，未覆盖 EXP-005 到 EXP-010 和 EXP-006 LUT 最新状态 |
| `claude-docs/toolchain_selection_and_github_references.md` | 高保真仿真工具链 | 当前未提交修改增加 PyFluent/Fluent 说明，评审中视为本地未冻结状态 |
| `claude-docs/maxwell_motorcad_simulation_plan.md` | Maxwell/Motor-CAD 落地方案 | 当前未提交修改补充 Fluent/Icepak 热流固复核口径，需提交前复核一致性 |

## 3. Wiki / HTML 证据

| 路径 | 当前观察 | 评审用途 |
|---|---|---|
| `wiki/controllable_flux_motor_research_plan.md` | 仍有早期 EXP-01 到 EXP-08/09 研发矩阵与状态标记说明 | 需要重新对齐当前 EXP-001 到 EXP-010 实际编号和结果路径 |
| `controllable_flux_motor_kb.html` | 可视化实验矩阵只展示 EXP-01 到 EXP-07，且 EXP-07 写为工况加权效率 | 与当前实验编号不一致：工况加权 Pareto 实际为 EXP-010 |
| `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | 冻结快照 | 如果活动 wiki 更新，必须同步刷新快照和 manifest |
| `claude-docs/snapshots/html/controllable_flux_motor_kb.html` | 冻结快照 | 如果活动 HTML 更新，必须同步刷新快照和 manifest |

## 4. 实验与模型事实源

| 路径 | 当前观察 | 评审用途 |
|---|---|---|
| `models/scheme_simulation_coverage.json` | version `2026-05-14-v1`，12 个方案均为 `passed_numeric_simulation` | 当前最高优先级事实源之一 |
| `experiments/exp_005_modulation_factor/summary.json` | `engineering_validated=false`，参数化过调制/谐波/损耗模型 | 证明 EXP-005 已有数值代理，但不是工程验证 |
| `experiments/exp_006_nonlinear_flux_lut/summary.json` | synthetic LUT，插值和非线性转矩验证，未接入电压约束控制搜索 | 证明 EXP-006 已落地 synthetic 数值证明，但 FEA/控制闭环仍缺 |
| `experiments/exp_007_hybrid_excitation/summary.json` | 等效 `psi_eff = psi_pm + kf*if`，无励磁动态/热耦合 | 证明 EXP-007 已有稳态代理模型 |
| `experiments/exp_008_winding_reconfiguration/summary.json` | 参数化绕组配置，切换连续性只做代理检查 | 证明 EXP-008 已有数值入口但暂态/硬件未验证 |
| `experiments/exp_009_multiphase_phase_group/summary.json` | 聚合电流降额，无谐波子空间/相级热模型 | 证明 EXP-009 已有故障降额代理模型 |
| `experiments/exp_010_weighted_efficiency_pareto/summary.json` | 说明性 drive cycle + 铜耗评分，不含铁耗/机械/逆变损耗 | 证明 EXP-010 已有 Pareto 代理排序但不能作为设计结论 |
| `models/flux_lut_schema.json` | 非线性 LUT schema | EXP-006 新增数据结构证据 |
| `models/flux_lut_sample.json` | synthetic LUT 样例 | EXP-006 样例证据 |

## 5. 测试与覆盖证据

| 路径 | 当前观察 | 评审用途 |
|---|---|---|
| `tests/` | 当前存在 20 个 `test_*.py` | 覆盖 EXP-001 到 EXP-010 的多数新入口 |
| `tests/test_scheme_simulation_coverage.py` | 检查每个 scheme 有 coverage、artifact 存在、6 个主线 scheme 为 numeric | 未检查 `pytest_tests` 路径是否真实存在，也未强制当前 12 项均为 numeric |
| `models/scheme_simulation_coverage.json` | `mtpa_fw_mtpv_control` 引用 `tests/test_control_search.py` | 当前 `tests/test_control_search.py` 不存在，是 coverage 证据链断点 |
| `tests/test_nonlinear_flux_lut.py` | 覆盖 EXP-006 LUT schema、边界和插值 | 支撑 EXP-006 数值证明成立 |

## 6. 工程报告证据

| 路径 | 当前用途 | 评审关注 |
|---|---|---|
| `reports/scheme_engineering_landing_matrix.md` | 12 个方案工程落地矩阵 | 需要与最新 EXP 状态同步引用 |
| `reports/scheme_driver_power_protocol_diagrams.md` | 驱动、上电、协议图 | 需要保留为架构证据，不应写成投板验证 |
| `reports/scheme_bom_eda_integration_design.md` | BOM / EDA 集成设计 | 需要保留 `v0_architecture` 或规划口径 |
| `reports/scheme_industry_design_stage_gate_process.md` | 行业 stage-gate 流程 | 可作为后续评审门槛来源 |
