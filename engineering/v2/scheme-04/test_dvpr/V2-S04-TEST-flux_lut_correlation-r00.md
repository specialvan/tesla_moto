# S04 DVP&R nonlinear flux LUT correlation draft

方案：`nonlinear_flux_lut`  
状态：`draft / planned / not executed / not validated`  
范围：DVP&R / 相关性测试协议草案；不是 FEA 结果、台架报告、LUT 发布或工程验证结论。

## 1. 草案目标

S04 测试草案用于规划非线性磁链 LUT 的 FEA 回灌、台架反标定、插值边界、residual 监控和 fallback 行为验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S04-CTRL-flux_lut_interpolation-r00.drawio` |
| PCB | `../pcb/V2-S04-PCB-lut_observer_inputs-r00.md` |
| BOM/EDA | `../bom_eda/V2-S04-BOM-lut_sensor_chain-r00.md` |
| CAD | `../cad/V2-S04-CAD-fea_geometry_source-r00.md` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S04-DV-001 | LUT 边界检查 | SIL planned | out-of-bounds 拒绝/clamp 日志 | planned |
| S04-DV-002 | 双线性插值一致性 | Unit/SIL planned | 插值误差报告 | planned |
| S04-DV-003 | FEA 几何版本绑定 | Document review planned | CAD/FEA/LUT version trace | planned |
| S04-DV-004 | 台架反标定相关性 | Bench planned | measured vs predicted residual | planned |
| S04-DV-005 | residual high fallback | HIL planned | fallback_active 与降额日志 | planned |

## 4. 验收前置条件

- 真实 CAD/FEA 几何源、材料和坐标约定冻结。
- LUT 输入误差预算完成。
- 台架测点和温度点可映射到几何位置。
- residual 阈值和 fallback 策略可被日志采集。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 当前 LUT 仍是 synthetic | 不能代表真实电机 | 接入 FEA/实测 LUT |
| 传感器误差未定 | residual 判断失真 | 完成采样链预算 |
| FEA/台架坐标不一致 | 相关性不可比 | 冻结 dq 坐标约定 |

## 6. 禁止误读

本文件只证明 DVP&R / 测试计划已进入页面级审查；不证明测试已执行、台架已搭建、HIL 已运行、样件已制造、数据已通过、功能安全已认证或工程验证已完成。
