"""配置加载：model.json / style.json / templates.json / schemes.json。"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PACKAGE_ROOT / "config"
PROMPTS_DIR = PACKAGE_ROOT / "prompts"
OUTPUTS_DIR = PACKAGE_ROOT / "outputs"


@dataclass(frozen=True)
class ModelConfig:
    base_url: str
    image_path: str
    edit_path: str
    api_key: str
    model: str
    defaults: dict[str, Any]
    fallback_models: list[str]
    request: dict[str, Any]

    @property
    def full_url(self) -> str:
        base = self.base_url.rstrip("/")
        path = (
            self.image_path
            if self.image_path.startswith("/")
            else "/" + self.image_path
        )
        return base + path

    @property
    def full_edit_url(self) -> str:
        base = self.base_url.rstrip("/")
        path = (
            self.edit_path if self.edit_path.startswith("/") else "/" + self.edit_path
        )
        return base + path

    @property
    def timeout_seconds(self) -> int:
        return int(self.request.get("timeout_seconds", 120))

    @property
    def max_retries(self) -> int:
        return int(self.request.get("max_retries", 3))

    @property
    def backoff_seconds(self) -> list[int]:
        raw = self.request.get("backoff_seconds", [5, 15, 45])
        return [int(x) for x in raw]

    @property
    def sleep_between_calls_seconds(self) -> float:
        return float(self.request.get("sleep_between_calls_seconds", 4))


@dataclass(frozen=True)
class StyleConfig:
    version: str
    positive_style_suffix: str
    negative_prompt: str
    default_size_by_template: dict[str, str]


def _validate_base_url(base_url: str, *, require_credentials: bool) -> None:
    parsed = urlparse(base_url)
    if require_credentials and parsed.scheme != "https":
        raise ValueError("GPT_IMAGE_BASE_URL must use https for external image calls")


def load_model_config(
    path: Path | None = None, *, require_credentials: bool = True
) -> ModelConfig:
    target = path or (CONFIG_DIR / "model.json")
    data = json.loads(target.read_text(encoding="utf-8"))
    local_path = CONFIG_DIR / "model.local.json"
    local_data = (
        json.loads(local_path.read_text(encoding="utf-8"))
        if local_path.exists()
        else {}
    )
    api_key = os.environ.get("GPT_IMAGE_API_KEY") or local_data.get("api_key")
    base_url = os.environ.get("GPT_IMAGE_BASE_URL") or local_data.get("base_url")
    if require_credentials and not api_key:
        raise ValueError(
            "GPT_IMAGE_API_KEY or untracked config/model.local.json api_key is required"
        )
    if require_credentials and not base_url:
        raise ValueError(
            "GPT_IMAGE_BASE_URL or untracked config/model.local.json base_url is required"
        )
    _validate_base_url(base_url or "http://dry-run.local", require_credentials=require_credentials)
    return ModelConfig(
        base_url=base_url or "http://dry-run.local",
        image_path=data.get("image_path", "/v1/images/generations"),
        edit_path=data.get("edit_path", "/v1/images/edits"),
        api_key=api_key or "dry-run",
        model=data["model"],
        defaults=data.get("defaults", {}),
        fallback_models=data.get("fallback_models", []),
        request=data.get("request", {}),
    )


def load_style_config(path: Path | None = None) -> StyleConfig:
    target = path or (CONFIG_DIR / "style.json")
    data = json.loads(target.read_text(encoding="utf-8"))
    return StyleConfig(
        version=data.get("version", "unknown"),
        positive_style_suffix=data["positive_style_suffix"],
        negative_prompt=data["negative_prompt"],
        default_size_by_template=data.get("default_size_by_template", {}),
    )


def load_templates(path: Path | None = None) -> dict[str, Any]:
    target = path or (PROMPTS_DIR / "templates.json")
    data = json.loads(target.read_text(encoding="utf-8"))
    return data["templates"]


def load_schemes(path: Path | None = None) -> dict[str, Any]:
    target = path or (PROMPTS_DIR / "schemes.json")
    data = json.loads(target.read_text(encoding="utf-8"))
    return data["schemes"]


def find_image_entry(image_id: str) -> tuple[str, dict[str, Any]]:
    """根据 image_id 在 schemes.json 内定位条目，返回 (scheme_key, image_entry)。"""
    schemes = load_schemes()
    for scheme_key, scheme in schemes.items():
        for entry in scheme["images"]:
            if entry["image_id"] == image_id:
                return scheme_key, entry
    raise KeyError(f"image_id not found in schemes.json: {image_id}")
