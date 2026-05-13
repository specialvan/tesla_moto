from __future__ import annotations

from math import isclose, sqrt

import pytest

from sim.dq_model import MotorParams
from sim.multiphase_phase_group import PhaseGroupCase, apply_phase_group_case
from sim.search import GridSpec


def sample_params() -> MotorParams:
    return MotorParams.from_dict(
        {
            "name": "multiphase_test_motor",
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


def sample_grid() -> GridSpec:
    return GridSpec(
        id_min_a=-100.0,
        id_max_a=20.0,
        iq_min_a=0.0,
        iq_max_a=100.0,
        step_a=2.0,
    )


def test_phase_group_case_validates_healthy_groups_in_range() -> None:
    with pytest.raises(ValueError):
        PhaseGroupCase(
            name="bad",
            total_groups=3,
            healthy_groups=4,
            per_group_current_limit_a=90.0,
            sharing_imbalance_ratio=0.0,
        )


def test_balanced_case_available_current_matches_total_capacity() -> None:
    case = PhaseGroupCase(
        name="balanced",
        total_groups=3,
        healthy_groups=3,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.0,
    )
    assert isclose(case.available_current_a, 270.0, rel_tol=1e-12)
    assert case.group_utilization == 1.0
    assert case.healthy_group_ratio == 1.0


def test_imbalanced_case_drops_available_current() -> None:
    case = PhaseGroupCase(
        name="imbalanced",
        total_groups=3,
        healthy_groups=3,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.08,
    )
    assert isclose(case.available_current_a, 270.0 / 1.08, rel_tol=1e-12)
    assert isclose(case.group_utilization, 1.08, rel_tol=1e-12)


def test_apply_phase_group_case_clamps_grid_and_imax() -> None:
    case = PhaseGroupCase(
        name="one_group_lost",
        total_groups=3,
        healthy_groups=2,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.08,
    )
    params, grid = apply_phase_group_case(sample_params(), sample_grid(), case)
    expected_available = 2 * 90.0 / 1.08
    assert isclose(params.i_max_a, expected_available, rel_tol=1e-12)
    # Grid bounds shrink so we never search above the available current.
    assert abs(grid.id_min_a) <= expected_available + 1e-9
    assert grid.iq_max_a <= expected_available + 1e-9
