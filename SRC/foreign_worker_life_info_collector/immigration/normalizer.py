"""Normalize and score official immigration notices."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urldefrag

from .models import OfficialNotice, OfficialNoticeItem

VISA_TYPES = ("E-9", "E-7", "E-2", "F-4", "F-6", "D-2", "D-10", "H-2", "C-3", "G-1")
USER_GROUP_RULES = {
    "foreign_workers": ("외국인근로자", "외국인 근로자", "foreign worker", "eps", "고용허가"),
    "international_students": ("유학생", "international student", "d-2", "d-10"),
    "marriage_immigrants": ("결혼이민", "f-6"),
    "employers": ("사업주", "고용주", "employer"),
    "undocumented_risk": ("불법체류", "미등록", "undocumented"),
    "skilled_workers": ("숙련", "skilled", "e-7"),
    "seasonal_workers": ("계절근로", "seasonal"),
    "eps_workers": ("eps", "e-9", "고용허가"),
}
POLICY_KEYWORDS = {
    "visa_policy": ("비자", "사증", "체류자격", "visa", "stay status"),
    "employment_policy": ("고용허가", "외국인고용", "employment permit", "eps"),
    "deadline": ("마감", "신청기간", "deadline", "접수기간"),
    "application": ("신청", "접수", "apply", "application"),
    "support": ("지원", "상담", "support"),
}
REGION_TERMS = ("서울", "부산", "인천", "대구", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주")


def normalize_notice_item(item: OfficialNoticeItem) -> OfficialNotice:
    title = normalize_text(item.title)
    content = normalize_text(item.content or item.summary)
    haystack = f"{title} {content}"
    visa_types = extract_visa_types(haystack)
    user_groups = extract_user_groups(haystack)
    keywords = extract_policy_keywords(haystack)
    regions = [region for region in REGION_TERMS if region in haystack]
    score = importance_score(item.notice_type, visa_types, user_groups, keywords, item.source_type)
    return OfficialNotice(
        source=item.source,
        source_name=item.source_name,
        source_type=item.source_type,
        notice_type=item.notice_type,
        title_ko=title,
        original_url=item.url,
        canonical_url=canonical_url(item.url),
        published_at=item.published_at,
        raw_content_ko=content,
        affected_visa_types=visa_types,
        affected_user_groups=user_groups,
        region_tags=regions,
        policy_keywords=keywords,
        importance_score=score,
        urgency_level=urgency_level(score, keywords),
        content_status="NORMALIZED",
        raw_response=item.raw_payload or {},
    )


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def canonical_url(url: str) -> str:
    clean, _fragment = urldefrag((url or "").strip())
    return clean


def absolute_url(base_url: str, href: str) -> str:
    return canonical_url(urljoin(base_url, href or ""))


def extract_visa_types(text: str) -> list[str]:
    normalized = text.upper().replace(" ", "")
    return [visa for visa in VISA_TYPES if visa.replace("-", "") in normalized.replace("-", "") or visa in normalized]


def extract_user_groups(text: str) -> list[str]:
    lower = text.lower()
    return [group for group, terms in USER_GROUP_RULES.items() if any(term.lower() in lower for term in terms)]


def extract_policy_keywords(text: str) -> list[str]:
    lower = text.lower()
    return [key for key, terms in POLICY_KEYWORDS.items() if any(term.lower() in lower for term in terms)]


def importance_score(notice_type: str, visa_types: list[str], user_groups: list[str], keywords: list[str], source_type: str) -> float:
    score = 20.0
    if notice_type in {"VISA_POLICY", "STAY_STATUS", "EMPLOYMENT_POLICY"}:
        score += 30.0
    if visa_types:
        score += min(25.0, len(visa_types) * 8.0)
    if user_groups:
        score += min(20.0, len(user_groups) * 5.0)
    if "deadline" in keywords or "application" in keywords:
        score += 15.0
    if source_type in {"MINISTRY_OF_JUSTICE", "HIKOREA", "EPS"}:
        score += 10.0
    return round(min(score, 100.0), 2)


def urgency_level(score: float, keywords: list[str]) -> str:
    if score >= 80 or "deadline" in keywords:
        return "HIGH"
    if score >= 55:
        return "MEDIUM"
    return "LOW"
