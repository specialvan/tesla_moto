# V2-S12 Pareto scorecard 控制/决策图 r00

状态：`draft`。

## 1. Scorecard 维度

| 维度 | 权重输入 | 惩罚项 | 输出 |
|---|---|---|---|
| Drive-cycle efficiency | EXP-010 / validated map | 代理模型置信度 | weighted efficiency score |
| Peak performance | torque/speed envelope | 退磁/热限制 | performance score |
| Cost | BOM material + electronics | missing BOM penalty | cost score |
| Maturity | PCB/CAD/BOM/DVP status | missing evidence penalty | maturity score |
| Safety | S11 diagnostic coverage | no fault path = stop | safety gate |
| Manufacturability | DFM/assembly/service | unknown process penalty | manufacturing score |

## 2. 决策规则

```text
if safety_gate == fail: recommendation = stop
elif maturity_score < threshold: recommendation = research_rank_only
elif weighted_score stable under sensitivity: recommendation = engineering_candidate
else: recommendation = needs_more_evidence
```

## 3. 权重扰动要求

- 对 efficiency/cost/maturity/safety/manufacturing 权重做 ±20% sensitivity。
- 若推荐结果随权重小幅变化翻转，禁止输出单一工程推荐。
- research pool 候选必须与 P0/P1 候选分开排序。

## 4. 下版生图提示词

生成 S12 Pareto scorecard decision diagram，包含 Drive-cycle Efficiency、Peak Performance、Cost、Maturity Evidence、Safety Gate、Manufacturability、Sensitivity Analysis、Recommendation Output。使用白底流程图，英文标签，红色 stop gate，黄色 research-only gate，绿色 engineering candidate。