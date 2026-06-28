from __future__ import annotations

from foreign_worker_life_info_collector.tools.living_info_backfill_apply import (
    bool_to_yn,
    build_plans,
    parse_actions,
    parse_ids,
    row_to_normalized_item,
    row_to_source_item,
    select_rows,
)


def sample_row(action: str = "MIGRATE_NORMALIZED_ITEM") -> dict:
    return {
        "content_candidate_id": 109268,
        "backfill_action": action,
        "source_url": "https://example.com/source",
        "canonical_url": "https://example.com/source",
        "effective_url": "https://example.com/source",
        "source_name": "Example",
        "source_type": "trusted_media",
        "language": "en",
        "raw_title": "Practical Korea living guide for foreign residents",
        "raw_summary": "Check address, insurance, and local support.",
        "source_trust_level": "TRUSTED_MEDIA",
        "privacy_risk_level": "LOW",
        "duplicate_key": "url:https://example.com/source",
        "content_hash": "abc",
        "published_at": "",
        "collected_at": "2026-06-28T00:00:00+00:00",
        "normalized_primary_category": "DAILY_LIFE",
        "normalized_secondary_category": "settlement_life",
        "source_usage": "TOPIC_CLUSTER_MATERIAL",
        "info_signal_type": "INFORMATIONAL",
        "target_user": "FOREIGN_RESIDENTS_IN_KOREA",
        "action_type": "PRACTICAL_CHECK",
        "topic_key_candidate": "daily_life:korea-living-guide",
        "validation_needed_yn": False,
        "validation_source_type": "TRUSTED_MEDIA",
        "actionability_score": 70,
        "repeatability_score": 80,
        "source_reliability_score": 70,
        "normalization_confidence": 90,
        "normalization_reason": "test",
    }


def test_parse_ids_and_actions() -> None:
    assert parse_ids("109268, 73215") == {109268, 73215}
    assert parse_actions("MIGRATE_SOURCE_ITEM;MIGRATE_NORMALIZED_ITEM") == {
        "MIGRATE_SOURCE_ITEM",
        "MIGRATE_NORMALIZED_ITEM",
    }


def test_select_rows_requires_candidate_ids_unless_all_matching() -> None:
    rows = [sample_row(), sample_row("LOW_VALUE_ARCHIVE")]

    selected = select_rows(rows, {109268}, set(), {"MIGRATE_NORMALIZED_ITEM"}, False, 50)
    all_matching = select_rows(rows, set(), set(), {"MIGRATE_NORMALIZED_ITEM"}, True, 50)

    assert len(selected) == 1
    assert len(all_matching) == 1


def test_source_only_candidate_ids_override_preview_action() -> None:
    rows = [sample_row("NEEDS_MANUAL_REVIEW")]

    selected = select_rows(rows, set(), {109268}, {"MIGRATE_NORMALIZED_ITEM"}, False, 50)
    plans, skipped = build_plans(selected)

    assert skipped == []
    assert len(plans) == 1
    assert plans[0].action == "MIGRATE_SOURCE_ITEM"
    assert plans[0].normalized_item is None


def test_build_plans_skips_missing_url() -> None:
    row = sample_row()
    row["effective_url"] = ""
    row["source_url"] = ""
    row["canonical_url"] = ""

    plans, skipped = build_plans([row])

    assert plans == []
    assert skipped[0]["reason"] == "missing_effective_url"


def test_row_conversion_for_source_and_normalized_items() -> None:
    row = sample_row()

    source_item = row_to_source_item(row)
    normalized_item = row_to_normalized_item(row)

    assert source_item.raw_ref_table == "content.content_candidate"
    assert source_item.raw_ref_id == 109268
    assert source_item.duplicate_key == "url:https://example.com/source"
    assert normalized_item.normalized_primary_category == "DAILY_LIFE"
    assert normalized_item.validation_needed_yn == "N"


def test_bool_to_yn() -> None:
    assert bool_to_yn(True) == "Y"
    assert bool_to_yn(False) == "N"
    assert bool_to_yn("true") == "Y"
    assert bool_to_yn("false") == "N"
