"""Temperature and demagnetization safety helpers for operating-point scans."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .dq_model import MotorParams
from .search import Candidate, GridSpec, current_grid, make_candidate


@dataclass(frozen=True)
class ThermalModel:
    reference_c: float
    copper_alpha_per_c: float
    pm_alpha_per_c: float

    def validate(self) -> None:
        values = {
            "reference_c": self.reference_c,
            "copper_alpha_per_c": self.copper_alpha_per_c,
            "pm_alpha_per_c": self.pm_alpha_per_c,
        }
        invalid = [name for name, value in values.items() if not isfinite(value)]
        if invalid:
            raise ValueError(
                f"ThermalModel values must be finite: {', '.join(invalid)}"
            )


@dataclass(frozen=True)
class DemagLimit:
    points_c_to_id_min_a: list[tuple[float, float]]

    def __post_init__(self) -> None:
        if len(self.points_c_to_id_min_a) < 2:
            raise ValueError("DemagLimit requires at least two points")
        sorted_points = sorted(self.points_c_to_id_min_a)
        if sorted_points != self.points_c_to_id_min_a:
            raise ValueError("DemagLimit points must be sorted by temperature")
        for temperature_c, id_min_a in self.points_c_to_id_min_a:
            if not isfinite(temperature_c) or not isfinite(id_min_a):
                raise ValueError("DemagLimit points must be finite")

    def id_min_allowed(self, temperature_c: float) -> float:
        if not isfinite(temperature_c):
            raise ValueError("temperature_c must be finite")
        points = self.points_c_to_id_min_a
        if temperature_c <= points[0][0]:
            return points[0][1]
        if temperature_c >= points[-1][0]:
            return points[-1][1]

        for (t0, id0), (t1, id1) in zip(points, points[1:]):
            if t0 <= temperature_c <= t1:
                ratio = (temperature_c - t0) / (t1 - t0)
                return id0 + ratio * (id1 - id0)
        raise RuntimeError("unreachable demag interpolation state")


def apply_temperature(
    params: MotorParams, temperature_c: float, thermal_model: ThermalModel
) -> MotorParams:
    thermal_model.validate()
    if not isfinite(temperature_c):
        raise ValueError("temperature_c must be finite")
    delta_c = temperature_c - thermal_model.reference_c
    rs_scale = 1.0 + thermal_model.copper_alpha_per_c * delta_c
    psi_scale = 1.0 + thermal_model.pm_alpha_per_c * delta_c
    if rs_scale <= 0.0 or psi_scale <= 0.0:
        raise ValueError("temperature scaling produced non-positive parameter")
    return replace(
        params,
        rs_ohm=params.rs_ohm * rs_scale,
        psi_f_wb=params.psi_f_wb * psi_scale,
        temperature_c=temperature_c,
    )


def find_min_current_for_torque_with_safety(
    params: MotorParams,
    omega_e: float,
    target_torque_nm: float,
    grid: GridSpec,
    demag_limit: DemagLimit,
) -> Candidate | None:
    id_min_allowed = demag_limit.id_min_allowed(params.temperature_c)
    best: Candidate | None = None
    best_key: tuple[float, float] | None = None
    for id_a, iq_a in current_grid(grid):
        if id_a < id_min_allowed:
            continue
        candidate = make_candidate(params, id_a, iq_a, omega_e)
        if not candidate.feasible or candidate.torque_nm < target_torque_nm:
            continue
        key = (candidate.current_a, abs(candidate.torque_nm - target_torque_nm))
        if best_key is None or key < best_key:
            best = candidate
            best_key = key
    return best
