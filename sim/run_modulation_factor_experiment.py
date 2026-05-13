"""Run EXP-005: SVPWM modulation-factor (k_mod) sweep.

The experiment scans ``k_mod`` from the linear region (``1.0``) into the
over-modulation region and measures, for each value, the boundary at
which the motor can still reach the target torque under the augmented
voltage budget. Harmonic / inverter / torque-ripple penalties are
applied as transparent first-order proxies; see ``sim/modulation.py``
for the curves.
"""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .modulation import (
    ModulationPenalty,
    harmonic_current_rms_ratio,
    inverter_loss_multiplier,
    modulation_penalty,
    torque_ripple_ratio,
    with_modulation_factor,
)
from .run_linear_dq_experiment import load_params, speed_grid
from .search import Candidate, GridSpec, find_min_current_for_torque

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_005_modulation_factor"

K_MOD_VALUES = [1.0, 1.04, 1.08, 1.12]
DEFAULT_SPEED_STEP_RPM = 1000.0
HARMONIC_SPEED_PENALTY = 0.215
LOSS_SPEED_PENALTY = 0.01


def _max_reachable(
    params: MotorParams, grid: GridSpec, speed_step_rpm: float
) -> tuple[float | None, Candidate | None]:
    best_speed: float | None = None
    best_candidate: Candidate | None = None
    for speed_rpm in speed_grid(params.speed_max_rpm, speed_step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        candidate = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid
        )
        if candidate is None:
            continue
        if best_speed is None or speed_rpm > best_speed:
            best_speed = speed_rpm
            best_candidate = candidate
    return best_speed, best_candidate


def evaluate_k_mod(
    base: MotorParams, grid: GridSpec, k_mod: float, speed_step_rpm: float
) -> dict[str, Any]:
    params = with_modulation_factor(base, k_mod)
    penalty = modulation_penalty(k_mod)
    speed_rpm, candidate = _max_reachable(params, grid, speed_step_rpm)

    copper_loss = float(candidate.copper_loss_w) if candidate is not None else None
    voltage_margin = (
        float(candidate.voltage_margin_v) if candidate is not None else None
    )

    if speed_rpm is None or copper_loss is None:
        score: float | None = None
    else:
        score = (
            speed_rpm
            - LOSS_SPEED_PENALTY * copper_loss * penalty.inverter_loss_multiplier
            - HARMONIC_SPEED_PENALTY
            * penalty.harmonic_current_rms_ratio
            * speed_rpm
        )

    return {
        "k_mod": k_mod,
        "svpwm_vmax_factor": params.svpwm_linear_vmax_factor,
        "vmax_v": params.vmax_v,
        "target_max_speed_rpm": speed_rpm,
        "target_boundary_voltage_margin_v": voltage_margin,
        "target_boundary_copper_loss_w": copper_loss,
        "harmonic_current_rms_ratio": penalty.harmonic_current_rms_ratio,
        "inverter_loss_multiplier": penalty.inverter_loss_multiplier,
        "torque_ripple_ratio": penalty.torque_ripple_ratio,
        "tradeoff_score": score,
    }


def run(speed_step_rpm: float | None = None) -> dict[str, Any]:
    base, raw, grid = load_params()
    base = replace(base, name="baseline_ipmsm_v1")  # ensure stable name
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if speed_step_rpm is None:
        speed_step_rpm = DEFAULT_SPEED_STEP_RPM

    rows = [
        evaluate_k_mod(base, grid, k_mod, speed_step_rpm) for k_mod in K_MOD_VALUES
    ]

    csv_path = OUTPUT_DIR / "modulation_sweep_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    feasible_rows = [
        row for row in rows if row["tradeoff_score"] is not None
    ]
    best_row = (
        max(feasible_rows, key=lambda row: float(row["tradeoff_score"]))
        if feasible_rows
        else None
    )

    summary = {
        "experiment": "exp_005_modulation_factor",
        "parameter_source": "illustrative_clean_room_baseline",
        "engineering_validated": False,
        "model_scope": "linear_dq_with_explicit_voltage_utilization_axis",
        "model_limitations": [
            "overmodulation harmonic penalties are parametric estimates",
            "no PWM waveform reconstruction or phase-current ripple simulation",
            "no inverter dead-time, device loss map, or EMI model",
        ],
        "sweep_axes": {
            "k_mod_values": K_MOD_VALUES,
            "speed_step_rpm": speed_step_rpm,
        },
        "scoring": {
            "loss_speed_penalty": LOSS_SPEED_PENALTY,
            "harmonic_speed_penalty": HARMONIC_SPEED_PENALTY,
        },
        "best_tradeoff": best_row,
        "row_count": len(rows),
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


__all__ = [
    "K_MOD_VALUES",
    "DEFAULT_SPEED_STEP_RPM",
    "evaluate_k_mod",
    "run",
]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
