# V2 方案图档生产参数化提示词 handoff（r01/r02/r03）

## 目的

本 handoff 串联 V2 方案图档从 r01 概念提示词、r02 参数/绑定表，到 r03 production drawing prompt pack 的交接关系，确保后续生图、审查和证据补强不会把代理仿真误写成工程验证。

## 分层定义

- r01 prompt：方案级概念图档提示词，用于表达控制/结构/安全意图。
- r02 参数/绑定：把方案约束绑定到参数 sheet、acceptance harness、schema/sample、pytest 或 smoke gate。
- r03 production prompt：把图档升级为可审查的 PCB、CAD、状态机和 evidence traceability 图，但仍保留 proxy / estimate / evidence gap 标识。

## 当前覆盖矩阵

| 方案 | r01 prompt | r02 参数/绑定 | r03 production prompt | 状态 |
|---|---:|---:|---:|---|
| S01 | 有 | 有 | 有 | 本轮补齐 |
| S02 | 有 | 有，最完整 | 有 | 本轮补齐 |
| S03 | 有 | 有 | 有 | 已覆盖 |
| S04 | 有 | 有 | 有 | 本轮补齐 |
| S05 | 有 | 有 | 有 | 已覆盖 |
| S06 | 有 | 有 | 有 | 已覆盖 |
| S07 | 有 | 有 | 有 | 已覆盖，research pool |
| S08 | 有 | 有 | 有 | 已覆盖，research pool |
| S09 | 有 | 有 | 有 | 已覆盖，research pool |
| S10 | 有 | 有 | 有 | 已覆盖，research pool |
| S11 | 有 | 有 | 有 | 本轮补齐 |
| S12 | 有 | 有 | 有 | 已覆盖 |

## r03 prompt pack 索引

- S01：`engineering/v2/scheme-01/prompts/V2-S01-PROMPT-r03-production_drawing_pack.md`
- S02：`engineering/v2/scheme-02/prompts/V2-S02-PROMPT-r03-production_drawing_pack.md`
- S03：`engineering/v2/scheme-03/prompts/V2-S03-PROMPT-r03-production_drawing_pack.md`
- S04：`engineering/v2/scheme-04/prompts/V2-S04-PROMPT-r03-production_drawing_pack.md`
- S05：`engineering/v2/scheme-05/prompts/V2-S05-PROMPT-r03-production_drawing_pack.md`
- S06：`engineering/v2/scheme-06/prompts/V2-S06-PROMPT-r03-production_drawing_pack.md`
- S07：`engineering/v2/scheme-07/prompts/V2-S07-PROMPT-r03-production_drawing_pack.md`
- S08：`engineering/v2/scheme-08/prompts/V2-S08-PROMPT-r03-production_drawing_pack.md`
- S09：`engineering/v2/scheme-09/prompts/V2-S09-PROMPT-r03-production_drawing_pack.md`
- S10：`engineering/v2/scheme-10/prompts/V2-S10-PROMPT-r03-production_drawing_pack.md`
- S11：`engineering/v2/scheme-11/prompts/V2-S11-PROMPT-r03-production_drawing_pack.md`
- S12：`engineering/v2/scheme-12/prompts/V2-S12-PROMPT-r03-production_drawing_pack.md`

## P0 四方案交接重点

### S01 Field Weakening

- r02 已覆盖 demag estimate、弱磁限幅、feasibility map 与 S11 安全关联。
- r03 图档必须呈现采样链、busbar/sensor/HV-LV 包装、`id_min(T,fault)` 状态机和证据链。
- 不得把 demag estimate 画成 bench/FEA validation。

### S02 MTPA / FW / MTPV

- r02 已覆盖 LUT 生成、扭矩轴扩展、模式切换 jump soft gate。
- r03 图档必须呈现 NVM A/B bank、CRC-32、XCP calibration、模式连续性和 Rs/Ld/Lq/psi_f evidence gap。
- `<=60 A` 是 r02 proxy soft gate，r03 目标应显式标注 `<=30 A`。

### S04 Nonlinear Flux LUT

- r02 当前仍是 synthetic fixture / smoke binding，不能上升为 FEA-derived validation。
- r03 图档必须呈现 LUT observer 输入、FEA geometry source、插值 fallback 状态机和 sample-only 到 FEA-backed 的证据链。
- 需要持续保留 `engineering_validated = false`、synthetic fixture、FEA gap 标识。

### S11 Thermal Demag Safety

- r02 已覆盖温度阈值、DemagLimit estimate、gate-disable 目标和安全边界实验。
- r03 图档必须呈现三温度链路、硬件 latch、传感器开短路检测、critical gate-disable 和 FMEDA/ASIL evidence gap。
- 不得把 r02/r03 proxy 画成 ASIL 验证或量产安全件 release。

## 后续建议

1. 用 r03 prompt pack 生成首轮图档后，逐张回填图档 ID、生成参数、模型版本和人工审查结论。
2. 对 S01/S02/S04/S11 优先补 bench/FEA/HIL evidence slot，避免图档成为“仅提示词完整”。
3. 下一轮成熟度审查应检查所有 prompt 是否保留 `engineering_validated = false`、proxy gate、evidence gap 和 S11 安全链路。
