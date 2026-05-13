from __future__ import annotations

import json
from pathlib import Path

from sim.run_multiphase_phase_group_experiment import DEFAULT_CASES, run


def test_multiphase_phase_group_experiment_writes_summary_and_csv() -> None:
    summary = run()
    summary_path = Path(
        "experiments/exp_009_multiphase_phase_group/summary.json"
    )
    csv_path = Path(
        "experiments/exp_009_multiphase_phase_group/multiphase_phase_group_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_009_multiphase_phase_group"
    assert summary["case_count"] == len(DEFAULT_CASES)

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    worst = saved["worst_case"]
    # The limp-home case has the lowest healthy_group_ratio so it should be
    # picked when speed reachability ties at None.
    assert worst["healthy_group_ratio"] <= 1.0


def test_multiphase_phase_group_csv_has_expected_header() -> None:
    run()
    header = Path(
        "experiments/exp_009_multiphase_phase_group/multiphase_phase_group_results.csv"
    ).read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith(
        "case,total_groups,healthy_groups,per_group_current_limit_a,"
    )
