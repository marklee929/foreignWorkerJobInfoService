from __future__ import annotations

from foreign_worker_life_info_collector.tools.living_info_backfill_preview import build_previews


def test_housing_valid_url_becomes_normalized_candidate() -> None:
    rows = [
        {
            "content": {
                "id": 1,
                "source_domain": "LIVING_INFO",
                "content_type": "LIVING_GUIDE",
                "category": "housing",
                "title": "Housing contract checks for foreign residents in Korea",
                "summary_en": "Check the deposit, monthly rent, address registration, and maintenance fees before signing.",
                "body_en": "Keep a written contract and ask a resident support center when terms are unclear.",
                "source_url": "https://example.go.kr/housing/contract-check",
                "source_name": "Local Support Center",
                "status": "SCORED",
                "raw_ref_table": "social_news.candidate",
                "raw_ref_id": 10,
            },
            "social": {},
        }
    ]

    preview = build_previews(rows)[0]

    assert preview["normalized_primary_category"] == "HOUSING"
    assert preview["backfill_action"] == "MIGRATE_NORMALIZED_ITEM"


def test_travel_row_becomes_low_value_archive() -> None:
    rows = [
        {
            "content": {
                "id": 2,
                "source_domain": "LIVING_INFO",
                "content_type": "LIVING_GUIDE",
                "category": "travel",
                "title": "Bali travel confidence rises after tourism campaign",
                "summary_en": "A tourism campaign promoted travel confidence.",
                "source_url": "https://example.com/bali-travel",
                "source_name": "Travel Wire",
                "status": "SCORED",
                "raw_ref_table": "social_news.candidate",
                "raw_ref_id": 11,
            },
            "social": {},
        }
    ]

    preview = build_previews(rows)[0]

    assert preview["backfill_action"] == "LOW_VALUE_ARCHIVE"


def test_lower_rank_duplicate_url_becomes_duplicate_skip() -> None:
    rows = [
        {
            "content": {
                "id": 3,
                "source_domain": "LIVING_INFO",
                "content_type": "LIVING_GUIDE",
                "category": "healthcare",
                "title": "Health insurance payment checks for foreign residents in Korea",
                "summary_en": "Confirm payment status before clinic visits and visa deadlines.",
                "source_url": "https://example.go.kr/health/insurance",
                "source_name": "NHIS",
                "status": "SCORED",
                "final_publish_score": 95,
                "raw_ref_table": "social_news.candidate",
                "raw_ref_id": 12,
            },
            "social": {},
        },
        {
            "content": {
                "id": 4,
                "source_domain": "LIVING_INFO",
                "content_type": "LIVING_GUIDE",
                "category": "healthcare",
                "title": "Health insurance payment checks for foreign residents in Korea",
                "summary_en": "Confirm payment status before clinic visits and visa deadlines.",
                "source_url": "https://example.go.kr/health/insurance",
                "source_name": "NHIS",
                "status": "SCORED",
                "final_publish_score": 20,
                "raw_ref_table": "social_news.candidate",
                "raw_ref_id": 13,
            },
            "social": {},
        },
    ]

    previews = build_previews(rows)
    actions = {item["content_candidate_id"]: item["backfill_action"] for item in previews}

    assert actions[3] == "MIGRATE_NORMALIZED_ITEM"
    assert actions[4] == "DUPLICATE_SKIP"


def test_missing_url_with_useful_source_needs_manual_review() -> None:
    rows = [
        {
            "content": {
                "id": 5,
                "source_domain": "LIVING_INFO",
                "content_type": "LIVING_GUIDE",
                "category": "healthcare",
                "title": "Health insurance payment status can affect clinic visits",
                "summary_en": "Foreign residents should confirm payment status before deadlines.",
                "source_name": "NHIS",
                "status": "READY_TO_REVIEW",
                "raw_ref_table": "social_news.candidate",
                "raw_ref_id": 14,
            },
            "social": {},
        }
    ]

    preview = build_previews(rows)[0]

    assert preview["backfill_action"] == "NEEDS_MANUAL_REVIEW"


def test_system_text_becomes_do_not_migrate() -> None:
    rows = [
        {
            "content": {
                "id": 6,
                "source_domain": "LIVING_INFO",
                "content_type": "LIVING_GUIDE",
                "category": "housing",
                "title": "No article body was saved.",
                "summary_en": "Failed to fetch article.",
                "source_url": "https://example.com/broken",
                "source_name": "Parser",
                "status": "SCORED",
                "raw_ref_table": "social_news.candidate",
                "raw_ref_id": 15,
            },
            "social": {},
        }
    ]

    preview = build_previews(rows)[0]

    assert preview["backfill_action"] == "DO_NOT_MIGRATE"
