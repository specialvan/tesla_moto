"""Run EXP-011: Iron loss estimation across speed and torque operating points.

This experiment extends the linear dq model with iron loss estimation using
the Bertotti (three-term) model. Iron loss is computed across the same speed
grid as EXP-001, enabling combined copper + iron loss efficiency analysis.

The experiment produces:
- summary.json: Experiment metadata, model limitations, and key findings
- iron_loss_sweep_results.csv: Per-speed-point iron loss breakdown and efficiency
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dq_model import (
    MotorParams,
    mechanical_rpm_to_electrical_rad_per_second,
)
from .iron_loss import (
    BertottiCoeffs,
    bertotti_iron_loss_per_phase,
    flux_density_from_lambda,
    iron_loss_from_id_iq,
)
from .run_linear_dq_experiment import (
    load_params,
    speed_grid,
)
from .search import (
    Candidate,
    find_max_torque_feasible,
    find_min_current_for_torque,
)

ROOT = Path(__file__).resolve().parents[1]


def candidate_to_row(
    prefix: str,
    candidate: Candidate | None,
    params: MotorParams,
    coeffs: BertottiCoeffs,
    freq_hz: float,
) -> dict[str, Any]:
    """Convert a Candidate to a CSV row with prefix."""
    if candidate is None:
        return {
            f"{prefix}_feasible": False,
            f"{prefix}_id_a": None,
            f"{prefix}_iq_a": None,
            f"{prefix}_torque_nm": None,
            f"{prefix}_current_a": None,
            f"{prefix}_voltage_v": None,
            f"{prefix}_copper_loss_w": None,
            f"{prefix}_iron_loss_w": None,
            f"{prefix}_total_loss_w": None,
            f"{prefix}_efficiency_pct": None,
            f"{prefix}_lambda_d_wb": None,
            f"{prefix}_lambda_q_wb": None,
            f"{prefix}_b_peak_t": None,
        }

    lambda_d = params.ld_h * candidate.id_a + params.psi_f_wb
    lambda_q = params.lq_h * candidate.iq_a
    lambda_mag = (lambda_d ** 2 + lambda_q ** 2) ** 0.5

    copper_loss = candidate.copper_loss_w

    # Compute iron loss (skip at 0 Hz)
    if freq_hz > 0:
        iron = iron_loss_from_id_iq(
            candidate.id_a,
            candidate.iq_a,
            params.ld_h,
            params.lq_h,
            params.psi_f_wb,
            freq_hz,
            coeffs=coeffs,
        )
        iron_loss_total = iron.total_three_phase_w
    else:
        iron_loss_total = 0.0

    total_loss = copper_loss + iron_loss_total

    # Mechanical output power
    omega_e = freq_hz * 2.0 * 3.14159265359
    mechanical_power_w = candidate.torque_nm * omega_e / params.pole_pairs
    input_power_w = mechanical_power_w + total_loss
    efficiency_pct = (mechanical_power_w / input_power_w * 100.0) if input_power_w > 0 else 0.0

    return {
        f"{prefix}_feasible": candidate.feasible,
        f"{prefix}_id_a": candidate.id_a,
        f"{prefix}_iq_a": candidate.iq_a,
        f"{prefix}_torque_nm": candidate.torque_nm,
        f"{prefix}_current_a": candidate.current_a,
        f"{prefix}_voltage_v": candidate.voltage_v,
        f"{prefix}_copper_loss_w": copper_loss,
        f"{prefix}_iron_loss_w": iron_loss_total,
        f"{prefix}_total_loss_w": total_loss,
        f"{prefix}_efficiency_pct": efficiency_pct,
        f"{prefix}_lambda_d_wb": lambda_d,
        f"{prefix}_lambda_q_wb": lambda_q,
        f"{prefix}_b_peak_t": flux_density_from_lambda(lambda_mag, 0.05),
    }


def run() -> dict[str, Any]:
    """Run the iron loss experiment."""
    params, raw_params, grid = load_params()

    step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))

    # Bertotti coefficients for the clean-room study
    coeffs = BertottiCoeffs(k_hyst=0.04, k_eddy=0.004, k_excess=0.003)

    rows: list[dict[str, Any]] = []

    for speed_rpm in speed_grid(params.speed_max_rpm, step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(speed_rpm, params.pole_pairs)
        freq_hz = omega_e / (2.0 * 3.14159265359)

        # Get candidates
        min_current = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid
        )
        max_torque = find_max_torque_feasible(params, omega_e, grid)

        # Baseline iron loss (id=0, iq=0) at this speed
        # Iron loss is zero at 0 Hz (standstill)
        if freq_hz > 0:
            iron_base = iron_loss_from_id_iq(
                0.0, 0.0,
                params.ld_h, params.lq_h, params.psi_f_wb,
                freq_hz, coeffs
            )
            baseline_iron_loss_w = iron_base.total_three_phase_w
        else:
            baseline_iron_loss_w = 0.0

        row: dict[str, Any] = {
            "speed_rpm": speed_rpm,
            "omega_e_rad_s": omega_e,
            "freq_hz": freq_hz,
            "target_torque_nm": params.torque_target_nm,
            "baseline_iron_loss_w": baseline_iron_loss_w,
        }
        row.update(candidate_to_row("min_current_target", min_current, params, coeffs, freq_hz))
        row.update(candidate_to_row("max_feasible_torque", max_torque, params, coeffs, freq_hz))
        rows.append(row)

    if not rows:
        raise ValueError("Iron loss scan produced no rows")

    # Write CSV
    output_dir = ROOT / "experiments" / "exp_011_iron_loss"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "iron_loss_sweep_results.csv"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Compute summary statistics
    target_points = [r for r in rows if r["min_current_target_feasible"]]
    max_torque_points = [r for r in rows if r["max_feasible_torque_feasible"]]

    avg_iron_loss_target = (
        sum(r["min_current_target_iron_loss_w"] for r in target_points)
        / len(target_points) if target_points else 0.0
    )
    avg_efficiency_target = (
        sum(r["min_current_target_efficiency_pct"] for r in target_points)
        / len(target_points) if target_points else 0.0
    )

    summary = {
        "experiment": "exp_011_iron_loss",
        "parameter_source": "illustrative_clean_room_baseline_plus_bertotti_iron_loss",
        "engineering_validated": False,
        "model_scope": "linear_dq_with_iron_loss_estimation",
        "model_limitations": [
            "iron loss uses simplified Bertotti model with fixed coefficients",
            "no FEA-derived B mapping, lamination stack, or frequency-dependent material data",
            "no thermal coupling to iron loss coefficients",
            "no PWM harmonics or skin effect in copper",
            "iron loss assumed uniform across stator/rotor for this clean-room study",
        ],
        "iron_loss_model": {
            "type": "bertotti_three_term",
            "k_hyst": coeffs.k_hyst,
            "k_eddy": coeffs.k_eddy,
            "k_excess": coeffs.k_excess,
            "core_radius_m": 0.05,
        },
        "target_torque_nm": params.torque_target_nm,
        "scan_step_rpm": step_rpm,
        "max_speed_configured_rpm": params.speed_max_rpm,
        "max_speed_scanned_rpm": max(row["speed_rpm"] for row in rows),
        "target_torque_feasible_count": len(target_points),
        "max_torque_feasible_count": len(max_torque_points),
        "avg_iron_loss_at_target_torque_w": avg_iron_loss_target,
        "avg_efficiency_at_target_torque_pct": avg_efficiency_target,
        "iron_loss_vs_copper_loss_ratio": (
            avg_iron_loss_target / target_points[0]["min_current_target_copper_loss_w"]
            if target_points and target_points[0]["min_current_target_copper_loss_w"] > 0
            else None
        ),
        "csv_path": str(csv_path.relative_to(ROOT)),
    }

    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))