# V2 r02 仿真锚点提示词批包

修订日期：2026-05-20  
定位：在 r01 图档提示词之上增加“面向下一轮仿真”的语义层。  
适用范围：12 个 V2 方案的 T01-T08 概念图、PCB/CAD 概念图、验证树、协议链路图。

## 1. 为什么需要 r02 simulation-facing prompt

r01 主要解决的是：

- 修正 r00 图面错连、错标题、错状态机；
- 禁止真实材料牌号、写实 3D、制造假象；
- 嵌入部分工程窗口参数；
- 强制 `CONCEPT ONLY` 边界。

r02 simulation-facing prompt 解决的是另一件事：

```text
让每张图变成“仿真审查锚点”，而不是“漂亮概念图”。
```

每张 r02 图必须能回答：

- 这张图对应哪个 `sim_binding-r02.json`？
- 当前 maturity 是 `binding_smoke_passed`、`numeric_proxy_passed`，还是更高？
- 图里哪些参数会进入 runner？
- 哪些字段由 pytest 强门禁检查？
- 哪些字段仍是 soft check、estimate、synthetic fixture 或 research pool？
- 下一轮仿真要替换什么参数源？

## 2. 与 r01 的关系

本批包不废弃 r01。执行方式是：

1. 先使用 `codex-review/docs/scheme_drawing_prompts_r01_batch/` 的分册 prompt。
2. 再追加本目录 `_simulation_globals.md` 中的 r02 仿真锚点规则。
3. 对 S02、S04 等高风险方案，追加本目录对应的 scheme-specific delta。
4. 输出命名建议：

```text
gpt-image-2/outputs/SXX/V2-SXX-ILL-TYY-<template>-r02-sim.png
gpt-image-2/outputs/SXX/V2-SXX-ILL-TYY-<template>-r02-sim-prompt.txt
```

## 3. 文件入口

| 文件 | 用途 |
|---|---|
| `_simulation_globals.md` | 所有 r02 仿真提示词必须追加的全局规则 |
| `simulation_anchor_matrix.json` | 12 方案的机器可读仿真锚点矩阵 |
| `scheme-02-r02-sim.md` | S02 MTPA/FW/MTPV 的详细仿真提示词增量 |
| `scheme-04-r02-sim.md` | S04 nonlinear flux LUT 的详细仿真提示词增量 |

## 4. 批量优先级

| 批次 | 范围 | 原因 |
|---|---|---|
| P0 | S02 T01/T03/T07/T08 | 当前最接近闭环，但阈值存在 30 A vs 60 A 不一致，必须可视化暴露 |
| P0 | S04 T01/T04/T05/T07 | 当前只是 synthetic fixture / smoke，必须阻断“已验证 LUT”的误读 |
| P1 | S01/S11 T03/T07/T08 | 退磁、安全、温度边界会影响所有控制仿真 |
| P1 | S03/S05/S06/S12 T07 | 代理模型可跑，但要明确 proxy maturity 和下一步物理模型替换 |
| P2 | S07/S08/S09/S10 T01/T07/T08 | research pool，只展示研究输入和下一轮仿真缺口 |

## 5. r02 图面验收标准

每张 r02-sim 图必须同时满足：

1. 有 `SIM ANCHOR` 面板。
2. 有 `maturity` 字段，不允许只写 `passed`。
3. 有 `engineering_validated=false`。
4. 至少引用一个 `sim_binding-r02.json` 或 pytest 路径。
5. 不把图片、PCB/CAD 草案、prompt 文本描述成仿真输入源。
6. 对 synthetic / proxy / research pool 使用红/琥珀风险标识。
7. 对 soft checks 与 strong checks 做视觉区分。

## 6. Claude 下一轮使用方式

打回 Claude 时建议直接要求：

```text
基于 codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/
把 r01 图档提示词升级为 r02-sim 图档提示词。
不要继续追求写实图纸。
每张图必须暴露 sim_binding、maturity、strong/soft checks、next_simulation_step。
```

