# V2-S10 CAD 相组封装草案 r00

方案：S10 多相 / 相组控制  
状态：`draft`，用于 CAD/热/NVH/服务评审输入，不替代 STEP 文件。

## 1. CAD 对象

| 对象 | 生产参数 | 评审要求 |
|---|---|---|
| Six-phase terminals | A1/B1/C1/A2/B2/C2 | 标注相序、防错和服务可达性 |
| Phase-group busbar | 双三相或六相母排 | 标注电流路径、回路面积和屏蔽 |
| Power module layout | 六相功率模块或双三相模块 | 标注热均衡和故障隔离边界 |
| Cooling plate | 相组热区、流道、温度测点 | 单相失效后热点可控 |
| Harness package | 六相线束、屏蔽、固定 | 标注 NVH 和装配防错 |

## 2. 必标注截面

| 截面 | 必含内容 | 用途 |
|---|---|---|
| A-A | 六相端子与线束出口 | 装配/服务评审 |
| B-B | 相组母排与功率模块 | 电感/热评审 |
| C-C | 冷却板与热点 | 容错热评审 |
| D-D | 屏蔽、接地、HV/LV 分区 | EMC 评审 |

## 3. G3 禁止通过项

- 无六相端子、相序或防错标识。
- 无相组热均衡和单相故障热路径。
- 无线束/NVH 固定策略。
- 只给三相封装重复图。

## 4. 下版生图/CAD 提示词

Generate an isometric CAD cutaway titled “S10 Six-Phase Phase-Group Inverter Package”. Show A1/B1/C1/A2/B2/C2 terminals, dual three-phase or six-phase busbar, six phase current sensors, power modules, cooling plate, thermal zones, shielded harness, service labels, phase-order keying, and fault-isolated phase-group boundaries. White background, engineering CAD style, readable English labels.
