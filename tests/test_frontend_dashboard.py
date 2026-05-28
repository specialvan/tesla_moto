from pathlib import Path
from html.parser import HTMLParser
import subprocess
import re


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "controllable_flux_motor_kb.html"


class _ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_script = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._in_script = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_script:
            self.scripts.append(data)


def test_dashboard_inline_script_is_browser_parseable(tmp_path):
    parser = _ScriptCollector()
    parser.feed(HTML.read_text(encoding="utf-8"))
    script = "\n".join(parser.scripts)
    script_path = tmp_path / "dashboard-inline.js"
    script_path.write_text(script, encoding="utf-8")

    result = subprocess.run(
        ["node", "--check", str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_dashboard_has_modern_data_visualization_contract():
    page = HTML.read_text(encoding="utf-8")

    assert "<title>可控磁通量电机客户数据看板</title>" in page
    assert 'id="app-dashboard"' in page
    assert 'id="pareto-chart"' in page
    assert 'id="cycle-chart"' in page
    assert 'id="iron-loss-chart"' in page
    assert 'data-candidate-filter' in page
    assert "let paretoFront =" in page
    assert "hybrid_excitation_if_plus_20" in page


def test_dashboard_dom_ids_are_unique_for_frontend_bindings():
    page = HTML.read_text(encoding="utf-8")
    ids = re.findall(r'id="([^"]+)"', page)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})

    assert duplicates == []


def test_dashboard_keeps_engineering_evidence_links():
    page = HTML.read_text(encoding="utf-8")

    assert "experiments/exp_010_weighted_efficiency_pareto/weighted_efficiency_pareto_results.csv" in page
    assert "experiments/exp_011_iron_loss/iron_loss_sweep_results.csv" in page
    assert "wiki/controllable_flux_motor_research_plan.md" in page


def test_dashboard_is_customer_facing_chinese_algorithm_board():
    page = HTML.read_text(encoding="utf-8")

    assert "客户数据看板" in page
    assert 'id="benefit-chart"' in page
    assert 'id="algorithm-map"' in page
    assert "算法落地对应关系" in page
    assert "前后变化收益" in page
    assert "animateValue" in page
    assert "MTPA / 弱磁 / MTPV" in page
    assert "Bertotti 铁耗估算" in page
    assert "控制 LUT 生成" in page


def test_dashboard_has_customer_demo_playback_and_delivery_board():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="demo-flow"' in page
    assert 'id="play-toggle"' in page
    assert "自动演示" in page
    assert "数据动效展示" in page
    assert "客户验证准备清单" in page
    assert "renderDemoFlow" in page
    assert "startPlayback" in page
    assert "验证材料" in page


def test_dashboard_uses_candidate_and_validation_wording_not_delivery_claims():
    page = HTML.read_text(encoding="utf-8")
    handoff = (ROOT / "reports" / "dashboard_black_gold_handoff.md").read_text(
        encoding="utf-8"
    )

    forbidden_phrases = [
        "客户交付清单",
        "每一项交付物",
        "可交付的软件模块",
        "可刷写的控制查表数据",
        "可交付软件资产",
        "控制轨迹可交付",
        "客户决策已接入",
        "可交付的客户决策",
        "落地交付",
        "交付动作",
        "交付闭环",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in page

    assert "客户验证准备清单" in page
    assert "候选控制查表数据" in page
    assert "控制 LUT 候选" in page
    assert "验证准备" in page
    assert "验证准备清单" in handoff
    assert "交付清单" not in handoff


def test_dashboard_fetches_backend_api_with_fallback():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="api-status"' in page
    assert 'id="refresh-data"' in page
    assert "loadDashboardData" in page
    assert 'fetch("/api/dashboard"' in page
    assert 'fetch("/api/schema"' in page
    assert "payload.meta?.source !== \"backend-api\"" in page
    assert "payload.meta?.schemaVersion !== 1" in page
    assert "applyBackendSchema" in page
    assert "API schema contract incomplete" in page
    assert "validateDashboardSchema" in page
    assert 'validateDashboardSchema(endpoints.find(endpoint => endpoint.path === "/api/dashboard"))' in page
    assert 'includesAll(endpoint.responseObjectKeys?.paretoFront, ["candidate", "label", "meanScore", "feasible", "loss", "family", "color"])' in page
    assert 'includesAll(endpoint.responseObjectKeys?.cycleRows, ["candidate", "cycle", "feasibleWeight", "copperLoss", "score"])' in page
    assert 'includesAll(endpoint.responseObjectKeys?.ironLossRows, ["speed", "targetFeasible", "ironLoss", "efficiency", "freqOutOfRange"])' in page
    assert "endpoint.responseTupleLengths?.algorithmRows !== 4" in page
    assert "endpoint.responseTupleLengths?.deliveryItems !== 2" in page
    assert "接口已连接" in page
    assert "离线回退数据" in page
    assert "正在同步" in page


def test_dashboard_has_customer_summary_and_export_controls():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="customer-brief"' in page
    assert 'id="export-brief"' in page
    assert "客户汇报摘要" in page
    assert "导出摘要" in page
    assert "renderCustomerBrief" in page
    assert "exportCustomerBrief" in page
    assert "loadCustomerBrief" in page
    assert 'fetch("/api/customer-brief", {' in page
    assert "buildDecisionPackState()" in page
    assert 'recordApiSync("/api/customer-brief", true' in page
    assert 'recordApiSync("/api/customer-brief", false' in page
    assert "navigator.clipboard.writeText" in page


def test_dashboard_has_compare_mode_and_briefing_cards():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="compare-mode"' in page
    assert 'id="compare-target"' in page
    assert 'id="compare-board"' in page
    assert "方案对比模式" in page
    assert "客户汇报信息卡" in page
    assert "renderCompareBoard" in page
    assert "compareCandidate" in page


def test_dashboard_has_workload_weight_simulator():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="weight-simulator"' in page
    assert 'data-weight-input="urban_low_speed"' in page
    assert 'data-weight-input="highway_high_speed"' in page
    assert 'data-weight-input="launch_peak_torque"' in page
    assert 'id="simulated-ranking"' in page
    assert 'id="weight-recommendation"' in page
    assert 'id="apply-recommendation"' in page
    assert "renderWeightSimulator" in page
    assert "calculateWeightedRanking" in page
    assert "bindWeightSimulator" in page


def test_dashboard_has_opendesign_handoff_contract():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"

    assert 'data-design-system="opendesign-dashboard"' in page
    assert 'id="design-handoff"' in page
    assert 'id="export-design-spec"' in page
    assert "OpenDesign 设计交付" in page
    assert "OPENDESIGN_TOKENS" in page
    assert "exportOpenDesignSpec" in page
    assert "loadOpenDesignSpec" in page
    assert 'fetch("/api/design-spec", { headers: { "Accept": "application/json" } })' in page
    assert 'recordApiSync("/api/design-spec", true' in page
    assert 'recordApiSync("/api/design-spec", false' in page
    assert "reports/open_design_dashboard_spec.json" in page
    assert spec.exists()
    assert "customer_dashboard" in spec.read_text(encoding="utf-8")



def test_dashboard_locks_black_gold_visual_handoff():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert "--bg: #08090d" in page
    assert "--panel: #12141b" in page
    assert "--gold: #d6b260" in page
    assert "#f8ecd2" in page
    assert "linear-gradient(135deg, #f3d58a, #b78a32)" in page
    assert 'id="opendesign-status"' in page
    assert 'id="decision-grid"' in page
    assert 'id="benefit-waterfall"' in page
    assert 'id="scenario-presets"' in page
    assert 'id="interactive-insights"' in page
    assert "premium black-gold engineering dashboard" in spec_text
    assert '"background": "#08090d"' in spec_text
    assert '"surface": "#12141b"' in spec_text
    assert "黑金高级工程风格" in handoff_text
    assert "禁止跑偏" in handoff_text



def test_dashboard_has_roi_sensitivity_matrix():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="sensitivity-matrix"' in page
    assert 'data-opendesign-component="sensitivity-matrix"' in page
    assert 'id="sensitivity-grid"' in page
    assert 'id="sensitivity-headline"' in page
    assert "收益敏感性矩阵" in page
    assert "ROI 敏感性" in page
    assert "const sensitivityProfiles" in page
    assert "renderSensitivityMatrix" in page
    assert "applySensitivityProfile" in page
    assert "computeBusinessCase" in page
    assert "sensitivity-matrix" in spec_text
    assert "ROI sensitivity matrix" in spec_text


def test_dashboard_has_customer_validation_stage_gate_board():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="stage-gate-board"' in page
    assert 'data-opendesign-component="stage-gate-board"' in page
    assert 'id="stage-gate-grid"' in page
    assert 'id="stage-gate-progress"' in page
    assert "客户验证阶段门" in page
    assert "验证里程碑" in page
    assert "buildStageGateState" in page
    assert "renderStageGateBoard" in page
    assert "stage-gate-board" in spec_text
    assert "customer validation stage gate board" in spec_text


def test_dashboard_has_evidence_gap_priority_board():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="evidence-gap-priority"' in page
    assert 'data-opendesign-component="evidence-gap-priority"' in page
    assert 'id="evidence-gap-grid"' in page
    assert 'id="evidence-gap-headline"' in page
    assert 'data-evidence-gap' in page
    assert "证据缺口优先级" in page
    assert "优先补证" in page
    assert "evidenceGapRows" in page
    assert "activeEvidenceGap" in page
    assert "buildEvidenceGapPriority" in page
    assert "renderEvidenceGapPriority" in page
    assert "applyEvidenceGap" in page
    assert "evidence-gap-priority" in spec_text
    assert "evidence gap priority board" in spec_text
    assert "证据缺口优先级" in handoff_text

def test_dashboard_has_customer_meeting_script_value_path():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="meeting-script"' in page
    assert 'data-opendesign-component="meeting-script"' in page
    assert 'id="meeting-script-headline"' in page
    assert 'id="meeting-script-path"' in page
    assert 'id="meeting-objections"' in page
    assert 'id="copy-meeting-script"' in page
    assert "客户决策讲解脚本" in page
    assert "价值路径" in page
    assert "buildMeetingScript" in page
    assert "engineering_validated=false" in page
    assert "renderMeetingScript" in page
    assert "copyMeetingScript" in page
    assert "meeting-script" in spec_text
    assert "customer decision talk track" in spec_text


def test_dashboard_has_customer_review_question_board():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="review-question-board"' in page
    assert 'data-opendesign-component="review-question-board"' in page
    assert 'id="review-question-list"' in page
    assert 'id="review-question-answer"' in page
    assert 'id="copy-review-answer"' in page
    assert 'data-review-question' in page
    assert "客户评审问题清单" in page
    assert "问题闭环" in page
    assert "reviewQuestionRows" in page
    assert "activeReviewQuestion" in page
    assert "buildReviewAnswer" in page
    assert "renderReviewQuestionBoard" in page
    assert "copyReviewAnswer" in page
    assert "review-question-board" in spec_text
    assert "customer review question board" in spec_text
    assert "客户评审问题清单" in handoff_text

def test_dashboard_has_algorithm_maturity_matrix():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="algorithm-maturity"' in page
    assert 'data-opendesign-component="algorithm-maturity"' in page
    assert 'id="algorithm-maturity-grid"' in page
    assert 'id="algorithm-maturity-headline"' in page
    assert 'data-maturity-algorithm' in page
    assert "算法落地成熟度矩阵" in page
    assert "模型成熟度" in page
    assert "数据成熟度" in page
    assert "接口成熟度" in page
    assert "验证成熟度" in page
    assert "客户价值" in page
    assert "algorithmMaturityRows" in page
    assert "activeAlgorithmMaturity" in page
    assert "renderAlgorithmMaturity" in page
    assert "applyAlgorithmMaturity" in page
    assert "algorithm-maturity" in spec_text
    assert "algorithm implementation maturity matrix" in spec_text
    assert "算法落地成熟度矩阵" in handoff_text

def test_dashboard_has_solution_drilldown_workbench():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="solution-drilldown"' in page
    assert 'id="drilldown-tabs"' in page
    assert 'id="drilldown-panel"' in page
    assert 'data-drilldown-tab' in page
    assert 'activeDrilldown = "benefit"' in page
    assert '"benefit"' in page
    assert '"risk"' in page
    assert '"delivery"' in page
    assert '"evidence"' in page
    assert "renderSolutionDrilldown" in page
    assert "renderConfidenceMeter" in page
    assert "renderEvidenceLadder" in page
    assert "calculateCandidateContext" in page
    assert "solution-drilldown" in spec_text
    assert "four-tab candidate diagnostic workbench" in spec_text



def test_dashboard_has_business_case_calculator():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="business-case"' in page
    assert 'id="business-controls"' in page
    assert 'id="business-results"' in page
    assert 'id="business-note"' in page
    assert 'data-business-input="production"' in page
    assert 'data-business-input="mileage"' in page
    assert 'data-business-input="energyPrice"' in page
    assert 'data-business-input="validationInvestment"' in page
    assert "calculateBusinessCase" in page
    assert "ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW = 0.12" in page
    assert "savedWatts / 1000 * ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW" in page
    assert "savedWatts / 1000 * 1.8" not in page
    assert "renderBusinessCase" in page
    assert "bindBusinessCase" in page
    assert "business-case" in spec_text
    assert "ROI calculator" in spec_text



def test_dashboard_has_presentation_mode():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="presentation-bar"' in page
    assert 'id="presentation-toggle"' in page
    assert 'id="presentation-progress"' in page
    assert "presentationSteps" in page
    assert "bindPresentationMode" in page
    assert "focusPresentationStep" in page
    assert "nextPresentationStep" in page
    assert "presentation-mode" in page
    assert "presentation-mode" in spec_text



def test_dashboard_exports_customer_decision_pack():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="export-decision-pack"' in page
    assert "buildDecisionPack" in page
    assert "exportDecisionPack" in page
    assert "premium black-gold engineering dashboard" in page
    assert "fleetAnnualSavingYuan" in page
    assert "paybackMonths" in page
    assert "maturity: engineeringMaturityContract()" in page
    assert "engineering_validated: false" in page
    assert "production_release_allowed: false" in page
    assert "Decision pack copy skipped" in page
    assert "decision-pack-export" in page
    assert "decision-pack-export" in spec_text


def test_dashboard_has_customer_decision_pack_preview():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="decision-pack-preview"' in page
    assert 'data-opendesign-component="decision-pack-preview"' in page
    assert 'id="decision-pack-preview-summary"' in page
    assert 'id="decision-pack-preview-list"' in page
    assert 'id="decision-pack-evidence-score"' in page
    assert 'id="copy-decision-pack-preview"' in page
    assert 'id="decision-pack-preview-toast"' in page
    assert 'data-pack-preview-item' in page
    assert "客户决策包预览" in page
    assert "证据链完整度" in page
    assert "复制预览" in page
    assert "maturityDisclaimerLines().join" in page
    assert "buildDecisionPackPreview" in page
    assert "renderDecisionPackPreview" in page
    assert "copyDecisionPackPreview" in page
    assert "renderDecisionPackPreview();" in page
    assert "const topGap = gapState.active" in page
    assert "activeReviewQuestion = button.dataset.reviewQuestion;" in page
    assert "renderReviewQuestionBoard();\n          renderDecisionPackPreview();" in page
    assert "function applyEvidenceGap(id)" in page
    assert "renderEvidenceGapPriority();\n      renderDecisionPackPreview();" in page
    assert "decision-pack-preview" in spec_text
    assert "customer decision package preview" in spec_text
    assert "客户决策包预览" in handoff_text


def test_dashboard_has_customer_minutes_generator():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="customer-minutes-generator"' in page
    assert 'data-opendesign-component="customer-minutes-generator"' in page
    assert 'id="customer-minutes-mode-tabs"' in page
    assert 'id="customer-minutes-summary"' in page
    assert 'id="customer-minutes-actions"' in page
    assert 'id="customer-minutes-risks"' in page
    assert 'id="copy-customer-minutes"' in page
    assert 'id="customer-minutes-toast"' in page
    assert 'data-minutes-mode' in page
    assert "客户评审纪要生成" in page
    assert "行动项闭环" in page
    assert "复制纪要" in page
    assert "minutesModes" in page
    assert "activeMinutesMode" in page
    assert "buildCustomerMinutes" in page
    assert "...maturityDisclaimerLines()" in page
    assert "renderCustomerMinutes" in page
    assert "copyCustomerMinutes" in page
    assert "renderCustomerMinutes();" in page
    assert "customer-minutes-generator" in spec_text
    assert "customer review minutes generator" in spec_text
    assert "客户评审纪要生成" in handoff_text


def test_dashboard_has_validation_action_timeline():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="validation-action-timeline"' in page
    assert 'data-opendesign-component="validation-action-timeline"' in page
    assert 'id="validation-timeline-summary"' in page
    assert 'id="validation-timeline-rail"' in page
    assert 'id="validation-timeline-detail"' in page
    assert 'id="copy-validation-timeline"' in page
    assert 'id="validation-timeline-toast"' in page
    assert 'data-validation-step' in page
    assert "客户验证行动时间轴" in page
    assert "回填目标" in page
    assert "复制时间轴" in page
    assert "activeValidationStep" in page
    assert "buildValidationTimeline" in page
    assert "renderValidationTimeline" in page
    assert "copyValidationTimeline" in page
    assert "renderValidationTimeline();" in page
    assert "validation-action-timeline" in spec_text
    assert "customer validation action timeline" in spec_text
    assert "客户验证行动时间轴" in handoff_text


def test_dashboard_has_validation_risk_heatmap():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="validation-risk-heatmap"' in page
    assert 'data-opendesign-component="validation-risk-heatmap"' in page
    assert 'id="validation-risk-summary"' in page
    assert 'id="validation-risk-grid"' in page
    assert 'id="validation-risk-detail"' in page
    assert 'id="copy-validation-risk"' in page
    assert 'id="validation-risk-toast"' in page
    assert 'data-validation-risk' in page
    assert "验证风险热力图" in page
    assert "责任矩阵" in page
    assert "复制风险矩阵" in page
    assert "activeValidationRisk" in page
    assert "buildValidationRiskHeatmap" in page
    assert "renderValidationRiskHeatmap" in page
    assert "copyValidationRiskHeatmap" in page
    assert "renderValidationRiskHeatmap();" in page
    assert "validation-risk-heatmap" in spec_text
    assert "customer validation risk heatmap" in spec_text
    assert "验证风险热力图" in handoff_text


def test_dashboard_has_customer_acceptance_gate():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    handoff = ROOT / "reports" / "dashboard_black_gold_handoff.md"
    spec_text = spec.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert 'id="customer-acceptance-gate"' in page
    assert 'data-opendesign-component="customer-acceptance-gate"' in page
    assert 'id="acceptance-gate-summary"' in page
    assert 'id="acceptance-gate-meter"' in page
    assert 'id="acceptance-gate-checks"' in page
    assert 'id="acceptance-gate-detail"' in page
    assert 'id="copy-acceptance-gate"' in page
    assert 'id="acceptance-gate-toast"' in page
    assert 'data-acceptance-check' in page
    assert "客户验收门禁" in page
    assert "验收门禁分" in page
    assert "复制验收结论" in page
    assert "????" not in page
    assert "activeAcceptanceCheck" in page
    assert "buildCustomerAcceptanceGate" in page
    assert "not for engineering release / production release" in page
    assert "renderCustomerAcceptanceGate" in page
    assert "copyCustomerAcceptanceGate" in page
    assert "renderCustomerAcceptanceGate();" in page
    assert "buildValidationRiskHeatmap" in page
    assert "buildValidationTimeline" in page
    assert "buildDecisionPackPreview" in page
    assert "customer-acceptance-gate" in spec_text
    assert "customer acceptance gate" in spec_text
    assert "customer-acceptance-gate" in handoff_text
    assert "????" not in handoff_text


def test_dashboard_decision_pack_export_uses_backend_api_with_fallback():
    page = HTML.read_text(encoding="utf-8")

    assert "loadDecisionPack" in page
    assert "buildDecisionPackQuery" in page
    assert "/api/decision-pack?${buildDecisionPackQuery()}" in page
    assert "URLSearchParams" in page
    assert "params.set(\"candidate\", selected)" in page
    assert "validateDecisionPackSchema" in page
    assert "getQueryKeys" in page
    assert "postJson" in page
    assert "responseObjectKeys" in page
    assert "API decision-pack schema contract incomplete" in page
    assert "validateEngineeringMaturity(payload.maturity)" in page
    assert "payload.businessCase.conversionKwhPer100kmPerKw !== ROI_ENERGY_CONVERSION_KWH_PER_100KM_PER_KW" in page
    assert 'includesAll(endpoint.responseObjectKeys?.businessCase, ["assumptions", "conversionKwhPer100kmPerKw", "perVehicleAnnualSavingYuan", "fleetAnnualSavingYuan", "paybackMonths"])' in page
    assert 'includesAll(endpoint.responseObjectKeys?.maturity, ["engineering_validated", "production_release_allowed", "model_maturity", "required_evidence", "not_allowed_claims"])' in page
    assert "[data-weight-input]" in page
    assert "businessAssumptions" in page
    assert "buildDecisionPack" in page
    assert "return buildDecisionPack()" in page
    assert "exportDecisionPack" in page
    assert "schemaVersion: 1" in page


def test_dashboard_saves_backend_session_snapshot_from_current_ui_state():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="save-session-snapshot"' in page
    assert 'id="clear-session-snapshot"' in page
    assert 'id="session-snapshot-status"' in page
    assert "buildSessionSnapshot" in page
    assert "saveSessionSnapshot" in page
    assert "clearSessionSnapshot" in page
    assert "validateSessionSnapshotSchema" in page
    assert 'includesAll(endpoint.methods, ["GET", "POST", "DELETE"])' in page
    assert 'includesAll(endpoint.responseObjectKeys?.snapshot, ["candidate", "businessAssumptions", "weights", "decisionPack", "apiSyncLog", "metadata"])' in page
    assert "API session-snapshot schema contract incomplete" in page
    assert 'fetch("/api/session-snapshot", {' in page
    assert 'fetch("/api/session-snapshot", { method: "DELETE"' in page
    assert 'recordApiSync("/api/session-snapshot", true' in page
    assert 'recordApiSync("/api/session-snapshot", false' in page
    assert "apiSyncLog" in page
    assert "decisionPack" in page
    assert "snapshot.metadata" in page
    assert "snapshotId" in page
    assert "updatedAt" in page
    assert '"/api/session-snapshot"' in page


def test_dashboard_restores_backend_session_snapshot_on_runtime_load():
    page = HTML.read_text(encoding="utf-8")

    assert "applySessionSnapshotPayload" in page
    assert "loadSessionSnapshot" in page
    assert 'fetch("/api/session-snapshot", { headers: { "Accept": "application/json" } })' in page
    assert "payload.snapshotAvailable" in page
    assert "applyScenarioState(payload.snapshot)" in page
    assert "renderSessionSnapshotStatus(payload.metadata" in page
    assert 'recordApiSync("/api/session-snapshot", true, payload.snapshot?.candidate || "none")' in page
    assert "await loadSessionSnapshot()" in page


def test_dashboard_restores_session_snapshot_api_sync_log_history():
    page = HTML.read_text(encoding="utf-8")

    assert "applySessionSnapshotApiSyncLog" in page
    assert "payload.snapshot?.apiSyncLog" in page
    assert "restored:" in page
    assert "const basePaths =" in page
    assert "!basePaths.includes(path)" in page
    assert 'apiSyncLog[path] = {' in page
    assert "...item" in page
    assert "renderApiSyncLog()" in page



def test_dashboard_has_route_benchmark_board():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="benchmark-board"' in page
    assert 'id="benchmark-toolbar"' in page
    assert 'id="benchmark-grid"' in page
    assert 'id="benchmark-summary"' in page
    assert "benchmarkFamilies" in page
    assert "renderBenchmarkBoard" in page
    assert "data-benchmark-candidate" in page
    assert "benchmark-board" in spec_text



def test_dashboard_has_risk_closure_board():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="closure-board"' in page
    assert 'id="closure-grid"' in page
    assert "renderClosureBoard" in page
    assert "closure-card" in page
    assert "closure-status" in page
    assert "Vmax - |Vdq|" in page
    assert "Bertotti" in page
    assert "HIL" in page
    assert "closure-board" in spec_text



def test_dashboard_has_delivery_health_panel():
    page = HTML.read_text(encoding="utf-8")
    spec = ROOT / "reports" / "open_design_dashboard_spec.json"
    spec_text = spec.read_text(encoding="utf-8")

    assert 'id="delivery-health"' in page
    assert 'id="health-grid"' in page
    assert "renderDeliveryHealth" in page
    assert "health-item" in page
    assert "health-dot" in page
    assert "/api/dashboard" in page
    assert "OpenDesign" in page
    assert "EXP-010" in page
    assert "delivery-health" in spec_text


def test_dashboard_fetches_runtime_health_for_delivery_status():
    page = HTML.read_text(encoding="utf-8")

    assert "let backendHealth = null" in page
    assert "applyBackendHealth" in page
    assert "loadBackendHealth" in page
    assert "loadBackendSchema" in page
    assert "loadScenarioState" in page
    assert 'fetch("/api/health"' in page
    assert 'fetch("/api/schema"' in page
    assert 'fetch("/api/scenario-state"' in page
    assert "loadRuntimeData" in page
    assert "Promise.all([loadDashboardData(), loadBackendHealth(), loadBackendSchema(), loadOpenDesignSpec()])" in page
    assert "await loadScenarioState()" in page
    assert "backendHealth.counts.paretoFront" in page
    assert "backendHealth.counts.cycleRows" in page
    assert "backendHealth.counts.ironLossRows" in page
    assert "validateHealthSchema" in page
    assert 'validateHealthSchema(endpoints.find(endpoint => endpoint.path === "/api/health"))' in page
    assert 'includesAll(endpoint.responseObjectKeys?.counts, ["paretoFront", "cycleRows", "ironLossRows", "algorithmRows", "deliveryItems"])' in page


def test_dashboard_surfaces_per_endpoint_api_sync_diagnostics():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="api-sync-log"' in page
    assert "let apiSyncLog =" in page
    assert "recordApiSync" in page
    assert "renderApiSyncLog" in page
    assert "api-sync-item" in page
    assert 'recordApiSync("/api/dashboard", true' in page
    assert 'recordApiSync("/api/health", true' in page
    assert 'recordApiSync("/api/schema", true' in page
    assert 'recordApiSync("/api/scenario-state", true' in page
    assert 'recordApiSync("/api/decision-pack", true' in page
    assert 'recordApiSync("/api/decision-pack", false' in page
    assert 'recordApiSync("/api/session-snapshot", true' in page
    assert 'recordApiSync("/api/customer-brief", true' in page
    assert 'recordApiSync("/api/customer-brief", false' in page
    assert 'recordApiSync("/api/design-spec", true' in page
    assert 'recordApiSync("/api/design-spec", false' in page
    assert 'const paths = ["/api/dashboard", "/api/health", "/api/schema", "/api/scenario-state", "/api/decision-pack", "/api/session-snapshot", "/api/customer-brief", "/api/design-spec"]' in page


def test_dashboard_validates_customer_brief_schema_contract():
    page = HTML.read_text(encoding="utf-8")

    assert "validateCustomerBriefSchema" in page
    assert "API customer-brief schema contract incomplete" in page
    assert 'validateCustomerBriefSchema(endpoints.find(endpoint => endpoint.path === "/api/customer-brief"))' in page
    assert 'const required = ["/api/dashboard", "/api/health", "/api/schema", "/api/scenario-state", "/api/decision-pack", "/api/session-snapshot", "/api/customer-brief", "/api/design-spec"]' in page
    assert 'includesAll(endpoint.methods, ["GET", "POST"])' in page
    assert 'includesAll(endpoint.requestStateKeys, ["candidate", "businessAssumptions", "weights"])' in page
    assert 'includesAll(endpoint.responseKeys, ["source", "schemaVersion", "candidate", "brief", "decisionPack"])' in page
    assert 'includesAll(endpoint.responseObjectKeys?.decisionPack, ["source", "schemaVersion", "selected", "gains", "businessCase", "weights", "ranking"])' in page


def test_dashboard_loads_design_spec_during_runtime_contract_check():
    page = HTML.read_text(encoding="utf-8")

    assert "validateDesignSpecSchema" in page
    assert "API design-spec schema contract incomplete" in page
    assert 'validateDesignSpecSchema(endpoints.find(endpoint => endpoint.path === "/api/design-spec"))' in page
    assert 'includesAll(endpoint.methods, ["GET"])' in page
    assert 'includesAll(endpoint.responseKeys, ["source", "schemaVersion", "file", "spec"])' in page
    assert 'includesAll(endpoint.responseObjectKeys?.spec, ["name", "product", "page", "design_system", "audience", "tokens", "components"])' in page
    assert "Promise.all([loadDashboardData(), loadBackendHealth(), loadBackendSchema(), loadOpenDesignSpec()])" in page


def test_dashboard_surfaces_backend_scenario_state_restore_status():
    page = HTML.read_text(encoding="utf-8")

    assert 'id="scenario-state-status"' in page
    assert 'id="clear-scenario-state"' in page
    assert "let backendScenarioState = null" in page
    assert "applyScenarioStatePayload" in page
    assert "clearScenarioState" in page
    assert "renderScenarioStateStatus" in page
    assert "BUSINESS_ASSUMPTION_BOUNDS" in page
    assert "WEIGHT_BOUNDS" in page
    assert "clampInputValue" in page
    assert "businessAssumptions[key] = clampInputValue(key, value, BUSINESS_ASSUMPTION_BOUNDS)" in page
    assert "input.value = String(businessAssumptions[key])" in page
    assert "payload.stateAvailable" in page
    assert "payload.stateSource" in page
    assert "backendScenarioState.stateSource" in page
    assert "validateScenarioStateSchema" in page
    assert 'validateScenarioStateSchema(endpoints.find(endpoint => endpoint.path === "/api/scenario-state"))' in page
    assert 'includesAll(endpoint.responseObjectKeys?.state, ["candidate", "businessAssumptions", "weights"])' in page
    assert 'fetch("/api/scenario-state", { method: "DELETE"' in page
    assert "scenario-state-status" in page


def test_dashboard_fetches_backend_health_for_delivery_panel():
    page = HTML.read_text(encoding="utf-8")

    assert "let backendHealth =" in page
    assert "loadBackendHealth" in page
    assert 'fetch("/api/health"' in page
    assert "applyBackendHealth" in page


def test_dashboard_marks_iron_loss_frequency_out_of_range_points():
    page = HTML.read_text(encoding="utf-8")

    assert "FALLBACK_DATA_PROVENANCE" in page
    assert "generatedFrom" in page
    assert "sourceHash" in page
    assert "freqOutOfRange" in page
    assert "d.freqOutOfRange" in page
    assert "stroke-dasharray" in page
    assert 'includesAll(endpoint.responseObjectKeys?.ironLossRows, ["speed", "targetFeasible", "ironLoss", "efficiency", "freqOutOfRange"])' in page
    assert "backendHealth.counts.paretoFront" in page
    assert "backendHealth.pageAvailable" in page
