from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

from tests.test_scheme_catalog import EXPECTED_SCHEME_IDS


COVERAGE_PATH = Path("models/scheme_simulation_coverage.json")
SIM_BINDING_SCHEMA_PATH = Path("models/sim_binding_schema.json")
SIM_BINDING_GLOB = "engineering/v2/scheme-*/parameters/V2-S*-PARAM-sim_binding-r02.json"


def _sim_binding_paths() -> list[Path]:
    paths = sorted(Path(".").glob(SIM_BINDING_GLOB))
    assert len(paths) == 12
    return paths


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
        assert record["gate_class"] in {"smoke", "proxy", "production_target"}
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


def test_high_fidelity_next_steps_reference_pyfluent_cfd_path() -> None:
    data = _load_json(COVERAGE_PATH)
    records = {record["id"]: record for record in data["schemes"]}

    for scheme_id in {
        "nonlinear_flux_lut",
        "magnetic_saturation_codesign",
        "pmasynrm_high_saliency_low_pm",
        "thermal_demag_safety_protection",
    }:
        next_step = records[scheme_id]["next_simulation_step"]
        assert "sim.run_pyfluent_workflow" in next_step, scheme_id
        assert "cooling CFD" in next_step, scheme_id


def test_all_sim_bindings_match_schema() -> None:
    schema = _load_json(SIM_BINDING_SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    for path in _sim_binding_paths():
        binding = _load_json(path)
        errors = sorted(validator.iter_errors(binding), key=lambda error: error.path)
        assert errors == [], f"{path}: {errors}"


def test_sim_binding_maturity_and_gate_class_match_coverage() -> None:
    coverage = _load_json(COVERAGE_PATH)
    records = {record["id"]: record for record in coverage["schemes"]}

    for path in _sim_binding_paths():
        binding = _load_json(path)
        record = records[binding["scheme_id"]]

        assert binding["engineering_validated"] is False, path
        assert binding["simulation_status"] == record["simulation_status"], path
        assert binding["model_maturity"] == record["model_maturity"], path
        assert binding["gate_class"] == record["gate_class"], path
        if binding["simulation_status"] == "binding_smoke_passed":
            assert binding["gate_class"] == "smoke", path
        else:
            assert binding["gate_class"] in {"proxy", "production_target"}, path
