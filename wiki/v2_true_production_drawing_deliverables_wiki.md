# V2 真实生产图纸交付物 Wiki

来源文档：`claude-review/docs/2026-05-15/v0.5_true_production_drawing_deliverables_matrix.md`  
触发评审：`codex-review/docs/claude_image_to_production_deep_review_2026-05-19.md`

## 核心结论

当前 V2 图档生产化仍处于 `concept_drawing`、`parameter_sheet`、`binding_smoke` 和 `numeric_proxy` 档位；所有方案保持：

```text
production_drawing_ready=false
manufacturing_release_ready=false
engineering_validated=false
```

## 五档交付物口径

| 档位 | 当前含义 |
|---|---|
| `concept_drawing` | PNG、drawio、Markdown 页级草案，只能做沟通锚点 |
| `parameter_sheet` | 带单位/来源/maturity 的参数表或 sim_binding |
| `source_design_file` | 真实 EDA/CAD/FEA/控制器源文件，当前缺失 |
| `simulation_input` | FEA mesh、材料曲线、loss map、bench map 等，当前多为 proxy/synthetic |
| `manufacturing_release` | Gerber、ODB++、正式 BOM、DVP 结果、DFMEA/FMDEA，当前缺失 |

## Codex 打回闭环

- S02：60 A jump 阈值已明确为 r02 proxy soft gate；30 A 是 r03 production target。
- S04：`models/flux_lut_sample.json` 已明确为 synthetic 3×3 smoke fixture。
- 全方案：`models/scheme_simulation_coverage.json` 已增加 maturity flags，不再统一写 `passed_numeric_simulation`。
- 生图：r00/r01/r03 prompt 只能作为 concept anchor，不参与制造验收。

## 下一步

1. 用真实 EDA/CAD/FEA 源文件替换 Markdown 草案。
2. 用 FEA-derived LUT、材料曲线、HIL/bench 数据替换 synthetic/proxy。
3. 将 pytest 从 binding smoke 逐步升级为 physics/model gate。
