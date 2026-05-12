"""Weighted numeric selection helpers for controllable-flux scheme ranking."""

from __future__ import annotations

from math import isfinite


def weighted_score(
    target_max_speed_rpm: float,
    loss_w: float,
    risk_penalty: float,
    weights: dict[str, float],
) -> float:
    for name, value in {
        "target_max_speed_rpm": target_max_speed_rpm,
        "loss_w": loss_w,
        "risk_penalty": risk_penalty,
    }.items():
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")
    required = {"speed", "loss", "risk"}
    if set(weights) != required:
        raise ValueError("weights must contain speed, loss, and risk")
    return (
        weights["speed"] * target_max_speed_rpm
        - weights["loss"] * (loss_w / 1000.0)
        - weights["risk"] * (risk_penalty * 10000.0)
    )
