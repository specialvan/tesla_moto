"""Tests for sim/run_control_lut_generator.py."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from sim.search import Candidate
from sim.safety_limits import DemagLimit
from sim.run_control_lut_generator import _candidate_infeasibility_reason, run


FLUX_LUT_PATH = Path("models/flux_lut_sample.json")


def generate_control_lut(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    return run(output_path=tmp_path / "control_lut.json", **kwargs)


def test_control_lut_generator_writes_json_output(tmp_path: Path) -> None:
    output_path = tmp_path / "control_lut.json"

    result = run(output_path=output_path)

    assert output_path.exists()
    assert result["schema_version"] == "2026-05-14-v1"
    assert result["unit_convention"]["dq_transform"] == "amplitude_invariant"
    assert result["model_source"]["model_type"] == "linear_dq"
    assert result["pole_pairs"] == 4


def test_control_lut_has_speed_torque_grid(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    assert len(result["grid_definition"]["speed_axis_rpm"]) > 0
    assert result["grid_definition"]["torque_axis_nm"] == [100.0]
    assert result["grid_definition"]["interpolation_method"] == "nearest"
    assert result["grid_definition"]["extrapolation_policy"] == "clamp"


def test_control_lut_has_control_points(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    assert len(result["control_points"]) > 0
    for cp in result["control_points"]:
        assert "speed_rpm" in cp
        assert "torque_nm" in cp
        assert "id_a" in cp
        assert "iq_a" in cp
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


def test_control_lut_has_validation_metrics(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    v = result["validation"]
    assert "mode_continuity_check_passed" in v
    assert "max_id_slope_per_rpm" in v
    assert "max_iq_slope_per_rpm" in v
    assert "voltage_margin_warning_threshold_v" in v
    assert "low_voltage_margin_points" in v


def test_control_lut_has_metadata(tmp_path: Path) -> None:
    result = generate_control_lut(tmp_path)

    m = result["metadata"]
    assert "generated_at" in m
    assert "generator_script" in m
    assert "generator_version" in m


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
