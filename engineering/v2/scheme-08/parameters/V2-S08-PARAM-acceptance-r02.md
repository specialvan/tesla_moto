# V2-S08-PARAM-acceptance-r02 · RESEARCH POOL

方案：`hybrid_excitation`
domain：electrical + control + verification（合并 sheet，**研究池**）
关联：
- 仿真入口：`sim.run_hybrid_excitation_experiment.run`
- 仿真绑定：`engineering/v2/scheme-08/parameters/V2-S08-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-08/test_dvpr/V2-S08-DVP-hybrid_excitation-r00.md`
- r01 视觉：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-08-r01.md`

> **研究池声明**：S08 不是生产候选；EXP-007 用 `psi_eff = psi_pm + kf · if` 代理硬件。

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 励磁 DC/DC 输出 | 48 V 标称 |
| if 范围 | [-20, +30] A |
| psi_eff 范围 | 0.02-0.10 Wb |
| 工程结论可认定 | psi_eff 代理下的工作点比较 |
| 不可认定 | 励磁绕组损耗、loss-of-field 物理路径、滑环 / 无刷励磁 |

`engineering_validated = false`，research pool。

## 2. 研究池占位参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 励磁 DC/DC | 48 | V | r01 estimate |
| if 范围 | [-20, +30] | A | r01 estimate |
| psi_eff range | 0.02-0.10 | Wb | r01 estimate |
| Loss-of-field 检测窗 | < 5 | ms | r01 estimate |
| 励磁绕组绝缘等级 | H | — | r01 工程占位 |
| 冷却方式 | 油 / 液冷 | — | r01 工程占位 |

## 3. 不可破坏边界

1. **psi_eff 代理 ≠ 硬件励磁**：必须保留代理标识。
2. **loss-of-field 优先 fallback**：任何 r03 推进先验证 fallback。
3. **绝缘等级 H 不得降级**：r02 工程占位，r03 实测。
4. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_hybrid_excitation_experiment import run
output = run()
```

期望产物：
- `experiment == "exp_007_hybrid_excitation"`
- `row_count ≥ 1`
- `csv_path` 存在

## 5. DVP&R 验收映射

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S08-DV-001 | 励磁热应力 | §2 绝缘等级 H |
| S08-DV-002 | loss-of-field 检测 | §2 < 5 ms |
| S08-DV-003 | 三变量优化 | §2 if / psi_eff range |
| S08-DV-004 | 台架相关性 | r03 bench |

## 6. r02 → r03 升级清单

1. EXP-007 升级为 field winding 电感 + exciter loss 模型。
2. 引入转子漏磁与热耦合。
3. 接入 S11 thermal 验证励磁绕组温升。
4. **保留研究池标识**。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 EXP-007 psi_eff 代理 |
