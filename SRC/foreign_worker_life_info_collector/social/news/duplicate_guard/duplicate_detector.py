"""News duplicate detection helpers."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable

from ..models import NewsCandidate


def title_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def find_duplicate(candidate: NewsCandidate, existing_items: Iterable[NewsCandidate]) -> NewsCandidate | None:
    for existing in existing_items:
        if candidate.source_url and candidate.source_url == existing.source_url:
            return existing
        if candidate.hash_key and candidate.hash_key == existing.hash_key:
            return existing
        if title_similarity(candidate.similarity_key, existing.similarity_key) >= 0.92:
            return existing
    return None


def is_duplicate(item, existing_items) -> bool:
    return find_duplicate(item, existing_items) is not None
