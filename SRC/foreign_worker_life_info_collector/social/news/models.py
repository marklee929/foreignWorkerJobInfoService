"""News content models for social publishing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NewsItem:
    title: str
    url: str
    source: str = ""
    source_name: str = ""
    google_news_url: str = ""
    canonical_url: str = ""
    publisher_name: str = ""
    summary: str = ""
    content: str = ""
    image_url: str = ""
    image_urls: list[str] | None = None
    language: str = "ko"
    category: str = ""


@dataclass
class NewsCandidate:
    title: str
    source_url: str
    source_type: str
    source_name: str = ""
    google_news_url: str = ""
    canonical_url: str = ""
    publisher_name: str = ""
    summary: str = ""
    content: str = ""
    image_url: str = ""
    image_urls: list[str] | None = None
    language: str = "ko"
    category: str = ""
    content_category: str = ""
    content_priority_group: str = ""
    settlement_relevance_score: float = 0.0
    practical_value_score: float = 0.0
    category_rotation_score: float = 0.0
    content_potential_score: float = 0.0
    category_selection_reason: str = ""
    is_sensitive: bool = False
    review_required_reason: str = ""
    keyword: str = ""
    hash_key: str = ""
    similarity_key: str = ""
    short_summary: str = ""
    key_points: str = ""
    relevance_reason: str = ""
    risk_notes: str = ""
    generated_title: str = ""
    generated_summary_en: str = ""
    generated_why_it_matters_en: str = ""
    evaluation_score: float = 0.0
    duplicate_risk_score: float = 0.0
    foreign_worker_relevance_score: float = 0.0
    korea_relevance_score: float = 0.0
    visa_or_labor_policy_score: float = 0.0
    freshness_score: float = 0.0
    source_reliability_score: float = 0.0
    facebook_post_suitability_score: float = 0.0
    selection_reason: str = ""
    skip_reason: str = ""
    facebook_post_url: str = ""
    facebook_post_id: str = ""
    last_publish_attempt_at: str = ""
    publish_attempt_count: int = 0
    score_threshold: float = 0.0
    score_breakdown_json: str = ""
    telegram_notified: bool = False
    fail_reason: str = ""
    risk_level: str = ""
    post_expired: bool = False
    post_expired_at: str = ""
    post_expired_reason: str = ""
    cycle_id: str = ""
    publish_status: str = ""
    status: str = "CANDIDATE"
    collected_at: str = ""
    published_at: str | None = None
    duplicate_group_id: int | None = None
    related_source_count: int = 1
    duplicate_count: int = 0
    group_item_count: int = 1
    last_seen_at: str = ""
    is_representative: bool = True
    existing_representative: bool = False
    id: int | None = None

    @classmethod
    def from_item(cls, item: NewsItem) -> "NewsCandidate":
        return cls(
            title=item.title,
            source_url=item.url,
            source_type=item.source or "manual",
            source_name=item.source_name,
            google_news_url=item.google_news_url,
            canonical_url=item.canonical_url or item.url,
            publisher_name=item.publisher_name,
            summary=item.summary,
            content=item.content,
            image_url=item.image_url,
            image_urls=item.image_urls or [],
            language=item.language,
            category=item.category,
            content_category=item.category,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "google_news_url": self.google_news_url,
            "canonical_url": self.canonical_url,
            "publisher_name": self.publisher_name,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "image_url": self.image_url,
            "image_urls": self.image_urls or [],
            "language": self.language,
            "category": self.category,
            "content_category": self.content_category,
            "content_priority_group": self.content_priority_group,
            "settlement_relevance_score": self.settlement_relevance_score,
            "practical_value_score": self.practical_value_score,
            "category_rotation_score": self.category_rotation_score,
            "content_potential_score": self.content_potential_score,
            "category_selection_reason": self.category_selection_reason,
            "is_sensitive": self.is_sensitive,
            "review_required_reason": self.review_required_reason,
            "keyword": self.keyword,
            "hash_key": self.hash_key,
            "similarity_key": self.similarity_key,
            "short_summary": self.short_summary,
            "key_points": self.key_points,
            "relevance_reason": self.relevance_reason,
            "risk_notes": self.risk_notes,
            "generated_title": self.generated_title,
            "generated_summary_en": self.generated_summary_en,
            "generated_why_it_matters_en": self.generated_why_it_matters_en,
            "evaluation_score": self.evaluation_score,
            "duplicate_risk_score": self.duplicate_risk_score,
            "foreign_worker_relevance_score": self.foreign_worker_relevance_score,
            "korea_relevance_score": self.korea_relevance_score,
            "visa_or_labor_policy_score": self.visa_or_labor_policy_score,
            "freshness_score": self.freshness_score,
            "source_reliability_score": self.source_reliability_score,
            "facebook_post_suitability_score": self.facebook_post_suitability_score,
            "selection_reason": self.selection_reason,
            "skip_reason": self.skip_reason,
            "facebook_post_url": self.facebook_post_url,
            "facebook_post_id": self.facebook_post_id,
            "last_publish_attempt_at": self.last_publish_attempt_at,
            "publish_attempt_count": self.publish_attempt_count,
            "score_threshold": self.score_threshold,
            "score_breakdown_json": self.score_breakdown_json,
            "telegram_notified": self.telegram_notified,
            "fail_reason": self.fail_reason,
            "risk_level": self.risk_level,
            "post_expired": self.post_expired,
            "post_expired_at": self.post_expired_at,
            "post_expired_reason": self.post_expired_reason,
            "cycle_id": self.cycle_id,
            "publish_status": self.publish_status,
            "duplicate_group_id": self.duplicate_group_id,
            "status": self.status,
            "collected_at": self.collected_at,
            "published_at": self.published_at,
            "related_source_count": self.related_source_count,
            "duplicate_count": self.duplicate_count,
            "group_item_count": self.group_item_count,
            "last_seen_at": self.last_seen_at,
            "is_representative": self.is_representative,
        }


@dataclass
class NewsSummary:
    short_summary: str
    key_points: list[str]
    relevance_reason: str
    risk_notes: str = ""
    generated_title: str = ""
    generated_summary_en: str = ""
    generated_why_it_matters_en: str = ""


@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    duplicate_group_id: int | None = None
    duplicate_risk_score: float = 0.0
    reason: str = ""
    advisory_source: str = "deterministic"


@dataclass
class CandidateEvaluation:
    candidate_id: int
    total_score: float
    foreign_worker_relevance_score: float
    korea_relevance_score: float
    visa_or_labor_policy_score: float
    freshness_score: float
    source_reliability_score: float
    duplicate_risk_score: float
    content_clarity_score: float
    facebook_post_suitability_score: float
    decision: str
    settlement_relevance_score: float = 0.0
    practical_value_score: float = 0.0
    content_potential_score: float = 0.0
    is_sensitive: bool = False
    review_required_reason: str = ""
    reason: str = ""
    threshold: float = 0.0
    score_breakdown_json: str = ""
