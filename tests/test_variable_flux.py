from __future__ import annotations

from math import isclose, sqrt

import pytest

from sim.dq_model import MotorParams
from sim.variable_flux import with_flux_scale


def sample_params() -> MotorParams:
    return MotorParams.from_dict(
        {
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
    )


def test_with_flux_scale_returns_new_params_without_mutating_original() -> None:
    params = sample_params()
    low_flux = with_flux_scale(params, 0.7, "psi_70pct")

    assert low_flux is not params
    assert params.psi_f_wb == 0.05
    assert isclose(low_flux.psi_f_wb, 0.035, rel_tol=1e-12)
    assert low_flux.name == "test_motor_psi_70pct"


def test_with_flux_scale_rejects_invalid_scale() -> None:
    with pytest.raises(ValueError, match="positive"):
        with_flux_scale(sample_params(), 0.0, "bad")
