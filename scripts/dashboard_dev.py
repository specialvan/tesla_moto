"""Developer entrypoint for the dashboard frontend/backend integration."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str], timeout: int | None = None) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "sim.dashboard_api", *args],
        cwd=ROOT,
        text=True,
        check=False,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run_smoke(quick: bool) -> int:
    commands = [["--smoke"], ["--browser-interaction-smoke"]]
    if not quick:
        commands.extend(
            [
                ["--browser-smoke"],
                ["--browser-error-smoke"],
                ["--browser-contract-smoke"],
                ["--browser-screenshot-smoke"],
            ]
        )
    for command in commands:
        _run(command, timeout=60)
    print("dashboard_dev_smoke=ok")
    return 0


def serve(host: str, port: int) -> int:
    print(f"dashboard_dev_serve=http://{host}:{port}/controllable_flux_motor_kb.html")
    _run(["--host", host, "--port", str(port)])
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the dashboard dev server and frontend/backend smoke checks, "
            "including browser-interaction coverage."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="Start the local dashboard API and page.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    smoke_parser = subparsers.add_parser("smoke", help="Run dashboard integration smoke checks.")
    smoke_parser.add_argument(
        "--quick",
        action="store_true",
        help="Run HTTP and browser interaction checks only.",
    )

    args = parser.parse_args()
    if args.command == "serve":
        raise SystemExit(serve(args.host, args.port))
    if args.command == "smoke":
        raise SystemExit(run_smoke(args.quick))
    parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
