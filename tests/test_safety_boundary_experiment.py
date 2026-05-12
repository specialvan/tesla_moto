from __future__ import annotations

import json
from pathlib import Path

from sim.run_safety_boundary_experiment import run


def test_safety_boundary_experiment_writes_summary_and_csv() -> None:
    summary = run()
    summary_path = Path("experiments/exp_004_safety_boundaries/summary.json")
    csv_path = Path("experiments/exp_004_safety_boundaries/safety_boundary_results.csv")

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_004_safety_boundaries"
    assert summary["case_count"] > 1

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["worst_case"]["temperature_c"] >= 25.0
    assert "demag_limited_target_max_speed_rpm" in saved["worst_case"]
    assert csv_path.read_text(encoding="utf-8").splitlines()[0].startswith("case_id,")
