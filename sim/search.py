"""Grid-search helpers for v1 linear dq operating-point scans."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor, isfinite
from typing import Iterable

from .dq_model import (
    MotorParams,
    copper_loss_w,
    current_mag_a,
    torque_nm,
    voltage_mag_v,
)


@dataclass(frozen=True)
class GridSpec:
    """Current grid definition in phase-peak amperes."""

    id_min_a: float
    id_max_a: float
    iq_min_a: float
    iq_max_a: float
    step_a: float

    @staticmethod
    def from_dict(data: dict[str, float]) -> "GridSpec":
        required = ["id_min_a", "id_max_a", "iq_min_a", "iq_max_a", "step_a"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing grid fields: {', '.join(missing)}")
        grid = GridSpec(
            id_min_a=float(data["id_min_a"]),
            id_max_a=float(data["id_max_a"]),
            iq_min_a=float(data["iq_min_a"]),
            iq_max_a=float(data["iq_max_a"]),
            step_a=float(data["step_a"]),
        )
        grid.validate()
        return grid

    def validate(self) -> None:
        values = {
            "id_min_a": self.id_min_a,
            "id_max_a": self.id_max_a,
            "iq_min_a": self.iq_min_a,
            "iq_max_a": self.iq_max_a,
            "step_a": self.step_a,
        }
        non_finite = [name for name, value in values.items() if not isfinite(value)]
        if non_finite:
            raise ValueError(f"Grid values must be finite: {', '.join(non_finite)}")
        if self.id_min_a > self.id_max_a:
            raise ValueError("id_min_a must be <= id_max_a")
        if self.iq_min_a > self.iq_max_a:
            raise ValueError("iq_min_a must be <= iq_max_a")
        if self.step_a <= 0:
            raise ValueError("step_a must be positive")


@dataclass(frozen=True)
class Candidate:
    id_a: float
    iq_a: float
    torque_nm: float
    current_a: float
    voltage_v: float
    voltage_margin_v: float
    current_margin_a: float
    copper_loss_w: float
    feasible: bool


def axis_grid(minimum: float, maximum: float, step: float) -> Iterable[float]:
    """Yield grid values clamped to the configured bounds."""
    values = {"minimum": minimum, "maximum": maximum, "step": step}
    non_finite = [name for name, value in values.items() if not isfinite(value)]
    if non_finite:
        raise ValueError(f"axis_grid values must be finite: {', '.join(non_finite)}")
    if minimum > maximum:
        raise ValueError("axis_grid minimum must be <= maximum")
    if step <= 0:
        raise ValueError("axis_grid step must be positive")

    count = floor((maximum - minimum) / step)
    for index in range(count + 1):
        yield minimum + index * step
    last = minimum + count * step
    if last < maximum:
        yield maximum


def current_grid(grid: GridSpec) -> Iterable[tuple[float, float]]:
    for id_a in axis_grid(grid.id_min_a, grid.id_max_a, grid.step_a):
        for iq_a in axis_grid(grid.iq_min_a, grid.iq_max_a, grid.step_a):
            yield id_a, iq_a


def make_candidate(
    params: MotorParams, id_a: float, iq_a: float, omega_e: float
) -> Candidate:
    torque = torque_nm(params, id_a, iq_a)
    current = current_mag_a(id_a, iq_a)
    voltage = voltage_mag_v(params, id_a, iq_a, omega_e)
    return Candidate(
        id_a=id_a,
        iq_a=iq_a,
        torque_nm=torque,
        current_a=current,
        voltage_v=voltage,
        voltage_margin_v=params.vmax_v - voltage,
        current_margin_a=params.imax_a - current,
        copper_loss_w=copper_loss_w(params, id_a, iq_a),
        feasible=current <= params.imax_a and voltage <= params.vmax_v,
    )


def find_min_current_for_torque(
    params: MotorParams,
    omega_e: float,
    target_torque_nm: float,
    grid: GridSpec,
) -> Candidate | None:
    """Find the feasible grid point with minimum current and target torque reached."""
    best: Candidate | None = None
    best_key: tuple[float, float] | None = None
    for id_a, iq_a in current_grid(grid):
        candidate = make_candidate(params, id_a, iq_a, omega_e)
        if not candidate.feasible or candidate.torque_nm < target_torque_nm:
            continue
        key = (candidate.current_a, abs(candidate.torque_nm - target_torque_nm))
        if best_key is None or key < best_key:
            best = candidate
            best_key = key
    return best


def find_max_torque_feasible(
    params: MotorParams, omega_e: float, grid: GridSpec
) -> Candidate | None:
    """Find the feasible grid point with maximum torque at a speed."""
    best: Candidate | None = None
    for id_a, iq_a in current_grid(grid):
        candidate = make_candidate(params, id_a, iq_a, omega_e)
        if not candidate.feasible:
            continue
        if best is None or candidate.torque_nm > best.torque_nm:
            best = candidate
    return best


def find_id_zero_candidate(
    params: MotorParams, omega_e: float, target_torque_nm: float, grid: GridSpec
) -> Candidate | None:
    """Find an id=0 feasible point that reaches target torque with least overshoot."""
    best: Candidate | None = None
    best_error: float | None = None
    for iq_a in axis_grid(grid.iq_min_a, grid.iq_max_a, grid.step_a):
        candidate = make_candidate(params, 0.0, iq_a, omega_e)
        if not candidate.feasible or candidate.torque_nm < target_torque_nm:
            continue
        error = abs(candidate.torque_nm - target_torque_nm)
        if best_error is None or error < best_error:
            best = candidate
            best_error = error
    return best
