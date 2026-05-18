# V2-S09 控制器绕组重构状态机草案 r00

方案：S09 绕组重构  
状态：`draft`，用于控制评审和 HIL 输入，不替代量产代码。

## 1. 状态机

| 状态 | 进入条件 | 退出条件 | 输出限制 |
|---|---|---|---|
| Config A active | 当前绕组构型确认 | 收益满足且切换请求有效 | 常规转矩控制 |
| Switch request | 目标构型收益通过 | 进入零转矩窗口或撤销 | 限制转矩斜率 |
| Zero-torque window | torque request 接近 0 且相电流衰减 | 电流/电压满足或超时 | 禁止大转矩输出 |
| Open old path | 旧路径开关断开命令 | 位置反馈确认 | 检查 arc/残压 |
| Close new path | 新路径闭合命令 | 位置反馈和环流确认 | 环流 <5 A |
| Config B active | 新构型确认 | 新切换请求或故障 | 更新 Ke/Kt/Ld/Lq map |
| Illegal-state fallback | 反馈矛盾、stuck、环流或 arc | 维修/复位 | 断开可控开关并降扭 |

## 2. 输入信号

- `target_winding_config`
- `torque_request_nm`
- `phase_current_a`
- `switch_position_feedback`
- `switch_voltage_v`
- `circulating_current_a`
- `arc_detected`
- `hvil_valid`
- `safety_request`

## 3. 标定参数

| 标定名 | 初值 | 单位 | 说明 |
|---|---:|---|---|
| `SWITCH_WINDOW_MIN_MS` | 50 | ms | 最短零转矩切换窗口 |
| `SWITCH_WINDOW_MAX_MS` | 200 | ms | 最长切换窗口 |
| `CIRC_CURRENT_LIMIT_A` | 5 | A | 环流上限 |
| `INTERLOCK_MAX_LATENCY_MS` | 1 | ms | 非法状态互锁目标 |
| `TORQUE_ZERO_THRESH_NM` | 5 | Nm | 零转矩窗口阈值初值 |
| `STUCK_SWITCH_TIMEOUT_MS` | 20 | ms | 开关反馈超时初值 |

## 4. 验收闭环

- EXP-008 静态 Ke/Kt 代理不能证明切换瞬态安全。
- 每次切换必须记录 `from_config/to_config/torque/current/switch_feedback/arc/circulating_current/result`。
- 非法状态回退必须优先于效率或高速收益。

## 5. 下版生图提示词

Generate a controller state-machine diagram titled “S09 Winding Reconfiguration State Machine”. Nodes: Config A Active, Switch Request, Zero-Torque Window, Open Old Path, Close New Path, Config B Active, Illegal-State Fallback, Fault Shutdown. Transitions labeled by torque request, phase current, switch feedback, switch voltage, circulating current, arc detection, HVIL, and S11 safety request. Use red fallback arrows and blue normal switching arrows.
