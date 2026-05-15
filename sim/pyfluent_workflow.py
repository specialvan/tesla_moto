"""PyFluent orchestration boundary for high-fidelity CFD/thermal runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class BoundaryUpdate:
    zone: str
    variable: str
    value: float | str | bool
    unit: str | None = None


@dataclass(frozen=True)
class ReportExport:
    name: str
    filename: str


@dataclass(frozen=True)
class FluentRunConfig:
    case_path: Path
    output_dir: Path
    boundary_updates: list[BoundaryUpdate]
    report_exports: list[ReportExport]
    iterations: int
    save_case_data: bool = True

    def validate(self) -> None:
        if not self.case_path.exists():
            raise FileNotFoundError(f"Fluent case file not found: {self.case_path}")
        if self.iterations <= 0:
            raise ValueError("iterations must be positive")
        for export in self.report_exports:
            if Path(export.filename).name != export.filename:
                raise ValueError(
                    f"report filename must not include directories: {export.filename}"
                )


@dataclass(frozen=True)
class FluentRunResult:
    manifest_path: Path
    report_paths: list[Path]
    case_data_path: Path | None


class FluentAdapter(Protocol):
    def load_case(self, case_path: Path) -> None: ...

    def set_boundary(self, update: BoundaryUpdate) -> None: ...

    def initialize(self) -> None: ...

    def iterate(self, iterations: int) -> None: ...

    def export_report(self, export: ReportExport, output_path: Path) -> None: ...

    def write_case_data(self, output_path: Path) -> None: ...

    def close(self) -> None: ...


class FluentWorkflow:
    def __init__(self, adapter: FluentAdapter) -> None:
        self.adapter = adapter

    def run(self, config: FluentRunConfig) -> FluentRunResult:
        config.validate()
        config.output_dir.mkdir(parents=True, exist_ok=True)
        report_paths = [
            config.output_dir / export.filename for export in config.report_exports
        ]
        case_data_path = config.output_dir / "solved.cas.h5" if config.save_case_data else None

        try:
            self.adapter.load_case(config.case_path)
            for update in config.boundary_updates:
                self.adapter.set_boundary(update)
            self.adapter.initialize()
            self.adapter.iterate(config.iterations)
            for export, output_path in zip(config.report_exports, report_paths):
                self.adapter.export_report(export, output_path)
            if case_data_path is not None:
                self.adapter.write_case_data(case_data_path)
        finally:
            self.adapter.close()

        manifest_path = config.output_dir / "run_manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "case_path": str(config.case_path),
                    "iterations": config.iterations,
                    "boundary_updates": [
                        asdict(update) for update in config.boundary_updates
                    ],
                    "report_exports": [
                        asdict(export) for export in config.report_exports
                    ],
                    "report_paths": [str(path) for path in report_paths],
                    "case_data_path": str(case_data_path) if case_data_path else None,
                    "engineering_validated": False,
                    "validation_note": (
                        "PyFluent automation proves workflow reproducibility only; "
                        "engineering release requires reviewed Fluent setup and "
                        "bench or design-review evidence."
                    ),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return FluentRunResult(
            manifest_path=manifest_path,
            report_paths=report_paths,
            case_data_path=case_data_path,
        )


class PyFluentAdapter:
    """Thin wrapper around ansys.fluent.core, imported only when instantiated."""

    def __init__(self, product_version: str | None = None, precision: str = "double"):
        from ansys.fluent.core import launch_fluent

        launch_kwargs: dict[str, str] = {"precision": precision}
        if product_version is not None:
            launch_kwargs["product_version"] = product_version
        self.session = launch_fluent(**launch_kwargs)

    def load_case(self, case_path: Path) -> None:
        self.session.file.read_case(file_name=str(case_path))

    def set_boundary(self, update: BoundaryUpdate) -> None:
        zone = self.session.setup.boundary_conditions[update.zone]
        setattr(zone, update.variable.replace("-", "_"), update.value)

    def initialize(self) -> None:
        self.session.solution.initialization.hybrid_initialize()

    def iterate(self, iterations: int) -> None:
        self.session.solution.run_calculation.iterate(iter_count=iterations)

    def export_report(self, export: ReportExport, output_path: Path) -> None:
        report = self.session.solution.report_definitions[export.name]
        report.write(file_name=str(output_path))

    def write_case_data(self, output_path: Path) -> None:
        self.session.file.write_case_data(file_name=str(output_path))

    def close(self) -> None:
        self.session.exit()
