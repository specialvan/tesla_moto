# 12 方案图档生图工作清单

更新日期：2026-05-18  
工作流：**手动**逐张上传参考图 + 复制提示词 → 生图 → 下载 PNG → 汇总归档  
落点目录：`codex-review/docs/image_worklist_2026-05-18/`  
配套文档：
- `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18.md`（r00 模板与差分 token 详释）
- `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18_r01.md`（**r01 提示词目录**，2026-05-18 评审后产出）
- `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md`（r00 96 张深度评审，列 P0/P1/P2 修订优先级）

## r01 接入说明

1. r00 96 张 PNG 已落地 `gpt-image-2/outputs/SXX/V2-SXX-ILL-TYY-...-r00.png`，本清单 §5 的 r00 复选框可在落档后陆续勾选。
2. r01 提示词只迭代评审 P0/P1 级问题，P2 保留 r00。
3. r01 出图按 `-r01.png` 命名，与 r00 共存于同目录，不覆盖 r00。
4. r01 prompt 与改图工作流详见 `scheme_drawing_prompt_catalog_2026-05-18_r01.md` §2 / §3 / §4。

## 0. 不可破坏的边界

1. 本目录所有生成图只用于 **概念示意 / 评审可视化**，不替代 EDA / CAD / FEA / 制造文件。
2. 任何生成图都 **不会** 把 `engineering_validated` 改成 `true`。
3. 标注语言以英文为主（与 `.drawio`、mermaid 一致），中文只用于副标题。
4. 不允许在生图里出现：人脸 / marketing 渲染 / 任意厂商 LOGO / 任意可识别的真实零件号。
5. 任何"看起来很像真实 PCB layout / STEP 模型"的输出，必须在文件名加 `concept-` 前缀提醒读者。

## 1. 通用风格基线

每次生图都把以下两段贴到提示词（生图工具支持负向 prompt 的情况下）。

### 1.1 正向风格 token（拼在每条 prompt 末尾）

```text
technical engineering schematic, flat infographic style, clean vector look,
dark navy background, pale blue node fills, gold and white labels,
crisp sans-serif typography, high contrast, orthogonal connectors,
professional automotive powertrain documentation aesthetic, single image
```

### 1.2 负向 prompt（统一）

```text
photorealistic faces, glamour photography, marketing render, watercolor,
cartoon mascots, anime style, low contrast, blurry, motion blur, lens flare,
busy decorative background, fake measurement units, hand-drawn sketch noise,
chinese calligraphy stroke, emoji, watermark, logo, real manufacturer parts,
real component photos
```

### 1.3 生图参数建议

| 参数 | 推荐 | 说明 |
|---|---|---|
| 尺寸 | 1024×1024 | 截图工具默认 |
| 数量 | 先 1 张 | 满意再加张 |
| 风格 | 鲜明 | 截图工具有该选项 |
| 格式 | PNG | 透明背景非必需 |
| 比例 | T01/T08 用 16:9 | 横向块图更舒展 |

## 2. 图档类型与优先级

12 方案 × 8 类 = 96 张图。按工程评审价值分三档：

| 模板 | 类型 | 数量 | 优先级 | 说明 |
|---|---|---|---|---|
| T01 | 驱动设计图 | 12 | **P0** | 系统块图，对外讲解第一张 |
| T03 | 控制器状态机 | 12 | **P0** | 控制评审最关键的图 |
| T04 | PCB 页面草案 | 12 | **P1** | 接口闭合直观图 |
| T05 | 3D/CAD 封装边界 | 12 | **P1** | 物理布局直觉 |
| T08 | 协议链路 | 12 | **P1** | 软件 / 通信架构图 |
| T02 | 上电时序 | 12 | **P2** | 评审常引用，但密度低 |
| T06 | BOM/EDA 风险树 | 12 | P2 | 辅助型 |
| T07 | 测试树 | 12 | P2 | 辅助型 |

**P0 = 这次必做**：24 张。  
**P1 = 下一轮做**：36 张。  
**P2 = 视精力做**：36 张。

方案分册（`scheme-01.md` … `scheme-12.md`）按方案完整列出 8 张图，每张图都给可粘贴 prompt；你按 P0 → P1 → P2 顺序生即可。

## 3. 96 张图就绪矩阵

| 方案 | T01 driver | T02 sequence | T03 state | T04 PCB | T05 CAD | T06 BOM | T07 Test | T08 protocol |
|---|---|---|---|---|---|---|---|---|
| S01 negative_d_axis_field_weakening | mmd | mmd | drawio | 无 | 无 | 无 | 无 | mmd |
| S02 mtpa_fw_mtpv_control | mmd | mmd | drawio | 无 | 无 | 无 | 无 | mmd |
| S03 svpwm_overmodulation_voltage_utilization | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |
| S04 nonlinear_flux_lut | mmd | mmd | drawio | 无 | 无 | 无 | 无 | mmd |
| S05 magnetic_saturation_codesign | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |
| S06 pmasynrm_high_saliency_low_pm | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |
| S07 variable_magnetization_memory_motor | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |
| S08 hybrid_excitation | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |
| S09 winding_reconfiguration | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |
| S10 multiphase_phase_group_control | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |
| S11 thermal_demag_safety_protection | mmd | mmd | drawio | 无 | 无 | 无 | 无 | mmd |
| S12 weighted_efficiency_pareto_selection | mmd | mmd | 无 | 无 | 无 | 无 | 无 | mmd |

矩阵格说明：

- `drawio`：可用 draw.io 桌面端把对应 `.drawio` 导出为 PNG，再上传给生图工具作"改图"输入。
- `mmd`：可在 VS Code 用 Mermaid 预览插件，或本机 `mmdc` 渲染对应 mermaid 块为 PNG，再上传作"改图"输入。
- `无`：仓库无现成像素源，先用纯 prompt 走"生图"出 v0，再把 v0 作参考图迭代。

## 4. 推荐归档结构

每张生成图建议落到对应方案目录的 `illustrations/` 子目录（当前不存在，第一次落图时新建）：

```text
engineering/v2/scheme-01/illustrations/
  V2-S01-ILL-T01-driver_block-r00.png
  V2-S01-ILL-T01-driver_block-r00-prompt.txt
  V2-S01-ILL-T02-power_on_sequence-r00.png
  V2-S01-ILL-T02-power_on_sequence-r00-prompt.txt
  ...
  V2-S01-ILL-T08-protocol_link-r00.png
  V2-S01-ILL-T08-protocol_link-r00-prompt.txt
```

命名规则：

```text
V2-S{编号:02}-ILL-T{模板号}-{语义短名}-r{修订号:02}.png
```

每张 PNG 旁边必须有同名 `-prompt.txt`，里面保存：

```text
[date]    2026-05-18
[tool]    text-to-image (vivid 1024x1024, gpt backend)
[mode]    生图 or 改图
[reference image] <相对路径或"无">
[positive prompt]
<最终生效的完整 prompt>
[negative prompt]
<最终生效的负向 prompt>
[notes]
<本张图的关键调参备注>
```

这样 6 个月后任何人都能复现这张图。

## 5. 进度勾选总表

请用 markdown 复选框直接编辑此表，每生成并归档一张就勾。本表是手动进度面板，不会被自动化覆盖。

### 5.1 P0 必做（24 张）

| 方案 | T01 driver | T03 state |
|---|---|---|
| S01 | [ ] | [ ] |
| S02 | [ ] | [ ] |
| S03 | [ ] | [ ] |
| S04 | [ ] | [ ] |
| S05 | [ ] | [ ] |
| S06 | [ ] | [ ] |
| S07 | [ ] | [ ] |
| S08 | [ ] | [ ] |
| S09 | [ ] | [ ] |
| S10 | [ ] | [ ] |
| S11 | [ ] | [ ] |
| S12 | [ ] | [ ] |

### 5.2 P1 推进（36 张）

| 方案 | T04 PCB | T05 CAD | T08 protocol |
|---|---|---|---|
| S01 | [ ] | [ ] | [ ] |
| S02 | [ ] | [ ] | [ ] |
| S03 | [ ] | [ ] | [ ] |
| S04 | [ ] | [ ] | [ ] |
| S05 | [ ] | [ ] | [ ] |
| S06 | [ ] | [ ] | [ ] |
| S07 | [ ] | [ ] | [ ] |
| S08 | [ ] | [ ] | [ ] |
| S09 | [ ] | [ ] | [ ] |
| S10 | [ ] | [ ] | [ ] |
| S11 | [ ] | [ ] | [ ] |
| S12 | [ ] | [ ] | [ ] |

### 5.3 P2 视精力做（36 张）

| 方案 | T02 sequence | T06 BOM tree | T07 Test tree |
|---|---|---|---|
| S01 | [ ] | [ ] | [ ] |
| S02 | [ ] | [ ] | [ ] |
| S03 | [ ] | [ ] | [ ] |
| S04 | [ ] | [ ] | [ ] |
| S05 | [ ] | [ ] | [ ] |
| S06 | [ ] | [ ] | [ ] |
| S07 | [ ] | [ ] | [ ] |
| S08 | [ ] | [ ] | [ ] |
| S09 | [ ] | [ ] | [ ] |
| S10 | [ ] | [ ] | [ ] |
| S11 | [ ] | [ ] | [ ] |
| S12 | [ ] | [ ] | [ ] |

## 6. 方案分册入口

| 方案 | 分册 |
|---|---|
| S01 negative_d_axis_field_weakening | `scheme-01.md` |
| S02 mtpa_fw_mtpv_control | `scheme-02.md` |
| S03 svpwm_overmodulation_voltage_utilization | `scheme-03.md` |
| S04 nonlinear_flux_lut | `scheme-04.md` |
| S05 magnetic_saturation_codesign | `scheme-05.md` |
| S06 pmasynrm_high_saliency_low_pm | `scheme-06.md` |
| S07 variable_magnetization_memory_motor | `scheme-07.md` |
| S08 hybrid_excitation | `scheme-08.md` |
| S09 winding_reconfiguration | `scheme-09.md` |
| S10 multiphase_phase_group_control | `scheme-10.md` |
| S11 thermal_demag_safety_protection | `scheme-11.md` |
| S12 weighted_efficiency_pareto_selection | `scheme-12.md` |

## 7. 单张图操作步骤（粘贴速查）

1. 打开本方案分册 `scheme-XX.md`，找到目标图条目（按 ID，如 `IMG-S01-T03`）。
2. 看「参考图」字段：
   - `drawio` → 用 draw.io desktop 打开对应 `.drawio`，菜单 File → Export as → PNG（建议 2x scale），保存为本地参考图。
   - `mmd` → 在 VS Code 打开 `reports/scheme_driver_power_protocol_diagrams.md`，定位该方案的对应 mermaid 块，预览插件右键导出 PNG，或运行 `mmdc -i temp.mmd -o ref.png`。
   - `无` → 跳过参考图，走纯"生图"路径。
3. 把 `[positive prompt]` 整段复制粘贴到生图工具左侧文本框。
4. 如果工具支持负向 prompt，把第 1.2 节负向 prompt 复制进去。
5. 选 1024×1024、鲜明、PNG，1 张，生图。
6. 不满意就在工具里切到「改图」，上传 v0 当参考图，再贴改图提示词（每个条目末尾有"改图微调建议"段）。
7. 满意后下载 PNG，按第 4 节命名规则改名，放到 `engineering/v2/scheme-XX/illustrations/`。
8. 在同目录建 `<同名>-prompt.txt`，按第 4 节格式记录最终 prompt。
9. 回到本 README 第 5 节勾掉对应复选框。

## 8. 汇总移交

当某个方案的 P0 + P1 都完成（共 5 张），建议：

1. 在 `engineering/v2/scheme-XX/illustrations/` 加一份 `INDEX.md`，列出本方案所有图、当前修订号和 prompt 文件。
2. 在 `codex-review/docs/landing_progress_log_2026-05-14.md` 追加一行进展记录。
3. 如全部 12 方案都完成 P0，做一次集中评审，再决定要不要进 P1 / P2。

## 9. 改图通用微调指令

如果第一版生图风格偏差大，可在改图模式下追加这些指令（分行任选）：

```text
make background a single solid dark navy color, remove any gradient
make all node fills the same pale blue, only stroke and text vary in color
make all node corners rounded with radius 12 px
use crisp orthogonal connectors only, no diagonal lines
make all labels English sans-serif, all caps for state names
remove any decorative texture from the background
remove any small icons inside nodes, keep text only
ensure no node overlaps another node
ensure every transition has a short English label
make the layout left-to-right (for block diagrams) or grid (for state machines)
```

10 条按需挑 1-3 条贴到改图框，比起完整 prompt 改写更容易收敛。

---

下一步：打开 `scheme-01.md` 开始 P0 两张图。
