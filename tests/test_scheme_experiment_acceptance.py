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

ROOT = Path(__file__).resolve().parents[1]

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


def _walk(output: Any, dotted: str) -> Any:
    cursor: Any = output
    for part in dotted.split("."):
        if isinstance(cursor, dict):
            if part not in cursor:
                raise KeyError(f"missing key {part!r} in path {dotted!r}")
            cursor = cursor[part]
        else:
            raise TypeError(
                f"cannot descend into non-dict {type(cursor).__name__} at {dotted!r}"
            )
    return cursor


SUFFIXES = (
    ".equals",
    ".regex",
    ".enum",
    ".count_min",
    ".count_max",
    ".min",
    ".max",
    ".present",
    ".absent",
)


def _split_key(key: str) -> tuple[str, str]:
    for suffix in SUFFIXES:
        if key.endswith(suffix):
            return key[: -len(suffix)], suffix[1:]
    raise ValueError(f"expect key {key!r} missing recognised suffix {SUFFIXES}")


def _eval_check(key: str, expected: Any, output: dict[str, Any]) -> tuple[bool, str]:
    path, op = _split_key(key)
    try:
        value = _walk(output, path)
    except (KeyError, TypeError) as exc:
        if op == "present":
            return False, f"{path}: {exc}"
        if op == "absent":
            return True, f"{path}: absent"
        return False, f"{path}: {exc}"
    if op == "equals":
        return value == expected, f"{path}={value!r} == {expected!r}"
    if op == "regex":
        if not isinstance(value, str):
            return False, f"{path}={value!r} not a string"
        return bool(re.match(expected, value)), f"{path}={value!r} regex={expected}"
    if op == "enum":
        return value in expected, f"{path}={value!r} in {expected}"
    if op == "count_min":
        length = len(value) if hasattr(value, "__len__") else 0
        return length >= expected, f"len({path})={length} >= {expected}"
    if op == "count_max":
        length = len(value) if hasattr(value, "__len__") else 0
        return length <= expected, f"len({path})={length} <= {expected}"
    if op == "min":
        return value >= expected, f"{path}={value} >= {expected}"
    if op == "max":
        return value <= expected, f"{path}={value} <= {expected}"
    if op == "present":
        return value is not None, f"{path} present={value is not None}"
    if op == "absent":
        return value is None, f"{path} absent={value is None}"
    raise ValueError(f"unhandled op {op!r}")


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", SCHEME_BINDINGS)
def test_scheme_experiment_sim_binding_drives_run(
    scheme_id: str, scheme_dir: str, binding_file: str
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    module = importlib.import_module(binding["entry"])
    function = getattr(module, binding["function"])
    output = function(**binding["kwargs"])

    expect = binding["expect"]
    strong_keys = set(binding["strong_checks"])
    soft_keys = set(binding["soft_checks"])

    strong_failures: list[str] = []
    soft_warnings: list[str] = []

    for key, expected_value in expect.items():
        passed, message = _eval_check(key, expected_value, output)
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
    assert binding["engineering_validated"] is False, (
        f"{scheme_id} r02 sim binding must keep engineering_validated=false"
    )


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
    for dvp_id in mapping:
        assert re.match(rf"^{scheme_id}-DV-\d{{3}}$", dvp_id), (
            f"{scheme_id} dvp id {dvp_id!r} does not match S<id>-DV-NNN"
        )
