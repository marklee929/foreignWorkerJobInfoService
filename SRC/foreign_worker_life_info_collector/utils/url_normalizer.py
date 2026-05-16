"""Common URL normalization helpers."""


def normalize_url(value: str) -> str:
    return (value or "").strip()
