# S03 SVPWM / 过调制图纸包

方案 ID：`svpwm_overmodulation_voltage_utilization`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S03-PCB-gate_pwm_emc-r00.pdf` | missing | 绘制栅极驱动、死区、EMI/EMC、相电流采样页 |
| 3D/CAD | `cad/V2-S03-CAD-inverter_power_stage-r00.step` | missing | 定义功率模块、DC-link、母排、散热器与屏蔽结构 |
| Controller | `controller/V2-S03-CTRL-overmodulation_state_machine-r00.drawio` | missing | 绘制 SVPWM/过调制/六步进入退出状态机 |
| BOM/EDA | `bom_eda/V2-S03-BOM-inverter_overmodulation-r00.xlsx` | missing | 列出 gate driver、功率模块、电容、母排、EMI 元件 |
| Test/DVP | `test_dvpr/V2-S03-DVP-thd_emc_nvh-r00.md` | missing | 定义 THD、EMC、NVH、逆变器损耗和热测试 |
| Simulation | `simulation/V2-S03-SIM-overmodulation_loss_trace-r00.md` | missing | 关联过调制电压利用率、损耗、THD 和 NVH 代理证据 |

## 现有证据

- `experiments/exp_005_modulation_factor/summary.json` 有调制因子代理实验。

## 当前判断

当前只具备数值代理和报告说明，尚无功率级 PCB/CAD/EMC 图纸。
