"""Automatic candidate scoring and selection."""

from __future__ import annotations

from ..models import CandidateEvaluation, NewsCandidate

FOREIGN_WORKER_TERMS = (
    "foreign worker",
    "foreign workers",
    "foreigner",
    "migrant worker",
    "외국인",
    "외국인 근로자",
    "외국인 노동자",
    "이주노동자",
)

KOREA_TERMS = (
    "한국",
    "korea",
    "국내",
    "법무부",
    "고용노동부",
    "출입국",
    "고용허가제",
    "지역특화형 비자",
    "외국인 노동자",
    "외국인 근로자",
    "외국인 취업비자",
    "정주",
    "산업현장",
    "중소기업",
)

VISA_LABOR_TERMS = (
    "visa",
    "e-9",
    "e9",
    "e-7",
    "e7",
    "비자",
    "취업비자",
    "고용허가",
    "고용허가제",
    "노동",
    "근로",
    "취업",
    "체류",
)

NON_KOREA_PENALTY_TERMS = (
    "h-1b",
    "h1b",
    "미국",
    " us ",
    "canada",
    "australia",
    "해외 취업",
)

RELIABLE_SOURCE_HINTS = ("go.kr", "moel", "hikorea", "immigration", "kbs", "yonhap", "yna", "news")


class CandidateEvaluator:
    def __init__(self, publish_threshold: float = 0.62):
        self.publish_threshold = publish_threshold

    def evaluate(self, candidate: NewsCandidate) -> CandidateEvaluation:
        foreign_worker = self._term_score(candidate, FOREIGN_WORKER_TERMS)
        korea = self._korea_relevance(candidate)
        visa_labor = self._term_score(candidate, VISA_LABOR_TERMS)
        freshness = 1.0 if candidate.collected_at else 0.7
        reliability = self._source_reliability(candidate)
        duplicate_risk = min(max(candidate.duplicate_risk_score, 0.0), 1.0)
        facebook = self._facebook_suitability(candidate)
        penalty = self._non_korea_penalty(candidate)
        total = (
            foreign_worker * 0.22
            + korea * 0.25
            + visa_labor * 0.18
            + freshness * 0.08
            + reliability * 0.10
            + (1.0 - duplicate_risk) * 0.10
            + facebook * 0.07
            - penalty
        )
        total = max(0.0, min(total, 1.0))
        decision = "READY_TO_PUBLISH" if total >= self.publish_threshold and duplicate_risk < 0.85 else "SKIPPED"
        reason = self._reason(candidate, decision, korea, visa_labor, penalty)
        return CandidateEvaluation(
            candidate_id=candidate.id or 0,
            total_score=round(total, 4),
            foreign_worker_relevance_score=round(foreign_worker, 4),
            korea_relevance_score=round(korea, 4),
            visa_or_labor_policy_score=round(visa_labor, 4),
            freshness_score=round(freshness, 4),
            source_reliability_score=round(reliability, 4),
            duplicate_risk_score=round(duplicate_risk, 4),
            content_clarity_score=round(self._content_clarity(candidate), 4),
            facebook_post_suitability_score=round(facebook, 4),
            decision=decision,
            reason=reason,
        )

    def _text(self, candidate: NewsCandidate) -> str:
        return f" {candidate.title} {candidate.summary} {candidate.short_summary} {candidate.relevance_reason} {candidate.source_name} {candidate.source_url} ".lower()

    def _term_score(self, candidate: NewsCandidate, terms: tuple[str, ...]) -> float:
        text = self._text(candidate)
        matches = sum(1 for term in terms if term.lower() in text)
        if matches >= 3:
            return 1.0
        if matches == 2:
            return 0.78
        if matches == 1:
            return 0.55
        return 0.1

    def _korea_relevance(self, candidate: NewsCandidate) -> float:
        score = self._term_score(candidate, KOREA_TERMS)
        text = self._text(candidate)
        if "외국인 취업비자" in text or "고용허가제" in text or "e-9" in text or "e-7" in text:
            score = max(score, 0.95)
        return score

    def _non_korea_penalty(self, candidate: NewsCandidate) -> float:
        text = self._text(candidate)
        if any(term in text for term in NON_KOREA_PENALTY_TERMS):
            return 0.35 if self._korea_relevance(candidate) < 0.55 else 0.12
        return 0.0

    def _source_reliability(self, candidate: NewsCandidate) -> float:
        text = self._text(candidate)
        if any(hint in text for hint in RELIABLE_SOURCE_HINTS):
            return 0.85
        if candidate.source_url.startswith("https://"):
            return 0.62
        return 0.4

    def _content_clarity(self, candidate: NewsCandidate) -> float:
        text = candidate.short_summary or candidate.summary or candidate.title
        if len(text) >= 80:
            return 0.9
        if len(text) >= 30:
            return 0.7
        return 0.4

    def _facebook_suitability(self, candidate: NewsCandidate) -> float:
        if not candidate.source_url or not candidate.title:
            return 0.0
        if len(candidate.title) > 160:
            return 0.45
        return 0.88 if candidate.short_summary or candidate.summary else 0.62

    def _reason(self, candidate: NewsCandidate, decision: str, korea: float, visa_labor: float, penalty: float) -> str:
        if penalty >= 0.35:
            return "Skipped because it appears to be non-Korea visa news, not Korea foreign worker support."
        if decision == "READY_TO_PUBLISH" and korea >= 0.75 and visa_labor >= 0.55:
            return "Selected because it directly discusses Korea foreign worker visa or labor policy."
        if decision == "READY_TO_PUBLISH":
            return "Selected because it is relevant to foreign workers in Korea."
        return "Skipped because Korea-specific foreign worker relevance was not strong enough."
