from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "gpt-image-2"
import sys

sys.path.insert(0, str(PACKAGE_ROOT))

from gpt_image2.generate import _resolve_reference_image
from gpt_image2.prompt_packs import discover_r03_prompt_packs, load_prompt_pack


def test_load_s01_r03_prompt_pack_extracts_four_prompts() -> None:
    pack_path = (
        Path(__file__).resolve().parents[1]
        / "engineering/v2/scheme-01/prompts/V2-S01-PROMPT-r03-production_drawing_pack.md"
    )

    selections = load_prompt_pack(pack_path)

    assert len(selections) == 4
    scheme_key, first = selections[0]
    assert scheme_key == "S01"
    assert first["image_id"] == "PACK-S01-R03-T01"
    assert first["output_name"] == "V2-S01-R03-T01-fw_sensing_and_fault_pcb_page.png"
    assert first["template"] == "PROMPT_PACK"
    assert first["revision"] == "r03"
    assert first["prompt"].startswith(
        "Generate a white-background engineering schematic"
    )
    assert "engineering_validated = false" not in first["prompt"]


def test_discover_r03_prompt_packs_finds_all_schemes() -> None:
    packs = discover_r03_prompt_packs(Path(__file__).resolve().parents[1])

    assert len(packs) == 12
    assert all(path.name.endswith("r03-production_drawing_pack.md") for path in packs)


def test_load_prompt_pack_rejects_unknown_filename(tmp_path: Path) -> None:
    pack_path = tmp_path / "bad.md"
    pack_path.write_text(
        "## 图 1：Bad\n\nPrompt: Generate a test image.\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="cannot infer scheme"):
        load_prompt_pack(pack_path)


def test_reference_dir_matches_by_scheme_and_t_number(tmp_path: Path) -> None:
    reference_dir = tmp_path / "refs" / "S01"
    reference_dir.mkdir(parents=True)
    reference = reference_dir / "V2-S01-ILL-T01-driver_block-r00.png"
    reference.write_bytes(b"png")
    entry = {
        "image_id": "PACK-S01-R03-T01",
        "output_name": "V2-S01-R03-T01-fw_sensing_and_fault_pcb_page.png",
    }

    resolved = _resolve_reference_image(
        "S01", entry, reference_image=None, reference_dir=tmp_path / "refs"
    )

    assert resolved == reference.resolve()
