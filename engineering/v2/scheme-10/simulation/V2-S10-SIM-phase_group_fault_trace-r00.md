# V2-S10 仿真追溯：相组故障容错草案 r00

方案：S10 多相 / 相组控制  
状态：`draft`，用于把多相降额代理升级为容错证据链，不替代 HIL/台架报告。

## 1. 证据链

| 层级 | 输入 | 输出 | 必须回答 |
|---|---|---|---|
| EXP proxy | EXP-009 多相可用电流代理 | derated torque delta | 是否值得进入多相硬件评审 |
| Six-phase model | 六相电机参数、相序 | alpha-beta / xy currents | 谐波子空间是否可控 |
| Fault model | open/short/gate fault | isolation time, torque ripple | <2 ms 降额是否可达 |
| Thermal model | 剩余相电流重分配 | phase temp balance | 50% derate 是否热可持续 |
| NVH model | torque ripple, xy harmonics | NVH risk | 容错运行是否可接受 |
| DVP | 单相/相组故障、热、NVH | gate result | 能否退出研究池 |

## 2. 日志字段

- `fault_phase`
- `fault_type`
- `fault_detect_latency_ms`
- `isolation_time_ms`
- `remaining_phase_current_a[5]`
- `xy_harmonic_current_a`
- `torque_derate_pct`
- `phase_temp_balance_c`

## 3. 当前结论

S10 仍是研究池方案。必须证明六相硬件、每相隔离、xy 谐波抑制、热均衡和 NVH 可接受后，多相降额代理才可进入候选评审。
