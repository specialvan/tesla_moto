# V2-S08 控制器三变量控制草案 r00

方案：S08 混合励磁  
状态：`draft`，用于控制评审和 HIL 输入，不替代量产代码。

## 1. 控制模式

| 模式 | 进入条件 | 退出条件 | 输出限制 |
|---|---|---|---|
| PM-assist baseline | 励磁不可用或低收益区 | 励磁可用且收益满足 | `if=0` 或保守励磁 |
| Three-variable optimize | `id/iq/if` 优化收益有效 | 热、失励或电压约束触发 | 限制 `if` 斜率和绕组温升 |
| Field weakening assist | 高速电压受限 | 电压裕度恢复或热降额 | 协调 `id` 与 `if` |
| Thermal derate | field winding temp 超限 | 温度回落并滞环确认 | 降低 `if` 上限 |
| Loss-of-field fallback | open/short/失励 latch | 故障清除并重新校验 | 转矩降额，禁用励磁收益 |
| Fault shutdown | S11 safety request | 维修复位 | 关闭 field converter |

## 2. 输入信号

- `id_ref_a`
- `iq_ref_a`
- `if_ref_a`
- `if_measured_a`
- `field_voltage_v`
- `field_winding_temp_c`
- `psi_eff_estimate`
- `loss_of_field_latch`
- `vdc_margin_v`

## 3. 标定参数

| 标定名 | 初值 | 单位 | 说明 |
|---|---:|---|---|
| `IF_MIN_A` | -20 | A | 反向/弱励磁边界 |
| `IF_MAX_A` | 30 | A | 正向励磁边界 |
| `IF_SLEW_A_PER_MS` | 0.5 | A/ms | 励磁电流斜率初值 |
| `FIELD_TEMP_DERATE_C` | 140 | °C | H 级绝缘热降额入口 |
| `LOSS_FIELD_DETECT_MS` | 5 | ms | 失励检测目标 |
| `FALLBACK_TORQUE_DERATE_PCT` | 40 | % | 失励降扭初值 |

## 4. 验收闭环

- EXP-007 的 `psi_eff` 代理只证明趋势，不证明励磁硬件热与可靠性。
- 控制日志必须包含 `id/iq/if/psi_eff/temp/loss_of_field/derate_reason`。
- Loss-of-field fallback 必须优先于效率收益。

## 5. 下版生图提示词

Generate a controller block and state diagram titled “S08 Hybrid Excitation id-iq-if Control”. Include MTPA/FW torque request, three-variable optimizer, field current loop, psi_eff estimator, voltage margin guard, field thermal derate, loss-of-field detector, PM-assist fallback, and S11 safety request. Use English labels, blue normal-control paths, red safety fallback path.
