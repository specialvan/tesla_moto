from __future__ import annotations

import json
from pathlib import Path

from sim.dq_model import MotorParams
from sim.modulation_sweep import (
    modulation_penalty,
    params_with_modulation_factor,
)
from sim.run_modulation_sweep_experiment import run


def test_modulation_factor_raises_voltage_limit_and_penalizes_overmodulation() -> None:
    base = MotorParams(
        name="mod_test",
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

    overmod = params_with_modulation_factor(base, k_mod=1.08)
    penalty = modulation_penalty(k_mod=1.08)

    assert overmod.svpwm_linear_vmax_factor > base.svpwm_linear_vmax_factor
    assert penalty["harmonic_current_rms_ratio"] > 0.0
    assert penalty["inverter_loss_multiplier"] > 1.0


def test_modulation_sweep_experiment_writes_kmod_axis_and_artifacts() -> None:
    summary = run(speed_step_rpm=1000.0)
    summary_path = Path("experiments/exp_005_modulation_factor/summary.json")
    csv_path = Path(
        "experiments/exp_005_modulation_factor/modulation_sweep_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_005_modulation_factor"
    assert summary["best_tradeoff"]["k_mod"] >= 1.0
    assert any(k_mod > 1.0 for k_mod in summary["sweep_axes"]["k_mod_values"])

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "k_mod" in header
    assert "harmonic_current_rms_ratio" in header
    assert "inverter_loss_multiplier" in header
    assert "target_max_speed_rpm" in header

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["model_scope"] == "linear_dq_with_explicit_voltage_utilization_axis"
