from __future__ import annotations

from math import isclose, sqrt

import pytest

from sim.dq_model import MotorParams
from sim.modulation import (
    HARMONIC_RATIO_PER_K,
    INVERTER_LOSS_PER_K,
    TORQUE_RIPPLE_PER_K,
    harmonic_current_rms_ratio,
    inverter_loss_multiplier,
    modulation_penalty,
    torque_ripple_ratio,
    with_modulation_factor,
)


def sample_params() -> MotorParams:
    return MotorParams.from_dict(
        {
            "name": "kmod_test_motor",
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


def test_linear_region_has_no_penalty() -> None:
    assert harmonic_current_rms_ratio(1.0) == 0.0
    assert inverter_loss_multiplier(1.0) == 1.0
    assert torque_ripple_ratio(1.0) == 0.0


def test_overmodulation_curves_are_linear_in_excess_factor() -> None:
    excess = 0.04
    assert isclose(
        harmonic_current_rms_ratio(1.0 + excess),
        HARMONIC_RATIO_PER_K * excess,
        rel_tol=1e-12,
    )
    assert isclose(
        inverter_loss_multiplier(1.0 + excess),
        1.0 + INVERTER_LOSS_PER_K * excess,
        rel_tol=1e-12,
    )
    assert isclose(
        torque_ripple_ratio(1.0 + excess),
        TORQUE_RIPPLE_PER_K * excess,
        rel_tol=1e-12,
    )


def test_modulation_penalty_bundles_three_curves() -> None:
    bundle = modulation_penalty(1.08)
    assert bundle.k_mod == 1.08
    assert isclose(bundle.harmonic_current_rms_ratio, 0.144, rel_tol=1e-12)
    assert isclose(bundle.inverter_loss_multiplier, 1.0128, rel_tol=1e-12)
    assert isclose(bundle.torque_ripple_ratio, 0.20, rel_tol=1e-12)


def test_subunity_modulation_factor_rejected() -> None:
    with pytest.raises(ValueError):
        modulation_penalty(0.95)


def test_with_modulation_factor_scales_only_vmax_factor() -> None:
    base = sample_params()
    overdriven = with_modulation_factor(base, 1.1)

    assert isclose(
        overdriven.svpwm_linear_vmax_factor,
        base.svpwm_linear_vmax_factor * 1.1,
        rel_tol=1e-12,
    )
    assert overdriven.vdc_v == base.vdc_v
    assert overdriven.psi_f_wb == base.psi_f_wb
    assert overdriven.name.endswith("_kmod1.10")
