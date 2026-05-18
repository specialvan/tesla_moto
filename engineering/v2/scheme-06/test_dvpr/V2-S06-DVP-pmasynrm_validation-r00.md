# S06 DVP&R PMaSynRM validation draft

方案：`pmasynrm_high_saliency_low_pm`
状态：`draft / planned / not executed / not validated`
范围：DVP&R / PMaSynRM 验证协议草案；不是 FEA / 台架结果。

## 1. 草案目标

S06 测试草案用于规划高凸极低 PM 占比电机的 torque ripple、应力、退磁、热与 NVH 验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S06-CTRL-saliency_control_map-r00.drawio`（待落地） |
| CAD | `../cad/V2-S06-CAD-pmasynrm_rotor_stator-r00.step`（待落地） |
| BOM/EDA | `../bom_eda/V2-S06-BOM-low_pm_topology-r00.xlsx`（待落地） |
| Parameters | `../parameters/V2-S06-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S06-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S06-DV-001 | torque ripple ≤ 3 % | FEA + bench planned | ripple FFT vs baseline | planned |
| S06-DV-002 | 转子应力 < 700 MPa | FEA planned | stress map | planned |
| S06-DV-003 | 低 PM 退磁 id_min ≥ -200 A | FEA + EXP-004 cross | demag boundary | planned |
| S06-DV-004 | 热 / 冷却 | bench planned | 温度 vs 工况 | planned |
| S06-DV-005 | NVH | bench planned | torque ripple FFT | planned |

## 4. 验收前置条件

- 候选 PM fraction 与凸极比组合冻结。
- FEA 与 EXP-003 缩放对齐。
- 退磁与 S11 同步。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 低 PM 致 demag 高敏感 | 工程窗收窄 | id_min 早期标定 |
| 高凸极致 torque ripple 上升 | NVH 不达标 | 控制器 / 转子协同设计 |
| FEA 与 EXP-003 偏差 | 候选排序失真 | 早期对齐 |

## 6. 禁止误读

本文件只证明 DVP&R / 测试计划已进入页面级审查；不证明 FEA / 台架 / 样件 / 数据 / 安全认证 / 工程验证已完成。
