# V2-S08 r03 生产参数化生图提示词包

目标：把 S08 从“等效励磁代理”升级为可审查的励磁变换器、励磁绕组封装、三变量控制和证据追溯工程图。

## 通用负面约束

- 不要画营销海报、概念电机或抽象磁场光效。
- 不要生成虚构品牌、真实供应商 Logo 或不可读小字。
- 不要把 `psi_eff` 代理仿真画成已验证量产结论。
- 所有图必须保留英文工程标签、thermal derate、loss-of-field 和 safety request 标识。
- 所有图必须可见标注 `engineering_validated = false`、`research pool proxy only`、`evidence_gap`。
- field converter、loss-of-field 和 thermal derate 必须标为 control target / DVP target，不是已验证硬件结果。
- PNG/prompt 仅为 concept illustration，不是 production drawing 或 validation evidence。

## 图 1：Field excitation converter PCB

Prompt: Generate a white-background engineering schematic titled “S08 Hybrid Excitation Field Converter PCB”. Include 48V field supply, bidirectional field DC/DC or H-bridge, field winding connector, field current sensing, field voltage sensing, winding temperature input, isolated power, isolated communication, loss-of-field detector, hardware fault latch, traction torque derate request, and S11 safety request. Mark field current range -20A to 30A and loss-of-field detection below 5ms.

## 图 2：Field winding CAD package

Prompt: Generate an isometric CAD cutaway titled “S08 Hybrid Excitation Field Winding Package”. Show field winding, insulation class H layers, rotor/stator magnetic path, optional brushless excitation interface, terminal routing, cooling jacket, temperature sensors, psi_eff flux arrows, and loss-of-field risk callouts. White background, realistic CAD technical drawing style.

## 图 3：id-iq-if controller

Prompt: Generate a controller block and state diagram titled “S08 Hybrid Excitation id-iq-if Control”. Include torque request, MTPA/FW optimizer, id/iq current loop, field current loop, psi_eff estimator, voltage margin guard, field thermal derate, loss-of-field detector, PM-assist fallback, and S11 safety request. Use red safety fallback arrows and blue normal-control paths.

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S08 Evidence Chain: psi_eff Proxy to Field Excitation Gate”. Flow: EXP-007 proxy -> magnetic FEA -> field converter model -> winding thermal model -> HIL loss-of-field fallback -> DVP thermal and bench correlation -> gate review. Include warning callout “psi_eff proxy is not validation”.
