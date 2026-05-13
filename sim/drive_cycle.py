"""Drive-cycle weighted scoring for clean-room candidate ranking.

A drive cycle is a list of weighted operating points
(``speed_rpm``, ``torque_nm``, ``weight``). Weights must be positive
and sum to a known total (we normalize by their sum so cycles with
different absolute weights stay comparable). For each candidate motor
parameter set, we evaluate every operating point with the same grid
search used by other experiments and compute:

* ``feasible_weight``: the share of the cycle (0..1) that is reachable.
* ``weighted_copper_loss_w``: sum over reachable points of
  ``weight * copper_loss_w / total_weight``.
* ``score``: ``feasible_weight / (1 + weighted_copper_loss_w / loss_scale)``.

Lower copper loss and higher feasibility yield higher score.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .search import GridSpec, find_min_current_for_torque


@dataclass(frozen=True)
class DriveCyclePoint:
    speed_rpm: float
    torque_nm: float
    weight: float

    def __post_init__(self) -> None:
        for name, value in {
            "speed_rpm": self.speed_rpm,
            "torque_nm": self.torque_nm,
            "weight": self.weight,
        }.items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.speed_rpm < 0:
            raise ValueError("speed_rpm must be non-negative")
        if self.torque_nm < 0:
            raise ValueError("torque_nm must be non-negative")
        if self.weight <= 0:
            raise ValueError("weight must be positive")


@dataclass(frozen=True)
class DriveCycle:
    name: str
    points: tuple[DriveCyclePoint, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must be non-empty")
        if not self.points:
            raise ValueError("DriveCycle must have at least one point")

    @property
    def total_weight(self) -> float:
        return sum(point.weight for point in self.points)


@dataclass(frozen=True)
class DriveCycleScore:
    candidate: str
    cycle: str
    feasible_weight: float
    weighted_copper_loss_w: float
    score: float
    reachable_points: int
    total_points: int


def score_candidate_on_cycle(
    candidate_name: str,
    params: MotorParams,
    grid: GridSpec,
    cycle: DriveCycle,
    loss_scale_w: float,
) -> DriveCycleScore:
    if loss_scale_w <= 0:
        raise ValueError("loss_scale_w must be positive")

    total_weight = cycle.total_weight
    reachable_weight = 0.0
    weighted_loss = 0.0
    reachable_points = 0

    for point in cycle.points:
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            point.speed_rpm, params.pole_pairs
        )
        candidate = find_min_current_for_torque(
            params, omega_e, point.torque_nm, grid
        )
        if candidate is None:
            continue
        share = point.weight / total_weight
        reachable_weight += share
        weighted_loss += share * float(candidate.copper_loss_w)
        reachable_points += 1

    score = reachable_weight / (1.0 + weighted_loss / loss_scale_w)
    return DriveCycleScore(
        candidate=candidate_name,
        cycle=cycle.name,
        feasible_weight=reachable_weight,
        weighted_copper_loss_w=weighted_loss,
        score=score,
        reachable_points=reachable_points,
        total_points=len(cycle.points),
    )


def rank_candidates_on_cycle(
    cycle: DriveCycle,
    candidates: Sequence[tuple[str, MotorParams, GridSpec]],
    loss_scale_w: float,
) -> list[DriveCycleScore]:
    scored = [
        score_candidate_on_cycle(name, params, grid, cycle, loss_scale_w)
        for name, params, grid in candidates
    ]
    return sorted(scored, key=lambda row: row.score, reverse=True)
