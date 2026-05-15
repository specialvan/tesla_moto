# S01 BOM/EDA sensing fault components risk draft

方案：`negative_d_axis_field_weakening`  
状态：`draft`  
范围：BOM/EDA 风险登记草案；不是 XLSX BOM、EDA netlist、采购清单或制造发布文件。

## 1. 草案目标

S01 的 BOM/EDA 草案用于绑定弱磁控制所需采样链、温度输入、gate-disable 和 fault latch 页面，识别器件族与验证风险。

## 2. 器件族风险清单

| 器件族 | 作用 | 主要风险 | 下一步 |
|---|---|---|---|
| Phase current sensor | `ia/ib/ic` 电流闭环与过流诊断 | 精度、带宽、温漂未定 | 对比分流/霍尔方案 |
| DC bus divider / isolator | `vdc_sense` 电压裕度判断 | 分压误差、隔离耐压、EMC 注入 | 建立误差预算 |
| Temperature sensor | `id_min(T,fault)` 限幅输入 | 安装点与热点不一致 | 与 S11 热安全链复用 |
| Gate-disable latch | 硬件关断路径 | 未定义锁存逻辑和复位条件 | 输出安全链原理图草案 |
| Fault feedback input | 故障诊断回读 | 编码不完整导致台架不可复现 | 定义 fault reason map |

## 3. EDA 页面映射

| EDA 页 | S01 需求 | 当前状态 |
|---|---|---|
| `04_Current_Voltage_Sense` | 电流、Vdc、相电压重建采样 | 待原理图 |
| `05_Position_Temperature` | 温度采样与开短路诊断 | 待原理图 |
| `07_Safety_Watchdog` | gate-disable、fault latch、watchdog | 待原理图 |

## 4. 验收前置条件

- 完成传感器选型与误差预算。
- 输出 ERC 可检查的原理图页。
- 定义 fault latch 复位和诊断策略。
- 与 `V2-S01-PCB-sensing_fault_path-r00.md` 和控制器状态机闭合。

## 5. 禁止误读

本文件只证明 BOM/EDA 风险已进入页面级审查；不证明真实 XLSX BOM、EDA 原理图、netlist、封装库、pick-place、Gerber、ODB++、成本报价、供应链冻结或制造发布已完成。
