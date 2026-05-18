# S10 DVP&R multiphase fault tolerance draft · RESEARCH POOL

方案：`multiphase_phase_group_control`
状态：`draft / planned / not executed / not validated / research_pool`
范围：DVP&R 草案；不是多相逆变器样件、不是台架。

## 1. 草案目标

S10 测试草案用于规划六相 / 双 3-phase 相组的单相 / 相组故障、谐波子空间、热与 NVH 验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S10-CTRL-fault_torque_allocator-r00.drawio`（待落地） |
| PCB | `../pcb/V2-S10-PCB-multiphase_inverter-r00.pdf`（待落地） |
| Parameters | `../parameters/V2-S10-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S10-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S10-DV-001 | 单相故障 < 2 ms, derate 50 % | HIL planned | 故障注入 + derate 时序 | planned |
| S10-DV-002 | 相组故障 < 2 ms, shut down | HIL planned | shut down + service-only reset | planned |
| S10-DV-003 | 谐波子空间解耦 | SIL/HIL planned | αβ + xy 频谱 | planned |
| S10-DV-004 | per-group 热平衡 | Bench planned | 单组故障下剩余组温升 | planned |
| S10-DV-005 | NVH under fault | Bench planned | torque ripple FFT | planned |

## 4. 验收前置条件

- 六相逆变器样件可用（双 3-phase）。
- 谐波子空间控制实现。
- per-group 热模型 + S11 thermal 联动。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 多相硬件复杂度高 | 成本 / 体积 | 早期成本评估 |
| 故障检测窗 < 2 ms 难达 | 安全风险 | 检测算法优化 |
| 谐波 NVH 不可控 | 用户体验 | 控制器调优 |

## 6. 禁止误读

研究池；不证明多相硬件样件、台架、HIL、安全认证或工程发布已完成。
