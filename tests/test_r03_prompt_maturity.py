from pathlib import Path

R03_PROMPT_GLOB = "engineering/v2/scheme-*/prompts/*r03-production_drawing_pack.md"


def test_r03_prompt_packs_preserve_maturity_boundaries() -> None:
    paths = sorted(Path(".").glob(R03_PROMPT_GLOB))

    assert len(paths) == 12
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        assert "engineering_validated = false" in text, path
        assert "evidence_gap" in text or "evidence gap" in text or "fea gap" in text, path
        assert "proxy" in text or "synthetic fixture" in text or "sample-only" in text, path


def test_r03_prompt_packs_do_not_overstate_validation() -> None:
    forbidden_phrases = {
        "fea-backed validation",
        "green engineering candidate gate",
        "engineering recommendation",
    }
    paths = sorted(Path(".").glob(R03_PROMPT_GLOB))

    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden_phrases:
            assert phrase not in text, f"{path}: {phrase}"
