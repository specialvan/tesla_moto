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

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .nonlinear_flux_lut import FluxLut
from .run_linear_dq_experiment import load_params, speed_grid
from .safety_limits import DemagLimit, ThermalModel, apply_temperature
from .search import (
    Candidate,
    GridSpec,
    current_grid,
    make_candidate,
)
from .dq_model import mechanical_rpm_to_electrical_rad_per_second

ROOT = Path(__file__).resolve().parents[1]


# Default voltage margin warning threshold (V)
DEFAULT_VOLTAGE_MARGIN_WARNING_V = 5.0


def run(
    model_type: str = "linear_dq",
    lut_path: Path | None = None,
    output_path: Path | None = None,
    temperature_c: float | None = None,
    thermal_model: ThermalModel | None = None,
    demag_limit: DemagLimit | None = None,
    torque_axis_nm: list[float] | None = None,
    torque_step_nm: float | None = None,
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
        raise ValueError(
            f"model_type must be 'linear_dq' or 'nonlinear_flux_lut', got {model_type}"
        )

    if model_type == "nonlinear_flux_lut":
        if lut_path is None:
            raise ValueError("lut_path is required for nonlinear_flux_lut model type")
        resolved_lut_path = (
            lut_path if lut_path.is_absolute() else ROOT / lut_path
        ).resolve()
        try:
            resolved_lut_path.relative_to(ROOT)
        except ValueError as exc:
            raise ValueError("lut_path must resolve inside the project root") from exc
        flux_lut = FluxLut.from_file(resolved_lut_path)
    else:
        resolved_lut_path = None
        flux_lut = None

    params, raw_params, grid = load_params()
    if temperature_c is not None:
        if thermal_model is None:
            thermal_model = ThermalModel(
                reference_c=25.0,
                copper_alpha_per_c=0.0039,
                pm_alpha_per_c=-0.001,
            )
        params = apply_temperature(params, temperature_c, thermal_model)
    step_rpm = float(raw_params.get("base_speed_scan_step_rpm", 250.0))
    speed_axis_rpm = list(speed_grid(params.speed_max_rpm, step_rpm))
    resolved_torque_axis_nm = _resolve_torque_axis(
        torque_axis_nm, params.torque_target_nm
    )
    resolved_torque_step_nm = _resolve_torque_step(
        resolved_torque_axis_nm, torque_step_nm
    )

    # Generate control points
    control_points: list[dict[str, Any]] = []
    mode_counts = {"MTPA": 0, "FW": 0, "MTPV": 0, "INFEASIBLE": 0, "IDLE": 0}

    for speed_rpm in speed_axis_rpm:
        omega_e = mechanical_rpm_to_electrical_rad_per_second(
            speed_rpm, params.pole_pairs
        )
        for torque_nm in resolved_torque_axis_nm:
            min_current, infeasibility_reason = _find_min_current_with_optional_safety(
                params,
                omega_e,
                torque_nm,
                grid,
                flux_lut=flux_lut,
                demag_limit=demag_limit,
            )

            # Determine control mode for target torque point (min_current)
            control_mode = _determine_control_mode(
                speed_rpm, min_current, params.vmax_v, params.imax_a
            )
            mode_counts[control_mode] = mode_counts.get(control_mode, 0) + 1

            control_point = _candidate_to_control_point(
                speed_rpm,
                torque_nm,
                min_current,
                control_mode,
                params,
                infeasibility_reason=infeasibility_reason,
            )
            control_points.append(control_point)

    # Calculate validation metrics
    voltage_margin_warning_threshold = DEFAULT_VOLTAGE_MARGIN_WARNING_V
    low_voltage_margin_points = sum(
        1
        for cp in control_points
        if cp.get("voltage_margin_v") is not None
        and cp["voltage_margin_v"] < voltage_margin_warning_threshold
    )

    # Determine mode transitions
    mode_transitions = _detect_mode_transitions(control_points)
    if demag_limit is not None:
        _add_demag_limit_transition(mode_transitions, control_points)

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
            "linear_dq_ref": (
                "models/motor_params.json" if model_type == "linear_dq" else None
            ),
            "flux_lut_ref": (
                resolved_lut_path.relative_to(ROOT).as_posix()
                if resolved_lut_path
                else None
            ),
            "experiment_ref": (
                "experiments/exp_001_linear_dq/"
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
            "speed_axis_rpm": speed_axis_rpm,
            "torque_axis_nm": resolved_torque_axis_nm,
            "speed_step_rpm": step_rpm,
            "torque_step_nm": resolved_torque_step_nm,
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
            "torque_discontinuity_at_transitions_nm": _max_transition_torque_jump(
                mode_transitions
            ),
            "voltage_margin_warning_threshold_v": voltage_margin_warning_threshold,
            "low_voltage_margin_points": low_voltage_margin_points,
        },
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_script": "sim/run_control_lut_generator.py",
            "generator_version": "2026-05-14-v1",
            "demag_limit": _demag_limit_metadata(demag_limit, params.temperature_c),
            "notes": [
                f"Generated from {model_type} search",
                f"Speed range: 0 to {params.speed_max_rpm} RPM",
                f"Torque axis: {resolved_torque_axis_nm[0]} to {resolved_torque_axis_nm[-1]} Nm",
            ],
        },
    }

    # Write output
    if output_path is None:
        output_path = ROOT / "models" / "control_lut.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(control_lut, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return control_lut


def _resolve_torque_axis(
    torque_axis_nm: list[float] | None, default_torque_nm: float
) -> list[float]:
    source_axis = [default_torque_nm] if torque_axis_nm is None else torque_axis_nm
    resolved = [float(torque_nm) for torque_nm in source_axis]
    if not resolved:
        raise ValueError("torque_axis_nm must not be empty")
    if any(not math.isfinite(torque_nm) for torque_nm in resolved):
        raise ValueError("torque_axis_nm values must be finite")
    if any(torque_nm < 0.0 for torque_nm in resolved):
        raise ValueError("torque_axis_nm values must be non-negative")
    if any(right <= left for left, right in zip(resolved, resolved[1:])):
        raise ValueError("torque_axis_nm must be strictly increasing")
    return resolved


def _resolve_torque_step(
    torque_axis_nm: list[float], explicit_torque_step_nm: float | None
) -> float | None:
    if explicit_torque_step_nm is not None:
        resolved_step = float(explicit_torque_step_nm)
        if not math.isfinite(resolved_step):
            raise ValueError("torque_step_nm must be finite")
        if resolved_step <= 0.0:
            raise ValueError("torque_step_nm must be positive")
        return resolved_step
    if len(torque_axis_nm) < 2:
        return 0.0
    first_step = torque_axis_nm[1] - torque_axis_nm[0]
    if all(
        abs((right - left) - first_step) < 1e-9
        for left, right in zip(torque_axis_nm, torque_axis_nm[1:])
    ):
        return first_step
    return None


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
    infeasibility_reason: str | None = None,
) -> dict[str, Any]:
    """Convert a Candidate to a ControlPoint dictionary."""
    if candidate is None:
        return {
            "speed_rpm": speed_rpm,
            "torque_nm": torque_nm,
            "id_a": None,
            "iq_a": None,
            "actual_torque_nm": None,
            "control_mode": "INFEASIBLE",
            "feasible": False,
            "infeasibility_reason": infeasibility_reason or "search_not_converged",
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
        "actual_torque_nm": candidate.torque_nm,
        "control_mode": control_mode,
        "feasible": candidate.feasible,
        "infeasibility_reason": _candidate_infeasibility_reason(
            candidate, infeasibility_reason or "search_not_converged"
        ),
        "current_a": candidate.current_a,
        "voltage_v": candidate.voltage_v,
        "voltage_margin_v": candidate.voltage_margin_v,
        "current_margin_a": candidate.current_margin_a,
        "copper_loss_w": candidate.copper_loss_w,
        "efficiency": None,
        "search_method": "min_current",
        "confidence": "high",
    }


def _find_min_current_with_optional_safety(
    params: Any,
    omega_e: float,
    target_torque_nm: float,
    grid: GridSpec,
    flux_lut: FluxLut | None = None,
    demag_limit: DemagLimit | None = None,
) -> tuple[Candidate | None, str | None]:
    id_min_allowed = (
        demag_limit.id_min_allowed(params.temperature_c)
        if demag_limit is not None
        else None
    )
    saw_in_flux_bounds = flux_lut is None
    demag_blocked_target = False
    blocked_reason_counts = {"current_exceeded": 0, "voltage_exceeded": 0}
    best: Candidate | None = None
    best_key: tuple[float, float] | None = None

    for id_a, iq_a in current_grid(grid):
        if flux_lut is not None and not flux_lut.contains(id_a, iq_a):
            continue
        saw_in_flux_bounds = True
        candidate = make_candidate(params, id_a, iq_a, omega_e, flux_lut=flux_lut)
        if candidate.torque_nm < target_torque_nm:
            continue
        if id_min_allowed is not None and id_a < id_min_allowed:
            demag_blocked_target = True
            continue
        if not candidate.feasible:
            reason = _candidate_infeasibility_reason(candidate)
            if reason in blocked_reason_counts:
                blocked_reason_counts[reason] += 1
            continue
        key = (candidate.current_a, abs(candidate.torque_nm - target_torque_nm))
        if best_key is None or key < best_key:
            best = candidate
            best_key = key

    if best is not None:
        return best, None
    if flux_lut is not None and not saw_in_flux_bounds:
        return None, "out_of_flux_lut_bounds"
    if demag_blocked_target:
        return None, "demagnetization_risk"
    if blocked_reason_counts["voltage_exceeded"] > 0:
        return None, "voltage_exceeded"
    if blocked_reason_counts["current_exceeded"] > 0:
        return None, "current_exceeded"
    return None, "search_not_converged"


def _candidate_infeasibility_reason(
    candidate: Candidate | None,
    fallback_reason: str = "search_not_converged",
) -> str | None:
    if candidate is None:
        return fallback_reason
    if candidate.feasible:
        return None
    if candidate.current_margin_a < 0.0:
        return "current_exceeded"
    if candidate.voltage_margin_v < 0.0:
        return "voltage_exceeded"
    return fallback_reason


def _demag_limit_metadata(
    demag_limit: DemagLimit | None, temperature_c: float
) -> dict[str, Any] | None:
    if demag_limit is None:
        return None
    return {
        "points_c_to_id_min_a": [
            {"temperature_c": temperature, "id_min_a": id_min}
            for temperature, id_min in demag_limit.points_c_to_id_min_a
        ],
        "effective_temperature_c": temperature_c,
        "effective_id_min_a": demag_limit.id_min_allowed(temperature_c),
    }


def _detect_mode_transitions(
    control_points: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Detect mode transition boundaries from control points."""
    transitions: dict[str, list[dict[str, Any]]] = {
        "mtpa_to_fw_boundary": [],
        "fw_to_mtpv_boundary": [],
        "demagnetization_limit": [],
        "current_limit_boundary": [],
    }

    for torque_slice in _control_points_by_torque(control_points):
        prev_cp = None
        for cp in torque_slice:
            current_mode = cp["control_mode"]
            if prev_cp is not None and current_mode != prev_cp["control_mode"]:
                prev_mode = prev_cp["control_mode"]
                transition = _transition_point(prev_cp, cp, prev_mode, current_mode)
                if prev_mode == "MTPA" and current_mode == "FW":
                    transitions["mtpa_to_fw_boundary"].append(transition)
                elif prev_mode == "FW" and current_mode == "MTPV":
                    transitions["fw_to_mtpv_boundary"].append(transition)
            prev_cp = cp

    return transitions


def _control_points_by_torque(
    control_points: list[dict[str, Any]]
) -> list[list[dict[str, Any]]]:
    torque_values = sorted({float(cp["torque_nm"]) for cp in control_points})
    return [
        sorted(
            [cp for cp in control_points if float(cp["torque_nm"]) == torque_nm],
            key=lambda cp: float(cp["speed_rpm"]),
        )
        for torque_nm in torque_values
    ]


def _transition_point(
    prev_cp: dict[str, Any],
    cp: dict[str, Any],
    prev_mode: str,
    current_mode: str,
) -> dict[str, Any]:
    return {
        "speed_rpm": cp["speed_rpm"],
        "torque_nm": cp["torque_nm"],
        "from_mode": prev_mode,
        "to_mode": current_mode,
        "id_jump_a": _abs_delta(prev_cp.get("id_a"), cp.get("id_a")),
        "iq_jump_a": _abs_delta(prev_cp.get("iq_a"), cp.get("iq_a")),
        "torque_jump_nm": _abs_delta(
            _transition_torque_for_jump(prev_cp), _transition_torque_for_jump(cp)
        ),
        "notes": f"Transition from {prev_mode} to {current_mode}",
    }


def _transition_torque_for_jump(cp: dict[str, Any]) -> Any:
    actual_torque = cp.get("actual_torque_nm")
    if actual_torque is not None:
        return actual_torque
    return cp.get("torque_nm")


def _abs_delta(left: Any, right: Any) -> float | None:
    if left is None or right is None:
        return None
    return abs(float(right) - float(left))


def _add_demag_limit_transition(
    mode_transitions: dict[str, list[dict[str, Any]]],
    control_points: list[dict[str, Any]],
) -> None:
    demag_points = [
        cp
        for cp in control_points
        if cp.get("infeasibility_reason") == "demagnetization_risk"
    ]
    if not demag_points:
        return
    first = demag_points[0]
    mode_transitions["demagnetization_limit"].append(
        {
            "speed_rpm": first["speed_rpm"],
            "torque_nm": first["torque_nm"],
            "from_mode": "FW",
            "to_mode": "MTPV",
            "id_jump_a": None,
            "iq_jump_a": None,
            "torque_jump_nm": None,
            "notes": "Demagnetization limit rejected target operating point",
        }
    )


def _max_transition_torque_jump(
    mode_transitions: dict[str, list[dict[str, Any]]]
) -> float:
    max_jump = 0.0
    for transitions in mode_transitions.values():
        for transition in transitions:
            torque_jump = transition.get("torque_jump_nm")
            if torque_jump is not None:
                max_jump = max(max_jump, float(torque_jump))
    return max_jump


def _build_feasibility_map(control_points: list[dict[str, Any]]) -> dict[str, Any]:
    """Build feasibility statistics from control points."""
    total = len(control_points)
    feasible = sum(1 for cp in control_points if cp["feasible"])
    infeasible_reasons = {
        "voltage_exceeded": 0,
        "current_exceeded": 0,
        "demagnetization_risk": 0,
        "out_of_flux_lut_bounds": 0,
        "search_not_converged": 0,
    }

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
    return _max_id_slope(control_points) <= threshold


def _max_id_slope(control_points: list[dict[str, Any]]) -> float:
    """Calculate maximum id slope across control points (A/RPM)."""
    return _max_current_slope(control_points, "id_a")


def _max_iq_slope(control_points: list[dict[str, Any]]) -> float:
    """Calculate maximum iq slope across control points (A/RPM)."""
    return _max_current_slope(control_points, "iq_a")


def _max_current_slope(control_points: list[dict[str, Any]], current_key: str) -> float:
    max_slope = 0.0
    for torque_slice in _control_points_by_torque(control_points):
        for i in range(1, len(torque_slice)):
            prev = torque_slice[i - 1]
            curr = torque_slice[i]
            if prev[current_key] is not None and curr[current_key] is not None:
                speed_jump = curr["speed_rpm"] - prev["speed_rpm"]
                if speed_jump > 0:
                    slope = abs(curr[current_key] - prev[current_key]) / speed_jump
                    max_slope = max(max_slope, slope)
    return max_slope


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
