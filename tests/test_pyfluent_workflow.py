from __future__ import annotations

import json
from pathlib import Path

import pytest

from sim.pyfluent_workflow import (
    BoundaryUpdate,
    FluentRunConfig,
    FluentWorkflow,
    ReportExport,
)


class FakeFluentAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def load_case(self, case_path: Path) -> None:
        self.calls.append(("load_case", case_path))

    def set_boundary(self, update: BoundaryUpdate) -> None:
        self.calls.append(("set_boundary", update))

    def initialize(self) -> None:
        self.calls.append(("initialize", None))

    def iterate(self, iterations: int) -> None:
        self.calls.append(("iterate", iterations))

    def export_report(self, export: ReportExport, output_path: Path) -> None:
        self.calls.append(("export_report", (export, output_path)))
        output_path.write_text("name,value\npressure_drop_pa,42.0\n", encoding="utf-8")

    def write_case_data(self, output_path: Path) -> None:
        self.calls.append(("write_case_data", output_path))
        output_path.write_text("case-data-placeholder", encoding="utf-8")

    def close(self) -> None:
        self.calls.append(("close", None))


def test_config_rejects_missing_case_file(tmp_path: Path) -> None:
    config = FluentRunConfig(
        case_path=tmp_path / "missing.cas.h5",
        output_dir=tmp_path / "out",
        boundary_updates=[],
        report_exports=[],
        iterations=20,
    )

    with pytest.raises(FileNotFoundError, match="missing.cas.h5"):
        config.validate()


def test_workflow_runs_adapter_and_writes_manifest(tmp_path: Path) -> None:
    case_path = tmp_path / "baseline.cas.h5"
    case_path.write_text("case-placeholder", encoding="utf-8")
    adapter = FakeFluentAdapter()
    config = FluentRunConfig(
        case_path=case_path,
        output_dir=tmp_path / "run",
        boundary_updates=[
            BoundaryUpdate(
                zone="cooling_inlet",
                variable="velocity-magnitude",
                value=25.0,
                unit="m/s",
            )
        ],
        report_exports=[
            ReportExport(name="pressure_drop", filename="pressure_drop.csv")
        ],
        iterations=80,
        save_case_data=True,
    )

    result = FluentWorkflow(adapter).run(config)

    assert [name for name, _ in adapter.calls] == [
        "load_case",
        "set_boundary",
        "initialize",
        "iterate",
        "export_report",
        "write_case_data",
        "close",
    ]
    assert result.manifest_path.exists()
    assert result.report_paths == [tmp_path / "run" / "pressure_drop.csv"]
    assert result.case_data_path == tmp_path / "run" / "solved.cas.h5"

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["case_path"] == str(case_path)
    assert manifest["iterations"] == 80
    assert manifest["boundary_updates"][0]["zone"] == "cooling_inlet"
    assert manifest["report_exports"][0]["name"] == "pressure_drop"
    assert manifest["engineering_validated"] is False
