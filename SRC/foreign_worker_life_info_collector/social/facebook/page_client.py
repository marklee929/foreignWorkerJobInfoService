"""Facebook Page client."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .error_normalizer import build_error_context, classify_meta_error, meta_error_from_body, retryable_for_category


class FacebookPageClient:
    def __init__(self, timeout: int | None = None):
        self.timeout = timeout or int(os.getenv("FACEBOOK_TIMEOUT_SEC", "20"))
        self.graph_base_url = os.getenv("FACEBOOK_GRAPH_API_BASE_URL", "https://graph.facebook.com/v25.0").rstrip("/")

    def debug_token(self, input_token: str, app_access_token: str) -> dict:
        url = f"{self.graph_base_url}/debug_token?{urlencode({'input_token': input_token, 'access_token': app_access_token})}"
        try:
            with urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except HTTPError as exc:
            return self._failed_http(exc)
        except URLError as exc:
            return {
                "status": "FAILED",
                "error_code": "FACEBOOK_DEBUG_NETWORK_ERROR",
                "error_message": str(exc.reason)[:500],
                "response_code": "",
                "response_body": "",
            }
        except Exception as exc:
            return {
                "status": "FAILED",
                "error_code": "FACEBOOK_DEBUG_ERROR",
                "error_message": str(exc)[:500],
                "response_code": "",
                "response_body": "",
            }
        data = payload.get("data") or {}
        return {
            "status": "OK",
            "token_type": str(data.get("type") or ""),
            "is_valid": bool(data.get("is_valid")),
            "profile_id": str(data.get("profile_id") or ""),
            "scopes": sorted(str(scope) for scope in (data.get("scopes") or [])),
            "expires_at": data.get("expires_at") or 0,
            "app_id": str(data.get("app_id") or ""),
            "response_code": "200",
            "response_body": self._safe_body(payload),
        }

    def publish(self, message: str, page_id: str, access_token: str, link: str = "") -> dict:
        url = f"{self.graph_base_url}/{page_id}/feed"
        payload = {"message": message, "access_token": access_token}
        if link:
            payload["link"] = link
        body = urlencode(payload).encode("utf-8")
        request = Request(url, data=body, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except HTTPError as exc:
            return self._failed_http(exc)
        except URLError as exc:
            return {
                "status": "FAILED_RETRYABLE",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "error_code": "FACEBOOK_NETWORK_ERROR",
                "error_message": str(exc.reason)[:500],
                "response_code": "",
                "response_body": "",
            }
        except Exception as exc:
            return {
                "status": "FAILED_RETRYABLE",
                "facebook_post_id": "",
                "facebook_post_url": "",
                "error_code": "FACEBOOK_PUBLISH_ERROR",
                "error_message": str(exc)[:500],
                "response_code": "",
                "response_body": "",
            }

        facebook_post_id = str(payload.get("id", ""))
        permalink = self.permalink(facebook_post_id, access_token) if facebook_post_id else ""
        return {
            "status": "PUBLISHED" if facebook_post_id else "FAILED",
            "facebook_post_id": facebook_post_id,
            "facebook_post_url": permalink or (f"https://www.facebook.com/{facebook_post_id}" if facebook_post_id else ""),
            "error_code": "" if facebook_post_id else "FACEBOOK_EMPTY_POST_ID",
            "error_message": "" if facebook_post_id else "Facebook 응답에서 게시글 ID를 확인하지 못했습니다.",
            "response_code": "200",
            "response_body": self._safe_body(payload),
        }

    def permalink(self, facebook_post_id: str, access_token: str) -> str:
        url = f"{self.graph_base_url}/{facebook_post_id}?{urlencode({'fields': 'id,permalink_url,created_time', 'access_token': access_token})}"
        try:
            with urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
            return str(payload.get("permalink_url") or "")
        except Exception:
            return ""

    def recent_feed(self, page_id: str, access_token: str, limit: int = 25) -> list[dict]:
        fields = "id,message,created_time,permalink_url,shares,comments.summary(true),reactions.summary(true)"
        url = f"{self.graph_base_url}/{page_id}/feed?{urlencode({'fields': fields, 'limit': limit, 'access_token': access_token})}"
        try:
            with urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
            return list(payload.get("data") or [])
        except Exception:
            return []

    def comments(self, post_id: str, access_token: str, limit: int = 10) -> list[dict]:
        fields = "id,message,created_time,like_count,comment_count"
        url = f"{self.graph_base_url}/{post_id}/comments?{urlencode({'fields': fields, 'limit': limit, 'access_token': access_token})}"
        try:
            with urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
            return list(payload.get("data") or [])
        except Exception:
            return []

    def _failed_http(self, exc: HTTPError) -> dict:
        raw = exc.read().decode("utf-8", errors="replace")
        error_code = "FACEBOOK_HTTP_ERROR"
        error_message = raw[:500]
        meta_error = meta_error_from_body(raw)
        try:
            payload = json.loads(raw)
            error = payload.get("error") or {}
            error_code = str(error.get("code") or error.get("type") or error_code)
            error_message = str(error.get("message") or raw)[:500]
        except json.JSONDecodeError:
            pass
        category = classify_meta_error(meta_error, exc.code) if meta_error else "FACEBOOK_API_TEMPORARY" if exc.code in {408, 409, 425, 429, 500, 502, 503, 504} else "FACEBOOK_UNKNOWN_ERROR"
        retryable = retryable_for_category(category)
        context = build_error_context(
            error_code=error_code,
            error_message=error_message,
            response_code=str(exc.code),
            response_body=raw,
        )
        return {
            "status": "FAILED_RETRYABLE" if retryable else "FAILED",
            "facebook_post_id": "",
            "facebook_post_url": "",
            "error_code": error_code,
            "error_category": category,
            "error_message": error_message,
            "meta_error": meta_error,
            "retryable_yn": retryable,
            "response_code": str(exc.code),
            "response_body": raw[:1000],
            "error_context": context,
        }

    def _safe_body(self, payload: dict) -> str:
        return json.dumps(payload, ensure_ascii=False)[:1000]
