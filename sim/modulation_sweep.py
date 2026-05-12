"""Explicit voltage-utilization sweep helpers for SVPWM overmodulation."""

from __future__ import annotations

from math import isfinite

from .dq_model import MotorParams


def params_with_modulation_factor(params: MotorParams, k_mod: float) -> MotorParams:
    """Return motor params with the phase-voltage limit scaled by k_mod."""
    if not isfinite(k_mod) or k_mod <= 0.0:
        raise ValueError("k_mod must be positive and finite")

    return MotorParams(
        name=f"{params.name}_kmod_{k_mod:.3f}",
        pole_pairs=params.pole_pairs,
        rs_ohm=params.rs_ohm,
        ld_h=params.ld_h,
        lq_h=params.lq_h,
        psi_f_wb=params.psi_f_wb,
        vdc_v=params.vdc_v,
        i_max_a=params.i_max_a,
        speed_max_rpm=params.speed_max_rpm,
        torque_target_nm=params.torque_target_nm,
        temperature_c=params.temperature_c,
        svpwm_linear_vmax_factor=params.svpwm_linear_vmax_factor * k_mod,
    )


def modulation_penalty(k_mod: float) -> dict[str, float]:
    """Estimate incremental harmonic current and inverter loss for k_mod > 1."""
    if not isfinite(k_mod) or k_mod <= 0.0:
        raise ValueError("k_mod must be positive and finite")

    overmod_depth = max(0.0, k_mod - 1.0)
    harmonic_current_rms_ratio = 1.8 * overmod_depth
    inverter_loss_multiplier = 1.0 + 4.0 * overmod_depth * overmod_depth
    torque_ripple_ratio = 2.5 * overmod_depth
    return {
        "overmod_depth": overmod_depth,
        "harmonic_current_rms_ratio": harmonic_current_rms_ratio,
        "inverter_loss_multiplier": inverter_loss_multiplier,
        "torque_ripple_ratio": torque_ripple_ratio,
    }
