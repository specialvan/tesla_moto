# V2-S12-PARAM-acceptance-r02

方案：`weighted_efficiency_pareto_selection`
domain：verification + audit（合并 sheet，聚合候选方案）
关联：
- 仿真入口：`sim.run_weighted_efficiency_pareto_experiment.run`
- 仿真绑定：`engineering/v2/scheme-12/parameters/V2-S12-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-12/test_dvpr/V2-S12-DVP-pareto_traceability-r00.md`
- r01 视觉：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-12-r01.md`
- 数据底座：EXP-010 weighted efficiency pareto + EXP-011 iron loss

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 候选方案数 | 11（S01-S11） |
| Drive cycles | WLTP / CLTC / Urban / Highway（4 个示例工况，权重 0.4 / 0.3 / 0.2 / 0.1） |
| 评分维度 | 5（效率 / 性能 / 成本 / 体积 / 风险） |
| Pareto sweep | ±20 % 权重扰动 |
| 工程结论可认定 | 在 EXP-010 / EXP-011 损耗模型下的候选排序 |
| 不可认定 | 真实 drive cycle、机械损耗、逆变器损耗、温度耦合 |

`engineering_validated = false`。S12 不引入新硬件，仅聚合 S01-S11 候选。

## 2. 评分生产参数

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| WLTP 权重 | 0.4 | — | r01 工程窗 |
| CLTC 权重 | 0.3 | — | r01 工程窗 |
| Urban 权重 | 0.2 | — | r01 工程窗 |
| Highway 权重 | 0.1 | — | r01 工程窗 |
| Score 维度 | 5 | — | r01 工程窗 |
| Maturity 等级 | 1-5（TRL 等价） | — | r01 工程窗 |
| Risk 等级 | 1-5 | — | r01 工程窗 |
| Sensitivity sweep | ±20 % | — | r01 工程窗 |

## 3. 不可破坏边界

1. **S12 不引入新硬件**：BOM / PCB / CAD 都指向被聚合的方案版本号。
2. **候选必须有 r02 sim_binding**：否则不进入 pareto。
3. **权重必须版本化**：drive cycle / weight 来源必须可审计。
4. `engineering_validated` 不翻；S12 通过不意味某方案 engineering validated。

## 4. 仿真绑定

```python
from sim.run_weighted_efficiency_pareto_experiment import run
output = run()
```

期望产物：
- `experiment == "exp_010_weighted_efficiency_pareto"`
- `cycles ≥ 1`、`candidates ≥ 1`
- `cycle_winners`、`pareto_front` 存在
- `row_count ≥ 1`

## 5. DVP&R 验收映射

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S12-DV-001 | drive cycle audit | §2 权重 + drive cycle 版本 |
| S12-DV-002 | 系统损耗 audit | §1 EXP-010 + EXP-011 |
| S12-DV-003 | sensitivity sweep ±20 % | §2 sensitivity |
| S12-DV-004 | evidence-path audit | §3 不可破坏边界 #2 |

## 6. r02 → r03 升级清单

1. drive cycle 替换为真实 WLTP / CLTC 数据。
2. 损耗模型加入机械损耗 + 逆变器损耗 + 温度耦合。
3. 加 transient acceleration / regen energy 权重。
4. 每方案 r02 sim_binding 必须存在才能进入 S12 pareto。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 EXP-010 / EXP-011 pareto 聚合 |
