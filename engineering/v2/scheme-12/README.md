# S12 工况加权效率 / Pareto 选择图纸包

方案 ID：`weighted_efficiency_pareto_selection`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S12-PCB-candidate_index-r00.md` | draft | 已建立候选方案 PCB/BOM/EDA 版本索引 |
| 3D/CAD | `cad/V2-S12-CAD-candidate_package_index-r00.md` | draft | 已建立候选拓扑 CAD、质量、封装和冷却边界索引 |
| Controller | `controller/V2-S12-CTRL-pareto_scorecard-r00.md` | draft | 已绘制 drive cycle、系统损耗、成熟度权重和风险评分图草案 |
| BOM/EDA | `bom_eda/V2-S12-BOM-pareto_cost_risk-r00.md` | draft | 已汇总候选 BOM 成本、制造风险、供应风险和控制器差异字段 |
| Test/DVP | `test_dvpr/V2-S12-DVP-pareto_traceability-r00.md` | draft | 已定义工况、系统损耗、敏感性和证据路径审计 |
| Simulation | `simulation/V2-S12-SIM-pareto_traceability-r00.md` | draft | 已关联 drive cycle、系统损耗、敏感性和证据路径审计 |
| Prompts/r03 | `prompts/V2-S12-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- EXP-010 有加权效率 Pareto 代理实验。

## 当前判断

Pareto 决策当前已具备候选图纸/BOM/测试证据版本绑定草案，但仍缺正式 reviewed/released 证据；只能输出 research rank 或 needs_more_evidence，不能直接输出工程推荐。
