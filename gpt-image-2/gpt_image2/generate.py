"""CLI：单张 / 按方案串行 / 全方案优先级筛选 / 烟囱测试 / 干跑。"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

from .client import GenerationError, GenerationResult, edit_image, generate_image
from .config import (
    OUTPUTS_DIR,
    ModelConfig,
    StyleConfig,
    find_image_entry,
    load_model_config,
    load_schemes,
    load_style_config,
    load_templates,
)
from .prompt_packs import discover_r03_prompt_packs, load_prompt_pack
from .render import render_prompt, resolve_size


SMOKE_PROMPT = (
    "Flat technical infographic showing the words 'gpt-image-2 smoke test 2026-05-18' "
    "in clean sans-serif typography on a dark navy background with gold accents. "
    "Single image, no people, no marketing copy."
)


def _now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _write_prompt_sidecar(
    *,
    output_path: Path,
    image_id: str,
    model: str,
    size: str,
    mode: str,
    positive_prompt: str,
    negative_prompt: str | None,
    result: GenerationResult | None,
    reference_image: Path | None = None,
    notes: str = "",
) -> None:
    sidecar = output_path.with_name(output_path.stem + "-prompt.txt")
    lines: list[str] = []
    lines.append(f"[date]    {_now_iso()}")
    lines.append(f"[image_id] {image_id}")
    lines.append(f"[model]    {model}")
    lines.append(f"[size]     {size}")
    lines.append(f"[mode]     {mode}")
    lines.append(f"[reference image] {reference_image if reference_image else 'none'}")
    lines.append("[positive prompt]")
    lines.append(positive_prompt)
    lines.append("[negative prompt]")
    lines.append(negative_prompt or "not supported by endpoint")
    if result is not None:
        lines.append(f"[api_status] {result.status_code}")
        lines.append(f"[duration_ms] {result.duration_ms}")
        raw_keys = list(result.raw_response.keys())
        lines.append(f"[response keys] {raw_keys}")
    if notes:
        lines.append("[notes]")
        lines.append(notes)
    sidecar.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _select_images_for_scheme(
    scheme_key: str,
    schemes: dict[str, Any],
    *,
    priorities: set[str] | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    if scheme_key not in schemes:
        raise KeyError(f"scheme not found: {scheme_key}")
    result: list[tuple[str, dict[str, Any]]] = []
    for entry in schemes[scheme_key]["images"]:
        if priorities is not None and entry.get("priority") not in priorities:
            continue
        result.append((scheme_key, entry))
    return result


def _select_images_for_all(
    schemes: dict[str, Any],
    *,
    priorities: set[str] | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    for scheme_key in sorted(schemes.keys()):
        result.extend(
            _select_images_for_scheme(scheme_key, schemes, priorities=priorities)
        )
    return result


def _resolve_output_path(
    scheme_key: str,
    image_entry: dict[str, Any],
    *,
    output_dir: Path | None,
) -> Path:
    revision = image_entry.get("revision")
    if output_dir is not None:
        base = output_dir
    elif revision:
        base = OUTPUTS_DIR / scheme_key / revision
    else:
        base = OUTPUTS_DIR / scheme_key
    base.mkdir(parents=True, exist_ok=True)
    return base / image_entry["output_name"]


def _render_entry_prompt(
    image_entry: dict[str, Any],
    *,
    templates: dict[str, Any],
    style_config: StyleConfig,
) -> str:
    if image_entry.get("template") == "PROMPT_PACK":
        return f"{image_entry['prompt'].strip()} {style_config.positive_style_suffix.strip()}".strip()
    return render_prompt(image_entry, templates=templates, style=style_config)


def _validate_reference_image(path: Path) -> Path:
    if path.is_symlink():
        raise ValueError(f"reference image must not be a symlink: {path}")
    resolved = path.resolve()
    if not resolved.exists() or not resolved.is_file():
        raise ValueError(f"reference image is not a file: {path}")
    if resolved.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError(f"reference image must be png/jpg/webp: {path}")
    if resolved.stat().st_size > 25 * 1024 * 1024:
        raise ValueError(f"reference image is larger than 25 MB: {path}")
    return resolved


def _resolve_reference_image(
    scheme_key: str,
    image_entry: dict[str, Any],
    *,
    reference_image: Path | None,
    reference_dir: Path | None,
) -> Path | None:
    if reference_image is not None:
        return _validate_reference_image(reference_image)
    if reference_dir is None:
        return None
    output_name = Path(image_entry["output_name"])
    image_id = image_entry["image_id"]
    t_match = next((part for part in image_id.split("-") if part.startswith("T")), "")
    search_roots = [reference_dir, reference_dir / scheme_key]
    candidates = [root / output_name.name for root in search_roots]
    if t_match:
        candidates.extend(
            candidate
            for root in search_roots
            for pattern in (
                f"V2-{scheme_key}-ILL-{t_match}-*.png",
                f"*{scheme_key}*{t_match}*.png",
            )
            for candidate in root.glob(pattern)
        )
    for candidate in candidates:
        if candidate.exists():
            return _validate_reference_image(candidate)
    return None


def _generate_one(
    *,
    scheme_key: str,
    image_entry: dict[str, Any],
    model_config: ModelConfig,
    style_config: StyleConfig,
    templates: dict[str, Any],
    output_dir: Path | None,
    dry_run: bool,
    force: bool,
    reference_image: Path | None,
    reference_dir: Path | None,
) -> dict[str, Any]:
    image_id = image_entry["image_id"]
    output_path = _resolve_output_path(scheme_key, image_entry, output_dir=output_dir)

    if output_path.exists() and not force and not dry_run:
        return {
            "image_id": image_id,
            "status": "skipped_existing",
            "output_path": str(output_path),
        }

    final_prompt = _render_entry_prompt(
        image_entry, templates=templates, style_config=style_config
    )
    size = resolve_size(image_entry, style=style_config)
    try:
        resolved_reference = _resolve_reference_image(
            scheme_key,
            image_entry,
            reference_image=reference_image,
            reference_dir=reference_dir,
        )
    except ValueError as exc:
        return {
            "image_id": image_id,
            "status": "error",
            "error": str(exc),
            "output_path": str(output_path),
        }

    if reference_dir is not None and resolved_reference is None:
        return {
            "image_id": image_id,
            "status": "error",
            "error": f"reference image not found in {reference_dir}",
            "output_path": str(output_path),
        }

    if dry_run:
        dry_dir = output_dir or (OUTPUTS_DIR / "_dry_run")
        dry_dir.mkdir(parents=True, exist_ok=True)
        target = dry_dir / f"{image_id}.prompt.txt"
        target.write_text(final_prompt + "\n", encoding="utf-8")
        return {
            "image_id": image_id,
            "status": "dry_run",
            "prompt_path": str(target),
            "prompt_length": len(final_prompt),
        }

    try:
        if resolved_reference is not None:
            result = edit_image(
                config=model_config,
                prompt=final_prompt,
                reference_image_path=resolved_reference,
                size=size,
            )
            mode = "改图"
        else:
            result = generate_image(
                config=model_config,
                prompt=final_prompt,
                size=size,
            )
            mode = "生图"
    except GenerationError as exc:
        _write_prompt_sidecar(
            output_path=output_path,
            image_id=image_id,
            model=model_config.model,
            size=size,
            mode="改图 (failed)" if resolved_reference else "生图 (failed)",
            positive_prompt=final_prompt,
            negative_prompt=style_config.negative_prompt,
            result=None,
            reference_image=resolved_reference,
            notes=f"FAILED: {exc}",
        )
        return {
            "image_id": image_id,
            "status": "error",
            "error": str(exc),
            "output_path": str(output_path),
        }

    output_path.write_bytes(result.image_bytes)
    _write_prompt_sidecar(
        output_path=output_path,
        image_id=image_id,
        model=model_config.model,
        size=size,
        mode=mode,
        positive_prompt=final_prompt,
        negative_prompt=style_config.negative_prompt,
        result=result,
        reference_image=resolved_reference,
    )
    return {
        "image_id": image_id,
        "status": "ok",
        "duration_ms": result.duration_ms,
        "bytes": len(result.image_bytes),
        "output_path": str(output_path),
    }


def _generate_many(
    selections: Iterable[tuple[str, dict[str, Any]]],
    *,
    model_config: ModelConfig,
    style_config: StyleConfig,
    templates: dict[str, Any],
    output_dir: Path | None,
    dry_run: bool,
    force: bool,
    reference_image: Path | None,
    reference_dir: Path | None,
    concurrency: int = 1,
) -> list[dict[str, Any]]:
    selections = list(selections)
    total = len(selections)
    sleep_seconds = model_config.sleep_between_calls_seconds if not dry_run else 0.0

    if concurrency <= 1:
        reports: list[dict[str, Any]] = []
        for idx, (scheme_key, entry) in enumerate(selections, 1):
            print(
                f"[{idx}/{total}] {entry['image_id']} priority={entry.get('priority', '?')}",
                flush=True,
            )
            report = _generate_one(
                scheme_key=scheme_key,
                image_entry=entry,
                model_config=model_config,
                style_config=style_config,
                templates=templates,
                output_dir=output_dir,
                dry_run=dry_run,
                force=force,
                reference_image=reference_image,
                reference_dir=reference_dir,
            )
            reports.append(report)
            print(f"    -> {report['status']}", flush=True)
            if idx < total and sleep_seconds > 0:
                time.sleep(sleep_seconds)
        return reports

    # 并发路径：N 个 worker 同时跑，进度打印加锁防止交错。
    print_lock = threading.Lock()
    indexed = list(enumerate(selections, 1))

    def _run_indexed(item: tuple[int, tuple[str, dict[str, Any]]]) -> dict[str, Any]:
        idx, (scheme_key, entry) = item
        with print_lock:
            print(
                f"[{idx}/{total}] {entry['image_id']} priority={entry.get('priority', '?')} start",
                flush=True,
            )
        report = _generate_one(
            scheme_key=scheme_key,
            image_entry=entry,
            model_config=model_config,
            style_config=style_config,
            templates=templates,
            output_dir=output_dir,
            dry_run=dry_run,
            force=force,
            reference_image=reference_image,
            reference_dir=reference_dir,
        )
        with print_lock:
            print(
                f"[{idx}/{total}] {entry['image_id']} -> {report['status']}", flush=True
            )
        return report

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_item = {executor.submit(_run_indexed, item): item for item in indexed}
        for future in as_completed(future_to_item):
            results.append(future.result())
    # 按 idx 排序返回，便于和串行模式输出格式一致
    results.sort(key=lambda r: r.get("image_id", ""))
    return results


def _do_smoke(model_config: ModelConfig, output_dir: Path | None) -> int:
    print(f"smoke test endpoint = {model_config.full_url}")
    print(f"smoke test model    = {model_config.model}")
    base = output_dir or (OUTPUTS_DIR / "_smoke")
    base.mkdir(parents=True, exist_ok=True)
    output_path = base / "smoke-r00.png"
    try:
        result = generate_image(
            config=model_config, prompt=SMOKE_PROMPT, size="1024x1024"
        )
    except GenerationError as exc:
        print(f"smoke FAILED: {exc}", file=sys.stderr)
        return 2
    output_path.write_bytes(result.image_bytes)
    _write_prompt_sidecar(
        output_path=output_path,
        image_id="smoke",
        model=model_config.model,
        size="1024x1024",
        mode="生图 (smoke)",
        positive_prompt=SMOKE_PROMPT,
        negative_prompt=None,
        result=result,
        notes="endpoint reachability check",
    )
    print(
        f"smoke OK  duration_ms={result.duration_ms}  bytes={len(result.image_bytes)}",
        flush=True,
    )
    print(f"saved     {output_path}", flush=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gpt_image2.generate",
        description="串行调用 gpt-image-2 端点为 12 个方案生图。",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--image-id", help="单张图 ID，如 IMG-S01-T03")
    group.add_argument("--scheme", help="按方案串行，如 S01")
    group.add_argument("--all", action="store_true", help="按全部 12 方案串行")
    group.add_argument("--smoke", action="store_true", help="端点烟囱测试，仅 1 张图")
    group.add_argument("--prompt-pack", type=Path, help="按单个 r03 prompt pack 串行")
    group.add_argument(
        "--prompt-pack-all", action="store_true", help="按全部 r03 prompt pack 串行"
    )
    parser.add_argument(
        "--priority",
        action="append",
        choices=["P0", "P1", "P2"],
        help="筛选优先级，可重复（如 --priority P0 --priority P1）",
    )
    parser.add_argument("--output-dir", type=Path, help="覆盖默认输出目录")
    parser.add_argument(
        "--edit-reference", type=Path, help="使用单张参考图走 images/edits 改图"
    )
    parser.add_argument(
        "--edit-reference-dir", type=Path, help="批量改图时从目录查找参考图"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只渲染 prompt，不调用 API"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="即使 PNG 已存在也重生（默认跳过）",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="把每张图的执行结果汇总写入 json 报告",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="保留兼容参数；外部生图强制严格串行，值必须为 1。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.concurrency != 1:
        parser.error(
            "external image generation is approval-gated and must run with --concurrency 1"
        )
    if args.smoke and args.dry_run:
        parser.error("--smoke cannot be combined with --dry-run")

    model_config = load_model_config(require_credentials=not args.dry_run)
    style_config = load_style_config()
    templates = load_templates()
    schemes = load_schemes()

    if args.smoke:
        return _do_smoke(model_config, args.output_dir)

    priorities: set[str] | None = set(args.priority) if args.priority else None

    if args.image_id:
        scheme_key, entry = find_image_entry(args.image_id)
        selections = [(scheme_key, entry)]
    elif args.scheme:
        selections = _select_images_for_scheme(
            args.scheme, schemes, priorities=priorities
        )
    elif args.all:
        selections = _select_images_for_all(schemes, priorities=priorities)
    elif args.prompt_pack:
        selections = load_prompt_pack(args.prompt_pack)
    elif args.prompt_pack_all:
        selections = []
        for pack_path in discover_r03_prompt_packs():
            selections.extend(load_prompt_pack(pack_path))
    else:
        parser.print_help()
        return 1

    reports = _generate_many(
        selections,
        model_config=model_config,
        style_config=style_config,
        templates=templates,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        force=args.force,
        reference_image=args.edit_reference,
        reference_dir=args.edit_reference_dir,
        concurrency=max(1, args.concurrency),
    )

    ok = sum(1 for r in reports if r["status"] == "ok")
    skipped = sum(1 for r in reports if r["status"] == "skipped_existing")
    errored = sum(1 for r in reports if r["status"] == "error")
    dry = sum(1 for r in reports if r["status"] == "dry_run")
    print(
        f"\nsummary  total={len(reports)} ok={ok} skipped={skipped} error={errored} dry={dry}",
        flush=True,
    )

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"report saved to {args.report_json}", flush=True)

    return 0 if errored == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
