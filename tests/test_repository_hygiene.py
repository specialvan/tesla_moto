from __future__ import annotations

from pathlib import Path


def test_gitignore_excludes_local_review_artifacts() -> None:
    ignored_patterns = {
        line.strip()
        for line in Path(".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert "review-pr/" in ignored_patterns
    assert ".claude/worktrees/" in ignored_patterns
    assert ".claude/cache/" in ignored_patterns
    assert ".claude/sessions/" in ignored_patterns
