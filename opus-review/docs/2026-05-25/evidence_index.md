# 证据索引

评审日期：2026-05-25  
用途：登记本轮 Opus 评审实际读取或引用的证据路径，确保结论可追溯。

## A. Git 引用

| 引用 | 用途 |
|---|---|
| `claude-mainline` HEAD `d7abf6e docs(v2): 同步r03提示词成熟度收敛状态` | 评审 HEAD |
| `codex-review-line` HEAD `6b137bf docs: 增加Claude评审目标覆盖审计` | 对照分支 HEAD |
| 共同祖先 `6f0ae80 feat: 建立Claude主线可控磁通量电机仿真闭环` | 分叉起点 |
| `git diff codex-review-line..claude-mainline` | 跨分支差异确认 |
| `git status --short --branch` | 工作树健康度 |

## B. Codex 评审 / 知识库（在 `codex-review-line`）

| 文件 | 在 Opus 报告中的引用位置 |
|---|---|
| `codex-review/docs/claude_development_review_2026-05-15.md` | §5.1 CDR 复审 |
| `codex-review/docs/artifact_mutation_review_2026-05-15.md` | §5.2 AMR 复审、§7 工作树健康 |
| `codex-review/docs/goal_traceability_audit_2026-05-15.md` | §5.3 评审目标审计 |
| `codex-review/docs/evidence_index_2026-05-15.md` | §3.1 交付盘点 |
| `codex-review/docs/git_state_2026-05-15.md` | §6 跨分支差异 |
| `codex-review/docs/review_action_register_2026-05-15.json` | §10 优先行动汇总 |
| `codex-review/docs/artifact_mutation_matrix_2026-05-15.json` | §5.2 AMR 复审 |
| `codex-review/docs/goal_traceability_checklist_2026-05-15.json` | §5.3 |
| `codex-docs/README.md` | §3.1 |
| `codex-docs/toolchain_selection_and_github_references.md` | §3.1、§5.4 |
| `codex-docs/handoff_context.md` | §3.1 |
| `codex-docs/evidence_manifest.md` | §3.1 |
| `codex-docs/simulation_traceability.md` | §3.1 |
| `codex-docs/wiki_html_evidence.md` | §3.1 |
| `codex-docs/snapshots/html/controllable_flux_motor_kb.html` | §3.1 |
| `codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | §3.1 |

## C. Codex PyFluent 工作流（`codex-review-line` 独有）

| 文件 | 引用位置 |
|---|---|
| `sim/pyfluent_workflow.py` | §4.1 设计、§4.2 风险 OPUS-2026-05-25-001/002/004 |
| `sim/run_pyfluent_workflow.py` | §4.2 风险 OPUS-2026-05-25-003 |
| `tests/test_pyfluent_workflow.py` | §4.1 测试隔离正向 |
| `tests/test_run_pyfluent_workflow.py` | §4.1 |

## D. Claude 主线 r02 仿真合同（12 份）

| 文件 |
|---|
| `engineering/v2/scheme-01/parameters/V2-S01-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-03/parameters/V2-S03-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-05/parameters/V2-S05-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-06/parameters/V2-S06-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-07/parameters/V2-S07-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-08/parameters/V2-S08-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-09/parameters/V2-S09-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-10/parameters/V2-S10-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-11/parameters/V2-S11-PARAM-sim_binding-r02.json` |
| `engineering/v2/scheme-12/parameters/V2-S12-PARAM-sim_binding-r02.json` |

引用位置：§3.3、§8.2。

## E. Claude 主线 r03 prompt packs（12 份）

| 文件 |
|---|
| `engineering/v2/scheme-01/prompts/V2-S01-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-02/prompts/V2-S02-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-03/prompts/V2-S03-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-04/prompts/V2-S04-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-05/prompts/V2-S05-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-06/prompts/V2-S06-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-07/prompts/V2-S07-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-08/prompts/V2-S08-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-09/prompts/V2-S09-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-10/prompts/V2-S10-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-11/prompts/V2-S11-PROMPT-r03-production_drawing_pack.md` |
| `engineering/v2/scheme-12/prompts/V2-S12-PROMPT-r03-production_drawing_pack.md` |

引用位置：§3.3、§8.1。S02 抽样使用第 14-27 行，S04 / S11 / S01 / S03 / S12 整文件读取。

## F. Claude 主线测试 / 代码

| 文件 | 引用位置 |
|---|---|
| `tests/test_r03_prompt_maturity.py` | §8.1、§9 OPUS-2026-05-25-007 |
| `tests/test_scheme_p0_lut_acceptance.py` | §8.2、§9 OPUS-2026-05-25-005/006 |
| `tests/test_scheme_experiment_acceptance.py` | §8.3 |
| `tests/test_scheme_simulation_coverage.py` | §8 现场验证 |
| `sim/run_control_lut_generator.py` | §7 AMR 复核、§9 OPUS-2026-05-25-013 |
| `models/scheme_simulation_coverage.json` | §3.3、§9 OPUS-2026-05-25-005 |
| `engineering/v2/scheme-02/parameters/V2-S02-PARAM-control-r02.md` | §8.2 抽查、S02 60 A vs 30 A 边界证据 |

## G. Codex 提示词批包（当前工作树 untracked）

| 文件 | 引用位置 |
|---|---|
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/README.md` | §3.2 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/_simulation_globals.md` | §3.2 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/simulation_anchor_matrix.json` | §3.2、§9 OPUS-2026-05-25-008 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/scheme-02-r02-sim.md` | §3.2 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/scheme-04-r02-sim.md` | §3.2 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S02-PROMPT-r02-simulation_anchor_pack.md` | §3.2 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S04-PROMPT-r02-simulation_anchor_pack.md` | §3.2 |
| `codex-review/docs/v2_r02_sim_image_generation_handoff_2026-05-20.md` | §3.2 |

## H. Claude 配套评审

| 文件 | 引用位置 |
|---|---|
| `claude-review/docs/2026-05-20/v2_r03_prompt_parameter_sim_deep_review.md` | §3.3 |
| `claude-review/docs/2026-05-20/v2_scheme_drawing_parameter_prompt_handoff.md` | §3.3 |
| `claude-review/docs/2026-05-20/v2_high_speed_back_emf_pending_scheme_deep_dive.md` | §3.3 |

## I. 现场验证记录

| 命令 | 输出 |
|---|---|
| `python -m pytest tests/test_r03_prompt_maturity.py tests/test_scheme_p0_lut_acceptance.py tests/test_scheme_experiment_acceptance.py tests/test_scheme_simulation_coverage.py -q` | `42 passed in 235.85s` |
| `git status` | 5 项 untracked + 1 项 modified（详见 §7） |
| `git log --oneline codex-review-line ^claude-mainline` | 17 行（evidence for §6） |
| `git log --oneline claude-mainline ^codex-review-line` | 30 行（evidence for §6） |
