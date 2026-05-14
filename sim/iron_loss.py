"""Iron loss models for electrical machines.

This module implements iron loss (core loss) estimation for IPMSM motors using
two standard approaches:

1. **Bertotti model** (three-term):
   - P_hyst = k_hyst * f * B^2       (hysteresis)
   - P_eddy = k_eddy * f^2 * B^2    (eddy current)
   - P_excess = k_excess * f^1.5 * B^2  (excess/anhysteretic)

2. **Steinmetz empirical equation** (single-term, widely used in industry):
   - P_fe = k * f^α * B^β

The dq model provides per-phase RMS flux density estimates from lambda_d/lambda_q.
Iron loss is combined with copper loss for efficiency estimation.

References:
- Bertotti, G. (1998). "General properties of power losses in soft
  ferromagnetic materials." IEEE Trans. Magn., 34(5), 2872-2878.
- Ion, O. (2013). "Losses in AC motors." ABB Review, 3, 34-41.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import NamedTuple


@dataclass(frozen=True)
class BertottiCoeffs:
    """Bertotti iron loss coefficients for a specific lamination material.

    Attributes
    ----------
    k_hyst:
        Hysteresis coefficient (W·s/T^2 per m^3).
        Typical values: 0.02 - 0.10 for SiFe steels.
    k_eddy:
        Eddy current coefficient (W·s^2/T^2 per m^3).
        Typical values: 0.001 - 0.01.
    k_excess:
        Excess loss coefficient (W-s^(1.5)/T^2 per m^3).
        Typical values: 0.001 - 0.008.
    freq_max_hz:
        Maximum frequency for which coefficients are valid.
    """

    k_hyst: float
    k_eddy: float
    k_excess: float
    freq_max_hz: float = 400.0

    def __post_init__(self) -> None:
        for name, value in {
            "k_hyst": self.k_hyst,
            "k_eddy": self.k_eddy,
            "k_excess": self.k_excess,
        }.items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.freq_max_hz <= 0:
            raise ValueError("freq_max_hz must be positive")

    def validate(self) -> None:
        pass  # Validation is done in __post_init__


@dataclass(frozen=True)
class SteinmetzCoeffs:
    """Steinmetz iron loss coefficients.

    Attributes
    ----------
    k_st:
        Steinmetz coefficient (W/m^3).
        Typical values: 0.01 - 0.1 for SiFe.
    alpha:
        Frequency exponent. Typically 1.2 - 1.6.
    beta:
        Flux density exponent. Typically 1.6 - 2.2.
    """

    k_st: float
    alpha: float
    beta: float

    def __post_init__(self) -> None:
        for name, value in {
            "k_st": self.k_st,
            "alpha": self.alpha,
            "beta": self.beta,
        }.items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.k_st <= 0:
            raise ValueError("k_st must be positive")
        if not (0.5 <= self.alpha <= 3.0):
            raise ValueError("alpha must be in [0.5, 3.0]")
        if not (1.0 <= self.beta <= 4.0):
            raise ValueError("beta must be in [1.0, 4.0]")

    def validate(self) -> None:
        pass  # Validation is done in __post_init__


# Default material coefficients for clean-room studies
DEFAULT_BERTOTTI = BertottiCoeffs(k_hyst=0.04, k_eddy=0.004, k_excess=0.003)
DEFAULT_STEINMETZ = SteinmetzCoeffs(k_st=0.03, alpha=1.4, beta=2.0)


class IronLossComponents(NamedTuple):
    """Separated iron loss components (W per phase, then total)."""

    hysteresis_w: float
    eddy_current_w: float
    excess_w: float
    total_per_phase_w: float

    @property
    def total_three_phase_w(self) -> float:
        return 3.0 * self.total_per_phase_w


def flux_density_from_lambda(lambda_wb: float, core_radius_m: float) -> float:
    """Estimate peak flux density B from flux linkage and core geometry.

    B_peak = lambda_peak / (sqrt(2) * A_core)

    Args:
        lambda_wb: Flux linkage in Weber (peak, amplitude-invariant dq).
        core_radius_m: Effective core radius for area estimation.

    Returns:
        Peak flux density in Tesla.
    """
    if not isfinite(lambda_wb) or not isfinite(core_radius_m):
        raise ValueError("lambda_wb and core_radius_m must be finite")
    if core_radius_m <= 0:
        raise ValueError("core_radius_m must be positive")
    # B_peak = lambda_peak / (sqrt(2) * A), A = pi * r^2
    area_m2 = 3.14159265359 * core_radius_m * core_radius_m
    if area_m2 <= 0:
        raise ValueError("core_radius_m must be positive")
    return abs(lambda_wb) / (sqrt(2.0) * area_m2)


def bertotti_iron_loss_per_phase(
    lambda_d_wb: float,
    lambda_q_wb: float,
    freq_hz: float,
    coeffs: BertottiCoeffs,
    core_radius_m: float = 0.05,
) -> IronLossComponents:
    """Compute three-phase iron loss using the Bertotti model.

    The flux density is estimated from both d and q axis flux linkages.
    The fundamental frequency is used for all three terms.

    Args:
        lambda_d_wb: d-axis flux linkage (Weber, peak/amplitude-invariant).
        lambda_q_wb: q-axis flux linkage (Weber, peak/amplitude-invariant).
        freq_hz: Electrical frequency (Hz).
        coeffs: Bertotti loss coefficients for the lamination material.
        core_radius_m: Effective core radius for B estimation.

    Returns:
        IronLossComponents with per-phase and total losses.
    """
    coeffs.validate()
    if not isfinite(freq_hz):
        raise ValueError("freq_hz must be finite")
    if freq_hz <= 0:
        raise ValueError("freq_hz must be positive")

    # Use magnitude of fundamental flux density
    lambda_mag = sqrt(lambda_d_wb * lambda_d_wb + lambda_q_wb * lambda_q_wb)
    b_peak = flux_density_from_lambda(lambda_mag, core_radius_m)

    # Bertotti terms (W/kg, scaled to per-phase machine volume proxy)
    p_hyst = coeffs.k_hyst * freq_hz * b_peak * b_peak
    p_eddy = coeffs.k_eddy * freq_hz * freq_hz * b_peak * b_peak
    p_excess = coeffs.k_excess * sqrt(freq_hz) * freq_hz * b_peak * b_peak

    total = p_hyst + p_eddy + p_excess
    return IronLossComponents(
        hysteresis_w=p_hyst,
        eddy_current_w=p_eddy,
        excess_w=p_excess,
        total_per_phase_w=total,
    )


def steinmetz_iron_loss_per_phase(
    lambda_d_wb: float,
    lambda_q_wb: float,
    freq_hz: float,
    coeffs: SteinmetzCoeffs,
    core_radius_m: float = 0.05,
) -> IronLossComponents:
    """Compute iron loss using the Steinmetz empirical equation.

    Args:
        lambda_d_wb: d-axis flux linkage (Weber, peak/amplitude-invariant).
        lambda_q_wb: q-axis flux linkage (Weber, peak/amplitude-invariant).
        freq_hz: Electrical frequency (Hz).
        coeffs: Steinmetz loss coefficients.
        core_radius_m: Effective core radius for B estimation.

    Returns:
        IronLossComponents with hysteresis_w containing the Steinmetz total.
    """
    coeffs.validate()
    if not isfinite(freq_hz):
        raise ValueError("freq_hz must be finite")
    if freq_hz <= 0:
        raise ValueError("freq_hz must be positive")

    lambda_mag = sqrt(lambda_d_wb * lambda_d_wb + lambda_q_wb * lambda_q_wb)
    b_peak = flux_density_from_lambda(lambda_mag, core_radius_m)

    # Steinmetz equation: P = k * f^alpha * B^beta
    p_st = coeffs.k_st * (freq_hz ** coeffs.alpha) * (b_peak ** coeffs.beta)

    # Map to Bertotti-style structure
    return IronLossComponents(
        hysteresis_w=p_st,  # Total Steinmetz loss
        eddy_current_w=0.0,
        excess_w=0.0,
        total_per_phase_w=p_st,
    )


def iron_loss_from_id_iq(
    id_a: float,
    iq_a: float,
    ld_h: float,
    lq_h: float,
    psi_f_wb: float,
    freq_hz: float,
    coeffs: BertottiCoeffs | SteinmetzCoeffs | None = None,
    use_steinmetz: bool = False,
    core_radius_m: float = 0.05,
) -> IronLossComponents:
    """Estimate iron loss from dq currents and machine parameters.

    This function computes flux linkages from id/iq, then derives
    the iron loss. For linear models, lambda_d = ld*id + psi_f,
    lambda_q = lq*iq.

    Args:
        id_a: d-axis current (A, phase-peak).
        iq_a: q-axis current (A, phase-peak).
        ld_h: d-axis inductance (H).
        lq_h: q-axis inductance (H).
        psi_f_wb: Permanent magnet flux linkage (Wb).
        freq_hz: Electrical frequency (Hz).
        coeffs: Loss coefficients (Bertotti or Steinmetz). Defaults to DEFAULT_BERTOTTI.
        use_steinmetz: Use Steinmetz model instead of Bertotti.
        core_radius_m: Effective core radius.

    Returns:
        IronLossComponents with per-phase and total iron losses.
    """
    if coeffs is None:
        coeffs = DEFAULT_STEINMETZ if use_steinmetz else DEFAULT_BERTOTTI

    # Linear flux linkage estimation
    lambda_d = ld_h * id_a + psi_f_wb
    lambda_q = lq_h * iq_a

    if use_steinmetz and isinstance(coeffs, SteinmetzCoeffs):
        return steinmetz_iron_loss_per_phase(
            lambda_d, lambda_q, freq_hz, coeffs, core_radius_m
        )
    elif isinstance(coeffs, BertottiCoeffs):
        return bertotti_iron_loss_per_phase(
            lambda_d, lambda_q, freq_hz, coeffs, core_radius_m
        )
    else:
        raise TypeError("coeffs must be BertottiCoeffs or SteinmetzCoeffs")


def combined_losses(
    iron_loss: IronLossComponents,
    copper_loss_w: float,
) -> tuple[float, float]:
    """Combine iron and copper losses and compute efficiency.

    Args:
        iron_loss: Iron loss components from bertotti_iron_loss_per_phase.
        copper_loss_w: Total three-phase copper loss (W).

    Returns:
        (total_loss_w, efficiency_percent)
    """
    if not isfinite(copper_loss_w) or copper_loss_w < 0:
        raise ValueError("copper_loss_w must be non-negative and finite")

    total_iron = iron_loss.total_three_phase_w
    total_loss = total_iron + copper_loss_w
    return total_loss, total_iron / total_loss if total_loss > 0 else 0.0