"""HTTP 客户端：调用 OpenAI 兼容 /v1/images/generations。"""

from __future__ import annotations

import base64
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from .config import ModelConfig


class GenerationError(RuntimeError):
    """生图失败的统一错误。"""


@dataclass
class GenerationResult:
    image_bytes: bytes
    raw_response: dict[str, Any]
    duration_ms: int
    status_code: int
    request_payload: dict[str, Any]


def _sanitize_error_text(value: str, *, limit: int = 240) -> str:
    sanitized = re.sub(
        r"(?i)(authorization|api[_-]?key|token|secret|password)\s*[:=]\s*[^\s,'\"]+",
        r"\1=[REDACTED]",
        value,
    )
    return sanitized[:limit]


def _decode_first_image(payload: dict[str, Any]) -> bytes:
    """从响应里取第一张图片字节。优先 b64_json，回退 url。"""
    data = payload.get("data") or []
    if not data:
        raise GenerationError(f"response has no data field: {payload!r}")
    first = data[0]
    if isinstance(first, dict):
        if first.get("b64_json"):
            return base64.b64decode(first["b64_json"])
    raise GenerationError(
        f"response data item has no b64_json: {_sanitize_error_text(str(first))}"
    )


def _build_payload(
    *,
    model: str,
    prompt: str,
    size: str,
    n: int,
    response_format: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
    }
    if response_format:
        payload["response_format"] = response_format
    return payload


def _request_attempts(config: ModelConfig) -> int:
    return config.max_retries + 1


def _sleep_seconds(config: ModelConfig, attempt: int, default: int) -> int:
    backoff = config.backoff_seconds
    return backoff[min(attempt, len(backoff) - 1)] if backoff else default


def _raise_for_status_or_retry(
    *,
    status: int,
    body: str,
    payload: dict[str, Any],
    attempt: int,
    attempts: int,
    config: ModelConfig,
) -> dict[str, Any]:
    if status == 400 and "response_format" in payload:
        time.sleep(1)
        return {k: v for k, v in payload.items() if k != "response_format"}
    if status in (401, 403, 404):
        raise GenerationError(f"{status} non-retriable: {_sanitize_error_text(body)}")
    if status == 429 or 500 <= status < 600:
        if attempt < attempts - 1:
            time.sleep(_sleep_seconds(config, attempt, 10))
            return payload
        raise GenerationError(f"{status} retriable: {_sanitize_error_text(body)}")
    raise GenerationError(f"unexpected status {status}: {_sanitize_error_text(body)}")


def generate_image(
    *,
    config: ModelConfig,
    prompt: str,
    size: str | None = None,
    n: int | None = None,
    response_format: str | None = None,
    model_override: str | None = None,
) -> GenerationResult:
    """同步串行调用图像端点。失败按 backoff 重试，不并发。"""
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    model = model_override or config.model
    defaults = config.defaults
    final_size = size or defaults.get("size", "1024x1024")
    final_n = n or int(defaults.get("n", 1))
    final_response_format = response_format or defaults.get("response_format")

    payload = _build_payload(
        model=model,
        prompt=prompt,
        size=final_size,
        n=final_n,
        response_format=final_response_format,
    )

    attempts = _request_attempts(config)
    last_error: Exception | None = None

    for attempt in range(attempts):
        start = time.monotonic()
        try:
            response = requests.post(
                config.full_url,
                headers=headers,
                json=payload,
                timeout=config.timeout_seconds,
            )
        except requests.RequestException as exc:
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(_sleep_seconds(config, attempt, 5))
                continue
            raise GenerationError(
                f"network error after {attempts} attempts: {exc}"
            ) from exc

        duration_ms = int((time.monotonic() - start) * 1000)
        status = response.status_code

        if status == 200:
            try:
                payload_resp = response.json()
            except ValueError as exc:
                raise GenerationError(
                    f"response is not json: {_sanitize_error_text(response.text)}"
                ) from exc
            image_bytes = _decode_first_image(payload_resp)
            return GenerationResult(
                image_bytes=image_bytes,
                raw_response=payload_resp,
                duration_ms=duration_ms,
                status_code=status,
                request_payload=payload,
            )

        new_payload = _raise_for_status_or_retry(
            status=status,
            body=response.text,
            payload=payload,
            attempt=attempt,
            attempts=attempts,
            config=config,
        )
        if new_payload != payload or status == 429 or 500 <= status < 600:
            last_error = GenerationError(
                f"{status} retriable: {_sanitize_error_text(response.text)}"
            )
            payload = new_payload
            continue

    raise GenerationError(f"exhausted attempts ({attempts}), last error: {last_error}")


def edit_image(
    *,
    config: ModelConfig,
    prompt: str,
    reference_image_path: Path,
    size: str | None = None,
    n: int | None = None,
    response_format: str | None = None,
    model_override: str | None = None,
) -> GenerationResult:
    """同步串行调用图像编辑端点，使用单张参考图。"""
    headers = {"Authorization": f"Bearer {config.api_key}"}

    model = model_override or config.model
    defaults = config.defaults
    final_size = size or defaults.get("size", "1024x1024")
    final_n = n or int(defaults.get("n", 1))
    final_response_format = response_format or defaults.get("response_format")
    data = _build_payload(
        model=model,
        prompt=prompt,
        size=final_size,
        n=final_n,
        response_format=final_response_format,
    )

    attempts = _request_attempts(config)
    last_error: Exception | None = None

    for attempt in range(attempts):
        start = time.monotonic()
        try:
            with reference_image_path.open("rb") as image_file:
                files = {"image": (reference_image_path.name, image_file, "image/png")}
                response = requests.post(
                    config.full_edit_url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=config.timeout_seconds,
                )
        except requests.RequestException as exc:
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(_sleep_seconds(config, attempt, 5))
                continue
            raise GenerationError(
                f"network error after {attempts} attempts: {exc}"
            ) from exc

        duration_ms = int((time.monotonic() - start) * 1000)
        status = response.status_code

        if status == 200:
            try:
                payload_resp = response.json()
            except ValueError as exc:
                raise GenerationError(
                    f"response is not json: {_sanitize_error_text(response.text)}"
                ) from exc
            image_bytes = _decode_first_image(payload_resp)
            return GenerationResult(
                image_bytes=image_bytes,
                raw_response=payload_resp,
                duration_ms=duration_ms,
                status_code=status,
                request_payload=data,
            )

        new_data = _raise_for_status_or_retry(
            status=status,
            body=response.text,
            payload=data,
            attempt=attempt,
            attempts=attempts,
            config=config,
        )
        if new_data != data or status == 429 or 500 <= status < 600:
            last_error = GenerationError(
                f"{status} retriable: {_sanitize_error_text(response.text)}"
            )
            data = new_data
            continue

    raise GenerationError(f"exhausted attempts ({attempts}), last error: {last_error}")
