"""Facebook publish error normalization helpers."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any


TOKEN_INVALID = "TOKEN_INVALID"
TOKEN_EXPIRED = "TOKEN_EXPIRED"
TOKEN_EXPIRING_SOON = "TOKEN_EXPIRING_SOON"
TOKEN_PERMISSION_MISSING = "TOKEN_PERMISSION_MISSING"
TOKEN_WRONG_TYPE = "TOKEN_WRONG_TYPE"
TOKEN_PAGE_MISMATCH = "TOKEN_PAGE_MISMATCH"
FACEBOOK_RATE_LIMIT = "FACEBOOK_RATE_LIMIT"
FACEBOOK_POLICY_BLOCK = "FACEBOOK_POLICY_BLOCK"
FACEBOOK_LINK_INVALID = "FACEBOOK_LINK_INVALID"
FACEBOOK_LINK_BLOCKED = "FACEBOOK_LINK_BLOCKED"
FACEBOOK_PAYLOAD_INVALID = "FACEBOOK_PAYLOAD_INVALID"
FACEBOOK_API_TEMPORARY = "FACEBOOK_API_TEMPORARY"
FACEBOOK_UNKNOWN_ERROR = "FACEBOOK_UNKNOWN_ERROR"
INTERNAL_ENV_MISSING = "INTERNAL_ENV_MISSING"
INTERNAL_VALIDATION_FAILED = "INTERNAL_VALIDATION_FAILED"
INTERNAL_EXCEPTION = "INTERNAL_EXCEPTION"

RETRYABLE_CATEGORIES = {FACEBOOK_API_TEMPORARY, FACEBOOK_RATE_LIMIT}


def token_fingerprint(value: str, length: int = 8) -> str:
    value = (value or "").strip()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length] if value else ""


def meta_error_from_body(body: str) -> dict[str, Any]:
    if not body:
        return {}
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {}
    error = payload.get("error") or {}
    if not isinstance(error, dict):
        return {}
    return {
        "message": str(error.get("message") or ""),
        "type": str(error.get("type") or ""),
        "code": error.get("code"),
        "error_subcode": error.get("error_subcode"),
        "fbtrace_id": str(error.get("fbtrace_id") or ""),
    }


def classify_meta_error(meta_error: dict[str, Any], http_status: int | str = "") -> str:
    code = _int_or_none(meta_error.get("code"))
    message = str(meta_error.get("message") or "").lower()
    error_type = str(meta_error.get("type") or "").lower()
    status = _int_or_none(http_status)
    if code == 190:
        if any(token in message for token in ("expired", "session has expired", "token has expired")):
            return TOKEN_EXPIRED
        if "validating access token" in message or "invalid" in message or "oauth" in error_type:
            return TOKEN_INVALID
        return TOKEN_INVALID
    if code == 200:
        return TOKEN_PERMISSION_MISSING
    if code in {4, 17, 32, 613} or status == 429:
        return FACEBOOK_RATE_LIMIT
    if code == 368:
        return FACEBOOK_POLICY_BLOCK
    if code == 100:
        if any(token in message for token in ("link", "url", "href", "domain")):
            return FACEBOOK_LINK_INVALID
        return FACEBOOK_PAYLOAD_INVALID
    if status in {408, 409, 425, 500, 502, 503, 504}:
        return FACEBOOK_API_TEMPORARY
    return FACEBOOK_UNKNOWN_ERROR


def classify_internal_error(error_code: str, error_message: str = "") -> str:
    code = (error_code or "").upper()
    message = (error_message or "").lower()
    if code in {"MISSING_FACEBOOK_ENV", "MISSING_FACEBOOK_APP_TOKEN"}:
        return INTERNAL_ENV_MISSING
    if code in {"FACEBOOK_LINK_INVALID"}:
        return FACEBOOK_LINK_INVALID
    if code in {"FACEBOOK_MESSAGE_INVALID"}:
        return INTERNAL_VALIDATION_FAILED
    if code in {"FACEBOOK_PAGE_TOKEN_MISMATCH"}:
        return TOKEN_PAGE_MISMATCH
    if code in {"FACEBOOK_PERMISSION_MISSING", "FACEBOOK_PERMISSION_ERROR", "FACEBOOK_TOKEN_OR_PERMISSION_ERROR"}:
        return TOKEN_PERMISSION_MISSING
    if code in {"FACEBOOK_TOKEN_INVALID", "FACEBOOK_DEBUG_TOKEN_FAILED"}:
        if "expired" in message:
            return TOKEN_EXPIRED
        return TOKEN_INVALID
    if code in {"FACEBOOK_NETWORK_ERROR"}:
        return FACEBOOK_API_TEMPORARY
    if code in {"FACEBOOK_PUBLISH_ERROR", "FACEBOOK_DEBUG_ERROR", "FACEBOOK_DEBUG_NETWORK_ERROR"}:
        return INTERNAL_EXCEPTION
    return INTERNAL_VALIDATION_FAILED if code else FACEBOOK_UNKNOWN_ERROR


def retryable_for_category(category: str) -> bool:
    return category in RETRYABLE_CATEGORIES


def token_status_snapshot(
    *,
    token: str = "",
    token_debug: dict[str, Any] | None = None,
    page_id: str = "",
    required_scopes: set[str] | None = None,
) -> dict[str, Any]:
    debug = token_debug or {}
    scopes = set(str(scope) for scope in (debug.get("scopes") or []))
    required = required_scopes or set()
    expires_at = _int_or_none(debug.get("expires_at"))
    expires_in = expires_at - int(time.time()) if expires_at else None
    profile_id = str(debug.get("profile_id") or "")
    return {
        "token_type": str(debug.get("token_type") or "UNKNOWN"),
        "is_valid": debug.get("is_valid") if debug.get("is_valid") is not None else "unknown",
        "page_id_match": (profile_id == page_id) if profile_id and page_id else "unknown",
        "required_scopes_present": required.issubset(scopes) if scopes and required else "unknown",
        "expires_at": expires_at or "",
        "expires_in_seconds": expires_in if expires_in is not None else "",
        "token_fingerprint": str(debug.get("token_fingerprint") or token_fingerprint(token)),
        "validation_checked_at": int(time.time()),
    }


def build_error_context(
    *,
    error_code: str = "",
    error_message: str = "",
    response_code: str = "",
    response_body: str = "",
    link_url: str = "",
    endpoint: str = "",
    mode: str = "real",
    candidate_id: int | None = None,
    content_id: int | None = None,
    token_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    meta_error = meta_error_from_body(response_body)
    category = classify_meta_error(meta_error, response_code) if meta_error else classify_internal_error(error_code, error_message)
    return {
        "error_category": category,
        "error_code": str(error_code or ""),
        "error_message": str(error_message or meta_error.get("message") or ""),
        "meta_error": meta_error,
        "http_status": str(response_code or ""),
        "endpoint": endpoint,
        "link_url": link_url,
        "request_mode": mode,
        "candidate_id": candidate_id,
        "content_id": content_id,
        "token_status": token_status or {},
        "retryable_yn": retryable_for_category(category),
        "failed_at": int(time.time()),
    }


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
