# r01 提示词批包全局基线

修订日期：2026-05-18
作用：所有 12 方案 × 8 模板的 r01 提示词共享的正向风格 token、负向 prompt 与尺寸建议。
所有 `scheme-XX-r01.md` 分册末尾必须追加 §1.1；工具支持负向 prompt 时附加 §1.2；尺寸按 §1.3 覆盖。

---

## 1.1 全局正向风格 token（追加到每条 prompt 末尾）

```text
technical engineering schematic, flat infographic style, clean vector look,
single solid dark navy background hex #0B1A33, no gradient, no texture,
node fills pale blue hex #B6C7E0 with gold strokes hex #D8A638,
labels in crisp sans-serif white hex #F2F2F2 and gold hex #D8A638,
fault and safety states use red-tinted stroke hex #C0392B,
high contrast, sharp edges, orthogonal connectors only, no diagonal lines,
professional automotive powertrain documentation aesthetic, single image,
title bar text MUST be: "<SCHEME_TITLE>" — do NOT add any other title,
do NOT add a generic "MOTOR CONTROLLER SUBSYSTEM" title when scheme is not a motor controller.
```

## 1.2 全局负向 prompt

```text
photorealistic faces, glamour photography, marketing render, watercolor,
cartoon mascots, anime style, low contrast, blurry, motion blur, lens flare,
busy decorative background, fake measurement units, hand-drawn sketch noise,
chinese calligraphy stroke, emoji, watermark icon, manufacturer logo,
real manufacturer parts, real component photos,
specific steel grades, specific magnet grades, specific copper grades,
M235-35A, M270-35A, 35PN440, ADC12, C11000, SmCo, NdFeB, FR-4, real material designations,
real engineering dimensions in mm, real torque or current numeric callouts not present in the prompt,
photorealistic 3D motor cross-section, metallic shading, surface reflection,
shadow casting, depth-of-field blur, decorative trophy or icon flourishes,
generic title "MOTOR CONTROLLER SUBSYSTEM" when scheme is not a motor controller,
duplicated arrow labels on different edges,
self-loop arrows that do not return to a different state,
missing transition labels
```

## 1.3 模板长宽比与尺寸建议（落实到 `gpt-image-2/prompts/schemes.json`）

| 模板 | r00 默认 | r01 建议 | 理由 |
|---|---|---|---|
| T01 driver block | 1024×1024 | 1792×1024 | 左右链路长 |
| T02 power-on sequence | 1024×1024 | 1792×1024 | 多 lifeline 横向呼吸 |
| T03 state machine | 1024×1024 | 1024×1024 | 6 状态 2×3 网格 |
| T04 PCB sheet | 1024×1024 | 1024×1280 | 信号名垂直补齐 |
| T05 CAD packaging | 1024×1024 | 1280×1024 | 等轴侧视图横向 |
| T06 BOM tree | 1024×1024 | 1024×1024 | 树状自上而下 |
| T07 verification tree | 1024×1024 | 1792×1024 | 左到右树 |
| T08 protocol link | 1024×1024 | 1024×1280 | 主链垂直 + 旁路诊断 |

## 1.4 显式枚举规则（应用到 T03 / T07 等需逐条列出节点的模板）

```text
You MUST render EXACTLY N nodes/states listed below — no more, no less.
You MUST render EXACTLY M directed edges listed below — no more, no less.
Each edge label MUST appear verbatim in English; do NOT abbreviate.
Do NOT add a self-loop unless it is explicitly listed in EDGES.
Do NOT duplicate any label on multiple edges; each label is unique.
Highlight any node whose label contains "Fault", "Fallback", "Shut down",
"Latched", "Unknown", "Loss-of-field", or "Illegal" with red-tinted stroke
hex #C0392B; all other nodes use gold stroke hex #D8A638.
Reserve at least 80 px of inter-node spacing so orthogonal connectors do not overlap.
```

## 1.5 概念水印（应用到 T04 PCB 与 T05 CAD）

```text
Top-right corner: monospace text "CONCEPT ONLY · NOT FOR LAYOUT · r01" in
gold hex #D8A638, opacity 0.75, font size 18 px.
The image MUST clearly read as a concept, not a manufacturable layout or
a CAD/FEA render. Forbid component pin numbers, real part outlines,
photorealistic shading. For T05 specifically: render as flat isometric line
illustration only — NO shading, NO surface texture, NO metallic reflection,
NO photorealistic motor cross-section. Use generic material category labels
(electrical steel, magnet, copper, insulator, coolant) without grade designations.
```

## 1.6 研究池水印（应用到 S07 / S08 / S09 / S10 所有模板）

```text
Top-left corner: monospace text "RESEARCH POOL CONCEPT · NOT ENGINEERING RELEASE"
in red-tinted hex #C0392B, opacity 0.75, font size 16 px.
This scheme is in the research pool; the diagram does NOT represent a release-grade
artifact and MUST NOT be interpreted as production hardware.
```

## 1.7 引用注释

- 每条 prompt 自带 `<r01 GLOBAL POSITIVE>`、`<r01 GLOBAL NEGATIVE>`、`<r01 ENUM RULE>`、`<r01 CONCEPT WATERMARK>`、`<r01 RESEARCH POOL WATERMARK>` 五种占位符。
- 跑批量前在工具或脚本中先把这些占位符替换为本文件对应段落整段（保留换行）。
