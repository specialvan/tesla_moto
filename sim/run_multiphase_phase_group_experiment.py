"""Run EXP-009: multiphase phase-group derating cases.

For each declared case we clamp the operating-point grid and the
``MotorParams.i_max_a`` to the available current the healthy phase
groups can deliver, then sweep speeds to find the highest reachable
speed at the target torque.
"""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .multiphase_phase_group import PhaseGroupCase, apply_phase_group_case
from .run_linear_dq_experiment import load_params, speed_grid
from .search import Candidate, GridSpec, find_min_current_for_torque

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_009_multiphase_phase_group"

DEFAULT_CASES: tuple[PhaseGroupCase, ...] = (
    PhaseGroupCase(
        name="all_groups_balanced",
        total_groups=3,
        healthy_groups=3,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.0,
    ),
    PhaseGroupCase(
        name="all_groups_imbalanced",
        total_groups=3,
        healthy_groups=3,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.08,
    ),
    PhaseGroupCase(
        name="one_group_lost",
        total_groups=3,
        healthy_groups=2,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.08,
    ),
    PhaseGroupCase(
        name="limp_home_single_group",
        total_groups=3,
        healthy_groups=1,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.05,
    ),
)
DEFAULT_SPEED_STEP_RPM = 1000.0


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


def evaluate_case(
    base: MotorParams,
    grid: GridSpec,
    case: PhaseGroupCase,
    speed_step_rpm: float,
) -> dict[str, Any]:
    params, scaled_grid = apply_phase_group_case(base, grid, case)
    speed_rpm, _ = _max_reachable(params, scaled_grid, speed_step_rpm)
    return {
        "case": case.name,
        "total_groups": case.total_groups,
        "healthy_groups": case.healthy_groups,
        "per_group_current_limit_a": case.per_group_current_limit_a,
        "sharing_imbalance_ratio": case.sharing_imbalance_ratio,
        "available_current_a": case.available_current_a,
        "group_utilization": case.group_utilization,
        "healthy_group_ratio": case.healthy_group_ratio,
        "target_max_speed_rpm": speed_rpm,
    }


def run(
    speed_step_rpm: float | None = None,
    cases: Sequence[PhaseGroupCase] | None = None,
) -> dict[str, Any]:
    base, _, grid = load_params()
    base = replace(base, name="baseline_ipmsm_v1")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if speed_step_rpm is None:
        speed_step_rpm = DEFAULT_SPEED_STEP_RPM
    if cases is None:
        cases = DEFAULT_CASES

    rows = [evaluate_case(base, grid, case, speed_step_rpm) for case in cases]

    csv_path = OUTPUT_DIR / "multiphase_phase_group_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    def sort_key(row: dict[str, Any]) -> tuple[float, float]:
        speed = row["target_max_speed_rpm"]
        speed_value = -1.0 if speed is None else float(speed)
        return (speed_value, float(row["healthy_group_ratio"]))

    worst_case = min(rows, key=sort_key)

    summary = {
        "experiment": "exp_009_multiphase_phase_group",
        "parameter_source": "illustrative_clean_room_phase_group_derating",
        "engineering_validated": False,
        "model_scope": "linear_dq_with_phase_group_current_derating",
        "model_limitations": [
            "phase groups are represented as aggregate current derating only",
            "no harmonic subspace, neutral-shift, or open-phase voltage-vector model",
            "no per-phase thermal RC or current-controller saturation dynamics",
        ],
        "cases": [
            {
                "name": case.name,
                "total_groups": case.total_groups,
                "healthy_groups": case.healthy_groups,
                "per_group_current_limit_a": case.per_group_current_limit_a,
                "sharing_imbalance_ratio": case.sharing_imbalance_ratio,
            }
            for case in cases
        ],
        "case_count": len(rows),
        "worst_case": worst_case,
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


__all__ = [
    "DEFAULT_CASES",
    "DEFAULT_SPEED_STEP_RPM",
    "evaluate_case",
    "run",
]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
