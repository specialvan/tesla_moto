# S08 DVP&R hybrid excitation draft · RESEARCH POOL

方案：`hybrid_excitation`
状态：`draft / planned / not executed / not validated / research_pool`
范围：DVP&R 草案；不是 field converter / bench / HIL 实测。

> **研究池声明**：EXP-007 仅 psi_eff 代理，不能代理硬件。

## 1. 草案目标

S08 测试草案用于规划混合励磁的励磁热、loss-of-field、三变量优化与台架相关性验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S08-CTRL-three_variable_control-r00.drawio`（待落地） |
| PCB | `../pcb/V2-S08-PCB-field_excitation_converter-r00.pdf`（待落地） |
| Parameters | `../parameters/V2-S08-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S08-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S08-DV-001 | 励磁绕组热应力 | Bench planned | 绕组 T < 180 °C class H | planned |
| S08-DV-002 | Loss-of-field 检测 | HIL planned | 故障注入 → 5 ms 内检测 | planned |
| S08-DV-003 | 三变量优化 | SIL/HIL planned | id/iq/if pareto | planned |
| S08-DV-004 | 台架相关性 | Bench planned | psi_eff 测量 vs 预测 | planned |

## 4. 验收前置条件

- 励磁 DC/DC 样件可用。
- 与 traction inverter 隔离方案冻结。
- loss-of-field 故障注入夹具准入。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 励磁损耗高于估算 | 系统效率下降 | bench 早期实测 |
| 滑环 / 无刷励磁选型未定 | 寿命与维修 | 早期决定拓扑 |
| Loss-of-field fallback 时间长 | 安全 | HIL 时序验证 |

## 6. 禁止误读

研究池草案；不证明 field converter 样件、台架、HIL、ASIL 安全或工程发布已完成。
