"""Automatic candidate scoring and selection."""

from __future__ import annotations

from ..models import CandidateEvaluation, NewsCandidate

RELEVANCE_TERMS = (
    "foreign worker",
    "foreign workers",
    "foreigner",
    "migrant",
    "visa",
    "e-9",
    "e7",
    "외국인",
    "외국인 근로자",
    "외국인 노동자",
    "비자",
    "고용허가",
    "취업",
    "체류",
)

RELIABLE_SOURCE_HINTS = ("go.kr", "moel", "hikorea", "immigration", "korea", "naver", "google")


class CandidateEvaluator:
    def __init__(self, publish_threshold: float = 0.55):
        self.publish_threshold = publish_threshold

    def evaluate(self, candidate: NewsCandidate) -> CandidateEvaluation:
        relevance = self._foreign_worker_relevance(candidate)
        freshness = 1.0 if candidate.collected_at else 0.7
        reliability = self._source_reliability(candidate)
        duplicate_risk = min(max(candidate.duplicate_risk_score, 0.0), 1.0)
        clarity = self._content_clarity(candidate)
        facebook = self._facebook_suitability(candidate)
        total = (
            relevance * 0.30
            + freshness * 0.15
            + reliability * 0.15
            + (1.0 - duplicate_risk) * 0.20
            + clarity * 0.10
            + facebook * 0.10
        )
        decision = "READY_TO_PUBLISH" if total >= self.publish_threshold and duplicate_risk < 0.85 else "SKIPPED"
        reason = "Selected automatically for Facebook publishing." if decision == "READY_TO_PUBLISH" else "Below automatic publishing threshold."
        return CandidateEvaluation(
            candidate_id=candidate.id or 0,
            total_score=round(total, 4),
            foreign_worker_relevance_score=round(relevance, 4),
            freshness_score=round(freshness, 4),
            source_reliability_score=round(reliability, 4),
            duplicate_risk_score=round(duplicate_risk, 4),
            content_clarity_score=round(clarity, 4),
            facebook_post_suitability_score=round(facebook, 4),
            decision=decision,
            reason=reason,
        )

    def _foreign_worker_relevance(self, candidate: NewsCandidate) -> float:
        text = f"{candidate.title} {candidate.summary} {candidate.short_summary} {candidate.relevance_reason}".lower()
        matches = sum(1 for term in RELEVANCE_TERMS if term in text)
        if matches >= 3:
            return 1.0
        if matches == 2:
            return 0.8
        if matches == 1:
            return 0.6
        return 0.2

    def _source_reliability(self, candidate: NewsCandidate) -> float:
        text = f"{candidate.source_type} {candidate.source_url}".lower()
        if any(hint in text for hint in RELIABLE_SOURCE_HINTS):
            return 0.85
        if candidate.source_url.startswith("https://"):
            return 0.65
        return 0.45

    def _content_clarity(self, candidate: NewsCandidate) -> float:
        text = candidate.short_summary or candidate.summary or candidate.title
        if len(text) >= 80:
            return 0.9
        if len(text) >= 30:
            return 0.7
        return 0.4

    def _facebook_suitability(self, candidate: NewsCandidate) -> float:
        text = candidate.short_summary or candidate.summary
        if not candidate.source_url or not candidate.title:
            return 0.0
        if len(candidate.title) > 160:
            return 0.5
        return 0.85 if text else 0.65
