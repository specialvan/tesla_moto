"""Equivalent-flux model for hybrid-excitation controllable-flux motors."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .dq_model import MotorParams


@dataclass(frozen=True)
class HybridExcitationSpec:
    kf_wb_per_a: float
    field_resistance_ohm: float

    def validate(self) -> None:
        if not isfinite(self.kf_wb_per_a) or self.kf_wb_per_a <= 0.0:
            raise ValueError("kf_wb_per_a must be positive and finite")
        if not isfinite(self.field_resistance_ohm) or self.field_resistance_ohm <= 0.0:
            raise ValueError("field_resistance_ohm must be positive and finite")


def params_with_field_current(
    params: MotorParams, spec: HybridExcitationSpec, field_current_a: float
) -> MotorParams:
    spec.validate()
    if not isfinite(field_current_a):
        raise ValueError("field_current_a must be finite")
    effective_psi = params.psi_f_wb + spec.kf_wb_per_a * field_current_a
    if effective_psi <= 0.0:
        raise ValueError("field_current_a drives effective flux non-positive")
    return MotorParams(
        name=f"{params.name}_if_{field_current_a:.1f}",
        pole_pairs=params.pole_pairs,
        rs_ohm=params.rs_ohm,
        ld_h=params.ld_h,
        lq_h=params.lq_h,
        psi_f_wb=effective_psi,
        vdc_v=params.vdc_v,
        i_max_a=params.i_max_a,
        speed_max_rpm=params.speed_max_rpm,
        torque_target_nm=params.torque_target_nm,
        temperature_c=params.temperature_c,
        svpwm_linear_vmax_factor=params.svpwm_linear_vmax_factor,
    )


def field_loss_w(spec: HybridExcitationSpec, field_current_a: float) -> float:
    spec.validate()
    if not isfinite(field_current_a):
        raise ValueError("field_current_a must be finite")
    return field_current_a * field_current_a * spec.field_resistance_ohm
