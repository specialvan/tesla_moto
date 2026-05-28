"""r03 acceptance test for V2 scheme S02 mtpa_fw_mtpv_control.

Loads V2-S02-PARAM-sim_binding-r02.json, drives sim.run_control_lut_generator.run
with the bound kwargs, and asserts the strong / soft checks in expect{}.

Strong checks raise on failure; soft checks emit warnings via pytest.warns or
emit_warning helper. This is the r03 minimal harness that proves the r02 production
parameter sheet can drive a simulation acceptance test.

Not engineering-validated. r02 estimates (Rs, Ld, Lq, psi_f, DemagLimit) must be
replaced with FEA / bench data before any production claim.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import pytest

from sim.run_control_lut_generator import run
from sim.safety_limits import DemagLimit
from tests.scheme_expect_dsl import eval_expect_check

ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = (
    ROOT
    / "engineering"
    / "v2"
    / "scheme-02"
    / "parameters"
    / "V2-S02-PARAM-sim_binding-r02.json"
)


def _materialize_demag_limit(spec: dict[str, Any]) -> DemagLimit:
    points = [tuple(pair) for pair in spec["points_c_to_id_min_a"]]
    return DemagLimit(points_c_to_id_min_a=points)


def _load_binding() -> dict[str, Any]:
    return json.loads(BINDING_PATH.read_text(encoding="utf-8"))


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


@pytest.mark.integration
def test_scheme_02_r02_sim_binding_drives_run(tmp_path: Path) -> None:
    """r02 sim binding must produce a control LUT that satisfies strong checks."""
    binding = _load_binding()
    kwargs = _resolve_kwargs(binding)
    kwargs["output_path"] = tmp_path / "control_lut_r02_acceptance.json"

    output = run(**kwargs)

    expect = binding["expect"]
    strong_keys = set(binding["strong_checks"])
    soft_keys = set(binding["soft_checks"])

    strong_failures: list[str] = []
    soft_warnings: list[str] = []
    output_view = _with_p0_derived_metrics(output)

    for key, expected_value in expect.items():
        passed, message = eval_expect_check(key, expected_value, output_view)
        if passed:
            continue
        if key in strong_keys:
            strong_failures.append(f"STRONG fail: {key} -> {message}")
        elif key in soft_keys:
            soft_warnings.append(f"SOFT warn: {key} -> {message}")
        else:
            strong_failures.append(f"UNCLASSIFIED fail: {key} -> {message}")

    for warning_message in soft_warnings:
        warnings.warn(warning_message, stacklevel=1)

    assert not strong_failures, (
        "S02 r02 sim binding produced strong-check failures:\n  - "
        + "\n  - ".join(strong_failures)
    )


def test_scheme_02_jump_thresholds_are_marked_as_r02_proxy_gates() -> None:
    binding = _load_binding()
    threshold_maturity = binding["threshold_maturity"]

    for key, maturity_key in (
        ("p0_acceptance.max_id_jump_a.max", "mode_transitions.id_jump_a_max"),
        ("p0_acceptance.max_iq_jump_a.max", "mode_transitions.iq_jump_a_max"),
    ):
        assert binding["expect"][key] == 60.0
        assert key in binding["soft_checks"]
        assert key not in binding["strong_checks"]
        maturity = threshold_maturity[maturity_key]
        assert maturity["r02_proxy_soft_gate_a"] == 60.0
        assert maturity["r03_production_target_a"] == 30.0
        assert maturity["engineering_validated"] is False


@pytest.mark.integration
def test_scheme_02_binding_dvp_mapping_is_documented() -> None:
    """Every S02-DV-xxx ID in the DVP draft must appear in binding dvp_mapping."""
    binding = _load_binding()
    mapping = binding["dvp_mapping"]
    expected_ids = {
        "S02-DV-001",
        "S02-DV-002",
        "S02-DV-003",
        "S02-DV-004",
        "S02-DV-005",
    }
    missing = expected_ids - set(mapping)
    assert not missing, f"binding dvp_mapping missing: {sorted(missing)}"


@pytest.mark.integration
def test_scheme_02_binding_engineering_validated_is_false() -> None:
    """r02 sheets must NOT flip engineering_validated to true."""
    binding = _load_binding()
    assert binding["engineering_validated"] is False, (
        "S02 r02 sim binding must keep engineering_validated=false; "
        "only after FEA + bench + HIL closure can this be flipped."
    )
