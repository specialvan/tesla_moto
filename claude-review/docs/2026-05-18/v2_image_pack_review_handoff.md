# V2 生图包 r00 评审 → r01 提示词 Handoff

日期：2026-05-18
评审者：Claude（claude-mainline 分支）
范围：12 方案 × 8 模板 = 96 张 r00 PNG（`gpt-image-2/outputs/`）→ 96+ 张 r01 提示词（`codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18_r01.md`）

---

## 1. 本轮做了什么

1. 深度评审 r00 生图 96 张（采样 ~20 张关键图），输出三轴评级：工程语义 / 风格基线 / 不可破坏边界。
2. 落地评审报告 + r01 提示词目录 + HTML 快照 + Wiki：
   - `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md`
   - `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.html`
   - `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18_r01.md`
   - `wiki/v2_image_pack_r01_prompts_wiki.md`
   - `codex-review/docs/image_worklist_2026-05-18/README.md`（接入 r01 索引）
3. 锁定 P0 必修 8 张：S01/S02/S03/S04 T03、S05/S06/S12 T03 标题、S04 T04、S04/S07/S08 T05。
4. 锁定 BLOCKER 违规：S04/S07/S08 T05 出现真实材料牌号（M270-35A、NdFeB、SmCo、ADC12 等）与写实 3D motor render，必须重生。

## 2. 本轮没做什么

1. 未触发任何新的生图调用；r00 PNG 仍是 r00。
2. 未修改 `engineering/v2/scheme-XX/` 任何 markdown 草案、`.drawio` 或 mermaid 源。
3. 未修改 `gpt-image-2/prompts/schemes.json`；尺寸覆盖建议留给下一轮。
4. 未把 `engineering_validated` 改成 `true`。

## 3. 评审证据采样矩阵

实际打开评审的图：

| 方案 | T01 | T02 | T03 | T04 | T05 | T06 | T07 | T08 |
|---|---|---|---|---|---|---|---|---|
| S01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| S02 | — | — | ✓ | — | — | — | — | ✓ |
| S03 | ✓ | — | ✓ | — | — | — | — | — |
| S04 | ✓ | — | ✓ | ✓ | ✓ | — | — | — |
| S05 | — | — | ✓ | — | — | — | — | — |
| S06 | — | — | ✓ | — | — | — | — | — |
| S07 | — | — | ✓ | — | ✓ | — | — | — |
| S08 | — | — | ✓ | — | ✓ | — | — | — |
| S09 | — | — | ✓ | — | — | — | — | — |
| S10 | — | — | ✓ | — | — | — | — | — |
| S11 | ✓ | — | ✓ | ✓ | — | — | ✓ | — |
| S12 | ✓ | — | ✓ | — | — | — | — | — |

未被打开但被评估的张数：其余 ~75 张按 prompt + 共性规律外推。已被打开评审的 ~21 张能覆盖全部 8 模板与 12 方案的差异组合。

## 4. r01 P0 必修 8 张定位

| # | 文件 | 失败原因 | r01 prompt 入口 |
|---|---|---|---|
| 1 | `gpt-image-2/outputs/S01/V2-S01-ILL-T03-state_machine-r00.png` | 缺 `V margin < limit` 转移；fault state 无红边 | `r01_catalog §2.1` |
| 2 | `gpt-image-2/outputs/S02/V2-S02-ILL-T03-state_machine-r00.png` | `mode reset` 指向 Derate（应指 MTPA idle） | `r01_catalog §2.2` |
| 3 | `gpt-image-2/outputs/S03/V2-S03-ILL-T03-state_machine-r00.png` | `voltage utilization rising` 与 `Vdc recovered` 在多边重复 | `r01_catalog §2.3` |
| 4 | `gpt-image-2/outputs/S04/V2-S04-ILL-T04-pcb_sheet_concept-r00.png` | 信号密度过高、缺 CONCEPT 水印 | `r01_catalog §2.4` |
| 5 | `gpt-image-2/outputs/S04/V2-S04-ILL-T05-cad_packaging_concept-r00.png` | M270-35A / NdFeB / ADC12 / C11000 真实牌号 + 写实 3D | `r01_catalog §2.4`（BLOCKER） |
| 6 | `gpt-image-2/outputs/S05/V2-S05-ILL-T03-state_machine-r00.png` | 顶端 "MOTOR CONTROLLER SUBSYSTEM" 通用标题 | `r01_catalog §2.5` |
| 7 | `gpt-image-2/outputs/S06/V2-S06-ILL-T03-state_machine-r00.png` | 模型加了 6 号 `Fault Fallback`（catalog 5 状态） | `r01_catalog §2.6` |
| 8 | `gpt-image-2/outputs/S07/V2-S07-ILL-T05-cad_packaging_concept-r00.png` | M235-35A / 35PN440 / SmCo / NdFeB + 420×290×130mm + 写实 motor render | `r01_catalog §2.7`（BLOCKER） |

补充 BLOCKER：`S08 T05` 同 S07 模式，写实 3D motor，需按 `r01_catalog §2.8` 重做。

另：`S08 T03` 状态机箭头方向错误（"if reference set" 反、"recover" 反），按 `r01_catalog §2.8` 显式枚举修复，不能用改图模式补救。

`S12 T03` 同 GEN-01 标题问题，按 `r01_catalog §2.12` 重生。

## 5. 下一轮入口

| 任务 | 推荐执行者 | 工具 |
|---|---|---|
| 重生 P0 8 张 + BLOCKER 修补（共 ≥ 10 张） | 用户手动 + `gpt-image-2` CLI | `r01_catalog §2 / §3` prompt 整段粘贴 |
| 重生 P1 40 张（T02 sequence + T05 CAD 一批） | 用户手动 | 同上 |
| `gpt-image-2/prompts/schemes.json` 单条尺寸覆盖 | 下一轮代码变更 | `r01_catalog §1.3` |
| r01 二次评审 | 下一轮 Claude | 比较 r00 vs r01，落到 `claude-review/docs/2026-05-19/...` |
| 把 r01 PNG 归档到 `engineering/v2/scheme-XX/illustrations/` | 用户或下一轮 | `image_worklist §4` 命名规则 |

## 6. 关键决策记录

1. **不修复 r00 PNG，重生 r01 PNG**：改图模式无法修复状态机方向反、缺转移、真实牌号等语义问题。
2. **r01 不引入新增图档类型**：仍是 T01..T08 8 模板；新需求走 r02。
3. **r01 提示词与 r00 共存**：r00 catalog 保留为历史快照，r01 catalog 作为当前主源。
4. **概念水印强制化**：T04 / T05 必须显式 `CONCEPT ONLY · NOT FOR LAYOUT · r01` watermark，阻止误读。
5. **研究池方案 S07 / S08 强化标注**：r01 在 T01 / T03 / T05 / T08 加 `RESEARCH POOL CONCEPT` watermark。

## 7. 风险与未决

| 风险 | 影响 | 缓解 |
|---|---|---|
| 模型仍可能忽略 hex 颜色或显式枚举 | r01 出图仍偏差 | 配合改图模式 + 手工筛选 |
| 真实牌号可能以变体出现（如 "M270-35"、"ADC-12"） | 负向 prompt 漏检 | r01 出图后人工目视审查 |
| `gpt-image-2/prompts/schemes.json` 尺寸覆盖未本轮落地 | T01 16:9 仍可能落 1:1 | 下一轮执行 R01-CONF-01 |
| r01 二次评审未排期 | r01 质量无人复核 | 下一轮 Claude 在 2026-05-19 排查 |

## 8. 与上一轮（V2 P0 DVP&R 草案）的关系

注：本仓库仍存在 V2 P0 DVP&R 草案与 v0.3 control LUT mainline closure 等未提交变更（见 `git status`）。本轮 r00 评审 + r01 提示词包是独立的工作流，建议作为单独 commit；其余历史变更按原有节奏提交。
