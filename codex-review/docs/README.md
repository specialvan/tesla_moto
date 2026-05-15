# Codex Review Docs 工程包

## 1. 包定位

`codex-review/docs` 是持续评审 Claude 开发内容的工程包。它只沉淀评审、证据索引、Git 状态、风险登记和后续行动项，不替代 Claude 主线源码、正式仿真产物、FEA、台架、热、EMC 或安全验证报告。

本包当前建立在 `codex-review-line` 工作区内，同时对照 `claude-mainline` 分支的最新提交和本地工作树状态。后续每轮评审都应追加新日期文件，保持可追踪、可复核、可回滚。

## 2. 当前入口

| 文件 | 用途 |
|---|---|
| `claude_development_review_2026-05-15.md` | 本轮 Claude 开发内容深度评审报告 |
| `evidence_index_2026-05-15.md` | 本轮读取的文档、wiki、HTML、Git、代码和测试证据索引 |
| `git_state_2026-05-15.md` | 当前评审线与 Claude 主线的 Git 状态、分叉和工作树风险 |
| `review_action_register_2026-05-15.json` | 机器可读评审发现、严重度、状态和建议动作 |

## 3. 本轮基线

| 项 | 当前观察 |
|---|---|
| 当前工作区 | `G:\tesla_moto-codex` |
| 当前分支 | `codex-review-line` |
| 当前 HEAD | `4e0c489 feat: 增加PyFluent高保真工作流入口` |
| 对照主线 | `claude-mainline` |
| 对照主线 HEAD | `391ce20 feat(exp011): 新增铁损模型和Bertotti三相铁损速度扫描实验` |
| 当前分支本地状态 | ahead origin 1，且有 8 个实验 summary 的路径差异 |
| Claude 主线本地状态 | `models/control_lut.json` 已修改，`.claude/` 未跟踪 |

## 4. 维护规则

1. 每次新增评审报告都必须同步更新本 README 的入口表。
2. 每条评审发现必须指向证据路径、Git 提交或可复核命令。
3. `passed_numeric_simulation` 只能解释为可复现数值或代理实验，不得写成工程验证。
4. 评审包只新增或更新评审文件，不顺手提交实验 summary、CSV 或本地 agent 目录。
5. 若评审依赖另一分支内容，必须记录分支名、HEAD、工作树状态和对照命令。
