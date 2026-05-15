# S11 CAD thermal sensor / cooling boundary draft

方案：`thermal_demag_safety_protection`  
状态：`draft`  
范围：3D/CAD 热传感与冷却边界草案；不是 STEP、Parasolid、SolidWorks、Fluent、Motor-CAD 或制造发布文件。

## 1. 草案目标

S11 的 CAD 草案用于定义磁钢/绕组/油温传感器安装、冷却路径、控制器散热和 gate-disable 安全链所需机械边界。

## 2. 关联图纸包

| 类型 | 路径 | 作用 |
|---|---|---|
| Controller | `../controller/V2-S11-CTRL-safety_fault_state_machine-r00.drawio` | 定义热/退磁安全状态机 |
| PCB | `../pcb/V2-S11-PCB-safety_fault_latch-r00.md` | 定义安全链和 fault latch 接口 |
| BOM/EDA | `../bom_eda/V2-S11-BOM-safety_chain-r00.md` | 定义安全链器件族风险 |

## 3. 热/冷却边界草案

| 边界项 | 当前草案 | 未决项 |
|---|---|---|
| 磁钢温度观测 | 需要接近磁钢热点的等效观测点 | 传感器安装不可直接位于磁钢时的估算策略未定 |
| 绕组温度观测 | 需定义绕组端部或槽内等效点 | CAD 安装方式未定 |
| 油温/冷却路径 | 需记录入口/出口/局部热点位置 | 油路 CAD 和流量未定 |
| 控制器散热 | safety latch、gate driver、MCU 区需热路径 | 控制器壳体散热面未定 |
| 服务与维修 | 温度传感器和线束需可装配/更换 | 维修空间未定义 |

## 4. Keep-out / 装配问题

| 问题 | 影响 | 下一步 |
|---|---|---|
| 传感点与热点偏差未知 | 退磁保护可能误判 | 建立 thermal correlation plan |
| 油路边界未知 | 冷却能力不可评审 | 建立冷却路径 CAD 初稿 |
| 安全链器件热路径未知 | 高温下 gate-disable 可靠性未知 | 与 PCB 安全页联审 |

## 5. CAD 前置输入

- 磁钢、绕组、油路和控制器壳体 datum。
- 传感器封装、安装方式和线束出口。
- 冷却入口/出口、流量和热边界条件。
- 与 EXP-004 简化热/退磁模型的参数映射。

## 6. 禁止误读

本文件只证明 3D/CAD 封装边界已进入页面级审查；不证明真实 STEP、Parasolid、SolidWorks、Motor-CAD/Maxwell 几何、装配公差、结构强度、热仿真、FEA 网格或制造发布已完成。
