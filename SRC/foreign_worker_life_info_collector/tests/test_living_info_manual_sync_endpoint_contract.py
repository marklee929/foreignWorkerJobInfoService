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
