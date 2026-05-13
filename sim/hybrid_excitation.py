"""Hybrid-excitation equivalent-flux helpers for clean-room studies.

The model represents a hybrid PM + wound-field rotor as a virtual
``psi_f`` shift on top of the linear dq model. We do not simulate the
field-winding inductance, current-loop dynamics, brushless exciter, or
rotor leakage. Field-loss is reduced to ``if^2 * Rf`` (steady-state
copper loss in the field circuit). This is purely an architectural
proxy for ranking weak-flux benefits against added field copper loss.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .dq_model import MotorParams


@dataclass(frozen=True)
class HybridExcitationModel:
    """Linear flux-shift coupling for the equivalent psi_f model.

    Attributes
    ----------
    kf_wb_per_a:
        Coupling coefficient between field current ``if`` and the
        equivalent ``psi_f`` shift, in Wb / A.
    field_resistance_ohm:
        Series resistance of the field circuit. Used to compute the
        steady-state field copper loss ``if^2 * Rf``.
    """

    kf_wb_per_a: float
    field_resistance_ohm: float

    def __post_init__(self) -> None:
        for name, value in {
            "kf_wb_per_a": self.kf_wb_per_a,
            "field_resistance_ohm": self.field_resistance_ohm,
        }.items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.field_resistance_ohm <= 0:
            raise ValueError("field_resistance_ohm must be positive")

    def effective_psi_f(self, base_psi_f_wb: float, field_current_a: float) -> float:
        """Return the equivalent ``psi_f`` for the given field current."""
        if not isfinite(base_psi_f_wb) or not isfinite(field_current_a):
            raise ValueError("base_psi_f_wb and field_current_a must be finite")
        return base_psi_f_wb + self.kf_wb_per_a * field_current_a

    def field_loss_w(self, field_current_a: float) -> float:
        """Return the steady-state field copper loss ``if^2 * Rf``."""
        if not isfinite(field_current_a):
            raise ValueError("field_current_a must be finite")
        return field_current_a * field_current_a * self.field_resistance_ohm


def with_field_current(
    params: MotorParams,
    model: HybridExcitationModel,
    field_current_a: float,
) -> MotorParams:
    """Return MotorParams whose ``psi_f_wb`` reflects the field-current shift."""
    if not isfinite(field_current_a):
        raise ValueError("field_current_a must be finite")
    new_psi = model.effective_psi_f(params.psi_f_wb, field_current_a)
    if new_psi <= 0:
        raise ValueError(
            "effective psi_f must remain positive; reduce |field_current_a|"
        )
    return replace(
        params,
        name=f"{params.name}_if{field_current_a:+.0f}",
        psi_f_wb=new_psi,
    )
