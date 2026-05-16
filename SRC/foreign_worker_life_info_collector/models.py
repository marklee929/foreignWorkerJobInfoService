from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_hash_key(*parts: str) -> str:
    payload = "|".join((part or "").strip().lower() for part in parts)
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class RawSourceData:
    source_type: str
    source_url: str
    search_keyword: str
    raw_title: str
    raw_content: str = ""
    raw_phone: str = ""
    raw_address: str = ""
    collected_at: str = field(default_factory=utc_now_iso)
    hash_key: str = ""
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.hash_key:
            self.hash_key = make_hash_key(self.source_type, self.source_url, self.raw_title, self.raw_phone)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BusinessLanguageSupport:
    language_code: str
    language_name: str
    confidence_score: float
    evidence_text: str = ""
    id: Optional[int] = None
    business_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BusinessServiceTag:
    tag_name: str
    confidence_score: float
    evidence_text: str = ""
    id: Optional[int] = None
    business_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LifeServiceBusiness:
    business_name: str
    category: str
    sub_category: str = ""
    phone: str = ""
    address: str = ""
    sido: str = ""
    sigungu: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website_url: str = ""
    kakao_url: str = ""
    naver_place_url: str = ""
    google_place_url: str = ""
    is_active: bool = True
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    id: Optional[int] = None
    languages: List[BusinessLanguageSupport] = field(default_factory=list)
    tags: List[BusinessServiceTag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrawlLog:
    crawler_name: str
    keyword: str
    status: str
    collected_count: int = 0
    error_message: str = ""
    started_at: str = field(default_factory=utc_now_iso)
    ended_at: str = ""
    id: Optional[int] = None

    def finish(self, status: str, collected_count: int = 0, error_message: str = "") -> None:
        self.status = status
        self.collected_count = collected_count
        self.error_message = error_message
        self.ended_at = utc_now_iso()


@dataclass
class DataQualityScore:
    business_id: Optional[int]
    duplicate_score: float
    freshness_score: float
    contact_validity_score: float
    foreigner_relevance_score: float
    total_score: float
    calculated_at: str = field(default_factory=utc_now_iso)
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
