# V2-S12 PCB 候选版本索引 r00

方案：S12 工况加权效率 / Pareto 选择  
状态：`draft`，用于候选证据追溯，不替代任何候选方案的真实 PCB 发布。

## 1. 候选 PCB 版本表

| 候选 | PCB/硬件证据 | 当前状态 | 可进入 Pareto 权重 |
|---|---|---|---|
| S01 negative d-axis FW | `scheme-01/pcb/V2-S01-PCB-sensing_fault_path-r00.md` | draft | 可作为 P0 控制候选，但需 G4 硬件评审 |
| S02 MTPA/FW/MTPV | `scheme-02/pcb/V2-S02-PCB-control_io_map-r00.md` | draft | 可作为主线控制候选 |
| S03 overmodulation | `scheme-03/pcb/V2-S03-PCB-gate_pwm_emc-r00.md` | draft | 需 EMC/NVH 风险惩罚 |
| S04 nonlinear flux LUT | `scheme-04/pcb/V2-S04-PCB-lut_observer_inputs-r00.md` | draft | 需采样精度误差惩罚 |
| S05 saturation co-design | sensor interface pending | indexed | 不得作为硬件成熟候选 |
| S06 PMaSynRM | sensor/thermal interface pending | indexed | 不得作为硬件成熟候选 |
| S07~S10 research pool | hardware topology missing | missing/indexed | 仅研究排名，不给工程推荐 |
| S11 safety | `scheme-11/pcb/V2-S11-PCB-safety_fault_latch-r00.md` | draft | 所有候选必须复用 |

## 2. Pareto 规则

- 没有 PCB/硬件版本号的候选只能进入 research rank。
- 任何候选若不绑定 S11 safety chain，工程推荐权重置零。
- PCB 状态低于 `draft` 时，成本/效率收益必须加成熟度惩罚。

## 3. 下版生图提示词

生成 S12 candidate PCB evidence index matrix，展示 S01~S12 candidate rows 和 columns: PCB evidence, CAD evidence, BOM evidence, DVP evidence, maturity penalty, recommendation allowed。白底工程表格，英文标签，红色标出 missing evidence。