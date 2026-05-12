from __future__ import annotations

import json
from math import isclose
from pathlib import Path

from sim.nonlinear_flux_lut import FluxLut, nonlinear_torque_nm
from sim.run_nonlinear_flux_lut_experiment import run


def test_flux_lut_interpolates_inside_grid_and_rejects_out_of_bounds() -> None:
    lut = FluxLut.from_file(Path("models/flux_lut_sample.json"))

    lambdas = lut.interpolate(id_a=-100.0, iq_a=100.0)

    assert isclose(lambdas.lambda_d_wb, 0.033, rel_tol=1e-12)
    assert isclose(lambdas.lambda_q_wb, 0.0375, rel_tol=1e-12)
    assert lut.contains(-200.0, 200.0)
    assert not lut.contains(-260.0, 200.0)


def test_nonlinear_torque_uses_cross_flux_difference() -> None:
    lut = FluxLut.from_file(Path("models/flux_lut_sample.json"))

    torque = nonlinear_torque_nm(lut, pole_pairs=4, id_a=-100.0, iq_a=100.0)

    assert isclose(torque, 42.3, rel_tol=1e-12)


def test_nonlinear_flux_lut_experiment_writes_summary_and_csv() -> None:
    summary = run()
    summary_path = Path("experiments/exp_006_nonlinear_flux_lut/summary.json")
    csv_path = Path(
        "experiments/exp_006_nonlinear_flux_lut/nonlinear_flux_lut_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_006_nonlinear_flux_lut"
    assert summary["grid_points"] == 9
    assert summary["best_torque_point"]["torque_nm"] > 0.0

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "lambda_d_wb" in header
    assert "lambda_q_wb" in header
    assert "torque_nm" in header

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["model_scope"] == "synthetic_lambda_d_lambda_q_lut_interpolation"
