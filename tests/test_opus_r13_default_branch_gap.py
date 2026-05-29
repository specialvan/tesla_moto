from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OPUS_REVIEW_DIR = REPO_ROOT / 'opus-review' / 'docs' / '2026-05-25'


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def test_r13_register_tracks_default_branch_staleness_gap() -> None:
    register = json.loads(
        (OPUS_REVIEW_DIR / 'codex_progress_action_register_r13_followup.json').read_text(
            encoding='utf-8'
        )
    )
    item = register['items'][0]

    assert item['id'] == 'OPUS-2026-05-29-R13-DEFAULT-BRANCH-STALE'
    assert item['status'] == 'open'
    assert item['severity'] == 'P1'
    assert 'origin/HEAD resolves to origin/codex-review-line' in item['finding']
    assert 'git symbolic-ref refs/remotes/origin/HEAD' in item['evidence']


def test_default_branch_gap_is_reproducible_from_git_state() -> None:
    assert _git('symbolic-ref', 'refs/remotes/origin/HEAD').stdout.strip() == (
        'refs/remotes/origin/codex-review-line'
    )
    assert _git('rev-list', '--left-right', '--count', 'origin/codex-review-line...codex-review-line').stdout.strip() == '0\t4'
    assert _git('cat-file', '-e', 'origin/codex-review-line:sim/pyfluent_workflow.py', check=False).returncode != 0
    assert _git(
        'cat-file',
        '-e',
        'origin/codex-review-line:codex-review/docs/claude_development_review_2026-05-15.md',
        check=False,
    ).returncode != 0


def test_current_handoff_scopes_zero_open_to_claude_mainline_and_mentions_r13() -> None:
    handoff = (OPUS_REVIEW_DIR / 'opus_handoff_for_review_current_2026-05-29.md').read_text(
        encoding='utf-8'
    )

    assert '该对齐结论只覆盖 `claude-mainline`' in handoff
    assert 'OPUS-2026-05-29-R13-DEFAULT-BRANCH-STALE' in handoff
    assert 'origin/HEAD = origin/codex-review-line' in handoff


def test_r13_open_item_is_not_hidden_by_previous_supersedes() -> None:
    registers = sorted(OPUS_REVIEW_DIR.glob('codex_progress_action_register*.json'))
    superseded = set()
    items: list[dict[str, str]] = []
    for path in registers:
        register = json.loads(path.read_text(encoding='utf-8'))
        superseded.update(register.get('supersedes', []))
        items.extend(register.get('items', []))

    effective_open_ids = {
        item['id']
        for item in items
        if item.get('status') == 'open' and item.get('id') not in superseded
    }

    assert effective_open_ids == {'OPUS-2026-05-29-R13-DEFAULT-BRANCH-STALE'}
