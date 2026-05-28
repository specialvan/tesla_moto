# V2-S07 r03 生产参数化生图提示词包

目标：把 S07 从“可变磁链代理”升级为可审查的磁化脉冲硬件、磁路、控制状态机和证据追溯工程图。

## SIM ANCHOR

```text
scheme_id: variable_magnetization_memory_motor
simulation_status: binding_smoke_passed
model_maturity: research_pool_proxy
sim_binding: engineering/v2/scheme-07/parameters/V2-S07-PARAM-sim_binding-r02.json
pytest_gate: tests/test_scheme_experiment_acceptance.py
engineering_validated: false
next_simulation_step: Add state transition energy, state confidence, and unknown-state derating to the variable flux experiment.
```


## 通用负面约束

- 不要画营销海报、科幻电机、抽象磁场光效。
- 不要生成虚构品牌、真实供应商 Logo 或不可读小字。
- 不要把 `psi_f` 代理仿真画成已验证量产结论。
- 所有图必须保留英文工程标签、状态门槛和 safety interlock 标识。
- 所有图必须可见标注 `engineering_validated = false`、`research pool proxy only`、`evidence_gap`。
- 脉冲电流、脉宽、能量和 interlock 延迟必须标为 design target，不是硬件验证结果。
- PNG/prompt 仅为 concept illustration，不是 production drawing 或 validation evidence。

## 图 1：Magnetization pulse driver PCB

Prompt: Generate a white-background engineering schematic titled “S07 Memory Motor Magnetization Pulse Driver PCB”. Include 800V energy storage, precharge, discharge, pulse switch, isolated gate driver, DESAT, UVLO, magnetization coil terminals, pulse current sensing, coil voltage sensing, traction inverter hardware interlock, HVIL, gate-disable latch, and S11 safety request. Mark 1000A peak pulse, 50us pulse width, 100J energy limit, and interlock latency below 1ms. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S07 | model_maturity=research_pool_proxy | simulation_status=binding_smoke_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 2：Variable magnetization CAD cutaway

Prompt: Generate an isometric CAD cutaway titled “S07 Memory Motor Variable Magnetization Magnetic Path”. Show reversible magnet segments, rotor bridges, magnetization coil path, eight flux-state arrows, thermal path, temperature sensors, mechanical retention, and unknown-state observer reference marks. Use readable English labels and realistic CAD technical drawing style. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S07 | model_maturity=research_pool_proxy | simulation_status=binding_smoke_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 3：Flux state machine

Prompt: Generate a controller state-machine diagram titled “S07 Memory Motor Flux State Machine”. Nodes: Flux Known, Magnetize Request, Pulse Armed, Pulse Fire, Verify State, Unknown-State Fallback, Fault Shutdown. Transitions labeled by flux confidence, magnet temperature, pulse current, coil voltage, traction gate disabled, HVIL, life counter, and S11 safety request. Red arrows for safety fallback, blue arrows for normal flow. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S07 | model_maturity=research_pool_proxy | simulation_status=binding_smoke_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S07 Evidence Chain: Proxy Flux Scaling to Magnetization Hardware Gate”. Flow: EXP-002 proxy -> magnetic FEA -> pulse circuit stress -> thermal retention -> HIL state observer -> DVP life cycling -> gate review. Include warning callout “proxy flux scaling is not validation”. Callout: engineering_validated = false; evidence_gap.
Anchor: S07 | model_maturity=research_pool_proxy | simulation_status=binding_smoke_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

