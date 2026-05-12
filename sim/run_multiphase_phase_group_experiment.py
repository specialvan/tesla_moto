"""Run EXP-009: multiphase phase-group derating scan."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .multiphase_phase_group import PhaseGroupCase, derated_current_limit
from .run_linear_dq_experiment import load_params, speed_grid
from .search import find_min_current_for_torque

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_009_multiphase_phase_group"

CASES = [
    PhaseGroupCase("all_groups_balanced", 3, 3, 90.0, 0.0),
    PhaseGroupCase("all_groups_imbalanced", 3, 3, 90.0, 0.08),
    PhaseGroupCase("one_group_lost", 3, 2, 90.0, 0.08),
    PhaseGroupCase("limp_home_single_group", 3, 1, 90.0, 0.05),
]


def _params_for_current_limit(base: MotorParams, current_limit_a: float) -> MotorParams:
    return MotorParams(
        name=f"{base.name}_iphase_{current_limit_a:.1f}",
        pole_pairs=base.pole_pairs,
        rs_ohm=base.rs_ohm,
        ld_h=base.ld_h,
        lq_h=base.lq_h,
        psi_f_wb=base.psi_f_wb,
        vdc_v=base.vdc_v,
        i_max_a=current_limit_a,
        speed_max_rpm=base.speed_max_rpm,
        torque_target_nm=base.torque_target_nm,
        temperature_c=base.temperature_c,
        svpwm_linear_vmax_factor=base.svpwm_linear_vmax_factor,
    )


def _target_max_speed(
    params: MotorParams, grid: Any, speed_step_rpm: float
) -> float | None:
    reachable: list[float] = []
    for speed_rpm in speed_grid(params.speed_max_rpm, speed_step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        candidate = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid
        )
        if candidate is not None:
            reachable.append(speed_rpm)
    return max(reachable) if reachable else None


def run(speed_step_rpm: float | None = None) -> dict[str, Any]:
    base_params, raw_params, grid = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if speed_step_rpm is None:
        speed_step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))

    rows: list[dict[str, Any]] = []
    for case in CASES:
        derating = derated_current_limit(case)
        params = _params_for_current_limit(base_params, derating["available_current_a"])
        target_max_speed_rpm = _target_max_speed(params, grid, speed_step_rpm)
        rows.append(
            {
                "case": case.name,
                "total_groups": case.total_groups,
                "healthy_groups": case.healthy_groups,
                "per_group_current_limit_a": case.per_group_current_limit_a,
                "sharing_imbalance_ratio": case.sharing_imbalance_ratio,
                "available_current_a": derating["available_current_a"],
                "group_utilization": derating["group_utilization"],
                "healthy_group_ratio": derating["healthy_group_ratio"],
                "target_max_speed_rpm": target_max_speed_rpm,
            }
        )

    csv_path = OUTPUT_DIR / "multiphase_phase_group_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    worst_case = min(
        rows,
        key=lambda row: (
            -1.0
            if row["target_max_speed_rpm"] is None
            else float(row["target_max_speed_rpm"])
        ),
    )
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
        "cases": [case.__dict__ for case in CASES],
        "case_count": len(rows),
        "worst_case": worst_case,
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
