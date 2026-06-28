"""Service layer for the unified content publishing hub."""

from __future__ import annotations

import os
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..social.facebook.page_client import FacebookPageClient
from ..social.facebook.token_manager import get_facebook_page_token
from ..social.news.publisher.facebook_publisher import (
    facebook_message_reject_reason,
    mask_token,
    sharing_debugger_url,
    token_fingerprint,
    validate_facebook_article_link,
)
from ..utils.text_normalizer import normalize_plain_text
from .repository import ContentRepository


TELEGRAM_REVIEW_SOURCE_DOMAINS = {"LIVING_INFO", "IMMIGRATION_INFO"}
TARGET_COUNTRY = "Korea"
TARGET_COUNTRY_TERMS = (
    "korea",
    "south korea",
    "korean",
    "seoul",
    "busan",
    "incheon",
    "daegu",
    "daejeon",
    "gwangju",
    "ulsan",
    "jeju",
    "gyeonggi",
    "hi korea",
    "hikorea",
    "moel",
    "ministry of employment and labor",
    "ministry of justice",
)
OTHER_COUNTRY_REFERENCE_TERMS = (
    "japan",
    "japanese",
    "united states",
    "u.s.",
    "usa",
    "america",
    "american",
    "bali",
    "indonesia",
    "australia",
    "canada",
    "singapore",
    "taiwan",
    "thailand",
    "vietnam",
)
USER_NEED_TERMS = (
    "foreigner",
    "foreign worker",
    "foreign workers",
    "foreign resident",
    "foreign residents",
    "migrant",
    "immigrant",
    "visa",
    "immigration",
    "work permit",
    "labor",
    "employment",
    "worker rights",
    "housing",
    "rent",
    "bank account",
    "remittance",
    "health insurance",
    "national pension",
    "telecom",
    "support center",
    "resident registration",
    "alien registration",
    "application",
    "eligibility",
)
ACTIONABILITY_TERMS = (
    "apply",
    "application",
    "register",
    "registration",
    "deadline",
    "eligible",
    "eligibility",
    "required",
    "requirement",
    "check",
    "guide",
    "manual",
    "lookup",
    "address",
    "location",
    "contact",
    "phone",
    "fee",
    "payment",
    "insurance",
    "benefit",
    "support",
    "subsidy",
    "permit",
    "renewal",
)
GENERIC_TRAVEL_TERMS = (
    "travel",
    "tourism",
    "tourist",
    "destination",
    "airline",
    "airport",
    "hotel",
    "resort",
    "trip",
    "vacation",
    "travel warning",
    "travel confidence",
)
GENERIC_CRYPTO_TERMS = (
    "crypto",
    "cryptocurrency",
    "bitcoin",
    "ethereum",
    "blockchain",
    "token",
    "exchange",
    "defi",
)
ESSENTIAL_FINANCE_TERMS = (
    "bank account",
    "remittance",
    "tax",
    "national pension",
    "health insurance payment",
    "wage payment",
    "salary payment",
    "foreign worker bank",
    "foreigner bank",
)
DOMESTIC_POLITICS_TERMS = (
    "election",
    "local election",
    "president",
    "presidential",
    "party",
    "parliament",
    "assembly",
    "approval rating",
    "governance",
    "campaign trail",
)
GENERIC_ECONOMY_TERMS = (
    "stock market",
    "kospi",
    "kosdaq",
    "shares",
    "market closing",
    "bond market",
    "interest rate",
    "gdp",
    "inflation",
    "exports",
)
LOW_USER_NEED_NOTICE_TERMS = (
    "award ceremony",
    "ceremony",
    "mou",
    "memorandum of understanding",
    "partnership",
    "campaign",
    "meeting held",
    "conference held",
    "public contest",
    "contest awards",
    "inspection meeting",
)
SYSTEM_MESSAGE_TERMS = (
    "저장된 기사 본문이 없습니다",
    "일부 rss",
    "검색 결과는 원문 html 접근이 제한",
    "no article body was saved",
    "content unavailable",
    "failed to fetch article",
    "parser error",
    "access denied",
    "관리자 재게시 요청",
    "게시 기준",
    "현재 점수",
    "ready_to_publish",
    "content candidate",
    "candidate_id",
    "candidate id",
    "queue",
    "threshold",
    "publish_status",
)
ATTACHMENT_REVIEW_STATE = "ATTACHMENT_REVIEW_REQUIRED"
ATTACHMENT_EVIDENCE_ONLY_STATE = "EVIDENCE_ONLY"
DOCUMENT_EXTRACTION_REQUIRED_STATE = "DOCUMENT_EXTRACTION_REQUIRED"
ATTACHMENT_ONLY_TERMS = (
    "attachment exists",
    "attached file",
    "attached files",
    "attachment only",
    "zip attachment",
    "downloadallzip.do",
    "첨부파일",
    "첨부 파일",
    "泥⑤",
)
ATTACHMENT_FILE_TERMS = (
    ".zip",
    ".pdf",
    ".hwp",
    ".hwpx",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    "downloadallzip.do",
)


@dataclass(frozen=True)
class ContentGateDecision:
    code: str
    reason: str
    review_eligible: bool
    publish_eligible: bool
    hard_block: bool = False
    watch_topic: str = ""
    global_reference_only: bool = False

    def as_payload(self) -> dict[str, Any]:
        return {
            "target_country": TARGET_COUNTRY,
            "content_quality_gate_code": self.code,
            "content_quality_gate_reason": self.reason,
            "review_eligible_yn": self.review_eligible,
            "auto_publish_eligible_yn": self.publish_eligible,
            "hard_block_yn": self.hard_block,
            "watch_topic": self.watch_topic,
            "global_reference_only_yn": self.global_reference_only,
        }


class ContentService:
    def __init__(self, repository: ContentRepository | None = None, living_info_service: Any | None = None) -> None:
        self.repository = repository or ContentRepository()
        self.living_info_service = living_info_service

    def sync_all(self, limit: int = 200) -> dict[str, Any]:
        news = self.sync_social_news(limit=limit)
        immigration = self.sync_immigration(limit=limit)
        return {
            "ok": True,
            "social_news": news,
            "immigration": immigration,
            "synced_total": news["synced_count"] + immigration["synced_count"],
        }

    def sync_living_info(self, limit: int = 100) -> dict[str, Any]:
        living_info_service = self._living_info_service()
        clusters = living_info_service.list_ready_topic_clusters(limit=max(1, min(int(limit), 500)))
        synced = 0
        skipped = 0
        skipped_reasons: dict[str, int] = {}
        for cluster in clusters:
            evidence = living_info_service.topic_cluster_evidence(int(cluster.get("id") or 0))
            payload = living_info_service.topic_cluster_to_content_candidate_payload(cluster, evidence)
            if not payload.get("ready"):
                skipped += 1
                reason = str(payload.get("skip_reason") or "unknown")
                skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
                continue
            content_payload = {key: value for key, value in payload.items() if key != "ready"}
            self.repository.upsert_candidate(content_payload)
            synced += 1
        return {
            "source": "living_info.topic_cluster",
            "seen_count": len(clusters),
            "synced_count": synced,
            "skipped_count": skipped,
            "skipped_reasons": skipped_reasons,
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

        return self._sync_social_news_rows(rows)

    def _living_info_service(self) -> Any:
        if self.living_info_service is None:
            from ..living_info.service import LivingInfoService

            self.living_info_service = LivingInfoService()
        return self.living_info_service

    def _sync_social_news_rows(self, rows: list[tuple[Any, ...]]) -> dict[str, Any]:
        content_candidate_synced = 0
        living_info_ingested = 0
        living_info_skipped = 0
        skipped_no_title = 0
        for row in rows:
            payload = social_news_payload(row)
            if not payload["title"]:
                skipped_no_title += 1
                continue
            if payload.get("source_domain") == "LIVING_INFO":
                result = self._living_info_service().ingest_from_social_news_candidate(payload)
                if result.get("ok"):
                    living_info_ingested += 1
                else:
                    living_info_skipped += 1
                continue
            self.repository.upsert_candidate(payload)
            content_candidate_synced += 1
        archived = self.repository.archive_non_representative_social_news()
        return {
            "source": "social_news.candidate",
            "seen_count": len(rows),
            "synced_count": content_candidate_synced + living_info_ingested,
            "content_candidate_synced_count": content_candidate_synced,
            "living_info_ingested_count": living_info_ingested,
            "living_info_skipped_count": living_info_skipped,
            "skipped_no_title_count": skipped_no_title,
            "archived_duplicate_count": archived,
        }

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

    def publish_next(self, dry_run: bool = False) -> dict[str, Any]:
        if not dry_run:
            cooldown = self.publish_cooldown_info()
            if cooldown["active"]:
                return {
                    "ok": True,
                    "status": "WAITING_COOLDOWN",
                    "message": f"Content publish cooldown active until {cooldown['next_publish_at']}",
                    "cooldown": cooldown,
                }
        candidates = self.repository.list_candidates({"publishable": "1", "page": 1, "size": 20}).get("items", [])
        eligible_candidate: dict[str, Any] = {}
        for item in candidates:
            detail = self.repository.get_candidate(int(item["id"])) or item
            if content_quality_gate(detail).publish_eligible:
                eligible_candidate = detail
                break
        if not eligible_candidate:
            return {"ok": True, "status": "SKIPPED", "message": "No publishable content candidates."}
        candidate_id = int(eligible_candidate["id"])
        result = self.publish(candidate_id, dry_run=dry_run)
        return {"ok": result.get("ok", False), "candidate_id": candidate_id, **result}

    def publish_cooldown_info(self) -> dict[str, Any]:
        cooldown_minutes = max(0, int(os.getenv("NEWS_PUBLISH_COOLDOWN_MINUTES", "30") or "30"))
        last = self.repository.last_successful_publish_at()
        if not last or cooldown_minutes <= 0:
            return {"active": False, "cooldown_minutes": cooldown_minutes, "last_post_at": "", "next_publish_at": "", "remaining_seconds": 0}
        last_at = last if getattr(last, "tzinfo", None) else last.replace(tzinfo=timezone.utc)
        next_at = last_at + timedelta(minutes=cooldown_minutes)
        remaining = max(0, int((next_at - datetime.now(timezone.utc)).total_seconds()))
        return {
            "active": remaining > 0,
            "cooldown_minutes": cooldown_minutes,
            "last_post_at": last_at.isoformat(),
            "next_publish_at": next_at.isoformat(),
            "remaining_seconds": remaining,
        }

    def publish(self, candidate_id: int, dry_run: bool = True) -> dict[str, Any]:
        candidate = self.repository.get_candidate(candidate_id)
        if not candidate:
            return {"ok": False, "status": "NOT_FOUND", "message": "content candidate not found"}
        gate = content_quality_gate(candidate)
        if not gate.publish_eligible:
            self.repository.mark_candidate_quality_blocked(candidate_id, gate.as_payload())
            return {
                "ok": True,
                "status": "SKIPPED",
                "message": gate.reason,
                "error_code": gate.code,
                "content_quality_gate": gate.as_payload(),
            }
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
            return {**result, "facebook_status": result.get("status", ""), **update}
        real_publish_enabled = (
            os.getenv("CONTENT_FACEBOOK_PUBLISH_ENABLED", "").strip().lower() == "true"
            and os.getenv("CONTENT_AUTO_PUBLISH", "").strip().lower() == "true"
        )
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
            return {**result, "facebook_status": result.get("status", ""), **update}

        token_selection = get_facebook_page_token(allow_refresh=True)
        page_id = token_selection.page_id or os.getenv("FACEBOOK_PAGE_ID", "").strip()
        access_token = token_selection.access_token
        request_payload.update(
            {
                "page_id": page_id,
                "token_source": token_selection.source,
                "token_config_path": token_selection.config_path,
                "token_fingerprint": token_fingerprint(access_token),
            }
        )
        if not page_id or not access_token:
            result = {
                "ok": False,
                "status": "FAILED_RETRYABLE",
                "message": message,
                "link_url": link_url,
                "request_payload": {
                    **request_payload,
                    "token_masked": mask_token(access_token),
                },
                "error_code": "MISSING_FACEBOOK_ENV",
                "error_message": "FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN are required.",
            }
            update = self.repository.update_publish_result(candidate_id, result, dry_run=False)
            return {**result, "facebook_status": result.get("status", ""), **update}

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
        return {**result, "facebook_status": result.get("status", ""), **update}

    def review_targets(self, limit: int = 5) -> list[dict[str, Any]]:
        fetch_limit = max(limit, min(limit * 4, 20))
        targets = self.repository.list_review_targets(limit=fetch_limit)
        return [candidate for candidate in targets if self.requires_telegram_review(candidate)][:limit]

    def requires_telegram_review(self, candidate: dict[str, Any]) -> bool:
        source_domain = str(candidate.get("source_domain") or "").upper()
        return source_domain in TELEGRAM_REVIEW_SOURCE_DOMAINS and content_quality_gate(candidate).review_eligible

    def telegram_review_message(self, candidate: dict[str, Any], card_preview: dict[str, Any] | None = None) -> str:
        gate = content_quality_gate(candidate)
        if gate.code == ATTACHMENT_REVIEW_STATE:
            return build_attachment_metadata_review_message(candidate, gate)
        card_ok = bool((card_preview or {}).get("ok"))
        format_label = "CARD_IMAGE" if card_ok else "LINK_OR_TEXT"
        template = (card_preview or {}).get("template_type") or "-"
        score = float(candidate.get("final_publish_score") or 0)
        source = candidate.get("source_domain") or "-"
        content_type = candidate.get("content_type") or "-"
        source_name = candidate.get("source_name") or candidate.get("original_source_name") or "-"
        link = candidate.get("link_url") or candidate.get("source_url") or candidate.get("original_source_url") or "-"
        return "\n".join(
            [
                "[Content Review]",
                f"ID: {candidate.get('id')}",
                f"Source: {source} / {content_type} / {source_name}",
                f"Score: {score:.1f}",
                f"Format: {format_label}",
                f"Template: {template}",
                f"Link: {link}",
                "",
                "Preview image attached." if card_ok else "Preview image: not required.",
                "",
                "[Facebook Format Preview]",
                build_facebook_message(candidate),
                "",
                "Check next:",
                "- Confirm the source before publishing.",
                "- Confirm whether this applies to work, visa, housing, healthcare, banking, or daily life.",
                "",
                "Operator scoring only. This does not publish to Facebook.",
            ]
        )

    def telegram_review_metadata(self, candidate: dict[str, Any], message: str) -> dict[str, Any]:
        return build_telegram_review_metadata(candidate, message)

    def telegram_review_card_preview(self, candidate: dict[str, Any]) -> dict[str, Any]:
        from .card_generator import build_content_card_preview

        return build_content_card_preview(candidate)

    def apply_operator_score(self, candidate_id: int, score: float, comment: str = "") -> dict[str, Any]:
        return self.repository.apply_operator_score(candidate_id, score, comment=comment)


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
    living = is_living_content(content_category or category or "", content_priority_group or "")
    payload = {
        "source_domain": "LIVING_INFO" if living else "SOCIAL_NEWS",
        "content_type": "LIVING_GUIDE" if living else "NEWS_ARTICLE",
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
        "hashtags": hashtags_for_content(content_priority_group or "", content_category or category or ""),
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
    return apply_content_quality_gate(payload)


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
    payload = {
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
    return apply_content_quality_gate(payload)


def apply_content_quality_gate(payload: dict[str, Any]) -> dict[str, Any]:
    decision = content_quality_gate(payload)
    raw_payload = payload.get("raw_payload") if isinstance(payload.get("raw_payload"), dict) else {}
    payload["raw_payload"] = {**raw_payload, **decision.as_payload()}
    if decision.code == ATTACHMENT_REVIEW_STATE:
        payload["content_type"] = DOCUMENT_EXTRACTION_REQUIRED_STATE
        payload["priority_group"] = ATTACHMENT_EVIDENCE_ONLY_STATE
        payload["raw_payload"] = {
            **payload["raw_payload"],
            "attachment_review_state": ATTACHMENT_REVIEW_STATE,
            "classification_status": "CLASSIFICATION_PENDING",
            "evidence_only_yn": True,
            "public_preview_allowed_yn": False,
            "telegram_review_suppression_reason": "zip_attachment_evidence_only",
            "attachment_review_reason": "attachment_content_not_inspected",
        }
    if decision.code != "REVIEW_ELIGIBLE":
        payload["review_reason"] = f"{decision.code}: {decision.reason}"
    if not decision.publish_eligible:
        payload["review_required_yn"] = False
        payload["sensitive_yn"] = False
        if payload.get("status") in {"READY_TO_PUBLISH", "READY_TO_REVIEW", "FAILED_RETRYABLE"}:
            payload["status"] = "SCORED"
        score_cap = 0.0 if decision.hard_block else 39.0
        for key in ("quality_score", "relevance_score", "practical_value_score", "content_potential_score", "final_publish_score"):
            try:
                payload[key] = min(float(payload.get(key) or 0), score_cap)
            except (TypeError, ValueError):
                payload[key] = score_cap
    return payload


def content_quality_gate(candidate: dict[str, Any]) -> ContentGateDecision:
    source_domain = clean(candidate.get("source_domain") or "").upper()
    content_type = clean(candidate.get("content_type") or "").upper()
    category = clean(candidate.get("category") or "").lower()
    priority_group = clean(candidate.get("priority_group") or "").upper()
    score = safe_float(candidate.get("final_publish_score") or candidate.get("quality_score") or 0)
    text = gate_text(candidate)
    link = usable_link(candidate)
    official = source_domain == "IMMIGRATION_INFO" or "NOTICE" in content_type or priority_group in {"OFFICIAL_NOTICE", "PRIMARY_SOURCE"}
    has_korea = has_any(text, TARGET_COUNTRY_TERMS)
    has_other_country = has_any(text, OTHER_COUNTRY_REFERENCE_TERMS)
    has_user_need = has_any(text, USER_NEED_TERMS)
    has_actionability = has_any(text, ACTIONABILITY_TERMS)
    practical_category = category in {
        "housing",
        "banking",
        "finance",
        "healthcare",
        "transportation",
        "insurance",
        "telecom",
        "korean_language",
        "cost_of_living",
        "local_community",
        "education",
        "settlement_life",
        "immigration",
        "work_visa",
        "government_notice",
    }
    official_utility = official and has_any(
        text,
        (
            "manual",
            "guide",
            "lookup",
            "institution",
            "agency",
            "office",
            "medical institution",
            "hospital",
            "immigration office",
            "visa",
            "stay",
        ),
    )

    if not valid_content_link(link):
        return ContentGateDecision(
            "BLOCKED_SOURCE_INVALID",
            "A usable source, canonical, or publishable link is missing.",
            False,
            False,
            hard_block=True,
        )
    if official_attachment_review_required(candidate, text, link, official):
        return ContentGateDecision(
            ATTACHMENT_REVIEW_STATE,
            (
                "official_notice_attachment_review_required: "
                "attachment_content_not_inspected; zip_attachment_evidence_only; "
                "generic_attachment_preview_not_publishable; "
                "source_menu_label_classification_pending"
            ),
            False,
            False,
        )
    if has_any(text, SYSTEM_MESSAGE_TERMS):
        return ContentGateDecision(
            "BLOCKED_SYSTEM_TEXT",
            "System, queue, parser, or internal operation text is present in public content fields.",
            False,
            False,
            hard_block=True,
        )
    if has_other_country and not has_korea:
        return ContentGateDecision(
            "BLOCKED_GLOBAL_REFERENCE_ONLY",
            "The item is a non-Korea reference and should not enter the current WorkConnect Korea queue.",
            False,
            False,
            hard_block=True,
            global_reference_only=True,
        )
    if generic_travel_item(text, category, has_actionability, practical_category):
        return ContentGateDecision(
            "BLOCKED_GENERIC_TRAVEL",
            "Generic travel, tourism, or destination-safety content is not practical Korea settlement guidance.",
            False,
            False,
        )
    if generic_crypto_item(text):
        return ContentGateDecision(
            "BLOCKED_GENERIC_CRYPTO",
            "Generic crypto or investment content is not core living, work, visa, or settlement guidance.",
            False,
            False,
        )
    if domestic_politics_item(text, has_user_need, has_actionability):
        return ContentGateDecision(
            "BLOCKED_DOMESTIC_POLITICS",
            "Domestic politics or election coverage has no direct visa, labor, settlement, or support action.",
            False,
            False,
        )
    if generic_economy_item(text):
        return ContentGateDecision(
            "BLOCKED_GENERIC_ECONOMY",
            "Generic market or macro-economy coverage has no direct foreign-resident actionability.",
            False,
            False,
        )
    watch_topic = watch_topic_code(text)
    if watch_topic:
        return ContentGateDecision(
            "WATCH_TOPIC_ONLY",
            f"Keep as watch topic {watch_topic}; do not review or publish until an actionable outcome appears.",
            False,
            False,
            watch_topic=watch_topic,
        )
    if low_user_need_notice(text, has_user_need, has_actionability):
        return ContentGateDecision(
            "BLOCKED_LOW_USER_NEED",
            "Public campaign, meeting, ceremony, MOU, or PR-style item has low direct user need.",
            False,
            False,
        )
    if title_only_or_missing_content(candidate, official):
        return ContentGateDecision(
            "BLOCKED_CONTENT_MISSING",
            "The item has no useful body or summary for review/public content.",
            False,
            False,
            hard_block=True,
        )
    if not official and not has_korea and not (has_user_need and practical_category):
        return ContentGateDecision(
            "BLOCKED_TARGET_COUNTRY_MISMATCH",
            "The item does not have enough direct Korea relevance for the current channel.",
            False,
            False,
            hard_block=True,
        )
    if score <= 0:
        return ContentGateDecision(
            "BLOCKED_LOW_USER_NEED",
            "Score is zero, so the item should not enter review or publishing queues.",
            False,
            False,
        )
    if score < 40 and not (official_utility or (has_user_need and has_actionability and practical_category)):
        return ContentGateDecision(
            "BLOCKED_LOW_USER_NEED",
            "Score is below the minimum review threshold and no strong practical user action is present.",
            False,
            False,
        )

    review_eligible = source_domain in TELEGRAM_REVIEW_SOURCE_DOMAINS and (
        official_utility
        or source_domain == "IMMIGRATION_INFO"
        or (score >= 40 and (practical_category or has_user_need) and has_actionability)
    )
    return ContentGateDecision(
        "REVIEW_ELIGIBLE",
        "The item has a valid link, Korea relevance, and practical user value.",
        review_eligible,
        True,
    )


def gate_text(candidate: dict[str, Any]) -> str:
    parts = [
        candidate.get("title"),
        candidate.get("original_title"),
        candidate.get("summary_en"),
        candidate.get("why_it_matters_en"),
        candidate.get("body_en"),
        candidate.get("source_name"),
        candidate.get("original_source_name"),
        candidate.get("category"),
        candidate.get("content_type"),
        candidate.get("review_reason"),
        candidate.get("link_url"),
        candidate.get("source_url"),
    ]
    return normalize_plain_text(" ".join(str(part or "") for part in parts)).lower()


def public_body_text(candidate: dict[str, Any]) -> str:
    return normalize_plain_text(
        " ".join(
            str(candidate.get(key) or "")
            for key in ("summary_en", "body_en")
        )
    ).lower()


def raw_payload_text(candidate: dict[str, Any]) -> str:
    raw_payload = candidate.get("raw_payload") or {}
    if not isinstance(raw_payload, dict):
        return normalize_plain_text(str(raw_payload)).lower()
    parts: list[str] = []
    for value in raw_payload.values():
        if isinstance(value, (dict, list, tuple)):
            parts.append(str(value))
        elif value is not None:
            parts.append(str(value))
    return normalize_plain_text(" ".join(parts)).lower()


def official_attachment_review_required(candidate: dict[str, Any], text: str, link: str, official: bool) -> bool:
    if not official:
        return False
    link_text = clean(link).lower()
    evidence_text = " ".join([text, link_text, raw_payload_text(candidate)])
    has_attachment_evidence = has_any(evidence_text, ATTACHMENT_FILE_TERMS) or has_any(evidence_text, ATTACHMENT_ONLY_TERMS)
    if not has_attachment_evidence:
        return False
    body_text = public_body_text(candidate)
    if not body_text:
        return True
    body_without_attachment_words = body_text
    for term in ATTACHMENT_ONLY_TERMS:
        body_without_attachment_words = body_without_attachment_words.replace(term.lower(), " ")
    body_without_attachment_words = re.sub(r"[^0-9a-z]+", " ", body_without_attachment_words).strip()
    if not body_without_attachment_words:
        return True
    if has_any(body_text, ATTACHMENT_ONLY_TERMS) and len(body_without_attachment_words) < 24:
        return True
    return False


def usable_link(candidate: dict[str, Any]) -> str:
    return clean(candidate.get("link_url") or candidate.get("source_url") or candidate.get("original_source_url") or "")


def valid_content_link(value: str) -> bool:
    link = clean(value)
    if not link or link == "-":
        return False
    try:
        parsed = urlsplit(link)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    if "news.google." in host:
        return False
    return True


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def generic_travel_item(text: str, category: str, has_actionability: bool, practical_category: bool) -> bool:
    if category != "travel" and not has_any(text, GENERIC_TRAVEL_TERMS):
        return False
    settlement_exception = practical_category and has_actionability and has_any(text, USER_NEED_TERMS)
    return not settlement_exception


def generic_crypto_item(text: str) -> bool:
    return has_any(text, GENERIC_CRYPTO_TERMS) and not has_any(text, ESSENTIAL_FINANCE_TERMS)


def domestic_politics_item(text: str, has_user_need: bool, has_actionability: bool) -> bool:
    if not has_any(text, DOMESTIC_POLITICS_TERMS):
        return False
    policy_exception = has_user_need and has_actionability and has_any(text, ("visa", "immigration", "labor", "foreign worker", "foreign resident"))
    return not policy_exception


def generic_economy_item(text: str) -> bool:
    return has_any(text, GENERIC_ECONOMY_TERMS) and not has_any(text, ESSENTIAL_FINANCE_TERMS + USER_NEED_TERMS)


def watch_topic_code(text: str) -> str:
    if ("minimum wage" in text or "최저임금" in text) and has_any(text, ("committee", "meeting", "회의", "위원회")):
        if not has_any(text, ("decided", "announced", "set at", "increase", "decrease", "결정", "인상", "확정", "발표")):
            return "MINIMUM_WAGE_2026"
    if has_any(text, OTHER_COUNTRY_REFERENCE_TERMS) and has_any(text, ("immigration policy", "foreigner policy", "migrant policy")):
        return "GLOBAL_MIGRATION_POLICY_REFERENCE"
    return ""


def low_user_need_notice(text: str, has_user_need: bool, has_actionability: bool) -> bool:
    return has_any(text, LOW_USER_NEED_NOTICE_TERMS) and not (has_user_need and has_actionability)


def title_only_or_missing_content(candidate: dict[str, Any], official: bool) -> bool:
    if official:
        return False
    public_text = normalize_plain_text(
        " ".join(
            str(candidate.get(key) or "")
            for key in ("summary_en", "why_it_matters_en", "body_en")
        )
    )
    title = clean(candidate.get("title") or candidate.get("original_title") or "")
    return bool(title) and len(public_text) < 40


def build_attachment_metadata_review_message(candidate: dict[str, Any], decision: ContentGateDecision) -> str:
    source_name = clean(candidate.get("source_name") or candidate.get("original_source_name") or "-")
    title = clean(candidate.get("title") or candidate.get("original_title") or "-")
    link = clean(candidate.get("link_url") or candidate.get("source_url") or candidate.get("original_source_url") or "-")
    parsed = urlsplit(link) if link.startswith(("http://", "https://")) else None
    query = dict(parse_qsl(parsed.query, keep_blank_values=True)) if parsed else {}
    raw_payload = candidate.get("raw_payload") if isinstance(candidate.get("raw_payload"), dict) else {}
    raw_response = raw_payload.get("raw_response") if isinstance(raw_payload.get("raw_response"), dict) else {}
    attachment_name = clean(
        raw_payload.get("attachment_filename")
        or raw_payload.get("attachment_name")
        or raw_response.get("attachment_filename")
        or raw_response.get("attachment_name")
        or "-"
    )
    attachment_size = clean(
        raw_payload.get("attachment_size")
        or raw_response.get("attachment_size")
        or "-"
    )
    bbs_seq = clean(query.get("bbs_seq") or raw_payload.get("bbs_seq") or raw_response.get("bbs_seq") or "-")
    bbs_id = clean(query.get("bbs_id") or raw_payload.get("bbs_id") or raw_response.get("bbs_id") or "-")
    return "\n".join(
        [
            "[Content Review - Evidence Only]",
            f"ID: {candidate.get('id')}",
            f"Source: {candidate.get('source_domain') or '-'} / {candidate.get('content_type') or '-'} / {source_name}",
            f"Status: {ATTACHMENT_EVIDENCE_ONLY_STATE}",
            f"Reason: {decision.reason}",
            f"Title: {title}",
            f"Link: {link}",
            f"bbs_seq: {bbs_seq}",
            f"bbs_id: {bbs_id}",
            f"Attachment: {attachment_name}",
            f"Attachment size: {attachment_size}",
            "",
            "No Facebook Format Preview is generated.",
            "Document extraction is required before public classification or publishing.",
        ]
    )


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def build_facebook_message(candidate: dict[str, Any]) -> str:
    title = clean(candidate.get("title", ""))[:180]
    summary = bullet_lines(candidate.get("summary_en", ""), limit=5)
    why = bullet_lines(candidate.get("why_it_matters_en", ""), limit=4)
    source_name = clean(candidate.get("source_name") or candidate.get("original_source_name") or "")
    parts = [title]
    if summary:
        parts.append("What changed:\n" + "\n".join(summary))
    if why:
        parts.append("Why it matters for foreign workers in Korea:\n" + "\n".join(why))
    parts.append("Check next:\n- Open the official/source link before making decisions.\n- Confirm whether the update applies to your visa, job, city, or household situation.")
    if source_name:
        parts.append(f"Source: {source_name}")
    hashtags = clean(candidate.get("hashtags", "")) or "#KoreaJobs #WorkInKorea #ForeignWorkers"
    parts.append(hashtags)
    return "\n\n".join(part for part in parts if part.strip())


def build_telegram_review_metadata(candidate: dict[str, Any], message: str) -> dict[str, Any]:
    candidate_id = int(candidate.get("id") or 0)
    source_domain = clean(candidate.get("source_domain") or "").upper()
    content_type = clean(candidate.get("content_type") or "").upper()
    status = clean(candidate.get("status") or "")
    score = float(candidate.get("final_publish_score") or 0)
    bucket = score_bucket(score)
    review_url = review_identity_url(candidate)
    message_hash = review_message_hash(candidate, message, review_url)
    candidate_review_key = stable_hash(
        "|".join(
            [
                "candidate",
                str(candidate_id),
                status,
                bucket,
                message_hash,
            ]
        )
    )
    semantic_identity = review_url or normalized_hash_text(candidate.get("title") or candidate.get("original_title") or "")
    semantic_review_key = stable_hash(
        "|".join(
            [
                "semantic",
                source_domain,
                content_type,
                semantic_identity,
                status,
                bucket,
                message_hash,
            ]
        )
    )
    return {
        "telegram_review_key": candidate_review_key,
        "semantic_review_key": semantic_review_key,
        "telegram_review_key_basis": "content_candidate_id|status|score_bucket|message_hash",
        "semantic_review_key_basis": "source_domain|content_type|canonical_url_or_title|status|score_bucket|message_hash",
        "content_candidate_id": candidate_id,
        "source_domain": source_domain,
        "content_type": content_type,
        "status": status,
        "score": round(score, 2),
        "score_bucket": bucket,
        "message_hash": message_hash,
        "review_identity_url": review_url,
        "review_reason_hash": stable_hash(normalized_hash_text(candidate.get("review_reason") or "")),
        "duplicate_signal_bucket": duplicate_signal_bucket(candidate),
        "message_preview": message[:500],
    }


def score_bucket(score: float) -> str:
    if score < 40:
        return "0-39"
    if score < 60:
        return "40-59"
    if score < 80:
        return "60-79"
    return "80-100"


def review_identity_url(candidate: dict[str, Any]) -> str:
    return normalize_review_url(
        candidate.get("link_url")
        or candidate.get("source_url")
        or candidate.get("original_source_url")
        or ""
    )


def normalize_review_url(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    try:
        parsed = urlsplit(text)
    except ValueError:
        return normalized_hash_text(text)
    if not parsed.scheme or not parsed.netloc:
        return normalized_hash_text(text)
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid"}
    ]
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            urlencode(query_pairs, doseq=True),
            "",
        )
    )


def review_message_hash(candidate: dict[str, Any], message: str, review_url: str) -> str:
    content_parts = [
        candidate.get("title") or "",
        candidate.get("summary_en") or "",
        candidate.get("why_it_matters_en") or "",
        candidate.get("body_en") or "",
        candidate.get("review_reason") or "",
        review_url,
        duplicate_signal_bucket(candidate),
    ]
    normalized = normalized_hash_text("\n".join(str(part or "") for part in content_parts))
    if not normalized:
        normalized = normalized_hash_text(message)
    return stable_hash(normalized)


def duplicate_signal_bucket(candidate: dict[str, Any]) -> str:
    raw_payload = candidate.get("raw_payload") or {}
    if not isinstance(raw_payload, dict):
        raw_payload = {}
    count = 0
    for key in ("source_spread_count", "related_source_count", "duplicate_count", "group_item_count"):
        value = candidate.get(key, raw_payload.get(key))
        try:
            count = max(count, int(value or 0))
        except (TypeError, ValueError):
            continue
    if count >= 10:
        return "10+"
    if count >= 5:
        return "5-9"
    if count >= 2:
        return "2-4"
    return "0-1"


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def normalized_hash_text(value: Any) -> str:
    text = normalize_plain_text(str(value or "")).lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^0-9a-z\uac00-\ud7a3]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_living_content(category: str, priority_group: str = "") -> bool:
    living_categories = {
        "housing",
        "banking",
        "healthcare",
        "transportation",
        "insurance",
        "korean_language",
        "cost_of_living",
        "local_community",
        "education",
        "settlement_life",
        "travel",
        "lifestyle",
        "culture",
        "local_events",
        "safety",
    }
    return (category or "").strip() in living_categories or (priority_group or "").strip().upper() in {"SECONDARY", "TERTIARY"}


def hashtags_for_content(priority_group: str, category: str) -> str:
    group = (priority_group or "").strip().upper()
    if group in {"SECONDARY", "TERTIARY"} or is_living_content(category, group):
        return "#LivingInKorea #ForeignersInKorea #KoreaLife #WorkConnectKorea"
    if (category or "").strip() in {"immigration", "work_visa", "government_notice"}:
        return "#KoreaVisa #ImmigrationKorea #ForeignWorkers #WorkConnectKorea"
    return "#KoreaJobs #WorkInKorea #ForeignWorkers #WorkConnectKorea"


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
