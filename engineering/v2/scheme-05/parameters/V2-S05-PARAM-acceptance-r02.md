# V2-S05-PARAM-acceptance-r02

方案：`magnetic_saturation_codesign`
domain：mechanical + control + verification（合并 sheet）
关联：
- 仿真入口：`sim.run_param_sweep_experiment.run`（与 S06 共享）
- 仿真绑定：`engineering/v2/scheme-05/parameters/V2-S05-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-05/test_dvpr/V2-S05-DVP-saturation_codesign-r00.md`
- r01 视觉：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-05-r01.md`
- 数据底座：EXP-003 param sweep

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 候选 geometry 数 | 3-6 |
| FEA LUT 节点 | id × iq × T = 30 × 30 × 5（r03 目标，当前 EXP-003 为参数缩放代理） |
| 工程结论可认定 | Ld/Lq/saliency 参数缩放下的候选排序 |
| 不可认定 | FEA 实算、磁钢应力、转子机械强度、铁损实测 |

`engineering_validated = false`。当前 EXP-003 仅是 clean-room 缩放代理。

## 2. 候选 scorecard 生产参数

| 参数 | 标称阈值 | 单位 | 用途 |
|---|---|---|---|
| 转矩增益 vs baseline | ≥ +5 | % | scorecard 通过门槛 |
| 铁损增量 vs baseline | ≤ +3 | % | scorecard 否决门槛 |
| 转子最大应力 | < 600 | MPa | r03 FEA 必须验证 |
| Demag id_min @ 25 °C | ≥ -240 | A | 与 S01 / S11 共享 DemagLimit |
| 扭矩纹波 | ≤ 3 | % | NVH 与控制双约束 |
| 候选 variant_count | ≥ 1 | — | sim_binding 强制 |

> 阈值均为 r01 工程窗，r03 需 FEA / 台架替换。

## 3. 不可破坏边界

1. **不得用 Ld/Lq 缩放代替 FEA**：r02 通过仅是结构性验证。
2. **应力 / 退磁优先级 > 转矩**：scorecard 必须先过应力 / demag 才纳入排序。
3. **候选必须有 CAD / FEA 版本号**：r02 待对齐，r03 锁定。
4. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_param_sweep_experiment import run
output = run()
```

期望产物：
- `experiment == "exp_003_param_sweep"`
- `variant_count ≥ 1`
- `top_candidates` 非空
- `csv_path` 存在

## 5. DVP&R 验收映射（来自 `V2-S05-DVP-saturation_codesign-r00.md`）

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S05-DV-001 | FEA correlation | §2 转矩增益 / 铁损增量 阈值 |
| S05-DV-002 | 转子机械应力 < 600 MPa | §2 stress 阈值（r03 FEA） |
| S05-DV-003 | 铁损 audit | §2 iron loss budget |
| S05-DV-004 | 退磁 audit（跨 S11） | §2 DemagLimit |
| S05-DV-005 | NVH 扭矩纹波 ≤ 3 % | §2 ripple 阈值 |

## 6. r02 → r03 升级清单

1. 替换 Ld/Lq 缩放为 FEA-derived lambda_d/lambda_q。
2. 引入应力 / 退磁字段到候选 scorecard。
3. 锁定 candidate CAD / FEA 版本绑定。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 EXP-003 参数缩放代理 |
