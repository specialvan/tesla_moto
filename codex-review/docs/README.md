# Codex Review Docs 工程包

## 1. 包定位

`codex-review/docs` 用于持续沉淀 Codex 对 Claude 开发内容的深度评审，评审对象包括：

- `claude-docs/` 过程文档、handoff、证据 manifest、仿真追踪矩阵和工具链方案；
- `wiki/controllable_flux_motor_research_plan.md` 研发过程 wiki；
- `controllable_flux_motor_kb.html` HTML 可视化知识库；
- `models/`、`experiments/`、`sim/`、`tests/` 中的可复现实验事实源；
- `reports/` 工程落地、BOM/EDA、驱动/协议/阶段门报告；
- git 分支、提交、未提交改动和本地工作树风险。

本包只做评审、事实核验、风险登记和后续行动追踪，不替代 Claude 主线源码、实验产物、正式 FEA 结果或台架验证报告。

## 2. 当前文件入口

| 文件 | 用途 |
|---|---|
| `claude_development_deep_review_2026-05-14.md` | 首轮 Claude 开发内容深度评审报告 |
| `documentation_sync_matrix_2026-05-14.md` | 下一轮文档状态修复的文件级同步矩阵 |
| `evidence_index.md` | 本轮评审读取和引用的证据路径索引 |
| `landing_progress_log_2026-05-14.md` | 方案落地推进日志，记录已完成 P0 证据链修复 |
| `review_action_register.json` | 机器可读的评审发现、风险等级和行动项 |
| `scheme_landing_roadmap_2026-05-14.md` | 12 个方案的分层落地路线图、阶段门和下一步工作包 |
| `scheme_landing_work_packages_2026-05-14.json` | 机器可读的方案落地工作包登记 |
| `working_tree_delta_note_2026-05-14.md` | 首轮评审落盘后观察到的额外工作树变化补充记录 |
| `claude_development_review_2026-05-15.md` | Codex 对 Claude 主线开发进度的 10 条 CDR 深度评审，作为 Opus 2026-05-25 复审证据源 |
| `review_action_register_2026-05-15.json` | 2026-05-15 CDR 机器可读行动登记 |
| `artifact_mutation_review_2026-05-15.md` | artifact mutation 风险复审，覆盖 control LUT 污染、生成时间与工作树卫生风险 |
| `artifact_mutation_matrix_2026-05-15.json` | artifact mutation 风险矩阵的机器可读版本 |
| `goal_traceability_audit_2026-05-15.md` | Codex 对目标链路、证据链与落地缺口的追踪审计 |
| `goal_traceability_checklist_2026-05-15.json` | goal traceability checklist 的机器可读版本 |
| `evidence_index_2026-05-15.md` | 2026-05-15 CDR/AMR 评审读取与引用的证据索引 |
| `git_state_2026-05-15.md` | 2026-05-15 评审时的 git 状态记录 |
| `claude_image_to_production_deep_review_2026-05-19.md` | Claude 图档生产化深度评审与打回意见，核对生图评审、r01 提示词、r02 参数化和真实图纸缺口 |
| `image_to_production_action_register_2026-05-19.json` | 图档生产化打回项的机器可读行动登记 |
| `scheme_drawing_prompts_r02_simulation_batch/` | 面向下一轮仿真的 r02 图档提示词升级包，新增 SIM ANCHOR、maturity、sim_binding、pytest gate 和 next simulation step |
| `v2_r02_sim_image_generation_handoff_2026-05-20.md` | 等待生图服务器确认后的 S02/S04 首批 r02-sim 改图开跑 handoff，含 smoke、dry-run、改图命令和验收清单 |
| `../../claude-review/docs/2026-05-15/v0.5_true_production_drawing_deliverables_matrix.md` | Claude 按打回意见补充的真实生产图纸五档交付物矩阵 |

## 3. 首轮评审结论摘要

当前 Claude 主线在最近提交中已经补齐 EXP-005、EXP-006、EXP-007、EXP-008、EXP-009、EXP-010 的可重跑 Python 数值入口、测试或实验产物，并把 `models/scheme_simulation_coverage.json` 提升到 12 个方案均为 `passed_numeric_simulation`。

但文档层存在明显滞后和口径分裂：

- `claude-docs/README.md` 和 `claude-docs/handoff_context.md` 仍把 Claude 主线描述为只落地 EXP-001 到 EXP-004 与 EXP-006；
- `claude-docs/evidence_manifest.md` 只索引 EXP-001 到 EXP-004，未纳入 EXP-005 到 EXP-010 与 EXP-006 的完整产物；
- `wiki/controllable_flux_motor_research_plan.md` 和 `controllable_flux_motor_kb.html` 仍保留早期实验编号和路线矩阵，未同步当前 EXP-005 到 EXP-010 的实际实现状态；
- `codex-docs/` 与 `claude-docs/` 也出现状态差异，尤其 `nonlinear_flux_lut` 在 `codex-docs` 中仍写为唯一缺位，但当前 `models/scheme_simulation_coverage.json` 已标记为 `passed_numeric_simulation`；
- git 工作树显示 `claude-docs/maxwell_motorcad_simulation_plan.md` 和 `claude-docs/toolchain_selection_and_github_references.md` 有未提交修改，且 `.claude/` 为未跟踪目录。

## 4. 评审维护规则

1. 每次新增评审报告必须在本 README 的入口表中登记。
2. 每条评审结论必须至少引用一个证据路径。
3. 对 `passed_numeric_simulation` 的描述必须同时保留 `engineering_validated=false` 或同等工程限制口径。
4. 不能把参数化代理模型、synthetic LUT、说明性 drive cycle 或简化退磁边界写成工程验证结论。
5. 如果 Claude 主线继续推进实验，必须同步评审 `claude-docs/`、`codex-docs/`、wiki、HTML、coverage JSON 和 git 状态是否一致。
