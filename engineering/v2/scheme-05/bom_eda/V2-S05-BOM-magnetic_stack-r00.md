# V2-S05 BOM/材料与制造风险登记 r00

状态：`draft`，不替代正式 BOM XLSX 或供应商定点文件。

## 1. 材料/工艺字段

| 类别 | 生产参数字段 | 风险 | 必需证据 |
|---|---|---|---|
| Electrical steel | grade、thickness、loss curve、BH curve | 铁耗和供应 | 材料曲线 + lot control |
| Magnet | grade、Br/Hcj、temp rating、coating | 退磁/成本 | demag curve + corrosion spec |
| Lamination tooling | min bridge/rib、burr、stack tolerance | 制造可行性 | DFM review |
| Rotor assembly | magnet retention、adhesive、sleeve | 高速可靠性 | spin test plan |
| Sensor interface | temp/current/position accuracy | LUT 误差 | 与 S04/S11 采样链绑定 |

## 2. 供应链评审

- 每个候选几何必须关联材料牌号和供应风险。
- 低成本材料替换必须重新跑 FEA LUT、铁耗和退磁边界。
- 磁钢涂层、胶水、护套和冲片毛刺不得留空。

## 3. 下版生图提示词

生成 S05 magnetic stack BOM risk table，包含 electrical steel、magnet、lamination tooling、rotor assembly、sensor interface 五类，字段包括 grade、loss curve、BH curve、demag curve、DFM risk、supply risk、gate evidence。白底工程表格，英文标注。