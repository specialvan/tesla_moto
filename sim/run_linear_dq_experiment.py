"""Run EXP-001: quasi-steady linear dq operating-point scan."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from math import floor, isfinite
from pathlib import Path
from typing import Any

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .search import (
    Candidate,
    GridSpec,
    find_id_zero_candidate,
    find_max_torque_feasible,
    find_min_current_for_torque,
)

ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = ROOT / "models" / "motor_params.json"
OUTPUT_DIR = ROOT / "experiments" / "exp_001_linear_dq"


def load_params() -> tuple[MotorParams, dict[str, Any], GridSpec]:
    raw = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    params = MotorParams.from_dict(raw)
    grid = GridSpec.from_dict(raw.get("grid", {}))
    return params, raw, grid


def candidate_to_row(
    prefix: str, candidate: Candidate | None
) -> dict[str, float | bool | None]:
    if candidate is None:
        return {
            f"{prefix}_id_a": None,
            f"{prefix}_iq_a": None,
            f"{prefix}_torque_nm": None,
            f"{prefix}_current_a": None,
            f"{prefix}_voltage_v": None,
            f"{prefix}_voltage_margin_v": None,
            f"{prefix}_current_margin_a": None,
            f"{prefix}_copper_loss_w": None,
            f"{prefix}_feasible": False,
        }
    data = asdict(candidate)
    return {
        f"{prefix}_id_a": data["id_a"],
        f"{prefix}_iq_a": data["iq_a"],
        f"{prefix}_torque_nm": data["torque_nm"],
        f"{prefix}_current_a": data["current_a"],
        f"{prefix}_voltage_v": data["voltage_v"],
        f"{prefix}_voltage_margin_v": data["voltage_margin_v"],
        f"{prefix}_current_margin_a": data["current_margin_a"],
        f"{prefix}_copper_loss_w": data["copper_loss_w"],
        f"{prefix}_feasible": data["feasible"],
    }


def speed_grid(max_speed_rpm: float, step_rpm: float) -> list[float]:
    if not isfinite(max_speed_rpm) or not isfinite(step_rpm):
        raise ValueError("speed grid values must be finite")
    if max_speed_rpm < 0:
        raise ValueError("max_speed_rpm must be non-negative")
    if step_rpm <= 0:
        raise ValueError("base_speed_scan_step_rpm must be positive")

    count = floor(max_speed_rpm / step_rpm)
    speeds = [index * step_rpm for index in range(count + 1)]
    if not speeds or speeds[-1] < max_speed_rpm:
        speeds.append(max_speed_rpm)
    return speeds


def run() -> dict[str, Any]:
    params, raw_params, grid = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))
    rows: list[dict[str, Any]] = []

    for speed_rpm in speed_grid(params.speed_max_rpm, step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        id_zero = find_id_zero_candidate(params, omega_e, params.torque_target_nm, grid)
        min_current = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid
        )
        max_torque = find_max_torque_feasible(params, omega_e, grid)
        row: dict[str, Any] = {
            "speed_rpm": speed_rpm,
            "omega_e_rad_s": omega_e,
            "target_torque_nm": params.torque_target_nm,
            "vmax_v": params.vmax_v,
            "imax_a": params.imax_a,
        }
        row.update(candidate_to_row("id_zero", id_zero))
        row.update(candidate_to_row("min_current_target", min_current))
        row.update(candidate_to_row("max_feasible_torque", max_torque))
        rows.append(row)

    if not rows:
        raise ValueError("speed scan produced no rows")

    csv_path = OUTPUT_DIR / "scan_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    target_reachable = [row for row in rows if row["min_current_target_feasible"]]
    positive_torque = [
        row
        for row in rows
        if row["max_feasible_torque_torque_nm"] is not None
        and row["max_feasible_torque_torque_nm"] > 1.0
    ]
    id_zero_reachable = [row for row in rows if row["id_zero_feasible"]]

    summary = {
        "params_name": params.name,
        "parameter_source": "illustrative_clean_room_baseline",
        "engineering_validated": False,
        "model_scope": "quasi_steady_linear_dq_grid_search",
        "model_limitations": [
            "no_current_loop_dynamics",
            "no_nonlinear_flux_lut",
            "no_iron_loss",
            "no_inverter_voltage_drop",
            "no_temperature_derating",
            "no_demagnetization_boundary",
        ],
        "target_torque_nm": params.torque_target_nm,
        "temperature_c": params.temperature_c,
        "vdc_v": params.vdc_v,
        "vmax_v": params.vmax_v,
        "imax_a": params.imax_a,
        "scan_step_rpm": step_rpm,
        "max_speed_configured_rpm": params.speed_max_rpm,
        "max_speed_scanned_rpm": max(row["speed_rpm"] for row in rows),
        "id_zero_target_max_speed_rpm": max(
            (row["speed_rpm"] for row in id_zero_reachable), default=None
        ),
        "min_current_target_max_speed_rpm": max(
            (row["speed_rpm"] for row in target_reachable), default=None
        ),
        "max_feasible_positive_torque_max_speed_rpm": max(
            (row["speed_rpm"] for row in positive_torque), default=None
        ),
        "csv_path": str(csv_path),
        "notes": [
            "v1 uses quasi-steady linear dq equations and grid search.",
            "Results are illustrative until parameters are replaced by measured or FEA-derived values.",
            "min_current_target means minimum-current feasible grid point for target torque under voltage/current constraints.",
            "max_feasible_torque means maximum feasible torque under voltage/current constraints at each speed.",
        ],
    }

    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
