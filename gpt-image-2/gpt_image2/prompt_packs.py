"""解析 r03 production drawing prompt pack。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PACK_PATTERN = re.compile(
    r"^## 图\s*(?P<number>\d+)：(?P<title>.+?)\s*$\n(?P<body>.*?)(?=^## 图\s*\d+：|\Z)",
    re.MULTILINE | re.DOTALL,
)
PROMPT_LINE_PATTERN = re.compile(r"Prompt:\s*(?P<prompt>.*)", re.DOTALL)
SCHEME_PATTERN = re.compile(r"V2-(S\d{2})-PROMPT-r(?P<revision>\d+)-")
GLOBAL_CONSTRAINT_PATTERN = re.compile(
    r"## 通用负面约束\s*\n(?P<body>.*?)(?=^## 图\s*\d+：)",
    re.MULTILINE | re.DOTALL,
)


def _slugify(value: str, fallback: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return normalized or fallback


def _extract_scheme(path: Path) -> tuple[str, str]:
    match = SCHEME_PATTERN.search(path.name)
    if not match:
        raise ValueError(f"cannot infer scheme/revision from prompt pack name: {path}")
    return match.group(1), f"r{match.group('revision')}"


def _extract_prompt(body: str) -> str:
    match = PROMPT_LINE_PATTERN.search(body.strip())
    if not match:
        raise ValueError("prompt pack section has no Prompt: line")
    return " ".join(match.group("prompt").strip().split())


def _extract_global_constraints(text: str) -> str:
    match = GLOBAL_CONSTRAINT_PATTERN.search(text)
    if not match:
        return ""
    body = re.sub(r"^\s*-\s*", "", match.group("body"), flags=re.MULTILINE)
    return " ".join(body.strip().split())


def _merge_constraints(prompt: str, constraints: str) -> str:
    if not constraints:
        return prompt
    return f"{prompt} Global constraints: {constraints}"


def load_prompt_pack(path: Path) -> list[tuple[str, dict[str, Any]]]:
    """读取单个 r03 prompt pack，返回 generate.py 可消费的 selections。"""
    scheme_key, revision = _extract_scheme(path)
    text = path.read_text(encoding="utf-8")
    global_constraints = _extract_global_constraints(text)
    entries: list[tuple[str, dict[str, Any]]] = []

    for match in PROMPT_PACK_PATTERN.finditer(text):
        number = int(match.group("number"))
        title = match.group("title").strip()
        prompt = _merge_constraints(
            _extract_prompt(match.group("body")), global_constraints
        )
        slug = _slugify(title, f"figure_{number:02d}")
        image_id = f"PACK-{scheme_key}-{revision.upper()}-T{number:02d}"
        entry = {
            "image_id": image_id,
            "template": "PROMPT_PACK",
            "title": title,
            "prompt": prompt,
            "priority": "P0",
            "revision": revision,
            "output_name": f"V2-{scheme_key}-{revision.upper()}-T{number:02d}-{slug}.png",
            "source_pack": str(path),
        }
        entries.append((scheme_key, entry))

    if not entries:
        raise ValueError(f"prompt pack has no drawable Prompt sections: {path}")
    return entries


def discover_r03_prompt_packs(root: Path | None = None) -> list[Path]:
    """发现仓库内全部 r03 production drawing prompt pack。"""
    base = root or REPO_ROOT
    return sorted(
        base.glob("engineering/v2/scheme-*/prompts/*r03-production_drawing_pack.md")
    )
