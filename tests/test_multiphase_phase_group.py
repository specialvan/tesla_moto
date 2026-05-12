from __future__ import annotations

import json
from math import isclose
from pathlib import Path

from sim.multiphase_phase_group import PhaseGroupCase, derated_current_limit
from sim.run_multiphase_phase_group_experiment import run


def test_phase_group_derating_reduces_current_limit_for_lost_group() -> None:
    case = PhaseGroupCase(
        name="one_group_lost",
        total_groups=3,
        healthy_groups=2,
        per_group_current_limit_a=90.0,
        sharing_imbalance_ratio=0.08,
    )

    derated = derated_current_limit(case)

    assert isclose(derated["available_current_a"], 166.66666666666666, rel_tol=1e-12)
    assert isclose(derated["group_utilization"], 1.08, rel_tol=1e-12)


def test_multiphase_phase_group_experiment_writes_derating_artifacts() -> None:
    summary = run(speed_step_rpm=1000.0)
    summary_path = Path("experiments/exp_009_multiphase_phase_group/summary.json")
    csv_path = Path(
        "experiments/exp_009_multiphase_phase_group/multiphase_phase_group_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_009_multiphase_phase_group"
    assert (
        summary["worst_case"]["healthy_groups"] < summary["worst_case"]["total_groups"]
    )
    assert summary["case_count"] >= 3

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "available_current_a" in header
    assert "group_utilization" in header
    assert "target_max_speed_rpm" in header

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["model_scope"] == "linear_dq_with_phase_group_current_derating"
