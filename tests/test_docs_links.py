from __future__ import annotations

from pathlib import Path

from scripts.docs_link_check import find_broken_markdown_links


DOC_ROOTS = [
    Path("claude-review"),
    Path("codex-review/docs"),
    Path("opus-review"),
    Path("claude-docs"),
    Path("codex-docs"),
]


def test_review_markdown_relative_links_resolve() -> None:
    broken_links = find_broken_markdown_links(DOC_ROOTS)

    assert broken_links == []
