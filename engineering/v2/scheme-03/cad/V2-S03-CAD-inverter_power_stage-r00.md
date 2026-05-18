# V2-S03 CAD 逆变器功率级封装草案 r00

方案：S03 SVPWM / 过调制  
状态：`draft`，用于 CAD/热/EMC 联合评审输入，不替代 STEP/Parasolid/SolidWorks 文件。

## 1. 封装对象

| 对象 | 生产参数 | 评审要求 |
|---|---|---|
| Power module | 360 V bus，按峰值电流与过调制热脉冲选型 | 标注开关节点、热界面、固定孔 |
| DC-link capacitor | 纹波电流、ESR、温升、寿命 | 与母排高频回路最短闭合 |
| Laminated busbar | 低杂散电感、相间绝缘、爬电距离 | 与 PCB gate/采样接口同坐标 |
| Cooling plate | 功率模块、DC-link、gate driver 热路径 | 入口/出口、压降和接触热阻 |
| EMI shield | HV/LV 分区、屏蔽接地点、线束出口 | 与 PCB EMC 页一致 |

## 2. 必标注坐标系

- `X`：逆变器横向母排方向。
- `Y`：控制板到功率模块堆叠方向。
- `Z`：冷却板法向。
- HV 区、LV 区、屏蔽区必须用不同图层/颜色区分。

## 3. CAD 截面要求

| 截面 | 必含内容 | 用途 |
|---|---|---|
| A-A | DC-link capacitor → busbar → power module 高频回路 | 杂散电感评审 |
| B-B | power module → TIM → cooling plate 热路径 | 热阻评审 |
| C-C | HV connector → shield → enclosure | EMC/爬电评审 |
| D-D | current sensor / phase output packaging | 采样窗口和装配评审 |

## 4. G3 禁止通过项

- 无 DC-link 到功率模块的高频电流回路标注。
- 无冷却板接触面、TIM 厚度或热阻目标。
- 无 HV/LV 分区和屏蔽接地路径。
- 只给外观盒子，不给母排、模块、电容和线束相对位置。

## 5. 下版生图/CAD 提示词

生成汽车牵引逆变器 3D CAD 剖视工程图，主题为“S03 overmodulation inverter power stage package”。包含 DC-link capacitor bank、laminated busbar、three-phase power module、gate driver PCB、cooling plate、HV/LV separation、EMI shield、phase output current sensor。使用白底等距视角和局部剖面，标注 stray inductance loop、thermal path、creepage/clearance、shield ground。风格为真实工程 CAD 草图，不要渲染海报。