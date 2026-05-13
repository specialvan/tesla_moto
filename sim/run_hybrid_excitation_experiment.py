"""Run EXP-007: hybrid-excitation field-current sweep.

The experiment scans the equivalent field current ``if`` to compare
weak-flux vs strong-flux operating points against the combined
``copper_loss + field_loss`` cost. The model is an architectural proxy
only; see ``sim/hybrid_excitation.py`` for assumptions.
"""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .hybrid_excitation import HybridExcitationModel, with_field_current
from .run_linear_dq_experiment import load_params, speed_grid
from .search import Candidate, GridSpec, find_min_current_for_torque

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_007_hybrid_excitation"

DEFAULT_FIELD_CURRENTS_A = [-60.0, -40.0, -20.0, 0.0, 20.0]
DEFAULT_SPEED_STEP_RPM = 1000.0
DEFAULT_KF_WB_PER_A = 0.00018
DEFAULT_FIELD_RESISTANCE_OHM = 1.2
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


def evaluate_field_current(
    base: MotorParams,
    grid: GridSpec,
    model: HybridExcitationModel,
    field_current_a: float,
    speed_step_rpm: float,
) -> dict[str, Any]:
    params = with_field_current(base, model, field_current_a)
    speed_rpm, candidate = _max_reachable(params, grid, speed_step_rpm)
    field_loss = model.field_loss_w(field_current_a)

    if candidate is None:
        copper_loss: float | None = None
        boundary_current: float | None = None
        combined_loss: float | None = None
        score: float | None = None
    else:
        copper_loss = float(candidate.copper_loss_w)
        boundary_current = float(candidate.current_a)
        combined_loss = copper_loss + field_loss
        assert speed_rpm is not None
        score = speed_rpm - LOSS_SPEED_PENALTY * combined_loss

    return {
        "field_current_a": field_current_a,
        "effective_psi_f_wb": params.psi_f_wb,
        "target_max_speed_rpm": speed_rpm,
        "boundary_current_a": boundary_current,
        "boundary_copper_loss_w": copper_loss,
        "field_loss_w": field_loss,
        "combined_loss_w": combined_loss,
        "tradeoff_score": score,
    }


def run(
    speed_step_rpm: float | None = None,
    field_currents_a: list[float] | None = None,
    kf_wb_per_a: float | None = None,
    field_resistance_ohm: float | None = None,
) -> dict[str, Any]:
    base, _, grid = load_params()
    base = replace(base, name="baseline_ipmsm_v1")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if speed_step_rpm is None:
        speed_step_rpm = DEFAULT_SPEED_STEP_RPM
    if field_currents_a is None:
        field_currents_a = list(DEFAULT_FIELD_CURRENTS_A)
    if kf_wb_per_a is None:
        kf_wb_per_a = DEFAULT_KF_WB_PER_A
    if field_resistance_ohm is None:
        field_resistance_ohm = DEFAULT_FIELD_RESISTANCE_OHM

    model = HybridExcitationModel(
        kf_wb_per_a=kf_wb_per_a,
        field_resistance_ohm=field_resistance_ohm,
    )

    rows = [
        evaluate_field_current(base, grid, model, field_current_a, speed_step_rpm)
        for field_current_a in field_currents_a
    ]

    csv_path = OUTPUT_DIR / "hybrid_excitation_results.csv"
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
            "kf_wb_per_a": model.kf_wb_per_a,
            "field_resistance_ohm": model.field_resistance_ohm,
        },
        "sweep_axes": {
            "field_current_a": field_currents_a,
            "speed_step_rpm": speed_step_rpm,
        },
        "scoring": {
            "loss_speed_penalty": LOSS_SPEED_PENALTY,
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
    "DEFAULT_FIELD_CURRENTS_A",
    "DEFAULT_KF_WB_PER_A",
    "DEFAULT_FIELD_RESISTANCE_OHM",
    "DEFAULT_SPEED_STEP_RPM",
    "evaluate_field_current",
    "run",
]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
