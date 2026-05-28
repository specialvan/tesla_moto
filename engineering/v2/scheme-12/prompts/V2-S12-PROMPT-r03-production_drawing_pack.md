# V2-S12 r03 生产参数化生图提示词包

目标：把 S12 Pareto 从代理排序升级为带候选证据版本、成熟度惩罚和安全 gate 的工程决策图。

## SIM ANCHOR

```text
scheme_id: weighted_efficiency_pareto_selection
simulation_status: numeric_proxy_passed
model_maturity: proxy_model
sim_binding: engineering/v2/scheme-12/parameters/V2-S12-PARAM-sim_binding-r02.json
pytest_gate: tests/test_scheme_experiment_acceptance.py
engineering_validated: false
next_simulation_step: Replace iron loss coefficients with FEA-derived material data; add mechanical loss, inverter loss, and temperature coupling.
```


## 通用负面约束

- 不要把 research rank 画成 engineering release recommendation。
- 不要隐藏 missing evidence。
- 不要只画效率曲线，必须显示 PCB/CAD/BOM/DVP/S11 safety 证据。
- 所有图必须可见标注 `engineering_validated = false`、`proxy ranking only`、`evidence_gap`。
- recommendation allowed 必须表示 candidate-for-review gate，不是工程推荐或量产 release。
- PNG/prompt 仅为 concept illustration，不是 production drawing 或 validation evidence。

## 图 1：Candidate evidence index

Prompt: Generate a matrix titled “S12 Candidate Evidence Index”. Rows: S01 to S12. Columns: PCB evidence, CAD evidence, BOM evidence, DVP evidence, S11 safety binding, maturity penalty, recommendation allowed. Mark missing evidence in red, draft evidence in amber, reviewed evidence in green. White background, technical audit table. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S12 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 2：Pareto scorecard decision diagram

Prompt: Generate a decision flow titled “S12 Pareto Scorecard Gate”. Include Drive-cycle Efficiency, Peak Performance, Cost, Maturity Evidence, Safety Gate, Manufacturability, Sensitivity Analysis, Candidate-for-review Output. Use red stop gate, yellow research-only gate, green candidate-for-review gate, English labels. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S12 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 3：BOM cost-risk Pareto input

Prompt: Generate a BOM cost-risk table titled “S12 Pareto Cost and Supply Risk Inputs”. Rows: PM mass delta, electrical steel grade delta, inverter component delta, excitation hardware delta, switching hardware delta, multiphase hardware delta, diagnostic safety delta. Columns: cost impact, supply risk, missing evidence penalty, gate status. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S12 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 4：Traceability flow

Prompt: Generate a traceability flowchart titled “S12 No Evidence, No Recommendation”. Flow: EXP-010 drive cycle -> candidate evidence index -> BOM cost risk -> CAD package penalty -> S11 safety gate -> sensitivity analysis -> recommendation class. White background, technical report style, explicit callout “proxy ranking is not engineering validation”. Callout: engineering_validated = false; evidence_gap.
Anchor: S12 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

