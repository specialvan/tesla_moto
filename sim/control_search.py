from __future__ import annotations

from dataclasses import asdict, dataclass
from math import inf, isfinite, sqrt
from typing import Iterable

from sim.dq_model import MotorParams, copper_loss, current_magnitude, voltage_magnitude


@dataclass(frozen=True)
class SearchResult:
    id_a: float
    iq_a: float
    torque_nm: float
    current_a: float
    voltage_v: float
    voltage_margin_v: float
    current_margin_a: float
    copper_loss_w: float
    feasible: bool
    mode: str

    def to_dict(self) -> dict[str, float | bool | str | None]:
        data = asdict(self)
        return {
            key: None if isinstance(value, float) and not isfinite(value) else value
            for key, value in data.items()
        }


def _empty_result(mode: str) -> SearchResult:
    return SearchResult(
        id_a=0.0,
        iq_a=0.0,
        torque_nm=0.0,
        current_a=0.0,
        voltage_v=inf,
        voltage_margin_v=-inf,
        current_margin_a=0.0,
        copper_loss_w=0.0,
        feasible=False,
        mode=mode,
    )


def current_grid(i_max_a: float, step_a: float) -> Iterable[tuple[float, float]]:
    if step_a <= 0.0:
        raise ValueError("current_step_a must be positive")
    steps = int(i_max_a // step_a)
    for id_index in range(-steps, 1):
        id_a = id_index * step_a
        for iq_index in range(0, steps + 1):
            iq_a = iq_index * step_a
            if current_magnitude(id_a, iq_a) <= i_max_a + 1e-9:
                yield id_a, iq_a


def make_result(
    params: MotorParams,
    id_a: float,
    iq_a: float,
    mechanical_speed_rpm: float,
    mode: str,
) -> SearchResult:
    omega_e = params.mechanical_to_electrical_rad_s(mechanical_speed_rpm)
    vd_v = params.voltage_d(id_a, iq_a, omega_e)
    vq_v = params.voltage_q(id_a, iq_a, omega_e)
    current_a = current_magnitude(id_a, iq_a)
    voltage_v = voltage_magnitude(vd_v, vq_v)
    torque_nm = params.torque_nm(id_a, iq_a)
    return SearchResult(
        id_a=id_a,
        iq_a=iq_a,
        torque_nm=torque_nm,
        current_a=current_a,
        voltage_v=voltage_v,
        voltage_margin_v=params.vmax_phase_v - voltage_v,
        current_margin_a=params.i_max_a - current_a,
        copper_loss_w=copper_loss(current_a / sqrt(2.0), params.rs_ohm),
        feasible=current_a <= params.i_max_a + 1e-9
        and voltage_v <= params.vmax_phase_v + 1e-9,
        mode=mode,
    )


def mtpa_grid_search(
    params: MotorParams, target_torque_nm: float, current_step_a: float
) -> SearchResult:
    best: SearchResult | None = None
    best_score = inf
    for id_a, iq_a in current_grid(params.i_max_a, current_step_a):
        result = make_result(params, id_a, iq_a, mechanical_speed_rpm=0.0, mode="mtpa")
        if result.torque_nm < target_torque_nm:
            continue
        score = result.current_a + abs(result.torque_nm - target_torque_nm) * 0.01
        if score < best_score:
            best = result
            best_score = score
    return best if best is not None else _empty_result("mtpa")


def field_weakening_search(
    params: MotorParams,
    target_torque_nm: float,
    mechanical_speed_rpm: float,
    current_step_a: float,
) -> SearchResult:
    best: SearchResult | None = None
    best_score = inf
    for id_a, iq_a in current_grid(params.i_max_a, current_step_a):
        result = make_result(
            params, id_a, iq_a, mechanical_speed_rpm, mode="field_weakening"
        )
        if not result.feasible or result.torque_nm < target_torque_nm:
            continue
        score = result.current_a + abs(result.torque_nm - target_torque_nm) * 0.01
        if score < best_score:
            best = result
            best_score = score
    return best if best is not None else _empty_result("field_weakening")


def mtpv_grid_search(
    params: MotorParams, mechanical_speed_rpm: float, current_step_a: float
) -> SearchResult:
    best: SearchResult | None = None
    for id_a, iq_a in current_grid(params.i_max_a, current_step_a):
        result = make_result(params, id_a, iq_a, mechanical_speed_rpm, mode="mtpv")
        if not result.feasible:
            continue
        if best is None or result.torque_nm > best.torque_nm:
            best = result
    return best if best is not None else _empty_result("mtpv")
