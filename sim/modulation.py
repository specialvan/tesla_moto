"""SVPWM overmodulation parametric helpers for clean-room studies.

The model intentionally stays parametric: it does not reconstruct PWM
waveforms or simulate phase-current ripple. The harmonic, inverter-loss,
and torque-ripple curves below are first-order proxies derived from the
expected qualitative behaviour of SVPWM as ``k_mod`` exits the linear
modulation region (``k_mod`` > 1.0). Real engineering use requires
calibration against measured inverter loss maps and motor THD.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .dq_model import MotorParams


HARMONIC_RATIO_PER_K = 1.8
INVERTER_LOSS_PER_K = 0.16
TORQUE_RIPPLE_PER_K = 2.5


@dataclass(frozen=True)
class ModulationPenalty:
    """Parametric penalties applied at a given over-modulation factor."""

    k_mod: float
    harmonic_current_rms_ratio: float
    inverter_loss_multiplier: float
    torque_ripple_ratio: float


def _validate_k_mod(k_mod: float) -> None:
    if not isfinite(k_mod):
        raise ValueError("k_mod must be finite")
    if k_mod < 1.0:
        raise ValueError("k_mod must be >= 1.0")


def harmonic_current_rms_ratio(k_mod: float) -> float:
    """Linear proxy for the harmonic-current RMS uplift in over-modulation."""
    _validate_k_mod(k_mod)
    return HARMONIC_RATIO_PER_K * (k_mod - 1.0)


def inverter_loss_multiplier(k_mod: float) -> float:
    """Linear proxy for the inverter switching+conduction loss multiplier."""
    _validate_k_mod(k_mod)
    return 1.0 + INVERTER_LOSS_PER_K * (k_mod - 1.0)


def torque_ripple_ratio(k_mod: float) -> float:
    """Linear proxy for the average-to-peak torque ripple uplift."""
    _validate_k_mod(k_mod)
    return TORQUE_RIPPLE_PER_K * (k_mod - 1.0)


def modulation_penalty(k_mod: float) -> ModulationPenalty:
    """Bundle the three parametric penalty curves for a given k_mod."""
    return ModulationPenalty(
        k_mod=k_mod,
        harmonic_current_rms_ratio=harmonic_current_rms_ratio(k_mod),
        inverter_loss_multiplier=inverter_loss_multiplier(k_mod),
        torque_ripple_ratio=torque_ripple_ratio(k_mod),
    )


def with_modulation_factor(params: MotorParams, k_mod: float) -> MotorParams:
    """Return MotorParams whose svpwm_linear_vmax_factor has been multiplied
    by ``k_mod``. The base ``vdc_v`` is unchanged; only the usable peak
    fundamental voltage budget grows.
    """
    _validate_k_mod(k_mod)
    return replace(
        params,
        name=f"{params.name}_kmod{k_mod:.2f}",
        svpwm_linear_vmax_factor=params.svpwm_linear_vmax_factor * k_mod,
    )
