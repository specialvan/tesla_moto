# S11 BOM/EDA safety chain risk draft

方案：`thermal_demag_safety_protection`  
状态：`draft`  
范围：BOM/EDA 风险登记草案；不是 XLSX BOM、EDA netlist、采购清单、ASIL 认证包或制造发布文件。

## 1. 草案目标

S11 的 BOM/EDA 草案用于识别温度/退磁安全链、fault latch、gate-disable、看门狗和诊断回读的器件风险，支撑后续 DFMEA/FM EDA 和故障注入 DVP&R。

## 2. 器件族风险清单

| 器件族 | 作用 | 主要风险 | 下一步 |
|---|---|---|---|
| Magnet/winding/oil temp sensors | 热降额和退磁保护 | 热点代表性不足、开短路诊断未定 | 与 CAD/热模型联审 |
| Safety latch / watchdog | 故障锁存和复位控制 | 软件依赖过强或复位策略不清 | 设计硬件 latch 草图 |
| Gate-disable path | 独立硬件关断 | 与 gate driver 兼容性未定 | 验证关断电平和延迟 |
| Isolated power / sense | 安全链隔离供电和采样 | 隔离耐压和故障传播未评估 | 建立隔离边界表 |
| Fault reason interface | DVP&R 复现和诊断 | reason 编码不完整 | 定义故障码和日志字段 |

## 3. EDA 页面映射

| EDA 页 | S11 需求 | 当前状态 |
|---|---|---|
| `05_Position_Temperature` | 多温度采样、开短路诊断 | 待原理图 |
| `07_Safety_Watchdog` | fault latch、watchdog、gate-disable | 待原理图 |
| `03_Gate_Drivers` | gate-disable 与驱动故障反馈 | 待原理图 |

## 4. 验收前置条件

- 完成安全链器件候选和诊断覆盖字段。
- 定义 gate-disable 独立路径和复位策略。
- 建立 fault reason map 与 DVP&R 故障注入矩阵。
- 与 `V2-S11-PCB-safety_fault_latch-r00.md` 和控制器状态机闭合。

## 5. 禁止误读

本文件只证明 BOM/EDA 风险已进入页面级审查；不证明真实 XLSX BOM、EDA 原理图、netlist、封装库、pick-place、Gerber、ODB++、成本报价、供应链冻结或制造发布已完成。
