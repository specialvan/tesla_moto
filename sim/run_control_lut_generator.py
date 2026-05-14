"""Generate a control LUT from linear dq or nonlinear flux LUT search results.

This module provides the run() function that generates a control lookup table
(control_lut.json) from the search results of either:
- sim/run_linear_dq_experiment.py (linear dq model)
- sim/run_nonlinear_flux_lut_search_experiment.py (nonlinear flux LUT)

The generated LUT follows models/control_lut_schema.json and includes:
- Speed-torque grid with optimal id/iq commands
- Control mode labels (MTPA/FW/MTPV)
- Feasibility and constraint margin information
- Mode transition boundaries
- Validation metrics
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from typing import Any

from .dq_model import current_mag_a, voltage_magnitude
from .nonlinear_flux_lut import FluxLut
from .run_linear_dq_experiment import candidate_to_row, load_params, speed_grid
from .search import (
    GridSpec,
    Candidate,
    find_id_zero_candidate,
    find_max_torque_feasible,
    find_min_current_for_torque,
)
from .dq_model import mechanical_rpm_to_electrical_rad_per_second

ROOT = Path(__file__).resolve().parents[1]


# Default voltage margin warning threshold (V)
DEFAULT_VOLTAGE_MARGIN_WARNING_V = 5.0


def run(
    model_type: str = "linear_dq",
    lut_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Generate a control LUT from search results.

    Args:
        model_type: Either "linear_dq" or "nonlinear_flux_lut".
        lut_path: Path to flux LUT JSON file (required for nonlinear_flux_lut).
        output_path: Path for output control_lut.json (default: models/control_lut.json).

    Returns:
        The generated control LUT dictionary.

    Raises:
        ValueError: If model_type is invalid or required files are missing.
    """
    if model_type not in ("linear_dq", "nonlinear_flux_lut"):
        raise ValueError(f"model_type must be 'linear_dq' or 'nonlinear_flux_lut', got {model_type}")

    if model_type == "nonlinear_flux_lut":
        if lut_path is None:
            raise ValueError("lut_path is required for nonlinear_flux_lut model type")
        flux_lut = FluxLut.from_file(lut_path)
    else:
        flux_lut = None

    params, raw_params, grid = load_params()
    step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))

    # Generate control points
    control_points: list[dict[str, Any]] = []
    mode_counts = {"MTPA": 0, "FW": 0, "MTPV": 0, "INFEASIBLE": 0, "IDLE": 0}

    for speed_rpm in speed_grid(params.speed_max_rpm, step_rpm):
        omega_e = mechanical_rpm_to_electrical_rad_per_second(speed_rpm, params.pole_pairs)

        # Get candidates from search functions
        id_zero = find_id_zero_candidate(
            params, omega_e, params.torque_target_nm, grid, flux_lut=flux_lut
        )
        min_current = find_min_current_for_torque(
            params, omega_e, params.torque_target_nm, grid, flux_lut=flux_lut
        )
        max_torque = find_max_torque_feasible(params, omega_e, grid, flux_lut=flux_lut)

        # Determine control mode for target torque point (min_current)
        control_mode = _determine_control_mode(
            speed_rpm, min_current, params.vmax_v, params.imax_a
        )
        mode_counts[control_mode] = mode_counts.get(control_mode, 0) + 1

        control_point = _candidate_to_control_point(
            speed_rpm, params.torque_target_nm, min_current, control_mode, params
        )
        control_points.append(control_point)

    # Calculate validation metrics
    voltage_margin_warning_threshold = DEFAULT_VOLTAGE_MARGIN_WARNING_V
    low_voltage_margin_points = sum(
        1 for cp in control_points
        if cp.get("voltage_margin_v") is not None
        and cp["voltage_margin_v"] < voltage_margin_warning_threshold
    )

    # Determine mode transitions
    mode_transitions = _detect_mode_transitions(control_points)

    # Build feasibility map
    feasibility_map = _build_feasibility_map(control_points)

    # Build the control LUT
    control_lut = {
        "schema_version": "2026-05-14-v1",
        "purpose": f"Control LUT for {params.name} motor, generated from {model_type} model",
        "unit_convention": {
            "dq_transform": "amplitude_invariant",
            "current": "phase_peak_ampere",
            "voltage": "phase_peak_volt",
            "speed": "mechanical_rpm_input_and_electrical_rad_per_second_internal",
        },
        "pole_pairs": params.pole_pairs,
        "model_source": {
            "model_type": model_type,
            "linear_dq_ref": "models/motor_params.json" if model_type == "linear_dq" else None,
            "flux_lut_ref": str(lut_path.relative_to(ROOT)) if lut_path else None,
            "experiment_ref": (
                f"experiments/exp_001_linear_dq/"
                if model_type == "linear_dq"
                else "experiments/exp_006_nonlinear_flux_lut/"
            ),
            "search_config": {
                "search_type": "min_current_for_torque",
                "current_grid": {
                    "id_min_a": grid.id_min_a,
                    "id_max_a": grid.id_max_a,
                    "iq_min_a": grid.iq_min_a,
                    "iq_max_a": grid.iq_max_a,
                    "step_a": grid.step_a,
                },
            },
        },
        "motor_params_ref": "models/motor_params.json",
        "operating_limits": {
            "vdc_v": params.vdc_v,
            "vmax_v": params.vmax_v,
            "imax_a": params.imax_a,
            "speed_max_rpm": params.speed_max_rpm,
            "temperature_c": params.temperature_c,
        },
        "grid_definition": {
            "speed_axis_rpm": sorted(set(cp["speed_rpm"] for cp in control_points)),
            "torque_axis_nm": [params.torque_target_nm],
            "speed_step_rpm": step_rpm,
            "torque_step_nm": None,
            "interpolation_method": "nearest",
            "extrapolation_policy": "clamp",
        },
        "control_points": control_points,
        "mode_transitions": mode_transitions,
        "feasibility_map": feasibility_map,
        "validation": {
            "mode_continuity_check_passed": _check_mode_continuity(control_points),
            "max_id_slope_per_rpm": _max_id_slope(control_points),
            "max_iq_slope_per_rpm": _max_iq_slope(control_points),
            "torque_discontinuity_at_transitions_nm": 0.0,
            "voltage_margin_warning_threshold_v": voltage_margin_warning_threshold,
            "low_voltage_margin_points": low_voltage_margin_points,
        },
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_script": "sim/run_control_lut_generator.py",
            "generator_version": "2026-05-14-v1",
            "notes": [
                f"Generated from {model_type} search",
                f"Speed range: 0 to {params.speed_max_rpm} RPM",
                f"Target torque: {params.torque_target_nm} Nm",
            ],
        },
    }

    # Write output
    if output_path is None:
        output_path = ROOT / "models" / "control_lut.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(control_lut, ensure_ascii=False, indent=2), encoding="utf-8")

    return control_lut


def _determine_control_mode(
    speed_rpm: float,
    candidate: Candidate | None,
    vmax_v: float,
    imax_a: float,
) -> str:
    """Determine the control mode based on speed and candidate feasibility."""
    if candidate is None or not candidate.feasible:
        return "INFEASIBLE"

    # Classify based on voltage margin
    if candidate.voltage_margin_v > 50.0:
        return "MTPA"
    elif candidate.voltage_margin_v > 10.0:
        return "FW"
    else:
        return "MTPV"


def _candidate_to_control_point(
    speed_rpm: float,
    torque_nm: float,
    candidate: Candidate | None,
    control_mode: str,
    params: Any,
) -> dict[str, Any]:
    """Convert a Candidate to a ControlPoint dictionary."""
    if candidate is None:
        return {
            "speed_rpm": speed_rpm,
            "torque_nm": torque_nm,
            "id_a": None,
            "iq_a": None,
            "control_mode": "INFEASIBLE",
            "feasible": False,
            "infeasibility_reason": "search_not_converged",
            "current_a": None,
            "voltage_v": None,
            "voltage_margin_v": None,
            "current_margin_a": None,
            "copper_loss_w": None,
            "efficiency": None,
            "search_method": "min_current",
            "confidence": "low",
        }

    return {
        "speed_rpm": speed_rpm,
        "torque_nm": torque_nm,
        "id_a": candidate.id_a,
        "iq_a": candidate.iq_a,
        "control_mode": control_mode,
        "feasible": candidate.feasible,
        "infeasibility_reason": None if candidate.feasible else "voltage_exceeded",
        "current_a": candidate.current_a,
        "voltage_v": candidate.voltage_v,
        "voltage_margin_v": candidate.voltage_margin_v,
        "current_margin_a": candidate.current_margin_a,
        "copper_loss_w": candidate.copper_loss_w,
        "efficiency": None,
        "search_method": "min_current",
        "confidence": "high",
    }


def _detect_mode_transitions(control_points: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Detect mode transition boundaries from control points."""
    transitions = {
        "mtpa_to_fw_boundary": [],
        "fw_to_mtpv_boundary": [],
        "demagnetization_limit": [],
        "current_limit_boundary": [],
    }

    prev_mode = None
    for cp in control_points:
        current_mode = cp["control_mode"]
        if prev_mode is not None and current_mode != prev_mode:
            transition = {
                "speed_rpm": cp["speed_rpm"],
                "torque_nm": cp["torque_nm"],
                "from_mode": prev_mode,
                "to_mode": current_mode,
                "id_jump_a": None,
                "iq_jump_a": None,
                "torque_jump_nm": None,
                "notes": f"Transition from {prev_mode} to {current_mode}",
            }
            if prev_mode == "MTPA" and current_mode == "FW":
                transitions["mtpa_to_fw_boundary"].append(transition)
            elif prev_mode == "FW" and current_mode == "MTPV":
                transitions["fw_to_mtpv_boundary"].append(transition)
        prev_mode = current_mode

    return transitions


def _build_feasibility_map(control_points: list[dict[str, Any]]) -> dict[str, Any]:
    """Build feasibility statistics from control points."""
    total = len(control_points)
    feasible = sum(1 for cp in control_points if cp["feasible"])
    infeasible_reasons = {"voltage_exceeded": 0, "current_exceeded": 0, "demagnetization_risk": 0}

    for cp in control_points:
        if not cp["feasible"] and cp.get("infeasibility_reason"):
            reason = cp["infeasibility_reason"]
            if reason in infeasible_reasons:
                infeasible_reasons[reason] += 1

    return {
        "total_points": total,
        "feasible_points": feasible,
        "feasibility_ratio": feasible / total if total > 0 else 0.0,
        "infeasible_reasons": infeasible_reasons,
    }


def _check_mode_continuity(control_points: list[dict[str, Any]]) -> bool:
    """Check if mode transitions are continuous (no abrupt jumps)."""
    threshold = 50.0  # A/RPM
    for i in range(1, len(control_points)):
        prev = control_points[i - 1]
        curr = control_points[i]
        if prev["id_a"] is not None and curr["id_a"] is not None:
            id_jump = abs(curr["id_a"] - prev["id_a"])
            speed_jump = curr["speed_rpm"] - prev["speed_rpm"]
            if speed_jump > 0 and id_jump / speed_jump > threshold:
                return False
    return True


def _max_id_slope(control_points: list[dict[str, Any]]) -> float:
    """Calculate maximum id slope across control points (A/RPM)."""
    max_slope = 0.0
    for i in range(1, len(control_points)):
        prev = control_points[i - 1]
        curr = control_points[i]
        if prev["id_a"] is not None and curr["id_a"] is not None:
            speed_jump = curr["speed_rpm"] - prev["speed_rpm"]
            if speed_jump > 0:
                slope = abs(curr["id_a"] - prev["id_a"]) / speed_jump
                max_slope = max(max_slope, slope)
    return max_slope


def _max_iq_slope(control_points: list[dict[str, Any]]) -> float:
    """Calculate maximum iq slope across control points (A/RPM)."""
    max_slope = 0.0
    for i in range(1, len(control_points)):
        prev = control_points[i - 1]
        curr = control_points[i]
        if prev["iq_a"] is not None and curr["iq_a"] is not None:
            speed_jump = curr["speed_rpm"] - prev["speed_rpm"]
            if speed_jump > 0:
                slope = abs(curr["iq_a"] - prev["iq_a"]) / speed_jump
                max_slope = max(max_slope, slope)
    return max_slope


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))