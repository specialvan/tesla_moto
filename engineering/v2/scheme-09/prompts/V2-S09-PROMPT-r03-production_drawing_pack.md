# V2-S09 r03 生产参数化生图提示词包

目标：把 S09 从“绕组参数代理”升级为可审查的开关矩阵、可重构绕组封装、切换状态机和瞬态证据追溯工程图。

## 通用负面约束

- 不要画营销海报、概念电机或抽象电流光效。
- 不要生成虚构品牌、真实供应商 Logo 或不可读小字。
- 不要把静态 Ke/Kt 代理画成已验证切换安全。
- 所有图必须保留英文工程标签、illegal-state interlock、arc suppression 和 S11 safety request 标识。
- 所有图必须可见标注 `engineering_validated = false`、`research pool proxy only`、`evidence_gap`。
- 800V/300A、switching window、circulating current 和 arc suppression 必须标为 DVP target，不是切换暂态验证结果。
- PNG/prompt 仅为 concept illustration，不是 production drawing 或 validation evidence。

## 图 1：Winding switch matrix schematic

Prompt: Generate a white-background engineering schematic titled “S09 Winding Reconfiguration Switch Matrix”. Include HV contactors or solid-state switches, star/delta or series/parallel winding paths, coil/gate drivers, position feedback, zero-torque window enable, zero-current detector, circulating current sensing, snubbers, TVS arc suppression, HVIL, illegal-state hardware interlock, and S11 safety request. Mark 800V/300A class, interlock below 1ms, switching window 50-200ms, circulating current below 5A. Callout: proxy only; engineering_validated = false; evidence_gap.

## 图 2：Reconfigurable winding CAD package

Prompt: Generate an isometric CAD cutaway titled “S09 Reconfigurable Winding and Switch Matrix Package”. Show stator end-turns, winding taps, HV switch matrix, star/delta or series/parallel busbar paths, insulated terminals, shielded harness, service cover, temperature sensors, creepage/clearance callouts, and thermal path arrows. White background, realistic CAD technical drawing style. Callout: proxy only; engineering_validated = false; evidence_gap.

## 图 3：Winding reconfiguration state machine

Prompt: Generate a controller state-machine diagram titled “S09 Winding Reconfiguration State Machine”. Nodes: Config A Active, Switch Request, Zero-Torque Window, Open Old Path, Close New Path, Config B Active, Illegal-State Fallback, Fault Shutdown. Transitions labeled by torque request, phase current, switch feedback, switch voltage, circulating current, arc detection, HVIL, and S11 safety request. Red fallback arrows and blue normal switching arrows. Callout: proxy only; engineering_validated = false; evidence_gap.

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S09 Evidence Chain: Static Winding Proxy to Switching Transient Gate”. Flow: EXP-008 proxy -> circuit transient model -> arc suppression model -> HIL zero-torque switching -> thermal and NVH model -> DVP stuck/open/short fault -> gate review. Include warning callout “static winding proxy is not switching validation”. Callout: engineering_validated = false; evidence_gap.
