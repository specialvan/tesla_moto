# V2-S06 CAD PMaSynRM 转子/定子拓扑草案 r00

方案：S06 PMaSynRM / 高凸极低永磁占比  
状态：`draft`，用于拓扑/FEA/制造评审输入，不替代正式 CAD/FEA 文件。

## 1. 拓扑生产参数

| 参数 | r00 目标字段 | 评审意义 |
|---|---|---|
| `pm_fraction_pct` | 相对基线降低 | 成本、退磁、峰值转矩权衡 |
| `saliency_ratio_lq_ld` | 目标高于基线 | 决定磁阻转矩贡献 |
| `barrier_layer_count` | 2~4 候选 | 决定凸极、应力和制造复杂度 |
| `bridge_width_mm` | FEA 候选 | 决定高速机械强度 |
| `hairpin_slot_fill_pct` | 与热模型绑定 | 决定铜耗与制造可行性 |
| `cooling_interface` | oil jacket / direct oil candidate | 决定低 PM 高电流热边界 |

## 2. 必含 CAD 视图

| 视图 | 内容 | Gate 用途 |
|---|---|---|
| Rotor topology | low PM pocket、barrier、bridge、rib、shaft | G3 拓扑评审 |
| Stator/hairpin slot | slot fill、端部空间、绝缘 | G3 制造/热评审 |
| Stress map | bridge/rib 高速应力 | G4 机械安全 |
| Demag map | 低 PM 退磁热点 | G4 S11 安全边界 |
| Cooling section | winding、stator、housing heat path | G4 热边界 |

## 3. 禁止误判

- 不能把 EXP-003 的高凸极参数组合直接写成真实 PMaSynRM 设计成立。
- 低 PM 成本收益必须同时满足峰值转矩、NVH、热和退磁约束。
- 若 hairpin 槽满率或端部空间无法制造，scorecard 必须停止。

## 4. 下版生图提示词

生成 PMaSynRM rotor-stator CAD engineering drawing，主题为“S06 high-saliency low-PM topology”。包含 low PM magnet pockets、multi-layer flux barriers、bridge/rib stress map、hairpin stator slots、cooling path、demag hotspot overlay。白底四视图工程图，英文标注，强调 saliency ratio、PM fraction、stress safety factor、demag margin。