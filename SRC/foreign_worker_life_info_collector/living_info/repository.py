"""PostgreSQL repository skeleton for living information tables."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..storage.db.postgres import connect, load_env_file
from .models import (
    LivingNormalizedItem,
    LivingSourceItem,
    LivingSourceSignal,
    LivingTopicCluster,
)


REQUIRED_TABLES = {
    "source_item",
    "normalized_item",
    "source_signal",
    "topic_cluster",
    "topic_cluster_item",
}


class LivingInfoRepository:
    """Repository methods are explicit; this class does not run migrations."""

    def __init__(self) -> None:
        load_env_file()

    def schema_state(self) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'living_info'
                    ORDER BY table_name
                    """
                )
                tables = [row[0] for row in cur.fetchall()]
                cur.execute(
                    """
                    SELECT indexname
                    FROM pg_indexes
                    WHERE schemaname = 'living_info'
                    ORDER BY indexname
                    """
                )
                indexes = [row[0] for row in cur.fetchall()]
                cur.execute(
                    """
                    SELECT table_name, constraint_name, constraint_type
                    FROM information_schema.table_constraints
                    WHERE table_schema = 'living_info'
                    ORDER BY table_name, constraint_type, constraint_name
                    """
                )
                constraints = [
                    {"table_name": row[0], "constraint_name": row[1], "constraint_type": row[2]}
                    for row in cur.fetchall()
                ]
        return {
            "ready": REQUIRED_TABLES.issubset(set(tables)),
            "tables": tables,
            "missing_tables": sorted(REQUIRED_TABLES - set(tables)),
            "index_count": len(indexes),
            "indexes": indexes,
            "constraint_count": len(constraints),
            "constraints": constraints,
        }

    def require_schema_ready(self) -> None:
        state = self.schema_state()
        if not state["ready"]:
            missing = ", ".join(state["missing_tables"])
            raise RuntimeError(f"living_info schema is not ready. missing={missing}")

    def counts(self) -> dict[str, int]:
        self.require_schema_ready()
        with connect() as conn:
            with conn.cursor() as cur:
                result: dict[str, int] = {}
                for table in sorted(REQUIRED_TABLES):
                    cur.execute(f"SELECT COUNT(*)::int FROM living_info.{table}")
                    result[table] = int(cur.fetchone()[0])
        return result

    def upsert_source_item(self, item: LivingSourceItem) -> int:
        self.require_schema_ready()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO living_info.source_item (
                        source_url, canonical_url, publishable_link_url, source_name, source_type,
                        source_access_policy, language, country, region_in_korea, raw_title,
                        raw_summary, raw_body, published_at, collected_at, last_checked_at,
                        source_trust_level, privacy_risk_level, duplicate_key, content_hash,
                        source_status, active_yn, raw_ref_table, raw_ref_id, raw_payload
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        NULLIF(%s, '')::timestamptz,
                        COALESCE(NULLIF(%s, '')::timestamptz, CURRENT_TIMESTAMP),
                        NULLIF(%s, '')::timestamptz,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
                    )
                    ON CONFLICT (duplicate_key) DO UPDATE
                    SET canonical_url = EXCLUDED.canonical_url,
                        publishable_link_url = EXCLUDED.publishable_link_url,
                        source_name = EXCLUDED.source_name,
                        raw_title = EXCLUDED.raw_title,
                        raw_summary = EXCLUDED.raw_summary,
                        raw_body = COALESCE(NULLIF(EXCLUDED.raw_body, ''), living_info.source_item.raw_body),
                        last_checked_at = COALESCE(EXCLUDED.last_checked_at, CURRENT_TIMESTAMP),
                        source_trust_level = EXCLUDED.source_trust_level,
                        privacy_risk_level = EXCLUDED.privacy_risk_level,
                        content_hash = COALESCE(NULLIF(EXCLUDED.content_hash, ''), living_info.source_item.content_hash),
                        source_status = EXCLUDED.source_status,
                        active_yn = EXCLUDED.active_yn,
                        raw_payload = living_info.source_item.raw_payload || EXCLUDED.raw_payload,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                    """,
                    source_item_values(item),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0

    def upsert_normalized_item(self, item: LivingNormalizedItem) -> int:
        self.require_schema_ready()
        if not item.source_item_id:
            raise ValueError("source_item_id is required.")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO living_info.normalized_item (
                        source_item_id, normalized_primary_category, normalized_secondary_category,
                        source_usage, info_signal_type, target_user, action_type, topic_key_candidate,
                        validation_needed_yn, validation_source_type, actionability_score,
                        repeatability_score, source_reliability_score, normalization_confidence,
                        normalization_reason, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_item_id) DO UPDATE
                    SET normalized_primary_category = EXCLUDED.normalized_primary_category,
                        normalized_secondary_category = EXCLUDED.normalized_secondary_category,
                        source_usage = EXCLUDED.source_usage,
                        info_signal_type = EXCLUDED.info_signal_type,
                        target_user = EXCLUDED.target_user,
                        action_type = EXCLUDED.action_type,
                        topic_key_candidate = EXCLUDED.topic_key_candidate,
                        validation_needed_yn = EXCLUDED.validation_needed_yn,
                        validation_source_type = EXCLUDED.validation_source_type,
                        actionability_score = EXCLUDED.actionability_score,
                        repeatability_score = EXCLUDED.repeatability_score,
                        source_reliability_score = EXCLUDED.source_reliability_score,
                        normalization_confidence = EXCLUDED.normalization_confidence,
                        normalization_reason = EXCLUDED.normalization_reason,
                        status = EXCLUDED.status,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                    """,
                    normalized_item_values(item),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0

    def insert_source_signal(self, signal: LivingSourceSignal) -> int:
        self.require_schema_ready()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO living_info.source_signal (
                        signal_source_name, signal_source_url, signal_platform, signal_type, language,
                        country, region_in_korea, primary_category, topic_key_candidate, target_user,
                        pain_point_summary, signal_count, privacy_risk_level, source_access_policy,
                        validation_needed_yn, status, observed_at, raw_payload
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, COALESCE(NULLIF(%s, '')::timestamptz, CURRENT_TIMESTAMP), %s::jsonb
                    )
                    RETURNING id
                    """,
                    source_signal_values(signal),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0

    def upsert_topic_cluster(self, cluster: LivingTopicCluster) -> int:
        self.require_schema_ready()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO living_info.topic_cluster (
                        topic_key, primary_category, secondary_category, target_user, action_type,
                        source_count, evidence_count, community_signal_count, official_source_count,
                        secondary_source_count, source_spread_count, readiness_score,
                        public_candidate_ready_yn, validation_status, cluster_status,
                        last_signal_at, last_evidence_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        NULLIF(%s, '')::timestamptz, NULLIF(%s, '')::timestamptz
                    )
                    ON CONFLICT (topic_key, primary_category, target_user, action_type) DO UPDATE
                    SET secondary_category = EXCLUDED.secondary_category,
                        source_count = EXCLUDED.source_count,
                        evidence_count = EXCLUDED.evidence_count,
                        community_signal_count = EXCLUDED.community_signal_count,
                        official_source_count = EXCLUDED.official_source_count,
                        secondary_source_count = EXCLUDED.secondary_source_count,
                        source_spread_count = EXCLUDED.source_spread_count,
                        readiness_score = EXCLUDED.readiness_score,
                        public_candidate_ready_yn = EXCLUDED.public_candidate_ready_yn,
                        validation_status = EXCLUDED.validation_status,
                        cluster_status = EXCLUDED.cluster_status,
                        last_signal_at = COALESCE(EXCLUDED.last_signal_at, living_info.topic_cluster.last_signal_at),
                        last_evidence_at = COALESCE(EXCLUDED.last_evidence_at, living_info.topic_cluster.last_evidence_at),
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                    """,
                    topic_cluster_values(cluster),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0

    def list_source_items(self, limit: int = 50, status: str = "") -> list[dict[str, Any]]:
        self.require_schema_ready()
        limit = max(1, min(int(limit or 50), 500))
        where = []
        values: list[Any] = []
        if status:
            where.append("source_status = %s")
            values.append(status)
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, source_url, canonical_url, publishable_link_url, source_name, source_type,
                           language, country, raw_title, raw_summary, source_trust_level,
                           privacy_risk_level, duplicate_key, content_hash, source_status,
                           active_yn, raw_ref_table, raw_ref_id, collected_at, updated_at
                    FROM living_info.source_item
                    {where_sql}
                    ORDER BY collected_at DESC, id DESC
                    LIMIT %s
                    """,
                    tuple(values + [limit]),
                )
                rows = cur.fetchall()
        return [source_item_row(row) for row in rows]

    def list_normalized_items_for_clustering(self, limit: int = 100) -> list[dict[str, Any]]:
        self.require_schema_ready()
        limit = max(1, min(int(limit or 100), 500))
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        ni.id AS normalized_item_id,
                        ni.source_item_id,
                        ni.normalized_primary_category,
                        ni.normalized_secondary_category,
                        ni.source_usage,
                        ni.info_signal_type,
                        ni.target_user,
                        ni.action_type,
                        ni.topic_key_candidate,
                        ni.actionability_score,
                        ni.repeatability_score,
                        ni.source_reliability_score,
                        ni.normalization_confidence,
                        ni.status,
                        si.source_url,
                        si.canonical_url,
                        si.publishable_link_url,
                        si.source_name,
                        si.source_type,
                        si.source_trust_level,
                        si.raw_title,
                        si.raw_summary,
                        si.published_at,
                        si.collected_at
                    FROM living_info.normalized_item ni
                    JOIN living_info.source_item si
                      ON si.id = ni.source_item_id
                    WHERE COALESCE(ni.topic_key_candidate, '') <> ''
                      AND ni.source_usage IN ('TOPIC_CLUSTER_MATERIAL', 'SOURCE_EVIDENCE')
                      AND COALESCE(ni.status, '') NOT IN ('BLOCKED', 'SKIPPED')
                      AND COALESCE(si.active_yn, 'Y') = 'Y'
                      AND COALESCE(si.source_url, '') <> ''
                    ORDER BY ni.updated_at DESC, si.collected_at DESC NULLS LAST, ni.id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
        return [normalized_cluster_item_row(row) for row in rows]

    def upsert_topic_cluster_item_normalized(
        self,
        *,
        topic_cluster_id: int,
        normalized_item_id: int,
        item_role: str = "EVIDENCE",
        weight_score: float = 1.0,
    ) -> int:
        self.require_schema_ready()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO living_info.topic_cluster_item (
                        topic_cluster_id, normalized_item_id, source_signal_id, item_role, weight_score
                    )
                    VALUES (%s, %s, NULL, %s, %s)
                    ON CONFLICT (topic_cluster_id, normalized_item_id)
                    WHERE normalized_item_id IS NOT NULL
                    DO UPDATE
                    SET item_role = EXCLUDED.item_role,
                        weight_score = EXCLUDED.weight_score
                    RETURNING id
                    """,
                    (int(topic_cluster_id), int(normalized_item_id), item_role, float(weight_score or 0)),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0]) if row else 0

    def list_ready_topic_clusters(self, limit: int = 100) -> list[dict[str, Any]]:
        self.require_schema_ready()
        limit = max(1, min(int(limit or 100), 500))
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, topic_key, primary_category, secondary_category, target_user,
                           action_type, source_count, evidence_count, community_signal_count,
                           official_source_count, secondary_source_count, source_spread_count,
                           readiness_score, public_candidate_ready_yn, validation_status,
                           cluster_status, last_signal_at, last_evidence_at, updated_at
                    FROM living_info.topic_cluster
                    WHERE public_candidate_ready_yn = 'Y'
                      AND validation_status IN ('VALIDATED', 'READY')
                      AND cluster_status IN ('OPEN', 'READY')
                      AND readiness_score >= 60
                      AND source_count >= 1
                      AND evidence_count >= 1
                    ORDER BY readiness_score DESC, last_evidence_at DESC NULLS LAST, updated_at DESC, id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
        return [topic_cluster_row(row) for row in rows]

    def topic_cluster_evidence(self, topic_cluster_id: int, limit: int = 10) -> list[dict[str, Any]]:
        self.require_schema_ready()
        limit = max(1, min(int(limit or 10), 50))
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        si.id AS source_item_id,
                        ni.id AS normalized_item_id,
                        si.source_url,
                        si.canonical_url,
                        si.publishable_link_url,
                        si.source_name,
                        si.source_type,
                        si.source_trust_level,
                        si.raw_title,
                        si.raw_summary,
                        si.raw_body,
                        si.published_at,
                        si.collected_at,
                        ni.normalized_primary_category,
                        ni.normalized_secondary_category,
                        ni.source_usage,
                        ni.info_signal_type,
                        ni.action_type,
                        ni.actionability_score,
                        ni.repeatability_score,
                        ni.source_reliability_score,
                        ni.normalization_confidence,
                        tci.item_role,
                        tci.weight_score
                    FROM living_info.topic_cluster_item tci
                    JOIN living_info.normalized_item ni
                      ON ni.id = tci.normalized_item_id
                    JOIN living_info.source_item si
                      ON si.id = ni.source_item_id
                    WHERE tci.topic_cluster_id = %s
                      AND tci.normalized_item_id IS NOT NULL
                    ORDER BY
                        CASE si.source_trust_level
                            WHEN 'PRIMARY' THEN 1
                            WHEN 'OFFICIAL' THEN 2
                            WHEN 'TRUSTED_MEDIA' THEN 3
                            ELSE 4
                        END,
                        tci.weight_score DESC,
                        si.collected_at DESC,
                        si.id DESC
                    LIMIT %s
                    """,
                    (int(topic_cluster_id), limit),
                )
                rows = cur.fetchall()
        return [topic_cluster_evidence_row(row) for row in rows]


def source_item_values(item: LivingSourceItem) -> tuple[Any, ...]:
    return (
        item.source_url,
        item.canonical_url,
        item.publishable_link_url,
        item.source_name,
        item.source_type,
        item.source_access_policy,
        item.language,
        item.country,
        item.region_in_korea,
        item.raw_title,
        item.raw_summary,
        item.raw_body,
        item.published_at,
        item.collected_at,
        item.last_checked_at,
        item.source_trust_level,
        item.privacy_risk_level,
        item.duplicate_key,
        item.content_hash,
        item.source_status,
        item.active_yn,
        item.raw_ref_table,
        item.raw_ref_id,
        json.dumps(item.raw_payload, ensure_ascii=False),
    )


def normalized_item_values(item: LivingNormalizedItem) -> tuple[Any, ...]:
    return (
        item.source_item_id,
        item.normalized_primary_category,
        item.normalized_secondary_category,
        item.source_usage,
        item.info_signal_type,
        item.target_user,
        item.action_type,
        item.topic_key_candidate,
        item.validation_needed_yn,
        item.validation_source_type,
        float(item.actionability_score or 0),
        float(item.repeatability_score or 0),
        float(item.source_reliability_score or 0),
        float(item.normalization_confidence or 0),
        item.normalization_reason,
        item.status,
    )


def source_signal_values(signal: LivingSourceSignal) -> tuple[Any, ...]:
    return (
        signal.signal_source_name,
        signal.signal_source_url,
        signal.signal_platform,
        signal.signal_type,
        signal.language,
        signal.country,
        signal.region_in_korea,
        signal.primary_category,
        signal.topic_key_candidate,
        signal.target_user,
        signal.pain_point_summary,
        int(signal.signal_count or 0),
        signal.privacy_risk_level,
        signal.source_access_policy,
        signal.validation_needed_yn,
        signal.status,
        signal.observed_at,
        json.dumps(signal.raw_payload, ensure_ascii=False),
    )


def topic_cluster_values(cluster: LivingTopicCluster) -> tuple[Any, ...]:
    return (
        cluster.topic_key,
        cluster.primary_category,
        cluster.secondary_category,
        cluster.target_user,
        cluster.action_type,
        int(cluster.source_count or 0),
        int(cluster.evidence_count or 0),
        int(cluster.community_signal_count or 0),
        int(cluster.official_source_count or 0),
        int(cluster.secondary_source_count or 0),
        int(cluster.source_spread_count or 0),
        float(cluster.readiness_score or 0),
        cluster.public_candidate_ready_yn,
        cluster.validation_status,
        cluster.cluster_status,
        cluster.last_signal_at,
        cluster.last_evidence_at,
    )


def source_item_row(row: tuple[Any, ...]) -> dict[str, Any]:
    keys = (
        "id",
        "source_url",
        "canonical_url",
        "publishable_link_url",
        "source_name",
        "source_type",
        "language",
        "country",
        "raw_title",
        "raw_summary",
        "source_trust_level",
        "privacy_risk_level",
        "duplicate_key",
        "content_hash",
        "source_status",
        "active_yn",
        "raw_ref_table",
        "raw_ref_id",
        "collected_at",
        "updated_at",
    )
    result = dict(zip(keys, row))
    for key in ("collected_at", "updated_at"):
        result[key] = isoformat(result.get(key))
    return result


def topic_cluster_row(row: tuple[Any, ...]) -> dict[str, Any]:
    keys = (
        "id",
        "topic_key",
        "primary_category",
        "secondary_category",
        "target_user",
        "action_type",
        "source_count",
        "evidence_count",
        "community_signal_count",
        "official_source_count",
        "secondary_source_count",
        "source_spread_count",
        "readiness_score",
        "public_candidate_ready_yn",
        "validation_status",
        "cluster_status",
        "last_signal_at",
        "last_evidence_at",
        "updated_at",
    )
    result = dict(zip(keys, row))
    for key in ("last_signal_at", "last_evidence_at", "updated_at"):
        result[key] = isoformat(result.get(key))
    for key in (
        "source_count",
        "evidence_count",
        "community_signal_count",
        "official_source_count",
        "secondary_source_count",
        "source_spread_count",
    ):
        result[key] = int(result.get(key) or 0)
    result["readiness_score"] = float(result.get("readiness_score") or 0)
    return result


def topic_cluster_evidence_row(row: tuple[Any, ...]) -> dict[str, Any]:
    keys = (
        "source_item_id",
        "normalized_item_id",
        "source_url",
        "canonical_url",
        "publishable_link_url",
        "source_name",
        "source_type",
        "source_trust_level",
        "raw_title",
        "raw_summary",
        "raw_body",
        "published_at",
        "collected_at",
        "normalized_primary_category",
        "normalized_secondary_category",
        "source_usage",
        "info_signal_type",
        "action_type",
        "actionability_score",
        "repeatability_score",
        "source_reliability_score",
        "normalization_confidence",
        "item_role",
        "weight_score",
    )
    result = dict(zip(keys, row))
    for key in ("published_at", "collected_at"):
        result[key] = isoformat(result.get(key))
    for key in (
        "actionability_score",
        "repeatability_score",
        "source_reliability_score",
        "normalization_confidence",
        "weight_score",
    ):
        result[key] = float(result.get(key) or 0)
    return result


def normalized_cluster_item_row(row: tuple[Any, ...]) -> dict[str, Any]:
    keys = (
        "normalized_item_id",
        "source_item_id",
        "normalized_primary_category",
        "normalized_secondary_category",
        "source_usage",
        "info_signal_type",
        "target_user",
        "action_type",
        "topic_key_candidate",
        "actionability_score",
        "repeatability_score",
        "source_reliability_score",
        "normalization_confidence",
        "status",
        "source_url",
        "canonical_url",
        "publishable_link_url",
        "source_name",
        "source_type",
        "source_trust_level",
        "raw_title",
        "raw_summary",
        "published_at",
        "collected_at",
    )
    result = dict(zip(keys, row))
    for key in ("published_at", "collected_at"):
        result[key] = isoformat(result.get(key))
    for key in (
        "actionability_score",
        "repeatability_score",
        "source_reliability_score",
        "normalization_confidence",
    ):
        result[key] = float(result.get(key) or 0)
    for key in ("normalized_item_id", "source_item_id"):
        result[key] = int(result.get(key) or 0)
    return result


def isoformat(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return str(value)
