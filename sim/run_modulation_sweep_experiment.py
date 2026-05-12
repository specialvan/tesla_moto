"""Run EXP-005: explicit SVPWM voltage-utilization and overmodulation sweep."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dq_model import mechanical_rpm_to_electrical_rad_per_second
from .modulation_sweep import modulation_penalty, params_with_modulation_factor
from .run_linear_dq_experiment import load_params, speed_grid
from .search import find_min_current_for_torque

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_005_modulation_factor"

K_MOD_VALUES = [1.0, 1.04, 1.08, 1.12]


def _target_max_speed_rpm(
    k_params: Any,
    grid: Any,
    speed_step_rpm: float,
) -> tuple[float | None, float | None, float | None]:
    target_rows: list[tuple[float, float, float]] = []
    for speed_rpm in speed_grid(k_params.speed_max_rpm, speed_step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, k_params.pole_pairs
        )
        candidate = find_min_current_for_torque(
            k_params, omega_e, k_params.torque_target_nm, grid
        )
        if candidate is not None:
            target_rows.append(
                (speed_rpm, candidate.voltage_margin_v, candidate.copper_loss_w)
            )
    if not target_rows:
        return None, None, None
    speed_rpm, voltage_margin_v, copper_loss_w = max(
        target_rows, key=lambda row: row[0]
    )
    return speed_rpm, voltage_margin_v, copper_loss_w


def run(speed_step_rpm: float | None = None) -> dict[str, Any]:
    base_params, raw_params, grid = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if speed_step_rpm is None:
        speed_step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))

    rows: list[dict[str, Any]] = []
    for k_mod in K_MOD_VALUES:
        k_params = params_with_modulation_factor(base_params, k_mod)
        target_max_speed_rpm, voltage_margin_v, copper_loss_w = _target_max_speed_rpm(
            k_params, grid, speed_step_rpm
        )
        penalty = modulation_penalty(k_mod)
        loss_multiplier = penalty["inverter_loss_multiplier"]
        weighted_loss_w = (
            None if copper_loss_w is None else copper_loss_w * loss_multiplier
        )
        score = (
            -1_000_000.0
            if target_max_speed_rpm is None
            else target_max_speed_rpm
            - 1500.0 * penalty["harmonic_current_rms_ratio"]
            - 0.01 * float(weighted_loss_w or 0.0)
        )
        rows.append(
            {
                "k_mod": k_mod,
                "svpwm_vmax_factor": k_params.svpwm_linear_vmax_factor,
                "vmax_v": k_params.vmax_v,
                "target_max_speed_rpm": target_max_speed_rpm,
                "target_boundary_voltage_margin_v": voltage_margin_v,
                "target_boundary_copper_loss_w": copper_loss_w,
                "harmonic_current_rms_ratio": penalty["harmonic_current_rms_ratio"],
                "inverter_loss_multiplier": loss_multiplier,
                "torque_ripple_ratio": penalty["torque_ripple_ratio"],
                "tradeoff_score": score,
            }
        )

    csv_path = OUTPUT_DIR / "modulation_sweep_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best_tradeoff = max(rows, key=lambda row: float(row["tradeoff_score"]))
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
        "best_tradeoff": best_tradeoff,
        "row_count": len(rows),
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
