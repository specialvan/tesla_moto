# V2-S02-PROMPT-r02-simulation_anchor_pack

用途：S02 r02-sim 首批改图 prompt pack，可被 `gpt_image2.generate --prompt-pack` 直接消费。  
范围：T01 / T03 / T07 / T08。  
边界：concept diagram only；not production drawing；not simulation source；engineering_validated=false。

## 通用负面约束

- Do not claim production ready, FEA proven, HIL passed, bench verified, manufacturing release, or engineering validated.
- Do not hide soft checks inside green success marks.
- Do not imply the image is EDA, Gerber, STEP, ODB++, FEA mesh, or a simulation source file.
- Do not show a green pass badge for the 30 A document target while current binding still uses 60 A.
- Do not omit engineering_validated=false.

## 图 1：S02 r02-sim driver block

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim engineering review image. Edit the S02 T01 driver block reference into a flat technical schematic with a clearly separated lower-right "SIM ANCHOR" panel. Title text: "S02 r02-sim MTPA/FW/MTPV driver block". Main diagram: preserve the r01/r00 driver-block composition, but add a slim simulation data path lane: "sim_binding kwargs -> sim.run_control_lut_generator.run -> control_lut output -> feasibility_map / mode_transitions / validation". Add SIM ANCHOR panel values exactly: scheme_id = mtpa_fw_mtpv_control; simulation_status = numeric_proxy_passed; model_maturity = parameterized_linear_model; sim_binding = engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_02_lut_acceptance.py + tests/test_scheme_p0_lut_acceptance.py; engineering_validated = false; next_simulation_step = replace estimate motor parameters with FEA/bench and tighten jump gate. Tag "torque_axis [50,100,150,200] Nm" as [binding]. Tag "Rs/Ld/Lq/psi_f" as [estimate from motor_params]. Tag "DemagLimit" as [estimate]. Add amber callout near Mode Selector: "proxy pass only: linear dq estimate, no FEA/bench". Add amber "GATE MISMATCH" callout: "document target id/iq jump <=30 A; current binding gate <=60 A". Style: dark navy technical vector, pale blue nodes, gold borders, amber warning badges, crisp readable text. Concept boundary label top-left: "CONCEPT DIAGRAM · SIMULATION ANCHOR ONLY · NOT A SIMULATION SOURCE".

## 图 3：S02 r02-sim state machine

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim engineering review image. Edit the S02 T03 state-machine reference into a clean 2x3 finite state machine. Title text: "S02 r02-sim mode transition state machine". Preserve exactly six states: MTPA idle; MTPA active; Field Weakening (V_margin < 5 V); MTPV (boundary reached); Derate (thermal / demag); LUT CRC fault fallback. Preserve exactly seven edges and ensure "mode reset" points to "MTPA idle", not Derate. Add edge tags: "speed > base" = [mode_transition]; "MTPV boundary reached" = [mode_transition]; "thermal / demag risk" = [soft check]; "LUT CRC fail" = [DVP S02-DV-002 planned HIL]. Add lower-right SIM ANCHOR panel: scheme_id = mtpa_fw_mtpv_control; simulation_status = numeric_proxy_passed; model_maturity = parameterized_linear_model; sim_binding = engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_p0_lut_acceptance.py; engineering_validated = false; next_simulation_step = tighten id/iq jump threshold and define DTC enums. Add bottom amber note: "Current pytest binding uses <=60 A jump threshold; document target remains <=30 A". Do not show 30 A as green passed.

## 图 7：S02 r02-sim verification tree

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim verification tree. Create or edit a left-to-right verification tree with three clearly separated lanes: STRONG CHECKS, SOFT CHECKS, PLANNED / DOCUMENT TARGET. Title text: "S02 r02-sim verification gates". SIM ANCHOR panel values: scheme_id = mtpa_fw_mtpv_control; simulation_status = numeric_proxy_passed; model_maturity = parameterized_linear_model; sim_binding = engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_02_lut_acceptance.py + tests/test_scheme_p0_lut_acceptance.py; engineering_validated = false. STRONG CHECKS lane: generator_version regex; model_source.model_type enum; speed_axis count >= 60; torque_axis count >= 4; feasible_points >= 60 (r02 binding gate); torque_discontinuity <= 5.0 Nm; demag_limit present. SOFT CHECKS lane: search_not_converged <= 100; demagnetization_risk <= 200; voltage_exceeded_ratio <= 0.95; id_jump <= 60 A current binding; iq_jump <= 60 A current binding. PLANNED / DOCUMENT TARGET lane: id_jump <= 30 A; iq_jump <= 30 A; DTC S02-DTC-LUT-CRC-FAIL; DTC S02-DTC-LUT-VER-MISMATCH. Use gold for strong, amber dashed for soft, grey/amber for planned. No green pass for 30 A.

## 图 8：S02 r02-sim protocol link

Prompt: Use case: infographic-diagram. Asset type: V2 r02-sim protocol/telemetry link. Edit the S02 T08 protocol reference into a vertical protocol chain. Title text: "S02 r02-sim protocol and telemetry link". Keep blocks: VCU CAN-FD; MCU command parser; Mode Selector (MTPA/FW/MTPV); FOC id/iq controller; SVPWM; 3-phase inverter; External NVM; UDS/XCP diagnostics; Calibration Tool. Add right-side diagnostic telemetry branch from MCU to Diagnostics with labels: lut_crc_status, lut_version, mode_state, id_jump_a, iq_jump_a, torque_discontinuity_nm, infeasible_reason. Mark these telemetry labels as "pytest observable" badges except DTC enums, which must be tagged "planned HIL". Add SIM ANCHOR panel: scheme_id = mtpa_fw_mtpv_control; simulation_status = numeric_proxy_passed; model_maturity = parameterized_linear_model; sim_binding = engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json; pytest_gate = tests/test_scheme_02_lut_acceptance.py; engineering_validated = false; next_simulation_step = replace estimate parameters with FEA/bench and tighten jump gate. Add amber GATE MISMATCH badge: document target <=30 A, current binding <=60 A.

