"""PostgreSQL repository for unified content candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..storage.db.postgres import connect


MIGRATION_PATH = Path(__file__).resolve().parents[1] / "storage" / "db" / "migrations" / "2026_06_07_content_candidate.sql"


class ContentRepository:
    def __init__(self) -> None:
        self.ensure_schema()

    def ensure_schema(self) -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(MIGRATION_PATH.read_text(encoding="utf-8"))
            conn.commit()

    def dashboard(self) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        COUNT(*)::int,
                        COUNT(*) FILTER (WHERE status = 'READY_TO_PUBLISH')::int,
                        COUNT(*) FILTER (WHERE status = 'READY_TO_REVIEW')::int,
                        COUNT(*) FILTER (WHERE status = 'POSTED')::int,
                        COUNT(*) FILTER (WHERE status = 'FAILED_RETRYABLE')::int,
                        COUNT(*) FILTER (WHERE source_domain = 'SOCIAL_NEWS')::int,
                        COUNT(*) FILTER (WHERE source_domain = 'IMMIGRATION_INFO')::int,
                        MAX(updated_at)
                    FROM content.content_candidate
                    WHERE status <> 'ARCHIVED'
                    """
                )
                counts = cur.fetchone()
                cur.execute(
                    """
                    SELECT source_domain, content_type, status, COUNT(*)::int
                    FROM content.content_candidate
                    WHERE status <> 'ARCHIVED'
                    GROUP BY source_domain, content_type, status
                    ORDER BY source_domain, content_type, status
                    """
                )
                groups = cur.fetchall()
        return {
            "total_count": counts[0] if counts else 0,
            "ready_count": counts[1] if counts else 0,
            "review_count": counts[2] if counts else 0,
            "posted_count": counts[3] if counts else 0,
            "failed_retryable_count": counts[4] if counts else 0,
            "social_news_count": counts[5] if counts else 0,
            "immigration_count": counts[6] if counts else 0,
            "latest_updated_at": counts[7].isoformat() if counts and counts[7] else "",
            "groups": [
                {"source_domain": row[0], "content_type": row[1], "status": row[2], "count": row[3]}
                for row in groups
            ],
        }

    def list_candidates(self, params: dict[str, Any]) -> dict[str, Any]:
        page = max(1, int(params.get("page", 1)))
        size = max(1, min(200, int(params.get("size", 20))))
        offset = (page - 1) * size
        where = ["status <> 'ARCHIVED'"]
        values: list[Any] = []
        if params.get("search"):
            pattern = f"%{params['search']}%"
            where.append("(title ILIKE %s OR summary_en ILIKE %s OR source_name ILIKE %s OR category ILIKE %s)")
            values.extend([pattern, pattern, pattern, pattern])
        for field in ("source_domain", "content_type", "category", "status"):
            if params.get(field):
                where.append(f"{field} = %s")
                values.append(params[field])
        if params.get("publishable") in {"1", "true", True}:
            where.append("status IN ('READY_TO_PUBLISH', 'FAILED_RETRYABLE')")
        where_sql = " AND ".join(where)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*)::int FROM content.content_candidate WHERE {where_sql}", tuple(values))
                total = int(cur.fetchone()[0])
                cur.execute(
                    f"""
                    SELECT id, source_domain, content_type, priority_group, category, title,
                           summary_en, source_url, source_name, original_source_url,
                           original_source_name, original_title, original_published_at,
                           original_collected_at, image_url, link_url, hashtags,
                           final_publish_score, quality_score, relevance_score, practical_value_score,
                           urgency_score, freshness_score, source_reliability_score,
                           sensitive_yn, review_required_yn, review_reason, status,
                           publish_attempt_count, last_publish_error, next_retry_at, published_at,
                           facebook_post_id, facebook_post_url, created_at, updated_at,
                           content_created_at, content_updated_at,
                           raw_ref_table, raw_ref_id
                    FROM content.content_candidate
                    WHERE {where_sql}
                    ORDER BY
                        CASE status
                            WHEN 'READY_TO_PUBLISH' THEN 0
                            WHEN 'FAILED_RETRYABLE' THEN 1
                            WHEN 'READY_TO_REVIEW' THEN 2
                            ELSE 3
                        END,
                        final_publish_score DESC,
                        COALESCE(original_collected_at, updated_at) DESC,
                        content_updated_at DESC,
                        id DESC
                    LIMIT %s OFFSET %s
                    """,
                    tuple(values + [size, offset]),
                )
                rows = cur.fetchall()
        return {
            "items": [content_row(row) for row in rows],
            "total_count": total,
            "page": page,
            "size": size,
        }

    def get_candidate(self, candidate_id: int) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, source_domain, content_type, priority_group, category, title,
                           summary_en, why_it_matters_en, body_en, source_url, source_name,
                           original_source_url, original_source_name, original_title,
                           original_published_at, original_collected_at, image_url,
                           link_url, hashtags, language, quality_score, relevance_score,
                           practical_value_score, urgency_score, freshness_score, source_reliability_score,
                           content_potential_score, rotation_score, final_publish_score, sensitive_yn,
                           review_required_yn, review_reason, status, publish_attempt_count,
                           last_publish_error, next_retry_at, published_at, facebook_post_id,
                           facebook_post_url, created_at, updated_at, content_created_at,
                           content_updated_at, raw_ref_table, raw_ref_id, raw_payload
                    FROM content.content_candidate
                    WHERE id = %s
                    """,
                    (candidate_id,),
                )
                row = cur.fetchone()
                cur.execute(
                    """
                    SELECT id, channel, status, dry_run, message_preview, link_url,
                           facebook_post_id, facebook_post_url, error_code, error_message,
                           request_payload, response_payload, created_at
                    FROM content.publish_log
                    WHERE content_candidate_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT 20
                    """,
                    (candidate_id,),
                )
                logs = cur.fetchall()
        if not row:
            return {}
        result = content_detail_row(row)
        result["publish_logs"] = [publish_log_row(item) for item in logs]
        return result

    def upsert_candidate(self, payload: dict[str, Any]) -> int:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO content.content_candidate(
                        source_domain, content_type, priority_group, category, title, summary_en,
                        why_it_matters_en, body_en, source_url, source_name, image_url, link_url,
                        original_source_url, original_source_name, original_title,
                        original_published_at, original_collected_at,
                        hashtags, language, quality_score, relevance_score, practical_value_score,
                        urgency_score, freshness_score, source_reliability_score, content_potential_score,
                        rotation_score, final_publish_score, sensitive_yn, review_required_yn,
                        review_reason, status, published_at, facebook_post_id, facebook_post_url,
                        raw_ref_table, raw_ref_id, raw_payload
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
                    )
                    ON CONFLICT (raw_ref_table, raw_ref_id) DO UPDATE
                    SET source_domain = EXCLUDED.source_domain,
                        content_type = EXCLUDED.content_type,
                        priority_group = EXCLUDED.priority_group,
                        category = EXCLUDED.category,
                        title = EXCLUDED.title,
                        summary_en = COALESCE(NULLIF(EXCLUDED.summary_en, ''), content.content_candidate.summary_en),
                        why_it_matters_en = COALESCE(NULLIF(EXCLUDED.why_it_matters_en, ''), content.content_candidate.why_it_matters_en),
                        body_en = COALESCE(NULLIF(EXCLUDED.body_en, ''), content.content_candidate.body_en),
                        source_url = COALESCE(NULLIF(EXCLUDED.source_url, ''), content.content_candidate.source_url),
                        source_name = COALESCE(NULLIF(EXCLUDED.source_name, ''), content.content_candidate.source_name),
                        original_source_url = COALESCE(NULLIF(EXCLUDED.original_source_url, ''), content.content_candidate.original_source_url),
                        original_source_name = COALESCE(NULLIF(EXCLUDED.original_source_name, ''), content.content_candidate.original_source_name),
                        original_title = COALESCE(NULLIF(EXCLUDED.original_title, ''), content.content_candidate.original_title),
                        original_published_at = COALESCE(EXCLUDED.original_published_at, content.content_candidate.original_published_at),
                        original_collected_at = COALESCE(EXCLUDED.original_collected_at, content.content_candidate.original_collected_at),
                        image_url = COALESCE(NULLIF(EXCLUDED.image_url, ''), content.content_candidate.image_url),
                        link_url = COALESCE(NULLIF(EXCLUDED.link_url, ''), content.content_candidate.link_url),
                        hashtags = COALESCE(NULLIF(EXCLUDED.hashtags, ''), content.content_candidate.hashtags),
                        language = EXCLUDED.language,
                        quality_score = GREATEST(content.content_candidate.quality_score, EXCLUDED.quality_score),
                        relevance_score = GREATEST(content.content_candidate.relevance_score, EXCLUDED.relevance_score),
                        practical_value_score = GREATEST(content.content_candidate.practical_value_score, EXCLUDED.practical_value_score),
                        urgency_score = GREATEST(content.content_candidate.urgency_score, EXCLUDED.urgency_score),
                        freshness_score = GREATEST(content.content_candidate.freshness_score, EXCLUDED.freshness_score),
                        source_reliability_score = GREATEST(content.content_candidate.source_reliability_score, EXCLUDED.source_reliability_score),
                        content_potential_score = GREATEST(content.content_candidate.content_potential_score, EXCLUDED.content_potential_score),
                        rotation_score = EXCLUDED.rotation_score,
                        final_publish_score = GREATEST(content.content_candidate.final_publish_score, EXCLUDED.final_publish_score),
                        sensitive_yn = EXCLUDED.sensitive_yn,
                        review_required_yn = EXCLUDED.review_required_yn,
                        review_reason = COALESCE(NULLIF(EXCLUDED.review_reason, ''), content.content_candidate.review_reason),
                        status = CASE
                            WHEN content.content_candidate.status IN ('POSTED', 'POST_EXPIRED') THEN content.content_candidate.status
                            WHEN content.content_candidate.status = 'ARCHIVED' AND EXCLUDED.status = 'ARCHIVED' THEN 'ARCHIVED'
                            ELSE EXCLUDED.status
                        END,
                        published_at = COALESCE(EXCLUDED.published_at, content.content_candidate.published_at),
                        facebook_post_id = COALESCE(NULLIF(EXCLUDED.facebook_post_id, ''), content.content_candidate.facebook_post_id),
                        facebook_post_url = COALESCE(NULLIF(EXCLUDED.facebook_post_url, ''), content.content_candidate.facebook_post_url),
                        raw_payload = EXCLUDED.raw_payload,
                        updated_at = CURRENT_TIMESTAMP,
                        content_updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                    """,
                    upsert_values(payload),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0

    def update_publish_result(self, candidate_id: int, result: dict[str, Any], dry_run: bool) -> dict[str, Any]:
        status = "POSTED" if result.get("status") in {"OK", "POSTED", "PUBLISHED"} else "FAILED_RETRYABLE"
        if dry_run:
            status = "READY_TO_PUBLISH"
        error_message = str(result.get("error_message") or result.get("message") or "")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE content.content_candidate
                    SET status = %s,
                        publish_attempt_count = publish_attempt_count + 1,
                        last_publish_error = %s,
                        published_at = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE published_at END,
                        facebook_post_id = COALESCE(NULLIF(%s, ''), facebook_post_id),
                        facebook_post_url = COALESCE(NULLIF(%s, ''), facebook_post_url),
                        updated_at = CURRENT_TIMESTAMP,
                        content_updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, status, raw_ref_table, raw_ref_id
                    """,
                    (
                        status,
                        "" if status == "POSTED" else error_message,
                        status == "POSTED",
                        result.get("facebook_post_id", ""),
                        result.get("facebook_post_url", ""),
                        candidate_id,
                    ),
                )
                row = cur.fetchone()
                if row and row[2] == "social_news.candidate":
                    cur.execute(
                        """
                        UPDATE social_news.candidate
                        SET status = CASE WHEN %s THEN 'POSTED' ELSE status END,
                            publish_status = CASE WHEN %s THEN 'POSTED' ELSE publish_status END,
                            published_at = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE published_at END,
                            facebook_post_id = COALESCE(NULLIF(%s, ''), facebook_post_id),
                            facebook_post_url = COALESCE(NULLIF(%s, ''), facebook_post_url),
                            fail_reason = CASE WHEN %s THEN '' ELSE %s END,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (
                            status == "POSTED",
                            status == "POSTED",
                            status == "POSTED",
                            result.get("facebook_post_id", ""),
                            result.get("facebook_post_url", ""),
                            status == "POSTED",
                            error_message,
                            int(row[3]),
                        ),
                    )
                cur.execute(
                    """
                    INSERT INTO content.publish_log(
                        content_candidate_id, channel, status, dry_run, message_preview, link_url,
                        facebook_post_id, facebook_post_url, error_code, error_message,
                        request_payload, response_payload
                    )
                    VALUES (%s, 'facebook', %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                    """,
                    (
                        candidate_id,
                        "DRY_RUN" if dry_run else result.get("status", status),
                        dry_run,
                        str(result.get("message") or "")[:500],
                        str(result.get("link_url") or result.get("facebook_link_url") or ""),
                        str(result.get("facebook_post_id") or ""),
                        str(result.get("facebook_post_url") or ""),
                        str(result.get("error_code") or ""),
                        error_message,
                        json.dumps(result.get("request_payload", {}), ensure_ascii=False),
                        json.dumps(result, ensure_ascii=False),
                    ),
                )
            conn.commit()
        return {"ok": bool(row), "id": candidate_id, "status": row[1] if row else status}

    def archive_non_representative_social_news(self) -> int:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE content.content_candidate content_row
                    SET status = 'ARCHIVED',
                        updated_at = CURRENT_TIMESTAMP,
                        content_updated_at = CURRENT_TIMESTAMP,
                        raw_payload = content_row.raw_payload || jsonb_build_object(
                            'archive_reason', 'non_representative_or_duplicate_social_news'
                        )
                    FROM social_news.candidate candidate
                    WHERE content_row.raw_ref_table = 'social_news.candidate'
                      AND content_row.raw_ref_id = candidate.id
                      AND (
                          COALESCE(candidate.is_representative, TRUE) = FALSE
                          OR COALESCE(candidate.publish_status, candidate.status, '') IN ('DUPLICATE', 'DUPLICATE_SKIPPED', 'SKIPPED', 'TEXT_INVALID', 'ARCHIVED')
                          OR COALESCE(candidate.status, '') IN ('DUPLICATE', 'DUPLICATE_SKIPPED', 'SKIPPED', 'TEXT_INVALID', 'ARCHIVED')
                      )
                    """
                )
                count = cur.rowcount
            conn.commit()
        return int(count or 0)


def upsert_values(payload: dict[str, Any]) -> tuple[Any, ...]:
    return (
        payload.get("source_domain", ""),
        payload.get("content_type", ""),
        payload.get("priority_group", "NORMAL"),
        payload.get("category", ""),
        payload.get("title", ""),
        payload.get("summary_en", ""),
        payload.get("why_it_matters_en", ""),
        payload.get("body_en", ""),
        payload.get("source_url", ""),
        payload.get("source_name", ""),
        payload.get("image_url", ""),
        payload.get("link_url", ""),
        payload.get("original_source_url", ""),
        payload.get("original_source_name", ""),
        payload.get("original_title", ""),
        payload.get("original_published_at") or None,
        payload.get("original_collected_at") or None,
        payload.get("hashtags", ""),
        payload.get("language", "en"),
        float(payload.get("quality_score") or 0),
        float(payload.get("relevance_score") or 0),
        float(payload.get("practical_value_score") or 0),
        float(payload.get("urgency_score") or 0),
        float(payload.get("freshness_score") or 0),
        float(payload.get("source_reliability_score") or 0),
        float(payload.get("content_potential_score") or 0),
        float(payload.get("rotation_score") or 0),
        float(payload.get("final_publish_score") or 0),
        bool(payload.get("sensitive_yn", False)),
        bool(payload.get("review_required_yn", False)),
        payload.get("review_reason", ""),
        payload.get("status", "RAW"),
        payload.get("published_at") or None,
        payload.get("facebook_post_id", ""),
        payload.get("facebook_post_url", ""),
        payload.get("raw_ref_table", ""),
        int(payload.get("raw_ref_id") or 0),
        json.dumps(payload.get("raw_payload", {}), ensure_ascii=False),
    )


def content_row(row: tuple) -> dict[str, Any]:
    keys = (
        "id", "source_domain", "content_type", "priority_group", "category", "title",
        "summary_en", "source_url", "source_name", "original_source_url",
        "original_source_name", "original_title", "original_published_at",
        "original_collected_at", "image_url", "link_url", "hashtags",
        "final_publish_score", "quality_score", "relevance_score", "practical_value_score",
        "urgency_score", "freshness_score", "source_reliability_score", "sensitive_yn",
        "review_required_yn", "review_reason", "status", "publish_attempt_count",
        "last_publish_error", "next_retry_at", "published_at", "facebook_post_id",
        "facebook_post_url", "created_at", "updated_at", "content_created_at",
        "content_updated_at", "raw_ref_table", "raw_ref_id",
    )
    result = dict(zip(keys, row))
    for key in (
        "next_retry_at", "published_at", "created_at", "updated_at",
        "content_created_at", "content_updated_at", "original_published_at", "original_collected_at",
    ):
        result[key] = result[key].isoformat() if result.get(key) else ""
    for key in (
        "final_publish_score", "quality_score", "relevance_score", "practical_value_score",
        "urgency_score", "freshness_score", "source_reliability_score",
    ):
        result[key] = float(result.get(key) or 0)
    return result


def content_detail_row(row: tuple) -> dict[str, Any]:
    keys = (
        "id", "source_domain", "content_type", "priority_group", "category", "title",
        "summary_en", "why_it_matters_en", "body_en", "source_url", "source_name",
        "original_source_url", "original_source_name", "original_title",
        "original_published_at", "original_collected_at", "image_url", "link_url",
        "hashtags", "language", "quality_score", "relevance_score",
        "practical_value_score", "urgency_score", "freshness_score", "source_reliability_score",
        "content_potential_score", "rotation_score", "final_publish_score", "sensitive_yn",
        "review_required_yn", "review_reason", "status", "publish_attempt_count",
        "last_publish_error", "next_retry_at", "published_at", "facebook_post_id",
        "facebook_post_url", "created_at", "updated_at", "content_created_at",
        "content_updated_at", "raw_ref_table", "raw_ref_id", "raw_payload",
    )
    result = dict(zip(keys, row))
    for key in (
        "next_retry_at", "published_at", "created_at", "updated_at",
        "content_created_at", "content_updated_at", "original_published_at", "original_collected_at",
    ):
        result[key] = result[key].isoformat() if result.get(key) else ""
    for key in (
        "quality_score", "relevance_score", "practical_value_score", "urgency_score",
        "freshness_score", "source_reliability_score", "content_potential_score",
        "rotation_score", "final_publish_score",
    ):
        result[key] = float(result.get(key) or 0)
    return result


def publish_log_row(row: tuple) -> dict[str, Any]:
    keys = (
        "id", "channel", "status", "dry_run", "message_preview", "link_url",
        "facebook_post_id", "facebook_post_url", "error_code", "error_message",
        "request_payload", "response_payload", "created_at",
    )
    result = dict(zip(keys, row))
    result["created_at"] = result["created_at"].isoformat() if result.get("created_at") else ""
    return result
