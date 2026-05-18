# S05 DVP&R saturation co-design draft

方案：`magnetic_saturation_codesign`
状态：`draft / planned / not executed / not validated`
范围：DVP&R / FEA 协议草案；不是 FEA / 台架结果。

## 1. 草案目标

S05 测试草案用于规划饱和协同设计候选 geometry 的 FEA correlation、应力、铁损、退磁与 NVH 联合验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S05-CTRL-saturation_scorecard-r00.drawio`（待落地） |
| CAD | `../cad/V2-S05-CAD-rotor_barrier_bridge-r00.step`（待落地） |
| BOM/EDA | `../bom_eda/V2-S05-BOM-magnetic_stack-r00.xlsx`（待落地） |
| Parameters | `../parameters/V2-S05-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S05-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S05-DV-001 | FEA correlation | FEA planned | lambda_d/lambda_q vs param-scaled | planned |
| S05-DV-002 | 转子应力 < 600 MPa | FEA planned | stress map @ 18000 rpm | planned |
| S05-DV-003 | 铁损 ≤ baseline + 3 % | FEA planned | iron loss vs baseline | planned |
| S05-DV-004 | 退磁 id_min ≥ -240 A | FEA + EXP-004 cross | demag boundary | planned |
| S05-DV-005 | NVH 扭矩纹波 ≤ 3 % | FEA + bench planned | torque ripple FFT | planned |

## 4. 验收前置条件

- 候选 geometry STEP 版本冻结。
- FEA solver（Motor-CAD / Maxwell）与材料库选定。
- 退磁边界与 S11 thermal sheet 同步。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| FEA 与 EXP-003 参数缩放偏差 | 候选排序失真 | 早期对齐校准 |
| 应力 / 退磁冲突无法同时满足 | 候选淘汰 | 增加 barrier / bridge 几何自由度 |
| NVH 实测与 FEA 偏差 | 验收不达标 | bench 反标定 |

## 6. 禁止误读

本文件只证明 DVP&R / 测试计划已进入页面级审查；不证明 FEA 已执行、台架已搭建、样件已制造、数据已通过或工程验证已完成。
