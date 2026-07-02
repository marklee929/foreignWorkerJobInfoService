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
    assert "fetchLivingInfoReadinessDiagnostics" in source
    assert "getJson(withQuery('/api/admin/content/living-info/readiness-diagnostics', params))" in source


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


def test_content_management_page_displays_living_info_readiness_diagnostics() -> None:
    source = (
        ROOT
        / "foreign_worker_life_info_collector"
        / "admin_ui"
        / "src"
        / "views"
        / "ContentManagementPage.vue"
    ).read_text(encoding="utf-8")

    assert "fetchLivingInfoReadinessDiagnostics" in source
    assert "livingInfoReadiness" in source
    assert "loadLivingInfoReadiness" in source
    assert "Living readiness" in source
    assert "living_info readiness:" in source
    assert "publicReady" in source
    assert "topReason" in source


def test_lifestyle_bot_default_collection_inputs_are_source_expanded() -> None:
    source = (ROOT / "foreign_worker_life_info_collector" / "api" / "admin_server.py").read_text(encoding="utf-8")

    assert "LIFESTYLE_BOT_DEFAULT_MAX_KEYWORDS = 8" in source
    assert "LIFESTYLE_BOT_DEFAULT_PER_KEYWORD_LIMIT = 3" in source
    assert "site:seoul.go.kr foreign residents living support Korea" in source
    assert "site:global.seoul.go.kr foreign residents housing healthcare" in source
    assert "site:nhis.or.kr foreigners Korea health insurance" in source
    assert "site:nps.or.kr foreign workers Korea national pension" in source
    assert "site:moel.go.kr foreign workers Korea labor rights" in source
    assert "site:hikorea.go.kr foreign residents Korea stay guide" in source
    assert "site:gov.kr foreigners Korea public service" in source


def test_lifestyle_bot_uses_configurable_manual_limits_without_external_publish() -> None:
    source = (ROOT / "foreign_worker_life_info_collector" / "api" / "admin_server.py").read_text(encoding="utf-8")

    start = source.index("def run_lifestyle_bot_once()")
    end = source.index("def start_lifestyle_bot()", start)
    block = source[start:end]

    assert "LIFESTYLE_BOT_KEYWORDS[:max_keywords]" in block
    assert 'os.environ.get("LIFESTYLE_BOT_MAX_KEYWORDS"' in block
    assert 'os.environ.get("LIFESTYLE_BOT_PER_KEYWORD_LIMIT"' in block
    assert "dry_run=True" in block
    assert "limit=per_keyword_limit" in block
    assert "limit=1" not in block
    assert "send_content_review_to_telegram" not in block
    assert ".publish(" not in block


def test_living_info_readiness_diagnostics_endpoint_is_dry_run_only() -> None:
    source = (ROOT / "foreign_worker_life_info_collector" / "api" / "admin_server.py").read_text(encoding="utf-8")

    route_index = source.index('path == "/api/admin/content/living-info/readiness-diagnostics"')
    route_block = source[route_index : route_index + 260]

    function_index = source.index("def living_info_readiness_diagnostics")
    function_block = source[function_index : source.index("def living_info_cluster_skip_reasons", function_index)]

    assert "living_info_readiness_diagnostics(limit=limit)" in route_block
    assert "prepare_living_info_topic_clusters(limit=limit, dry_run=True)" in function_block
    assert '"public_ready_count"' in function_block
    assert '"top_skip_reasons"' in function_block
    assert '"external_output": "NONE"' in function_block
    assert "send_content_review_to_telegram" not in function_block
    assert ".publish(" not in function_block


def test_living_info_readiness_diagnostics_reports_skip_reason_categories() -> None:
    source = (ROOT / "foreign_worker_life_info_collector" / "api" / "admin_server.py").read_text(encoding="utf-8")

    function_index = source.index("def living_info_cluster_skip_reasons")
    function_block = source[function_index : source.index("def run_living_info_content_prep_scheduler", function_index)]

    assert "readiness_score_below_threshold" in function_block
    assert "validation_status_not_ready" in function_block
    assert "missing_primary_evidence" in function_block
    assert "missing_trusted_evidence" in function_block
    assert "missing_source_evidence" in function_block
