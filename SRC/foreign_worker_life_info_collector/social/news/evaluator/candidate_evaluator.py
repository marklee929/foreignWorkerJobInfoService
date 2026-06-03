"""Automatic candidate scoring and selection."""

from __future__ import annotations

import json
import math
import os
import re

from ..models import CandidateEvaluation, NewsCandidate

FOREIGN_WORKER_TERMS = (
    "foreign worker",
    "foreign workers",
    "migrant worker",
    "migrant workers",
    "migrant",
    "foreign resident",
    "foreign residents",
    "foreign national",
    "foreign nationals",
    "foreign student",
    "foreign students",
    "international student",
    "international students",
    "international worker",
    "expat worker",
    "guest worker",
    "seasonal worker",
    "skilled worker",
    "skilled workers",
    "nonprofessional foreign worker",
    "e-9",
    "e9",
    "h-2",
    "h2",
)

VISA_TERMS = (
    "visa",
    "visas",
    "immigration",
    "immigrant",
    "immigrants",
    "sojourn",
    "residence permit",
    "residency",
    "stay permit",
    "entry permit",
    "employment permit",
    "work permit",
    "work visa",
    "eps",
    "quota",
    "eligibility",
    "e-7",
    "e7",
    "e-9",
    "e9",
    "h-2",
    "h2",
    "f-4",
    "f4",
    "d-10",
    "d10",
)

LABOR_TERMS = (
    "employment",
    "job",
    "jobs",
    "hiring",
    "hire",
    "worker",
    "workers",
    "wage",
    "salary",
    "labor",
    "labour",
    "workplace",
    "industrial accident",
    "rights",
    "protection",
    "abuse",
    "recruitment",
    "employer",
    "employers",
    "job transfer",
    "employment scheme",
)

KOREA_TERMS = (
    "korea",
    "south korea",
    "korean",
    "seoul",
    "jeju",
    "moel",
    "hikorea",
    "justice ministry",
    "employment ministry",
    "ministry of employment",
)

LIFE_TERMS = (
    "housing",
    "hospital",
    "medical",
    "transport",
    "banking",
    "education",
    "settle",
    "settlement",
    "support center",
    "support programme",
    "support program",
)

ACTION_TERMS = (
    "apply",
    "application",
    "deadline",
    "document",
    "support fund",
    "contact",
    "registration",
    "policy",
    "announcement",
    "new rules",
    "changes",
)

NON_KOREA_TERMS = (
    "h-1b",
    "h1b",
    "canada",
    "australia",
    "uk visa",
    "u.s. immigration",
    "us immigration",
)
SPAM_TERMS = ("coupon", "casino", "lottery", "click here", "sponsored", "advertorial")
RELIABLE_SOURCE_HINTS = (
    "go.kr",
    "moel",
    "hikorea",
    "immigration",
    "korea.net",
    "koreaherald",
    "korea herald",
    "koreatimes",
    "korea times",
    "yonhap",
    "yna",
    "joongang",
    "bal immigration",
)


class CandidateEvaluator:
    def __init__(self, publish_threshold: float = 50.0, min_safety_score: float | None = None):
        self.publish_threshold = publish_threshold
        self.min_safety_score = min_safety_score if min_safety_score is not None else env_float("NEWS_MINIMUM_SAFE_SCORE", 40.0, 40.0, 50.0)

    def evaluate(self, candidate: NewsCandidate, threshold: float | None = None) -> CandidateEvaluation:
        threshold_value = threshold if threshold is not None else self.publish_threshold
        sections = self._sections(candidate)
        text = " ".join(sections.values())

        foreign_worker = self._term_score(sections, FOREIGN_WORKER_TERMS, 32)
        visa = self._term_score(sections, VISA_TERMS, 28)
        labor = self._term_score(sections, LABOR_TERMS, 24)
        korea = self._term_score(sections, KOREA_TERMS, 18)
        life = self._term_score(sections, LIFE_TERMS, 10)
        action = self._term_score(sections, ACTION_TERMS, 8)
        source = self._source_score(candidate)
        freshness = 8.0 if candidate.collected_at else 4.0
        title_signal = self._title_signal(candidate, sections)
        content_quality = self._content_quality_bonus(candidate)
        group_signal = self._group_signal_bonus(candidate)
        penalty = self._penalty(candidate, text)
        duplicate_penalty = self._duplicate_penalty(candidate)

        raw_score = (
            foreign_worker
            + visa
            + labor
            + korea
            + life
            + action
            + source
            + freshness
            + title_signal
            + content_quality
            + group_signal
            - penalty
            - duplicate_penalty
        )
        score = max(0.0, min(100.0, raw_score))
        disallowed = self._hard_block(candidate, text, score)
        decision = "READY_TO_PUBLISH" if not disallowed and score >= threshold_value and candidate.duplicate_risk_score < 0.85 else "SKIPPED"
        reason = disallowed or self._reason(decision, score, threshold_value)
        breakdown = {
            "foreign_worker": foreign_worker,
            "visa": visa,
            "labor": labor,
            "korea": korea,
            "life": life,
            "action": action,
            "source": source,
            "freshness": freshness,
            "title_signal": title_signal,
            "content_quality": content_quality,
            "group_signal": group_signal,
            "penalty": penalty,
            "duplicate_penalty": duplicate_penalty,
            "threshold": threshold_value,
            "min_safety_score": self.min_safety_score,
        }
        return CandidateEvaluation(
            candidate_id=candidate.id or 0,
            total_score=round(score, 2),
            foreign_worker_relevance_score=round(foreign_worker / 32, 4),
            korea_relevance_score=round(korea / 18, 4),
            visa_or_labor_policy_score=round(max(visa / 28, labor / 24, life / 10), 4),
            freshness_score=round(freshness / 8, 4),
            source_reliability_score=round(source / 16, 4),
            duplicate_risk_score=round(candidate.duplicate_risk_score, 4),
            content_clarity_score=round(self._content_clarity(candidate), 4),
            facebook_post_suitability_score=round(self._facebook_suitability(candidate), 4),
            decision=decision,
            reason=reason,
            threshold=threshold_value,
            score_breakdown_json=json.dumps(breakdown, ensure_ascii=False),
        )

    def _sections(self, candidate: NewsCandidate) -> dict[str, str]:
        return {
            "title": normalize_text(candidate.title),
            "summary": normalize_text(" ".join([candidate.summary, candidate.short_summary, candidate.relevance_reason])),
            "content": normalize_text(candidate.content),
            "source": normalize_text(" ".join([candidate.source_name, candidate.publisher_name, candidate.source_url, candidate.canonical_url])),
        }

    def _term_score(self, sections: dict[str, str], terms: tuple[str, ...], max_score: int) -> float:
        title_matches = count_matches(sections["title"], terms)
        summary_matches = count_matches(sections["summary"], terms)
        content_matches = count_matches(sections["content"], terms)
        source_matches = count_matches(sections["source"], terms)

        weighted = title_matches * 1.45 + summary_matches * 1.0 + min(content_matches, 5) * 0.55 + source_matches * 0.35
        if weighted <= 0:
            return 0.0
        score = max_score * (1 - math.exp(-weighted / 1.8))
        return round(min(float(max_score), score), 2)

    def _source_score(self, candidate: NewsCandidate) -> float:
        text = " ".join([candidate.source_name, candidate.publisher_name, candidate.source_url, candidate.canonical_url]).lower()
        if any(hint in text for hint in RELIABLE_SOURCE_HINTS):
            return 16.0
        if candidate.publisher_name or candidate.source_name:
            return 11.0
        if candidate.source_url.startswith("https://"):
            return 8.0
        return 0.0

    def _title_signal(self, candidate: NewsCandidate, sections: dict[str, str]) -> float:
        title = sections["title"]
        has_audience = any(term in title for term in FOREIGN_WORKER_TERMS)
        has_policy = any(term in title for term in VISA_TERMS + LABOR_TERMS)
        has_korea = any(term in title for term in KOREA_TERMS) or "korea" in sections["source"]
        if has_audience and has_policy and has_korea:
            return 10.0
        if has_audience and has_policy:
            return 7.0
        if has_policy and has_korea:
            return 5.0
        return 0.0

    def _content_quality_bonus(self, candidate: NewsCandidate) -> float:
        text = candidate.content or candidate.summary or candidate.short_summary
        length = len(text.strip())
        if length >= 900:
            return 8.0
        if length >= 350:
            return 6.0
        if length >= 120:
            return 3.5
        if length >= 40:
            return 1.5
        return -4.0

    def _group_signal_bonus(self, candidate: NewsCandidate) -> float:
        related = max(0, int(candidate.related_source_count or 0) - 1)
        duplicate = max(0, int(candidate.duplicate_count or 0))
        group_items = max(0, int(candidate.group_item_count or 0) - 1)
        source_bonus = min(7.0, related * 2.2)
        duplicate_bonus = min(5.0, math.log1p(duplicate) * 1.4)
        group_bonus = min(4.0, math.log1p(group_items) * 1.0)
        return round(source_bonus + duplicate_bonus + group_bonus, 2)

    def _duplicate_penalty(self, candidate: NewsCandidate) -> float:
        if bool(getattr(candidate, "is_representative", True)):
            return 0.0
        if candidate.duplicate_risk_score >= 0.85:
            return 40.0
        if candidate.duplicate_risk_score >= 0.6:
            return 18.0
        return 0.0

    def _penalty(self, candidate: NewsCandidate, text: str) -> float:
        penalty = 0.0
        has_korea = any(term in text for term in KOREA_TERMS)
        if any(term in text for term in NON_KOREA_TERMS) and not has_korea:
            penalty += 30
        if any(term in text for term in SPAM_TERMS):
            penalty += 35
        if not candidate.source_url:
            penalty += 25
        if not (candidate.source_name or candidate.publisher_name):
            penalty += 6
        if len(candidate.title) > 180:
            penalty += 8
        if len(candidate.title.strip()) < 12:
            penalty += 8
        return penalty

    def _hard_block(self, candidate: NewsCandidate, text: str, score: float) -> str:
        if not candidate.source_url:
            return "원문 링크가 없어 게시할 수 없습니다."
        if not candidate.title:
            return "제목이 없어 게시할 수 없습니다."
        if score < self.min_safety_score:
            return f"최소 안전 점수 {self.min_safety_score:.0f}점 미만으로 게시하지 않습니다."
        if not any(term in text for term in FOREIGN_WORKER_TERMS + VISA_TERMS + LABOR_TERMS):
            return "외국인 근로자, 비자, 취업, 노동 정보와의 직접 관련성이 부족합니다."
        if any(term in text for term in SPAM_TERMS):
            return "광고 또는 스팸성 표현이 포함되어 게시하지 않습니다."
        return ""

    def _content_clarity(self, candidate: NewsCandidate) -> float:
        text = candidate.content or candidate.short_summary or candidate.summary or candidate.title
        if len(text) >= 350:
            return 0.95
        if len(text) >= 120:
            return 0.82
        if len(text) >= 40:
            return 0.65
        return 0.35

    def _facebook_suitability(self, candidate: NewsCandidate) -> float:
        if not candidate.source_url or not candidate.title:
            return 0.0
        if len(candidate.title) > 180:
            return 0.45
        if candidate.generated_summary_en and candidate.generated_why_it_matters_en:
            return 0.95
        if candidate.short_summary or candidate.summary or candidate.content:
            return 0.82
        return 0.58

    def _reason(self, decision: str, score: float, threshold: float) -> str:
        if decision == "READY_TO_PUBLISH":
            return f"게시 기준 {threshold:.0f}점 이상을 충족했습니다. 현재 점수: {score:.0f}점"
        return f"게시 기준 {threshold:.0f}점에 미달했습니다. 현재 점수: {score:.0f}점"


def normalize_text(value: str) -> str:
    text = (value or "").lower()
    text = text.replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return f" {text.strip()} "


def count_matches(text: str, terms: tuple[str, ...]) -> int:
    return sum(1 for term in terms if normalize_text(term).strip() in text)


def env_float(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(os.getenv(name, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))
