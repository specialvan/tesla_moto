# Phase 1 Linear dq Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal, testable Phase 1 linear dq simulation loop for controllable flux motor research.

**Architecture:** Keep the implementation as small Python modules with explicit data boundaries. `sim/dq_model.py` owns equations and scalar metrics, `sim/control_search.py` owns grid-search control trajectories, `models/motor_params.json` provides a sample motor, and `experiments/exp_001_linear_dq/run.py` generates reproducible JSON/CSV outputs.

**Tech Stack:** Python 3.12, standard library, `pytest` for test execution.

---

### Task 1: Linear dq Model

**Files:**
- Create: `sim/__init__.py`
- Create: `sim/dq_model.py`
- Test: `tests/test_dq_model.py`

- [ ] **Step 1: Write failing tests**

```python
from math import isclose

from sim.dq_model import MotorParams, copper_loss, current_magnitude, voltage_magnitude


def test_linear_flux_voltage_and_torque_equations():
    params = MotorParams(
        name="sample",
        pole_pairs=4,
        rs_ohm=0.03,
        ld_h=0.00012,
        lq_h=0.00025,
        psi_f_wb=0.045,
        vdc_v=400.0,
        i_max_a=500.0,
        speed_max_rpm=18000.0,
        torque_target_nm=220.0,
        temperature_c=25.0,
    )

    assert isclose(params.flux_d(-100.0), 0.033, rel_tol=1e-12)
    assert isclose(params.flux_q(200.0), 0.05, rel_tol=1e-12)
    assert isclose(params.voltage_d(-100.0, 200.0, 1000.0), -53.0, rel_tol=1e-12)
    assert isclose(params.voltage_q(-100.0, 200.0, 1000.0), 39.0, rel_tol=1e-12)
    assert isclose(params.torque_nm(-100.0, 200.0), 69.6, rel_tol=1e-12)


def test_magnitudes_and_copper_loss():
    assert isclose(current_magnitude(-3.0, 4.0), 5.0, rel_tol=1e-12)
    assert isclose(voltage_magnitude(6.0, 8.0), 10.0, rel_tol=1e-12)
    assert isclose(copper_loss(10.0, 0.03), 9.0, rel_tol=1e-12)
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_dq_model.py -q`

Expected: FAIL because `sim.dq_model` does not exist.

- [ ] **Step 3: Implement linear dq equations**

Create `MotorParams` with `flux_d`, `flux_q`, `voltage_d`, `voltage_q`, and `torque_nm`, plus scalar helper functions.

- [ ] **Step 4: Run tests and verify pass**

Run: `pytest tests/test_dq_model.py -q`

Expected: PASS.

### Task 2: Control Search

**Files:**
- Create: `sim/control_search.py`
- Test: `tests/test_control_search.py`

- [ ] **Step 1: Write failing tests**

```python
from sim.control_search import field_weakening_search, mtpa_grid_search, mtpv_grid_search
from sim.dq_model import MotorParams


def sample_params():
    return MotorParams(
        name="sample",
        pole_pairs=4,
        rs_ohm=0.03,
        ld_h=0.00012,
        lq_h=0.00025,
        psi_f_wb=0.045,
        vdc_v=400.0,
        i_max_a=500.0,
        speed_max_rpm=18000.0,
        torque_target_nm=120.0,
        temperature_c=25.0,
    )


def test_mtpa_finds_low_current_point_for_target_torque():
    result = mtpa_grid_search(sample_params(), target_torque_nm=80.0, current_step_a=20.0)
    assert result.feasible
    assert result.torque_nm >= 80.0
    assert result.current_a <= sample_params().i_max_a


def test_field_weakening_respects_voltage_limit():
    params = sample_params()
    result = field_weakening_search(
        params,
        target_torque_nm=80.0,
        mechanical_speed_rpm=8000.0,
        current_step_a=20.0,
    )
    assert result.feasible
    assert result.voltage_v <= params.vmax_phase_v + 1e-9
    assert result.torque_nm >= 80.0


def test_mtpv_returns_maximum_feasible_torque_point():
    params = sample_params()
    result = mtpv_grid_search(params, mechanical_speed_rpm=12000.0, current_step_a=25.0)
    assert result.feasible
    assert result.voltage_v <= params.vmax_phase_v + 1e-9
    assert result.current_a <= params.i_max_a + 1e-9
    assert result.torque_nm > 0.0
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_control_search.py -q`

Expected: FAIL because `sim.control_search` does not exist.

- [ ] **Step 3: Implement grid search**

Create `SearchResult`, current grid generation, MTPA, field-weakening, and MTPV search functions.

- [ ] **Step 4: Run tests and verify pass**

Run: `pytest tests/test_control_search.py -q`

Expected: PASS.

### Task 3: Reproducible Experiment

**Files:**
- Create: `models/motor_params.json`
- Create: `experiments/exp_001_linear_dq/run.py`
- Test: `tests/test_exp_001_runner.py`

- [ ] **Step 1: Write failing test**

```python
import json
from pathlib import Path

from experiments.exp_001_linear_dq.run import run_experiment


def test_exp_001_writes_json_and_csv_outputs(tmp_path):
    output_dir = tmp_path / "out"
    json_path, csv_path = run_experiment(output_dir=output_dir)

    assert json_path.exists()
    assert csv_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["experiment"] == "exp_001_linear_dq"
    assert len(data["speed_points"]) > 3
    assert all("speed_rpm" in point for point in data["speed_points"])
    assert csv_path.read_text(encoding="utf-8").splitlines()[0].startswith("speed_rpm,")
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_exp_001_runner.py -q`

Expected: FAIL because experiment runner does not exist.

- [ ] **Step 3: Implement runner**

Load `models/motor_params.json`, scan speeds, call search functions, and write JSON/CSV.

- [ ] **Step 4: Run all tests**

Run: `pytest -q`

Expected: PASS.
