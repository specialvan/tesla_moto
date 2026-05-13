"""Winding-reconfiguration parameter scaling for clean-room studies.

The model assumes a series-parallel reconfigurable winding family. We
derive electrical parameters from three scalar scales:

* ``turns_scale``: relative number of effective series turns
  (``Ke``, ``psi_f``, and back-EMF scale linearly; inductance scales by
  ``turns_scale**2``).
* ``resistance_scale``: relative phase resistance
  (often ``turns_scale**2 / parallel_paths``).
* ``current_limit_scale``: relative phase current limit imposed by the
  inverter / connector / cabling (``parallel_paths`` typically lifts this).

This proxy does not model contactor arc, switching transients,
insulation stress, circulating currents, or thermal sharing between
parallel paths. It is only used to rank candidate winding
configurations before a real switching design.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .dq_model import MotorParams


@dataclass(frozen=True)
class WindingConfig:
    """A symbolic reconfiguration setting (e.g., ``series`` / ``parallel``)."""

    name: str
    turns_scale: float
    resistance_scale: float
    current_limit_scale: float

    def __post_init__(self) -> None:
        scales = {
            "turns_scale": self.turns_scale,
            "resistance_scale": self.resistance_scale,
            "current_limit_scale": self.current_limit_scale,
        }
        for key, value in scales.items():
            if not isfinite(value):
                raise ValueError(f"{key} must be finite")
            if value <= 0:
                raise ValueError(f"{key} must be positive")
        if not self.name:
            raise ValueError("name must be non-empty")


def apply_winding_config(
    params: MotorParams, config: WindingConfig
) -> MotorParams:
    """Return MotorParams scaled to the given winding configuration."""
    turns_sq = config.turns_scale * config.turns_scale
    return replace(
        params,
        name=f"{params.name}_{config.name}",
        rs_ohm=params.rs_ohm * config.resistance_scale,
        ld_h=params.ld_h * turns_sq,
        lq_h=params.lq_h * turns_sq,
        psi_f_wb=params.psi_f_wb * config.turns_scale,
        i_max_a=params.i_max_a * config.current_limit_scale,
    )
