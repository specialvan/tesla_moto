"""Run EXP-004: temperature and demag safety boundary scan."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dq_model import MotorParams, mechanical_rpm_to_electrical_rad_per_second
from .run_linear_dq_experiment import PARAMS_PATH, speed_grid
from .safety_limits import (
    DemagLimit,
    ThermalModel,
    apply_temperature,
    find_min_current_for_torque_with_safety,
)
from .search import GridSpec, find_min_current_for_torque

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_004_safety_boundaries"


def load_base() -> tuple[MotorParams, dict[str, Any], GridSpec]:
    raw = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    return MotorParams.from_dict(raw), raw, GridSpec.from_dict(raw["grid"])


def _max_reachable_speed(
    params: MotorParams,
    grid: GridSpec,
    speed_step_rpm: float,
    demag_limit: DemagLimit | None,
) -> float | None:
    reachable: list[float] = []
    for speed_rpm in speed_grid(params.speed_max_rpm, speed_step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        if demag_limit is None:
            candidate = find_min_current_for_torque(
                params, omega_e, params.torque_target_nm, grid
            )
        else:
            candidate = find_min_current_for_torque_with_safety(
                params, omega_e, params.torque_target_nm, grid, demag_limit
            )
        if candidate is not None:
            reachable.append(speed_rpm)
    return max(reachable) if reachable else None


def run() -> dict[str, Any]:
    base, raw, grid = load_base()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    thermal_model = ThermalModel(
        reference_c=25.0,
        copper_alpha_per_c=0.0039,
        pm_alpha_per_c=-0.001,
    )
    demag_limit = DemagLimit(
        points_c_to_id_min_a=[
            (25.0, -240.0),
            (100.0, -210.0),
            (140.0, -180.0),
        ]
    )

    cases: list[dict[str, Any]] = []
    speed_step_rpm = float(raw.get("base_speed_scan_step_rpm", 250.0))
    for temperature_c in [25.0, 100.0, 140.0]:
        for vdc_scale in [1.0, 0.85]:
            hot = apply_temperature(base, temperature_c, thermal_model)
            params = MotorParams(
                name=f"{hot.name}_T{temperature_c:.0f}_V{vdc_scale:.2f}",
                pole_pairs=hot.pole_pairs,
                rs_ohm=hot.rs_ohm,
                ld_h=hot.ld_h,
                lq_h=hot.lq_h,
                psi_f_wb=hot.psi_f_wb,
                vdc_v=hot.vdc_v * vdc_scale,
                i_max_a=hot.i_max_a,
                speed_max_rpm=hot.speed_max_rpm,
                torque_target_nm=hot.torque_target_nm,
                temperature_c=hot.temperature_c,
                svpwm_linear_vmax_factor=hot.svpwm_linear_vmax_factor,
            )
            unconstrained = _max_reachable_speed(
                params, grid, speed_step_rpm, demag_limit=None
            )
            demag_limited = _max_reachable_speed(
                params, grid, speed_step_rpm, demag_limit=demag_limit
            )
            cases.append(
                {
                    "case_id": params.name,
                    "temperature_c": temperature_c,
                    "vdc_scale": vdc_scale,
                    "rs_ohm": params.rs_ohm,
                    "psi_f_wb": params.psi_f_wb,
                    "id_min_allowed_a": demag_limit.id_min_allowed(temperature_c),
                    "unconstrained_target_max_speed_rpm": unconstrained,
                    "demag_limited_target_max_speed_rpm": demag_limited,
                }
            )

    csv_path = OUTPUT_DIR / "safety_boundary_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cases[0].keys()))
        writer.writeheader()
        writer.writerows(cases)

    def sort_key(case: dict[str, Any]) -> tuple[float, float]:
        speed = case["demag_limited_target_max_speed_rpm"]
        return (-1.0 if speed is None else float(speed), -case["temperature_c"])

    worst_case = min(cases, key=sort_key)
    summary = {
        "experiment": "exp_004_safety_boundaries",
        "model_scope": "temperature_corrected_linear_dq_with_simplified_demag_limit",
        "engineering_validated": False,
        "thermal_model": {
            "reference_c": thermal_model.reference_c,
            "copper_alpha_per_c": thermal_model.copper_alpha_per_c,
            "pm_alpha_per_c": thermal_model.pm_alpha_per_c,
        },
        "demag_limit_points": demag_limit.points_c_to_id_min_a,
        "case_count": len(cases),
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
