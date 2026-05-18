# V2-S07 PCB 磁化脉冲驱动草案 r00

方案：S07 可变磁化状态 / Memory Motor  
状态：`draft`，用于 EDA 原理图与安全评审输入，不替代正式 PCB/原理图文件。

## 1. 电气页

| 页 | 必含电路 | 生产参数 |
|---|---|---|
| Pulse energy | DC-link/储能电容、预充、泄放、母线采样 | 800 V class、单脉冲能量 100 J 初值 |
| Pulse switch | IGBT/SiC 脉冲开关、栅极驱动、DESAT/UVLO | 峰值 1000 A、脉宽 50 μs 初值 |
| Magnetization coil | 磁化线圈端子、极性检测、反灌保护 | 8 档磁状态，禁止牵引开关同时导通 |
| Interlock | HVIL、gate-disable、S11 safety request、硬件互锁 | 互锁响应 <1 ms |
| Sensing | pulse current、coil voltage、temperature、state observer input | 采样带宽覆盖脉冲上升沿 |

## 2. 布局边界

- 脉冲高 di/dt 回路必须和低压观测链隔离分区。
- 储能电容、脉冲开关、磁化线圈端子形成最小环路。
- 牵引逆变器 gate enable 与磁化 pulse enable 必须硬件互斥。

## 3. G3 禁止通过项

- 无牵引/磁化互锁链路。
- 无脉冲电流与线圈电压观测。
- 无预充、泄放或 residual energy 标注。
- 只画控制框图，不画功率脉冲路径。

## 4. 下版生图提示词

Generate a white-background engineering schematic titled “S07 Memory Motor Magnetization Pulse Driver PCB”. Include 800V energy storage, precharge, discharge, pulse switch, gate driver with DESAT/UVLO, magnetization coil terminals, pulse current sensing, coil voltage sensing, HVIL, traction inverter interlock, gate-disable latch, and S11 safety request. Use red high-energy pulse path, blue sensing path, amber interlock callouts, readable English labels, no marketing render.
