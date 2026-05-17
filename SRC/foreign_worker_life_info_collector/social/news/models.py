"""News content models for social publishing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NewsItem:
    title: str
    url: str
    source: str = ""
    source_name: str = ""
    summary: str = ""
    content: str = ""
    language: str = "ko"
    category: str = ""


@dataclass
class NewsCandidate:
    title: str
    source_url: str
    source_type: str
    source_name: str = ""
    summary: str = ""
    content: str = ""
    language: str = "ko"
    category: str = ""
    keyword: str = ""
    hash_key: str = ""
    similarity_key: str = ""
    short_summary: str = ""
    key_points: str = ""
    relevance_reason: str = ""
    risk_notes: str = ""
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
    status: str = "CANDIDATE"
    collected_at: str = ""
    published_at: str | None = None
    duplicate_group_id: int | None = None
    id: int | None = None

    @classmethod
    def from_item(cls, item: NewsItem) -> "NewsCandidate":
        return cls(
            title=item.title,
            source_url=item.url,
            source_type=item.source or "manual",
            source_name=item.source_name,
            summary=item.summary,
            content=item.content,
            language=item.language,
            category=item.category,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "title": self.title,
            "summary": self.summary,
            "language": self.language,
            "category": self.category,
            "keyword": self.keyword,
            "hash_key": self.hash_key,
            "similarity_key": self.similarity_key,
            "short_summary": self.short_summary,
            "key_points": self.key_points,
            "relevance_reason": self.relevance_reason,
            "risk_notes": self.risk_notes,
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
            "duplicate_group_id": self.duplicate_group_id,
            "status": self.status,
            "collected_at": self.collected_at,
            "published_at": self.published_at,
        }


@dataclass
class NewsSummary:
    short_summary: str
    key_points: list[str]
    relevance_reason: str
    risk_notes: str = ""


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
    reason: str = ""
