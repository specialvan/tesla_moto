from __future__ import annotations

import json
from math import isclose
from pathlib import Path

from sim.dq_model import MotorParams
from sim.hybrid_excitation import (
    HybridExcitationSpec,
    field_loss_w,
    params_with_field_current,
)
from sim.run_hybrid_excitation_experiment import run


def test_field_current_changes_effective_flux_and_field_loss() -> None:
    base = MotorParams(
        name="hybrid_test",
        pole_pairs=4,
        rs_ohm=0.035,
        ld_h=0.00018,
        lq_h=0.00042,
        psi_f_wb=0.055,
        vdc_v=360.0,
        i_max_a=260.0,
        speed_max_rpm=18000.0,
        torque_target_nm=100.0,
    )
    spec = HybridExcitationSpec(kf_wb_per_a=0.00018, field_resistance_ohm=1.2)

    weakened = params_with_field_current(base, spec, field_current_a=-40.0)

    assert isclose(weakened.psi_f_wb, 0.0478, rel_tol=1e-12)
    assert isclose(field_loss_w(spec, -40.0), 1920.0, rel_tol=1e-12)


def test_hybrid_excitation_experiment_writes_comparison_artifacts() -> None:
    summary = run(speed_step_rpm=1000.0)
    summary_path = Path("experiments/exp_007_hybrid_excitation/summary.json")
    csv_path = Path(
        "experiments/exp_007_hybrid_excitation/hybrid_excitation_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_007_hybrid_excitation"
    assert summary["best_tradeoff"]["field_current_a"] <= 0.0
    assert any(value < 0.0 for value in summary["sweep_axes"]["field_current_a"])

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "effective_psi_f_wb" in header
    assert "field_loss_w" in header
    assert "combined_loss_w" in header
    assert "target_max_speed_rpm" in header

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["model_scope"] == "linear_dq_with_equivalent_field_excitation"
