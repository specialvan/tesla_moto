from __future__ import annotations

from math import isclose, pi, sqrt

import pytest

from sim.dq_model import (
    MotorParams,
    copper_loss,
    current_mag_a,
    mechanical_rpm_to_electrical_rad_per_second,
    torque_nm,
    voltage_d_v,
    voltage_q_v,
)
from sim.run_linear_dq_experiment import speed_grid
from sim.search import GridSpec, axis_grid


def valid_params_dict() -> dict:
    return {
        "name": "test_motor",
        "unit_convention": {
            "dq_transform": "amplitude_invariant",
            "current": "phase_peak_ampere",
            "voltage": "phase_peak_volt",
            "resistance": "single_phase_ohm",
            "speed": "mechanical_rpm_input_and_electrical_rad_per_second_internal",
        },
        "pole_pairs": 4,
        "Rs_ohm": 0.1,
        "Ld_h": 0.001,
        "Lq_h": 0.002,
        "psi_f_wb": 0.05,
        "Vdc_v": 300.0,
        "Imax_a": 100.0,
        "speed_max_rpm": 6000.0,
        "torque_target_nm": 10.0,
        "temperature_c": 25.0,
        "svpwm_linear_vmax_factor": 1.0 / sqrt(3.0),
    }


def test_speed_conversion_uses_pole_pairs() -> None:
    omega_e = mechanical_rpm_to_electrical_rad_per_second(60.0, 4)
    assert isclose(omega_e, 8.0 * pi, rel_tol=1e-12)


def test_torque_at_id_zero_is_pm_torque() -> None:
    params = MotorParams.from_dict(valid_params_dict())
    assert isclose(torque_nm(params, 0.0, 10.0), 3.0, rel_tol=1e-12)


def test_zero_speed_voltage_only_uses_resistance() -> None:
    params = MotorParams.from_dict(valid_params_dict())
    assert isclose(voltage_d_v(params, -2.0, 3.0, 0.0), -0.2, rel_tol=1e-12)
    assert isclose(voltage_q_v(params, -2.0, 3.0, 0.0), 0.3, rel_tol=1e-12)


def test_peak_current_to_rms_copper_loss_convention() -> None:
    peak_current = current_mag_a(3.0, 4.0)
    current_rms = peak_current / sqrt(2.0)
    assert isclose(copper_loss(current_rms, 0.1), 3.75, rel_tol=1e-12)


def test_invalid_unit_convention_is_rejected() -> None:
    data = valid_params_dict()
    data = {**data, "unit_convention": {**data["unit_convention"], "current": "rms"}}
    with pytest.raises(ValueError, match="unit_convention"):
        MotorParams.from_dict(data)


def test_nan_parameter_is_rejected() -> None:
    data = {**valid_params_dict(), "Imax_a": float("nan")}
    with pytest.raises(ValueError, match="finite"):
        MotorParams.from_dict(data)


def test_negative_torque_target_is_rejected() -> None:
    data = {**valid_params_dict(), "torque_target_nm": -1.0}
    with pytest.raises(ValueError, match="torque_target_nm"):
        MotorParams.from_dict(data)


def test_grid_axis_clamps_to_maximum() -> None:
    assert list(axis_grid(0.0, 1.0, 0.6)) == [0.0, 0.6, 1.0]


def test_axis_grid_rejects_invalid_step() -> None:
    with pytest.raises(ValueError, match="step"):
        list(axis_grid(0.0, 1.0, 0.0))


def test_invalid_grid_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="id_min_a"):
        GridSpec.from_dict(
            {
                "id_min_a": 1.0,
                "id_max_a": 0.0,
                "iq_min_a": 0.0,
                "iq_max_a": 1.0,
                "step_a": 0.1,
            }
        )


def test_invalid_grid_step_is_rejected() -> None:
    with pytest.raises(ValueError, match="step_a"):
        GridSpec.from_dict(
            {
                "id_min_a": 0.0,
                "id_max_a": 1.0,
                "iq_min_a": 0.0,
                "iq_max_a": 1.0,
                "step_a": 0.0,
            }
        )


def test_speed_grid_appends_exact_maximum() -> None:
    assert speed_grid(1000.0, 300.0) == [0.0, 300.0, 600.0, 900.0, 1000.0]


def test_speed_grid_rejects_invalid_step() -> None:
    with pytest.raises(ValueError, match="positive"):
        speed_grid(1000.0, 0.0)
