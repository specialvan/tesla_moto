"""Run EXP-006: nonlinear flux LUT interpolation and torque ranking."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .nonlinear_flux_lut import FluxLut, nonlinear_torque_nm
from .run_linear_dq_experiment import PARAMS_PATH

ROOT = Path(__file__).resolve().parents[1]
LUT_PATH = ROOT / "models" / "flux_lut_sample.json"
OUTPUT_DIR = ROOT / "experiments" / "exp_006_nonlinear_flux_lut"


def run() -> dict[str, Any]:
    params = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    lut = FluxLut.from_file(LUT_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for id_a in lut.id_axis_a:
        for iq_a in lut.iq_axis_a:
            lambdas = lut.interpolate(id_a, iq_a)
            rows.append(
                {
                    "id_a": id_a,
                    "iq_a": iq_a,
                    "lambda_d_wb": lambdas.lambda_d_wb,
                    "lambda_q_wb": lambdas.lambda_q_wb,
                    "torque_nm": nonlinear_torque_nm(
                        lut, int(params["pole_pairs"]), id_a, iq_a
                    ),
                }
            )

    csv_path = OUTPUT_DIR / "nonlinear_flux_lut_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best_torque_point = max(rows, key=lambda row: float(row["torque_nm"]))
    summary = {
        "experiment": "exp_006_nonlinear_flux_lut",
        "parameter_source": "synthetic_clean_room_flux_lut",
        "engineering_validated": False,
        "model_scope": "synthetic_lambda_d_lambda_q_lut_interpolation",
        "model_limitations": [
            "sample LUT is synthetic and not FEA-derived",
            "only interpolation and torque consistency are validated",
            "no voltage, loss, thermal, or demagnetization coupling yet",
        ],
        "lut_path": str(LUT_PATH),
        "id_axis_a": lut.id_axis_a,
        "iq_axis_a": lut.iq_axis_a,
        "grid_points": len(rows),
        "best_torque_point": best_torque_point,
        "csv_path": str(csv_path),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
