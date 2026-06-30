from __future__ import annotations

from foreign_worker_life_info_collector.living_info.service import (
    LivingInfoService,
    build_topic_clusters,
    normalize_category,
    social_news_payload_to_normalized_item,
    social_news_payload_to_source_item,
    topic_cluster_to_content_candidate_payload,
    usable_source_url,
)


class FakeRepository:
    def __init__(self) -> None:
        self.source_items = []
        self.normalized_items = []
        self.cluster_items = []

    def upsert_source_item(self, item):
        self.source_items.append(item)
        return 101

    def upsert_normalized_item(self, item):
        self.normalized_items.append(item)
        return 202

    def list_normalized_items_for_clustering(self, limit=100):
        return sample_normalized_cluster_items()[:limit]

    def upsert_topic_cluster(self, cluster):
        self.source_items.append(cluster)
        return 303

    def upsert_topic_cluster_item_normalized(self, **payload):
        self.cluster_items.append(payload)
        return len(self.cluster_items)


def sample_living_payload() -> dict:
    return {
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "priority_group": "SECONDARY",
        "category": "healthcare",
        "title": "Health insurance checks for foreign residents",
        "summary_en": "Foreign residents should check NHIS payment and clinic coverage.",
        "body_en": "Keep receipts and confirm payment status before deadlines.",
        "link_url": "https://www.nhis.or.kr/guide",
        "source_url": "https://www.nhis.or.kr/guide",
        "source_name": "NHIS",
        "language": "en",
        "quality_score": 72,
        "practical_value_score": 81,
        "source_reliability_score": 90,
        "raw_ref_table": "social_news.candidate",
        "raw_ref_id": 109268,
    }


def test_usable_source_url_requires_http_url() -> None:
    assert usable_source_url({"link_url": "-"}) == ""
    assert usable_source_url({"source_url": "https://example.com/item"}) == "https://example.com/item"


def test_category_mapping_keeps_living_domain_terms() -> None:
    assert normalize_category("healthcare") == ("HEALTHCARE", "healthcare")
    assert normalize_category("banking") == ("BANKING_FINANCE", "banking")
    assert normalize_category("unknown living topic") == ("DAILY_LIFE", "unknown_living_topic")


def test_social_news_payload_maps_to_living_source_and_normalized_items() -> None:
    payload = sample_living_payload()

    source_item = social_news_payload_to_source_item(payload)
    normalized_item = social_news_payload_to_normalized_item(payload)

    assert source_item.source_url == "https://www.nhis.or.kr/guide"
    assert source_item.source_type == "SOCIAL_NEWS"
    assert source_item.source_trust_level == "PRIMARY"
    assert source_item.raw_ref_table == "social_news.candidate"
    assert source_item.raw_ref_id == 109268
    assert normalized_item.normalized_primary_category == "HEALTHCARE"
    assert normalized_item.source_usage == "TOPIC_CLUSTER_MATERIAL"
    assert normalized_item.status == "NORMALIZED"


def test_ingest_from_social_news_candidate_uses_repository() -> None:
    repository = FakeRepository()
    service = LivingInfoService(repository=repository)

    result = service.ingest_from_social_news_candidate(sample_living_payload())

    assert result["ok"] is True
    assert result["status"] == "INGESTED"
    assert result["source_item_id"] == 101
    assert result["normalized_item_id"] == 202
    assert repository.normalized_items[0].source_item_id == 101


def test_ingest_skips_missing_source_url() -> None:
    result = LivingInfoService(repository=FakeRepository()).ingest_from_social_news_candidate(
        {
            "title": "Missing URL",
            "source_domain": "LIVING_INFO",
            "raw_ref_table": "social_news.candidate",
            "raw_ref_id": 1,
        }
    )

    assert result["ok"] is False
    assert result["status"] == "SKIPPED_SOURCE_INVALID"


def sample_ready_topic_cluster() -> dict:
    return {
        "id": 77,
        "topic_key": "healthcare:insurance-check",
        "primary_category": "HEALTHCARE",
        "secondary_category": "insurance",
        "target_user": "FOREIGN_RESIDENTS_IN_KOREA",
        "action_type": "PRACTICAL_CHECK",
        "source_count": 2,
        "evidence_count": 1,
        "community_signal_count": 3,
        "official_source_count": 1,
        "secondary_source_count": 1,
        "source_spread_count": 2,
        "readiness_score": 82,
        "public_candidate_ready_yn": "Y",
        "validation_status": "VALIDATED",
        "cluster_status": "READY",
    }


def sample_topic_evidence() -> list[dict]:
    return [
        {
            "source_item_id": 501,
            "normalized_item_id": 601,
            "source_url": "https://www.nhis.or.kr/guide",
            "canonical_url": "https://www.nhis.or.kr/guide",
            "publishable_link_url": "https://www.nhis.or.kr/guide",
            "source_name": "NHIS",
            "source_trust_level": "PRIMARY",
            "raw_title": "Health insurance guide",
            "raw_summary": "Foreign residents should confirm health insurance status before clinic visits.",
            "actionability_score": 80,
            "source_reliability_score": 95,
            "weight_score": 1,
        }
    ]


def sample_normalized_cluster_items() -> list[dict]:
    return [
        {
            "normalized_item_id": 601,
            "source_item_id": 501,
            "normalized_primary_category": "HEALTHCARE",
            "normalized_secondary_category": "insurance",
            "source_usage": "TOPIC_CLUSTER_MATERIAL",
            "info_signal_type": "INFORMATIONAL",
            "target_user": "FOREIGN_RESIDENTS_IN_KOREA",
            "action_type": "PRACTICAL_CHECK",
            "topic_key_candidate": "healthcare:insurance-check",
            "actionability_score": 80,
            "repeatability_score": 90,
            "source_reliability_score": 95,
            "normalization_confidence": 88,
            "status": "NORMALIZED",
            "source_url": "https://www.nhis.or.kr/guide",
            "canonical_url": "https://www.nhis.or.kr/guide",
            "publishable_link_url": "https://www.nhis.or.kr/guide",
            "source_name": "NHIS",
            "source_type": "OFFICIAL",
            "source_trust_level": "PRIMARY",
            "raw_title": "Health insurance guide",
            "raw_summary": "Foreign residents should confirm health insurance status before clinic visits.",
            "published_at": "2026-06-28T00:00:00+00:00",
            "collected_at": "2026-06-28T01:00:00+00:00",
        },
        {
            "normalized_item_id": 602,
            "source_item_id": 502,
            "normalized_primary_category": "HEALTHCARE",
            "normalized_secondary_category": "insurance",
            "source_usage": "SOURCE_EVIDENCE",
            "info_signal_type": "INFORMATIONAL",
            "target_user": "FOREIGN_RESIDENTS_IN_KOREA",
            "action_type": "PRACTICAL_CHECK",
            "topic_key_candidate": "healthcare:insurance-check",
            "actionability_score": 70,
            "repeatability_score": 85,
            "source_reliability_score": 80,
            "normalization_confidence": 75,
            "status": "NORMALIZED",
            "source_url": "https://www.koreaherald.com/guide",
            "canonical_url": "https://www.koreaherald.com/guide",
            "publishable_link_url": "https://www.koreaherald.com/guide",
            "source_name": "The Korea Herald",
            "source_type": "MEDIA",
            "source_trust_level": "TRUSTED_MEDIA",
            "raw_title": "Health insurance reminder",
            "raw_summary": "A trusted media explainer.",
            "published_at": "2026-06-27T00:00:00+00:00",
            "collected_at": "2026-06-27T01:00:00+00:00",
        },
    ]


def test_build_topic_clusters_uses_source_evidence_only() -> None:
    plans = build_topic_clusters(sample_normalized_cluster_items())

    assert len(plans) == 1
    cluster = plans[0]["cluster"]
    assert cluster.topic_key == "healthcare:insurance-check"
    assert cluster.evidence_count == 2
    assert cluster.community_signal_count == 0
    assert cluster.official_source_count == 1
    assert cluster.secondary_source_count == 1
    assert cluster.source_spread_count == 2
    assert cluster.validation_status == "VALIDATED"
    assert cluster.public_candidate_ready_yn == "Y"
    assert plans[0]["items"][0]["item_role"] == "REPRESENTATIVE"


def test_prepare_topic_clusters_dry_run_does_not_write() -> None:
    repository = FakeRepository()
    result = LivingInfoService(repository=repository).prepare_topic_clusters(limit=10, dry_run=True)

    assert result["dry_run"] is True
    assert result["seen_count"] == 2
    assert result["cluster_count"] == 1
    assert result["written_count"] == 0
    assert repository.cluster_items == []


def test_prepare_topic_clusters_execute_writes_cluster_and_links() -> None:
    repository = FakeRepository()
    result = LivingInfoService(repository=repository).prepare_topic_clusters(limit=10, dry_run=False)

    assert result["dry_run"] is False
    assert result["written_count"] == 1
    assert result["clusters"][0]["topic_cluster_id"] == 303
    assert [item["normalized_item_id"] for item in repository.cluster_items] == [601, 602]


def test_topic_cluster_payload_creates_ready_to_review_content_candidate() -> None:
    payload = topic_cluster_to_content_candidate_payload(sample_ready_topic_cluster(), sample_topic_evidence())

    assert payload["ready"] is True
    assert payload["source_domain"] == "LIVING_INFO"
    assert payload["content_type"] == "LIVING_GUIDE"
    assert payload["raw_ref_table"] == "living_info.topic_cluster"
    assert payload["raw_ref_id"] == 77
    assert payload["status"] == "READY_TO_REVIEW"
    assert payload["review_required_yn"] is True
    assert payload["link_url"] == "https://www.nhis.or.kr/guide"
    assert payload["raw_payload"]["representative_source_item_id"] == 501


def test_topic_cluster_payload_blocks_community_only_cluster() -> None:
    cluster = sample_ready_topic_cluster()
    cluster["source_count"] = 1
    cluster["evidence_count"] = 0
    cluster["official_source_count"] = 0
    cluster["secondary_source_count"] = 0
    cluster["community_signal_count"] = 5

    payload = topic_cluster_to_content_candidate_payload(cluster, [])

    assert payload["ready"] is False
    assert payload["skip_reason"] == "missing_source_evidence"
