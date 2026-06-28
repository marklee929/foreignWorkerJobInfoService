"""Service helpers for living information ingestion."""

from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import urlsplit

from .models import LivingNormalizedItem, LivingSourceItem
from .repository import LivingInfoRepository


class LivingInfoService:
    def __init__(self, repository: LivingInfoRepository | None = None) -> None:
        self.repository = repository or LivingInfoRepository()

    def list_ready_topic_clusters(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.repository.list_ready_topic_clusters(limit=limit)

    def topic_cluster_evidence(self, topic_cluster_id: int, limit: int = 10) -> list[dict[str, Any]]:
        return self.repository.topic_cluster_evidence(topic_cluster_id=topic_cluster_id, limit=limit)

    def ingest_from_social_news_candidate(self, payload: dict[str, Any]) -> dict[str, Any]:
        source_url = usable_source_url(payload)
        if not source_url:
            return {
                "ok": False,
                "status": "SKIPPED_SOURCE_INVALID",
                "reason": "source_url/link_url/original_source_url is missing",
                "raw_ref_table": payload.get("raw_ref_table", ""),
                "raw_ref_id": payload.get("raw_ref_id"),
            }
        source_item = social_news_payload_to_source_item(payload, source_url)
        source_item_id = self.repository.upsert_source_item(source_item)
        normalized = social_news_payload_to_normalized_item(payload)
        normalized.source_item_id = source_item_id
        normalized_item_id = self.repository.upsert_normalized_item(normalized)
        return {
            "ok": True,
            "status": "INGESTED",
            "source_item_id": source_item_id,
            "normalized_item_id": normalized_item_id,
            "raw_ref_table": payload.get("raw_ref_table", ""),
            "raw_ref_id": payload.get("raw_ref_id"),
        }

    def topic_cluster_to_content_candidate_payload(self, cluster: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
        return topic_cluster_to_content_candidate_payload(cluster, evidence)


def social_news_payload_to_source_item(payload: dict[str, Any], source_url: str | None = None) -> LivingSourceItem:
    source_url = source_url or usable_source_url(payload)
    return LivingSourceItem(
        source_url=source_url,
        canonical_url=str(payload.get("original_source_url") or payload.get("source_url") or source_url),
        publishable_link_url=str(payload.get("link_url") or source_url),
        source_name=str(payload.get("source_name") or payload.get("original_source_name") or ""),
        source_type="SOCIAL_NEWS",
        language=str(payload.get("language") or "en"),
        raw_title=str(payload.get("original_title") or payload.get("title") or ""),
        raw_summary=str(payload.get("summary_en") or ""),
        raw_body=str(payload.get("body_en") or ""),
        published_at=str(payload.get("original_published_at") or ""),
        collected_at=str(payload.get("original_collected_at") or ""),
        source_trust_level=source_trust_level(payload),
        privacy_risk_level="LOW",
        duplicate_key=duplicate_key(payload, source_url),
        content_hash=content_hash(payload),
        source_status="COLLECTED",
        active_yn="Y",
        raw_ref_table=str(payload.get("raw_ref_table") or "social_news.candidate"),
        raw_ref_id=int(payload.get("raw_ref_id") or 0),
        raw_payload={"source": "content.sync.social_news", "content_payload": payload},
    )


def social_news_payload_to_normalized_item(payload: dict[str, Any]) -> LivingNormalizedItem:
    primary, secondary = normalize_category(str(payload.get("category") or ""))
    score = max(to_float(payload.get("final_publish_score")), to_float(payload.get("quality_score")))
    return LivingNormalizedItem(
        normalized_primary_category=primary,
        normalized_secondary_category=secondary,
        source_usage="TOPIC_CLUSTER_MATERIAL" if score >= 40 else "SOURCE_EVIDENCE",
        info_signal_type="NEWS_EVENT",
        target_user="FOREIGN_RESIDENTS_IN_KOREA",
        action_type=action_type(primary),
        topic_key_candidate=topic_key(primary, str(payload.get("title") or "")),
        validation_needed_yn="Y",
        validation_source_type=source_trust_level(payload),
        actionability_score=to_float(payload.get("practical_value_score")),
        repeatability_score=repeatability_score(primary),
        source_reliability_score=to_float(payload.get("source_reliability_score")),
        normalization_confidence=min(100.0, max(40.0, score)),
        normalization_reason=f"ingested_from_social_news; source_domain={payload.get('source_domain')}; category={payload.get('category')}",
        status="NORMALIZED",
    )


def topic_cluster_to_content_candidate_payload(cluster: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    ready, reason = topic_cluster_review_ready(cluster, evidence)
    if not ready:
        return {"ready": False, "skip_reason": reason, "topic_cluster_id": cluster.get("id")}
    representative = representative_evidence(evidence)
    category = str(cluster.get("primary_category") or representative.get("normalized_primary_category") or "DAILY_LIFE")
    source_url = usable_evidence_url(representative)
    readiness_score = to_float(cluster.get("readiness_score"))
    source_reliability_score = max(to_float(item.get("source_reliability_score")) for item in evidence) if evidence else 0.0
    practical_score = max(to_float(item.get("actionability_score")) for item in evidence) if evidence else 0.0
    title = guide_title(category)
    summary = guide_summary(cluster, representative)
    body = guide_body(cluster, representative)
    return {
        "ready": True,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "priority_group": "LIVING_INFO",
        "category": category.lower(),
        "title": title,
        "summary_en": summary,
        "why_it_matters_en": (
            "This topic can affect daily life, paperwork, payments, housing, healthcare, "
            "or local support for foreign residents in Korea."
        ),
        "body_en": body,
        "source_url": source_url,
        "source_name": str(representative.get("source_name") or "WorkConnect source evidence"),
        "original_source_url": source_url,
        "original_source_name": str(representative.get("source_name") or ""),
        "original_title": str(representative.get("raw_title") or title),
        "original_published_at": str(representative.get("published_at") or ""),
        "original_collected_at": str(representative.get("collected_at") or ""),
        "image_url": "",
        "link_url": source_url,
        "hashtags": "#LivingInKorea #ForeignersInKorea #KoreaLife #WorkConnectKorea",
        "language": "en",
        "quality_score": readiness_score,
        "relevance_score": readiness_score,
        "practical_value_score": practical_score,
        "urgency_score": 0,
        "freshness_score": 0,
        "source_reliability_score": source_reliability_score,
        "content_potential_score": readiness_score,
        "rotation_score": 0,
        "final_publish_score": readiness_score,
        "sensitive_yn": False,
        "review_required_yn": True,
        "review_reason": "living_info topic cluster requires operator review before public content",
        "status": "READY_TO_REVIEW",
        "published_at": "",
        "facebook_post_id": "",
        "facebook_post_url": "",
        "raw_ref_table": "living_info.topic_cluster",
        "raw_ref_id": int(cluster.get("id") or 0),
        "raw_payload": {
            "source": "living_info.topic_cluster",
            "topic_cluster": cluster,
            "representative_source_item_id": representative.get("source_item_id"),
            "evidence_source_item_ids": [item.get("source_item_id") for item in evidence],
            "evidence_count": len(evidence),
        },
    }


def topic_cluster_review_ready(cluster: dict[str, Any], evidence: list[dict[str, Any]]) -> tuple[bool, str]:
    if str(cluster.get("public_candidate_ready_yn") or "").upper() != "Y":
        return False, "public_candidate_ready_yn_not_y"
    if str(cluster.get("validation_status") or "").upper() not in {"VALIDATED", "READY"}:
        return False, "validation_status_not_ready"
    if str(cluster.get("cluster_status") or "").upper() not in {"OPEN", "READY"}:
        return False, "cluster_status_not_open_or_ready"
    if to_float(cluster.get("readiness_score")) < 60:
        return False, "readiness_score_below_threshold"
    if int(cluster.get("evidence_count") or 0) < 1 or int(cluster.get("source_count") or 0) < 1:
        return False, "missing_source_evidence"
    if not evidence:
        return False, "missing_normalized_evidence"
    if int(cluster.get("community_signal_count") or 0) > 0 and int(cluster.get("evidence_count") or 0) == 0:
        return False, "community_signal_only"
    if not usable_evidence_url(representative_evidence(evidence)):
        return False, "missing_publishable_evidence_url"
    return True, "ready"


def representative_evidence(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    if not evidence:
        return {}
    return sorted(
        evidence,
        key=lambda item: (
            trust_rank(str(item.get("source_trust_level") or "")),
            -to_float(item.get("weight_score")),
            -to_float(item.get("source_reliability_score")),
        ),
    )[0]


def trust_rank(value: str) -> int:
    return {
        "PRIMARY": 0,
        "OFFICIAL": 1,
        "TRUSTED_MEDIA": 2,
        "SECONDARY": 3,
        "DISCOVERY": 4,
    }.get(value.upper(), 9)


def usable_evidence_url(evidence: dict[str, Any]) -> str:
    for key in ("publishable_link_url", "canonical_url", "source_url"):
        value = str(evidence.get(key) or "").strip()
        if valid_url(value):
            return value
    return ""


def guide_title(category: str) -> str:
    label = category_label(category)
    return f"{label} checklist for foreign residents in Korea"


def guide_summary(cluster: dict[str, Any], evidence: dict[str, Any]) -> str:
    summary = compact_text(str(evidence.get("raw_summary") or ""))
    if summary:
        return summary[:500]
    label = category_label(str(cluster.get("primary_category") or "DAILY_LIFE")).lower()
    return f"Check source-backed {label} information before making daily life decisions in Korea."


def guide_body(cluster: dict[str, Any], evidence: dict[str, Any]) -> str:
    title = compact_text(str(evidence.get("raw_title") or "the source notice"))
    source_name = compact_text(str(evidence.get("source_name") or "the original source"))
    return "\n".join(
        [
            f"- Review {title[:140]} from {source_name[:120]}.",
            "- Confirm whether the guidance applies to your visa, city, household, school, job, or insurance status.",
            "- Recheck the source before taking action because local support rules and deadlines can change.",
        ]
    )


def category_label(category: str) -> str:
    token = re.sub(r"[^A-Z0-9_]+", "_", category.strip().upper()).strip("_")
    labels = {
        "HOUSING": "Housing",
        "HEALTHCARE": "Healthcare",
        "BANKING_FINANCE": "Banking and finance",
        "TELECOM": "Telecom",
        "TELECOM_DIGITAL_ID": "Telecom and digital ID",
        "TRANSPORTATION": "Transportation",
        "PUBLIC_SERVICES": "Public services",
        "LEGAL_AID": "Legal aid",
        "EDUCATION_LANGUAGE": "Education and language",
        "FAMILY_CHILDCARE": "Family and childcare",
        "SAFETY_SCAM": "Safety and scam prevention",
        "REGIONAL_SUPPORT": "Regional support",
        "DAILY_LIFE": "Daily life",
    }
    return labels.get(token, "Daily life")


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def usable_source_url(payload: dict[str, Any]) -> str:
    for key in ("link_url", "source_url", "original_source_url"):
        value = str(payload.get(key) or "").strip()
        if valid_url(value):
            return value
    return ""


def valid_url(value: str) -> bool:
    if not value or value == "-":
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def source_trust_level(payload: dict[str, Any]) -> str:
    text = " ".join(
        str(payload.get(key) or "").lower()
        for key in ("source_name", "original_source_name", "source_url", "link_url")
    )
    if any(term in text for term in ("go.kr", "hikorea", "moel", "moj", "nhis", "ministry")):
        return "PRIMARY"
    if any(term in text for term in ("korea times", "korea herald", "yonhap", "joongang", "chosun")):
        return "TRUSTED_MEDIA"
    return "DISCOVERY"


def normalize_category(category: str) -> tuple[str, str]:
    token = re.sub(r"[^a-z0-9_]+", "_", category.strip().lower()).strip("_")
    mapping = {
        "housing": ("HOUSING", "housing"),
        "banking": ("BANKING_FINANCE", "banking"),
        "finance": ("BANKING_FINANCE", "finance"),
        "healthcare": ("HEALTHCARE", "healthcare"),
        "insurance": ("HEALTHCARE", "insurance"),
        "transportation": ("TRANSPORTATION", "transportation"),
        "telecom": ("TELECOM", "telecom"),
        "education": ("EDUCATION_LANGUAGE", "education"),
        "korean_language": ("EDUCATION_LANGUAGE", "korean_language"),
        "local_community": ("REGIONAL_SUPPORT", "local_community"),
        "settlement_life": ("DAILY_LIFE", "settlement_life"),
        "safety": ("SAFETY_SCAM", "safety"),
    }
    return mapping.get(token, ("DAILY_LIFE", token or "living"))


def action_type(primary: str) -> str:
    return {
        "HOUSING": "CONTRACT_CHECK",
        "BANKING_FINANCE": "PAYMENT_CHECK",
        "HEALTHCARE": "PRACTICAL_CHECK",
        "TRANSPORTATION": "PRACTICAL_CHECK",
        "TELECOM": "PRACTICAL_CHECK",
        "EDUCATION_LANGUAGE": "INFORMATION_REVIEW",
        "REGIONAL_SUPPORT": "SUPPORT_LOOKUP",
        "SAFETY_SCAM": "SAFETY_CHECK",
    }.get(primary, "INFORMATION_REVIEW")


def repeatability_score(primary: str) -> float:
    return 80.0 if primary in {"HOUSING", "BANKING_FINANCE", "HEALTHCARE", "TRANSPORTATION", "TELECOM", "EDUCATION_LANGUAGE", "REGIONAL_SUPPORT", "DAILY_LIFE"} else 40.0


def topic_key(primary: str, title: str) -> str:
    words = re.findall(r"[a-z0-9]+", title.lower())
    useful = [word for word in words if len(word) > 3 and word not in {"korea", "korean", "foreign", "residents"}]
    return f"{primary.lower()}:" + "-".join(useful[:6])


def duplicate_key(payload: dict[str, Any], source_url: str) -> str:
    raw_ref_table = str(payload.get("raw_ref_table") or "")
    raw_ref_id = str(payload.get("raw_ref_id") or "")
    if raw_ref_table and raw_ref_id:
        return f"{raw_ref_table}:{raw_ref_id}"
    return "url:" + hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:24]


def content_hash(payload: dict[str, Any]) -> str:
    value = "|".join(str(payload.get(key) or "") for key in ("title", "summary_en", "body_en", "link_url"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def to_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
