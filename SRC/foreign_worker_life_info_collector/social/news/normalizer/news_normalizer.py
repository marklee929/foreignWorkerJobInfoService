"""News item normalization helpers."""

from __future__ import annotations

import re

from ....utils.date_utils import utc_now_iso
from ....utils.hash_utils import stable_hash
from ....utils.text_normalizer import normalize_plain_text
from ....utils.url_normalizer import normalize_url
from ..collector.google_news_url_resolver import is_acceptable_source_url, is_google_news_url
from ..models import NewsCandidate, NewsItem


def normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", normalize_plain_text(value).strip())


def split_source_from_title(title: str) -> tuple[str, str]:
    cleaned = normalize_title(title)
    match = re.match(r"^(?P<title>.+?)\s+-\s+(?P<source>[^-]{2,40})$", cleaned)
    if not match:
        return cleaned, ""
    return match.group("title").strip(), match.group("source").strip()


def build_similarity_key(title: str) -> str:
    normalized = normalize_title(title).lower()
    return re.sub(r"[^0-9a-z가-힣]+", "", normalized)


def normalize_news_item(item: NewsItem | NewsCandidate) -> NewsCandidate:
    candidate = item if isinstance(item, NewsCandidate) else NewsCandidate.from_item(item)
    title, source_name_from_title = split_source_from_title(candidate.title)
    source_url = normalize_url(candidate.source_url).rstrip("/")
    google_news_url = normalize_url(candidate.google_news_url).rstrip("/")
    if is_google_news_url(source_url) or not is_acceptable_source_url(source_url):
        source_url = ""
    canonical_url = normalize_url(candidate.canonical_url).rstrip("/")
    if is_google_news_url(canonical_url) or not is_acceptable_source_url(canonical_url):
        canonical_url = ""
    similarity_key = build_similarity_key(title)
    hash_key = stable_hash(source_url or google_news_url or similarity_key)
    return NewsCandidate(
        id=candidate.id,
        title=title,
        source_url=source_url,
        source_type=(candidate.source_type or "manual").strip(),
        source_name=normalize_plain_text(candidate.source_name or source_name_from_title),
        google_news_url=google_news_url,
        canonical_url=canonical_url,
        publisher_name=normalize_plain_text(candidate.publisher_name or candidate.source_name or source_name_from_title),
        summary=normalize_plain_text(candidate.summary),
        content=normalize_plain_text(candidate.content),
        image_url=normalize_url(candidate.image_url).strip(),
        image_urls=[normalize_url(url).strip() for url in (candidate.image_urls or []) if normalize_url(url).strip()],
        language=(candidate.language or "ko").strip(),
        category=(candidate.category or "").strip(),
        keyword=(candidate.keyword or "").strip(),
        hash_key=hash_key,
        similarity_key=similarity_key,
        short_summary=normalize_plain_text(candidate.short_summary),
        key_points=normalize_plain_text(candidate.key_points),
        relevance_reason=normalize_plain_text(candidate.relevance_reason),
        risk_notes=normalize_plain_text(candidate.risk_notes),
        generated_title=normalize_plain_text(candidate.generated_title),
        generated_summary_en=normalize_plain_text(candidate.generated_summary_en),
        generated_why_it_matters_en=normalize_plain_text(candidate.generated_why_it_matters_en),
        evaluation_score=candidate.evaluation_score,
        duplicate_risk_score=candidate.duplicate_risk_score,
        foreign_worker_relevance_score=candidate.foreign_worker_relevance_score,
        korea_relevance_score=candidate.korea_relevance_score,
        visa_or_labor_policy_score=candidate.visa_or_labor_policy_score,
        freshness_score=candidate.freshness_score,
        source_reliability_score=candidate.source_reliability_score,
        facebook_post_suitability_score=candidate.facebook_post_suitability_score,
        selection_reason=normalize_plain_text(candidate.selection_reason),
        skip_reason=normalize_plain_text(candidate.skip_reason),
        facebook_post_url=candidate.facebook_post_url,
        facebook_post_id=candidate.facebook_post_id,
        last_publish_attempt_at=candidate.last_publish_attempt_at,
        publish_attempt_count=candidate.publish_attempt_count,
        score_threshold=candidate.score_threshold,
        score_breakdown_json=candidate.score_breakdown_json,
        telegram_notified=candidate.telegram_notified,
        fail_reason=normalize_plain_text(candidate.fail_reason),
        risk_level=candidate.risk_level,
        post_expired=candidate.post_expired,
        post_expired_at=candidate.post_expired_at,
        post_expired_reason=normalize_plain_text(candidate.post_expired_reason),
        cycle_id=candidate.cycle_id,
        publish_status=candidate.publish_status or candidate.status,
        status=candidate.status or "CANDIDATE",
        collected_at=candidate.collected_at or utc_now_iso(),
        published_at=candidate.published_at,
        duplicate_group_id=candidate.duplicate_group_id,
    )
