"""Run EXP-007: hybrid-excitation equivalent field-current sweep."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dq_model import mechanical_rpm_to_electrical_rad_per_second
from .hybrid_excitation import (
    HybridExcitationSpec,
    field_loss_w,
    params_with_field_current,
)
from .run_linear_dq_experiment import load_params, speed_grid
from .search import find_min_current_for_torque

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_007_hybrid_excitation"

FIELD_CURRENT_A = [-60.0, -40.0, -20.0, 0.0, 20.0]
SPEC = HybridExcitationSpec(kf_wb_per_a=0.00018, field_resistance_ohm=1.2)


def _target_boundary(
    params: Any, grid: Any, speed_step_rpm: float
) -> tuple[float | None, float | None, float | None]:
    reachable: list[tuple[float, float, float]] = []
    for speed_rpm in speed_grid(params.speed_max_rpm, speed_step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        candidate = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid
        )
        if candidate is not None:
            reachable.append((speed_rpm, candidate.current_a, candidate.copper_loss_w))
    if not reachable:
        return None, None, None
    return max(reachable, key=lambda row: row[0])


def run(speed_step_rpm: float | None = None) -> dict[str, Any]:
    base_params, raw_params, grid = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if speed_step_rpm is None:
        speed_step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))

    rows: list[dict[str, Any]] = []
    for field_current_a in FIELD_CURRENT_A:
        params = params_with_field_current(base_params, SPEC, field_current_a)
        target_max_speed_rpm, boundary_current_a, copper_loss_w = _target_boundary(
            params, grid, speed_step_rpm
        )
        excitation_loss_w = field_loss_w(SPEC, field_current_a)
        combined_loss_w = (
            None if copper_loss_w is None else copper_loss_w + excitation_loss_w
        )
        tradeoff_score = (
            -1_000_000.0
            if target_max_speed_rpm is None
            else target_max_speed_rpm - 0.01 * float(combined_loss_w or 0.0)
        )
        rows.append(
            {
                "field_current_a": field_current_a,
                "effective_psi_f_wb": params.psi_f_wb,
                "target_max_speed_rpm": target_max_speed_rpm,
                "boundary_current_a": boundary_current_a,
                "boundary_copper_loss_w": copper_loss_w,
                "field_loss_w": excitation_loss_w,
                "combined_loss_w": combined_loss_w,
                "tradeoff_score": tradeoff_score,
            }
        )

    csv_path = OUTPUT_DIR / "hybrid_excitation_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best_tradeoff = max(rows, key=lambda row: float(row["tradeoff_score"]))
    summary = {
        "experiment": "exp_007_hybrid_excitation",
        "parameter_source": "illustrative_clean_room_baseline_plus_equivalent_field_axis",
        "engineering_validated": False,
        "model_scope": "linear_dq_with_equivalent_field_excitation",
        "model_limitations": [
            "field axis is represented as an equivalent psi_f shift",
            "no field winding inductance, current-loop dynamics, or thermal coupling",
            "no rotor leakage, saturation, rectifier loss, or brushless exciter model",
        ],
        "field_model": {
            "kf_wb_per_a": SPEC.kf_wb_per_a,
            "field_resistance_ohm": SPEC.field_resistance_ohm,
        },
        "sweep_axes": {
            "field_current_a": FIELD_CURRENT_A,
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
