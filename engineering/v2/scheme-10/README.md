# S10 多相 / 相组控制图纸包

方案 ID：`multiphase_phase_group_control`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S10-PCB-multiphase_inverter-r00.pdf` | missing | 绘制多相逆变器、相组电流采样、隔离、故障切除和连接器页 |
| 3D/CAD | `cad/V2-S10-CAD-phase_group_packaging-r00.step` | missing | 绘制多相端子、线束、相组布置、热路径和封装 CAD |
| Controller | `controller/V2-S10-CTRL-fault_torque_allocator-r00.drawio` | missing | 绘制 fault torque allocator、谐波子空间和相组降额状态机 |
| BOM/EDA | `bom_eda/V2-S10-BOM-multiphase_powertrain-r00.xlsx` | missing | 列出多相功率模块、采样链、连接器和线束 |
| Test/DVP | `test_dvpr/V2-S10-DVP-multiphase_fault_tolerance-r00.md` | missing | 定义单相/相组故障、谐波、热和 NVH 测试 |
| Simulation | `simulation/V2-S10-SIM-phase_group_fault_trace-r00.md` | missing | 关联相组故障、谐波子空间、热降额和容错收益证据 |

## 现有证据

- EXP-009 有多相相组降额代理实验。

## 当前判断

缺少多相逆变器、相组封装和 fault allocator 图纸，不能只用可用电流降额代理。
