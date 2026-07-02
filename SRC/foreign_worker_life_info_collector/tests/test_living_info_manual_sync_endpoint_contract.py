from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_manual_living_info_sync_endpoint_calls_only_sync_living_info() -> None:
    source = (ROOT / "foreign_worker_life_info_collector" / "api" / "admin_server.py").read_text(encoding="utf-8")

    route_index = source.index('path == "/api/admin/content/living-info/sync"')
    route_block = source[route_index : route_index + 450]

    assert "content_service().sync_living_info" in route_block
    assert "sync_all" not in route_block
    assert "send_content_review_to_telegram" not in route_block
    assert ".publish(" not in route_block


def test_manual_living_info_prepare_clusters_endpoint_defaults_to_dry_run() -> None:
    source = (ROOT / "foreign_worker_life_info_collector" / "api" / "admin_server.py").read_text(encoding="utf-8")

    route_index = source.index('path == "/api/admin/content/living-info/prepare-clusters"')
    route_block = source[route_index : route_index + 650]

    assert "prepare_living_info_topic_clusters" in route_block
    assert "dry_run=not execute" in route_block
    assert "send_content_review_to_telegram" not in route_block
    assert ".publish(" not in route_block


def test_frontend_api_client_exposes_manual_living_info_sync() -> None:
    source = (ROOT / "foreign_worker_life_info_collector" / "admin_ui" / "src" / "services" / "apiClient.js").read_text(encoding="utf-8")

    assert "syncLivingInfoContentCandidates" in source
    assert "postJson('/api/admin/content/living-info/sync', payload)" in source
    assert "runLivingInfoPrepCycle" in source
    assert "postJson('/api/admin/content/living-info/prep-cycle', payload" in source


def test_content_management_page_uses_prep_cycle_for_living_info_prepare() -> None:
    source = (
        ROOT
        / "foreign_worker_life_info_collector"
        / "admin_ui"
        / "src"
        / "views"
        / "ContentManagementPage.vue"
    ).read_text(encoding="utf-8")

    start = source.index("async function syncLivingInfo()")
    end = source.index("async function generateLivingInfoCardPreviewBatch", start)
    block = source[start:end]

    assert "runLivingInfoPrepCycle({ limit: 100, dryRun: false })" in block
    assert "syncLivingInfoContentCandidates" not in block
