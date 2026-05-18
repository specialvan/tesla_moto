from __future__ import annotations

import json
from pathlib import Path

from tests.test_scheme_catalog import EXPECTED_SCHEME_IDS


COVERAGE_PATH = Path("models/scheme_simulation_coverage.json")


def test_every_scheme_has_simulation_coverage_record() -> None:
    data = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    records = data["schemes"]

    assert {record["id"] for record in records} == EXPECTED_SCHEME_IDS


def test_each_simulation_record_has_reproducible_artifacts() -> None:
    data = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))

    for record in data["schemes"]:
        assert record["simulation_status"] in {
            "binding_smoke_passed",
            "numeric_proxy_passed",
            "needs_next_numeric_model",
        }
        assert record["model_maturity"] in {
            "synthetic_fixture",
            "proxy_model",
            "research_pool_proxy",
            "parameterized_linear_model",
            "physics_model",
        }
        assert record["production_drawing_ready"] is False
        assert record["manufacturing_release_ready"] is False
        assert record["engineering_validated"] is False
        maturity_flags = record["maturity_flags"]
        assert maturity_flags["binding_smoke_passed"] is True
        assert maturity_flags["physics_model_validated"] is False
        assert maturity_flags["engineering_validated"] is False
        assert record["pytest_tests"], record["id"]
        assert record["result_artifacts"], record["id"]
        assert record["next_simulation_step"], record["id"]
        for pytest_test in record["pytest_tests"]:
            assert Path(
                pytest_test
            ).exists(), f"{record['id']} pytest test missing: {pytest_test}"
        for artifact in record["result_artifacts"]:
            assert Path(
                artifact
            ).exists(), f"{record['id']} artifact missing: {artifact}"


def test_mainline_and_research_schemes_use_non_overstated_maturity() -> None:
    data = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    records = {record["id"]: record for record in data["schemes"]}

    for scheme_id in {
        "negative_d_axis_field_weakening",
        "mtpa_fw_mtpv_control",
        "thermal_demag_safety_protection",
    }:
        assert records[scheme_id]["simulation_status"] == "numeric_proxy_passed"
        assert records[scheme_id]["model_maturity"] == "parameterized_linear_model"

    for scheme_id in {
        "variable_magnetization_memory_motor",
        "hybrid_excitation",
        "winding_reconfiguration",
        "multiphase_phase_group_control",
    }:
        assert records[scheme_id]["simulation_status"] == "binding_smoke_passed"
        assert records[scheme_id]["model_maturity"] == "research_pool_proxy"
        assert records[scheme_id]["maturity_flags"]["numeric_proxy_passed"] is False

    assert records["nonlinear_flux_lut"]["model_maturity"] == "synthetic_fixture"
    assert records["nonlinear_flux_lut"]["simulation_status"] == "binding_smoke_passed"
