# S09 绕组重构图纸包

方案 ID：`winding_reconfiguration`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S09-PCB-winding_switch_matrix-r00.md` | draft | 已落地高压接触器/固态开关、互锁、arc suppression、零电流和状态反馈页级草案 |
| 3D/CAD | `cad/V2-S09-CAD-reconfigurable_winding_layout-r00.md` | draft | 已落地绕组端部、重构开关布置、绝缘、热路径和线束 CAD 草案 |
| Controller | `controller/V2-S09-CTRL-winding_reconfig_state_machine-r00.md` | draft | 已落地切换状态机、零转矩窗口、非法状态回退、环流和 stuck fault 草案 |
| BOM/EDA | `bom_eda/V2-S09-BOM-switching_winding-r00.md` | draft | 已落地开关、驱动、互锁、arc suppression、线束和绝缘件 BOM 草案 |
| Test/DVP | `test_dvpr/V2-S09-DVP-switching_transient-r00.md` | draft（research pool） | 已落地切换瞬态、环流、arc、open/short/stuck fault 测试草案 |
| Simulation | `simulation/V2-S09-SIM-switching_transient_trace-r00.md` | draft | 已落地绕组切换瞬态、环流、arc、非法状态和热/NVH 追溯草案 |
| Prompt/r03 | `prompts/V2-S09-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- EXP-008 有绕组重构代理实验。

## 当前判断

缺少开关矩阵、互锁和瞬态安全图纸，不能用静态 Ke/Kt 缩放代表工程可行。
