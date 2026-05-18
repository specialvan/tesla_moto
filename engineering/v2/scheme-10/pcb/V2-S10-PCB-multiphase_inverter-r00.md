# V2-S10 PCB 多相逆变器草案 r00

方案：S10 多相 / 相组控制  
状态：`draft`，用于 EDA/故障切除/EMC 评审输入，不替代正式 PCB 文件。

## 1. 电气页

| 页 | 必含电路 | 生产参数 |
|---|---|---|
| Six-phase power | A1/B1/C1 与 A2/B2/C2 gate drive | 6 相，130 A/相初值 |
| Phase sensing | 六相电流、相电压、DC-link sensing | 支持 αβ 与 xy 子空间观测 |
| Fault isolation | 单相/相组 gate-disable、fuse/solid-state cutoff | 故障检出到降额 <2 ms |
| Connector/harness | 双三相端子、屏蔽、相序防错 | 服务复位与诊断标识 |
| EMC/sampling | 多相 PWM 同步、采样窗口、共模路径 | 谐波和 NVH 风险标注 |

## 2. 布局边界

- 两组三相 gate drive 和采样链必须清晰分区。
- 每相故障 latch 必须可单独屏蔽，不影响安全关断总链。
- xy 子空间观测所需采样通道不得被三相等效简化。

## 3. G3 禁止通过项

- 只画三相逆变器并声称多相。
- 无单相/相组故障切除路径。
- 无六相电流采样和相序防错。
- 无谐波子空间或 NVH/EMC 风险标注。

## 4. 下版生图提示词

Generate a white-background engineering schematic titled “S10 Six-Phase Multiphase Inverter PCB”. Include six isolated gate drivers, six phase current sensors, phase voltage sensing, DC-link sensing, dual three-phase connectors, per-phase gate-disable latch, phase-group fault isolation, fuse or solid-state cutoff, PWM sampling windows, alpha-beta and xy harmonic observer signals, shield ground, and S11 safety request. Mark 6 phases, 130A per phase, fault derate below 2ms, 50% derate mode.
