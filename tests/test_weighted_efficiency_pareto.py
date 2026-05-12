from __future__ import annotations

import json
from pathlib import Path

from sim.weighted_efficiency_pareto import weighted_score
from sim.run_weighted_efficiency_pareto_experiment import run


def test_weighted_score_rewards_speed_and_penalizes_loss() -> None:
    score = weighted_score(
        target_max_speed_rpm=7000.0,
        loss_w=3500.0,
        risk_penalty=0.12,
        weights={"speed": 0.65, "loss": 0.25, "risk": 0.10},
    )

    assert score == 0.65 * 7000.0 - 0.25 * 3.5 - 0.10 * 1200.0


def test_weighted_efficiency_pareto_experiment_writes_ranked_artifacts() -> None:
    summary = run()
    summary_path = Path("experiments/exp_010_weighted_efficiency_pareto/summary.json")
    csv_path = Path(
        "experiments/exp_010_weighted_efficiency_pareto/weighted_efficiency_pareto_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_010_weighted_efficiency_pareto"
    assert summary["candidate_count"] >= 4
    assert (
        summary["top_candidate"]["weighted_score"]
        >= summary["ranked_candidates"][-1]["weighted_score"]
    )

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "scheme_id" in header
    assert "weighted_score" in header
    assert "source_experiment" in header

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["model_scope"] == "traceable_weighted_scheme_selection"
