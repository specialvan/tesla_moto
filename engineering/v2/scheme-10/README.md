# S10 多相 / 相组控制图纸包

方案 ID：`multiphase_phase_group_control`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S10-PCB-multiphase_inverter-r00.md` | draft | 已落地多相逆变器、六相电流采样、隔离、故障切除和连接器页级草案 |
| 3D/CAD | `cad/V2-S10-CAD-phase_group_packaging-r00.md` | draft | 已落地多相端子、线束、相组布置、热路径和封装 CAD 草案 |
| Controller | `controller/V2-S10-CTRL-fault_torque_allocator-r00.md` | draft | 已落地 fault torque allocator、αβ/xy 谐波子空间和相组降额状态机草案 |
| BOM/EDA | `bom_eda/V2-S10-BOM-multiphase_powertrain-r00.md` | draft | 已落地多相功率模块、采样链、故障隔离、连接器和线束 BOM 草案 |
| Test/DVP | `test_dvpr/V2-S10-DVP-multiphase_fault_tolerance-r00.md` | draft（research pool） | 已落地单相/相组故障、谐波、热和 NVH 测试草案 |
| Simulation | `simulation/V2-S10-SIM-phase_group_fault_trace-r00.md` | draft | 已落地相组故障、谐波子空间、热降额和容错收益追溯草案 |
| Prompt/r03 | `prompts/V2-S10-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- EXP-009 有多相相组降额代理实验。

## 当前判断

缺少多相逆变器、相组封装和 fault allocator 图纸，不能只用可用电流降额代理。
