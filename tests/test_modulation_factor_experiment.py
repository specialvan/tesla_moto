from __future__ import annotations

import json
from pathlib import Path

from sim.run_modulation_factor_experiment import K_MOD_VALUES, run


def test_modulation_factor_experiment_writes_summary_and_csv() -> None:
    summary = run()
    summary_path = Path("experiments/exp_005_modulation_factor/summary.json")
    csv_path = Path("experiments/exp_005_modulation_factor/modulation_sweep_results.csv")

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_005_modulation_factor"
    assert summary["row_count"] == len(K_MOD_VALUES)
    assert summary["sweep_axes"]["k_mod_values"] == K_MOD_VALUES

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    best = saved["best_tradeoff"]
    assert best is not None
    assert best["k_mod"] in K_MOD_VALUES
    assert best["target_max_speed_rpm"] is not None

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("k_mod,svpwm_vmax_factor,vmax_v,")


def test_modulation_factor_overmodulation_lifts_vmax_above_linear_region() -> None:
    summary = run()
    saved = json.loads(
        Path("experiments/exp_005_modulation_factor/summary.json").read_text(
            encoding="utf-8"
        )
    )
    rows = saved["sweep_axes"]["k_mod_values"]
    assert rows[0] == 1.0
    # The linear point should not have any harmonic penalty.
    best = saved["best_tradeoff"]
    if best["k_mod"] == 1.0:
        assert best["harmonic_current_rms_ratio"] == 0.0
    # The CSV should always include all configured k_mod values.
    text = Path(
        "experiments/exp_005_modulation_factor/modulation_sweep_results.csv"
    ).read_text(encoding="utf-8")
    for k_mod in K_MOD_VALUES:
        assert f"{k_mod}" in text
