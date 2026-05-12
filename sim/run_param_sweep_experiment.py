"""Run EXP-003: sweep ψf/Ld/Lq/Vdc/Imax parameter families."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dq_model import mechanical_rpm_to_electrical_rad_per_second
from .param_sweep import ParamVariant, variant_grid
from .run_linear_dq_experiment import load_params
from .search import (
    Candidate,
    GridSpec,
    find_max_torque_feasible,
    find_min_current_for_torque,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_003_param_sweep"

PSI_SCALES = [1.0, 0.85, 0.70]
LD_SCALES = [0.8, 1.0, 1.2]
LQ_SCALES = [1.0, 1.3, 1.6]
VDC_SCALES = [1.0, 1.15]
IMAX_SCALES = [1.0, 1.15]
LOW_SPEED_RPM = 1000.0
HIGH_SPEED_RPM = 12000.0
PEAK_TORQUE_TARGET_NM = 100.0
HIGH_SPEED_TORQUE_TARGET_NM = 60.0


def scale_grid_for_variant(base_grid: GridSpec, variant: ParamVariant) -> GridSpec:
    imax_ratio = variant.imax_scale
    return GridSpec(
        id_min_a=base_grid.id_min_a * imax_ratio,
        id_max_a=base_grid.id_max_a * imax_ratio,
        iq_min_a=base_grid.iq_min_a * imax_ratio,
        iq_max_a=base_grid.iq_max_a * imax_ratio,
        step_a=base_grid.step_a,
    )


def safe_metrics(candidate: Candidate | None) -> dict[str, float | bool | None]:
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


def evaluate_variant(variant: ParamVariant, grid: Any) -> dict[str, Any]:
    params = variant.params
    low_omega = mechanical_rpm_to_electrical_rad_per_second(
        LOW_SPEED_RPM, params.pole_pairs
    )
    high_omega = mechanical_rpm_to_electrical_rad_per_second(
        HIGH_SPEED_RPM, params.pole_pairs
    )
    low_peak = find_min_current_for_torque(
        params, low_omega, PEAK_TORQUE_TARGET_NM, grid
    )
    high_target = find_min_current_for_torque(
        params, high_omega, HIGH_SPEED_TORQUE_TARGET_NM, grid
    )
    high_max = find_max_torque_feasible(params, high_omega, grid)

    low_metrics = safe_metrics(low_peak)
    high_target_metrics = safe_metrics(high_target)
    high_max_metrics = safe_metrics(high_max)
    score = score_variant(low_metrics, high_target_metrics, high_max_metrics)

    return {
        "variant": variant.name,
        "psi_scale": variant.psi_scale,
        "ld_scale": variant.ld_scale,
        "lq_scale": variant.lq_scale,
        "vdc_scale": variant.vdc_scale,
        "imax_scale": variant.imax_scale,
        "psi_f_wb": params.psi_f_wb,
        "ld_h": params.ld_h,
        "lq_h": params.lq_h,
        "saliency_ratio": variant.saliency_ratio,
        "vdc_v": params.vdc_v,
        "imax_a": params.imax_a,
        "score": score,
        **{f"low_peak_{key}": value for key, value in low_metrics.items()},
        **{f"high_target_{key}": value for key, value in high_target_metrics.items()},
        **{f"high_max_{key}": value for key, value in high_max_metrics.items()},
    }


def score_variant(
    low_peak: dict[str, float | bool | None],
    high_target: dict[str, float | bool | None],
    high_max: dict[str, float | bool | None],
) -> float:
    if not low_peak["feasible"]:
        return -1_000_000.0
    if not high_target["feasible"]:
        return -500_000.0
    high_margin = float(high_target["voltage_margin_v"] or 0.0)
    low_loss = float(low_peak["copper_loss_w"] or 0.0)
    high_loss = float(high_target["copper_loss_w"] or 0.0)
    high_max_torque = float(high_max["torque_nm"] or 0.0)
    high_id_penalty = abs(float(high_target["id_a"] or 0.0))
    return (
        high_margin
        + 0.25 * high_max_torque
        - 0.002 * (low_loss + high_loss)
        - 0.05 * high_id_penalty
    )


def run() -> dict[str, Any]:
    base_params, _, grid = load_params()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = [
        evaluate_variant(variant, scale_grid_for_variant(grid, variant))
        for variant in variant_grid(
            base_params,
            PSI_SCALES,
            LD_SCALES,
            LQ_SCALES,
            VDC_SCALES,
            IMAX_SCALES,
        )
    ]
    ranked_rows = sorted(rows, key=lambda row: float(row["score"]), reverse=True)

    csv_path = OUTPUT_DIR / "param_sweep_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(ranked_rows)

    summary = {
        "experiment": "exp_003_param_sweep",
        "parameter_source": "illustrative_clean_room_baseline_scaled_family",
        "engineering_validated": False,
        "model_scope": "quasi_steady_linear_dq_scaled_parameter_family",
        "model_limitations": [
            "scaled Ld/Lq/psi_f do not represent a validated geometry",
            "no nonlinear saturation or cross-saturation LUT",
            "no demagnetization boundary",
            "no iron loss, inverter loss, mechanical loss, or thermal derating",
            "score is heuristic and only ranks candidates for deeper FEA",
        ],
        "sweep_axes": {
            "psi_scales": PSI_SCALES,
            "ld_scales": LD_SCALES,
            "lq_scales": LQ_SCALES,
            "vdc_scales": VDC_SCALES,
            "imax_scales": IMAX_SCALES,
        },
        "evaluation_points": {
            "low_speed_rpm": LOW_SPEED_RPM,
            "peak_torque_target_nm": PEAK_TORQUE_TARGET_NM,
            "high_speed_rpm": HIGH_SPEED_RPM,
            "high_speed_torque_target_nm": HIGH_SPEED_TORQUE_TARGET_NM,
        },
        "variant_count": len(rows),
        "top_candidates": ranked_rows[:10],
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
