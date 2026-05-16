"""Common text normalization helpers."""

import re


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()
