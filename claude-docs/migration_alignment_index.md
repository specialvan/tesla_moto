# Claude 文档迁移与 Codex 对齐索引

## 1. 对齐目标

本文件用于确认 Claude 主线产生的知识库、wiki、HTML、上下文 handoff、仿真方案和关键证据已经像 `codex-docs` 一样迁移到 `claude-docs`。

## 2. Claude-docs 当前文件清单

| Claude 文档 | 状态 | 对齐用途 |
|---|---|---|
| `claude-docs/README.md` | 已落地 | 知识库入口 |
| `claude-docs/handoff_context.md` | 已落地 | 上下文交接 |
| `claude-docs/evidence_manifest.md` | 已落地 | 证据清单 |
| `claude-docs/simulation_traceability.md` | 已落地 | 仿真追踪矩阵 |
| `claude-docs/wiki_html_evidence.md` | 已落地 | wiki/html 快照说明 |
| `claude-docs/toolchain_selection_and_github_references.md` | 已落地 | 高保真仿真工具链和 GitHub 参考项目 |
| `claude-docs/maxwell_motorcad_simulation_plan.md` | 已落地 | Maxwell / Motor-CAD / 开源链路详细落地方案 |
| `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | 已落地 | wiki 冻结快照 |
| `claude-docs/snapshots/html/controllable_flux_motor_kb.html` | 已落地 | HTML 冻结快照 |

## 3. 与 Codex-docs 的结构对齐

| Codex 文档 | Claude 对应文档 | 状态 |
|---|---|---|
| `codex-docs/README.md` | `claude-docs/README.md` | 已对齐 |
| `codex-docs/handoff_context.md` | `claude-docs/handoff_context.md` | 已对齐 |
| `codex-docs/evidence_manifest.md` | `claude-docs/evidence_manifest.md` | 已对齐 |
| `codex-docs/simulation_traceability.md` | `claude-docs/simulation_traceability.md` | 已对齐 |
| `codex-docs/wiki_html_evidence.md` | `claude-docs/wiki_html_evidence.md` | 已对齐 |
| `codex-docs/toolchain_selection_and_github_references.md` | `claude-docs/toolchain_selection_and_github_references.md` | 已补齐 |
| Codex 无同名详细方案 | `claude-docs/maxwell_motorcad_simulation_plan.md` | Claude 额外补充 |
| `codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | 已对齐 |
| `codex-docs/snapshots/html/controllable_flux_motor_kb.html` | `claude-docs/snapshots/html/controllable_flux_motor_kb.html` | 已对齐 |

## 4. 活动源到快照迁移状态

| 活动源 | Claude-docs 快照/索引 | 状态 |
|---|---|---|
| `wiki/controllable_flux_motor_research_plan.md` | `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | 已迁移 |
| `controllable_flux_motor_kb.html` | `claude-docs/snapshots/html/controllable_flux_motor_kb.html` | 已迁移 |
| `experiments/exp_001_linear_dq/README.md` | `claude-docs/evidence_manifest.md` | 已索引 |
| `experiments/exp_002_variable_flux/README.md` | `claude-docs/evidence_manifest.md` | 已索引 |
| `experiments/exp_003_param_sweep/README.md` | `claude-docs/evidence_manifest.md` | 已索引 |
| `experiments/exp_004_safety_boundaries/summary.json` | `claude-docs/evidence_manifest.md` | 已索引 |
| `models/scheme_simulation_coverage.json` | `claude-docs/simulation_traceability.md` | 已迁移为追踪矩阵 |
| `reports/scheme_engineering_landing_matrix.md` | `claude-docs/evidence_manifest.md` | 已索引 |
| `reports/scheme_driver_power_protocol_diagrams.md` | `claude-docs/evidence_manifest.md` | 已索引 |
| `reports/scheme_bom_eda_integration_design.md` | `claude-docs/evidence_manifest.md` | 已索引 |
| `reports/scheme_industry_design_stage_gate_process.md` | `claude-docs/evidence_manifest.md` | 已索引 |

## 5. 当前缺口判断

截至本索引创建时，Claude 主线关键文档已具备以下闭环：

```text
知识库入口
+ 上下文 handoff
+ wiki 快照
+ HTML 快照
+ 证据 manifest
+ 仿真追踪矩阵
+ 高保真工具链选型
+ Maxwell/Motor-CAD 落地方案
```

仍未纳入 `claude-docs` 的内容主要是活动源本体，而非缺失：`sim/` 源码、`tests/` 测试、`models/` 结构化 JSON、`reports/` 工程报告、`experiments/` 实验产物。这些目录不复制进 `claude-docs`，只在 `evidence_manifest.md` 和 `simulation_traceability.md` 中索引，避免文档包重复存放活动事实源。
