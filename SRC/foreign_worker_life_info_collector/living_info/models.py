"""Models for living information source evidence and normalized items."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LivingSourceItem:
    id: int | None = None
    source_url: str = ""
    canonical_url: str = ""
    publishable_link_url: str = ""
    source_name: str = ""
    source_type: str = "DISCOVERY"
    source_access_policy: str = "PUBLIC_PAGE"
    language: str = "en"
    country: str = "Korea"
    region_in_korea: str = ""
    raw_title: str = ""
    raw_summary: str = ""
    raw_body: str = ""
    published_at: str = ""
    collected_at: str = ""
    last_checked_at: str = ""
    source_trust_level: str = "DISCOVERY"
    privacy_risk_level: str = "LOW"
    duplicate_key: str = ""
    content_hash: str = ""
    source_status: str = "COLLECTED"
    active_yn: str = "Y"
    raw_ref_table: str = ""
    raw_ref_id: int | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class LivingNormalizedItem:
    id: int | None = None
    source_item_id: int | None = None
    normalized_primary_category: str = ""
    normalized_secondary_category: str = ""
    source_usage: str = "SOURCE_EVIDENCE"
    info_signal_type: str = "INFORMATIONAL"
    target_user: str = "FOREIGN_RESIDENTS_IN_KOREA"
    action_type: str = ""
    topic_key_candidate: str = ""
    validation_needed_yn: str = "Y"
    validation_source_type: str = ""
    actionability_score: float = 0.0
    repeatability_score: float = 0.0
    source_reliability_score: float = 0.0
    normalization_confidence: float = 0.0
    normalization_reason: str = ""
    status: str = "NORMALIZED"


@dataclass
class LivingSourceSignal:
    id: int | None = None
    signal_source_name: str = ""
    signal_source_url: str = ""
    signal_platform: str = ""
    signal_type: str = "TREND_SIGNAL"
    language: str = ""
    country: str = "Korea"
    region_in_korea: str = ""
    primary_category: str = ""
    topic_key_candidate: str = ""
    target_user: str = "FOREIGN_RESIDENTS_IN_KOREA"
    pain_point_summary: str = ""
    signal_count: int = 1
    privacy_risk_level: str = "MEDIUM"
    source_access_policy: str = "PUBLIC_METADATA_ONLY"
    validation_needed_yn: str = "Y"
    status: str = "SIGNAL_COLLECTED"
    observed_at: str = ""
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class LivingTopicCluster:
    id: int | None = None
    topic_key: str = ""
    primary_category: str = ""
    secondary_category: str = ""
    target_user: str = "FOREIGN_RESIDENTS_IN_KOREA"
    action_type: str = ""
    source_count: int = 0
    evidence_count: int = 0
    community_signal_count: int = 0
    official_source_count: int = 0
    secondary_source_count: int = 0
    source_spread_count: int = 0
    readiness_score: float = 0.0
    public_candidate_ready_yn: str = "N"
    validation_status: str = "PENDING"
    cluster_status: str = "OPEN"
    last_signal_at: str = ""
    last_evidence_at: str = ""
