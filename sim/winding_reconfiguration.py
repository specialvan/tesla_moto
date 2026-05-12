"""Parameterized winding-configuration model for reconfigurable motors."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from .dq_model import MotorParams


@dataclass(frozen=True)
class WindingConfig:
    name: str
    turns_scale: float
    resistance_scale: float
    current_limit_scale: float

    def validate(self) -> None:
        if not self.name:
            raise ValueError("winding config name is required")
        for field_name, value in {
            "turns_scale": self.turns_scale,
            "resistance_scale": self.resistance_scale,
            "current_limit_scale": self.current_limit_scale,
        }.items():
            if not isfinite(value) or value <= 0.0:
                raise ValueError(f"{field_name} must be positive and finite")


def apply_winding_config(params: MotorParams, config: WindingConfig) -> MotorParams:
    config.validate()
    inductance_scale = config.turns_scale * config.turns_scale
    return MotorParams(
        name=f"{params.name}_{config.name}",
        pole_pairs=params.pole_pairs,
        rs_ohm=params.rs_ohm * config.resistance_scale,
        ld_h=params.ld_h * inductance_scale,
        lq_h=params.lq_h * inductance_scale,
        psi_f_wb=params.psi_f_wb * config.turns_scale,
        vdc_v=params.vdc_v,
        i_max_a=params.i_max_a * config.current_limit_scale,
        speed_max_rpm=params.speed_max_rpm,
        torque_target_nm=params.torque_target_nm,
        temperature_c=params.temperature_c,
        svpwm_linear_vmax_factor=params.svpwm_linear_vmax_factor,
    )


def transition_delta(
    from_point: dict[str, Any], to_point: dict[str, Any]
) -> dict[str, float | None]:
    if from_point["torque_nm"] is None or to_point["torque_nm"] is None:
        torque_delta = None
    else:
        torque_delta = float(to_point["torque_nm"]) - float(from_point["torque_nm"])
    if from_point["current_a"] is None or to_point["current_a"] is None:
        current_delta = None
    else:
        current_delta = float(to_point["current_a"]) - float(from_point["current_a"])
    return {
        "torque_delta_nm": torque_delta,
        "current_delta_a": current_delta,
    }
