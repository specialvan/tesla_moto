from __future__ import annotations

import json
from pathlib import Path

from tests.test_scheme_catalog import EXPECTED_SCHEME_IDS


PROCESS_PATH = Path("models/scheme_industry_stage_gate_process.json")
REPORT_PATH = Path("reports/scheme_industry_design_stage_gate_process.md")

REQUIRED_PHASES = [
    "G0_strategy_and_item_definition",
    "G1_requirements_and_safety_concept",
    "G2_system_architecture_and_trade_study",
    "G3_model_simulation_and_controls",
    "G4_bom_eda_schematic_and_dfmea",
    "G5_pcb_layout_prototype_and_bringup",
    "G6_bench_dv_and_calibration",
    "G7_pv_release_and_change_control",
]


def test_industry_stage_gate_process_has_required_phases() -> None:
    data = json.loads(PROCESS_PATH.read_text(encoding="utf-8"))
    phase_ids = [phase["id"] for phase in data["common_stage_gates"]]

    assert phase_ids == REQUIRED_PHASES
    for phase in data["common_stage_gates"]:
        assert phase["entry_criteria"]
        assert phase["work_products"]
        assert phase["exit_criteria"]
        assert phase["review_board"]


def test_each_scheme_has_process_overlay_and_work_products() -> None:
    data = json.loads(PROCESS_PATH.read_text(encoding="utf-8"))
    overlays = data["scheme_overlays"]

    assert set(overlays) == EXPECTED_SCHEME_IDS
    for scheme_id, overlay in overlays.items():
        assert overlay["primary_risk"]
        assert len(overlay["mandatory_work_products"]) >= 4, scheme_id
        assert len(overlay["eda_focus"]) >= 2, scheme_id
        assert len(overlay["bom_focus"]) >= 2, scheme_id
        assert len(overlay["next_design_actions"]) >= 3, scheme_id


def test_stage_gate_report_references_every_scheme_and_mature_methods() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")

    for scheme_id in EXPECTED_SCHEME_IDS:
        assert scheme_id in report

    for phrase in [
        "V 模型",
        "APQP",
        "功能安全",
        "ASPICE",
        "DFMEA",
        "DVP&R",
        "PPAP",
    ]:
        assert phrase in report
