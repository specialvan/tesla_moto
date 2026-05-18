# V2-S07 控制器磁状态机草案 r00

方案：S07 可变磁化状态 / Memory Motor  
状态：`draft`，用于控制评审和 HIL 输入，不替代量产代码。

## 1. 状态机

| 状态 | 进入条件 | 退出条件 | 输出限制 |
|---|---|---|---|
| Flux known | 磁状态观测置信度有效 | 置信度下降或温漂超限 | 允许按当前 flux map 控制 |
| Magnetize request | 工况收益满足且安全互锁有效 | 脉冲窗口关闭或请求撤销 | 锁定牵引转矩变化率 |
| Pulse armed | 预充完成、traction gate disabled | 任一互锁失效 | 禁止牵引 PWM |
| Pulse fire | 脉冲开关执行 | 达到电流/时间/能量上限 | 峰值 1000 A、50 μs 初值 |
| Verify state | 脉冲结束后观测磁状态 | 状态确认或超时 | 不允许立即大转矩阶跃 |
| Unknown-state fallback | 状态不可信、温漂或传感异常 | 重新识别完成 | 降扭并使用保守 flux map |

## 2. 输入信号

- `flux_state_estimate`
- `flux_state_confidence`
- `magnet_temp_c`
- `pulse_current_a`
- `coil_voltage_v`
- `traction_gate_disabled`
- `hvil_valid`
- `pulse_life_count`

## 3. 标定参数

| 标定名 | 初值 | 单位 | 说明 |
|---|---:|---|---|
| `FLUX_STATE_LEVELS` | 8 | count | 磁状态档位 |
| `PULSE_PEAK_CURRENT_A` | 1000 | A | 脉冲峰值初值 |
| `PULSE_WIDTH_US` | 50 | μs | 脉宽初值 |
| `PULSE_ENERGY_LIMIT_J` | 100 | J | 单脉冲能量上限 |
| `INTERLOCK_MAX_LATENCY_MS` | 1 | ms | 硬件互锁响应目标 |
| `UNKNOWN_STATE_DERATE_PCT` | 50 | % | 未知状态降额初值 |

## 4. 验收闭环

- EXP-002 只能作为磁链缩放代理，不证明可逆磁化硬件可行。
- 每次脉冲必须记录 `pre_state/requested_state/post_state/confidence/current/energy/temp/life_count`。
- Unknown-state fallback 必须优先于效率收益。

## 5. 下版生图提示词

Generate a controller state-machine diagram titled “S07 Memory Motor Flux State Machine”. Nodes: Flux Known, Magnetize Request, Pulse Armed, Pulse Fire, Verify State, Unknown-State Fallback, Fault Shutdown. Transitions labeled by flux confidence, magnet temperature, pulse current, coil voltage, traction gate disabled, HVIL, life counter, and S11 safety request. Use blue normal-control arrows and red safety fallback arrows.
