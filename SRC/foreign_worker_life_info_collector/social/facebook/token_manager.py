"""Facebook long-lived token storage and refresh helpers."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

FACEBOOK_CONFIG_PATH_ENV = "FACEBOOK_CONFIG_PATH"
FACEBOOK_APP_ID_ENV = "FACEBOOK_APP_ID"
FACEBOOK_APP_SECRET_ENV = "FACEBOOK_APP_SECRET"
FACEBOOK_APP_TOKEN_ENV = "FACEBOOK_APP_TOKEN"
FACEBOOK_PAGE_ID_ENV = "FACEBOOK_PAGE_ID"
FACEBOOK_PAGE_ACCESS_TOKEN_ENV = "FACEBOOK_PAGE_ACCESS_TOKEN"
FACEBOOK_USER_ACCESS_TOKEN_ENV = "FACEBOOK_USER_ACCESS_TOKEN"
FACEBOOK_GRAPH_API_BASE_URL_ENV = "FACEBOOK_GRAPH_API_BASE_URL"
FACEBOOK_TIMEOUT_SEC_ENV = "FACEBOOK_TIMEOUT_SEC"
FACEBOOK_REFRESH_MARGIN_SECONDS_ENV = "FACEBOOK_LONG_LIVED_REFRESH_MARGIN_SECONDS"

DEFAULT_REFRESH_MARGIN_SECONDS = 7 * 24 * 60 * 60


@dataclass
class FacebookTokenSelection:
    page_id: str
    access_token: str
    source: str
    token_fingerprint: str
    config_path: str
    token_status: dict[str, Any] | None = None


def default_config_path() -> Path:
    configured = os.getenv(FACEBOOK_CONFIG_PATH_ENV, "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path(__file__).resolve().parents[2] / "config" / "facebook_config.json"


def token_fingerprint(value: str, length: int = 8) -> str:
    value = (value or "").strip()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length] if value else ""


def mask_token(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if len(value) <= 12:
        return f"{value[:2]}***{value[-2:]}"
    return f"{value[:6]}...{value[-6:]}"


class FacebookTokenManager:
    def __init__(self, config_path: Path | None = None, timeout: int | None = None) -> None:
        self.config_path = config_path or default_config_path()
        self.timeout = timeout or int(os.getenv(FACEBOOK_TIMEOUT_SEC_ENV, "20"))
        self.graph_base_url = os.getenv(FACEBOOK_GRAPH_API_BASE_URL_ENV, "https://graph.facebook.com/v25.0").rstrip("/")

    def get_page_token(self, *, allow_refresh: bool = True, force_refresh: bool = False) -> FacebookTokenSelection:
        page_id = os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip()
        config = self.load_config()
        config_token = str(config.get("page_access_token") or "").strip()
        if page_id and config_token and not force_refresh:
            debug = self.debug_token(config_token)
            if self._token_usable(debug, page_id):
                return FacebookTokenSelection(
                    page_id=page_id,
                    access_token=config_token,
                    source="facebook_config.json",
                    token_fingerprint=token_fingerprint(config_token),
                    config_path=str(self.config_path),
                    token_status=debug,
                )
            if not allow_refresh:
                return FacebookTokenSelection(
                    page_id=page_id,
                    access_token=config_token,
                    source="facebook_config.json_invalid",
                    token_fingerprint=token_fingerprint(config_token),
                    config_path=str(self.config_path),
                    token_status=debug,
                )

        refresh_error = ""
        if allow_refresh:
            try:
                refreshed = self.refresh_from_user_token(config=config)
                if refreshed.access_token:
                    return refreshed
            except RuntimeError as exc:
                refresh_error = str(exc)[:500]

        env_token = os.getenv(FACEBOOK_PAGE_ACCESS_TOKEN_ENV, "").strip()
        debug = self.debug_token(env_token) if env_token else None
        if refresh_error:
            debug = {**(debug or {}), "refresh_error": refresh_error}
        return FacebookTokenSelection(
            page_id=page_id,
            access_token=env_token,
            source="env_fallback",
            token_fingerprint=token_fingerprint(env_token),
            config_path=str(self.config_path),
            token_status=debug,
        )

    def refresh_from_user_token(self, *, config: dict[str, Any] | None = None) -> FacebookTokenSelection:
        config = config or self.load_config()
        page_id = os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip()
        user_seed = (
            os.getenv(FACEBOOK_USER_ACCESS_TOKEN_ENV, "").strip()
            or str(config.get("long_lived_user_access_token") or "").strip()
        )
        if not page_id:
            raise RuntimeError("FACEBOOK_PAGE_ID is required to refresh Facebook page token.")
        if not user_seed:
            raise RuntimeError("FACEBOOK_USER_ACCESS_TOKEN or stored long_lived_user_access_token is required.")

        long_user = self.exchange_long_lived_user_token(user_seed)
        user_token = str(long_user.get("access_token") or user_seed).strip()
        page = self.fetch_page_token(user_token=user_token, page_id=page_id)
        page_token = str(page.get("access_token") or "").strip()
        if not page_token:
            raise RuntimeError(f"Page token was not returned for FACEBOOK_PAGE_ID={page_id}.")

        now = int(time.time())
        debug = self.debug_token(page_token)
        payload = {
            "version": 1,
            "updated_at": now,
            "graph_base_url": self.graph_base_url,
            "page_id": page_id,
            "page_name": page.get("name", ""),
            "page_access_token": page_token,
            "page_token_fingerprint": token_fingerprint(page_token),
            "page_token_masked": mask_token(page_token),
            "page_token_debug": self.safe_debug(debug),
            "long_lived_user_access_token": user_token,
            "user_token_fingerprint": token_fingerprint(user_token),
            "user_token_masked": mask_token(user_token),
            "user_token_obtained_at": now,
            "user_token_expires_at": now + int(long_user.get("expires_in") or 0) if long_user.get("expires_in") else "",
            "source": "FACEBOOK_USER_ACCESS_TOKEN",
        }
        self.write_config(payload)
        return FacebookTokenSelection(
            page_id=page_id,
            access_token=page_token,
            source="refreshed_facebook_config.json",
            token_fingerprint=token_fingerprint(page_token),
            config_path=str(self.config_path),
            token_status=debug,
        )

    def exchange_long_lived_user_token(self, user_token: str) -> dict[str, Any]:
        app_id = os.getenv(FACEBOOK_APP_ID_ENV, "").strip()
        app_secret = os.getenv(FACEBOOK_APP_SECRET_ENV, "").strip()
        if not app_id or not app_secret:
            raise RuntimeError("FACEBOOK_APP_ID and FACEBOOK_APP_SECRET are required for long-lived user token exchange.")
        payload = self._get_json(
            "/oauth/access_token",
            {
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": user_token,
            },
        )
        access_token = str(payload.get("access_token") or "").strip()
        if not access_token:
            raise RuntimeError("Meta token exchange did not return access_token.")
        return payload

    def fetch_page_token(self, *, user_token: str, page_id: str) -> dict[str, Any]:
        payload = self._get_json(
            "/me/accounts",
            {
                "fields": "id,name,access_token,tasks",
                "access_token": user_token,
            },
        )
        for item in payload.get("data") or []:
            if str(item.get("id") or "") == page_id:
                return item
        raise RuntimeError(f"FACEBOOK_PAGE_ID={page_id} was not found in /me/accounts response.")

    def debug_token(self, input_token: str) -> dict[str, Any]:
        if not input_token:
            return {}
        app_token = os.getenv(FACEBOOK_APP_TOKEN_ENV, "").strip()
        app_id = os.getenv(FACEBOOK_APP_ID_ENV, "").strip()
        app_secret = os.getenv(FACEBOOK_APP_SECRET_ENV, "").strip()
        access_token = app_token or (f"{app_id}|{app_secret}" if app_id and app_secret else "")
        if not access_token:
            return {}
        try:
            payload = self._get_json("/debug_token", {"input_token": input_token, "access_token": access_token})
        except RuntimeError:
            return {}
        data = payload.get("data") or {}
        return {
            "token_type": str(data.get("type") or ""),
            "is_valid": data.get("is_valid"),
            "profile_id": str(data.get("profile_id") or ""),
            "scopes": sorted(str(scope) for scope in (data.get("scopes") or [])),
            "expires_at": data.get("expires_at") or 0,
            "app_id": str(data.get("app_id") or ""),
            "checked_at": int(time.time()),
        }

    def load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}
        try:
            payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def write_config(self, payload: dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(self.config_path.parent), suffix=".tmp") as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2, sort_keys=True)
            tmp.write("\n")
            temp_name = tmp.name
        os.replace(temp_name, self.config_path)

    def safe_config_summary(self) -> dict[str, Any]:
        config = self.load_config()
        return {
            "config_path": str(self.config_path),
            "exists": self.config_path.exists(),
            "page_id": config.get("page_id", ""),
            "page_name": config.get("page_name", ""),
            "page_token_fingerprint": config.get("page_token_fingerprint", ""),
            "user_token_fingerprint": config.get("user_token_fingerprint", ""),
            "updated_at": config.get("updated_at", ""),
            "user_token_expires_at": config.get("user_token_expires_at", ""),
            "page_token_debug": config.get("page_token_debug", {}),
        }

    def safe_debug(self, debug: dict[str, Any]) -> dict[str, Any]:
        return {
            "token_type": debug.get("token_type", ""),
            "is_valid": debug.get("is_valid", "unknown"),
            "profile_id": debug.get("profile_id", ""),
            "scopes": debug.get("scopes", []),
            "expires_at": debug.get("expires_at", 0),
            "app_id_present": bool(debug.get("app_id")),
            "checked_at": debug.get("checked_at", int(time.time())),
        }

    def _token_usable(self, debug: dict[str, Any], page_id: str) -> bool:
        if not debug:
            return True
        if debug.get("is_valid") is False:
            return False
        profile_id = str(debug.get("profile_id") or "")
        if profile_id and profile_id != page_id:
            return False
        expires_at = _int_or_none(debug.get("expires_at"))
        if not expires_at:
            return True
        margin = int(os.getenv(FACEBOOK_REFRESH_MARGIN_SECONDS_ENV, str(DEFAULT_REFRESH_MARGIN_SECONDS)))
        return expires_at - int(time.time()) > margin

    def _get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.graph_base_url}{path}?{urlencode(params)}"
        try:
            with urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(_safe_meta_error(raw) or f"Meta HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(str(exc.reason)) from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Meta response was not valid JSON.") from exc
        return payload if isinstance(payload, dict) else {}


def _safe_meta_error(raw: str) -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw[:240]
    error = payload.get("error") or {}
    if not isinstance(error, dict):
        return raw[:240]
    code = error.get("code", "")
    subcode = error.get("error_subcode", "")
    message = str(error.get("message") or "")
    return f"Meta error code={code} subcode={subcode}: {message[:220]}"


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def get_facebook_page_token(*, allow_refresh: bool = True, force_refresh: bool = False) -> FacebookTokenSelection:
    return FacebookTokenManager().get_page_token(allow_refresh=allow_refresh, force_refresh=force_refresh)
