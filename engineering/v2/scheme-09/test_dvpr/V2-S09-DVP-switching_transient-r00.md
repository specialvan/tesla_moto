# S09 DVP&R switching transient draft · RESEARCH POOL

方案：`winding_reconfiguration`
状态：`draft / planned / not executed / not validated / research_pool`
范围：DVP&R 草案；不是接触器实测、不是台架。

## 1. 草案目标

S09 测试草案用于规划绕组重构切换瞬态、环流、电弧 / 绝缘与非法状态 fallback 验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S09-CTRL-winding_reconfig_state_machine-r00.drawio`（待落地） |
| PCB | `../pcb/V2-S09-PCB-winding_switch_matrix-r00.pdf`（待落地） |
| Parameters | `../parameters/V2-S09-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S09-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S09-DV-001 | 切换瞬态 zero-torque 50-200 ms | Bench planned | 切换前后扭矩 | planned |
| S09-DV-002 | 环流 < 5 A | Bench planned | 切换中环流测量 | planned |
| S09-DV-003 | 电弧 / 绝缘 @ 800 V | Bench planned | flashover 测试 | planned |
| S09-DV-004 | 非法状态 fallback < 1 ms | HIL planned | fault injection | planned |

## 4. 验收前置条件

- HV 接触器样件可用。
- arc 抑制电路冻结。
- 互锁 + watchdog 路径硬件验证。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 接触器寿命短 | 系统可靠性 | 寿命循环测试 |
| 切换时机不准 | 环流过大 | 控制器时序优化 |
| 电弧 / EMI 干扰 traction | 安全 | 隔离与屏蔽设计 |

## 6. 禁止误读

研究池；不证明接触器样件、台架、HIL、安全认证或工程发布已完成。
