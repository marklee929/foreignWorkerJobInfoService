from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from ..social.news.models import NewsCandidate, NewsItem
from ..social.news.repository.news_repository import NewsRepository
from ..storage.db.postgres import connect


DEFAULT_SQLITE_DB = Path("SRC/foreign_worker_life_info_collector/logs/news.db")


def row_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def sqlite_value(row: sqlite3.Row, key: str, default: str = ""):
    return row[key] if key in row.keys() else default


def candidate_from_row(row: sqlite3.Row) -> NewsCandidate:
    data = row_dict(row)
    return NewsCandidate(
        id=None,
        source_type=data.get("source_type") or "legacy_sqlite",
        source_url=data.get("source_url") or "",
        source_name=data.get("source_name") or "",
        title=data.get("title") or "",
        summary=data.get("summary") or "",
        content=data.get("content") or "",
        language=data.get("language") or "ko",
        category=data.get("category") or "",
        keyword=data.get("keyword") or "",
        hash_key=data.get("hash_key") or "",
        similarity_key=data.get("similarity_key") or "",
        short_summary=data.get("short_summary") or "",
        key_points=data.get("key_points") or "",
        relevance_reason=data.get("relevance_reason") or "",
        risk_notes=data.get("risk_notes") or "",
        evaluation_score=float(data.get("evaluation_score") or 0),
        duplicate_risk_score=float(data.get("duplicate_risk_score") or 0),
        foreign_worker_relevance_score=float(data.get("foreign_worker_relevance_score") or 0),
        korea_relevance_score=float(data.get("korea_relevance_score") or 0),
        visa_or_labor_policy_score=float(data.get("visa_or_labor_policy_score") or 0),
        freshness_score=float(data.get("freshness_score") or 0),
        source_reliability_score=float(data.get("source_reliability_score") or 0),
        facebook_post_suitability_score=float(data.get("facebook_post_suitability_score") or 0),
        selection_reason=data.get("selection_reason") or "",
        skip_reason=data.get("skip_reason") or "",
        facebook_post_url=data.get("facebook_post_url") or "",
        facebook_post_id=data.get("facebook_post_id") or "",
        last_publish_attempt_at=data.get("last_publish_attempt_at") or "",
        publish_attempt_count=int(data.get("publish_attempt_count") or 0),
        score_threshold=float(data.get("score_threshold") or 0),
        score_breakdown_json=data.get("score_breakdown_json") or "",
        telegram_notified=bool(data.get("telegram_notified")),
        fail_reason=data.get("fail_reason") or "",
        risk_level=data.get("risk_level") or "",
        post_expired=bool(data.get("post_expired")),
        post_expired_at=data.get("post_expired_at") or "",
        post_expired_reason=data.get("post_expired_reason") or "",
        cycle_id=data.get("cycle_id") or "",
        publish_status=data.get("publish_status") or data.get("status") or "",
        duplicate_group_id=None,
        status=data.get("status") or "NORMALIZED",
        collected_at=data.get("collected_at") or "",
        published_at=data.get("published_at"),
    )


def migrate(sqlite_db: Path) -> dict[str, int]:
    if not sqlite_db.exists():
        raise FileNotFoundError(f"SQLite DB를 찾을 수 없습니다: {sqlite_db}")

    repository = NewsRepository()
    existing_urls = {candidate.source_url for candidate in repository.list_candidates() if candidate.source_url}
    existing_hashes = {candidate.hash_key for candidate in repository.list_candidates() if candidate.hash_key}

    inserted = 0
    skipped = 0
    legacy_candidate_map: dict[int, int] = {}
    conn = sqlite3.connect(sqlite_db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM news_candidate ORDER BY id").fetchall()
        for row in rows:
            candidate = candidate_from_row(row)
            legacy_id = int(row["id"])
            if (candidate.source_url and candidate.source_url in existing_urls) or (candidate.hash_key and candidate.hash_key in existing_hashes):
                matched = next(
                    (
                        item.id
                        for item in repository.list_candidates()
                        if (candidate.source_url and item.source_url == candidate.source_url)
                        or (candidate.hash_key and item.hash_key == candidate.hash_key)
                    ),
                    None,
                )
                if matched:
                    legacy_candidate_map[legacy_id] = int(matched)
                skipped += 1
                continue
            item = NewsItem(
                title=candidate.title,
                url=candidate.source_url,
                source=candidate.source_type,
                source_name=candidate.source_name,
                summary=candidate.summary,
                content=candidate.content,
                language=candidate.language,
                category=candidate.category,
            )
            saved = repository.save(item)
            candidate.id = saved.id
            repository.update_candidate(candidate)
            legacy_candidate_map[legacy_id] = int(candidate.id)
            if candidate.source_url:
                existing_urls.add(candidate.source_url)
            if candidate.hash_key:
                existing_hashes.add(candidate.hash_key)
            inserted += 1
        pipeline_logs = migrate_pipeline_logs(conn, repository, legacy_candidate_map)
        facebook_logs = migrate_facebook_logs(conn, repository, legacy_candidate_map)
        telegram_logs = migrate_telegram_logs(conn, repository, legacy_candidate_map)
    finally:
        conn.close()
    return {
        "inserted": inserted,
        "skipped": skipped,
        "pipelineLogs": pipeline_logs,
        "facebookLogs": facebook_logs,
        "telegramLogs": telegram_logs,
    }


def valid_json_text(value: str | None) -> str:
    if not value:
        return "{}"
    try:
        parsed = __import__("json").loads(value)
    except Exception:
        return "{}"
    return __import__("json").dumps(parsed, ensure_ascii=False)


def migrate_pipeline_logs(conn: sqlite3.Connection, repository: NewsRepository, legacy_candidate_map: dict[int, int]) -> int:
    try:
        rows = conn.execute("SELECT * FROM news_pipeline_log ORDER BY id").fetchall()
    except sqlite3.OperationalError:
        return 0
    inserted = 0
    cycle_id = repository._runtime_cycle_id()
    pg = connect()
    for row in rows:
        legacy_candidate_id = sqlite_value(row, "news_candidate_id")
        candidate_id = legacy_candidate_map.get(int(legacy_candidate_id)) if legacy_candidate_id else None
        with pg.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM social_news.pipeline_step_log
                WHERE COALESCE(news_candidate_id, 0) = COALESCE(%s, 0)
                  AND step_name = %s
                  AND COALESCE(message, '') = %s
                  AND created_at = %s
                LIMIT 1
                """,
                (candidate_id, sqlite_value(row, "step"), sqlite_value(row, "message") or "", sqlite_value(row, "created_at")),
            )
            if cur.fetchone():
                continue
            payload = valid_json_text(sqlite_value(row, "payload_json") or "{}")
            created = sqlite_value(row, "created_at") or ""
            message = sqlite_value(row, "message") or ""
            cur.execute(
                """
                INSERT INTO social_news.pipeline_step_log(
                    cycle_id, module_key, step_name, status, skipped_reason, detail_json,
                    news_candidate_id, message, payload_json, created_at, started_at
                )
                VALUES (%s, 'social_news_bot', %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, %s, %s)
                """,
                (cycle_id, sqlite_value(row, "step") or "legacy", sqlite_value(row, "status") or "INFO", message, payload, candidate_id, message, payload, created, created),
            )
            inserted += 1
    pg.commit()
    pg.close()
    return inserted


def migrate_facebook_logs(conn: sqlite3.Connection, repository: NewsRepository, legacy_candidate_map: dict[int, int]) -> int:
    try:
        rows = conn.execute("SELECT * FROM facebook_publish_log ORDER BY id").fetchall()
    except sqlite3.OperationalError:
        return 0
    inserted = 0
    pg = connect()
    for row in rows:
        legacy_candidate_id = sqlite_value(row, "news_candidate_id")
        candidate_id = legacy_candidate_map.get(int(legacy_candidate_id)) if legacy_candidate_id else None
        if not candidate_id:
            continue
        with pg.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM social_news.publish_log
                WHERE news_candidate_id = %s
                  AND status = %s
                  AND published_at = %s
                LIMIT 1
                """,
                (candidate_id, sqlite_value(row, "status") or "", sqlite_value(row, "published_at")),
            )
            if cur.fetchone():
                continue
        repository.insert_facebook_log(
            news_candidate_id=candidate_id,
            status=sqlite_value(row, "status") or "",
            published_at=sqlite_value(row, "published_at") or "",
            page_id=sqlite_value(row, "page_id") or "",
            facebook_post_id=sqlite_value(row, "facebook_post_id") or "",
            facebook_permalink=sqlite_value(row, "facebook_permalink") or "",
            score=float(sqlite_value(row, "score", 0) or 0),
            threshold=float(sqlite_value(row, "threshold", 0) or 0),
            message_preview=sqlite_value(row, "message_preview") or "",
            response_code=sqlite_value(row, "response_code") or "",
            response_body=sqlite_value(row, "response_body") or "",
            error_code=sqlite_value(row, "error_code") or "",
            error_message=sqlite_value(row, "error_message") or "",
        )
        inserted += 1
    pg.close()
    return inserted


def migrate_telegram_logs(conn: sqlite3.Connection, repository: NewsRepository, legacy_candidate_map: dict[int, int]) -> int:
    try:
        rows = conn.execute("SELECT * FROM telegram_notify_log ORDER BY id").fetchall()
    except sqlite3.OperationalError:
        return 0
    inserted = 0
    pg = connect()
    for row in rows:
        legacy_candidate_id = sqlite_value(row, "news_candidate_id")
        candidate_id = legacy_candidate_map.get(int(legacy_candidate_id)) if legacy_candidate_id else None
        with pg.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM social_news.telegram_notify_log
                WHERE COALESCE(news_candidate_id, 0) = COALESCE(%s, 0)
                  AND status = %s
                  AND sent_at = %s
                LIMIT 1
                """,
                (candidate_id, sqlite_value(row, "status") or "", sqlite_value(row, "sent_at")),
            )
            if cur.fetchone():
                continue
        repository.insert_telegram_log(
            message=sqlite_value(row, "message") or "",
            status=sqlite_value(row, "status") or "",
            sent_at=sqlite_value(row, "sent_at") or "",
            news_candidate_id=candidate_id,
            error_message=sqlite_value(row, "error_message") or "",
        )
        inserted += 1
    pg.close()
    return inserted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manually migrate legacy social-news SQLite data to PostgreSQL.")
    parser.add_argument("--sqlite-db", type=Path, default=DEFAULT_SQLITE_DB)
    args = parser.parse_args(argv)

    result = migrate(args.sqlite_db)
    print(
        "SQLite 이전 완료: "
        f"후보 신규 {result['inserted']}건, 후보 중복 스킵 {result['skipped']}건, "
        f"파이프라인 로그 {result['pipelineLogs']}건, Facebook 로그 {result['facebookLogs']}건, Telegram 로그 {result['telegramLogs']}건"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
