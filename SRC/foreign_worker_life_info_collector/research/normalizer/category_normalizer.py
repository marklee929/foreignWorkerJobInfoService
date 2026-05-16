from __future__ import annotations

from ...config.categories import SERVICE_CATEGORIES


def normalize_category(text: str) -> str:
    lowered = (text or "").lower()
    for category, keywords in SERVICE_CATEGORIES.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "local_life_info"
