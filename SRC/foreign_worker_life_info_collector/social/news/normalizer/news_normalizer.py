"""News item normalization helpers."""

from __future__ import annotations

import re

from ....utils.date_utils import utc_now_iso
from ....utils.hash_utils import stable_hash
from ....utils.url_normalizer import normalize_url
from ..models import NewsCandidate, NewsItem


def normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def build_similarity_key(title: str) -> str:
    normalized = normalize_title(title).lower()
    return re.sub(r"[^0-9a-z가-힣]+", "", normalized)


def normalize_news_item(item: NewsItem | NewsCandidate) -> NewsCandidate:
    candidate = item if isinstance(item, NewsCandidate) else NewsCandidate.from_item(item)
    title = normalize_title(candidate.title)
    source_url = normalize_url(candidate.source_url).rstrip("/")
    similarity_key = build_similarity_key(title)
    hash_key = stable_hash(source_url or similarity_key)
    return NewsCandidate(
        id=candidate.id,
        title=title,
        source_url=source_url,
        source_type=(candidate.source_type or "manual").strip(),
        summary=normalize_title(candidate.summary),
        content=(candidate.content or "").strip(),
        language=(candidate.language or "ko").strip(),
        category=(candidate.category or "").strip(),
        keyword=(candidate.keyword or "").strip(),
        hash_key=hash_key,
        similarity_key=similarity_key,
        short_summary=(candidate.short_summary or "").strip(),
        key_points=(candidate.key_points or "").strip(),
        relevance_reason=(candidate.relevance_reason or "").strip(),
        risk_notes=(candidate.risk_notes or "").strip(),
        evaluation_score=candidate.evaluation_score,
        duplicate_risk_score=candidate.duplicate_risk_score,
        status=candidate.status or "CANDIDATE",
        collected_at=candidate.collected_at or utc_now_iso(),
        published_at=candidate.published_at,
        duplicate_group_id=candidate.duplicate_group_id,
    )
