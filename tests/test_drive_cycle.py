from __future__ import annotations

from math import isclose, sqrt

import pytest

from sim.drive_cycle import (
    DriveCycle,
    DriveCyclePoint,
    rank_candidates_on_cycle,
    score_candidate_on_cycle,
)
from sim.dq_model import MotorParams
from sim.search import GridSpec


def sample_params() -> MotorParams:
    return MotorParams.from_dict(
        {
            "name": "drive_cycle_test_motor",
            "unit_convention": {
                "dq_transform": "amplitude_invariant",
                "current": "phase_peak_ampere",
                "voltage": "phase_peak_volt",
                "resistance": "single_phase_ohm",
                "speed": "mechanical_rpm_input_and_electrical_rad_per_second_internal",
            },
            "pole_pairs": 4,
            "Rs_ohm": 0.05,
            "Ld_h": 0.0005,
            "Lq_h": 0.001,
            "psi_f_wb": 0.06,
            "Vdc_v": 360.0,
            "Imax_a": 200.0,
            "speed_max_rpm": 6000.0,
            "torque_target_nm": 50.0,
            "temperature_c": 25.0,
            "svpwm_linear_vmax_factor": 1.0 / sqrt(3.0),
        }
    )


def sample_grid() -> GridSpec:
    return GridSpec(
        id_min_a=-200.0,
        id_max_a=20.0,
        iq_min_a=0.0,
        iq_max_a=200.0,
        step_a=4.0,
    )


def test_drive_cycle_point_validates_weight_positive() -> None:
    with pytest.raises(ValueError):
        DriveCyclePoint(speed_rpm=1000.0, torque_nm=20.0, weight=0.0)


def test_drive_cycle_total_weight_sums_points() -> None:
    cycle = DriveCycle(
        name="test",
        points=(
            DriveCyclePoint(speed_rpm=1000.0, torque_nm=10.0, weight=0.4),
            DriveCyclePoint(speed_rpm=2000.0, torque_nm=10.0, weight=0.6),
        ),
    )
    assert isclose(cycle.total_weight, 1.0, rel_tol=1e-12)


def test_score_candidate_on_unreachable_cycle_returns_zero_score() -> None:
    params = sample_params()
    grid = sample_grid()
    cycle = DriveCycle(
        name="impossible",
        points=(
            DriveCyclePoint(speed_rpm=1000.0, torque_nm=1000.0, weight=1.0),
        ),
    )
    score = score_candidate_on_cycle("baseline", params, grid, cycle, loss_scale_w=3000.0)
    assert score.feasible_weight == 0.0
    assert score.weighted_copper_loss_w == 0.0
    assert score.score == 0.0


def test_rank_candidates_on_cycle_orders_by_score() -> None:
    base = sample_params()
    grid = sample_grid()
    weak = MotorParams.from_dict(
        {
            **{k: v for k, v in {
                "name": "weak",
                "unit_convention": {
                    "dq_transform": "amplitude_invariant",
                    "current": "phase_peak_ampere",
                    "voltage": "phase_peak_volt",
                    "resistance": "single_phase_ohm",
                    "speed": "mechanical_rpm_input_and_electrical_rad_per_second_internal",
                },
                "pole_pairs": 4,
                "Rs_ohm": 0.20,  # higher resistance → more loss
                "Ld_h": 0.0005,
                "Lq_h": 0.001,
                "psi_f_wb": 0.06,
                "Vdc_v": 360.0,
                "Imax_a": 200.0,
                "speed_max_rpm": 6000.0,
                "torque_target_nm": 50.0,
                "temperature_c": 25.0,
                "svpwm_linear_vmax_factor": 1.0 / sqrt(3.0),
            }.items()}
        }
    )
    cycle = DriveCycle(
        name="modest",
        points=(
            DriveCyclePoint(speed_rpm=1000.0, torque_nm=20.0, weight=1.0),
        ),
    )
    ranked = rank_candidates_on_cycle(
        cycle,
        [("baseline", base, grid), ("weak", weak, grid)],
        loss_scale_w=3000.0,
    )
    # Baseline should outrank "weak" because lower Rs gives lower copper loss.
    assert ranked[0].candidate == "baseline"
    assert ranked[0].score >= ranked[1].score
