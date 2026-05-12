from __future__ import annotations

from math import isclose, sqrt

from sim.dq_model import MotorParams
from sim.safety_limits import (
    DemagLimit,
    ThermalModel,
    apply_temperature,
    find_min_current_for_torque_with_safety,
)
from sim.search import GridSpec


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


def test_apply_temperature_scales_resistance_and_pm_flux() -> None:
    model = ThermalModel(
        reference_c=25.0, copper_alpha_per_c=0.004, pm_alpha_per_c=-0.001
    )
    hot = apply_temperature(sample_params(), 125.0, model)

    assert isclose(hot.rs_ohm, 0.14, rel_tol=1e-12)
    assert isclose(hot.psi_f_wb, 0.045, rel_tol=1e-12)
    assert hot.temperature_c == 125.0


def test_demag_limit_interpolates_id_min() -> None:
    limit = DemagLimit(points_c_to_id_min_a=[(25.0, -100.0), (125.0, -60.0)])

    assert isclose(limit.id_min_allowed(25.0), -100.0, rel_tol=1e-12)
    assert isclose(limit.id_min_allowed(75.0), -80.0, rel_tol=1e-12)
    assert isclose(limit.id_min_allowed(150.0), -60.0, rel_tol=1e-12)


def test_safety_search_rejects_candidates_beyond_demag_limit() -> None:
    params = sample_params()
    grid = GridSpec(
        id_min_a=-100.0, id_max_a=0.0, iq_min_a=0.0, iq_max_a=100.0, step_a=10.0
    )
    limit = DemagLimit(points_c_to_id_min_a=[(25.0, -30.0), (125.0, -10.0)])

    result = find_min_current_for_torque_with_safety(
        params=params,
        omega_e=0.0,
        target_torque_nm=20.0,
        grid=grid,
        demag_limit=limit,
    )

    assert result is not None
    assert result.id_a >= -30.0
