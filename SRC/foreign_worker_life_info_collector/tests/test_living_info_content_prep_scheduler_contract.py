from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADMIN_SERVER = ROOT / "foreign_worker_life_info_collector" / "api" / "admin_server.py"


def test_living_info_content_prep_scheduler_is_disabled_by_default() -> None:
    source = ADMIN_SERVER.read_text(encoding="utf-8")

    assert 'env_flag("LIVING_INFO_CONTENT_PREP_ENABLED", "false")' in source
    assert 'os.environ.get("LIVING_INFO_CONTENT_PREP_INTERVAL_MINUTES", "60")' in source
    assert 'os.environ.get("LIVING_INFO_CONTENT_PREP_LIMIT", "20")' in source


def test_living_info_content_prep_cycle_has_no_external_outputs() -> None:
    source = ADMIN_SERVER.read_text(encoding="utf-8")
    start = source.index("def run_living_info_content_prep_cycle")
    end = source.index("def run_living_info_content_prep_scheduler", start)
    block = source[start:end]

    assert "prepare_living_info_topic_clusters" in block
    assert "sync_living_info" in block
    assert '"telegram": "NOT_SENT"' in block
    assert '"publish": "BLOCKED"' in block
    assert "send_content_review_to_telegram" not in block
    assert ".publish(" not in block
    assert "FacebookPublisher" not in block


def test_living_info_content_prep_manual_route_defaults_to_dry_run() -> None:
    source = ADMIN_SERVER.read_text(encoding="utf-8")
    route_index = source.index('path == "/api/admin/content/living-info/prep-cycle"')
    route_block = source[route_index : route_index + 450]

    assert "run_living_info_content_prep_cycle" in route_block
    assert 'payload.get("dryRun", True)' in route_block
    assert "send_content_review_to_telegram" not in route_block
    assert ".publish(" not in route_block


def test_living_info_content_prep_startup_only_uses_gate() -> None:
    source = ADMIN_SERVER.read_text(encoding="utf-8")
    start = source.index("def start_living_info_content_prep_scheduler_if_enabled")
    end = source.index("class SingleKeywordNewsCollector", start)
    block = source[start:end]

    assert "if not settings[\"enabled\"]" in block
    assert "Thread(" in block
    assert "set_bot_switch_enabled" not in block


def test_living_info_content_prep_cycle_dry_run_executes_without_sync_or_external_output(monkeypatch) -> None:
    from foreign_worker_life_info_collector.api import admin_server

    class FakeContentService:
        def __init__(self) -> None:
            self.prepare_calls = []
            self.sync_calls = []

        def prepare_living_info_topic_clusters(self, limit: int, dry_run: bool):
            self.prepare_calls.append({"limit": limit, "dry_run": dry_run})
            return {"seen_count": 2, "cluster_count": 1, "written_count": 0}

        def sync_living_info(self, limit: int):
            self.sync_calls.append({"limit": limit})
            return {"synced_count": 1, "skipped_count": 0}

    fake = FakeContentService()
    logs = []
    monkeypatch.setattr(admin_server, "content_service", lambda: fake)
    monkeypatch.setattr(admin_server, "write_bot_log", lambda *args, **kwargs: logs.append(args))
    monkeypatch.setattr(admin_server, "set_living_info_content_prep_status", lambda *args, **kwargs: {})

    result = admin_server.run_living_info_content_prep_cycle(limit=3, dry_run=True)

    assert fake.prepare_calls == [{"limit": 3, "dry_run": True}]
    assert fake.sync_calls == []
    assert result["dry_run"] is True
    assert result["external_output"] == "NONE"
    assert result["publish"] == "BLOCKED"
    assert result["telegram"] == "NOT_SENT"
    assert logs


def test_living_info_content_prep_cycle_execute_syncs_ready_to_review_only(monkeypatch) -> None:
    from foreign_worker_life_info_collector.api import admin_server

    class FakeContentService:
        def prepare_living_info_topic_clusters(self, limit: int, dry_run: bool):
            return {"seen_count": 2, "cluster_count": 1, "written_count": 1}

        def sync_living_info(self, limit: int):
            return {
                "source": "living_info.topic_cluster",
                "seen_count": 1,
                "synced_count": 1,
                "skipped_count": 0,
                "skipped_reasons": {},
                "candidate_status": "READY_TO_REVIEW",
            }

    monkeypatch.setattr(admin_server, "content_service", lambda: FakeContentService())
    monkeypatch.setattr(admin_server, "write_bot_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(admin_server, "set_living_info_content_prep_status", lambda *args, **kwargs: {})

    result = admin_server.run_living_info_content_prep_cycle(limit=3, dry_run=False)

    assert result["dry_run"] is False
    assert result["sync"]["synced_count"] == 1
    assert result["sync"]["candidate_status"] == "READY_TO_REVIEW"
    assert result["external_output"] == "NONE"
