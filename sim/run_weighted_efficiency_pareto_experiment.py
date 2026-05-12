"""Run EXP-010: traceable weighted selection across scheme experiments."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .weighted_efficiency_pareto import weighted_score

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "exp_010_weighted_efficiency_pareto"

WEIGHTS = {"speed": 0.65, "loss": 0.25, "risk": 0.10}


def _read_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _candidates() -> list[dict[str, Any]]:
    exp005 = _read_json("experiments/exp_005_modulation_factor/summary.json")
    exp007 = _read_json("experiments/exp_007_hybrid_excitation/summary.json")
    exp008 = _read_json("experiments/exp_008_winding_reconfiguration/summary.json")
    exp009 = _read_json("experiments/exp_009_multiphase_phase_group/summary.json")

    mod = exp005["best_tradeoff"]
    hybrid = exp007["best_tradeoff"]
    winding = exp008["recommended_config"]
    multiphase = exp009["worst_case"]
    return [
        {
            "scheme_id": "svpwm_overmodulation_voltage_utilization",
            "source_experiment": exp005["experiment"],
            "target_max_speed_rpm": float(mod["target_max_speed_rpm"]),
            "loss_w": float(mod["target_boundary_copper_loss_w"] or 0.0)
            * float(mod["inverter_loss_multiplier"]),
            "risk_penalty": float(mod["harmonic_current_rms_ratio"]),
        },
        {
            "scheme_id": "hybrid_excitation",
            "source_experiment": exp007["experiment"],
            "target_max_speed_rpm": float(hybrid["target_max_speed_rpm"]),
            "loss_w": float(hybrid["combined_loss_w"]),
            "risk_penalty": 0.18,
        },
        {
            "scheme_id": "winding_reconfiguration",
            "source_experiment": exp008["experiment"],
            "target_max_speed_rpm": float(winding["target_max_speed_rpm"]),
            "loss_w": 0.0,
            "risk_penalty": 0.24,
        },
        {
            "scheme_id": "multiphase_phase_group_control",
            "source_experiment": exp009["experiment"],
            "target_max_speed_rpm": (
                0.0
                if multiphase["target_max_speed_rpm"] is None
                else float(multiphase["target_max_speed_rpm"])
            ),
            "loss_w": 0.0,
            "risk_penalty": 0.35,
        },
    ]


def run() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for candidate in _candidates():
        row = dict(candidate)
        row["weighted_score"] = weighted_score(
            row["target_max_speed_rpm"],
            row["loss_w"],
            row["risk_penalty"],
            WEIGHTS,
        )
        rows.append(row)

    ranked = sorted(rows, key=lambda row: float(row["weighted_score"]), reverse=True)
    csv_path = OUTPUT_DIR / "weighted_efficiency_pareto_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ranked[0].keys()))
        writer.writeheader()
        writer.writerows(ranked)

    summary = {
        "experiment": "exp_010_weighted_efficiency_pareto",
        "parameter_source": "derived_from_existing_experiment_summaries",
        "engineering_validated": False,
        "model_scope": "traceable_weighted_scheme_selection",
        "model_limitations": [
            "score weights are v0 engineering assumptions",
            "loss metrics are not normalized to a full drive cycle yet",
            "risk penalty is a numeric screening factor, not a safety case",
        ],
        "weights": WEIGHTS,
        "candidate_count": len(ranked),
        "top_candidate": ranked[0],
        "ranked_candidates": ranked,
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
