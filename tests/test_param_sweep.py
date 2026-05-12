from __future__ import annotations

from math import isclose, sqrt

import pytest

from sim.dq_model import MotorParams
from sim.param_sweep import make_variant, variant_grid
from sim.run_param_sweep_experiment import scale_grid_for_variant
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


def test_make_variant_scales_expected_fields_without_mutation() -> None:
    base = sample_params()
    variant = make_variant(base, 0.8, 1.2, 1.5, 1.1, 1.3)

    assert base.psi_f_wb == 0.05
    assert isclose(variant.params.psi_f_wb, 0.04, rel_tol=1e-12)
    assert isclose(variant.params.ld_h, 0.0012, rel_tol=1e-12)
    assert isclose(variant.params.lq_h, 0.003, rel_tol=1e-12)
    assert isclose(variant.params.vdc_v, 330.0, rel_tol=1e-12)
    assert isclose(variant.params.imax_a, 130.0, rel_tol=1e-12)
    assert isclose(variant.saliency_ratio, 2.5, rel_tol=1e-12)


def test_make_variant_rejects_invalid_scale() -> None:
    with pytest.raises(ValueError, match="psi_scale"):
        make_variant(sample_params(), 0.0, 1.0, 1.0, 1.0, 1.0)


def test_variant_grid_combines_axes() -> None:
    variants = list(
        variant_grid(
            sample_params(),
            psi_scales=[1.0, 0.8],
            ld_scales=[1.0],
            lq_scales=[1.0, 1.2],
            vdc_scales=[1.0],
            imax_scales=[1.0],
        )
    )
    assert len(variants) == 4


def test_scale_grid_for_variant_expands_current_search_bounds() -> None:
    base_grid = GridSpec(
        id_min_a=-100.0,
        id_max_a=20.0,
        iq_min_a=0.0,
        iq_max_a=100.0,
        step_a=2.0,
    )
    variant = make_variant(sample_params(), 1.0, 1.0, 1.0, 1.0, 1.3)

    scaled_grid = scale_grid_for_variant(base_grid, variant)

    assert isclose(scaled_grid.id_min_a, -130.0, rel_tol=1e-12)
    assert isclose(scaled_grid.id_max_a, 26.0, rel_tol=1e-12)
    assert isclose(scaled_grid.iq_max_a, 130.0, rel_tol=1e-12)
    assert isclose(scaled_grid.step_a, 2.0, rel_tol=1e-12)
