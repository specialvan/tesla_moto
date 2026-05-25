# 2026-05-25 评审包

## 入口

| 文件 | 用途 |
|---|---|
| `codex_progress_deep_review.md` | Codex 当前开发进度的 Opus 4.7 深度评审主报告 |
| `codex_deliverable_inventory.md` | Codex 在 `codex-review-line` 与 `claude-mainline` 上的产物清单（含跨分支映射） |
| `codex_progress_action_register.json` | 评审发现 / 风险 / 行动项的机器可读登记 |
| `evidence_index.md` | 本轮评审读取或引用的证据路径索引 |
| `branch_integration_strategy.md` | `codex-review-line` 与 `claude-mainline` 集成、cherry-pick、回归策略 |

## 评审范围

- 分支：`codex-review-line` (origin/HEAD) 与 `claude-mainline` (本地 HEAD `d7abf6e`)
- Codex 关键贡献：PyFluent 工作流、`codex-docs/` 知识库、`codex-review/docs/*_2026-05-15.md` 评审包、r02 仿真锚点提示词批包（已扩散到当前分支但仍未跟踪）
- Claude 主线相关吸收物：12 方案 r02 `sim_binding-r02.json`、P0/P1 通用 acceptance harness、r03 提示词包、`tests/test_r03_prompt_maturity.py` 护栏

## 现场验证基线

- `python -m pytest tests/test_r03_prompt_maturity.py tests/test_scheme_p0_lut_acceptance.py tests/test_scheme_experiment_acceptance.py tests/test_scheme_simulation_coverage.py -q` → **42 passed in 235.85s**（运行时间 2026-05-25 当日）。
- 提交 `d7abf6e docs(v2): 同步r03提示词成熟度收敛状态` 为评审 HEAD。
