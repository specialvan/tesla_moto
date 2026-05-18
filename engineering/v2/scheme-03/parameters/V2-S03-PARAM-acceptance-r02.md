# V2-S03-PARAM-acceptance-r02

方案：`svpwm_overmodulation_voltage_utilization`
domain：control + verification（合并 sheet）
关联：
- 仿真入口：`sim.run_modulation_factor_experiment.run`
- 仿真绑定：`engineering/v2/scheme-03/parameters/V2-S03-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-03/test_dvpr/V2-S03-DVP-thd_emc_nvh-r00.md`
- r01 视觉：`gpt-image-2/outputs/S03/V2-S03-ILL-T01-driver_block-r00.png` 与 `codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-03-r01.md`
- 数据底座：`models/motor_params.json`、EXP-005 modulation factor

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| Vdc | 360 V 标称 |
| Vmax linear | 207.85 V（= Vdc · 1/√3） |
| Vmax six-step | ≈ 229.18 V（六步） |
| Modulation index axis | [linear ≤ 0.907, R1 ≤ 0.952, R2 < 1.000, six-step = 1.000] |
| 工程结论可认定 | 参数化谐波/损耗惩罚下的 k_mod 折中 |
| 不可认定 | PWM 波形重建、真实 EMC、真实 NVH、台架损耗 |

`engineering_validated = false`。

## 2. 调制 / 控制生产参数

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| 开关频率 f_sw | 10 | kHz | r01 估值 |
| Dead-time | 1.5 | μs | r01 估值 |
| Modulation index linear | ≤ 0.907 | — | EXP-005 |
| Modulation index R1 | 0.907-0.952 | — | EXP-005 |
| Modulation index R2 | 0.952-1.000 | — | EXP-005 |
| THD limit | ≤ 8 | % | r01 估值（NVH 联动） |
| EMC standard | EN 55025 Class 5 | — | r01 工程占位 |
| Loss speed penalty 系数 | parametric | — | EXP-005 `scoring.loss_speed_penalty` |
| Harmonic speed penalty 系数 | parametric | — | EXP-005 `scoring.harmonic_speed_penalty` |

> 所有数值 r01 estimate；r03 需 FEA / 台架替换。

## 3. 不可破坏边界

1. **过调制不得越 THD 上限**：r02 标称 8 %，r03 替换为台架数据。
2. **六步运行有限时长**：JT 上限 r03 标定；本 sheet 暂禁连续六步评估。
3. **EMC 风险随 k_mod 上升**：r02 不替代 EMC chamber 测量。
4. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_modulation_factor_experiment import run
output = run()  # default k_mod sweep
```

期望产物（详见 `V2-S03-PARAM-sim_binding-r02.json::expect`）：
- `experiment == "exp_005_modulation_factor"`
- `sweep_axes.k_mod_values` 节点 ≥ 3
- `scoring.loss_speed_penalty` 与 `scoring.harmonic_speed_penalty` 字段存在
- `best_tradeoff` 非空（feasible 行至少 1 条）

## 5. DVP&R 验收映射（来自 `V2-S03-DVP-thd_emc_nvh-r00.md`）

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S03-DV-001 | THD 测量 | §2 THD limit + §4 best_tradeoff |
| S03-DV-002 | EMC 合规 | §2 EMC standard（HIL/chamber-side） |
| S03-DV-003 | NVH 扭矩纹波 | §2 harmonic penalty（bench） |
| S03-DV-004 | 逆变器损耗 sweep | §2 loss penalty + EXP-005 CSV |
| S03-DV-005 | 六步热应力 | §3 六步连续时长禁评 |

## 6. r02 → r03 升级清单

1. 替换参数化谐波 / 损耗曲线为实测 inverter loss maps。
2. 引入 PWM 波形重建 + THD 实测。
3. 六步连续运行 junction T 标定（< 150 °C）。
4. EMC chamber 验证替换 r01 占位。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 EXP-005 modulation factor，参数化谐波/损耗代理 |
