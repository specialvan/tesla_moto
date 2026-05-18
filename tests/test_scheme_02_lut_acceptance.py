"""r03 acceptance test for V2 scheme S02 mtpa_fw_mtpv_control.

Loads V2-S02-PARAM-sim_binding-r02.json, drives sim.run_control_lut_generator.run
with the bound kwargs, and asserts the strong / soft checks in expect{}.

Strong checks raise on failure; soft checks emit warnings via pytest.warns or
emit_warning helper. This is the r03 minimal harness that proves the r02 production
parameter sheet can drive a simulation acceptance test.

Not engineering-validated. r02 estimates (Rs, Ld, Lq, psi_f, DemagLimit) must be
replaced with FEA / bench data before any production claim.
"""

from __future__ import annotations

import json
import re
import warnings
from pathlib import Path
from typing import Any

import pytest

from sim.run_control_lut_generator import run
from sim.safety_limits import DemagLimit

ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = (
    ROOT
    / "engineering"
    / "v2"
    / "scheme-02"
    / "parameters"
    / "V2-S02-PARAM-sim_binding-r02.json"
)


def _materialize_demag_limit(spec: dict[str, Any]) -> DemagLimit:
    points = [tuple(pair) for pair in spec["points_c_to_id_min_a"]]
    return DemagLimit(points_c_to_id_min_a=points)


def _load_binding() -> dict[str, Any]:
    return json.loads(BINDING_PATH.read_text(encoding="utf-8"))


def _resolve_kwargs(binding: dict[str, Any]) -> dict[str, Any]:
    kwargs = dict(binding["kwargs"])
    demag_spec = kwargs.get("demag_limit")
    if isinstance(demag_spec, dict) and demag_spec.get("type") == "DemagLimit":
        kwargs["demag_limit"] = _materialize_demag_limit(demag_spec)
    return kwargs


def _walk(output: dict[str, Any], dotted: str) -> Any:
    cursor: Any = output
    for part in dotted.split("."):
        cursor = cursor[part]
    return cursor


def _voltage_exceeded_ratio(output: dict[str, Any]) -> float:
    fmap = output["feasibility_map"]
    total = max(int(fmap.get("total_points", 0)), 1)
    return int(fmap["infeasible_reasons"]["voltage_exceeded"]) / total


def _eval_check(key: str, expected: Any, output: dict[str, Any]) -> tuple[bool, str]:
    """Return (passed, message) for one expect key."""
    if key == "metadata.generator_version.regex":
        value = output["metadata"]["generator_version"]
        ok = bool(re.match(expected, value))
        return ok, f"generator_version={value!r} regex={expected}"
    if key == "model_source.model_type.enum":
        value = output["model_source"]["model_type"]
        ok = value in expected
        return ok, f"model_type={value!r} enum={expected}"
    if key == "grid_definition.speed_axis_rpm.count_min":
        value = len(output["grid_definition"]["speed_axis_rpm"])
        return value >= expected, f"speed_axis count={value} >= {expected}"
    if key == "grid_definition.torque_axis_nm.count_min":
        value = len(output["grid_definition"]["torque_axis_nm"])
        return value >= expected, f"torque_axis count={value} >= {expected}"
    if key == "feasibility_map.feasible_points_min":
        value = output["feasibility_map"]["feasible_points"]
        return value >= expected, f"feasible_points={value} >= {expected}"
    if key == "feasibility_map.infeasible_reasons.search_not_converged_max":
        value = output["feasibility_map"]["infeasible_reasons"]["search_not_converged"]
        return value <= expected, f"search_not_converged={value} <= {expected}"
    if key == "feasibility_map.infeasible_reasons.demagnetization_risk_max":
        value = output["feasibility_map"]["infeasible_reasons"]["demagnetization_risk"]
        return value <= expected, f"demagnetization_risk={value} <= {expected}"
    if key == "feasibility_map.infeasible_reasons.voltage_exceeded_ratio_max":
        ratio = _voltage_exceeded_ratio(output)
        return ratio <= expected, f"voltage_exceeded_ratio={ratio:.3f} <= {expected}"
    if key == "validation.torque_discontinuity_at_transitions_nm_max":
        value = output["validation"]["torque_discontinuity_at_transitions_nm"]
        return value <= expected, f"torque_discontinuity={value} <= {expected}"
    if key == "mode_transitions.id_jump_a_max":
        transitions = output["mode_transitions"].get("mtpa_to_fw_boundary", [])
        transitions += output["mode_transitions"].get("fw_to_mtpv_boundary", [])
        worst = max((abs(t.get("id_jump_a", 0.0)) for t in transitions), default=0.0)
        return worst <= expected, f"max id_jump={worst} <= {expected}"
    if key == "mode_transitions.iq_jump_a_max":
        transitions = output["mode_transitions"].get("mtpa_to_fw_boundary", [])
        transitions += output["mode_transitions"].get("fw_to_mtpv_boundary", [])
        worst = max((abs(t.get("iq_jump_a", 0.0)) for t in transitions), default=0.0)
        return worst <= expected, f"max iq_jump={worst} <= {expected}"
    if key == "metadata.demag_limit_present":
        value = output["metadata"].get("demag_limit")
        ok = value is not None and bool(expected)
        return ok, f"metadata.demag_limit present={value is not None}"
    raise KeyError(f"unhandled expect key: {key}")


@pytest.mark.integration
def test_scheme_02_r02_sim_binding_drives_run(tmp_path: Path) -> None:
    """r02 sim binding must produce a control LUT that satisfies strong checks."""
    binding = _load_binding()
    kwargs = _resolve_kwargs(binding)
    kwargs["output_path"] = tmp_path / "control_lut_r02_acceptance.json"

    output = run(**kwargs)

    expect = binding["expect"]
    strong_keys = set(binding["strong_checks"])
    soft_keys = set(binding["soft_checks"])

    strong_failures: list[str] = []
    soft_warnings: list[str] = []

    for key, expected_value in expect.items():
        passed, message = _eval_check(key, expected_value, output)
        if passed:
            continue
        if key in strong_keys:
            strong_failures.append(f"STRONG fail: {key} -> {message}")
        elif key in soft_keys:
            soft_warnings.append(f"SOFT warn: {key} -> {message}")
        else:
            strong_failures.append(f"UNCLASSIFIED fail: {key} -> {message}")

    for warning_message in soft_warnings:
        warnings.warn(warning_message, stacklevel=1)

    assert not strong_failures, (
        "S02 r02 sim binding produced strong-check failures:\n  - "
        + "\n  - ".join(strong_failures)
    )


def test_scheme_02_jump_thresholds_are_marked_as_r02_proxy_gates() -> None:
    binding = _load_binding()
    threshold_maturity = binding["threshold_maturity"]

    for key in ("mode_transitions.id_jump_a_max", "mode_transitions.iq_jump_a_max"):
        assert binding["expect"][key] == 60.0
        assert key in binding["soft_checks"]
        assert key not in binding["strong_checks"]
        maturity = threshold_maturity[key]
        assert maturity["r02_proxy_soft_gate_a"] == 60.0
        assert maturity["r03_production_target_a"] == 30.0
        assert maturity["engineering_validated"] is False


@pytest.mark.integration
def test_scheme_02_binding_dvp_mapping_is_documented() -> None:
    """Every S02-DV-xxx ID in the DVP draft must appear in binding dvp_mapping."""
    binding = _load_binding()
    mapping = binding["dvp_mapping"]
    expected_ids = {
        "S02-DV-001",
        "S02-DV-002",
        "S02-DV-003",
        "S02-DV-004",
        "S02-DV-005",
    }
    missing = expected_ids - set(mapping)
    assert not missing, f"binding dvp_mapping missing: {sorted(missing)}"


@pytest.mark.integration
def test_scheme_02_binding_engineering_validated_is_false() -> None:
    """r02 sheets must NOT flip engineering_validated to true."""
    binding = _load_binding()
    assert binding["engineering_validated"] is False, (
        "S02 r02 sim binding must keep engineering_validated=false; "
        "only after FEA + bench + HIL closure can this be flipped."
    )
