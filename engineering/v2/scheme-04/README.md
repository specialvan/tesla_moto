# S04 非线性磁链 LUT 图纸包

方案 ID：`nonlinear_flux_lut`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S04-PCB-lut_observer_inputs-r00.md` | draft | 已落地 LUT 观测输入、边界检查、fallback 诊断和误差预算页面级草案 |
| 3D/CAD | `cad/V2-S04-CAD-fea_geometry_source-r00.md` | draft | 已落地 FEA 几何源、dq 坐标、材料表、网格边界和传感器位置版本绑定草案 |
| Controller | `controller/V2-S04-CTRL-flux_lut_interpolation-r00.drawio` | draft | 已落地 LUT 边界检查、双线性插值、误差监控和 fallback 草图 |
| BOM/EDA | `bom_eda/V2-S04-BOM-lut_sensor_chain-r00.md` | draft | 已落地电流、位置、温度、Vdc 和诊断存储器件族风险草案 |
| Test/DVP | `test_dvpr/V2-S04-TEST-flux_lut_correlation-r00.md` | draft | 已落地 LUT 边界、插值一致性、FEA 版本绑定、台架相关性和 fallback 计划草案 |
| Parameters/r02 | `parameters/V2-S04-PARAM-acceptance-r02.md`、`parameters/V2-S04-PARAM-sim_binding-r02.json` | r02 接入 | 生产参数 + 仿真绑定（驱动 nonlinear_flux_lut 分支），由 `tests/test_scheme_p0_lut_acceptance.py` 自动校验 |
| Simulation | `simulation/V2-S04-SIM-flux_lut_correlation-r00.md` | missing | 关联非线性磁链 LUT、插值边界和 FEA/实测回灌证据 |

## 现有证据

- `models/flux_lut_sample.json` 和 EXP-006 提供 synthetic LUT 数值证明。

## 当前判断

LUT 数值链已存在，但真实 FEA/CAD 几何源与传感器图纸尚未落地。
