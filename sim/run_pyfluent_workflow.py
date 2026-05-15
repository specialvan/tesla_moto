"""CLI entry point for parameterized PyFluent runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .pyfluent_workflow import (
    BoundaryUpdate,
    FluentRunConfig,
    FluentWorkflow,
    PyFluentAdapter,
    ReportExport,
)


def _resolve_config_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return base_dir / path


def load_config(config_path: Path) -> FluentRunConfig:
    base_dir = config_path.resolve().parent
    data: dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
    return FluentRunConfig(
        case_path=_resolve_config_path(base_dir, data["case_path"]),
        output_dir=_resolve_config_path(base_dir, data["output_dir"]),
        boundary_updates=[
            BoundaryUpdate(
                zone=update["zone"],
                variable=update["variable"],
                value=update["value"],
                unit=update.get("unit"),
            )
            for update in data.get("boundary_updates", [])
        ],
        report_exports=[
            ReportExport(name=export["name"], filename=export["filename"])
            for export in data.get("report_exports", [])
        ],
        iterations=int(data["iterations"]),
        save_case_data=bool(data.get("save_case_data", True)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a PyFluent CFD workflow.")
    parser.add_argument("config", type=Path, help="Path to a PyFluent run JSON file.")
    parser.add_argument(
        "--product-version",
        default=None,
        help="Optional Fluent product version passed to ansys.fluent.core.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    result = FluentWorkflow(
        PyFluentAdapter(product_version=args.product_version)
    ).run(config)
    print(
        json.dumps(
            {
                "manifest_path": str(result.manifest_path),
                "report_paths": [str(path) for path in result.report_paths],
                "case_data_path": (
                    str(result.case_data_path) if result.case_data_path else None
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
