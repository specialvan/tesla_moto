# S01 DVP&R field-weakening fault injection draft

方案：`negative_d_axis_field_weakening`  
状态：`draft / planned / not executed / not validated`  
范围：DVP&R 测试协议草案；不是台架报告、HIL 结果、认证报告或工程验证结论。

## 1. 草案目标

S01 测试草案用于规划弱磁区电压裕度、负 d 轴电流限幅、温度降额、采样故障和 gate-disable/fault latch 的故障注入验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S01-CTRL-field_weakening_state_machine-r00.drawio` |
| PCB | `../pcb/V2-S01-PCB-sensing_fault_path-r00.md` |
| BOM/EDA | `../bom_eda/V2-S01-BOM-sensing_fault_components-r00.md` |
| CAD | `../cad/V2-S01-CAD-sensor_busbar_layout-r00.md` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S01-DV-001 | 弱磁进入/退出状态机 | HIL planned | 状态切换日志、V margin 记录 | planned |
| S01-DV-002 | `id_min(T,fault)` 限幅 | SIL/HIL planned | 温度 sweep 与 `id` clamp 日志 | planned |
| S01-DV-003 | Vdc 采样故障 | Fault injection planned | fallback 与 fault reason 记录 | planned |
| S01-DV-004 | 电流采样异常 | Fault injection planned | derate / gate-disable 触发记录 | planned |
| S01-DV-005 | gate-disable latch | Bench planned | latch 置位、保持和复位记录 | planned |

## 4. 验收前置条件

- HIL 模型包含 Vdc、电流、温度和 gate-disable 输入。
- fault reason map 与 PCB fault latch 页面一致。
- 测试日志能绑定控制 LUT 不可行原因。
- 台架执行前完成安全评审。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| HIL 未建模 gate-disable latch | 无法验证硬件关断 | 建立 latch I/O 模型 |
| 温度输入无热惯性 | 降额验证不代表实机 | 接入 S11 热模型 |
| 采样故障阈值未标定 | 故障注入不闭合 | 定义诊断阈值 |

## 6. 禁止误读

本文件只证明 DVP&R / 测试计划已进入页面级审查；不证明测试已执行、台架已搭建、HIL 已运行、样件已制造、数据已通过、功能安全已认证或工程验证已完成。
