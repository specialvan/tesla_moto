import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
R03_PROMPT_GLOB = "engineering/v2/scheme-*/prompts/*r03-production_drawing_pack.md"
EXPECTED_SCHEMES = {f"S{scheme_id:02d}" for scheme_id in range(1, 13)}
MATURITY_MARKERS = (
    "engineering_validated = false",
    "evidence_gap",
)
PROXY_MARKERS = (
    "proxy",
    "synthetic fixture",
    "sample-only",
)
FORBIDDEN_PHRASES = {
    "fea-backed validation",
    "green engineering candidate gate",
    "engineering recommendation",
    "engineering_validated = true",
    "validated = true",
    "production release approved",
    "manufacturing release approved",
    "released in green",
    "engineering gate decision",
}
PROMPT_SECTION_RE = re.compile(
    r"^Prompt:\s*(.*?)(?=\n## 图|\nPrompt:|\Z)",
    re.MULTILINE | re.DOTALL,
)
FIGURE_HEADING_RE = re.compile(r"^## 图 (\d)：", re.MULTILINE)
SCHEME_RE = re.compile(r"scheme-(\d{2})")


def _r03_prompt_paths() -> list[Path]:
    paths = sorted(REPO_ROOT.glob(R03_PROMPT_GLOB))
    discovered_schemes = {
        f"S{match.group(1)}"
        for path in paths
        if (match := SCHEME_RE.search(path.as_posix()))
    }

    assert discovered_schemes == EXPECTED_SCHEMES
    assert len(paths) == len(EXPECTED_SCHEMES)
    return paths


def test_r03_prompt_packs_preserve_maturity_boundaries() -> None:
    for path in _r03_prompt_paths():
        text = path.read_text(encoding="utf-8").lower()
        for marker in MATURITY_MARKERS:
            assert marker in text, path
        assert any(marker in text for marker in PROXY_MARKERS), path


def test_r03_prompt_packs_do_not_overstate_validation() -> None:
    for path in _r03_prompt_paths():
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, f"{path}: {phrase}"


def test_r03_standalone_prompts_keep_visible_maturity_callouts() -> None:
    for path in _r03_prompt_paths():
        text = path.read_text(encoding="utf-8")
        prompts = PROMPT_SECTION_RE.findall(text)

        assert len(prompts) == 4, path
        for prompt in prompts:
            lowered = prompt.lower()
            assert "engineering_validated = false" in lowered, f"{path}: {prompt}"
            assert "evidence_gap" in lowered, f"{path}: {prompt}"
            assert any(
                marker in lowered for marker in PROXY_MARKERS
            ), f"{path}: {prompt}"


def test_r03_prompt_pack_figure_ids_are_sequential() -> None:
    for path in _r03_prompt_paths():
        text = path.read_text(encoding="utf-8")
        figure_ids = [int(match.group(1)) for match in FIGURE_HEADING_RE.finditer(text)]
        assert figure_ids == [1, 2, 3, 4], path
