from __future__ import annotations

from pathlib import Path
from typing import Any

from foreign_worker_life_info_collector.content.service import ContentService


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def candidate(candidate_id: int = 901, **overrides: Any) -> dict[str, Any]:
    data = {
        "id": candidate_id,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "category": "healthcare",
        "status": "READY_TO_REVIEW",
        "title": "Health insurance checklist for foreign residents in Korea",
        "summary_en": "Check NHIS payment status before clinic visits or visa renewals.",
        "why_it_matters_en": "This can prevent unpaid bills and deadline problems.",
        "body_en": "- Check payment status.\n- Keep receipts.\n- Ask NHIS before deadlines.",
        "source_name": "NHIS",
        "source_url": "https://www.nhis.or.kr",
        "link_url": "https://www.nhis.or.kr",
        "final_publish_score": 82,
    }
    data.update(overrides)
    return data


def generated_preview(**overrides: Any) -> dict[str, Any]:
    data = {
        "ok": True,
        "status": "CARD_PREVIEW_GENERATED",
        "card_required": True,
        "template_type": "LIVING_IN_KOREA",
        "image_path": "C:/WORK/foreign_worker_job_info/SRC/foreign_worker_life_info_collector/storage/cache/content_cards/sample.png",
        "image_name": "sample.png",
        "payload": {"template_type": "LIVING_IN_KOREA", "title": "Health Insurance Checklist"},
    }
    data.update(overrides)
    return data


def failed_preview(**overrides: Any) -> dict[str, Any]:
    data = {
        "ok": False,
        "status": "INSUFFICIENT_VALID_CARD_POINTS",
        "reason": "Card requires at least 3 validated points before image generation.",
        "card_required": False,
    }
    data.update(overrides)
    return data


class FakeCardPreviewRepository:
    def __init__(self, candidates: dict[int, dict[str, Any]], targets: list[dict[str, Any]] | None = None) -> None:
        self.candidates = candidates
        self.targets = targets or list(candidates.values())
        self.records: list[dict[str, Any]] = []

    def get_candidate(self, candidate_id: int) -> dict[str, Any]:
        return self.candidates.get(candidate_id, {})

    def record_content_card_preview(
        self,
        candidate_id: int,
        status: str,
        preview: dict[str, Any],
        source: str = "manual_card_preview_dry_run",
    ) -> int:
        self.records.append(
            {
                "candidate_id": candidate_id,
                "status": status,
                "preview": preview,
                "source": source,
            }
        )
        return len(self.records)

    def list_living_info_card_preview_targets(self, limit: int = 20, status: str = "READY_TO_REVIEW") -> list[dict[str, Any]]:
        return self.targets[:limit]


class FakePreviewContentService(ContentService):
    def __init__(self, repository: FakeCardPreviewRepository, previews: dict[int, dict[str, Any]]) -> None:
        super().__init__(repository=repository)
        self.previews = previews

    def telegram_review_card_preview(self, candidate: dict[str, Any]) -> dict[str, Any]:
        return self.previews[int(candidate["id"])]


def test_single_candidate_card_preview_dry_run_logs_generated_preview() -> None:
    repository = FakeCardPreviewRepository({901: candidate(901)})
    service = FakePreviewContentService(repository, {901: generated_preview()})

    result = service.generate_card_preview_dry_run(901)

    assert result["ok"] is True
    assert result["status"] == "CARD_PREVIEW_DRY_RUN"
    assert result["log_id"] == 1
    assert result["content_card_preview"]["status"] == "CARD_PREVIEW_GENERATED"
    assert repository.records == [
        {
            "candidate_id": 901,
            "status": "CARD_PREVIEW_DRY_RUN",
            "preview": result["content_card_preview"],
            "source": "manual_card_preview_dry_run",
        }
    ]


def test_single_candidate_card_preview_dry_run_logs_failure_reason() -> None:
    repository = FakeCardPreviewRepository({902: candidate(902)})
    service = FakePreviewContentService(repository, {902: failed_preview()})

    result = service.generate_card_preview_dry_run(902)

    assert result["ok"] is True
    assert result["status"] == "CARD_PREVIEW_FAILED"
    assert result["content_card_preview"]["status"] == "INSUFFICIENT_VALID_CARD_POINTS"
    assert "validated points" in result["content_card_preview"]["reason"]
    assert repository.records[0]["status"] == "CARD_PREVIEW_FAILED"
    assert repository.records[0]["preview"]["reason"] == result["content_card_preview"]["reason"]


def test_bulk_living_info_card_preview_processes_living_info_only() -> None:
    living_ok = candidate(903)
    living_failed = candidate(904, category="housing")
    social_news = candidate(905, source_domain="SOCIAL_NEWS", content_type="NEWS_ARTICLE")
    repository = FakeCardPreviewRepository(
        {903: living_ok, 904: living_failed, 905: social_news},
        targets=[living_ok, living_failed, social_news],
    )
    service = FakePreviewContentService(
        repository,
        {
            903: generated_preview(image_name="living-ok.png"),
            904: failed_preview(status="CARD_NOT_READY", reason="single_news_public_card_not_ready"),
        },
    )

    result = service.generate_living_info_card_previews(limit=10, status="READY_TO_REVIEW")

    assert result["ok"] is True
    assert result["seen_count"] == 3
    assert result["generated_count"] == 1
    assert result["failed_count"] == 1
    assert result["skipped_count"] == 1
    assert [record["candidate_id"] for record in repository.records] == [903, 904]
    assert result["items"][2]["preview_status"] == "SKIPPED_NON_LIVING_INFO"


def test_card_preview_service_path_does_not_call_external_publishers() -> None:
    source = (PROJECT_ROOT / "content" / "service.py").read_text(encoding="utf-8")
    start = source.index("def generate_card_preview_dry_run")
    end = source.index("def apply_operator_score", start)
    block = source[start:end]

    assert "send_content_review_to_telegram" not in block
    assert "telegram_api" not in block
    assert "telegram_api_multipart" not in block
    assert "FacebookPageClient" not in block


def test_admin_api_and_ui_contract_expose_card_preview_actions() -> None:
    api_server = (PROJECT_ROOT / "api" / "admin_server.py").read_text(encoding="utf-8")
    api_client = (PROJECT_ROOT / "admin_ui" / "src" / "services" / "apiClient.js").read_text(encoding="utf-8")
    content_page = (PROJECT_ROOT / "admin_ui" / "src" / "views" / "ContentManagementPage.vue").read_text(encoding="utf-8")

    assert "/api/admin/content/candidates/" in api_server
    assert "/card-preview-dry-run" in api_server
    assert "/api/admin/content/living-info/card-preview-dry-run" in api_server
    assert "generateContentCandidateCardPreview" in api_client
    assert "generateLivingInfoCardPreviews" in api_client
    assert "Living info card preview" in content_page
    assert "Latest card preview" in content_page
