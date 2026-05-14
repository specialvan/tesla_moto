from __future__ import annotations

import json
from math import isclose
from pathlib import Path

import pytest

from sim.nonlinear_flux_lut import FluxLut, nonlinear_torque_nm
from sim.run_nonlinear_flux_lut_experiment import run

SCHEMA_PATH = Path("models/flux_lut_schema.json")
LUT_SAMPLE_PATH = Path("models/flux_lut_sample.json")
SUMMARY_PATH = Path("experiments/exp_006_nonlinear_flux_lut/summary.json")
CSV_PATH = Path("experiments/exp_006_nonlinear_flux_lut/nonlinear_flux_lut_results.csv")


REQUIRED_LUT_FIELDS = {
    "version",
    "purpose",
    "pole_pairs",
    "unit_convention",
    "id_axis_a",
    "iq_axis_a",
    "lambda_d_wb",
    "lambda_q_wb",
}


def load_lut() -> FluxLut:
    return FluxLut.from_file(LUT_SAMPLE_PATH)


def test_flux_lut_schema_matches_sample_and_runtime_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    sample = json.loads(LUT_SAMPLE_PATH.read_text(encoding="utf-8"))

    assert REQUIRED_LUT_FIELDS == set(schema["required"])
    assert REQUIRED_LUT_FIELDS == set(schema["properties"])
    assert REQUIRED_LUT_FIELDS == set(sample)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["pole_pairs"]["minimum"] == 1
    assert (
        schema["properties"]["unit_convention"]["properties"]["dq_transform"]["const"]
        == "amplitude_invariant"
    )
    assert (
        schema["properties"]["unit_convention"]["properties"]["current"]["const"]
        == "phase_peak_ampere"
    )
    assert (
        schema["properties"]["unit_convention"]["properties"]["flux_linkage"]["const"]
        == "weber"
    )

    lut = FluxLut.from_dict(sample)
    assert lut.pole_pairs == sample["pole_pairs"]
    assert lut.id_axis_a == sample["id_axis_a"]
    assert lut.iq_axis_a == sample["iq_axis_a"]


def test_flux_lut_from_dict_rejects_unsorted_axes_and_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        FluxLut.from_dict(
            {
                "pole_pairs": 4,
                "unit_convention": {
                    "dq_transform": "amplitude_invariant",
                    "current": "phase_peak_ampere",
                    "flux_linkage": "weber",
                },
                "id_axis_a": [-100.0, -200.0],
                "iq_axis_a": [0.0, 100.0],
                "lambda_d_wb": [[0.02, 0.03], [0.04, 0.05]],
                "lambda_q_wb": [[0.00, 0.01], [0.00, 0.02]],
            }
        )

    with pytest.raises(ValueError, match="row count"):
        FluxLut.from_dict(
            {
                "pole_pairs": 4,
                "unit_convention": {
                    "dq_transform": "amplitude_invariant",
                    "current": "phase_peak_ampere",
                    "flux_linkage": "weber",
                },
                "id_axis_a": [-200.0, -100.0],
                "iq_axis_a": [0.0, 100.0],
                "lambda_d_wb": [[0.02, 0.03]],
                "lambda_q_wb": [[0.00, 0.01], [0.00, 0.02]],
            }
        )

    with pytest.raises(ValueError, match="column count"):
        FluxLut.from_dict(
            {
                "pole_pairs": 4,
                "unit_convention": {
                    "dq_transform": "amplitude_invariant",
                    "current": "phase_peak_ampere",
                    "flux_linkage": "weber",
                },
                "id_axis_a": [-200.0, -100.0],
                "iq_axis_a": [0.0, 100.0],
                "lambda_d_wb": [[0.02], [0.04]],
                "lambda_q_wb": [[0.00, 0.01], [0.00, 0.02]],
            }
        )


def test_flux_lut_interpolates_bilinearly_inside_cell() -> None:
    point = load_lut().interpolate(id_a=-150.0, iq_a=50.0)

    assert isclose(point.lambda_d_wb, 0.026, rel_tol=1e-12)
    assert isclose(point.lambda_q_wb, 0.019125, rel_tol=1e-12)


def test_flux_lut_accepts_boundary_points_and_rejects_out_of_bounds() -> None:
    lut = load_lut()

    assert lut.contains(-200.0, 200.0)
    assert not lut.contains(-260.0, 200.0)

    with pytest.raises(ValueError, match="outside the flux LUT bounds"):
        lut.interpolate(-260.0, 200.0)


def test_nonlinear_torque_uses_cross_flux_difference_and_rejects_invalid_pole_pairs() -> None:
    lut = load_lut()
    torque = nonlinear_torque_nm(lut, pole_pairs=lut.pole_pairs, id_a=-100.0, iq_a=100.0)

    assert isclose(torque, 42.3, rel_tol=1e-12)

    with pytest.raises(ValueError, match="pole_pairs"):
        nonlinear_torque_nm(lut, pole_pairs=0, id_a=-100.0, iq_a=100.0)


def test_exp_006_runner_writes_summary_and_csv_outputs() -> None:
    summary = run()

    assert SUMMARY_PATH.exists()
    assert CSV_PATH.exists()
    assert summary["experiment"] == "exp_006_nonlinear_flux_lut"
    assert summary["pole_pairs"] == 4
    assert summary["lut_path"] == "models\\flux_lut_sample.json"
    assert summary["csv_path"] == "experiments\\exp_006_nonlinear_flux_lut\\nonlinear_flux_lut_results.csv"
    assert summary["grid_points"] == 9
    assert summary["best_torque_point"]["torque_nm"] > 0.0

    header = CSV_PATH.read_text(encoding="utf-8").splitlines()[0]
    assert "lambda_d_wb" in header
    assert "lambda_q_wb" in header
    assert "torque_nm" in header

    data = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert data["model_scope"] == "synthetic_lambda_d_lambda_q_lut_interpolation"
    assert data["pole_pairs"] == 4
    assert data["lut_path"] == "models\\flux_lut_sample.json"
    assert data["csv_path"] == "experiments\\exp_006_nonlinear_flux_lut\\nonlinear_flux_lut_results.csv"


def test_exp_006_json_outputs_do_not_contain_nonstandard_numbers() -> None:
    run()
    text = SUMMARY_PATH.read_text(encoding="utf-8")

    assert "Infinity" not in text
    assert "NaN" not in text


def test_exp_006_csv_outputs_do_not_contain_infinite_values() -> None:
    run()
    text = CSV_PATH.read_text(encoding="utf-8")

    assert "inf" not in text.lower()
    assert "nan" not in text.lower()
