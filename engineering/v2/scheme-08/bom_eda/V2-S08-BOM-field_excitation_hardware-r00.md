# V2-S08 BOM/EDA 励磁硬件草案 r00

方案：S08 混合励磁  
状态：`draft`，用于 BOM/EDA 风险拆解，不替代采购发布。

## 1. BOM 分类

| 类别 | 关键器件 | 参数字段 | 风险 |
|---|---|---|---|
| Field converter | MOSFET/IGBT, gate driver, inductor | voltage, current, switching frequency, isolation | 热与 EMI |
| Field winding | copper winding, bobbin, potting | resistance, inductance, insulation class H | 绕组温升和制造一致性 |
| Excitation interface | slip ring / brushless exciter candidate | current rating, wear, service interval | 寿命和维护 |
| Sensors | field current, voltage, temperature | accuracy, bandwidth, isolation | 失励误判 |
| Protection | fuse, TVS, discharge, latch | trip threshold, response time | open/short 保护覆盖不足 |
| Connector/harness | field connector, shielded cable | creepage, current, vibration | 接触电阻与热失控 |

## 2. EDA 约束

- 励磁功率器件、采样和控制隔离必须分区。
- loss-of-field fault net 必须进入硬件 latch 与控制器诊断。
- 连接器 pinout 必须标出 field+/field-/shield/temp return。

## 3. G3 禁止通过项

- 无励磁绕组物料和绝缘等级。
- 无失励保护器件。
- 无励磁接口寿命或维护字段。
- 无隔离与爬电约束。
