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
            "passed_numeric_simulation",
            "passed_architecture_verification",
            "needs_next_numeric_model",
        }
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


def test_at_least_mainline_schemes_have_numeric_simulation_results() -> None:
    data = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    statuses = {record["id"]: record["simulation_status"] for record in data["schemes"]}

    for scheme_id in {
        "negative_d_axis_field_weakening",
        "mtpa_fw_mtpv_control",
        "variable_magnetization_memory_motor",
        "magnetic_saturation_codesign",
        "pmasynrm_high_saliency_low_pm",
        "thermal_demag_safety_protection",
    }:
        assert statuses[scheme_id] == "passed_numeric_simulation"
