# S11 DVP&R safety fault injection draft

方案：`thermal_demag_safety_protection`  
状态：`draft / planned / not executed / not validated`  
范围：DVP&R / 安全故障注入测试协议草案；不是 HIL/台架执行结果、ASIL 认证报告或工程验证结论。

## 1. 草案目标

S11 测试草案用于规划温度、退磁、传感器开短路、unknown sensor fallback、gate-disable 和 fault latch 的安全故障注入验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S11-CTRL-safety_fault_state_machine-r00.drawio` |
| PCB | `../pcb/V2-S11-PCB-safety_fault_latch-r00.md` |
| BOM/EDA | `../bom_eda/V2-S11-BOM-safety_chain-r00.md` |
| CAD | `../cad/V2-S11-CAD-thermal_sensor_cooling-r00.md` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S11-DV-001 | 温度 warning / critical 阈值 | HIL planned | derate、latch、复位日志 | planned |
| S11-DV-002 | 传感器开路/短路 | Fault injection planned | unknown sensor fallback 记录 | planned |
| S11-DV-003 | demag margin 低 | SIL/HIL planned | `id_min_allowed` 与降额动作 | planned |
| S11-DV-004 | gate-disable 断言 | Bench planned | 关断延迟、锁存和复位记录 | planned |
| S11-DV-005 | fault reason 追溯 | HIL/Bench planned | DTC、日志和 DVP&R case 绑定 | planned |

## 4. 验收前置条件

- 温度传感器位置与热模型映射冻结。
- fault reason map 和诊断日志字段冻结。
- gate-disable 独立硬件路径进入原理图草案。
- 台架执行前完成高压安全和功能安全评审。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 传感点不代表磁钢热点 | demag 保护误判 | 建立 thermal correlation |
| gate-disable 延迟未知 | 安全关断不可评估 | 定义测量夹具 |
| ASIL/FM EDA 未完成 | 不能进入安全发布 | 开始 DFMEA/FM EDA |

## 6. 禁止误读

本文件只证明 DVP&R / 测试计划已进入页面级审查；不证明测试已执行、台架已搭建、HIL 已运行、样件已制造、数据已通过、功能安全已认证或工程验证已完成。
