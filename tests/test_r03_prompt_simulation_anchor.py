import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANCHOR_MATRIX = (
    REPO_ROOT
    / "codex-review"
    / "docs"
    / "scheme_drawing_prompts_r02_simulation_batch"
    / "simulation_anchor_matrix.json"
)
PROMPT_PATH = (
    "engineering/v2/scheme-{scheme}/prompts/"
    "V2-S{scheme}-PROMPT-r03-production_drawing_pack.md"
)
REQUIRED_ANCHOR_FIELDS = (
    "scheme_id",
    "simulation_status",
    "model_maturity",
    "sim_binding",
    "pytest_gate",
    "engineering_validated",
    "next_simulation_step",
)


def _anchor_rows() -> list[dict[str, str]]:
    matrix = json.loads(ANCHOR_MATRIX.read_text(encoding="utf-8"))
    rows = matrix["schemes"]
    assert len(rows) == 12
    return rows


def _prompt_path(row: dict[str, str]) -> Path:
    scheme = row["scheme_short"].removeprefix("S")
    return REPO_ROOT / PROMPT_PATH.format(scheme=scheme)


def test_r03_prompts_embed_machine_readable_sim_anchor() -> None:
    for row in _anchor_rows():
        path = _prompt_path(row)
        text = path.read_text(encoding="utf-8")

        assert "SIM ANCHOR" in text, path
        for field in REQUIRED_ANCHOR_FIELDS:
            assert re.search(rf"\b{field}\b", text), f"{path}: missing {field}"

        assert row["scheme_id"] in text, path
        assert row["simulation_status"] in text, path
        assert row["model_maturity"] in text, path
        assert row["sim_binding"] in text, path
        for gate in row["pytest_gate"].split(";"):
            assert gate.strip() in text, f"{path}: missing pytest gate {gate!r}"
        assert "engineering_validated=false" in text.replace(" ", ""), path


def test_r03_prompt_blocks_embed_compact_sim_anchor() -> None:
    prompt_re = re.compile(r"^Prompt:\s*(.*?)(?=^## |^Prompt:|\Z)", re.MULTILINE | re.DOTALL)
    for row in _anchor_rows():
        path = _prompt_path(row)
        text = path.read_text(encoding="utf-8")
        prompts = prompt_re.findall(text)
        assert prompts, path

        for index, prompt in enumerate(prompts, start=1):
            compact = prompt.replace(" ", "")
            assert "Anchor:" in prompt, f"{path}: Prompt {index} missing Anchor line"
            assert row["scheme_short"] in prompt, f"{path}: Prompt {index} missing scheme short"
            assert row["model_maturity"] in prompt, f"{path}: Prompt {index} missing model maturity"
            assert "engineering_validated=false" in compact, f"{path}: Prompt {index} missing false validation flag"
            assert "evidence_gap" in prompt, f"{path}: Prompt {index} missing evidence_gap"


def test_r03_prompts_do_not_use_ambiguous_numeric_simulation_status() -> None:
    for row in _anchor_rows():
        text = _prompt_path(row).read_text(encoding="utf-8")
        assert "passed_numeric_simulation" not in text
