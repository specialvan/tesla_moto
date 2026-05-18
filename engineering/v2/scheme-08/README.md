# S08 混合励磁图纸包

方案 ID：`hybrid_excitation`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S08-PCB-field_excitation_converter-r00.md` | draft | 已落地励磁 DC/DC、field current sensing、loss-of-field、隔离保护页级草案 |
| 3D/CAD | `cad/V2-S08-CAD-field_winding_package-r00.md` | draft | 已落地励磁绕组、滑环/无刷励磁、冷却、绝缘和封装 CAD 草案 |
| Controller | `controller/V2-S08-CTRL-three_variable_control-r00.md` | draft | 已落地 `id/iq/if` 三变量控制、热降额和 loss-of-field fallback 草案 |
| BOM/EDA | `bom_eda/V2-S08-BOM-field_excitation_hardware-r00.md` | draft | 已落地励磁功率器件、绕组、绝缘、连接器、传感器和保护器件 BOM 草案 |
| Test/DVP | `test_dvpr/V2-S08-DVP-hybrid_excitation-r00.md` | draft（research pool） | 已落地励磁热、loss-of-field、三变量优化与台架相关性计划草案 |
| Parameters/r02 | `parameters/V2-S08-PARAM-acceptance-r02.md`、`parameters/V2-S08-PARAM-sim_binding-r02.json` | r02 接入（research pool） | 励磁占位参数 + 仿真绑定（绑 EXP-007），由 `tests/test_scheme_experiment_acceptance.py` 自动校验 |
| Simulation | `simulation/V2-S08-SIM-field_excitation_trace-r00.md` | draft | 已落地励磁电流、励磁损耗、loss-of-field、热约束和 HIL fallback 追溯草案 |
| Prompt/r03 | `prompts/V2-S08-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- EXP-007 有等效 `psi_eff` 代理实验。

## 当前判断

缺少励磁功率硬件和绕组 CAD，不能只靠 `psi_eff` 代理晋级。
