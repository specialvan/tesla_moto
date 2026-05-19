import base64
from pathlib import Path

import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "gpt-image-2"
sys.path.insert(0, str(PACKAGE_ROOT))

from gpt_image2.client import edit_image
from gpt_image2.config import ModelConfig


class FakeResponse:
    status_code = 200
    text = "{}"

    def json(self) -> dict[str, object]:
        return {"data": [{"b64_json": base64.b64encode(b"png-bytes").decode("ascii")}]}


def test_edit_image_posts_multipart_reference(monkeypatch, tmp_path: Path) -> None:
    reference = tmp_path / "reference.png"
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
    assert kwargs["files"]["image"][0] == "reference.png"
    assert kwargs["timeout"] == 120
