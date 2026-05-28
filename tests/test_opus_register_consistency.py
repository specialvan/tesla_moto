from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OPUS_REVIEW_DIR = REPO_ROOT / 'opus-review' / 'docs' / '2026-05-25'


def _git(*args: str) -> str:
    return subprocess.check_output(['git', *args], cwd=REPO_ROOT, text=True).strip()


def test_latest_opus_followup_register_tracks_published_integration_anchor() -> None:
    latest_register = OPUS_REVIEW_DIR / 'codex_progress_action_register_r12_followup.json'
    register = json.loads(latest_register.read_text(encoding='utf-8'))
    published_anchor = register['review_head']['claude-mainline']

    assert published_anchor == '1ddf7da'
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', published_anchor, 'HEAD'], cwd=REPO_ROOT)


def test_branch_integration_result_records_final_publish_commit() -> None:
    result_text = (OPUS_REVIEW_DIR / 'branch_integration_result_2026-05-29.md').read_text(
        encoding='utf-8'
    )

    assert '1ddf7da' in result_text
    assert '6eaee5b..1ddf7da' in result_text
    assert '1ddf7da1a24a1fda0797a8610c5dc633384fe90e refs/heads/claude-mainline' in result_text
