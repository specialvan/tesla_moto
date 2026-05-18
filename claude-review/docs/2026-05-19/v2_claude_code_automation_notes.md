# V2 Claude Code 自动化落地说明

日期：2026-05-19

## 本轮选择

用户要求“跳过第一步，继续深入推进”，因此本轮未配置 PreToolUse/PostToolUse Hook，优先落地只读/审查型自动化：

1. 项目技能：沉淀可复用审查流程。
2. 项目子代理：支持后续并行复核成熟度和 schema/test 契约。
3. handoff 文档：方便后续 agent 直接接续优化。

## 已新增项目技能

| 技能 | 路径 | 用途 |
|---|---|---|
| `v2-maturity-review` | `.claude/skills/v2-maturity-review/SKILL.md` | 检查 V2 成熟度口径、生产图纸边界、S02/S04 特例、图像外部上传限制 |
| `evidence-sync` | `.claude/skills/evidence-sync/SKILL.md` | 检查 `claude-review/docs`、wiki、HTML、evidence manifest、Codex README、scheme README 是否同步 |

## 已新增项目子代理

| 子代理 | 路径 | 用途 |
|---|---|---|
| `maturity-consistency-reviewer` | `.claude/agents/maturity-consistency-reviewer.md` | 并行审查文档和模型矩阵中的过度生产化声明 |
| `schema-test-contract-reviewer` | `.claude/agents/schema-test-contract-reviewer.md` | 审查 JSON schema、fixture、生成输出和 pytest 契约漂移 |

## 推荐使用时机

- 修改 `engineering/v2/**`、`claude-review/docs/**`、`codex-review/docs/**` 后：运行成熟度一致性审查。
- 修改 `models/*.json`、`models/*schema*.json`、`sim/**/*.py`、`tests/**/*.py` 后：运行 schema/test 契约审查。
- 新增评审文档或证据包后：运行 evidence-sync 流程检查同步遗漏。

## 仍未落地的自动化

Hook 暂未配置。若后续要继续自动化，优先级建议：

1. 阻止 `git add -A`、`.claude/worktrees/**`、`review-pr/**`、`gpt-image-2/outputs/**` 误提交。
2. 提交前扫描 `sk-`、真实 endpoint、`.env`、`model.local.json`。
3. Python 或 JSON 契约变更后提示运行目标 pytest。

## 交接入口

详见：`claude-review/docs/2026-05-19/v2_automation_handoff.md`
