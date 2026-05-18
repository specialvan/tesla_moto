# V2-S09 PCB 绕组开关矩阵草案 r00

方案：S09 绕组重构  
状态：`draft`，用于 EDA/互锁/瞬态评审输入，不替代正式 PCB 或 HV 接线图。

## 1. 电气页

| 页 | 必含电路 | 生产参数 |
|---|---|---|
| Switch matrix | HV contactor/solid-state switch、series/parallel/star/delta path | 800 V / 300 A class 初值 |
| Gate/coil drive | 接触器线圈驱动或固态开关 gate driver | 开关确认与故障反馈 |
| Interlock | 非法组合硬件互锁、HVIL、S11 request | 互锁响应 <1 ms |
| Arc suppression | snubber、TVS、预充/泄放、零电流检测 | 切换窗口 50-200 ms |
| Circulating current | phase current、loop current、switch voltage sensing | 环流目标 <5 A |

## 2. 布局边界

- HV 开关矩阵和低压驱动/诊断必须隔离。
- 每个重构状态必须有独立位置反馈或等效电压确认。
- 零转矩/零电流窗口信号必须进入硬件允许链。

## 3. G3 禁止通过项

- 无非法状态互锁真值表。
- 无 arc suppression 或残余能量路径。
- 无开关位置反馈。
- 无环流检测链。

## 4. 下版生图提示词

Generate a white-background engineering schematic titled “S09 Winding Reconfiguration Switch Matrix”. Include HV contactors or solid-state switches, star/delta or series/parallel winding paths, coil/gate drivers, position feedback, zero-torque window enable, zero-current detector, circulating current sensing, snubbers, TVS arc suppression, HVIL, illegal-state hardware interlock, and S11 safety request. Mark 800V/300A class, interlock below 1ms, switching window 50-200ms, circulating current below 5A.
