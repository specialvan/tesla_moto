# V2-S06 BOM/材料低 PM 拓扑登记 r00

状态：`draft`。

## 1. BOM 字段

| 类别 | 生产字段 | 风险 | 证据 |
|---|---|---|---|
| Low-PM magnet | grade、mass、Hcj、temp limit、coating | 退磁/供应/成本 | demag curve + cost model |
| Electrical steel | grade、thickness、BH/loss curves | 铁耗/NVH | material curves |
| Hairpin winding | conductor size、slot fill、insulation class | 热/制造 | DFM + thermal model |
| Rotor retention | sleeve/adhesive/geometry | 高速失效 | stress FEA + spin test plan |
| Thermal sensors | winding/oil/magnet proxy | 退磁保护 | S11 diagnostic binding |

## 2. 成本/风险要求

- PM 用量降低必须量化到材料成本和供应风险，不得只写“低 PM”。
- 若为降低 PM 牺牲高温峰值转矩或退磁裕度，必须在 S12 Pareto 中降权。
- 每个材料替换必须触发 FEA LUT、热和退磁重跑。

## 3. 下版生图提示词

生成 S06 low-PM topology BOM and risk matrix，展示 low-PM magnet、electrical steel、hairpin winding、rotor retention、thermal sensors，字段包括 cost impact、supply risk、demag curve、loss curve、DFM evidence、gate status。白底工程表格，英文标签。