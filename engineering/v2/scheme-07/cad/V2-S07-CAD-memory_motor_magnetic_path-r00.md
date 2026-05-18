# V2-S07 CAD 记忆电机磁路草案 r00

方案：S07 可变磁化状态 / Memory Motor  
状态：`draft`，用于 CAD/FEA/热评审输入，不替代 STEP/FEA 几何文件。

## 1. CAD 对象

| 对象 | 生产参数 | 评审要求 |
|---|---|---|
| Variable magnet segment | 可逆磁化材料、8 档磁状态 | 标注磁化方向、退磁风险区和机械保持 |
| Magnetization path | 脉冲磁通路径、局部饱和桥 | 给出磁化线圈到磁体的闭合路径 |
| Rotor bridge | 机械桥宽、应力集中、涡流路径 | 与最高转速强度评审绑定 |
| Thermal path | 磁体、线圈、转子铁心到冷却路径 | 标注温漂影响和热点位置 |
| Position/state reference | resolver/encoder 与磁状态观测基准 | 与控制器 unknown-state 回退一致 |

## 2. 必标注截面

| 截面 | 必含内容 | 用途 |
|---|---|---|
| A-A | 磁化线圈、可变磁体、磁通闭合路径 | 磁化效率评审 |
| B-B | 转子桥、磁体槽、机械保持结构 | 强度/寿命评审 |
| C-C | 热路径、绝缘层、温度采样点 | 热漂移评审 |
| D-D | 传感器基准与磁状态分区 | 状态观测评审 |

## 3. G3 禁止通过项

- 无磁化路径或只画普通 PM rotor。
- 无可变磁体材料/磁化方向标注。
- 无温漂、应力或退磁风险区。
- 无 unknown-state 可观测特征。

## 4. 下版生图/CAD 提示词

Generate an isometric CAD cutaway engineering drawing titled “S07 Memory Motor Variable Magnetization Magnetic Path”. Show rotor core, reversible magnet segments, magnetization coil path, magnetic flux arrows for eight flux states, rotor bridges, mechanical retention, thermal path, temperature sensor locations, and state-observer reference marks. White background, CAD technical style, readable English labels, no poster effects.
