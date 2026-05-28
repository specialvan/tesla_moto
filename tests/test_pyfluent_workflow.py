from __future__ import annotations

import json
from pathlib import Path

import pytest

from sim.pyfluent_workflow import (
    BoundaryUpdate,
    FluentRunConfig,
    FluentWorkflow,
)


class FakeAdapter:
    def __init__(self, fail_on_iterate: bool = False) -> None:
        self.fail_on_iterate = fail_on_iterate
        self.calls: list[tuple[str, object]] = []

    def load_case(self, path: Path) -> None:
        self.calls.append(("load_case", path))

    def set_boundary(self, update: BoundaryUpdate) -> None:
        self.calls.append(("set_boundary", update))

    def iterate(self, count: int) -> None:
        self.calls.append(("iterate", count))
        if self.fail_on_iterate:
            raise RuntimeError("solver failed")

    def write_case_data(self, path: Path) -> None:
        self.calls.append(("write_case_data", path))

    def close(self) -> None:
        self.calls.append(("close", None))


def _config(tmp_path: Path, manifest_path: Path | None = None) -> FluentRunConfig:
    return FluentRunConfig(
        case_path=tmp_path / "cooling.cas.h5",
        output_case_data_path=tmp_path / "cooling-out.cas.h5",
        manifest_path=manifest_path or tmp_path / "manifest.json",
        iterations=25,
        boundary_updates=[
            BoundaryUpdate(zone="inlet", variable="velocity-magnitude", value=3.0),
        ],
        allowed_boundary_variables={"inlet": {"velocity-magnitude"}},
        validation_chain={
            "cad_source_sha256": "abc123",
            "material_card_path": "materials/cooling-fluid.json",
            "mesh_summary": "coarse smoke mesh, 120k cells",
        },
    )


def test_workflow_writes_success_manifest_and_closes_adapter(tmp_path: Path) -> None:
    adapter = FakeAdapter()
    config = _config(tmp_path)

    result = FluentWorkflow(config=config, adapter=adapter).run()

    manifest = json.loads(config.manifest_path.read_text(encoding="utf-8"))
    assert result["success"] is True
    assert manifest["success"] is True
    assert manifest["engineering_validated"] is False
    assert manifest["validation_note"]
    assert manifest["validation_chain"]["cad_source_sha256"] == "abc123"
    assert ("close", None) in adapter.calls


def test_workflow_writes_failure_manifest_before_reraising(tmp_path: Path) -> None:
    adapter = FakeAdapter(fail_on_iterate=True)
    config = _config(tmp_path)

    with pytest.raises(RuntimeError, match="solver failed"):
        FluentWorkflow(config=config, adapter=adapter).run()

    manifest = json.loads(config.manifest_path.read_text(encoding="utf-8"))
    assert manifest["success"] is False
    assert manifest["engineering_validated"] is False
    assert manifest["error"]["type"] == "RuntimeError"
    assert manifest["error"]["message"] == "solver failed"
    assert ("close", None) in adapter.calls


def test_config_rejects_boundary_update_outside_allow_list(tmp_path: Path) -> None:
    config = _config(tmp_path)
    config.boundary_updates[0] = BoundaryUpdate(
        zone="inlet", variable="temperature", value=300.0
    )

    with pytest.raises(ValueError, match="boundary update not allowed"):
        config.validate()


def test_config_requires_validation_chain_fields(tmp_path: Path) -> None:
    config = _config(tmp_path)
    del config.validation_chain["mesh_summary"]

    with pytest.raises(ValueError, match="mesh_summary"):
        config.validate()
