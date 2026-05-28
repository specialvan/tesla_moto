"""Tests for sim/run_control_lut_generator.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

import sim.run_control_lut_generator as control_lut_generator
from sim.search import Candidate
from sim.safety_limits import DemagLimit
from sim.run_control_lut_generator import (
    _candidate_infeasibility_reason,
    _check_mode_continuity,
    _detect_mode_transitions,
    _max_transition_torque_jump,
    run,
)


CONTROL_LUT_SCHEMA_PATH = Path("models/control_lut_schema.json")
FLUX_LUT_PATH = Path("models/flux_lut_sample.json")
FIXED_GENERATED_AT = "2026-05-28T00:00:00+00:00"
_GENERATED_LUT_CACHE: dict[str, dict[str, Any]] = {}


def _cache_key(kwargs: dict[str, Any]) -> str:
    def default(value: Any) -> Any:
        if isinstance(value, Path):
            return value.as_posix()
        if isinstance(value, DemagLimit):
            return {"points_c_to_id_min_a": value.points_c_to_id_min_a}
        raise TypeError(f"unhandled cache value {type(value).__name__}")

    return json.dumps(kwargs, sort_keys=True, separators=(",", ":"), default=default)


def generate_control_lut(
    tmp_path: Path, output_path: Path | None = None, **kwargs: Any
) -> dict[str, Any]:
    kwargs.setdefault("generated_at", FIXED_GENERATED_AT)
    output_path = output_path or tmp_path / "control_lut.json"
    cache_key = _cache_key({**kwargs, "output_path": output_path})
    if cache_key not in _GENERATED_LUT_CACHE:
        _GENERATED_LUT_CACHE[cache_key] = run(output_path=output_path, **kwargs)
    return _GENERATED_LUT_CACHE[cache_key]


def test_generate_control_lut_caches_identical_successful_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _GENERATED_LUT_CACHE.clear()
    calls = 0

    def fake_run(**kwargs: Any) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return {"kwargs": kwargs}

    monkeypatch.setattr(sys.modules[__name__], "run", fake_run)

    first = generate_control_lut(tmp_path, torque_axis_nm=[50.0, 100.0])
    second = generate_control_lut(tmp_path, torque_axis_nm=[50.0, 100.0])

    assert first == second
    assert calls == 1
    _GENERATED_LUT_CACHE.clear()


def test_generate_control_lut_cache_key_includes_output_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _GENERATED_LUT_CACHE.clear()
    calls: list[Path] = []

    def fake_run(**kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs["output_path"])
        return {"output_path": kwargs["output_path"].as_posix()}

    monkeypatch.setattr(sys.modules[__name__], "run", fake_run)

    first = generate_control_lut(tmp_path, output_path=tmp_path / "first.json")
    second = generate_control_lut(tmp_path, output_path=tmp_path / "second.json")

    assert first != second
    assert calls == [tmp_path / "first.json", tmp_path / "second.json"]
    _GENERATED_LUT_CACHE.clear()


def assert_matches_control_lut_schema(control_lut: dict[str, Any]) -> None:
    schema = json.loads(CONTROL_LUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(control_lut), key=lambda error: error.path)
    assert errors == []


def test_control_lut_generator_writes_json_output(tmp_path: Path) -> None:
    output_path = tmp_path / "control_lut.json"

    result = run(output_path=output_path)

    assert output_path.exists()
    assert result["schema_version"] == "2026-05-14-v1"
    assert result["unit_convention"]["dq_transform"] == "amplitude_invariant"
    assert result["model_source"]["model_type"] == "linear_dq"
    assert result["pole_pairs"] == 4


def test_control_lut_requires_explicit_output_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(control_lut_generator, "ROOT", tmp_path)

    with pytest.raises(ValueError, match="output_path is required"):
        control_lut_generator.run()

    assert not (tmp_path / "models" / "control_lut.json").exists()


def test_control_lut_cli_requires_output_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(control_lut_generator, "ROOT", tmp_path)

    with pytest.raises(SystemExit):
        control_lut_generator.main([])

    assert not (tmp_path / "models" / "control_lut.json").exists()


def test_control_lut_cli_writes_explicit_output_path(tmp_path: Path) -> None:
    output_path = tmp_path / "cli_control_lut.json"

    result = control_lut_generator.main(
        ["--output-path", str(output_path), "--generated-at", FIXED_GENERATED_AT]
    )

    assert output_path.exists()
    assert result["metadata"]["generated_at"] == FIXED_GENERATED_AT


def test_control_lut_schema_allows_documented_nullable_enums() -> None:
    schema = json.loads(CONTROL_LUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    control_point_schema = schema["$defs"]["ControlPoint"]["properties"]

    assert control_point_schema["control_mode"]["type"] == ["string", "null"]
    assert control_point_schema["infeasibility_reason"]["type"] == ["string", "null"]
    assert control_point_schema["search_method"]["type"] == ["string", "null"]
    assert control_point_schema["confidence"]["type"] == ["string", "null"]


def test_control_lut_default_output_matches_schema(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    assert_matches_control_lut_schema(result)


def test_control_lut_multi_torque_output_matches_schema(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path, torque_axis_nm=[25.0, 50.0, 120.0])

    assert_matches_control_lut_schema(result)


def test_control_lut_demag_output_matches_schema(tmp_path: Path) -> None:
    demag_limit = DemagLimit(points_c_to_id_min_a=[(25.0, -10.0), (140.0, -10.0)])

    result = generate_control_lut(tmp_path, demag_limit=demag_limit)

    assert_matches_control_lut_schema(result)


def test_control_lut_nonlinear_output_matches_schema(tmp_path: Path) -> None:
    result = generate_control_lut(
        tmp_path, model_type="nonlinear_flux_lut", lut_path=FLUX_LUT_PATH
    )

    assert_matches_control_lut_schema(result)


def test_control_lut_has_speed_torque_grid(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    speed_axis = result["grid_definition"]["speed_axis_rpm"]
    torque_axis = result["grid_definition"]["torque_axis_nm"]
    assert len(speed_axis) > 0
    assert torque_axis == [100.0]
    assert result["grid_definition"]["torque_step_nm"] == 0.0
    assert result["grid_definition"]["interpolation_method"] == "nearest"
    assert result["grid_definition"]["extrapolation_policy"] == "clamp"
    assert len(result["control_points"]) == len(speed_axis) * len(torque_axis)


def test_control_lut_accepts_explicit_torque_axis(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path, torque_axis_nm=[50.0, 100.0, 150.0])

    speed_axis = result["grid_definition"]["speed_axis_rpm"]
    torque_axis = result["grid_definition"]["torque_axis_nm"]
    assert torque_axis == [50.0, 100.0, 150.0]
    assert result["grid_definition"]["torque_step_nm"] == 50.0
    assert len(result["control_points"]) == len(speed_axis) * len(torque_axis)


def test_control_lut_covers_speed_torque_cartesian_grid(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path, torque_axis_nm=[50.0, 100.0])

    speed_axis = result["grid_definition"]["speed_axis_rpm"]
    torque_axis = result["grid_definition"]["torque_axis_nm"]
    expected_pairs = {
        (speed_rpm, torque_nm) for speed_rpm in speed_axis for torque_nm in torque_axis
    }
    actual_pairs = {
        (cp["speed_rpm"], cp["torque_nm"]) for cp in result["control_points"]
    }
    assert actual_pairs == expected_pairs


def test_control_lut_allows_nonuniform_torque_axis(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path, torque_axis_nm=[25.0, 50.0, 120.0])

    assert result["grid_definition"]["torque_axis_nm"] == [25.0, 50.0, 120.0]
    assert result["grid_definition"]["torque_step_nm"] is None


def test_control_lut_rejects_invalid_torque_axis(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="torque_axis_nm"):
        generate_control_lut(tmp_path, torque_axis_nm=[100.0, 50.0])


def test_control_lut_rejects_non_finite_torque_axis(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="finite"):
        generate_control_lut(tmp_path, torque_axis_nm=[50.0, float("nan")])


def test_control_lut_rejects_non_finite_torque_step(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="finite"):
        generate_control_lut(
            tmp_path, torque_axis_nm=[50.0, 100.0], torque_step_nm=float("inf")
        )


def test_control_lut_has_control_points(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    assert len(result["control_points"]) > 0
    for cp in result["control_points"]:
        assert "speed_rpm" in cp
        assert "torque_nm" in cp
        assert "id_a" in cp
        assert "iq_a" in cp
        assert "actual_torque_nm" in cp
        assert "control_mode" in cp
        assert "feasible" in cp
        assert cp["speed_rpm"] >= 0
        assert cp["speed_rpm"] <= 18000


def test_control_lut_mode_classification(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    modes = {cp["control_mode"] for cp in result["control_points"]}
    assert modes.issubset({"MTPA", "FW", "MTPV", "INFEASIBLE", "IDLE"})


def test_control_lut_has_feasibility_map(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    fm = result["feasibility_map"]
    assert fm["total_points"] > 0
    assert fm["feasible_points"] >= 0
    assert 0.0 <= fm["feasibility_ratio"] <= 1.0
    assert "infeasible_reasons" in fm


def test_control_lut_has_mode_transitions(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    mt = result["mode_transitions"]
    assert "mtpa_to_fw_boundary" in mt
    assert "fw_to_mtpv_boundary" in mt
    assert "demagnetization_limit" in mt
    assert "current_limit_boundary" in mt


def test_mode_transitions_record_current_and_torque_jumps() -> None:
    control_points = [
        {
            "speed_rpm": 0.0,
            "torque_nm": 100.0,
            "actual_torque_nm": 100.0,
            "id_a": -10.0,
            "iq_a": 80.0,
            "control_mode": "MTPA",
        },
        {
            "speed_rpm": 250.0,
            "torque_nm": 100.0,
            "actual_torque_nm": 101.5,
            "id_a": -20.0,
            "iq_a": 70.0,
            "control_mode": "FW",
        },
        {
            "speed_rpm": 500.0,
            "torque_nm": 100.0,
            "actual_torque_nm": 99.0,
            "id_a": -35.0,
            "iq_a": 60.0,
            "control_mode": "MTPV",
        },
    ]

    transitions = _detect_mode_transitions(control_points)

    mtpa_to_fw = transitions["mtpa_to_fw_boundary"][0]
    fw_to_mtpv = transitions["fw_to_mtpv_boundary"][0]
    assert mtpa_to_fw["id_jump_a"] == 10.0
    assert mtpa_to_fw["iq_jump_a"] == 10.0
    assert mtpa_to_fw["torque_jump_nm"] == 1.5
    assert fw_to_mtpv["id_jump_a"] == 15.0
    assert fw_to_mtpv["iq_jump_a"] == 10.0
    assert fw_to_mtpv["torque_jump_nm"] == 2.5
    assert _max_transition_torque_jump(transitions) == 2.5


def test_mode_transitions_are_detected_per_torque_slice() -> None:
    control_points = [
        {
            "speed_rpm": 0.0,
            "torque_nm": 50.0,
            "actual_torque_nm": 50.0,
            "id_a": -10.0,
            "iq_a": 80.0,
            "control_mode": "MTPA",
        },
        {
            "speed_rpm": 0.0,
            "torque_nm": 100.0,
            "actual_torque_nm": 100.0,
            "id_a": -20.0,
            "iq_a": 90.0,
            "control_mode": "FW",
        },
        {
            "speed_rpm": 250.0,
            "torque_nm": 50.0,
            "actual_torque_nm": 51.0,
            "id_a": -15.0,
            "iq_a": 75.0,
            "control_mode": "FW",
        },
        {
            "speed_rpm": 250.0,
            "torque_nm": 100.0,
            "actual_torque_nm": 101.0,
            "id_a": -25.0,
            "iq_a": 85.0,
            "control_mode": "FW",
        },
    ]

    transitions = _detect_mode_transitions(control_points)

    assert len(transitions["mtpa_to_fw_boundary"]) == 1
    assert transitions["mtpa_to_fw_boundary"][0]["torque_nm"] == 50.0


def test_mode_transition_torque_jump_falls_back_to_target_torque() -> None:
    control_points = [
        {
            "speed_rpm": 0.0,
            "torque_nm": 100.0,
            "actual_torque_nm": None,
            "id_a": -10.0,
            "iq_a": 80.0,
            "control_mode": "MTPA",
        },
        {
            "speed_rpm": 250.0,
            "torque_nm": 100.0,
            "actual_torque_nm": None,
            "id_a": -20.0,
            "iq_a": 70.0,
            "control_mode": "FW",
        },
    ]

    transitions = _detect_mode_transitions(control_points)

    assert transitions["mtpa_to_fw_boundary"][0]["torque_jump_nm"] == 0.0


def test_mode_continuity_check_fails_on_large_current_jump() -> None:
    control_points = [
        {"speed_rpm": 0.0, "torque_nm": 100.0, "id_a": 0.0, "iq_a": 0.0},
        {"speed_rpm": 10.0, "torque_nm": 100.0, "id_a": 1000.0, "iq_a": 0.0},
    ]

    assert _check_mode_continuity(control_points) is False


def test_control_lut_has_validation_metrics(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    v = result["validation"]
    assert "mode_continuity_check_passed" in v
    assert "max_id_slope_per_rpm" in v
    assert "max_iq_slope_per_rpm" in v
    assert "torque_discontinuity_at_transitions_nm" in v
    assert "voltage_margin_warning_threshold_v" in v
    assert "low_voltage_margin_points" in v


def test_control_lut_has_metadata(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    m = result["metadata"]
    assert "generated_at" in m
    assert "generator_script" in m
    assert "generator_version" in m


def test_control_lut_accepts_injected_generated_at(tmp_path: Path) -> None:
    generated_at = "2026-05-28T00:00:00+00:00"

    result = run(output_path=tmp_path / "control_lut.json", generated_at=generated_at)

    assert result["metadata"]["generated_at"] == generated_at


def test_control_lut_persists_to_disk(tmp_path: Path) -> None:
    output_path = tmp_path / "persisted_control_lut.json"

    run(output_path=output_path)

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["schema_version"] == "2026-05-14-v1"
    assert len(saved["control_points"]) > 0


def test_control_lut_search_config_matches_current_grid(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    sc = result["model_source"]["search_config"]
    assert sc["search_type"] == "min_current_for_torque"
    assert "id_min_a" in sc["current_grid"]
    assert "id_max_a" in sc["current_grid"]
    assert "iq_min_a" in sc["current_grid"]
    assert "iq_max_a" in sc["current_grid"]
    assert "step_a" in sc["current_grid"]


def test_control_lut_operating_limits_match_params(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    ol = result["operating_limits"]
    assert ol["vmax_v"] > 0
    assert ol["imax_a"] > 0
    assert ol["speed_max_rpm"] > 0
    assert ol["temperature_c"] > 0


def test_control_lut_infeasible_reason_counts_close(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    control_points = result["control_points"]
    infeasible_points = [cp for cp in control_points if not cp["feasible"]]
    allowed_reasons = {
        "voltage_exceeded",
        "current_exceeded",
        "demagnetization_risk",
        "out_of_flux_lut_bounds",
        "search_not_converged",
    }

    assert all(
        cp["infeasibility_reason"] in allowed_reasons for cp in infeasible_points
    )
    reason_counts = result["feasibility_map"]["infeasible_reasons"]
    assert set(reason_counts) == allowed_reasons
    assert sum(reason_counts.values()) == len(infeasible_points)
    assert reason_counts["voltage_exceeded"] > 0
    assert reason_counts["current_exceeded"] == 0


def test_candidate_infeasibility_reason_distinguishes_current_and_voltage() -> None:
    current_limited = Candidate(
        id_a=300.0,
        iq_a=0.0,
        torque_nm=0.0,
        current_a=300.0,
        voltage_v=10.0,
        voltage_margin_v=100.0,
        current_margin_a=-40.0,
        copper_loss_w=1.0,
        feasible=False,
    )
    voltage_limited = Candidate(
        id_a=0.0,
        iq_a=10.0,
        torque_nm=0.0,
        current_a=10.0,
        voltage_v=300.0,
        voltage_margin_v=-50.0,
        current_margin_a=100.0,
        copper_loss_w=1.0,
        feasible=False,
    )

    assert _candidate_infeasibility_reason(current_limited) == "current_exceeded"
    assert _candidate_infeasibility_reason(voltage_limited) == "voltage_exceeded"
    assert (
        _candidate_infeasibility_reason(None, "search_not_converged")
        == "search_not_converged"
    )


def test_control_lut_applies_demag_limit_to_feasible_points(tmp_path: Path) -> None:
    demag_limit = DemagLimit(points_c_to_id_min_a=[(25.0, -10.0), (140.0, -10.0)])

    result = generate_control_lut(tmp_path, demag_limit=demag_limit)

    feasible_points = [cp for cp in result["control_points"] if cp["feasible"]]
    assert all(cp["id_a"] is None or cp["id_a"] >= -10.0 for cp in feasible_points)
    assert result["feasibility_map"]["infeasible_reasons"]["demagnetization_risk"] > 0
    assert result["mode_transitions"]["demagnetization_limit"]
    assert result["metadata"]["demag_limit"] == {
        "points_c_to_id_min_a": [
            {"temperature_c": 25.0, "id_min_a": -10.0},
            {"temperature_c": 140.0, "id_min_a": -10.0},
        ],
        "effective_temperature_c": 25.0,
        "effective_id_min_a": -10.0,
    }


def test_control_lut_nonlinear_mode_records_flux_lut_source(tmp_path: Path) -> None:
    result = generate_control_lut(
        tmp_path, model_type="nonlinear_flux_lut", lut_path=FLUX_LUT_PATH
    )

    assert result["model_source"]["model_type"] == "nonlinear_flux_lut"
    assert result["model_source"]["flux_lut_ref"] == "models/flux_lut_sample.json"
    assert result["model_source"]["linear_dq_ref"] is None
    assert (
        result["model_source"]["experiment_ref"]
        == "experiments/exp_006_nonlinear_flux_lut/"
    )


def test_control_lut_nonlinear_mode_infeasible_reason_counts_close(
    tmp_path: Path,
) -> None:
    result = generate_control_lut(
        tmp_path, model_type="nonlinear_flux_lut", lut_path=FLUX_LUT_PATH
    )

    control_points = result["control_points"]
    infeasible_points = [cp for cp in control_points if not cp["feasible"]]
    reason_counts = result["feasibility_map"]["infeasible_reasons"]

    assert sum(reason_counts.values()) == len(infeasible_points)
    assert all(cp["infeasibility_reason"] is not None for cp in infeasible_points)


def test_control_lut_nonlinear_in_bounds_failure_is_not_lut_bounds(
    tmp_path: Path,
) -> None:
    result = generate_control_lut(
        tmp_path, model_type="nonlinear_flux_lut", lut_path=FLUX_LUT_PATH
    )

    reason_counts = result["feasibility_map"]["infeasible_reasons"]
    assert reason_counts["current_exceeded"] > 0
    assert reason_counts["out_of_flux_lut_bounds"] == 0


def test_control_lut_rejects_flux_lut_outside_project_root(
    tmp_path: Path,
) -> None:
    outside_lut_path = tmp_path / "flux_lut.json"
    outside_lut_path.write_text(
        FLUX_LUT_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="inside the project root"):
        generate_control_lut(
            tmp_path, model_type="nonlinear_flux_lut", lut_path=outside_lut_path
        )


def test_control_lut_rejects_flux_lut_pole_pair_mismatch(tmp_path: Path) -> None:
    lut_data = json.loads(FLUX_LUT_PATH.read_text(encoding="utf-8"))
    lut_data["pole_pairs"] = 6
    mismatch_path = Path("reports/test_flux_lut_pole_pair_mismatch.json")
    mismatch_path.write_text(json.dumps(lut_data), encoding="utf-8")

    try:
        with pytest.raises(ValueError, match="flux_lut.pole_pairs"):
            generate_control_lut(
                tmp_path, model_type="nonlinear_flux_lut", lut_path=mismatch_path
            )
    finally:
        mismatch_path.unlink(missing_ok=True)


def test_control_lut_rejects_flux_lut_motor_id_mismatch(tmp_path: Path) -> None:
    lut_data = json.loads(FLUX_LUT_PATH.read_text(encoding="utf-8"))
    lut_data["motor_id"] = "different_motor"
    mismatch_path = Path("reports/test_flux_lut_motor_id_mismatch.json")
    mismatch_path.write_text(json.dumps(lut_data), encoding="utf-8")

    try:
        with pytest.raises(ValueError, match="motor_id"):
            generate_control_lut(
                tmp_path, model_type="nonlinear_flux_lut", lut_path=mismatch_path
            )
    finally:
        mismatch_path.unlink(missing_ok=True)
