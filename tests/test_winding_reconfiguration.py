from __future__ import annotations

from math import isclose, sqrt

import pytest

from sim.dq_model import MotorParams
from sim.winding_reconfiguration import WindingConfig, apply_winding_config


def sample_params() -> MotorParams:
    return MotorParams.from_dict(
        {
            "name": "winding_test_motor",
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


def test_winding_config_validates_positive_scales() -> None:
    with pytest.raises(ValueError):
        WindingConfig(
            name="bad",
            turns_scale=0.0,
            resistance_scale=1.0,
            current_limit_scale=1.0,
        )


def test_apply_winding_config_scales_inductance_by_turns_squared() -> None:
    base = sample_params()
    config = WindingConfig(
        name="series_torque",
        turns_scale=1.2,
        resistance_scale=1.4,
        current_limit_scale=0.85,
    )
    scaled = apply_winding_config(base, config)

    assert isclose(scaled.psi_f_wb, base.psi_f_wb * 1.2, rel_tol=1e-12)
    assert isclose(scaled.ld_h, base.ld_h * 1.44, rel_tol=1e-12)
    assert isclose(scaled.lq_h, base.lq_h * 1.44, rel_tol=1e-12)
    assert isclose(scaled.rs_ohm, base.rs_ohm * 1.4, rel_tol=1e-12)
    assert isclose(scaled.i_max_a, base.i_max_a * 0.85, rel_tol=1e-12)
    assert scaled.name.endswith("_series_torque")
