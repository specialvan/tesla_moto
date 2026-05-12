from __future__ import annotations

import csv
import json
from math import isfinite
from pathlib import Path

from sim.control_search import (
    field_weakening_search,
    mtpa_grid_search,
    mtpv_grid_search,
)
from sim.dq_model import MotorParams


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMS_PATH = ROOT / "models" / "motor_params.json"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "exp_001_linear_dq"


def load_motor_params(params_path: Path = DEFAULT_PARAMS_PATH) -> MotorParams:
    raw = json.loads(params_path.read_text(encoding="utf-8"))
    return MotorParams.from_dict(raw)


def _speed_points(max_speed_rpm: float, step_rpm: float) -> list[float]:
    count = int(max_speed_rpm // step_rpm)
    points = [index * step_rpm for index in range(count + 1)]
    if points[-1] < max_speed_rpm:
        points.append(max_speed_rpm)
    return points


def _csv_value(value: float | bool | str) -> float | bool | str | None:
    if isinstance(value, float) and not isfinite(value):
        return None
    return value


def run_experiment(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    params_path: Path = DEFAULT_PARAMS_PATH,
    speed_step_rpm: float = 1000.0,
    current_step_a: float = 20.0,
) -> tuple[Path, Path]:
    params = load_motor_params(params_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, float | bool | str | None]] = []
    speed_results: list[dict[str, object]] = []

    for speed_rpm in _speed_points(params.speed_max_rpm, speed_step_rpm):
        mtpa = mtpa_grid_search(params, params.torque_target_nm, current_step_a)
        fw = field_weakening_search(
            params, params.torque_target_nm, speed_rpm, current_step_a
        )
        mtpv = mtpv_grid_search(params, speed_rpm, current_step_a)
        row: dict[str, float | bool | str] = {
            "speed_rpm": speed_rpm,
            "target_torque_nm": params.torque_target_nm,
            "vmax_phase_v": params.vmax_phase_v,
            "i_max_a": params.i_max_a,
            "mtpa_id_a": mtpa.id_a,
            "mtpa_iq_a": mtpa.iq_a,
            "mtpa_current_a": mtpa.current_a,
            "mtpa_torque_nm": mtpa.torque_nm,
            "fw_id_a": fw.id_a,
            "fw_iq_a": fw.iq_a,
            "fw_voltage_v": fw.voltage_v,
            "fw_voltage_margin_v": fw.voltage_margin_v,
            "fw_current_a": fw.current_a,
            "fw_torque_nm": fw.torque_nm,
            "fw_feasible": fw.feasible,
            "mtpv_id_a": mtpv.id_a,
            "mtpv_iq_a": mtpv.iq_a,
            "mtpv_voltage_v": mtpv.voltage_v,
            "mtpv_current_a": mtpv.current_a,
            "mtpv_torque_nm": mtpv.torque_nm,
            "mtpv_feasible": mtpv.feasible,
        }
        rows.append({key: _csv_value(value) for key, value in row.items()})
        speed_results.append(
            {
                "speed_rpm": speed_rpm,
                "mtpa": mtpa.to_dict(),
                "field_weakening": fw.to_dict(),
                "mtpv": mtpv.to_dict(),
            }
        )

    csv_path = output_dir / "scan_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "exp_001_linear_dq",
        "motor": params.name,
        "speed_step_rpm": speed_step_rpm,
        "current_step_a": current_step_a,
        "speed_points": speed_results,
    }
    json_path = output_dir / "summary.json"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return json_path, csv_path


if __name__ == "__main__":
    summary_path, results_path = run_experiment()
    print(f"Wrote {summary_path}")
    print(f"Wrote {results_path}")
