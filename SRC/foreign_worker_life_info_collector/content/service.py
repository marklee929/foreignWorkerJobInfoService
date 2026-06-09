"""Service layer for the unified content publishing hub."""

from __future__ import annotations

import os
from typing import Any

from ..social.facebook.page_client import FacebookPageClient
from ..social.news.publisher.facebook_publisher import (
    facebook_message_reject_reason,
    mask_token,
    sharing_debugger_url,
    token_fingerprint,
    validate_facebook_article_link,
)
from ..utils.text_normalizer import normalize_plain_text
from .repository import ContentRepository


class ContentService:
    def __init__(self, repository: ContentRepository | None = None) -> None:
        self.repository = repository or ContentRepository()

    def sync_all(self, limit: int = 200) -> dict[str, Any]:
        news = self.sync_social_news(limit=limit)
        immigration = self.sync_immigration(limit=limit)
        return {
            "ok": True,
            "social_news": news,
            "immigration": immigration,
            "synced_total": news["synced_count"] + immigration["synced_count"],
        }

    def sync_social_news(self, limit: int = 200) -> dict[str, Any]:
        from ..storage.db.postgres import connect

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, title, generated_title, short_summary, summary, generated_summary_en,
                           generated_why_it_matters_en, relevance_reason, content, source_url,
                           canonical_url, google_news_url, publisher_name, source_name, image_url,
                           category, content_category, content_priority_group, practical_value_score,
                           content_potential_score, category_rotation_score, category_selection_reason,
                           is_sensitive, review_required_reason, language, evaluation_score, korea_relevance_score,
                           foreign_worker_relevance_score, facebook_post_suitability_score,
                           freshness_score, source_reliability_score, risk_level, publish_status,
                           status, collected_at, published_at, facebook_post_id, facebook_post_url,
                           duplicate_group_id, representative_candidate_id, is_representative
                    FROM social_news.candidate
                    WHERE COALESCE(is_representative, TRUE) = TRUE
                      AND COALESCE(publish_status, status, '') NOT IN ('ARCHIVED', 'DUPLICATE_SKIPPED', 'DUPLICATE', 'SKIPPED', 'TEXT_INVALID')
                    ORDER BY updated_at DESC NULLS LAST, collected_at DESC NULLS LAST, id DESC
                    LIMIT %s
                    """,
                    (max(1, min(int(limit), 1000)),),
                )
                rows = cur.fetchall()

        synced = 0
        for row in rows:
            payload = social_news_payload(row)
            if payload["title"]:
                self.repository.upsert_candidate(payload)
                synced += 1
        archived = self.repository.archive_non_representative_social_news()
        return {"source": "social_news.candidate", "seen_count": len(rows), "synced_count": synced, "archived_duplicate_count": archived}

    def sync_immigration(self, limit: int = 200) -> dict[str, Any]:
        from ..storage.db.postgres import connect

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, source_name, source_type, notice_type, title_ko, title_en,
                           original_url, canonical_url, raw_content_ko, raw_content_en,
                           summary_en, why_it_matters_en, affected_visa_types, affected_user_groups,
                           policy_keywords, importance_score, urgency_level, content_status,
                           collected_at, published_at, raw_response
                    FROM immigration_info.official_notice
                    WHERE active_yn = 'Y'
                    ORDER BY importance_score DESC, collected_at DESC, id DESC
                    LIMIT %s
                    """,
                    (max(1, min(int(limit), 1000)),),
                )
                rows = cur.fetchall()

        synced = 0
        for row in rows:
            payload = immigration_payload(row)
            if payload["title"]:
                self.repository.upsert_candidate(payload)
                synced += 1
        return {"source": "immigration_info.official_notice", "seen_count": len(rows), "synced_count": synced}

    def publish(self, candidate_id: int, dry_run: bool = True) -> dict[str, Any]:
        candidate = self.repository.get_candidate(candidate_id)
        if not candidate:
            return {"ok": False, "status": "NOT_FOUND", "message": "content candidate not found"}
        message = build_facebook_message(candidate)
        link_url = (candidate.get("link_url") or candidate.get("source_url") or "").strip()
        request_payload = {
            "message": message,
            "link": link_url,
            "source": "content.content_candidate",
            "content_candidate_id": candidate_id,
            "facebook_debugger_url": sharing_debugger_url(link_url),
        }
        link_valid, link_reject_reason = validate_facebook_article_link(link_url)
        message_reject_reason = facebook_message_reject_reason(message)
        if message_reject_reason or not link_valid:
            error_code = "FACEBOOK_MESSAGE_INVALID" if message_reject_reason else "FACEBOOK_LINK_INVALID"
            error_message = message_reject_reason or f"Facebook link card URL is invalid: {link_reject_reason}"
            result = {
                "ok": False,
                "status": "FAILED_RETRYABLE",
                "message": message,
                "link_url": link_url,
                "facebook_post_id": "",
                "facebook_post_url": "",
                "request_payload": {
                    **request_payload,
                    "link_valid_yn": link_valid,
                    "link_reject_reason": link_reject_reason,
                },
                "error_code": error_code,
                "error_message": error_message,
            }
            update = self.repository.update_publish_result(candidate_id, result, dry_run=False)
            return {**update, **result}
        real_publish_enabled = os.getenv("CONTENT_AUTO_PUBLISH", "").strip().lower() == "true"
        test_mode = os.getenv("CONTENT_PUBLISH_TEST_MODE", "true").strip().lower() != "false"
        dry_run = bool(dry_run or not real_publish_enabled or test_mode)
        if dry_run:
            result = {
                "ok": True,
                "status": "DRY_RUN",
                "message": message,
                "link_url": link_url,
                "facebook_post_id": f"dry-run-content-{candidate_id}",
                "facebook_post_url": f"https://www.facebook.com/dry-run-content-{candidate_id}",
                "request_payload": request_payload,
                "error_code": "",
                "error_message": "",
            }
            update = self.repository.update_publish_result(candidate_id, result, dry_run=True)
            return {**update, **result}

        page_id = os.getenv("FACEBOOK_PAGE_ID", "").strip()
        access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
        if not page_id or not access_token:
            result = {
                "ok": False,
                "status": "FAILED_RETRYABLE",
                "message": message,
                "link_url": link_url,
                "request_payload": {
                    **request_payload,
                    "page_id": page_id,
                    "token_masked": mask_token(access_token),
                    "token_fingerprint": token_fingerprint(access_token),
                },
                "error_code": "MISSING_FACEBOOK_ENV",
                "error_message": "FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN are required.",
            }
            update = self.repository.update_publish_result(candidate_id, result, dry_run=False)
            return {**update, **result}

        response = FacebookPageClient().publish(message=message, link=link_url, page_id=page_id, access_token=access_token)
        result = {
            "ok": response.get("status") == "OK",
            "status": response.get("status", "FAILED_RETRYABLE"),
            "message": message,
            "link_url": link_url,
            "facebook_post_id": response.get("facebook_post_id", ""),
            "facebook_post_url": response.get("facebook_post_url", ""),
            "request_payload": request_payload,
            "error_code": response.get("error_code", ""),
            "error_message": response.get("error_message", ""),
            "response_payload": response,
        }
        update = self.repository.update_publish_result(candidate_id, result, dry_run=False)
        return {**update, **result}


def social_news_payload(row: tuple[Any, ...]) -> dict[str, Any]:
    (
        row_id, title, generated_title, short_summary, summary, generated_summary_en,
        generated_why_it_matters_en, relevance_reason, content, source_url, canonical_url,
        google_news_url, publisher_name, source_name, image_url, category, content_category,
        content_priority_group, practical_value_score, content_potential_score, category_rotation_score,
        category_selection_reason, is_sensitive, review_required_reason, language,
        evaluation_score, korea_relevance_score, foreign_worker_relevance_score,
        facebook_post_suitability_score, freshness_score, source_reliability_score,
        risk_level, publish_status, status, collected_at, published_at,
        facebook_post_id, facebook_post_url, duplicate_group_id, representative_candidate_id, is_representative,
    ) = row
    score = float(evaluation_score or 0)
    review_required = bool(is_sensitive) or str(risk_level or "").upper() == "HIGH"
    publish_state = str(publish_status or status or "")
    if publish_state in {"DUPLICATE", "DUPLICATE_SKIPPED", "SKIPPED", "TEXT_INVALID", "ARCHIVED"}:
        content_status = "ARCHIVED"
    elif published_at or publish_state in {"POSTED", "PUBLISHED", "NOTIFIED", "DRY_RUN_PUBLISHED", "DRY_RUN_NOTIFIED"}:
        content_status = "POSTED"
    elif score >= 40 and not review_required:
        content_status = "READY_TO_PUBLISH"
    elif score >= 40:
        content_status = "READY_TO_REVIEW"
    else:
        content_status = "SCORED"
    link = source_url or canonical_url or ""
    return {
        "source_domain": "SOCIAL_NEWS",
        "content_type": "NEWS_ARTICLE",
        "priority_group": content_priority_group or "PRIMARY",
        "category": content_category or category or "foreign_jobs",
        "title": clean(generated_title or title),
        "summary_en": clean(generated_summary_en or short_summary or summary),
        "why_it_matters_en": clean(generated_why_it_matters_en or relevance_reason),
        "body_en": clean(content),
        "source_url": clean(source_url or canonical_url or ""),
        "source_name": clean(publisher_name or source_name or ""),
        "original_source_url": clean(source_url or canonical_url or ""),
        "original_source_name": clean(publisher_name or source_name or ""),
        "original_title": clean(title),
        "original_published_at": "",
        "original_collected_at": collected_at.isoformat() if collected_at else "",
        "image_url": clean(image_url),
        "link_url": clean(link),
        "hashtags": "#KoreaJobs #WorkInKorea #ForeignWorkers #VisaInfo",
        "language": language or "en",
        "quality_score": score,
        "relevance_score": float(korea_relevance_score or foreign_worker_relevance_score or 0),
        "practical_value_score": float(practical_value_score or facebook_post_suitability_score or 0),
        "urgency_score": 0,
        "freshness_score": float(freshness_score or 0),
        "source_reliability_score": float(source_reliability_score or 0),
        "content_potential_score": float(content_potential_score or score),
        "rotation_score": float(category_rotation_score or 0),
        "final_publish_score": score,
        "sensitive_yn": review_required,
        "review_required_yn": review_required,
        "review_reason": clean(review_required_reason or category_selection_reason or ("sensitive/high-risk news article" if review_required else "")),
        "status": content_status,
        "published_at": published_at.isoformat() if published_at else "",
        "facebook_post_id": clean(facebook_post_id),
        "facebook_post_url": clean(facebook_post_url),
        "raw_ref_table": "social_news.candidate",
        "raw_ref_id": row_id,
        "raw_payload": {
            "publish_status": publish_status,
            "status": status,
            "google_news_url": google_news_url,
            "duplicate_group_id": duplicate_group_id,
            "representative_candidate_id": representative_candidate_id,
            "is_representative": bool(is_representative),
            "collected_at": collected_at.isoformat() if collected_at else "",
            "published_at": published_at.isoformat() if published_at else "",
        },
    }


def immigration_payload(row: tuple[Any, ...]) -> dict[str, Any]:
    (
        row_id, source_name, source_type, notice_type, title_ko, title_en, original_url,
        canonical_url, raw_content_ko, raw_content_en, summary_en, why_it_matters_en,
        affected_visa_types, affected_user_groups, policy_keywords, importance_score,
        urgency_level, content_status, collected_at, published_at, raw_response,
    ) = row
    score = float(importance_score or 0)
    urgency = {"HIGH": 90, "MEDIUM": 60, "LOW": 30}.get(str(urgency_level or "").upper(), 30)
    if published_at or str(content_status or "") == "POSTED":
        status = "POSTED"
    elif score >= 70:
        status = "READY_TO_PUBLISH"
    elif score >= 50:
        status = "READY_TO_REVIEW"
    else:
        status = "SCORED"
    tags = list(policy_keywords or [])[:4]
    hashtags = " ".join(["#WorkInKorea", "#KoreaVisa", "#ForeignWorkers"] + [f"#{tag}" for tag in tags if str(tag).isascii()])
    return {
        "source_domain": "IMMIGRATION_INFO",
        "content_type": "GOVERNMENT_NOTICE" if source_type == "government" else "IMMIGRATION_NOTICE",
        "priority_group": "OFFICIAL_NOTICE",
        "category": notice_type or "immigration",
        "title": clean(title_en or title_ko),
        "summary_en": clean(summary_en or raw_content_en or raw_content_ko),
        "why_it_matters_en": clean(why_it_matters_en),
        "body_en": clean(raw_content_en or summary_en or raw_content_ko),
        "source_url": clean(canonical_url or original_url),
        "source_name": clean(source_name),
        "original_source_url": clean(canonical_url or original_url),
        "original_source_name": clean(source_name),
        "original_title": clean(title_ko or title_en),
        "original_published_at": "",
        "original_collected_at": collected_at.isoformat() if collected_at else "",
        "image_url": "",
        "link_url": clean(canonical_url or original_url),
        "hashtags": hashtags.strip(),
        "language": "en" if title_en or summary_en else "ko",
        "quality_score": score,
        "relevance_score": score,
        "practical_value_score": score,
        "urgency_score": urgency,
        "freshness_score": 80,
        "source_reliability_score": 100,
        "content_potential_score": max(score, urgency),
        "rotation_score": 0,
        "final_publish_score": round((score * 0.55) + (urgency * 0.2) + 25, 2),
        "sensitive_yn": False,
        "review_required_yn": not bool(summary_en),
        "review_reason": "" if summary_en else "English summary is not ready",
        "status": status,
        "published_at": published_at.isoformat() if published_at else "",
        "facebook_post_id": "",
        "facebook_post_url": "",
        "raw_ref_table": "immigration_info.official_notice",
        "raw_ref_id": row_id,
        "raw_payload": {
            "source_type": source_type,
            "affected_visa_types": affected_visa_types or [],
            "affected_user_groups": affected_user_groups or [],
            "content_status": content_status,
            "collected_at": collected_at.isoformat() if collected_at else "",
            "published_at": published_at.isoformat() if published_at else "",
            "raw_response": raw_response or {},
        },
    }


def build_facebook_message(candidate: dict[str, Any]) -> str:
    title = clean(candidate.get("title", ""))[:180]
    summary = bullet_lines(candidate.get("summary_en", ""), limit=5)
    why = bullet_lines(candidate.get("why_it_matters_en", ""), limit=4)
    parts = [title]
    if summary:
        parts.append("Summary:\n" + "\n".join(summary))
    if why:
        parts.append("Why it matters for foreign workers in Korea:\n" + "\n".join(why))
    parts.append("Read more below.")
    hashtags = clean(candidate.get("hashtags", "")) or "#KoreaJobs #WorkInKorea #ForeignWorkers"
    parts.append(hashtags)
    return "\n\n".join(part for part in parts if part.strip())


def bullet_lines(value: str, limit: int) -> list[str]:
    lines: list[str] = []
    for line in clean(value).splitlines():
        line = line.strip().lstrip("-").strip()
        if line:
            lines.append(f"- {line[:240]}")
    if not lines and value:
        cleaned = clean(value)
        if cleaned:
            lines.append(f"- {cleaned[:240]}")
    return lines[:limit]


def clean(value: Any) -> str:
    return normalize_plain_text(str(value or "")).strip()
