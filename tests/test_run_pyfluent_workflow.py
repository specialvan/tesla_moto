from __future__ import annotations

import json
from pathlib import Path

from sim.run_pyfluent_workflow import load_config


def test_load_config_resolves_paths_and_boundary_updates(tmp_path: Path) -> None:
    case_path = tmp_path / "cases" / "motor_cooling.cas.h5"
    case_path.parent.mkdir()
    case_path.write_text("case-placeholder", encoding="utf-8")
    config_path = tmp_path / "pyfluent_run.json"
    config_path.write_text(
        json.dumps(
            {
                "case_path": "cases/motor_cooling.cas.h5",
                "output_dir": "runs/cfd_baseline",
                "iterations": 120,
                "boundary_updates": [
                    {
                        "zone": "cooling_inlet",
                        "variable": "velocity-magnitude",
                        "value": 18.0,
                        "unit": "m/s",
                    }
                ],
                "report_exports": [
                    {"name": "pressure_drop", "filename": "pressure_drop.csv"}
                ],
                "save_case_data": False,
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.case_path == case_path
    assert config.output_dir == tmp_path / "runs" / "cfd_baseline"
    assert config.iterations == 120
    assert config.boundary_updates[0].zone == "cooling_inlet"
    assert config.report_exports[0].filename == "pressure_drop.csv"
    assert config.save_case_data is False
