"""Facebook publisher for automated news pipeline."""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from ....utils.text_normalizer import normalize_plain_text
from ...facebook.error_normalizer import (
    TOKEN_EXPIRING_SOON,
    build_error_context,
    classify_internal_error,
    retryable_for_category,
    token_status_snapshot,
)
from ...facebook.page_client import FacebookPageClient
from ...facebook.token_manager import get_facebook_page_token
from ..category_rotation import hashtags_for_group
from ..collector.google_news_url_resolver import is_acceptable_source_url, is_google_news_url
from ..models import NewsCandidate

FACEBOOK_PAGE_ID_ENV = "FACEBOOK_PAGE_ID"
FACEBOOK_PAGE_ACCESS_TOKEN_ENV = "FACEBOOK_PAGE_ACCESS_TOKEN"
FACEBOOK_APP_TOKEN_ENV = "FACEBOOK_APP_TOKEN"
REQUIRED_PAGE_SCOPES = {"pages_read_engagement", "pages_manage_posts"}
OPERATIONAL_MESSAGE_BLOCKLIST = (
    "admin",
    "administrator",
    "current score",
    "facebook publish",
    "pipeline_log",
    "publish_status",
    "queue",
    "ready_to_publish",
    "review_required",
    "threshold",
)


@dataclass
class FacebookLinkDecision:
    url: str
    valid: bool
    reject_reason: str = ""


def mask_token(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if len(value) <= 12:
        return f"{value[:2]}***{value[-2:]}"
    return f"{value[:6]}...{value[-6:]}"


def token_fingerprint(value: str) -> str:
    value = (value or "").strip()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8] if value else ""


def facebook_runtime_config_summary() -> dict:
    page_id = os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip()
    selection = get_facebook_page_token(allow_refresh=False)
    page_token = selection.access_token
    return {
        "page_id": page_id,
        "page_token_masked": mask_token(page_token),
        "page_token_fingerprint": token_fingerprint(page_token),
        "page_token_source": selection.source,
        "user_token_present": bool(os.getenv("FACEBOOK_USER_ACCESS_TOKEN", "").strip()),
    }


class FacebookPublisher:
    def __init__(self, client: FacebookPageClient | None = None):
        self.client = client or FacebookPageClient()

    def build_message(self, candidate: NewsCandidate) -> str:
        title = normalize_plain_text(candidate.generated_title or candidate.title)[:180]
        summary_lines = _bullet_lines(candidate.generated_summary_en or candidate.key_points or candidate.short_summary or candidate.summary, limit=5)
        why_lines = _bullet_lines(candidate.generated_why_it_matters_en or candidate.relevance_reason, limit=4)
        parts = [title]
        if summary_lines:
            parts.append("Summary:\n" + "\n".join(summary_lines[:5]))
        if why_lines:
            audience = "foreigners living in Korea" if candidate.content_priority_group in {"SECONDARY", "TERTIARY"} else "foreign workers in Korea"
            parts.append(f"Why it matters for {audience}:\n" + "\n".join(why_lines[:4]))
        parts.append("Read more below.")
        parts.append(hashtags_for_group(candidate.content_priority_group))
        return "\n\n".join(part for part in parts if part and part.strip())

    def publish(self, candidate: NewsCandidate, dry_run: bool = False) -> dict:
        message = self.build_message(candidate)
        link_decision = facebook_link_url(candidate)
        request_payload = {
            "message": message,
            "link": link_decision.url,
            "link_valid_yn": link_decision.valid,
            "link_reject_reason": link_decision.reject_reason,
            "facebook_debugger_url": sharing_debugger_url(link_decision.url),
        }
        reject_reason = facebook_message_reject_reason(message)
        if reject_reason:
            return with_error_context({
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip(),
                "message": message,
                "facebook_link_url": link_decision.url,
                "link_valid_yn": link_decision.valid,
                "link_reject_reason": link_decision.reject_reason,
                "request_payload": request_payload,
                "error_code": "FACEBOOK_MESSAGE_INVALID",
                "error_message": reject_reason,
                "response_code": "",
                "response_body": "",
            }, candidate=candidate, link_url=link_decision.url, mode="dry_run" if dry_run else "real")
        if not link_decision.valid:
            return with_error_context({
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip(),
                "message": message,
                "facebook_link_url": link_decision.url,
                "link_valid_yn": False,
                "link_reject_reason": link_decision.reject_reason,
                "request_payload": request_payload,
                "error_code": "FACEBOOK_LINK_INVALID",
                "error_message": f"Facebook link card URL is invalid: {link_decision.reject_reason}",
                "response_code": "",
                "response_body": "",
            }, candidate=candidate, link_url=link_decision.url, mode="dry_run" if dry_run else "real")
        if dry_run:
            facebook_post_id = f"dry-run-news-{candidate.id}"
            return {
                "status": "DRY_RUN",
                "facebook_post_id": facebook_post_id,
                "facebook_post_url": f"https://www.facebook.com/{facebook_post_id}",
                "page_id": "dry-run",
                "message": message,
                "facebook_link_url": link_decision.url,
                "link_valid_yn": True,
                "link_reject_reason": "",
                "request_payload": request_payload,
                "error_code": "",
                "error_message": "",
                "response_code": "",
                "response_body": "",
            }

        token_selection = get_facebook_page_token(allow_refresh=True)
        page_id = token_selection.page_id or os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip()
        access_token = token_selection.access_token
        app_token = os.getenv(FACEBOOK_APP_TOKEN_ENV, "").strip()
        request_payload.update(
            {
                "page_id": page_id,
                "token_source": token_selection.source,
                "token_config_path": token_selection.config_path,
                "token_masked": mask_token(access_token),
                "token_fingerprint": token_fingerprint(access_token),
                "user_token_present": bool(os.getenv("FACEBOOK_USER_ACCESS_TOKEN", "").strip()),
            }
        )
        if not page_id or not access_token:
            return with_error_context({
                "status": "FAILED_RETRYABLE",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "facebook_link_url": link_decision.url,
                "link_valid_yn": True,
                "link_reject_reason": "",
                "request_payload": request_payload,
                "error_code": "MISSING_FACEBOOK_ENV",
                "error_message": "FACEBOOK_PAGE_ID와 FACEBOOK_PAGE_ACCESS_TOKEN이 필요합니다.",
                    "response_code": "",
                    "response_body": "",
                    "token_debug": {
                        "token_masked": mask_token(access_token),
                        "token_fingerprint": token_fingerprint(access_token),
                        "token_source": token_selection.source,
                    },
                }, candidate=candidate, link_url=link_decision.url, mode="real")
        safe_debug = {
            "token_source": token_selection.source,
            "token_masked": mask_token(access_token),
            "token_fingerprint": token_fingerprint(access_token),
            "token_type": "",
            "is_valid": None,
            "profile_id": "",
            "scopes": [],
            "expires_at": 0,
            "app_id": "",
        }
        token_debug = {}
        if app_token:
            token_debug = self.client.debug_token(access_token, app_token)
            safe_debug.update(
                {
                    "token_type": token_debug.get("token_type", ""),
                    "is_valid": token_debug.get("is_valid", False),
                    "profile_id": token_debug.get("profile_id", ""),
                    "scopes": token_debug.get("scopes", []),
                    "expires_at": token_debug.get("expires_at", 0),
                    "app_id": token_debug.get("app_id", ""),
                }
            )
            request_payload["token_debug"] = safe_debug
            if token_debug.get("status") != "OK" and not safe_debug["is_valid"]:
                return with_error_context({
                    "status": "FAILED_RETRYABLE",
                    "facebook_post_id": "",
                    "facebook_post_url": "",
                    "page_id": page_id,
                    "message": message,
                    "facebook_link_url": link_decision.url,
                    "link_valid_yn": True,
                    "link_reject_reason": "",
                    "request_payload": request_payload,
                    "error_code": token_debug.get("error_code", "FACEBOOK_DEBUG_TOKEN_FAILED"),
                    "error_message": token_debug.get("error_message", "Facebook token debug에 실패했습니다."),
                    "response_code": token_debug.get("response_code", ""),
                    "response_body": token_debug.get("response_body", ""),
                    "token_debug": safe_debug,
                }, candidate=candidate, link_url=link_decision.url, mode="real", token=access_token)
        else:
            request_payload["token_debug"] = safe_debug
        if safe_debug["is_valid"] is False:
            return with_error_context({
                "status": "FAILED_RETRYABLE",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "facebook_link_url": link_decision.url,
                "link_valid_yn": True,
                "link_reject_reason": "",
                "request_payload": request_payload,
                "error_code": "FACEBOOK_TOKEN_INVALID",
                "error_message": "FACEBOOK_PAGE_ACCESS_TOKEN이 유효하지 않습니다.",
                "response_code": token_debug.get("response_code", ""),
                "response_body": token_debug.get("response_body", ""),
                "token_debug": safe_debug,
            }, candidate=candidate, link_url=link_decision.url, mode="real", token=access_token)
        if safe_debug["profile_id"] and safe_debug["profile_id"] != page_id:
            return with_error_context({
                "status": "FAILED_RETRYABLE",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "facebook_link_url": link_decision.url,
                "link_valid_yn": True,
                "link_reject_reason": "",
                "request_payload": request_payload,
                "error_code": "FACEBOOK_PAGE_TOKEN_MISMATCH",
                "error_message": f"Page token profile_id가 FACEBOOK_PAGE_ID와 다릅니다. profile_id={safe_debug['profile_id']}, page_id={page_id}",
                "response_code": token_debug.get("response_code", ""),
                "response_body": token_debug.get("response_body", ""),
                "token_debug": safe_debug,
            }, candidate=candidate, link_url=link_decision.url, mode="real", token=access_token)
        missing_scopes = sorted(REQUIRED_PAGE_SCOPES - set(safe_debug["scopes"]))
        if safe_debug["scopes"] and missing_scopes:
            return with_error_context({
                "status": "FAILED_RETRYABLE",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "facebook_link_url": link_decision.url,
                "link_valid_yn": True,
                "link_reject_reason": "",
                "request_payload": request_payload,
                "error_code": "FACEBOOK_PERMISSION_MISSING",
                "error_message": f"Facebook Page token 권한이 부족합니다: {', '.join(missing_scopes)}",
                "response_code": token_debug.get("response_code", ""),
                "response_body": token_debug.get("response_body", ""),
                "token_debug": safe_debug,
            }, candidate=candidate, link_url=link_decision.url, mode="real", token=access_token)

        result = self.client.publish(message=message, link=link_decision.url, page_id=page_id, access_token=access_token)
        facebook_post_id = result.get("facebook_post_id", "")
        payload = {
            "status": result.get("status", "FAILED"),
            "facebook_post_id": facebook_post_id,
            "facebook_post_url": result.get("facebook_post_url") or (f"https://www.facebook.com/{facebook_post_id}" if facebook_post_id else ""),
            "page_id": page_id,
            "message": message,
            "facebook_link_url": link_decision.url,
            "link_valid_yn": True,
            "link_reject_reason": "",
            "request_payload": request_payload,
            "error_code": result.get("error_code", ""),
            "error_message": result.get("error_message", ""),
            "response_code": result.get("response_code", ""),
            "response_body": result.get("response_body", ""),
            "token_debug": safe_debug,
        }
        if payload["status"] not in {"PUBLISHED", "DRY_RUN"}:
            return with_error_context(payload, candidate=candidate, link_url=link_decision.url, mode="real", token=access_token)
        payload["token_status"] = token_status_snapshot(token=access_token, token_debug=safe_debug, page_id=page_id, required_scopes=REQUIRED_PAGE_SCOPES)
        if token_expiring_soon(payload["token_status"]):
            payload["token_warning_category"] = TOKEN_EXPIRING_SOON
        return payload


def _bullet_lines(value: str, limit: int) -> list[str]:
    lines: list[str] = []
    for line in (value or "").splitlines():
        cleaned = normalize_plain_text(line.strip().lstrip("-").strip())
        if cleaned:
            lines.append(f"- {cleaned[:240]}")
    if not lines and value:
        cleaned = normalize_plain_text(value)
        if cleaned:
            lines.append(f"- {cleaned[:240]}")
    return lines[:limit]


def with_error_context(
    result: dict,
    *,
    candidate: NewsCandidate,
    link_url: str,
    mode: str,
    token: str = "",
) -> dict:
    token_debug = result.get("token_debug") or {}
    page_id = str(result.get("page_id") or os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip())
    token_status = token_status_snapshot(
        token=token,
        token_debug=token_debug,
        page_id=page_id,
        required_scopes=REQUIRED_PAGE_SCOPES,
    )
    context = build_error_context(
        error_code=str(result.get("error_code") or ""),
        error_message=str(result.get("error_message") or ""),
        response_code=str(result.get("response_code") or ""),
        response_body=str(result.get("response_body") or ""),
        link_url=link_url,
        endpoint=f"/{page_id}/feed" if page_id else "",
        mode=mode,
        candidate_id=candidate.id,
        token_status=token_status,
    )
    if not context.get("meta_error") and result.get("error_category"):
        context["error_category"] = result["error_category"]
        context["retryable_yn"] = retryable_for_category(str(result["error_category"]))
    category = str(context.get("error_category") or classify_internal_error(result.get("error_code", ""), result.get("error_message", "")))
    result["error_category"] = category
    result["token_status"] = token_status
    result["retryable_yn"] = retryable_for_category(category)
    result["error_context"] = context
    return result


def token_expiring_soon(token_status: dict) -> bool:
    value = token_status.get("expires_in_seconds")
    try:
        return value != "" and 0 < int(value) <= 7 * 24 * 60 * 60
    except (TypeError, ValueError):
        return False


def has_korean_text(value: str, max_hangul_chars: int = 6) -> bool:
    text = value or ""
    hangul = sum(1 for char in text if "\uac00" <= char <= "\ud7a3")
    if hangul > max_hangul_chars:
        return True
    letters = sum(1 for char in text if char.isalpha())
    return letters > 0 and hangul / max(letters, 1) > 0.08


def facebook_message_reject_reason(message: str) -> str:
    text = normalize_plain_text(message or "")
    if has_korean_text(text, max_hangul_chars=6):
        return "Facebook message contains Korean text; English-only automated posts are required."
    lowered = text.lower()
    for blocked in OPERATIONAL_MESSAGE_BLOCKLIST:
        if blocked in lowered:
            return f"Facebook message contains operational/admin text: {blocked}"
    return ""


def facebook_link_url(candidate: NewsCandidate) -> FacebookLinkDecision:
    candidates = [
        ("source_url", candidate.source_url),
        ("canonical_url", candidate.canonical_url),
        ("original_url", str(getattr(candidate, "original_url", "") or "")),
    ]
    reject_reasons: list[str] = []
    for label, value in candidates:
        url = (value or "").strip()
        valid, reason = validate_facebook_article_link(url)
        if valid:
            return FacebookLinkDecision(url=url, valid=True)
        if url:
            reject_reasons.append(f"{label}: {reason}")
    return FacebookLinkDecision(url="", valid=False, reject_reason="; ".join(reject_reasons) or "no article URL")


def validate_facebook_article_link(url: str) -> tuple[bool, str]:
    url = (url or "").strip()
    if not url:
        return False, "empty"
    if is_google_news_url(url):
        return False, "google news URL is not allowed"
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False, "not absolute URL"
    path = (parsed.path or "").strip("/")
    if not path:
        return False, "publisher root URL is not allowed"
    if path.startswith("path/A"):
        return False, "legacy /path/A redirect URL is not allowed"
    if not is_acceptable_source_url(url):
        return False, "not a publisher article URL"
    if str(parse_qs(parsed.query).get("article_url_valid_yn", [""])[0]).lower() == "false":
        return False, "article_url_valid_yn=false"
    return True, ""


def sharing_debugger_url(url: str) -> str:
    if not url:
        return ""
    return f"https://developers.facebook.com/tools/debug/?q={url}"
