# V2-S07 仿真追溯：磁化状态草案 r00

方案：S07 可变磁化状态 / Memory Motor  
状态：`draft`，用于把代理实验升级为磁状态证据链，不替代 FEA/HIL/台架报告。

## 1. 证据链

| 层级 | 输入 | 输出 | 必须回答 |
|---|---|---|---|
| EXP proxy | EXP-002 磁链缩放代理 | torque/efficiency delta | 收益是否值得进入硬件评审 |
| Magnetic FEA | 可逆磁体 B-H、线圈脉冲 | post-pulse flux state | 8 档状态是否可分辨 |
| Pulse circuit | 电容、开关、线圈参数 | current/energy/thermal stress | 1000 A/50 μs 是否安全 |
| Thermal drift | 磁体/线圈温度 | state retention error | 温漂是否触发 fallback |
| HIL controller | 状态机与观测器 | unknown-state handling | 未知状态是否降扭安全 |
| DVP | 脉冲、保持、寿命 | gate result | 能否退出研究池 |

## 2. 日志字段

- `requested_flux_state`
- `estimated_flux_state`
- `state_confidence`
- `pulse_peak_current_a`
- `pulse_energy_j`
- `magnet_temp_c`
- `retention_time_s`
- `unknown_state_fallback_active`

## 3. 当前结论

S07 仍是研究池方案。只有当磁化脉冲硬件、磁状态观测、温漂保持和寿命循环均形成闭环证据后，才能从 `psi_f` 代理升级为工程候选。
