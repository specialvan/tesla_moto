# V2-S12 Pareto 仿真证据追溯 r00

状态：`draft`。

## 1. 当前证据

| 证据 | 路径 | 可证明 | 不可证明 |
|---|---|---|---|
| EXP-010 weighted efficiency | `experiments/exp_010_weighted_efficiency_pareto/summary.json` | 代理工况权重下的排序机制 | 工程推荐 |
| 候选 PCB/CAD/BOM r00 | S01~S12 对应目录 | 成熟度证据路径 | 正式量产可行性 |
| DVP 草案 | `test_dvpr/V2-S12-DVP-pareto_traceability-r00.md` | 证据审计计划 | 已执行审计 |

## 2. Traceability 输出

- 每个候选输出 `evidence_status`：missing/indexed/draft/reviewed/released。
- 每个候选输出 `recommendation_class`：stop/research_rank_only/needs_more_evidence/engineering_candidate。
- 每个推荐必须列出支撑它的 PCB、CAD、BOM、DVP 和 safety 文件。

## 3. 下版提示词

生成 S12 Pareto traceability flowchart，从 EXP-010 drive cycle 到 candidate evidence index、BOM cost risk、CAD package penalty、S11 safety gate、sensitivity analysis、recommendation class。白底工程流程图，英文标签，强调 no evidence no recommendation。