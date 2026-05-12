from __future__ import annotations

import json
from math import isclose
from pathlib import Path

from sim.dq_model import MotorParams
from sim.winding_reconfiguration import (
    WindingConfig,
    apply_winding_config,
    transition_delta,
)
from sim.run_winding_reconfiguration_experiment import run


def test_winding_config_scales_ke_resistance_inductance_and_current() -> None:
    base = MotorParams(
        name="winding_test",
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
    config = WindingConfig(
        name="parallel",
        turns_scale=0.7,
        resistance_scale=0.5,
        current_limit_scale=1.25,
    )

    params = apply_winding_config(base, config)

    assert isclose(params.psi_f_wb, 0.0385, rel_tol=1e-12)
    assert isclose(params.ld_h, 0.00018 * 0.49, rel_tol=1e-12)
    assert isclose(params.lq_h, 0.00042 * 0.49, rel_tol=1e-12)
    assert isclose(params.rs_ohm, 0.0175, rel_tol=1e-12)
    assert isclose(params.i_max_a, 325.0, rel_tol=1e-12)


def test_transition_delta_reports_torque_and_current_steps() -> None:
    low = {"torque_nm": 80.0, "current_a": 200.0}
    high = {"torque_nm": 76.0, "current_a": 220.0}

    delta = transition_delta(low, high)

    assert delta["torque_delta_nm"] == -4.0
    assert delta["current_delta_a"] == 20.0


def test_winding_reconfiguration_experiment_writes_config_and_transition_results() -> (
    None
):
    summary = run(speed_step_rpm=1000.0)
    summary_path = Path("experiments/exp_008_winding_reconfiguration/summary.json")
    csv_path = Path(
        "experiments/exp_008_winding_reconfiguration/winding_reconfiguration_results.csv"
    )

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["experiment"] == "exp_008_winding_reconfiguration"
    assert len(summary["configs"]) >= 2
    assert summary["recommended_config"]["target_max_speed_rpm"] is not None
    assert "torque_delta_nm" in summary["transition_check"]

    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "config" in header
    assert "target_max_speed_rpm" in header
    assert "psi_f_wb" in header

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["model_scope"] == "linear_dq_multi_winding_configuration_sweep"
