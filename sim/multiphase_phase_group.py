"""Multiphase phase-group derating for clean-room studies.

Phase groups are represented as an aggregate phase-current limit:

    available_current_a = healthy_groups * per_group_current_limit_a
                          / (1 + sharing_imbalance_ratio)

The denominator captures the worst-case sharing imbalance across
healthy groups: ``imbalance = 0`` means perfect sharing, ``0.08`` means
the most-loaded group runs 8% above the mean.

The model does not include harmonic subspace decoupling, neutral-shift
voltage vectors, per-phase thermal RC, or controller saturation. It is
only used to bound feasibility under phase-group failures.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .dq_model import MotorParams
from .search import GridSpec


@dataclass(frozen=True)
class PhaseGroupCase:
    """A single phase-group operating case (healthy / faulted / limp)."""

    name: str
    total_groups: int
    healthy_groups: int
    per_group_current_limit_a: float
    sharing_imbalance_ratio: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must be non-empty")
        if self.total_groups <= 0:
            raise ValueError("total_groups must be positive")
        if self.healthy_groups < 0 or self.healthy_groups > self.total_groups:
            raise ValueError("healthy_groups must be in [0, total_groups]")
        if not isfinite(self.per_group_current_limit_a):
            raise ValueError("per_group_current_limit_a must be finite")
        if self.per_group_current_limit_a <= 0:
            raise ValueError("per_group_current_limit_a must be positive")
        if not isfinite(self.sharing_imbalance_ratio):
            raise ValueError("sharing_imbalance_ratio must be finite")
        if self.sharing_imbalance_ratio < 0:
            raise ValueError("sharing_imbalance_ratio must be non-negative")

    @property
    def available_current_a(self) -> float:
        return (
            self.healthy_groups
            * self.per_group_current_limit_a
            / (1.0 + self.sharing_imbalance_ratio)
        )

    @property
    def group_utilization(self) -> float:
        return 1.0 + self.sharing_imbalance_ratio

    @property
    def healthy_group_ratio(self) -> float:
        return self.healthy_groups / self.total_groups


def apply_phase_group_case(
    params: MotorParams, grid: GridSpec, case: PhaseGroupCase
) -> tuple[MotorParams, GridSpec]:
    """Return ``(params, grid)`` clamped to the case's available current.

    The grid is rescaled so that the search never proposes currents
    above ``available_current_a``; the params' ``i_max_a`` is set to
    the same value so feasibility checks line up.
    """
    available = case.available_current_a
    scaled_params = replace(
        params,
        name=f"{params.name}_{case.name}",
        i_max_a=available,
    )
    base_max = max(abs(grid.id_min_a), abs(grid.id_max_a), abs(grid.iq_max_a))
    if base_max <= 0:
        scale = 1.0
    else:
        scale = available / base_max
    scaled_grid = GridSpec(
        id_min_a=grid.id_min_a * scale,
        id_max_a=grid.id_max_a * scale,
        iq_min_a=grid.iq_min_a * scale,
        iq_max_a=grid.iq_max_a * scale,
        step_a=grid.step_a,
    )
    return scaled_params, scaled_grid
