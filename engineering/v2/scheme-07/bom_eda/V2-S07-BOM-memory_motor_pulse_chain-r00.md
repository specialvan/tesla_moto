# V2-S07 BOM/EDA 磁化脉冲链草案 r00

方案：S07 可变磁化状态 / Memory Motor  
状态：`draft`，用于 BOM 风险拆解，不替代采购发布。

## 1. BOM 分类

| 类别 | 关键器件 | 参数字段 | 风险 |
|---|---|---|---|
| Energy storage | HV film capacitor / pulse capacitor | voltage, capacitance, ESR, pulse current, lifetime | 体积、寿命、残余能量 |
| Pulse switch | IGBT/SiC module, gate driver | peak current, pulse width, DESAT, isolation | 短路能量和误触发 |
| Magnetization coil | coil, terminals, insulation | inductance, resistance, insulation class, thermal class | 热漂移和绝缘老化 |
| Sensing | current sensor, voltage divider, temperature sensor | bandwidth, isolation, accuracy | 脉冲边沿观测不足 |
| Safety chain | HVIL, relay/contactor, discharge resistor | response time, diagnostic coverage | 牵引互锁失效 |
| Magnetic material | reversible magnet segment | coercivity, remanence, temp coefficient | 材料供应和寿命漂移 |

## 2. EDA 约束

- 高能脉冲网络单独 net class，标注爬电、间隙、铜厚和热容量。
- 采样链必须有隔离和过压保护。
- 牵引 gate-disable 与 pulse enable 必须形成硬件互锁，不只依赖软件。

## 3. G3 禁止通过项

- 未给 pulse capacitor 能量与寿命字段。
- 未给可逆磁体材料参数。
- 未给互锁器件诊断覆盖率。
- BOM 仅列通用“MOSFET/电容/传感器”。
