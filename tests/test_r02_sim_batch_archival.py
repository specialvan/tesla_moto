from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
R02_README = (
    REPO_ROOT
    / "codex-review"
    / "docs"
    / "scheme_drawing_prompts_r02_simulation_batch"
    / "README.md"
)
R03_PROMPT_TEMPLATE = (
    "engineering/v2/scheme-{scheme}/prompts/"
    "V2-S{scheme}-PROMPT-r03-production_drawing_pack.md"
)


def test_r02_sim_batch_declares_r03_supersession_archive() -> None:
    text = R02_README.read_text(encoding="utf-8")

    assert "archive_status = archived_by_r03" in text
    assert "superseded_by = engineering/v2/scheme-*/prompts/*r03-production_drawing_pack.md" in text
    assert "retained_scope = S02/S04 r02-sim historical prompt evidence only" in text
    assert "do_not_expand_r02_sim_batch = true" in text


def test_r02_sim_batch_points_to_all_r03_prompt_packs() -> None:
    text = R02_README.read_text(encoding="utf-8")

    for scheme_index in range(1, 13):
        scheme = f"{scheme_index:02d}"
        prompt_path = R03_PROMPT_TEMPLATE.format(scheme=scheme)
        assert (REPO_ROOT / prompt_path).exists(), prompt_path
        assert prompt_path in text
