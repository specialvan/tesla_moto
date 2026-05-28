# V2-S03 r03 生产参数化生图提示词包

目标：把 S03 从“过调制代理实验”升级为可审查的功率级、PCB、控制器和证据追溯工程图。

## SIM ANCHOR

```text
scheme_id: svpwm_overmodulation_voltage_utilization
simulation_status: numeric_proxy_passed
model_maturity: proxy_model
sim_binding: engineering/v2/scheme-03/parameters/V2-S03-PARAM-sim_binding-r02.json
pytest_gate: tests/test_scheme_experiment_acceptance.py
engineering_validated: false
next_simulation_step: Replace parametric harmonic / loss curves with measured inverter loss maps and PWM-reconstructed THD.
```


## 通用负面约束

- 不要画营销海报、概念车、抽象光效。
- 不要生成虚构品牌、真实供应商 Logo 或不可读小字。
- 不要把代理仿真画成已验证量产结论。
- 所有图必须保留英文工程标签和 gate/status 标识。
- 所有图必须可见标注 `engineering_validated = false`、`proxy / estimate only`、`evidence_gap`。
- PNG/prompt 仅为 concept illustration，不是 production drawing 或 validation evidence。

## 图 1：Gate/PWM/EMC PCB 页

Prompt: Generate a clean white-background engineering schematic titled “S03 SVPWM Overmodulation Gate/PWM/EMC Interface”. Include isolated gate drivers, UVLO, DESAT, Miller clamp, three-phase current sensing, DC-link voltage sensing, PWM sampling window, EMI filter, shield ground, gate-disable fault latch, and S11 safety request. Use readable English labels, thin CAD-like lines, blue signal paths, red hardware shutdown path, and amber EMC risk callouts. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S03 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 2：Inverter power stage CAD 剖视

Prompt: Generate an isometric CAD cutaway engineering drawing titled “S03 Overmodulation Inverter Power Stage Package”. Show DC-link capacitor bank, laminated busbar, three-phase power module, gate-driver PCB, cooling plate, HV/LV separation, EMI shield, phase-output current sensors, thermal path arrows, and stray inductance loop annotation. White background, realistic engineering CAD style, no photorealistic marketing render. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S03 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 3：Overmodulation guarded state machine

Prompt: Generate a controller state-machine diagram titled “S03 Guarded Overmodulation State Machine”. Nodes: Linear SVPWM, Overmodulation-1, Overmodulation-2, Six-step Guarded, Fallback Linear, Fault Shutdown. Transitions labeled by k_mod, voltage margin, THD estimate, NVH/EMC guard, inverter temperature, sampling valid, gate-disable request. Use red safety fallback arrows and blue normal-control arrows. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S03 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S03 Evidence Chain: Proxy Simulation to Engineering Gate”. Flow: EXP-005 k_mod sweep -> PWM harmonic model -> inverter loss map -> PCB/CAD thermal path -> THD/EMC/NVH DVP -> gate review. Include warning callout “proxy simulation is not validation”. White background, technical report style. Callout: engineering_validated = false; evidence_gap.
Anchor: S03 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

