# Codex 可控磁通量电机知识库

## 1. 目录定位

`codex-docs` 是当前 `codex-review-line` 分支的交接知识库，负责沉淀：

- 开发上下文和 handoff；
- wiki / HTML 原始知识库快照；
- 工程落地、BOM/EDA、驱动/协议/上电时序的证据链；
- 当前 EXP-001 到 EXP-004 仿真产物追踪；
- EXP-005 到 EXP-010 的后续建模方向和证据缺口。

本目录是知识库入口，不替代正式仿真代码、EDA 工程或台架验证报告。

## 2. 快速入口

| 文件 | 用途 |
|---|---|
| `handoff_context.md` | 给下一位 agent / 工程师的上下文交接 |
| `evidence_manifest.md` | 关键证据文件、哈希、来源和用途 |
| `simulation_traceability.md` | 12 类方案到当前仿真/待建模状态的追踪矩阵 |
| `wiki_html_evidence.md` | wiki 与 HTML 知识库快照说明 |
| `snapshots/wiki/controllable_flux_motor_research_plan.md` | wiki 原始快照 |
| `snapshots/html/controllable_flux_motor_kb.html` | HTML 知识库原始快照 |

## 3. 当前分支状态

- 当前分支：`codex-review-line`
- 覆盖目录：`models/scheme_simulation_coverage.json`
- 当前覆盖状态：6 个 `passed_numeric_simulation`，5 个 `needs_next_numeric_model`，1 个 `passed_architecture_verification`
- 当前落地实验：EXP-001、EXP-002、EXP-003、EXP-004
- 当前工程文档：`reports/` 下已有工程落地矩阵、驱动/上电/协议图、BOM/EDA、stage-gate 流程

## 4. 重要边界

当前分支证明的是：

- 已有 V1/V2 初步仿真闭环；
- 主线线性 dq、可变磁链、参数族扫描、热/退磁安全边界可复现；
- 每种方案均有工程落地或下一步数值模型记录；
- wiki/html 证据已快照留痕。

当前分支尚未证明：

- EXP-005 到 EXP-010 已在当前分支全部落地；
- 电机磁路已通过 FEA；
- 逆变器、驱动、BOM、EDA 已可直接投板；
- 热、EMC、绝缘、失效安全已完成车规验证；
- 当前方案排序可以作为最终设计决策。

## 5. 下一步知识库维护规则

1. 新增实验必须同步更新 `simulation_traceability.md` 和 `models/scheme_simulation_coverage.json`。
2. 新增 wiki/html 证据必须放到 `snapshots/` 并更新 `evidence_manifest.md` 的 SHA256。
3. 所有工程结论必须标注证据路径，避免只写结论。
4. `engineering_validated=false` 的结果不得表述为工程释放结论。
