# V2-S10-PARAM-acceptance-r02 · RESEARCH POOL

方案：`multiphase_phase_group_control`
domain：electrical + safety + verification（合并 sheet，**研究池**）
关联：
- 仿真入口：`sim.run_multiphase_phase_group_experiment.run`
- 仿真绑定：`engineering/v2/scheme-10/parameters/V2-S10-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-10/test_dvpr/V2-S10-DVP-multiphase_fault_tolerance-r00.md`
- r01 视觉：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-10-r01.md`

> **研究池声明**：EXP-009 仅可用电流降额代理。

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 相数 | 6（双 3-phase 相组） |
| Per-phase 峰值电流 | 130 A |
| 工程结论可认定 | 可用电流降额下的最大可达速度 |
| 不可认定 | 谐波子空间解耦、中性点偏移、相间热传导 |

`engineering_validated = false`，research pool。

## 2. 研究池占位参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 相数 | 6（双 3-phase） | — | r01 估值 |
| Per-phase 峰值 | 130 | A | r01 估值（双组共 260 A） |
| 故障检测窗 | < 2 | ms | r01 estimate |
| 谐波子空间维度 | 2（αβ + xy） | — | r01 estimate |
| 单相故障 derate | 50 | % | r01 estimate |
| 相组故障 derate | 100（shut down） | % | r01 estimate |

## 3. 不可破坏边界

1. **shut down → 服务复位**：相组故障后禁止自动恢复。
2. **谐波子空间必须解耦**：αβ + xy 不可混叠。
3. **per-group 热平衡**：单组故障不得引发剩余组热失控。
4. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_multiphase_phase_group_experiment import run
output = run()
```

期望产物：
- `experiment == "exp_009_multiphase_phase_group"`
- `cases ≥ 2`
- `case_count ≥ 2`
- `worst_case` 存在

## 5. DVP&R 验收映射

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S10-DV-001 | 单相故障 < 2 ms, derate 50 % | §2 时序 + derate |
| S10-DV-002 | 相组故障 < 2 ms, shut down | §3 不可破坏边界 #1 |
| S10-DV-003 | 谐波子空间解耦 | §2 αβ + xy |
| S10-DV-004 | per-group 热平衡 | §3 不可破坏边界 #3 |
| S10-DV-005 | NVH under fault | bench |

## 6. r02 → r03 升级清单

1. EXP-009 升级为谐波子空间 + 中性点偏移模型。
2. 引入 per-phase 热 RC 网络。
3. 接入 S11 thermal 验证相组热平衡。
4. **保留研究池标识**。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 EXP-009 可用电流降额代理 |
