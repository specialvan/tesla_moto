"""Run EXP-002: compare fixed-psi weak flux with lower equivalent psi_f states."""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .run_linear_dq_experiment import load_params, speed_grid
from .search import Candidate, find_min_current_for_torque
from .variable_flux import with_flux_scale

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_002_variable_flux"
FLUX_STATES = {
    "psi_100pct": 1.0,
    "psi_85pct": 0.85,
    "psi_70pct": 0.70,
    "psi_55pct": 0.55,
}
TORQUE_TARGETS_NM = [100.0, 80.0, 60.0, 40.0]


def candidate_metrics(candidate: Candidate | None) -> dict[str, float | bool | None]:
    if candidate is None:
        return {
            "id_a": None,
            "iq_a": None,
            "torque_nm": None,
            "current_a": None,
            "voltage_v": None,
            "voltage_margin_v": None,
            "current_margin_a": None,
            "copper_loss_w": None,
            "feasible": False,
        }
    return {
        "id_a": candidate.id_a,
        "iq_a": candidate.iq_a,
        "torque_nm": candidate.torque_nm,
        "current_a": candidate.current_a,
        "voltage_v": candidate.voltage_v,
        "voltage_margin_v": candidate.voltage_margin_v,
        "current_margin_a": candidate.current_margin_a,
        "copper_loss_w": candidate.copper_loss_w,
        "feasible": candidate.feasible,
    }


def state_row(
    base_params: MotorParams,
    speed_rpm: float,
    torque_target_nm: float,
    state_name: str,
    flux_scale: float,
    grid: Any,
) -> dict[str, Any]:
    target_params = replace(base_params, torque_target_nm=torque_target_nm)
    state_params = with_flux_scale(target_params, flux_scale, state_name)
    omega_e = mechanical_rpm_to_electrical_rad_per_second(
        speed_rpm, state_params.pole_pairs
    )
    candidate = find_min_current_for_torque(
        state_params, omega_e, state_params.torque_target_nm, grid
    )
    metrics = candidate_metrics(candidate)
    return {
        "speed_rpm": speed_rpm,
        "target_torque_nm": torque_target_nm,
        "state": state_name,
        "flux_scale": flux_scale,
        "psi_f_wb": state_params.psi_f_wb,
        "ke_relative": flux_scale,
        **metrics,
    }


def summarize(rows: list[dict[str, Any]], state_names: list[str]) -> dict[str, Any]:
    state_summaries: dict[str, dict[str, dict[str, float | None]]] = {}
    torque_targets = sorted({row["target_torque_nm"] for row in rows}, reverse=True)
    for torque_target in torque_targets:
        state_summaries[str(torque_target)] = {}
        for state_name in state_names:
            state_rows = [
                row
                for row in rows
                if row["state"] == state_name
                and row["target_torque_nm"] == torque_target
            ]
            feasible_rows = [row for row in state_rows if row["feasible"]]
            state_summaries[str(torque_target)][state_name] = {
                "target_max_speed_rpm": max(
                    (row["speed_rpm"] for row in feasible_rows), default=None
                ),
                "min_copper_loss_w": min(
                    (row["copper_loss_w"] for row in feasible_rows), default=None
                ),
                "max_voltage_margin_v": max(
                    (row["voltage_margin_v"] for row in feasible_rows), default=None
                ),
                "most_negative_id_a": min(
                    (row["id_a"] for row in feasible_rows), default=None
                ),
            }
    return state_summaries


def run() -> dict[str, Any]:
    params, raw_params, grid = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))
    speeds = speed_grid(params.speed_max_rpm, step_rpm)

    rows = [
        state_row(params, speed_rpm, torque_target, state_name, flux_scale, grid)
        for torque_target in TORQUE_TARGETS_NM
        for speed_rpm in speeds
        for state_name, flux_scale in FLUX_STATES.items()
    ]

    csv_path = OUTPUT_DIR / "variable_flux_scan.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "exp_002_variable_flux",
        "parameter_source": "illustrative_clean_room_baseline",
        "engineering_validated": False,
        "model_scope": "quasi_steady_linear_dq_virtual_psi_f_scaling",
        "model_limitations": [
            "psi_f scaling does not model magnetization pulse energy",
            "psi_f scaling does not model irreversible demagnetization",
            "Ld/Lq are held constant across flux states",
            "no iron loss or inverter loss",
            "no thermal derating",
        ],
        "base_psi_f_wb": params.psi_f_wb,
        "torque_targets_nm": TORQUE_TARGETS_NM,
        "flux_states": FLUX_STATES,
        "state_summaries_by_torque": summarize(rows, list(FLUX_STATES.keys())),
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
