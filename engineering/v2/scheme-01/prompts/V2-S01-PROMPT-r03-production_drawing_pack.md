# V2-S01 r03 生产参数化生图提示词包

目标：把 S01 负 d 轴弱磁从概念状态机升级为可审查的采样链、弱磁限幅、安全退磁边界和证据追溯工程图。

## SIM ANCHOR

```text
scheme_id: negative_d_axis_field_weakening
simulation_status: numeric_proxy_passed
model_maturity: parameterized_linear_model
sim_binding: engineering/v2/scheme-01/parameters/V2-S01-PARAM-sim_binding-r02.json
pytest_gate: tests/test_scheme_p0_lut_acceptance.py
engineering_validated: false
next_simulation_step: Replace Rs/Ld/Lq/psi_f estimates with nonlinear-flux LUT / FEA values; lock gate-disable < 100 us latency via r03 bench.
```


## 通用负面约束

- 不要画营销海报、概念车、抽象磁场光效。
- 不要生成虚构品牌、真实供应商 Logo 或不可读小字。
- 不要把 r02 demag estimate 或代理仿真画成已验证量产结论。
- 所有图必须保留英文工程标签、CONCEPT / PROXY / GATE 状态标识。
- 明确标注 `engineering_validated = false` 或 “proxy gate only”。

## 图 1：FW sensing and fault PCB page

Prompt: Generate a white-background engineering schematic titled “S01 Field Weakening Sensing and Fault Path”. Include phase current ADC channels ia/ib/ic, Vdc divider, motor temperature input, inverter temperature input, resolver or encoder input, MCU FOC block, gate-disable hardware latch, fault_latched feedback, and S11 safety request. Mark current ADC as 12-bit ±0.5% FS / 100 kSPS, Vdc sense as ±1% FS, temperature detection below 1 ms, and gate-disable target below 100 us. Use blue normal signal paths, red hardware shutdown path, and amber proxy-estimate callouts. Callout: engineering_validated = false; evidence_gap.
Anchor: S01 | model_maturity=parameterized_linear_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_p0_lut_acceptance.py

## 图 2：Busbar / sensor / HV-LV CAD package

Prompt: Generate an isometric CAD cutaway titled “S01 Weakening Sensor and Busbar Package”. Show DC link, three-phase laminated busbar, phase current sensor locations, Vdc sense tap, motor/inverter temperature sensor routing, HV/LV separation, shield ground, service connector, gate-disable wiring path, and cooling contact surface. White background, CAD technical drawing style, no photorealistic marketing render, no real material trade names. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S01 | model_maturity=parameterized_linear_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_p0_lut_acceptance.py

## 图 3：id_min(T,fault) guarded state machine

Prompt: Generate a controller state-machine diagram titled “S01 Guarded Field Weakening State Machine”. Nodes: Torque Idle, MTPA, Field Weakening, Demag-Limited Derate, Sensor-Fault Derate, Gate-Disable Fault. Transitions labeled by voltage margin below 5 V, Vdc recovery, id_min(T,fault), demagnetization risk, sensor invalid, and gate-disable request. Use red safety fallback arrows, blue normal-control arrows, and a callout “r02 demag estimate, not bench validation”. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S01 | model_maturity=parameterized_linear_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_p0_lut_acceptance.py

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S01 Evidence Chain: FW Proxy Gate to Engineering Evidence”. Flow: r02 acceptance sheet -> DemagLimit estimate at 25/100/140 C -> control LUT generator -> feasibility map demagnetization_risk -> S11 thermal safety link -> HIL fault injection plan -> bench/FEA evidence gap. Include warning callout “proxy simulation is not engineering validation”. Callout: engineering_validated = false; evidence_gap.
Anchor: S01 | model_maturity=parameterized_linear_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_p0_lut_acceptance.py

