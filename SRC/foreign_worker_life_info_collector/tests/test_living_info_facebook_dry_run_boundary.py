from __future__ import annotations

from typing import Any

from foreign_worker_life_info_collector.content.service import ContentService


def publish_candidate(**overrides: Any) -> dict[str, Any]:
    candidate = {
        "id": 701,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "priority_group": "LIVING_INFO",
        "category": "healthcare",
        "status": "READY_TO_PUBLISH",
        "title": "Health insurance checklist for foreign residents in Korea",
        "summary_en": "Foreign residents in Korea should check NHIS payment status before clinic visits.",
        "why_it_matters_en": "This helps avoid unpaid bills, clinic issues, and renewal deadline problems.",
        "body_en": "- Check your NHIS payment status.\n- Keep receipts.\n- Ask NHIS before renewal deadlines.",
        "review_reason": "Operator scored this living-info guide for dry-run validation.",
        "link_url": "https://www.nhis.or.kr/guide/health-insurance-for-foreign-residents.html",
        "source_url": "https://www.nhis.or.kr/guide/health-insurance-for-foreign-residents.html",
        "source_name": "NHIS",
        "final_publish_score": 82,
        "quality_score": 82,
        "hashtags": "#LivingInKorea #ForeignersInKorea #KoreaLife",
        "raw_payload": {"source": "living_info.topic_cluster"},
    }
    candidate.update(overrides)
    return candidate


class FakePublishRepository:
    def __init__(self, candidate: dict[str, Any]) -> None:
        self.candidate = candidate
        self.updates: list[dict[str, Any]] = []
        self.quality_blocks: list[dict[str, Any]] = []

    def get_candidate(self, candidate_id: int) -> dict[str, Any]:
        return self.candidate if int(self.candidate["id"]) == int(candidate_id) else {}

    def update_publish_result(self, candidate_id: int, result: dict[str, Any], dry_run: bool) -> dict[str, Any]:
        self.updates.append({"candidate_id": candidate_id, "result": result, "dry_run": dry_run})
        return {"updated": True, "recorded_dry_run": dry_run}

    def mark_candidate_quality_blocked(self, candidate_id: int, gate_payload: dict[str, Any]) -> dict[str, Any]:
        self.quality_blocks.append({"candidate_id": candidate_id, "gate": gate_payload})
        return {"updated": True}


def test_living_info_publish_dry_run_records_without_real_facebook(monkeypatch) -> None:
    from foreign_worker_life_info_collector.content import service as content_service_module

    repository = FakePublishRepository(publish_candidate())
    monkeypatch.setenv("CONTENT_FACEBOOK_PUBLISH_ENABLED", "true")
    monkeypatch.setenv("CONTENT_AUTO_PUBLISH", "true")
    monkeypatch.setenv("CONTENT_PUBLISH_TEST_MODE", "false")
    monkeypatch.setattr(
        content_service_module,
        "FacebookPageClient",
        lambda: (_ for _ in ()).throw(AssertionError("real Facebook post blocked")),
    )

    result = ContentService(repository=repository).publish(701, dry_run=True)

    assert result["status"] == "DRY_RUN"
    assert result["facebook_status"] == "DRY_RUN"
    assert repository.updates[0]["dry_run"] is True
    request_payload = repository.updates[0]["result"]["request_payload"]
    assert request_payload["source"] == "content.content_candidate"
    assert "access_token" not in request_payload
    assert "token_masked" not in request_payload
    assert "token_fingerprint" not in request_payload


def test_living_info_facebook_invalid_link_is_blocked_as_dry_run_validation(monkeypatch) -> None:
    repository = FakePublishRepository(
        publish_candidate(
            link_url="https://example.go.kr/path/A/legacy-redirect",
            source_url="https://example.go.kr/path/A/legacy-redirect",
        )
    )
    monkeypatch.setenv("CONTENT_FACEBOOK_PUBLISH_ENABLED", "true")
    monkeypatch.setenv("CONTENT_AUTO_PUBLISH", "true")
    monkeypatch.setenv("CONTENT_PUBLISH_TEST_MODE", "false")

    result = ContentService(repository=repository).publish(701, dry_run=True)

    assert result["status"] == "FAILED_RETRYABLE"
    assert result["error_code"] == "FACEBOOK_LINK_INVALID"
    assert "legacy /path/A redirect URL" in result["error_message"]
    assert repository.updates[0]["dry_run"] is True


def test_living_info_facebook_message_invalid_is_blocked_as_dry_run_validation() -> None:
    repository = FakePublishRepository(
        publish_candidate(title="건강보험 납부 확인 안내 for foreign residents in Korea")
    )

    result = ContentService(repository=repository).publish(701, dry_run=True)

    assert result["status"] == "FAILED_RETRYABLE"
    assert result["error_code"] == "FACEBOOK_MESSAGE_INVALID"
    assert "Korean text" in result["error_message"]
    assert repository.updates[0]["dry_run"] is True


def test_living_info_quality_gate_failure_records_reason_without_publish_update() -> None:
    repository = FakePublishRepository(
        publish_candidate(link_url="", source_url="", final_publish_score=0, quality_score=0)
    )

    result = ContentService(repository=repository).publish(701, dry_run=True)

    assert result["status"] == "SKIPPED"
    assert result["error_code"] == "BLOCKED_SOURCE_INVALID"
    assert repository.quality_blocks[0]["gate"]["content_quality_gate_code"] == "BLOCKED_SOURCE_INVALID"
    assert repository.updates == []
