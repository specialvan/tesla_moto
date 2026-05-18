# S07 DVP&R magnetization state draft · RESEARCH POOL

方案：`variable_magnetization_memory_motor`
状态：`draft / planned / not executed / not validated / research_pool`
范围：DVP&R 草案；不是脉冲驱动器实测、不是台架样件、不是工程发布。

> **研究池声明**：S07 不是生产候选；本草案用于研究记录。

## 1. 草案目标

S07 测试草案用于规划记忆电机磁化 / 去磁脉冲、磁状态保持、温度漂移、unknown-state fallback 与寿命循环验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S07-CTRL-flux_state_machine-r00.drawio`（待落地） |
| PCB | `../pcb/V2-S07-PCB-magnetization_pulse_driver-r00.pdf`（待落地） |
| Parameters | `../parameters/V2-S07-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S07-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S07-DV-001 | 磁化 / 去磁脉冲 | Pulse rig planned | 1000 A / 50 μs / 100 J 复现 | planned |
| S07-DV-002 | 状态保持 | Bench planned | 8 级状态 vs 72 h 漂移 | planned |
| S07-DV-003 | 温度漂移 | Bench planned | 25-120 °C 状态稳定性 | planned |
| S07-DV-004 | unknown-state fallback | HIL planned | safe retreat < 1 ms | planned |
| S07-DV-005 | 寿命循环 | Endurance planned | 10 000 cycles 状态可重复 | planned |

## 4. 验收前置条件

- 脉冲驱动器 + 储能 bank 样件可用。
- 与 traction inverter 的硬件互锁路径冻结。
- 磁钢温度采样与磁状态观测分离。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 脉冲触发干扰 traction 路径 | 安全 | 互锁 + EMI 早期评估 |
| 状态观测不可信 | unknown 比例高 | 多传感器融合 |
| 寿命累积导致状态漂移 | 控制器精度 | counter + 重标定流程 |

## 6. 禁止误读

本文件研究池，**不得**视为生产候选；只证明 DVP&R / 研究计划已进入页面级；不证明脉冲样件、台架、HIL、安全认证或工程验证已完成。
