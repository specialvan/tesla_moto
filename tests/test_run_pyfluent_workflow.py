from __future__ import annotations

import json
from pathlib import Path

import pytest

import sim.run_pyfluent_workflow as runner
from sim.pyfluent_workflow import FluentRunConfig


def _write_config(path: Path, tmp_path: Path) -> None:
    payload = {
        "case_path": str(tmp_path / "cooling.cas.h5"),
        "output_case_data_path": str(tmp_path / "cooling-out.cas.h5"),
        "manifest_path": str(tmp_path / "manifest.json"),
        "iterations": 10,
        "boundary_updates": [
            {"zone": "inlet", "variable": "velocity-magnitude", "value": 2.5}
        ],
        "allowed_boundary_variables": {"inlet": ["velocity-magnitude"]},
        "validation_chain": {
            "cad_source_sha256": "abc123",
            "material_card_path": "materials/cooling-fluid.json",
            "mesh_summary": "coarse smoke mesh, 120k cells",
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_config_materializes_dataclass(tmp_path: Path) -> None:
    config_path = tmp_path / "pyfluent.json"
    _write_config(config_path, tmp_path)

    config = runner.load_config(config_path)

    assert isinstance(config, FluentRunConfig)
    assert config.iterations == 10
    assert config.boundary_updates[0].zone == "inlet"


def test_dry_run_loads_config_without_launching_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    config_path = tmp_path / "pyfluent.json"
    _write_config(config_path, tmp_path)

    def fail_adapter(*args: object, **kwargs: object) -> object:
        raise AssertionError("adapter must not be created during dry-run")

    monkeypatch.setattr(runner, "PyFluentAdapter", fail_adapter)

    assert runner.main(["--config", str(config_path), "--dry-run"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["dry_run"] is True
    assert output["engineering_validated"] is False
    assert output["validation_chain"]["mesh_summary"]


def test_main_rejects_dry_run_with_run_flag(tmp_path: Path) -> None:
    config_path = tmp_path / "pyfluent.json"
    _write_config(config_path, tmp_path)

    with pytest.raises(SystemExit):
        runner.main(["--config", str(config_path), "--dry-run", "--run"])
