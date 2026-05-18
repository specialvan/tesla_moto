# V2-S09 BOM/EDA 绕组开关链草案 r00

方案：S09 绕组重构  
状态：`draft`，用于 BOM/EDA 风险拆解，不替代采购发布。

## 1. BOM 分类

| 类别 | 关键器件 | 参数字段 | 风险 |
|---|---|---|---|
| HV switching | contactor / solid-state switch | voltage, current, breaking capacity, life cycles | 电弧和寿命 |
| Driver | coil driver / isolated gate driver | drive voltage, diagnostic feedback, isolation | stuck fault 诊断不足 |
| Arc suppression | snubber, TVS, precharge/discharge | energy rating, clamp voltage, thermal | 切换过压 |
| Sensing | switch voltage, position, loop current | accuracy, response time, isolation | 非法状态漏检 |
| Harness/busbar | winding taps, switch busbar, shield | current, creepage, vibration | 热与装配误接 |
| Insulation | terminal block, potting, barriers | CTI, thickness, temp class | 800 V 绝缘失效 |

## 2. EDA 约束

- switch state truth table 必须和原理图 net name 一致。
- illegal-state interlock 必须硬件实现并进入 S11 安全链。
- 每个开关节点必须有诊断反馈，不允许只靠命令状态。

## 3. G3 禁止通过项

- BOM 未定义开断能力和寿命循环。
- 未列 arc suppression 额定能量。
- 未定义 winding tap 连接器防错。
- 未定义 stuck-open/stuck-closed 诊断路径。
