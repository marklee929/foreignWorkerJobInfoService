from __future__ import annotations

from foreign_worker_life_info_collector.tools.living_info_manual_sync_dry_run import run_dry_run


def test_manual_sync_dry_run_ready_cluster_creates_ready_to_review_candidate() -> None:
    payload = run_dry_run(mode="ready")

    assert payload["ok"] is True
    assert payload["result"]["source"] == "living_info.topic_cluster"
    assert payload["result"]["seen_count"] == 1
    assert payload["result"]["synced_count"] == 1
    assert payload["result"]["skipped_count"] == 0
    assert payload["created_candidates"][0]["status"] == "READY_TO_REVIEW"
    assert payload["created_candidates"][0]["raw_ref_table"] == "living_info.topic_cluster"
    assert payload["external_output"]["telegram_sent"] is False
    assert payload["external_output"]["facebook_posted"] is False


def test_manual_sync_dry_run_community_only_cluster_is_skipped() -> None:
    payload = run_dry_run(mode="community-only")

    assert payload["result"]["seen_count"] == 1
    assert payload["result"]["synced_count"] == 0
    assert payload["result"]["skipped_count"] == 1
    assert payload["created_candidates"] == []
    assert payload["external_output"]["telegram_sent"] is False
    assert payload["external_output"]["facebook_posted"] is False
