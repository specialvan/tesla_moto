"""r03 acceptance harness for V2 P0 schemes (S01, S02, S04, S11).

Loads each scheme's V2-S<id>-PARAM-sim_binding-r02.json, materialises kwargs (handling
DemagLimit dataclass and lut_path string), drives sim.run_control_lut_generator.run,
and asserts the strong checks while emitting warnings for soft checks.

Strong checks raise on failure; soft checks emit warnings. This file replaces the
S02-only test (tests/test_scheme_02_lut_acceptance.py) by parametrising over all P0
schemes. The original S02 test remains for backwards compatibility.

Not engineering-validated. r02 estimates must be replaced with FEA / bench data
before any production claim. r03 only proves binding ↔ simulation wiring works.
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

P0_SCHEMES = [
    ("S01", "scheme-01", "V2-S01-PARAM-sim_binding-r02.json"),
    ("S02", "scheme-02", "V2-S02-PARAM-sim_binding-r02.json"),
    ("S04", "scheme-04", "V2-S04-PARAM-sim_binding-r02.json"),
    ("S11", "scheme-11", "V2-S11-PARAM-sim_binding-r02.json"),
]


def _binding_path(scheme_dir: str, file_name: str) -> Path:
    return ROOT / "engineering" / "v2" / scheme_dir / "parameters" / file_name


def _materialize_demag_limit(spec: dict[str, Any]) -> DemagLimit:
    points = [tuple(pair) for pair in spec["points_c_to_id_min_a"]]
    return DemagLimit(points_c_to_id_min_a=points)


def _resolve_kwargs(binding: dict[str, Any]) -> dict[str, Any]:
    kwargs = dict(binding["kwargs"])
    demag_spec = kwargs.get("demag_limit")
    if isinstance(demag_spec, dict) and demag_spec.get("type") == "DemagLimit":
        kwargs["demag_limit"] = _materialize_demag_limit(demag_spec)
    lut_path = kwargs.get("lut_path")
    if isinstance(lut_path, str):
        kwargs["lut_path"] = Path(lut_path)
    return kwargs


def _voltage_exceeded_ratio(output: dict[str, Any]) -> float:
    fmap = output["feasibility_map"]
    total = max(int(fmap.get("total_points", 0)), 1)
    return int(fmap["infeasible_reasons"]["voltage_exceeded"]) / total


def _all_transition_jumps(output: dict[str, Any], field: str) -> float:
    transitions = output["mode_transitions"].get("mtpa_to_fw_boundary", [])
    transitions += output["mode_transitions"].get("fw_to_mtpv_boundary", [])
    return max((abs(t.get(field, 0.0)) for t in transitions), default=0.0)


def _eval_check(key: str, expected: Any, output: dict[str, Any]) -> tuple[bool, str]:
    if key == "metadata.generator_version.regex":
        value = output["metadata"]["generator_version"]
        return bool(re.match(expected, value)), f"generator_version={value!r}"
    if key == "model_source.model_type.enum":
        value = output["model_source"]["model_type"]
        return value in expected, f"model_type={value!r} enum={expected}"
    if key == "model_source.flux_lut_ref_present":
        value = output["model_source"].get("flux_lut_ref")
        ok = (value is not None) == bool(expected)
        return ok, f"flux_lut_ref present={value is not None}"
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
    if key == "feasibility_map.infeasible_reasons.out_of_flux_lut_bounds_max":
        value = output["feasibility_map"]["infeasible_reasons"][
            "out_of_flux_lut_bounds"
        ]
        return value <= expected, f"out_of_flux_lut_bounds={value} <= {expected}"
    if key == "feasibility_map.infeasible_reasons.voltage_exceeded_ratio_max":
        ratio = _voltage_exceeded_ratio(output)
        return ratio <= expected, f"voltage_exceeded_ratio={ratio:.3f} <= {expected}"
    if key == "validation.torque_discontinuity_at_transitions_nm_max":
        value = output["validation"]["torque_discontinuity_at_transitions_nm"]
        return value <= expected, f"torque_discontinuity={value} <= {expected}"
    if key == "mode_transitions.id_jump_a_max":
        worst = _all_transition_jumps(output, "id_jump_a")
        return worst <= expected, f"max id_jump={worst} <= {expected}"
    if key == "mode_transitions.iq_jump_a_max":
        worst = _all_transition_jumps(output, "iq_jump_a")
        return worst <= expected, f"max iq_jump={worst} <= {expected}"
    if key == "metadata.demag_limit_present":
        value = output["metadata"].get("demag_limit")
        ok = (value is not None) == bool(expected)
        return ok, f"metadata.demag_limit present={value is not None}"
    if key == "operating_limits.temperature_c.equals":
        value = output["operating_limits"]["temperature_c"]
        return value == expected, f"operating_limits.temperature_c={value} == {expected}"
    raise KeyError(f"unhandled expect key: {key}")


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", P0_SCHEMES)
def test_scheme_p0_sim_binding_drives_run(
    tmp_path: Path,
    scheme_id: str,
    scheme_dir: str,
    binding_file: str,
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    kwargs = _resolve_kwargs(binding)
    kwargs["output_path"] = tmp_path / f"control_lut_{scheme_id.lower()}.json"

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
            strong_failures.append(f"[{scheme_id}] STRONG fail: {key} -> {message}")
        elif key in soft_keys:
            soft_warnings.append(f"[{scheme_id}] SOFT warn: {key} -> {message}")
        else:
            strong_failures.append(
                f"[{scheme_id}] UNCLASSIFIED fail: {key} -> {message}"
            )

    for warning_message in soft_warnings:
        warnings.warn(warning_message, stacklevel=1)

    assert not strong_failures, (
        f"{scheme_id} r02 sim binding produced strong-check failures:\n  - "
        + "\n  - ".join(strong_failures)
    )


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", P0_SCHEMES)
def test_scheme_p0_engineering_validated_is_false(
    scheme_id: str, scheme_dir: str, binding_file: str
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    assert binding["engineering_validated"] is False, (
        f"{scheme_id} r02 sim binding must keep engineering_validated=false"
    )


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", P0_SCHEMES)
def test_scheme_p0_dvp_mapping_present(
    scheme_id: str, scheme_dir: str, binding_file: str
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    mapping = binding["dvp_mapping"]
    assert mapping, f"{scheme_id} dvp_mapping must not be empty"
    for dvp_id in mapping:
        assert re.match(rf"^{scheme_id}-DV-\d{{3}}$", dvp_id), (
            f"{scheme_id} dvp id {dvp_id!r} does not match S<id>-DV-NNN"
        )
