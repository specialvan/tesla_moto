from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import unquote, urlsplit


_INLINE_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
_FENCED_BLOCK_RE = re.compile(r"^```.*?$.*?^```\s*$", re.MULTILINE | re.DOTALL)


def find_broken_markdown_links(roots: Iterable[Path | str]) -> list[str]:
    broken: list[str] = []

    for root in roots:
        root_path = Path(root)
        if root_path.is_file():
            markdown_files = [root_path]
        else:
            markdown_files = sorted(root_path.rglob("*.md"))

        for markdown_file in markdown_files:
            text = markdown_file.read_text(encoding="utf-8")
            text_without_code = _FENCED_BLOCK_RE.sub("", text)
            for line_number, raw_destination in _iter_markdown_destinations(
                text_without_code
            ):
                destination = _normalise_destination(raw_destination)
                if destination is None:
                    continue
                path_part = destination.split("#", 1)[0]
                if not path_part:
                    continue
                target_path = (markdown_file.parent / unquote(path_part)).resolve()
                if not target_path.exists():
                    broken.append(
                        f"{markdown_file}:{line_number} -> {destination}"
                    )

    return broken


def _iter_markdown_destinations(text: str) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in _INLINE_LINK_RE.finditer(line):
            yield line_number, match.group(1)


def _normalise_destination(raw_destination: str) -> str | None:
    destination = raw_destination.strip()
    if not destination:
        return None

    if destination.startswith("<"):
        close_index = destination.find(">")
        if close_index == -1:
            destination = destination[1:]
        else:
            destination = destination[1:close_index]
    else:
        destination = _strip_optional_title(destination)

    if _is_external_or_absolute(destination):
        return None
    return destination


def _strip_optional_title(destination: str) -> str:
    parts = destination.split()
    if len(parts) > 1 and parts[1].startswith(('"', "'", "(")):
        return parts[0]
    return destination


def _is_external_or_absolute(destination: str) -> bool:
    if destination.startswith("#") or destination.startswith("//"):
        return True
    parsed = urlsplit(destination)
    return bool(parsed.scheme or parsed.netloc or Path(destination).is_absolute())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate local relative links in Markdown files."
    )
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args(argv)

    broken_links = find_broken_markdown_links(args.roots)
    for broken_link in broken_links:
        print(broken_link)
    return 1 if broken_links else 0


if __name__ == "__main__":
    sys.exit(main())
