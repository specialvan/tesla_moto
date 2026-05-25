# Opus Review 工程包

## 1. 包定位

`opus-review/` 是 Opus 4.7 (1M) 在 `claude-mainline` 之上对 **Codex 开发线** 当前进度的独立深度评审沉淀。

与既有评审包的关系：

| 包 | 视角 | 评审对象 |
|---|---|---|
| `claude-review/` | Claude 主线视角 | 处置 Codex 返回的评审意见 |
| `codex-review/` | Codex 视角 | 评审 Claude 主线开发 |
| `codex-docs/` | Codex 视角 | Codex 知识库 / handoff |
| **`opus-review/`** | **Opus 独立视角** | **评审 Codex 当前开发进度与交付物** |

本包不替代源码、`models/`、`experiments/`、`tests/` 或 `reports/`。它做四件事：

1. 沉淀 Opus 对 Codex 当前开发进度的事实核验；
2. 把发现拆成可执行的行动项与机器可读登记；
3. 跨分支记录 Codex 已落地但 Claude 主线尚未吸收的能力；
4. 守住 `engineering_validated=false`、`proxy/synthetic/research_pool` 与 r02/r03 成熟度边界，不被表象“看似闭环”模糊。

## 2. 文件入口

| 文件 | 用途 |
|---|---|
| `docs/2026-05-25/README.md` | 本日期评审包的入口索引 |
| `docs/2026-05-25/codex_progress_deep_review.md` | Codex 开发进度深度评审主报告 |
| `docs/2026-05-25/codex_progress_action_register.json` | 行动项机器可读登记表 |
| `docs/2026-05-25/codex_deliverable_inventory.md` | Codex 当前产物全量清单与跨分支映射 |
| `docs/2026-05-25/evidence_index.md` | 本轮评审读取/引用的证据路径索引 |
| `docs/2026-05-25/branch_integration_strategy.md` | `codex-review-line` 与 `claude-mainline` 集成策略 |

## 3. 维护规则

1. 评审包只增不覆盖，按日期目录追加；
2. 每条评审结论必须至少引用一个证据路径；
3. 不得把 r02 proxy / synthetic / research_pool / parameterized linear model 描述为 FEA / 台架 / HIL / 量产释放结论；
4. 不得把 60 A r02 soft gate 通过描述为 30 A r03 production target 通过；
5. 后续评审若发现旧结论失效，必须新增条目并显式标注 supersedes，不得静默修改历史结论。
