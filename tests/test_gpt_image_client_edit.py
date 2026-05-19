import base64
import json
from pathlib import Path

import pytest
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "gpt-image-2"
sys.path.insert(0, str(PACKAGE_ROOT))

from gpt_image2.client import edit_image
from gpt_image2.config import ModelConfig, load_model_config


class FakeResponse:
    status_code = 200
    text = "{}"

    def json(self) -> dict[str, object]:
        return {"data": [{"b64_json": base64.b64encode(b"png-bytes").decode("ascii")}]}


def test_edit_image_posts_multipart_reference(monkeypatch, tmp_path: Path) -> None:
    reference = tmp_path / "reference.jpg"
    reference.write_bytes(b"reference-bytes")
    calls: list[dict[str, object]] = []

    def fake_post(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return FakeResponse()

    monkeypatch.setattr("gpt_image2.client.requests.post", fake_post)
    config = ModelConfig(
        base_url="https://example.test",
        image_path="/v1/images/generations",
        edit_path="/v1/images/edits",
        api_key="test-key",
        model="gpt-image-2",
        defaults={"size": "1024x1024", "n": 1, "response_format": "b64_json"},
        fallback_models=[],
        request={"timeout_seconds": 120, "max_retries": 0, "backoff_seconds": []},
    )

    result = edit_image(
        config=config, prompt="make it technical", reference_image_path=reference
    )

    assert result.image_bytes == b"png-bytes"
    assert calls[0]["args"] == ("https://example.test/v1/images/edits",)
    kwargs = calls[0]["kwargs"]
    assert kwargs["headers"] == {"Authorization": "Bearer test-key"}
    assert kwargs["data"]["prompt"] == "make it technical"
    assert kwargs["data"]["model"] == "gpt-image-2"
    assert kwargs["files"]["image"][0] == "reference.jpg"
    assert kwargs["files"]["image"][2] == "image/jpeg"
    assert kwargs["timeout"] == 120


def test_model_config_rejects_http_for_external_calls(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "model.json"
    config_path.write_text(
        json.dumps(
            {
                "image_path": "/v1/images/generations",
                "edit_path": "/v1/images/edits",
                "model": "gpt-image-2",
                "defaults": {},
                "request": {},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GPT_IMAGE_BASE_URL", "http://example.test")
    monkeypatch.setenv("GPT_IMAGE_API_KEY", "test-key")

    with pytest.raises(ValueError, match="must use https"):
        load_model_config(config_path, require_credentials=True)
