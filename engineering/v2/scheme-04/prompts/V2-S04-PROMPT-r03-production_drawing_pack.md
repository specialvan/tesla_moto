# V2-S04 r03 生产参数化生图提示词包

目标：把 S04 非线性磁链 LUT 从 synthetic fixture / smoke binding 升级为可审查的 FEA LUT 来源、边界检查、插值 fallback 和证据追溯工程图。

## 通用负面约束

- 不要把 `models/flux_lut_sample.json` 画成 FEA-derived validation。
- 不要画真实材料牌号、真实供应商 Logo 或不可读小字。
- 不要隐藏 synthetic fixture / sample-only 状态。
- 所有图必须保留英文工程标签、synthetic fixture、FEA gap、fallback active 标识。
- 明确标注 `engineering_validated = false`。

## 图 1：LUT observer input PCB page

Prompt: Generate a white-background engineering schematic titled “S04 Nonlinear Flux LUT Observer Inputs”. Include phase current ADC, resolver/encoder theta_e input, Vdc sensing, temperature sensing, MCU dq transform, LUT address generator, bilinear interpolation block, residual monitor, out-of-bounds detector, fallback to linear dq, NVM LUT storage, CRC checker, and S11 safety request. Mark current ADC 12-bit ±0.5% FS, resolver delay <= 60 us, temperature detection <= 1 ms, and residual_high threshold 12%. Use red fallback paths and amber synthetic-fixture callouts.

## 图 2：FEA geometry and LUT source package

Prompt: Generate a four-panel engineering drawing titled “S04 FEA Geometry Source to Flux LUT Package”. Panels: dq-axis rotor/stator geometry source, id/iq grid definition, lambda_d/lambda_q LUT surface, temperature slice placeholder. Show current r02 sample as 3x3 synthetic LUT and r03 target as >=30x30 with >=5 temperature slices. White background, CAD/FEA technical style, no real material trade names, no manufacturing release claims.

## 图 3：LUT interpolation and fallback state machine

Prompt: Generate a controller state-machine diagram titled “S04 Flux LUT Interpolation and Fallback Guard”. Nodes: LUT Ready, Interpolate Bilinear, Bounds Check, Residual Monitor, Linear-dq Fallback, Fault Derate. Transitions labeled by id/iq in bounds, out_of_flux_lut_bounds, residual_high > 12%, CRC fail, temperature slice missing, and S11 safety request. Use blue nominal data path, red fallback path, and callout “synthetic LUT smoke binding only”.

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S04 Evidence Chain: Synthetic LUT to FEA-backed Evidence Plan”. Flow: flux_lut_sample synthetic fixture -> schema/runtime smoke test -> nonlinear control LUT branch -> FEA geometry source target -> >=30x30 id/iq grid target -> temperature slices target -> bench correlation plan -> DVP gate plan. Include warning callout “sample-only LUT is not FEA validation; engineering_validated = false; evidence_gap”.
