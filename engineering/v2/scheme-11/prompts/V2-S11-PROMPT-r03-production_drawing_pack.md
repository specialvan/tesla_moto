# V2-S11 r03 生产参数化生图提示词包

目标：把 S11 温度 / 退磁 / 安全保护从简化安全边界模型升级为可审查的温度三链路、demag limit、gate-disable latch 和证据追溯工程图。

## 通用负面约束

- 不要画营销海报、抽象安全盾牌或概念车。
- 不要把 r02 温度阈值 estimate 画成 ASIL / FMEDA / HIL 已验证。
- 不要隐藏 gate-disable 延迟和传感器开短路仍待台架验证。
- 所有图必须保留英文工程标签、warning/critical、hardware latch、evidence gap 标识。
- 明确标注 `engineering_validated = false`。

## 图 1：Thermal demag safety PCB chain

Prompt: Generate a white-background engineering schematic titled “S11 Thermal Demag Safety and Fault Latch PCB”. Include pm_temp dual NTC channels, winding_temp PT1000, oil_temp NTC, Vdc safety window monitor, id_min_allowed lookup, MCU safety monitor, independent hardware fault latch, gate_disable_n output, fault_latched feedback, fault_reason coding, and service-only reset. Mark pm warning/critical 100/120 C, winding warning/critical 140/160 C, oil warning/critical 80/100 C, Vdc critical window 240-420 V, sensor open/short detection below 1 ms, and gate-disable target below 100 us. Use red hardware shutdown path and blue diagnostic path.

## 图 2：Thermal sensor and cooling CAD package

Prompt: Generate an isometric CAD cutaway titled “S11 Thermal Sensor and Cooling Boundary Package”. Show PM temperature sensing location, winding temperature sensing, oil temperature sensor, cooling jacket or oil path, controller thermal path, HV/LV separation, sensor harness routing, service access, and safety latch connection. Add callouts for demag risk rising with temperature and r02 estimate thresholds. White background, CAD technical drawing style, no photorealistic marketing render.

## 图 3：Safety fault state machine

Prompt: Generate a safety state-machine diagram titled “S11 Thermal Demag Fault State Machine”. Nodes: Normal Torque, Thermal Warning Derate, Demag-Limited Derate, Sensor-Unknown Fallback, Critical Gate-Disable, Latched Fault. Transitions labeled by pm_temp, winding_temp, oil_temp, Vdc critical, sensor open/short, demag margin low, service reset, and gate_disable asserted. Use red critical shutdown arrows, amber derate arrows, and blue normal recovery arrows.

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S11 Evidence Chain: Safety Boundary Proxy to Bench Gate”. Flow: r02 temperature thresholds -> DemagLimit estimate 25/100/140 C -> control LUT demagnetization_risk -> safety boundary experiment -> PCB hardware latch draft -> HIL fault injection -> bench gate-disable timing -> FMEDA/ASIL evidence gap. Include warning callout “r02/r03 proxy is not ASIL validation”.
