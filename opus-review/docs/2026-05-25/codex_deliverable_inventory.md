# Codex 当前产物清单

评审日期：2026-05-25  
范围：Codex 在 `codex-review-line` 与对 `claude-mainline` 工作树有影响的全部产物。  
评审基线：`claude-mainline` HEAD `d7abf6e`、`codex-review-line` HEAD `6b137bf`。

---

## A. `codex-review-line` 独有产物（17 个 unique 提交）

### A.1 代码 (`sim/` + `tests/`)

| 提交 | 文件 | 行数 | Opus 评级 |
|---|---|---|---|
| `4e0c489` | `sim/pyfluent_workflow.py` | 159 | 高质量；frozen dataclass + Protocol + 懒加载；建议 cherry-pick |
| `4e0c489` | `sim/run_pyfluent_workflow.py` | 80 | 单一入口 CLI，支持 JSON config；建议补 `--dry-run` |
| `4e0c489` | `tests/test_pyfluent_workflow.py` | 99 | 模式正向（`tmp_path` + FakeAdapter） |
| `4e0c489` | `tests/test_run_pyfluent_workflow.py` | 44 | 验证 CLI / load_config |

### A.2 知识库 (`codex-docs/`)

| 提交 | 文件 | 用途 |
|---|---|---|
| `14462e9` | `codex-docs/README.md` | Codex 知识库入口 |
| `14462e9` | `codex-docs/evidence_manifest.md` | 证据 manifest |
| `14462e9` | `codex-docs/handoff_context.md` | handoff |
| `14462e9` | `codex-docs/simulation_traceability.md` | 12 方案到仿真状态追踪矩阵 |
| `14462e9` | `codex-docs/wiki_html_evidence.md` | wiki/HTML 证据说明 |
| `14462e9` | `codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | wiki 快照 |
| `14462e9` | `codex-docs/snapshots/html/controllable_flux_motor_kb.html` | HTML 快照 |
| `90d2a66` | 上述五份 | 闭环状态修正 |
| `cfda256` | `codex-docs/toolchain_selection_and_github_references.md` | Maxwell / Motor-CAD / Simulink / Pyleecan / motulator 选型 |

### A.3 评审报告 (`codex-review/docs/*_2026-05-15.md`)

| 提交 | 文件 | 类别 | Opus 评级 |
|---|---|---|---|
| `69b40b4` | `claude_development_review_2026-05-15.md` | 10 条 CDR 深度评审 | 高 |
| `69b40b4` | `evidence_index_2026-05-15.md` | 证据路径索引 | 中 |
| `69b40b4` | `git_state_2026-05-15.md` | git 分支状态 | 中 |
| `69b40b4` | `review_action_register_2026-05-15.json` | 机器可读行动登记 | 高 |
| `dd47e70` | `artifact_mutation_review_2026-05-15.md` | 4 条 AMR | 高 |
| `dd47e70` | `artifact_mutation_matrix_2026-05-15.json` | 机器可读测试污染矩阵 | 高 |
| `6b137bf` | `goal_traceability_audit_2026-05-15.md` | 评审目标到产物覆盖审计 | 高 |
| `6b137bf` | `goal_traceability_checklist_2026-05-15.json` | 机器可读 checklist | 中 |

### A.4 Codex 早期沉淀

| 提交 | 文件 | 用途 |
|---|---|---|
| `951657a` | `codex-reviwe/controllable_flux_motor_deep_review.md` | 早期 V1 深度评审（首版） |
| `951657a` | `codex-reviwe/controllable_flux_motor_scheme_dissection.md` | 12 方案逐项拆解 |
| `951657a` | `codex-reviwe/phase1_linear_dq_implementation_plan.md` | phase1 实施计划（已被主线 e7edde3 / a8169fb 覆盖） |
| `951657a` | `codex-reviwe/v1_simulation_review_and_v2_plan.md` | V2 路线建议 |
| `951657a` | `experiments/exp_001_linear_dq/run.py` | EXP-001 入口（已被主线 `sim/run_linear_dq_experiment.py` 覆盖） |
| `951657a` | `sim/control_search.py` | 控制搜索（已被主线 `sim/search.py` 重做） |
| `951657a` | `tests/test_control_search.py` | 已被主线测试集替换 |
| `e16af86` | `codex-reviwe/v2_numeric_simulation_closure.md` | V2 数值闭环复核 |

Opus 建议：`codex-reviwe/` 拼写错误，目录应统一改为 `codex-review/`。`d2be095..27bfe15..b3afc6f..21fc948..37de045..8f3312d` 这一连串实验快照 chore 提交可在主线侧考虑 squash 或直接丢弃（主线 r02/r03 已重做覆盖矩阵）。

---

## B. 当前工作树 untracked / modified（Codex 影响主线但未跟踪）

| 路径 | 状态 | 起源 | 建议动作 |
|---|---|---|---|
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/` | untracked | Codex 提示词批包 | 本次提交 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/README.md` | untracked | 同上 | 同上 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/_simulation_globals.md` | untracked | 全局 SIM ANCHOR 规则 | 同上 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/simulation_anchor_matrix.json` | untracked | 12 方案机器可读锚点矩阵 | 同上 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/scheme-02-r02-sim.md` | untracked | S02 增量提示词 | 同上 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/scheme-04-r02-sim.md` | untracked | S04 增量提示词 | 同上 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S02-PROMPT-r02-simulation_anchor_pack.md` | untracked | S02 r02 sim prompt pack | 同上 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S04-PROMPT-r02-simulation_anchor_pack.md` | untracked | S04 r02 sim prompt pack | 同上 |
| `codex-review/docs/v2_r02_sim_image_generation_handoff_2026-05-20.md` | untracked | r02-sim 改图 handoff | 同上 |
| `codex-review/docs/README.md` | modified | 新增两项入口 | 同上 |
| `codex-docs/wereview.md` | untracked | 内容未审 / 疑空 | 删除或合入 handoff |
| `review-pr/新能源汽车驱动电机系列（）——驱动电机发展趋势（扁线、油冷、多合一）.html` | untracked | 外部资料 | `.gitignore` 或迁出 |
| `review-pr/新能源汽车驱动电机系列（）——驱动电机发展趋势（扁线、油冷、多合一）_files/` | untracked | 外部资料资源 | 同上 |
| `review-pr/这是奇瑞公司的可变磁通电机，技术思路非常巧妙.html` | untracked | 外部资料 | 同上 |
| `review-pr/这是奇瑞公司的可变磁通电机，技术思路非常巧妙_files/` | untracked | 外部资料资源 | 同上 |
| `.claude/worktrees/` | untracked | 14 个 agent worktree 缓存 | `.gitignore` |

---

## C. Codex 反馈已被 `claude-mainline` 吸收的产物

### C.1 P0 通用 acceptance harness

| 文件 | 起源 | 状态 |
|---|---|---|
| `tests/test_scheme_p0_lut_acceptance.py` | 主线 `1e26568` / `02fadda` / `a0fd057` 系列 | 12 方案 r02 binding → 仿真闭环；strong/soft check + DVP id 校验 |
| `tests/test_scheme_experiment_acceptance.py` | 主线同上 | 8 个 P1/P2 方案的 suffix DSL 通用 harness |
| `tests/test_r03_prompt_maturity.py` | 主线 `e06c1fe` | 48 条 r03 prompt × `engineering_validated=false`/`evidence_gap` 护栏 |
| `tests/test_scheme_simulation_coverage.py` | 主线 baseline | 12 方案 coverage 一致性 |

### C.2 r02 仿真合同（12 份）

| 方案 | 仿真合同 | 模型成熟度 | runner |
|---|---|---|---|
| S01 | `engineering/v2/scheme-01/parameters/V2-S01-PARAM-sim_binding-r02.json` | parameterized_linear_model | `sim.run_control_lut_generator.run` |
| S02 | `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json` | parameterized_linear_model | 同上 |
| S03 | `engineering/v2/scheme-03/parameters/V2-S03-PARAM-sim_binding-r02.json` | proxy_model | `sim.run_modulation_factor_experiment.run` |
| S04 | `engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json` | synthetic_fixture | `sim.run_control_lut_generator.run` (nonlinear) |
| S05 | `engineering/v2/scheme-05/parameters/V2-S05-PARAM-sim_binding-r02.json` | proxy_model | `sim.run_param_sweep_experiment.run` |
| S06 | `engineering/v2/scheme-06/parameters/V2-S06-PARAM-sim_binding-r02.json` | proxy_model | 同上 |
| S07 | `engineering/v2/scheme-07/parameters/V2-S07-PARAM-sim_binding-r02.json` | research_pool_proxy | `sim.run_variable_flux_experiment.run` |
| S08 | `engineering/v2/scheme-08/parameters/V2-S08-PARAM-sim_binding-r02.json` | research_pool_proxy | `sim.run_hybrid_excitation_experiment.run` |
| S09 | `engineering/v2/scheme-09/parameters/V2-S09-PARAM-sim_binding-r02.json` | research_pool_proxy | `sim.run_winding_reconfiguration_experiment.run` |
| S10 | `engineering/v2/scheme-10/parameters/V2-S10-PARAM-sim_binding-r02.json` | research_pool_proxy | `sim.run_multiphase_phase_group_experiment.run` |
| S11 | `engineering/v2/scheme-11/parameters/V2-S11-PARAM-sim_binding-r02.json` | parameterized_linear_model | `sim.run_control_lut_generator.run` (温度 120 °C) |
| S12 | `engineering/v2/scheme-12/parameters/V2-S12-PARAM-sim_binding-r02.json` | proxy_model | `sim.run_weighted_efficiency_pareto_experiment.run` |

### C.3 r03 提示词包（12 份）

`engineering/v2/scheme-*/prompts/V2-S*-PROMPT-r03-production_drawing_pack.md`

每包 4 条 prompt（PCB / CAD / state machine / traceability），全部满足：

- `engineering_validated = false`
- `evidence_gap`
- `proxy` 或 `synthetic fixture` 或 `sample-only`
- 不含 `fea-backed validation` / `engineering recommendation` / `production release approved` 等 9 个超成熟度短语
- 由 `tests/test_r03_prompt_maturity.py` 守门

### C.4 配套 Claude 评审

| 文件 | 用途 |
|---|---|
| `claude-review/docs/2026-05-20/v2_r03_prompt_parameter_sim_deep_review.md` | r03 提示词与 r02 仿真合同一致性深度自查 |
| `claude-review/docs/2026-05-20/v2_scheme_drawing_parameter_prompt_handoff.md` | 提示词参数化 handoff |
| `claude-review/docs/2026-05-20/v2_high_speed_back_emf_pending_scheme_deep_dive.md/.html` | 高速反电动势待定方案深度暂存 |
| `claude-review/docs/2026-05-19/v2_automation_handoff.md` | V2 成熟度审查自动化 handoff |
| `claude-review/docs/2026-05-19/v2_claude_code_automation_notes.md` | 自动化技能注释 |
| `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md/.html` | r00 96 张图深度评审 |
| `claude-review/docs/2026-05-18/v2_image_pack_r02_production_roadmap.md` | r02 生产化路线图 |
| `claude-review/docs/2026-05-15/v0.5_true_production_drawing_deliverables_matrix.md/.html` | 真生产图纸五档交付物矩阵 |
| `claude-review/docs/2026-05-15/v0.6_research_pool_production_drawing_prompt_closure.md` | 研究池方案 r03 草案闭环 |

---

## D. 跨分支差异总览

```text
                       claude-mainline           codex-review-line
                       ───────────────           ─────────────────
EXP-001..004 baseline     present                  present
EXP-005..010 数值入口      重新实现 (e52c3b4..1e26568..02fadda) 旧版 d2be095 已被覆盖
EXP-006 nonlinear LUT phase-2 present              缺失（评审线未引入主线 5b0995c）
EXP-011 铁损 Bertotti      present (391ce20)        缺失
控制 LUT 生成器             present (e7edde3 + a8169fb) 缺失
r02 仿真合同 (12 份)        present                  缺失
r03 prompt pack (12 份)    present                  缺失
P0 通用 harness             present                  缺失
test_r03_prompt_maturity   present                  缺失
PyFluent 工作流             **缺失**                 present (4e0c489) ← 必须 cherry-pick
codex-docs/                **缺失**                 present (14462e9 + 90d2a66 + cfda256)
codex-review/2026-05-15 评审包 **缺失**              present (69b40b4 + dd47e70 + 6b137bf)
codex-review r02 sim 批包    untracked              **缺失**（评审线没有该批包）
```

> 关键观察：当前评审线（`codex-review-line`）的 `codex-review/docs/` 不包含 r02 sim 批包 —— 该批包仅以 untracked 形态存在于 `claude-mainline` 工作树上。这进一步证明需要把 Codex 已经写出来的批包先 commit 到 `claude-mainline`，再决定是否合回评审线。
