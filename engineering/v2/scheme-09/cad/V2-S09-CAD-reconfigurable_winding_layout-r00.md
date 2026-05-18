# V2-S09 CAD 可重构绕组布局草案 r00

方案：S09 绕组重构  
状态：`draft`，用于 CAD/制造/绝缘/热评审输入，不替代 STEP 或绕组制造图。

## 1. CAD 对象

| 对象 | 生产参数 | 评审要求 |
|---|---|---|
| Winding end-turn | 可重构端部连接、相组引出 | 标注端部高度、绝缘和振动固定 |
| Switch package | HV 接触器/固态开关封装 | 标注服务边界、热路径和爬电距离 |
| Harness/busbar | phase tap、switch matrix、shield | 标注大电流路径和回路面积 |
| Insulation | 相间、对地、开关端子隔离 | 与 800 V class 一致 |
| Thermal path | 开关、端部绕组、连接器热路径 | 标注热点和温度传感器 |

## 2. 必标注截面

| 截面 | 必含内容 | 用途 |
|---|---|---|
| A-A | 绕组端部与 tap 引出 | 制造可行性评审 |
| B-B | 开关矩阵封装与 HV/LV 分区 | 安全/服务评审 |
| C-C | 绝缘层、爬电距离、固定结构 | 800 V 绝缘评审 |
| D-D | 热路径和传感器位置 | 切换发热评审 |

## 3. G3 禁止通过项

- 无绕组 tap 与开关矩阵的真实空间关系。
- 无端部固定、绝缘或服务空间。
- 无开关热路径或温度测点。
- 只画电路框图，不给封装布局。

## 4. 下版生图/CAD 提示词

Generate an isometric CAD cutaway titled “S09 Reconfigurable Winding and Switch Matrix Package”. Show stator end-turns, winding taps, HV switch matrix, star/delta or series/parallel busbar paths, insulated terminals, shielded harness, service cover, temperature sensors, creepage/clearance callouts, and thermal path arrows. White background, realistic engineering CAD style, readable English labels.
