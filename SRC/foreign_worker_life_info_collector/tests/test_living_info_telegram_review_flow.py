from __future__ import annotations

from typing import Any

from foreign_worker_life_info_collector.content.service import ContentService


def living_candidate(**overrides: Any) -> dict[str, Any]:
    candidate = {
        "id": 501,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "priority_group": "LIVING_INFO",
        "category": "healthcare",
        "status": "READY_TO_REVIEW",
        "title": "Health insurance checklist for foreign residents in Korea",
        "summary_en": "Foreign residents in Korea should check NHIS payment status before clinic visits.",
        "why_it_matters_en": "This helps avoid unpaid bills, clinic issues, and deadline problems.",
        "body_en": "- Check your NHIS payment status.\n- Keep receipts.\n- Ask NHIS before renewal deadlines.",
        "review_reason": "living_info topic cluster requires operator review before public content",
        "link_url": "https://www.nhis.or.kr/guide",
        "source_url": "https://www.nhis.or.kr/guide",
        "source_name": "NHIS",
        "final_publish_score": 82,
        "quality_score": 82,
        "raw_payload": {"source": "living_info.topic_cluster"},
    }
    candidate.update(overrides)
    return candidate


class FakeReviewTargetRepository:
    def list_review_targets(self, limit: int = 5) -> list[dict[str, Any]]:
        return [
            living_candidate(),
            living_candidate(id=502, source_domain="SOCIAL_NEWS", content_type="NEWS_ARTICLE"),
        ][:limit]


class FakeTelegramContentService:
    def requires_telegram_review(self, candidate: dict[str, Any]) -> bool:
        return True

    def telegram_review_card_preview(self, candidate: dict[str, Any]) -> dict[str, Any]:
        return {"ok": False, "card_required": False, "status": "NOT_REQUIRED", "reason": ""}

    def telegram_review_message(self, candidate: dict[str, Any], card_preview: dict[str, Any] | None = None) -> str:
        return (
            "[Content Review]\n"
            f"ID: {candidate.get('id')}\n"
            "Source: LIVING_INFO / LIVING_GUIDE / NHIS\n"
            "Score: 82.0\n"
            "Preview image: not required.\n"
            "Operator scoring only. This does not publish to Facebook."
        )

    def telegram_review_metadata(self, candidate: dict[str, Any], message: str) -> dict[str, Any]:
        return {
            "telegram_review_key": "candidate-501-ready-60-79-message",
            "semantic_review_key": "living-info-nhis-guide-ready-60-79-message",
            "content_candidate_id": int(candidate["id"]),
            "source_domain": "LIVING_INFO",
            "content_type": "LIVING_GUIDE",
            "status": candidate["status"],
            "score_bucket": "60-79",
            "message_preview": message[:500],
        }


class FakeTelegramRepository:
    def __init__(self, duplicate: dict[str, Any] | None = None) -> None:
        self.duplicate = duplicate or {}
        self.records: list[dict[str, Any]] = []

    def find_duplicate_telegram_review(self, review_metadata: dict[str, Any]) -> dict[str, Any]:
        return self.duplicate

    def record_telegram_review(
        self,
        candidate_id: int,
        status: str,
        dry_run: bool,
        message: str,
        response: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        self.records.append(
            {
                "candidate_id": candidate_id,
                "status": status,
                "dry_run": dry_run,
                "message": message,
                "response": response or {},
                "metadata": metadata or {},
            }
        )
        return len(self.records)


def test_living_info_candidate_appears_as_review_target() -> None:
    targets = ContentService(repository=FakeReviewTargetRepository()).review_targets(limit=5)

    assert len(targets) == 1
    assert targets[0]["source_domain"] == "LIVING_INFO"
    assert targets[0]["status"] == "READY_TO_REVIEW"


def test_living_info_telegram_review_dry_run_records_log_without_real_send(monkeypatch) -> None:
    from foreign_worker_life_info_collector.api import admin_server

    repository = FakeTelegramRepository()
    monkeypatch.setattr(admin_server, "content_service", lambda: FakeTelegramContentService())
    monkeypatch.setattr(admin_server, "content_repository", lambda: repository)
    monkeypatch.setattr(admin_server, "telegram_api", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("real send blocked")))
    monkeypatch.setattr(admin_server, "telegram_api_multipart", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("real send blocked")))

    result = admin_server.send_content_review_to_telegram(living_candidate(), dry_run=True)

    assert result["status"] == "DRY_RUN"
    assert result["log_id"] == 1
    assert repository.records[0]["status"] == "DRY_RUN"
    assert repository.records[0]["dry_run"] is True
    assert repository.records[0]["metadata"]["source_domain"] == "LIVING_INFO"


def test_living_info_duplicate_review_is_suppressed_without_real_send(monkeypatch) -> None:
    from foreign_worker_life_info_collector.api import admin_server

    repository = FakeTelegramRepository(duplicate={"id": 11, "status": "DRY_RUN"})
    monkeypatch.setattr(admin_server, "content_service", lambda: FakeTelegramContentService())
    monkeypatch.setattr(admin_server, "content_repository", lambda: repository)
    monkeypatch.setattr(admin_server, "telegram_api", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("real send blocked")))
    monkeypatch.setattr(admin_server, "telegram_api_multipart", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("real send blocked")))

    result = admin_server.send_content_review_to_telegram(living_candidate(), dry_run=True)

    assert result["status"] == "REVIEW_SUPPRESSED_DUPLICATE"
    assert result["suppressed"] is True
    assert result["matched_log_id"] == 11
    assert repository.records[0]["status"] == "REVIEW_SUPPRESSED_DUPLICATE"
    assert repository.records[0]["dry_run"] is True
