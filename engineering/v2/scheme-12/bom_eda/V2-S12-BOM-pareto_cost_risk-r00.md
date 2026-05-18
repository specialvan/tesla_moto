# V2-S12 BOM 成本/风险 Pareto 输入 r00

状态：`draft`，不替代候选方案正式 BOM。

## 1. 成本/风险字段

| 字段 | 单位 | 来源 | 缺失处理 |
|---|---:|---|---|
| PM mass delta | kg / % | S05/S06 BOM | 缺失则高惩罚 |
| electrical steel grade delta | grade/cost | S05/S06 BOM | 缺失则不可成本推荐 |
| inverter component delta | cost/risk | S03 BOM | 缺失则 EMC/thermal 惩罚 |
| excitation hardware delta | cost/risk | S08 BOM | research pool only |
| switching hardware delta | cost/risk | S09 BOM | research pool only |
| multiphase hardware delta | cost/risk | S10 BOM | research pool only |
| diagnostic/safety delta | coverage/cost | S11 BOM | 缺失则 stop |

## 2. 成本评分规则

- 成本收益不得单独压过 safety gate。
- BOM 状态低于 `draft` 时，成本分只能作为 research estimate。
- 供应风险高且无替代料时，成熟度分降级。

## 3. 下版生图提示词

生成 S12 BOM cost-risk Pareto input table，列出 PM mass、steel grade、inverter delta、excitation hardware、switching hardware、multiphase hardware、diagnostic safety delta、supply risk、maturity penalty。白底工程表格，英文标注，红色标出 stop conditions。