# S12 DVP&R pareto traceability draft

方案：`weighted_efficiency_pareto_selection`
状态：`draft / planned / not executed / not validated`
范围：DVP&R / 审计协议草案；不替代真实 drive cycle 实测、不替代各候选方案的台架。

## 1. 草案目标

S12 测试草案用于规划候选方案的 drive cycle、系统损耗、敏感性 sweep 与证据路径审计。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S12-CTRL-pareto_scorecard-r00.drawio`（待落地） |
| Parameters | `../parameters/V2-S12-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S12-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S12-DV-001 | drive cycle audit | Document review planned | WLTP / CLTC 数据版本 | planned |
| S12-DV-002 | 系统损耗 audit | Document review planned | 每候选损耗源 | planned |
| S12-DV-003 | sensitivity sweep ±20 % | Sim planned | 权重扰动 ranking | planned |
| S12-DV-004 | evidence-path audit | Document review planned | 每候选 PCB / CAD / BOM / DVP / r02 sim_binding | planned |

## 4. 验收前置条件

- 11 候选方案 r02 sim_binding 全部存在。
- WLTP / CLTC 数据版本冻结。
- 损耗模型 EXP-010 + EXP-011 通过。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| drive cycle 版本不一致 | ranking 失真 | 早期版本锁定 |
| 损耗模型简化过度 | 候选排序不可信 | 加入更多损耗源 |
| 敏感性 sweep 不稳定 | 推荐不可信 | r03 加 sweep ranking |

## 6. 禁止误读

本文件审计性质；不证明任何候选方案 engineering_validated；S12 pareto 通过不晋升任何候选为工程方案。
