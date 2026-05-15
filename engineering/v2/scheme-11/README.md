# S11 温度 / 退磁 / 安全保护图纸包

方案 ID：`thermal_demag_safety_protection`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S11-PCB-safety_fault_latch-r00.pdf` | missing | 绘制磁钢/油温/绕组温度采样、gate-disable、fault latch 和 ASIL 诊断页 |
| 3D/CAD | `cad/V2-S11-CAD-thermal_sensor_cooling-r00.step` | missing | 绘制温度传感器安装、油路、磁钢热路径和控制器散热 CAD |
| Controller | `controller/V2-S11-CTRL-safety_fault_state_machine-r00.drawio` | missing | 绘制 fault state machine、derating、unknown sensor fallback、gate-disable 映射 |
| BOM/EDA | `bom_eda/V2-S11-BOM-safety_chain-r00.xlsx` | missing | 列出传感器、隔离、诊断、关断和锁存器件 |
| Test/DVP | `test_dvpr/V2-S11-DVP-safety_fault_injection-r00.md` | missing | 定义高温、退磁、传感器开短路、gate-disable fault injection |
| Simulation | `simulation/V2-S11-SIM-thermal_demag_fault_trace-r00.md` | missing | 关联温度、退磁、传感器开短路和 gate-disable 故障注入证据 |

## 现有证据

- EXP-004 和 `sim/safety_limits.py` 已提供简化安全边界模型。

## 当前判断

安全模型已进入数值层，但 PCB 安全链和热传感 CAD 尚未落地。
