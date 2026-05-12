from __future__ import annotations

import json
from pathlib import Path


CATALOG_PATH = Path("models/scheme_engineering_catalog.json")
REPORT_PATH = Path("reports/scheme_engineering_landing_matrix.md")
DIAGRAM_REPORT_PATH = Path("reports/scheme_driver_power_protocol_diagrams.md")
BOM_EDA_PATH = Path("models/scheme_bom_eda_catalog.json")
BOM_EDA_REPORT_PATH = Path("reports/scheme_bom_eda_integration_design.md")

EXPECTED_SCHEME_IDS = {
    "negative_d_axis_field_weakening",
    "mtpa_fw_mtpv_control",
    "svpwm_overmodulation_voltage_utilization",
    "nonlinear_flux_lut",
    "magnetic_saturation_codesign",
    "pmasynrm_high_saliency_low_pm",
    "variable_magnetization_memory_motor",
    "hybrid_excitation",
    "winding_reconfiguration",
    "multiphase_phase_group_control",
    "thermal_demag_safety_protection",
    "weighted_efficiency_pareto_selection",
}

REQUIRED_FIELDS = {
    "id",
    "name",
    "route_class",
    "maturity",
    "engineering_goal",
    "modeling_artifacts",
    "required_inputs",
    "experiments",
    "acceptance_criteria",
    "failure_modes",
    "stage_gate",
    "deliverables",
}


def test_scheme_catalog_covers_every_engineering_route() -> None:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    schemes = data["schemes"]
    ids = {scheme["id"] for scheme in schemes}

    assert ids == EXPECTED_SCHEME_IDS


def test_each_scheme_has_engineering_landing_fields() -> None:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    for scheme in data["schemes"]:
        assert REQUIRED_FIELDS <= set(scheme), scheme["id"]
        for field in REQUIRED_FIELDS - {"id", "name", "route_class", "maturity"}:
            assert scheme[field], f"{scheme['id']} missing non-empty {field}"
        assert len(scheme["modeling_artifacts"]) >= 2
        assert len(scheme["experiments"]) >= 2
        assert len(scheme["acceptance_criteria"]) >= 2
        assert len(scheme["deliverables"]) >= 2


def test_engineering_landing_report_references_every_scheme() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")

    for scheme_id in EXPECTED_SCHEME_IDS:
        assert scheme_id in report


def test_driver_power_protocol_diagram_report_references_every_scheme() -> None:
    report = DIAGRAM_REPORT_PATH.read_text(encoding="utf-8")

    for scheme_id in EXPECTED_SCHEME_IDS:
        assert scheme_id in report

    assert "驱动设计图" in report
    assert "上电时序图" in report
    assert "协议链路图" in report
    assert report.count("```mermaid") >= 36


def test_bom_eda_catalog_covers_every_scheme_with_required_design_fields() -> None:
    data = json.loads(BOM_EDA_PATH.read_text(encoding="utf-8"))
    entries = data["schemes"]
    ids = {entry["id"] for entry in entries}

    assert ids == EXPECTED_SCHEME_IDS

    required = {
        "id",
        "bom_groups",
        "eda_blocks",
        "interfaces",
        "protections",
        "pcb_integration_notes",
        "design_status",
    }
    for entry in entries:
        assert required <= set(entry), entry["id"]
        assert len(entry["bom_groups"]) >= 4, entry["id"]
        assert len(entry["eda_blocks"]) >= 3, entry["id"]
        assert len(entry["interfaces"]) >= 2, entry["id"]
        assert len(entry["protections"]) >= 2, entry["id"]
        assert entry["design_status"] in {
            "v0_architecture",
            "v1_schematic_planning",
            "requires_hardware_trade_study",
        }


def test_bom_eda_integration_report_references_every_scheme_and_core_sections() -> None:
    report = BOM_EDA_REPORT_PATH.read_text(encoding="utf-8")

    for scheme_id in EXPECTED_SCHEME_IDS:
        assert scheme_id in report

    assert "BOM 配件清单" in report
    assert "EDA 电路集成设计" in report
    assert "连接器与协议" in report
    assert "PCB/安规集成注意事项" in report
