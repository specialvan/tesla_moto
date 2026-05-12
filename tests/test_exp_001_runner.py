import json

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


def test_exp_001_json_outputs_do_not_contain_nonstandard_numbers(tmp_path):
    json_path, _ = run_experiment(output_dir=tmp_path / "out")
    text = json_path.read_text(encoding="utf-8")

    assert "Infinity" not in text
    assert "NaN" not in text


def test_exp_001_csv_outputs_do_not_contain_infinite_values(tmp_path):
    _, csv_path = run_experiment(output_dir=tmp_path / "out")
    text = csv_path.read_text(encoding="utf-8")

    assert "inf" not in text.lower()
    assert "nan" not in text.lower()
