"""PostgreSQL repository for social news automation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ....storage.db.postgres import connect, load_env_file
from ....utils.hash_utils import stable_hash
from ..collector.google_news_url_resolver import is_acceptable_source_url, is_google_news_url
from ..models import NewsCandidate
from ..normalizer.news_normalizer import normalize_news_item


MIGRATION_PATH = Path(__file__).resolve().parents[3] / "storage" / "db" / "migrations" / "2026_06_02_postgres_runtime_storage.sql"

NEWS_SELECT = """
    id,
    source_type,
    source_url,
    canonical_url,
    google_news_url,
    source_name,
    publisher_name,
    title,
    summary,
    content,
    image_url,
    image_urls_json,
    language,
    category,
    keyword,
    hash_key,
    similarity_key,
    short_summary,
    key_points,
    relevance_reason,
    risk_notes,
    generated_title,
    generated_summary_en,
    generated_why_it_matters_en,
    evaluation_score,
    duplicate_risk_score,
    foreign_worker_relevance_score,
    korea_relevance_score,
    visa_or_labor_policy_score,
    freshness_score,
    source_reliability_score,
    facebook_post_suitability_score,
    selection_reason,
    skip_reason,
    duplicate_group_id,
    facebook_post_url,
    facebook_post_id,
    last_publish_attempt_at,
    publish_attempt_count,
    score_threshold,
    score_breakdown_json,
    telegram_notified,
    fail_reason,
    risk_level,
    post_expired,
    post_expired_at,
    post_expired_reason,
    publish_cycle_id AS cycle_id,
    publish_status,
    status,
    collected_at,
    published_at,
    related_source_count,
    duplicate_count,
    group_item_count,
    last_seen_at,
    is_representative
"""


def json_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return []
        if isinstance(loaded, list):
            return [str(item) for item in loaded if item]
    return []


class NewsRepository:
    def __init__(self) -> None:
        load_env_file()
        self.initialize()

    def initialize(self) -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(MIGRATION_PATH.read_text(encoding="utf-8"))
            conn.commit()

    def _runtime_cycle_id(self, keyword: str = "runtime") -> int:
        cycle_key = "runtime-social-news"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO social_news.pipeline_cycle(cycle_key, keyword, dry_run, trigger_source, status)
                    VALUES (%s, %s, FALSE, 'RUNTIME', 'RUNNING')
                    ON CONFLICT (cycle_key) DO UPDATE
                    SET keyword = EXCLUDED.keyword,
                        status = 'RUNNING'
                    RETURNING id
                    """,
                    (cycle_key, keyword),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0])

    def list_candidates(self) -> list[NewsCandidate]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {NEWS_SELECT} FROM social_news.candidate ORDER BY id")
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [self._row_to_candidate(dict(zip(columns, row))) for row in rows]

    def get_candidate(self, candidate_id: int) -> NewsCandidate | None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT {NEWS_SELECT} FROM social_news.candidate WHERE id = %s",
                    (candidate_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                columns = [column.name for column in cur.description]
        return self._row_to_candidate(dict(zip(columns, row)))

    def list_recent_published(self, limit: int = 20) -> list[NewsCandidate]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {NEWS_SELECT}
                    FROM social_news.candidate
                    WHERE publish_status IN ('POSTED', 'PUBLISHED', 'NOTIFIED', 'DRY_RUN_PUBLISHED', 'DRY_RUN_NOTIFIED')
                       OR status IN ('POSTED', 'PUBLISHED', 'NOTIFIED')
                    ORDER BY published_at DESC NULLS LAST, id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [self._row_to_candidate(dict(zip(columns, row))) for row in rows]

    def list_publish_queue(self, limit: int = 200) -> list[NewsCandidate]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {NEWS_SELECT}
                    FROM social_news.candidate
                    WHERE publish_status IN ('READY_TO_PUBLISH', 'FAILED_RETRYABLE')
                      AND COALESCE(post_expired, FALSE) = FALSE
                      AND COALESCE(is_representative, TRUE) = TRUE
                      AND published_at IS NULL
                      AND COALESCE(facebook_post_url, '') = ''
                      AND COALESCE(risk_level, '') != 'HIGH'
                    ORDER BY evaluation_score DESC, collected_at DESC, id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [self._row_to_candidate(dict(zip(columns, row))) for row in rows]

    def list_ready_for_cycle(self, cycle_id: str, limit: int = 500) -> list[NewsCandidate]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {NEWS_SELECT}
                    FROM social_news.candidate
                    WHERE publish_cycle_id = %s
                      AND publish_status = 'READY_TO_PUBLISH'
                      AND COALESCE(post_expired, FALSE) = FALSE
                      AND COALESCE(is_representative, TRUE) = TRUE
                      AND published_at IS NULL
                      AND COALESCE(facebook_post_url, '') = ''
                    ORDER BY evaluation_score DESC, collected_at DESC, id DESC
                    LIMIT %s
                    """,
                    (cycle_id, limit),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [self._row_to_candidate(dict(zip(columns, row))) for row in rows]

    def list_expandable_for_cycle(self, cycle_id: str, limit: int = 500) -> list[NewsCandidate]:
        statuses = (
            "COLLECTED",
            "NORMALIZED",
            "SUMMARIZED",
            "SCORED",
            "SKIPPED",
            "SKIPPED_LOW_SCORE",
            "FAILED_RETRYABLE",
        )
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {NEWS_SELECT}
                    FROM social_news.candidate
                    WHERE publish_cycle_id = %s
                      AND COALESCE(post_expired, FALSE) = FALSE
                      AND COALESCE(is_representative, TRUE) = TRUE
                      AND published_at IS NULL
                      AND COALESCE(facebook_post_url, '') = ''
                      AND COALESCE(risk_level, '') != 'HIGH'
                      AND (
                          status = ANY(%s)
                          OR publish_status = ANY(%s)
                      )
                    ORDER BY evaluation_score DESC, collected_at DESC, id DESC
                    LIMIT %s
                    """,
                    (cycle_id, list(statuses), list(statuses), limit),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [self._row_to_candidate(dict(zip(columns, row))) for row in rows]

    def list_publish_candidates_for_cycle(self, cycle_id: str, limit: int = 1000) -> list[NewsCandidate]:
        statuses = (
            "READY_TO_PUBLISH",
            "FAILED_RETRYABLE",
            "COLLECTED",
            "NORMALIZED",
            "SUMMARIZED",
            "SCORED",
            "SKIPPED_LOW_SCORE",
        )
        excluded = (
            "POSTED",
            "PUBLISHED",
            "NOTIFIED",
            "DRY_RUN_PUBLISHED",
            "DRY_RUN_NOTIFIED",
            "POST_EXPIRED",
            "ARCHIVED",
            "AUTO_RETRY_BLOCKED",
            "DUPLICATE",
            "TEXT_INVALID",
        )
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {NEWS_SELECT}
                    FROM social_news.candidate
                    WHERE publish_cycle_id = %s
                      AND COALESCE(post_expired, FALSE) = FALSE
                      AND COALESCE(is_representative, TRUE) = TRUE
                      AND published_at IS NULL
                      AND COALESCE(facebook_post_url, '') = ''
                      AND NOT (COALESCE(status, '') = ANY(%s))
                      AND NOT (COALESCE(publish_status, '') = ANY(%s))
                      AND (
                          COALESCE(status, '') = ANY(%s)
                          OR COALESCE(publish_status, '') = ANY(%s)
                      )
                    ORDER BY evaluation_score DESC, collected_at DESC, id DESC
                    LIMIT %s
                    """,
                    (cycle_id, list(excluded), list(excluded), list(statuses), list(statuses), limit),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [self._row_to_candidate(dict(zip(columns, row))) for row in rows]

    def save(self, item: Any) -> NewsCandidate:
        candidate = normalize_news_item(item)
        candidate.status = candidate.status or "NORMALIZED"
        candidate.publish_status = candidate.publish_status or candidate.status
        runtime_cycle_id = self._runtime_cycle_id(candidate.keyword or "foreign worker visa Korea")
        source_hash = candidate.hash_key
        occurrence_hash = stable_hash(f"{source_hash}:{candidate.collected_at}:{runtime_cycle_id}:{candidate.source_type}")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO social_news.raw_item(
                        cycle_id, collector_module_key, source_type, source_url, google_news_url, source_name, publisher_name, search_keyword,
                        raw_title, raw_summary, raw_content, language, category, collected_at, hash_key, source_hash, raw_payload
                    )
                    VALUES (%s, 'social_news_bot', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING id
                    """,
                    (
                        runtime_cycle_id,
                        candidate.source_type,
                        candidate.source_url,
                        candidate.google_news_url,
                        candidate.source_name,
                        candidate.publisher_name,
                        candidate.keyword,
                        candidate.title,
                        candidate.summary,
                        candidate.content,
                        candidate.language,
                        candidate.category,
                        candidate.collected_at,
                        occurrence_hash,
                        source_hash,
                        json.dumps(candidate.to_dict(), ensure_ascii=False),
                    ),
                )
                raw_item_id = int(cur.fetchone()[0])
                cur.execute(
                    """
                    INSERT INTO social_news.normalized_item(
                        raw_item_id, cycle_id, source_type, source_url, canonical_url, google_news_url, source_name, publisher_name, title, summary,
                        content, image_url, image_urls_json, language, category, keyword, hash_key, title_hash, similarity_key
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (hash_key) DO UPDATE
                    SET source_url = EXCLUDED.source_url,
                        canonical_url = EXCLUDED.canonical_url,
                        google_news_url = EXCLUDED.google_news_url,
                        source_name = EXCLUDED.source_name,
                        publisher_name = EXCLUDED.publisher_name,
                        title = EXCLUDED.title,
                        summary = EXCLUDED.summary,
                        content = EXCLUDED.content,
                        image_url = EXCLUDED.image_url,
                        image_urls_json = EXCLUDED.image_urls_json,
                        similarity_key = EXCLUDED.similarity_key,
                        normalized_at = CURRENT_TIMESTAMP
                    RETURNING id
                    """,
                    (
                        raw_item_id,
                        runtime_cycle_id,
                        candidate.source_type,
                        candidate.source_url,
                        safe_canonical_url(candidate),
                        candidate.google_news_url,
                        candidate.source_name,
                        candidate.publisher_name,
                        candidate.title,
                        candidate.summary,
                        candidate.content,
                        candidate.image_url,
                        json.dumps(candidate.image_urls or [], ensure_ascii=False),
                        candidate.language,
                        candidate.category,
                        candidate.keyword,
                        candidate.hash_key,
                        candidate.hash_key,
                        candidate.similarity_key,
                    ),
                )
                normalized_item_id = int(cur.fetchone()[0])
                cur.execute(
                    """
                    UPDATE social_news.raw_item
                    SET normalized_item_id = %s,
                        is_duplicate = EXISTS (
                            SELECT 1 FROM social_news.raw_item older
                            WHERE older.source_hash = %s
                              AND older.id <> %s
                        ),
                        duplicate_reason = CASE
                            WHEN EXISTS (
                                SELECT 1 FROM social_news.raw_item older
                                WHERE older.source_hash = %s
                                  AND older.id <> %s
                            ) THEN 'SOURCE_HASH_DUPLICATE'
                            ELSE NULL
                        END
                    WHERE id = %s
                    """,
                    (normalized_item_id, source_hash, raw_item_id, source_hash, raw_item_id, raw_item_id),
                )
                cur.execute(
                    """
                    UPDATE social_news.normalized_item
                    SET raw_item_count = stats.raw_count,
                        last_seen_at = stats.last_seen_at,
                        normalized_at = CURRENT_TIMESTAMP
                    FROM (
                        SELECT COUNT(*)::int AS raw_count, MAX(collected_at) AS last_seen_at
                        FROM social_news.raw_item
                        WHERE normalized_item_id = %s
                    ) stats
                    WHERE id = %s
                    """,
                    (normalized_item_id, normalized_item_id),
                )
                cur.execute(
                    """
                    SELECT COUNT(*)::int AS raw_count,
                           GREATEST(COUNT(*)::int - 1, 0) AS duplicate_count,
                           COUNT(DISTINCT COALESCE(NULLIF(source_name, ''), source_url))::int AS related_source_count,
                           MAX(collected_at) AS last_seen_at
                    FROM social_news.raw_item
                    WHERE normalized_item_id = %s
                    """,
                    (normalized_item_id,),
                )
                raw_count, duplicate_count, related_source_count, last_seen_at = cur.fetchone()
                cur.execute(
                    """
                    SELECT id
                    FROM social_news.candidate
                    WHERE normalized_item_id = %s
                      AND COALESCE(is_representative, TRUE) = TRUE
                    ORDER BY id ASC
                    LIMIT 1
                    """,
                    (normalized_item_id,),
                )
                existing_row = cur.fetchone()
                if existing_row:
                    candidate.id = int(existing_row[0])
                    cur.execute(
                        """
                        UPDATE social_news.candidate
                        SET related_source_count = %s,
                            duplicate_count = %s,
                            group_item_count = %s,
                            last_seen_at = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (related_source_count, duplicate_count, raw_count, last_seen_at, candidate.id),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO social_news.candidate(
                            normalized_item_id, source_type, source_url, canonical_url, google_news_url, source_name, publisher_name, title, summary,
                            content, image_url, image_urls_json, language, category, keyword, hash_key, title_hash, similarity_key, short_summary,
                            key_points, relevance_reason, risk_notes, generated_title, generated_summary_en, generated_why_it_matters_en,
                            evaluation_score, duplicate_risk_score,
                            foreign_worker_relevance_score, korea_relevance_score, visa_or_labor_policy_score,
                            freshness_score, source_reliability_score, facebook_post_suitability_score,
                            selection_reason, skip_reason, facebook_post_url, facebook_post_id,
                            last_publish_attempt_at, publish_attempt_count, score_threshold, score_breakdown_json,
                            telegram_notified, fail_reason, risk_level, post_expired, post_expired_at,
                            post_expired_reason, publish_cycle_id, publish_status, status, collected_at, published_at,
                            related_source_count, duplicate_count, group_item_count, last_seen_at, is_representative
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        RETURNING id
                        """,
                        self._candidate_values(candidate, normalized_item_id),
                    )
                    candidate.id = int(cur.fetchone()[0])
                    candidate.duplicate_group_id = candidate.duplicate_group_id or candidate.id
                    cur.execute(
                        """
                        UPDATE social_news.candidate
                        SET duplicate_group_id = %s,
                            related_source_count = %s,
                            duplicate_count = %s,
                            group_item_count = %s,
                            last_seen_at = %s
                        WHERE id = %s
                        """,
                        (candidate.duplicate_group_id, related_source_count, duplicate_count, raw_count, last_seen_at, candidate.id),
                    )
            conn.commit()
        if existing_row:
            existing = self.get_candidate(candidate.id)
            if existing:
                existing.existing_representative = True
                return existing
        return candidate

    def update_candidate(self, candidate: NewsCandidate) -> NewsCandidate:
        if candidate.id is None:
            raise ValueError("candidate.id is required for update")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE social_news.candidate
                    SET source_type = %s, source_url = %s, canonical_url = %s, google_news_url = %s,
                        source_name = %s, publisher_name = %s, title = %s, summary = %s, content = %s,
                        image_url = %s, image_urls_json = %s::jsonb,
                        language = %s, category = %s, keyword = %s, hash_key = %s, similarity_key = %s,
                        short_summary = %s, key_points = %s, relevance_reason = %s, risk_notes = %s,
                        generated_title = %s, generated_summary_en = %s, generated_why_it_matters_en = %s,
                        evaluation_score = %s, duplicate_risk_score = %s, foreign_worker_relevance_score = %s,
                        korea_relevance_score = %s, visa_or_labor_policy_score = %s, freshness_score = %s,
                        source_reliability_score = %s, facebook_post_suitability_score = %s,
                        selection_reason = %s, skip_reason = %s, duplicate_group_id = %s,
                        facebook_post_url = %s, facebook_post_id = %s, last_publish_attempt_at = %s,
                        publish_attempt_count = %s, score_threshold = %s, score_breakdown_json = %s,
                        telegram_notified = %s, fail_reason = %s, risk_level = %s, post_expired = %s,
                        post_expired_at = %s, post_expired_reason = %s, publish_cycle_id = %s,
                        publish_status = %s, status = %s, collected_at = %s, published_at = %s,
                        related_source_count = %s, duplicate_count = %s, group_item_count = %s,
                        last_seen_at = %s, is_representative = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    self._candidate_update_values(candidate),
                )
            conn.commit()
        return candidate

    def mark_status(
        self,
        candidate_id: int,
        status: str,
        published_at: str | None = None,
        evaluation_score: float | None = None,
        duplicate_risk_score: float | None = None,
        duplicate_group_id: int | None = None,
        facebook_post_url: str | None = None,
        facebook_post_id: str | None = None,
        last_publish_attempt_at: str | None = None,
        publish_attempt_count: int | None = None,
        telegram_notified: bool | None = None,
        fail_reason: str | None = None,
        post_expired: bool | None = None,
        post_expired_at: str | None = None,
        post_expired_reason: str | None = None,
        cycle_id: str | None = None,
        publish_status: str | None = None,
    ) -> None:
        assignments = ["status = %s", "updated_at = CURRENT_TIMESTAMP"]
        values: list[Any] = [status]
        optional = {
            "published_at": published_at,
            "evaluation_score": evaluation_score,
            "duplicate_risk_score": duplicate_risk_score,
            "duplicate_group_id": duplicate_group_id,
            "facebook_post_url": facebook_post_url,
            "facebook_post_id": facebook_post_id,
            "last_publish_attempt_at": last_publish_attempt_at,
            "publish_attempt_count": publish_attempt_count,
            "telegram_notified": telegram_notified,
            "fail_reason": fail_reason,
            "post_expired": post_expired,
            "post_expired_at": post_expired_at,
            "post_expired_reason": post_expired_reason,
            "publish_cycle_id": cycle_id,
            "publish_status": publish_status,
        }
        for column, value in optional.items():
            if value is not None:
                assignments.append(f"{column} = %s")
                values.append(value)
        values.append(candidate_id)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE social_news.candidate SET {', '.join(assignments)} WHERE id = %s", values)
            conn.commit()

    def mark_ready_to_publish(self, limit: int = 5) -> list[NewsCandidate]:
        candidates = self.list_publish_queue(limit=limit)
        if candidates:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE social_news.candidate
                        SET status = 'READY_TO_PUBLISH', publish_status = 'READY_TO_PUBLISH', updated_at = CURRENT_TIMESTAMP
                        WHERE id = ANY(%s)
                        """,
                        ([candidate.id for candidate in candidates],),
                    )
                conn.commit()
        return candidates

    def mark_published(self, candidate_id: int, published_at: str) -> None:
        self.mark_status(candidate_id, "PUBLISHED", published_at=published_at, publish_status="PUBLISHED")

    def mark_notified(self, candidate_id: int) -> None:
        self.mark_status(candidate_id, "NOTIFIED", publish_status="NOTIFIED")

    def insert_facebook_log(
        self,
        news_candidate_id: int,
        status: str,
        published_at: str,
        page_id: str = "",
        facebook_post_id: str = "",
        facebook_permalink: str = "",
        score: float = 0.0,
        threshold: float = 0.0,
        message_preview: str = "",
        response_code: str = "",
        response_body: str = "",
        error_code: str = "",
        error_message: str = "",
    ) -> int:
        cycle_id = self._runtime_cycle_id()
        response_payload = {"code": response_code, "body": response_body[:1000], "permalink": facebook_permalink}
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO social_news.publish_log(
                        cycle_id, news_candidate_id, channel, page_id, external_post_id, dry_run, status,
                        response_payload, error_code, error_message, published_at, facebook_permalink,
                        score, threshold, message_preview, response_code, response_body
                    )
                    VALUES (%s, %s, 'facebook', %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        cycle_id,
                        news_candidate_id,
                        page_id,
                        facebook_post_id,
                        status == "DRY_RUN",
                        status,
                        json.dumps(response_payload, ensure_ascii=False),
                        error_code,
                        error_message,
                        published_at,
                        facebook_permalink,
                        score,
                        threshold,
                        message_preview[:1000],
                        response_code,
                        response_body[:1000],
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0])

    def insert_telegram_log(
        self,
        message: str,
        status: str,
        sent_at: str,
        news_candidate_id: int | None = None,
        error_message: str = "",
    ) -> int:
        cycle_id = self._runtime_cycle_id()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO social_news.telegram_notify_log(
                        cycle_id, news_candidate_id, dry_run, message, status, error_message, sent_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (cycle_id, news_candidate_id, status == "DRY_RUN", message, status, error_message, sent_at),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0])

    def insert_pipeline_log(
        self,
        step: str,
        status: str,
        message: str,
        news_candidate_id: int | None = None,
        payload_json: str = "",
        created_at: str = "",
    ) -> int:
        from ....utils.date_utils import utc_now_iso

        cycle_id = self._runtime_cycle_id()
        payload = payload_json if payload_json else "{}"
        created = created_at or utc_now_iso()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO social_news.pipeline_step_log(
                        cycle_id, module_key, step_name, status, skipped_reason, detail_json,
                        news_candidate_id, message, payload_json, created_at, started_at
                    )
                    VALUES (%s, 'social_news_bot', %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, %s, %s)
                    RETURNING id
                    """,
                    (cycle_id, step, status, message, payload, news_candidate_id, message, payload, created, created),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0])

    def list_pipeline_logs(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, news_candidate_id, step_name AS step, status,
                           COALESCE(message, skipped_reason, '') AS message,
                           payload_json::text AS payload_json,
                           created_at
                    FROM social_news.pipeline_step_log
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [dict(zip(columns, row)) for row in rows]

    def last_successful_facebook_publish_at(self) -> str:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT published_at
                    FROM social_news.publish_log
                    WHERE channel = 'facebook'
                      AND status IN ('PUBLISHED', 'DRY_RUN')
                    ORDER BY published_at DESC, id DESC
                    LIMIT 1
                    """
                )
                row = cur.fetchone()
        return str(row[0] or "") if row else ""

    def expire_ready_before_cycle(self, new_cycle_id: str, expired_at: str, reason: str = "DAILY_CYCLE_EXPIRED") -> tuple[int, str]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT MIN(publish_cycle_id) AS target_cycle_id
                    FROM social_news.candidate
                    WHERE publish_cycle_id < %s
                      AND publish_status = 'READY_TO_PUBLISH'
                      AND COALESCE(post_expired, FALSE) = FALSE
                      AND published_at IS NULL
                    """,
                    (new_cycle_id,),
                )
                target_row = cur.fetchone()
                cur.execute(
                    """
                    UPDATE social_news.candidate
                    SET post_expired = TRUE,
                        post_expired_at = %s,
                        post_expired_reason = %s,
                        publish_status = 'POST_EXPIRED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE publish_cycle_id < %s
                      AND publish_status = 'READY_TO_PUBLISH'
                      AND COALESCE(post_expired, FALSE) = FALSE
                      AND published_at IS NULL
                    """,
                    (expired_at, reason, new_cycle_id),
                )
                count = cur.rowcount or 0
            conn.commit()
        return int(count), str((target_row or [""])[0] or "")

    def delete_candidates(self, candidate_ids: list[int]) -> int:
        ids = [int(candidate_id) for candidate_id in candidate_ids if candidate_id]
        if not ids:
            return 0
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM social_news.telegram_notify_log WHERE news_candidate_id = ANY(%s)", (ids,))
                cur.execute("DELETE FROM social_news.publish_log WHERE news_candidate_id = ANY(%s)", (ids,))
                cur.execute("DELETE FROM social_news.pipeline_step_log WHERE news_candidate_id = ANY(%s)", (ids,))
                cur.execute("DELETE FROM social_news.candidate WHERE id = ANY(%s)", (ids,))
                deleted = cur.rowcount or 0
            conn.commit()
        return int(deleted)

    def _candidate_values(self, candidate: NewsCandidate, normalized_item_id: int) -> tuple[Any, ...]:
        return (
            normalized_item_id,
            candidate.source_type,
            candidate.source_url,
            safe_canonical_url(candidate),
            candidate.google_news_url,
            candidate.source_name,
            candidate.publisher_name,
            candidate.title,
            candidate.summary,
            candidate.content,
            candidate.image_url,
            json.dumps(candidate.image_urls or [], ensure_ascii=False),
            candidate.language,
            candidate.category,
            candidate.keyword,
            candidate.hash_key,
            candidate.hash_key,
            candidate.similarity_key,
            candidate.short_summary,
            candidate.key_points,
            candidate.relevance_reason,
            candidate.risk_notes,
            candidate.generated_title,
            candidate.generated_summary_en,
            candidate.generated_why_it_matters_en,
            candidate.evaluation_score,
            candidate.duplicate_risk_score,
            candidate.foreign_worker_relevance_score,
            candidate.korea_relevance_score,
            candidate.visa_or_labor_policy_score,
            candidate.freshness_score,
            candidate.source_reliability_score,
            candidate.facebook_post_suitability_score,
            candidate.selection_reason,
            candidate.skip_reason,
            candidate.facebook_post_url,
            candidate.facebook_post_id,
            candidate.last_publish_attempt_at or None,
            candidate.publish_attempt_count,
            candidate.score_threshold,
            candidate.score_breakdown_json,
            candidate.telegram_notified,
            candidate.fail_reason,
            candidate.risk_level,
            candidate.post_expired,
            candidate.post_expired_at or None,
            candidate.post_expired_reason,
            candidate.cycle_id,
            candidate.publish_status,
            candidate.status,
            candidate.collected_at,
            candidate.published_at,
            candidate.related_source_count,
            candidate.duplicate_count,
            candidate.group_item_count,
            candidate.last_seen_at or candidate.collected_at or None,
            candidate.is_representative,
        )

    def _candidate_update_values(self, candidate: NewsCandidate) -> tuple[Any, ...]:
        return (
            candidate.source_type,
            candidate.source_url,
            safe_canonical_url(candidate),
            candidate.google_news_url,
            candidate.source_name,
            candidate.publisher_name,
            candidate.title,
            candidate.summary,
            candidate.content,
            candidate.image_url,
            json.dumps(candidate.image_urls or [], ensure_ascii=False),
            candidate.language,
            candidate.category,
            candidate.keyword,
            candidate.hash_key,
            candidate.similarity_key,
            candidate.short_summary,
            candidate.key_points,
            candidate.relevance_reason,
            candidate.risk_notes,
            candidate.generated_title,
            candidate.generated_summary_en,
            candidate.generated_why_it_matters_en,
            candidate.evaluation_score,
            candidate.duplicate_risk_score,
            candidate.foreign_worker_relevance_score,
            candidate.korea_relevance_score,
            candidate.visa_or_labor_policy_score,
            candidate.freshness_score,
            candidate.source_reliability_score,
            candidate.facebook_post_suitability_score,
            candidate.selection_reason,
            candidate.skip_reason,
            candidate.duplicate_group_id,
            candidate.facebook_post_url,
            candidate.facebook_post_id,
            candidate.last_publish_attempt_at or None,
            candidate.publish_attempt_count,
            candidate.score_threshold,
            candidate.score_breakdown_json,
            candidate.telegram_notified,
            candidate.fail_reason,
            candidate.risk_level,
            candidate.post_expired,
            candidate.post_expired_at or None,
            candidate.post_expired_reason,
            candidate.cycle_id,
            candidate.publish_status,
            candidate.status,
            candidate.collected_at,
            candidate.published_at,
            candidate.related_source_count,
            candidate.duplicate_count,
            candidate.group_item_count,
            candidate.last_seen_at or candidate.collected_at or None,
            candidate.is_representative,
            candidate.id,
        )

    def _row_to_candidate(self, row: dict[str, Any], status: str | None = None) -> NewsCandidate:
        return NewsCandidate(
            id=int(row["id"]),
            source_type=row.get("source_type") or "",
            source_url=safe_url(row.get("source_url") or ""),
            canonical_url=safe_url(row.get("canonical_url") or ""),
            google_news_url=row.get("google_news_url") or "",
            source_name=row.get("source_name") or "",
            publisher_name=row.get("publisher_name") or row.get("source_name") or "",
            title=row.get("title") or "",
            summary=row.get("summary") or "",
            content=row.get("content") or "",
            image_url=row.get("image_url") or "",
            image_urls=json_list(row.get("image_urls_json")),
            language=row.get("language") or "ko",
            category=row.get("category") or "",
            keyword=row.get("keyword") or "",
            hash_key=row.get("hash_key") or "",
            similarity_key=row.get("similarity_key") or "",
            short_summary=row.get("short_summary") or "",
            key_points=row.get("key_points") or "",
            relevance_reason=row.get("relevance_reason") or "",
            risk_notes=row.get("risk_notes") or "",
            generated_title=row.get("generated_title") or "",
            generated_summary_en=row.get("generated_summary_en") or "",
            generated_why_it_matters_en=row.get("generated_why_it_matters_en") or "",
            evaluation_score=float(row.get("evaluation_score") or 0.0),
            duplicate_risk_score=float(row.get("duplicate_risk_score") or 0.0),
            foreign_worker_relevance_score=float(row.get("foreign_worker_relevance_score") or 0.0),
            korea_relevance_score=float(row.get("korea_relevance_score") or 0.0),
            visa_or_labor_policy_score=float(row.get("visa_or_labor_policy_score") or 0.0),
            freshness_score=float(row.get("freshness_score") or 0.0),
            source_reliability_score=float(row.get("source_reliability_score") or 0.0),
            facebook_post_suitability_score=float(row.get("facebook_post_suitability_score") or 0.0),
            selection_reason=row.get("selection_reason") or "",
            skip_reason=row.get("skip_reason") or "",
            facebook_post_url=row.get("facebook_post_url") or "",
            facebook_post_id=row.get("facebook_post_id") or "",
            last_publish_attempt_at=str(row.get("last_publish_attempt_at") or ""),
            publish_attempt_count=int(row.get("publish_attempt_count") or 0),
            score_threshold=float(row.get("score_threshold") or 0.0),
            score_breakdown_json=row.get("score_breakdown_json") or "",
            telegram_notified=bool(row.get("telegram_notified")),
            fail_reason=row.get("fail_reason") or "",
            risk_level=row.get("risk_level") or "",
            post_expired=bool(row.get("post_expired")),
            post_expired_at=str(row.get("post_expired_at") or ""),
            post_expired_reason=row.get("post_expired_reason") or "",
            cycle_id=row.get("cycle_id") or "",
            publish_status=row.get("publish_status") or row.get("status") or "",
            duplicate_group_id=row.get("duplicate_group_id"),
            status=status or row.get("status") or "",
            collected_at=str(row.get("collected_at") or ""),
            published_at=str(row.get("published_at")) if row.get("published_at") else None,
            related_source_count=int(row.get("related_source_count") or 1),
            duplicate_count=int(row.get("duplicate_count") or 0),
            group_item_count=int(row.get("group_item_count") or 1),
            last_seen_at=str(row.get("last_seen_at") or ""),
            is_representative=bool(row.get("is_representative", True)),
        )


def safe_url(value: str) -> str:
    url = (value or "").strip()
    if not url or is_google_news_url(url) or not is_acceptable_source_url(url):
        return ""
    return url


def safe_canonical_url(candidate: NewsCandidate) -> str:
    return safe_url(candidate.canonical_url) or safe_url(candidate.source_url)
