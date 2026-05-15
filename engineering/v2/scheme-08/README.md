# S08 混合励磁图纸包

方案 ID：`hybrid_excitation`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S08-PCB-field_excitation_converter-r00.pdf` | missing | 绘制励磁 DC/DC、field current sensing、loss-of-field 和隔离保护页 |
| 3D/CAD | `cad/V2-S08-CAD-field_winding_package-r00.step` | missing | 绘制励磁绕组、滑环/无刷励磁、冷却、绝缘和封装 CAD |
| Controller | `controller/V2-S08-CTRL-three_variable_control-r00.drawio` | missing | 绘制 `id/iq/if` 三变量控制和 loss-of-field fallback |
| BOM/EDA | `bom_eda/V2-S08-BOM-field_excitation_hardware-r00.xlsx` | missing | 列出励磁功率器件、绕组、绝缘、连接器和传感器 |
| Test/DVP | `test_dvpr/V2-S08-DVP-hybrid_excitation-r00.md` | missing | 定义励磁热、loss-of-field、三变量优化和台架测试 |
| Simulation | `simulation/V2-S08-SIM-field_excitation_trace-r00.md` | missing | 关联励磁电流、励磁损耗、loss-of-field 和热约束证据 |

## 现有证据

- EXP-007 有等效 `psi_eff` 代理实验。

## 当前判断

缺少励磁功率硬件和绕组 CAD，不能只靠 `psi_eff` 代理晋级。
