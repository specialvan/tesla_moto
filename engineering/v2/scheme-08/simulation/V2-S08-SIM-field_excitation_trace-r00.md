# V2-S08 仿真追溯：励磁链草案 r00

方案：S08 混合励磁  
状态：`draft`，用于把 `psi_eff` 代理升级为励磁硬件证据链，不替代 FEA/HIL/台架报告。

## 1. 证据链

| 层级 | 输入 | 输出 | 必须回答 |
|---|---|---|---|
| EXP proxy | EXP-007 `psi_eff` 代理 | efficiency/torque delta | 是否值得进入励磁硬件评审 |
| Magnetic FEA | `id/iq/if`、磁路几何 | flux map, saturation | 三变量收益是否稳定 |
| Converter model | 48 V、field winding、PWM | if ripple, loss, fault response | 失励 <5 ms 是否可检出 |
| Thermal model | 绕组损耗、冷却路径 | field temp, derate dwell | H 级绝缘是否满足 |
| HIL controller | 三变量控制与 fallback | torque continuity | 失励是否安全降扭 |
| DVP | 热、失励、台架相关性 | gate result | 能否退出研究池 |

## 2. 日志字段

- `id_a`
- `iq_a`
- `if_ref_a`
- `if_measured_a`
- `psi_eff_estimate`
- `field_winding_temp_c`
- `loss_of_field_detected`
- `fallback_torque_derate_pct`

## 3. 当前结论

S08 仍是研究池方案。励磁功率硬件、绕组封装、热降额和 loss-of-field 回退闭环前，不能把 `psi_eff` 代理收益视为工程可行性。
