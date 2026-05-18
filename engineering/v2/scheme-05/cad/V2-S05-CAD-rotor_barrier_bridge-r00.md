# V2-S05 CAD/FEA 转子 barrier/bridge 草案 r00

方案：S05 磁路饱和协同设计  
状态：`draft`，用于几何/FEA/制造评审输入，不替代 STEP、Maxwell、Motor-CAD 或制造图。

## 1. 几何生产参数

| 参数 | r00 字段 | 评审意义 |
|---|---|---|
| `barrier_count` | 2~4 候选 | 决定 Ld/Lq、应力和制造复杂度 |
| `bridge_width_mm` | 候选范围待 FEA | 控制机械强度和漏磁 |
| `rib_width_mm` | 候选范围待 FEA | 控制高速应力和饱和程度 |
| `magnet_arc_deg` | 与 S06/S11 共享 | 影响退磁和磁链 |
| `airgap_mm` | 与基线电机绑定 | 影响转矩脉动和 NVH |
| `stack_length_mm` | 与热/质量绑定 | 影响功率密度和成本 |

## 2. CAD 必含视图

| 视图 | 必含对象 | 输出用途 |
|---|---|---|
| Rotor cross-section | barrier、bridge、rib、magnet pocket、shaft | Maxwell/Motor-CAD 几何源 |
| Stress overlay | 高速应力热点、bridge 安全系数 | 机械 G3/G4 |
| Flux density overlay | 饱和区、漏磁区、磁桥饱和 | LUT 回灌 |
| Manufacturing section | 冲片最小宽度、倒角、装配定位 | 工艺评审 |

## 3. FEA 回灌要求

- 输出 `lambda_d/id/iq`、`lambda_q/id/iq`、torque ripple、iron loss、demag margin。
- 每个候选几何必须有版本号，不能用口头“优化后几何”。
- FEA LUT 必须绑定控制器 scorecard，禁止只用 `Ld/Lq` 参数缩放晋级。

## 4. 停止条件

1. bridge/rib 高速应力安全系数不足。
2. torque ripple 或 NVH 超出基线可接受范围。
3. FEA LUT 回灌后 drive-cycle 收益消失。
4. 退磁裕度不满足 S11 温度边界。

## 5. 下版生图提示词

生成 IPMSM rotor barrier/bridge CAD+FEA 工程图，主题为“S05 magnetic saturation co-design geometry”。包含 rotor cross-section、flux density overlay、stress hotspot overlay、bridge width、rib width、magnet pocket、airgap、manufacturing minimum web。白底工程图，英文标注，四宫格布局，强调 FEA LUT feedback and no parameter-scaling shortcut。