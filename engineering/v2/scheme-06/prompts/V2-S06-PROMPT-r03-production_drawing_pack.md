# V2-S06 r03 生产参数化生图提示词包

目标：把 S06 PMaSynRM / 高凸极低 PM 路线升级为可审查拓扑、控制图、BOM 风险和证据链图。

## SIM ANCHOR

```text
scheme_id: pmasynrm_high_saliency_low_pm
simulation_status: numeric_proxy_passed
model_maturity: proxy_model
sim_binding: engineering/v2/scheme-06/parameters/V2-S06-PARAM-sim_binding-r02.json
pytest_gate: tests/test_scheme_experiment_acceptance.py
engineering_validated: false
next_simulation_step: Add PM fraction and torque ripple screening fields instead of only psi/Ld/Lq scaling.
```


## 通用负面约束

- 不要把低 PM 写成自动低成本，必须显示 demag、torque ripple、thermal、stress 风险。
- 不要只画转子外观，必须标注 low PM pocket、flux barrier、hairpin slot、cooling path。
- 不要输出工程推荐，除非图中保留 evidence/maturity gate。
- 所有图必须可见标注 `engineering_validated = false`、`proxy / estimate only`、`evidence_gap`。
- CAD/FEA 元素必须标为 FEA evidence target / geometry placeholder，不得画成已完成验证。
- PNG/prompt 仅为 concept illustration，不是 production drawing 或 validation evidence。

## 图 1：Low-PM PMaSynRM topology CAD

Prompt: Generate a technical CAD/FEA drawing titled “S06 High-saliency Low-PM PMaSynRM Topology”. Include rotor low-PM magnet pockets, multi-layer flux barriers, bridge/rib stress map, stator hairpin slots, cooling path, demag hotspot overlay, saliency ratio, PM fraction, stress safety factor, demag margin. White background, four-view engineering layout, English labels. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S06 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 2：Control map

Prompt: Generate a controller diagram titled “S06 High-saliency Low-PM Control Map”. Include FEA evidence target flux LUT, MTPA, MTPV/high-speed, Demag Guard, Thermal Derating, Drive-cycle Scorecard, Candidate-for-review Gate Decision. Use red stop conditions and blue control data flow, white background. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S06 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 3：BOM cost-risk matrix

Prompt: Generate a BOM and risk matrix titled “S06 Low-PM Topology BOM Risk”. Rows: low-PM magnet, electrical steel, hairpin winding, rotor retention, thermal sensors. Columns: cost impact, supply risk, demag curve, loss curve, DFM evidence, gate status. Engineering report style. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S06 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

## 图 4：Evidence traceability

Prompt: Generate a traceability diagram titled “S06 Evidence Chain: Saliency Trend to Candidate-for-Review”. Flow: EXP-003 saliency trend -> low-PM CAD topology -> FEA evidence target LUT -> MTPA/MTPV control map -> demag/thermal guard -> BOM cost risk -> DVP gate plan. Include “research rank until CAD/FEA/DVP evidence exists” callout. Callout: proxy only; engineering_validated = false; evidence_gap.
Anchor: S06 | model_maturity=proxy_model | simulation_status=numeric_proxy_passed | engineering_validated=false | evidence_gap | pytest_gate=tests/test_scheme_experiment_acceptance.py

