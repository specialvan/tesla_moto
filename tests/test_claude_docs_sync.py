from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding='utf-8')


def _assert_contains_all(text: str, markers: list[str]) -> None:
    for marker in markers:
        assert marker in text


def test_claude_evidence_manifest_tracks_exp_011_and_prompt_maturity() -> None:
    text = _read('claude-docs/evidence_manifest.md')
    _assert_contains_all(
        text,
        [
            'EXP-011',
            'experiments/exp_011_iron_loss/summary.json',
            'experiments/exp_011_iron_loss/iron_loss_sweep_results.csv',
            'freq_out_of_range_points',
            'Bertotti',
            'proxy',
            'codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/README.md',
            'engineering/v2/scheme-*/prompts/*r03-production_drawing_pack.md',
            'tests/test_r02_sim_batch_archival.py',
            'tests/test_r03_prompt_simulation_anchor.py',
            'tests/test_r03_prompt_maturity.py',
            'engineering_validated=false',
        ],
    )


def test_wiki_html_evidence_tracks_current_experiment_and_maturity_scope() -> None:
    text = _read('claude-docs/wiki_html_evidence.md')
    _assert_contains_all(
        text,
        [
            'EXP-001 \u5230 EXP-011',
            'EXP-010',
            'EXP-011',
            'Bertotti',
            'freq_out_of_range_points',
            'r02 sim_binding',
            'r03 production drawing pack',
            'engineering_validated=false',
        ],
    )


def test_research_wiki_exposes_exp_011_without_validation_overclaim() -> None:
    text = _read('wiki/controllable_flux_motor_research_plan.md')
    _assert_contains_all(
        text,
        [
            'EXP-010',
            'EXP-011',
            'Bertotti',
            'freq_out_of_range_points',
            'r02 sim_binding',
            'r03 production drawing pack',
            'engineering_validated=false',
            '\u4e0d\u4ee3\u8868 FEA\u3001HIL\u3001\u53f0\u67b6\u6216\u91cf\u4ea7\u91ca\u653e\u7ed3\u8bba',
        ],
    )

    for marker in [
        'engineering_validated=true',
        'engineering_validated = true',
        'production_release_allowed=true',
        '\u5df2\u5b8c\u6210 FEA \u9a8c\u8bc1',
        '\u5df2\u5b8c\u6210 HIL',
        '\u5df2\u5b8c\u6210\u53f0\u67b6',
        '\u91cf\u4ea7\u91ca\u653e\u7ed3\u8bba\u5df2\u901a\u8fc7',
    ]:
        assert marker not in text


def test_html_kb_exposes_prompt_maturity_contract() -> None:
    text = _read('controllable_flux_motor_kb.html')
    _assert_contains_all(
        text,
        [
            'EXP-011',
            'Bertotti',
            'freqOutOfRange',
            'engineering_validated: false',
            'r02 sim_binding',
            'r03 production drawing pack',
        ],
    )


def test_claude_snapshots_match_active_wiki_and_html_sources() -> None:
    assert _read('claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md') == _read(
        'wiki/controllable_flux_motor_research_plan.md'
    )
    assert _read('claude-docs/snapshots/html/controllable_flux_motor_kb.html') == _read(
        'controllable_flux_motor_kb.html'
    )
