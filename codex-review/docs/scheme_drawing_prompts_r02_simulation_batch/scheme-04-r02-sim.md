# S04 r02-sim 提示词增量 · Nonlinear Flux LUT

修订日期：2026-05-20  
基底提示词：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-04-r01.md`  
仿真绑定：`engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json`  
pytest：`tests/test_scheme_p0_lut_acceptance.py`

## 1. 当前仿真口径

S04 当前必须按 `binding_smoke_passed` / `synthetic_fixture` 展示。`models/flux_lut_sample.json` 是 synthetic 3x3 fixture，不是 FEA-derived flux map。任何图面都不得暗示 S04 已经具备真实 nonlinear flux LUT 工程验证。

## 2. 追加到所有 S04 r02-sim prompt 的固定块

```text
SIM ANCHOR panel values:
scheme_id = nonlinear_flux_lut
simulation_status = binding_smoke_passed
model_maturity = synthetic_fixture
sim_binding = engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json
pytest_gate = tests/test_scheme_p0_lut_acceptance.py
engineering_validated = false
next_simulation_step = replace synthetic 3x3 LUT with FEA-derived 30x30xT LUT

Add red badge:
"SYNTHETIC FIXTURE ONLY · flux_lut_sample.json · not FEA-derived".
Do NOT use green validation badges.
Do NOT show "FEA validated" or "physics model validated".
```

## 3. T01 driver block 增量

在 r01 T01 prompt 末尾追加：

```text
Add a visible "current LUT source" label on the Nonlinear Flux LUT Observer:
source = models/flux_lut_sample.json [synthetic_fixture]
grid = 3x3 smoke fixture [not FEA]
target = FEA 30x30xT [planned]
Add simulation data path:
sim_binding kwargs -> sim.run_control_lut_generator.run(model_type=nonlinear_flux_lut)
-> model_source.flux_lut_ref -> feasibility_map.
```

验收：

- `synthetic_fixture` 和 `not FEA` 必须可读。
- `target = FEA 30x30xT` 必须可读。

## 4. T04 PCB concept 增量

在 r01 T04 prompt 末尾追加：

```text
Replace any "production input" language with "simulation variable map".
Each signal must map to a runner/LUT variable:
ia/ib/ic -> id, iq reconstruction [planned observer input]
resolver/encoder -> omega_e [input axis]
temperature sensors -> T slice [input axis]
Vdc sense -> voltage constraint [control search]
NVM LUT body -> flux_lut_ref [synthetic_fixture]
Add red warning callout:
"bounds check currently smoke-level; feasible_points_min = 1".
```

验收：

- `feasible_points_min = 1` 必须出现，并标为 smoke-level。
- PCB 图不得看起来像 layout。

## 5. T05 CAD / FEA concept 增量

在 r01 T05 prompt 末尾追加：

```text
Add a missing-evidence checklist on the right:
[ ] STEP / Motor-CAD geometry source
[ ] Maxwell / Motor-CAD mesh
[ ] material B-H curves
[ ] boundary conditions
[ ] FEA lambda_d/lambda_q export
[ ] temperature slices >= 5
At the bottom, add:
"Current image is FEA source boundary concept only; it is not a mesh or solver input."
```

验收：

- 六项 missing-evidence checklist 必须出现。
- 图面仍是 flat line concept，不是写实 cross-section。

## 6. T07 verification tree 增量

在 r01 T07 prompt 末尾追加：

```text
Split verification leaves into four lanes:
CURRENT SMOKE GATE:
- model_type == nonlinear_flux_lut
- flux_lut_ref present
- speed_axis count >= 60
- torque_axis count >= 2
- feasible_points >= 1
SOFT WARN:
- search_not_converged <= 200
- out_of_flux_lut_bounds <= 200
REQUIRED r03 PHYSICS GATE:
- FEA-derived LUT 30x30xT
- interpolation residual <= 12 %
- bounds fallback rate threshold defined
- temperature slices >= 5
- CAD/FEA/LUT version match
NOT YET EVIDENCE:
- bench correlation
- FEA mesh quality
- material curve audit
```

验收：

- `feasible_points >= 1` 必须在 CURRENT SMOKE GATE，而不是 physics gate。
- `FEA-derived LUT 30x30xT` 必须在 REQUIRED r03 PHYSICS GATE。

## 7. T08 protocol link 增量

在 r01 T08 prompt 末尾追加：

```text
Add telemetry labels:
flux_lut_ref, lut_crc_status, bounds_status, out_of_bounds_count,
fallback_active, residual_percent, temperature_slice_id.
Tag residual_percent and temperature_slice_id as r03 planned if not present in current binding.
```

验收：

- telemetry labels must distinguish current observable vs r03 planned.

