"""Run EXP-008: winding reconfiguration parameter-set sweep."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dq_model import mechanical_rpm_to_electrical_rad_per_second
from .run_linear_dq_experiment import load_params, speed_grid
from .search import Candidate, GridSpec, find_min_current_for_torque
from .winding_reconfiguration import (
    WindingConfig,
    apply_winding_config,
    transition_delta,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_008_winding_reconfiguration"

CONFIGS = [
    WindingConfig(
        "series_torque",
        turns_scale=1.15,
        resistance_scale=1.35,
        current_limit_scale=0.82,
    ),
    WindingConfig(
        "base", turns_scale=1.0, resistance_scale=1.0, current_limit_scale=1.0
    ),
    WindingConfig(
        "parallel_speed",
        turns_scale=0.72,
        resistance_scale=0.55,
        current_limit_scale=1.25,
    ),
]
TRANSITION_SPEED_RPM = 5000.0


def _boundary(
    params: Any, grid: GridSpec, speed_step_rpm: float
) -> tuple[float | None, dict[str, float | None]]:
    reachable: list[tuple[float, Candidate]] = []
    for speed_rpm in speed_grid(params.speed_max_rpm, speed_step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        candidate = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid
        )
        if candidate is not None:
            reachable.append((speed_rpm, candidate))
    if not reachable:
        return None, {"torque_nm": None, "current_a": None}
    speed_rpm, candidate = max(reachable, key=lambda row: row[0])
    return speed_rpm, {
        "torque_nm": candidate.torque_nm,
        "current_a": candidate.current_a,
    }


def _transition_point(params: Any, grid: Any) -> dict[str, float | None]:
    omega_e = mechanical_rpm_to_electrical_rad_per_second(
        TRANSITION_SPEED_RPM, params.pole_pairs
    )
    candidate = find_min_current_for_torque(
        params, omega_e, params.torque_target_nm, grid
    )
    if candidate is None:
        return {"torque_nm": None, "current_a": None}
    return {
        "torque_nm": candidate.torque_nm,
        "current_a": candidate.current_a,
    }


def run(speed_step_rpm: float | None = None) -> dict[str, Any]:
    base_params, raw_params, grid = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if speed_step_rpm is None:
        speed_step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))

    rows: list[dict[str, Any]] = []
    transition_points: dict[str, dict[str, float | None]] = {}
    for config in CONFIGS:
        params = apply_winding_config(base_params, config)
        target_max_speed_rpm, boundary_point = _boundary(params, grid, speed_step_rpm)
        transition_points[config.name] = _transition_point(params, grid)
        rows.append(
            {
                "config": config.name,
                "turns_scale": config.turns_scale,
                "resistance_scale": config.resistance_scale,
                "current_limit_scale": config.current_limit_scale,
                "rs_ohm": params.rs_ohm,
                "ld_h": params.ld_h,
                "lq_h": params.lq_h,
                "psi_f_wb": params.psi_f_wb,
                "imax_a": params.imax_a,
                "target_max_speed_rpm": target_max_speed_rpm,
                "boundary_torque_nm": boundary_point["torque_nm"],
                "boundary_current_a": boundary_point["current_a"],
            }
        )

    csv_path = OUTPUT_DIR / "winding_reconfiguration_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    recommended_config = max(
        rows,
        key=lambda row: (
            -1.0
            if row["target_max_speed_rpm"] is None
            else float(row["target_max_speed_rpm"])
        ),
    )
    transition_check = transition_delta(
        transition_points["base"], transition_points["parallel_speed"]
    )
    summary = {
        "experiment": "exp_008_winding_reconfiguration",
        "parameter_source": "illustrative_clean_room_winding_scale_family",
        "engineering_validated": False,
        "model_scope": "linear_dq_multi_winding_configuration_sweep",
        "model_limitations": [
            "configuration scaling is parametric, not a validated winding layout",
            "no switching transient, contactor arc, insulation, or circulating-current model",
            "no thermal sharing between parallel paths",
        ],
        "configs": [config.__dict__ for config in CONFIGS],
        "transition_speed_rpm": TRANSITION_SPEED_RPM,
        "transition_check": transition_check,
        "recommended_config": recommended_config,
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
