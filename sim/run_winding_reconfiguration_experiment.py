"""Run EXP-008: winding reconfiguration parameter sweep.

For each declared winding configuration we instantiate a scaled
``MotorParams``, find the boundary at which the target torque is still
reachable, then check the torque/current delta between the base
configuration and its neighbours at the declared transition speed.
"""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .run_linear_dq_experiment import load_params, speed_grid
from .search import Candidate, GridSpec, find_min_current_for_torque
from .winding_reconfiguration import WindingConfig, apply_winding_config

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_008_winding_reconfiguration"

DEFAULT_CONFIGS: tuple[WindingConfig, ...] = (
    WindingConfig(
        name="series_torque",
        turns_scale=1.15,
        resistance_scale=1.35,
        current_limit_scale=0.82,
    ),
    WindingConfig(
        name="base",
        turns_scale=1.0,
        resistance_scale=1.0,
        current_limit_scale=1.0,
    ),
    WindingConfig(
        name="parallel_speed",
        turns_scale=0.72,
        resistance_scale=0.55,
        current_limit_scale=1.25,
    ),
)
DEFAULT_TRANSITION_SPEED_RPM = 5000.0
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


def evaluate_config(
    base: MotorParams,
    grid: GridSpec,
    config: WindingConfig,
    speed_step_rpm: float,
) -> dict[str, Any]:
    params = apply_winding_config(base, config)
    speed_rpm, candidate = _max_reachable(params, grid, speed_step_rpm)

    return {
        "config": config.name,
        "turns_scale": config.turns_scale,
        "resistance_scale": config.resistance_scale,
        "current_limit_scale": config.current_limit_scale,
        "rs_ohm": params.rs_ohm,
        "ld_h": params.ld_h,
        "lq_h": params.lq_h,
        "psi_f_wb": params.psi_f_wb,
        "imax_a": params.i_max_a,
        "target_max_speed_rpm": speed_rpm,
        "boundary_torque_nm": (
            float(candidate.torque_nm) if candidate is not None else None
        ),
        "boundary_current_a": (
            float(candidate.current_a) if candidate is not None else None
        ),
    }


def transition_check(
    base: MotorParams,
    grid: GridSpec,
    config_a: WindingConfig,
    config_b: WindingConfig,
    transition_speed_rpm: float,
) -> dict[str, Any]:
    params_a = apply_winding_config(base, config_a)
    params_b = apply_winding_config(base, config_b)
    omega_a = mechanical_rpm_to_electrical_rad_per_second(
        transition_speed_rpm, params_a.pole_pairs
    )
    omega_b = mechanical_rpm_to_electrical_rad_per_second(
        transition_speed_rpm, params_b.pole_pairs
    )
    cand_a = find_min_current_for_torque(
        params_a, omega_a, params_a.torque_target_nm, grid
    )
    cand_b = find_min_current_for_torque(
        params_b, omega_b, params_b.torque_target_nm, grid
    )

    if cand_a is None or cand_b is None:
        return {
            "from_config": config_a.name,
            "to_config": config_b.name,
            "transition_speed_rpm": transition_speed_rpm,
            "torque_delta_nm": None,
            "current_delta_a": None,
            "feasible": False,
        }
    return {
        "from_config": config_a.name,
        "to_config": config_b.name,
        "transition_speed_rpm": transition_speed_rpm,
        "torque_delta_nm": float(cand_b.torque_nm - cand_a.torque_nm),
        "current_delta_a": float(cand_b.current_a - cand_a.current_a),
        "feasible": True,
    }


def run(
    speed_step_rpm: float | None = None,
    configs: Sequence[WindingConfig] | None = None,
    transition_speed_rpm: float | None = None,
) -> dict[str, Any]:
    base, _, grid = load_params()
    base = replace(base, name="baseline_ipmsm_v1")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if speed_step_rpm is None:
        speed_step_rpm = DEFAULT_SPEED_STEP_RPM
    if configs is None:
        configs = DEFAULT_CONFIGS
    if transition_speed_rpm is None:
        transition_speed_rpm = DEFAULT_TRANSITION_SPEED_RPM

    rows = [
        evaluate_config(base, grid, config, speed_step_rpm) for config in configs
    ]

    csv_path = OUTPUT_DIR / "winding_reconfiguration_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    transitions = [
        transition_check(base, grid, configs[i], configs[i + 1], transition_speed_rpm)
        for i in range(len(configs) - 1)
    ]

    feasible_rows = [
        row for row in rows if row["target_max_speed_rpm"] is not None
    ]
    recommended = (
        max(
            feasible_rows,
            key=lambda row: (
                float(row["target_max_speed_rpm"] or 0.0),
                float(row["boundary_torque_nm"] or 0.0),
            ),
        )
        if feasible_rows
        else None
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
        "configs": [
            {
                "name": config.name,
                "turns_scale": config.turns_scale,
                "resistance_scale": config.resistance_scale,
                "current_limit_scale": config.current_limit_scale,
            }
            for config in configs
        ],
        "transition_speed_rpm": transition_speed_rpm,
        "transitions": transitions,
        "recommended_config": recommended,
        "row_count": len(rows),
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


__all__ = [
    "DEFAULT_CONFIGS",
    "DEFAULT_TRANSITION_SPEED_RPM",
    "DEFAULT_SPEED_STEP_RPM",
    "evaluate_config",
    "transition_check",
    "run",
]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
