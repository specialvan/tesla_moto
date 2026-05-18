# S07 可变磁化状态 / Memory Motor 图纸包

方案 ID：`variable_magnetization_memory_motor`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S07-PCB-magnetization_pulse_driver-r00.md` | draft | 已落地磁化脉冲驱动、储能、电流检测、隔离和牵引互锁页级草案 |
| 3D/CAD | `cad/V2-S07-CAD-memory_motor_magnetic_path-r00.md` | draft | 已落地记忆磁体、磁化路径、转子桥、热路径和状态观测 CAD 草案 |
| Controller | `controller/V2-S07-CTRL-flux_state_machine-r00.md` | draft | 已落地磁状态机、脉冲执行、状态确认、unknown-state 回退和寿命计数草案 |
| BOM/EDA | `bom_eda/V2-S07-BOM-memory_motor_pulse_chain-r00.md` | draft | 已落地脉冲功率级、储能器件、磁体材料、观测传感器和安全链 BOM 草案 |
| Test/DVP | `test_dvpr/V2-S07-DVP-magnetization_state-r00.md` | draft（research pool） | 已落地脉冲、状态保持、温漂、unknown-state、寿命测试计划草案 |
| Parameters/r02 | `parameters/V2-S07-PARAM-acceptance-r02.md`、`parameters/V2-S07-PARAM-sim_binding-r02.json` | r02 接入（research pool） | 研究池占位参数 + 仿真绑定（绑 EXP-002），由 `tests/test_scheme_experiment_acceptance.py` 自动校验 |
| Simulation | `simulation/V2-S07-SIM-magnetization_state_trace-r00.md` | draft | 已落地磁化状态、脉冲电路、热漂移和未知状态回退追溯草案 |
| Prompt/r03 | `prompts/V2-S07-PROMPT-r03-production_drawing_pack.md` | draft | 已落地下版生产参数化生图提示词包 |

## 现有证据

- review-pr 外部资料已指出 Memory Motor 不能用 `psi_f` 缩放代理工程可行性。

## 当前判断

关键硬件拓扑、磁化脉冲驱动和磁状态机图纸全缺，必须保留研究池定位。
