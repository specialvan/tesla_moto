# V2-S08 CAD 励磁绕组封装草案 r00

方案：S08 混合励磁  
状态：`draft`，用于 CAD/热/绝缘评审输入，不替代 STEP/FEA 文件。

## 1. CAD 对象

| 对象 | 生产参数 | 评审要求 |
|---|---|---|
| Field winding | H 级绝缘、-20 A 到 30 A 励磁电流 | 标注槽位、端部、灌封和温度采样 |
| Excitation interface | 滑环/无刷励磁/旋转变压接口候选 | 标注磨损、冗余和服务边界 |
| Rotor/stator package | 励磁磁路、永磁辅助磁路 | 标注 psi_eff 贡献和饱和区 |
| Cooling path | 绕组到壳体/冷却套热路径 | 给出热点和热阻目标 |
| Insulation system | 相间、对地、励磁到牵引隔离 | 与 PCB 隔离边界一致 |

## 2. 必标注截面

| 截面 | 必含内容 | 用途 |
|---|---|---|
| A-A | 励磁绕组槽、绝缘、磁路 | 磁热耦合评审 |
| B-B | 端部绕组、固定、灌封 | 制造/振动评审 |
| C-C | 励磁接口、连接器或滑环路径 | 可靠性评审 |
| D-D | 冷却路径与温度传感器 | 热降额评审 |

## 3. G3 禁止通过项

- 无励磁绕组真实封装，只画电机外壳。
- 无绝缘系统或温度采样点。
- 无失励后的热/磁路径影响说明。
- 无滑环/无刷励磁接口方案边界。

## 4. 下版生图/CAD 提示词

Generate an isometric CAD cutaway titled “S08 Hybrid Excitation Field Winding Package”. Show field winding, insulation layers, rotor/stator magnetic path, optional brushless excitation interface, temperature sensors, cooling jacket, terminal routing, psi_eff flux arrows, and loss-of-field risk callouts. White background, realistic CAD engineering style, readable English labels, no marketing render.
