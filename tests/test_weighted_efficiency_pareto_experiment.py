from __future__ import annotations

import json
from pathlib import Path

from sim.run_weighted_efficiency_pareto_experiment import (
    DEFAULT_CYCLES,
    build_candidates,
    run,
)


def test_weighted_efficiency_pareto_experiment_writes_summary_and_csv() -> None:
    summary = run()
    summary_path = Path(
        "experiments/exp_010_weighted_efficiency_pareto/summary.json"
    )
    csv_path = Path(
        "experiments/exp_010_weighted_efficiency_pareto/"
        "weighted_efficiency_pareto_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_010_weighted_efficiency_pareto"

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert len(saved["cycles"]) == len(DEFAULT_CYCLES)
    assert "cycle_winners" in saved
    assert "pareto_front" in saved
    assert saved["pareto_front"], "expected non-empty pareto_front"


def test_weighted_efficiency_pareto_each_candidate_appears_per_cycle() -> None:
    summary = run()
    expected_candidates = [name for name, _, _ in build_candidates_from_summary()]
    rows = parse_csv(
        Path(
            "experiments/exp_010_weighted_efficiency_pareto/"
            "weighted_efficiency_pareto_results.csv"
        )
    )
    cycle_names = {cycle["name"] for cycle in summary["cycles"]}
    for cycle_name in cycle_names:
        candidates_for_cycle = {
            row["candidate"] for row in rows if row["cycle"] == cycle_name
        }
        assert candidates_for_cycle == set(expected_candidates), (
            f"missing candidates for cycle {cycle_name}: "
            f"{set(expected_candidates) - candidates_for_cycle}"
        )


def parse_csv(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    header = lines[0].split(",")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        values = line.split(",")
        rows.append(dict(zip(header, values)))
    return rows


def build_candidates_from_summary() -> list[tuple[str, object, object]]:
    # We mirror the runner's candidate construction so both stay in sync.
    from sim.run_linear_dq_experiment import load_params

    base, _, grid = load_params()
    return build_candidates(base, grid)
