from __future__ import annotations

import re
from typing import Any


SUFFIXES = (
    ".equals",
    ".regex",
    ".enum",
    ".count_min",
    ".count_max",
    ".min",
    ".max",
    ".present",
    ".absent",
)


def split_expect_key(key: str) -> tuple[str, str]:
    for suffix in SUFFIXES:
        if key.endswith(suffix):
            return key[: -len(suffix)], suffix[1:]
    raise ValueError(f"expect key {key!r} missing recognised suffix {SUFFIXES}")


def expect_key_has_suffix(key: str) -> bool:
    return key.endswith(SUFFIXES)


def _walk(output: Any, dotted: str) -> Any:
    cursor: Any = output
    for part in dotted.split("."):
        if isinstance(cursor, dict):
            if part not in cursor:
                raise KeyError(f"missing key {part!r} in path {dotted!r}")
            cursor = cursor[part]
        else:
            raise TypeError(
                f"cannot descend into non-dict {type(cursor).__name__} at {dotted!r}"
            )
    return cursor


def eval_expect_check(
    key: str, expected: Any, output: dict[str, Any]
) -> tuple[bool, str]:
    path, op = split_expect_key(key)
    try:
        value = _walk(output, path)
    except (KeyError, TypeError) as exc:
        if op == "present":
            return False, f"{path}: {exc}"
        if op == "absent":
            return True, f"{path}: absent"
        return False, f"{path}: {exc}"
    if op == "equals":
        return value == expected, f"{path}={value!r} == {expected!r}"
    if op == "regex":
        if not isinstance(value, str):
            return False, f"{path}={value!r} not a string"
        return bool(re.match(expected, value)), f"{path}={value!r} regex={expected}"
    if op == "enum":
        return value in expected, f"{path}={value!r} in {expected}"
    if op == "count_min":
        length = len(value) if hasattr(value, "__len__") else 0
        return length >= expected, f"len({path})={length} >= {expected}"
    if op == "count_max":
        length = len(value) if hasattr(value, "__len__") else 0
        return length <= expected, f"len({path})={length} <= {expected}"
    if op == "min":
        return value >= expected, f"{path}={value} >= {expected}"
    if op == "max":
        return value <= expected, f"{path}={value} <= {expected}"
    if op == "present":
        return value is not None, f"{path} present={value is not None}"
    if op == "absent":
        return value is None, f"{path} absent={value is None}"
    raise ValueError(f"unhandled op {op!r}")
