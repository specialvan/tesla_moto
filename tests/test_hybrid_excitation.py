from __future__ import annotations

from math import isclose, sqrt

import pytest

from sim.dq_model import MotorParams
from sim.hybrid_excitation import HybridExcitationModel, with_field_current


def sample_params() -> MotorParams:
    return MotorParams.from_dict(
        {
            "name": "hybrid_test_motor",
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


def test_hybrid_model_validates_resistance_positive() -> None:
    with pytest.raises(ValueError):
        HybridExcitationModel(kf_wb_per_a=0.0001, field_resistance_ohm=0.0)


def test_effective_psi_f_shifts_linearly_with_field_current() -> None:
    model = HybridExcitationModel(
        kf_wb_per_a=0.00018, field_resistance_ohm=1.2
    )
    assert isclose(model.effective_psi_f(0.05, 0.0), 0.05, rel_tol=1e-12)
    assert isclose(
        model.effective_psi_f(0.055, -20.0),
        0.055 - 0.0036,
        rel_tol=1e-12,
    )
    assert isclose(
        model.effective_psi_f(0.055, 20.0),
        0.055 + 0.0036,
        rel_tol=1e-12,
    )


def test_field_loss_is_quadratic_in_current() -> None:
    model = HybridExcitationModel(
        kf_wb_per_a=0.00018, field_resistance_ohm=1.2
    )
    assert model.field_loss_w(0.0) == 0.0
    assert isclose(model.field_loss_w(20.0), 480.0, rel_tol=1e-12)
    assert isclose(model.field_loss_w(-60.0), 4320.0, rel_tol=1e-12)


def test_with_field_current_rejects_negative_total_psi_f() -> None:
    base = sample_params()
    model = HybridExcitationModel(kf_wb_per_a=0.001, field_resistance_ohm=1.0)
    with pytest.raises(ValueError):
        with_field_current(base, model, -100.0)


def test_with_field_current_preserves_other_fields() -> None:
    base = sample_params()
    model = HybridExcitationModel(
        kf_wb_per_a=0.00018, field_resistance_ohm=1.2
    )
    boosted = with_field_current(base, model, 20.0)
    assert boosted.rs_ohm == base.rs_ohm
    assert boosted.ld_h == base.ld_h
    assert boosted.lq_h == base.lq_h
    assert boosted.i_max_a == base.i_max_a
    assert boosted.psi_f_wb > base.psi_f_wb
