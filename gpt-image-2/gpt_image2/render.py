"""模板 + 方案 placeholder → 最终 prompt。"""

from __future__ import annotations

from typing import Any

from .config import StyleConfig, load_style_config, load_templates


def render_prompt(
    image_entry: dict[str, Any],
    *,
    templates: dict[str, Any] | None = None,
    style: StyleConfig | None = None,
) -> str:
    """按 image_entry 找到模板，做占位符替换，追加风格基线，返回最终 prompt 字符串。"""
    templates = templates if templates is not None else load_templates()
    style = style if style is not None else load_style_config()

    template_key = image_entry["template"]
    if template_key not in templates:
        raise KeyError(f"template not found: {template_key}")
    template = templates[template_key]

    prompt_template: str = template["prompt_template"]
    placeholders: dict[str, str] = image_entry.get("placeholders", {})

    declared = set(template.get("placeholders", []))
    provided = set(placeholders.keys())
    missing = declared - provided
    if missing:
        raise ValueError(
            f"image {image_entry['image_id']} missing placeholders: {sorted(missing)}"
        )

    rendered = prompt_template
    for key, value in placeholders.items():
        rendered = rendered.replace("{" + key + "}", value)

    extra = template.get("aspect_ratio_hint")
    style_suffix = style.positive_style_suffix
    if extra and extra not in style_suffix:
        style_suffix = f"{style_suffix}, aspect ratio {extra}"

    return f"{rendered.strip()} {style_suffix.strip()}".strip()


def resolve_size(image_entry: dict[str, Any], style: StyleConfig | None = None) -> str:
    """优先 image_entry.size，其次 templates 默认，最后 1024x1024。"""
    style = style if style is not None else load_style_config()
    if "size" in image_entry:
        return str(image_entry["size"])
    template_key = image_entry.get("template", "")
    return style.default_size_by_template.get(template_key, "1024x1024")
