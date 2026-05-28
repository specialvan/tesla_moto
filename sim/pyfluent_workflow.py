"""Offline-testable PyFluent workflow wrapper.

The workflow keeps PyFluent behind an adapter boundary so config parsing,
manifest generation, and dry-run validation can be tested without an Ansys
Fluent installation or license.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


REQUIRED_VALIDATION_CHAIN_FIELDS = (
    "cad_source_sha256",
    "material_card_path",
    "mesh_summary",
)


@dataclass(frozen=True)
class BoundaryUpdate:
    zone: str
    variable: str
    value: float | int | str | bool

    def validate(self) -> None:
        if not self.zone:
            raise ValueError("boundary update zone must not be empty")
        if not self.variable:
            raise ValueError("boundary update variable must not be empty")


@dataclass
class FluentRunConfig:
    case_path: Path
    output_case_data_path: Path
    manifest_path: Path
    iterations: int
    boundary_updates: list[BoundaryUpdate] = field(default_factory=list)
    allowed_boundary_variables: dict[str, set[str]] = field(default_factory=dict)
    validation_chain: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if self.iterations <= 0:
            raise ValueError("iterations must be positive")
        for update in self.boundary_updates:
            update.validate()
            allowed = self.allowed_boundary_variables.get(update.zone)
            if allowed is None or update.variable not in allowed:
                raise ValueError(
                    "boundary update not allowed: "
                    f"zone={update.zone!r}, variable={update.variable!r}"
                )
        missing = [
            field_name
            for field_name in REQUIRED_VALIDATION_CHAIN_FIELDS
            if not self.validation_chain.get(field_name)
        ]
        if missing:
            raise ValueError(
                "validation_chain missing required fields: " + ", ".join(missing)
            )

    def to_manifest_dict(self) -> dict[str, Any]:
        return {
            "case_path": self.case_path.as_posix(),
            "output_case_data_path": self.output_case_data_path.as_posix(),
            "iterations": self.iterations,
            "boundary_updates": [
                {
                    "zone": update.zone,
                    "variable": update.variable,
                    "value": update.value,
                }
                for update in self.boundary_updates
            ],
            "allowed_boundary_variables": {
                zone: sorted(variables)
                for zone, variables in self.allowed_boundary_variables.items()
            },
            "validation_chain": dict(self.validation_chain),
        }


class FluentAdapter(Protocol):
    def load_case(self, path: Path) -> None: ...

    def set_boundary(self, update: BoundaryUpdate) -> None: ...

    def iterate(self, count: int) -> None: ...

    def write_case_data(self, path: Path) -> None: ...

    def close(self) -> None: ...


class PyFluentAdapter:
    """Thin adapter over ansys.fluent.core with lazy import."""

    def __init__(self) -> None:
        from ansys.fluent.core import launch_fluent  # type: ignore[import-untyped]

        self._session = launch_fluent()

    def load_case(self, path: Path) -> None:
        self._session.file.read_case(file_name=str(path))

    def set_boundary(self, update: BoundaryUpdate) -> None:
        zone = self._session.setup.boundary_conditions[update.zone]
        setattr(zone, update.variable.replace("-", "_"), update.value)

    def iterate(self, count: int) -> None:
        self._session.solution.run_calculation.iterate(iter_count=count)

    def write_case_data(self, path: Path) -> None:
        self._session.file.write_case_data(file_name=str(path))

    def close(self) -> None:
        self._session.exit()


class FluentWorkflow:
    def __init__(self, config: FluentRunConfig, adapter: FluentAdapter) -> None:
        self.config = config
        self.adapter = adapter

    def run(self) -> dict[str, Any]:
        self.config.validate()
        manifest: dict[str, Any] = self._base_manifest()
        success = False
        error: BaseException | None = None
        try:
            self.adapter.load_case(self.config.case_path)
            for update in self.config.boundary_updates:
                self.adapter.set_boundary(update)
            self.adapter.iterate(self.config.iterations)
            self.adapter.write_case_data(self.config.output_case_data_path)
            success = True
            return manifest | {"success": True}
        except BaseException as exc:
            error = exc
            raise
        finally:
            try:
                self.adapter.close()
            finally:
                manifest["success"] = success
                if error is not None:
                    manifest["error"] = {
                        "type": type(error).__name__,
                        "message": str(error),
                    }
                self._write_manifest(manifest)

    def _base_manifest(self) -> dict[str, Any]:
        return {
            "workflow": "pyfluent_cooling_cfd",
            "engineering_validated": False,
            "production_release_allowed": False,
            "validation_note": (
                "PyFluent automation is a CFD workflow scaffold only; it does not "
                "constitute FEA, bench, HIL, or production-release evidence."
            ),
            **self.config.to_manifest_dict(),
        }

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        self.config.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )
