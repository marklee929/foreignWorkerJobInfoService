"""News duplicate detection helpers."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable

from ..models import DuplicateCheckResult, NewsCandidate


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


def check_duplicate(candidate: NewsCandidate, existing_items: Iterable[NewsCandidate]) -> DuplicateCheckResult:
    for existing in existing_items:
        if existing.id == candidate.id:
            continue
        if candidate.id is not None and existing.id is not None and existing.id > candidate.id:
            continue
        if candidate.source_url and candidate.source_url == existing.source_url:
            return DuplicateCheckResult(True, existing.duplicate_group_id or existing.id, 1.0, "canonical_url")
        if candidate.hash_key and candidate.hash_key == existing.hash_key:
            return DuplicateCheckResult(True, existing.duplicate_group_id or existing.id, 1.0, "hash_key")
        similarity = title_similarity(candidate.similarity_key, existing.similarity_key)
        if similarity >= 0.92:
            return DuplicateCheckResult(
                True,
                existing.duplicate_group_id or existing.id,
                similarity,
                "title_similarity",
            )
        if (
            candidate.keyword
            and candidate.keyword == existing.keyword
            and candidate.collected_at[:10] == existing.collected_at[:10]
            and similarity >= 0.82
        ):
            return DuplicateCheckResult(
                True,
                existing.duplicate_group_id or existing.id,
                similarity,
                "same_day_keyword_event",
            )
    return DuplicateCheckResult(False, candidate.duplicate_group_id or candidate.id, 0.0, "no_duplicate")


def is_duplicate(item, existing_items) -> bool:
    return find_duplicate(item, existing_items) is not None
