# S05 磁路饱和协同设计图纸包

方案 ID：`magnetic_saturation_codesign`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S05-PCB-saturation_sensor_inputs-r00.pdf` | missing | 定义饱和观测所需采样输入和诊断接口 |
| 3D/CAD | `cad/V2-S05-CAD-rotor_barrier_bridge-r00.md` | draft | 已绘制 barrier、bridge、磁桥、叠片和应力约束页级草案；后续转 STEP/FEA |
| Controller | `controller/V2-S05-CTRL-saturation_scorecard-r00.md` | draft | 已绘制 FEA LUT 回灌和候选几何 scorecard 流程草案；后续转 drawio/Simulink |
| BOM/EDA | `bom_eda/V2-S05-BOM-magnetic_stack-r00.md` | draft | 已列出硅钢、磁钢、转子工艺和传感器接口生产字段；后续转正式 BOM |
| Test/DVP | `test_dvpr/V2-S05-DVP-saturation_codesign-r00.md` | draft | 已落地 FEA correlation、应力、铁损、退磁、NVH 联合验证计划草案 |
| Parameters/r02 | `parameters/V2-S05-PARAM-acceptance-r02.md`、`parameters/V2-S05-PARAM-sim_binding-r02.json` | r02 接入 | candidate scorecard 阈值 + 仿真绑定（绑 EXP-003），由 `tests/test_scheme_experiment_acceptance.py` 自动校验 |
| Simulation | `simulation/V2-S05-SIM-saturation_score_trace-r00.md` | draft | 已关联饱和协同设计、FEA、铁耗、退磁和结构约束证据 |
| Prompts/r03 | `prompts/V2-S05-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- `claude-review/docs/2026-05-15/v2_scheme_engineering_playbook.md` 已定义 candidate geometry → FEA LUT → scorecard 路径。

## 当前判断

当前已具备 r00 Markdown 页级 CAD/FEA、scorecard、BOM 和仿真追溯草案，但尚无真实候选几何 CAD/FEA 发布文件，不能晋级工程推荐。
