# V2-S07-PARAM-acceptance-r02 · RESEARCH POOL

方案：`variable_magnetization_memory_motor`
domain：electrical + safety + verification（合并 sheet，**研究池**）
关联：
- 仿真入口：`sim.run_variable_flux_experiment.run`
- 仿真绑定：`engineering/v2/scheme-07/parameters/V2-S07-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-07/test_dvpr/V2-S07-DVP-magnetization_state-r00.md`
- r01 视觉：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-07-r01.md`

> **研究池声明**：S07 不是生产候选；本 sheet 用于参数研究记录，不代表工程方向。

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| flux_state 数 | ≥ 2（EXP-002 默认 3 个） |
| torque_targets | ≥ 1（仿真用 N·m） |
| 工程结论可认定 | psi_f 缩放下的状态比较 |
| 不可认定 | 真实磁化脉冲、储能 bank、寿命、unknown state fallback |

`engineering_validated = false`，且 research pool。

## 2. 研究池占位参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 磁化脉冲电压 | 800 | V | r01 estimate（research pool） |
| 磁化脉冲峰值电流 | 1000 | A | r01 estimate |
| 脉冲持续时间 | 50 | μs | r01 estimate |
| 储能电容能量 | 100 | J | r01 estimate |
| 磁状态分辨率 | 8 | 级 | r01 estimate |
| 寿命循环上限 | 10 000 | 次 | r01 estimate |
| 互锁验证延迟 | < 1 | ms | r01 estimate |

> 全部为 research pool 占位，r02 / r03 仅作研究输入，不进入工程发布。

## 3. 不可破坏边界

1. **`psi_f` 缩放 ≠ 硬件磁状态**：EXP-002 不能代理脉冲驱动 / 储能 / 互锁。
2. **不得作为工程候选推荐**：研究池标识必须保留。
3. **互锁优先**：任何 r03 推进必须先证明脉冲与 traction 互锁。
4. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_variable_flux_experiment import run
output = run()
```

期望产物：
- `experiment == "exp_002_variable_flux"`
- `flux_states ≥ 2`
- `state_summaries_by_torque` 非空

## 5. DVP&R 验收映射

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S07-DV-001 | 磁化 / 去磁脉冲 | §2 脉冲参数（research） |
| S07-DV-002 | 状态保持 | §2 寿命循环 |
| S07-DV-003 | 温度漂移 | r03 + S11 联动 |
| S07-DV-004 | unknown-state fallback | §2 互锁延迟 |
| S07-DV-005 | 寿命循环 | §2 10 000 次上限 |

## 6. r02 → r03 升级清单

1. EXP-002 升级为 pulse + energy bank + interlock 模型。
2. 引入 lifetime cycle counter 实模型。
3. 接入 S11 thermal 验证状态保持。
4. **保持研究池标记，r03 通过不晋升为工程候选**。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 EXP-002 psi_f sweep（research pool） |
