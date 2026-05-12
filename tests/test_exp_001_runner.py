import json
from pathlib import Path

from sim.run_linear_dq_experiment import run


def test_exp_001_writes_json_and_csv_outputs() -> None:
    summary = run()
    summary_path = Path("experiments/exp_001_linear_dq/summary.json")
    csv_path = Path("experiments/exp_001_linear_dq/scan_results.csv")

    assert summary_path.exists()
    assert csv_path.exists()
    assert summary["params_name"] == "baseline_ipmsm_v1"
    assert summary["model_scope"] == "quasi_steady_linear_dq_grid_search"

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["target_torque_nm"] == 100.0
    assert csv_path.read_text(encoding="utf-8").splitlines()[0].startswith("speed_rpm,")


def test_exp_001_json_outputs_do_not_contain_nonstandard_numbers() -> None:
    run()
    text = Path("experiments/exp_001_linear_dq/summary.json").read_text(
        encoding="utf-8"
    )

    assert "Infinity" not in text
    assert "NaN" not in text


def test_exp_001_csv_outputs_do_not_contain_infinite_values() -> None:
    run()
    text = Path("experiments/exp_001_linear_dq/scan_results.csv").read_text(
        encoding="utf-8"
    )

    assert "inf" not in text.lower()
    assert "nan" not in text.lower()
