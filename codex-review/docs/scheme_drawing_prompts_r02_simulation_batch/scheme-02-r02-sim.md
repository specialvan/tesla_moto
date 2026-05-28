# S02 r02-sim 提示词增量 · MTPA / FW / MTPV

修订日期：2026-05-20  
基底提示词：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-02-r01.md`  
仿真绑定：`engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json`  
pytest：`tests/test_scheme_02_lut_acceptance.py`、`tests/test_scheme_p0_lut_acceptance.py`

## 1. 当前仿真口径

S02 目前是 `numeric_proxy_passed` / `parameterized_linear_model`。它可以展示 runner 可执行、LUT 绑定存在、DVP 映射存在，但不能展示 HIL、bench 或生产 LUT 发布完成。

特别注意：文档目标写 `id_jump_a <= 30 A`、`iq_jump_a <= 30 A`，但当前 `sim_binding-r02.json` 机器门禁仍是 `<= 60 A`。r02-sim 图必须把这个差异暴露出来。

## 2. 追加到所有 S02 r02-sim prompt 的固定块

```text
SIM ANCHOR panel values:
scheme_id = mtpa_fw_mtpv_control
simulation_status = numeric_proxy_passed
model_maturity = parameterized_linear_model
sim_binding = engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json
pytest_gate = tests/test_scheme_02_lut_acceptance.py + tests/test_scheme_p0_lut_acceptance.py
engineering_validated = false
next_simulation_step = replace estimate motor parameters with FEA/bench and tighten jump gate

Show an amber "GATE MISMATCH" callout:
document target: id_jump <= 30 A, iq_jump <= 30 A
current binding gate: id_jump <= 60 A, iq_jump <= 60 A
This mismatch MUST be visible on the diagram until JSON and markdown are reconciled.
Do NOT show a green pass badge for the 30 A target.
```

## 3. T01 driver block 增量

在 r01 T01 prompt 末尾追加：

```text
Add a slim "simulation data path" lane under the control row:
sim_binding kwargs -> sim.run_control_lut_generator.run -> control_lut output ->
feasibility_map / mode_transitions / validation.
Tag torque_axis [50,100,150,200] Nm as [binding].
Tag Rs/Ld/Lq/psi_f as [estimate from motor_params].
Tag DemagLimit as [estimate].
Place amber callout near Mode Selector:
"proxy pass only: linear dq estimate, no FEA/bench".
```

验收：

- 图里必须出现 `sim.run_control_lut_generator.run`。
- `torque_axis [50,100,150,200] Nm` 必须标 `[binding]`。
- `Rs/Ld/Lq/psi_f` 或 `motor_params estimate` 必须出现。

## 4. T03 state machine 增量

在 r01 T03 prompt 末尾追加：

```text
Add small tags on edges:
"speed > base" edge tag: [mode_transition]
"MTPV boundary reached" edge tag: [mode_transition]
"thermal / demag risk" edge tag: [soft check]
"LUT CRC fail" edge tag: [DVP S02-DV-002 planned HIL]
Add a bottom note:
"Current pytest gate uses 60 A jump threshold; document target remains 30 A."
```

验收：

- `mode reset` 仍必须回到 `MTPA idle`。
- 30 A / 60 A 差异必须出现在图中。
- `LUT CRC fail` 不能被画成已通过 HIL。

## 5. T07 verification tree 增量

在 r01 T07 prompt 末尾追加：

```text
Split leaves into three visual lanes:
STRONG CHECKS:
- generator_version regex
- model_source.model_type enum
- speed_axis count >= 60
- torque_axis count >= 4
- feasible_points >= 60 (r02 binding gate)
- torque_discontinuity <= 5.0 Nm
- demag_limit present
SOFT CHECKS:
- search_not_converged <= 100
- demagnetization_risk <= 200
- voltage_exceeded_ratio <= 0.95
- id_jump <= 60 A (current binding)
- iq_jump <= 60 A (current binding)
PLANNED / DOCUMENT TARGET:
- id_jump <= 30 A
- iq_jump <= 30 A
- DTC enums S02-DTC-LUT-CRC-FAIL and S02-DTC-LUT-VER-MISMATCH
```

验收：

- strong / soft / planned 三栏分开。
- 不允许把 30 A 目标放进 strong check，除非 JSON 已改。

## 6. T08 protocol link 增量

在 r01 T08 prompt 末尾追加：

```text
Add right-side diagnostic telemetry branch:
MCU -> Diagnostics:
"lut_crc_status", "lut_version", "mode_state", "id_jump_a", "iq_jump_a",
"torque_discontinuity_nm", "infeasible_reason".
Map each telemetry label to "pytest observable" badge except DTC enums, which
must be tagged "planned HIL".
```

验收：

- 至少 7 个 telemetry label 出现。
- DTC 枚举必须标 planned HIL，不标 passed。

