from __future__ import annotations

from datetime import datetime, timezone

from foreign_worker_life_info_collector.living_info.models import (
    LivingNormalizedItem,
    LivingSourceItem,
    LivingSourceSignal,
    LivingTopicCluster,
)
from foreign_worker_life_info_collector.living_info.repository import (
    REQUIRED_TABLES,
    normalized_item_values,
    source_item_row,
    source_item_values,
    source_signal_values,
    topic_cluster_evidence_row,
    topic_cluster_row,
    topic_cluster_values,
)


def test_required_tables_match_migration_contract() -> None:
    assert REQUIRED_TABLES == {
        "source_item",
        "normalized_item",
        "source_signal",
        "topic_cluster",
        "topic_cluster_item",
    }


def test_source_item_values_include_raw_payload_json() -> None:
    item = LivingSourceItem(
        source_url="https://example.go.kr/guide",
        source_type="OFFICIAL",
        duplicate_key="url:https://example.go.kr/guide",
        raw_payload={"content_candidate_id": 123},
    )

    values = source_item_values(item)

    assert values[0] == "https://example.go.kr/guide"
    assert values[4] == "OFFICIAL"
    assert values[17] == "url:https://example.go.kr/guide"
    assert '"content_candidate_id": 123' in values[-1]


def test_normalized_item_values_require_source_item_context() -> None:
    item = LivingNormalizedItem(
        source_item_id=10,
        normalized_primary_category="HEALTHCARE",
        source_usage="SOURCE_EVIDENCE",
        actionability_score=70,
        repeatability_score=80,
    )

    values = normalized_item_values(item)

    assert values[0] == 10
    assert values[1] == "HEALTHCARE"
    assert values[3] == "SOURCE_EVIDENCE"
    assert values[10] == 70.0
    assert values[11] == 80.0


def test_signal_and_cluster_values_are_stable() -> None:
    signal = LivingSourceSignal(primary_category="HOUSING", topic_key_candidate="housing:rental-deposit")
    cluster = LivingTopicCluster(topic_key="housing:rental-deposit", primary_category="HOUSING", evidence_count=2)

    signal_values = source_signal_values(signal)
    cluster_values = topic_cluster_values(cluster)

    assert signal_values[7] == "HOUSING"
    assert signal_values[8] == "housing:rental-deposit"
    assert cluster_values[0] == "housing:rental-deposit"
    assert cluster_values[1] == "HOUSING"
    assert cluster_values[6] == 2


def test_source_item_row_formats_datetime() -> None:
    row = (
        1,
        "https://example.go.kr/guide",
        "",
        "",
        "Example",
        "OFFICIAL",
        "en",
        "Korea",
        "Title",
        "Summary",
        "PRIMARY",
        "LOW",
        "dup-key",
        "hash",
        "COLLECTED",
        "Y",
        "content.content_candidate",
        100,
        datetime(2026, 6, 28, tzinfo=timezone.utc),
        datetime(2026, 6, 28, 1, 0, tzinfo=timezone.utc),
    )

    result = source_item_row(row)

    assert result["id"] == 1
    assert result["source_url"] == "https://example.go.kr/guide"
    assert result["collected_at"] == "2026-06-28T00:00:00+00:00"
    assert result["updated_at"] == "2026-06-28T01:00:00+00:00"


def test_topic_cluster_row_formats_scores_and_dates() -> None:
    row = (
        7,
        "healthcare:insurance-check",
        "HEALTHCARE",
        "insurance",
        "FOREIGN_RESIDENTS_IN_KOREA",
        "PRACTICAL_CHECK",
        2,
        1,
        3,
        1,
        1,
        2,
        82,
        "Y",
        "VALIDATED",
        "READY",
        datetime(2026, 6, 28, tzinfo=timezone.utc),
        datetime(2026, 6, 28, 1, 0, tzinfo=timezone.utc),
        datetime(2026, 6, 28, 2, 0, tzinfo=timezone.utc),
    )

    result = topic_cluster_row(row)

    assert result["id"] == 7
    assert result["evidence_count"] == 1
    assert result["readiness_score"] == 82.0
    assert result["last_evidence_at"] == "2026-06-28T01:00:00+00:00"


def test_topic_cluster_evidence_row_formats_numeric_values() -> None:
    row = (
        501,
        601,
        "https://www.nhis.or.kr/guide",
        "https://www.nhis.or.kr/guide",
        "https://www.nhis.or.kr/guide",
        "NHIS",
        "OFFICIAL",
        "PRIMARY",
        "Health insurance guide",
        "Check insurance status.",
        "Body",
        datetime(2026, 6, 28, tzinfo=timezone.utc),
        datetime(2026, 6, 28, 1, 0, tzinfo=timezone.utc),
        "HEALTHCARE",
        "insurance",
        "TOPIC_CLUSTER_MATERIAL",
        "INFORMATIONAL",
        "PRACTICAL_CHECK",
        80,
        90,
        95,
        88,
        "REPRESENTATIVE",
        1,
    )

    result = topic_cluster_evidence_row(row)

    assert result["source_item_id"] == 501
    assert result["publishable_link_url"] == "https://www.nhis.or.kr/guide"
    assert result["actionability_score"] == 80.0
    assert result["weight_score"] == 1.0
