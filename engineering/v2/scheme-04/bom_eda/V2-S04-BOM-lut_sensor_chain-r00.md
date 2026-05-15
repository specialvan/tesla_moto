# S04 BOM/EDA LUT sensor chain risk draft

方案：`nonlinear_flux_lut`  
状态：`draft`  
范围：BOM/EDA 风险登记草案；不是 XLSX BOM、EDA netlist、采购清单或制造发布文件。

## 1. 草案目标

S04 的 BOM/EDA 草案用于识别非线性磁链 LUT 所需观测输入器件和误差预算风险，避免把 synthetic LUT 数值证明误写成真实传感链闭合。

## 2. 器件族风险清单

| 器件族 | 作用 | 主要风险 | 下一步 |
|---|---|---|---|
| Current sensor chain | `id/iq` LUT 坐标来源 | 零漂、带宽和同步误差 | 建立采样误差预算 |
| Position front-end | dq 变换和高速角度输入 | 角度延迟导致 LUT 坐标偏移 | 建立 delay compensation |
| Temperature sensor | 温度修正和 LUT 切片选择 | 传感点不等于磁钢/绕组热点 | 与 CAD/热模型绑定 |
| DC bus sensing | voltage margin 预测 | 分压误差影响可行性判断 | 建立 voltage margin 预算 |
| Diagnostic storage | residual/fallback 记录 | 无日志则台架不可追溯 | 定义诊断缓冲区 |

## 3. EDA 页面映射

| EDA 页 | S04 需求 | 当前状态 |
|---|---|---|
| `04_Current_Voltage_Sense` | 电流与 Vdc 输入精度链 | 待原理图 |
| `05_Position_Temperature` | 位置和温度输入 | 待原理图 |
| `06_MCU_Control` | LUT residual、fallback 和日志字段 | 待原理图 |

## 4. 验收前置条件

- 完成 LUT 输入误差预算。
- 定义 bounds/fallback 诊断信号的存储与上报。
- 绑定 FEA 几何、传感器位置和 LUT 版本号。
- 与 `V2-S04-PCB-lut_observer_inputs-r00.md` 和控制器状态机闭合。

## 5. 禁止误读

本文件只证明 BOM/EDA 风险已进入页面级审查；不证明真实 XLSX BOM、EDA 原理图、netlist、封装库、pick-place、Gerber、ODB++、成本报价、供应链冻结或制造发布已完成。
