"""Tests for sim/run_control_lut_generator.py."""

from __future__ import annotations

import json
from pathlib import Path

from sim.run_control_lut_generator import run


CONTROL_LUT_PATH = Path("models/control_lut.json")


def test_control_lut_generator_writes_json_output() -> None:
    result = run()

    assert CONTROL_LUT_PATH.exists()
    assert result["schema_version"] == "2026-05-14-v1"
    assert result["unit_convention"]["dq_transform"] == "amplitude_invariant"
    assert result["model_source"]["model_type"] == "linear_dq"
    assert result["pole_pairs"] == 4


def test_control_lut_has_speed_torque_grid() -> None:
    result = run()

    assert len(result["grid_definition"]["speed_axis_rpm"]) > 0
    assert result["grid_definition"]["torque_axis_nm"] == [100.0]
    assert result["grid_definition"]["interpolation_method"] == "nearest"
    assert result["grid_definition"]["extrapolation_policy"] == "clamp"


def test_control_lut_has_control_points() -> None:
    result = run()

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


def test_control_lut_mode_classification() -> None:
    result = run()

    modes = {cp["control_mode"] for cp in result["control_points"]}
    assert modes.issubset({"MTPA", "FW", "MTPV", "INFEASIBLE", "IDLE"})


def test_control_lut_has_feasibility_map() -> None:
    result = run()

    fm = result["feasibility_map"]
    assert fm["total_points"] > 0
    assert fm["feasible_points"] >= 0
    assert 0.0 <= fm["feasibility_ratio"] <= 1.0
    assert "infeasible_reasons" in fm


def test_control_lut_has_mode_transitions() -> None:
    result = run()

    mt = result["mode_transitions"]
    assert "mtpa_to_fw_boundary" in mt
    assert "fw_to_mtpv_boundary" in mt
    assert "demagnetization_limit" in mt
    assert "current_limit_boundary" in mt


def test_control_lut_has_validation_metrics() -> None:
    result = run()

    v = result["validation"]
    assert "mode_continuity_check_passed" in v
    assert "max_id_slope_per_rpm" in v
    assert "max_iq_slope_per_rpm" in v
    assert "voltage_margin_warning_threshold_v" in v
    assert "low_voltage_margin_points" in v


def test_control_lut_has_metadata() -> None:
    result = run()

    m = result["metadata"]
    assert "generated_at" in m
    assert "generator_script" in m
    assert "generator_version" in m


def test_control_lut_persists_to_disk() -> None:
    result = run()

    saved = json.loads(CONTROL_LUT_PATH.read_text(encoding="utf-8"))
    assert saved["schema_version"] == "2026-05-14-v1"
    assert len(saved["control_points"]) > 0


def test_control_lut_search_config_matches_current_grid() -> None:
    result = run()

    sc = result["model_source"]["search_config"]
    assert sc["search_type"] == "min_current_for_torque"
    assert "id_min_a" in sc["current_grid"]
    assert "id_max_a" in sc["current_grid"]
    assert "iq_min_a" in sc["current_grid"]
    assert "iq_max_a" in sc["current_grid"]
    assert "step_a" in sc["current_grid"]


def test_control_lut_operating_limits_match_params() -> None:
    result = run()

    ol = result["operating_limits"]
    assert ol["vmax_v"] > 0
    assert ol["imax_a"] > 0
    assert ol["speed_max_rpm"] > 0
    assert ol["temperature_c"] > 0