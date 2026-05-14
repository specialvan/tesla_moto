from __future__ import annotations

import csv
import json
from math import isclose, sqrt
from pathlib import Path

from sim.dq_model import mechanical_rpm_to_electrical_rad_per_second
from sim.nonlinear_flux_lut import FluxLut
from sim.run_linear_dq_experiment import load_params
from sim.run_nonlinear_flux_lut_search_experiment import run
from sim.search import (
    find_id_zero_candidate,
    find_max_torque_feasible,
    find_min_current_for_torque,
    make_candidate,
)

LUT_PATH = Path("models/flux_lut_sample.json")
SUMMARY_PATH = Path("experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json")
CSV_PATH = Path("experiments/exp_006_nonlinear_flux_lut/lut_search_scan_results.csv")
EXP001_CSV_PATH = Path("experiments/exp_001_linear_dq/scan_results.csv")


def load_sample_lut() -> FluxLut:
    return FluxLut.from_file(LUT_PATH)


def test_make_candidate_uses_nonlinear_flux_for_torque_and_voltage() -> None:
    params, _, _ = load_params()
    lut = load_sample_lut()
    omega_e = mechanical_rpm_to_electrical_rad_per_second(3000.0, params.pole_pairs)

    result = make_candidate(params, -100.0, 100.0, omega_e, flux_lut=lut)

    expected_vd = params.rs_ohm * -100.0 - omega_e * 0.0375
    expected_vq = params.rs_ohm * 100.0 + omega_e * 0.033
    expected_voltage = sqrt(expected_vd * expected_vd + expected_vq * expected_vq)

    assert isclose(result.torque_nm, 42.3, rel_tol=1e-12)
    assert isclose(result.current_a, sqrt(20000.0), rel_tol=1e-12)
    assert isclose(result.voltage_v, expected_voltage, rel_tol=1e-12)
    assert isclose(result.voltage_margin_v, params.vmax_v - expected_voltage, rel_tol=1e-12)


def test_find_max_torque_feasible_clips_baseline_grid_to_lut_bounds() -> None:
    params, _, grid = load_params()
    lut = load_sample_lut()
    omega_e = mechanical_rpm_to_electrical_rad_per_second(0.0, params.pole_pairs)

    result = find_max_torque_feasible(params, omega_e, grid, flux_lut=lut)

    assert result is not None
    assert result.feasible
    assert lut.contains(result.id_a, result.iq_a)
    assert (result.id_a, result.iq_a) == (-166.0, 200.0)
    assert isclose(result.current_a, 259.9153708421262, rel_tol=1e-12)
    assert isclose(result.torque_nm, 98.00807999999999, rel_tol=1e-12)


def test_find_id_zero_candidate_returns_none_for_sample_lut_target() -> None:
    params, _, grid = load_params()
    lut = load_sample_lut()
    omega_e = mechanical_rpm_to_electrical_rad_per_second(0.0, params.pole_pairs)

    result = find_id_zero_candidate(
        params, omega_e, params.torque_target_nm, grid, flux_lut=lut
    )

    assert result is None


def test_find_min_current_for_torque_returns_none_when_lut_cannot_reach_target() -> None:
    params, _, grid = load_params()
    lut = load_sample_lut()
    omega_e = mechanical_rpm_to_electrical_rad_per_second(0.0, params.pole_pairs)

    result = find_min_current_for_torque(
        params, omega_e, params.torque_target_nm, grid, flux_lut=lut
    )

    assert result is None


def test_lut_search_runner_writes_summary_and_csv() -> None:
    summary = run()

    assert SUMMARY_PATH.exists()
    assert CSV_PATH.exists()
    assert summary["experiment"] == "exp_006_nonlinear_flux_lut_search"
    assert summary["model_scope"] == "quasi_steady_nonlinear_flux_lut_grid_search"
    assert summary["search_grid_clipped_to_lut_bounds"] is True
    assert summary["lut_path"] == "models\\flux_lut_sample.json"
    assert summary["csv_path"] == "experiments\\exp_006_nonlinear_flux_lut\\lut_search_scan_results.csv"

    saved = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert saved["experiment"] == "exp_006_nonlinear_flux_lut_search"
    assert saved["pole_pairs"] == 4
    assert saved["id_zero_target_max_speed_rpm"] is None
    assert saved["min_current_target_max_speed_rpm"] is None


def test_lut_search_csv_matches_clipped_search_semantics() -> None:
    run()
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))

    first_row = rows[0]
    assert first_row["min_current_target_feasible"] == "False"
    assert first_row["max_feasible_torque_id_a"] == "-166.0"
    assert first_row["max_feasible_torque_iq_a"] == "200.0"
    assert first_row["max_feasible_torque_feasible"] == "True"


def test_lut_search_csv_header_matches_exp001_scan_header() -> None:
    run()
    from sim.run_linear_dq_experiment import run as run_linear

    run_linear()
    lut_header = next(csv.reader(CSV_PATH.open(encoding="utf-8")))
    exp001_header = next(csv.reader(EXP001_CSV_PATH.open(encoding="utf-8")))

    assert lut_header == exp001_header
