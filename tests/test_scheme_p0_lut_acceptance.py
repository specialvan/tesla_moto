"""r03 acceptance harness for V2 P0 schemes (S01, S02, S04, S11).

Loads each scheme's V2-S<id>-PARAM-sim_binding-r02.json, materialises kwargs (handling
DemagLimit dataclass and lut_path string), drives sim.run_control_lut_generator.run,
and asserts the strong checks while emitting warnings for soft checks.

Strong checks raise on failure; soft checks emit warnings. This file replaces the
S02-only test (tests/test_scheme_02_lut_acceptance.py) by parametrising over all P0
schemes. The original S02 test remains for backwards compatibility.

Not engineering-validated. r02 estimates must be replaced with FEA / bench data
before any production claim. r03 only proves binding ↔ simulation wiring works.
"""

from __future__ import annotations

import json
import re
import warnings
from pathlib import Path
from typing import Any

import pytest

from sim.run_control_lut_generator import run
from sim.safety_limits import DemagLimit
from tests.scheme_expect_dsl import eval_expect_check, expect_key_has_suffix

ROOT = Path(__file__).resolve().parents[1]
FIXED_GENERATED_AT = "2026-05-28T00:00:00+00:00"

P0_SCHEMES = [
    ("S01", "scheme-01", "V2-S01-PARAM-sim_binding-r02.json"),
    ("S02", "scheme-02", "V2-S02-PARAM-sim_binding-r02.json"),
    ("S04", "scheme-04", "V2-S04-PARAM-sim_binding-r02.json"),
    ("S11", "scheme-11", "V2-S11-PARAM-sim_binding-r02.json"),
]


def _binding_path(scheme_dir: str, file_name: str) -> Path:
    return ROOT / "engineering" / "v2" / scheme_dir / "parameters" / file_name


def _materialize_demag_limit(spec: dict[str, Any]) -> DemagLimit:
    points = [tuple(pair) for pair in spec["points_c_to_id_min_a"]]
    return DemagLimit(points_c_to_id_min_a=points)


def _load_ref(spec: dict[str, Any]) -> dict[str, Any]:
    ref = spec["$ref"]
    ref_path = (ROOT / ref).resolve()
    try:
        ref_path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"ref must resolve inside project root: {ref}") from exc
    return json.loads(ref_path.read_text(encoding="utf-8"))


def _resolve_kwargs(binding: dict[str, Any]) -> dict[str, Any]:
    kwargs = dict(binding["kwargs"])
    demag_spec = kwargs.get("demag_limit")
    if isinstance(demag_spec, dict) and "$ref" in demag_spec:
        demag_spec = _load_ref(demag_spec)
    if isinstance(demag_spec, dict) and demag_spec.get("type") == "DemagLimit":
        kwargs["demag_limit"] = _materialize_demag_limit(demag_spec)
    lut_path = kwargs.get("lut_path")
    if isinstance(lut_path, str):
        kwargs["lut_path"] = Path(lut_path)
    return kwargs


def _voltage_exceeded_ratio(output: dict[str, Any]) -> float:
    fmap = output["feasibility_map"]
    total = max(int(fmap.get("total_points", 0)), 1)
    return int(fmap["infeasible_reasons"]["voltage_exceeded"]) / total


def _all_transition_jumps(output: dict[str, Any], field: str) -> float:
    transitions = output["mode_transitions"].get("mtpa_to_fw_boundary", [])
    transitions += output["mode_transitions"].get("fw_to_mtpv_boundary", [])
    return max((abs(t.get(field, 0.0)) for t in transitions), default=0.0)


def _with_p0_derived_metrics(output: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(output)
    enriched["p0_acceptance"] = {
        "voltage_exceeded_ratio": _voltage_exceeded_ratio(output),
        "max_id_jump_a": _all_transition_jumps(output, "id_jump_a"),
        "max_iq_jump_a": _all_transition_jumps(output, "iq_jump_a"),
    }
    return enriched


def test_scheme_p0_expect_keys_use_suffix_dsl() -> None:
    for scheme_id, scheme_dir, binding_file in P0_SCHEMES:
        binding = json.loads(
            _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
        )
        legacy_keys = [
            key for key in binding["expect"] if not expect_key_has_suffix(key)
        ]
        assert legacy_keys == [], f"{scheme_id} still uses non-DSL expect keys"


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", P0_SCHEMES)
def test_scheme_p0_sim_binding_drives_run(
    tmp_path: Path,
    scheme_id: str,
    scheme_dir: str,
    binding_file: str,
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    kwargs = _resolve_kwargs(binding)
    kwargs["output_path"] = tmp_path / f"control_lut_{scheme_id.lower()}.json"
    kwargs["generated_at"] = FIXED_GENERATED_AT

    output = run(**kwargs)

    expect = binding["expect"]
    strong_keys = set(binding["strong_checks"])
    soft_keys = set(binding["soft_checks"])

    strong_failures: list[str] = []
    soft_warnings: list[str] = []

    for key, expected_value in expect.items():
        passed, message = eval_expect_check(
            key, expected_value, _with_p0_derived_metrics(output)
        )
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


def test_resolve_kwargs_materializes_demag_limit_ref() -> None:
    binding = {
        "kwargs": {
            "demag_limit": {
                "$ref": "models/demag_limit_estimate.json",
            }
        }
    }

    kwargs = _resolve_kwargs(binding)

    assert isinstance(kwargs["demag_limit"], DemagLimit)
    assert kwargs["demag_limit"].points_c_to_id_min_a == [
        (25.0, -240.0),
        (100.0, -210.0),
        (140.0, -180.0),
    ]


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", P0_SCHEMES)
def test_scheme_p0_engineering_validated_is_false(
    scheme_id: str, scheme_dir: str, binding_file: str
) -> None:
    binding = json.loads(
        _binding_path(scheme_dir, binding_file).read_text(encoding="utf-8")
    )
    assert (
        binding["engineering_validated"] is False
    ), f"{scheme_id} r02 sim binding must keep engineering_validated=false"


@pytest.mark.integration
@pytest.mark.parametrize("scheme_id, scheme_dir, binding_file", P0_SCHEMES)
def test_scheme_p0_dvp_mapping_present(
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
