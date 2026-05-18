# S06 PMaSynRM / 高凸极低永磁占比图纸包

方案 ID：`pmasynrm_high_saliency_low_pm`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S06-PCB-pmasynrm_control_inputs-r00.pdf` | missing | 定义高凸极控制和退磁诊断输入页 |
| 3D/CAD | `cad/V2-S06-CAD-pmasynrm_rotor_stator-r00.md` | draft | 已绘制 PM fraction、barrier、bridge、扁线槽型 CAD 页级草案；后续转 STEP/FEA |
| Controller | `controller/V2-S06-CTRL-saliency_control_map-r00.md` | draft | 已绘制高凸极 MTPA/MTPV 和低 PM 退磁边界图草案；后续转 drawio/Simulink |
| BOM/EDA | `bom_eda/V2-S06-BOM-low_pm_topology-r00.md` | draft | 已列出低 PM 磁钢、叠片、扁线、冷却传感 BOM 生产字段；后续转正式 BOM |
| Test/DVP | `test_dvpr/V2-S06-DVP-pmasynrm_validation-r00.md` | draft | 已落地 torque ripple、应力、低 PM 退磁、热、NVH 验证计划草案 |
| Parameters/r02 | `parameters/V2-S06-PARAM-acceptance-r02.md`、`parameters/V2-S06-PARAM-sim_binding-r02.json` | r02 接入 | 凸极 / PM fraction 阈值 + 仿真绑定（共享 EXP-003），由 `tests/test_scheme_experiment_acceptance.py` 自动校验 |
| Simulation | `simulation/V2-S06-SIM-saliency_low_pm_trace-r00.md` | draft | 已关联高凸极低永磁拓扑、转矩脉动、退磁和热约束证据 |
| Prompts/r03 | `prompts/V2-S06-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- 当前只有路线级 playbook 和 scorecard 要求。

## 当前判断

当前已具备 r00 Markdown 页级拓扑 CAD、控制图、材料 BOM 和仿真追溯草案，但尚无正式拓扑 CAD/FEA/材料验证发布文件，不能宣称低 PM 方案工程成立。
