# V2 方案图纸 r01 提示词 Wiki

日期：2026-05-18  
来源：
- `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18_r01.md`
- `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md`

---

## 1. 页面定位

本 Wiki 是 V2 12 方案 96 张生图（r00 → r01）提示词与评审的知识库索引版，配合：

- `engineering/v2/scheme-XX/illustrations/`：未来 r01 PNG 与 prompt.txt 归档位（当前为空）
- `gpt-image-2/outputs/SXX/`：r00 PNG 与 prompt.txt 归档位
- `codex-review/docs/image_worklist_2026-05-18/`：每方案分册的手动工作清单

---

## 2. 为什么需要 r01

r00 96 张已生图，但深度评审发现：

1. 8 张 P0 必修（T03 状态机语义错 / T05 写实化超标 / T04 密度过高）。
2. 12 项共性问题（标题泄漏、bus label 占位、风格基线偏差等）。
3. 工程语义对齐度仍不足以做评审之外的用途，仍属于"概念示意"。

r01 收敛的目标是把 prompt 收紧到 LLM 必须遵守的显式枚举，把负向 prompt 扩到能拦截真实牌号 / 写实 render。

---

## 3. r01 全局升级清单

| 项 | r00 | r01 |
|---|---|---|
| 节点填充色 | "pale blue" 自由发挥 | 显式 hex `#B6C7E0` |
| 描边色 | "gold" | 显式 hex `#D8A638` |
| 背景色 | "dark navy" | 显式 hex `#0B1A33`，禁渐变 |
| 故障状态 | 无视觉差异 | 红色描边 hex `#C0392B` |
| 标题 | 模型自由发挥 | 强制 `Title bar text MUST be: <SCHEME_TITLE>` |
| 真实牌号 | 未明确禁用 | 负向 prompt 拦截 M270-35A / NdFeB / SmCo / ADC12 等 |
| 写实 3D | 未明确禁用 | 负向 prompt 拦截 photorealistic motor cross-section |
| 长宽比 | 1024×1024 默认 | T01/T07 → 1792×1024，T04 → 1024×1280，T05 → 1280×1024 |
| Bus 标签 | "Internal Bus" 占位 | 强制 CAN / CAN-FD / SPI / XCP 显式名 |
| T03 边数 | 模型自由发挥 | 显式 EDGES 枚举，禁止追加 |
| 概念水印 | 可选 | T04 / T05 强制 CONCEPT ONLY watermark |

---

## 4. 12 方案 r01 重点修订矩阵

| 方案 | P0 必修 | 关键 r01 增补 |
|---|---|---|
| S01 negative_d_axis_field_weakening | T03 锁死 7 条转移 | 显式枚举 + Fault Fallback 红边 |
| S02 mtpa_fw_mtpv_control | T03 mode reset 指向 MTPA idle | LUT CRC fallback 红边；T08 bus 显式 |
| S03 svpwm_overmodulation | T03 去重 voltage utilization 标签 | 修复转移逻辑 |
| S04 nonlinear_flux_lut | T04 重做（密度）；T05 重做（牌号 BLOCKER） | flat isometric only，禁止 NdFeB 等 |
| S05 magnetic_saturation_codesign | T03 标题改 "GEOMETRY CO-DESIGN PIPELINE" | 禁止 MOTOR CONTROLLER 通用标题 |
| S06 pmasynrm_high_saliency_low_pm | T03 去掉 Fault Fallback（catalog 无） | 5 状态固化 |
| S07 variable_magnetization_memory_motor | T05 重做（材料 + 写实 BLOCKER） | RESEARCH POOL CONCEPT 水印 |
| S08 hybrid_excitation | T03 修正箭头方向（recover 回 idle，非 three-var）；T05 BLOCKER | 修正方向 + flat illustration |
| S09 winding_reconfiguration | — | T03 illegal-state 手动恢复 |
| S10 multiphase_phase_group_control | — | T03 shut down 后禁止自恢复 |
| S11 thermal_demag_safety_protection | — | T07 用真实 DVP IDs S11-DV-001..005 |
| S12 weighted_efficiency_pareto_selection | T03 标题改 "PARETO SCORECARD PIPELINE" | 去 trophy 装饰 |

---

## 5. 下一步推进

| ID | 行动 | 责任 |
|---|---|---|
| R01-DRAW-01 | 重生 P0 8 张 r01 PNG | 用户手动逐张 |
| R01-DRAW-02 | 推荐重生 P1 40 张 | 用户手动逐张 |
| R01-CONF-01 | `gpt-image-2/prompts/schemes.json` 加 size 覆盖 | 下一轮代码变更 |
| R01-REVIEW-01 | r01 出图后做第二轮评审 | 下一轮 Claude |

---

## 6. 不可破坏边界（同 r00）

- 生图产物不是 EDA / CAD / FEA 输出。
- 生图不会把 `engineering_validated` 提升为 `true`。
- 任何方案语义改动必须先回到草案 / `.drawio` 源。
- r01 收敛只改善"图与提示词对齐"，不改善"图与真实工程交付物等价"。

---

## 7. 关联文档索引

| 文档 | 路径 | 用途 |
|---|---|---|
| r00 评审报告（MD） | `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md` | 96 张评级与共性问题 |
| r00 评审报告（HTML） | `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.html` | 离线阅读版 |
| r00 提示词目录 | `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18.md` | 基线 prompt |
| r01 提示词目录 | `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18_r01.md` | 收敛 prompt |
| 工作清单 | `codex-review/docs/image_worklist_2026-05-18/README.md` | 操作步骤索引 |
| 图档归档 | `gpt-image-2/outputs/SXX/` | r00 PNG + prompt.txt |
