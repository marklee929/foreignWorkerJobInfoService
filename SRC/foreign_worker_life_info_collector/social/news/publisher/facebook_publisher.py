"""Facebook publisher for automated news pipeline."""

from __future__ import annotations

import os

from ....utils.text_normalizer import normalize_plain_text
from ...facebook.page_client import FacebookPageClient
from ..collector.google_news_url_resolver import best_article_url, is_domain_root_url
from ..models import NewsCandidate

FACEBOOK_PAGE_ID_ENV = "FACEBOOK_PAGE_ID"
FACEBOOK_PAGE_ACCESS_TOKEN_ENV = "FACEBOOK_PAGE_ACCESS_TOKEN"
FACEBOOK_APP_TOKEN_ENV = "FACEBOOK_APP_TOKEN"
REQUIRED_PAGE_SCOPES = {"pages_read_engagement", "pages_manage_posts"}


def mask_token(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if len(value) <= 12:
        return f"{value[:2]}***{value[-2:]}"
    return f"{value[:6]}...{value[-6:]}"


def facebook_runtime_config_summary() -> dict:
    page_id = os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip()
    page_token = os.getenv(FACEBOOK_PAGE_ACCESS_TOKEN_ENV, "").strip()
    return {
        "page_id": page_id,
        "page_token_masked": mask_token(page_token),
        "page_token_env_key": FACEBOOK_PAGE_ACCESS_TOKEN_ENV,
        "user_token_present": bool(os.getenv("FACEBOOK_USER_ACCESS_TOKEN", "").strip()),
    }


class FacebookPublisher:
    def __init__(self, client: FacebookPageClient | None = None):
        self.client = client or FacebookPageClient()

    def build_message(self, candidate: NewsCandidate) -> str:
        title = normalize_plain_text(candidate.generated_title or candidate.title)[:180]
        summary_lines = _bullet_lines(candidate.generated_summary_en or candidate.key_points or candidate.short_summary or candidate.summary, limit=5)
        why_lines = _bullet_lines(candidate.generated_why_it_matters_en or candidate.relevance_reason or candidate.selection_reason, limit=4)
        read_more_url = _publisher_url(candidate)

        parts = [title]
        if summary_lines:
            parts.append("Summary:\n" + "\n".join(summary_lines[:5]))
        if why_lines:
            parts.append("Why it matters for foreign workers in Korea:\n" + "\n".join(why_lines[:4]))
        if read_more_url:
            parts.append(f"Read more:\n{read_more_url}")
        parts.append("#KoreaJobs #WorkInKorea #ForeignWorkers #VisaInfo")
        return "\n\n".join(part for part in parts if part and part.strip())

    def publish(self, candidate: NewsCandidate, dry_run: bool = False) -> dict:
        message = self.build_message(candidate)
        if dry_run:
            facebook_post_id = f"dry-run-news-{candidate.id}"
            return {
                "status": "DRY_RUN",
                "facebook_post_id": facebook_post_id,
                "facebook_post_url": f"https://www.facebook.com/{facebook_post_id}",
                "page_id": "dry-run",
                "message": message,
                "error_code": "",
                "error_message": "",
                "response_code": "",
                "response_body": "",
            }

        page_id = os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip()
        access_token = os.getenv(FACEBOOK_PAGE_ACCESS_TOKEN_ENV, "").strip()
        app_token = os.getenv(FACEBOOK_APP_TOKEN_ENV, "").strip()
        if not page_id or not access_token:
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "error_code": "MISSING_FACEBOOK_ENV",
                "error_message": "FACEBOOK_PAGE_ID와 FACEBOOK_PAGE_ACCESS_TOKEN이 필요합니다.",
                "response_code": "",
                "response_body": "",
                "token_debug": {
                    "token_masked": mask_token(access_token),
                    "token_env_key": FACEBOOK_PAGE_ACCESS_TOKEN_ENV,
                },
            }
        if not app_token:
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "error_code": "MISSING_FACEBOOK_APP_TOKEN",
                "error_message": "FACEBOOK_APP_TOKEN이 필요합니다. 게시 전 Page token debug_token 검증에 사용됩니다.",
                "response_code": "",
                "response_body": "",
                "token_debug": {
                    "token_masked": mask_token(access_token),
                    "token_env_key": FACEBOOK_PAGE_ACCESS_TOKEN_ENV,
                },
            }

        token_debug = self.client.debug_token(access_token, app_token)
        safe_debug = {
            "token_env_key": FACEBOOK_PAGE_ACCESS_TOKEN_ENV,
            "token_masked": mask_token(access_token),
            "token_type": token_debug.get("token_type", ""),
            "is_valid": token_debug.get("is_valid", False),
            "profile_id": token_debug.get("profile_id", ""),
            "scopes": token_debug.get("scopes", []),
            "expires_at": token_debug.get("expires_at", 0),
            "app_id": token_debug.get("app_id", ""),
        }
        if token_debug.get("status") != "OK":
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "error_code": token_debug.get("error_code", "FACEBOOK_DEBUG_TOKEN_FAILED"),
                "error_message": token_debug.get("error_message", "Facebook token debug에 실패했습니다."),
                "response_code": token_debug.get("response_code", ""),
                "response_body": token_debug.get("response_body", ""),
                "token_debug": safe_debug,
            }
        if not safe_debug["is_valid"]:
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "error_code": "FACEBOOK_TOKEN_INVALID",
                "error_message": "FACEBOOK_PAGE_ACCESS_TOKEN이 유효하지 않습니다.",
                "response_code": token_debug.get("response_code", ""),
                "response_body": token_debug.get("response_body", ""),
                "token_debug": safe_debug,
            }
        if safe_debug["profile_id"] != page_id:
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "error_code": "FACEBOOK_PAGE_TOKEN_MISMATCH",
                "error_message": f"Page token profile_id가 FACEBOOK_PAGE_ID와 다릅니다. profile_id={safe_debug['profile_id']}, page_id={page_id}",
                "response_code": token_debug.get("response_code", ""),
                "response_body": token_debug.get("response_body", ""),
                "token_debug": safe_debug,
            }
        missing_scopes = sorted(REQUIRED_PAGE_SCOPES - set(safe_debug["scopes"]))
        if missing_scopes:
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "page_id": page_id,
                "message": message,
                "error_code": "FACEBOOK_PERMISSION_MISSING",
                "error_message": f"Facebook Page token 권한이 부족합니다: {', '.join(missing_scopes)}",
                "response_code": token_debug.get("response_code", ""),
                "response_body": token_debug.get("response_body", ""),
                "token_debug": safe_debug,
            }

        result = self.client.publish(message=message, page_id=page_id, access_token=access_token)
        facebook_post_id = result.get("facebook_post_id", "")
        return {
            "status": result.get("status", "FAILED"),
            "facebook_post_id": facebook_post_id,
            "facebook_post_url": result.get("facebook_post_url") or (f"https://www.facebook.com/{facebook_post_id}" if facebook_post_id else ""),
            "page_id": page_id,
            "message": message,
            "error_code": result.get("error_code", ""),
            "error_message": result.get("error_message", ""),
            "response_code": result.get("response_code", ""),
            "response_body": result.get("response_body", ""),
            "token_debug": safe_debug,
        }


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


def _publisher_url(candidate: NewsCandidate) -> str:
    preferred = best_article_url(candidate.source_url, candidate.canonical_url)
    if preferred:
        return preferred
    for value in (candidate.source_url, candidate.canonical_url):
        url = (value or "").strip()
        if url and not is_domain_root_url(url):
            return url
    for value in (candidate.google_news_url,):
        url = (value or "").strip()
        if url:
            return url
    return ""
