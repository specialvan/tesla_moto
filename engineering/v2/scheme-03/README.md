# S03 SVPWM / 过调制图纸包

方案 ID：`svpwm_overmodulation_voltage_utilization`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S03-PCB-gate_pwm_emc-r00.md` | draft | 已落地栅极驱动、死区、EMI/EMC、相电流采样页级草案；后续转正式 EDA/PDF |
| 3D/CAD | `cad/V2-S03-CAD-inverter_power_stage-r00.md` | draft | 已定义功率模块、DC-link、母排、散热器与屏蔽结构草案；后续转 STEP/CAD |
| Controller | `controller/V2-S03-CTRL-overmodulation_state_machine-r00.md` | draft | 已落地 SVPWM/过调制/六步进入退出状态机草案；后续转 drawio/Simulink |
| BOM/EDA | `bom_eda/V2-S03-BOM-inverter_overmodulation-r00.md` | draft | 已列出 gate driver、功率模块、电容、母排、EMI 元件生产参数字段；后续转 BOM/EDA |
| Test/DVP | `test_dvpr/V2-S03-DVP-thd_emc_nvh-r00.md` | draft | 已落地 THD、EMC、NVH、逆变器损耗与六步热应力测试计划草案 |
| Parameters/r02 | `parameters/V2-S03-PARAM-acceptance-r02.md`、`parameters/V2-S03-PARAM-sim_binding-r02.json` | r02 接入 | 调制生产参数 + 仿真绑定（绑 EXP-005），由 `tests/test_scheme_experiment_acceptance.py` 自动校验 |
| Simulation | `simulation/V2-S03-SIM-overmodulation_loss_trace-r00.md` | draft | 已关联过调制电压利用率、损耗、THD 和 NVH 代理证据边界 |
| Prompts/r03 | `prompts/V2-S03-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- `experiments/exp_005_modulation_factor/summary.json` 有调制因子代理实验。

## 当前判断

当前已具备 r00 Markdown 页级工程图纸草案和 r03 生图提示词，但尚无正式功率级 PCB/CAD/EMC 发布文件，不能宣称完成 EDA/CAD 或台架验证。
