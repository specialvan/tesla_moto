"""HTTP 客户端：调用 OpenAI 兼容 /v1/images/generations。"""

from __future__ import annotations

import base64
import time
from dataclasses import dataclass
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


def _decode_first_image(payload: dict[str, Any]) -> bytes:
    """从响应里取第一张图片字节。优先 b64_json，回退 url。"""
    data = payload.get("data") or []
    if not data:
        raise GenerationError(f"response has no data field: {payload!r}")
    first = data[0]
    if isinstance(first, dict):
        if first.get("b64_json"):
            return base64.b64decode(first["b64_json"])
        url = first.get("url")
        if url:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            return resp.content
    raise GenerationError(f"response data item has no b64_json or url: {first!r}")


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

    backoff = config.backoff_seconds
    attempts = config.max_retries + 1
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
            sleep_seconds = backoff[min(attempt, len(backoff) - 1)] if backoff else 5
            if attempt < attempts - 1:
                time.sleep(sleep_seconds)
                continue
            raise GenerationError(f"network error after {attempts} attempts: {exc}") from exc

        duration_ms = int((time.monotonic() - start) * 1000)
        status = response.status_code

        if status == 200:
            try:
                payload_resp = response.json()
            except ValueError as exc:
                raise GenerationError(f"response is not json: {response.text[:500]}") from exc
            image_bytes = _decode_first_image(payload_resp)
            return GenerationResult(
                image_bytes=image_bytes,
                raw_response=payload_resp,
                duration_ms=duration_ms,
                status_code=status,
                request_payload=payload,
            )

        # 400 可能是 response_format 不被支持，尝试剥离重试一次。
        if status == 400 and "response_format" in payload:
            stripped = {k: v for k, v in payload.items() if k != "response_format"}
            payload = stripped
            time.sleep(1)
            continue

        # 401 / 403 / 404 立即失败。
        if status in (401, 403, 404):
            body = response.text[:500]
            raise GenerationError(f"{status} non-retriable: {body}")

        # 429 / 5xx 退避重试。
        if status == 429 or 500 <= status < 600:
            sleep_seconds = backoff[min(attempt, len(backoff) - 1)] if backoff else 10
            last_error = GenerationError(f"{status} retriable: {response.text[:200]}")
            if attempt < attempts - 1:
                time.sleep(sleep_seconds)
                continue
            raise last_error

        # 其它状态：报错。
        raise GenerationError(f"unexpected status {status}: {response.text[:500]}")

    raise GenerationError(f"exhausted attempts ({attempts}), last error: {last_error}")
