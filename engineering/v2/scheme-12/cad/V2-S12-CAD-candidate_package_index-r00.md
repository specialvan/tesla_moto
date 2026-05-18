# V2-S12 CAD/封装候选索引 r00

状态：`draft`。

## 1. CAD 版本索引

| 候选 | CAD/封装证据 | 当前状态 | Pareto 惩罚 |
|---|---|---|---|
| S01 | `scheme-01/cad/V2-S01-CAD-sensor_busbar_layout-r00.md` | draft | low-medium |
| S02 | `scheme-02/cad/V2-S02-CAD-controller_packaging-r00.md` | draft | low-medium |
| S03 | `scheme-03/cad/V2-S03-CAD-inverter_power_stage-r00.md` | draft | medium: EMC/thermal |
| S04 | `scheme-04/cad/V2-S04-CAD-fea_geometry_source-r00.md` | draft | medium: FEA source |
| S05 | `scheme-05/cad/V2-S05-CAD-rotor_barrier_bridge-r00.md` | draft | high until real FEA CAD |
| S06 | `scheme-06/cad/V2-S06-CAD-pmasynrm_rotor_stator-r00.md` | draft | high until real topology CAD |
| S07~S10 | CAD topology missing | missing | research only |
| S11 | `scheme-11/cad/V2-S11-CAD-thermal_sensor_cooling-r00.md` | draft | mandatory safety overlay |

## 2. 封装评分字段

- mass delta
- axial/radial envelope delta
- cooling interface maturity
- HV/LV serviceability
- manufacturing complexity
- safety sensor accessibility

## 3. 下版生图提示词

生成 S12 candidate packaging evidence matrix，比较 S01~S12 的 CAD evidence、mass、package envelope、cooling interface、manufacturing complexity、serviceability、maturity penalty。白底工程表格和小型拓扑缩略图布局，英文标签。