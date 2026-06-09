"""News duplicate detection helpers."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Iterable

from ..models import DuplicateCheckResult, NewsCandidate


def comparable_text(value: str) -> str:
    """Normalize titles and body text for source-independent duplicate checks."""
    text = (value or "").lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^0-9a-z가-힣]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def title_similarity(left: str, right: str) -> float:
    left = comparable_text(left)
    right = comparable_text(right)
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def content_similarity(left: str, right: str) -> float:
    left_text = comparable_text(left)[:1600]
    right_text = comparable_text(right)[:1600]
    if not left_text or not right_text:
        return 0.0
    return SequenceMatcher(None, left_text, right_text).ratio()


def find_duplicate(candidate: NewsCandidate, existing_items: Iterable[NewsCandidate]) -> NewsCandidate | None:
    for existing in existing_items:
        if candidate.source_url and candidate.source_url == existing.source_url:
            return existing
        if candidate.hash_key and candidate.hash_key == existing.hash_key:
            return existing

        title_score = title_similarity(candidate.title or candidate.similarity_key, existing.title or existing.similarity_key)
        body_score = content_similarity(candidate.content or candidate.summary, existing.content or existing.summary)
        if title_score >= 0.92:
            return existing
        if title_score >= 0.86 and body_score >= 0.70:
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

        title_score = title_similarity(candidate.title or candidate.similarity_key, existing.title or existing.similarity_key)
        body_score = content_similarity(candidate.content or candidate.summary, existing.content or existing.summary)
        if title_score >= 0.92:
            return DuplicateCheckResult(
                True,
                existing.duplicate_group_id or existing.id,
                title_score,
                "title_similarity",
            )
        if title_score >= 0.86 and body_score >= 0.70:
            return DuplicateCheckResult(
                True,
                existing.duplicate_group_id or existing.id,
                max(title_score, body_score),
                "title_content_similarity",
            )
        if (
            candidate.keyword
            and candidate.keyword == existing.keyword
            and candidate.collected_at[:10] == existing.collected_at[:10]
            and title_score >= 0.82
        ):
            return DuplicateCheckResult(
                True,
                existing.duplicate_group_id or existing.id,
                title_score,
                "same_day_keyword_event",
            )
    return DuplicateCheckResult(False, candidate.duplicate_group_id or candidate.id, 0.0, "no_duplicate")


def is_duplicate(item, existing_items) -> bool:
    return find_duplicate(item, existing_items) is not None
