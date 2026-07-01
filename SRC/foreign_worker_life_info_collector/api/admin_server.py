"""Admin API for the Vue dashboard with Telegram approval auth."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import subprocess
import traceback
import threading
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..content.repository import ContentRepository
from ..content.service import ContentService
from ..immigration.repository import ImmigrationNoticeRepository
from ..immigration.service import ImmigrationNoticeService
from ..jobs.employment_collector import EmploymentJobCollector
from ..jobs.repository import JobCollectorRepository
from ..occupation.collectors import JobInfoCollector, OccupationInfoCollector
from ..occupation.repository import OccupationRepository
from ..social.news.collector.article_text_extractor import fetch_article_metadata
from ..social.news.collector.google_news_url_resolver import is_acceptable_source_url, resolve_google_news_url
from ..social.news.evaluator.candidate_evaluator import CandidateEvaluator
from ..social.news.pipeline import NewsPipeline, today_cycle_id
from ..social.news.publisher.facebook_publisher import FacebookPublisher, facebook_runtime_config_summary, validate_facebook_article_link
from ..social.news.repository.news_repository import NewsRepository, safe_url
from ..social.news.summarizer.news_summarizer import NewsSummarizer
from ..storage.db.postgres import connect, load_env_file, safe_connection_summary


SESSION_COOKIE = "workconnect_admin_session"
APPROVED = "APPROVED"
PENDING = "PENDING"
REJECTED = "REJECTED"
LOGGED_OUT = "LOGGED_OUT"
PENDING_TIMEOUT_MINUTES = 3
BOT_KEY = "social_news_bot"
BOT_STATUS_LABELS = {
    "RUNNING": "실행 중",
    "STOPPED": "중지됨",
    "ERROR": "장애",
    "STARTING": "시작 중",
    "STOPPING": "종료 중",
}
CONTENT_BOT_MODULE_KEY = "bot.content_generation"
LIFESTYLE_BOT_MODULE_KEY = "bot.lifestyle_info"
IMMIGRATION_BOT_MODULE_KEY = "bot.immigration_info"
BOT_SWITCH_DEFINITIONS = {
    CONTENT_BOT_MODULE_KEY: {
        "group": "bot",
        "name": "콘텐츠 생성 봇",
        "description": "Facebook 포맷 생성과 Telegram 검토 전송을 담당합니다.",
        "run_order": 30,
    },
    LIFESTYLE_BOT_MODULE_KEY: {
        "group": "bot",
        "name": "생활정보 봇",
        "description": "생활/정착 관련 후보를 수집합니다.",
        "run_order": 40,
    },
    IMMIGRATION_BOT_MODULE_KEY: {
        "group": "bot",
        "name": "출입국 봇",
        "description": "법무부/하이코리아 공식 공지를 수집합니다.",
        "run_order": 50,
    },
}
BOT_STOP_EVENT = threading.Event()
BOT_THREAD: threading.Thread | None = None
CONTENT_BOT_STATUS = {
    "status": "STOPPED",
    "message": "콘텐츠 생성 봇 대기 중",
    "lastStartedAt": None,
    "lastStoppedAt": None,
    "lastErrorAt": None,
    "lastErrorMessage": None,
    "lastResult": None,
}
CONTENT_BOT_LOCK = threading.Lock()
CONTENT_BOT_STOP_EVENT = threading.Event()
CONTENT_BOT_THREAD: threading.Thread | None = None
LIFESTYLE_BOT_STATUS = {
    "status": "STOPPED",
    "message": "생활정보 봇 대기 중",
    "lastStartedAt": None,
    "lastStoppedAt": None,
    "lastErrorAt": None,
    "lastErrorMessage": None,
    "lastResult": None,
}
LIFESTYLE_BOT_LOCK = threading.Lock()
LIFESTYLE_BOT_THREAD: threading.Thread | None = None
IMMIGRATION_BOT_STATUS = {
    "status": "STOPPED",
    "message": "출입국 봇 대기 중",
    "lastStartedAt": None,
    "lastStoppedAt": None,
    "lastErrorAt": None,
    "lastErrorMessage": None,
    "lastResult": None,
}
IMMIGRATION_BOT_LOCK = threading.Lock()
IMMIGRATION_BOT_THREAD: threading.Thread | None = None
LIVING_INFO_CONTENT_PREP_STATUS = {
    "status": "DISABLED",
    "message": "living info content preparation scheduler is disabled by default",
    "schedulerEnabled": False,
    "nextRunAt": None,
    "lastStartedAt": None,
    "lastStoppedAt": None,
    "lastErrorAt": None,
    "lastErrorMessage": None,
    "lastResult": None,
}
LIVING_INFO_CONTENT_PREP_LOCK = threading.Lock()
LIVING_INFO_CONTENT_PREP_STOP = threading.Event()
LIVING_INFO_CONTENT_PREP_THREAD: threading.Thread | None = None
JOB_COLLECTOR_STATUS = {
    "status": "STOPPED",
    "lastErrorMessage": None,
    "schedulerEnabled": False,
    "nextRunAt": None,
}
JOB_COLLECTOR_LOCK = threading.Lock()
JOB_COLLECTOR_THREAD: threading.Thread | None = None
JOB_COLLECTOR_SCHEDULER_THREAD: threading.Thread | None = None
JOB_COLLECTOR_SCHEDULER_STOP = threading.Event()
ARTICLE_CLEANUP_THREAD: threading.Thread | None = None
ARTICLE_CLEANUP_STOP = threading.Event()
ARTICLE_CLEANUP_LOCK = threading.Lock()
DASHBOARD_SUMMARY_CACHE: dict[str, Any] = {"expires_at": 0.0, "payload": None}
DASHBOARD_SUMMARY_LOCK = threading.Lock()
LLAMA_STATE = {
    "enabled": False,
    "connected": False,
    "endpoint": "http://localhost:11434",
    "model": "llama3.1",
    "status": "DISABLED",
    "message": "로컬 LLaMA 비활성",
    "managed": True,
    "manual_off": False,
}
LLAMA_PROCESS: subprocess.Popen | None = None
LLAMA_MANUAL_OFF = False
PUBLIC_POST_PATHS = {"/api/admin/auth/check", "/api/admin/auth/logout", "/api/admin/telegram/callback"}
PUBLIC_GET_PREFIXES = ("/api/admin/auth/status/",)
PUBLIC_GET_PATHS = {"/api/health"}
ALLOWED_ADMIN_ORIGINS = {
    "http://127.0.0.1:5173",
    "http://localhost:5173",
}


def ensure_auth_schema() -> None:
    print("[storage] schema initialization skipped during recovery", flush=True)
    return
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(52765001)")
            locked = bool(cur.fetchone()[0])
            if not locked:
                print("[storage] schema initialization already running; skipping this process", flush=True)
                return
            cur.execute("SET LOCAL lock_timeout = '5s'")
            cur.execute(
                """
                CREATE SCHEMA IF NOT EXISTS admin;

                CREATE TABLE IF NOT EXISTS admin.module_config (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    module_key VARCHAR(120) NOT NULL UNIQUE,
                    module_group VARCHAR(60) NOT NULL,
                    module_name VARCHAR(120) NOT NULL,
                    description TEXT,
                    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    is_required BOOLEAN NOT NULL DEFAULT FALSE,
                    run_order INTEGER NOT NULL DEFAULT 100,
                    config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                INSERT INTO admin.module_config(module_key, module_group, module_name, description, is_enabled, run_order)
                VALUES
                    ('social_news_bot', 'bot', '소셜 뉴스 봇', '뉴스 수집, 요약, 평가, 게시 자동화 런타임', TRUE, 10),
                    ('job_collector_bot', 'bot', '채용정보 수집 봇', '고용24/워크넷 채용정보 수집 런타임', FALSE, 20)
                ON CONFLICT (module_key) DO NOTHING;

                CREATE TABLE IF NOT EXISTS admin.admin_login_session (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    device_id VARCHAR(120) NOT NULL,
                    ip_address VARCHAR(80) NOT NULL,
                    user_agent TEXT NOT NULL,
                    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
                    telegram_message_id BIGINT,
                    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    approved_at TIMESTAMPTZ,
                    rejected_at TIMESTAMPTZ,
                    logged_out_at TIMESTAMPTZ,
                    last_seen_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT ck_admin_login_session_status
                        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'LOGGED_OUT'))
                );

                CREATE INDEX IF NOT EXISTS idx_admin_login_session_lookup
                ON admin.admin_login_session(device_id, ip_address, left(user_agent, 180), status);

                CREATE UNIQUE INDEX IF NOT EXISTS ux_admin_login_session_approved_active
                ON admin.admin_login_session(device_id, ip_address, user_agent)
                WHERE status = 'APPROVED';

                CREATE UNIQUE INDEX IF NOT EXISTS ux_admin_login_session_pending_active
                ON admin.admin_login_session(device_id, ip_address, user_agent)
                WHERE status = 'PENDING';

                CREATE TABLE IF NOT EXISTS admin.admin_bot_runtime (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    bot_key VARCHAR(120) NOT NULL UNIQUE,
                    status VARCHAR(30) NOT NULL DEFAULT 'STOPPED',
                    last_started_at TIMESTAMPTZ,
                    last_stopped_at TIMESTAMPTZ,
                    last_error_at TIMESTAMPTZ,
                    last_error_message TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT ck_admin_bot_runtime_status
                        CHECK (status IN ('RUNNING', 'STOPPED', 'ERROR', 'STARTING', 'STOPPING'))
                );

                INSERT INTO admin.admin_bot_runtime(bot_key, status)
                VALUES ('social_news_bot', 'STOPPED')
                ON CONFLICT (bot_key) DO NOTHING;

                UPDATE admin.module_config
                SET is_enabled = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE module_key IN ('collector.naver', 'collector.google', 'publish.facebook', 'notify.telegram');

                UPDATE admin.module_config
                SET is_enabled = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE module_key = 'collector.rss';
                """
            )
            cur.execute("SELECT pg_advisory_unlock(52765001)")
        conn.commit()


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [column.name for column in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    rows = fetch_all(sql, params)
    return rows[0] if rows else {}


def fetch_one_with_timeout(sql: str, params: tuple[Any, ...] = (), timeout_ms: int = 3000) -> dict[str, Any]:
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('statement_timeout', %s, true)", (f"{int(timeout_ms)}ms",))
                cur.execute(sql, params)
                row = cur.fetchone()
                columns = [column.name for column in cur.description] if cur.description else []
            conn.commit()
        return dict(zip(columns, row)) if row else {}
    except Exception as exc:
        print(f"[dashboard][WARN] summary query timed out or failed: {str(exc)[:180]}", flush=True)
        return {}


def execute_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            columns = [column.name for column in cur.description] if cur.description else []
        conn.commit()
    return dict(zip(columns, row)) if row else {}


def bot_runtime_row() -> dict[str, Any]:
    return fetch_one(
        """
        SELECT bot_key, status, last_started_at, last_stopped_at, last_error_at, last_error_message
        FROM admin.admin_bot_runtime
        WHERE bot_key = %s
        """,
        (BOT_KEY,),
    )


def format_bot_status(row: dict[str, Any]) -> dict[str, Any]:
    status = row.get("status") or "STOPPED"
    return {
        "status": status,
        "label": BOT_STATUS_LABELS.get(status, status),
        "lastStartedAt": row.get("last_started_at"),
        "lastStoppedAt": row.get("last_stopped_at"),
        "lastErrorAt": row.get("last_error_at"),
        "lastErrorMessage": row.get("last_error_message"),
    }


def news_repository() -> NewsRepository:
    return NewsRepository()


def job_repository() -> JobCollectorRepository:
    return JobCollectorRepository()


def job_collector() -> EmploymentJobCollector:
    return EmploymentJobCollector(job_repository())


def occupation_repository() -> OccupationRepository:
    return OccupationRepository()


def job_info_collector() -> JobInfoCollector:
    return JobInfoCollector(occupation_repository())


def occupation_info_collector() -> OccupationInfoCollector:
    return OccupationInfoCollector(occupation_repository())


def write_bot_log(step: str, status: str, message: str) -> None:
    try:
        news_repository().insert_pipeline_log(step=step, status=status, message=message)
    except Exception:
        pass


def set_bot_status(status: str, error_message: str | None = None) -> dict[str, Any]:
    assignments = ["status = %s", "updated_at = CURRENT_TIMESTAMP"]
    params: list[Any] = [status]
    if status == "RUNNING":
        assignments.append("last_started_at = CURRENT_TIMESTAMP")
        assignments.append("last_error_message = NULL")
    elif status == "STOPPED":
        assignments.append("last_stopped_at = CURRENT_TIMESTAMP")
        assignments.append("last_error_message = NULL")
    elif status == "ERROR":
        assignments.append("last_error_at = CURRENT_TIMESTAMP")
        assignments.append("last_error_message = %s")
        params.append((error_message or "알 수 없는 오류")[:500])
    params.append(BOT_KEY)
    row = execute_one(
        f"""
        UPDATE admin.admin_bot_runtime
        SET {", ".join(assignments)}
        WHERE bot_key = %s
        RETURNING bot_key, status, last_started_at, last_stopped_at, last_error_at, last_error_message
        """,
        tuple(params),
    )
    return format_bot_status(row)


def is_retryable_db_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in (
            "deadlock detected",
            "lock timeout",
            "could not serialize access",
            "serialization failure",
        )
    )


def run_bot_loop() -> None:
    try:
        from ..crew_team.social.news_bot import NewsBot

        keyword = os.environ.get("NEWS_COLLECTOR_KEYWORD", "foreign worker visa Korea")
        interval = int(os.environ.get("NEWS_COLLECTOR_CYCLE_INTERVAL_MINUTES", "20")) * 60
        failure_limit = int(os.environ.get("NEWS_BOT_CONSECUTIVE_FAILURE_LIMIT", "3"))
        retry_backoff = int(os.environ.get("NEWS_BOT_RETRY_BACKOFF_SECONDS", "60"))
        consecutive_failures = 0
        write_bot_log("bot", "STARTED", f"소셜 뉴스 봇 시작: 검색어 '{keyword}'")
        while not BOT_STOP_EVENT.is_set():
            llama = ensure_llama(start_command=True)
            write_bot_log("llama", "COMPLETED" if llama.get("connected") else "FAILED", f"LLaMA 상태 확인: {llama.get('message')} / 모델 {llama.get('model')}")
            if not llama.get("connected"):
                write_bot_log("cycle", "FAILED", "Local LLaMA 연결 실패로 이번 수집 사이클을 건너뜁니다.")
                if BOT_STOP_EVENT.wait(60):
                    break
                continue
            content_publish_enabled = bot_switch_enabled(CONTENT_BOT_MODULE_KEY, default=False)
            write_bot_log(
                "cycle",
                "STARTED",
                "뉴스 수집/자동 게시 사이클 시작" if content_publish_enabled else "뉴스 수집/평가 사이클 시작",
            )
            try:
                result = NewsBot().run(keyword=keyword, dry_run=not content_publish_enabled, limit=1)
            except Exception as exc:
                if not is_retryable_db_error(exc):
                    raise
                consecutive_failures += 1
                write_bot_log(
                    "cycle",
                    "FAILED_RETRYABLE",
                    f"재시도 가능한 DB 잠금 오류로 이번 사이클만 건너뜁니다: {str(exc)[:180]}",
                )
                if BOT_STOP_EVENT.wait(max(retry_backoff, 5)):
                    break
                continue
            publish_results = result.get("publish_results") or []
            selection_log = result.get("selection_log") or {}
            no_publish_code = selection_log.get("no_publish_code") or ""
            write_bot_log(
                "cycle",
                "COMPLETED",
                f"뉴스 수집 완료: 수집 {result.get('collected_count', 0)}건, 저장 {result.get('saved_count', 0)}건, 게시 후보 {result.get('selected_count', 0)}건",
            )
            if result.get("selected_count", 0) == 0 and no_publish_code == "WAITING_COOLDOWN":
                write_bot_log(
                    "facebook_publish",
                    "WAITING",
                    (
                        f"뉴스 게시 대기: 쿨다운 적용 중, READY {selection_log.get('ready_count', 0)}건, "
                        f"후보풀 {selection_log.get('candidate_pool_count', 0)}건, "
                        f"남은 {int((int(selection_log.get('cooldown_remaining') or 0) + 59) // 60)}분"
                    ),
                )
            if result.get("selected_count", 0) == 0 and no_publish_code != "WAITING_COOLDOWN":
                write_bot_log(
                    "facebook_publish",
                    "SKIPPED",
                    f"뉴스 게시 후보 없음: threshold {float(result.get('threshold') or 0):.0f}점 미달 또는 중복 제외",
                )
            if publish_results and all(item.get("status") == "FAILED" for item in publish_results):
                consecutive_failures += 1
                write_bot_log("cycle", "FAILED", f"게시 실패 누적: {consecutive_failures}/{failure_limit}")
            else:
                consecutive_failures = 0
            if consecutive_failures >= failure_limit:
                raise RuntimeError("뉴스 자동 게시 연속 실패로 봇을 장애 상태로 전환합니다.")
            write_bot_log("cooldown", "WAITING", f"다음 수집까지 {max(interval, 30) // 60}분 대기")
            if BOT_STOP_EVENT.wait(max(interval, 30)):
                break
        write_bot_log("bot", "STOPPED", "소셜 뉴스 봇 종료")
        set_bot_status("STOPPED")
    except Exception as exc:
        BOT_STOP_EVENT.set()
        write_bot_log("bot", "FAILED", f"봇 장애 발생: {str(exc)[:180]}")
        set_bot_status("ERROR", str(exc))

def start_bot() -> dict[str, Any]:
    global BOT_THREAD
    if BOT_THREAD and BOT_THREAD.is_alive():
        return set_bot_status("RUNNING")
    BOT_STOP_EVENT.clear()
    set_bot_status("STARTING")
    write_bot_log("bot", "STARTING", "소셜 뉴스 봇 시작 요청")
    BOT_THREAD = threading.Thread(target=run_bot_loop, name="workconnect-social-news-bot", daemon=True)
    BOT_THREAD.start()
    return set_bot_status("RUNNING")


def stop_bot() -> dict[str, Any]:
    if BOT_THREAD and BOT_THREAD.is_alive():
        set_bot_status("STOPPING")
        BOT_STOP_EVENT.set()
        write_bot_log("bot", "STOPPING", "소셜 뉴스 봇 종료 요청")
        return set_bot_status("STOPPED")
    BOT_STOP_EVENT.set()
    write_bot_log("bot", "STOPPED", "소셜 뉴스 봇이 이미 중지 상태입니다.")
    return set_bot_status("STOPPED")


def reset_bot_error() -> dict[str, Any]:
    BOT_STOP_EVENT.set()
    return set_bot_status("STOPPED")


def utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bot_switch_definition(module_key: str) -> dict[str, Any]:
    return BOT_SWITCH_DEFINITIONS.get(
        module_key,
        {
            "group": "bot",
            "name": module_key,
            "description": "",
            "run_order": 999,
        },
    )


def ensure_bot_switch(module_key: str) -> dict[str, Any]:
    definition = bot_switch_definition(module_key)
    try:
        content_repository()
        return execute_one(
            """
            INSERT INTO admin.module_config(module_key, module_group, module_name, description, is_enabled, is_required, run_order, config_json)
            VALUES (%s, %s, %s, %s, FALSE, FALSE, %s, '{}'::jsonb)
            ON CONFLICT (module_key) DO UPDATE
            SET module_group = EXCLUDED.module_group,
                module_name = EXCLUDED.module_name,
                description = EXCLUDED.description,
                run_order = EXCLUDED.run_order,
                updated_at = CURRENT_TIMESTAMP
            RETURNING module_key, is_enabled, config_json
            """,
            (
                module_key,
                definition["group"],
                definition["name"],
                definition["description"],
                definition["run_order"],
            ),
        )
    except Exception as exc:
        print(f"[bot-switch][WARN] {module_key} 스위치 초기화 실패: {str(exc)[:180]}", flush=True)
        return {"module_key": module_key, "is_enabled": False, "config_json": {}}


def bot_switch_enabled(module_key: str, default: bool = False) -> bool:
    try:
        row = ensure_bot_switch(module_key)
        return bool(row.get("is_enabled", default))
    except Exception:
        return default


def set_bot_switch_enabled(module_key: str, enabled: bool) -> bool:
    try:
        ensure_bot_switch(module_key)
        row = execute_one(
            """
            UPDATE admin.module_config
            SET is_enabled = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE module_key = %s
            RETURNING is_enabled
            """,
            (bool(enabled), module_key),
        )
        return bool(row.get("is_enabled", enabled))
    except Exception as exc:
        print(f"[bot-switch][WARN] {module_key} 스위치 저장 실패: {str(exc)[:180]}", flush=True)
        return bool(enabled)


def one_shot_bot_status(state: dict[str, Any], thread: threading.Thread | None, lock: threading.Lock) -> dict[str, Any]:
    with lock:
        if thread and thread.is_alive() and state.get("status") not in {"STARTING", "STOPPING"}:
            state["status"] = "RUNNING"
        elif (not thread or not thread.is_alive()) and state.get("status") in {"RUNNING", "STARTING", "STOPPING"}:
            state["status"] = "STOPPED"
            state["lastStoppedAt"] = state.get("lastStoppedAt") or utc_iso_now()
        status = state.get("status") or "STOPPED"
        return {
            "status": status,
            "label": BOT_STATUS_LABELS.get(status, status),
            "message": state.get("message") or "",
            "lastStartedAt": state.get("lastStartedAt"),
            "lastStoppedAt": state.get("lastStoppedAt"),
            "lastErrorAt": state.get("lastErrorAt"),
            "lastErrorMessage": state.get("lastErrorMessage"),
            "lastResult": state.get("lastResult"),
            "dryRun": True,
        }


def set_one_shot_bot_status(
    state: dict[str, Any],
    lock: threading.Lock,
    status: str,
    message: str = "",
    result: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> dict[str, Any]:
    now = utc_iso_now()
    with lock:
        state["status"] = status
        if message:
            state["message"] = message
        if result is not None:
            state["lastResult"] = result
        if status in {"STARTING", "RUNNING"}:
            state["lastStartedAt"] = now
            state["lastErrorMessage"] = None
        elif status == "STOPPED":
            state["lastStoppedAt"] = now
            state["lastErrorMessage"] = None
        elif status == "ERROR":
            state["lastErrorAt"] = now
            state["lastErrorMessage"] = (error_message or message or "알 수 없는 오류")[:500]
        return {
            "status": state["status"],
            "label": BOT_STATUS_LABELS.get(state["status"], state["status"]),
            "message": state.get("message") or "",
            "lastStartedAt": state.get("lastStartedAt"),
            "lastStoppedAt": state.get("lastStoppedAt"),
            "lastErrorAt": state.get("lastErrorAt"),
            "lastErrorMessage": state.get("lastErrorMessage"),
            "lastResult": state.get("lastResult"),
            "dryRun": True,
        }


def content_bot_status() -> dict[str, Any]:
    enabled = bot_switch_enabled(CONTENT_BOT_MODULE_KEY, default=False)
    with CONTENT_BOT_LOCK:
        if CONTENT_BOT_THREAD and CONTENT_BOT_THREAD.is_alive() and CONTENT_BOT_STATUS.get("status") not in {"STARTING", "STOPPING"}:
            CONTENT_BOT_STATUS["status"] = "RUNNING"
        elif (not CONTENT_BOT_THREAD or not CONTENT_BOT_THREAD.is_alive()) and CONTENT_BOT_STATUS.get("status") in {"RUNNING", "STARTING", "STOPPING"}:
            CONTENT_BOT_STATUS["status"] = "STOPPED"
            CONTENT_BOT_STATUS["lastStoppedAt"] = CONTENT_BOT_STATUS.get("lastStoppedAt") or utc_iso_now()
        status = CONTENT_BOT_STATUS.get("status") or "STOPPED"
        return {
            "status": status,
            "label": BOT_STATUS_LABELS.get(status, status),
            "message": CONTENT_BOT_STATUS.get("message") or "",
            "lastStartedAt": CONTENT_BOT_STATUS.get("lastStartedAt"),
            "lastStoppedAt": CONTENT_BOT_STATUS.get("lastStoppedAt"),
            "lastErrorAt": CONTENT_BOT_STATUS.get("lastErrorAt"),
            "lastErrorMessage": CONTENT_BOT_STATUS.get("lastErrorMessage"),
            "lastResult": CONTENT_BOT_STATUS.get("lastResult"),
            "enabled": enabled,
            "facebookPublishBlocked": True,
            "telegramReviewEnabled": True,
        }


def set_content_bot_status(status: str, message: str = "", result: dict[str, Any] | None = None, error_message: str | None = None) -> dict[str, Any]:
    now = utc_iso_now()
    with CONTENT_BOT_LOCK:
        CONTENT_BOT_STATUS["status"] = status
        if message:
            CONTENT_BOT_STATUS["message"] = message
        if result is not None:
            CONTENT_BOT_STATUS["lastResult"] = result
        if status in {"STARTING", "RUNNING"}:
            CONTENT_BOT_STATUS["lastStartedAt"] = now
            CONTENT_BOT_STATUS["lastErrorMessage"] = None
        elif status == "STOPPED":
            CONTENT_BOT_STATUS["lastStoppedAt"] = now
            CONTENT_BOT_STATUS["lastErrorMessage"] = None
        elif status == "ERROR":
            CONTENT_BOT_STATUS["lastErrorAt"] = now
            CONTENT_BOT_STATUS["lastErrorMessage"] = (error_message or message or "알 수 없는 오류")[:500]
        current = CONTENT_BOT_STATUS.get("status") or "STOPPED"
        return {
            "status": current,
            "label": BOT_STATUS_LABELS.get(current, current),
            "message": CONTENT_BOT_STATUS.get("message") or "",
            "lastStartedAt": CONTENT_BOT_STATUS.get("lastStartedAt"),
            "lastStoppedAt": CONTENT_BOT_STATUS.get("lastStoppedAt"),
            "lastErrorAt": CONTENT_BOT_STATUS.get("lastErrorAt"),
            "lastErrorMessage": CONTENT_BOT_STATUS.get("lastErrorMessage"),
            "lastResult": CONTENT_BOT_STATUS.get("lastResult"),
            "enabled": bot_switch_enabled(CONTENT_BOT_MODULE_KEY, default=current in {"RUNNING", "STARTING"}),
            "facebookPublishBlocked": True,
            "telegramReviewEnabled": True,
        }


def telegram_card_preview_metadata(card_preview: dict[str, Any] | None) -> dict[str, Any]:
    preview = card_preview or {}
    payload = preview.get("payload") if isinstance(preview.get("payload"), dict) else {}
    result = {
        "ok": bool(preview.get("ok")),
        "status": str(preview.get("status") or ""),
        "reason": str(preview.get("reason") or "")[:500],
        "card_required": bool(preview.get("card_required")),
        "template_type": str(preview.get("template_type") or payload.get("template_type") or ""),
        "image_name": str(preview.get("image_name") or ""),
        "image_path": str(preview.get("image_path") or ""),
    }
    if payload:
        result["payload"] = {
            "template_type": str(payload.get("template_type") or ""),
            "title": str(payload.get("title") or "")[:180],
            "subtitle": str(payload.get("subtitle") or "")[:240],
            "source": str(payload.get("source") or "")[:120],
            "date": str(payload.get("date") or "")[:20],
        }
    return result


def send_content_review_to_telegram(candidate: dict[str, Any], dry_run: bool | None = None) -> dict[str, Any]:
    candidate_id = int(candidate.get("id") or 0)
    if not content_service().requires_telegram_review(candidate):
        return {
            "ok": True,
            "status": "SKIPPED",
            "candidate_id": candidate_id,
            "log_id": None,
            "message_id": None,
            "message": "SOCIAL_NEWS는 Telegram 검토 없이 뉴스 봇에서 직접 게시합니다.",
        }
    card_preview = content_service().telegram_review_card_preview(candidate)
    message = content_service().telegram_review_message(candidate, card_preview=card_preview)
    review_metadata = content_service().telegram_review_metadata(candidate, message)
    review_metadata["content_card_preview"] = telegram_card_preview_metadata(card_preview)
    if card_preview.get("card_required") and not card_preview.get("ok"):
        result = {
            "ok": False,
            "description": card_preview.get("reason") or "Content card preview generation failed.",
            "content_card_preview": telegram_card_preview_metadata(card_preview),
        }
        log_id = content_repository().record_telegram_review(
            candidate_id,
            str(card_preview.get("status") or "CARD_PREVIEW_FAILED")[:40],
            True,
            message,
            result,
            review_metadata,
        )
        return {
            "ok": False,
            "status": card_preview.get("status") or "CARD_PREVIEW_FAILED",
            "candidate_id": candidate_id,
            "log_id": log_id,
            "message_id": None,
            "content_card_preview": telegram_card_preview_metadata(card_preview),
            "error_message": card_preview.get("reason") or "Content card preview generation failed.",
        }
    duplicate_review = content_repository().find_duplicate_telegram_review(review_metadata)
    if duplicate_review:
        suppress_status = (
            "REVIEW_SUPPRESSED_LOW_VALUE"
            if review_metadata.get("score_bucket") == "0-39"
            else "REVIEW_SUPPRESSED_DUPLICATE"
        )
        suppress_reason = (
            "same telegram_review_key or semantic_review_key already reviewed; "
            f"matched_log_id={duplicate_review.get('id')}"
        )
        response = {
            "ok": True,
            "suppressed": True,
            "suppress_reason": suppress_reason,
            "matched_log_id": duplicate_review.get("id"),
            "matched_status": duplicate_review.get("status"),
            "telegram_review_key": review_metadata.get("telegram_review_key"),
            "semantic_review_key": review_metadata.get("semantic_review_key"),
            "content_card_preview": telegram_card_preview_metadata(card_preview),
        }
        if str(duplicate_review.get("status") or "").startswith("REVIEW_SUPPRESSED"):
            log_id = int(duplicate_review.get("id") or 0)
        else:
            log_id = content_repository().record_telegram_review(
                candidate_id,
                suppress_status,
                True,
                message,
                response,
                review_metadata,
            )
        return {
            "ok": True,
            "status": suppress_status,
            "candidate_id": candidate_id,
            "log_id": log_id,
            "message_id": None,
            "suppressed": True,
            "suppress_reason": suppress_reason,
            "matched_log_id": duplicate_review.get("id"),
            "content_card_preview": telegram_card_preview_metadata(card_preview),
        }
    token_ready = bool(os.environ.get("TELEGRAM_BOT_TOKEN", "").strip() and telegram_admin_chat_id())
    dry_run = (not token_ready) if dry_run is None else bool(dry_run)
    if dry_run:
        log_id = content_repository().record_telegram_review(
            candidate_id,
            "DRY_RUN",
            True,
            message,
            {"ok": True, "dry_run": True, "description": "Telegram token/chat id not configured or dry-run requested."},
            review_metadata,
        )
        return {
            "ok": True,
            "status": "DRY_RUN",
            "candidate_id": candidate_id,
            "log_id": log_id,
            "message_id": None,
            "content_card_preview": telegram_card_preview_metadata(card_preview),
        }

    reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "90 우선", "callback_data": build_content_score_callback(candidate_id, 90)},
                    {"text": "75 사용", "callback_data": build_content_score_callback(candidate_id, 75)},
                ],
                [
                    {"text": "60 보류", "callback_data": build_content_score_callback(candidate_id, 60)},
                    {"text": "40 낮춤", "callback_data": build_content_score_callback(candidate_id, 40)},
                ],
            ]
    }
    if card_preview.get("ok") and card_preview.get("image_path"):
        result = telegram_api_multipart(
            "sendPhoto",
            {
                "chat_id": telegram_admin_chat_id(),
                "caption": message[:1024],
                "reply_markup": json.dumps(reply_markup, ensure_ascii=False),
            },
            "photo",
            Path(str(card_preview["image_path"])),
        )
    else:
        result = telegram_api(
            "sendMessage",
            {
                "chat_id": telegram_admin_chat_id(),
                "text": message[:3900],
                "reply_markup": reply_markup,
            },
        )
    status = "SENT" if result.get("ok") else "FAILED"
    log_id = content_repository().record_telegram_review(candidate_id, status, False, message, result, review_metadata)
    return {
        "ok": bool(result.get("ok")),
        "status": status,
        "candidate_id": candidate_id,
        "log_id": log_id,
        "message_id": result.get("result", {}).get("message_id"),
        "content_card_preview": telegram_card_preview_metadata(card_preview),
        "error_message": "" if result.get("ok") else result.get("description", ""),
    }


def run_content_generation_cycle(limit: int = 5) -> dict[str, Any]:
    sync = content_service().sync_all(limit=500)
    targets = content_service().review_targets(limit=limit)
    deliveries = [send_content_review_to_telegram(candidate) for candidate in targets]
    sent = sum(1 for item in deliveries if item.get("status") == "SENT")
    dry_run = sum(1 for item in deliveries if item.get("status") == "DRY_RUN")
    failed = sum(1 for item in deliveries if item.get("status") == "FAILED")
    suppressed = sum(1 for item in deliveries if str(item.get("status") or "").startswith("REVIEW_SUPPRESSED"))
    return {
        "ok": failed == 0,
        "sync": sync,
        "review_target_count": len(targets),
        "telegram": {
            "sent": sent,
            "dry_run": dry_run,
            "failed": failed,
            "suppressed": suppressed,
            "items": deliveries,
        },
        "facebook_publish": "BLOCKED_BY_CONTENT_REVIEW",
    }


def run_content_bot_loop() -> None:
    interval = int(os.environ.get("CONTENT_BOT_INTERVAL_MINUTES", "15") or "15") * 60
    review_limit = max(1, min(int(os.environ.get("CONTENT_BOT_REVIEW_LIMIT", "5") or "5"), 20))
    try:
        set_content_bot_status("RUNNING", "콘텐츠 생성/Telegram 검토 루프 실행 중")
        write_bot_log("content_bot", "STARTED", "콘텐츠 생성 봇 시작: Facebook 게시 차단, Telegram review 전송")
        while not CONTENT_BOT_STOP_EVENT.is_set():
            result = run_content_generation_cycle(limit=review_limit)
            set_content_bot_status(
                "RUNNING",
                f"콘텐츠 동기화 {result.get('sync', {}).get('synced_total', 0)}건 / Telegram 대상 {result.get('review_target_count', 0)}건",
                result=result,
            )
            write_bot_log(
                "content_bot",
                "COMPLETED" if result.get("ok") else "FAILED",
                (
                    f"콘텐츠 생성 사이클: sync {result.get('sync', {}).get('synced_total', 0)}건, "
                    f"Telegram sent {result.get('telegram', {}).get('sent', 0)}건, "
                    f"dry-run {result.get('telegram', {}).get('dry_run', 0)}건, "
                    f"suppressed {result.get('telegram', {}).get('suppressed', 0)}건"
                ),
            )
            if CONTENT_BOT_STOP_EVENT.wait(max(interval, 60)):
                break
        set_content_bot_status("STOPPED", "콘텐츠 생성 봇 중지됨")
        write_bot_log("content_bot", "STOPPED", "콘텐츠 생성 봇 종료")
    except Exception as exc:
        CONTENT_BOT_STOP_EVENT.set()
        set_content_bot_status("ERROR", "콘텐츠 생성 봇 장애", error_message=str(exc))
        write_bot_log("content_bot", "FAILED", f"콘텐츠 생성 봇 장애: {str(exc)[:180]}")


def start_content_bot() -> dict[str, Any]:
    global CONTENT_BOT_THREAD
    set_bot_switch_enabled(CONTENT_BOT_MODULE_KEY, True)
    if CONTENT_BOT_THREAD and CONTENT_BOT_THREAD.is_alive():
        return content_bot_status()
    CONTENT_BOT_STOP_EVENT.clear()
    set_content_bot_status("STARTING", "콘텐츠 생성 봇 시작 요청")
    CONTENT_BOT_THREAD = threading.Thread(target=run_content_bot_loop, name="workconnect-content-bot", daemon=True)
    CONTENT_BOT_THREAD.start()
    return content_bot_status()


def stop_content_bot() -> dict[str, Any]:
    set_bot_switch_enabled(CONTENT_BOT_MODULE_KEY, False)
    if CONTENT_BOT_THREAD and CONTENT_BOT_THREAD.is_alive():
        CONTENT_BOT_STOP_EVENT.set()
        return set_content_bot_status("STOPPING", "콘텐츠 생성 봇 종료 요청")
    CONTENT_BOT_STOP_EVENT.set()
    return set_content_bot_status("STOPPED", "콘텐츠 생성 봇 중지됨")


def env_flag(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def living_info_content_prep_settings() -> dict[str, Any]:
    return {
        "enabled": env_flag("LIVING_INFO_CONTENT_PREP_ENABLED", "false"),
        "intervalMinutes": max(20, int(os.environ.get("LIVING_INFO_CONTENT_PREP_INTERVAL_MINUTES", "60") or "60")),
        "limit": max(1, min(int(os.environ.get("LIVING_INFO_CONTENT_PREP_LIMIT", "20") or "20"), 100)),
    }


def living_info_content_prep_status() -> dict[str, Any]:
    settings = living_info_content_prep_settings()
    with LIVING_INFO_CONTENT_PREP_LOCK:
        if not settings["enabled"]:
            LIVING_INFO_CONTENT_PREP_STATUS["status"] = "DISABLED"
            LIVING_INFO_CONTENT_PREP_STATUS["schedulerEnabled"] = False
            LIVING_INFO_CONTENT_PREP_STATUS["nextRunAt"] = None
        payload = dict(LIVING_INFO_CONTENT_PREP_STATUS)
    payload["settings"] = settings
    payload["threadAlive"] = bool(LIVING_INFO_CONTENT_PREP_THREAD and LIVING_INFO_CONTENT_PREP_THREAD.is_alive())
    return payload


def set_living_info_content_prep_status(
    status: str,
    message: str = "",
    *,
    result: dict[str, Any] | None = None,
    error_message: str | None = None,
    next_run_at: str | None = None,
) -> dict[str, Any]:
    now = utc_iso_now()
    with LIVING_INFO_CONTENT_PREP_LOCK:
        LIVING_INFO_CONTENT_PREP_STATUS["status"] = status
        if message:
            LIVING_INFO_CONTENT_PREP_STATUS["message"] = message
        if result is not None:
            LIVING_INFO_CONTENT_PREP_STATUS["lastResult"] = result
        if next_run_at is not None:
            LIVING_INFO_CONTENT_PREP_STATUS["nextRunAt"] = next_run_at
        if status in {"RUNNING", "STARTING"}:
            LIVING_INFO_CONTENT_PREP_STATUS["lastStartedAt"] = now
            LIVING_INFO_CONTENT_PREP_STATUS["lastErrorMessage"] = None
        elif status in {"STOPPED", "DISABLED"}:
            LIVING_INFO_CONTENT_PREP_STATUS["lastStoppedAt"] = now
            LIVING_INFO_CONTENT_PREP_STATUS["lastErrorMessage"] = None
        elif status == "ERROR":
            LIVING_INFO_CONTENT_PREP_STATUS["lastErrorAt"] = now
            LIVING_INFO_CONTENT_PREP_STATUS["lastErrorMessage"] = (error_message or message or "unknown error")[:500]
        return dict(LIVING_INFO_CONTENT_PREP_STATUS)


def run_living_info_content_prep_cycle(limit: int = 20, dry_run: bool = True) -> dict[str, Any]:
    limit = max(1, min(int(limit or 20), 100))
    prepare = content_service().prepare_living_info_topic_clusters(limit=limit, dry_run=bool(dry_run))
    sync = {
        "source": "living_info.topic_cluster",
        "dry_run": True,
        "seen_count": 0,
        "synced_count": 0,
        "skipped_count": 0,
        "skipped_reasons": {},
        "message": "dry-run skipped content_candidate writes",
    }
    if not dry_run:
        sync = content_service().sync_living_info(limit=limit)
    result = {
        "ok": True,
        "dry_run": bool(dry_run),
        "limit": limit,
        "prepare": prepare,
        "sync": sync,
        "external_output": "NONE",
        "publish": "BLOCKED",
        "telegram": "NOT_SENT",
    }
    write_bot_log(
        "living_info_content_prep",
        "DRY_RUN" if dry_run else "COMPLETED",
        (
            f"living info prep dry_run={bool(dry_run)} "
            f"seen={prepare.get('seen_count', 0)} clusters={prepare.get('cluster_count', 0)} "
            f"written={prepare.get('written_count', 0)} synced={sync.get('synced_count', 0)} "
            f"skipped={sync.get('skipped_count', 0)}"
        ),
    )
    set_living_info_content_prep_status("STOPPED", "living info content preparation cycle completed", result=result)
    return result


def run_living_info_content_prep_scheduler() -> None:
    settings = living_info_content_prep_settings()
    if not settings["enabled"]:
        set_living_info_content_prep_status("DISABLED", "LIVING_INFO_CONTENT_PREP_ENABLED=false")
        return
    set_living_info_content_prep_status("RUNNING", "living info content preparation scheduler running")
    try:
        while not LIVING_INFO_CONTENT_PREP_STOP.is_set():
            result = run_living_info_content_prep_cycle(limit=int(settings["limit"]), dry_run=False)
            interval_seconds = max(20, int(settings["intervalMinutes"])) * 60
            next_run = datetime.now(timezone.utc) + timedelta(seconds=interval_seconds)
            set_living_info_content_prep_status(
                "RUNNING",
                "living info content preparation scheduler waiting",
                result=result,
                next_run_at=next_run.isoformat(),
            )
            if LIVING_INFO_CONTENT_PREP_STOP.wait(interval_seconds):
                break
        set_living_info_content_prep_status("STOPPED", "living info content preparation scheduler stopped")
    except Exception as exc:
        set_living_info_content_prep_status("ERROR", "living info content preparation scheduler failed", error_message=str(exc))
        write_bot_log("living_info_content_prep", "FAILED", f"living info prep scheduler failed: {str(exc)[:180]}")


def start_living_info_content_prep_scheduler_if_enabled() -> dict[str, Any]:
    global LIVING_INFO_CONTENT_PREP_THREAD
    settings = living_info_content_prep_settings()
    if not settings["enabled"]:
        return set_living_info_content_prep_status("DISABLED", "LIVING_INFO_CONTENT_PREP_ENABLED=false")
    if LIVING_INFO_CONTENT_PREP_THREAD and LIVING_INFO_CONTENT_PREP_THREAD.is_alive():
        return living_info_content_prep_status()
    LIVING_INFO_CONTENT_PREP_STOP.clear()
    with LIVING_INFO_CONTENT_PREP_LOCK:
        LIVING_INFO_CONTENT_PREP_STATUS["schedulerEnabled"] = True
    LIVING_INFO_CONTENT_PREP_THREAD = threading.Thread(
        target=run_living_info_content_prep_scheduler,
        name="workconnect-living-info-content-prep",
        daemon=True,
    )
    LIVING_INFO_CONTENT_PREP_THREAD.start()
    return living_info_content_prep_status()


class SingleKeywordNewsCollector:
    def __init__(self, delegate: Any):
        self.delegate = delegate

    def collect(self, keyword: str, limit: int | None = None) -> list[Any]:
        try:
            return self.delegate.collect(keyword, limit=limit)
        except TypeError as exc:
            if "limit" not in str(exc):
                raise
            return self.delegate.collect(keyword)


def lifestyle_news_collectors() -> list[Any]:
    from ..social.news.collector.google_news_collector import GoogleNewsCollector
    from ..social.news.collector.naver_news_collector import NaverNewsCollector

    return [SingleKeywordNewsCollector(NaverNewsCollector()), SingleKeywordNewsCollector(GoogleNewsCollector())]


def lifestyle_bot_status() -> dict[str, Any]:
    payload = one_shot_bot_status(LIFESTYLE_BOT_STATUS, LIFESTYLE_BOT_THREAD, LIFESTYLE_BOT_LOCK)
    payload["enabled"] = bot_switch_enabled(LIFESTYLE_BOT_MODULE_KEY, default=False)
    if payload["enabled"] and payload["status"] == "STOPPED":
        payload["message"] = payload.get("message") or "생활정보 봇 ON / 다음 수집 대기"
    return payload


def immigration_bot_status() -> dict[str, Any]:
    payload = one_shot_bot_status(IMMIGRATION_BOT_STATUS, IMMIGRATION_BOT_THREAD, IMMIGRATION_BOT_LOCK)
    payload["enabled"] = bot_switch_enabled(IMMIGRATION_BOT_MODULE_KEY, default=False)
    if payload["enabled"] and payload["status"] == "STOPPED":
        payload["message"] = payload.get("message") or "출입국 봇 ON / 다음 수집 대기"
    return payload


def run_lifestyle_bot_once() -> None:
    keywords = [
        "foreign residents Korea living guide",
        "foreigners in Korea housing bank healthcare",
        "Korea cost of living foreigners",
    ]
    try:
        set_one_shot_bot_status(LIFESTYLE_BOT_STATUS, LIFESTYLE_BOT_LOCK, "RUNNING", "생활정보 후보 수집 중")
        write_bot_log("lifestyle_bot", "STARTED", "생활정보 봇 dry-run 수집 시작")
        summaries: list[dict[str, Any]] = []
        max_keywords = max(1, min(int(os.environ.get("LIFESTYLE_BOT_MAX_KEYWORDS", "3") or "3"), len(keywords)))
        for keyword in keywords[:max_keywords]:
            result = NewsPipeline(repository=news_repository(), collectors=lifestyle_news_collectors()).run(
                keyword=keyword,
                dry_run=True,
                limit=1,
            )
            summaries.append(
                {
                    "keyword": keyword,
                    "collected_count": result.get("collected_count", 0),
                    "saved_count": result.get("saved_count", 0),
                    "processed_count": result.get("processed_count", 0),
                    "selected_count": result.get("selected_count", 0),
                }
            )
        total_saved = sum(int(item.get("saved_count") or 0) for item in summaries)
        result_payload = {"keywords": summaries, "saved_count": total_saved}
        write_bot_log("lifestyle_bot", "COMPLETED", f"생활정보 봇 dry-run 수집 완료: 저장 {total_saved}건")
        set_one_shot_bot_status(
            LIFESTYLE_BOT_STATUS,
            LIFESTYLE_BOT_LOCK,
            "STOPPED",
            f"생활정보 후보 수집 완료: 저장 {total_saved}건",
            result=result_payload,
        )
    except Exception as exc:
        message = str(exc)[:500]
        write_bot_log("lifestyle_bot", "FAILED", f"생활정보 봇 수집 실패: {message[:180]}")
        set_one_shot_bot_status(LIFESTYLE_BOT_STATUS, LIFESTYLE_BOT_LOCK, "ERROR", "생활정보 봇 수집 실패", error_message=message)


def start_lifestyle_bot() -> dict[str, Any]:
    global LIFESTYLE_BOT_THREAD
    set_bot_switch_enabled(LIFESTYLE_BOT_MODULE_KEY, True)
    if LIFESTYLE_BOT_THREAD and LIFESTYLE_BOT_THREAD.is_alive():
        return lifestyle_bot_status()
    set_one_shot_bot_status(LIFESTYLE_BOT_STATUS, LIFESTYLE_BOT_LOCK, "STARTING", "생활정보 봇 시작 요청")
    LIFESTYLE_BOT_THREAD = threading.Thread(target=run_lifestyle_bot_once, name="workconnect-lifestyle-bot", daemon=True)
    LIFESTYLE_BOT_THREAD.start()
    return lifestyle_bot_status()


def stop_lifestyle_bot() -> dict[str, Any]:
    set_bot_switch_enabled(LIFESTYLE_BOT_MODULE_KEY, False)
    if LIFESTYLE_BOT_THREAD and LIFESTYLE_BOT_THREAD.is_alive():
        set_one_shot_bot_status(
            LIFESTYLE_BOT_STATUS,
            LIFESTYLE_BOT_LOCK,
            "STOPPING",
            "현재 수집 사이클 완료 후 중지됩니다.",
        )
        return lifestyle_bot_status()
    set_one_shot_bot_status(LIFESTYLE_BOT_STATUS, LIFESTYLE_BOT_LOCK, "STOPPED", "생활정보 봇 중지됨")
    return lifestyle_bot_status()


def run_immigration_bot_once() -> None:
    try:
        set_one_shot_bot_status(IMMIGRATION_BOT_STATUS, IMMIGRATION_BOT_LOCK, "RUNNING", "출입국 공식 공지 수집 중")
        result = immigration_service().collect(source="", limit=20)
        inserted = int(result.get("inserted_count") or 0)
        updated = int(result.get("updated_count") or 0)
        failed = int(result.get("failed_count") or 0)
        status = "ERROR" if failed and not (inserted or updated) else "STOPPED"
        message = f"출입국 수집 완료: 신규 {inserted}건, 갱신 {updated}건, 실패 {failed}건"
        set_one_shot_bot_status(
            IMMIGRATION_BOT_STATUS,
            IMMIGRATION_BOT_LOCK,
            status,
            message,
            result=result,
            error_message=result.get("message") if status == "ERROR" else None,
        )
    except Exception as exc:
        message = str(exc)[:500]
        set_one_shot_bot_status(IMMIGRATION_BOT_STATUS, IMMIGRATION_BOT_LOCK, "ERROR", "출입국 봇 수집 실패", error_message=message)


def start_immigration_bot() -> dict[str, Any]:
    global IMMIGRATION_BOT_THREAD
    set_bot_switch_enabled(IMMIGRATION_BOT_MODULE_KEY, True)
    if IMMIGRATION_BOT_THREAD and IMMIGRATION_BOT_THREAD.is_alive():
        return immigration_bot_status()
    set_one_shot_bot_status(IMMIGRATION_BOT_STATUS, IMMIGRATION_BOT_LOCK, "STARTING", "출입국 봇 시작 요청")
    IMMIGRATION_BOT_THREAD = threading.Thread(target=run_immigration_bot_once, name="workconnect-immigration-bot", daemon=True)
    IMMIGRATION_BOT_THREAD.start()
    return immigration_bot_status()


def stop_immigration_bot() -> dict[str, Any]:
    set_bot_switch_enabled(IMMIGRATION_BOT_MODULE_KEY, False)
    if IMMIGRATION_BOT_THREAD and IMMIGRATION_BOT_THREAD.is_alive():
        set_one_shot_bot_status(
            IMMIGRATION_BOT_STATUS,
            IMMIGRATION_BOT_LOCK,
            "STOPPING",
            "현재 수집 사이클 완료 후 중지됩니다.",
        )
        return immigration_bot_status()
    set_one_shot_bot_status(IMMIGRATION_BOT_STATUS, IMMIGRATION_BOT_LOCK, "STOPPED", "출입국 봇 중지됨")
    return immigration_bot_status()


def job_collector_settings() -> dict[str, Any]:
    return job_repository().settings()


def update_job_collector_settings(payload: dict[str, Any]) -> dict[str, Any]:
    return job_repository().update_settings(payload)


def format_job_log(log: dict[str, Any] | None) -> dict[str, Any] | None:
    if not log:
        return None
    return {
        "id": log.get("id"),
        "startedAt": log.get("started_at"),
        "endedAt": log.get("ended_at"),
        "pageFrom": log.get("page_from"),
        "pageTo": log.get("page_to"),
        "display": log.get("display"),
        "sortOrderBy": log.get("sort_order_by"),
        "totalReceived": log.get("total_received"),
        "insertedCount": log.get("inserted_count"),
        "updatedCount": log.get("updated_count"),
        "skippedCount": log.get("skipped_count"),
        "failedCount": log.get("failed_count"),
        "failedPages": log.get("failedPages", []),
        "status": log.get("status"),
        "errorMessage": log.get("error_message"),
    }


def clamp_query_int(query: dict[str, list[str]], key: str, default: int, minimum: int = 0, maximum: int = 100) -> int:
    try:
        value = int(query.get(key, [default])[0])
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def job_collector_logs(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    return [format_job_log(log) for log in job_repository().recent_logs(limit=limit, offset=offset)]


def job_posting_rows() -> list[dict[str, Any]]:
    return job_repository().list_postings(limit=200)


def occupation_dashboard() -> dict[str, Any]:
    return occupation_repository().dashboard()


def occupation_job_rows(query: dict[str, list[str]]) -> dict[str, Any]:
    return occupation_repository().list_jobs(
        page=clamp_query_int(query, "page", 1, minimum=1, maximum=100000),
        size=clamp_query_int(query, "size", 20, minimum=1, maximum=2000),
        keyword=str(query.get("keyword", [""])[0]).strip(),
        job_code=str(query.get("job_code", [""])[0]).strip(),
        active_yn=str(query.get("active_yn", [""])[0]).strip().upper(),
    )


def occupation_job_detail(item_id: int) -> dict[str, Any]:
    return occupation_repository().get_job(item_id)


def occupation_rows(query: dict[str, list[str]]) -> dict[str, Any]:
    return occupation_repository().list_occupations(
        page=clamp_query_int(query, "page", 1, minimum=1, maximum=100000),
        size=clamp_query_int(query, "size", 20, minimum=1, maximum=2000),
        keyword=str(query.get("keyword", [""])[0]).strip(),
        occupation_code=str(query.get("occupation_code", [""])[0]).strip(),
        active_yn=str(query.get("active_yn", [""])[0]).strip().upper(),
    )


def occupation_detail(item_id: int) -> dict[str, Any]:
    return occupation_repository().get_occupation(item_id)


def occupation_keyword_rows(query: dict[str, list[str]]) -> dict[str, Any]:
    return occupation_repository().list_keyword_mappings(
        page=clamp_query_int(query, "page", 1, minimum=1, maximum=100000),
        size=clamp_query_int(query, "size", 50, minimum=1, maximum=2000),
        keyword=str(query.get("keyword", [""])[0]).strip(),
        language_code=str(query.get("language_code", [""])[0]).strip(),
    )


def occupation_collect_logs(query: dict[str, list[str]]) -> list[dict[str, Any]]:
    return occupation_repository().collect_logs(
        limit=clamp_query_int(query, "limit", 50, minimum=1, maximum=500),
        offset=clamp_query_int(query, "offset", 0, minimum=0, maximum=10000),
    )


_IMMIGRATION_REPOSITORY: ImmigrationNoticeRepository | None = None
_IMMIGRATION_SERVICE: ImmigrationNoticeService | None = None
_CONTENT_REPOSITORY: ContentRepository | None = None
_CONTENT_SERVICE: ContentService | None = None


def immigration_repository() -> ImmigrationNoticeRepository:
    global _IMMIGRATION_REPOSITORY
    if _IMMIGRATION_REPOSITORY is None:
        _IMMIGRATION_REPOSITORY = ImmigrationNoticeRepository()
    return _IMMIGRATION_REPOSITORY


def immigration_service() -> ImmigrationNoticeService:
    global _IMMIGRATION_SERVICE
    if _IMMIGRATION_SERVICE is None:
        _IMMIGRATION_SERVICE = ImmigrationNoticeService(repository=immigration_repository())
    return _IMMIGRATION_SERVICE


def content_repository() -> ContentRepository:
    global _CONTENT_REPOSITORY
    if _CONTENT_REPOSITORY is None:
        _CONTENT_REPOSITORY = ContentRepository()
    return _CONTENT_REPOSITORY


def content_service() -> ContentService:
    global _CONTENT_SERVICE
    if _CONTENT_SERVICE is None:
        _CONTENT_SERVICE = ContentService(repository=content_repository())
    return _CONTENT_SERVICE


def module_enabled(module_key: str) -> bool:
    row = fetch_one("SELECT is_enabled FROM admin.module_config WHERE module_key = %s", (module_key,))
    return bool(row.get("is_enabled"))


def run_content_publish_cycle() -> dict[str, Any]:
    if content_bot_status().get("status") != "RUNNING":
        return {"ok": True, "status": "DISABLED", "message": "content bot is stopped; Facebook publishing is blocked"}
    review_result = run_content_generation_cycle(limit=5)
    return {
        "ok": review_result.get("ok", False),
        "sync": review_result.get("sync", {}),
        "review": review_result.get("telegram", {}),
        "publish": {"status": "BLOCKED", "message": "Facebook auto publish is disabled during Telegram review MVP."},
    }


def immigration_dashboard() -> dict[str, Any]:
    return immigration_repository().dashboard()


def content_dashboard() -> dict[str, Any]:
    return content_repository().dashboard()


def content_candidate_rows(query: dict[str, list[str]]) -> dict[str, Any]:
    return content_repository().list_candidates(
        {
            "page": clamp_query_int(query, "page", 1, minimum=1, maximum=100000),
            "size": clamp_query_int(query, "size", 20, minimum=1, maximum=200),
            "search": str(query.get("search", [""])[0]).strip(),
            "source_domain": str(query.get("source_domain", [""])[0]).strip(),
            "content_type": str(query.get("content_type", [""])[0]).strip(),
            "category": str(query.get("category", [""])[0]).strip(),
            "status": str(query.get("status", [""])[0]).strip(),
            "publishable": str(query.get("publishable", [""])[0]).strip(),
        }
    )


def content_candidate_detail(candidate_id: int) -> dict[str, Any]:
    return content_repository().get_candidate(candidate_id)


def immigration_notice_rows(query: dict[str, list[str]]) -> dict[str, Any]:
    params = {
        "page": clamp_query_int(query, "page", 1, minimum=1, maximum=100000),
        "size": clamp_query_int(query, "size", 20, minimum=1, maximum=200),
        "keyword": str(query.get("keyword", [""])[0]).strip(),
        "source_type": str(query.get("source_type", [""])[0]).strip(),
        "notice_type": str(query.get("notice_type", [""])[0]).strip(),
        "visa_type": str(query.get("visa_type", [""])[0]).strip(),
        "content_status": str(query.get("content_status", [""])[0]).strip(),
        "importance_min": str(query.get("importance_min", [""])[0]).strip(),
    }
    return immigration_repository().list_notices(params)


def immigration_notice_detail(notice_id: int) -> dict[str, Any]:
    return immigration_repository().get_notice(notice_id)


def immigration_collect(payload: dict[str, Any], source: str = "") -> dict[str, Any]:
    limit = int(payload.get("limit") or 20) if isinstance(payload, dict) else 20
    return immigration_service().collect(source=source, limit=max(1, min(limit, 100)))


def run_occupation_job_collection(payload: dict[str, Any]) -> dict[str, Any]:
    return job_info_collector().run(
        page_from=int(payload.get("pageFrom") or 1),
        page_to=int(payload.get("pageTo") or payload.get("pageFrom") or 1),
        size=int(payload.get("size") or 100),
    )


def run_occupation_info_collection(payload: dict[str, Any]) -> dict[str, Any]:
    return occupation_info_collector().run(
        page_from=int(payload.get("pageFrom") or 1),
        page_to=int(payload.get("pageTo") or payload.get("pageFrom") or 1),
        size=int(payload.get("size") or 100),
    )


def job_collector_status() -> dict[str, Any]:
    settings = job_collector_settings()
    latest = format_job_log(job_repository().latest_log())
    status = JOB_COLLECTOR_STATUS["status"]
    scheduler_enabled = bool(settings.get("schedulerEnabled"))
    if JOB_COLLECTOR_THREAD and JOB_COLLECTOR_THREAD.is_alive():
        status = "RUNNING"
    elif status == "RUNNING":
        status = "STOPPED"
        JOB_COLLECTOR_STATUS["status"] = "STOPPED"
    if JOB_COLLECTOR_SCHEDULER_THREAD and JOB_COLLECTOR_SCHEDULER_THREAD.is_alive():
        scheduler_enabled = True
    return {
        "status": status,
        "lastRunAt": latest.get("startedAt") if latest else None,
        "nextRunAt": JOB_COLLECTOR_STATUS.get("nextRunAt"),
        "schedulerEnabled": scheduler_enabled,
        "authKeyConfigured": bool(os.environ.get("EMPLOYEE_24_OPEN_API_EMPLOYMENT_KEY", "").strip()),
        "settings": settings,
        "latest": latest,
        "lastErrorMessage": JOB_COLLECTOR_STATUS.get("lastErrorMessage") or (latest or {}).get("errorMessage"),
    }


def run_job_collection_now(smoke: bool = False) -> dict[str, Any]:
    with JOB_COLLECTOR_LOCK:
        JOB_COLLECTOR_STATUS.update({"status": "RUNNING", "lastErrorMessage": None})
        settings = job_collector_settings()
        try:
            if smoke:
                result = job_collector().run(display=10, start_page_from=1, start_page_to=1, sort_order_by="DESC", delay_seconds=0.5)
            else:
                result = job_collector().run(
                    display=int(settings["display"]),
                    start_page_from=int(settings["startPageFrom"]),
                    start_page_to=int(settings["startPageTo"]),
                    sort_order_by=str(settings["sortOrderBy"]),
                    delay_seconds=0.7,
                )
            JOB_COLLECTOR_STATUS["status"] = "ERROR" if result["status"] == "FAILED" else "STOPPED"
            JOB_COLLECTOR_STATUS["lastErrorMessage"] = result.get("errorMessage")
            return result
        except Exception as exc:
            JOB_COLLECTOR_STATUS.update({"status": "ERROR", "lastErrorMessage": str(exc)[:300]})
            raise


def start_job_collection(smoke: bool = False) -> dict[str, Any]:
    global JOB_COLLECTOR_THREAD
    if JOB_COLLECTOR_THREAD and JOB_COLLECTOR_THREAD.is_alive():
        return {"accepted": False, "message": "채용정보 수집이 이미 실행 중입니다.", "status": job_collector_status()}

    def runner() -> None:
        try:
            run_job_collection_now(smoke=smoke)
        except Exception:
            return

    JOB_COLLECTOR_THREAD = threading.Thread(target=runner, name="workconnect-job-collector", daemon=True)
    JOB_COLLECTOR_THREAD.start()
    JOB_COLLECTOR_STATUS.update({"status": "RUNNING", "lastErrorMessage": None})
    return {"accepted": True, "message": "채용정보 수집을 시작했습니다.", "status": job_collector_status()}


def job_scheduler_loop() -> None:
    while not JOB_COLLECTOR_SCHEDULER_STOP.is_set():
        settings = job_collector_settings()
        if not settings.get("schedulerEnabled"):
            break
        interval_minutes = int(settings["intervalMinutes"])
        next_run = datetime.now(timezone.utc) + timedelta(minutes=interval_minutes)
        JOB_COLLECTOR_STATUS["nextRunAt"] = next_run.isoformat()
        if JOB_COLLECTOR_SCHEDULER_STOP.wait(max(60, interval_minutes * 60)):
            break
        try:
            run_job_collection_now(smoke=False)
        except Exception:
            pass
    job_repository().set_scheduler_enabled(False)
    JOB_COLLECTOR_STATUS.update({"schedulerEnabled": False, "nextRunAt": None})


def start_job_scheduler() -> dict[str, Any]:
    global JOB_COLLECTOR_SCHEDULER_THREAD
    if JOB_COLLECTOR_SCHEDULER_THREAD and JOB_COLLECTOR_SCHEDULER_THREAD.is_alive():
        return job_collector_status()
    JOB_COLLECTOR_SCHEDULER_STOP.clear()
    job_repository().set_scheduler_enabled(True)
    JOB_COLLECTOR_STATUS["schedulerEnabled"] = True
    JOB_COLLECTOR_SCHEDULER_THREAD = threading.Thread(target=job_scheduler_loop, name="workconnect-job-collector-scheduler", daemon=True)
    JOB_COLLECTOR_SCHEDULER_THREAD.start()
    return job_collector_status()


def stop_job_scheduler() -> dict[str, Any]:
    JOB_COLLECTOR_SCHEDULER_STOP.set()
    job_repository().set_scheduler_enabled(False)
    JOB_COLLECTOR_STATUS.update({"schedulerEnabled": False, "nextRunAt": None})
    return job_collector_status()


def is_llama_connected(endpoint: str) -> bool:
    try:
        with urlopen(f"{endpoint.rstrip('/')}/api/tags", timeout=3) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def llama_config() -> tuple[bool, str, str]:
    enabled = os.environ.get("LOCAL_LLAMA_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
    endpoint = os.environ.get("LOCAL_LLAMA_ENDPOINT", os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
    model = os.environ.get("LOCAL_LLAMA_MODEL") or os.environ.get("LOCAL_MODEL_GENERAL") or os.environ.get("LOCAL_MODEL_MASTER") or "llama3.1"
    return enabled, endpoint, model


def is_managed_llama_endpoint(endpoint: str) -> bool:
    parsed = urlparse(endpoint or "")
    host = (parsed.hostname or "").lower()
    return host in {"", "localhost", "127.0.0.1", "::1"}


def llama_base_state(enabled: bool, endpoint: str, model: str) -> dict[str, Any]:
    managed = is_managed_llama_endpoint(endpoint)
    return {
        "enabled": enabled,
        "endpoint": endpoint,
        "model": model,
        "managed": managed,
        "server_type": "managed-local" if managed else "external",
        "manual_off": LLAMA_MANUAL_OFF,
    }


def unload_llama_model(endpoint: str, model: str) -> None:
    if not model:
        return
    payload = json.dumps({"model": model, "prompt": "", "stream": False, "keep_alive": 0}).encode("utf-8")
    request = Request(
        f"{endpoint.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5):
            return
    except Exception:
        return


def should_stop_llama_server_on_off() -> bool:
    return os.environ.get("LOCAL_LLAMA_STOP_SERVER_ON_OFF", "true").lower() in {"1", "true", "yes", "on"}


def llama_process_env() -> dict[str, str]:
    env = os.environ.copy()
    defaults = {
        "OLLAMA_KEEP_ALIVE": "5s",
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_MAX_LOADED_MODELS": "1",
    }
    for key, value in defaults.items():
        env.setdefault(key, value)
    return env


def terminate_local_ollama_server() -> bool:
    terminated = False
    if LLAMA_PROCESS and LLAMA_PROCESS.poll() is None:
        try:
            LLAMA_PROCESS.terminate()
            LLAMA_PROCESS.wait(timeout=5)
            terminated = True
        except Exception:
            try:
                LLAMA_PROCESS.kill()
                terminated = True
            except Exception:
                pass
    if not should_stop_llama_server_on_off():
        return terminated
    try:
        subprocess.run(
            ["taskkill", "/IM", "ollama.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        )
        terminated = True
    except Exception:
        pass
    return terminated


def ensure_llama(start_command: bool = True, user_requested: bool = False) -> dict[str, Any]:
    global LLAMA_PROCESS, LLAMA_MANUAL_OFF
    enabled, endpoint, model = llama_config()
    base = llama_base_state(enabled, endpoint, model)
    LLAMA_STATE.update(base)
    if not enabled:
        LLAMA_STATE.update({"connected": False, "status": "DISABLED", "message": "LLaMA disabled by configuration."})
        return LLAMA_STATE
    if LLAMA_MANUAL_OFF and not user_requested:
        message = "External LLaMA connection is off." if not base["managed"] else "Local LLaMA is stopped."
        LLAMA_STATE.update({"connected": False, "status": "DISABLED", "message": message})
        return LLAMA_STATE
    if start_command and not user_requested and os.environ.get("LOCAL_LLAMA_AUTO_START", "false").lower() not in {"1", "true", "yes", "on"}:
        if is_llama_connected(endpoint):
            message = "External LLaMA connected." if not base["managed"] else "Local LLaMA connected."
            LLAMA_STATE.update({"connected": True, "status": "CONNECTED", "message": message})
            return LLAMA_STATE
        LLAMA_STATE.update({"connected": False, "status": "STANDBY", "message": "LLaMA auto-start disabled. Use reconnect/start when needed."})
        return LLAMA_STATE
    if user_requested:
        LLAMA_MANUAL_OFF = False
        LLAMA_STATE.update({"manual_off": False})
    if is_llama_connected(endpoint):
        message = "External LLaMA connected." if not base["managed"] else "Local LLaMA connected."
        LLAMA_STATE.update({"connected": True, "status": "CONNECTED", "message": message})
        return LLAMA_STATE
    if start_command and base["managed"]:
        command = os.environ.get("LOCAL_LLAMA_COMMAND", "ollama serve")
        LLAMA_STATE.update({"connected": False, "status": "STARTING", "message": "Starting local LLaMA process."})
        try:
            if not LLAMA_PROCESS or LLAMA_PROCESS.poll() is not None:
                LLAMA_PROCESS = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=llama_process_env())
            for _ in range(10):
                time.sleep(1)
                if is_llama_connected(endpoint):
                    LLAMA_STATE.update({"connected": True, "status": "CONNECTED", "message": "Local LLaMA connected."})
                    return LLAMA_STATE
        except Exception as exc:
            LLAMA_STATE.update({"connected": False, "status": "ERROR", "message": f"Failed to start local LLaMA: {str(exc)[:120]}"})
            return LLAMA_STATE
    message = "External LLaMA is not reachable." if not base["managed"] else "Local LLaMA is not connected."
    LLAMA_STATE.update({"connected": False, "status": "DISCONNECTED", "message": message})
    return LLAMA_STATE


def stop_llama() -> dict[str, Any]:
    global LLAMA_PROCESS, LLAMA_MANUAL_OFF
    enabled, endpoint, model = llama_config()
    base = llama_base_state(enabled, endpoint, model)
    LLAMA_MANUAL_OFF = True
    LLAMA_STATE.update({**base, "manual_off": True, "connected": False, "status": "STOPPING", "message": "Stopping LLaMA connection."})
    if base["managed"]:
        unload_llama_model(endpoint, model)
        terminated = terminate_local_ollama_server()
        LLAMA_PROCESS = None
        connected = is_llama_connected(endpoint)
        if connected:
            message = "Local LLaMA model unload requested, but the local Ollama server is still reachable."
        elif terminated:
            message = "Local LLaMA stopped and local Ollama server process was terminated."
        else:
            message = "Local LLaMA stopped."
        LLAMA_STATE.update({"connected": False, "status": "DISABLED", "message": message})
    else:
        LLAMA_STATE.update({"connected": False, "status": "DISABLED", "message": "External LLaMA connection disabled. Remote server was not stopped."})
    return LLAMA_STATE

def json_ready(value: Any) -> Any:
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def sanitize_news_url_fields(row: dict[str, Any]) -> dict[str, Any]:
    row["source_url"] = safe_url(row.get("source_url") or "")
    row["canonical_url"] = safe_url(row.get("canonical_url") or "")
    return row


def client_ip(handler: BaseHTTPRequestHandler) -> str:
    forwarded = handler.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    real_ip = handler.headers.get("X-Real-IP", "").strip()
    if real_ip:
        return real_ip
    return handler.client_address[0]


def callback_secret() -> str:
    return (
        os.environ.get("ADMIN_TELEGRAM_CALLBACK_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    )


def callback_signature(session_id: int, action: str) -> str:
    secret = callback_secret()
    if not secret:
        return ""
    digest = hmac.new(secret.encode("utf-8"), f"{session_id}:{action}".encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")[:24]


def build_callback_data(session_id: int, action: str) -> str:
    return f"admin_auth:{action}:{session_id}:{callback_signature(session_id, action)}"


def parse_callback_data(data: str) -> tuple[str, int, str] | None:
    parts = data.split(":")
    if len(parts) != 4 or parts[0] != "admin_auth":
        return None
    action = parts[1]
    if action not in {"approve", "reject"}:
        return None
    try:
        session_id = int(parts[2])
    except ValueError:
        return None
    return action, session_id, parts[3]


def content_score_signature(candidate_id: int, score: int) -> str:
    secret = callback_secret()
    if not secret:
        return ""
    digest = hmac.new(secret.encode("utf-8"), f"content_score:{candidate_id}:{score}".encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")[:12]


def build_content_score_callback(candidate_id: int, score: int) -> str:
    return f"content_score:{candidate_id}:{score}:{content_score_signature(candidate_id, score)}"


def parse_content_score_callback(data: str) -> tuple[int, int, str] | None:
    parts = data.split(":")
    if len(parts) != 4 or parts[0] != "content_score":
        return None
    try:
        candidate_id = int(parts[1])
        score = int(parts[2])
    except ValueError:
        return None
    if score < 0 or score > 100:
        return None
    return candidate_id, score, parts[3]


def verify_callback_secret(handler: BaseHTTPRequestHandler, parsed_url) -> bool:
    secret = os.environ.get("ADMIN_TELEGRAM_CALLBACK_TOKEN", "").strip() or os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if not secret:
        return True
    query_token = parse_qs(parsed_url.query).get("token", [""])[0]
    header_token = handler.headers.get("X-Telegram-Bot-Api-Secret-Token", "") or handler.headers.get("X-Admin-Telegram-Secret", "")
    return hmac.compare_digest(secret, query_token) or hmac.compare_digest(secret, header_token)


def telegram_api(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return {"ok": False, "description": "Telegram Bot Token이 설정되어 있지 않습니다."}
    request = Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(detail)
            return {"ok": False, "description": payload.get("description") or "Telegram 요청 전송에 실패했습니다."}
        except json.JSONDecodeError:
            return {"ok": False, "description": f"Telegram 요청 전송에 실패했습니다. HTTP {exc.code}"}
    except URLError:
        return {"ok": False, "description": "Telegram 서버에 연결할 수 없습니다."}
    except Exception:
        return {"ok": False, "description": "Telegram 요청 전송에 실패했습니다."}


def telegram_api_multipart(method: str, fields: dict[str, Any], file_field: str, file_path: Path) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return {"ok": False, "description": "Telegram Bot Token is not configured."}
    if not file_path.exists() or not file_path.is_file():
        return {"ok": False, "description": "Telegram image file is missing."}

    boundary = "----WorkConnectTelegram" + hashlib.sha256(f"{time.time()}:{file_path.name}".encode("utf-8")).hexdigest()[:16]
    body = bytearray()
    for key, value in fields.items():
        if value is None:
            continue
        field_value = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        body.extend(field_value.encode("utf-8"))
        body.extend(b"\r\n")

    filename = file_path.name.replace('"', "")
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        (
            f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'
            "Content-Type: image/png\r\n\r\n"
        ).encode("utf-8")
    )
    body.extend(file_path.read_bytes())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    request = Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(detail)
            return {"ok": False, "description": payload.get("description") or "Telegram multipart request failed."}
        except json.JSONDecodeError:
            return {"ok": False, "description": f"Telegram multipart request failed. HTTP {exc.code}"}
    except URLError:
        return {"ok": False, "description": "Could not connect to Telegram server."}
    except Exception:
        return {"ok": False, "description": "Telegram multipart request failed."}


def telegram_admin_chat_id() -> str:
    return os.environ.get("TELEGRAM_OWNER_CHAT_ID", "").strip() or os.environ.get("TELEGRAM_CHAT_ID", "").strip()


def telegram_owner_user_id() -> str:
    return os.environ.get("TELEGRAM_OWNER_USER_ID", "").strip()


def send_approval_request(session: dict[str, Any]) -> dict[str, Any]:
    if session.get("telegram_message_id"):
        return {"ok": True, "message_id": int(session["telegram_message_id"]), "error_message": ""}

    chat_id = telegram_admin_chat_id()
    if not chat_id:
        return {"ok": False, "message_id": None, "error_message": "Telegram 관리자 Chat ID가 설정되어 있지 않습니다."}

    session_id = int(session["id"])
    message = "\n".join(
        [
            "관리자 페이지 접속 요청이 있습니다.",
            f"장치 ID: {session['device_id']}",
            f"IP: {session['ip_address']}",
            f"브라우저: {session['user_agent']}",
            "승인하시겠습니까?",
        ]
    )
    payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "승인", "callback_data": build_callback_data(session_id, "approve")},
                    {"text": "거부", "callback_data": build_callback_data(session_id, "reject")},
                ]
            ]
        },
    }
    result = telegram_api("sendMessage", payload)
    if not result.get("ok"):
        return {"ok": False, "message_id": None, "error_message": result.get("description") or "Telegram 승인 메시지 전송에 실패했습니다."}
    message_id = result.get("result", {}).get("message_id")
    if message_id:
        execute_one(
            """
            UPDATE admin.admin_login_session
            SET telegram_message_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
            """,
            (message_id, session_id),
        )
    return {"ok": bool(message_id), "message_id": message_id, "error_message": "" if message_id else "Telegram 메시지 ID를 확인할 수 없습니다."}


def apply_telegram_auth_callback(callback_query: dict[str, Any]) -> dict[str, Any]:
    data = str(callback_query.get("data") or "")
    parsed = parse_callback_data(data)
    if not parsed:
        return {"ok": False, "status": None, "message": "처리할 수 없는 승인 요청입니다."}

    action, session_id, signature = parsed
    expected = callback_signature(session_id, action)
    if not expected or not hmac.compare_digest(expected, signature):
        return {"ok": False, "status": None, "message": "승인 요청 검증에 실패했습니다."}

    owner_id = telegram_owner_user_id()
    from_user_id = str((callback_query.get("from") or {}).get("id") or "")
    if owner_id and from_user_id != owner_id:
        return {"ok": False, "status": None, "message": "허가되지 않은 Telegram 사용자입니다."}

    status = APPROVED if action == "approve" else REJECTED
    time_column = "approved_at" if status == APPROVED else "rejected_at"
    row = execute_one(
        f"""
        UPDATE admin.admin_login_session
        SET status = %s,
            {time_column} = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND status = 'PENDING'
        RETURNING id, status
        """,
        (status, session_id),
    )
    return {
        "ok": True,
        "status": row.get("status", status),
        "message": "승인되었습니다." if status == APPROVED else "거부되었습니다.",
    }


def apply_telegram_content_callback(callback_query: dict[str, Any]) -> dict[str, Any]:
    data = str(callback_query.get("data") or "")
    parsed = parse_content_score_callback(data)
    if not parsed:
        return {"ok": False, "status": None, "message": "처리할 수 없는 콘텐츠 점수 요청입니다."}

    candidate_id, score, signature = parsed
    expected = content_score_signature(candidate_id, score)
    if not expected or not hmac.compare_digest(expected, signature):
        return {"ok": False, "status": None, "message": "콘텐츠 점수 요청 검증에 실패했습니다."}

    owner_id = telegram_owner_user_id()
    from_user_id = str((callback_query.get("from") or {}).get("id") or "")
    if owner_id and from_user_id != owner_id:
        return {"ok": False, "status": None, "message": "허가되지 않은 Telegram 사용자입니다."}

    candidate = content_service().apply_operator_score(
        candidate_id,
        score,
        comment=f"Telegram operator score {score}",
    )
    if not candidate:
        return {"ok": False, "status": None, "message": "콘텐츠 후보를 찾을 수 없습니다."}
    return {
        "ok": True,
        "status": candidate.get("status"),
        "candidate_id": candidate_id,
        "score": score,
        "message": f"콘텐츠 점수 {score}점이 반영되었습니다.",
    }


def apply_telegram_callback(callback_query: dict[str, Any]) -> dict[str, Any]:
    data = str(callback_query.get("data") or "")
    if data.startswith("content_score:"):
        return apply_telegram_content_callback(callback_query)
    return apply_telegram_auth_callback(callback_query)


def start_telegram_update_poller() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = telegram_admin_chat_id()
    if not token or not chat_id:
        print("[telegram] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_OWNER_CHAT_ID/TELEGRAM_CHAT_ID가 없어 승인 폴링을 건너뜁니다.", flush=True)
        return

    def poll() -> None:
        offset = 0
        telegram_api("deleteWebhook", {"drop_pending_updates": False})
        print("[telegram] 관리자 승인 버튼 폴링을 시작합니다.", flush=True)
        while True:
            result = telegram_api("getUpdates", {"offset": offset, "timeout": 25, "allowed_updates": ["callback_query"]})
            if not result.get("ok"):
                time.sleep(5)
                continue
            for update in result.get("result", []):
                offset = max(offset, int(update.get("update_id", 0)) + 1)
                callback_query = update.get("callback_query")
                if not callback_query:
                    continue
                callback_result = apply_telegram_callback(callback_query)
                callback_id = callback_query.get("id")
                if callback_id:
                    telegram_api(
                        "answerCallbackQuery",
                        {"callback_query_id": callback_id, "text": callback_result.get("message") or "처리되었습니다."},
                    )

    thread = threading.Thread(target=poll, name="telegram-admin-auth-poller", daemon=True)
    thread.start()


def find_approved_session(device_id: str, ip_address: str, user_agent: str) -> dict[str, Any]:
    return fetch_one(
        """
        UPDATE admin.admin_login_session
        SET ip_address = %s,
            user_agent = %s,
            last_seen_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = (
            SELECT id
            FROM admin.admin_login_session
            WHERE device_id = %s AND status = 'APPROVED'
            ORDER BY approved_at DESC NULLS LAST, id DESC
            LIMIT 1
        )
        RETURNING id, device_id, ip_address, user_agent, status, telegram_message_id,
                  requested_at, approved_at, rejected_at, logged_out_at, last_seen_at
        """,
        (ip_address, user_agent, device_id),
    )


def find_or_create_pending_session(device_id: str, ip_address: str, user_agent: str) -> dict[str, Any]:
    execute_one(
        """
        UPDATE admin.admin_login_session
        SET status = 'LOGGED_OUT',
            logged_out_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE device_id = %s
          AND ip_address = %s
          AND user_agent = %s
          AND status = 'PENDING'
          AND requested_at < CURRENT_TIMESTAMP - (%s || ' minutes')::interval
        RETURNING id
        """,
        (device_id, ip_address, user_agent, PENDING_TIMEOUT_MINUTES),
    )
    pending = fetch_one(
        """
        SELECT id, device_id, ip_address, user_agent, status, telegram_message_id,
               requested_at, approved_at, rejected_at, logged_out_at, last_seen_at
        FROM admin.admin_login_session
        WHERE device_id = %s AND ip_address = %s AND user_agent = %s AND status = 'PENDING'
        ORDER BY requested_at DESC, id DESC
        LIMIT 1
        """,
        (device_id, ip_address, user_agent),
    )
    if pending:
        return pending
    return execute_one(
        """
        INSERT INTO admin.admin_login_session(device_id, ip_address, user_agent, status, requested_at, last_seen_at)
        VALUES (%s, %s, %s, 'PENDING', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id, device_id, ip_address, user_agent, status, telegram_message_id,
                  requested_at, approved_at, rejected_at, logged_out_at, last_seen_at
        """,
        (device_id, ip_address, user_agent),
    )


def invalidate_login_sessions(device_id: str, ip_address: str, user_agent: str) -> None:
    execute_one(
        """
        UPDATE admin.admin_login_session
        SET status = 'LOGGED_OUT',
            logged_out_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE device_id = %s
          AND ip_address = %s
          AND user_agent = %s
          AND status IN ('APPROVED', 'PENDING')
        RETURNING id
        """,
        (device_id, ip_address, user_agent),
    )


def session_status(session_id: int) -> dict[str, Any]:
    execute_one(
        """
        UPDATE admin.admin_login_session
        SET status = 'LOGGED_OUT',
            logged_out_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND status = 'PENDING'
          AND requested_at < CURRENT_TIMESTAMP - (%s || ' minutes')::interval
        RETURNING id
        """,
        (session_id, PENDING_TIMEOUT_MINUTES),
    )
    return fetch_one(
        """
        SELECT id, device_id, ip_address, user_agent, status,
               requested_at, approved_at, rejected_at, logged_out_at, last_seen_at
        FROM admin.admin_login_session
        WHERE id = %s
        """,
        (session_id,),
    )


def module_rows() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT module_key, module_group, module_name, description, is_enabled, is_required, run_order
        FROM admin.module_config
        ORDER BY run_order, module_key
        """
    )


def dashboard_summary() -> dict[str, Any]:
    pipeline = NewsPipeline(repository=news_repository(), collectors=[])
    window_start = pipeline.publish_window_start().isoformat()
    candidate_counts = fetch_one_with_timeout(
        """
        SELECT
            (SELECT COUNT(id)::int FROM social_news.candidate) AS candidate_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE publish_status = 'READY_TO_PUBLISH'
                  AND COALESCE(last_seen_at, collected_at) >= %s
                  AND COALESCE(post_expired, FALSE) = FALSE
                  AND COALESCE(is_representative, TRUE) = TRUE
                  AND COALESCE(is_sensitive, FALSE) = FALSE
                  AND published_at IS NULL
                  AND COALESCE(facebook_post_url, '') = ''
                  AND COALESCE(risk_level, '') != 'HIGH'
            ) AS today_ready_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE COALESCE(last_seen_at, collected_at) < %s
                  AND publish_status = 'POST_EXPIRED'
            ) AS previous_post_expired_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE publish_status IN ('POSTED', 'PUBLISHED', 'DRY_RUN_PUBLISHED', 'NOTIFIED', 'DRY_RUN_NOTIFIED')
                   OR status IN ('POSTED', 'PUBLISHED', 'DRY_RUN_PUBLISHED', 'NOTIFIED', 'DRY_RUN_NOTIFIED')
            ) AS published_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE COALESCE(post_expired, FALSE) = TRUE
                   OR publish_status = 'POST_EXPIRED'
            ) AS post_expired_count,
            (SELECT COUNT(*)::int FROM social_news.candidate WHERE status = 'DUPLICATE') AS duplicate_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE status = 'FAILED'
                   OR publish_status IN ('FAILED', 'FAILED_RETRYABLE', 'FAILED_REPOST_REQUIRED', 'FAILED_PERMISSION')
            ) AS failed_count,
            (SELECT COUNT(*)::int FROM social_news.candidate WHERE COALESCE(last_seen_at, collected_at) >= %s) AS today_article_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE COALESCE(last_seen_at, collected_at) >= %s
                  AND COALESCE(post_expired, FALSE) = FALSE
                  AND published_at IS NULL
                  AND COALESCE(facebook_post_url, '') = ''
                  AND COALESCE(publish_status, '') NOT IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'POST_EXPIRED', 'ARCHIVED', 'AUTO_RETRY_BLOCKED', 'SKIPPED', 'DUPLICATE', 'DUPLICATE_SKIPPED')
                  AND COALESCE(status, '') NOT IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'POST_EXPIRED', 'ARCHIVED', 'AUTO_RETRY_BLOCKED', 'SKIPPED', 'DUPLICATE', 'DUPLICATE_SKIPPED')
            ) AS today_unposted_count,
            (
                SELECT ROUND(AVG(evaluation_score) FILTER (WHERE evaluation_score > 0), 2)
                FROM social_news.candidate
                WHERE COALESCE(last_seen_at, collected_at) >= %s
            ) AS avg_score,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE publish_status = 'READY_TO_PUBLISH'
                  AND COALESCE(post_expired, FALSE) = FALSE
                  AND COALESCE(is_representative, TRUE) = TRUE
                  AND COALESCE(is_sensitive, FALSE) = FALSE
                  AND published_at IS NULL
                  AND COALESCE(facebook_post_url, '') = ''
                  AND COALESCE(risk_level, '') != 'HIGH'
            ) AS ready_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE COALESCE(last_seen_at, collected_at) >= %s
                  AND publish_status = 'FAILED_RETRYABLE'
                  AND COALESCE(post_expired, FALSE) = FALSE
                  AND published_at IS NULL
            ) AS retryable_count,
            (
                SELECT COUNT(*)::int
                FROM social_news.candidate
                WHERE published_at >= %s
                  AND publish_status IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED')
            ) AS posted_today_count,
            (SELECT COUNT(*)::int FROM social_news.candidate WHERE COALESCE(last_seen_at, collected_at) >= %s AND content_priority_group = 'PRIMARY') AS primary_candidate_count,
            (SELECT COUNT(*)::int FROM social_news.candidate WHERE COALESCE(last_seen_at, collected_at) >= %s AND content_priority_group = 'SECONDARY') AS secondary_candidate_count,
            (SELECT COUNT(*)::int FROM social_news.candidate WHERE COALESCE(last_seen_at, collected_at) >= %s AND content_priority_group = 'TERTIARY') AS tertiary_candidate_count
        """,
        (
            window_start,
            window_start,
            window_start,
            window_start,
            window_start,
            window_start,
            window_start,
            window_start,
            window_start,
            window_start,
        ),
        timeout_ms=20000,
    )
    publish_metrics: dict[str, Any] = {}
    cooldown = pipeline.publish_cooldown_info()
    category_metrics: dict[str, Any] = {}
    recent_category_rows = fetch_all(
        """
        SELECT COALESCE(content_priority_group, 'PRIMARY') AS content_priority_group, COUNT(*)::int AS published_count
        FROM social_news.candidate
        WHERE published_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
          AND (publish_status IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED')
               OR status IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED'))
        GROUP BY COALESCE(content_priority_group, 'PRIMARY')
        """
    )
    module_counts = fetch_one(
        """
        SELECT
            COUNT(*)::int AS module_count,
            COUNT(*) FILTER (WHERE is_enabled)::int AS enabled_module_count,
            COUNT(*) FILTER (WHERE NOT is_enabled)::int AS disabled_module_count
        FROM admin.module_config
        """
    )
    latest_cycle = fetch_one(
        """
        SELECT status, dry_run, started_at, ended_at
        FROM social_news.pipeline_cycle
        ORDER BY started_at DESC
        LIMIT 1
        """
    )
    return {
        **candidate_counts,
        **publish_metrics,
        **category_metrics,
        "recent_24h_category_ratio": {row["content_priority_group"]: row["published_count"] for row in recent_category_rows},
        "target_publish_ratio": "PRIMARY:SECONDARY 2:1 dynamic",
        **module_counts,
        "latest_cycle": latest_cycle,
        "cooldown": cooldown,
        "cooldown_active": cooldown.get("active", False),
        "next_publish_at": cooldown.get("next_publish_at", ""),
        "publish_window_start": window_start,
    }


def cached_dashboard_summary(ttl_seconds: int = 15) -> dict[str, Any]:
    now = time.monotonic()
    cached = DASHBOARD_SUMMARY_CACHE.get("payload")
    if isinstance(cached, dict) and float(DASHBOARD_SUMMARY_CACHE.get("expires_at") or 0.0) > now:
        return cached
    with DASHBOARD_SUMMARY_LOCK:
        now = time.monotonic()
        cached = DASHBOARD_SUMMARY_CACHE.get("payload")
        if isinstance(cached, dict) and float(DASHBOARD_SUMMARY_CACHE.get("expires_at") or 0.0) > now:
            return cached
        payload = dashboard_summary()
        DASHBOARD_SUMMARY_CACHE["payload"] = payload
        DASHBOARD_SUMMARY_CACHE["expires_at"] = time.monotonic() + max(1, int(ttl_seconds))
        return payload


def candidate_rows(query: dict[str, list[str]] | None = None) -> dict[str, Any]:
    query = query or {}
    page = clamp_query_int(query, "page", 1, minimum=1, maximum=100000)
    size = clamp_query_int(query, "size", 10, minimum=1, maximum=100)
    include_duplicates = str(query.get("includeDuplicates", ["false"])[0]).lower() in {"1", "true", "yes", "on"}
    status = str(query.get("status", [""])[0]).strip()
    search = str(query.get("search", [""])[0]).strip()
    content_category = str(query.get("content_category", [""])[0]).strip()
    priority_group = str(query.get("priority_group", [""])[0]).strip().upper()
    sensitive = str(query.get("sensitive", [""])[0]).strip().lower()
    offset = (page - 1) * size
    where = []
    params: list[Any] = []
    if not include_duplicates:
        where.append("COALESCE(candidate.is_representative, TRUE) = TRUE")
    if status:
        where.append("(candidate.status = %s OR candidate.publish_status = %s)")
        params.extend([status, status])
    if content_category:
        where.append("candidate.content_category = %s")
        params.append(content_category)
    if priority_group:
        where.append("candidate.content_priority_group = %s")
        params.append(priority_group)
    if sensitive in {"1", "true", "yes", "on"}:
        where.append("COALESCE(candidate.is_sensitive, FALSE) = TRUE")
    elif sensitive in {"0", "false", "no", "off"}:
        where.append("COALESCE(candidate.is_sensitive, FALSE) = FALSE")
    if search:
        where.append(
            """
            (
                candidate.title ILIKE %s OR candidate.source_name ILIKE %s OR candidate.source_type ILIKE %s
                OR candidate.source_url ILIKE %s OR candidate.similarity_key ILIKE %s
            )
            """
        )
        term = f"%{search}%"
        params.extend([term, term, term, term, term])
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    total = fetch_one(f"SELECT COUNT(*)::int AS total_count FROM social_news.candidate candidate {where_sql}", tuple(params)).get("total_count", 0)
    rows = fetch_all(
        f"""
        SELECT candidate.id, candidate.category, candidate.content_category, candidate.content_priority_group, candidate.settlement_relevance_score,
               candidate.practical_value_score, candidate.category_rotation_score, candidate.content_potential_score,
               candidate.category_selection_reason, candidate.is_sensitive, candidate.review_required_reason,
               'KR' AS region, candidate.title, candidate.source_name, candidate.source_type, candidate.source_url, candidate.canonical_url,
               candidate.google_news_url, candidate.publisher_name, candidate.evaluation_score,
               candidate.duplicate_risk_score, candidate.status, candidate.publish_status, candidate.short_summary, candidate.selection_reason, candidate.skip_reason, candidate.fail_reason,
               candidate.collected_at, candidate.facebook_post_url, candidate.facebook_post_id, candidate.publish_cycle_id AS cycle_id,
               candidate.post_expired, candidate.post_expired_at, candidate.post_expired_reason, candidate.image_url,
               candidate.related_source_count, candidate.duplicate_count, candidate.group_item_count, candidate.last_seen_at, candidate.is_representative,
               candidate.representative_candidate_id, candidate.content_fetch_status, candidate.content_fetch_error,
               candidate.normalized_item_id, candidate.similarity_key,
               content_row.id AS content_candidate_id,
               content_row.status AS content_status,
               (content_row.status = 'POSTED') AS content_posted_yn,
               content_row.facebook_post_url AS content_facebook_post_url
        FROM social_news.candidate candidate
        LEFT JOIN content.content_candidate content_row
          ON content_row.raw_ref_table = 'social_news.candidate'
         AND content_row.raw_ref_id = candidate.id
        {where_sql}
        ORDER BY COALESCE(candidate.last_seen_at, candidate.collected_at) DESC, candidate.id DESC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [size, offset]),
    )
    return {"items": [sanitize_news_url_fields(row) for row in rows], "total_count": total, "page": page, "size": size}


def lifestyle_candidate_rows(query: dict[str, list[str]] | None = None) -> dict[str, Any]:
    query = {key: list(value) for key, value in (query or {}).items()}
    query.setdefault("includeDuplicates", ["false"])
    if not str(query.get("content_category", [""])[0]).strip():
        query["priority_group"] = ["SECONDARY"]
    return candidate_rows(query)


def candidate_detail(candidate_id: int) -> dict[str, Any]:
    candidate = fetch_one(
        """
        SELECT id, category, content_category, content_priority_group, settlement_relevance_score,
               practical_value_score, category_rotation_score, content_potential_score,
               category_selection_reason, is_sensitive, review_required_reason,
               'KR' AS region, title, source_name, source_type, source_url, canonical_url,
               google_news_url, publisher_name, generated_title, generated_summary_en, generated_why_it_matters_en,
               summary, content, image_url, image_urls_json, language, keyword, hash_key, similarity_key,
               evaluation_score, duplicate_risk_score, foreign_worker_relevance_score, korea_relevance_score,
               visa_or_labor_policy_score, freshness_score, source_reliability_score, facebook_post_suitability_score,
               status, publish_status, short_summary, key_points, relevance_reason, risk_notes,
               selection_reason, skip_reason, fail_reason, score_threshold, score_breakdown_json,
               collected_at, published_at, facebook_post_url, facebook_post_id, publish_cycle_id AS cycle_id,
               post_expired, post_expired_at, post_expired_reason, telegram_notified, publish_attempt_count,
               last_publish_attempt_at, normalized_item_id, related_source_count, duplicate_count, group_item_count,
               last_seen_at, is_representative, representative_candidate_id, content_fetch_status, content_fetch_error
        FROM social_news.candidate
        WHERE id = %s
        """,
        (candidate_id,),
    )
    if not candidate:
        return {}
    sanitize_news_url_fields(candidate)
    repo_candidate = news_repository().get_candidate(candidate_id)
    facebook_message = FacebookPublisher().build_message(repo_candidate) if repo_candidate else ""
    normalized_item_id = candidate.get("normalized_item_id")
    group_items = []
    raw_items = []
    if normalized_item_id:
        group_items = fetch_all(
            """
            SELECT id, title, source_name, source_type, source_url, canonical_url, google_news_url,
                   status, publish_status, evaluation_score, collected_at, last_seen_at, facebook_post_url,
                   is_representative, duplicate_count, related_source_count
                   , representative_candidate_id, content_fetch_status
            FROM social_news.candidate
            WHERE normalized_item_id = %s
            ORDER BY COALESCE(last_seen_at, collected_at) DESC, id DESC
            LIMIT 200
            """,
            (normalized_item_id,),
        )
        raw_items = fetch_all(
            """
            SELECT id, source_type, source_name, publisher_name, source_url, google_news_url,
                   raw_title AS title, language, is_duplicate, duplicate_reason, collected_at
            FROM social_news.raw_item
            WHERE normalized_item_id = %s
            ORDER BY collected_at DESC, id DESC
            LIMIT 200
            """,
            (normalized_item_id,),
        )
    group_items = [sanitize_news_url_fields(item) for item in group_items]
    raw_items = [sanitize_news_url_fields(item) for item in raw_items]
    return {
        "candidate": candidate,
        "facebookMessage": facebook_message,
        "groupItems": group_items,
        "rawItems": raw_items,
        "publishLogs": fetch_all(
            """
            SELECT id, channel, page_id, external_post_id, dry_run, status, error_code, error_message,
                   published_at, facebook_permalink, score, threshold, message_preview, response_code, response_body,
                   request_payload::text AS payload_preview,
                   request_payload ->> 'message' AS final_message,
                   request_payload ->> 'link' AS facebook_link_url,
                   request_payload ->> 'link_valid_yn' AS link_valid_yn,
                   request_payload ->> 'link_reject_reason' AS link_reject_reason,
                   request_payload ->> 'facebook_debugger_url' AS facebook_debugger_url,
                   request_payload ->> 'token_env_key' AS token_env_key,
                   request_payload ->> 'token_masked' AS token_masked,
                   request_payload ->> 'token_fingerprint' AS token_fingerprint,
                   request_payload -> 'token_debug' AS token_debug
            FROM social_news.publish_log
            WHERE news_candidate_id = %s
            ORDER BY published_at DESC, id DESC
            LIMIT 20
            """,
            (candidate_id,),
        ),
        "telegramLogs": fetch_all(
            """
            SELECT id, dry_run, message, status, error_message, sent_at
            FROM social_news.telegram_notify_log
            WHERE news_candidate_id = %s
            ORDER BY sent_at DESC, id DESC
            LIMIT 20
            """,
            (candidate_id,),
        ),
        "pipelineLogs": fetch_all(
            """
            SELECT id, step_name, status, COALESCE(message, skipped_reason, '') AS message,
                   payload_json::text AS payload_json, created_at
            FROM social_news.pipeline_step_log
            WHERE news_candidate_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT 50
            """,
            (candidate_id,),
        ),
    }


def lifestyle_candidate_detail(candidate_id: int) -> dict[str, Any]:
    return candidate_detail(candidate_id)


def delete_candidate_rows(ids: list[int]) -> int:
    deleted = news_repository().delete_candidates(ids)
    write_bot_log("candidate_delete", "COMPLETED", f"후보 기사 {deleted}건 삭제")
    return deleted


def cleanup_candidate_article_data(payload: dict[str, Any]) -> dict[str, Any]:
    ids = payload.get("ids") if isinstance(payload, dict) else []
    selected_ids = [int(item) for item in ids if str(item).isdigit()] if isinstance(ids, list) else []
    limit = int(payload.get("limit") or 50) if isinstance(payload, dict) else 50
    limit = max(1, min(limit, 100))
    force_resummarize = bool(payload.get("forceResummarize")) if isinstance(payload, dict) else False
    suppress_empty_log = bool(payload.get("suppressEmptyLog")) if isinstance(payload, dict) else False
    retryable_reset = reset_retryable_generation_failures(limit=limit)
    rows = cleanup_candidate_targets(payload, selected_ids, limit)
    result = {
        "target": len(rows),
        "updated": 0,
        "resolved_url": 0,
        "content_updated": 0,
        "summary_updated": 0,
        "score_updated": 0,
        "queue_updated": 0,
        "failed": 0,
        "skipped": 0,
        "retryable_reset": retryable_reset,
    }

    touched_ids: list[int] = []
    force_queue = bool(selected_ids)
    for row in rows:
        updated = cleanup_single_candidate(row, force_queue=force_queue, force_resummarize=force_resummarize)
        touched_ids.append(int(row["id"]))
        for key in result:
            if key in updated and key != "target":
                result[key] += int(updated[key] or 0)
    result["queue_updated"] = refresh_publish_queue_after_cleanup(touched_ids)
    if result["target"] or not suppress_empty_log:
        news_repository().insert_pipeline_log(
            "article_cleanup",
            "COMPLETED",
            f"article cleanup completed: target {result['target']}, updated {result['updated']}, failed {result['failed']}",
            payload_json=json.dumps(result, ensure_ascii=False),
        )
    return {"ok": True, **result}


def cleanup_candidate_targets(payload: dict[str, Any], selected_ids: list[int], limit: int) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []
    auto_repair_only = bool(payload.get("autoRepairOnly")) if isinstance(payload, dict) else False
    if selected_ids:
        where.append("id = ANY(%s)")
        params.append(selected_ids)
    elif auto_repair_only:
        retry_minutes = max(1, min(int(payload.get("retryMinutes") or 5), 1440))
        where.append(
            """
            (
                COALESCE(source_url, '') = ''
                OR source_url ~ '/path/A'
                OR canonical_url ~ '/path/A'
                OR COALESCE(content, '') = ''
                OR length(COALESCE(content, '')) < 120
                OR COALESCE(content_fetch_status, '') IN ('FAILED', 'URL_MISSING', 'PARTIAL')
                OR COALESCE(evaluation_score, 0) = 0
                OR COALESCE(status, '') = 'TEXT_INVALID'
                OR COALESCE(publish_status, '') = 'TEXT_INVALID'
            )
            """
        )
        where.append("COALESCE(status, '') NOT IN ('DUPLICATE', 'DUPLICATE_SKIPPED', 'ARCHIVED', 'POSTED', 'PUBLISHED', 'NOTIFIED')")
        where.append("COALESCE(publish_status, '') NOT IN ('DUPLICATE', 'DUPLICATE_SKIPPED', 'ARCHIVED', 'POSTED', 'PUBLISHED', 'NOTIFIED')")
        where.append("published_at IS NULL")
        where.append("COALESCE(facebook_post_url, '') = ''")
        where.append("COALESCE(is_representative, TRUE) = TRUE")
        where.append("(updated_at IS NULL OR updated_at < CURRENT_TIMESTAMP - (%s || ' minutes')::interval)")
        params.append(retry_minutes)
    else:
        where.append(
            """
            (
                COALESCE(source_url, '') = ''
                OR source_url ~ '/path/A'
                OR canonical_url ~ '/path/A'
                OR COALESCE(content, '') = ''
                OR COALESCE(content_fetch_status, '') IN ('FAILED', 'URL_MISSING')
                OR COALESCE(evaluation_score, 0) = 0
                OR COALESCE(status, '') IN ('TEXT_INVALID', 'DUPLICATE', 'SKIPPED', 'FAILED', 'POST_EXPIRED')
                OR COALESCE(publish_status, '') IN ('TEXT_INVALID', 'DUPLICATE', 'SKIPPED', 'FAILED', 'POST_EXPIRED')
            )
            """
        )
        status = str(payload.get("status") or "").strip()
        search = str(payload.get("search") or "").strip()
        include_duplicates = str(payload.get("includeDuplicates") or "") in {"1", "true", "True"}
        if not include_duplicates:
            where.append("COALESCE(is_representative, TRUE) = TRUE")
        if status:
            where.append("(status = %s OR publish_status = %s)")
            params.extend([status, status])
        if search:
            where.append(
                """
                (
                    title ILIKE %s OR source_name ILIKE %s OR source_type ILIKE %s
                    OR source_url ILIKE %s OR google_news_url ILIKE %s OR similarity_key ILIKE %s
                )
                """
            )
            term = f"%{search}%"
            params.extend([term, term, term, term, term, term])
    return fetch_all(
        f"""
        SELECT id, normalized_item_id, title, source_url, canonical_url, google_news_url,
               content, image_url, image_urls_json, publisher_name, source_name
        FROM social_news.candidate
        WHERE {' AND '.join(where)}
        ORDER BY COALESCE(last_seen_at, collected_at) DESC, id DESC
        LIMIT %s
        """,
        tuple(params + [limit]),
    )


def start_article_cleanup_scheduler() -> None:
    global ARTICLE_CLEANUP_THREAD
    enabled = os.getenv("NEWS_ARTICLE_AUTO_CLEANUP", "true").strip().lower() in {"1", "true", "yes", "on"}
    if not enabled:
        print("[article-cleanup] automatic cleanup disabled", flush=True)
        return
    if ARTICLE_CLEANUP_THREAD and ARTICLE_CLEANUP_THREAD.is_alive():
        return
    ARTICLE_CLEANUP_STOP.clear()
    ARTICLE_CLEANUP_THREAD = threading.Thread(target=run_article_cleanup_scheduler, name="workconnect-article-cleanup", daemon=True)
    ARTICLE_CLEANUP_THREAD.start()


def run_article_cleanup_scheduler() -> None:
    interval_minutes = int(os.getenv("NEWS_ARTICLE_AUTO_CLEANUP_INTERVAL_MINUTES", "5") or "5")
    interval_seconds = max(300, interval_minutes * 60)
    limit = max(1, min(int(os.getenv("NEWS_ARTICLE_AUTO_CLEANUP_LIMIT", "20") or "20"), 100))
    initial_delay = max(30, min(int(os.getenv("NEWS_ARTICLE_AUTO_CLEANUP_INITIAL_DELAY_SECONDS", "90") or "90"), interval_seconds))
    print(f"[article-cleanup] automatic cleanup every {interval_seconds // 60} minutes, limit={limit}", flush=True)
    if ARTICLE_CLEANUP_STOP.wait(initial_delay):
        return
    while not ARTICLE_CLEANUP_STOP.is_set():
        run_article_cleanup_once(limit=limit)
        if ARTICLE_CLEANUP_STOP.wait(interval_seconds):
            break


def run_article_cleanup_once(limit: int = 20) -> dict[str, Any]:
    if not ARTICLE_CLEANUP_LOCK.acquire(blocking=False):
        return {"ok": False, "status": "SKIPPED", "message": "article cleanup already running"}
    try:
        result = cleanup_candidate_article_data(
            {
                "limit": limit,
                "autoRepairOnly": True,
                "includeDuplicates": "0",
                "forceResummarize": False,
                "suppressEmptyLog": True,
                "retryMinutes": int(os.getenv("NEWS_ARTICLE_AUTO_CLEANUP_RETRY_MINUTES", "5") or "5"),
            }
        )
        if int(result.get("target") or 0) > 0:
            print(
                "[article-cleanup] "
                f"target={result.get('target')} updated={result.get('updated')} "
                f"content={result.get('content_updated')} failed={result.get('failed')} "
                f"queue={result.get('queue_updated')}",
                flush=True,
            )
        return result
    except Exception as exc:
        print(f"[article-cleanup][WARN] automatic cleanup failed: {exc}", flush=True)
        try:
            news_repository().insert_pipeline_log("article_cleanup", "FAILED", f"automatic cleanup failed: {str(exc)[:180]}")
        except Exception:
            pass
        return {"ok": False, "status": "FAILED", "message": str(exc)[:300]}
    finally:
        ARTICLE_CLEANUP_LOCK.release()


def cleanup_single_candidate(row: dict[str, Any], force_queue: bool = False, force_resummarize: bool = False) -> dict[str, int]:
    candidate_id = int(row["id"])
    source_url = safe_url(row.get("source_url") or "")
    canonical_url = safe_url(row.get("canonical_url") or "")
    google_news_url = str(row.get("google_news_url") or "").strip()
    result = {"updated": 0, "resolved_url": 0, "content_updated": 0, "summary_updated": 0, "score_updated": 0, "failed": 0, "skipped": 0}

    if not source_url:
        sibling_url = find_existing_article_url(row)
        if sibling_url:
            source_url = sibling_url
            canonical_url = canonical_url or sibling_url
            result["resolved_url"] = 1

    if not source_url and google_news_url:
        resolved_url = resolve_google_news_url(google_news_url, timeout=10)
        if is_acceptable_source_url(resolved_url):
            source_url = resolved_url
            canonical_url = canonical_url or resolved_url
            result["resolved_url"] = 1

    metadata = None
    content = str(row.get("content") or "")
    content_status = "URL_MISSING"
    content_error = ""
    canonical_valid, _ = validate_facebook_article_link(canonical_url)
    source_valid, _ = validate_facebook_article_link(source_url)
    if canonical_valid and (not source_valid or "/path/A" in source_url):
        source_url = canonical_url
        result["resolved_url"] = 1
        source_valid = True
    if source_url and not source_valid:
        sibling_url = find_existing_article_url(row)
        if sibling_url:
            source_url = sibling_url
            canonical_url = canonical_url or sibling_url
            result["resolved_url"] = 1
    if source_url:
        try:
            metadata = fetch_article_metadata(source_url, timeout=12)
            if metadata.canonical_url and is_acceptable_source_url(metadata.canonical_url):
                canonical_url = metadata.canonical_url
                source_url = metadata.canonical_url
            if metadata.content and len(metadata.content) >= 120:
                content = metadata.content
                result["content_updated"] = 1
                content_status = "FETCHED"
            else:
                content_status = "FAILED"
                content_error = "content too short"
        except Exception as exc:
            content_status = "FAILED"
            content_error = str(exc)[:300]
    summary_payload = summarize_cleanup_candidate(candidate_id, source_url, canonical_url, content) if force_resummarize else {}
    if summary_payload:
        result["summary_updated"] = 1

    score_payload = score_cleanup_candidate(candidate_id, source_url, canonical_url, content, force_queue=force_queue)
    if score_payload:
        result["score_updated"] = 1

    if not source_url or content_status == "FAILED":
        result["failed"] = 1
    else:
        result["updated"] = 1

    image_url = (metadata.image_url if metadata and metadata.image_url else row.get("image_url") or "").strip()
    image_urls = metadata.image_urls if metadata and metadata.image_urls else row.get("image_urls_json") or []
    publisher_name = metadata.publisher_name if metadata and metadata.publisher_name else row.get("publisher_name") or row.get("source_name") or ""
    update_cleanup_rows(
        candidate_id=candidate_id,
        normalized_item_id=row.get("normalized_item_id"),
        source_url=source_url,
        canonical_url=canonical_url,
        google_news_url=google_news_url,
        content=content,
        image_url=image_url,
        image_urls=image_urls,
        publisher_name=publisher_name,
        content_fetch_status=content_status,
        content_fetch_error=content_error,
        summary_payload=summary_payload,
        score_payload=score_payload,
    )
    return result


def find_existing_article_url(row: dict[str, Any]) -> str:
    title = str(row.get("title") or "").strip()
    normalized_item_id = row.get("normalized_item_id")
    source_name = str(row.get("source_name") or row.get("publisher_name") or "").strip()
    clauses = ["id <> %s", "COALESCE(source_url, '') <> ''"]
    params: list[Any] = [int(row["id"])]
    if normalized_item_id and title:
        clauses.append("(normalized_item_id = %s OR title = %s)")
        params.extend([normalized_item_id, title])
    elif normalized_item_id:
        clauses.append("normalized_item_id = %s")
        params.append(normalized_item_id)
    elif title:
        clauses.append("title = %s")
        params.append(title)
    if source_name:
        clauses.append("(source_name = %s OR publisher_name = %s)")
        params.extend([source_name, source_name])
    candidates = fetch_all(
        f"""
        SELECT source_url, canonical_url, content
        FROM social_news.candidate
        WHERE {' AND '.join(clauses)}
        ORDER BY
            CASE WHEN COALESCE(content, '') <> '' THEN 0 ELSE 1 END,
            COALESCE(last_seen_at, collected_at) DESC,
            id DESC
        LIMIT 10
        """,
        tuple(params),
    )
    for candidate in candidates:
        for value in (candidate.get("canonical_url"), candidate.get("source_url")):
            url = safe_url(value or "")
            valid, _ = validate_facebook_article_link(url)
            if valid:
                return url
    return ""


def score_cleanup_candidate(candidate_id: int, source_url: str, canonical_url: str, content: str, force_queue: bool = False) -> dict[str, Any]:
    candidate = news_repository().get_candidate(candidate_id)
    if not candidate:
        return {}
    candidate.source_url = source_url
    candidate.canonical_url = canonical_url
    candidate.content = content or candidate.content
    evaluation = CandidateEvaluator().evaluate(candidate, threshold=40.0)
    decision = evaluation.decision
    reason = (
        "관리자 링크/본문 정리 요청으로 재채점 후 게시 대기열에 다시 추가했습니다."
        if decision == "READY_TO_PUBLISH" and force_queue
        else evaluation.reason
    )
    return {
        "evaluation_score": evaluation.total_score,
        "duplicate_risk_score": evaluation.duplicate_risk_score,
        "foreign_worker_relevance_score": evaluation.foreign_worker_relevance_score,
        "korea_relevance_score": evaluation.korea_relevance_score,
        "visa_or_labor_policy_score": evaluation.visa_or_labor_policy_score,
        "freshness_score": evaluation.freshness_score,
        "source_reliability_score": evaluation.source_reliability_score,
        "facebook_post_suitability_score": evaluation.facebook_post_suitability_score,
        "content_category": candidate.content_category,
        "content_priority_group": candidate.content_priority_group,
        "settlement_relevance_score": evaluation.settlement_relevance_score,
        "practical_value_score": evaluation.practical_value_score,
        "category_rotation_score": candidate.category_rotation_score,
        "content_potential_score": evaluation.content_potential_score,
        "category_selection_reason": candidate.category_selection_reason,
        "is_sensitive": evaluation.is_sensitive,
        "review_required_reason": evaluation.review_required_reason,
        "score_threshold": evaluation.threshold,
        "score_breakdown_json": evaluation.score_breakdown_json,
        "risk_level": "HIGH" if evaluation.duplicate_risk_score >= 0.85 else "LOW",
        "decision": decision,
        "selection_reason": reason if decision == "READY_TO_PUBLISH" else "",
        "skip_reason": reason if decision != "READY_TO_PUBLISH" else "",
    }


def summarize_cleanup_candidate(candidate_id: int, source_url: str, canonical_url: str, content: str) -> dict[str, Any]:
    candidate = news_repository().get_candidate(candidate_id)
    if not candidate:
        return {}
    candidate.source_url = source_url or candidate.source_url
    candidate.canonical_url = canonical_url or candidate.canonical_url
    candidate.content = content or candidate.content
    summary = NewsSummarizer(timeout=60).summarize(candidate)
    return {
        "short_summary": summary.short_summary,
        "key_points": "\n".join(summary.key_points),
        "relevance_reason": summary.relevance_reason,
        "risk_notes": summary.risk_notes,
        "generated_title": summary.generated_title,
        "generated_summary_en": summary.generated_summary_en,
        "generated_why_it_matters_en": summary.generated_why_it_matters_en,
    }


def update_cleanup_rows(
    *,
    candidate_id: int,
    normalized_item_id: Any,
    source_url: str,
    canonical_url: str,
    google_news_url: str,
    content: str,
    image_url: str,
    image_urls: Any,
    publisher_name: str,
    content_fetch_status: str,
    content_fetch_error: str,
    summary_payload: dict[str, Any],
    score_payload: dict[str, Any],
) -> None:
    image_urls_json = json.dumps(image_urls or [], ensure_ascii=False) if not isinstance(image_urls, str) else image_urls
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL lock_timeout = '5s'")
            cur.execute(
                """
                UPDATE social_news.candidate
                SET source_url = %s,
                    canonical_url = %s,
                    content = %s,
                    image_url = COALESCE(NULLIF(%s, ''), image_url),
                    image_urls_json = %s::jsonb,
                    publisher_name = COALESCE(NULLIF(%s, ''), publisher_name),
                    content_fetch_status = %s,
                    content_fetch_error = %s,
                    short_summary = COALESCE(NULLIF(%s, ''), short_summary),
                    key_points = COALESCE(NULLIF(%s, ''), key_points),
                    relevance_reason = COALESCE(NULLIF(%s, ''), relevance_reason),
                    risk_notes = COALESCE(NULLIF(%s, ''), risk_notes),
                    generated_title = COALESCE(NULLIF(%s, ''), generated_title),
                    generated_summary_en = COALESCE(NULLIF(%s, ''), generated_summary_en),
                    generated_why_it_matters_en = COALESCE(NULLIF(%s, ''), generated_why_it_matters_en),
                    evaluation_score = COALESCE(%s, evaluation_score),
                    duplicate_risk_score = COALESCE(%s, duplicate_risk_score),
                    foreign_worker_relevance_score = COALESCE(%s, foreign_worker_relevance_score),
                    korea_relevance_score = COALESCE(%s, korea_relevance_score),
                    visa_or_labor_policy_score = COALESCE(%s, visa_or_labor_policy_score),
                    freshness_score = COALESCE(%s, freshness_score),
                    source_reliability_score = COALESCE(%s, source_reliability_score),
                    facebook_post_suitability_score = COALESCE(%s, facebook_post_suitability_score),
                    content_category = COALESCE(NULLIF(%s, ''), content_category),
                    content_priority_group = COALESCE(NULLIF(%s, ''), content_priority_group),
                    settlement_relevance_score = COALESCE(%s, settlement_relevance_score),
                    practical_value_score = COALESCE(%s, practical_value_score),
                    category_rotation_score = COALESCE(%s, category_rotation_score),
                    content_potential_score = COALESCE(%s, content_potential_score),
                    category_selection_reason = COALESCE(NULLIF(%s, ''), category_selection_reason),
                    is_sensitive = COALESCE(%s, is_sensitive),
                    review_required_reason = COALESCE(%s, review_required_reason),
                    score_threshold = COALESCE(%s, score_threshold),
                    score_breakdown_json = COALESCE(%s, score_breakdown_json),
                    risk_level = COALESCE(NULLIF(%s, ''), risk_level),
                    selection_reason = COALESCE(NULLIF(%s, ''), selection_reason),
                    skip_reason = COALESCE(NULLIF(%s, ''), skip_reason),
                    fail_reason = CASE
                        WHEN COALESCE(NULLIF(%s, ''), '') = 'READY_TO_PUBLISH' THEN ''
                        ELSE fail_reason
                    END,
                    post_expired = CASE
                        WHEN COALESCE(NULLIF(%s, ''), '') = 'READY_TO_PUBLISH' THEN FALSE
                        ELSE post_expired
                    END,
                    post_expired_reason = CASE
                        WHEN COALESCE(NULLIF(%s, ''), '') = 'READY_TO_PUBLISH' THEN ''
                        ELSE post_expired_reason
                    END,
                    is_representative = CASE
                        WHEN COALESCE(NULLIF(%s, ''), '') = 'READY_TO_PUBLISH' THEN TRUE
                        ELSE is_representative
                    END,
                    status = CASE
                        WHEN status NOT IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED', 'ARCHIVED', 'AUTO_RETRY_BLOCKED') THEN COALESCE(NULLIF(%s, ''), status)
                        ELSE status
                    END,
                    publish_status = CASE
                        WHEN publish_status NOT IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED', 'ARCHIVED', 'AUTO_RETRY_BLOCKED') THEN COALESCE(NULLIF(%s, ''), publish_status)
                        ELSE publish_status
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    source_url,
                    canonical_url,
                    content,
                    image_url,
                    image_urls_json,
                    publisher_name,
                    content_fetch_status,
                    content_fetch_error,
                    summary_payload.get("short_summary", ""),
                    summary_payload.get("key_points", ""),
                    summary_payload.get("relevance_reason", ""),
                    summary_payload.get("risk_notes", ""),
                    summary_payload.get("generated_title", ""),
                    summary_payload.get("generated_summary_en", ""),
                    summary_payload.get("generated_why_it_matters_en", ""),
                    score_payload.get("evaluation_score"),
                    score_payload.get("duplicate_risk_score"),
                    score_payload.get("foreign_worker_relevance_score"),
                    score_payload.get("korea_relevance_score"),
                    score_payload.get("visa_or_labor_policy_score"),
                    score_payload.get("freshness_score"),
                    score_payload.get("source_reliability_score"),
                    score_payload.get("facebook_post_suitability_score"),
                    score_payload.get("content_category", ""),
                    score_payload.get("content_priority_group", ""),
                    score_payload.get("settlement_relevance_score"),
                    score_payload.get("practical_value_score"),
                    score_payload.get("category_rotation_score"),
                    score_payload.get("content_potential_score"),
                    score_payload.get("category_selection_reason", ""),
                    score_payload.get("is_sensitive"),
                    score_payload.get("review_required_reason", ""),
                    score_payload.get("score_threshold"),
                    score_payload.get("score_breakdown_json"),
                    score_payload.get("risk_level", ""),
                    score_payload.get("selection_reason", ""),
                    score_payload.get("skip_reason", ""),
                    score_payload.get("decision", ""),
                    score_payload.get("decision", ""),
                    score_payload.get("decision", ""),
                    score_payload.get("decision", ""),
                    score_payload.get("decision", ""),
                    score_payload.get("decision", ""),
                    candidate_id,
                ),
            )
            if normalized_item_id:
                cur.execute(
                    """
                    UPDATE social_news.normalized_item
                    SET source_url = %s,
                        canonical_url = %s,
                        content = %s,
                        image_url = COALESCE(NULLIF(%s, ''), image_url),
                        image_urls_json = %s::jsonb,
                        publisher_name = COALESCE(NULLIF(%s, ''), publisher_name),
                        content_fetch_status = %s,
                        content_fetch_error = %s,
                        normalized_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (source_url, canonical_url, content, image_url, image_urls_json, publisher_name, content_fetch_status, content_fetch_error, normalized_item_id),
                )
                cur.execute(
                    """
                    UPDATE social_news.raw_item
                    SET source_url = %s,
                        raw_content = COALESCE(NULLIF(%s, ''), raw_content),
                        publisher_name = COALESCE(NULLIF(%s, ''), publisher_name),
                        content_fetch_status = %s,
                        content_fetch_error = %s
                    WHERE normalized_item_id = %s
                       OR (COALESCE(google_news_url, '') <> '' AND google_news_url = %s)
                    """,
                    (source_url, content, publisher_name, content_fetch_status, content_fetch_error, normalized_item_id, google_news_url),
                )
        conn.commit()


def reset_retryable_generation_failures(limit: int = 20) -> int:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL lock_timeout = '5s'")
            cur.execute(
                """
                WITH target AS (
                    SELECT id
                    FROM social_news.candidate
                    WHERE collected_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
                      AND published_at IS NULL
                      AND COALESCE(facebook_post_url, '') = ''
                      AND COALESCE(is_representative, TRUE) = TRUE
                      AND COALESCE(source_url, '') <> ''
                      AND COALESCE(content, '') <> ''
                      AND length(COALESCE(content, '')) >= 120
                      AND COALESCE(risk_level, '') != 'HIGH'
                      AND (
                          COALESCE(status, '') IN ('FAILED', 'FAILED_RETRYABLE')
                          OR COALESCE(publish_status, '') IN ('FAILED', 'FAILED_RETRYABLE')
                      )
                      AND (
                          COALESCE(fail_reason, '') ILIKE '%%LLaMA%%'
                          OR COALESCE(fail_reason, '') ILIKE '%%summary%%'
                          OR COALESCE(fail_reason, '') ILIKE '%%timed out%%'
                      )
                    ORDER BY updated_at ASC NULLS FIRST, id ASC
                    LIMIT %s
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE social_news.candidate candidate
                SET status = 'READY_TO_PUBLISH',
                    publish_status = 'READY_TO_PUBLISH',
                    post_expired = FALSE,
                    post_expired_reason = '',
                    fail_reason = '',
                    skip_reason = '',
                    updated_at = CURRENT_TIMESTAMP
                FROM target
                WHERE candidate.id = target.id
                """,
                (max(1, min(int(limit or 20), 100)),),
            )
            updated = cur.rowcount or 0
        conn.commit()
    if updated:
        news_repository().insert_pipeline_log(
            "article_cleanup",
            "COMPLETED",
            f"reset {updated} retryable LLaMA/article generation failures to READY_TO_PUBLISH",
        )
    return int(updated)


def refresh_publish_queue_after_cleanup(candidate_ids: list[int]) -> int:
    ids = [int(candidate_id) for candidate_id in candidate_ids if candidate_id]
    if not ids:
        return 0
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL lock_timeout = '5s'")
            cur.execute(
                """
                UPDATE social_news.candidate
                SET status = 'READY_TO_PUBLISH',
                    publish_status = 'READY_TO_PUBLISH',
                    post_expired = FALSE,
                    post_expired_reason = '',
                    fail_reason = '',
                    skip_reason = '',
                    is_representative = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s)
                  AND COALESCE(evaluation_score, 0) >= COALESCE(NULLIF(score_threshold, 0), 40)
                  AND collected_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
                  AND COALESCE(source_url, '') <> ''
                  AND source_url NOT ILIKE '%%news.google.com/rss/articles%%'
                  AND source_url NOT ILIKE '%%news.google.com/articles%%'
                  AND source_url !~ '://[^/]+/?$'
                  AND source_url !~ '/path/A'
                  AND COALESCE(risk_level, '') != 'HIGH'
                  AND published_at IS NULL
                  AND COALESCE(facebook_post_url, '') = ''
                  AND COALESCE(status, '') NOT IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED', 'ARCHIVED', 'AUTO_RETRY_BLOCKED')
                  AND COALESCE(publish_status, '') NOT IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED', 'ARCHIVED', 'AUTO_RETRY_BLOCKED')
                """,
                (ids,),
            )
            updated = cur.rowcount or 0
        conn.commit()
    return int(updated)


def repost_candidate(candidate_id: int) -> dict[str, Any]:
    repository = news_repository()
    candidate = repository.get_candidate(candidate_id)
    if candidate is None:
        return {"ok": False, "message": "재게시할 뉴스를 찾을 수 없습니다."}
    if not (candidate.source_url or candidate.canonical_url or candidate.google_news_url):
        return {"ok": False, "message": "원문 URL이 없어 재게시할 수 없습니다."}

    cycle_id = today_cycle_id()
    candidate.skip_reason = ""
    candidate.fail_reason = ""
    candidate.post_expired = False
    candidate.post_expired_reason = ""
    candidate.cycle_id = cycle_id
    candidate.status = "READY_TO_PUBLISH"
    candidate.publish_status = "READY_TO_PUBLISH"
    repository.update_candidate(candidate)
    repository.insert_pipeline_log("facebook_repost", "STARTED", f"관리자 재게시 시도: {candidate.title}", candidate.id)

    result = NewsPipeline(repository=repository, collectors=[]).auto_publish(candidate, dry_run=False)
    refreshed = repository.get_candidate(candidate_id)
    ok = result.get("facebook_status") == "PUBLISHED"
    repository.insert_pipeline_log(
        "facebook_repost",
        "COMPLETED" if ok else "FAILED",
        f"관리자 재게시 {'완료' if ok else '실패'}: {candidate.title}",
        candidate.id,
    )
    return {
        "ok": ok,
        "message": "재게시가 완료되었습니다." if ok else result.get("error_message") or "재게시가 실패했습니다.",
        "result": result,
        "candidate": refreshed.to_dict() if refreshed else None,
    }


def log_level(status: str) -> str:
    normalized = (status or "").upper()
    if normalized in {"FAILED", "ERROR"}:
        return "ERROR"
    if normalized in {"SKIPPED", "WAITING", "BLOCKED", "SUPPRESSED", "RETRY", "RETRYABLE"}:
        return "WARN"
    return "INFO"


def log_rows(
    limit: int = 50,
    offset: int = 0,
    level: str = "",
    status: str = "",
    search: str = "",
    module: str = "",
    date_from: str = "",
    date_to: str = "",
) -> list[dict[str, Any]]:
    logs = news_repository().list_pipeline_logs(
        limit=limit,
        offset=offset,
        level=level,
        status=status,
        search=search,
        module=module,
        date_from=date_from,
        date_to=date_to,
    )
    return [
        {
            "id": str(row["id"]),
            "bot": row.get("module_key") or "social_news_bot",
            "module": row.get("module_key") or "social_news_bot",
            "level": log_level(row.get("status", "")),
            "status": row.get("status") or "",
            "message": row["message"],
            "time": row["created_at"],
            "latency": row["step"],
            "step": row["step"],
            "candidate_id": row.get("news_candidate_id"),
            "payload_json": row.get("payload_json") or "{}",
        }
        for row in logs
    ]


class AdminRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_common_headers()
        self.end_headers()

    def do_GET(self) -> None:
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query = parse_qs(parsed_url.query)
            if not self._is_public_get(path) and not self._has_approved_cookie():
                self._send_json({"error": "unauthorized", "message": "관리자 승인이 필요합니다."}, status=401)
                return

            if path == "/api/health":
                self._send_json({"ok": True, "database": "foreign_worker_job_info"})
            elif path.startswith("/api/admin/auth/status/"):
                self._handle_auth_status(path)
            elif path == "/api/admin/modules":
                self._send_json({"items": module_rows()})
            elif path == "/api/admin/facebook/status":
                self._send_json(facebook_runtime_config_summary())
            elif path == "/api/dashboard/summary":
                self._send_json(cached_dashboard_summary())
            elif path == "/api/admin/content/dashboard":
                self._send_json(content_dashboard())
            elif path == "/api/admin/content/candidates":
                self._send_json(content_candidate_rows(query))
            elif path.startswith("/api/admin/content/candidates/"):
                raw_id = path.rsplit("/", 1)[-1]
                if not raw_id.isdigit():
                    self._send_json({"error": "bad_request", "message": "content candidate id is invalid"}, status=400)
                    return
                detail = content_candidate_detail(int(raw_id))
                self._send_json(detail if detail else {"error": "not_found", "message": "content candidate not found"}, status=200 if detail else 404)
            elif path == "/api/social/news/candidates":
                self._send_json(candidate_rows(query))
            elif path == "/api/admin/lifestyle/candidates":
                self._send_json(lifestyle_candidate_rows(query))
            elif path.startswith("/api/admin/lifestyle/candidates/"):
                raw_id = path.rsplit("/", 1)[-1]
                if not raw_id.isdigit():
                    self._send_json({"error": "bad_request", "message": "생활정보 후보 ID가 올바르지 않습니다."}, status=400)
                    return
                detail = lifestyle_candidate_detail(int(raw_id))
                if not detail:
                    self._send_json({"error": "not_found", "message": "생활정보 상세 데이터를 찾을 수 없습니다."}, status=404)
                    return
                self._send_json(detail)
            elif path.startswith("/api/social/news/candidates/"):
                raw_id = path.rsplit("/", 1)[-1]
                if not raw_id.isdigit():
                    self._send_json({"error": "bad_request", "message": "뉴스 ID가 올바르지 않습니다."}, status=400)
                    return
                detail = candidate_detail(int(raw_id))
                if not detail:
                    self._send_json({"error": "not_found", "message": "뉴스 상세 데이터를 찾을 수 없습니다."}, status=404)
                    return
                self._send_json(detail)
            elif path == "/api/logs/recent":
                limit = clamp_query_int(query, "limit", 50, minimum=1, maximum=100)
                offset = clamp_query_int(query, "offset", 0, minimum=0, maximum=10000)
                self._send_json(
                    {
                        "items": log_rows(
                            limit=limit,
                            offset=offset,
                            level=str(query.get("level", [""])[0]).strip(),
                            status=str(query.get("status", [""])[0]).strip(),
                            search=str(query.get("search", [""])[0]).strip(),
                            module=str(query.get("module", [""])[0]).strip(),
                            date_from=str(query.get("date_from", [""])[0]).strip(),
                            date_to=str(query.get("date_to", [""])[0]).strip(),
                        )
                    }
                )
            elif path == "/api/admin/bot/status":
                self._send_json(format_bot_status(bot_runtime_row()))
            elif path == "/api/admin/content-bot/status":
                self._send_json(content_bot_status())
            elif path == "/api/admin/content/living-info/prep-status":
                self._send_json(living_info_content_prep_status())
            elif path == "/api/admin/lifestyle-bot/status":
                self._send_json(lifestyle_bot_status())
            elif path == "/api/admin/immigration-bot/status":
                self._send_json(immigration_bot_status())
            elif path == "/api/admin/llama/status":
                self._send_json(ensure_llama(start_command=False))
            elif path == "/api/admin/job-collector/status":
                self._send_json(job_collector_status())
            elif path == "/api/admin/job-collector/logs":
                limit = clamp_query_int(query, "limit", 50, minimum=1, maximum=100)
                offset = clamp_query_int(query, "offset", 0, minimum=0, maximum=10000)
                self._send_json({"items": job_collector_logs(limit=limit, offset=offset)})
            elif path == "/api/admin/job-postings":
                self._send_json({"items": job_posting_rows()})
            elif path == "/api/admin/occupation/dashboard":
                self._send_json(occupation_dashboard())
            elif path == "/api/admin/occupation/jobs":
                self._send_json(occupation_job_rows(query))
            elif path.startswith("/api/admin/occupation/jobs/"):
                raw_id = path.rsplit("/", 1)[-1]
                if not raw_id.isdigit():
                    self._send_json({"error": "bad_request", "message": "직무정보 ID가 올바르지 않습니다."}, status=400)
                    return
                detail = occupation_job_detail(int(raw_id))
                self._send_json(detail if detail else {"error": "not_found", "message": "직무정보를 찾을 수 없습니다."}, status=200 if detail else 404)
            elif path == "/api/admin/occupation/occupations":
                self._send_json(occupation_rows(query))
            elif path.startswith("/api/admin/occupation/occupations/"):
                raw_id = path.rsplit("/", 1)[-1]
                if not raw_id.isdigit():
                    self._send_json({"error": "bad_request", "message": "직업정보 ID가 올바르지 않습니다."}, status=400)
                    return
                detail = occupation_detail(int(raw_id))
                self._send_json(detail if detail else {"error": "not_found", "message": "직업정보를 찾을 수 없습니다."}, status=200 if detail else 404)
            elif path == "/api/admin/occupation/keyword-mappings":
                self._send_json(occupation_keyword_rows(query))
            elif path == "/api/admin/occupation/collect-logs":
                self._send_json({"items": occupation_collect_logs(query)})
            elif path == "/api/admin/immigration/dashboard":
                self._send_json(immigration_dashboard())
            elif path == "/api/admin/immigration/notices":
                self._send_json(immigration_notice_rows(query))
            elif path.startswith("/api/admin/immigration/notices/"):
                raw_id = path.rsplit("/", 1)[-1]
                if not raw_id.isdigit():
                    self._send_json({"error": "bad_request", "message": "notice id is invalid"}, status=400)
                    return
                detail = immigration_notice_detail(int(raw_id))
                self._send_json(detail if detail else {"error": "not_found", "message": "notice not found"}, status=200 if detail else 404)
            else:
                self._send_json({"error": "not_found", "message": "요청한 API를 찾을 수 없습니다."}, status=404)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": "server_error", "message": "서버 처리 중 오류가 발생했습니다."}, status=500)

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        try:
            if path not in PUBLIC_POST_PATHS and not self._has_approved_cookie():
                self._send_json({"error": "unauthorized", "message": "관리자 승인이 필요합니다."}, status=401)
                return

            if path == "/api/admin/auth/check":
                self._handle_auth_check()
            elif path == "/api/admin/auth/logout":
                self._handle_logout()
            elif path == "/api/admin/telegram/callback":
                self._handle_telegram_callback(parsed_url)
            elif path == "/api/admin/bot/start":
                self._send_json(start_bot())
            elif path == "/api/admin/bot/stop":
                self._send_json(stop_bot())
            elif path == "/api/admin/bot/reset-error":
                self._send_json(reset_bot_error())
            elif path == "/api/admin/content-bot/start":
                self._send_json(start_content_bot())
            elif path == "/api/admin/content-bot/stop":
                self._send_json(stop_content_bot())
            elif path == "/api/admin/content-bot/run-once":
                self._send_json(run_content_generation_cycle(limit=5))
            elif path == "/api/admin/lifestyle-bot/start":
                self._send_json(start_lifestyle_bot())
            elif path == "/api/admin/lifestyle-bot/stop":
                self._send_json(stop_lifestyle_bot())
            elif path == "/api/admin/immigration-bot/start":
                self._send_json(start_immigration_bot())
            elif path == "/api/admin/immigration-bot/stop":
                self._send_json(stop_immigration_bot())
            elif path == "/api/admin/llama/reconnect":
                self._send_json(ensure_llama(start_command=True, user_requested=True))
            elif path == "/api/admin/llama/start":
                self._send_json(ensure_llama(start_command=True, user_requested=True))
            elif path == "/api/admin/llama/stop":
                self._send_json(stop_llama())
            elif path == "/api/social/news/candidates/delete":
                payload = self._read_json()
                ids = payload.get("ids") if isinstance(payload, dict) else []
                if not isinstance(ids, list):
                    self._send_json({"error": "bad_request", "message": "삭제할 항목을 선택해주세요."}, status=400)
                    return
                deleted = delete_candidate_rows([int(item) for item in ids if str(item).isdigit()])
                self._send_json({"deleted": deleted})
            elif path == "/api/social/news/candidates/repost":
                payload = self._read_json()
                candidate_id = int(payload.get("id") or 0) if isinstance(payload, dict) else 0
                if candidate_id <= 0:
                    self._send_json({"error": "bad_request", "message": "재게시할 뉴스를 선택해주세요."}, status=400)
                    return
                result = repost_candidate(candidate_id)
                self._send_json(result)
            elif path == "/api/social/news/candidates/cleanup-links":
                payload = self._read_json()
                self._send_json(cleanup_candidate_article_data(payload if isinstance(payload, dict) else {}))
            elif path == "/api/admin/content/sync":
                payload = self._read_json()
                limit = int(payload.get("limit") or 200) if isinstance(payload, dict) else 200
                self._send_json(content_service().sync_all(limit=max(1, min(limit, 1000))))
            elif path == "/api/admin/content/living-info/sync":
                payload = self._read_json()
                limit = int(payload.get("limit") or 100) if isinstance(payload, dict) else 100
                self._send_json(content_service().sync_living_info(limit=max(1, min(limit, 500))))
            elif path == "/api/admin/content/living-info/card-preview-dry-run":
                payload = self._read_json()
                limit = int(payload.get("limit") or 20) if isinstance(payload, dict) else 20
                status = str(payload.get("status") or "READY_TO_REVIEW") if isinstance(payload, dict) else "READY_TO_REVIEW"
                self._send_json(
                    content_service().generate_living_info_card_previews(
                        limit=max(1, min(limit, 100)),
                        status=status,
                    )
                )
            elif path == "/api/admin/content/living-info/prepare-clusters":
                payload = self._read_json()
                limit = int(payload.get("limit") or 100) if isinstance(payload, dict) else 100
                execute = bool(payload.get("execute")) if isinstance(payload, dict) else False
                self._send_json(
                    content_service().prepare_living_info_topic_clusters(
                        limit=max(1, min(limit, 500)),
                        dry_run=not execute,
                    )
                )
            elif path == "/api/admin/content/living-info/prep-cycle":
                payload = self._read_json()
                limit = int(payload.get("limit") or 20) if isinstance(payload, dict) else 20
                dry_run = bool(payload.get("dryRun", True)) if isinstance(payload, dict) else True
                self._send_json(run_living_info_content_prep_cycle(limit=max(1, min(limit, 100)), dry_run=dry_run))
            elif path.startswith("/api/admin/content/candidates/") and path.endswith("/card-preview-dry-run"):
                raw_id = path.split("/")[-2]
                if not raw_id.isdigit():
                    self._send_json({"ok": False, "message": "content candidate id is invalid"}, status=400)
                    return
                result = content_service().generate_card_preview_dry_run(int(raw_id))
                self._send_json(result, status=200 if result.get("ok") else 404)
            elif path.startswith("/api/admin/content/candidates/") and path.endswith("/send-telegram-review"):
                raw_id = path.split("/")[-2]
                candidate = content_candidate_detail(int(raw_id))
                if not candidate:
                    self._send_json({"ok": False, "message": "content candidate not found"}, status=404)
                    return
                payload = self._read_json()
                dry_run = None
                if isinstance(payload, dict) and "dryRun" in payload:
                    dry_run = bool(payload.get("dryRun"))
                self._send_json(send_content_review_to_telegram(candidate, dry_run=dry_run))
            elif path.startswith("/api/admin/content/candidates/") and path.endswith("/score"):
                raw_id = path.split("/")[-2]
                payload = self._read_json()
                score = float(payload.get("score") or 0) if isinstance(payload, dict) else 0
                comment = str(payload.get("comment") or "Admin content score") if isinstance(payload, dict) else "Admin content score"
                result = content_service().apply_operator_score(int(raw_id), score, comment=comment)
                self._send_json({"ok": bool(result), "candidate": result}, status=200 if result else 404)
            elif path.startswith("/api/admin/content/candidates/") and path.endswith("/publish"):
                raw_id = path.split("/")[-2]
                payload = self._read_json()
                dry_run = True
                if isinstance(payload, dict) and "dryRun" in payload:
                    dry_run = bool(payload.get("dryRun"))
                self._send_json(content_service().publish(int(raw_id), dry_run=dry_run))
            elif path == "/api/admin/occupation/jobs/collect":
                payload = self._read_json()
                self._send_json(run_occupation_job_collection(payload if isinstance(payload, dict) else {}))
            elif path == "/api/admin/occupation/occupations/collect":
                payload = self._read_json()
                self._send_json(run_occupation_info_collection(payload if isinstance(payload, dict) else {}))
            elif path == "/api/admin/occupation/keyword-mappings":
                payload = self._read_json()
                self._send_json(occupation_repository().upsert_keyword_mapping(payload if isinstance(payload, dict) else {}))
            elif path == "/api/admin/occupation/keyword-mappings/generate":
                self._send_json(occupation_repository().generate_keyword_mappings())
            elif path == "/api/admin/immigration/collect":
                payload = self._read_json()
                self._send_json(immigration_collect(payload if isinstance(payload, dict) else {}))
            elif path.startswith("/api/admin/immigration/collect/"):
                payload = self._read_json()
                source = path.rsplit("/", 1)[-1]
                self._send_json(immigration_collect(payload if isinstance(payload, dict) else {}, source=source))
            elif path.startswith("/api/admin/immigration/notices/") and path.endswith("/summarize"):
                raw_id = path.split("/")[-2]
                self._send_json(immigration_service().summarize(int(raw_id)))
            elif path.startswith("/api/admin/immigration/notices/") and path.endswith("/approve"):
                raw_id = path.split("/")[-2]
                self._send_json(immigration_service().approve(int(raw_id)))
            elif path.startswith("/api/admin/immigration/notices/") and path.endswith("/publish"):
                raw_id = path.split("/")[-2]
                self._send_json(immigration_service().publish_stub(int(raw_id)))
            elif path == "/api/admin/job-collector/run":
                self._send_json(start_job_collection(smoke=False))
            elif path == "/api/admin/job-collector/smoke-test":
                self._send_json(start_job_collection(smoke=True))
            elif path == "/api/admin/job-collector/scheduler/start":
                self._send_json(start_job_scheduler())
            elif path == "/api/admin/job-collector/scheduler/stop":
                self._send_json(stop_job_scheduler())
            else:
                self._send_json({"error": "not_found", "message": "요청한 API를 찾을 수 없습니다."}, status=404)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": "server_error", "message": "서버 처리 중 오류가 발생했습니다."}, status=500)

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        try:
            if not self._has_approved_cookie():
                self._send_json({"error": "unauthorized", "message": "관리자 승인이 필요합니다."}, status=401)
                return
            if path == "/api/admin/job-collector/settings":
                payload = self._read_json()
                self._send_json({"settings": update_job_collector_settings(payload)})
            elif path.startswith("/api/admin/occupation/keyword-mappings/"):
                raw_id = path.rsplit("/", 1)[-1]
                if not raw_id.isdigit():
                    self._send_json({"error": "bad_request", "message": "검색어 매핑 ID가 올바르지 않습니다."}, status=400)
                    return
                payload = self._read_json()
                self._send_json(occupation_repository().upsert_keyword_mapping(payload if isinstance(payload, dict) else {}, item_id=int(raw_id)))
            else:
                self._send_json({"error": "not_found", "message": "요청한 API를 찾을 수 없습니다."}, status=404)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": "server_error", "message": "서버 처리 중 오류가 발생했습니다."}, status=500)

    def _is_public_get(self, path: str) -> bool:
        return path in PUBLIC_GET_PATHS or any(path.startswith(prefix) for prefix in PUBLIC_GET_PREFIXES)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}

    def _cookie_session_id(self) -> int | None:
        raw_cookie = self.headers.get("Cookie", "")
        jar = cookies.SimpleCookie()
        jar.load(raw_cookie)
        morsel = jar.get(SESSION_COOKIE)
        if not morsel:
            return None
        try:
            return int(morsel.value)
        except ValueError:
            return None

    def _has_approved_cookie(self) -> bool:
        session_id = self._cookie_session_id()
        device_id = self.headers.get("X-Device-Id", "").strip()
        user_agent = self.headers.get("User-Agent", "").strip()
        if not device_id or not user_agent:
            return False
        ip_address = client_ip(self)
        if session_id:
            row = fetch_one(
                """
                UPDATE admin.admin_login_session
                SET ip_address = %s,
                    user_agent = %s,
                    last_seen_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND device_id = %s
                  AND status = 'APPROVED'
                RETURNING id
                """,
                (ip_address, user_agent, session_id, device_id),
            )
            if row:
                return True
        return bool(find_approved_session(device_id, ip_address, user_agent))

    def _handle_auth_check(self) -> None:
        payload = self._read_json()
        device_id = str(payload.get("deviceId") or "").strip()
        user_agent = str(payload.get("userAgent") or self.headers.get("User-Agent") or "").strip()
        force_approval_request = bool(payload.get("forceApprovalRequest"))
        if not device_id or not user_agent:
            self._send_json({"error": "bad_request", "message": "장치 식별값을 확인할 수 없습니다."}, status=400)
            return

        ip_address = client_ip(self)
        if force_approval_request:
            invalidate_login_sessions(device_id, ip_address, user_agent)
        else:
            approved = find_approved_session(device_id, ip_address, user_agent)
            if approved:
                self._send_auth_response(approved)
                return

        pending = find_or_create_pending_session(device_id, ip_address, user_agent)
        send_result = send_approval_request(pending)
        if not send_result.get("ok"):
            self._send_json(
                {
                    "sessionId": pending.get("id"),
                    "status": "ERROR",
                    "approved": False,
                    "message": f"Telegram 승인 메시지 전송에 실패했습니다. {send_result.get('error_message')}",
                },
                status=503,
                set_cookie=pending.get("id"),
            )
            return
        self._send_auth_response(pending)

    def _handle_auth_status(self, path: str) -> None:
        try:
            session_id = int(path.rstrip("/").split("/")[-1])
        except ValueError:
            self._send_json({"error": "bad_request", "message": "세션 정보를 확인할 수 없습니다."}, status=400)
            return
        row = session_status(session_id)
        if not row:
            self._send_json({"error": "not_found", "message": "세션 정보를 찾을 수 없습니다."}, status=404)
            return
        device_id = self.headers.get("X-Device-Id", "").strip()
        user_agent = self.headers.get("User-Agent", "").strip()
        if (
            not device_id
            or not user_agent
            or row.get("device_id") != device_id
            or row.get("ip_address") != client_ip(self)
            or row.get("user_agent") != user_agent
        ):
            self._send_json({"error": "forbidden", "message": "접속 아이디가 허가되지 않습니다."}, status=403)
            return
        if row.get("status") == APPROVED:
            row = execute_one(
                """
                UPDATE admin.admin_login_session
                SET last_seen_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, device_id, ip_address, user_agent, status,
                          requested_at, approved_at, rejected_at, logged_out_at, last_seen_at
                """,
                (session_id,),
            )
        self._send_auth_response(row)

    def _handle_logout(self) -> None:
        session_id = self._cookie_session_id()
        payload = self._read_json()
        device_id = str(payload.get("deviceId") or self.headers.get("X-Device-Id") or "").strip()
        user_agent = str(payload.get("userAgent") or self.headers.get("User-Agent") or "").strip()
        if session_id:
            execute_one(
                """
                UPDATE admin.admin_login_session
                SET status = 'LOGGED_OUT',
                    logged_out_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND status IN ('APPROVED', 'PENDING')
                RETURNING id
                """,
                (session_id,),
            )
        if device_id and user_agent:
            execute_one(
                """
                UPDATE admin.admin_login_session
                SET status = 'LOGGED_OUT',
                    logged_out_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE device_id = %s
                  AND ip_address = %s
                  AND user_agent = %s
                  AND status IN ('APPROVED', 'PENDING')
                RETURNING id
                """,
                (device_id, client_ip(self), user_agent),
            )
        self._send_json({"status": LOGGED_OUT, "message": "로그아웃되었습니다."}, clear_cookie=True)

    def _handle_telegram_callback(self, parsed_url) -> None:
        if not verify_callback_secret(self, parsed_url):
            self._send_json({"ok": False, "message": "Callback 검증에 실패했습니다."}, status=403)
            return
        payload = self._read_json()
        callback_query = payload.get("callback_query") or payload
        result = apply_telegram_callback(callback_query)
        callback_id = callback_query.get("id")
        if callback_id:
            telegram_api(
                "answerCallbackQuery",
                {"callback_query_id": callback_id, "text": result.get("message") or "처리되었습니다."},
            )
        self._send_json(result, status=200 if result.get("ok") else 403)

    def _send_auth_response(self, session: dict[str, Any], message: str | None = None) -> None:
        status = session.get("status")
        response_message = message or {
            PENDING: "Telegram에서 접속 승인을 완료해주세요.",
            APPROVED: "접속이 승인되었습니다.",
            REJECTED: "접속이 거부되었습니다.",
            LOGGED_OUT: "승인 요청 시간이 만료되었습니다. 다시 승인 요청을 눌러주세요.",
        }.get(status, "관리자 접속 확인 중입니다.")
        self._send_json(
            {
                "sessionId": session.get("id"),
                "status": status,
                "approved": status == APPROVED,
                "message": response_message,
            },
            set_cookie=session.get("id"),
        )

    def _send_common_headers(self) -> None:
        origin = self.headers.get("Origin", "").strip().rstrip("/")
        if not origin:
            referer = self.headers.get("Referer", "").strip()
            parsed_referer = urlparse(referer)
            if parsed_referer.scheme and parsed_referer.netloc:
                origin = f"{parsed_referer.scheme}://{parsed_referer.netloc}".rstrip("/")
        if origin not in ALLOWED_ADMIN_ORIGINS and origin.startswith("http://localhost:5173"):
            origin = "http://localhost:5173"
        if origin not in ALLOWED_ADMIN_ORIGINS and origin.startswith("http://127.0.0.1:5173"):
            origin = "http://127.0.0.1:5173"
        self.send_header("Access-Control-Allow-Origin", origin if origin in ALLOWED_ADMIN_ORIGINS else "http://127.0.0.1:5173")
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, X-Device-Id, X-Admin-Telegram-Secret, X-Telegram-Bot-Api-Secret-Token",
        )

    def _send_json(
        self,
        payload: dict[str, Any],
        status: int = 200,
        set_cookie: Any = None,
        clear_cookie: bool = False,
    ) -> None:
        body = json.dumps(json_ready(payload), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_common_headers()
        if clear_cookie:
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
        elif set_cookie:
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}={set_cookie}; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        try:
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def log_message(self, format: str, *args: Any) -> None:
        return


def initialize_admin_runtime() -> None:
    ensure_auth_schema()
    ignored_storage_keys = (
        "NEWS_BOT_" + "STORAGE",
        "NEWS_BOT_" + "SQLITE_DB",
        "JOB_COLLECTOR_" + "SQLITE_DB",
    )
    ignored_storage_env = [key for key in ignored_storage_keys if os.environ.get(key)]
    if ignored_storage_env:
        print(f"[storage][WARN] SQLite 저장소 환경변수는 더 이상 사용하지 않아 무시합니다: {', '.join(ignored_storage_env)}", flush=True)
    print(f"[storage] PostgreSQL 연결 사용: {safe_connection_summary()}", flush=True)
    facebook_config = facebook_runtime_config_summary()
    facebook_config_message = (
        f"Facebook runtime config: page_id={facebook_config['page_id'] or '-'}, "
        f"token_source={facebook_config['page_token_source']}, "
        f"page_token={facebook_config['page_token_masked'] or '-'}, "
        f"fingerprint={facebook_config['page_token_fingerprint'] or '-'}, "
        f"user_token_present={facebook_config['user_token_present']}"
    )
    print(f"[facebook] {facebook_config_message}", flush=True)
    try:
        news_repository().insert_pipeline_log("facebook_config", "COMPLETED", facebook_config_message, payload_json=json.dumps(facebook_config, ensure_ascii=False))
    except Exception as exc:
        print(f"[facebook][WARN] Facebook config 로그 저장 실패: {exc}", flush=True)
    row = bot_runtime_row()
    if row.get("status") in {"RUNNING", "STARTING"}:
        print("[bot] persisted RUNNING state found; restarting social news bot", flush=True)
        start_bot()
    elif row.get("status") == "STOPPING":
        set_bot_status("STOPPED")
    if bot_switch_enabled(CONTENT_BOT_MODULE_KEY):
        print("[content-bot] persisted ON switch found; restarting content bot", flush=True)
        start_content_bot()
    if bot_switch_enabled(LIFESTYLE_BOT_MODULE_KEY):
        print("[lifestyle-bot] persisted ON switch found; running startup collection", flush=True)
        start_lifestyle_bot()
    if bot_switch_enabled(IMMIGRATION_BOT_MODULE_KEY):
        print("[immigration-bot] persisted ON switch found; running startup collection", flush=True)
        start_immigration_bot()
    if job_collector_settings().get("schedulerEnabled"):
        print("[job-collector] persisted scheduler flag found; restarting scheduler", flush=True)
        start_job_scheduler()
    start_living_info_content_prep_scheduler_if_enabled()
    print(f"[llama] {ensure_llama(start_command=True)['message']}", flush=True)
    start_article_cleanup_scheduler()
    start_telegram_update_poller()


def main(argv: list[str] | None = None) -> int:
    load_env_file()
    parser = argparse.ArgumentParser(description="Run the WorkConnect admin API server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), AdminRequestHandler)
    print(f"Admin API listening on http://{args.host}:{args.port}")
    threading.Thread(target=initialize_admin_runtime, name="admin-runtime-init", daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

