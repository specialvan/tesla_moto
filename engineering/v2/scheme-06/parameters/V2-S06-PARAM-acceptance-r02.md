# V2-S06-PARAM-acceptance-r02

方案：`pmasynrm_high_saliency_low_pm`
domain：mechanical + control + verification（合并 sheet）
关联：
- 仿真入口：`sim.run_param_sweep_experiment.run`（与 S05 共享）
- 仿真绑定：`engineering/v2/scheme-06/parameters/V2-S06-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-06/test_dvpr/V2-S06-DVP-pmasynrm_validation-r00.md`
- r01 视觉：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-06-r01.md`

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 凸极比 Lq/Ld | ≥ 5 |
| PM fraction | 30-50 % |
| 工程结论可认定 | 高凸极 / 低 PM 参数缩放候选排序 |
| 不可认定 | FEA 实算、磁钢应力、torque ripple 实测 |

`engineering_validated = false`。

## 2. 生产参数

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| Lq/Ld | ≥ 5 | — | r01 工程窗 |
| PM fraction | 30-50 | % | r01 工程窗 |
| Demag id_min @ 25 °C（低 PM） | ≥ -200 | A | r01 工程窗（比 S01 更严） |
| 转子最大应力 | < 700 | MPa | r01 工程窗（受 PM 分布影响） |
| 扭矩纹波 | ≤ 3 | % | r01 工程窗 |

## 3. 不可破坏边界

1. **低 PM 退磁边界更严**：id_min ≥ -200 A，不得复用 S01 的 -240 A。
2. **PM fraction 不得低于 30 %**：低于此值 EXP-003 缩放外推不可靠。
3. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_param_sweep_experiment import run
output = run()
```

期望产物（同 S05）：variant_count ≥ 1、top_candidates ≥ 1、csv_path 存在。

## 5. DVP&R 验收映射

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S06-DV-001 | torque ripple ≤ 3 % | §2 ripple |
| S06-DV-002 | 应力 < 700 MPa | §2 stress |
| S06-DV-003 | 低 PM 退磁 ≥ -200 A | §2 id_min |
| S06-DV-004 | 热 / 冷却 | r03 与 S11 联动 |
| S06-DV-005 | NVH | bench |

## 6. r02 → r03 升级清单

1. 替换 psi/Ld/Lq 缩放为 FEA 候选地图。
2. PM fraction 与 torque ripple 加入 scorecard 字段。
3. 与 S11 thermal 联合验证低 PM 退磁。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；共享 EXP-003 与 S05 |
