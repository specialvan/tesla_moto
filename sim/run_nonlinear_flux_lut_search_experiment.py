"""Run EXP-006 phase-2: nonlinear flux LUT constrained speed sweep."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .nonlinear_flux_lut import FluxLut
from .run_linear_dq_experiment import candidate_to_row, load_params, speed_grid
from .search import (
    find_id_zero_candidate,
    find_max_torque_feasible,
    find_min_current_for_torque,
)
from .dq_model import mechanical_rpm_to_electrical_rad_per_second

ROOT = Path(__file__).resolve().parents[1]
LUT_PATH = ROOT / "models" / "flux_lut_sample.json"
OUTPUT_DIR = ROOT / "experiments" / "exp_006_nonlinear_flux_lut"



def run() -> dict[str, Any]:
    params, raw_params, grid = load_params()
    lut = FluxLut.from_file(LUT_PATH)
    if params.pole_pairs != lut.pole_pairs:
        raise ValueError("motor params pole_pairs must match flux LUT pole_pairs")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))
    rows: list[dict[str, Any]] = []

    for speed_rpm in speed_grid(params.speed_max_rpm, step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        id_zero = find_id_zero_candidate(
            params, omega_e, params.torque_target_nm, grid, flux_lut=lut
        )
        min_current = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid, flux_lut=lut
        )
        max_torque = find_max_torque_feasible(params, omega_e, grid, flux_lut=lut)
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
        raise ValueError("LUT speed scan produced no rows")

    csv_path = OUTPUT_DIR / "lut_search_scan_results.csv"
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
        "experiment": "exp_006_nonlinear_flux_lut_search",
        "parameter_source": "synthetic_clean_room_flux_lut",
        "engineering_validated": False,
        "model_scope": "quasi_steady_nonlinear_flux_lut_grid_search",
        "model_limitations": [
            "sample LUT is synthetic and not FEA-derived",
            "search grid is clipped to LUT bounds",
            "no iron loss, inverter drop, thermal, or demagnetization coupling yet",
            "no shared MTPA, field-weakening, or MTPV LUT export yet",
        ],
        "lut_path": str(LUT_PATH.relative_to(ROOT)),
        "pole_pairs": lut.pole_pairs,
        "lut_bounds": {
            "id_min_a": lut.id_axis_a[0],
            "id_max_a": lut.id_axis_a[-1],
            "iq_min_a": lut.iq_axis_a[0],
            "iq_max_a": lut.iq_axis_a[-1],
        },
        "search_grid_clipped_to_lut_bounds": True,
        "target_torque_nm": params.torque_target_nm,
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
        "csv_path": str(csv_path.relative_to(ROOT)),
    }
    summary_path = OUTPUT_DIR / "lut_search_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
