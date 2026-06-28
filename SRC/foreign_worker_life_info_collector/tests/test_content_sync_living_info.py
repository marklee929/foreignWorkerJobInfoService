from __future__ import annotations

from typing import Any

from foreign_worker_life_info_collector.content.service import ContentService


class FakeContentRepository:
    def __init__(self) -> None:
        self.payloads: list[dict[str, Any]] = []

    def upsert_candidate(self, payload: dict[str, Any]) -> int:
        self.payloads.append(payload)
        return len(self.payloads)


class FakeLivingInfoService:
    def __init__(self, *, payload_ready: bool = True) -> None:
        self.payload_ready = payload_ready
        self.evidence_requests: list[int] = []

    def list_ready_topic_clusters(self, limit: int = 100) -> list[dict[str, Any]]:
        return [
            {
                "id": 77,
                "topic_key": "healthcare:insurance-check",
                "primary_category": "HEALTHCARE",
                "readiness_score": 82,
                "public_candidate_ready_yn": "Y",
                "validation_status": "VALIDATED",
                "cluster_status": "READY",
                "source_count": 1,
                "evidence_count": 1,
            }
        ][:limit]

    def topic_cluster_evidence(self, topic_cluster_id: int) -> list[dict[str, Any]]:
        self.evidence_requests.append(topic_cluster_id)
        return [
            {
                "source_item_id": 501,
                "source_url": "https://www.nhis.or.kr/guide",
                "publishable_link_url": "https://www.nhis.or.kr/guide",
                "source_name": "NHIS",
            }
        ]

    def topic_cluster_to_content_candidate_payload(self, cluster: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
        if not self.payload_ready:
            return {"ready": False, "skip_reason": "missing_publishable_evidence_url"}
        return {
            "ready": True,
            "source_domain": "LIVING_INFO",
            "content_type": "LIVING_GUIDE",
            "priority_group": "LIVING_INFO",
            "category": "healthcare",
            "title": "Healthcare checklist for foreign residents in Korea",
            "summary_en": "Check insurance status.",
            "why_it_matters_en": "This affects clinic visits.",
            "body_en": "- Check the source.",
            "source_url": "https://www.nhis.or.kr/guide",
            "source_name": "NHIS",
            "link_url": "https://www.nhis.or.kr/guide",
            "hashtags": "#LivingInKorea",
            "language": "en",
            "quality_score": 82,
            "relevance_score": 82,
            "practical_value_score": 80,
            "urgency_score": 0,
            "freshness_score": 0,
            "source_reliability_score": 95,
            "content_potential_score": 82,
            "rotation_score": 0,
            "final_publish_score": 82,
            "sensitive_yn": False,
            "review_required_yn": True,
            "review_reason": "living_info topic cluster requires operator review before public content",
            "status": "READY_TO_REVIEW",
            "published_at": "",
            "facebook_post_id": "",
            "facebook_post_url": "",
            "raw_ref_table": "living_info.topic_cluster",
            "raw_ref_id": cluster["id"],
            "raw_payload": {"topic_cluster": cluster, "evidence_source_item_ids": [501]},
        }


def test_sync_living_info_creates_ready_to_review_content_candidate() -> None:
    repository = FakeContentRepository()
    living_info_service = FakeLivingInfoService()
    service = ContentService(repository=repository, living_info_service=living_info_service)

    result = service.sync_living_info(limit=10)

    assert result["source"] == "living_info.topic_cluster"
    assert result["seen_count"] == 1
    assert result["synced_count"] == 1
    assert result["skipped_count"] == 0
    assert living_info_service.evidence_requests == [77]
    assert repository.payloads[0]["raw_ref_table"] == "living_info.topic_cluster"
    assert repository.payloads[0]["source_domain"] == "LIVING_INFO"
    assert repository.payloads[0]["content_type"] == "LIVING_GUIDE"
    assert repository.payloads[0]["status"] == "READY_TO_REVIEW"
    assert "ready" not in repository.payloads[0]


def test_sync_living_info_skips_unready_payload_without_content_candidate() -> None:
    repository = FakeContentRepository()
    service = ContentService(repository=repository, living_info_service=FakeLivingInfoService(payload_ready=False))

    result = service.sync_living_info(limit=10)

    assert result["synced_count"] == 0
    assert result["skipped_count"] == 1
    assert result["skipped_reasons"] == {"missing_publishable_evidence_url": 1}
    assert repository.payloads == []
