# V2 方案 r01 提示词批包 · 索引

修订日期：2026-05-18
范围：12 方案 × 8 模板 = 96 张 r01 提示词，已嵌入生产参数，可一次性批量执行
依据：
- `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md`
- `claude-review/docs/2026-05-18/v2_image_pack_r02_production_roadmap.md`
- `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18_r01.md`
- `engineering/v2/scheme-XX/{controller,pcb,cad,bom_eda,test_dvpr}/` 草案
- `models/motor_params.json` `models/control_lut.json` `models/control_lut_schema.json`

---

## 0. 使用说明

1. 每条 prompt 已嵌入对应方案的生产参数（来自草案 / motor_params.json / control_lut.json）。
2. 全局正向 / 负向 prompt 已在 `_globals.md` 沉淀；每条 prompt 末尾 `<r01 GLOBAL POSITIVE>` 占位符替换为 `_globals.md §1.1`，`<r01 GLOBAL NEGATIVE>` 替换为 `_globals.md §1.2`。
3. 批量执行入口：用户在生图工具内按 §3 顺序粘贴 prompt，输出落到 `gpt-image-2/outputs/SXX/V2-SXX-ILL-TYY-...-r01.png`，prompt.txt 落到同目录同名 `-r01-prompt.txt`。
4. 每方案分册：`scheme-01-r01.md` ... `scheme-12-r01.md`。
5. 改图模式：以同方案 r00 PNG 作为参考图，使用各分册 §3 「改图微调」段。
6. 完整批量：96 条；建议一次跑 12 方案 × 2 模板（24 条）为一批，便于检查与回滚。

---

## 1. 分册入口

| 方案 | 分册路径 | 草案完整度 | r01 P0 张数 | r02 参数 sheet |
|---|---|---|---|---|
| S01 negative_d_axis_field_weakening | `scheme-01-r01.md` | 全（PCB/CAD/CTRL/BOM/DVP） | 1（T03） | 待补 |
| S02 mtpa_fw_mtpv_control | `scheme-02-r01.md` | 全 | 1（T03） | ✓（control + verification + sim_binding） |
| S03 svpwm_overmodulation_voltage_utilization | `scheme-03-r01.md` | 仅 README | 1（T03） | r01 占位 |
| S04 nonlinear_flux_lut | `scheme-04-r01.md` | 全 | 2（T04 / T05） | 待补 |
| S05 magnetic_saturation_codesign | `scheme-05-r01.md` | 仅 README | 1（T03 标题） | r01 占位 |
| S06 pmasynrm_high_saliency_low_pm | `scheme-06-r01.md` | 仅 README | 1（T03 加状态） | r01 占位 |
| S07 variable_magnetization_memory_motor | `scheme-07-r01.md` | 仅 README | 1（T05 BLOCKER） | r01 研究池占位 |
| S08 hybrid_excitation | `scheme-08-r01.md` | 仅 README | 2（T03 + T05） | r01 研究池占位 |
| S09 winding_reconfiguration | `scheme-09-r01.md` | 仅 README | — | r01 研究池占位 |
| S10 multiphase_phase_group_control | `scheme-10-r01.md` | 仅 README | — | r01 研究池占位 |
| S11 thermal_demag_safety_protection | `scheme-11-r01.md` | 全 | — | 待补 |
| S12 weighted_efficiency_pareto_selection | `scheme-12-r01.md` | 仅 README | 1（T03 标题） | r01 占位 |

P0 共 11 张是 r00 评审锁定的"工程语义错或 BLOCKER 必修"，先跑 P0；P1/P2 视精力跑。

---

## 2. 全局基线（`_globals.md`）

参见 `_globals.md`。三段：

- §1.1 全局正向风格 token
- §1.2 全局负向 prompt
- §1.3 模板长宽比与尺寸建议

每个分册的每条 prompt 末尾必须追加 §1.1，并在工具支持负向 prompt 时附加 §1.2。

---

## 3. 推荐批量执行顺序

| Batch | 内容 | 张数 | 估时 |
|---|---|---|---|
| **B1 r01-P0 必修** | S01-T03、S02-T03、S03-T03、S04-T04、S04-T05、S05-T03、S06-T03、S07-T05、S08-T03、S08-T05、S12-T03 | 11 | ~22 min |
| **B2 r01-P1 控制主线** | S01-T01、S02-T01、S04-T01、S11-T01、S01-T08、S02-T08、S04-T08、S11-T08（控制 & 协议） | 8 | ~16 min |
| **B3 r01-P1 状态机其他** | S07-T03、S09-T03、S10-T03、S11-T03（剩余 T03） | 4 | ~8 min |
| **B4 r01-P1 时序图** | 12 × T02 | 12 | ~24 min |
| **B5 r01-P1 PCB + CAD 概念** | 12 × T04 + 12 × T05（除 P0 已做） | 22 | ~44 min |
| **B6 r01-P2 BOM 与 Test 树** | 12 × T06 + 12 × T07 | 24 | ~48 min |
| **B7 r01-P2 协议剩余** | 8 × T08（除 B2 已做） | 8 | ~16 min |

总计：89 张 r01（11 + 8 + 4 + 12 + 22 + 24 + 8 = 89；剩 7 张可保留 r00）。

> 估时按 gpt-image-2 单张 ~60-120 s + sleep 4 s 排队估算；批量串行执行总耗时约 3.5 - 4 小时（不含检查）。

---

## 4. 不可破坏边界

1. r01 仍属"概念可视化"，不替代 EDA / CAD / FEA / HIL。
2. 任何分册嵌入的生产参数若与 `engineering/v2/scheme-XX/` 草案不一致，**草案为准**；分册随之更新。
3. 出现真实牌号（如 NDFEB / SmCo / M270-35A）或写实 motor render，立即拒收。
4. r01 不翻转 `engineering_validated`；r02 / r03 也不翻。
5. 分册引用的参考图（drawio / mermaid / r00 PNG）必须在仓库可达。

---

## 5. 与下一档（r02 / r03）的衔接

- r02 生产参数 sheet 在 `engineering/v2/scheme-XX/parameters/` 沉淀，本批包 prompt 直接嵌入数值。
- r03 仿真闭环（`tests/test_scheme_XX_*.py`）将读取 r02 `sim_binding.json`，与 r01 PNG 视觉无直接耦合。
- 因此，r01 PNG 可以与 r02 / r03 并行推进；它们不互锁。

---

## 6. 待办

| 行动 | 落点 | 责任 |
|---|---|---|
| 全部 12 分册 `scheme-XX-r01.md` 落地 | 本目录 | Claude（本轮） |
| `_globals.md` 沉淀 | 本目录 | Claude（本轮） |
| `gpt-image-2/prompts/schemes.json` 落实尺寸覆盖 | 工具配置 | 下一轮 |
| 一次性批量生图 r01 | `gpt-image-2/outputs/SXX/...-r01.png` | 用户手动（按 §3 顺序） |
| r01 二轮 Claude 评审 | `claude-review/docs/2026-05-19/...` | 下一轮 |
