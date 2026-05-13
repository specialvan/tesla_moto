from __future__ import annotations

import json
from pathlib import Path

from sim.run_winding_reconfiguration_experiment import (
    DEFAULT_CONFIGS,
    DEFAULT_TRANSITION_SPEED_RPM,
    run,
)


def test_winding_reconfiguration_experiment_writes_summary_and_csv() -> None:
    summary = run()
    summary_path = Path(
        "experiments/exp_008_winding_reconfiguration/summary.json"
    )
    csv_path = Path(
        "experiments/exp_008_winding_reconfiguration/winding_reconfiguration_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_008_winding_reconfiguration"
    assert summary["row_count"] == len(DEFAULT_CONFIGS)
    assert summary["transition_speed_rpm"] == DEFAULT_TRANSITION_SPEED_RPM
    assert len(summary["transitions"]) == len(DEFAULT_CONFIGS) - 1

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "recommended_config" in saved
    if saved["recommended_config"] is not None:
        assert saved["recommended_config"]["target_max_speed_rpm"] is not None

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("config,turns_scale,resistance_scale,")


def test_winding_reconfiguration_transition_check_returns_deltas_when_feasible() -> None:
    summary = run()
    transitions = summary["transitions"]
    assert transitions, "expected at least one transition"
    feasible_transitions = [t for t in transitions if t["feasible"]]
    for transition in feasible_transitions:
        assert transition["torque_delta_nm"] is not None
        assert transition["current_delta_a"] is not None
