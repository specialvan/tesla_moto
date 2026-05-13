from __future__ import annotations

import json
from pathlib import Path

from sim.run_hybrid_excitation_experiment import DEFAULT_FIELD_CURRENTS_A, run


def test_hybrid_excitation_experiment_writes_summary_and_csv() -> None:
    summary = run()
    summary_path = Path("experiments/exp_007_hybrid_excitation/summary.json")
    csv_path = Path("experiments/exp_007_hybrid_excitation/hybrid_excitation_results.csv")

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_007_hybrid_excitation"
    assert summary["row_count"] == len(DEFAULT_FIELD_CURRENTS_A)

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    field_model = saved["field_model"]
    assert field_model["kf_wb_per_a"] > 0
    assert field_model["field_resistance_ohm"] > 0

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("field_current_a,effective_psi_f_wb,")


def test_hybrid_excitation_zero_field_current_has_zero_field_loss() -> None:
    run()
    text = Path(
        "experiments/exp_007_hybrid_excitation/hybrid_excitation_results.csv"
    ).read_text(encoding="utf-8")
    rows = [line.split(",") for line in text.splitlines()]
    header, *data = rows
    field_loss_idx = header.index("field_loss_w")
    field_current_idx = header.index("field_current_a")
    zero_row = next(row for row in data if float(row[field_current_idx]) == 0.0)
    assert float(zero_row[field_loss_idx]) == 0.0
