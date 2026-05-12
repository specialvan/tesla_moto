"""Variable permanent-magnet flux state helpers for clean-room studies."""

from __future__ import annotations

from dataclasses import replace
from math import isfinite

from .dq_model import MotorParams


def with_flux_scale(
    params: MotorParams, flux_scale: float, name_suffix: str
) -> MotorParams:
    """Return a copied MotorParams with scaled psi_f for virtual flux-state studies."""
    if not isfinite(flux_scale):
        raise ValueError("flux_scale must be finite")
    if flux_scale <= 0:
        raise ValueError("flux_scale must be positive")
    return replace(
        params,
        name=f"{params.name}_{name_suffix}",
        psi_f_wb=params.psi_f_wb * flux_scale,
    )
