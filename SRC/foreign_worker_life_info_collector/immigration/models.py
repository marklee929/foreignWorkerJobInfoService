"""Models for official immigration notices."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OfficialNoticeItem:
    source: str
    source_name: str
    source_type: str
    notice_type: str
    title: str
    url: str
    published_at: str = ""
    summary: str = ""
    content: str = ""
    raw_payload: dict = field(default_factory=dict)


@dataclass
class OfficialNotice:
    id: int | None = None
    source: str = ""
    source_name: str = ""
    source_type: str = ""
    notice_type: str = ""
    title_ko: str = ""
    title_en: str = ""
    original_url: str = ""
    canonical_url: str = ""
    published_at: str = ""
    collected_at: str = ""
    updated_at: str = ""
    raw_content_ko: str = ""
    raw_content_en: str = ""
    summary_en: str = ""
    why_it_matters_en: str = ""
    affected_visa_types: list[str] = field(default_factory=list)
    affected_user_groups: list[str] = field(default_factory=list)
    region_tags: list[str] = field(default_factory=list)
    policy_keywords: list[str] = field(default_factory=list)
    importance_score: float = 0.0
    urgency_level: str = "LOW"
    content_status: str = "RAW_COLLECTED"
    active_yn: str = "Y"
    duplicate_group_id: int | None = None
    raw_response: dict = field(default_factory=dict)
