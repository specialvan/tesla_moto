"""CLI for the offline-testable PyFluent workflow."""

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
)


def load_config(path: Path) -> FluentRunConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    boundary_updates = [
        BoundaryUpdate(
            zone=str(item["zone"]),
            variable=str(item["variable"]),
            value=item["value"],
        )
        for item in data.get("boundary_updates", [])
    ]
    allowed_boundary_variables = {
        str(zone): {str(variable) for variable in variables}
        for zone, variables in data.get("allowed_boundary_variables", {}).items()
    }
    config = FluentRunConfig(
        case_path=Path(data["case_path"]),
        output_case_data_path=Path(data["output_case_data_path"]),
        manifest_path=Path(data["manifest_path"]),
        iterations=int(data["iterations"]),
        boundary_updates=boundary_updates,
        allowed_boundary_variables=allowed_boundary_variables,
        validation_chain={
            str(key): str(value) for key, value in data.get("validation_chain", {}).items()
        },
    )
    config.validate()
    return config


def _dry_run_payload(config: FluentRunConfig) -> dict[str, Any]:
    return {
        "dry_run": True,
        "engineering_validated": False,
        "production_release_allowed": False,
        **config.to_manifest_dict(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or validate a PyFluent CFD workflow config.")
    parser.add_argument("--config", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and validate config without creating a PyFluent adapter.",
    )
    mode.add_argument(
        "--run",
        action="store_true",
        help="Launch PyFluent through the adapter and execute the workflow.",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if args.dry_run:
        print(json.dumps(_dry_run_payload(config), ensure_ascii=False, indent=2, allow_nan=False))
        return 0

    result = FluentWorkflow(config=config, adapter=PyFluentAdapter()).run()
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
