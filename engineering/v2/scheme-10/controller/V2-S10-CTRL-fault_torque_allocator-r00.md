# V2-S10 控制器容错转矩分配草案 r00

方案：S10 多相 / 相组控制  
状态：`draft`，用于控制评审和 HIL 输入，不替代量产代码。

## 1. 状态机

| 状态 | 进入条件 | 退出条件 | 输出限制 |
|---|---|---|---|
| Six-phase nominal | 六相采样与 gate 全有效 | 任一相故障或热/NVH guard | αβ 转矩 + xy 抑制 |
| Single-phase fault detect | 相电流/电压/gate feedback 异常 | 故障确认或误报清除 | 限制转矩斜率 |
| Phase isolate | 对故障相 gate-disable/cutoff | 切除确认或超时 | 禁止故障相再使能 |
| Fault torque allocation | 剩余相重分配转矩 | 热/NVH/电流约束触发 | 50% derate 初值 |
| Phase-group degraded | 单相或相组容错运行 | 服务复位或二次故障 | 限制 xy 谐波和热点 |
| Fault shutdown | 多相故障、S11 request | 维修复位 | 安全关断 |

## 2. 输入信号

- `phase_current_a[6]`
- `phase_voltage_v[6]`
- `gate_feedback[6]`
- `phase_temp_c[6]`
- `alpha_beta_torque_request`
- `xy_harmonic_current`
- `nvh_guard_active`
- `safety_request`

## 3. 标定参数

| 标定名 | 初值 | 单位 | 说明 |
|---|---:|---|---|
| `PHASE_COUNT` | 6 | count | 六相系统 |
| `PHASE_CURRENT_LIMIT_A` | 130 | A | 单相电流初值 |
| `FAULT_DERATE_LATENCY_MS` | 2 | ms | 故障到降额目标 |
| `DEGRADED_TORQUE_LIMIT_PCT` | 50 | % | 容错转矩上限初值 |
| `XY_CURRENT_LIMIT_A` | 10 | A | 谐波子空间上限初值 |
| `PHASE_TEMP_BALANCE_C` | 10 | °C | 相间温差目标 |

## 4. 验收闭环

- EXP-009 可用电流降额代理不能证明多相硬件、谐波和 NVH 可行。
- 故障事件必须记录 `fault_phase/isolation_time/remaining_phase_currents/xy_current/torque_derate/temp_balance`。
- 二次故障和 S11 safety request 必须优先于容错收益。

## 5. 下版生图提示词

Generate a controller state-machine and block diagram titled “S10 Six-Phase Fault-Tolerant Torque Allocator”. Include Clarke transform for alpha-beta and xy subspaces, six-phase current feedback, fault phase detector, per-phase isolation, remaining-phase current allocator, torque derate, xy harmonic limiter, thermal balancer, NVH guard, service reset, and S11 safety request. Use red safety paths and blue torque-control paths.
