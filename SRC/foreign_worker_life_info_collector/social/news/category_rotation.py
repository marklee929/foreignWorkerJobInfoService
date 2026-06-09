"""Category classification and rotation helpers for social news publishing."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone

PRIMARY_CATEGORIES = {
    "foreign_jobs",
    "work_visa",
    "labor_rights",
    "immigration",
    "employment_policy",
    "government_notice",
}

SECONDARY_CATEGORIES = {
    "housing",
    "banking",
    "healthcare",
    "transportation",
    "insurance",
    "korean_language",
    "cost_of_living",
    "local_community",
    "education",
    "settlement_life",
}

TERTIARY_CATEGORIES = {
    "travel",
    "lifestyle",
    "culture",
    "local_events",
    "safety",
}

CATEGORY_KEYWORDS = {
    "foreign_jobs": ("job", "jobs", "hiring", "employment", "recruitment", "career", "workplace", "foreign worker", "migrant worker", "foreign workers", "채용", "취업", "고용"),
    "work_visa": ("work visa", "e-9", "e9", "e-7", "e7", "visa", "employment permit", "비자", "고용허가"),
    "labor_rights": ("labor rights", "labour rights", "wage", "salary", "job transfer", "workplace safety", "임금", "노동권", "산재"),
    "immigration": ("immigration", "sojourn", "residence", "residency", "hikorea", "출입국", "체류", "이민"),
    "employment_policy": ("employment policy", "quota", "skilled worker", "employment ministry", "고용노동부", "정책"),
    "government_notice": ("government", "ministry", "moel", "justice ministry", "notice", "announcement", "정부", "공고", "공지"),
    "housing": ("housing", "rent", "lease", "deposit", "dormitory", "real estate", "주거", "월세", "전세", "기숙사"),
    "banking": ("bank", "banking", "account", "remittance", "wire transfer", "은행", "계좌", "송금"),
    "healthcare": ("health", "healthcare", "hospital", "clinic", "medical", "insurance card", "병원", "의료", "건강"),
    "transportation": ("transport", "transportation", "subway", "bus", "train", "교통", "지하철", "버스"),
    "insurance": ("insurance", "national health insurance", "pension", "coverage", "보험", "국민연금"),
    "korean_language": ("korean language", "language class", "topik", "한국어", "언어교육"),
    "cost_of_living": ("cost of living", "prices", "utility bill", "living cost", "생활비", "물가", "공과금"),
    "local_community": ("support center", "community", "foreign resident center", "multicultural", "지원센터", "다문화"),
    "education": ("education", "school", "training", "course", "scholarship", "교육", "훈련", "학교"),
    "settlement_life": ("settlement", "living guide", "foreign residents", "life in korea", "정착", "생활정보"),
    "travel": ("travel", "airport", "tourist", "trip", "여행", "공항"),
    "lifestyle": ("lifestyle", "daily life", "expat life", "생활", "라이프"),
    "culture": ("culture", "festival", "custom", "문화", "축제"),
    "local_events": ("event", "local event", "program", "행사", "프로그램"),
    "safety": ("safety", "emergency", "disaster", "warning", "safe", "안전", "재난", "주의"),
}

PRACTICAL_TERMS = (
    "apply",
    "application",
    "deadline",
    "document",
    "documents",
    "registration",
    "contact",
    "center",
    "office",
    "fee",
    "cost",
    "how to",
    "guide",
    "steps",
    "requirements",
    "서류",
    "신청",
    "절차",
    "비용",
    "기관",
    "센터",
    "주의사항",
)

SENSITIVE_TERMS = (
    "assault",
    "attack",
    "abuse",
    "murder",
    "death",
    "dead",
    "crime",
    "violence",
    "violent",
    "political conflict",
    "hate",
    "sexual",
    "폭행",
    "학대",
    "사망",
    "범죄",
    "정치갈등",
    "혐오",
    "선정",
)

GROUP_LABELS = {
    "PRIMARY": "채용/비자/노동",
    "SECONDARY": "생활/정착",
    "TERTIARY": "생활 가이드",
}

GROUP_THRESHOLDS = {
    "PRIMARY": {"default": 50.0, "relaxed": 40.0, "floor": 40.0},
    "SECONDARY": {"default": 55.0, "relaxed": 45.0, "floor": 45.0},
    "TERTIARY": {"default": 65.0, "relaxed": 55.0, "floor": 55.0},
}

SEARCH_KEYWORDS = {
    "PRIMARY": (
        "foreign worker visa Korea",
        "Korea work visa foreign workers",
        "E-9 visa Korea",
        "E-7 visa Korea",
        "migrant workers Korea",
        "labor rights foreign workers Korea",
        "Korea immigration policy foreign workers",
        "foreign employment Korea",
    ),
    "SECONDARY": (
        "foreigners in Korea housing",
        "foreigners in Korea bank account",
        "foreigners in Korea health insurance",
        "foreigners in Korea transportation",
        "Korea cost of living foreigners",
        "Korean language support foreigners",
        "foreign residents Korea living guide",
        "migrant support center Korea",
        "foreigners Korea rent contract",
    ),
    "TERTIARY": (
        "Korea travel safety foreigners",
        "Korea local life foreigners",
        "Korea culture guide foreigners",
        "expat life Korea",
        "foreigners living in Seoul",
        "foreigners living in Busan",
    ),
}


@dataclass
class CategoryDecision:
    content_category: str
    priority_group: str
    settlement_relevance_score: float
    practical_value_score: float
    content_potential_score: float
    is_sensitive: bool
    review_required_reason: str
    reason: str


def classify_candidate(candidate) -> CategoryDecision:
    text = normalize(" ".join([
        getattr(candidate, "title", ""),
        getattr(candidate, "summary", ""),
        getattr(candidate, "short_summary", ""),
        getattr(candidate, "content", ""),
        getattr(candidate, "keyword", ""),
        getattr(candidate, "source_name", ""),
        getattr(candidate, "publisher_name", ""),
    ]))
    scores = {category: keyword_score(text, terms) for category, terms in CATEGORY_KEYWORDS.items()}
    category = max(scores, key=lambda key: scores[key])
    if scores[category] <= 0:
        category = "settlement_life" if any(term in text for term in ("korea", "foreign", "resident", "living")) else "foreign_jobs"
    group = category_group(category)
    sensitive_matches = [term for term in SENSITIVE_TERMS if term in text]
    practical_matches = keyword_score(text, PRACTICAL_TERMS)
    settlement_matches = keyword_score(text, CATEGORY_KEYWORDS["settlement_life"] + CATEGORY_KEYWORDS["local_community"] + CATEGORY_KEYWORDS["housing"] + CATEGORY_KEYWORDS["banking"] + CATEGORY_KEYWORDS["healthcare"])
    settlement_score = clamp01((settlement_matches + (3 if group in {"SECONDARY", "TERTIARY"} else 0)) / 8)
    practical_score = clamp01((practical_matches + (2 if any(token in text for token in ("guide", "how to", "support", "center", "notice")) else 0)) / 7)
    potential_score = clamp01((scores[category] + practical_matches + len(re.findall(r"\b(korea|foreigners?|workers?|visa|living|guide)\b", text))) / 15)
    review_reason = f"Sensitive topic detected: {', '.join(sensitive_matches[:3])}" if sensitive_matches else ""
    return CategoryDecision(
        content_category=category,
        priority_group=group,
        settlement_relevance_score=round(settlement_score, 4),
        practical_value_score=round(practical_score, 4),
        content_potential_score=round(potential_score, 4),
        is_sensitive=bool(sensitive_matches),
        review_required_reason=review_reason,
        reason=f"Matched {GROUP_LABELS[group]} category '{category}' with keyword score {scores[category]:.1f}.",
    )


def category_group(category: str) -> str:
    value = (category or "").strip()
    if value in PRIMARY_CATEGORIES:
        return "PRIMARY"
    if value in SECONDARY_CATEGORIES:
        return "SECONDARY"
    if value in TERTIARY_CATEGORIES:
        return "TERTIARY"
    return "PRIMARY"


def group_threshold(group: str, relaxed: bool = False) -> float:
    config = GROUP_THRESHOLDS.get(group or "PRIMARY", GROUP_THRESHOLDS["PRIMARY"])
    return float(config["relaxed" if relaxed else "default"])


def hashtags_for_group(group: str) -> str:
    if group == "SECONDARY":
        return "#LivingInKorea #ForeignersInKorea #KoreaLife #WorkConnectKorea"
    if group == "TERTIARY":
        return "#KoreaLife #LivingInKorea #KoreaGuide #ForeignersInKorea"
    return "#KoreaJobs #WorkInKorea #ForeignWorkers #VisaInfo"


def rotation_score(candidate, recent_counts: dict[str, int], last_group: str = "") -> float:
    group = getattr(candidate, "content_priority_group", "") or category_group(getattr(candidate, "content_category", "") or getattr(candidate, "category", ""))
    count = int(recent_counts.get(group, 0) or 0)
    score = 0.0
    if count == 0:
        score += 8.0
    elif count >= 3:
        score -= min(12.0, count * 3.0)
    if group == last_group:
        score -= 6.0
    if group == "PRIMARY":
        score += 4.0
    return round(score, 2)


def recent_category_ratio(candidates: list) -> dict[str, int]:
    counts = {"PRIMARY": 0, "SECONDARY": 0, "TERTIARY": 0}
    for candidate in candidates:
        group = getattr(candidate, "content_priority_group", "") or category_group(getattr(candidate, "content_category", "") or getattr(candidate, "category", ""))
        counts[group] = counts.get(group, 0) + 1
    return counts


def target_group(primary_count: int, secondary_count: int, recent_counts: dict[str, int], last_group: str = "") -> tuple[str, str]:
    primary_recent = int(recent_counts.get("PRIMARY", 0) or 0)
    secondary_recent = int(recent_counts.get("SECONDARY", 0) or 0)
    if primary_count <= 0 and secondary_count > 0:
        return "SECONDARY", "PRIMARY 후보가 없어 SECONDARY 후보로 대체합니다."
    if primary_count <= 0:
        return "TERTIARY", "PRIMARY/SECONDARY 후보가 부족해 TERTIARY 실용 후보를 확인합니다."
    if primary_count >= 3 and primary_recent < 3:
        return "PRIMARY", "PRIMARY 후보가 충분해 3:1 비율을 우선합니다."
    if primary_count < 2 and secondary_count > 0:
        return "SECONDARY", "PRIMARY 후보가 부족해 1:1 비율로 SECONDARY를 보강합니다."
    if primary_recent >= max(2, secondary_recent * 2 + 2) and secondary_count > 0 and last_group == "PRIMARY":
        return "SECONDARY", "최근 24시간 PRIMARY 비중이 높아 SECONDARY를 보강합니다."
    return "PRIMARY", "기본 2:1 비율에 따라 PRIMARY를 우선합니다."


def normalize(value: str) -> str:
    text = (value or "").lower()
    text = re.sub(r"\s+", " ", text)
    return f" {text.strip()} "


def keyword_score(text: str, terms: tuple[str, ...]) -> float:
    score = 0.0
    for term in terms:
        if normalize(term).strip() in text:
            score += 1.0 + min(1.5, len(term) / 18)
    return score


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def selection_payload_extra(selection: dict) -> str:
    return json.dumps(
        {
            "target_category_group": selection.get("target_category_group", ""),
            "selected_category": selection.get("selected_category", ""),
            "primary_candidate_count": selection.get("primary_candidate_count", 0),
            "secondary_candidate_count": selection.get("secondary_candidate_count", 0),
            "tertiary_candidate_count": selection.get("tertiary_candidate_count", 0),
            "recent_24h_category_ratio": selection.get("recent_24h_category_ratio", {}),
            "category_selection_reason": selection.get("category_selection_reason", ""),
            "fallback_used": selection.get("fallback_used", False),
            "no_publish_reason": selection.get("no_publish_reason", ""),
            "logged_at": datetime.now(timezone.utc).isoformat(),
        },
        ensure_ascii=False,
    )
