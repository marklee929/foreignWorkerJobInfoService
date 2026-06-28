from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from foreign_worker_life_info_collector.content.service import ContentService


class FakeContentRepository:
    def __init__(self) -> None:
        self.payloads: list[dict[str, Any]] = []

    def upsert_candidate(self, payload: dict[str, Any]) -> int:
        self.payloads.append(payload)
        return len(self.payloads)

    def archive_non_representative_social_news(self) -> int:
        return 0


class FakeLivingInfoService:
    def __init__(self) -> None:
        self.payloads: list[dict[str, Any]] = []

    def ingest_from_social_news_candidate(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return {"ok": True, "status": "INGESTED", "source_item_id": 10, "normalized_item_id": 20}


def social_news_row(
    *,
    row_id: int = 1,
    title: str = "Foreign worker support notice",
    source_url: str = "https://example.com/article",
    content_category: str = "foreign_jobs",
    priority_group: str = "PRIMARY",
    score: float = 70.0,
) -> tuple[Any, ...]:
    collected_at = datetime(2026, 6, 28, tzinfo=timezone.utc)
    return (
        row_id,
        title,
        "",
        "Short summary",
        "Summary",
        "Generated summary",
        "Generated why it matters",
        "Relevant to foreign workers in Korea",
        "Article body with enough useful information for WorkConnect.",
        source_url,
        source_url,
        "",
        "Example Publisher",
        "Example Source",
        "",
        content_category,
        content_category,
        priority_group,
        80.0,
        score,
        10.0,
        "test category",
        False,
        "",
        "en",
        score,
        90.0,
        90.0,
        80.0,
        80.0,
        80.0,
        "LOW",
        "READY_TO_PUBLISH",
        "READY_TO_PUBLISH",
        collected_at,
        None,
        "",
        "",
        None,
        None,
        True,
    )


def test_sync_social_news_keeps_non_living_rows_on_content_candidate_path() -> None:
    repository = FakeContentRepository()
    living_info_service = FakeLivingInfoService()
    service = ContentService(repository=repository, living_info_service=living_info_service)

    result = service._sync_social_news_rows(
        [
            social_news_row(
                row_id=11,
                title="New support for foreign workers in Korea",
                content_category="foreign_jobs",
                priority_group="PRIMARY",
            )
        ]
    )

    assert result["synced_count"] == 1
    assert result["content_candidate_synced_count"] == 1
    assert result["living_info_ingested_count"] == 0
    assert repository.payloads[0]["source_domain"] == "SOCIAL_NEWS"
    assert repository.payloads[0]["content_type"] == "NEWS_ARTICLE"
    assert living_info_service.payloads == []


def test_sync_social_news_routes_living_rows_to_living_info_only() -> None:
    repository = FakeContentRepository()
    living_info_service = FakeLivingInfoService()
    service = ContentService(repository=repository, living_info_service=living_info_service)

    result = service._sync_social_news_rows(
        [
            social_news_row(
                row_id=22,
                title="Health insurance checks for foreign residents",
                source_url="https://www.nhis.or.kr/guide",
                content_category="healthcare",
                priority_group="SECONDARY",
            )
        ]
    )

    assert result["synced_count"] == 1
    assert result["content_candidate_synced_count"] == 0
    assert result["living_info_ingested_count"] == 1
    assert repository.payloads == []
    assert living_info_service.payloads[0]["source_domain"] == "LIVING_INFO"
    assert living_info_service.payloads[0]["content_type"] == "LIVING_GUIDE"
    assert living_info_service.payloads[0]["raw_ref_table"] == "social_news.candidate"
    assert living_info_service.payloads[0]["raw_ref_id"] == 22


def test_sync_social_news_counts_living_ingest_skip_without_content_candidate() -> None:
    repository = FakeContentRepository()

    class SkippingLivingInfoService(FakeLivingInfoService):
        def ingest_from_social_news_candidate(self, payload: dict[str, Any]) -> dict[str, Any]:
            self.payloads.append(payload)
            return {"ok": False, "status": "SKIPPED_SOURCE_INVALID"}

    living_info_service = SkippingLivingInfoService()
    service = ContentService(repository=repository, living_info_service=living_info_service)

    result = service._sync_social_news_rows(
        [
            social_news_row(
                row_id=33,
                title="Housing guide with missing usable source",
                source_url="-",
                content_category="housing",
                priority_group="SECONDARY",
            )
        ]
    )

    assert result["synced_count"] == 0
    assert result["content_candidate_synced_count"] == 0
    assert result["living_info_ingested_count"] == 0
    assert result["living_info_skipped_count"] == 1
    assert repository.payloads == []
