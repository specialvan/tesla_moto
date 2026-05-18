# S11 温度 / 退磁 / 安全保护图纸包

方案 ID：`thermal_demag_safety_protection`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S11-PCB-safety_fault_latch-r00.md` | draft | 已落地温度/退磁安全链、fault latch、gate-disable 和故障分类页面级草案 |
| 3D/CAD | `cad/V2-S11-CAD-thermal_sensor_cooling-r00.md` | draft | 已落地磁钢/绕组/油温传感、冷却路径、控制器散热和维修边界草案 |
| Controller | `controller/V2-S11-CTRL-safety_fault_state_machine-r00.drawio` | draft | 已落地热/退磁 warning、derating、unknown sensor fallback 和 gate-disable 状态机草图 |
| BOM/EDA | `bom_eda/V2-S11-BOM-safety_chain-r00.md` | draft | 已落地温度传感、安全锁存、gate-disable、隔离和故障回读器件族风险草案 |
| Test/DVP | `test_dvpr/V2-S11-DVP-safety_fault_injection-r00.md` | draft | 已落地温度/退磁、传感器开短路、unknown fallback、gate-disable 和 fault latch 计划草案 |
| Parameters/r02 | `parameters/V2-S11-PARAM-acceptance-r02.md`、`parameters/V2-S11-PARAM-sim_binding-r02.json` | r02 接入 | 生产参数 + 仿真绑定（120 °C 高温退磁场景），由 `tests/test_scheme_p0_lut_acceptance.py` 自动校验 |
| Simulation | `simulation/V2-S11-SIM-thermal_demag_fault_trace-r00.md` | missing | 关联温度、退磁、传感器开短路和 gate-disable 故障注入证据 |

## 现有证据

- EXP-004 和 `sim/safety_limits.py` 已提供简化安全边界模型。

## 当前判断

安全模型已进入数值层，但 PCB 安全链和热传感 CAD 尚未落地。
