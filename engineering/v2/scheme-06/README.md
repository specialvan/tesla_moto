# S06 PMaSynRM / 高凸极低永磁占比图纸包

方案 ID：`pmasynrm_high_saliency_low_pm`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S06-PCB-pmasynrm_control_inputs-r00.pdf` | missing | 定义高凸极控制和退磁诊断输入页 |
| 3D/CAD | `cad/V2-S06-CAD-pmasynrm_rotor_stator-r00.step` | missing | 绘制 PM fraction、barrier、bridge、扁线槽型 CAD |
| Controller | `controller/V2-S06-CTRL-saliency_control_map-r00.drawio` | missing | 绘制高凸极 MTPA/MTPV 和低 PM 退磁边界图 |
| BOM/EDA | `bom_eda/V2-S06-BOM-low_pm_topology-r00.xlsx` | missing | 列出低 PM 磁钢、叠片、扁线、冷却传感 BOM |
| Test/DVP | `test_dvpr/V2-S06-DVP-pmasynrm_validation-r00.md` | missing | 定义 torque ripple、应力、退磁、热、NVH 验证 |
| Simulation | `simulation/V2-S06-SIM-saliency_low_pm_trace-r00.md` | missing | 关联高凸极低永磁拓扑、转矩脉动、退磁和热约束证据 |

## 现有证据

- 当前只有路线级 playbook 和 scorecard 要求。

## 当前判断

尚无拓扑 CAD、材料 BOM 和风险测试图纸，不能宣称低 PM 方案工程成立。
