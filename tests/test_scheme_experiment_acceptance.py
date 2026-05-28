"""r03 generic acceptance harness for V2 P1/P2 schemes that bind to existing sim runners.

For schemes S03/S05/S06/S07/S08/S09/S10/S12, each sim_binding-r02.json names an
``entry`` module + ``function`` (e.g. ``sim.run_modulation_factor_experiment.run``)
plus ``kwargs``, ``expect``, ``strong_checks``, ``soft_checks``. This harness
imports the module dynamically, invokes the function, and validates ``expect``
using a small suffix DSL:

- ``<path>.equals`` -> value match
- ``<path>.regex`` -> regex on string value
- ``<path>.enum`` -> value in list
- ``<path>.min`` -> value >= threshold
- ``<path>.max`` -> value <= threshold
- ``<path>.count_min`` -> len(value) >= threshold
- ``<path>.count_max`` -> len(value) <= threshold
- ``<path>.present`` -> value is not None
- ``<path>.absent`` -> value is None

Strong-check failures fail the test; soft-check failures emit warnings.
Not engineering-validated.
"""

from __future__ import annotations

import importlib
import json
import re
import warnings
from pathlib import Path
from typing import Any

import pytest

from tests.scheme_expect_dsl import eval_expect_check

ROOT = Path(__file__).resolve().parents[1]
_RUN_CACHE: dict[tuple[str, str, str], dict[str, Any]] = {}

SCHEME_BINDINGS = [
    ("S03", "scheme-03", "V2-S03-PARAM-sim_binding-r02.json"),
    ("S05", "scheme-05", "V2-S05-PARAM-sim_binding-r02.json"),
    ("S06", "scheme-06", "V2-S06-PARAM-sim_binding-r02.json"),
    ("S07", "scheme-07", "V2-S07-PARAM-sim_binding-r02.json"),
    ("S08", "scheme-08", "V2-S08-PARAM-sim_binding-r02.json"),
    ("S09", "scheme-09", "V2-S09-PARAM-sim_binding-r02.json"),
    ("S10", "scheme-10", "V2-S10-PARAM-sim_binding-r02.json"),
    ("S12", "scheme-12", "V2-S12-PARAM-sim_binding-r02.json"),
]


def _binding_path(scheme_dir: str, file_name: str) -> Path:
    return ROOT / "engineering" / "v2" / scheme_dir / "parameters" / file_name


def _run_binding(binding: dict[str, Any]) -> dict[str, Any]:
    kwargs = binding["kwargs"]
    cache_key = (
        binding["entry"],
        binding["function"],
        json.dumps(kwargs, sort_keys=True, separators=(",", ":")),
    )
    if cache_key not in _RUN_CACHE:
        module = importlib.import_module(binding["entry"])
        function = getattr(module, binding["function"])
        _RUN_CACHE[cache_key] = function(**kwargs)
    return _RUN_CACHE[cache_key]


def test_run_binding_caches_identical_runner_invocations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    class FakeModule:
        @staticmethod
        def run(**kwargs: Any) -> dict[str, Any]:
            nonlocal calls
            calls += 1
            return {"kwargs": kwargs}

    def fake_import_module(name: str) -> FakeModule:
        assert name == "fake.runner"
        return FakeModule()

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    binding = {"entry": "fake.runner", "function": "run", "kwargs": {"scale": 1}}

    first = _run_binding(binding)
    second = _run_binding(dict(binding))

    assert first == second == {"kwargs": {"scale": 1}}
    assert calls == 1


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", SCHEME_BINDINGS)
def test_scheme_experiment_sim_binding_drives_run(
    scheme_id: str, scheme_dir: str, binding_file: str
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    output = _run_binding(binding)

    expect = binding["expect"]
    strong_keys = set(binding["strong_checks"])
    soft_keys = set(binding["soft_checks"])

    strong_failures: list[str] = []
    soft_warnings: list[str] = []

    for key, expected_value in expect.items():
        passed, message = eval_expect_check(key, expected_value, output)
        if passed:
            continue
        if key in strong_keys:
            strong_failures.append(f"[{scheme_id}] STRONG fail: {key} -> {message}")
        elif key in soft_keys:
            soft_warnings.append(f"[{scheme_id}] SOFT warn: {key} -> {message}")
        else:
            strong_failures.append(
                f"[{scheme_id}] UNCLASSIFIED fail: {key} -> {message}"
            )

    for warning_message in soft_warnings:
        warnings.warn(warning_message, stacklevel=1)

    assert not strong_failures, (
        f"{scheme_id} r02 sim binding produced strong-check failures:\n  - "
        + "\n  - ".join(strong_failures)
    )


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", SCHEME_BINDINGS)
def test_scheme_experiment_engineering_validated_is_false(
    scheme_id: str, scheme_dir: str, binding_file: str
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    assert (
        binding["engineering_validated"] is False
    ), f"{scheme_id} r02 sim binding must keep engineering_validated=false"


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", SCHEME_BINDINGS)
def test_scheme_experiment_dvp_mapping_present(
    scheme_id: str, scheme_dir: str, binding_file: str
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    mapping = binding["dvp_mapping"]
    assert mapping, f"{scheme_id} dvp_mapping must not be empty"
    assert (
        len(mapping) >= 5
    ), f"{scheme_id} dvp_mapping must include at least 5 DVP items"
    for dvp_id in mapping:
        assert re.match(
            rf"^{scheme_id}-DV-\d{{3}}$", dvp_id
        ), f"{scheme_id} dvp id {dvp_id!r} does not match S<id>-DV-NNN"
