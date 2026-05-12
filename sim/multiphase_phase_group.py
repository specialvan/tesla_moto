"""Phase-group derating model for multiphase controllable-flux drives."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PhaseGroupCase:
    name: str
    total_groups: int
    healthy_groups: int
    per_group_current_limit_a: float
    sharing_imbalance_ratio: float = 0.0

    def validate(self) -> None:
        if not self.name:
            raise ValueError("phase group case name is required")
        if self.total_groups <= 0:
            raise ValueError("total_groups must be positive")
        if self.healthy_groups <= 0 or self.healthy_groups > self.total_groups:
            raise ValueError("healthy_groups must be in 1..total_groups")
        if (
            not isfinite(self.per_group_current_limit_a)
            or self.per_group_current_limit_a <= 0.0
        ):
            raise ValueError("per_group_current_limit_a must be positive and finite")
        if (
            not isfinite(self.sharing_imbalance_ratio)
            or self.sharing_imbalance_ratio < 0.0
        ):
            raise ValueError("sharing_imbalance_ratio must be non-negative and finite")


def derated_current_limit(case: PhaseGroupCase) -> dict[str, float]:
    case.validate()
    group_utilization = 1.0 + case.sharing_imbalance_ratio
    available_current_a = (
        case.healthy_groups * case.per_group_current_limit_a / group_utilization
    )
    return {
        "available_current_a": available_current_a,
        "group_utilization": group_utilization,
        "healthy_group_ratio": case.healthy_groups / case.total_groups,
    }
