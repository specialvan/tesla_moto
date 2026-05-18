# V2-S06 控制器高凸极低 PM 控制图 r00

状态：`draft`。

## 1. 控制图层

| 图层 | 输入 | 输出 | 验收 |
|---|---|---|---|
| High-saliency MTPA | FEA LUT、speed、torque | `id/iq` minimum current | 电流连续性和 torque ripple 可接受 |
| MTPV/high-speed | voltage margin、Vdc、speed | 高速弱磁轨迹 | 不突破 S11 退磁边界 |
| Demag guard | temp、id、magnet grade | `id_min(T)` | 与 S11 共用边界 |
| Thermal derating | winding/oil/magnet temp | torque/current limit | 与 CAD 冷却路径一致 |
| Scorecard output | efficiency、cost、risk | recommend/stop | 区分研究排名和工程推荐 |

## 2. 标定参数

| 标定名 | 初值/字段 | 说明 |
|---|---|---|
| `SAL_RATIO_MIN_GATE` | 来自 r02 参数 sheet | 高凸极最低门槛 |
| `PM_FRACTION_MAX_GATE` | 来自 r02 参数 sheet | 低 PM 占比门槛 |
| `DEMAG_MARGIN_MIN_PCT` | 与 S11 对齐 | 退磁安全门槛 |
| `TORQUE_RIPPLE_MAX_PCT` | DVP 绑定 | NVH 门槛 |
| `PEAK_TORQUE_MIN_NM` | 基线绑定 | 不牺牲峰值能力 |

## 3. 下版生图提示词

生成 S06 high-saliency low-PM control map diagram，包含 FEA Flux LUT、MTPA、MTPV/high-speed、Demag Guard、Thermal Derating、Drive-cycle Scorecard、Engineering Gate Decision。节点用英文标注，红色显示 stop conditions，蓝色显示 control data flow，白底工程风格。