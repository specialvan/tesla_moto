# S12 工况加权效率 / Pareto 选择图纸包

方案 ID：`weighted_efficiency_pareto_selection`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S12-PCB-candidate_index-r00.md` | missing | 建立候选方案 PCB/BOM/EDA 版本索引 |
| 3D/CAD | `cad/V2-S12-CAD-candidate_package_index-r00.md` | missing | 建立候选拓扑 CAD、质量、封装和冷却边界索引 |
| Controller | `controller/V2-S12-CTRL-pareto_scorecard-r00.drawio` | missing | 绘制 drive cycle、系统损耗、成熟度权重和风险评分图 |
| BOM/EDA | `bom_eda/V2-S12-BOM-pareto_cost_risk-r00.xlsx` | missing | 汇总候选 BOM 成本、制造风险、供应风险和控制器差异 |
| Test/DVP | `test_dvpr/V2-S12-DVP-pareto_traceability-r00.md` | missing | 定义工况、系统损耗、敏感性和证据路径审计 |
| Simulation | `simulation/V2-S12-SIM-pareto_traceability-r00.md` | missing | 关联 drive cycle、系统损耗、敏感性和证据路径审计 |

## 现有证据

- EXP-010 有加权效率 Pareto 代理实验。

## 当前判断

Pareto 决策目前缺少候选图纸/BOM/测试证据版本绑定，不能输出工程推荐。
