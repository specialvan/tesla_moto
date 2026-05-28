# 2026-05-25 评审包

## 入口

| 文件 | 用途 |
|---|---|
| `codex_progress_deep_review.md` | Codex 当前开发进度的 Opus 4.7 深度评审主报告 |
| `codex_progress_deep_review_r02.md` | R02 逐行 / 逐字段补遗，复核 CDR/AMR 与 r02/r03 边界 |
| `codex_progress_deep_review_r03.md` | R03 逐字段深挖补遗，核验运行时合同、API/展示层成熟度与测试护栏 |
| `codex_progress_deep_review_r04.md` | R04 前后端/客户出口逐句深挖补遗，定位 ROI 公式漂移与复制出口成熟度缺口 |
| `codex_deliverable_inventory.md` | Codex 在 `codex-review-line` 与 `claude-mainline` 上的产物清单（含跨分支映射） |
| `codex_progress_action_register.json` | 评审发现 / 风险 / 行动项的机器可读登记 |
| `codex_progress_action_register_r04_followup.json` | R03/R04 整改后的追加 closure/open register；显式 supersedes，不改写旧结论 |
| `codex_progress_action_register_r05_followup.json` | R04 follow-up 后继续推进的追加 closure/open register；关闭商业措辞、cache path、prompt block anchor |
| `codex_progress_action_register_r06_followup.json` | R01/R02/R03 继续推进的追加 closure/open register；关闭 control LUT 污染、sim_binding schema/gate class、仓库卫生护栏 |
| `codex_progress_action_register_r07_followup.json` | 内容分组提交后的追加 closure/open register；关闭工作树卫生项并保留分支集成/PyFluent open 项 |
| `codex_progress_action_register_r08_followup.json` | PyFluent 主线迁移后的追加 closure/open register；关闭 dry-run、manifest、validation_chain 与 boundary allow-list 项 |
| `codex_progress_action_register_r09_followup.json` | 跨包 Markdown 链接体检后的追加 closure/open register；关闭链接校验项并迁入缺失的 2026-05-15 Codex 评审证据包 |
| `evidence_index.md` | 本轮评审读取或引用的证据路径索引 |
| `branch_integration_strategy.md` | `codex-review-line` 与 `claude-mainline` 集成、cherry-pick、回归策略 |

## 评审范围

- 分支：`codex-review-line` (origin/HEAD) 与 `claude-mainline` (本地 HEAD `d7abf6e`)
- Codex 关键贡献：PyFluent 工作流、`codex-docs/` 知识库、`codex-review/docs/*_2026-05-15.md` 评审包、r02 仿真锚点提示词批包（已扩散到当前分支但仍未跟踪）
- Claude 主线相关吸收物：12 方案 r02 `sim_binding-r02.json`、P0/P1 通用 acceptance harness、r03 提示词包、`tests/test_r03_prompt_maturity.py` 护栏

## 现场验证基线

- `python -m pytest tests/test_r03_prompt_maturity.py tests/test_scheme_p0_lut_acceptance.py tests/test_scheme_experiment_acceptance.py tests/test_scheme_simulation_coverage.py -q` → **42 passed in 235.85s**（运行时间 2026-05-25 当日）。
- 提交 `d7abf6e docs(v2): 同步r03提示词成熟度收敛状态` 为评审 HEAD。
