"""Common text normalization helpers."""

from html import unescape
import re


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def strip_html(value: str) -> str:
    text = unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return normalize_whitespace(text)


def normalize_plain_text(value: str) -> str:
    return strip_html(value)
