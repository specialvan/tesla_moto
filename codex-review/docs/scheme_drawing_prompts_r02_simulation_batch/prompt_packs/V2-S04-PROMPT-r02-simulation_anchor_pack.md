# V2-S04-PROMPT-r02-simulation_anchor_pack

用途：S04 r02-sim 首批改图 prompt pack，可被 `gpt_image2.generate --prompt-pack` 直接消费。  
范围：T01 / T04 / T05 / T07。  
边界：concept diagram only；not production drawing；not FEA-derived LUT；engineering_validated=false。

## 通用负面约束

- Do not claim FEA-derived LUT, physics_model_validated, production nonlinear flux map, HIL passed, bench verified, manufacturing release, or engineering validated.
- Do not show green validation badges.
- Do not imply PCB/CAD diagrams are layout, EDA, Gerber, STEP, ODB++, FEA mesh, or solver input.
- Do not hide feasible_points_min=1 as a real validation threshold.
- Do not omit synthetic_fixture or engineering_validated=false.

## 图 1：S04 r02-sim driver block

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim engineering review image. Edit the S04 T01 driver block reference into a flat technical schematic with a red synthetic fixture warning. Title text: "S04 r02-sim nonlinear flux LUT driver block". Preserve the nonlinear flux LUT observer chain, but add a visible current LUT source label: "source = models/flux_lut_sample.json [synthetic_fixture]"; "grid = 3x3 smoke fixture [not FEA]"; "target = FEA 30x30xT [planned]". Add simulation data path: "sim_binding kwargs -> sim.run_control_lut_generator.run(model_type=nonlinear_flux_lut) -> model_source.flux_lut_ref -> feasibility_map". Add SIM ANCHOR panel: scheme_id = nonlinear_flux_lut; simulation_status = binding_smoke_passed; model_maturity = synthetic_fixture; sim_binding = engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_p0_lut_acceptance.py; engineering_validated = false; next_simulation_step = replace synthetic 3x3 LUT with FEA-derived 30x30xT LUT. Add red badge: "SYNTHETIC FIXTURE ONLY · not FEA-derived". Dark navy technical vector style, pale blue nodes, gold lines, red warning badge.

## 图 4：S04 r02-sim PCB variable map

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim PCB concept variable map. Edit the S04 T04 PCB reference so it reads as a simulation variable map, not layout. Title text: "S04 r02-sim PCB variable map (concept only)". Five groups: Observer Inputs; Bounds Check; Fallback Diagnostic; Error Budget Telemetry; MCU NVM. Map each signal to runner/LUT variables: ia/ib/ic -> id, iq reconstruction [planned observer input]; resolver/encoder -> omega_e [input axis]; temperature sensors -> T slice [input axis]; Vdc sense -> voltage constraint [control search]; NVM LUT body -> flux_lut_ref [synthetic_fixture]. Add red warning callout: "bounds check currently smoke-level; feasible_points_min = 1". Add SIM ANCHOR panel: scheme_id = nonlinear_flux_lut; simulation_status = binding_smoke_passed; model_maturity = synthetic_fixture; sim_binding = engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_p0_lut_acceptance.py; engineering_validated = false. Top-left boundary label: "CONCEPT DIAGRAM · SIMULATION ANCHOR ONLY · NOT PCB LAYOUT".

## 图 5：S04 r02-sim FEA boundary

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim CAD/FEA concept boundary. Edit the S04 T05 reference into a flat isometric line illustration only. Title text: "S04 r02-sim FEA source boundary (concept only)". Do not draw a photorealistic motor or real material grade. Show a simple coordinate frame, dq origin at rotor center, generic material boxes, and a missing-evidence checklist on the right: [ ] STEP / Motor-CAD geometry source; [ ] Maxwell / Motor-CAD mesh; [ ] material B-H curves; [ ] boundary conditions; [ ] FEA lambda_d/lambda_q export; [ ] temperature slices >= 5. Add bottom note: "Current image is FEA source boundary concept only; it is not a mesh or solver input." Add SIM ANCHOR panel: scheme_id = nonlinear_flux_lut; simulation_status = binding_smoke_passed; model_maturity = synthetic_fixture; sim_binding = engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_p0_lut_acceptance.py; engineering_validated = false; next_simulation_step = FEA 30x30xT LUT. Use red synthetic_fixture badge, no green validation.

## 图 7：S04 r02-sim verification tree

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim verification tree. Create or edit a left-to-right verification tree with four lanes: CURRENT SMOKE GATE, SOFT WARN, REQUIRED r03 PHYSICS GATE, NOT YET EVIDENCE. Title text: "S04 r02-sim nonlinear flux LUT verification gates". SIM ANCHOR panel values: scheme_id = nonlinear_flux_lut; simulation_status = binding_smoke_passed; model_maturity = synthetic_fixture; sim_binding = engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_p0_lut_acceptance.py; engineering_validated = false. CURRENT SMOKE GATE lane: model_type == nonlinear_flux_lut; flux_lut_ref present; speed_axis count >= 60; torque_axis count >= 2; feasible_points >= 1. SOFT WARN lane: search_not_converged <= 200; out_of_flux_lut_bounds <= 200. REQUIRED r03 PHYSICS GATE lane: FEA-derived LUT 30x30xT; interpolation residual <= 12%; bounds fallback rate threshold defined; temperature slices >= 5; CAD/FEA/LUT version match. NOT YET EVIDENCE lane: bench correlation; FEA mesh quality; material curve audit. Use red synthetic_fixture badge; feasible_points >= 1 must be visibly labeled as smoke gate, not validation.

