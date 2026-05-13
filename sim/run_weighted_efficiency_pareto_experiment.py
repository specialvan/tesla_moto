"""Run EXP-010: drive-cycle weighted efficiency Pareto scoring.

Brings together the candidate motor variants studied in
EXP-002 (variable flux), EXP-007 (hybrid excitation), and EXP-008
(winding reconfiguration) and ranks them under three illustrative
drive cycles (urban, highway, launch). Scoring is intentionally
auditable: every (candidate, cycle) row reports feasibility and
weighted copper loss before producing the final score, so a reader
can question the ranking without re-running the search.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from .drive_cycle import (
    DriveCycle,
    DriveCyclePoint,
    DriveCycleScore,
    rank_candidates_on_cycle,
    score_candidate_on_cycle,
)
from .dq_model import MotorParams
from .hybrid_excitation import HybridExcitationModel, with_field_current
from .run_linear_dq_experiment import load_params
from .search import GridSpec
from .variable_flux import with_flux_scale
from .winding_reconfiguration import WindingConfig, apply_winding_config

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_010_weighted_efficiency_pareto"

LOSS_SCALE_W = 3000.0

URBAN_CYCLE = DriveCycle(
    name="urban_low_speed",
    points=(
        DriveCyclePoint(speed_rpm=500.0, torque_nm=60.0, weight=0.2),
        DriveCyclePoint(speed_rpm=1000.0, torque_nm=80.0, weight=0.3),
        DriveCyclePoint(speed_rpm=2000.0, torque_nm=60.0, weight=0.3),
        DriveCyclePoint(speed_rpm=3000.0, torque_nm=40.0, weight=0.2),
    ),
)
HIGHWAY_CYCLE = DriveCycle(
    name="highway_high_speed",
    points=(
        DriveCyclePoint(speed_rpm=3000.0, torque_nm=40.0, weight=0.2),
        DriveCyclePoint(speed_rpm=4000.0, torque_nm=40.0, weight=0.3),
        DriveCyclePoint(speed_rpm=5000.0, torque_nm=40.0, weight=0.3),
        DriveCyclePoint(speed_rpm=6000.0, torque_nm=30.0, weight=0.2),
    ),
)
LAUNCH_CYCLE = DriveCycle(
    name="launch_peak_torque",
    points=(
        DriveCyclePoint(speed_rpm=500.0, torque_nm=100.0, weight=0.5),
        DriveCyclePoint(speed_rpm=1000.0, torque_nm=100.0, weight=0.5),
    ),
)
DEFAULT_CYCLES: tuple[DriveCycle, ...] = (URBAN_CYCLE, HIGHWAY_CYCLE, LAUNCH_CYCLE)


def build_candidates(
    base: MotorParams, grid: GridSpec
) -> list[tuple[str, MotorParams, GridSpec]]:
    """Build the (name, params, grid) candidate list ranked by EXP-010."""
    hybrid_model = HybridExcitationModel(
        kf_wb_per_a=0.00018,
        field_resistance_ohm=1.2,
    )
    candidates: list[tuple[str, MotorParams, GridSpec]] = []

    candidates.append(("baseline", base, grid))
    candidates.append(
        ("variable_flux_psi70", with_flux_scale(base, 0.70, "psi70pct"), grid)
    )
    candidates.append(
        ("variable_flux_psi55", with_flux_scale(base, 0.55, "psi55pct"), grid)
    )
    candidates.append(
        (
            "hybrid_excitation_if_minus_20",
            with_field_current(base, hybrid_model, -20.0),
            grid,
        )
    )
    candidates.append(
        (
            "hybrid_excitation_if_plus_20",
            with_field_current(base, hybrid_model, 20.0),
            grid,
        )
    )
    candidates.append(
        (
            "winding_series_torque",
            apply_winding_config(
                base,
                WindingConfig(
                    name="series_torque",
                    turns_scale=1.15,
                    resistance_scale=1.35,
                    current_limit_scale=0.82,
                ),
            ),
            grid,
        )
    )
    candidates.append(
        (
            "winding_parallel_speed",
            apply_winding_config(
                base,
                WindingConfig(
                    name="parallel_speed",
                    turns_scale=0.72,
                    resistance_scale=0.55,
                    current_limit_scale=1.25,
                ),
            ),
            grid,
        )
    )
    return candidates


def score_to_row(score: DriveCycleScore) -> dict[str, Any]:
    return {
        "candidate": score.candidate,
        "cycle": score.cycle,
        "reachable_points": score.reachable_points,
        "total_points": score.total_points,
        "feasible_weight": score.feasible_weight,
        "weighted_copper_loss_w": score.weighted_copper_loss_w,
        "score": score.score,
    }


def run(loss_scale_w: float | None = None) -> dict[str, Any]:
    base, _, grid = load_params()
    base = replace(base, name="baseline_ipmsm_v1")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if loss_scale_w is None:
        loss_scale_w = LOSS_SCALE_W

    candidates = build_candidates(base, grid)
    rows: list[dict[str, Any]] = []
    cycle_winners: dict[str, str] = {}

    for cycle in DEFAULT_CYCLES:
        ranked = rank_candidates_on_cycle(cycle, candidates, loss_scale_w)
        if ranked:
            cycle_winners[cycle.name] = ranked[0].candidate
        for entry in ranked:
            rows.append(score_to_row(entry))

    csv_path = OUTPUT_DIR / "weighted_efficiency_pareto_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    pareto_summary = compute_pareto_summary(rows)

    summary = {
        "experiment": "exp_010_weighted_efficiency_pareto",
        "parameter_source": "illustrative_clean_room_baseline_plus_candidate_family",
        "engineering_validated": False,
        "model_scope": "drive_cycle_weighted_copper_loss_with_grid_search",
        "model_limitations": [
            "drive cycles are illustrative and not from a measured dyno run",
            "scoring uses copper loss only; iron, mechanical, inverter losses ignored",
            "no transient acceleration / regen energy weighting",
        ],
        "loss_scale_w": loss_scale_w,
        "cycles": [
            {
                "name": cycle.name,
                "points": [asdict(point) for point in cycle.points],
                "total_weight": cycle.total_weight,
            }
            for cycle in DEFAULT_CYCLES
        ],
        "candidates": [name for name, _, _ in candidates],
        "cycle_winners": cycle_winners,
        "pareto_front": pareto_summary,
        "row_count": len(rows),
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def compute_pareto_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate per-candidate stats: mean score, min feasibility, total loss."""
    if not rows:
        return []
    by_candidate: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_candidate.setdefault(row["candidate"], []).append(row)

    aggregated: list[dict[str, Any]] = []
    for name, items in by_candidate.items():
        total = len(items)
        mean_score = sum(float(item["score"]) for item in items) / total
        min_feasibility = min(float(item["feasible_weight"]) for item in items)
        sum_loss = sum(float(item["weighted_copper_loss_w"]) for item in items)
        aggregated.append(
            {
                "candidate": name,
                "mean_score": mean_score,
                "min_feasible_weight": min_feasibility,
                "sum_weighted_copper_loss_w": sum_loss,
            }
        )
    aggregated.sort(key=lambda row: row["mean_score"], reverse=True)
    return aggregated


__all__ = [
    "DEFAULT_CYCLES",
    "URBAN_CYCLE",
    "HIGHWAY_CYCLE",
    "LAUNCH_CYCLE",
    "LOSS_SCALE_W",
    "build_candidates",
    "compute_pareto_summary",
    "run",
    "score_candidate_on_cycle",
]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
