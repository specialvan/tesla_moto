# V2-S09 仿真追溯：绕组切换瞬态草案 r00

方案：S09 绕组重构  
状态：`draft`，用于把静态构型代理升级为切换瞬态证据链，不替代台架报告。

## 1. 证据链

| 层级 | 输入 | 输出 | 必须回答 |
|---|---|---|---|
| EXP proxy | EXP-008 Ke/Kt/Ld/Lq 构型代理 | efficiency/torque delta | 是否值得进入开关矩阵评审 |
| Circuit transient | winding L/R、开关模型、snubber | overvoltage, arc energy | 切换是否安全 |
| Control HIL | 零转矩窗口、反馈、互锁 | switching success/fallback | 非法状态能否回退 |
| Thermal model | contact resistance, switch loss | switch temp, connector temp | 重复切换是否过热 |
| NVH model | torque interruption, current transient | jerk/NVH delta | 切换窗口是否可接受 |
| DVP | open/short/stuck/arc/circulation | gate result | 能否退出研究池 |

## 2. 日志字段

- `from_config`
- `to_config`
- `switch_window_ms`
- `phase_current_before_a`
- `switch_voltage_peak_v`
- `circulating_current_a`
- `arc_detected`
- `illegal_state_fallback_active`

## 3. 当前结论

S09 仍是研究池方案。必须证明零转矩窗口、开关电弧、环流、stuck fault 和热寿命闭环后，静态绕组构型收益才可进入候选评审。
