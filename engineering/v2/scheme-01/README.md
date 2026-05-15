# S01 负 d 轴弱磁图纸包

方案 ID：`negative_d_axis_field_weakening`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S01-PCB-sensing_fault_path-r00.pdf` | missing | 绘制电流/Vdc/温度采样与 gate-disable/fault latch 页 |
| 3D/CAD | `cad/V2-S01-CAD-sensor_busbar_layout-r00.step` | missing | 定义母排、传感器安装和热路径 |
| Controller | `controller/V2-S01-CTRL-field_weakening_state_machine-r00.drawio` | draft | 已落地弱磁、`id_min(T,fault)`、降额和 fault fallback 状态机草图 |
| BOM/EDA | `bom_eda/V2-S01-BOM-sensing_fault_components-r00.xlsx` | missing | 列出采样链、隔离和故障锁存器件 |
| Test/DVP | `test_dvpr/V2-S01-DVP-fw_fault_injection-r00.md` | missing | 定义高温、低压、高速、传感器故障注入 |
| Simulation | `simulation/V2-S01-SIM-fw_boundary_trace-r00.md` | missing | 关联控制 LUT、电压/电流/退磁边界仿真证据 |

## 现有证据

- `reports/scheme_driver_power_protocol_diagrams.md` 已有驱动、上电和协议 Mermaid 图。
- `reports/scheme_bom_eda_integration_design.md` 已有架构级 BOM/EDA 说明。

## 当前判断

已有图纸包落点，但正式 PCB、3D/CAD、控制器图和 DVP&R 文件尚未落地。
