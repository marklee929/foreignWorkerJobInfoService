from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any

from ..social.news.collector.article_text_extractor import fetch_article_metadata
from ..social.news.evaluator.candidate_evaluator import CandidateEvaluator
from ..social.news.models import NewsCandidate
from ..storage.db.postgres import connect, load_env_file


@dataclass
class BackfillResult:
    groups: int = 0
    representatives: int = 0
    duplicates_linked: int = 0
    content_updated: int = 0
    content_failed: int = 0
    rescored: int = 0
    ready: int = 0
    repaired_groups: int = 0


def row_to_candidate(row: dict[str, Any]) -> NewsCandidate:
    return NewsCandidate(
        id=int(row["id"]),
        title=row.get("title") or "",
        source_url=row.get("source_url") or "",
        canonical_url=row.get("canonical_url") or row.get("source_url") or "",
        google_news_url=row.get("google_news_url") or "",
        source_type=row.get("source_type") or "",
        source_name=row.get("source_name") or "",
        publisher_name=row.get("publisher_name") or row.get("source_name") or "",
        summary=row.get("summary") or "",
        content=row.get("content") or "",
        image_url=row.get("image_url") or "",
        language=row.get("language") or "en",
        category=row.get("category") or "",
        keyword=row.get("keyword") or "",
        hash_key=row.get("hash_key") or "",
        similarity_key=row.get("similarity_key") or "",
        short_summary=row.get("short_summary") or "",
        key_points=row.get("key_points") or "",
        relevance_reason=row.get("relevance_reason") or "",
        risk_notes=row.get("risk_notes") or "",
        evaluation_score=float(row.get("evaluation_score") or 0),
        duplicate_risk_score=float(row.get("duplicate_risk_score") or 0),
        selection_reason=row.get("selection_reason") or "",
        skip_reason=row.get("skip_reason") or "",
        risk_level=row.get("risk_level") or "",
        facebook_post_url=row.get("facebook_post_url") or "",
        facebook_post_id=row.get("facebook_post_id") or "",
        cycle_id=row.get("cycle_id") or "",
        publish_status=row.get("publish_status") or row.get("status") or "",
        status=row.get("status") or "",
        collected_at=str(row.get("collected_at") or ""),
        published_at=str(row.get("published_at")) if row.get("published_at") else None,
        duplicate_group_id=row.get("duplicate_group_id"),
        related_source_count=int(row.get("related_source_count") or 1),
        duplicate_count=int(row.get("duplicate_count") or 0),
        group_item_count=int(row.get("group_item_count") or 1),
        last_seen_at=str(row.get("last_seen_at") or ""),
        is_representative=bool(row.get("is_representative", True)),
    )


def fetch_groups(limit: int = 0) -> list[dict[str, Any]]:
    limit_sql = "LIMIT %s" if limit > 0 else ""
    params: tuple[Any, ...] = (limit,) if limit > 0 else ()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                WITH grouped AS (
                    SELECT
                        COALESCE(NULLIF(duplicate_group_id, 0), normalized_item_id, id) AS group_key,
                        COUNT(*)::int AS group_count,
                        COUNT(*) FILTER (WHERE publish_status = 'DUPLICATE' OR status = 'DUPLICATE')::int AS duplicate_count,
                        MAX(collected_at) AS last_seen_at
                    FROM social_news.candidate
                    WHERE COALESCE(post_expired, FALSE) = FALSE
                    GROUP BY COALESCE(NULLIF(duplicate_group_id, 0), normalized_item_id, id)
                    HAVING COUNT(*) > 1
                       OR COUNT(*) FILTER (WHERE publish_status = 'DUPLICATE' OR status = 'DUPLICATE') > 0
                )
                SELECT *
                FROM grouped
                ORDER BY duplicate_count DESC, group_count DESC, last_seen_at DESC
                {limit_sql}
                """,
                params,
            )
            columns = [column.name for column in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def fetch_group_members(group_key: int) -> list[dict[str, Any]]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, normalized_item_id, duplicate_group_id, source_type, source_url, canonical_url, google_news_url,
                       source_name, publisher_name, title, summary, content, image_url, language, category, keyword,
                       hash_key, similarity_key, short_summary, key_points, relevance_reason, risk_notes,
                       evaluation_score, duplicate_risk_score, selection_reason, skip_reason, risk_level,
                       facebook_post_url, facebook_post_id, published_at,
                       publish_cycle_id AS cycle_id, publish_status, status, collected_at,
                       related_source_count, duplicate_count, group_item_count, last_seen_at, is_representative
                FROM social_news.candidate
                WHERE COALESCE(NULLIF(duplicate_group_id, 0), normalized_item_id, id) = %s
                ORDER BY
                    CASE WHEN publish_status IN ('POSTED', 'PUBLISHED', 'NOTIFIED') OR status IN ('POSTED', 'PUBLISHED', 'NOTIFIED') THEN 0 ELSE 1 END,
                    CASE WHEN publish_status <> 'DUPLICATE' AND status <> 'DUPLICATE' THEN 0 ELSE 1 END,
                    evaluation_score DESC,
                    LENGTH(COALESCE(content, '')) DESC,
                    collected_at DESC,
                    id ASC
                """,
                (group_key,),
            )
            columns = [column.name for column in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def choose_representative(members: list[dict[str, Any]]) -> dict[str, Any]:
    def rank(row: dict[str, Any]) -> tuple[int, int, float, int, str, int]:
        status = row.get("publish_status") or row.get("status") or ""
        is_posted = status in {"POSTED", "PUBLISHED", "NOTIFIED"}
        is_not_duplicate = status != "DUPLICATE" and row.get("status") != "DUPLICATE"
        return (
            1 if is_posted else 0,
            1 if is_not_duplicate else 0,
            float(row.get("evaluation_score") or 0),
            len(row.get("content") or ""),
            str(row.get("collected_at") or ""),
            -int(row.get("id") or 0),
        )

    return sorted(members, key=rank, reverse=True)[0]


def fetch_and_update_content(candidate: NewsCandidate, timeout: int) -> tuple[NewsCandidate, str, str]:
    if len(candidate.content or "") >= 300:
        return candidate, "EXISTING", ""
    try:
        metadata = fetch_article_metadata(candidate.source_url, timeout=timeout)
    except Exception as exc:
        return candidate, "FAILED", str(exc)[:500]
    content = metadata.content.strip()
    if len(content) < 120:
        fallback = "\n\n".join(part for part in [candidate.summary, candidate.short_summary, candidate.title] if part)
        if len(fallback) < 80:
            return candidate, "FAILED", "본문 추출 결과가 너무 짧습니다."
        content = fallback
    candidate.content = content
    if metadata.canonical_url:
        candidate.canonical_url = metadata.canonical_url
    if metadata.publisher_name:
        candidate.publisher_name = metadata.publisher_name
        candidate.source_name = candidate.source_name or metadata.publisher_name
    if metadata.image_url:
        candidate.image_url = metadata.image_url
    return candidate, "FETCHED", ""


def update_group(
    group_key: int,
    representative: NewsCandidate,
    member_ids: list[int],
    evaluation: Any,
    content_status: str,
    content_error: str,
    threshold: float,
    dry_run: bool,
) -> tuple[int, bool]:
    rep_id = int(representative.id or 0)
    duplicate_ids = [member_id for member_id in member_ids if member_id != rep_id]
    group_count = len(member_ids)
    duplicate_count = max(0, group_count - 1)
    already_posted = bool(representative.facebook_post_url or representative.published_at)
    ready = evaluation.decision == "READY_TO_PUBLISH" and not already_posted
    publish_status = "POSTED" if already_posted else "READY_TO_PUBLISH" if ready else "SCORED"
    status = publish_status
    if dry_run:
        return len(duplicate_ids), ready
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE social_news.candidate
                SET is_representative = TRUE,
                    representative_candidate_id = %s,
                    duplicate_group_id = %s,
                    status = %s,
                    publish_status = %s,
                    content = %s,
                    canonical_url = COALESCE(NULLIF(%s, ''), canonical_url),
                    publisher_name = COALESCE(NULLIF(%s, ''), publisher_name),
                    image_url = COALESCE(NULLIF(%s, ''), image_url),
                    evaluation_score = %s,
                    duplicate_risk_score = %s,
                    foreign_worker_relevance_score = %s,
                    korea_relevance_score = %s,
                    visa_or_labor_policy_score = %s,
                    freshness_score = %s,
                    source_reliability_score = %s,
                    facebook_post_suitability_score = %s,
                    score_threshold = %s,
                    score_breakdown_json = %s,
                    risk_level = CASE WHEN %s >= 0.85 THEN 'HIGH' ELSE COALESCE(NULLIF(risk_level, ''), 'LOW') END,
                    selection_reason = %s,
                    skip_reason = CASE WHEN %s = 'READY_TO_PUBLISH' THEN '' ELSE %s END,
                    related_source_count = GREATEST(related_source_count, %s),
                    duplicate_count = %s,
                    group_item_count = %s,
                    content_fetch_status = %s,
                    content_fetch_error = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    rep_id,
                    rep_id,
                    status,
                    publish_status,
                    representative.content,
                    representative.canonical_url,
                    representative.publisher_name,
                    representative.image_url,
                    evaluation.total_score,
                    evaluation.duplicate_risk_score,
                    evaluation.foreign_worker_relevance_score,
                    evaluation.korea_relevance_score,
                    evaluation.visa_or_labor_policy_score,
                    evaluation.freshness_score,
                    evaluation.source_reliability_score,
                    evaluation.facebook_post_suitability_score,
                    threshold,
                    evaluation.score_breakdown_json,
                    evaluation.duplicate_risk_score,
                    evaluation.reason,
                    publish_status,
                    evaluation.reason,
                    group_count,
                    duplicate_count,
                    group_count,
                    content_status,
                    content_error,
                    rep_id,
                ),
            )
            if duplicate_ids:
                cur.execute(
                    """
                    UPDATE social_news.candidate
                    SET is_representative = FALSE,
                        representative_candidate_id = %s,
                        duplicate_group_id = %s,
                        status = 'DUPLICATE',
                        publish_status = 'DUPLICATE',
                        evaluation_score = %s,
                        score_threshold = %s,
                        selection_reason = %s,
                        skip_reason = '대표 후보로 그룹화됨',
                        group_item_count = %s,
                        duplicate_count = %s,
                        related_source_count = GREATEST(related_source_count, %s),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ANY(%s)
                    """,
                    (
                        rep_id,
                        rep_id,
                        evaluation.total_score,
                        threshold,
                        f"대표 후보 {rep_id} 점수를 그룹 점수로 사용합니다.",
                        group_count,
                        duplicate_count,
                        group_count,
                        duplicate_ids,
                    ),
                )
            normalized_id = None
            cur.execute("SELECT normalized_item_id FROM social_news.candidate WHERE id = %s", (rep_id,))
            row = cur.fetchone()
            if row:
                normalized_id = row[0]
            if normalized_id:
                cur.execute(
                    """
                    UPDATE social_news.normalized_item
                    SET content = %s,
                        canonical_url = COALESCE(NULLIF(%s, ''), canonical_url),
                        publisher_name = COALESCE(NULLIF(%s, ''), publisher_name),
                        content_fetch_status = %s,
                        content_fetch_error = %s,
                        normalized_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (representative.content, representative.canonical_url, representative.publisher_name, content_status, content_error, normalized_id),
                )
                cur.execute(
                    """
                    UPDATE social_news.raw_item
                    SET raw_content = COALESCE(NULLIF(%s, ''), raw_content),
                        content_fetch_status = %s,
                        content_fetch_error = %s
                    WHERE normalized_item_id = %s
                    """,
                    (representative.content, content_status, content_error, normalized_id),
                )
        conn.commit()
    return len(duplicate_ids), ready


def repair_representative_flags(threshold: float, dry_run: bool = False) -> int:
    """Ensure every duplicate/topic group has exactly one non-DUPLICATE representative."""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                WITH grouped AS (
                    SELECT
                        COALESCE(NULLIF(duplicate_group_id, 0), normalized_item_id, id) AS group_key,
                        COUNT(*)::int AS group_count
                    FROM social_news.candidate
                    WHERE COALESCE(post_expired, FALSE) = FALSE
                    GROUP BY COALESCE(NULLIF(duplicate_group_id, 0), normalized_item_id, id)
                    HAVING COUNT(*) > 1
                       OR COUNT(*) FILTER (
                           WHERE COALESCE(is_representative, FALSE) = TRUE
                             AND (status = 'DUPLICATE' OR publish_status = 'DUPLICATE')
                       ) > 0
                ),
                ranked AS (
                    SELECT
                        c.id,
                        g.group_key,
                        g.group_count,
                        ROW_NUMBER() OVER (
                            PARTITION BY g.group_key
                            ORDER BY
                                CASE
                                    WHEN c.publish_status IN ('POSTED', 'PUBLISHED', 'NOTIFIED')
                                      OR c.status IN ('POSTED', 'PUBLISHED', 'NOTIFIED') THEN 0
                                    ELSE 1
                                END,
                                CASE
                                    WHEN c.publish_status <> 'DUPLICATE'
                                     AND c.status <> 'DUPLICATE' THEN 0
                                    ELSE 1
                                END,
                                COALESCE(c.evaluation_score, 0) DESC,
                                LENGTH(COALESCE(c.content, '')) DESC,
                                c.collected_at DESC NULLS LAST,
                                c.id ASC
                        ) AS rn
                    FROM social_news.candidate c
                    JOIN grouped g
                      ON COALESCE(NULLIF(c.duplicate_group_id, 0), c.normalized_item_id, c.id) = g.group_key
                )
                SELECT COUNT(*)::int
                FROM ranked
                WHERE rn = 1
                """
            )
            repaired = int(cur.fetchone()[0] or 0)
            if dry_run:
                return repaired
            cur.execute(
                """
                WITH grouped AS (
                    SELECT
                        COALESCE(NULLIF(duplicate_group_id, 0), normalized_item_id, id) AS group_key,
                        COUNT(*)::int AS group_count
                    FROM social_news.candidate
                    WHERE COALESCE(post_expired, FALSE) = FALSE
                    GROUP BY COALESCE(NULLIF(duplicate_group_id, 0), normalized_item_id, id)
                    HAVING COUNT(*) > 1
                       OR COUNT(*) FILTER (
                           WHERE COALESCE(is_representative, FALSE) = TRUE
                             AND (status = 'DUPLICATE' OR publish_status = 'DUPLICATE')
                       ) > 0
                ),
                ranked AS (
                    SELECT
                        c.id,
                        g.group_key,
                        g.group_count,
                        ROW_NUMBER() OVER (
                            PARTITION BY g.group_key
                            ORDER BY
                                CASE
                                    WHEN c.publish_status IN ('POSTED', 'PUBLISHED', 'NOTIFIED')
                                      OR c.status IN ('POSTED', 'PUBLISHED', 'NOTIFIED') THEN 0
                                    ELSE 1
                                END,
                                CASE
                                    WHEN c.publish_status <> 'DUPLICATE'
                                     AND c.status <> 'DUPLICATE' THEN 0
                                    ELSE 1
                                END,
                                COALESCE(c.evaluation_score, 0) DESC,
                                LENGTH(COALESCE(c.content, '')) DESC,
                                c.collected_at DESC NULLS LAST,
                                c.id ASC
                        ) AS rn
                    FROM social_news.candidate c
                    JOIN grouped g
                      ON COALESCE(NULLIF(c.duplicate_group_id, 0), c.normalized_item_id, c.id) = g.group_key
                ),
                reps AS (
                    SELECT id AS representative_id, group_key, group_count
                    FROM ranked
                    WHERE rn = 1
                ),
                member_reps AS (
                    SELECT r.id, reps.representative_id, reps.group_count
                    FROM ranked r
                    JOIN reps ON reps.group_key = r.group_key
                )
                UPDATE social_news.candidate c
                SET is_representative = (c.id = member_reps.representative_id),
                    representative_candidate_id = member_reps.representative_id,
                    duplicate_group_id = member_reps.representative_id,
                    status = CASE
                        WHEN c.id = member_reps.representative_id
                         AND (NULLIF(c.facebook_post_url, '') IS NOT NULL OR c.published_at IS NOT NULL)
                            THEN 'POSTED'
                        WHEN c.id = member_reps.representative_id
                         AND COALESCE(c.evaluation_score, 0) >= %s
                            THEN 'READY_TO_PUBLISH'
                        WHEN c.id = member_reps.representative_id
                            THEN 'SCORED'
                        ELSE 'DUPLICATE'
                    END,
                    publish_status = CASE
                        WHEN c.id = member_reps.representative_id
                         AND (NULLIF(c.facebook_post_url, '') IS NOT NULL OR c.published_at IS NOT NULL)
                            THEN 'POSTED'
                        WHEN c.id = member_reps.representative_id
                         AND COALESCE(c.evaluation_score, 0) >= %s
                            THEN 'READY_TO_PUBLISH'
                        WHEN c.id = member_reps.representative_id
                            THEN 'SCORED'
                        ELSE 'DUPLICATE'
                    END,
                    group_item_count = member_reps.group_count,
                    duplicate_count = GREATEST(member_reps.group_count - 1, 0),
                    related_source_count = GREATEST(COALESCE(c.related_source_count, 1), member_reps.group_count),
                    skip_reason = CASE
                        WHEN c.id = member_reps.representative_id THEN COALESCE(NULLIF(c.skip_reason, ''), '')
                        ELSE '대표 후보로 그룹화됨'
                    END,
                    updated_at = CURRENT_TIMESTAMP
                FROM member_reps
                WHERE c.id = member_reps.id
                """,
                (threshold, threshold),
            )
        conn.commit()
    return repaired


def backfill(limit: int = 0, timeout: int = 10, threshold: float = 40.0, dry_run: bool = False) -> BackfillResult:
    load_env_file()
    evaluator = CandidateEvaluator(min_safety_score=0.0)
    result = BackfillResult()
    groups = fetch_groups(limit=limit)
    result.groups = len(groups)
    for group in groups:
        group_key = int(group["group_key"])
        members = fetch_group_members(group_key)
        if not members:
            continue
        rep_row = choose_representative(members)
        representative = row_to_candidate(rep_row)
        representative, content_status, content_error = fetch_and_update_content(representative, timeout=timeout)
        if content_status == "FAILED":
            result.content_failed += 1
        elif content_status == "FETCHED":
            result.content_updated += 1
        representative.duplicate_risk_score = 0.0
        evaluation = evaluator.evaluate(representative, threshold=threshold)
        result.rescored += 1
        duplicate_count, ready = update_group(
            group_key=group_key,
            representative=representative,
            member_ids=[int(member["id"]) for member in members],
            evaluation=evaluation,
            content_status=content_status,
            content_error=content_error,
            threshold=threshold,
            dry_run=dry_run,
        )
        result.representatives += 1
        result.duplicates_linked += duplicate_count
        if ready:
            result.ready += 1
        message = (
            f"group={group_key} rep={representative.id} score={evaluation.total_score:.2f} "
            f"status={'READY_TO_PUBLISH' if ready else 'SCORED'} duplicates={duplicate_count} content={content_status} title={representative.title[:80]}"
        )
        print(message.encode("cp949", errors="replace").decode("cp949"))
    result.repaired_groups = repair_representative_flags(threshold=threshold, dry_run=dry_run)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backfill duplicate groups so every group has one scored representative candidate.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum duplicate groups to process. 0 means all.")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--threshold", type=float, default=40.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = backfill(limit=args.limit, timeout=args.timeout, threshold=args.threshold, dry_run=args.dry_run)
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
