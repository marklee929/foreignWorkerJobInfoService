"""PostgreSQL repository for official immigration notices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..storage.db.postgres import connect
from .models import OfficialNotice

MIGRATION_PATH = Path(__file__).resolve().parents[1] / "storage" / "db" / "migrations" / "2026_06_06_immigration_info.sql"


class ImmigrationNoticeRepository:
    def __init__(self):
        self.ensure_schema()

    def ensure_schema(self) -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(MIGRATION_PATH.read_text(encoding="utf-8"))
            conn.commit()

    def upsert_notice(self, notice: OfficialNotice) -> tuple[OfficialNotice, bool]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO immigration_info.official_notice(
                        source, source_name, source_type, notice_type, title_ko, title_en,
                        original_url, canonical_url, published_at, raw_content_ko, raw_content_en,
                        summary_en, why_it_matters_en, affected_visa_types, affected_user_groups,
                        region_tags, policy_keywords, importance_score, urgency_level, content_status,
                        active_yn, raw_response
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULLIF(%s, '')::timestamptz, %s, %s, %s, %s,
                            %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (canonical_url) DO UPDATE
                    SET title_ko = EXCLUDED.title_ko,
                        source_name = EXCLUDED.source_name,
                        source_type = EXCLUDED.source_type,
                        notice_type = EXCLUDED.notice_type,
                        raw_content_ko = COALESCE(NULLIF(EXCLUDED.raw_content_ko, ''), immigration_info.official_notice.raw_content_ko),
                        affected_visa_types = EXCLUDED.affected_visa_types,
                        affected_user_groups = EXCLUDED.affected_user_groups,
                        region_tags = EXCLUDED.region_tags,
                        policy_keywords = EXCLUDED.policy_keywords,
                        importance_score = EXCLUDED.importance_score,
                        urgency_level = EXCLUDED.urgency_level,
                        updated_at = CURRENT_TIMESTAMP,
                        raw_response = EXCLUDED.raw_response
                    RETURNING id, xmax = 0 AS inserted
                    """,
                    (
                        notice.source,
                        notice.source_name,
                        notice.source_type,
                        notice.notice_type,
                        notice.title_ko,
                        notice.title_en,
                        notice.original_url,
                        notice.canonical_url,
                        notice.published_at,
                        notice.raw_content_ko,
                        notice.raw_content_en,
                        notice.summary_en,
                        notice.why_it_matters_en,
                        json.dumps(notice.affected_visa_types, ensure_ascii=False),
                        json.dumps(notice.affected_user_groups, ensure_ascii=False),
                        json.dumps(notice.region_tags, ensure_ascii=False),
                        json.dumps(notice.policy_keywords, ensure_ascii=False),
                        notice.importance_score,
                        notice.urgency_level,
                        notice.content_status,
                        notice.active_yn,
                        json.dumps(notice.raw_response, ensure_ascii=False),
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        notice.id = int(row[0]) if row else None
        return notice, bool(row[1]) if row else False

    def insert_collect_log(self, payload: dict[str, Any]) -> int:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO immigration_info.collect_log(
                        collector_type, source_name, status, requested_count, inserted_count, updated_count,
                        skipped_count, failed_count, started_at, finished_at, error_message, request_params
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s::jsonb)
                    RETURNING id
                    """,
                    (
                        payload.get("collector_type", ""),
                        payload.get("source_name", ""),
                        payload.get("status", "COMPLETED"),
                        int(payload.get("requested_count", 0)),
                        int(payload.get("inserted_count", 0)),
                        int(payload.get("updated_count", 0)),
                        int(payload.get("skipped_count", 0)),
                        int(payload.get("failed_count", 0)),
                        payload.get("started_at"),
                        payload.get("error_message", ""),
                        json.dumps(payload.get("request_params", {}), ensure_ascii=False),
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0

    def dashboard(self) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        COUNT(*)::int,
                        COUNT(*) FILTER (WHERE collected_at >= CURRENT_DATE)::int,
                        COUNT(*) FILTER (WHERE content_status = 'READY_TO_REVIEW')::int,
                        COUNT(*) FILTER (WHERE content_status = 'POSTED')::int,
                        COUNT(*) FILTER (WHERE importance_score >= 70)::int,
                        MAX(collected_at)
                    FROM immigration_info.official_notice
                    WHERE active_yn = 'Y'
                    """
                )
                counts = cur.fetchone()
                cur.execute(
                    """
                    SELECT source_type, COUNT(*)::int
                    FROM immigration_info.official_notice
                    WHERE active_yn = 'Y'
                    GROUP BY source_type
                    ORDER BY source_type
                    """
                )
                source_counts = cur.fetchall()
                cur.execute(
                    """
                    SELECT collector_type, source_name, status, inserted_count, updated_count, failed_count, finished_at, error_message
                    FROM immigration_info.collect_log
                    ORDER BY started_at DESC
                    LIMIT 10
                    """
                )
                logs = cur.fetchall()
        return {
            "total_count": counts[0] if counts else 0,
            "collected_today_count": counts[1] if counts else 0,
            "ready_to_review_count": counts[2] if counts else 0,
            "posted_count": counts[3] if counts else 0,
            "high_importance_count": counts[4] if counts else 0,
            "latest_collected_at": counts[5].isoformat() if counts and counts[5] else "",
            "source_counts": [{"source_type": row[0], "count": row[1]} for row in source_counts],
            "recent_logs": [
                {
                    "collector_type": row[0],
                    "source_name": row[1],
                    "status": row[2],
                    "inserted_count": row[3],
                    "updated_count": row[4],
                    "failed_count": row[5],
                    "finished_at": row[6].isoformat() if row[6] else "",
                    "error_message": row[7] or "",
                }
                for row in logs
            ],
        }

    def list_notices(self, params: dict[str, Any]) -> dict[str, Any]:
        page = max(1, int(params.get("page", 1)))
        size = max(1, min(200, int(params.get("size", 20))))
        offset = (page - 1) * size
        where = ["active_yn = 'Y'"]
        values: list[Any] = []
        if params.get("keyword"):
            values.append(f"%{params['keyword']}%")
            where.append("(title_ko ILIKE %s OR summary_en ILIKE %s OR raw_content_ko ILIKE %s)")
            values.extend([values[-1], values[-1]])
        for field in ("source_type", "notice_type", "content_status"):
            if params.get(field):
                values.append(params[field])
                where.append(f"{field} = %s")
        if params.get("visa_type"):
            values.append(json.dumps([params["visa_type"]]))
            where.append("affected_visa_types @> %s::jsonb")
        if params.get("importance_min"):
            values.append(float(params["importance_min"]))
            where.append("importance_score >= %s")
        where_sql = " AND ".join(where)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM immigration_info.official_notice WHERE {where_sql}", tuple(values))
                total = int(cur.fetchone()[0])
                cur.execute(
                    f"""
                    SELECT id, source_name, source_type, notice_type, title_ko, original_url, published_at,
                           collected_at, affected_visa_types, affected_user_groups, importance_score,
                           urgency_level, content_status
                    FROM immigration_info.official_notice
                    WHERE {where_sql}
                    ORDER BY importance_score DESC, published_at DESC NULLS LAST, collected_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    tuple(values + [size, offset]),
                )
                rows = cur.fetchall()
        return {
            "items": [notice_row(row) for row in rows],
            "total_count": total,
            "page": page,
            "size": size,
        }

    def get_notice(self, notice_id: int) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, source, source_name, source_type, notice_type, title_ko, title_en,
                           original_url, canonical_url, published_at, collected_at, updated_at,
                           raw_content_ko, raw_content_en, summary_en, why_it_matters_en,
                           affected_visa_types, affected_user_groups, region_tags, policy_keywords,
                           importance_score, urgency_level, content_status, active_yn, raw_response
                    FROM immigration_info.official_notice
                    WHERE id = %s
                    """,
                    (notice_id,),
                )
                row = cur.fetchone()
        return notice_detail_row(row) if row else {}

    def update_status(self, notice_id: int, status: str) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE immigration_info.official_notice
                    SET content_status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id
                    """,
                    (status, notice_id),
                )
                row = cur.fetchone()
            conn.commit()
        return {"ok": bool(row), "id": notice_id, "content_status": status}

    def insert_publish_log(self, notice_id: int, status: str, error_message: str = "") -> int:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO immigration_info.publish_log(notice_id, status, error_message, created_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                    """,
                    (notice_id, status, error_message),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0


def notice_row(row: tuple) -> dict[str, Any]:
    return {
        "id": row[0],
        "source_name": row[1],
        "source_type": row[2],
        "notice_type": row[3],
        "title_ko": row[4],
        "original_url": row[5],
        "published_at": row[6].isoformat() if row[6] else "",
        "collected_at": row[7].isoformat() if row[7] else "",
        "affected_visa_types": row[8] or [],
        "affected_user_groups": row[9] or [],
        "importance_score": float(row[10] or 0),
        "urgency_level": row[11],
        "content_status": row[12],
    }


def notice_detail_row(row: tuple) -> dict[str, Any]:
    keys = (
        "id", "source", "source_name", "source_type", "notice_type", "title_ko", "title_en",
        "original_url", "canonical_url", "published_at", "collected_at", "updated_at",
        "raw_content_ko", "raw_content_en", "summary_en", "why_it_matters_en",
        "affected_visa_types", "affected_user_groups", "region_tags", "policy_keywords",
        "importance_score", "urgency_level", "content_status", "active_yn", "raw_response",
    )
    result = dict(zip(keys, row))
    for key in ("published_at", "collected_at", "updated_at"):
        result[key] = result[key].isoformat() if result.get(key) else ""
    result["importance_score"] = float(result.get("importance_score") or 0)
    return result
